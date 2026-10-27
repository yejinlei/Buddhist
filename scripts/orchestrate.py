#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大正藏全量入库「分批循环」编排器
流程：下载一批 -> 增量解析 -> 重建索引 -> 提交推送 -> 循环，直到 2459 部全部完成。
相对 loop_pipeline.sh 的修正：
  1) 批次判断用 t*.json（原脚本误用 n*.json 恒为 0）
  2) 解析改为「增量」：只解析尚无 JSON 的 XML，避免每批重解析全库
  3) 缓存/清单均在工作目录，断点续跑
"""
import sys, os, json, time, subprocess, importlib.util
from pathlib import Path
import concurrent.futures

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('pf', Path(__file__).parent / 'pipeline_full.py')
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)

LOG = ROOT / 'orchestrate.log'
LOCK = ROOT / '.orchestrate.lock'
CHUNK_DL = 150


def acquire_lock():
    """单实例锁：已有存活实例则退出，避免重复进程互相抢缓存。"""
    if LOCK.exists():
        try:
            pid = int(LOCK.read_text().strip())
            os.kill(pid, 0)
            print(f'已有实例 {pid} 在运行，本进程退出', flush=True)
            return False
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    LOCK.write_text(str(os.getpid()))
    return True


def release_lock():
    try:
        if LOCK.exists() and LOCK.read_text().strip() == str(os.getpid()):
            LOCK.unlink()
    except Exception:
        pass


def log(m):
    line = f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] {m}'
    print(line, flush=True)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def parse_incremental(workers=4):
    """只解析还没有对应 JSON 的 XML，避免重复解析已入库的部。"""
    man = pf.load_manifest()
    volof = {n: v for v, names in man.items() for n in names}
    metas = pf.load_meta()
    files = sorted(pf.CACHE.glob('[Tt]*.xml'))
    todo = []
    for fp in files:
        short = pf.work_short(fp.stem)
        if not short:
            continue
        if not (pf.OUT / f'{short.lower()}.json').exists():
            todo.append((fp, short))
    log(f'增量解析: 待解析 {len(todo)} / 缓存 {len(files)}')
    if not todo:
        return 0

    def one(item):
        fp, short = item
        try:
            parsed = pf.parse_tei(fp.read_bytes())
        except Exception:
            return None
        if not parsed:
            return None
        meta = metas.get(short)
        if not meta:
            meta = pf.fetch_meta(short)
            metas[short] = meta
        title = parsed['title'] or meta.get('title', '') or fp.stem
        translator = meta.get('byline', '') or parsed['author']
        content = parsed['chapters']
        out = {
            'id': short.lower(),
            'taisho': short,
            'title': title,
            'translator': translator,
            'vol': volof.get(fp.stem, ''),
            'juan': len(content),
            'chars': sum(len(c['text']) for c in content),
            'content': content,
        }
        (pf.OUT / f'{short.lower()}.json').write_text(
            json.dumps(out, ensure_ascii=False), encoding='utf-8')
        return True

    n = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(one, todo)):
            if r:
                n += 1
            if (i + 1) % 100 == 0:
                try:
                    pf.META_CACHE.write_text(json.dumps(metas, ensure_ascii=False))
                except Exception:
                    pass
                log(f'  解析 {i + 1}/{len(todo)}')
    try:
        pf.META_CACHE.write_text(json.dumps(metas, ensure_ascii=False))
    except Exception:
        pass
    log(f'增量解析完成: 新增 {n} 部')
    return n


def rebuild_index():
    index = []
    for fp in sorted(pf.OUT.glob('t*.json')):
        try:
            d = json.loads(fp.read_text())
            index.append({k: d.get(k) for k in
                          ('id', 'taisho', 'title', 'translator', 'vol', 'juan', 'chars')})
        except Exception:
            pass
    index.sort(key=lambda x: (x.get('taisho') or ''))
    idx = {
        'total': len(index),
        'chars': sum((x.get('chars') or 0) for x in index),
        'source': 'CBETA大正藏',
        'updated': time.strftime('%Y-%m-%d %H:%M'),
        'sutras': index,
    }
    (pf.OUT / 'index.json').write_text(
        json.dumps(idx, ensure_ascii=False, indent=1), encoding='utf-8')
    log(f'索引重建: {idx["total"]} 部 / {idx["chars"]} 字')
    return idx


def download_chunk(chunk, workers=4):
    ok = fail = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(pf.dl_one, it) for it in chunk]
        for i, f in enumerate(concurrent.futures.as_completed(futs)):
            st, _ = f.result()
            if st == 'ok':
                ok += 1
            elif st == 'fail':
                fail += 1
            if (i + 1) % 25 == 0 or i == len(chunk) - 1:
                log(f'  下载 {i + 1}/{len(chunk)} ok={ok} fail={fail}')
    return ok, fail


def git_setup():
    for k, v in [('http.postBuffer', '524288000'),
                 ('user.name', 'yejinlei'),
                 ('user.email', 'yejinlei@users.noreply.github.com')]:
        subprocess.run(['git', 'config', k, v], cwd=ROOT, check=False)


def git_commit_push(tag, n, final=False):
    try:
        subprocess.run(['git', 'add', 'sutras/', 'scripts/'], cwd=ROOT, check=False)
        d = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=ROOT)
        if d.returncode == 0:
            log('  无变更，跳过提交')
            return
        msg = (f'✅ 大正藏全量入库完成，共 {n} 部' if final
               else f'🚀 第{tag}批：大正藏经文库入库，累计 {n} 部')
        subprocess.run(['git', 'commit', '-m', msg], cwd=ROOT, check=False)
        r = subprocess.run(['git', 'push'], cwd=ROOT, capture_output=True, text=True)
        log(f'  推送 rc={r.returncode} {r.stderr.strip()[:200]}')
    except Exception as e:
        log(f'  git 错误: {e}')


def remaining(man):
    return [(v, n) for v, names in man.items() for n in names if not (pf.CACHE / n).exists()]


def main():
    log('=== 编排流水线启动 ===')
    git_setup()
    man = pf.load_manifest()
    total = sum(len(v) for v in man.values())
    log(f'目标: 大正藏 {total} 部')
    batch = 0
    while True:
        todo = remaining(man)
        if todo:
            chunk = todo[:CHUNK_DL]
            log(f'第{batch + 1}批 下载 {len(chunk)} 部 (尚缺 {len(todo)})')
            ok, fail = download_chunk(chunk)
            log(f'  下载结果 ok={ok} fail={fail}')
        else:
            log('下载已全部完成')

        parse_incremental()
        idx = rebuild_index()
        git_commit_push(batch + 1, idx['total'])

        batch += 1
        todo_after = remaining(man)
        parsed = len(list(pf.OUT.glob('t*.json')))
        if not todo_after and parsed >= total:
            log(f'=== 全部完成: {parsed} 部 ===')
            git_commit_push('final', parsed, final=True)
            break
        if batch > 40:
            log('达到批次上限，停止')
            break
        time.sleep(3)


if __name__ == '__main__':
    main()

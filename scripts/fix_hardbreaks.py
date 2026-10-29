#!/usr/bin/env python3
"""修复经文JSON中的散文硬折行。
规则：只删换行符、删相邻空白，绝不改动汉字字符。
- 偈颂/齐言诗行（5-9字，行首缩进对齐）→ 保留换行
- 行末为句末/句读标点（。！？…」』）） → 保留换行（自然段）
- 行末为句中点号（，、；：）且下一行首字是汉字 → 删除换行（把两句接起来）
- 行末为汉字/字母，下一行首是汉字 → 删除换行（硬折）
- 行末/行首是引号类配对符号 → 按情况处理
处理后逐字核对：修复后非空汉字序列必须 === 修复前非空汉字序列。
"""
import json, os, glob, re, sys

SUTRA_DIR = 'sutras'
BACKUP_DIR = '/tmp/sutras_backup_before_hardbreak'

# 句末标点（表示一段完整语义，保留换行）
END_PUNCT = set('。！？…」』）】〕〗〉》'+'」』）')
# 句中点号（语义未完，若下行接汉字则为硬折）
MID_PUNCT = set('，、；：「『（【〔〖〈《')

def is_cjk(c):
    return '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf' or '\uf900' <= c <= '\ufaff'

def is_verse(lines):
    """判断是否偈颂：所有非空行长度在 4-10 之间且整齐（五言/七言）"""
    lens = []
    for ln in lines:
        s = ln.strip()
        if not s: continue
        n = sum(1 for c in s if is_cjk(c))
        lens.append(n)
    if len(lens) < 3: return False
    if not lens: return False
    if min(lens) < 3: return False
    if max(lens) > 11: return False
    avg = sum(lens)/len(lens)
    if not (4 <= avg <= 9.5): return False
    if max(lens) - min(lens) > 4: return False
    return True

def fix_text(text):
    """修复硬折行。返回 (修复后文本, 合并处数)"""
    if '\n' not in text:
        return text, 0
    lines = text.split('\n')
    if is_verse(lines):
        return text, 0
    # 预处理：给每行计算是否"短行题头"（译者/品题/卷题，通常<15字且无标点）
    def is_title_line(s):
        s = s.strip()
        if not s: return False
        cjk_n = sum(1 for c in s if is_cjk(c))
        # 短行（<=18字）且无句末标点、无句中点号（除了可能的标点）→ 题头
        if cjk_n <= 18:
            # 若含句末标点则不是题头
            if not any(c in END_PUNCT for c in s):
                # 若以"譯/译"结尾（译者题）→ 是题头
                if s.endswith('譯') or s.endswith('译'): return True
                # 若是"如是我聞"/"一時"开头且紧跟正文 → 不是题头（是正文起句）
                if s.startswith('如是我聞') or s.startswith('如是我闻'): return False
                if s.startswith('一時') or s.startswith('一时'): return False
                # 无句末标点的短行，可能是品题或卷题
                return True
        return False
    # 行尾-行首对的处理
    out = []
    merges = 0
    i = 0
    while i < len(lines):
        cur = lines[i]
        cur_stripped = cur.rstrip()
        # 处理连续行
        while i + 1 < len(lines):
            nxt = lines[i+1]
            nxt_lstrip = nxt.lstrip()
            if not cur_stripped:
                break  # 空行保留
            if not nxt_lstrip:
                break  # 下一行空，断段
            # 若当前行是题头短行 → 不合并
            if is_title_line(cur_stripped):
                break
            # 若下一行是题头短行 → 不合并
            if is_title_line(nxt_lstrip):
                break
            last_ch = cur_stripped[-1]
            first_ch = nxt_lstrip[0]
            # 若上一行末是句末标点 → 保留换行
            if last_ch in END_PUNCT:
                break
            # 上一行末是汉字/字母/数字 且下一行首是汉字/字母 → 硬折，拼接
            if (is_cjk(last_ch) or last_ch.isalnum()) and (is_cjk(first_ch) or first_ch.isalnum()):
                # 直接拼接（无空格）
                cur = cur_stripped + nxt_lstrip
                cur_stripped = cur  # 更新用于下一次判断
                i += 1
                merges += 1
                continue
            # 上一行末是句中点号（，、；：） → 下一行若是汉字开头则拼接
            if last_ch in MID_PUNCT and is_cjk(first_ch):
                cur = cur_stripped + nxt_lstrip
                cur_stripped = cur
                i += 1
                merges += 1
                continue
            # 上一行末是引号闭合类（」』））但不是句末 → 看下一字
            # 其余情况保留换行
            break
        out.append(cur)
        i += 1
    return '\n'.join(out), merges

def cjk_chars_only(s):
    return ''.join(c for c in s if is_cjk(c) or c in '，。、；：！？「」『』（）【】〔〕《》〈〉—…·')

def process_file(fp):
    fname = os.path.basename(fp)
    with open(fp, 'r', encoding='utf-8') as f:
        d = json.load(f)
    content = d.get('content', [])
    total_merges = 0
    changed = False
    for ch in content:
        t = ch.get('text','')
        if not t or '\n' not in t:
            continue
        before_cjk = cjk_chars_only(t).replace('\n','').replace(' ','')
        new_t, merges = fix_text(t)
        after_cjk = cjk_chars_only(new_t).replace('\n','').replace(' ','')
        # 关键校验：汉字序列必须完全一致
        if before_cjk != after_cjk:
            print(f'  !! 校验失败 {fname} ch[{ch.get("chapter","?")[:20]}]: 字符序列变了！', file=sys.stderr)
            print(f'     before len={len(before_cjk)} after len={len(after_cjk)}', file=sys.stderr)
            return False, 0
        if merges > 0:
            ch['text'] = new_t
            total_merges += merges
            changed = True
    if changed:
        # 更新 actual_char_count (按非空白字符数)
        new_total = sum(len(c['text']) for c in content)
        d['actual_char_count'] = new_total
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    return True, total_merges

def main():
    files = sorted([f for f in glob.glob(f'{SUTRA_DIR}/*.json')
                    if 'search-order' not in f and 'index' not in f and 'hant2simp' not in f])
    print(f'待扫描经文: {len(files)}')
    total_changed = 0
    total_merges = 0
    fail = 0
    for i, fp in enumerate(files):
        ok, merges = process_file(fp)
        if not ok:
            fail += 1; continue
        if merges > 0:
            total_changed += 1
            total_merges += merges
        if (i+1) % 500 == 0:
            print(f'  进度 {i+1}/{len(files)}  已修复 {total_changed} 经 {total_merges} 处硬折')
    print(f'\n完成: 修复 {total_changed} 部经，共合并 {total_merges} 处硬折行')
    if fail:
        print(f'失败 {fail} 部经，已跳过（字符校验未通过，未修改）')

if __name__ == '__main__':
    main()

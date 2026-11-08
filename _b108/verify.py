# -*- coding: utf-8 -*-
"""第108批收尾核验：线上↔本地逐文件哈希 + 仓库树接口全量核验清单。"""
import base64, json, os, re, subprocess, sys, time, urllib.request, urllib.error

def sh(*a):
    return subprocess.check_output(list(a)).decode('utf-8', 'replace')

root = sh('git', 'rev-parse', '--show-toplevel').strip()
os.chdir(root)
url = sh('git', 'remote', 'get-url', 'origin').strip()
cred = re.search(r'://([^:]+):([^@]+)@', url)
repo_m = re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)

def api(path, accept='application/vnd.github+json', tries=6):
    for k in range(tries):
        req = urllib.request.Request('https://api.github.com' + path,
            headers={'Authorization': 'token ' + token, 'Accept': accept,
                     'User-Agent': 'buddhist-verify'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode('utf-8', 'replace'))
        except Exception as e:
            print('  重试', k + 1, str(e)[:80]); time.sleep(3)
    return None

BATCH = ["data/modern-translation/%s.json" % t for t in
         ["t1618","t1589","t1613","t1608","t1526","t1652","t1493","t1919","t2020","t1793","t2781","t1773"]]
BATCH.append("pages/sutras.html")

print("=== 1) 线上↔本地逐文件哈希 ===")
ok = 0
tree = api('/repos/%s/%s/git/trees/main?recursive=1' % (owner, repo))
online_paths = set()
if tree:
    for it in tree.get('tree', []):
        if it.get('type') == 'blob':
            online_paths.add(it['path'])
print('仓库树 blob 数:', len(online_paths))
for fp in BATCH:
    if fp not in online_paths:
        print('  ✗ 线上缺失', fp); continue
    local = sh('git', 'hash-object', fp).strip()
    blob = api('/repos/%s/%s/contents/%s?ref=main' % (owner, repo, fp), accept='application/vnd.github+json')
    rsha = blob.get('sha') if isinstance(blob, dict) else None
    if rsha == local:
        ok += 1
    else:
        print('  ✗ 不一致', fp, 'local', local, 'online', rsha)
print('哈希一致: %d/%d' % (ok, len(BATCH)))

print("=== 2) 清单 ↔ 线上实现 ===")
s = open('pages/sutras.html', encoding='utf-8').read()
m = re.search(r'const BAIHUA_AVAILABLE = new Set\(\[([^\]]*)\]\);', s)
ids = [x.strip().strip("'") for x in m.group(1).split(',') if x.strip()]
print('清单条数', len(ids))
missing = []
for i in ids:
    p = 'data/modern-translation/%s.json' % i
    if p not in online_paths:
        missing.append(i)
print('线上缺失', len(missing), missing[:20])
online_mt = sum(1 for p in online_paths if p.startswith('data/modern-translation/') and p.endswith('.json'))
print('线上译文文件数', online_mt, '| 本地清单', len(ids))

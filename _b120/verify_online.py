# -*- coding: utf-8 -*-
import base64, json, re, subprocess, urllib.request, os, sys, time
root='/home/user/workspace/13511660557912876654/buddhist-ontology'
os.chdir(root)
def sh(*a): return subprocess.check_output(list(a)).decode()
url=sh('git','remote','get-url','origin').strip()
cred=re.search(r'://([^:]+):([^@]+)@', url)
repo_m=re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)
branch='main'
def api(path):
    req=urllib.request.Request('https://api.github.com'+path,
        headers={'Authorization':'token '+token,'Accept':'application/vnd.github+json','User-Agent':'x'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, r.read()

files=['data/modern-translation/t0008.json','data/modern-translation/t0229.json','data/modern-translation/t0324.json','pages/sutras.html','data/baihua-audit.json']
print('=== 线上↔本地哈希比对 ===')
for fp in files:
    local=sh('git','hash-object',fp).strip()
    st, body = api(f'/repos/{owner}/{repo}/contents/{fp}?ref={branch}')
    remote=json.loads(body)['sha']
    print(('OK  ' if local==remote else 'DIFF'), fp, local[:12], remote[:12])

# 仓库树全量
print('=== 拉取仓库树 ===')
tree=None
for attempt in range(6):
    try:
        st, body = api(f'/repos/{owner}/{repo}/git/trees/{branch}?recursive=1')
        j=json.loads(body)
        if j.get('truncated'):
            print('  truncated=True 重试...'); time.sleep(3); continue
        tree=j['tree']; break
    except Exception as e:
        print('  重试', attempt, e); time.sleep(4)
online=set()
for it in tree:
    p=it['path']
    if p.startswith('data/modern-translation/') and p.endswith('.json'):
        online.add(os.path.basename(p)[:-5])
print('线上译文文件数:', len(online))
s=open('pages/sutras.html',encoding='utf-8').read()
m=re.search(r'const BAIHUA_AVAILABLE = new Set\(\[([^\]]*)\]\);',s)
ids=[x.strip().strip("'") for x in m.group(1).split(',') if x.strip()]
missing=[i for i in ids if i not in online]
print('清单条数:', len(ids), '| 缺失:', len(missing), missing[:20])

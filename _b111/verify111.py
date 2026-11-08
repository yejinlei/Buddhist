# -*- coding: utf-8 -*-
import json, os, re, subprocess, urllib.request, urllib.error
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)
url = subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode().strip()
cred = re.search(r'://([^:]+):([^@]+)@', url)
repo_m = re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)

def api(path, timeout=60):
    req = urllib.request.Request('https://api.github.com' + path,
        headers={'Authorization': 'token ' + token, 'Accept': 'application/vnd.github+json', 'User-Agent': 'bd'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode('utf-8', 'replace'))
    except urllib.error.HTTPError as e:
        return e.code, None

B = "t1361 t1465 t1879b t2760 t0741 t1637 t1628 t1609 t1930 t0277 t0730 t0350".split()
files = [f'data/modern-translation/{t}.json' for t in B] + ['pages/sutras.html']
print("=== 逐文件哈希 ===")
same = 0
for fp in files:
    local = subprocess.check_output(['git', 'hash-object', fp]).decode().strip()
    st, d = api(f'/repos/{owner}/{repo}/contents/{fp}?ref=main')
    remote = d.get('sha') if st == 200 and isinstance(d, dict) else None
    ok = (local == remote)
    same += ok
    print(('OK  ' if ok else 'DIFF'), fp, local[:8], (remote[:8] if remote else 'MISSING'))
print(f"哈希一致 {same}/{len(files)}")

print("=== 线上全量核验 ===")
st, tree = api(f'/repos/{owner}/{repo}/git/trees/main?recursive=1')
print('tree status=', st, 'truncated=', (tree or {}).get('truncated'))
paths = [e['path'] for e in (tree or {}).get('tree', []) if e['type'] == 'blob']
online = set(p for p in paths if p.startswith('data/modern-translation/') and p.endswith('.json'))
s = open('pages/sutras.html', encoding='utf-8').read()
m = re.search(r'BAIHUA_AVAILABLE = new Set\(\[(.*?)\]\);', s, re.S)
ids = re.findall(r"'([^']+)'", m.group(1))
missing = [i for i in ids if f'data/modern-translation/{i}.json' not in online]
print('清单条数=', len(ids), '线上译文文件数=', len(online), '缺失=', len(missing), missing[:12])

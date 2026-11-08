#!/usr/bin/env python3
"""轻量部署：把本次改动涉及的文件逐个 PUT 到 GitHub（自动获取/创建 blob+tree+commit）。"""
import base64, json, os, subprocess, sys, urllib.request, urllib.error, time, re

API = 'https://api.github.com'
ROOT = subprocess.check_output(['git','rev-parse','--show-toplevel']).decode().strip()
os.chdir(ROOT)

url = subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
m = re.search(r'://[^:]+:([^@]+)@github\.com/([^/]+)/([^/.]+)', url)
if not m:
    sys.exit('无法解析 remote 凭据');
TOKEN, OWNER, REPO = m.group(1), m.group(2), m.group(3)
HEADERS = {'Authorization':'token '+TOKEN,'Accept':'application/vnd.github+json','User-Agent':'bd'}

def gh(path, method='GET', data=None, timeout=60):
    req = urllib.request.Request(API+path, method=method,
        data=json.dumps(data).encode() if data is not None else None,
        headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode('utf-8','replace')
                return r.status, (json.loads(body) if body else None)
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode('utf-8','replace')[:500]
        except Exception as e:
            if attempt==2: return 0, str(e)
            time.sleep(2*(attempt+1))

def get(path): return gh(path)
def put(path,data): return gh(path,'PUT',data)

def sha_of_remote(path):
    code, r = get(f'/repos/{OWNER}/{REPO}/contents/{path}?ref=main')
    if code==200 and isinstance(r,dict):
        return r.get('sha'), r.get('content','')
    return None, None

def upload_file(local_path, repo_path=None):
    repo_path = repo_path or local_path
    with open(local_path,'rb') as f: content = f.read()
    b64 = base64.b64encode(content).decode()
    code, r = get(f'/repos/{OWNER}/{REPO}/contents/{repo_path}?ref=main')
    sha = r.get('sha') if code==200 and isinstance(r,dict) else None
    payload = {'message':'M4 全量事件覆盖：'+os.path.basename(local_path),
               'content':b64, 'branch':'main'}
    if sha: payload['sha'] = sha
    code2, r2 = put(f'/repos/{OWNER}/{REPO}/contents/{repo_path}', payload)
    return code2, (r2.get('commit',{}).get('sha','')[:7] if isinstance(r2,dict) else str(r2)[:100])

def main():
    # 列出本次改动的关键文件
    files = [
        'pages/ontology.html',
        'pages/sutras.html',
        'ontology/ontology.yaml',
        'data/ontology-schema.json',
        'ontology/dharma_assemblies.json',
        'ontology/instances/events.json',
        'ontology/instances/manifest.json',
        'ontology/instances/shard-map.json',
        'scripts/build_shards.py',
        'scripts/patch_m4_finalize.py',
    ]
    # 分片
    for i in range(17):
        files.append(f'ontology/instances/shards/shard-{i:03d}.json')
    ok=0; fail=[]
    for fp in files:
        if not os.path.exists(fp):
            print(f'SKIP {fp} (不存在)'); continue
        sz = os.path.getsize(fp)
        print(f'上传 {fp} ({sz/1024:.1f} KB) ... ', end='', flush=True)
        code, msg = upload_file(fp)
        if code in (200,201):
            print(f'OK {code} {msg}'); ok+=1
        else:
            print(f'FAIL {code} {msg}'); fail.append((fp,code,msg))
    print(f'\n完成 {ok}/{len(files)}')
    if fail:
        print('失败:')
        for f,c,m in fail: print(f'  {f}: {c} {m[:120]}')

if __name__=='__main__':
    main()

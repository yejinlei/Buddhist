#!/usr/bin/env python3
"""部署 M2 相关文件（API 逐文件 PUT）。"""
import base64, json, os, sys, urllib.request, urllib.error, time, re, subprocess

API = 'https://api.github.com'
ROOT = subprocess.check_output(['git','rev-parse','--show-toplevel']).decode().strip()
os.chdir(ROOT)
url = subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
m = re.search(r'://[^:]+:([^@]+)@github\.com/([^/]+)/([^/.]+)', url)
if not m: sys.exit('无法解析凭据');
TOKEN, OWNER, REPO = m.group(1), m.group(2), m.group(3)
HEADERS = {'Authorization':'token '+TOKEN,'Accept':'application/vnd.github+json','User-Agent':'bd'}

def gh(path, method='GET', data=None, timeout=90):
    req = urllib.request.Request(API+path, method=method,
        data=json.dumps(data).encode() if data is not None else None, headers=HEADERS)
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

def upload_file(local_path, repo_path=None):
    repo_path = repo_path or local_path
    with open(local_path,'rb') as f: content = f.read()
    b64 = base64.b64encode(content).decode()
    code, r = gh(f'/repos/{OWNER}/{REPO}/contents/{repo_path}?ref=main')
    sha = r.get('sha') if code==200 and isinstance(r,dict) else None
    payload = {'message':'M2 ABox 全量补全: '+repo_path,'content':b64,'branch':'main'}
    if sha: payload['sha'] = sha
    code2, r2 = gh(f'/repos/{OWNER}/{REPO}/contents/{repo_path}','PUT',payload)
    return code2, (r2.get('commit',{}).get('sha','')[:7] if isinstance(r2,dict) else str(r2)[:200])

def main():
    files = [
        'pages/ontology.html',
        'pages/graph.html',
        'ontology/ontology.yaml',
        'ontology/instances/m2_index.json',
        'ontology/instances/m2_manifest.json',
        'ontology/instances/relations.json',
        'scripts/merge_m2_abox.py',
    ]
    # 实例详情 json（concepts/persons/sutras/sects）
    for sub in ['concepts','persons','sutras','sects']:
        d = f'ontology/instances/{sub}'
        for fn in sorted(os.listdir(d)):
            if fn.endswith('.json'):
                files.append(f'{d}/{fn}')
    ok=0; fail=[]; total=len(files)
    print(f'共 {total} 个文件待上传', flush=True)
    for i, fp in enumerate(files, 1):
        if not os.path.exists(fp):
            print(f'[{i}/{total}] SKIP {fp}'); continue
        sz = os.path.getsize(fp)
        if sz > 900_000:
            print(f'[{i}/{total}] SKIP {fp} ({sz/1024:.0f}KB 过大)'); continue
        code, msg = upload_file(fp)
        if code in (200,201):
            print(f'[{i}/{total}] OK  {fp} ({sz/1024:.1f}KB) {msg}', flush=True); ok+=1
        else:
            print(f'[{i}/{total}] FAIL {fp} code={code} {msg}', flush=True); fail.append((fp,code,msg))
        time.sleep(0.3)
    print(f'\n完成 {ok}/{total}, 失败 {len(fail)}')
    for f,c,m in fail[:10]: print(' -',f,c,m)

if __name__=='__main__':
    main()

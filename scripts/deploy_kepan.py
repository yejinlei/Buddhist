#!/usr/bin/env python3
"""科判数据部署：把全量科判 core.json + index.json 推到 GitHub main。"""
import base64, json, os, subprocess, sys, urllib.request, urllib.error, time, re

API = 'https://api.github.com'
ROOT = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode().strip()
os.chdir(ROOT)
url = subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode().strip()
m = re.search(r'://[^:]+:([^@]+)@github\.com/([^/]+)/([^/.]+)', url)
if not m:
    sys.exit('无法解析 remote 凭据')
TOKEN, OWNER, REPO = m.group(1), m.group(2), m.group(3)
HEADERS = {'Authorization': 'token ' + TOKEN, 'Accept': 'application/vnd.github+json', 'User-Agent': 'bd'}


def gh(path, method='GET', data=None, timeout=300):
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(data).encode() if data is not None else None,
        headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode('utf-8', 'replace')
                return r.status, (json.loads(body) if body else None)
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode('utf-8', 'replace')[:400]
        except Exception as e:
            if attempt == 2:
                return 0, str(e)
            time.sleep(3 * (attempt + 1))


def upload_file(local_path, repo_path=None, msg=None):
    repo_path = repo_path or local_path
    with open(local_path, 'rb') as f:
        content = f.read()
    b64 = base64.b64encode(content).decode()
    code, r = gh(f'/repos/{OWNER}/{REPO}/contents/{repo_path}?ref=main')
    sha = r.get('sha') if code == 200 and isinstance(r, dict) else None
    payload = {
        'message': msg or ('科判全量: ' + os.path.basename(local_path)),
        'content': b64,
        'branch': 'main',
    }
    if sha:
        payload['sha'] = sha
    code2, r2 = gh(f'/repos/{OWNER}/{REPO}/contents/{repo_path}', 'PUT', payload)
    commit = r2.get('commit', {}).get('sha', '')[:7] if isinstance(r2, dict) else str(r2)[:120]
    return code2, commit


def main():
    files = [
        ('kepan/core.json', '科判: 古德精判73部（读经页优先加载）'),
        ('kepan/shard-map.json', '科判分片映射: id→shard'),
        ('kepan/index.json', '科判索引: 2506部摘要与分计数（含别译单行本）'),
    ]
    import glob
    for f in sorted(glob.glob('kepan/shards/shard-*.json')):
        files.append((f, '科判分片: ' + os.path.basename(f)))
    for local, msg in files:
        if not os.path.exists(local):
            print(f'  跳过(不存在): {local}')
            continue
        size = os.path.getsize(local)
        t0 = time.time()
        code, commit = upload_file(local, local, msg)
        dt = time.time() - t0
        ok = '✅' if code in (200, 201) else '❌'
        print(f'  {ok} {local} ({size/1024:.0f}KB, {dt:.0f}s) -> {code} {commit}')


if __name__ == '__main__':
    main()

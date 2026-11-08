#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署：全量科判（分片）+ 读经页/科判页接入 + 复审报告，逐个 PUT 到 GitHub main。"""
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


def gh(path, method='GET', data=None, timeout=120):
    req = urllib.request.Request(API + path, method=method,
        data=json.dumps(data).encode() if data is not None else None, headers=HEADERS)
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


def upload(local_path, repo_path=None):
    repo_path = repo_path or local_path
    with open(local_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    code, r = gh(f'/repos/{OWNER}/{REPO}/contents/{repo_path}?ref=main')
    sha = r.get('sha') if code == 200 and isinstance(r, dict) else None
    payload = {'message': '科判全量：' + os.path.basename(local_path), 'content': b64, 'branch': 'main'}
    if sha:
        payload['sha'] = sha
    code2, r2 = gh(f'/repos/{OWNER}/{REPO}/contents/{repo_path}', 'PUT', payload)
    ok = code2 in (200, 201)
    cs = r2.get('commit', {}).get('sha', '')[:7] if isinstance(r2, dict) else str(r2)[:80]
    return ok, code2, cs


def main():
    files = [
        'pages/sutras.html',
        'pages/kepan.html',
        'kepan/core.json',
        'kepan/index.json',
        'kepan/shard-map.json',
        'kepan/shards/shard-000.json',
        'kepan/shards/shard-001.json',
        'kepan/shards/shard-002.json',
        'kepan/shards/shard-003.json',
        'kepan/shards/shard-004.json',
        'kepan/shards/shard-005.json',
        'kepan/audit_report.json',
        'kepan/audit_report.md',
        'scripts/build_full_kepan.py',
        'scripts/build_kepan_shards.py',
        'scripts/normalize_kepan_fields.py',
        'scripts/patch_kepan_gaps.py',
        'scripts/audit_kepan_gude.py',
    ]
    done = 0
    for f in files:
        if not os.path.exists(f):
            print('SKIP(缺失)', f, flush=True)
            continue
        ok, code, cs = upload(f)
        print(('OK  ' if ok else 'FAIL'), f, code, cs, flush=True)
        if ok:
            done += 1
        time.sleep(0.5)
    print(f'== 完成 {done}/{len(files)} ==', flush=True)


if __name__ == '__main__':
    main()

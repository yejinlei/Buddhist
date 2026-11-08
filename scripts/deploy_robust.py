# -*- coding: utf-8 -*-
"""稳健部署：逐文件 API 提交，带重试与间隔，适合网络不稳。
用法：python3 scripts/deploy_robust.py <file1> <file2> ...
"""
import base64, json, os, re, subprocess, sys, time, urllib.request, urllib.error

def sh(*a):
    return subprocess.check_output(list(a)).decode('utf-8', 'replace')

def api(path, method='GET', data=None, token=None):
    req = urllib.request.Request(
        'https://api.github.com' + path, method=method,
        data=json.dumps(data).encode() if data is not None else None,
        headers={'Authorization': 'token ' + token,
                 'Accept': 'application/vnd.github+json',
                 'User-Agent': 'buddhist-deploy'})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode('utf-8', 'replace')
            return resp.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')[:300]
    except Exception as e:
        return 0, str(e)[:200]

def main():
    root = sh('git', 'rev-parse', '--show-toplevel').strip()
    os.chdir(root)
    url = sh('git', 'remote', 'get-url', 'origin').strip()
    cred = re.search(r'://([^:]+):([^@]+)@', url)
    repo_m = re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
    token = cred.group(2)
    repo = f"{repo_m.group(1)}/{repo_m.group(2)}"
    files = sys.argv[1:]
    okf, failf = [], []
    for f in files:
        f = f.strip()
        if not f:
            continue
        rel = os.path.relpath(os.path.abspath(f), root)
        content = base64.b64encode(open(f, 'rb').read()).decode()
        done = False
        for attempt in range(4):
            st, cur = api(f"/repos/{repo}/contents/{rel}?ref=main", token=token)
            sha = cur.get('sha') if isinstance(cur, dict) else None
            payload = {'message': f'deploy {rel}', 'content': content, 'branch': 'main'}
            if sha:
                payload['sha'] = sha
            st2, r2 = api(f"/repos/{repo}/contents/{rel}", method='PUT', data=payload, token=token)
            if st2 in (200, 201):
                print(f"OK  {rel}", flush=True)
                okf.append(rel); done = True; break
            print(f"retry({attempt+1}) {rel} st={st2}", flush=True)
            time.sleep(2)
        if not done:
            print(f"FAIL {rel}", flush=True); failf.append(rel)
        time.sleep(0.6)
    print(f"=== 完成 成功{len(okf)} 失败{len(failf)} ===", flush=True)
    if failf:
        print("失败清单:", ' '.join(failf), flush=True)

if __name__ == "__main__":
    main()

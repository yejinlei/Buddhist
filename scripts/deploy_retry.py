#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""带重试的 GitHub Contents API 部署：单文件失败重试，整体不中断。
用法：python3 scripts/deploy_retry.py <file...>
"""
import base64, json, os, re, subprocess, sys, time, urllib.request, urllib.error


def sh(*a):
    return subprocess.check_output(list(a)).decode('utf-8', 'replace')


def api(path, method='GET', data=None, token=None, accept='application/vnd.github+json', timeout=40):
    req = urllib.request.Request(
        'https://api.github.com' + path, method=method,
        data=json.dumps(data).encode() if data is not None else None,
        headers={'Authorization': 'token ' + token, 'Accept': accept, 'User-Agent': 'buddhist-deploy'},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', 'replace')
            return resp.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')[:400]
    except Exception as e:
        return -1, repr(e)[:200]


def main():
    root = sh('git', 'rev-parse', '--show-toplevel').strip()
    os.chdir(root)
    url = sh('git', 'remote', 'get-url', 'origin').strip()
    cred = re.search(r'://([^:]+):([^@]+)@', url)
    repo_m = re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
    token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)
    branch = 'main'
    files = sys.argv[1:]
    ok = fail = 0
    for fp in files:
        if not os.path.exists(fp):
            print('SKIP 不存在: ' + fp, flush=True)
            continue
        b64 = base64.b64encode(open(fp, 'rb').read()).decode()
        ep = f'/repos/{owner}/{repo}/contents/{fp}?ref={branch}'
        done = False
        for attempt in range(1, 5):
            st, cur = api(ep, token=token)
            cur_sha = cur.get('sha') if (st == 200 and isinstance(cur, dict)) else None
            data = {'message': 'deploy: ' + fp, 'content': b64, 'branch': branch}
            if cur_sha:
                data['sha'] = cur_sha
            st2, r = api(ep, 'PUT', data=data, token=token)
            if st2 in (200, 201):
                print(f'OK  {fp} ({len(b64)}b) try{attempt}', flush=True)
                ok += 1
                done = True
                break
            print(f'..  retry {fp} st={st2} {str(r)[:120]}', flush=True)
            time.sleep(3)
        if not done:
            print('FAIL ' + fp, flush=True)
            fail += 1
    print(f'完成: 成功 {ok} 失败 {fail}', flush=True)


if __name__ == '__main__':
    main()

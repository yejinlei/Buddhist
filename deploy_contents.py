#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 GitHub Contents API 逐文件提交（小文件/少并发，更稳）。
用法：python3 scripts/deploy_contents.py <file1> <file2> ...
"""
import base64, json, os, re, subprocess, sys, urllib.request, urllib.error

def sh(*a):
    return subprocess.check_output(list(a)).decode('utf-8','replace')

def api(path, method='GET', data=None, token=None, accept='application/vnd.github+json'):
    req = urllib.request.Request(
        'https://api.github.com'+path, method=method,
        data=json.dumps(data).encode() if data is not None else None,
        headers={'Authorization':'token '+token,'Accept':accept,'User-Agent':'buddhist-deploy'},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body=resp.read().decode('utf-8','replace')
            return resp.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8','replace')[:500]

def main():
    root = sh('git','rev-parse','--show-toplevel').strip()
    os.chdir(root)
    url = sh('git','remote','get-url','origin').strip()
    cred = re.search(r'://([^:]+):([^@]+)@', url)
    repo_m = re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
    if not cred or not repo_m:
        sys.exit('remote 解析失败')
    token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)
    branch='main'
    files = sys.argv[1:]
    if not files:
        sys.exit('用法: deploy_contents.py <file...>')
    ok=0; fail=0
    for fp in files:
        if not os.path.exists(fp):
            print(f'SKIP 不存在: {fp}'); continue
        content = open(fp,'rb').read()
        b64 = base64.b64encode(content).decode()
        # 先查当前 sha
        ep = f'/repos/{owner}/{repo}/contents/{fp}?ref={branch}'
        st, cur = api(ep, token=token)
        cur_sha = None
        if st==200 and isinstance(cur,dict):
            cur_sha = cur.get('sha')
        msg = f'deploy: {fp}'
        data = {'message':msg,'content':b64,'branch':branch}
        if cur_sha: data['sha']=cur_sha
        st2, r = api(ep, 'PUT', data=data, token=token)
        if st2 in (200,201):
            print(f'OK  {fp} ({len(content)} bytes)')
            ok+=1
        else:
            print(f'FAIL {fp} status={st2}: {str(r)[:200]}')
            fail+=1
    print(f'\n完成: 成功 {ok} 失败 {fail}')

if __name__=='__main__':
    main()

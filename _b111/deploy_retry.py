# -*- coding: utf-8 -*-
import base64, json, os, re, subprocess, sys, time, urllib.request
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)
url = subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode().strip()
cred = re.search(r'://([^:]+):([^@]+)@', url)
repo_m = re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)
branch = 'main'

def api(path, method='GET', data=None, timeout=25):
    req = urllib.request.Request('https://api.github.com' + path, method=method,
        data=json.dumps(data).encode() if data is not None else None,
        headers={'Authorization': 'token ' + token,
                 'Accept': 'application/vnd.github+json', 'User-Agent': 'bd'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        b = resp.read().decode('utf-8', 'replace')
        return resp.status, (json.loads(b) if b else None)

for fp in sys.argv[1:]:
    content = open(fp, 'rb').read(); b64 = base64.b64encode(content).decode()
    ep = f'/repos/{owner}/{repo}/contents/{fp}?ref={branch}'
    done = False
    for att in range(1, 8):
        try:
            st, cur = api(ep)
            sha = cur.get('sha') if st == 200 and isinstance(cur, dict) else None
            data = {'message': f'deploy: {fp}', 'content': b64, 'branch': branch}
            if sha: data['sha'] = sha
            st2, r = api(ep, 'PUT', data=data)
            if st2 in (200, 201):
                print(f'OK  {fp} ({len(content)} bytes)', flush=True); done = True; break
            print(f'FAIL {fp} status={st2} att={att}', flush=True); time.sleep(4)
        except Exception as e:
            print(f'ERR {fp} att={att}: {type(e).__name__}', flush=True); time.sleep(5)
    if not done: print(f'GIVEUP {fp}', flush=True)
print('ALLDONE', flush=True)

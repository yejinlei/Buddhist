# -*- coding: utf-8 -*-
import json,re,subprocess,urllib.request,time
def sh(*a): return subprocess.check_output(list(a)).decode()
url=sh('git','remote','get-url','origin').strip()
cred=re.search(r'://([^:]+):([^@]+)@', url)
repo_m=re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)
def api(path, method='GET', data=None):
    req=urllib.request.Request('https://api.github.com'+path, method=method,
        data=json.dumps(data).encode() if data else None,
        headers={'Authorization':'token '+token,'Accept':'application/vnd.github+json','User-Agent':'x'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            b=r.read().decode('utf-8','replace'); return r.status,(json.loads(b) if b else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8','replace')[:200]
fp='data/modern-translation/t1545.json'
st,cur=api('/repos/%s/%s/contents/%s?ref=main'%(owner,repo,fp))
if st==200 and isinstance(cur,dict):
    st2,r=api('/repos/%s/%s/contents/%s'%(owner,repo,fp),'DELETE',
              {'message':'cleanup: remove orphan t1545 (残缺遗留, 不在清单)','sha':cur['sha'],'branch':'main'})
    print('删除 t1545:', st2, str(r)[:150])
else:
    print('线上不存在 t1545 或无 sha:', st)

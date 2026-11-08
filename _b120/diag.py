# -*- coding: utf-8 -*-
import os,json,re,subprocess,urllib.request,time
root='/home/user/workspace/13511660557912876654/buddhist-ontology'
os.chdir(root)
def sh(*a): return subprocess.check_output(list(a)).decode()
url=sh('git','remote','get-url','origin').strip()
cred=re.search(r'://([^:]+):([^@]+)@', url)
repo_m=re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)
def api(path):
    req=urllib.request.Request('https://api.github.com'+path,
        headers={'Authorization':'token '+token,'Accept':'application/vnd.github+json','User-Agent':'x'})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.status, r.read()
local=sorted(f[:-5] for f in os.listdir('data/modern-translation') if f.endswith('.json'))
print('本地文件数:', len(local))
tree=None
for att in range(8):
    try:
        st,body=api('/repos/%s/%s/git/trees/main?recursive=1'%(owner,repo))
        j=json.loads(body)
        if j.get('truncated'):
            print('  truncated=True'); break
        tree=j['tree']; break
    except Exception as e:
        print('  重试', att, type(e).__name__); time.sleep(4)
if tree is None:
    print('tree 拉取失败或不完整')
else:
    online=sorted(os.path.basename(it['path'])[:-5] for it in tree
                  if it['path'].startswith('data/modern-translation/') and it['path'].endswith('.json'))
    print('线上文件数:', len(online))
    print('本地有线上无:', sorted(set(local)-set(online)))
    print('线上有本地无:', sorted(set(online)-set(local)))

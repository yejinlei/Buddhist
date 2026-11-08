# -*- coding: utf-8 -*-
import os,json,re,subprocess,urllib.request,time
root='/home/user/workspace/13511660557912876654/buddhist-ontology'
os.chdir(root)
def sh(*a): return subprocess.check_output(list(a)).decode()
url=sh('git','remote','get-url','origin').strip()
cred=re.search(r'://([^:]+):([^@]+)@', url)
repo_m=re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)
def api(path, tries=6):
    for i in range(tries):
        try:
            req=urllib.request.Request('https://api.github.com'+path,
                headers={'Authorization':'token '+token,'Accept':'application/vnd.github+json','User-Agent':'x'})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except Exception as e:
            print('   retry',i,type(e).__name__); time.sleep(3)
    return None
# 1. 顶层 tree
top=api('/repos/%s/%s/git/trees/main'%(owner,repo))
data_sha=next(it['sha'] for it in top['tree'] if it['path']=='data')
# 2. data/tree
dt=api('/repos/%s/%s/git/trees/%s'%(owner,repo,data_sha))
mt_sha=next(it['sha'] for it in dt['tree'] if it['path']=='modern-translation')
# 3. modern-translation/tree
mt=api('/repos/%s/%s/git/trees/%s'%(owner,repo,mt_sha))
online=sorted(it['path'][:-5] for it in mt['tree'] if it['path'].endswith('.json'))
local=sorted(f[:-5] for f in os.listdir('data/modern-translation') if f.endswith('.json'))
print('truncated:', mt.get('truncated'))
print('本地文件数:', len(local), '| 线上文件数:', len(online))
print('本地有线上无:', sorted(set(local)-set(online)))
print('线上有本地无:', sorted(set(online)-set(local)))

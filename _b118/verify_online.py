import subprocess,re,json,urllib.request,time,os
url=subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
cred=re.search(r'://([^:]+):([^@]+)@',url); repo=re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$',url)
token=cred.group(2); owner=repo.group(1); name=repo.group(2)
def api(p,tries=4):
    for i in range(tries):
        try:
            req=urllib.request.Request('https://api.github.com'+p,headers={'Authorization':'token '+token,'User-Agent':'x','Accept':'application/vnd.github+json'})
            return json.loads(urllib.request.urlopen(req,timeout=90).read().decode())
        except Exception as e:
            print('retry',i,repr(e),flush=True); time.sleep(3)
    raise SystemExit('fetch failed')
info=api('/repos/%s/%s/branches/main'%(owner,name))
tree_sha=info['commit']['commit']['tree']['sha']
data=api('/repos/%s/%s/git/trees/%s?recursive=1'%(owner,name,tree_sha))
print('truncated',data.get('truncated'),flush=True)
paths=[t['path'] for t in data['tree'] if t['type']=='blob']
online=set(p for p in paths if p.startswith('data/modern-translation/'))
print('线上文件数',len(online),flush=True)
s=open('pages/sutras.html',encoding='utf-8').read()
m=re.search(r'BAIHUA_AVAILABLE\s*=\s*new Set\(\[(.*?)\]\)', s, re.S)
ids=[x.strip().strip('"\'') for x in m.group(1).split(',') if x.strip()]
missing=[t for t in ids if ('data/modern-translation/%s.json'%t) not in online]
print('清单',len(ids),'缺失',len(missing),missing[:20],flush=True)
local=set(f for f in os.listdir('data/modern-translation') if f.endswith('.json'))
listed=set(t+'.json' for t in ids)
print('本地未入清单',len(local-listed),sorted(local-listed)[:10],flush=True)
print('DONE',flush=True)

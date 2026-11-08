import subprocess,re,json,urllib.request,time,os
url=subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
cred=re.search(r'://([^:]+):([^@]+)@',url); repo=re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$',url)
token=cred.group(2); owner=repo.group(1); name=repo.group(2)
def api(p,tries=5):
    for i in range(tries):
        try:
            req=urllib.request.Request('https://api.github.com'+p,headers={'Authorization':'token '+token,'User-Agent':'x','Accept':'application/vnd.github+json'})
            raw=b''
            with urllib.request.urlopen(req,timeout=90) as r:
                while True:
                    b=r.read(65536)
                    if not b: break
                    raw+=b
            return json.loads(raw.decode())
        except Exception as e:
            print('retry',p,i,repr(e),flush=True); time.sleep(2)
    raise SystemExit('fail '+p)
info=api('/repos/%s/%s/branches/main'%(owner,name))
root=info['commit']['commit']['tree']['sha']
top=api('/repos/%s/%s/git/trees/%s'%(owner,name,root))
data_sha=[t['sha'] for t in top['tree'] if t['path']=='data'][0]
data=api('/repos/%s/%s/git/trees/%s'%(owner,name,data_sha))
mt_sha=[t['sha'] for t in data['tree'] if t['path']=='modern-translation'][0]
mt=api('/repos/%s/%s/git/trees/%s'%(owner,name,mt_sha))
print('truncated',mt.get('truncated'),flush=True)
online=set('data/modern-translation/'+t['path'] for t in mt['tree'] if t['type']=='blob')
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

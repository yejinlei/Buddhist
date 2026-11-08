import json, re, subprocess, urllib.request, time
url=subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
cred=re.search(r'://([^:]+):([^@]+)@',url); repo_m=re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$',url)
token,owner,repo=cred.group(2),repo_m.group(1),repo_m.group(2)
def api(path):
    for _ in range(5):
        try:
            req=urllib.request.Request('https://api.github.com'+path,headers={'Authorization':'token '+token,'Accept':'application/vnd.github+json','User-Agent':'x'})
            with urllib.request.urlopen(req,timeout=60) as r: return json.loads(r.read().decode())
        except Exception as e:
            time.sleep(2)
    raise SystemExit('api fail '+path)
s=open('pages/sutras.html',encoding='utf-8').read()
m=re.search(r'BAIHUA_AVAILABLE = new Set\(\[(.*?)\]\)',s)
ids=[x.strip().strip("'") for x in m.group(1).split(',') if x.strip()]
idset=set(ids)
ref=api('/repos/%s/%s/git/ref/heads/main'%(owner,repo)); sha=ref['object']['sha']
tree=api('/repos/%s/%s/git/trees/%s?recursive=1'%(owner,repo,sha))
print('truncated',tree.get('truncated'))
online={e['path']:e['sha'] for e in tree['tree']}
online_files=set(p for p in online if p.startswith('data/modern-translation/') and p.endswith('.json'))
online_ids=set(p.split('/')[-1][:-5] for p in online_files)
missing=[i for i in ids if ('data/modern-translation/%s.json'%i) not in online]
print('清单条数',len(ids),'线上译文件数',len(online_files))
print('清单缺失线上(',len(missing),'):',missing[:20])
extra=[i for i in sorted(online_ids) if i not in idset]
print('线上多余(',len(extra),'):',extra[:30])
files=['data/modern-translation/t0633.json','data/modern-translation/t0641.json','data/modern-translation/t0744.json','data/modern-translation/t1490.json','data/modern-translation/t1588.json','pages/sutras.html','data/baihua-audit.json']
ok=0
for f in files:
    local=subprocess.check_output(['git','hash-object',f]).decode().strip()
    rem=online.get(f)
    if local==rem: ok+=1
    print(('OK' if local==rem else 'DIFF'),f,local[:10],(rem or 'NA')[:10])
print('hash一致',ok,'/',len(files))

import subprocess,json,urllib.request,re,time
url=subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
m=re.search(r'://([^:]+):([^@]+)@github.com/(.+?)\.git',url); tok=m.group(2); repo=m.group(3)
def get(u,tries=8):
    for _ in range(tries):
        try:
            req=urllib.request.Request(u,headers={'Authorization':'token '+tok,'User-Agent':'x','Accept':'application/vnd.github+json'})
            with urllib.request.urlopen(req,timeout=25) as r: return json.load(r)
        except Exception: time.sleep(2)
    raise SystemExit('net fail')
br=get('https://api.github.com/repos/%s/branches/main'%repo)['commit']['sha']
tree=get('https://api.github.com/repos/%s/git/trees/%s:data/modern-translation'%(repo,br))
remote={x['path']:x['sha'] for x in tree['tree']}
ids='t1040 t1084 t1226 t1240 t1740 t2019b t2094 t2141a t2143 t2164 t2166 t2169 t2171 t2175 t2756 t2830 t2840 t2845 t2853 t2862 t2864 t2872 t2918'.split()
bad=[]
for i in ids:
    p='data/modern-translation/%s.json'%i
    loc=subprocess.check_output(['git','hash-object',p]).decode().strip()
    if remote.get('%s.json'%i)!=loc: bad.append(i)
print('比对 %d 部，线上↔本地不一致: %s'%(len(ids), bad if bad else '无'))

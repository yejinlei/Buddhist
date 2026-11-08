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
def tree(path):
    t=get('https://api.github.com/repos/%s/git/trees/%s%s'%(repo,br,path))
    return {x['path']:x['sha'] for x in t['tree']}
rem_tr=tree(':data/modern-translation')
trs='t1151 t1173 t1187 t1188 t1189 t1234 t1242 t1245 t1260 t1276'.split()
bad=[]
for i in trs:
    p='data/modern-translation/%s.json'%i
    if rem_tr.get('%s.json'%i)!=subprocess.check_output(['git','hash-object',p]).decode().strip(): bad.append('tr/'+i)
rem_pages=tree(':pages')
if rem_pages.get('sutras.html')!=subprocess.check_output(['git','hash-object','pages/sutras.html']).decode().strip(): bad.append('pages/sutras.html')
print('比对 %d 文件，不一致: %s'%(len(trs)+1, bad if bad else '无'))

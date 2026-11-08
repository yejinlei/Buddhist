import subprocess,json,urllib.request,re,time
url=subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
m=re.search(r'://([^:]+):([^@]+)@github.com/(.+?)\.git',url); tok=m.group(2); repo=m.group(3)
def get(u,tries=8):
    for _ in range(tries):
        try:
            req=urllib.request.Request(u,headers={'Authorization':'token '+tok,'User-Agent':'x','Accept':'application/vnd.github+json'})
            with urllib.request.urlopen(req,timeout=25) as r: return json.load(r)
        except Exception:
            time.sleep(2)
    raise SystemExit('net fail '+u)
br=get('https://api.github.com/repos/%s/branches/main'%repo)['commit']['sha']
tree=get('https://api.github.com/repos/%s/git/trees/%s:data/modern-translation'%(repo,br))
online=set(x['path'] for x in tree['tree'])
html=subprocess.check_output(['git','show','HEAD:pages/sutras.html']).decode()
raw=re.search(r'const BAIHUA_AVAILABLE = new Set\(\[(.*?)\]\)',html,re.S).group(1)
lst=set(x.strip().strip("'") for x in raw.split(','))
missing=[t for t in sorted(lst) if (t+'.json') not in online]
print('清单条数:',len(lst),' 线上译文文件数:',len(online),' 线上缺失:',len(missing))
print('缺失:',missing[:30])

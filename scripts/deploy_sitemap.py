#!/usr/bin/env python3
# 轻量部署：只推 ontology.html、js/site-map.js、js/ontology-tbox-viz.js
import os,sys,json,base64,urllib.request,urllib.error
sys.path.insert(0,'scripts')

REPO='yejinlei/Buddhist'
BRANCH='main'
TOKEN=os.environ.get('GITHUB_TOKEN','')
if not TOKEN:
    # 从 git config 读取
    import subprocess
    try:
        url=subprocess.check_output(['git','config','remote.origin.url'],stderr=subprocess.DEVNULL).decode().strip()
        m=__import__('re').match(r'https://[^:]+:([^@]+)@github',url)
        if m: TOKEN=m.group(1)
    except Exception: pass
if not TOKEN:
    for f in ['scripts/.gh_token','.gh_token']:
        if os.path.exists(f): TOKEN=open(f).read().strip(); break
if not TOKEN:
    print('NO TOKEN'); sys.exit(1)

FILES=[
    ('pages/ontology.html','text/html; charset=utf-8'),
    ('js/site-map.js','application/javascript; charset=utf-8'),
    ('js/ontology-tbox-viz.js','application/javascript; charset=utf-8'),
    ('data/dict_index.json','application/json; charset=utf-8'),
    ('ontology/instances/relations.json','application/json; charset=utf-8'),
]

def api(path,data=None,method=None):
    url='https://api.github.com'+path
    req=urllib.request.Request(url,headers={
        'Authorization':'token '+TOKEN,
        'Accept':'application/vnd.github+json',
        'User-Agent':'sitemap-deploy'
    })
    if data is not None:
        req.data=json.dumps(data).encode('utf-8')
        req.add_header('Content-Type','application/json')
    if method: req.method=method
    import time
    last=None
    for i in range(3):
        try:
            with urllib.request.urlopen(req,timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return {'_error':e.code,'_body':e.read().decode('utf-8','ignore')}
        except Exception as e:
            last=e; time.sleep(2*(i+1))
    return {'_error':-1,'_body':str(last)}

def put(path,content,msg):
    sha=None
    g=api('/repos/'+REPO+'/contents/'+path+'?ref='+BRANCH)
    if '_error' not in g: sha=g.get('sha')
    import base64
    b=base64.b64encode(open(content,'rb').read()).decode('ascii')
    payload={'message':msg,'content':b,'branch':BRANCH}
    if sha: payload['sha']=sha
    r=api('/repos/'+REPO+'/contents/'+path,payload,method='PUT')
    if '_error' in r:
        print('FAIL',path,r['_error'],r['_body'][:200])
        return False
    print('OK',path,r.get('content',{}).get('sha','')[:8])
    return True

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
for fp,ct in FILES:
    put(fp,fp,'站点地图：四轴×七层坐标式导航 + 本体类节点跳转对应页面')
print('DONE')

# -*- coding: utf-8 -*-
import base64, json, os, re, subprocess, sys
root=subprocess.check_output(['git','rev-parse','--show-toplevel']).decode().strip()
os.chdir(root)
url=subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
m=re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$',url)
owner,repo=m.group(1),m.group(2)
t=re.search(r'://([^:@]+):([^@]+)@',url) or re.search(r'://([^@]+)@',url)
token=t.group(2) if t.lastindex==2 else t.group(1)
def curl(args):
    p=subprocess.run(['curl','-s','-w','\n%{http_code}']+args,capture_output=True,text=True)
    return p.stdout
ok=fail=0
for fp in sys.argv[1:]:
    content=open(fp,'rb').read()
    b64=base64.b64encode(content).decode()
    ep=f'https://api.github.com/repos/{owner}/{repo}/contents/{fp}?ref=main'
    r=curl(['-H',f'Authorization: token {token}','-H','Accept: application/vnd.github+json',ep])
    body,code=r.rsplit('\n',1)
    cur_sha=None
    try: cur_sha=json.loads(body).get('sha')
    except Exception: pass
    data={'message':f'deploy: {fp}','content':b64,'branch':'main'}
    if cur_sha: data['sha']=cur_sha
    open('/tmp/payload.json','w').write(json.dumps(data))
    r2=curl(['-X','PUT','-H',f'Authorization: token {token}','-H','Accept: application/vnd.github+json','-H','Content-Type: application/json','--data-binary','@/tmp/payload.json',f'https://api.github.com/repos/{owner}/{repo}/contents/{fp}'])
    b2,c2=r2.rsplit('\n',1)
    if c2 in ('200','201'):
        print(f'OK  {fp} ({len(content)} bytes)'); ok+=1
    else:
        print(f'FAIL {fp} status={c2}: {str(b2)[:200]}'); fail+=1
print(f'\n完成: 成功 {ok} 失败 {fail}')

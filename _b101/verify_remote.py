# -*- coding: utf-8 -*-
import base64, hashlib, json, os, re, subprocess, sys
url=subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
m=re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$',url)
owner,repo=m.group(1),m.group(2)
t=re.search(r'://([^:@]+):([^@]+)@',url) or re.search(r'://([^@]+)@',url)
token=t.group(2) if t.lastindex==2 else t.group(1)
for fp in sys.argv[1:]:
    local=hashlib.sha256(open(fp,'rb').read()).hexdigest()
    ep=f'https://api.github.com/repos/{owner}/{repo}/contents/{fp}?ref=main'
    r=subprocess.run(['curl','-s','-H',f'Authorization: token {token}','-H','Accept: application/vnd.github+json',ep],capture_output=True,text=True).stdout
    try:
        d=json.loads(r); rem=hashlib.sha256(base64.b64decode(d['content'].replace('\n',''))).hexdigest()
    except Exception as e:
        rem='ERR:'+str(e)[:60]
    print(('一致' if local==rem else '不一致'), fp, '| local',local[:12],'remote',rem[:12])

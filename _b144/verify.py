import base64, json, re, subprocess, urllib.request, hashlib
url = subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
cred = re.search(r'://([^:]+):([^@]+)@', url)
repo_m = re.search(r'github\.com[/:]([^/]+)/([^/.]+?)(?:\.git)?$', url)
token, owner, repo = cred.group(2), repo_m.group(1), repo_m.group(2)

def get(path):
    req = urllib.request.Request('https://api.github.com/repos/%s/%s/contents/%s?ref=main'%(owner,repo,path),
        headers={'Authorization':'token '+token,'Accept':'application/vnd.github+json','User-Agent':'v'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))

for p in ['data/modern-translation/t2007.json','pages/sutras.html','data/baihua-audit.json']:
    try:
        d = get(p)
        content = base64.b64decode(d['content'])
        local = open(p,'rb').read()
        print(p, 'sha_len', len(content), 'md5线上', hashlib.md5(content).hexdigest()[:12], '本地', hashlib.md5(local).hexdigest()[:12], '一致', content==local)
    except Exception as e:
        print(p, 'ERR', e)
# 清单是否含 t2007
try:
    d = get('pages/sutras.html')
    s = base64.b64decode(d['content']).decode('utf-8')
    m = re.search(r'BAIHUA_AVAILABLE = new Set\(\[(.*?)\]\);', s, re.S)
    ids = re.findall(r"'([^']+)'", m.group(1))
    print('线上清单部数', len(ids), '含t2007', 't2007' in ids)
except Exception as e:
    print('清单校验 ERR', e)

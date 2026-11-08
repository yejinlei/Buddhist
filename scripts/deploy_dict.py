#!/usr/bin/env python3
"""精简单文件部署：只传本次词典打通新增/修改的关键文件，绕过大文件"""
import base64, json, os, subprocess, sys, urllib.request, urllib.error, time, re

API = 'https://api.github.com'
ROOT = subprocess.check_output(['git','rev-parse','--show-toplevel']).decode().strip()
os.chdir(ROOT)
url = subprocess.check_output(['git','remote','get-url','origin']).decode().strip()
m = re.search(r'://[^:]+:([^@]+)@github\.com/([^/]+)/([^/.]+)', url)
if not m: sys.exit('无法解析 remote')
TOKEN, OWNER, REPO = m.group(1), m.group(2), m.group(3)
HEADERS = {'Authorization':'token '+TOKEN,'Accept':'application/vnd.github+json','User-Agent':'bd'}

def gh(path, method='GET', data=None):
    req = urllib.request.Request(API+path, method=method,
        data=json.dumps(data).encode() if data else None, headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.status, json.loads(r.read().decode() or '{}')
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode('utf-8','replace')[:300]
        except Exception as e:
            if attempt==2: return 0, str(e)
            time.sleep(2)

# 本次必须上传的文件（新增+修改的关键文件）
FILES = [
    # 新生成的映射/补丁/缺口文件
    'ontology/dict-links.json',
    'ontology/dict-alias-patch.json',
    'ontology/dict-expansion-candidates.json',
    # 被补丁更新过的实例文件（别名/同义关系）
    'ontology/instances/relations.json',
    # 修改过的页面
    'pages/dict.html',
    'pages/graph.html',
]
# 再追加 87 个被补丁改过的实例文件
import glob
for pat in ['ontology/instances/persons/p*.json','ontology/instances/concepts/c*.json','ontology/instances/sutras/s*.json']:
    # 用 git diff 看哪些改过，或者直接挑有 dict_alias_sources 标记的
    for f in glob.glob(pat):
        try:
            content = open(f, encoding='utf-8').read()
            if 'dict_alias_sources' in content:
                FILES.append(f)
        except: pass
FILES = sorted(set(FILES))
print(f'准备上传 {len(FILES)} 个文件')

# 取最新 main 分支 SHA
st, branch = gh(f'/repos/{OWNER}/{REPO}/git/refs/heads/main')
if st != 200:
    sys.exit(f'获取分支失败: {branch}')
base_sha = branch['object']['sha']
print(f'最新 main commit: {base_sha[:10]}')

# 取 base tree
st, base_tree = gh(f'/repos/{OWNER}/{REPO}/git/commits/{base_sha}')
if st != 200: sys.exit(f'获取commit失败: {base_tree}')
base_tree_sha = base_tree['tree']['sha']

# 创建 blob
blobs = []
ok = 0; fail = 0
for fp in FILES:
    if not os.path.exists(fp):
        print(f'  SKIP {fp} (不存在)'); continue
    content = open(fp,'rb').read()
    b64 = base64.b64encode(content).decode()
    st, res = gh(f'/repos/{OWNER}/{REPO}/git/blobs', 'POST', {'content':b64,'encoding':'base64'})
    if st == 201:
        mode = '100755' if fp.endswith('.py') else '100644'
        blobs.append({'path':fp,'mode':mode,'type':'blob','sha':res['sha']})
        ok += 1
        print(f'  blob OK {fp} ({len(content)/1024:.1f} KB)')
    else:
        fail += 1
        print(f'  blob FAIL {fp}: {st} {str(res)[:100]}')

print(f'\nblob 完成: {ok} OK, {fail} FAIL')

# 创建 tree
st, new_tree = gh(f'/repos/{OWNER}/{REPO}/git/trees', 'POST',
    {'base_tree':base_tree_sha, 'tree':blobs})
if st != 201:
    sys.exit(f'创建 tree 失败: {st} {new_tree}')
print(f'tree 创建: {new_tree["sha"][:10]}')

# 创建 commit
st, new_commit = gh(f'/repos/{OWNER}/{REPO}/git/commits', 'POST',
    {'message':'词典↔本体打通：术语对齐/参见别名/双向跳转/释义卡/缺口清单',
     'tree':new_tree['sha'], 'parents':[base_sha]})
if st != 201:
    sys.exit(f'创建 commit 失败: {st} {new_commit}')
print(f'commit 创建: {new_commit["sha"][:10]}')

# 更新 ref
st, upd = gh(f'/repos/{OWNER}/{REPO}/git/refs/heads/main', 'PATCH',
    {'sha':new_commit['sha'], 'force':False})
if st == 200:
    print(f'\n✅ 部署完成 → {new_commit["sha"][:10]}')
else:
    print(f'更新 ref 失败: {st} {upd}')

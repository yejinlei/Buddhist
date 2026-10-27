#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建 CBETA T 藏经目清单（逐册列举，带凭据）"""
import urllib.request, json, os, time
TOKEN = os.environ.get('GITHUB_TOKEN', '')
API = 'https://api.github.com/repos/cbeta-org/xml-p5/contents'

def get(url):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Authorization': f'Bearer {TOKEN}'})
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e:
            if i == 3: raise
            time.sleep(3)

vols = [x['name'] for x in get(API + '/T?ref=master') if x['type'] == 'dir']
man = {}
for v in vols:
    try:
        man[v] = [x['name'] for x in get(f'{API}/T/{v}?ref=master') if x['name'].endswith('.xml')]
        print(f'{v}: {len(man[v])} 部', flush=True)
    except Exception as e:
        print(f'{v}: 失败 {e}', flush=True)
json.dump(man, open('/tmp/manifest_T.json', 'w'), ensure_ascii=False)
print(f'完成 册数={len(man)} 经数={sum(len(v) for v in man.values())}', flush=True)

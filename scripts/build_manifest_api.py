#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用 GitHub API 递归获取xml-p5仓库T目录下所有xml文件路径"""
import json, urllib.request, time, sys

OUT = '/tmp/manifest_T_full.json'
OWNER = 'cbeta-org'
REPO = 'xml-p5'
BRANCH = 'master'
TOKEN = ''  # 无token也可访问，60次/小时；用token 5000次/小时

def api(url):
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github+json'}
    if TOKEN: headers['Authorization'] = f'Bearer {TOKEN}'
    req = urllib.request.Request(url, headers=headers)
    # 用递归tree一次拿全
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode())

def main():
    print('获取仓库递归tree...', flush=True)
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1'
    d = api(url)
    items = d.get('tree', [])
    print(f'总条目 {len(items)}', flush=True)
    manifest = {}
    for it in items:
        p = it.get('path', '')
        if not p.endswith('.xml'): continue
        # 只取 T/ 目录
        if not p.startswith('T/'): continue
        parts = p.split('/')
        if len(parts) < 3: continue
        vol = parts[1]
        fname = parts[2]
        manifest.setdefault(vol, []).append(fname)
    for vol in manifest:
        manifest[vol] = sorted(set(manifest[vol]))
    total = sum(len(v) for v in manifest.values())
    print(f'共 {len(manifest)} 册 {total} 部 XML，写入 {OUT}', flush=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    for vol in sorted(manifest.keys())[:10]:
        print(f'  {vol}: {len(manifest[vol])} 部  例：{manifest[vol][:2]}')

if __name__ == '__main__':
    main()

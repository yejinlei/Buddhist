#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按册获取CBETA T目录下所有xml文件列表"""
import json, urllib.request, time

OUT = '/tmp/manifest_T_full.json'
OWNER, REPO, BRANCH = 'cbeta-org', 'xml-p5', 'master'
VOLS = [f'T{i:02d}' for i in range(1, 56)] + ['T85']

def api(url, retry=3):
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/vnd.github+json'
            })
            return json.loads(urllib.request.urlopen(req, timeout=90).read().decode())
        except Exception as e:
            if i == retry - 1: raise
            time.sleep(3)

def list_dir(path):
    """调用contents API列目录下所有xml文件"""
    d = api(f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}')
    files = []
    for it in d:
        if it['type'] == 'file' and it['name'].endswith('.xml'):
            files.append(it['name'])
    return sorted(files)

def main():
    manifest = {}
    for vol in VOLS:
        path = f'T/{vol}'
        try:
            fs = list_dir(path)
            manifest[vol] = fs
            print(f'{vol}: {len(fs)} 部', flush=True)
        except Exception as e:
            print(f'{vol} 失败: {e}', flush=True)
            manifest[vol] = []
        time.sleep(0.3)
    total = sum(len(v) for v in manifest.values())
    print(f'\n总计 {len(manifest)} 册 {total} 部，写入 {OUT}', flush=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()

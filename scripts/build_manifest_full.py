#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成大正藏56册每册的XML文件清单（通过jsdelivr列目录）"""
import json, re, urllib.request, time

OUT = '/tmp/manifest_T_full.json'
CDN_LIST = 'https://cdn.jsdelivr.net/gh/cbeta-org/xml-p5@master/T/{vol}/'
VOLS = [f'T{i:02d}' for i in range(1, 56)] + ['T85']

def http(url, timeout=60):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', 'ignore')

def list_files(vol):
    """解析cdn.jsdelivr.net目录页面，提取所有.xml文件名"""
    try:
        html = http(CDN_LIST.format(vol=vol))
    except Exception as e:
        print(f'{vol} 列表失败: {e}')
        return []
    # 匹配 href="Txx/Txx/Txxnxxxx.xml" 形式
    pat = re.compile(r'href="/cbeta-org/xml-p5@master/' + vol + r'/([^"?]+\.xml)"')
    files = pat.findall(html)
    return sorted(set(files))

def main():
    manifest = {}
    for vol in VOLS:
        names = list_files(vol)
        manifest[vol] = names
        print(f'{vol}: {len(names)} 部', flush=True)
        time.sleep(1)
    total = sum(len(v) for v in manifest.values())
    print(f'\n总计 {total} 部，写入 {OUT}')
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()

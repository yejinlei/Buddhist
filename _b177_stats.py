import json, os, re

batch = [
    ("t0818", "大莊嚴法門經"),
    ("t1278", "迦樓羅及諸天密言經"),
    ("t1185b", "文殊師利寶藏陀羅尼經"),
    ("t1154", "佛說隨求即得大自在陀羅尼神呪經"),
    ("t0339", "得無垢女經"),
    ("t1659", "發菩提心經論"),
    ("t0327", "發覺淨心經"),
    ("t0843", "佛說大乘不思議神通境界經"),
    ("t2818", "大乘二十二問本"),
    ("t1737", "大華嚴經略策"),
    ("t0652", "佛說大乘隨轉宣說諸法經"),
    ("t0405", "虛空藏菩薩經"),
]

def norm(s): return re.sub(r'\s+', '', s)

ROOT = '/home/user/workspace/13511660557912876654/buddhist-ontology'
total_seg = 0
total_orig = 0
total_modern = 0
rows = []
for tid, title in batch:
    tr = json.load(open(os.path.join(ROOT, 'data/modern-translation', tid+'.json'), encoding='utf-8'))
    sut = json.load(open(os.path.join(ROOT, 'sutras', tid+'.json'), encoding='utf-8'))
    orig_text = norm('\n'.join(c['text'] for c in sut.get('content', [])))
    modern_text = norm(''.join(s.get('modern','') for s in tr['translations']))
    n = len(tr['translations'])
    translator = tr.get('translator', '') or sut.get('translator', '')
    total_seg += n
    total_orig += len(orig_text)
    total_modern += len(modern_text)
    rows.append((tid, title, translator, n, len(orig_text)))
    print(f"{tid}\t{title}\t{translator}\t{n}段\t原文{len(orig_text)}字")

print(f"\n总计: {total_seg}段, 原文{total_orig}字, 白话{total_modern}字")

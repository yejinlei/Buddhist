import json, os, re

SUTRAS_DIR = "sutras"
META_PATH = ".xmlcache/meta_cache.json"

with open(META_PATH, 'r', encoding='utf-8') as f:
    meta_raw = json.load(f)
meta_map = {k.lower(): v for k, v in meta_raw.items()}

fixed = 0
for fname in os.listdir(SUTRAS_DIR):
    if not re.match(r'^t\d{4}\.json$', fname):
        continue
    sid = fname.replace('.json', '')
    fpath = os.path.join(SUTRAS_DIR, fname)
    
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    meta = meta_map.get(sid)
    if not meta:
        continue
    
    current = data.get('translator', '')
    if current in ['失译', '佚名', '', '失譯', '不详'] or len(current) < 2:
        byline = meta.get('byline', '')
        creators = meta.get('creators', '')
        dynasty = meta.get('time_dynasty', '')
        
        if byline:
            data['translator'] = byline.replace('譯', '译')
        elif creators:
            data['translator'] = f"{dynasty} {creators}译" if dynasty else f"{creators}译"
        else:
            continue
            
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        fixed += 1

print(f"修复译者字段：{fixed}部")

# 重建索引
index = []
for fname in sorted(os.listdir(SUTRAS_DIR)):
    if not re.match(r'^t\d{4}\.json$', fname):
        continue
    with open(os.path.join(SUTRAS_DIR, fname), 'r', encoding='utf-8') as f:
        d = json.load(f)
    index.append({
        'id': d.get('id'),
        'title': d.get('title'),
        'translator': d.get('translator', '失译'),
        'vol': d.get('vol', ''),
        'category': d.get('category', '未分类'),
        'juan_count': d.get('juan_count', len(d.get('chapters', []))),
        'chapters': len(d.get('chapters', [])),
        'actual_char_count': d.get('actual_char_count', 0),
        'official_char_count': d.get('official_char_count', 0),
        'completeness_ratio': d.get('completeness_ratio', 0),
        'time_from': d.get('time_from', '')
    })

with open(os.path.join(SUTRAS_DIR, 'index.json'), 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
print("索引重建完成")

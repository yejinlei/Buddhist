import json, os, re
from collections import defaultdict

SUTRAS_DIR = "sutras"
META_PATH = ".xmlcache/meta_cache.json"
REPORT_PATH = "clean_report.md"

# 1. 加载官方元数据（字典格式：key=经号）
print("加载官方经目元数据...")
with open(META_PATH, 'r', encoding='utf-8') as f:
    meta_raw = json.load(f)
meta_map = {}
for sid, item in meta_raw.items():
    sid = sid.lower()
    meta_map[sid] = item
print(f"官方经目共 {len(meta_map)} 条")

# 2. 遍历所有经文JSON
stats = defaultdict(int)
abnormal = []
filled = 0
total = 0
cat_count = defaultdict(int)

for fname in os.listdir(SUTRAS_DIR):
    if not re.match(r'^t\d{4}\.json$', fname):
        continue
    sutra_id = fname.replace('.json', '')
    fpath = os.path.join(SUTRAS_DIR, fname)
    total += 1
    
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    meta = meta_map.get(sutra_id)
    if not meta:
        stats['no_meta'] += 1
        continue
    
    # 回填字段
    changed = False
    # 册号
    if not data.get('vol'):
        vol = meta.get('vol', '')
        if vol:
            data['vol'] = vol.upper()
            changed = True
            stats['vol_filled'] += 1
    # 部类
    if not data.get('category'):
        cat = meta.get('category', '').replace('類', '类')
        if cat:
            data['category'] = cat
            changed = True
            stats['category_filled'] += 1
    # 译者
    if not data.get('translator') or data.get('translator') in ['失译', '佚名', '', '失譯']:
        translator = meta.get('creators', '')
        if translator and translator not in ['失譯', '失译', '佚名']:
            dynasty = meta.get('time_dynasty', '')
            if dynasty:
                translator = f"{dynasty} {translator}译"
            data['translator'] = translator
            changed = True
            stats['translator_filled'] += 1
    # 译出时间
    if not data.get('time_from'):
        tf = meta.get('time_from')
        if tf:
            data['time_from'] = tf
            changed = True
    # 译地
    places = meta.get('places', [])
    if places and not data.get('translation_place'):
        data['translation_place'] = places[0]['name']
        changed = True
    # 官方字数
    official_count = meta.get('cjk_chars', 0)
    if official_count:
        data['official_char_count'] = int(official_count)
        changed = True
    # 实际字数
    actual_count = sum(len(ch.get('content', '')) for ch in data.get('chapters', []))
    data['actual_char_count'] = actual_count
    # 完整性校验
    if official_count and actual_count > 0:
        ratio = actual_count / official_count
        data['completeness_ratio'] = round(ratio, 2)
        if ratio < 0.5:
            abnormal.append({
                'id': sutra_id,
                'title': data.get('title', ''),
                'vol': data.get('vol', ''),
                'category': data.get('category', ''),
                'official': official_count,
                'actual': actual_count,
                'ratio': round(ratio, 2)
            })
            stats['abnormal'] += 1
    # 卷数
    if not data.get('juan_count'):
        juan = meta.get('juan', 0)
        if juan:
            data['juan_count'] = int(juan)
            changed = True
    
    # 统计部类
    cat = data.get('category', '未分类')
    cat_count[cat] += 1
    
    if changed:
        filled += 1
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# 重建索引
print("重建经文库索引...")
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

# 生成报告
report = f"""# 佛学本体论数据清洗报告（第一阶段：元数据回填）

## 总体统计
- 总经文数：{total} 部
- 元数据匹配成功：{filled} 部
- 无元数据匹配（主要是拾遗、古逸部）：{stats['no_meta']} 部
- ✅ 回填册号（vol）：{stats['vol_filled']} 部
- ✅ 回填部类（category）：{stats['category_filled']} 部
- ✅ 回填译者/朝代（translator）：{stats['translator_filled']} 部
- ⚠️ 内容异常（解析字数<官方字数50%，待重新解析）：{stats['abnormal']} 部

## 部类分布
"""
for cat, cnt in sorted(cat_count.items(), key=lambda x: -x[1]):
    report += f"- {cat}：{cnt}部\n"

report += "\n## 内容异常清单（待修复）\n"
report += "| 经号 | 经名 | 册号 | 部类 | 官方字数 | 实际字数 | 完整度 |\n"
report += "|---|---|---|---|---|---|---|\n"
for a in sorted(abnormal, key=lambda x: x['ratio']):
    report += f"| {a['id']} | {a['title']} | {a['vol']} | {a['category']} | {a['official']} | {a['actual']} | {a['ratio']*100:.0f}% |\n"

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✅ 清洗完成！共处理{total}部，回填{filled}部元数据，发现{stats['abnormal']}部内容异常")
print(f"报告已写入{REPORT_PATH}")

import json, re, os

def replace_in_sutra(sid, replacements, check_unique=False):
    """在指定经所有modern中替换，不改动preview"""
    path = f'data/modern-translation/{sid}.json'
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    total = 0
    for old, new in replacements:
        cnt = 0
        for seg in d['translations']:
            m = seg.get('modern', '')
            if old in m:
                if check_unique:
                    assert m.count(old) == 1, f"'{old}'出现多次"
                seg['modern'] = m.replace(old, new)
                cnt += 1
        total += cnt
    # 批量处理双【义解】标签：只保留第一个【义解】，删除其余
    for seg in d['translations']:
        m = seg.get('modern', '')
        first_idx = m.find('【义解】')
        if first_idx != -1:
            rest = m[first_idx+4:]
            rest = rest.replace('【义解】', '')
            seg['modern'] = m[:first_idx+4] + rest
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"修复完成：{sid}，替换{total}处")

# ==================== t2139 繁简修复 ====================
replace_in_sutra('t2139', [
    ('髮', '发'),  # 所有繁体"髮"转简体
])

# ==================== t1961 引号修复 ====================
replace_in_sutra('t1961', [
    ('何必求生西方净土呢？’', '何必求生西方净土呢？”'),
])
with open('data/modern-translation/t1961.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
seg28 = d['translations'][28]['modern']
seg28 = seg28.replace('回答说：‘', '回答说：“')
if not seg28.rstrip().endswith('”'):
    seg28 = seg28.rstrip() + '”'
d['translations'][28]['modern'] = seg28
# 清理双义解
first_idx = seg28.find('【义解】')
if first_idx != -1:
    rest = seg28[first_idx+4:].replace('【义解】', '')
    d['translations'][28]['modern'] = seg28[:first_idx+4] + rest
with open('data/modern-translation/t1961.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("修复完成：t1961")

# ==================== t2101 修复 ====================
with open('data/baihua-tasks/t2101.json', 'r', encoding='utf-8') as f:
    skel = json.load(f)
orig_dharani = skel['translations'][15]['original_preview'].strip()
replace_in_sutra('t2101', [
    ('唵嘛呢叭𠺗吽', orig_dharani + '（即通行“唵嘛呢叭咪吽”）'),
    ('安奉在现在丞相公所建的。', '安奉在现在丞相公所建'),
])

# ==================== t1897 修复 ====================
replace_in_sutra('t1897', [
    ('always', '常常'),
    ('铁钾地狱', '铁甲地狱'),
])

# ==================== t1951 修复 ====================
replace_in_sutra('t1951', [
    ('文殊、普贤、观音等菩萨像', '文殊、普贤、观世音等菩萨像'),
])

# ==================== t2019a 修复 ====================
replace_in_sutra('t2019a', [
    ('永明寿禅师', '永明延寿禅师'),
])

# ==================== t1103a 修复 ====================
replace_in_sutra('t1103a', [
    ('漏十万遍', '满十万遍'),
    ('大母指', '大拇指'),
    ('慕入佛道', '归入佛道'),
    ('曼茶罗', '曼荼罗'),
    ('弟婆', '提婆'),
    ('竪', '竖'),
])

# ==================== t1867 修复 ====================
replace_in_sutra('t1867', [
    ('曼茶罗', '曼荼罗'),
])

# ==================== t2005 修复 ====================
with open('data/modern-translation/t2005.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
seg0 = d['translations'][0]['modern']
seg0 = seg0.rstrip('，。') + '。'
d['translations'][0]['modern'] = seg0
with open('data/modern-translation/t2005.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
replace_in_sutra('t2005', [])  # 仅清理双义解

# ==================== jingang_jiumo t1632 仅清理双义解（如果有）====================
for sid in ['jingang_jiumo', 't1632']:
    replace_in_sutra(sid, [])

print("===== 所有校对问题修复完成 =====")


import json, re
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'
files = ['t1058','t0716','t1434','t1243','t1904','t2069','t1069','t1080','t1633','t1959','t0150a','t0199']

print("=== 半角标点抽查 ===")
for f in files:
    data = json.load(open(base+f+'.json'))
    for i, seg in enumerate(data['translations']):
        m = seg.get('modern','')
        if not m: continue
        # 半角,.!? 在中文之间
        for pm in re.finditer(r'[\u4e00-\u9fff][,.!?][\u4e00-\u9fff]', m):
            print(f'  {f} seg{i+1}: 半角标点: ...{m[max(0,pm.start()-3):pm.end()+3]}...')
        # 半角引号在中文之间
        for pm in re.finditer(r'[\u4e00-\u9fff][\"\'][\u4e00-\u9fff]', m):
            print(f'  {f} seg{i+1}: 半角引号: ...{m[max(0,pm.start()-3):pm.end()+3]}...')

# 双【义解】
print()
print("=== 双【义解】检查 ===")
for f in files:
    data = json.load(open(base+f+'.json'))
    for i, seg in enumerate(data['translations']):
        m = seg.get('modern','')
        if m.count('【义解】') > 1:
            print(f'  {f} seg{i+1}: 出现{m.count("【义解】")}次【义解】')

# 末段modern是否覆盖原文内容（对比长度）
print()
print("=== 末段覆盖情况核查 ===")
for f in files:
    data = json.load(open(base+f+'.json'))
    last = data['translations'][-1]
    o = last['original_preview']
    m = last.get('modern','')
    ratio = len(m)/max(1,len(o))
    if ratio < 0.3:
        print(f'  {f}: 末段modern长度{len(m)}/原文{len(o)}={ratio:.2f}，可能未覆盖')

# 检查modern截断：末尾不是完整句
print()
print("=== modern末尾截断检查（不以。/」/）等结尾的非空段）===")
for f in files:
    data = json.load(open(base+f+'.json'))
    for i, seg in enumerate(data['translations']):
        m = seg.get('modern','')
        if not m: continue
        tail = m.rstrip()
        if tail and tail[-1] not in '。」）"”':
            # 允许末尾是汉字（部分梵字结尾）
            if not ('\u4e00' <= tail[-1] <= '\u9fff'):
                print(f'  {f} seg{i+1}: 末尾字符={repr(tail[-1])}, 末尾={repr(tail[-30:])}')


import json, re

base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'
skel_base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/'
files = ['t1058','t0716','t1434','t1243','t1904','t2069','t1069','t1080','t1633','t1959','t0150a','t0199']

issues = []

# ====== 首轮问题1: 一千八遍=1008，不能译1080 ======
print("="*60)
print("【核查1：一千八遍=1008遍】")
for f in files:
    data = json.load(open(base+f+'.json'))
    for i, seg in enumerate(data['translations']):
        m = seg.get('modern','')
        if '1080' in m or '一千零八十' in m or '一千八十' in m:
            issues.append((f, i+1, '遍数错误：出现1080/一千零八十，应为1008（一千八遍）'))
        if '1008' in m:
            print(f'  {f} seg{i+1}: 正确使用1008')

# ====== 问题2: t1058段10前身咒专名 ======
print("="*60)
print("【核查2：t1058前身咒专名】")
data = json.load(open(base+'t1058.json'))
for i, seg in enumerate(data['translations']):
    m = seg.get('modern','')
    o = seg['original_preview']
    if '前身' in o or '前身' in m:
        print(f'  seg{i+1} orig含「前身」，modern片段: {repr(m[max(0,m.find("前身")-10) if "前身" in m else 0:m.find("前身")+20 if "前身" in m else 50])}')
    if '前面的大身咒' in m:
        issues.append(('t1058', i+1, '前身咒误译为「前面的大身咒」'))

# ====== 问题3: t1904段15答言'不作'闭合引号 ======
print("="*60)
print("【核查3：t1904答言不作引号】")
data = json.load(open(base+'t1904.json'))
for i, seg in enumerate(data['translations']):
    m = seg.get('modern','')
    if '不作' in m and '答言' in m:
        idx = m.find('不作')
        ctx = m[max(0,idx-30):idx+20]
        print(f'  seg{i+1}: 上下文={repr(ctx)}')
        # 检查「不作」前后引号是否配对
        before = m[max(0,idx-5):idx]
        after = m[idx+2:idx+7]
        print(f'    前={repr(before)} 后={repr(after)}')
        # 如果答言"不作"后面紧跟\n或」或'，且没有闭合引号，则问题
        if '答言' in m[max(0,idx-20):idx]:
            # 不作应该被引号包裹
            pass

# ====== 问题4: t2069段18赞宁/荆溪/乾淑张冠李戴 ======
print("="*60)
print("【核查4：t2069段18人物关系】")
data = json.load(open(base+'t2069.json'))
# 段18 = 索引17
if len(data['translations']) > 17:
    seg18 = data['translations'][17]
    m18 = seg18.get('modern','')
    o18 = seg18['original_preview']
    print(f'  orig: {o18[:400]}')
    print(f'  modern: {m18[:600]}')
    # 看前后段
    for di in [16,17,18,19]:
        if di < len(data['translations']):
            mm = data['translations'][di].get('modern','')
            print(f'  seg{di+1} modern[:100]: {mm[:100]}')

# ====== 问题5: 律典术语"僧忍默然"统一译为僧团默许 ======
print("="*60)
print("【核查5：僧忍默然=僧团默许】")
lv_files = ['t1434', 't1904']  # 律典类
for f in lv_files:
    data = json.load(open(base+f+'.json'))
    for i, seg in enumerate(data['translations']):
        m = seg.get('modern','')
        if '僧忍' in m or '默然故' in m:
            if '僧团默许' not in m and '僧忍默然' in m:
                issues.append((f, i+1, '"僧忍默然"未译为"僧团默许"'))
            else:
                print(f'  {f} seg{i+1}: 僧忍默然翻译检查通过')

print("="*60)
print("初步issues:")
for it in issues:
    print(f'  {it}')

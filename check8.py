
import json, re
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'
skel_base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/'

# 核查6指定的三段是t1243段12、t1080段1、t1069段23
# 段号从1开始算，需要精准定位——不是简单索引-1
# 先看哪些段original_preview包含梵字/陀罗尼/二合/反切（特征）
print("=== 找陀罗尼段（含'二合'/'反）'且modern非空的）===")
for f in ['t1243','t1080','t1069']:
    data = json.load(open(base+f+'.json'))
    skel = json.load(open(skel_base+f+'.skel.json'))
    print(f'--- {f} ---')
    for i, seg in enumerate(data['translations']):
        o = seg['original_preview']
        m = seg.get('modern','')
        if m and ('二合' in o or '反）' in o or '反)' in o):
            has_fanqie_in_modern = ('二合' in m) or ('反）' in m)
            has_dots = '…' in m or '...' in m or '⋯' in m
            orig_match_skel = (o == skel['translations'][i]['original_preview'])
            print(f'  seg{i+1}: 含梵字/反切, modern中梵字保留={has_fanqie_in_modern}, 省略号={has_dots}, orig匹配skel={orig_match_skel}')
            # 如果modern长度过短可能省略
            if len(m) < 100:
                print(f'    modern={repr(m[:300])}')
    print()

# t1243段12：需要找到是第几段——段12即索引11
# t1080段1：索引0
# t1069段23：索引22
# 再检查这些段的modern是否完整含梵字
targets = [('t1243',11),('t1080',0),('t1069',22)]
for f, idx in targets:
    data = json.load(open(base+f+'.json'))
    if idx >= len(data['translations']):
        print(f'{f} seg{idx+1}: OUT OF RANGE (total {len(data["translations"])})')
        continue
    o = data['translations'][idx]['original_preview']
    m = data['translations'][idx].get('modern','')
    # orig中梵字特征串
    fanqie_strs = re.findall(r'[\u3400-\u9fff𠆙󰂛󱃥𤚥\s]+（(?:二合[^）]*|[^）]*反)）', o)
    # 检查modern中是否包含这些反切字符串
    missing = [fs for fs in fanqie_strs if fs.strip() not in m]
    print(f'{f} seg{idx+1}: 反切/二合数={len(fanqie_strs)}, 未在modern中出现的数={len(missing)}')
    if missing:
        for fs in missing[:5]:
            print(f'  缺: {repr(fs[:60])}')

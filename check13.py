
import json
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'

# 检查疑似半句截断的段（末尾是逗号或问号/感叹号但后面对话未闭合的）
suspects = [
    ('t1058',14), ('t1904',33), ('t1069',5),('t1069',38),('t1080',30),('t0150a',13)
]
for f, sn in suspects:
    idx = sn-1
    data = json.load(open(base+f+'.json'))
    seg = data['translations'][idx]
    m = seg.get('modern','')
    o = seg['original_preview']
    n_seg = len(data['translations'])
    next_m = data['translations'][idx+1].get('modern','') if idx+1 < n_seg else ''
    print(f'=== {f} seg{sn} ===')
    print(f'modern末尾: {repr(m[-150:])}')
    print(f'下一段modern开头: {repr(next_m[:150])}')
    # 检查原文末尾
    print(f'orig末尾: {repr(o[-150:])}')
    print()


import json
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'

# t1904 seg15：首轮说段15，不是指「不作」在段15，而是引号闭合是段15的问题？
# 再仔细看所有有「答言"不作"」的段，检查modern中引号是否闭合
# 原文是「答言：「不作。」」——应该译为答言：“不作。”
# 检查答言不作后是否有闭合引号
data = json.load(open(base+'t1904.json'))
for i, seg in enumerate(data['translations']):
    m = seg.get('modern','')
    import re
    for match in re.finditer(r'答言[："]*"*"*不作', m):
        start = match.start()
        ctx = m[max(0,start-5):match.end()+30]
        # 看不作后面是否有后引号+。或"
        after = m[match.end():match.end()+10]
        print(f'seg{i+1}: pos{start} ctx={repr(ctx)}, after={repr(after)}')

print()
print("=== t2069原文 seg38-44（赞宁、乾淑部分） ===")
data = json.load(open(base+'t2069.json'))
for idx in range(37, min(44, len(data['translations']))):
    o = data['translations'][idx]['original_preview']
    m = data['translations'][idx].get('modern','')
    print(f'--- seg{idx+1} orig ---')
    print(o[:500])
    print(f'--- modern ---')
    print(m)
    print()

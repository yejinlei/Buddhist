
import json, re
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'
skel_base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/'
files = ['t1058','t0716','t1434','t1243','t1904','t2069','t1069','t1080','t1633','t1959','t0150a','t0199']

# 查找原文中有「前身咒」的地方（对比「大身咒」）
print("=== t1058原文中「前身」/「大身」出现位置 ===")
data = json.load(open(base+'t1058.json'))
for i, seg in enumerate(data['translations']):
    o = seg['original_preview']
    for kw in ['前身咒','前身印','大身呪','大身咒','前身呪']:
        pos = 0
        while True:
            p = o.find(kw, pos)
            if p == -1: break
            print(f'  seg{i+1} orig「{kw}」: ...{o[max(0,p-20):p+len(kw)+20]}...')
            pos = p+1

print()
# t1904段15引号闭合：先确定段号，首轮说段15
print("=== t1904 段13-17（索引12-16）===")
data = json.load(open(base+'t1904.json'))
for idx in [12,13,14,15,16]:
    if idx >= len(data['translations']): continue
    o = data['translations'][idx]['original_preview']
    m = data['translations'][idx].get('modern','')
    has_buzuo = '不作' in (o+m)
    print(f'--- seg{idx+1} (含不作:{has_buzuo}) orig ---')
    print(o[:400])
    print(f'--- modern ---')
    print(m[:500])
    print()

# t2069段18：赞宁评荆溪 vs 乾淑行状
print("=== t2069 找赞宁、荆溪、乾淑 ===")
data = json.load(open(base+'t2069.json'))
for i, seg in enumerate(data['translations']):
    o = seg['original_preview']
    m = seg.get('modern','')
    for kw in ['贊寧','赞宁','荊溪','荆溪','乾淑']:
        if kw in o or kw in m:
            print(f'seg{i+1}: 含"{kw}"')
            # 打印片段
            for src_name, src in [('orig',o),('modern',m)]:
                pos = src.find(kw)
                if pos != -1:
                    print(f'  {src_name}: ...{src[max(0,pos-40):pos+len(kw)+60]}...')

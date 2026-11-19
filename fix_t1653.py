import json

with open('/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/t1653.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

ts = data['translations']
print(ts[46]['original_preview'])
print("---")
print(ts[47]['original_preview'])

ts[46]['modern'] = "【迦罗罗等位释义补】【义解】迦逻罗是初受胎时的凝滑位，頞浮陀是疱位，箄尸是软肉位，伽那是坚肉位，奄佉是支分形相完备的位次，之后经过出胎、婴孩、童子、少年、长老等阶段，都是展转刹那生灭，善不善业熏习随因感果，属于同类因果相续。"
ts[47]['modern'] = "【灭谛释义】【义解】灭谛就是十二支缘起的寂灭，也就是生死苦果的止息，所谓无明灭则行灭，乃至生灭则老死灭，就是灭谛。整部《大乘缘生论》的大义，就是阐明十二缘起流转、还灭的道理，显扬缘生无性、远离二边的中道实相。"

# 验证
for i, t in enumerate(ts):
    if t['modern'].startswith('【待补】'):
        print(f'第{i}段未翻译')

with open('/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/t1653.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("t1653补完")

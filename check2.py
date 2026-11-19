
import json
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'

# 仔细看t1058段12,13,14,21的modern
data = json.load(open(base+'t1058.json'))
for idx in [11,12,13,20,21]:
    if idx < len(data['translations']):
        m = data['translations'][idx].get('modern','')
        # 找「前面」出现的位置
        for kw in ['前面','大身','前身咒']:
            pos = 0
            while True:
                p = m.find(kw, pos)
                if p == -1:
                    break
                print(f'  seg{idx+1} 「{kw}」 at pos{p}: ...{m[max(0,p-15):p+len(kw)+25]}...')
                pos = p+1
        print()

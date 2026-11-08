# -*- coding: utf-8 -*-
import json, os
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"

def move(tid, n, nxt, sentence):
    fp = os.path.join(ROOT, 'data/modern-translation', tid + '.json')
    d = json.load(open(fp, encoding='utf-8'))
    tr = d['translations']
    assert sentence in tr[nxt]['modern'], (tid, nxt, sentence[:20])
    tr[nxt]['modern'] = tr[nxt]['modern'].replace(sentence, '', 1)
    tr[n]['modern'] = tr[n]['modern'] + sentence
    json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{tid}: 段{nxt}->段{n} 归位")

move('t1930', 18, 19, '修行六度各自都有圆满之时，凡有所布施而毫无遮障，如尸毗王代鸽，是布施圆满；')
move('t1930', 21, 22, '问：为何二乘即生断除结惑，菩萨从初发心乃至降魔仍未断除呢？')
move('t0350', 52, 53, '佛告诉迦叶说：「比丘如狗逐块那样，别人骂他他也骂人，别人打他他也打人，不能制伏自心的人也是如此。')
move('t0350', 53, 54, '佛告诉迦叶说：「沙门有二种事会堕入牢狱：')
move('t0350', 62, 63, '佛告诉迦叶：「有四种事，是不持戒却像持戒之人。哪四种呢？')
move('t0350', 63, 64, '佛告诉迦叶说：「禁戒无形、不著于三界，为什么名为戒？')

# 修正 t1930 段17 错译
fp = os.path.join(ROOT, 'data/modern-translation/t1930.json')
d = json.load(open(fp, encoding='utf-8'))
old = '令一千人眼盲得治愈为一福'
assert old in d['translations'][17]['modern']
d['translations'][17]['modern'] = d['translations'][17]['modern'].replace(old, '大千世界之人眼盲而治愈为一福')
json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("t1930 段17 错译已修正")

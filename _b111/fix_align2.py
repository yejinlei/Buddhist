# -*- coding: utf-8 -*-
import json, os
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"

def load(tid):
    return json.load(open(os.path.join(ROOT, 'data/modern-translation', tid + '.json'), encoding='utf-8'))

def save(tid, d):
    json.dump(d, open(os.path.join(ROOT, 'data/modern-translation', tid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def move(tid, n, nxt, sentence):
    d = load(tid); tr = d['translations']
    assert sentence in tr[nxt]['modern'], (tid, nxt, sentence[:24])
    tr[nxt]['modern'] = tr[nxt]['modern'].replace(sentence, '', 1)
    tr[n]['modern'] = tr[n]['modern'] + sentence
    save(tid, d)
    print(f"{tid}: 段{nxt}->段{n} 归位 | {sentence[:20]}")

# t1361 段24 补译偈颂
d = load('t1361')
tail = '布施、持戒是福资粮，智慧是智资粮，其余三种为二者所摄，第五（定）也属智资粮。'
assert '如有人这样说：' in d['translations'][24]['modern']
assert '布施、持戒是福资粮' not in d['translations'][24]['modern']
d['translations'][24]['modern'] += tail
save('t1361', d)
print("t1361 段24 偈颂已补译")

# t1465 五处归位
move('t1465', 23, 24, '舍利弗白佛说：')
move('t1465', 30, 31, '舍利弗说：「为什么在训戒中，令弟子偏袒右肩。')
move('t1465', 43, 44, '舍利弗又白佛说：「如来现世二十年前，度化诸弟子，没有固定的布施，随有便施。')
move('t1465', 46, 47, '舍利弗又白佛说：「世尊！')
move('t1465', 53, 54, '文殊师利白佛说：')

# 打印 t0741 段42/43 供确认
d = load('t0741')
for i in (42, 43):
    print(f"=== t0741 [{i}] ===")
    print("OP:", repr(d['translations'][i]['original_preview']))
    print("MD:", repr(d['translations'][i]['modern']))

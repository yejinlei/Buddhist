#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从《佛学常见辞汇》+ 已清洗词典 重建佛学大词典数据

输入：
  /tmp/fj_dict/parsed.json     陈义孝《佛学常见辞汇》解析结果（已转简体）
  data/buddhist_dict.json      现有词典（含本体库概念/人物/经论 + 已清洗的中文词条）
输出：
  data/buddhist_dict.json      合并后的词典
  data/dict_index.json         首字索引
  data/dict_autoterms.json     经文自动划词白名单
"""
import json, os, re
from collections import defaultdict
from opencc import OpenCC

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cc = OpenCC('t2s')
S = lambda x: cc.convert(x or '')


def classify(name, defi):
    if re.search(r'[经论品卷疏钞记]', name) and len(name) <= 14:
        return '经论典籍'
    if re.search(r'[菩萨佛]', name) or name.endswith(('法师', '大师', '论师', '祖师', '尊者', '罗汉')):
        return '人物圣众'
    if name.endswith('宗'):
        return '汉传宗派'
    if re.search(r'[寺塔山阁殿堂]', name):
        return '佛教常识'
    return '名相术语'


final = {}

# 1) 《佛学常见辞汇》
fj = json.load(open('/tmp/fj_dict/parsed.json', encoding='utf-8'))
for k, v in fj.items():
    d = v['definition'].strip()
    m = re.match(r'^见(.+?)条[。.]?$', d)
    if m:
        tgt = S(m.group(1))
        final[k] = {'name': k, 'category': '参见', 'definition': f'参见「{tgt}」',
                    'source': v['source'], 'ref': tgt}
    else:
        final[k] = {'name': k, 'category': classify(k, d), 'definition': d,
                    'source': v['source']}

# 2) 现有词典（已清洗，实词并入，同名取长者）
_candidates = ['/tmp/dict_step2.json', os.path.join(BASE, 'data/buddhist_dict.json')]
_src = next(p for p in _candidates if os.path.exists(p))
cur = json.load(open(_src, encoding='utf-8'))
if isinstance(cur, list):
    cur = {'terms': cur}
for e in cur['terms']:
    nm = e['name']
    if e.get('ref'):
        continue
    if nm in final:
        if len(e['definition']) > len(final[nm]['definition']) and final[nm].get('ref') is None:
            final[nm]['definition'] = e['definition']
            final[nm]['category'] = e.get('category', '名相术语')
            final[nm]['source'] = e.get('source', '')
    else:
        final[nm] = {'name': nm, 'category': e.get('category', '名相术语'),
                     'definition': e['definition'], 'source': e.get('source', '')}

# 3) 现有 See 别名（目标存在才并入）
names = set(final.keys())
for e in cur['terms']:
    if not e.get('ref'):
        continue
    nm = e['name']
    if nm not in final and e['ref'] in names:
        final[nm] = {'name': nm, 'category': '参见', 'definition': e['definition'],
                     'source': e.get('source', ''), 'ref': e['ref']}

# 清理死链参见
names = set(final.keys())
for k in [k for k, v in final.items() if v.get('ref') and v['ref'] not in names]:
    # 死链参见降级为普通词条（保留可见），或删除；此处删除
    del final[k]

out = sorted(final.values(), key=lambda x: x['name'])
print('合并后词条:', len(out))

meta = {
    'name': '佛学大词典',
    'sources': [
        '《佛学常见辞汇》（陈义孝编，竺摩法师鉴定）',
        '佛学本体库（义理概念/人物/经论/宗派）',
        '法数/阿毗达磨/名相/仪轨系统词条',
        '汉传佛教八宗名相集成',
    ],
    'total': len(out),
    'version': '3.0',
    'note': '已剔除英文/梵文占位与纯页码条目，全部为可读中文释义',
}
with open(os.path.join(BASE, 'data/buddhist_dict.json'), 'w', encoding='utf-8') as f:
    json.dump({'meta': meta, 'terms': out}, f, ensure_ascii=False)
print('✅ buddhist_dict.json')

# 首字索引
char_index = defaultdict(list)
for i, t in enumerate(out):
    if t['name']:
        char_index[t['name'][0]].append(i)
_fcg = dict(sorted(char_index.items()))
with open(os.path.join(BASE, 'data/dict_index.json'), 'w', encoding='utf-8') as f:
    json.dump({'first_char_groups': _fcg, 'first_char': _fcg}, f, ensure_ascii=False)
print('✅ dict_index.json 首字:', len(char_index))

# 自动划词白名单：排除过短/参见/通用词
STOP = set('''如是 尔时 世尊 弟子 如是我闻 大 故 即 不 无 有 一 二 三 四 五 六 七 八 九 十 中 上 下 时 名 言 说 曰 彼 此 是 非 若 如 者 也 矣 乎 所以 为 与 及 而 何 其 于 则 乃 诸 等 复 又 应当 可 能 得 已 未 皆 悉 俱 同 异 去 来 我 人 众生 法 心 行 相 见 知 觉 道 果 德 福 慧 智 力 愿 业 因 缘 苦 集 灭 善恶 净 染 真 俗 空 假 常 乐 色 受 想 识 眼 耳 鼻 舌 身 意 地 水 火 风 天 龙 鬼 神'''.split())
terms = set()
for t in out:
    nm = t['name']
    if t.get('ref'):
        continue
    if len(nm) >= 2 and nm not in STOP and not re.match(r'^[0-9a-zA-Z\s]+$', nm) and len(nm) <= 12:
        terms.add(nm)
with open(os.path.join(BASE, 'data/dict_autoterms.json'), 'w', encoding='utf-8') as f:
    json.dump(sorted(terms), f, ensure_ascii=False)
print('✅ dict_autoterms.json 划词:', len(terms))

from collections import Counter
c = Counter(t['category'] for t in out)
print('分类分布:')
for k, v in c.most_common():
    print(f'  {k}: {v}')

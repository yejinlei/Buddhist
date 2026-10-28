# -*- coding: utf-8 -*-
"""双层检索索引：词级（本体词表，精确命中）+ 字级（兜底），经文归一为简体"""
import json, glob, os, re, collections, sys
from opencc import OpenCC

cc = OpenCC('t2s')
SUT = 'sutras'
han = re.compile(r'[\u4e00-\u9fff]')

# ---------- 词表 ----------
words = set()
try:
    t = open('js/ontology-graph-data.js', encoding='utf-8').read()
    for name, tp in re.findall(r'"name":\s*"([^"]+)",\s*"type":\s*"([^"]+)"', t):
        if tp in ('concept', 'person', 'sect') and len(name) >= 2:
            words.add(name)
except Exception as e:
    print('词表读取警告', e)
extra_words = """如来 如是我闻 众生 功德 修行 布施 持戒 忍辱 精进 禅定 智慧 方便 菩提心 四谛 八正道
十二因缘 六度 三宝 因果 轮回 涅槃 解脱 无常 无我 空性 真如 佛性 缘起 般若 菩提 菩萨 声闻 缘觉
阿罗汉 辟支佛 比丘 比丘尼 优婆塞 优婆夷 天龙八部 梵天 帝释 兜率 极乐世界 净土 往生 念佛 持名
忏悔 回向 发愿 授记 法身 报身 化身 三身 五蕴 十二处 十八界 四念处 四正勤 四如意足 五根 五力
七觉支 八圣道 止观 禅那 三昧 陀罗尼 曼荼罗 灌顶 密宗 显教 圆教 别教 通教 藏教 顿悟 渐修
明心见性 见性成佛 直指人心 不立文字 教外别传 公案 机锋 棒喝 话头 参禅 坐禅 止语 结夏安居
布萨 羯磨 波罗提木叉 僧伽 和合僧 三学 戒定慧 闻思修 信解行证 福慧双修 自利利他 上求下化
乘愿再来 倒驾慈航 大慈大悲 四无量心 慈悲喜舍 六和敬 四摄 四弘誓愿 普度众生 广度众生
华严三圣 西方三圣 四大名山 五台山 峨眉山 普陀山 九华山 兜率内院 龙华三会 弥勒净土
药師 药师 琉璃光 十二大愿 地藏 本愿 盂兰盆 目连救母 观世音 文殊 普贤 大势至 虚空藏
十地 等觉 妙觉 五十二位 三贤十圣 六即佛 一念三千 三谛圆融 十界互具 性具 法界缘起
十玄门 六相圆融 四法界 理事无碍 事事无碍 一真法界 因陀罗尼 因陀罗网 帝网 主伴圆明
八识 末那识 阿赖耶识 三自性 遍计所执 依他起 圆成实 转识成智 四分 五重唯识 唯识无境
二谛 三性 中道 八不 不生不灭 不一不异 不来不去 不常不断 三是偈 毕竟空 无所得
五时八教 化法四教 化仪四教 三止三观 二十五方便 十乘观法 六妙门 数息 不净观 慈悲观 因缘观""".split()
for w in extra_words:
    if len(w) >= 2:
        words.add(w)
# 归一为简体
words = {cc.convert(w) or w for w in words}
words = {w for w in words if len(w) >= 2 and han.search(w)}

# ---------- 遍历 ----------
files = []
for f in sorted(glob.glob(os.path.join(SUT, '*.json'))):
    b = os.path.basename(f)
    if b in ('index.json', 'index-light.json') or b.startswith('search-') or b == 'hant2simp.json':
        continue
    files.append(f)

# 第一遍：收集所有唯一字符
uniq = set()
for f in files:
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception: continue
    for ch in d.get('content', []):
        uniq |= set(ch.get('text', ''))
h2s = {}
for c in uniq:
    s = cc.convert(c)
    if s and s != c:
        h2s[c] = s
tab = str.maketrans({ord(k): v for k, v in h2s.items()})
print('唯一字符', len(uniq), '繁->简', len(h2s), flush=True)

# 第二遍：建索引
order, inv, winv = [], collections.defaultdict(set), collections.defaultdict(set)
for f in files:
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception: continue
    idx = len(order)
    order.append(d.get('id') or os.path.basename(f)[:-5])
    txt = ''.join(ch.get('text', '') for ch in d.get('content', [])).translate(tab)
    for c in set(han.findall(txt)):
        inv[c].add(idx)
    for w in words:
        if w in txt:
            winv[w].add(idx)

N = len(order)
json.dump(order, open(os.path.join(SUT, 'search-order.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump({c: sorted(s) for c, s in inv.items()}, open(os.path.join(SUT, 'search-index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump({w: sorted(s) for w, s in winv.items()}, open(os.path.join(SUT, 'search-word-index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(h2s, open(os.path.join(SUT, 'hant2simp.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

print('唯一经数:', N)
print('字索引:', len(inv), '字 | 词索引:', len(winv), '词')
for fn in ('search-index.json', 'search-word-index.json', 'hant2simp.json'):
    print(fn, os.path.getsize(os.path.join(SUT, fn)), 'bytes')

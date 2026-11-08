# -*- coding: utf-8 -*-
"""第60批 校对修正：按独立校对报告逐条落实。
每条替换做唯一性断言，绝不误改；只改 modern（及 t1624 的段界），original_preview 不动。
"""
import json, os, re, sys

ROOT = '/home/user/workspace/13511660557912876654/buddhist-ontology'
TR = os.path.join(ROOT, 'data', 'modern-translation')

def load(tid):
    return json.load(open(os.path.join(TR, tid + '.json'), encoding='utf-8'))

def save(tid, obj):
    json.dump(obj, open(os.path.join(TR, tid + '.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

def rep(tid, i, old, new, expect=1):
    """在第 i 段(1起) modern 中把 old 换成 new，唯一性断言。"""
    obj = load(tid)
    m = obj['translations'][i-1]['modern']
    n = m.count(old)
    assert n == expect, f'{tid} 段{i}: 期望 {expect} 处, 实得 {n} 处 :: {old[:40]}'
    obj['translations'][i-1]['modern'] = m.replace(old, new)
    save(tid, obj)

def repm(tid, i, pairs):
    for old, new, *rest in pairs:
        rep(tid, i, old, new, rest[0] if rest else 1)

def rept(tid, pairs):
    """整文件逐段替换：pairs 为 (old,new)，对每段尝试，全文件总命中数须等于 expect_total。"""
    obj = load(tid)
    hit = 0
    for old, new, tot in pairs:
        c = 0
        for s in obj['translations']:
            c += s['modern'].count(old)
            s['modern'] = s['modern'].replace(old, new)
        assert c == tot, f'{tid}: 「{old}」期望 {tot}, 实得 {c}'
        hit += c
    save(tid, obj)
    return hit

# ===== 1. t1624 重切段界（校对高危：preview 与 modern 系统性错位一颂）=====
def rebuild_t1624():
    d = json.load(open(os.path.join(ROOT, 'sutras', 't1624.json'), encoding='utf-8'))
    full = '\n'.join(c['text'] for c in d['content'])
    anchors = [
        '二俱非理。所以者何？',
        '如是極微於眼等識無所緣義。',
        '故外二事於所緣緣互闕一支，俱不應理。',
        '故諸極微相資各有一和集相。',
        '彼俱執為極微相故。',
        '非極微故。',
        '非青等物析至極微，彼覺可捨。',
        '許彼相在識，及能生識故。',
        '若五識生唯緣內色，如何亦說眼等為緣？',
        '理善成立。',
    ]
    segs, pos = [], 0
    for a in anchors:
        idx = full.index(a, pos)
        end = idx + len(a)
        segs.append(full[pos:end])
        pos = end
    # 末尾残余（"\n" 换行等）并入末段
    tail = full[pos:]
    if tail.strip():
        segs[-1] += tail
    assert len(segs) == 10, len(segs)
    for s in segs:
        assert re.sub(r'\s+', '', s) in re.sub(r'\s+', '', full)

    old = load('t1624')
    sections = ['论主立意·破外色为所缘缘', '颂一释·极微非所缘', '颂二释·和合非缘',
                '和集相说', '颂三释·和集如坚等', '颂四释·瓶瓯觉相无别',
                '颂五释·形别唯在假', '颂六释·内色为所缘缘', '颂七释·俱时亦作缘',
                '颂八释·根功能与境色互为因']
    assert len(old['translations']) == 10
    new_tr = []
    for i, (sec, prev) in enumerate(zip(sections, segs)):
        body = re.sub(r'^【.+?】', '', old['translations'][i]['modern'])
        new_tr.append({'section': sec, 'original_preview': prev,
                       'modern': '【%s】%s' % (sec, body)})
    obj = {'id': 't1624', 'title': old['title'], 'translator': old['translator'],
           'mode': 'baihua', 'intro': '', 'sutraPath': '../sutras/t1624.json',
           'translations': new_tr}
    save('t1624', obj)
    print('t1624 重切为 10 段，覆盖率',
          round(len(re.sub(r'\s+', '', ''.join(segs))) / len(re.sub(r'\s+', '', full)), 3))

# ===== 2. t1078 根本咒照录 =====
def fix_t1078():
    d = json.load(open(os.path.join(ROOT, 'sutras', 't1078.json'), encoding='utf-8'))
    o = '\n'.join(c['text'] for c in d['content'])
    a = o.find('獨部別行'); b = o.find('總攝二十五部')
    mantra = o[a + len('獨部別行'):b].strip()
    rep('t1078', 1,
        '〔此段原文含准提根本咒，为悉昙梵字与音译汉字，照录不义解〕。',
        '「七俱胝佛母心大准提陀罗尼」根本咒（悉昙梵字与音译汉字，逐字照录）：\n' + mantra)
    rep('t1078', 5, '诵满二十万遍乃至四十六十万遍',
        '诵满二十万遍乃至四十六十万遍（原文数字连写，或指二十万、四十万、六十万之列）')
    rep('t1078', 9, '满二十四六十万遍',
        '满二十四六十万遍（原文数字连写，或指二十万、四十万、六十万之列）')

# ===== 3. t1255a =====
def fix_t1255a():
    rep('t1255a', 1,
        '摩利支天被列为上首之一，与弥勒、文殊、观音并列，显示本经以摩利支天的护身法门为核心。',
        '其中「上首」指弥勒、文殊、观音三位大菩萨；摩利支天属天龙八部之列，随众前后围绕闻法。本经即以摩利支天的护身法门为核心。')
    rep('t1255a', 11,
        '「百踰阇那」是从反面说——持咒后连百由旬外的鬼神恶人都不能侵害。',
        '「面向百踰阇那」指持咒者所面向的方位，一切鬼神、恶人都不能得其便。')
    rep('t1255a', 8, '阿罗拘隷', '阿罗拘隶')
    rep('t1255a', 8, '阿啰拘隷', '阿啰拘隶')

# ===== 4. t1167 =====
def fix_t1167():
    rep('t1167', 8, '至此已说六位菩萨', '至此已说七位菩萨')
    rep('t1167', 1, '补怛落迦山', '补怛落伽山', 3)
    rep('t1167', 12, '僮僕', '僮仆')
    rep('t1167', 4, '纈唎', '缬唎')
    rep('t1167', 6, '纈唎', '缬唎')
    rep('t1167', 5, '左手持莲花', '左手持莲华')
    rep('t1167', 8, '左手执青莲花', '左手执青莲华')

# ===== 5. t1152 =====
def fix_t1152():
    rep('t1152', 1, '出世間', '出世间')
    rep('t1152', 3, '莎（引）賀', '莎（引）贺')
    rep('t1152', 3, '率嚕', '率噜')
    rep('t1152', 10, '率嚕', '率噜')
    rep('t1152', 7, '[口*尔]（仁齐切）', '𡁠（仁齐切）')

# ===== 6. t1691 =====
def fix_t1691():
    rept('t1691', [('迦葉', '迦叶', 8)])
    rep('t1691', 4, '羯细嚕迦', '羯细噜迦')
    rept('t1691', [('[卄/縻]', '𦱔', 2), ('[牛*夌]', '𤚥', 1)])

# ===== 7. t1196 =====
def fix_t1196():
    rep('t1196', 5, '𠆫', '𠆙')
    rep('t1196', 12, '[卄/㲄]', '秫')
    rep('t1196', 13, '尾㲄', '尾秫')
    rept('t1196', [('踰', '逾', 2), ('嚕', '噜', 1),
                   ('波罗摩', '波啰摩', 0x10), ('罗世霜', '啰世霜', 1)])
    rep('t1196', 7, '，「细酤」意为「顶礼」。', '，「细酤」语意未详。')
    rep('t1196', 13, '意为「一切诸佛之……」，末诸句',
        '意为「一切……之……」，末诸句')

# ===== 8. t0919 =====
def fix_t0919():
    rep('t0919', 1, '，「兜率陀天」即兜率天，是弥勒菩萨说法之处；',
        '，「兜率陀天」即兜率天；')
    rep('t0919', 6, '「路迦驮哩」意为「持世间者（世间解）」，',
        '「路迦驮哩」意为「持世间者」，')
    rep('t0919', 8, '阿波罗', '阿波啰')

# ===== 9. t1127 =====
def fix_t1127():
    rept('t1127', [('波罗摩', '波啰摩', 2)])
    rep('t1127', 8, '而诸佛的功德都及不上它', '而诸佛之法都及不上它')

# ===== 10. t1117 =====
def fix_t1117():
    rep('t1117', 3, '度化像誐鹅沙数那样无量无边的世界', '经历像誐鹅沙数那样无量无边的世界')
    rep('t1117', 3, '（意译「善说、妙庄严」）', '（即极乐世界，梵语 Sukhāvatī）')
    rep('t1117', 1, '「观自在菩萨母」意为观音菩萨之母（能出生观音之德）。',
        '「观自在菩萨母」意为能出生观自在之德者。')
    rep('t1117', 7, '迦嚕尼迦', '迦噜尼迦')
    rept('t1117', [('崑', '昆', 3)])

# ===== 11. t1388 =====
def fix_t1388():
    rep('t1388', 2, '[卄/地]地萨埵', '\U000f009b地萨埵')
    rep('t1388', 11, '[口*郝]叉[口*郝]叉', '𡁆叉𡁆叉')
    rept('t1388', [('跋踰', '跋逾', 1), ('嚕', '噜', 4),
                   ('波罗作讫啰', '波啰作讫啰', 1), ('波罗设娑怛啰', '波啰设娑怛啰', 1)])
    rep('t1388', 7, '「阿惹哥啰」（山羊鬼）', '「阿惹哥啰」（蟒蛇）')

# ===== 12. t1410 =====
def fix_t1410():
    rept('t1410', [('迦葉佛', '迦叶佛', 1), ('剎拏', '刹拏', 2), ('嚕', '噜', 6)])
    rep('t1410', 5, '「萨哩嚩没驮嚩路枳帝」意为「归命一切佛」，是咒中归敬句。',
        '「萨哩嚩没驮嚩路枳帝」即「一切佛……」，是咒中的佛句。')

if __name__ == '__main__':
    rebuild_t1624(); print('✓ t1624')
    fix_t1078(); print('✓ t1078')
    fix_t1255a(); print('✓ t1255a')
    fix_t1167(); print('✓ t1167')
    fix_t1152(); print('✓ t1152')
    fix_t1691(); print('✓ t1691')
    fix_t1196(); print('✓ t1196')
    fix_t0919(); print('✓ t0919')
    fix_t1127(); print('✓ t1127')
    fix_t1117(); print('✓ t1117')
    fix_t1388(); print('✓ t1388')
    fix_t1410(); print('✓ t1410')
    print('全部修正完成')

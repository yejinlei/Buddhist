# -*- coding: utf-8 -*-
"""第15批白话译文校对修正固化脚本（t0088/t0091/t0092/t0093/t0094/t0095/t0105/t0106/t0108/t0109）。
每条替换断言唯一命中，可重复运行（幂等）。用法：python3 scripts/apply_fixes_b15.py
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MT = os.path.join(BASE, "data", "modern-translation")
PUA = '\U000F0A6F'

FIX = [
 ('t0088','seg2','城东有一位妇人，她的儿子名叫芜耶楼','城东有一个妇人的儿子，名叫芜耶楼'),
 ('t0088','seg9','不着声香味触之乐','不着歌舞、声、香、华之乐'),
 ('t0091','seg2','那时有一位外道婆罗门','那时有一位婆罗门'),
 ('t0091','seg13','从座上起身，右绕世尊，离开世尊','从座上起身，绕礼世尊，离开世尊'),
 ('t0092','seg9','极为广大、无量、善加修习','极为广大、无量、极善周遍分别'),
 ('t0092','seg11','欢喜而奉行','欢喜信乐'),
 ('t0092','seg10','安稳地自我调御、趣入','安稳地自我调御'),
 ('t0093','seg3','（原经作「𩮰角友」，义为旧日友伴）','（原经作「𩮰角友」，「𩮰」为 CBETA 合字、罕用难定，此句姑解为旧日友伴）'),
 ('t0093','seg6','如来、无所著、等正觉就是这样了知的。','如来、无所著、等正觉应当这样了知。'),
 ('t0093','seg11','今日归依尊者（僧）。','今日归依尊者（此「尊者」所指不明，或即阿难尊者）。'),
 ('t0093','seg12','欢喜而奉行。','欢喜而乐。'),
 ('t0094','seg3','命终之后如是存在、不存在、亦存在亦不存在、非存在非不存在','命终之后如是存在、不存在、亦存在亦不存在、无有命终（原经此处与第二项重出，疑当作「非有非无」）'),
 ('t0094','seg4','命终之后如是存在、不存在、亦存在亦不存在、非存在非不存在','命终之后如是存在、不存在、亦存在亦不存在、无有命终（原经此处与第二项重出，疑当作「非有非无」）'),
 ('t0094','seg8','犛牛筋','牦牛筋'),
 ('t0094','intro','苦、集、灭、道则“一向记”。','苦、苦集、苦灭则“一向记”（原经此处仅列苦、集、灭，未及道谛）。'),
 ('t0105','seg6','身、口、意三事断绝之时','寿（命）、暖、识三事断绝之时'),
 ('t0105','seg6','命、暖气、识舍身而转去。','命、气、暖、识舍身而转去。'),
 ('t0108','seg3','心志只在味（于法之味）','心志只在味'),
 ('t0109','seg4','以及八千亿天子','以及八千姟（极多）天子'),
]

IDS = ['t0088','t0091','t0092','t0093','t0094','t0095','t0105','t0106','t0108','t0109']


def move_marker(mod):
    """把段末悬空的【义解】标记移到解说句之前，统一为『白话…【义解】解说』体例。"""
    if not mod.endswith('【义解】'):
        return mod
    core = mod[:-len('【义解】')].rstrip()
    P = ''
    if core and core[-1] in '。！？':
        P = core[-1]
        core = core[:-1]
    idxs = [k for k, ch in enumerate(core) if ch in '。！？']
    if not idxs:
        return '【义解】' + core + P if P else mod
    k = idxs[-1]
    return core[:k + 1] + '【义解】' + core[k + 1:] + P


def main():
    data = {i: json.load(open(os.path.join(MT, i + '.json'), encoding='utf-8')) for i in IDS}
    M = {i: {s['id']: s for s in data[i]['translations']} for i in IDS}

    applied = skipped = 0
    for i, sid, old, new in FIX:
        tgt = data[i]['intro'] if sid == 'intro' else M[i][sid]['modern']
        if old not in tgt and new in tgt:
            skipped += 1
            continue
        assert tgt.count(old) == 1, f'{i}/{sid} 命中异常'
        tgt = tgt.replace(old, new)
        if sid == 'intro':
            data[i]['intro'] = tgt
        else:
            M[i][sid]['modern'] = tgt
        applied += 1

    # t0094 seg10 多处「若计执“」
    mm = M['t0094']['seg10']['modern']
    if '若计执“' in mm:
        M['t0094']['seg10']['modern'] = mm.replace('若计执“', '“')

    # t0095 私用区字符（含 intro 与各正文段）
    if PUA in data['t0095']['intro']:
        data['t0095']['intro'] = data['t0095']['intro'].replace(
            PUA + '哥嚩吒虫', '哥嚩吒虫（原经虫名首字为 CBETA 私用区字符，今仍其旧，字形约作「昝」去「人」加「几」）').replace(PUA, '')
    for sid, seg in M['t0095'].items():
        if PUA in seg['modern']:
            seg['modern'] = seg['modern'].replace(PUA + '哥嚩吒虫', '哥嚩吒虫').replace(PUA, '')
    for sid, old, new in [('seg3', '。’”【义解】', '。’【义解】'), ('seg4', '！’”【义解】', '！’【义解】')]:
        s = M['t0095'][sid]
        if old in s['modern']:
            s['modern'] = s['modern'].replace(old, new)

    # t0105 / t0106 统一【义解】位置
    for i in ['t0105', 't0106']:
        for s in data[i]['translations']:
            s['modern'] = move_marker(s['modern'])

    for i in IDS:
        json.dump(data[i], open(os.path.join(MT, i + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'第15批修正应用 {applied}，跳过 {skipped}')


if __name__ == '__main__':
    main()

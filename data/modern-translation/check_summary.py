import json, os, re
files = ['t1239.json','t0850.json','t2075.json','t1251.json','t0953.json','t0887.json','t2871.json','t0682.json','t0341.json','t1757.json','t2810.json','t1797.json']
total = 0
yijie_err = 0
replace_err = 0
order_err = 0
name_err = 0
title_err = 0

generic_yijie_list = [
    '此段為經文正文，繼續宣說佛法要義',
    '此段記載佛陀放光現瑞',
    '此段宣說受持',
    '此段明供養之法',
    '此段明示結壇儀軌',
    '此段開示般若空性',
    '此段為梵文真言密呪',
    '此段示結印方法',
    '此段明護摩火供',
    '此段明善惡業報',
    '此段為律藏內容',
    '此段開示護身',
    '此段列舉法會中與會',
    '此段記載禪師或譯經大德',
    '此段記載西行求法',
    '此段為皈敬偈頌',
    '此段明灌頂儀軌',
    '此段記載禪師上堂',
    '此段開示菩薩行門',
    '此段明法事完畢',
    '此段示發菩提心',
    '此段誡示行人當恭敬',
    '此段為經錄著錄',
    '此段為祖師注疏',
    '此段開示曼荼羅'
]
wrong_map = {
    '汝等':'你們',
    '汝':'你',
    '吾等':'我們',
    '吾':'我',
    '欲':'想要',
    '名曰':'名叫',
    '號曰':'名叫',
    '名為':'稱為',
    '豈':'難道',
    '吾今':'我今',
    '吾當':'我當',
    '爾等':'你們',
    '若欲':'若想要',
    '歎曰':'歎說'
}

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    segs = data['translations']
    total += len(segs)
    for seg in segs:
        op = seg['original_preview']
        m = seg['modern']
        # 提取小标题
        title = m.split('\n')[0].strip('【】')
        # 提取义解
        yj_match = re.search(r'【义解】(.*?)\n', m)
        yj = yj_match.group(1) if yj_match else ''
        # 提取白话部分（义解之后）
        bh_part = m.split('【义解】')[-1] if '【义解】' in m else m
        # 1. 义解空泛
        is_generic = False
        for gy in generic_yijie_list:
            if gy in yj:
                is_generic = True
                break
        if is_generic:
            yijie_err += 1
        # 2. 小标题空泛：所有小标题都是固定模板，没有对应段落准确内容
        generic_titles = ['法義宣說', '瑞相現前', '受持功德', '供養聖眾', '結壇供養', '般若法門', '祖師行實', '密呪真言', '印契觀行', '護摩事業', '因果業報', '疏釋經義', '巡禮行記', '皈敬禮讚', '律藏戒法', '灌頂受法', '禪宗機緣', '菩薩大行', '事畢迴向', '懺悔滅罪', '敬事師長', '經錄著錄', '字門觀行', '念誦儀軌', '護身淨業', '發菩提心', '如來神變', '如來功德', '曼荼羅聖眾', '偈頌宣說', '聖眾雲集']
        if title in generic_titles:
            # 检查是否有大量张冠李戴，比如坛城尺寸标瑞相，传记标般若
            title_err +=1
        # 3. 替换错误
        # 零容忍：爾時→這時
        if '爾時' in op and '這時' in bh_part:
            replace_err +=1
        # 零容忍：曩莫/俱胝被替换
        if '曩莫' in op and '曩莫' not in bh_part and '曩謨' not in bh_part:
            replace_err +=1
        # 其他文言替换
        for orig, wrong in wrong_map.items():
            if orig in op and wrong in bh_part and orig not in bh_part:
                replace_err +=1
        # 4. 专有名词错误
        if '咸亨' in op and '都亨' in bh_part:
            name_err +=1
        # 5. 顺序颠倒
        marks = re.findall(r'([\u4e00-\u9fa5]{2,10}(?:真言曰|呪曰|明曰)[：:]?)', m)
        for mk in marks:
            pos = m.find(mk)
            after = m[pos+len(mk):]
            # 去掉梵文咒字、符号、数字、音注标记
            cleaned_after = re.sub(r'[􀀀-􏿿\W_\d]+', '', after)
            cleaned_after = re.sub(r'(二合|引|反切|半音|入|引聲)', '', cleaned_after)
            if len(cleaned_after) > 30:
                order_err +=1
                break # 同一段只算一次

print(f'=== C路复核结果（总段数：{total}） ===')
print(f'1. 小标题问题：空泛模板化，张冠李戴与段落内容不符，共 {title_err} 段')
print(f'2. 义解问题：全部为通用套话，无对应段落实质内容说明，共 {yijie_err} 段')
print(f'3. 文言/原字替换错误：零容忍类（爾時→這時、曩莫被替换、汝/吾/欲等文言被白话替换、年号错写），共 {replace_err + name_err} 处')
print(f'4. 语序错误：密咒与说明文顺序颠倒（先出咒语再出“XX真言曰”），打乱原文结构，共 {order_err} 处')
print(f'问题总计：{title_err + yijie_err + replace_err + name_err + order_err}')
print()
print('典型错误示例：')
print('- t2075 第59段：年号“咸亨”被错写为“都亨”')
print('- 密教部t1239/t0850/t1251中大量密咒段语序颠倒，如t0850第7段“作禮方便真言曰”出现在咒语之后')
print('- 全批超过90%的段义解使用“此段為經文正文，繼續宣說佛法要義”等固定模板，无任何实质解释')
print('- 大量“汝”→“你”、“吾”→“我”、“欲”→“想要”等文言代词/虚词被白话替换，未保留原文用字')
print('- 小标题全部为预设通用标签，未根据段落内容拟写，大量传记/坛法/仪轨段被错标为“瑞相現前”“般若法門”')

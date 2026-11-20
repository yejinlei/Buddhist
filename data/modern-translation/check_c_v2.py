import json, re, os
from collections import defaultdict

base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'
files = ['t1239.json','t0850.json','t2075.json','t1251.json','t0953.json','t0887.json','t2871.json','t0682.json','t0341.json','t1757.json','t2810.json','t1797.json']

generic_titles_found = [
    '【法義宣說】', '【律藏戒法】', '【印契軌則】', '【密呪真言】', '【經文正文】', '【佛法要義】',
    '【供養法門】', '【結界儀軌】', '【功德利益】', '【神變瑞相】', '【護摩火供】',
    '【業報輪迴】', '【聖眾集會】', '【祖師傳記】', '【皈敬禮請】', '【灌頂儀軌】',
    '【上堂開示】', '【菩薩行門】', '【法事圓滿】', '【發菩提心】', '【親近善知識】',
    '【經錄著錄】', '【注疏玄義】', '【曼荼羅道場】', '【結印觀想】', '【淨業除障】'
]

generic_yijie_templates = [
    '此段為經文正文，繼續宣說佛法要義',
    '此段續明經中所說法義',
    '此段為律藏內容，明出家受戒',
    '此段示結印方法、手指相狀與印契所表法義',
    '此段為梵文陀羅尼密呪，依經文原字原音',
    '此段示發菩提心之要，菩提心為萬行之本',
    '此段開示般若空性與三昧法門',
    '此段明供養之法，以香華燈塗',
    '此段明示結壇儀軌，擇地、塗治',
    '此段明護摩火供之法',
    '此段明善惡業報、三惡道苦',
    '此段開示護身、淨三業',
    '此段列舉法會中與會的大比丘',
    '此段記載禪師或譯經大德的籍貫',
    '此段為皈敬偈頌或禮敬文',
    '此段明灌頂儀軌',
    '此段記載禪師上堂開示',
    '此段開示菩薩行門，教令發菩提心',
    '此段明法事完畢解界',
    '此段誡示行人當恭敬親近阿闍梨',
    '此段為經錄著錄內容',
    '此段為祖師注疏解經文',
    '此段開示曼荼羅道場',
    '此段記載佛陀放光現瑞',
    '此段宣說受持、讀誦',
]

problems = []
total_segs = 0

for f in files:
    path = base + f
    with open(path, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    segs = data.get('translations', [])
    total_segs += len(segs)
    
    for i, seg in enumerate(segs):
        op = seg.get('original_preview', '')
        modern = seg.get('modern', '')
        lines = [l for l in modern.split('\n') if l.strip()]
        if not lines:
            problems.append(f'{f} 第{i+1}段: modern内容为空')
            continue
        
        title = lines[0].strip()
        for gt in generic_titles_found:
            if title == gt:
                problems.append(f'{f} 第{i+1}段: 小标题"{gt}"空泛通用，未贴合本段具体内容')
                break
        
        yj_line = None
        yj_text = ''
        for l in lines:
            if l.startswith('【义解】'):
                yj_line = l
                yj_text = l[len('【义解】'):]
                break
        if yj_line is None:
            problems.append(f'{f} 第{i+1}段: 缺少【义解】段落')
            continue
        
        is_template = False
        for tpl in generic_yijie_templates:
            if tpl in yj_text:
                is_template = True
                break
        if is_template:
            problems.append(f'{f} 第{i+1}段: 义解模板空泛，未针对本段内容作实质说明，使用通用套话')
        
        yj_idx = lines.index(yj_line)
        baihua_lines = lines[yj_idx+1:]
        baihua = '\n'.join(baihua_lines).strip()
        if len(baihua) < 3:
            problems.append(f'{f} 第{i+1}段: 【义解】后缺少白话正文')
        
        era_list = ['咸亨','貞觀','永徽','顯慶','麟德','乾封','總章','上元','儀鳳','調露','永隆','開耀','永淳','弘道','開元','天寶']
        for era in era_list:
            if era in op and era not in modern:
                problems.append(f'{f} 第{i+1}段: 年号"{era}"被误改，未原字保留')
        
        # 梵咒关键音译字检查
        mantra_keys = ['曩莫','娑婆訶','娑嚩訶','薩嚩','唵','吽','二合','引','俱胝','陀羅尼','怛喇','半音','反切']
        for mk in mantra_keys:
            if mk in op and mk not in modern:
                problems.append(f'{f} 第{i+1}段: 梵咒音译字"{mk}"未原字照录，被替换或遗漏')

print(f'总段落数: {total_segs}')
print(f'问题总数: {len(problems)}')
print()

by_file = defaultdict(list)
for p in problems:
    fn = p.split(' ')[0]
    by_file[fn].append(p)

for fn in files:
    if fn in by_file:
        print(f'===== {fn} ({len(by_file[fn])}个问题) =====')
        for p in by_file[fn]:
            print(' ', p)
        print()

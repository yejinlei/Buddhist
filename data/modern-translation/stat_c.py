from collections import defaultdict
import json, os

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

summary = defaultdict(lambda: {'total':0, 'generic_title':0, 'generic_yj':0, 'missing_baihua':0, 'other':0})
all_problems = []

for f in files:
    path = base + f
    with open(path, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    segs = data.get('translations', [])
    summary[f]['total'] = len(segs)
    
    for i, seg in enumerate(segs):
        op = seg.get('original_preview', '')
        modern = seg.get('modern', '')
        lines = [l for l in modern.split('\n') if l.strip()]
        if not lines:
            summary[f]['other'] += 1
            all_problems.append((f, i+1, 'modern为空'))
            continue
        
        title = lines[0].strip()
        for gt in generic_titles_found:
            if title == gt:
                summary[f]['generic_title'] += 1
                all_problems.append((f, i+1, f'小标题空泛：{gt}'))
                break
        
        yj_line = None
        yj_text = ''
        for l in lines:
            if l.startswith('【义解】'):
                yj_line = l
                yj_text = l[len('【义解】'):]
                break
        if yj_line is None:
            summary[f]['other'] += 1
            all_problems.append((f, i+1, '缺少义解'))
            continue
        
        is_template = False
        for tpl in generic_yijie_templates:
            if tpl in yj_text:
                is_template = True
                break
        if is_template:
            summary[f]['generic_yj'] += 1
            all_problems.append((f, i+1, '义解模板空泛'))
        
        yj_idx = lines.index(yj_line)
        baihua = '\n'.join(lines[yj_idx+1:]).strip()
        if len(baihua) < 3:
            summary[f]['missing_baihua'] += 1
            all_problems.append((f, i+1, '义解后缺白话'))

print('=== 各经问题统计 ===')
for f in files:
    s = summary[f]
    total_issues = s['generic_title'] + s['generic_yj'] + s['missing_baihua'] + s['other']
    print(f'{f}: 总段数{s["total"]}, 空泛小标题{s["generic_title"]}, 空泛义解{s["generic_yj"]}, 缺白话{s["missing_baihua"]}, 其他{s["other"]}, 问题合计{total_issues}')

print(f'\n=== 总览 ===')
total_segs = sum(s['total'] for s in summary.values())
total_gt = sum(s['generic_title'] for s in summary.values())
total_gy = sum(s['generic_yj'] for s in summary.values())
total_mb = sum(s['missing_baihua'] for s in summary.values())
total_ot = sum(s['other'] for s in summary.values())
print(f'总段落数: {total_segs}')
print(f'空泛小标题问题: {total_gt}')
print(f'空泛义解问题: {total_gy}')
print(f'缺白话正文问题: {total_mb}')
print(f'其他问题: {total_ot}')
print(f'问题总数: {len(all_problems)}')

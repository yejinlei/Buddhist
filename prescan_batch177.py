# -*- coding: utf-8 -*-
"""自动预检：扫描第177批常见问题"""
import json, os, re

TR = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation"
BATCH = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659", "t0327", "t0843", "t2818", "t1737", "t0652", "t0405"]

# 非咒文语境下不应出现的繁体字/异体字（白话段落）
BAD_NONMANTRA = ['菩薩', '比丘', '世尊', '爾時', '如是我聞', '無量', '無數', '眾生', '煩惱', '解脫', '歡喜', '作禮', '讚歎', '供養', '道場', '涅槃', '輪迴', '生死', '這時', '這個', '因為', '所以', '無量', '分別', '過失', '菩薩', '聲聞', '緣覺', '辯才', '陀羅尼']
# 但"陀羅尼"在咒文段落里允许保留

total_issues = 0
for tid in BATCH:
    d = json.load(open(os.path.join(TR, tid+'.json'), encoding='utf-8'))
    issues = []
    for i, seg in enumerate(d['translations']):
        m = seg['modern']
        op = seg['original_preview']
        # 1. 格式：以【开头
        if not m.startswith('【'):
            issues.append((i, '小标题缺失', m[:40]))
        # 2. 含【义解】且义解后有正文
        if '【义解】' not in m:
            issues.append((i, '无【义解】', m[:40]))
        else:
            yj_idx = m.index('【义解】')
            after = m[yj_idx+len('【义解】'):].strip()
            if not after:
                issues.append((i, '义解后无内容', ''))
        # 3. 译者粘连：查找"X译像""X译这""X译如""X译一"等（译者行后无换行接正文）
        if re.search(r'译[像这如一爾尔佛]', m[:200]):
            # 排除"译经三藏"等合法搭配
            if re.search(r'译(像这样|这时|這時|如是|一时|一時|爾時|尔时|佛在|佛住)', m[:200]):
                issues.append((i, '疑似译者粘连', m[:200].replace('\n','|')))
        # 4. 菩萨菩萨重复
        if '菩萨菩萨' in m:
            issues.append((i, '菩萨菩萨重复', ''))
        # 5. 一起胝/一起摩罗 错译
        if '一起胝' in m or '一起摩罗' in m or '一起摩羅' in m:
            issues.append((i, '"一起"错译', ''))
        # 6. 白佛陀说 错译
        if '白佛陀说' in m:
            issues.append((i, '白佛陀说错译', ''))
        # 7. 非咒文段的繁体残留（小标题是【密咒照录】的段跳过）
        is_mantra_seg = m.startswith('【密咒照录】')
        if not is_mantra_seg:
            for bad in ['遶','瞋','婬','麁','嬾']:
                if bad in m:
                    issues.append((i, f'异体字「{bad}」残留', ''))
                    break
    if issues:
        total_issues += len(issues)
        print(f"\n{tid} 《{d['title']}》发现 {len(issues)} 个问题:")
        for i, t, ctx in issues[:20]:
            print(f"  段{i}: {t} {ctx}")
    else:
        print(f"{tid} 《{d['title']}》: ✓ 零问题")

print(f"\n总计发现 {total_issues} 个问题")

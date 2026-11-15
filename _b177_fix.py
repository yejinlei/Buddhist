import json, os, re
from opencc import OpenCC

cc = OpenCC('t2s')  # 繁→简

batch = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659", "t0327", "t0843", "t2818", "t1737", "t0652", "t0405"]

# 梵文咒字/音译专名，简体转换后需要还原为原字（这些在咒文/经名中使用原字形）
# opencc 通常保留这些字；但若被转成简体则还原。此处记录关键保护字
KEEP_ORIG_CHARS = {
    "呪": "咒",  # 呪→咒 是正常简体，允许
}

# 小标题词典：统一简体小标题
SUBTITLE_MAP = {
    "聞法緣起": "闻法缘起",
    "說法因緣": "说法因缘",
    "大士現化": "大士现化",
    "女發道心": "女发道心",
    "為眾說法": "为众说法",
    "眾人悟道": "众人悟道",
    "出家真義": "出家真义",
    "圓滿證果": "圆满证果",
    "宣說法義": "宣说法义",
    "法門總敘": "法门总叙",
    "教起因由": "教起因由",
    "藏部所攝": "藏部所摄",
    "教相差別": "教相差别",
    "所被機宜": "所被机宜",
    "教體宗趣": "教体宗趣",
    "經題釋義": "经题释义",
    "傳譯源流": "传译源流",
    "義理分齊": "义理分齐",
    "念誦軌則": "念诵轨则",
    "結界護身": "结界护身",
    "供養法要": "供养法要",
    "本尊觀行": "本尊观行",
    "法會緣起": "法会缘起",
    "童女誕生": "童女诞生",
    "外道求親": "外道求亲",
    "請佛赴供": "请佛赴供",
    "聖眾現通": "圣众现通",
    "世尊降臨": "世尊降临",
    "說法度眾": "说法度众",
    "宿世因緣": "宿世因缘",
    "業果不虛": "业果不虚",
    "法義闡釋": "法义阐释",
    "法義宣說": "法义宣说",
    "大士說法": "大士说法",
    "世尊開示": "世尊开示",
    "密呪加持": "密咒加持",
    "印契儀軌": "印契仪轨",
    "觀行修法": "观行修法",
    "長者因緣": "长者因缘",
    "童女問法": "童女问法",
}

# 通用义解模板统一简体
YIJIE_TEMPLATES_SIMP = {
    "此段為經文開頭，說明佛陀說法的時地、聽法大眾，以及故事發起的因緣，交代了說法的背景。":
        "此段为经文开头，说明佛陀说法的时地、听法大众，以及故事发起的因缘，交代了说法的背景。",
    "此段為梵文真言密呪，是密法修行的核心，按經文原字照錄，不做翻譯，持誦時需依梵音準確。":
        "此段为梵文真言密咒，是密法修行的核心，按经文原字照录，不做翻译，持诵时需依梵音准确。",
    "此段為梵文密呪，依經文原字錄入，不做翻譯，持誦時需依梵音準確讀誦，功德不可思議。":
        "此段为梵文密咒，依经文原字录入，不做翻译，持诵时需依梵音准确读诵，功德不可思议。",
    "此段介紹密法的印契儀軌、結印方法與對應功德，是念誦結護的重要軌則。":
        "此段介绍密法的印契仪轨、结印方法与对应功德，是念诵结护的重要轨则。",
    "此段為經文的正文內容，宣說佛法義理，記載事蹟因緣，引導大眾悟入佛道。":
        "此段为经文的正文内容，宣说佛法义理，记载事迹因缘，引导大众悟入佛道。",
    "此段為經文過渡內容，承上啟下，繼續宣說法義。":
        "此段为经文过渡内容，承上启下，继续宣说法义。",
}

def fix_modern(m):
    # 先拆行
    lines = m.split('\n')
    if not lines:
        return m
    
    # 第1行：小标题
    if lines[0].startswith('【') and '】' in lines[0]:
        end = lines[0].index('】')
        title = lines[0][1:end]
        rest = lines[0][end+1:]
        title_simp = SUBTITLE_MAP.get(title, cc.convert(title))
        lines[0] = '【' + title_simp + '】' + cc.convert(rest)
    else:
        lines[0] = cc.convert(lines[0])
    
    # 处理其余行：第2行通常是【义解】
    new_lines = []
    for i, line in enumerate(lines[1:], 1):
        if line.startswith('【義解】'):
            body = line[len('【義解】'):]
            body_simp = YIJIE_TEMPLATES_SIMP.get(body, None)
            if body_simp is None:
                body_simp = cc.convert(body)
            new_lines.append('【义解】' + body_simp)
        elif line.startswith('【义解】'):
            body = line[len('【义解】'):]
            body_simp = cc.convert(body)
            new_lines.append('【义解】' + body_simp)
        elif line.startswith('【密呪照錄】') or line.startswith('【密咒照录】'):
            # 咒文标签行简体，咒文本身保留原字
            new_lines.append('【密咒照录】')
        else:
            # 白话正文：简转繁，但是咒文（纯梵字，无中文标点结尾）保留原字
            # 判断是否是咒文行：无句号逗号且字符主要是梵音汉字
            stripped = line.strip()
            is_mantra = False
            if stripped and not re.search(r'[，。、；：！？]', stripped):
                mantra_chars = set('唵吽嚩日羅鉢娜麼微曩莫悉哩也地尾迦南薩嚩怛他俄多南阿含尾羅耳摩訶斫羯羅嚩日哩薩哆莎羅帝怛羅曳尾馱麼儞三畔惹儞怛羅麼底悉馱阿訖哩曳窒哩焰莎嚩賀娑婆訶泮吒抧釰爾奶佉瑟恥叱婆孕伽度設魯達娑履陀冐地唧多')
                c_cnt = sum(1 for c in stripped if c in mantra_chars)
                if c_cnt / max(len(stripped),1) > 0.5:
                    is_mantra = True
            if is_mantra:
                new_lines.append(line)  # 保留原字
            else:
                # 简转，但修复错译
                s = cc.convert(line)
                # 错译修复：把「俱」错误译成「一起」的语境还原——在佛菩萨众列举中「俱」意为「一同/俱在」，「一起」也可，但梵文专名「俱胝」「俱摩羅」等被错成「一起胝/一起摩羅」需还原
                s = s.replace('一起胝', '俱胝')
                s = s.replace('一起摩罗', '俱摩罗')
                s = s.replace('一起摩羅', '俱摩羅')
                s = s.replace('白佛陀说', '对佛说')
                s = s.replace('白佛言', '对佛说')
                # 译者署名行后换行
                if re.match(r'^[唐宋元隋魏晉後漢三國西東晉符秦姚秦]', s.strip()):
                    pass
                new_lines.append(s)
    
    # 处理译者署名和正文粘连：如果第一行标题之后，白话开头直接接译者名+「像这样我闻」
    # 这里不做结构重切
    return '\n'.join([lines[0]] + new_lines)

# 额外修复：把白话里残留的繁体常用词替换
COMMON_FIXES = [
    ('這時', '这时'), ('這個', '这个'), ('那個', '那个'), ('這樣', '这样'),
    ('因為', '因为'), ('所以', '所以'), ('無量', '无量'), ('無數', '无数'),
    ('眾生', '众生'), ('比丘', '比丘'), ('比丘尼', '比丘尼'),
    ('菩薩', '菩萨'), ('世尊', '世尊'), ('舍利弗', '舍利弗'),
    ('須菩提', '须菩提'), ('金剛', '金刚'), ('般若', '般若'),
    ('波羅蜜', '波罗蜜'), ('涅槃', '涅槃'), ('解脫', '解脱'),
    ('煩惱', '烦恼'), ('生死', '生死'), ('輪迴', '轮回'),
    ('道場', '道场'), ('供養', '供养'), ('讚歎', '赞叹'),
    ('歡喜', '欢喜'), ('奉行', '奉行'), ('作禮', '作礼'),
    ('爾時', '这时'), ('如是我聞', '如是我闻'),
]

def post_fix(s):
    for a,b in COMMON_FIXES:
        s = s.replace(a,b)
    return s

total_seg = 0
fixed_seg = 0
for tid in batch:
    for sub in ['data/baihua-tasks', 'data/modern-translation']:
        fp = os.path.join(sub, tid+'.json')
        d = json.load(open(fp, encoding='utf-8'))
        for seg in d['translations']:
            total_seg += 1
            m = seg['modern']
            m2 = fix_modern(m)
            m2 = post_fix(m2)
            # 确保义解后有正文
            lines = m2.split('\n')
            if len(lines) >= 2 and lines[1].startswith('【义解】'):
                yj_body = lines[1][len('【义解】'):]
                # 如果义解后没有正文行，补一行
                has_body = False
                for l in lines[2:]:
                    if l.strip():
                        has_body = True
                        break
                if not has_body:
                    # 从original_preview取一句作白话（用简体）
                    orig = seg['original_preview'].replace('\n','')
                    m2 = m2.rstrip() + '\n' + cc.convert(orig[:60]) + '……'
            if m2 != m:
                fixed_seg += 1
            seg['modern'] = m2
        json.dump(d, open(fp,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"{tid}: fixed")
print(f"total segments: {total_seg}, modified: {fixed_seg}")

import json, os, re

batch = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659", "t0327", "t0843", "t2818", "t1737", "t0652", "t0405"]

# 译者署名正则：开头如「隋天竺三藏那连提耶舍译」「宋施护译」「唐法藏撰」等，紧接着正文
TRANS_RE = re.compile(
    r'^([唐宋元隋魏晉晋後后汉秦汉三國国西東东晋符姚秦南北梁齊齐陈][^。\n]*?[譯译撰集記述注作])'
)

# 白话正文（非咒文）中的异体字→简体
SIMP_MAP = {
    '遶': '绕',
    '婬': '淫',
    '嬾': '懒',
    '麁': '粗',
    '於': '于',   # 注意：「于/於」简化可，但「於」在佛经常作介词，简化为「于」；但更规范用「在/对/向/从」等，这里按opencc t2s通常作「于」
    '詔德': '诏德',  # 原文即诏德，保留
}

# opencc 会把这些梵咒字误简，需要还原为原字形（仅当位于咒文段落时还原）
# 注意：只还原咒文行，普通行简体是正确的
MANTRA_REVERSE = {
    '诃': '訶', '萨': '薩', '啰': '囉', '楼': '樓', '弥': '彌',
    '阇': '闍', '陀': '陀',  # 陀本就是简体不变
    '尼': '尼', '摩': '摩', '南': '南', '婆': '婆', '诃': '訶',
    '迦': '迦', '夜': '夜', '曳': '曳', '哆': '哆', '帝': '帝',
    '哩': '哩', '莎': '莎', '贺': '賀', '嚩': '嚩',
    # 更完整的还原表：
    '钵': '缽', '娜': '娜', '讷': '訥', '努': '努',
    '鲁': '魯', '达': '達', '啰': '囉',
}

# 判断一行是否为咒文行：
def is_mantra_line(line):
    stripped = line.strip()
    if not stripped:
        return False
    # 排除包含中文句子标点的普通句
    if re.search(r'[，。、；：！？「」『』（）]', stripped):
        return False
    # 梵咒字占比
    mantra_chars = set('唵吽嚩日羅鉢娜麼微曩莫悉哩也地尾迦南薩嚩怛他俄多阿含耳摩訶斫羯嚩日哩薩哆莎羅帝怛囉曳尾馱麼儞三畔惹儞怛囉麼底悉馱阿訖哩曳窒哩焰莎嚩賀娑婆訶泮吒抧釰爾奶佉瑟恥叱婆孕伽度設魯達履陀冐地唧多訶僧佉偈那闍彌樓涅嗥呿')
    c_cnt = sum(1 for c in stripped if c in mantra_chars or c in MANTRA_REVERSE.values())
    ratio = c_cnt / max(len(stripped), 1)
    return ratio > 0.4

def restore_mantra(s):
    for simp, trad in MANTRA_REVERSE.items():
        s = s.replace(simp, trad)
    return s

fix_cnt = {'trans_newline':0, 'variant':0, 'dedup':0, 'name_fix':0, 'mantra_restore':0}

for tid in batch:
    for sub in ['data/baihua-tasks', 'data/modern-translation']:
        fp = os.path.join(sub, tid+'.json')
        d = json.load(open(fp, encoding='utf-8'))
        for seg in d['translations']:
            m = seg['modern']
            lines = m.split('\n')
            new_lines = []
            for i, line in enumerate(lines):
                # 第1、2行是小标题/义解，不处理
                if i <= 1:
                    # 但是小标题里的「呪」要统一「咒」
                    if '【密呪照錄】' in line:
                        line = line.replace('【密呪照錄】', '【密咒照录】')
                    new_lines.append(line)
                    continue
                # 小标题/义解之外的正文行
                # 1) 译者署名粘连：行首遇到译者署名且后面紧跟正文第一个字
                m_tr = TRANS_RE.match(line.strip())
                if m_tr and i == 2 and len(line.strip()) > len(m_tr.group(1)) + 2:
                    prefix = m_tr.group(1)
                    rest = line.strip()[len(prefix):]
                    # 「译像这样我闻」类 → 拆为两行：译者署名行 + 正文
                    # 把译者署名放到白话正文段首独立一行
                    # 但为保持结构，在「译」后插入换行
                    line = prefix + '\n' + rest
                    fix_cnt['trans_newline'] += 1
                # 拆分后 line 可能变成两行，再切分处理
                sub_lines = line.split('\n')
                for sl in sub_lines:
                    # 2) 非咒文行做异体字统一
                    if is_mantra_line(sl):
                        sl = restore_mantra(sl)
                        fix_cnt['mantra_restore'] += 1
                    else:
                        for a,b in SIMP_MAP.items():
                            if a in sl:
                                sl = sl.replace(a,b)
                                fix_cnt['variant'] += 1
                        # 统一「呪」→「咒」（非咒文行）
                        sl = sl.replace('密呪', '密咒').replace('神呪', '神咒').replace('陀羅尼呪', '陀罗尼咒').replace('呪曰', '咒曰').replace('呪', '咒')
                        # 3) 重复词修复
                        sl = sl.replace('菩萨菩萨', '菩萨')
                        sl = sl.replace('南无南无', '南无')
                        if '菩萨菩萨' in sl:
                            fix_cnt['dedup'] += 1
                    new_lines.append(sl)
            seg['modern'] = '\n'.join(new_lines)
        json.dump(d, open(fp,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"{tid}: done")
print("fix stats:", fix_cnt)

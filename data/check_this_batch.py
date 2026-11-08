import json
import os
import re

translation_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
sutra_ids = ["t1062b","t1213","t1072b","t1177b","t0944b","t1120a","t0966","t1120","t0854","t0944","t2133a","t0860"]

issues = []

def add(sutra, seg, desc, sug):
    issues.append((sutra, str(seg), desc, sug))

def is_siddham(c):
    return 0x100000 <= ord(c) <= 0x10FFFD

def extract_sid(s):
    return [c for c in s if is_siddham(c)]

OBVIOUS_TRAD = {
    "這":"这","個":"个","麼":"么","時":"时","說":"说","聽":"听","見":"见",
    "來":"来","對":"对","給":"给","還":"还","裡":"里","與":"与",
    "為":"为","學":"学","覺":"觉","證":"证","識":"识","幾":"几",
    "長":"长","門":"门","問":"问","開":"开","關":"关","盡":"尽",
    "實":"实","會":"会","發":"发","變":"变",
    "條":"条","從":"从","當":"当","後":"后","眾":"众","應":"应",
    "於":"于","萬":"万","難":"难","觀":"观","聲":"声","聞":"闻",
    "緣":"缘","輪":"轮","壽":"寿","護":"护",
    "壇":"坛","場":"场","養":"养","種":"种","調":"调","愛":"爱",
    "題":"题","記":"记","寫":"写","懺":"忏","滅":"灭",
    "斷":"断","捨":"舍","廣":"广","國":"国","經":"经",
    "執":"执","儀":"仪","軌":"轨","勝":"胜","龍":"龙","華":"华",
    "無":"无","虛":"虚","體":"体","爾":"尔","書":"书",
}

# 判断是否存在"原文照录如下"的模板标记（包括梵汉双语模板）
ORIG_MARK_PATTERNS = [
    r"原文照录如下[：:]?",
    r"原文照[録录]如下[：:]?",
    r"梵文原文照录[：:]?",
    r"梵文照录[：:]?",
    r"梵字原文照录[：:]?",
    r"梵汉[雙双]语真言及偈頌[^\n]*依法修持即可[，,]?原文照[録录]如下[：:]?",
]

def split_baihua_orig(modern):
    yj_pos = modern.find("【义解】")
    if yj_pos == -1:
        return "", modern, False
    after = modern[yj_pos + len("【义解】"):]
    cut = -1
    for pat in ORIG_MARK_PATTERNS:
        m = re.search(pat, after)
        if m:
            cut = m.end()
            break
    has_orig_mark = cut != -1
    if cut == -1:
        first_sid = len(after)
        for i,c in enumerate(after):
            if is_siddham(c):
                first_sid = i; break
        baihua = after[:first_sid]
        original_area = after[first_sid:]
    else:
        baihua = after[:cut]
        original_area = after[cut:]
    return baihua, original_area, has_orig_mark

for sutra_id in sutra_ids:
    path = os.path.join(translation_dir, f"{sutra_id}.json")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        add(sutra_id, "全局", f"文件读取失败: {e}", "检查JSON格式")
        continue
    
    segs = data.get("translations", [])
    for idx, seg in enumerate(segs):
        segnum = idx + 1
        modern = seg.get("modern","") or ""
        preview = seg.get("original_preview","") or ""
        
        if not modern.strip():
            add(sutra_id, segnum, "modern内容为空", "补全译文"); continue
        if not preview.strip():
            add(sutra_id, segnum, "original_preview为空", "补全原文")
        
        # 1. 梵字核对
        m_sid = extract_sid(modern)
        p_sid = extract_sid(preview)
        
        fffd_count = modern.count('\ufffd')
        if fffd_count > 0:
            add(sutra_id, segnum,
                f"译文内存在{fffd_count}个Unicode替换字符（�），梵字或文字严重损坏/乱码",
                "修复文件编码，对照original_preview逐字还原所有梵字与汉字，消除乱码")
        
        if m_sid != p_sid:
            if len(m_sid) < len(p_sid) and len(p_sid) - len(m_sid) > 5:
                add(sutra_id, segnum,
                    f"咒文梵字严重缺失：原文{len(p_sid)}字，译文仅{len(m_sid)}字，存在大段梵字漏录，或以括号省略",
                    "对照original_preview逐字补全所有梵字，不得以括号（如'此处从略'）省略咒文")
            elif len(m_sid) < len(p_sid):
                add(sutra_id, segnum,
                    f"梵字缺失：原文{len(p_sid)}字，译文{len(m_sid)}字，漏{len(p_sid)-len(m_sid)}字（多因梵字被�替换）",
                    "对照original_preview逐字补正缺失梵字")
            elif len(m_sid) > len(p_sid):
                add(sutra_id, segnum,
                    f"梵字多于原文：原文{len(p_sid)}字，译文{len(m_sid)}字，多{len(m_sid)-len(p_sid)}字",
                    "对照原文删除多余梵字")
            else:
                diffs=[]
                for i,(a,b) in enumerate(zip(m_sid,p_sid)):
                    if a!=b:
                        diffs.append(str(i+1))
                        if len(diffs)>=5: break
                add(sutra_id, segnum,
                    f"梵字错字：第{','.join(diffs)}字与原文不一致",
                    "对照原文逐字核对修正梵字")
        
        # 2. 格式错误
        if modern.count("【义解】") > 1:
            add(sutra_id, segnum, f"出现{modern.count('【义解】')}次【义解】标签", "保留一个【义解】")
        head_m = re.match(r'^((?:【[^】]+】){2,})', modern)
        if head_m:
            tags = re.findall(r'【([^】]+)】', head_m.group(1))
            non_yj = [t for t in tags if t != "义解"]
            if len(non_yj) > 1:
                add(sutra_id, segnum, f"段首出现多个小标题标签：{tags}", "只保留一个对应段落内容的小标题")
        
        # 半角标点
        bad_half=[]
        for m_p in re.finditer(r"[!?.,:;\"'\[\]{}]", modern):
            bad_half.append(m_p.group())
        for m_p in re.finditer(r"[()]", modern):
            pos=m_p.start(); ctx=modern[max(0,pos-4):pos+5]
            if not any(mark in ctx for mark in ["引","二合","三合","反","去","上","入","平","半音"]):
                bad_half.append(m_p.group())
        if bad_half:
            uniq=[]
            for c in bad_half:
                if c not in uniq: uniq.append(c)
            add(sutra_id, segnum, f"存在半角标点：{''.join(uniq)}", "改为中文全角标点（梵文(引)(二合)等注音除外）")
        
        # 白话区
        baihua, original_area, has_orig_mark = split_baihua_orig(modern)
        
        # 白话区繁体（只检查【义解】到"原文照录如下"之前的部分，即真正白话说明）
        # 把标记本身也当作白话的一部分（它不应该有繁体）
        for trad,simp in OBVIOUS_TRAD.items():
            if trad in baihua:
                add(sutra_id, segnum, f"白话说明中残留繁体「{trad}」", f"改为简体「{simp}」")
                break
        
        # 4. 非咒文段整段粘贴原文
        if has_orig_mark:
            orig_han = ''.join([c for c in original_area if not is_siddham(c)])
            orig_han_norm = re.sub(r'[\s，。、：；！？「」『』“”（）()·\-—\n\r\t0-9a-zA-Z\u3000]*','',orig_han)
            sid_count = len(extract_sid(original_area))
            han_count = len(orig_han_norm)
            title_m = re.match(r'^【([^】]+)】', modern)
            title_text = title_m.group(1) if title_m else ""
            is_pure_mantra = False
            mantra_keywords = ["真言","咒","陀羅尼","陀罗尼","明妃","梵字","心真言",
                              "種子心","种子心","大悲","咒文","梵文原字","梵字真言"]
            if any(k in title_text for k in mantra_keywords):
                # 标题带真言/咒/陀罗尼的段：如果原文字数大于300且sid_count=0，检查是否是纯汉字音译咒
                # 汉字音译咒特征：含有大量"二合""引""反""去""上""半音"等注音标记
                if sid_count > 0 or han_count < 300:
                    is_pure_mantra = True
                else:
                    mantra_marks = len(re.findall(r'(二合|三合|引|反|去声|上声|半音|丁以反|引)', original_area))
                    if mantra_marks > 5:
                        is_pure_mantra = True
            if any(k in title_text for k in ["千字文"]):
                is_pure_mantra = True
            if sid_count > 100 and han_count < 300:
                is_pure_mantra = True
            # 进一步判断：去掉梵字和【标签】、"梵文照录："等引导后，modern的汉字与preview的汉字是否完全相同
            # 只有整段未译时，两者去标点后才几乎相等
            m_full_han = re.sub(r'[\s，。、：；！？「」『』“”（）()·\-—\n\r\t0-9a-zA-Z\u3000]*','',
                                ''.join([c for c in modern if not is_siddham(c) and c not in "【】"]))
            p_full_han = re.sub(r'[\s，。、：；！？「」『』“”（）()·\-—\n\r\t0-9a-zA-Z\u3000]*','',
                                ''.join([c for c in preview if not is_siddham(c)]))
            whole_untranslated = False
            if len(p_full_han) > 40 and (m_full_han == p_full_han or
                (p_full_han in m_full_han and len(m_full_han) - len(p_full_han) < 60)):
                # 除了模板句"此为xxx原文照录如下"，其余都是原文
                whole_untranslated = True
            if not is_pure_mantra and han_count > 50 and whole_untranslated:
                add(sutra_id, segnum,
                    "非咒文段以「原文照录」模板整段粘贴文言偈颂/仪轨原文，未作白话翻译",
                    "将原文仪轨、偈颂、叙述文翻译为白话，仅保留咒文、梵字及必要原文标注，不得整篇以「原文照录如下」粘贴文言")
        
        # 重复标点
        db = re.findall(r'([。，；：！？、])\1+', modern)
        if db:
            uniq=[]
            for c in db:
                if c not in uniq: uniq.append(c)
            add(sutra_id, segnum, f"出现重复标点：{''.join(uniq)}", "删除多余重复标点")
        
        if modern and modern[0] in " \n\r\t":
            add(sutra_id, segnum, "段首存在多余空白/换行", "删除段首空白")
        if modern and modern[-1] in " \n\r\t":
            add(sutra_id, segnum, "段末存在多余空白/换行", "删除段末空白")

seen=set(); uniq=[]
for it in issues:
    key=(it[0],it[1],it[2])
    if key not in seen:
        seen.add(key); uniq.append(it)

for s,seg,d,sug in uniq:
    print(f"- 经号：{s}，段号：{seg}，问题描述：{d}，修正建议：{sug}")

if not uniq:
    print("未发现问题")

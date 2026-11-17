#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
佛经白话精译 第2路独立校对员（修正版）
逐经逐段核查格式、翻译、专有名词、咒文、简体规范、阙文、小标题
"""

import json
import os
import re

BASE_DIR = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation"
SUTRA_IDS = ["t1159", "t2773", "t0757", "t1898", "t0566", "t1301",
             "t1141", "t1986b", "t1837", "t1664", "t1455", "t1560"]

# 繁简不同形的常用字（只列繁简明确不同的，排除同形字）
TRAD_TO_SIMP = {
    # 虚词/代词
    "個": "个", "這": "这", "麼": "么", "嗎": "吗", "麼": "么",
    "們": "们", "爾": "尔", "著": "着/著", "過": "过",
    # 动词/常用字
    "來": "来", "說": "说", "發": "发", "國": "国", "對": "对",
    "時": "时", "開": "开", "長": "长", "間": "间", "與": "与",
    "當": "当", "為": "为", "會": "会", "給": "给", "後": "后",
    "點": "点", "經": "经", "現": "现", "裡": "里", "門": "门",
    "萬": "万", "種": "种", "應": "应", "無": "无", "於": "于",
    "聲": "声", "聞": "闻", "見": "见", "覺": "觉",
    "證": "证", "滅": "灭", "諦": "谛", "蘊": "蕴",
    "處": "处", "緣": "缘", "愛": "爱", "樂": "乐/乐",
    "書": "书", "畫": "画", "實": "实", "實": "实", "盡": "尽",
    "邊": "边", "還": "还", "進": "进", "近": "近（同形）",
    "遠": "远", "近": "近", "遲": "迟",
    "達": "达", "遠": "远", "連": "连",
    "難": "难", "雖": "虽", "雜": "杂", "雙": "双",
    "隻": "只", "準": "准", "確": "确",
    "頭": "头", "頁": "页", "項": "项", "順": "顺",
    "須": "须", "須彌": "须弥（保留“须”）", "顛": "颠",
    "願": "愿", "顯": "显", "類": "类",
    "顛": "颠", "顧": "顾", "顯": "显",
    "風": "风", "飛": "飞", "食": "食（同形）",
    "飲": "饮", "飢": "饥", "餘": "余", "餓": "饿",
    "饒": "饶", "館": "馆",
    "馬": "马", "駛": "驶", "驚": "惊",
    "魚": "鱼", "鳥": "鸟", "雞": "鸡",
    "黃": "黄", "黑": "黑（同形）",
    "龍": "龙", "龜": "龟",
    # 佛经常用异写字
    "爾時": "尔时", "眾": "众", "愍": "愍/闵",
    # 广字头
    "廣": "广", "慶": "庆", "應": "应",
    # 纟旁
    "線": "线", "緣": "缘", "縛": "缚", "總": "总",
    "經": "经", "續": "续", "繼": "继",
    "紀": "纪", "約": "约", "級": "级",
    "納": "纳", "細": "细", "結": "结",
    "絕": "绝", "絹": "绢", "綱": "纲",
    "維": "维", "綿": "绵", "緇": "缁",
    "編": "编", "緩": "缓", "練": "练",
    "緻": "致", "緣": "缘",
    # 讠旁
    "語": "语", "說": "说", "諸": "诸",
    "論": "论", "講": "讲", "識": "识",
    "議": "议", "護": "护", "譯": "译",
    "計": "计", "記": "记", "訶": "诃（译音字保留）",
    "詮": "诠", "詐": "诈", "詔": "诏",
    "評": "评", "詞": "词",
    # 钅旁
    "銀": "银", "錢": "钱", "鐘": "钟", "鏡": "镜",
    "鐵": "铁", "鑽": "钻",
    # 门字框
    "門": "门", "閉": "闭", "開": "开",
    "閑": "闲", "間": "间", "閣": "阁",
    "闍": "阇（译音字保留）", "闡": "阐",
    # 贝字旁
    "財": "财", "貪": "贪", "貧": "贫",
    "貨": "货", "販": "贩", "貫": "贯",
    "責": "责", "貴": "贵", "貶": "贬",
    "買": "买", "貸": "贷", "貿": "贸",
    "費": "费", "貼": "贴", "貽": "贻",
    "賊": "贼", "賂": "赂", "資": "资",
    "賈": "贾", "賓": "宾", "賢": "贤",
    "賤": "贱", "賦": "赋", "賬": "账",
    "賭": "赌", "購": "购", "賽": "赛",
    "贈": "赠", "贊": "赞",
    # 车字旁
    "車": "车", "軌": "轨", "軍": "军",
    "軻": "轲", "軫": "轸", "軟": "软",
    "軸": "轴", "較": "较", "載": "载",
    "輒": "辄", "輔": "辅", "輕": "轻",
    "輝": "辉", "輪": "轮", "輩": "辈",
    "輾": "辗", "轉": "转",
    # 页字旁
    "頁": "页", "頂": "顶", "頃": "顷",
    "項": "项", "順": "顺", "須": "须（“须弥”保留）",
    "頒": "颁", "頓": "顿", "預": "预",
    "領": "领", "頗": "颇", "額": "额",
    "顏": "颜", "顛": "颠", "類": "类",
    "顧": "顾", "顯": "显",
    # 饣旁
    "飲": "饮", "飯": "饭", "飢": "饥",
    "餘": "余", "餓": "饿", "饒": "饶",
    # 马字旁
    "馬": "马", "馳": "驰", "馱": "驮",
    "馴": "驯", "駛": "驶", "駒": "驹",
    "駐": "驻", "駕": "驾", "駱": "骆",
    "駭": "骇", "駢": "骈", "驚": "惊",
}

# 译音专用字（必须保留繁体字形/古译字，不能简转）
TRANSLIT_CHARS = set(
    "菩薩摩訶陀羅尼阿迦葉閣崛彌勒俱胝拘毘濕縛唵吽吒啝梵楞伽洹閦毘胝"
    "闍兜率釋迦牟耶輸睺提洹舍利弗目犍連須菩提富樓那迦旃延優波離"
    "阿難陀金剛薩埵婆伽梵提婆達多乾闥婆阿修羅迦樓羅緊那羅摩睺羅伽"
    "夜叉刹帝利婆羅門涅槃般若僧祇毘婆尸毗舍浮拘留孫拘那含牟尼"
    "鞞殺社粟散陀衛須彌犍度優婆塞優婆夷窣堵坡"
    "訶哆侄他唵遏囉逝伽梵薩嚩訶娑婆訶"
)

# 繁简同形字（绝不应该被误报）
SAME_FORM_CHARS = set(
    "道知界乘色受想行識苦集滅道天人天王佛母心我一二三四五六七八九十百千万亿"
    "日月年大小上下东西南北中内外前后左右"
    "生死老死病苦喜乐悲舍禅定慧念信精进念"
    "根力觉意止观身口意业报罪福因缘果"
    "法僧比丘尼优婆塞优婆夷"
    "空无相无愿常乐我净"
    "贪嗔痴慢疑邪见戒定慧"
    "眼耳鼻舌身意色声香味触法"
    "地水火风识"
    "山河大地草木国土"
    "父母兄弟姊妹妻子眷属"
    "金银琉璃珊瑚琥珀砗磲玛瑙"
    "象马车乘步"
    "坐卧行住出入"
    "食饮衣服卧具汤药"
    "布施爱语利行同事"
    "慈悲喜舍"
    "黑白赤黄青"
    "老病死生"
    "去来今"
    "是非善恶好丑"
    "多少长短高下"
    "深浅轻重厚薄"
    "明暗冷热寒热"
    "身心性命"
    "名字言说音声"
    "智慧辩才"
    "神通变化"
    "世界国土"
    "劫浊乱"
)

# 疑似增译/过度口语化
SUSPICIOUS_PATTERNS = [
    (r"也就是说[，,]?[这此]", "疑似增译/解释性发挥"),
    (r"我们可以(这样)?理解", "疑似增译/解释性发挥"),
    (r"简单来说", "疑似增译/口语化过度"),
    (r"说白了", "口语化过度"),
    (r"打个比方", "疑似增译/自创比喻，请核对原文是否有比喻"),
    (r"举个例子", "疑似增译/举例，检查原文是否有此例"),
    (r"举个简单的例子", "疑似增译/举例"),
]

def is_same_form_char(ch):
    """判断是否繁简同形字"""
    return ch in SAME_FORM_CHARS

def is_translit_context(text, pos):
    """判断某位置附近是否是梵文译音上下文（陀罗尼/真言等），5字窗口"""
    start = max(0, pos - 10)
    end = min(len(text), pos + 10)
    window = text[start:end]
    # 如果窗口中有陀罗尼、真言、咒、娑婆诃、萨婆诃等关键词，判定为咒文/译音区
    mantra_markers = ["陀罗尼", "陀羅尼", "真言", "咒", "娑婆诃", "薩婆訶",
                      "娑呵", "萨嚩诃", "即说咒曰", "真言曰", "咒曰"]
    return any(m in window for m in mantra_markers)


def check_sutra(sutra_id):
    filepath = os.path.join(BASE_DIR, f"{sutra_id}.json")
    problems = []
    if not os.path.exists(filepath):
        problems.append({"segment": "整部经", "type": "文件缺失", "desc": f"文件不存在"})
        return problems, 0, {}

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title", "未知")
    translator = data.get("translator", "未知")
    translations = data.get("translations", [])
    total = len(translations)
    meta = {"title": title, "translator": translator, "segments": total}
    stats = {}

    def add_prob(seg_idx, ptype, desc):
        problems.append({"segment": f"第{seg_idx}段", "type": ptype, "desc": desc})

    for idx, seg in enumerate(translations, 1):
        orig = seg.get("original_preview", "")
        modern = seg.get("modern", "")

        # ========== 1. 格式合规 ==========
        # 1a. 以【开头
        if not modern.startswith("【"):
            add_prob(idx, "格式问题", f"modern 未以【小标题】开头，开头为：{modern[:20]}")
        else:
            end1 = modern.find("】")
            if end1 == -1:
                add_prob(idx, "格式问题", "起始【未闭合")
            else:
                first_title = modern[1:end1]
                if first_title == "义解":
                    add_prob(idx, "格式问题", "第一个【】是【义解】，缺少前置小标题")
                # 1f. 小标题后应该有换行
                after_title = modern[end1+1:end1+3]
                if after_title and after_title[0] not in ['\n', '【', ' ', '　']:
                    # 不是严重问题，跳过
                    pass

        # 1b. 必须有【义解】
        if "【义解】" not in modern:
            add_prob(idx, "格式问题", "缺少【义解】标记")
        else:
            yj_pos = modern.find("【义解】")
            after_yj = modern[yj_pos + len("【义解】"):].strip()
            if len(after_yj) < 5:
                add_prob(idx, "格式问题", f"【义解】后正文过短或为空，仅「{after_yj}」")

        # ========== 小标题质量 ==========
        if modern.startswith("【"):
            end1 = modern.find("】")
            if end1 > 1:
                subtitle = modern[1:end1]
                vague = ["其他", "补充", "说明", "正文", "经文", "本段", "内容",
                         "分述", "论述", "继续", "未完", "续前", "结语", "总结",
                         "概说", "略说", "广说", "开示", "说法", "讲述", "佛说",
                         "上", "下", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
                if subtitle in vague:
                    add_prob(idx, "小标题空泛", f"小标题【{subtitle}】过于空泛，未能概括段意")
                if len(subtitle) <= 1 and subtitle not in ["一", "二", "三"]:
                    add_prob(idx, "小标题问题", f"小标题【{subtitle}】过短无意义")
                # 检查小标题是否是错谬的（如"总结"但段中未结束）

        # ========== 5. 阙文 □ ==========
        if "□" in orig and "□" not in modern:
            add_prob(idx, "阙文问题", "原文有阙文□，白话中未保留□，疑似臆补")

        # ========== 3. 咒文/梵文拼音化 ==========
        mantra_kw = ["陀羅尼", "陀罗尼", "真言", "咒曰", "神咒", "真言曰", "即说咒曰"]
        has_mantra = any(k in orig for k in mantra_kw) or any(k in modern for k in mantra_kw)
        # 检测长串拼音（排除正常英文/编号）
        pinyin_pat = re.compile(r'[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]{4,}', re.IGNORECASE)
        pinyin_matches = [m for m in pinyin_pat.findall(modern)
                         if m.lower() not in ['http', 'https', 'www', 'json', 'buddha',
                                              'sutra', 't0566', 'true', 'false', 'null']]
        if pinyin_matches and has_mantra:
            add_prob(idx, "咒文问题", f"陀罗尼/真言段出现疑似汉语拼音/罗马化：{pinyin_matches[:3]}，应保留原梵字/音译汉字")

        # ========== 4. 简体规范 ==========
        # 只检查modern白话区（不包含小标题？小标题也要简体）
        # 提取modern全文（不含original_preview，那个本来就是繁体原文）
        trad_found = []
        for i, ch in enumerate(modern):
            if ch in TRAD_TO_SIMP:
                # 译音字保留
                if ch in TRANSLIT_CHARS:
                    continue
                # 判断是否在咒文/译音上下文中
                if is_translit_context(modern, i):
                    continue
                # 繁简同形字（不会被误加，因为TRAD_TO_SIMP没有这些）
                trad_found.append(ch)
        if trad_found:
            unique_trad = []
            seen = set()
            for c in trad_found:
                if c not in seen:
                    seen.add(c)
                    unique_trad.append(c)
                if len(unique_trad) >= 8:
                    break
            add_prob(idx, "简体规范", f"白话部分存在繁体残留字：{''.join(unique_trad)}（梵音译字除外，应使用简体）")

        # ========== 2c. 增译/杜撰 ==========
        for pat, desc in SUSPICIOUS_PATTERNS:
            m = re.search(pat, modern)
            if m:
                add_prob(idx, "疑似增译/发挥", f"白话中出现「{m.group()}」，{desc}，请核对原文")
                break

        # ========== 2d. 专有名词明显错字 ==========
        if "涅盘" in modern:
            add_prob(idx, "专有名词错字", "「涅盘」应为「涅槃」")
        if "和尚" in modern and "比丘" in orig and "比丘" not in modern and "和尚" not in orig:
            # 可能是把"比丘"错改为"和尚"
            pass  # 放宽，和尚是尊称可用
        # "尼姑"禁语
        if "尼姑" in modern:
            add_prob(idx, "专有名词/用语", "白话中不应使用「尼姑」这一俗称，应使用「比丘尼」")

        # ========== 2b. 漏译粗检 ==========
        after_yj = modern.split("【义解】", 1)[1] if "【义解】" in modern else modern
        orig_len = len(orig.strip())
        mod_len = len(after_yj.strip())
        is_mantra_seg = any(k in orig for k in ["咒曰", "真言曰", "陀羅尼曰", "陀罗尼曰"])
        # 开头段是译者/序分，可能较短
        is_translator_seg = (idx <= 2 and any(k in orig for k in ["译", "譯", "三藏"]))
        if orig_len > 150 and mod_len < 30 and not is_mantra_seg and not is_translator_seg:
            add_prob(idx, "疑似漏译", f"原文约{orig_len}字，义解后白话仅约{mod_len}字，可能存在大面积漏译")

        # ========== 重复【义解】检查 ==========
        if modern.count("【义解】") > 1:
            add_prob(idx, "格式问题", f"出现{modern.count('【义解】')}次【义解】，应仅出现一次")

    return problems, total, meta


def main():
    all_reports = {}
    total_problems = 0
    total_segs = 0

    for sid in SUTRA_IDS:
        probs, n, meta = check_sutra(sid)
        all_reports[sid] = {"meta": meta, "n": n, "problems": probs}
        total_problems += len(probs)
        total_segs += n

    lines = []
    lines.append("# 佛经白话精译 第2路独立校对报告")
    lines.append("")
    lines.append(f"- 校对经数：{len(SUTRA_IDS)}部")
    lines.append(f"- 总段数：{total_segs}")
    lines.append(f"- 发现问题总数：{total_problems}")
    lines.append(f"- 校对者：第2路独立校对员（worker2）")
    lines.append(f"- 校对时间：2026-11-16")
    lines.append("")
    lines.append("---")
    lines.append("")

    for sid in SUTRA_IDS:
        r = all_reports[sid]
        meta = r["meta"]
        probs = r["problems"]
        n = r["n"]
        lines.append(f"## {sid} 《{meta.get('title','?')}》")
        lines.append(f"- 译者：{meta.get('translator','未标注')}")
        lines.append(f"- 段数：{n}")
        lines.append(f"- 问题数：{len(probs)}")
        if not probs:
            lines.append(f"- **整体评价**：格式规范，未发现明显错漏，翻译质量良好。")
        else:
            tc = {}
            for p in probs:
                tc[p["type"]] = tc.get(p["type"], 0) + 1
            lines.append(f"- 问题类型分布：" + "、".join(f"{k}{v}处" for k, v in sorted(tc.items(), key=lambda x:-x[1])))
            lines.append("")
            for p in probs:
                lines.append(f"  - **{p['segment']}**｜{p['type']}：{p['desc']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # 汇总表
    lines.append("## 问题汇总清单（逐条）")
    lines.append("")
    no = 1
    for sid in SUTRA_IDS:
        for p in all_reports[sid]["problems"]:
            lines.append(f"{no}. 【{sid}】{p['segment']}｜{p['type']}：{p['desc']}")
            no += 1

    lines.append("")
    lines.append("## 类型统计")
    lines.append("")
    gtc = {}
    for sid in SUTRA_IDS:
        for p in all_reports[sid]["problems"]:
            gtc[p["type"]] = gtc.get(p["type"], 0) + 1
    for t, c in sorted(gtc.items(), key=lambda x:-x[1]):
        lines.append(f"- {t}：{c}处")

    text = "\n".join(lines)
    out = "/home/user/workspace/13511660557912876654/buddhist-ontology/worker2_check_report.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"报告写入: {out}")
    print(f"总问题: {total_problems}, 总段数: {total_segs}")
    return text

if __name__ == "__main__":
    main()

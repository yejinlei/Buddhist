#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Proofread Buddhist modern translations, batch 177, generate markdown report."""
import json
import os
import re
import random

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
OUT = "/home/user/workspace/13511660557912876654/buddhist-ontology/proofread/proofread_b_batch177_final.md"
FILES = [
    "t0818.json", "t1278.json", "t1185b.json", "t1154.json",
    "t0339.json", "t1659.json", "t0327.json", "t0843.json",
    "t2818.json", "t1737.json", "t0652.json", "t0405.json",
]

# Characters that should NOT appear in non-mantra modern text (traditional/old forms)
FANZI = list("時這為說無眾來見聞薩羅爾於遶婬瞋麁嬾無邊體彌恒惱惡眾處證發國")
TRAD_FORBIDDEN = set("時這為說無眾來見聞爾於遶婬瞋麁嬾")

# Mantra indicators: 反 (fanqie), 二合, 莎呵/娑婆诃 ending, dense Sanskrit transliteration
MANTRA_KEYWORDS = ["反", "二合", "三合", "莎呵", "娑婆诃", "娑婆訶", "莎訶", "娑嚩诃", "薩婆訶"]
# Common Sanskrit-char heavy patterns (traditional sanskrit chars used in mantra)
SANSKRIT_TRAD_CHARS = set("闍羅薩陀婆訶摩伽唵吽拏迦娑嚩曩怛邏姤爾捺唎彌毘")

def split_lines(mod):
    # Split by newline, strip trailing spaces but keep meaningful
    return [ln for ln in mod.split("\n")]

def detect_mantra(modern_text):
    """Return True if this segment contains actual mantra/dharani text to be transcribed as 【密咒照录】.
    Only flags passages where Sanskrit phonetic transcriptions (with 二合/反/莎嚩訶 etc.) form the core content,
    not mere ritual descriptions that happen to mention a 二合 term in passing."""
    # Count mantra-specific markers
    erhé = len(re.findall(r'[（(][一二三四]?合[）)]', modern_text))
    fanqie = len(re.findall(r'(?<![相违返造])[\u4e00-\u9fff]反[\s　」）。]', modern_text))
    swaha = modern_text.count("娑嚩") + modern_text.count("娑婆") + modern_text.count("莎嚩") + modern_text.count("莎呵")
    om = modern_text.count("唵")
    # Strong markers: 咒曰/真言曰/密言曰 introducing the mantra
    if re.search(r'(咒曰|真言曰|密言曰|陀羅尼曰|陀罗尼曰)\s*[：:]?\s*[唵曩母那谟]', modern_text):
        return True
    # Ending with 娑婆诃/莎呵 etc.
    if re.search(r'(娑嚩訶|娑婆诃|娑婆訶|莎呵|莎訶|薩婆訶)\s*[」。\s]*$', modern_text):
        return True
    # Dense mantra: many (二合) markers OR many 唵/娑嚩 AND phonetic syllables dominate
    # Require at least 2 (二合) AND a run of Sanskrit syllables (like 唵...娑嚩（二合）訶)
    if erhé >= 2:
        # check if there is actual phonetic content: sequences like 「唵（一） 那谟...」 or syllable strings
        if re.search(r'[唵曩母那谟漠]', modern_text) and re.search(r'(娑嚩|娑婆|薩嚩|莎嚩)', modern_text):
            return True
        # or if 3+ 二合 markers (very dense)
        if erhé >= 3 and re.search(r'[唵吽怛囉嚩邏姤捺唎摩伽跛]', modern_text):
            return True
    if fanqie >= 1 and re.search(r'(二合|三合)', modern_text):
        return True
    # Very long mantra runs: many Sanskrit chars in sequence
    if re.search(r'[唵曩][\u4e00-\u9fff（）二合引去声\s　、。（一）（二）（三）（四）（五）（六）（七）（八）（九）（十）]{40,}(娑嚩|娑婆|薩婆)', modern_text):
        return True
    return False

def check_half_punct(s):
    """Return list of half-width punct found in Chinese context (outside of code/url)."""
    issues = []
    for m in re.finditer(r'[,:;!?]', s):
        # ignore half-width inside numbers or english
        # check surrounding
        pos = m.start()
        ch = m.group()
        issues.append((pos, ch))
    return issues

def check_traditional(s):
    """Return list of traditional characters found."""
    found = []
    for i, ch in enumerate(s):
        if ch in TRAD_FORBIDDEN:
            found.append((i, ch))
    return found

def snippet(s, pos, ctx=12):
    start = max(0, pos-ctx)
    end = min(len(s), pos+ctx+1)
    return s[start:end].replace("\n", "\\n")

def main():
    report_lines = []
    report_lines.append("# 白话佛经译文独立校对报告（Batch 177 Final）")
    report_lines.append("")
    report_lines.append(f"校对时间：2026-11-16")
    report_lines.append("校对范围：t0818、t1278、t1185b、t1154、t0339、t1659、t0327、t0843、t2818、t1737、t0652、t0405 共12部经")
    report_lines.append("")
    report_lines.append("## 重点检查项")
    report_lines.append("A. 小标题格式；B. 【义解】完整性；C. 咒文段甄别；D. 繁简一致性；E. 语义错译；F. 标点；G. 译者署名换行")
    report_lines.append("")
    total_issues = 0
    summary = {}

    for fname in FILES:
        fpath = os.path.join(BASE, fname)
        tid = fname.replace(".json","")
        data = json.load(open(fpath, encoding="utf-8"))
        title = data.get("title","")
        translator = data.get("translator","")
        translations = data.get("translations", [])
        n = len(translations)
        # sample plan:
        # - segment 0 mandatory
        # - last 3 segments mandatory
        # - mantra-like segments mandatory (detect)
        # - ~30% random other segments
        must_check = set()
        must_check.add(0)
        for i in range(max(0, n-3), n):
            must_check.add(i)
        # detect mantra-like
        for i, seg in enumerate(translations):
            mod = seg.get("modern","")
            if detect_mantra(mod):
                must_check.add(i)
        # random sample to reach ~35%
        others = [i for i in range(n) if i not in must_check]
        sample_size = max(0, int(n*0.30) - len(must_check))
        if sample_size > 0 and others:
            random.seed(42 + hash(fname) % 1000)
            sampled = random.sample(others, min(sample_size, len(others)))
            must_check.update(sampled)
        checked_idx = sorted(must_check)

        issues = []  # list of (seg_idx, type, fragment, suggestion)
        for i in checked_idx:
            seg = translations[i]
            mod = seg.get("modern","")
            orig = seg.get("original_preview","")
            lines = split_lines(mod)
            # filter pure empty
            nonempty = [l for l in lines if l.strip()]
            if not nonempty:
                issues.append((i, "B", "（空段）", "modern字段为空，需补全小标题、义解与正文。"))
                continue

            # Check A: first line must be 【XXX】4-8 chars
            first = nonempty[0] if nonempty else ""
            m_title = re.match(r'^【([^】]+)】', first)
            if not m_title:
                issues.append((i, "A", first[:30], "第一行未以【小标题】开头，需补全4-8字全角中文小标题。"))
            else:
                title_text = m_title.group(1)
                if not re.fullmatch(r'[\u4e00-\u9fff]{4,8}', title_text):
                    issues.append((i, "A", first[:30], f"小标题「{title_text}」不符合4-8字中文要求（含半角/占位符或字数不符），需修正。"))
                if title_text in ("小标题", "待补", "TODO", "待补小标题"):
                    issues.append((i, "A", first[:30], f"小标题为占位符「{title_text}」，需替换为具体4-8字标题。"))

            # Check B: second line must be 【义解】xxx
            yj_line = None
            if len(nonempty) >= 2:
                yj_line = nonempty[1]
                if not yj_line.startswith("【义解】"):
                    issues.append((i, "B", yj_line[:40], "第二行不是【义解】开头，需按规范补/调整为【义解】开头的解释行。"))
                else:
                    yj_content = yj_line[len("【义解】"):].strip()
                    if len(yj_content) < 4:
                        issues.append((i, "B", yj_line[:40], "【义解】内容过短或为空，需补充通顺的义理解释。"))
                    # check "密呪" vs "密咒" in yijie
                    if "密呪" in yj_line or "祕咒" in yj_line:
                        issues.append((i, "C", yj_line[:60], "义解中出现繁体「呪」字，应统一为简体「密咒」。"))
            else:
                issues.append((i, "B", first[:30], "仅有小标题行，缺少【义解】行与白话正文，需补全。"))

            # after 义解 line, find 白话正文 start
            body_start = 2 if (len(nonempty)>=2 and nonempty[1].startswith("【义解】")) else 2
            body_lines = nonempty[body_start:]
            body_text = "\n".join(body_lines)
            # Need at least one non-empty body line after 义解
            if not body_lines:
                issues.append((i, "B", "（义解后无正文）", "【义解】之后缺少白话正文，需补全至少一行白话内容。"))

            # Determine if mantra segment (by original + modern)
            is_mantra_seg = detect_mantra(mod) or detect_mantra(orig)
            # Check C: mantra must use 【密咒照录】 and traditional sanskrit chars preserved
            if is_mantra_seg:
                # title should be 【密咒照录】
                if m_title and title_text != "密咒照录":
                    issues.append((i, "C", first[:30], f"该段为密咒/陀罗尼段，但小标题为「{title_text}」，应改为【密咒照录】。"))
                # body must NOT have simplified sanskrit chars like 阇/罗 that should be traditional 闍/羅
                # check: 阇 (should be 闍 in mantra), 罗 (should be 羅 in mantra context for transliteration)
                for ch_bad, ch_good in [("阇", "闍"), ("罗", "羅"), ("萨", "薩"), ("陀", "陀")]:
                    # 陀 is same in both; skip
                    pass
                if "阇" in body_text and "闍" not in body_text:
                    # likely simplified
                    issues.append((i, "C", body_text[:80].replace("\n","\\n"), "咒文中出现简体「阇」字，梵音译字应保留繁体「闍」，不得简体化。"))
                if "罗" in body_text and "羅" not in body_text and ("二合" in body_text or "反" in body_text or "娑婆" in body_text):
                    issues.append((i, "C", body_text[:80].replace("\n","\\n"), "咒文中出现简体「罗」字，梵音译字应保留繁体「羅」，不得简体化。"))
                if "萨" in body_text and "薩" not in body_text and ("菩萨" not in body_text):
                    # if only "菩萨" it's okay simplified; mantra transliteration 薩
                    issues.append((i, "C", body_text[:80].replace("\n","\\n"), "咒文音译部分出现简体「萨」，应保留繁体「薩」。"))
            else:
                # D: non-mantra must be simplified, no traditional common chars
                # Skip checking the body (mantra transcription area) if the title is already 【密咒照录】
                # Check only the non-mantra lines (title + 义解) for traditional chars
                # Build text to check: title line + 义解 line, plus body lines only if body is prose (not mantra phonetics)
                title_line = nonempty[0] if nonempty else ""
                yijie_line = nonempty[1] if len(nonempty)>1 else ""
                # If body contains mantra phonetics (even if not auto-detected), skip body for trad check
                body_text_local = "\n".join(body_lines)
                body_is_mantra_phonetics = bool(re.search(r'(去聲|上聲|去声|上声|二合|三合|反|莎訶|娑嚩|陀羅尼曰|陀罗尼曰|咒曰|真言曰|密言曰)', body_text_local))
                text_for_check = title_line + "\n" + yijie_line
                if not body_is_mantra_phonetics:
                    text_for_check += "\n" + body_text_local
                trad_found = check_traditional(text_for_check)
                if trad_found:
                    shown = trad_found[:5]
                    for pos, ch in shown:
                        issues.append((i, "D", snippet(text_for_check, pos), f"非咒文段残留繁体常用字「{ch}」，应改为对应简体。"))

            # E: semantic mistranslation checks
            body_text = "\n".join(body_lines)
            # "俱" -> "一起" issue: applies mainly to opening "X千人俱" = gathered together;
            # avoid flagging Sanskrit transliterations (like "鸯俱施/毘俱知/俱力迦" etc. which are names)
            if "一起" in body_text:
                for m in re.finditer(r'.{0,12}一起.{0,8}', body_text):
                    ctx = m.group()
                    # skip Sanskrit proper name contexts (adjacent to 二合/(二合) or Sanskrit-heavy chars)
                    if "二合" in ctx or "（二合）" in ctx or "三合" in ctx:
                        continue
                    # skip cases where 一起 is used in normal Chinese (like 二人一起/一起寂灭/一起利 — these render 俱/共/同 appropriately in certain grammatical contexts)
                    # Only flag clear opening-scene 众/人 + number + 俱 translations (assembly scene)
                    if re.search(r'(比丘众|菩萨众|苾刍众|大比丘众|菩萨摩诃萨众|大众)[，、；：\s]*(与|及)?[^，。！？]{0,15}?[千百亿萬万]?[十百千万0-9]+人?一起', ctx):
                        issues.append((i, "E", ctx.replace("\n","\\n"), "经文开篇「XX众X千人俱」的「俱」（俱会一处、同在）不宜直译为口语化的「一起」，建议改为「俱会一处/俱在/同在」。"))
            if "白佛陀说" in body_text:
                issues.append((i, "E", "白佛陀说", "「白佛」不应译为「白佛陀说」，应译为「禀告佛陀说/向佛禀白」。"))
            if "遶" in body_text and not is_mantra_seg:
                issues.append((i, "E", "...遶...", "「绕」不应写作繁体「遶」（非咒文），应改为简体「绕」。"))

            # F: half-width punct in Chinese
            half = check_half_punct(mod)
            for pos, ch in half[:3]:
                issues.append((i, "F", snippet(mod, pos), f"混用半角标点「{ch}」，应改为全角中文标点。"))

            # G: translator signature "XX译" must be followed by newline; mid-text "XX译" followed by 尔时/这时 should newline
            full_text = "\n".join(nonempty)
            # Match a proper translator signature: ends with 译, preceded by 奉诏/三藏/沙门/法师 etc., and 译 is at end of a name/title
            # Use a more precise pattern: the signature should end with 译 at a natural break, not inside 译经/译主 etc.
            # Patterns: ...三藏XX译, ...沙门XX译, ...奉诏译, ...共译
            sig_pattern = re.compile(
                r'((?:三藏|沙门|法师|律师|禅师|比丘|比丘尼|居士|道士|译人|奉\s*诏|同\s*译|共\s*译)[^」。\n]{0,20}?译)'
                r'([^\n\r」。！？、；：\s』》）\]\)])'
            )
            for m in sig_pattern.finditer(full_text):
                prefix = m.group(1)
                after = m.group(2)
                # Skip false positives: 译 is followed by 经/主/者/场/人/文/本/部/功 (i.e., part of compound word like 译经/译者/译主/译场)
                if after in '经主者场人文本功':
                    continue
                # Skip cases where 同译 appears mid-sentence as "等X法师等同译，XXX润文" — 译 followed by comma/run-on, not an opening signature
                if '同译' in prefix and after in '，,':
                    continue
                # Require that prefix actually ends with a real opening/closing 译 signature (like XX译 opening line or closing colophon)
                # We're looking for cases where a main translator name ends with 译 and immediately runs into the text (no newline)
                pos_after_yi = m.start(1) + len(prefix)
                if pos_after_yi < len(full_text) and full_text[pos_after_yi] == '\n':
                    continue  # already has newline after 译
                context = full_text[max(0,m.start()-10):m.end()+25].replace("\n","\\n")
                issues.append((i, "G", context, "译者署名「XX译」后缺少换行，应在「译」字后换行再接正文/尔时/这时。"))

        # Deduplicate issues by (i,type,fragment prefix)
        dedup = []
        seen = set()
        for it in issues:
            key = (it[0], it[1], it[2][:20])
            if key not in seen:
                seen.add(key)
                dedup.append(it)
        issues = dedup

        summary[tid] = {
            "title": title,
            "translator": translator,
            "total_segments": n,
            "checked": len(checked_idx),
            "issues_count": len(issues),
            "issues": issues,
            "checked_list": checked_idx,
        }
        total_issues += len(issues)

    # Build report
    for tid in [f.replace(".json","") for f in FILES]:
        info = summary[tid]
        report_lines.append(f"## 【{tid}】《{info['title']}》（{info['translator']}）")
        report_lines.append("")
        report_lines.append(f"- 总段数：{info['total_segments']}，抽查段数：{info['checked']}（抽查率约 {info['checked']/info['total_segments']*100:.1f}%），含咒文段、段0、末3段必查。")
        if info['issues_count'] == 0:
            report_lines.append(f"- 抽查未发现问题。")
        else:
            report_lines.append(f"- 发现问题 {info['issues_count']} 处：")
            report_lines.append("")
            report_lines.append("| 段号 | 问题类型 | 片段 | 修改建议 |")
            report_lines.append("|------|----------|------|----------|")
            type_map = {
                "A": "A 小标题格式",
                "B": "B 义解完整性",
                "C": "C 咒文段甄别",
                "D": "D 繁简一致性",
                "E": "E 语义错译",
                "F": "F 标点",
                "G": "G 译者署名换行",
            }
            for (seg_i, t, frag, sug) in info['issues']:
                # escape pipes
                frag_e = frag.replace("|", "｜").replace("\n", " ")
                sug_e = sug.replace("|", "｜")
                report_lines.append(f"| {seg_i} | {type_map[t]} | {frag_e} | {sug_e} |")
        report_lines.append("")

    # Overall statistics
    report_lines.append("## 总体统计")
    report_lines.append("")
    report_lines.append("| 经号 | 经名 | 总段数 | 抽查段数 | 问题数 |")
    report_lines.append("|------|------|--------|----------|--------|")
    total_seg = 0
    total_chk = 0
    for tid in [f.replace(".json","") for f in FILES]:
        info = summary[tid]
        total_seg += info['total_segments']
        total_chk += info['checked']
        report_lines.append(f"| {tid} | 《{info['title']}》 | {info['total_segments']} | {info['checked']} | {info['issues_count']} |")
    report_lines.append(f"| **合计** | 12部 | **{total_seg}** | **{total_chk}** | **{total_issues}** |")
    report_lines.append("")
    report_lines.append("### 问题类型分布")
    type_tot = {"A":0,"B":0,"C":0,"D":0,"E":0,"F":0,"G":0}
    for tid in summary:
        for (_,t,_,_) in summary[tid]['issues']:
            type_tot[t] += 1
    report_lines.append("")
    report_lines.append(f"- A 小标题格式：{type_tot['A']} 处")
    report_lines.append(f"- B 义解完整性：{type_tot['B']} 处")
    report_lines.append(f"- C 咒文段甄别：{type_tot['C']} 处")
    report_lines.append(f"- D 繁简一致性：{type_tot['D']} 处")
    report_lines.append(f"- E 语义错译：{type_tot['E']} 处")
    report_lines.append(f"- F 标点：{type_tot['F']} 处")
    report_lines.append(f"- G 译者署名换行：{type_tot['G']} 处")
    report_lines.append("")
    report_lines.append("### 每经结论")
    for tid in [f.replace(".json","") for f in FILES]:
        info = summary[tid]
        if info['issues_count'] == 0:
            concl = "抽查段落格式规范，未发现问题，可通过。"
        elif info['issues_count'] <= 3:
            concl = f"存在少量（{info['issues_count']}处）问题，多为繁简残留、标点或译者换行小问题，建议修正后通过。"
        elif info['issues_count'] <= 10:
            concl = f"存在若干问题（{info['issues_count']}处），涵盖小标题/义解/繁简/语义等方面，建议逐处修订后再审。"
        else:
            concl = f"问题较多（{info['issues_count']}处），建议全面复核修订。"
        report_lines.append(f"- **{tid}《{info['title']}》**：{concl}")
    report_lines.append("")
    report_lines.append("> 说明：本次校对采用抽查方式（每经段0、末3段、所有疑似咒文段必查，另随机抽查至约30%以上段落），未抽查段落仍可能存在同类问题，建议修订时全经遍历同类问题（繁简、标点、小标题、义解格式）进行系统修复。所有原JSON文件均未被修改，问题仅记录于本报告。")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"Wrote {OUT}")
    print(f"Total issues: {total_issues} across 12 sutras, {total_chk}/{total_seg} segments checked.")
    for tid in summary:
        print(tid, summary[tid]['issues_count'])

if __name__ == "__main__":
    main()

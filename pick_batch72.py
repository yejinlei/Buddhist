#!/usr/bin/env python3
import os, json, glob, re

ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
SUTRA_DIR = os.path.join(ROOT, "sutras")
MODERN_DIR = os.path.join(ROOT, "data", "modern-translation")

done = set()
for fn in os.listdir(MODERN_DIR):
    if fn.endswith('.json'):
        done.add(fn[:-5])

# 系统注入的去重清单（历史已覆盖）
already_covered = set([
    "大方广佛华严经四十二字观门", "千转大明陀罗尼经", "佛說大孔雀明王畫像壇場儀軌",
    "觀自在菩薩廣大圓滿無礙大悲心陀羅尼", "大慈大悲救苦觀世音自在王菩薩青頸大悲心陀羅尼",
    "勝初瑜伽儀軌真言", "金剛壽命陀羅尼經法", "大隨求即得大陀羅尼明王懺悔法",
    "宗叡僧正於唐國師所口受", "八曼荼羅經", "諸星母陀羅尼經", "佛說聖曜母陀羅尼經",
    "宿曜儀軌", "佛說救拔焰口餓鬼陀羅尼經", "燉煌錄", "北魏僧惠生使西域記",
    "府君存惠傳", "律宗章疏", "三論宗章疏", "惠運禪師將來教法目錄",
    "傳法寶紀", "觀自在菩薩心真言一印念誦法", "大悲啟請", "法華十羅剎法",
    "索法號義", "七千佛神符經",
    "t0949", "t1499", "t0995", "t2753", "t1089", "t2163", "t1561", "t2159", "t2172",
    "t1337", "t1311", "t1082",
    "使呪法經", "摩訶毘盧遮那如來定惠均等入三昧耶身雙身大聖歡喜天菩薩修行祕密法儀軌",
    "八大靈塔梵讚", "護身命經", "觀自在菩薩阿麼𪘨法", "金有陀羅尼經",
    "大乘方廣曼殊室利菩薩華嚴本教閻曼德迦忿怒王真言大威德儀軌品",
    "略明般若末後一頌讚述", "禮懺文", "無量大慈教經", "聖救度佛母二十一種禮讚經",
    "何耶揭唎婆觀世音菩薩受法壇"
])

def pua_ratio(text):
    if not text: return 1.0
    total = len(text)
    pua = 0
    for ch in text:
        cp = ord(ch)
        if (0xF000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0xFFFFD) or (0x100000 <= cp <= 0x10FFFD):
            pua += 1
    blank = text.count('□')
    return (pua + blank) / total if total > 0 else 1.0, pua, blank, total

def get_text(sutra):
    parts = []
    content = sutra.get('content', [])
    for sec in content:
        if isinstance(sec, dict):
            if 'text' in sec:
                parts.append(sec['text'])
            for k in ['paragraphs', 'sections']:
                if k in sec:
                    for p in sec[k]:
                        if isinstance(p, str):
                            parts.append(p)
                        elif isinstance(p, dict) and 'text' in p:
                            parts.append(p['text'])
        elif isinstance(sec, str):
            parts.append(sec)
    return '\n'.join(parts)

candidates = []
for fn in os.listdir(SUTRA_DIR):
    if not fn.endswith('.json'):
        continue
    sid = fn[:-5]
    if sid in done:
        continue
    fp = os.path.join(SUTRA_DIR, fn)
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            s = json.load(f)
    except:
        continue
    if isinstance(s, list):
        title = ''
        translator = ''
        parts = []
        for c in s:
            if isinstance(c, dict):
                if not title and 'title' in c: title = c['title']
                if not translator and 'translator' in c: translator = c['translator']
                if 'text' in c: parts.append(c['text'])
            elif isinstance(c, str):
                parts.append(c)
        text = '\n'.join(parts)
    else:
        title = s.get('title', '')
        translator = s.get('translator', '')
        parts = []
        for c in s.get('content', []):
            if isinstance(c, dict):
                if 'text' in c: parts.append(c['text'])
                for k in ['paragraphs', 'sections']:
                    if k in c:
                        for p in c[k]:
                            if isinstance(p, str): parts.append(p)
                            elif isinstance(p, dict) and 'text' in p: parts.append(p['text'])
            elif isinstance(c, str):
                parts.append(c)
        text = '\n'.join(parts)
    
    if title in already_covered or sid in already_covered:
        continue
    if not text:
        continue
    ratio, pua, blank, total = pua_ratio(text)
    if ratio > 0.05:
        continue
    # 400-2500字优先
    if 400 <= total <= 2500:
        # 计算切段后段数≥3
        import re
        def norm(s): return re.sub(r"\s+", "", s)
        SPLIT_RE = re.compile(r'(?<=[。！？；：」』）\)\n])')
        parts_split = [p for p in SPLIT_RE.split(text) if p != ""]
        segs, buf = [], ""
        for p in parts_split:
            if len(norm(p)) > 340:
                sub = re.split(r'(?<=[，、])', p)
                for q in sub:
                    if not q: continue
                    buf += q
                    if len(norm(buf)) >= 90:
                        segs.append(buf); buf = ""
                continue
            buf += p
            if len(norm(buf)) >= 90:
                segs.append(buf); buf = ""
        if buf.strip():
            if segs and len(norm(buf)) < 30:
                segs[-1] += buf
            else:
                segs.append(buf)
        nseg = len(segs)
        if nseg >= 3:
            candidates.append((total, ratio, sid, title, pua, blank, nseg))

candidates.sort()
print(f"400-2500字合格候选: {len(candidates)}")
for i, (total, ratio, sid, title, pua, blank, nseg) in enumerate(candidates[:20]):
    print(f"  {sid}: {total}字, {nseg}段, PUA+阙={ratio*100:.1f}% ({pua}pua,{blank}□) - {title[:40]}")

# 取前12
selected = candidates[:12]
selected_ids = [c[2] for c in selected]
print("\n本批选中经号:", ' '.join(selected_ids))

with open(os.path.join(ROOT, 'current_batch.txt'), 'w') as f:
    f.write(' '.join(selected_ids))

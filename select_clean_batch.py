#!/usr/bin/env python3
import os
import json
import glob

# 系统注入的已覆盖经号（历史已完成）
HISTORY_DONE = {
    "大佛顶放光悉怛多钵怛啰陀罗尼", "佛说一髻尊陀罗尼经", "智证大师请来目录", 
    "现在贤劫千佛名经", "过去庄严劫千佛名经", "文殊指南图赞", 
    "t1200", "t1159b", "t1284", "t0899", "t1025", "t2152", "t2815", "t0448b",
    "t2791", "t0407", "t2074", "t1688",
    # 按名称匹配
}
HISTORY_SKIP_TITLES = {
    "過去莊嚴劫千佛名經", "现在贤劫千佛名经", "未来星宿劫千佛名经",
    "續古今譯經圖紀", "佛說地藏菩薩陀羅尼經", "底哩三昧耶不動尊威怒王使者念誦法",
    "佛說聖寶藏神儀軌經", "清淨法身毗盧遮那心地法門成就一切陀羅尼三種悉地",
    "佛頂放無垢光明入普門觀察一切如來心陀羅尼經", "續古今譯經圖紀",
    "起信論注", "宗四分比丘隨門要略行儀", "虛空藏菩薩神咒經", "大方廣佛華嚴經感應傳",
    "密跡力士大權神王經偈頌",
    # 咒类已译过的
}

# 已完成集合
done = set()
for f in glob.glob('data/modern-translation/*.json'):
    sid = os.path.basename(f).replace('.json', '')
    done.add(sid)

# 读取所有经文元数据
candidates = []
sutra_dir = 'sutras'
for f in glob.glob(os.path.join(sutra_dir, '*.json')):
    sid = os.path.basename(f).replace('.json', '')
    if sid in done:
        continue
    if sid in HISTORY_DONE:
        continue
    if sid in {"hant2simp","index","index-light","search-index","search-word-index","search-order"}:
        continue
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
        if not isinstance(data, dict):
            continue
        title = data.get('title', '')
        if title in HISTORY_SKIP_TITLES:
            continue
        # 拼接全文
        text = ''
        content = data.get('content', [])
        if isinstance(content, str):
            text = content
        else:
            for chap in content:
                if isinstance(chap, dict):
                    text += chap.get('text', '') + '\n'
                elif isinstance(chap, str):
                    text += chap + '\n'
        total_len = len(text.replace('\n', '').replace(' ', ''))
        if total_len < 400:
            continue
        # 统计PUA字符
        pua_count = 0
        square_count = 0
        for ch in text:
            cp = ord(ch)
            if (0xF000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0xFFFFD) or (0x100000 <= cp <= 0x10FFFD):
                pua_count += 1
            if ch == '□':
                square_count += 1
        bad_ratio = (pua_count + square_count) / max(total_len, 1)
        if bad_ratio > 0.05:
            continue
        candidates.append((total_len, sid, title, bad_ratio, len(content)))
    except Exception as e:
        continue

# 按字数排序，从短篇开始选，选前12个
candidates.sort()
selected = candidates[:12]
print(f"选中{len(selected)}部经文：")
kids = []
for length, sid, title, ratio, nseg in selected:
    print(f"{sid}\t{length}字\t{nseg}原段\t{title}\t坏字率{ratio:.2%}")
    kids.append(sid)

# 写入选中列表
with open('selected_batch.txt', 'w', encoding='utf-8') as fp:
    fp.write(" ".join(kids))
print("\n空格分隔: " + " ".join(kids))

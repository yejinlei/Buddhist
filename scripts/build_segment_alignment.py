#!/usr/bin/env python3
"""
段级自动对齐脚本：基于关键词共现 + 字符 n-gram + DTW 动态规划。

为异译组生成 segment_alignments/*.json。
每个文件结构:
{
  "group_id": "jingangjing",
  "group_title": "金剛般若波羅蜜經",
  "versions": [
    {"id": "t0235", "title": "...", "translator": "...", "n_paras": N},
    ...
  ],
  "alignments": [
    {
      "id": 1,
      "refs": {"t0235": [para_idx,...], "t0237": [para_idx,...], ...},
      "keyword": "须菩提/於意云何/..."
    },
    ...
  ]
}

对齐思路：
1. 先为每个译本切段（已有 content 数据）；
2. 提取每段"关键术语"（佛学名相 + 2-gram 高频字）作为特征；
3. 以最短译本为"参考轴"，对其他译本用 DTW 做最优段对应；
4. 合并多译本对应关系，构建跨译本对齐组。
"""
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUTRA_DIR = os.path.join(ROOT, 'sutras')
OUT_DIR = os.path.join(ROOT, 'data', 'segment_alignments')
os.makedirs(OUT_DIR, exist_ok=True)

# ==== 佛学名相关键词表（用于强特征匹配）====
BUDDHIST_TERMS = [
    # 金刚经高频术语
    '須菩提','善男子','善女人','阿耨多羅三藐三菩提','菩薩','如來','世尊','阿羅漢',
    '般若波羅蜜','波羅蜜','布施','忍辱','持戒','精進','禪定','般若',
    '須陀洹','斯陀含','阿那含','辟支佛','恒河沙','七宝','三千大千世界',
    '滅度','無我相','無人相','無眾生相','無壽者相','應無所住','金剛','四句偈',
    '實相','信心清淨','無為法','有為法','夢幻泡影','露','電','應化非真',
    '離相','無住','第一波羅蜜','然燈佛','釋迦牟尼','捨利弗','目犍連',
    '大迦葉','須彌山','極樂世界','阿彌陀佛','觀世音菩薩','大勢至菩薩',
    '一心不亂','阿鞞跋致','不退轉','莊嚴','功德','五眼','肉眼','天眼',
    '慧眼','法眼','佛眼','六通','三明','涅槃','菩提','煩惱','生死','輪迴',
    '緣起','性空','中道','真如','法身','色','受','想','行','識',
    '無明','行','識','名色','六入','觸','受','愛','取','有','生','老死',
    '四諦','八正道','十二因緣','六波羅蜜','六度','聲聞','緣覺',
    # 阿弥陀经术语
    '極樂','七寶池','八功德水','金沙','蓮華','青','黃','赤','白','鵝','鴈','鴛鴦',
    '天樂','黃金','晝夜','六時','雨花','迦陵頻伽','共命之鳥',
    '風吹','行樹','羅網','法音','苦','空','無常','無我','念佛','念法','念僧',
    '阿閦佛','須彌相佛','大须弥佛','须弥光佛','妙音佛','如是等恒河沙數佛',
    '東方','南方','西方','北方','下方','上方','虛空','皆大歡喜','信受奉行',
    # 起信论术语
    '一心','真如','生滅','如來藏','阿梨耶識','阿賴耶識','覺','不覺',
    '本覺','始覺','相似覺','隨分覺','究竟覺','無明','業識','轉識','現識','智識','相續識',
    '三細','六粗','智淨相','不思議業相','法身','報身','應身',
    '體大','相大','用大','真如門','生滅門','大乘','起信','熏習','淨法',
    '分別','執著','我見','法執','煩惱障','所知障',
]
# 按长度倒序，长词优先匹配
BUDDHIST_TERMS = sorted(set(BUDDHIST_TERMS), key=lambda x: -len(x))


def extract_paras(sid):
    """从经文 JSON 提取段落列表，返回 [(ci, pi, text_norm, raw_text)]"""
    p = os.path.join(SUTRA_DIR, f'{sid}.json')
    if not os.path.exists(p):
        return []
    s = json.load(open(p, encoding='utf-8'))
    paras = []
    chapters = s.get('chapters')
    if chapters:
        for ci, c in enumerate(chapters):
            for pi, para in enumerate(c.get('paragraphs', [])):
                t = (para or '').strip()
                if len(t) >= 2:
                    paras.append((ci, pi, t, t))
    content = s.get('content')
    if content and not paras:
        for ci, c in enumerate(content):
            t = c.get('text', '')
            parts = re.split(r'(?<=[。！？])\s*|\n+', t)
            for pi, para in enumerate(parts):
                para = para.strip()
                if len(para) >= 2:
                    paras.append((ci, pi, para, para))
    # 去空段、过滤过短
    return paras


def norm_text(t):
    """文本归一：去标点空白，用于相似度计算"""
    return re.sub(r'[\s，。！？、：；「」『』""''…·—\-（）()《》〈〉\[\]【】]*', '', t)


def para_features(text):
    """提取段落特征：(terms_set, 2gram_set, char_set, norm_len)"""
    t = text
    terms = set()
    for kw in BUDDHIST_TERMS:
        if kw in t:
            terms.add(kw)
    nt = norm_text(t)
    bigrams = set()
    for i in range(len(nt) - 1):
        bigrams.add(nt[i:i + 2])
    chars = set(nt)
    return terms, bigrams, chars, len(nt)


def para_similarity(fa, fb):
    """计算两段相似度 [0,1]"""
    ta, ba, ca, la = fa
    tb, bb, cb, lb = fb
    score = 0.0
    # 1) 术语共现（权重最高）
    common_terms = ta & tb
    if ta and tb:
        score += 0.5 * len(common_terms) / max(1, min(len(ta), len(tb)))
    # 2) 2-gram Jaccard
    if ba and bb:
        inter = len(ba & bb)
        union = len(ba | bb)
        if union > 0:
            score += 0.35 * inter / union
    # 3) 字 Jaccard
    if ca and cb:
        inter = len(ca & cb)
        union = len(ca | cb)
        if union > 0:
            score += 0.15 * inter / union
    return score


def dtw_align(feats_a, feats_b, offset_slack=0.25):
    """DTW 对齐：a → b 的映射。
    返回 list of (a_idx, [b_idx,...])，a 每个元素对应 b 的一个或多个段。
    offset_slack 控制允许的位置偏移比例（避免对角线太远的错配）。
    """
    n, m = len(feats_a), len(feats_b)
    if n == 0 or m == 0:
        return []
    INF = float('inf')
    # DP 表
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    bt = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0
    for i in range(n):
        window = max(5, int(m * offset_slack))
        j_start = max(0, int(i * m / n) - window)
        j_end = min(m, int(i * m / n) + window + 1)
        for j in range(j_start, j_end):
            cost = 1.0 - para_similarity(feats_a[i], feats_b[j])
            # 三种转移：diag(1-1)、down(1-0 合并)、right(0-1 展开)
            cands = [
                (dp[i][j] + cost, (i, j, 'diag')),
                (dp[i][j + 1] + cost * 0.7, (i, j + 1, 'down')),  # a 一段对应 b 多段
                (dp[i + 1][j] + cost * 0.7, (i + 1, j, 'right')),  # b 一段对应 a 多段
            ]
            best = min(cands, key=lambda x: x[0])
            if best[0] < dp[i + 1][j + 1]:
                dp[i + 1][j + 1] = best[0]
                bt[i + 1][j + 1] = best[1]
    # 回溯
    a_to_bs = defaultdict(list)
    i, j = n, m
    # 如果到达 (n,m) 的代价太大，尝试找到 (n,*) 的最佳终点
    if dp[n][m] == INF:
        best_j = min(range(m + 1), key=lambda jj: dp[n][jj])
        j = best_j
    while i > 0 and j > 0:
        prev = bt[i][j]
        if prev is None:
            break
        pi, pj, move = prev
        if move == 'diag':
            a_to_bs[i - 1].append(j - 1)
            i, j = pi, pj
        elif move == 'down':
            a_to_bs[i - 1].append(j - 1)
            i = pi
        elif move == 'right':
            a_to_bs[pi].append(pj)
            j = pj
    # 去重排序
    result = []
    for ai in range(n):
        bs = sorted(set(a_to_bs.get(ai, [])))
        result.append(bs)
    return result


def build_alignment(group_id, group_title, version_ids, skip_start=0, skip_noise=False):
    """为一组异译构建对齐。
    skip_start: 参考译本要跳过的开头段数（比如笈多本开头有归敬颂）
    """
    versions = []
    all_paras = {}
    all_feats = {}
    for sid in version_ids:
        paras = extract_paras(sid)
        if not paras:
            print(f'  ⚠️ {sid} 无段落，跳过')
            return None
        all_paras[sid] = paras
        all_feats[sid] = [para_features(p[3]) for p in paras]
        s = json.load(open(os.path.join(SUTRA_DIR, f'{sid}.json'), encoding='utf-8'))
        versions.append({
            'id': sid,
            'title': s.get('title', ''),
            'translator': s.get('translator', ''),
            'n_paras': len(paras),
        })
    # 取段落数最少的译本作为参考轴（最凝练，信息密度高，通常是鸠摩罗什本）
    ref_id = min(version_ids, key=lambda x: len(all_paras[x]))
    ref_idx = version_ids.index(ref_id)
    # 把参考轴放第一位
    ordered = [ref_id] + [v for v in version_ids if v != ref_id]
    # 对每个其他译本，对齐到参考轴
    # 映射结构：ref_idx -> [(ref_para_idx, [other_para_idx,...]), ...]
    mappings = {}  # version_id -> {ref_pi: [other_pi,...]}
    for other_id in ordered[1:]:
        fa = all_feats[ref_id]
        fb = all_feats[other_id]
        # 容忍度：两本字数差距大则 slack 放宽
        ratio = max(len(fb), 1) / max(len(fa), 1)
        slack = 0.35 if ratio > 1.5 else 0.25
        alist = dtw_align(fa, fb, offset_slack=slack)
        m = defaultdict(list)
        for ref_pi, bs in enumerate(alist):
            for b in bs:
                m[ref_pi].append(b)
        mappings[other_id] = m
    # 组装对齐组
    alignments = []
    used_other = defaultdict(set)
    for ref_pi in range(len(all_paras[ref_id])):
        ref_para_raw = all_paras[ref_id][ref_pi][3]
        ref_term = all_feats[ref_id][ref_pi][0]
        refs = {ref_id: [ref_pi]}
        for other_id in ordered[1:]:
            bs = mappings[other_id].get(ref_pi, [])
            bs = [b for b in bs if b not in used_other[other_id]]
            if bs:
                refs[other_id] = bs
                for b in bs:
                    used_other[other_id].add(b)
        # 跳过过短的"如是我闻""一時"等开头噪声
        if skip_noise and ref_pi < skip_start:
            continue
        # 关键词：取参考段最突出的术语
        kws = list(ref_term)[:5]
        keyword = '/'.join(kws) if kws else ref_para_raw[:18].replace('\n', '')
        alignments.append({
            'id': len(alignments) + 1,
            'refs': refs,
            'keyword': keyword,
        })
    # 处理未匹配的"尾部"段：合并到最后一个组
    for other_id in ordered[1:]:
        n = len(all_paras[other_id])
        leftover = [i for i in range(n) if i not in used_other[other_id]]
        if leftover and alignments:
            # 把剩余段就近分到最后一个组
            last = alignments[-1]
            last['refs'][other_id] = sorted(set(last['refs'].get(other_id, []) + leftover))
    # 过滤空对齐（只有 ref 一个译本的也要保留，避免丢失）
    out = {
        'group_id': group_id,
        'group_title': group_title,
        'reference_id': ref_id,
        'versions': versions,
        'n_alignments': len(alignments),
        'alignments': alignments,
    }
    out_path = os.path.join(OUT_DIR, f'{group_id}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    # 简单统计
    aligned_sum = sum(1 for a in alignments if len(a['refs']) > 1)
    print(f'  ✅ {group_title}  | {len(versions)}译本 | {len(alignments)}组对齐 | 多译对齐率{aligned_sum}/{len(alignments)}')
    for v in versions:
        print(f'      · {v["id"]} {v["translator"]} {v["n_paras"]}段')
    return out


def main():
    groups = [
        # 金刚经（4 译本）——鸠摩罗什/真谛/笈多/义净
        {
            'group_id': 'jingangjing',
            'group_title': '金剛般若波羅蜜經（金剛經）',
            'ids': ['t0235', 't0237', 't0238', 't0239'],
        },
        # 阿弥陀经（2 译本）——鸠摩罗什/玄奘（玄奘本叫"称赞净土佛摄受经"）
        {
            'group_id': 'amituojing',
            'group_title': '阿彌陀經',
            'ids': ['t0366', 't0367'],
        },
        # 大乘起信论（2 译本）——真谛/实叉难陀
        {
            'group_id': 'dachengqixinlun',
            'group_title': '大乘起信論',
            'ids': ['t1666', 't1667'],
        },
    ]
    # 检查佛遗教经（t0389）、四十二章经（t0784）、八大人觉经（t0779）等常用短经是否有2译以上
    # 实际在异译清单里它们是单译，跳过
    for g in groups:
        print(f'处理 {g["group_title"]}...')
        build_alignment(g['group_id'], g['group_title'], g['ids'])

    # 生成清单文件
    manifest = []
    for fn in sorted(os.listdir(OUT_DIR)):
        if fn.endswith('.json') and fn != 'manifest.json':
            data = json.load(open(os.path.join(OUT_DIR, fn), encoding='utf-8'))
            manifest.append({
                'group_id': data['group_id'],
                'group_title': data['group_title'],
                'n_versions': len(data['versions']),
                'n_alignments': data['n_alignments'],
                'versions': [{'id': v['id'], 'translator': v['translator'], 'title': v['title']} for v in data['versions']],
            })
    with open(os.path.join(OUT_DIR, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f'\n=== 段级对齐完成，共 {len(manifest)} 组 ===')


if __name__ == '__main__':
    main()

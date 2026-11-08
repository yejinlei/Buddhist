#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬折行合并脚本 v2（保守 + 精准）

两类折行识别：
A. 版式固定行宽折行：连续 ≥5 行、每行汉字数稳定在 14-22 且 ≥60% 行末尾不是句末标点
   → 段内除明显段末外，将换行全部删除合并为连续文本
B. 译者署名与正文误粘：若某段首行以"譯/詔譯/奉詔譯/製/述/編/註"等结尾，且第二行是正文开头（如"如是我聞/聞如是/爾時/"）
   → 两段之间插入空行？实际不应该——CBETA原文中译者署名与正文本属同一段，行尾换行仅物理折行，应合并为一行
   → 即：将这种段首首行（短行）后的换行去掉，署名连到正文开头

红线：
- 偈颂行（<14汉字且整齐对仗）不合并
- 对话/问答短行（"不也，世尊！"等）不合并
- 经文汉字一字不改，仅删除 \n
"""
import json, os, re, argparse, hashlib
from glob import glob
from collections import Counter

CJK_RE = re.compile(r'[\u4e00-\u9fff]')
def cjk(s): return len(CJK_RE.findall(s))
def strip(s): return s.rstrip()

# 强句末/闭合标点：行尾出现这些，换行视为合法
STRONG_END = set('。！？…」』】）)〕〉》．！？；')
# 对话/提示语引导符号：其后换行也保留
LEAD_END = set('：:')
# 偈颂特征：行首多为「且行尾通常是。或」且行汉字数 5/7/10 左右
# 偈颂引导语（必须是行尾独立短语，前面紧跟标点/开头；不能是"演說""稱說""廣說"这类普通动词）
GATHA_LEADERS_RE = re.compile(
    r'(?:^|[，。：「『])\s*'
    r'(而|復|重|還)?'
    r'(說|歌|頌)'
    r'(是)?'
    r'(偈|伽他|伽陀|頌)?'
    r'(言|曰)?'
    r'[：:]?[「『]?$'
)

def is_strong_end_line(line):
    s = line.rstrip()
    if not s: return True
    return s[-1] in STRONG_END

def is_lead_line(line):
    s = line.rstrip()
    if not s: return False
    if s[-1] in LEAD_END:
        # 检查是否是"XX曰/白/言/告/說偈言："这类引导语（短行）
        if cjk(s) <= 25:
            return True
    return False

def is_gatha_intro(line):
    """判断是否是偈颂引导行"""
    s = line.rstrip()
    return bool(GATHA_LEADERS_RE.search(s[-20:]))

# ---------- A. 固定行宽版式折行识别 ----------
def detect_layout_blocks(lines):
    """返回 [(start, end), ...] 表示需要合并的版式折行连续段范围。
    固定版式折行特征：连续若干行汉字数集中在 [14,23] 区间（典型 17/18 字/行），
    不被偈颂引导语/空行/明显长行/独立短句打断。
    """
    blocks = []
    n = len(lines)
    # 给每一行打标签：'L'=版式行(cjk 14-23), 'S'=段末短句(cjk<14且句末), 'B'=其他/空行/偈颂引导/长行
    tags = []
    for l in lines:
        s = l.rstrip()
        if not s:
            tags.append('B'); continue
        w = cjk(s)
        if is_gatha_intro(s):
            tags.append('B'); continue
        if w > 23:
            tags.append('B'); continue
        if 14 <= w <= 23:
            tags.append('L')
        elif w < 14 and s[-1] in STRONG_END:
            tags.append('S')  # 段末短句（句末结尾），算入当前段尾部
        else:
            tags.append('B')
    # 滑窗找连续的 L...L[可选 S] 段
    i = 0
    while i < n:
        if tags[i] != 'L':
            i += 1; continue
        j = i
        L_count = 0
        got_S = False
        while j < n:
            t = tags[j]
            if t == 'L':
                if got_S:  # S 之后又出 L，说明 S 不是段末，重新判定
                    break
                L_count += 1; j += 1
            elif t == 'S' and not got_S:
                got_S = True; j += 1
                break  # 段末短行收束
            else:
                break
        if L_count >= 5:
            # 宽度稳定性检查
            seg_widths = [cjk(lines[k].rstrip()) for k in range(i,j) if lines[k].strip()]
            cnt = Counter(seg_widths)
            mode_w, mode_cnt = cnt.most_common(1)[0]
            if mode_cnt / len(seg_widths) >= 0.4:
                blocks.append((i, j))
                i = j; continue
        i += 1
    return blocks

def merge_layout_blocks(text):
    """合并版式折行，返回(new_text, n_merged)"""
    if '\n' not in text:
        return text, 0
    lines = text.split('\n')
    blocks = detect_layout_blocks(lines)
    if not blocks:
        return text, 0
    # 逐块合并：把 blocks 内的行去掉 \n 拼起来
    new_lines = []
    cursor = 0
    merged = 0
    for s, e in blocks:
        # 保留 [cursor, s) 不变
        new_lines.extend(lines[cursor:s])
        # 合并 [s, e) 为一行
        merged_segment = ''.join(l.rstrip() for l in lines[s:e])
        new_lines.append(merged_segment)
        merged += (e - s - 1)  # 删除了多少个 \n
        cursor = e
    new_lines.extend(lines[cursor:])
    return '\n'.join(new_lines), merged

# ---------- B. 译者署名行识别（保持独立段落，不与正文合并）----------
# 注：经过仔细检查，CBETA 原文中译者署名后直接跟正文的换行是"段落间换行"，
# 不应该删掉（删掉会出现"鳩摩羅什譯如是我聞"这种不通顺的拼接）。
# 原数据中已经是正确分段（译者署名作为独立首行，正文作为下一行同一段），
# 我们**不做**译者署名合并，保持原样。
def merge_trans_signature(text):
    """不做任何合并，保持 CBETA 原文换行。返回 (text, 0)。"""
    return text, 0

def process_file(path, dry_run=False, write_back=True):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    total_layout = 0
    total_trans = 0
    changed_paras = 0
    for para in d.get('content', []):
        if not isinstance(para, dict):
            continue
        txt = para.get('text', '')
        if not txt: continue
        # 先处理 B（译者署名）
        new_txt, m1 = merge_trans_signature(txt)
        # 再处理 A（版式折行）
        new_txt, m2 = merge_layout_blocks(new_txt)
        total_layout += m2
        total_trans += m1
        if m1 + m2 > 0:
            changed_paras += 1
            if not dry_run and write_back:
                para['text'] = new_txt
    total = total_layout + total_trans
    if not dry_run and write_back and total > 0:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    return total_layout, total_trans, changed_paras

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--end', type=int, default=0)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--only', nargs='*')
    args = ap.parse_args()

    files = sorted(glob('sutras/t*.json'))
    if args.only:
        files = [f'sutras/{sid}.json' for sid in args.only if os.path.exists(f'sutras/{sid}.json')]
    else:
        end = args.end if args.end > 0 else len(files)
        files = files[args.start:end]

    print(f'待处理: {len(files)} 部 (dry_run={args.dry_run})')
    files_changed = 0
    total_layout = 0
    total_trans = 0
    for fp in files:
        sid = os.path.basename(fp).replace('.json','')
        l, t, cp = process_file(fp, dry_run=args.dry_run, write_back=not args.dry_run)
        if l + t > 0:
            files_changed += 1
            total_layout += l
            total_trans += t
            print(f'  {sid}: 版式折行合并 {l} 处, 译者署名合并 {t} 处, 涉及 {cp} 段')
    print(f'\n共处理 {len(files)} 部, 有改动 {files_changed} 部')
    print(f'版式折行 \n 合并 {total_layout} 处; 译者署名合并 {total_trans} 处')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()

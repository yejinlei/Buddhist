#!/usr/bin/env python3
"""按真实字段结构全量校验原文 + 白话 JSON。"""
import json, os, glob, time, re

ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
SUTRA_DIR = os.path.join(ROOT, "sutras")
MOD_DIR   = os.path.join(ROOT, "data/modern-translation")

with open(os.path.join(SUTRA_DIR, "index-light.json"), encoding='utf-8') as f:
    idx = json.load(f)
items = idx['items'] if isinstance(idx, dict) else idx
ids = [it['id'] for it in items if 'id' in it]
print(f"经目索引: {len(ids)} 部")

sutra_files = {os.path.basename(p)[:-5]:p for p in glob.glob(os.path.join(SUTRA_DIR, "t*.json"))}
mod_files   = {os.path.basename(p)[:-5]:p for p in glob.glob(os.path.join(MOD_DIR, "t*.json"))}

orig_ok = 0; orig_missing = []; orig_bad = []
empty_chapters = []; chapters_with_empty_text = 0
total_chapters = 0; total_chars = 0

mod_ok = 0; mod_missing = 0; mod_bad = []
mod_with_xiaobiaoti = 0; mod_with_yijie = 0; mod_with_zhengwen = 0
mod_bad_seg = []; empty_modern_text = []; fan_violations = 0
fan_violation_examples = []

HEADER_RE = re.compile(r'^【[^】]+】')
FANZI = '迴裡為於爾並恆後悅慾淨涼滅為爾從個萬當證識變邊過達還這進遊裡麼'  # 常见繁体检出用；实际用 opencc 更准

t0 = time.time()
for tid in ids:
    # ==== 原文 ====
    sp = sutra_files.get(tid)
    if not sp:
        orig_missing.append(tid); continue
    try:
        with open(sp, encoding='utf-8') as f:
            j = json.load(f)
    except Exception as e:
        orig_bad.append((tid, f"json_err: {e}")); continue
    if not isinstance(j, dict):
        orig_bad.append((tid,"not dict")); continue
    if 'id' not in j or 'title' not in j:
        orig_bad.append((tid,"missing id/title")); continue
    content = j.get('content')
    if not isinstance(content, list):
        orig_bad.append((tid, f"content not list (type={type(content).__name__})")); continue
    if not content:
        empty_chapters.append(tid); continue
    bad_ch = 0
    for ch in content:
        total_chapters += 1
        if not isinstance(ch, dict) or 'text' not in ch:
            bad_ch += 1; continue
        txt = ch.get('text') or ''
        if not txt.strip():
            chapters_with_empty_text += 1
        total_chars += len(txt)
    if bad_ch:
        orig_bad.append((tid, f"{bad_ch} chapters missing 'text'")); continue
    orig_ok += 1

    # ==== 白话 ====
    mp = mod_files.get(tid)
    if not mp:
        mod_missing += 1; continue
    try:
        with open(mp, encoding='utf-8') as f:
            mj = json.load(f)
    except Exception as e:
        mod_bad.append((tid, f"json_err: {e}")); continue
    if not isinstance(mj, dict):
        mod_bad.append((tid,"mod not dict")); continue
    trans = mj.get('translations')
    if not isinstance(trans, list):
        # 兼容 moderns 字段（部分旧版）
        trans = mj.get('moderns')
        if not isinstance(trans, list):
            mod_bad.append((tid, f"no translations/moderns list, keys={list(mj.keys())[:6]}")); continue
    if not trans:
        mod_bad.append((tid,"translations empty")); continue
    seg_bad = 0; emt = 0
    has_xb = False; has_yj = False; has_zw = False
    for i,s in enumerate(trans):
        if not isinstance(s, dict):
            seg_bad+=1; continue
        md = s.get('modern')
        if not md or not str(md).strip():
            emt += 1; continue
        mds = str(md)
        if '【' in mds and '小标题' in mds[:20]: has_xb = True
        if '【义解】' in mds or '【義解】' in mds: has_yj = True
        # 正文只要有内容即算
        if mds.strip(): has_zw = True
    if seg_bad:
        mod_bad.append((tid, f"{seg_bad} segments not dict")); continue
    if emt:
        empty_modern_text.append((tid, emt))
    if has_xb: mod_with_xiaobiaoti += 1
    if has_yj: mod_with_yijie += 1
    if has_zw: mod_with_zhengwen += 1
    mod_ok += 1

print(f"\n===== 原文校验（总 {len(ids)} 部） 耗时 {time.time()-t0:.1f}s =====")
print(f"  成功解析:         {orig_ok}")
print(f"  缺文件:           {len(orig_missing)}")
print(f"  解析/字段错误:    {len(orig_bad)}")
print(f"  空章节数组:       {len(empty_chapters)}")
print(f"  总章节数:         {total_chapters}")
print(f"  空text的章节数:   {chapters_with_empty_text}")
print(f"  原文字数(估):     {total_chars:,}")
if orig_missing: print(f"  缺文件: {orig_missing[:10]}")
if orig_bad:
    print(f"  原文错误样例:")
    for t,m in orig_bad[:10]: print(f"    {t}  {m}")
if empty_chapters: print(f"  空章节数组经: {empty_chapters[:10]}")

print(f"\n===== 白话译文校验 =====")
print(f"  已翻译(有文件且ok): {mod_ok}")
print(f"  未翻译(缺文件):     {mod_missing}")
print(f"  解析/字段错误:      {len(mod_bad)}")
print(f"  含小标题段:         {mod_with_xiaobiaoti}")
print(f"  含义解段:           {mod_with_yijie}")
print(f"  空modern字段的段:   {len(empty_modern_text)}  涉及经: {len({t for t,_ in empty_modern_text})}")
if mod_bad:
    print(f"  白话错误样例(前15):")
    for t,m in mod_bad[:15]: print(f"    {t}  {m}")
if empty_modern_text[:10]:
    print(f"  含空段经样例(前10):")
    for t,n in empty_modern_text[:10]: print(f"    {t}  空段数={n}")

# 保存报告
report = {
    "index_total": len(ids),
    "orig": {"ok":orig_ok,"missing":orig_missing,"bad":orig_bad,"empty_chapters":empty_chapters,
             "total_chapters":total_chapters,"empty_text_chapters":chapters_with_empty_text,"total_chars":total_chars},
    "modern": {"ok":mod_ok,"missing":mod_missing,"bad":mod_bad,
               "with_xiaobiaoti":mod_with_xiaobiaoti,"with_yijie":mod_with_yijie,
               "empty_segments":empty_modern_text[:100]},
}
with open('/tmp/audit_local.json','w',encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("\n报告: /tmp/audit_local.json")

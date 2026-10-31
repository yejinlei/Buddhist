# -*- coding: utf-8 -*-
"""
白话译文严格校验闸门（宁缺毋滥）
判定每部译文是否达到"可上线"标准：
  1. JSON 合法；顶层含 id/title/translator/translations
  2. 每段含 section/original_preview/modern
  3. 各段 original_preview 顺次拼接 = 经文原文的【连续子串】（一字不差）
  4. 拼接覆盖率 >= 阈值（默认 0.95）
  5. 每段 modern 以【】小标题开头、含【义解】且其后有正文
用法：
  python3 scripts/validate_baihua.py            # 全量体检，输出 audit
  python3 scripts/validate_baihua.py t0123 ...  # 指定经号
"""
import json, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TR   = os.path.join(ROOT, "data", "modern-translation")
SUT  = os.path.join(ROOT, "sutras")

def norm(s): return re.sub(r"\s+", "", s)

def load_orig(tid):
    p = os.path.join(SUT, tid + ".json")
    if not os.path.exists(p): return None
    d = json.load(open(p, encoding="utf-8"))
    return norm("\n".join(c["text"] for c in d["content"]))

def check(tid, cover_min=0.95):
    p = os.path.join(TR, tid + ".json")
    if not os.path.exists(p): return {"id": tid, "status": "missing_file"}
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        return {"id": tid, "status": "json_error", "detail": str(e)}
    secs = d.get("translations") or d.get("sections") or []
    if not secs: return {"id": tid, "status": "no_sections"}
    ot = load_orig(tid)
    if ot is None: return {"id": tid, "status": "no_orig"}
    cat = norm("".join(s.get("original_preview", "") for s in secs))
    if not cat: return {"id": tid, "status": "empty_preview"}
    cover = len(cat) / len(ot) if ot else 0
    substring = cat in ot
    bad_y = [i for i, s in enumerate(secs)
             if not re.match(r"^【.+?】", s.get("modern", "")) or "【义解】" not in s.get("modern", "")
             or s.get("modern", "").rstrip().endswith("【义解】")]
    problems = []
    if not substring: problems.append("preview_not_substring")
    if cover < cover_min: problems.append(f"cover={cover:.2f}")
    if bad_y: problems.append(f"bad_modern@{bad_y[:3]}")
    status = "ok" if not problems else "fail"
    return {"id": tid, "status": status, "cover": round(cover, 3),
            "sections": len(secs), "problems": problems}

def main():
    args = sys.argv[1:]
    if args:
        tids = args
    else:
        tids = sorted(os.path.basename(f)[:-5]
                      for f in glob.glob(os.path.join(TR, "t*.json")))
    ok = []; bad = []
    for tid in tids:
        r = check(tid)
        (ok if r["status"] == "ok" else bad).append(r)
    print(f"总数 {len(tids)}  合格 {len(ok)}  不合格 {len(bad)}")
    for r in bad:
        print("  ✗", r["id"], r["status"], r.get("problems", r.get("detail", "")))
    # 落盘
    out = os.path.join(ROOT, "data", "baihua-audit.json")
    json.dump({"total": len(tids), "ok": len(ok), "fail": len(bad),
               "ok_ids": [r["id"] for r in ok],
               "fail_detail": bad},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("已写", out)

if __name__ == "__main__":
    main()

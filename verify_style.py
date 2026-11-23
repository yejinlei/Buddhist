#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""样式篡改检测脚本（v4 - SPA版）。
项目正确架构：
- pages/sutras.html 是唯一的富客户端SPA（左侧4个下拉框：按册/按部类/按朝代/按译者，右侧动态加载经文+白话+注音+词典+笔记+科判）
- data/modern-translation/*.json 是白话数据，SPA动态加载，无需静态HTML
- 根目录 tXXXX.html 是冗余的静态HTML，未来会逐步改为跳转页（当前保留但不作为主入口）
- 禁止任何脚本覆盖 pages/sutras.html

检查项：
1. pages/sutras.html 存在且为SPA（含4个下拉框 id=vol-filter/cat-filter/dyn-filter/tr-filter，含 parseModern 函数，动态加载数据）
2. pages/sutras.html 不含简陋固定CSS（max-width:820px / 8b0000标题色 等_rebuild_pages标志）
3. data/modern-translation-index.json 存在且长度等于实际译文数
4. 所有可能覆盖sutras.html的脚本（_rebuild_pages/_rebuild_sutras_page/render_all_pages/build_sutra_index/build_sutra_pages）已作废
5. sutras/index-light.json 存在
"""
import os, re, sys
from pathlib import Path

ROOT = Path("/home/user/workspace/13511660557912876654/buddhist-ontology")
TRANS = ROOT / "data" / "modern-translation"

BAD_CSS_SIGS = ['max-width: 820px', 'color:#8b0000', '.xiaobiaoti { font-weight:bold']
BANNED_SCRIPTS = ["_rebuild_pages.py", "_rebuild_sutras_page.py", "render_all_pages.py",
                  "build_sutra_pages.py", "build_sutras_index.py"]
REQUIRED_SELECTS = ['id="vol-filter"', 'id="cat-filter"', 'id="dyn-filter"', 'id="tr-filter"']
REQUIRED_JS = ['parseModern', 'loadMoreChapters', 'initFilters']

def main():
    errors = []
    warnings = []

    # 1. 作废脚本检查
    for s in BANNED_SCRIPTS:
        p = ROOT / s
        if p.exists():
            content = p.read_text(encoding="utf-8", errors="ignore")
            if "sys.exit" not in content and "已作废" not in content:
                errors.append(f"危险脚本 {s} 已被重新启用！可能覆盖SPA样式，请立即停用。")

    # 2. 真实已译数量
    real_count = sum(1 for f in os.listdir(TRANS) if f.endswith(".json") and f != "tree.json")

    # 3. 经目页 SPA 检查
    sp = ROOT / "pages" / "sutras.html"
    if not sp.exists():
        errors.append("pages/sutras.html 不存在")
    else:
        shtml = sp.read_text(encoding="utf-8", errors="ignore")
        # 4个下拉框
        for sel in REQUIRED_SELECTS:
            if sel not in shtml:
                errors.append(f"pages/sutras.html 缺少下拉框 {sel}，左侧筛选UI不完整")
        # JS函数
        for js in REQUIRED_JS:
            if f"function {js}" not in shtml:
                errors.append(f"pages/sutras.html 缺少核心函数 {js}，SPA功能被破坏")
        # 不应有简陋固定CSS
        for sig in BAD_CSS_SIGS:
            if sig in shtml:
                errors.append(f"pages/sutras.html 含简陋样式标记「{sig}」，疑似被错误脚本覆盖")
        # 动态加载数据引用
        if "../sutras/index-light.json" not in shtml:
            errors.append("pages/sutras.html 未动态加载 sutras/index-light.json")
        if "../data/modern-translation/" not in shtml:
            errors.append("pages/sutras.html 未动态加载白话译文")
        # 行数合理（SPA版约1500+行，静态生成版只有约250行）
        lines = shtml.count("\n")
        if lines < 800:
            errors.append(f"pages/sutras.html 仅{lines}行，SPA版本应在1000行以上，疑似被静态版覆盖")

    # 4. 数据依赖
    for dep in ["sutras/index-light.json", "data/modern-translation-index.json",
                "sutras/hant2simp.json", "data/buddhist_dict.json", "data/cross-links.json"]:
        if not (ROOT / dep).exists():
            errors.append(f"数据依赖 {dep} 缺失")
    idx_file = ROOT / "data" / "modern-translation-index.json"
    if idx_file.exists():
        import json
        try:
            idx = json.loads(idx_file.read_text(encoding="utf-8"))
            if isinstance(idx, list):
                if len(idx) != real_count:
                    errors.append(f"modern-translation-index.json 有{len(idx)}条，实际译文{real_count}部，不一致")
        except Exception as e:
            errors.append(f"modern-translation-index.json 解析失败: {e}")

    # 报告
    print(f"真实已译：{real_count} 部")
    print(f"pages/sutras.html 行数：{sum(1 for _ in open(ROOT/'pages/sutras.html', encoding='utf-8'))}")
    print()
    if errors:
        print(f"❌ 发现 {len(errors)} 个错误：")
        for e in errors: print(f"  - {e}")
    else:
        print("✅ SPA样式正常，未被篡改")
    if warnings:
        print(f"⚠️  {len(warnings)} 个警告：")
        for w in warnings: print(f"  - {w}")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_ontology_index.py
--------------------------------------------------------------------
为本体总纲页的「四轴 × 七层」交互图构建【活索引】。

产出：ontology/ontology-index.json
  - meta       : 生成时间、版本、各源文件 mtime/大小/条数
  - global     : 全局统计
  - axes/layers: 按轴、按层的类数与实例数汇总
  - classes    : 每个本体类的
        count / unit / coverage / breakdown  （实时统计）
        origin / storage / generator / update_cmd / note （来源与存放位置）
        samples   : 样例实例
        live_key  : 前端实时汇总时使用的数据源与规则标识
  - relations  : 关系三元组统计（按类型）

设计原则：
  1. 本脚本只做「扫描 + 汇总」，不改动任何原始数据。
  2. 前端页面会优先用同一批原始索引文件实时重算（见 ontology-tbox-viz.js），
     本文件为预计算快照与来源元数据（供静态展示 / 校验 / 回退）。
  3. 数据补全后重跑本脚本即可刷新快照；页面刷新即可看到实时值。

用法：
    python3 scripts/build_ontology_index.py
"""
import json
import os
import sys
import datetime
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INST = os.path.join(ROOT, "ontology", "instances")


def P(*parts):
    return os.path.join(ROOT, *parts)


def jload(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("  [!] 读取失败 %s : %s" % (path, e), file=sys.stderr)
        return default


def fstat(path):
    """返回文件的相对路径、字节数、mtime（ISO）。"""
    rel = os.path.relpath(path, ROOT)
    if not os.path.exists(path):
        return {"path": rel, "exists": False, "bytes": 0, "mtime": None}
    st = os.stat(path)
    return {
        "path": rel,
        "exists": True,
        "bytes": st.st_size,
        "mtime": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    }


def count_dir(path, exts=(".json",)):
    if not os.path.isdir(path):
        return 0
    n = 0
    for fn in os.listdir(path):
        if fn.lower().endswith(exts):
            n += 1
    return n


def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------- 1. 读取各数据源 ----------
    manifest = jload(P("ontology", "instances", "manifest.json"), {}) or {}
    m2 = jload(P("ontology", "instances", "m2_index.json"), {}) or {}
    events = jload(P("ontology", "instances", "events.json"), {}) or {}
    da = jload(P("ontology", "dharma_assemblies.json"), {}) or {}
    relations = jload(P("ontology", "instances", "relations.json"), {}) or {}
    kepan = jload(P("kepan", "core.json"), {}) or {}
    shardmap = jload(P("ontology", "instances", "shard-map.json"), {}) or {}
    tbox = jload(P("ontology", "tbox_data.json"), {}) or {}

    sutras = manifest.get("sutras", []) or []
    mstats = manifest.get("stats", {}) or {}

    concepts = m2.get("concepts", []) or []
    persons = m2.get("persons", []) or []
    core_sutras = m2.get("sutras", []) or []
    sects = m2.get("sects", []) or []

    councils = events.get("councils", []) or []
    trans = events.get("transmission_events", []) or []
    stories = events.get("story_events", []) or []
    assemblies = (da.get("assemblies", {}) or {})
    rels = relations.get("relations", []) or []

    # ---------- 2. 派生统计 ----------
    # M3 文本层：按三藏粗分
    def cat_has(s, *kw):
        c = s.get("category", "") or ""
        return any(k in c for k in kw)

    sutra_cnt = sum(1 for s in sutras if cat_has(s, "經", "经", "阿含", "般若", "法華", "华严", "華嚴", "寶積", "涅槃", "大集", "密", "淨土", "净土"))
    vinaya_cnt = sum(1 for s in sutras if cat_has(s, "律"))
    sastra_cnt = sum(1 for s in sutras if cat_has(s, "論", "论", "釋", "释", "疏", "鈔"))

    # M2 概念分层
    concept_L1 = [c for c in concepts if (c.get("layer") == "L1")]
    concept_L2 = [c for c in concepts if (c.get("layer") == "L2")]
    concept_L3 = [c for c in concepts if (c.get("layer") == "L3")]

    # 人物按类
    pcat = Counter((p.get("category") or "未分类") for p in persons)

    # 事件字段统计
    council_evt = len(councils)
    trans_evt = len(trans)
    story_evt = len(stories)
    da_cnt = len(assemblies)

    # 关系类型
    rel_types = Counter((r.get("type") or "未分类") for r in rels)

    # 分片
    shard_meta = shardmap.get("meta", {}) or {}
    shard_count = shard_meta.get("shard_count") or len(shardmap.get("shards", {}) or {})

    # 目录级实例数
    n_concepts_dir = count_dir(P("ontology", "instances", "concepts"))
    n_persons_dir = count_dir(P("ontology", "instances", "persons"))
    n_sutras_dir = count_dir(P("ontology", "instances", "sutras"))
    n_sects_dir = count_dir(P("ontology", "instances", "sects"))

    # 全藏实例文件数（instances 根目录下 t####.json + 别名 id）
    inst_root_files = [f for f in os.listdir(INST) if f.endswith(".json")] if os.path.isdir(INST) else []
    aggregate_files = {"manifest.json", "m2_index.json", "m2_manifest.json", "relations.json",
                       "events.json", "instance-links.json", "shard-map.json"}
    sutra_files = [f for f in inst_root_files if f not in aggregate_files]

    # ---------- 3. 类 → 统计/来源 映射 ----------
    CLS = OrderedDict()

    def add(cid, *, count=None, unit="", coverage=None, breakdown=None,
            origin, storage, generator, update_cmd, note="", samples=None,
            status="active", live_key=None, category_field=None):
        CLS[cid] = {
            "id": cid,
            "status": status,                # active=有独立实例 / field=字段承载 / abstract=结构性抽象类
            "count": count,
            "unit": unit,
            "coverage": coverage,            # {"have":x,"total":y,"pct":z}
            "breakdown": breakdown or {},
            "origin": origin,                # 数据来源（文件 / 目录）
            "storage": storage,              # 存放位置
            "generator": generator,           # 生成脚本
            "update_cmd": update_cmd,        # 更新方式（命令）
            "note": note,
            "samples": samples or [],
            "live_key": live_key,            # 前端实时汇总标识
            "category_field": category_field,
        }

    REBUILD = "python3 scripts/build_ontology_index.py"

    # —— L4 文本层 ——
    add("Text", count=len(sutras), unit="部",
        coverage={"have": len(sutras), "total": mstats.get("total") and 2506 or 2506, "pct": 100.0},
        breakdown={"经": sutra_cnt, "律": vinaya_cnt, "论": sastra_cnt},
        origin=["ontology/instances/manifest.json", "ontology/instances/t####.json"],
        storage="ontology/instances/（2506 个 t####.json 平铺）+ ontology/instances/shards/（%d 片）" % shard_count,
        generator="scripts/build_all_instances.py → scripts/build_shards.py",
        update_cmd="python3 scripts/build_all_instances.py && python3 scripts/build_shards.py && " + REBUILD,
        note="全藏文本本体，按大正藏经号 t#### 平铺存储，分片用于大文件分发。",
        samples=[s.get("id") for s in sutras[:6]], live_key="manifest.sutras")

    add("Sutra", count=sutra_cnt, unit="部",
        coverage={"have": sutra_cnt, "total": len(sutras), "pct": round(sutra_cnt * 100.0 / max(len(sutras), 1), 1)},
        breakdown=dict(Counter((s.get("category") or "").split(",")[0] for s in sutras if cat_has(s, "經", "经", "阿含", "般若", "法華", "华严", "華嚴", "寶積", "涅槃", "大集", "密", "淨土", "净土")).most_common(12)),
        origin=["ontology/instances/manifest.json"],
        storage="ontology/instances/t####.json（category 字段）",
        generator="scripts/build_all_instances.py",
        update_cmd=REBUILD,
        note="category 字段含经部类者；部类细分见 breakdown。",
        live_key="manifest.sutras.category")

    add("Vinaya", count=vinaya_cnt, unit="部",
        coverage={"have": vinaya_cnt, "total": len(sutras), "pct": round(vinaya_cnt * 100.0 / max(len(sutras), 1), 1)},
        breakdown=dict(Counter(s.get("category", "") for s in sutras if cat_has(s, "律")).most_common(12)),
        origin=["ontology/instances/manifest.json"],
        storage="ontology/instances/t####.json（category 字段）",
        generator="scripts/build_all_instances.py", update_cmd=REBUILD,
        note="category 字段含律部类者。", live_key="manifest.sutras.category")

    add("Sastra", count=sastra_cnt, unit="部",
        coverage={"have": sastra_cnt, "total": len(sutras), "pct": round(sastra_cnt * 100.0 / max(len(sutras), 1), 1)},
        breakdown=dict(Counter(s.get("category", "") for s in sutras if cat_has(s, "論", "论", "釋", "释", "疏", "鈔")).most_common(12)),
        origin=["ontology/instances/manifest.json"],
        storage="ontology/instances/t####.json（category 字段）",
        generator="scripts/build_all_instances.py", update_cmd=REBUILD,
        note="category 字段含论/释/疏部类者。", live_key="manifest.sutras.category")

    add("Kepan", count=len(kepan), unit="部",
        coverage={"have": len(kepan), "total": len(sutras), "pct": round(len(kepan) * 100.0 / max(len(sutras), 1), 1)},
        breakdown={"已建科判": len(kepan), "待补": max(len(sutras) - len(kepan), 0)},
        origin=["kepan/core.json"],
        storage="kepan/core.json（%d 条，键为经号）" % len(kepan),
        generator="scripts/build_kepan.py → scripts/extend_kepan.py",
        update_cmd="python3 scripts/extend_kepan.py && " + REBUILD,
        note="科判（序分/正宗分/流通分及品章结构）。补充科判后重跑脚本，本页数字自动更新。",
        samples=list(kepan.keys())[:8], live_key="kepan.core")

    add("Chapter", count=mstats.get("total_chapters"), unit="品/章",
        breakdown={"含品章之经": None},
        origin=["ontology/instances/manifest.json", "ontology/instances/t####.json（chapters 字段）"],
        storage="ontology/instances/t####.json 内 chapters 数组；汇总于 manifest.stats",
        generator="scripts/build_all_instances.py", update_cmd=REBUILD,
        note="品/章级结构节点，来自每部经的科判切分。", live_key="manifest.stats.total_chapters")

    add("Section", count=mstats.get("total_paragraphs"), unit="段落",
        origin=["ontology/instances/manifest.json", "ontology/instances/t####.json（paragraphs 字段）"],
        storage="ontology/instances/t####.json 内段落数组；汇总于 manifest.stats",
        generator="scripts/build_all_instances.py", update_cmd=REBUILD,
        note="段落级文本节点。", live_key="manifest.stats.total_paragraphs")

    add("Gatha", count=mstats.get("total_gathas"), unit="偈颂",
        coverage={"have": mstats.get("sutras_with_gathas"), "total": len(sutras),
                  "pct": round((mstats.get("sutras_with_gathas") or 0) * 100.0 / max(len(sutras), 1), 1)},
        breakdown={"偈颂总数": mstats.get("total_gathas"), "含偈之经": mstats.get("sutras_with_gathas")},
        origin=["ontology/instances/manifest.json"],
        storage="ontology/instances/t####.json（gatha 标记）",
        generator="scripts/build_all_instances.py（偈颂识别保守策略）", update_cmd=REBUILD,
        note="偈颂节点，识别采取“宁可漏判、不可误判”。", live_key="manifest.stats.total_gathas")

    add("Mantra", count=mstats.get("total_mantras"), unit="咒语",
        coverage={"have": mstats.get("sutras_with_mantras"), "total": len(sutras),
                  "pct": round((mstats.get("sutras_with_mantras") or 0) * 100.0 / max(len(sutras), 1), 1)},
        breakdown={"咒语总数": mstats.get("total_mantras"), "含咒之经": mstats.get("sutras_with_mantras")},
        origin=["ontology/instances/manifest.json"],
        storage="ontology/instances/t####.json（mantra 标记）",
        generator="scripts/build_all_instances.py", update_cmd=REBUILD,
        note="咒语节点，按梵音特征 + “莎婆訶”结尾 + “即說咒曰”导语识别。", live_key="manifest.stats.total_mantras")

    add("Commentary", count=None, unit="部", status="field",
        origin=["ontology/instances/t####.json（cross_links / is_commentary）"],
        storage="ontology/instances/t####.json；注疏关系见 data/cross-links.json",
        generator="scripts/build_instance_links.py", update_cmd=REBUILD,
        note="注疏类，以实例字段与 cross-links 表达，未单列实例目录。")

    add("Translation", count=None, unit="组", status="field",
        origin=["ontology/parallel_translations.json", "ontology/instances/relations.json"],
        storage="ontology/parallel_translations.json + relation:translation_of",
        generator="scripts/build_instance_links.py", update_cmd=REBUILD,
        note="异译译本，以异译分组与 translation_of 关系表达。")

    add("Translator", count=n_persons_dir and len([p for p in persons if "译" in (p.get("category") or "") or "法师" in (p.get("name") or "")]) or None,
        unit="位", status="field",
        origin=["ontology/instances/persons/", "ontology/instances/manifest.json（translator 字段）"],
        storage="ontology/instances/persons/（category=祖师译经师）+ 每经 translator 字段",
        generator="scripts/build_all_instances.py", update_cmd=REBUILD,
        note="译者，由人物实例与经文 translator 字段共同承载。")

    for cid, label in [("Genre", "十二分教"), ("CanonCategory", "部类"), ("Division", "分部"),
                       ("Vehicle", "乘"), ("Mode", "显密"), ("ThreeBaskets", "三藏"),
                       ("Edition", "藏经版本"), ("SourceLanguage", "原本语言"), ("TranslationEra", "译时代")]:
        add(cid, count=None, unit="", status="field",
            origin=["ontology/instances/t####.json（字段）", "ontology/ontology.yaml（枚举定义）"],
            storage="ontology/instances/t####.json 的对应字段 / ontology.yaml 枚举",
            generator="scripts/build_all_instances.py", update_cmd=REBUILD,
            note="由实例字段或主档枚举承载，尚无独立实例目录。")

    # —— L1/L2/L3 义理层 ——
    add("Concept", count=len(concepts), unit="个",
        breakdown={"L1 教理本体": len(concept_L1), "L2 义理范畴": len(concept_L2), "L3 宗派行持": len(concept_L3)},
        origin=["ontology/instances/concepts/", "ontology/instances/m2_index.json"],
        storage="ontology/instances/concepts/c###.json（%d 个）" % n_concepts_dir,
        generator="scripts/build_m2_instances.py（并入旧 ontology-data.js）", update_cmd=REBUILD,
        note="M2 义理层概念实例，按 layer 字段分 L1/L2/L3。",
        samples=[c.get("id") + " " + (c.get("name") or "") for c in concepts[:6]],
        live_key="m2.concepts")

    add("Doctrine", count=len(concept_L2), unit="个",
        breakdown=dict(Counter((c.get("primary_sect") or "通途") for c in concept_L2).most_common(10)),
        origin=["ontology/instances/concepts/"],
        storage="ontology/instances/concepts/（layer=L2）",
        generator="scripts/build_m2_instances.py", update_cmd=REBUILD,
        note="义理范畴层（L2），含系统化教理范畴。", live_key="m2.concepts.L2")

    add("School", count=len(sects), unit="家",
        breakdown={"宗派": len(sects)},
        origin=["ontology/instances/sects/", "ontology/instances/m2_index.json"],
        storage="ontology/instances/sects/sec###.json（%d 个）" % n_sects_dir,
        generator="scripts/build_m2_instances.py", update_cmd=REBUILD,
        samples=[s.get("id") + " " + (s.get("name") or "") for s in sects], live_key="m2.sects")

    add("PanjiaoSystem", count=len(sects), unit="套",
        origin=["ontology/instances/sects/", "pages/panjiao.html"],
        storage="ontology/instances/sects/sec###.json（判教字段）+ pages/panjiao.html",
        generator="scripts/build_m2_instances.py", update_cmd=REBUILD,
        note="判教体系，与宗派实例一体两面。", live_key="m2.sects")

    add("Practice", count=len(concept_L3), unit="条", status="field",
        breakdown=dict(Counter((c.get("primary_sect") or "通途") for c in concept_L3).most_common(10)),
        origin=["ontology/instances/concepts/（layer=L3）"],
        storage="ontology/instances/concepts/（layer=L3 宗派行持层）",
        generator="scripts/build_m2_instances.py", update_cmd=REBUILD,
        note="法门/行持，含于 L3 宗派行持层。", live_key="m2.concepts.L3")

    # —— L5 人物层 ——
    add("Person", count=len(persons), unit="位",
        coverage={"have": len(persons), "total": len(persons), "pct": 100.0},
        breakdown=dict(pcat.most_common()),
        origin=["ontology/instances/persons/", "ontology/instances/m2_index.json"],
        storage="ontology/instances/persons/p###.json（%d 个）" % n_persons_dir,
        generator="scripts/build_m2_instances.py", update_cmd=REBUILD,
        samples=[p.get("id") + " " + (p.get("name") or "") for p in persons[:6]],
        live_key="m2.persons")

    for cid, cat, label in [("Buddha", "佛陀", "佛陀"), ("Bodhisattva", "菩萨", "菩萨"),
                            ("Arhat", "阿罗汉", "阿罗汉"), ("Patriarch", "祖师译经师", "祖师"),
                            ("ModernScholar", "学者", "现代学者"), ("Deity", "神祇", "护法诸天"),
                            ("FolkFigure", "民间信仰", "民间信仰人物")]:
        cnt = pcat.get(cat)
        if cid == "Patriarch":
            cnt = pcat.get("祖师译经师", 0) + pcat.get("祖师", 0)
        if cid == "ModernScholar":
            cnt = pcat.get("学者", 0) + pcat.get("现代学者", 0)
        if cid == "Deity":
            cnt = pcat.get("神祇", 0) + pcat.get("护法诸天", 0)
        add(cid, count=cnt, unit="位",
            coverage={"have": cnt, "total": len(persons), "pct": round((cnt or 0) * 100.0 / max(len(persons), 1), 1)},
            origin=["ontology/instances/persons/（category 字段）"],
            storage="ontology/instances/persons/p###.json（category=%s）" % cat,
            generator="scripts/build_m2_instances.py", update_cmd=REBUILD,
            samples=[p.get("id") + " " + (p.get("name") or "") for p in persons if (p.get("category") or "") == cat][:6],
            live_key="m2.persons.category")

    add("Protector", count=pcat.get("护法", 0), unit="位",
        origin=["ontology/instances/persons/（category=护法）"],
        storage="ontology/instances/persons/p###.json", generator="scripts/build_m2_instances.py",
        update_cmd=REBUILD, note="护法类，目前多为法会/经中人名，独立实例待扩。", live_key="m2.persons.category")

    # —— M4 事件层 ——
    add("Event", count=council_evt + trans_evt + story_evt + da_cnt, unit="条",
        breakdown={"法会": da_cnt, "结集": council_evt, "译经传法": trans_evt, "本生故事": story_evt},
        origin=["ontology/instances/events.json", "ontology/dharma_assemblies.json"],
        storage="ontology/instances/events.json + ontology/dharma_assemblies.json",
        generator="scripts/extract_dharma_assemblies.py → scripts/build_events.py", update_cmd=REBUILD,
        note="M4 事件层四类事件合计。", live_key="events.all")

    add("DharmaAssembly", count=da_cnt, unit="会",
        coverage={"have": da.get("sutras_linked"), "total": len(sutras),
                  "pct": round((da.get("sutras_linked") or 0) * 100.0 / max(len(sutras), 1), 1)},
        breakdown={"法会数": da_cnt, "关联经数": da.get("sutras_linked")},
        origin=["ontology/dharma_assemblies.json"],
        storage="ontology/dharma_assemblies.json（assemblies 字典，%d 会）" % da_cnt,
        generator="scripts/extract_dharma_assemblies.py → scripts/build_dharma_assemblies.py",
        update_cmd=REBUILD,
        samples=[a.get("name") for a in list(assemblies.values())[:5]], live_key="dharma_assemblies")

    add("Council", count=council_evt, unit="次",
        origin=["ontology/instances/events.json（councils）"],
        storage="ontology/instances/events.json → councils 数组（%d 条）" % council_evt,
        generator="scripts/build_events.py", update_cmd=REBUILD,
        samples=[c.get("label_zh") for c in councils[:5]], live_key="events.councils")

    add("TransmissionEvent", count=trans_evt, unit="件",
        coverage={"have": mstats.get("sutras_with_transmission_event"), "total": len(sutras),
                  "pct": round((mstats.get("sutras_with_transmission_event") or 0) * 100.0 / max(len(sutras), 1), 1)},
        origin=["ontology/instances/events.json（transmission_events）"],
        storage="ontology/instances/events.json → transmission_events 数组（%d 条）" % trans_evt,
        generator="scripts/build_events.py → scripts/finalize_events.py", update_cmd=REBUILD,
        note="译经传法事件；失译经统一挂 te_unknown 单一聚合事件，不编造译者。",
        live_key="events.transmission")

    add("StoryEvent", count=story_evt, unit="则",
        coverage={"have": mstats.get("sutras_with_story_event"), "total": len(sutras),
                  "pct": round((mstats.get("sutras_with_story_event") or 0) * 100.0 / max(len(sutras), 1), 1)},
        origin=["ontology/instances/events.json（story_events）"],
        storage="ontology/instances/events.json → story_events 数组（%d 条）" % story_evt,
        generator="scripts/build_events.py", update_cmd=REBUILD,
        samples=[s.get("label_zh") for s in stories[:5]], live_key="events.stories")

    # —— 抽象类（无独立实例，结构性） ——
    for cid, note in [
        ("Entity", "根类，一切本体元素的总类。"),
        ("Axis", "轴元类（四轴定义）。"),
        ("Layer", "层元类（七层定义）。"),
        ("OntologyClass", "类元类（本页所列举的所有类）。"),
        ("DatatypeProperty", "数据属性元类。"),
        ("ObjectProperty", "关系谓词元类。"),
        ("Individual", "个体元类（ABox 实例的总类）。"),
        ("ThreeBaskets", "三藏结构类，由 Sutra/Vinaya/Sastra 承载。"),
        ("SutraPitaka", "经藏，由 Sutra 实例承载。"),
        ("VinayaPitaka", "律藏，由 Vinaya 实例承载。"),
        ("AbhidharmaPitaka", "论藏，由 Sastra 实例承载。"),
        ("IntroductoryPart", "序分，由科判结构承载。"),
        ("EssentialPart", "正宗分，由科判结构承载。"),
        ("CirculationPart", "流通分，由科判结构承载。"),
        ("CulturalElement", "文化外延元素，L6 外延层，实例待建。"),
    ]:
        add(cid, count=None, unit="", status="abstract",
            origin=["ontology/ontology.yaml"],
            storage="ontology/ontology.yaml（类定义）",
            generator="scripts/build_ontology.py", update_cmd=REBUILD,
            note=note)

    # 过滤掉不需要展示的占位


    # ---------- 4. 轴 / 层汇总 ----------
    tbox_classes = {c.get("id"): c for c in tbox.get("classes", []) or []}
    axes_sum, layers_sum = OrderedDict(), OrderedDict()
    for cid, meta in CLS.items():
        tc = tbox_classes.get(cid)
        if not tc:
            continue
        for a in (tc.get("axes") or []):
            e = axes_sum.setdefault(a, {"classes": 0, "instances": 0, "active": 0})
            e["classes"] += 1
            if meta["count"]:
                e["instances"] += meta["count"]
                e["active"] += 1
        l = tc.get("layer")
        if l:
            e = layers_sum.setdefault(l, {"classes": 0, "instances": 0, "active": 0})
            e["classes"] += 1
            if meta["count"]:
                e["instances"] += meta["count"]
                e["active"] += 1

    # ---------- 5. 源文件登记 ----------
    src_paths = [
        ("ontology/instances/manifest.json", "M3 文本层全量索引"),
        ("ontology/instances/m2_index.json", "M2 义理层轻量索引"),
        ("ontology/instances/events.json", "M4 事件层（结集/传法/故事）"),
        ("ontology/dharma_assemblies.json", "M4 法会索引"),
        ("ontology/instances/relations.json", "M2 关系三元组"),
        ("ontology/instances/instance-links.json", "义理↔文本反向索引"),
        ("ontology/instances/shard-map.json", "实例分片映射"),
        ("kepan/core.json", "科判数据"),
        ("ontology/tbox_data.json", "TBox 结构与关系（交互图）"),
        ("ontology/ontology.yaml", "本体主档（四轴×七层）"),
    ]
    sources = []
    for rel, desc in src_paths:
        st = fstat(P(rel))
        st["desc"] = desc
        sources.append(st)

    # ---------- 6. 输出 ----------
    out = OrderedDict()
    out["meta"] = {
        "version": "1.0.0",
        "generated_at": now,
        "generated_by": "scripts/build_ontology_index.py",
        "structure": "%d 类 / %d 关系谓词 / %d 数据属性" % (
            tbox.get("counts", {}).get("n_cls", len(tbox.get("classes", []))),
            tbox.get("counts", {}).get("n_rel", len(tbox.get("relations", []))),
            tbox.get("counts", {}).get("n_prop", len(tbox.get("properties", [])))),
        "note": "本页统计由脚本扫描原始索引生成；页面加载时会实时重算，本文件为快照与来源元数据。",
    }
    out["global"] = {
        "sutras": len(sutras),
        "sutra_files": len(sutra_files),
        "shards": shard_count,
        "chapters": mstats.get("total_chapters"),
        "paragraphs": mstats.get("total_paragraphs"),
        "gathas": mstats.get("total_gathas"),
        "mantras": mstats.get("total_mantras"),
        "concepts": len(concepts),
        "persons": len(persons),
        "core_sutras": len(core_sutras),
        "sects": len(sects),
        "kepan": len(kepan),
        "events": council_evt + trans_evt + story_evt + da_cnt,
        "assemblies": da_cnt,
        "councils": council_evt,
        "transmission_events": trans_evt,
        "story_events": story_evt,
        "relations": len(rels),
    }
    out["axes"] = axes_sum
    out["layers"] = layers_sum
    out["classes"] = CLS
    out["relations"] = {
        "total": len(rels),
        "by_type": dict(rel_types.most_common()),
        "storage": "ontology/instances/relations.json",
        "generator": "scripts/build_m2_instances.py",
        "origin": ["data/relations-expanded.json", "ontology/instances/relations.json"],
    }
    out["sources"] = sources

    dst = P("ontology", "ontology-index.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print("[OK] 已生成 %s" % os.path.relpath(dst, ROOT))
    print("     类 %d / 源文件 %d / 全局实例：经 %d · 概念 %d · 人物 %d · 事件 %d · 关系 %d · 科判 %d" % (
        len(CLS), len(sources), len(sutras), len(concepts), len(persons),
        council_evt + trans_evt + story_evt + da_cnt, len(rels), len(kepan)))


if __name__ == "__main__":
    main()

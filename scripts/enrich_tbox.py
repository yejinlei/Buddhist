#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 ontology/tbox_data.json 的「属性节点」补充丰富元信息。

权威来源：ontology/ontology.yaml（谓词定义 §relations、数据属性定义 §properties）。
本脚本重建 tbox_data.json 的 relations / properties 两段，为每个
对象属性（ObjectProperty）与数据属性（DatatypeProperty）补充：

    定义 description / 别名 aliases / 逆向 inverse / 对称 symmetric
    归属轴 axis / 关系组 group
    数据来源 origin / 存放位置 storage / 生成脚本 generator
    值域中文名、字段用途等

classes / axes / layers 原样保留（避免前端结构变化）。

用法: python3 scripts/enrich_tbox.py
"""
import json
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML = os.path.join(ROOT, "ontology", "ontology.yaml")
TBOX = os.path.join(ROOT, "ontology", "tbox_data.json")

GEN = "scripts/build_ontology.py（schema 导出）→ scripts/enrich_tbox.py（元信息增强）"
ORIGIN_HEAD = ["ontology/ontology.yaml", "data/ontology-schema.json（前端镜像）"]


def arr(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


# —— 关系组 → 轴 ——
GROUP_AXIS = {
    "分类关系类（A1 横向分类轴）": "A1",
    "文本结构关系类（A2 纵向内容轴）": "A2",
    "宗派判教关系类（A1 / L3）": "A1",
    "人物关系类（A3 人物传承轴）": "A3",
    "义理关系类（A2 / L1–L2）": "A2",
    "事件关系类（A4 事件缘起轴）": "A4",
}

# —— 关系组 → 数据来源 / 存放位置 ——
GROUP_SRC = {
    "分类关系类（A1 横向分类轴）": {
        "origin": ["ontology/instances/manifest.json（部类/分部/文体/乘/显密/版本字段）",
                   "ontology/instances/t####.json（category 等分类字段）"],
        "storage": "ontology/instances/relations.json（ABox 三元组）；分类枚举见 ontology/instances/t####.json 与 ontology/ontology.yaml",
    },
    "文本结构关系类（A2 纵向内容轴）": {
        "origin": ["ontology/instances/t####.json（chapters / paragraphs 结构字段）",
                   "kepan/core.json（古德三分科判）",
                   "ontology/instances/relations.json（ABox 三元组）"],
        "storage": "ontology/instances/relations.json；文本结构见 ontology/instances/t####.json 与 kepan/",
    },
    "宗派判教关系类（A1 / L3）": {
        "origin": ["ontology/instances/sects/sec###.json（宗派与判教字段）",
                   "ontology/instances/relations.json（ABox 三元组）"],
        "storage": "ontology/instances/relations.json + ontology/instances/sects/sec###.json",
    },
    "人物关系类（A3 人物传承轴）": {
        "origin": ["ontology/instances/persons/p###.json（人物实例）",
                   "ontology/instances/events.json（transmission_events 传法事件）",
                   "ontology/instances/relations.json（ABox 三元组）"],
        "storage": "ontology/instances/relations.json + ontology/instances/persons/p###.json",
    },
    "义理关系类（A2 / L1–L2）": {
        "origin": ["ontology/instances/concepts/c###.json（义理概念实例）",
                   "ontology/instances/relations.json（ABox 三元组）"],
        "storage": "ontology/instances/relations.json + ontology/instances/concepts/c###.json",
    },
    "事件关系类（A4 事件缘起轴）": {
        "origin": ["ontology/instances/events.json（结集/传法/本生故事）",
                   "ontology/dharma_assemblies.json（法会）",
                   "ontology/instances/relations.json（ABox 三元组）"],
        "storage": "ontology/instances/relations.json + ontology/instances/events.json + ontology/dharma_assemblies.json",
    },
}

# —— 数据属性 domain → 存放位置 / 来源 ——
DOM_SRC = {
    "所有类": {
        "origin": ["ontology/instances/t####.json、concepts/c###.json、persons/p###.json、sects/sec###.json、events.json（各实例文件通用字段）"],
        "storage": "ontology/instances/ 全部实例文件（t####.json / concepts / persons / sects / events.json）",
    },
    "Text": {
        "origin": ["ontology/instances/manifest.json", "ontology/instances/t####.json（经录元数据）"],
        "storage": "ontology/instances/t####.json（2506 部经元数据）",
    },
    "Chapter": {
        "origin": ["ontology/instances/t####.json（chapters 字段）"],
        "storage": "ontology/instances/t####.json → chapters 数组（47531 品/章）",
    },
    "Section": {
        "origin": ["ontology/instances/t####.json（paragraphs 字段）"],
        "storage": "ontology/instances/t####.json → paragraphs 数组（781474 段）",
    },
    "Gatha": {
        "origin": ["ontology/instances/t####.json（gatha 标记）"],
        "storage": "ontology/instances/t####.json（偈颂标记，10749 偈）",
    },
    "Mantra": {
        "origin": ["ontology/instances/t####.json（mantra 标记）"],
        "storage": "ontology/instances/t####.json（咒语标记，1876 咒）",
    },
    "Concept": {
        "origin": ["ontology/instances/concepts/（M2 ABox 概念实例）", "ontology/instances/m2_index.json"],
        "storage": "ontology/instances/concepts/c###.json + ontology/instances/m2_index.json",
    },
    "Doctrine": {
        "origin": ["ontology/instances/concepts/（M2 ABox 义理范畴）"],
        "storage": "ontology/instances/concepts/c###.json",
    },
    "Practice": {
        "origin": ["ontology/instances/concepts/（layer=L3 法门行持）"],
        "storage": "ontology/instances/concepts/c###.json（layer=L3）",
    },
    "Person": {
        "origin": ["ontology/instances/persons/（M2 ABox 人物实例）"],
        "storage": "ontology/instances/persons/p###.json",
    },
    "School": {
        "origin": ["ontology/instances/sects/（M2 ABox 宗派实例）"],
        "storage": "ontology/instances/sects/sec###.json",
    },
    "Event": {
        "origin": ["ontology/instances/events.json（M4 事件层）"],
        "storage": "ontology/instances/events.json",
    },
    "DharmaAssembly": {
        "origin": ["ontology/dharma_assemblies.json（M4 法会层）"],
        "storage": "ontology/dharma_assemblies.json",
    },
    "Kepan": {
        "origin": ["kepan/core.json（古德精判）", "kepan/shards/（结构科判分片）"],
        "storage": "kepan/core.json + kepan/shards/shard-000.json … shard-005.json",
    },
}

# —— 数据属性定义（客观释义） ——
PROP_DESC = {
    "bc:name": "实例的规范名称。",
    "bc:alias": "同一实体的其他称谓/异名，用于检索消歧。",
    "bc:definition": "义理概念/范畴的释义，取自佛学大词典等工具书，不杜撰。",
    "bc:sanskrit": "对应的梵文（或巴利/藏文）原语名。",
    "bc:description": "对实例的补充说明。",
    "bc:taisho_id": "CBETA 大正藏编号（T 号），如 T0235。",
    "bc:volume_count": "该经总卷数。",
    "bc:translator": "汉译者；失译者记为「失译 / 译人不详」。",
    "bc:translate_time": "译出年代或朝代。",
    "bc:translate_place": "译经地点（如长安、洛阳、建康）。",
    "bc:source_language": "所据原典语言（梵 / 巴利 / 藏 / 于阗等）。",
    "bc:translation_era": "所属译经时代（汉 / 魏晋 / 隋唐等）。",
    "bc:vehicle": "所属乘（大乘 / 小乘 / 一佛乘）。",
    "bc:mode": "显教或密教。",
    "bc:category": "所属大正藏部类（阿含 / 般若 / 法华…）。",
    "bc:genre": "十二分教文体（契经 / 应颂 / 因缘…）。",
    "bc:char_count": "字符数统计。",
    "bc:core_content": "该经主要内容概述。",
    "bc:core_doctrine": "该经 / 宗派的核心教理。",
    "bc:parallel_versions": "同经异译本列表。",
    "bc:edition_list": "存世藏经版本（宋 / 元 / 明 / 高丽…）。",
    "bc:keywords": "RAG 检索用关键词标签。",
    "bc:commentary_count": "历代注疏数统计。",
    "bc:chapter_no": "品/章在经中的序号。",
    "bc:chapter_title": "品/章标题。",
    "bc:section_no": "段落在章内的序号。",
    "bc:part_of_kepan": "所属科判三分（序分 / 正宗分 / 流通分）。",
    "bc:gatha_meter": "偈颂句式（五言 / 七言 / 四句等）。",
    "bc:mantra_siddham": "咒语的悉昙 / 梵字转写（音译加梵文）。",
    "bc:founder": "宗派创立者。",
    "bc:found_time": "宗派创立时间。",
    "bc:era": "人物 / 事件所属时代。",
    "bc:birth_place": "人物籍贯或出生地。",
    "bc:location": "事件发生地点。",
    "bc:audience": "法会当机众 / 听众。",
    "bc:event_time": "事件发生时间。",
    "bc:sutra_source": "义理概念的经论出处（t#### 经号）。",
    "bc:sect_interpretation": "各宗派对概念的诠释。",
    "bc:modern_interpretation": "现代学术 / 白话解读。",
}


def build_relations(rel_yaml):
    out = []
    for group, items in rel_yaml.items():
        src = GROUP_SRC.get(group, {})
        for r in items or []:
            out.append({
                "id": r["id"],
                "label": r.get("label", r["id"]),
                "group": group,
                "axis": GROUP_AXIS.get(group, ""),
                "domain": arr(r.get("domain")),
                "range": arr(r.get("range")),
                "inverse": r.get("inverse"),
                "symmetric": bool(r.get("symmetric", False)),
                "aliases": arr(r.get("aliases")),
                "description": r.get("description", ""),
                "origin": ORIGIN_HEAD + list(src.get("origin", [])),
                "storage": src.get("storage", ""),
                "generator": GEN,
            })
    return out


def build_properties(prop_yaml):
    out = []
    for p in prop_yaml:
        dom = arr(p.get("domain"))
        key = dom[0] if dom else "所有类"
        if key in ("all", "所有类"):
            key = "所有类"
        src = DOM_SRC.get(key, DOM_SRC["所有类"])
        out.append({
            "id": p["id"],
            "label": p.get("label", p["id"]),
            "domain": dom,
            "range": p.get("range"),
            "description": PROP_DESC.get(p["id"], ""),
            "origin": ORIGIN_HEAD + list(src.get("origin", [])),
            "storage": src.get("storage", ""),
            "generator": GEN,
        })
    return out


def main():
    y = yaml.safe_load(open(YAML, encoding="utf-8"))
    tbox = json.load(open(TBOX, encoding="utf-8"))

    rels = build_relations(y.get("relations", {}))
    props = build_properties(y.get("properties", []))

    tbox["relations"] = rels
    tbox["properties"] = props
    tbox["counts"] = {
        "n_cls": len(tbox.get("classes", [])),
        "n_rel": len(rels),
        "n_prop": len(props),
    }
    tbox["meta"] = {
        "version": "3.1.0",
        "generated_by": "scripts/enrich_tbox.py",
        "note": "对象属性 / 数据属性已补充定义、别名、逆向、归属轴、数据来源、存放位置、生成脚本等元信息；classes/axes/layers 取自既有 tbox_data.json。",
    }

    with open(TBOX, "w", encoding="utf-8") as f:
        json.dump(tbox, f, ensure_ascii=False, indent=1)

    # 同步增强 data/ontology-schema.json 的 relations（供本体页「四、关系谓词」表使用）
    schema_path = os.path.join(ROOT, "data", "ontology-schema.json")
    if os.path.exists(schema_path):
        schema = json.load(open(schema_path, encoding="utf-8"))
        for group, items in (schema.get("relations") or {}).items():
            src = GROUP_SRC.get(group, {})
            for r in items:
                r["origin"] = ORIGIN_HEAD + list(src.get("origin", []))
                r["storage"] = src.get("storage", "")
                r["axis"] = GROUP_AXIS.get(group, "")
                r["generator"] = GEN
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
        print("schema relations 已增强：", sum(len(v or []) for v in (schema.get("relations") or {}).values()))

    # 校验：每个属性节点都必须有 origin / storage
    bad = [r["id"] for r in rels if not r["origin"] or not r["storage"]]
    bad += [p["id"] for p in props if not p["origin"] or not p["storage"]]
    print("relations:", len(rels), "properties:", len(props), "classes:", len(tbox["classes"]))
    print("缺失 origin/storage 的属性节点:", bad or "无")


if __name__ == "__main__":
    main()

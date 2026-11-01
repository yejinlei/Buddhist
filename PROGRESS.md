# 白话翻译进度

## 总体进度
- 全量藏经：2495 部
- **已译并合格上线：516 部（20.7%）**
- 第 52 批（格式收敛批）：
  - 统一 16 个文件的白话字段格式为站点可读的 `translations`（此前 12 个用 `sections`、4 个用 `segments`，页面会渲染为空白）
  - 重译 `sishi_erzhang`《佛说四十二章经》全 42 章，覆盖率由 32% 提升至 100%
  - 8 个文件残留半角引号统一为全角「」『』
  - 全库复检：**516 部合格 / 0 部不合格**

## 质量标准
- 顶层字段：`id / title / translator / translations`，供经页直接读取
- 每段字段：`section / original_preview / modern`
- `original_preview` 逐字取自原文，各段顺次拼接 = 原文连续子串（一字不差）
- 段拼接覆盖率 ≥ 95%（绝大多数为 100%）
- 每段 `modern` 以【小标题】开头、含【义解】且义解有正文
- 全角标点「」『』，无半角引号，白话为简体
- 法数 / 术语 / 同本异译专项逐项核对

## 校验方式
- `python3 scripts/validate_baihua.py` 全量体检
- `python3 scripts/gen_baihua_index.py` 同步经页白话清单 `BAIHUA_AVAILABLE`

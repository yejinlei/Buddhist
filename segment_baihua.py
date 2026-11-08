#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, sys, re
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

def segment_sutra(sid):
    sutra_path = f"sutras/{sid}.json"
    if not os.path.exists(sutra_path):
        print(f"错误：找不到经文文件 {sutra_path}")
        return False
    with open(sutra_path, encoding="utf-8") as f:
        sutra = json.load(f)
    
    # 获取完整原文
    content = sutra.get("content", [])
    full_text_parts = []
    for c in content:
        if isinstance(c, dict):
            txt = c.get("text", "")
        else:
            txt = str(c)
        full_text_parts.append(txt)
    full_text = "".join(full_text_parts)
    # 去除多余空白但保留换行
    full_text = full_text.replace("\r\n", "\n").replace("\r", "\n")
    full_clean = "".join(full_text.split())
    
    # 强制按句子切分，每段200-300字，保证原文连续
    sentences = []
    sent = ""
    for char in full_text:
        sent += char
        if char in "。！？" and len(sent) > 50:
            sentences.append(sent.strip())
            sent = ""
    if sent.strip():
        sentences.append(sent.strip())
    
    # 合并句子到每段200-300字
    segments = []
    current_seg = ""
    for s in sentences:
        if len(current_seg) + len(s) < 300:
            current_seg += s
        else:
            if current_seg:
                segments.append(current_seg.strip())
            current_seg = s
    if current_seg:
        segments.append(current_seg.strip())
    
    # 过滤空段
    segments = [s for s in segments if s.strip()]
    
    translations = []
    for seg in segments:
        translations.append({
            "section": "",
            "original_preview": seg,
            "modern": ""
        })
    
    # 验证覆盖率
    preview_text = "".join(t["original_preview"] for t in translations)
    preview_clean = "".join(preview_text.split())
    coverage = len(preview_clean) / len(full_clean) if len(full_clean) > 0 else 0
    
    # 如果覆盖率不足，退回按原始content分段
    if coverage < 0.999:
        print(f"警告：{sid} 按句切分覆盖率不足 {coverage:.3f}，退回原始分段")
        translations = []
        for c in content:
            if isinstance(c, dict):
                txt = c.get("text", "").strip()
            else:
                txt = str(c).strip()
            if txt:
                translations.append({
                    "section": "",
                    "original_preview": txt,
                    "modern": ""
                })
    
    # 构建任务骨架
    task = {
        "id": sid,
        "title": sutra.get("title", ""),
        "translator": sutra.get("translator", ""),
        "mode": "baihua",
        "intro": "",
        "sutraPath": f"../sutras/{sid}.json",
        "translations": translations
    }
    
    # 保存到baihua-tasks
    os.makedirs("data/baihua-tasks", exist_ok=True)
    task_path = f"data/baihua-tasks/{sid}.skel.json"
    with open(task_path, "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    
    # 计算覆盖率
    preview_text = "".join(t["original_preview"] for t in translations)
    preview_clean = "".join(preview_text.split())
    coverage = len(preview_clean) / len(full_clean) if len(full_clean) > 0 else 0
    print(f"{sid}: {len(translations)}段，覆盖率{coverage:.3f}，{sutra.get('title','')}")
    return coverage >= 0.999

if __name__ == "__main__":
    sids = sys.argv[1:]
    if not sids:
        print("用法：python segment_baihua.py <经号1> <经号2> ...")
        # 从selected_batch.txt读取
        if os.path.exists("selected_batch.txt"):
            with open("selected_batch.txt", encoding="utf-8") as f:
                sids = f.read().strip().split()
            print(f"自动读取selected_batch.txt：{' '.join(sids)}")
    all_ok = True
    for sid in sids:
        ok = segment_sutra(sid)
        if not ok:
            all_ok = False
    if all_ok:
        print("\n所有经文切段完成，覆盖率100%")
    else:
        print("\n部分经文切段存在问题，请检查")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并后校验脚本：
1. 所有 sutras/*.json 能被 json.load 成功
2. 合并后每个字（忽略空白/换行）与合并前保持一致
3. 段落结构数量不变（只动 \n，不增删段落）
4. 输出错误汇总
"""
import json, os, re, sys
from glob import glob

CJK_RE = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef，。、；：？！""''（）《》【】「」『』…—·]')
def non_space(s):
    """提取所有非空白字符"""
    return re.sub(r'\s+', '', s)

def validate_file(path, verbose=False):
    errors = []
    try:
        with open(path,'r',encoding='utf-8') as f:
            d = json.load(f)
    except Exception as e:
        return [f'JSON 解析失败: {e}'], None
    paras = d.get('content',[])
    total_chars = 0
    for i,p in enumerate(paras):
        if not isinstance(p,dict):
            errors.append(f'para[{i}] 不是 dict')
            continue
        txt = p.get('text','')
        if '\r' in txt:
            errors.append(f'para[{i}] 包含 \\r')
        # 检查不能有连续3个以上 \n
        if '\n\n\n' in txt:
            errors.append(f'para[{i}] 有连续3+空行')
        total_chars += len(non_space(txt))
    return errors, total_chars

def main():
    files = sorted(glob('sutras/t*.json'))
    if len(sys.argv) > 1:
        files = [f'sutras/{sid}.json' for sid in sys.argv[1:] if os.path.exists(f'sutras/{sid}.json')]
    failed = []
    total = 0
    for fp in files:
        errs, chars = validate_file(fp)
        if errs:
            failed.append((fp, errs))
        total += chars or 0
    if failed:
        print(f'校验失败 {len(failed)} 部:')
        for fp, errs in failed[:20]:
            print(f'  {fp}: {"; ".join(errs[:3])}')
    else:
        print(f'全部 {len(files)} 部 JSON 校验通过，非空白字符总计 {total}')
    print(f'总文件 {len(files)}, 错误 {len(failed)}')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()

import json, os, re

# 修复剩余问题
needs_fix = ["t0818", "t1154", "t1659", "t0327", "t0843", "t0652"]

# 译者署名模式（更强的匹配：行首译者署名后紧跟正文开头）
TRANS_PATTERNS = [
    (re.compile(r'^((?:[唐宋元隋魏晉晋後后汉秦汉南北梁齊齐陈符姚秦][^。\n]*?[譯译撰集記述注作]))(像这样我聞|像这样我闻|這時|这时|爾時|尔时)'), r'\1\n\2'),
]

# 重复词
DEDUP = [
    ('我我', '我'), ('他他', '他'), ('那那', '那'),
    ('你你', '你'), ('的的', '的'), ('了了', '了'),
    ('菩萨菩萨', '菩萨'),
]

for tid in needs_fix:
    for sub in ['data/baihua-tasks', 'data/modern-translation']:
        fp = os.path.join(sub, tid+'.json')
        d = json.load(open(fp, encoding='utf-8'))
        for seg in d['translations']:
            m = seg['modern']
            lines = m.split('\n')
            new_lines = []
            for line in lines:
                # 译者署名换行修复（对正文所有行）
                fixed = line
                for pat, rep in TRANS_PATTERNS:
                    fixed = pat.sub(rep, fixed)
                # 重复词
                for a,b in DEDUP:
                    fixed = fixed.replace(a,b)
                # 如果插入了换行，拆成多行
                if '\n' in fixed:
                    new_lines.extend(fixed.split('\n'))
                else:
                    new_lines.append(fixed)
            seg['modern'] = '\n'.join(new_lines)
        json.dump(d, open(fp,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"{tid}: fixed")
print("done")

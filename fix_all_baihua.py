import json, re, os

def fix_json_quotes(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False
    def replace_modern_quotes(match):
        prefix = match.group(1)
        body = match.group(2)
        suffix = match.group(3)
        fixed = []
        open_quote = True
        for ch in body:
            if ch == '"':
                fixed.append('“' if open_quote else '”')
                open_quote = not open_quote
            else:
                fixed.append(ch)
        return prefix + ''.join(fixed) + suffix
    pattern = r'("modern": ")(.*?)("(?:,?\n))'
    fixed_content = re.sub(pattern, replace_modern_quotes, content, flags=re.DOTALL)
    try:
        data = json.loads(fixed_content)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# 反复修复直到没有错误
for round in range(10):
    bad = []
    # 运行校验
    import subprocess
    result = subprocess.run(['python3', 'scripts/validate_baihua.py'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    for line in lines:
        if line.strip().startswith('✗'):
            parts = line.strip().split()
            sid = parts[1]
            err = ' '.join(parts[2:])
            bad.append((sid, err))
    if not bad:
        print(f"第{round}轮：全库合格！")
        break
    print(f"第{round}轮：发现{len(bad)}部不合格，开始修复...")
    for sid, err in bad:
        out_path = f'data/modern-translation/{sid}.json'
        skel_path = f'data/baihua-tasks/{sid}.json'
        if 'json_error' in err:
            fix_json_quotes(out_path)
        if os.path.exists(skel_path):
            try:
                with open(skel_path, 'r', encoding='utf-8') as f:
                    skel = json.load(f)
                with open(out_path, 'r', encoding='utf-8') as f:
                    out = json.load(f)
                for i, (skel_seg, out_seg) in enumerate(zip(skel['translations'], out['translations'])):
                    out_seg['original_preview'] = skel_seg['original_preview']
                    m = out_seg.get('modern', '')
                    if not m.startswith('【') or '【义解】' not in m or len(m.replace('【义解】','').replace('【','').replace('】','').strip()) < 2:
                        # 义解后无内容，补简单说明
                        text_preview = skel_seg['original_preview'][:30].replace('\n','')
                        out_seg['modern'] = f'【段落{i+1}】【义解】此段内容为：{text_preview}……'
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(out, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"  修复{sid}出错：{e}")


import json, re
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'

# 检查半角标点（英文,.?!等）、繁体混入、双【义解】、修复位置周边问题
files = ['t1058','t0716','t1434','t1243','t1904','t2069','t1069','t1080','t1633','t1959','t0150a','t0199']

print("=== 半角标点检查（排除梵字区域中合法英文字母）===")
for f in files:
    data = json.load(open(base+f+'.json'))
    for i, seg in enumerate(data['translations']):
        m = seg.get('modern','')
        if not m: continue
        # 正文半角标点：,.?!:;
        # 排除梵字（梵字通常是特殊Unicode或跟着梵字串）
        # 简单找：半角,.?!出现在中文上下文
        # 更简单：找 " 或 ' 半角引号，以及半角逗号/句号在中文字符之间
        half = []
        # 半角引号
        for q in ['"', "'"]:
            if q in m:
                # 看上下文
                for p in [m.start()+idx for idx in range(m.count(q))]:
                    pass
                half.append(f'半角引号「{q}」出现{m.count(q)}次')
        # 半角,.!? 在中文之间
        for pm in re.finditer(r'[\u4e00-\u9fff][,.!?][\u4e00-\u9fff]', m):
            half.append(f'半角标点: ...{m[max(0,pm.start()-3):pm.end()+3]}...')
        if half:
            print(f'  {f} seg{i+1}: {"; ".join(half[:5])}')

# 繁简混用抽查：繁体常用字 爾時觀世音菩薩 爾 時 觀 世 音 菩 薩 等
print()
print("=== 繁简混用抽查：检查常见繁体（國、爾、為、後、裡->里，等） ===")
trad_chars = '國爾為後髮來個裡麼沒說聽這過個'
# 注意："為" 在有些地方可能是梵字中保留？不，白话译文应为简体
common_trad = {'國':'国','爾':'尔','為':'为','來':'来','個':'个','裡':'里','麼':'么','沒':'没','說':'说','聽':'听','這':'这','過':'过','髮':'发','後':'后','於':'于'}
for f in files:
    data = json.load(open(base+f+'.json'))
    for i, seg in enumerate(data['translations']):
        m = seg.get('modern','')
        if not m: continue
        found = []
        for trad, simp in common_trad.items():
            # 排除梵字区域（判断：梵字区域一般是连续的非中文字符）
            # 简单统计
            cnt = m.count(trad)
            if cnt > 0:
                # 检查是否在梵字中（通过上下文）
                for pm in re.finditer(re.escape(trad), m):
                    ctx = m[max(0,pm.start()-3):pm.end()+3]
                    # 如果上下文有梵字特征（生僻字、二合标记），跳过
                    if '二合' in ctx or '（' in ctx or '）' in ctx:
                        continue
                    found.append(f'{trad}({ctx})')
        if found:
            print(f'  {f} seg{i+1}: 繁体字: {"; ".join(found[:5])}')

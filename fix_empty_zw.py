#!/usr/bin/env python3
"""
修复空正文v2——处理这种结构：
【小标题】xxx
（简体化后的文言原文，没有标签——这是正文）
【义解】xxx（模板套话）
【正文】（空）
→ 把中间那段文言原文移入【正文】，重写模板义解
"""
import json, os, re, opencc, sys, time
sys.stdout.reconfigure(encoding='utf-8')

TRANS_DIR = 'data/modern-translation'
cc = opencc.OpenCC('t2s.json')

_FORCE = [
    ('為','为'),('於','于'),('無','无'),('說','说'),('爾','尔'),('雲','云'),
    ('蓋','盖'),('恆','恒'),('呪','咒'),('過','过'),('還','还'),('這','这'),
    ('麼','么'),('裡','里'),('會','会'),('個','个'),('並','并'),('薩','萨'),
    ('葉','叶'),('闍','阇'),('餘','余'),('後','后'),('係','系'),('徵','征'),
    ('鍾','钟'),('醜','丑'),('瞭','了'),('藉','借'),('佈','布'),('儘','尽'),
    ('驚','惊'),('亂','乱'),('師','师'),('恥','耻'),('國','国'),('實','实'),
    ('現','现'),('對','对'),('發','发'),('應','应'),('當','当'),('時','时'),
    ('來','来'),('從','从'),('長','长'),('門','门'),('關','关'),('點','点'),
    ('樂','乐'),('經','经'),('書','书'),('學','学'),('問','问'),('話','话'),
    ('語','语'),('見','见'),('聞','闻'),('覺','觉'),('義','义'),('題','题'),
    ('標','标'),('觀','观'),('羅','罗'),('毘','毗'),('優','优'),('難','难'),
    ('歡','欢'),('轉','转'),('輪','轮'),('迴','回'),('靜','静'),('慮','虑'),
    ('處','处'),('遠','远'),('離','离'),('邊','边'),('盡','尽'),('脫','脱'),
    ('煩','烦'),('惱','恼'),('貪','贪'),('瞋','嗔'),('癡','痴'),('惡','恶'),
    ('業','业'),('報','报'),('緣','缘'),('諦','谛'),('滅','灭'),('訶','诃'),
    ('補','补'),('觸','触'),('愛','爱'),('願','愿'),('識','识'),
]

def to_simp(s):
    if not s: return ''
    if not isinstance(s, str): s = str(s)
    s = cc.convert(s)
    for k,v in _FORCE:
        s = s.replace(k, v)
    return s

TEMPLATE_YJ_PATTERNS = [
    re.compile(r'^.{0,30}中此段指出'),
    re.compile(r'^.{0,30}译.{0,20}经典'),
    re.compile(r'^此段(是|为|主要|宣说|讲述|开示|叙述|记述|记载|说明)'),
    re.compile(r'^这段(是|为|主要|宣说|讲述|开示|叙述|记述|记载|说明)'),
    re.compile(r'破疑执而显正理'),
    re.compile(r'为后学树立圭臬'),
    re.compile(r'令修行者不堕邪见'),
]

def is_template_yj(yj):
    for p in TEMPLATE_YJ_PATTERNS:
        if p.search(yj):
            return True
    return False

def make_yj(title, zw_first100):
    """从标题和正文首句生成简短、有针对性的义解"""
    # 提取正文首句
    first_sent = re.split(r'[。！？]', zw_first100)[0] if zw_first100 else ''
    first_sent = first_sent[:40]
    t = title.strip('：:·，,。.')
    if first_sent and len(first_sent) > 10:
        return f'此段叙说{t}，经文记：{first_sent}。'
    return f'此段叙说{t}的内容。'

def fix_segment(mod):
    """修复单段：把【小标题】和【义解】之间的无标签文言移入【正文】"""
    # 用正则精确切分：找【小标题】...【义解】...【正文】
    # 先定位三个标签位置
    p_title = mod.find('【小标题】')
    p_yj = mod.find('【义解】')
    p_zw = mod.find('【正文】')
    
    if p_title < 0:
        return mod  # 没法修
    
    # 提取标题：【小标题】后到第一个换行或【义解】之前
    after_title = mod[p_title+5:]
    # 标题是到第一个换行或【义解】为止（标题本身不跨多行）
    m = re.match(r'([^\n【]+)', after_title)
    title = m.group(1).strip() if m else ''
    after_title = after_title[len(m.group(0)) if m else 0:]
    
    # 从after_title开始找【义解】
    p_yj_rel = after_title.find('【义解】')
    if p_yj_rel < 0:
        return mod
    # 标题和【义解】之间的内容（无标签文言）
    mid_text = after_title[:p_yj_rel].strip()
    
    # 提取义解
    after_yj = after_title[p_yj_rel+4:]
    p_zw_rel = after_yj.find('【正文】')
    if p_zw_rel < 0:
        return mod
    yj_text = after_yj[:p_zw_rel].strip()
    
    # 提取现有正文
    zw_text = after_yj[p_zw_rel+4:].strip()
    
    # 如果正文为空但中间有文本，把中间文本作为正文
    if len(zw_text) < 30 and mid_text:
        zw_text = mid_text
        mid_text = ''
    
    # 如果正文仍不够长，检查义解后面是否贴了文言（在【义解】标签和义解文字之间，或义解文字里混了文言）
    if len(zw_text) < 30:
        # 义解通常较短（<150字），如果yj_text很长，里面可能混了文言
        yj_paras = [p.strip() for p in re.split(r'\n+', yj_text) if p.strip()]
        yj_end_idx = 0
        for i, p in enumerate(yj_paras):
            if is_template_yj(p) and i == 0:
                yj_end_idx = 1
                break
            # 检测文言特征
            wy_count = len(re.findall(r'[之乎者也曰矣焉哉吾汝弗勿毋乃遂俱咸悉]', p))
            if wy_count >= 3 and len(p) > 30:
                break
            yj_end_idx = i + 1
            if yj_end_idx >= 2:
                break
        new_yj = '\n'.join(yj_paras[:yj_end_idx]).strip()
        more_wy = '\n'.join(yj_paras[yj_end_idx:]).strip()
        if more_wy:
            zw_text = (zw_text + '\n' + more_wy).strip()
        yj_text = new_yj
    
    # 如果义解是模板套话，重写
    if is_template_yj(yj_text):
        yj_text = make_yj(title, zw_text[:200])
    
    # 简体化
    title = to_simp(title)
    yj_text = to_simp(yj_text)
    zw_text = to_simp(zw_text)
    
    # 清理末尾截断
    zw_text = re.sub(r'[…。\s]*$', '', zw_text).rstrip('，：；、,;:')
    
    # 组装
    parts = [f'【小标题】{title}']
    if yj_text:
        parts.append(f'【义解】{yj_text}')
    parts.append(f'【正文】{zw_text}')
    return '\n'.join(parts)

def process_file(tid):
    fpath = os.path.join(TRANS_DIR, f'{tid}.json')
    if not os.path.exists(fpath): return False
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except: return False
    
    if 'title' in data:
        data['title'] = to_simp(data['title'])
    
    changed = 0
    for t in data.get('translations', []):
        if 'modern' not in t and 'explanation' in t:
            t['modern'] = t.pop('explanation')
        mod = t.get('modern', '')
        if 'section' in t:
            t['section'] = to_simp(str(t['section'])).strip('【】')
        
        new_mod = fix_segment(mod)
        if new_mod != mod:
            t['modern'] = new_mod
            changed += 1
    
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return changed

if __name__ == '__main__':
    batch_start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    
    all_tids = sorted([f.replace('.json','') for f in os.listdir(TRANS_DIR) if f.endswith('.json') and f != 'tree.json'])
    all_tids = [t for t in all_tids if re.match(r'^t\d+[a-z]?$', t)]
    batch = all_tids[batch_start:batch_start+batch_size]
    
    t0 = time.time()
    total_changed = 0
    ok = 0
    for tid in batch:
        c = process_file(tid)
        if c is not False:
            ok += 1
            total_changed += c
    print(f'[{batch_start}:{batch_start+batch_size}] {ok}部 修改{total_changed}段 {time.time()-t0:.1f}s')

#!/usr/bin/env python3
"""批量修复-分批运行版，不重新加载opencc，快速处理"""
import json, os, re, opencc, time, sys
sys.stdout.reconfigure(encoding='utf-8')

TRANS_DIR = 'data/modern-translation'
cc = opencc.OpenCC('t2s.json')

# 字级繁→简强制映射（覆盖opencc词切漏字）
_FORCE = [
    ('為','为'),('於','于'),('無','无'),('說','说'),('爾','尔'),('雲','云'),('蓋','盖'),('恆','恒'),
    ('呪','咒'),('過','过'),('還','还'),('這','这'),('麼','么'),('裡','里'),('會','会'),('個','个'),
    ('並','并'),('薩','萨'),('葉','叶'),('闍','阇'),('餘','余'),('後','后'),('係','系'),('徵','征'),
    ('鍾','钟'),('醜','丑'),('瞭','了'),('藉','借'),('佈','布'),('儘','尽'),('驚','惊'),('亂','乱'),
    ('師','师'),('恥','耻'),('國','国'),('實','实'),('現','现'),('對','对'),('發','发'),('應','应'),
    ('當','当'),('時','时'),('來','来'),('從','从'),('長','长'),('門','门'),('關','关'),('點','点'),
    ('樂','乐'),('經','经'),('書','书'),('學','学'),('問','问'),('話','话'),('語','语'),('見','见'),
    ('聞','闻'),('覺','觉'),('義','义'),('題','题'),('標','标'),('觀','观'),('羅','罗'),('毘','毗'),
    ('優','优'),('難','难'),('歡','欢'),('轉','转'),('輪','轮'),('迴','回'),('靜','静'),('慮','虑'),
    ('處','处'),('遠','远'),('離','离'),('邊','边'),('盡','尽'),('脫','脱'),('煩','烦'),('惱','恼'),
    ('貪','贪'),('瞋','嗔'),('癡','痴'),('惡','恶'),('業','业'),('報','报'),('緣','缘'),('諦','谛'),
    ('滅','灭'),('訶','诃'),('補','补'),('觸','触'),('愛','爱'),('願','愿'),('識','识'),
]

def to_simp(s):
    if not s: return ''
    if not isinstance(s, str):
        s = str(s)
    s = cc.convert(s)
    for k, v in _FORCE:
        s = s.replace(k, v)
    return s

def fix_modern(mod):
    if not mod: return mod
    # 简体化
    mod = to_simp(mod)
    # 标签分隔（连写的【】换行）
    mod = re.sub(r'】\s*(?=【)', '】\n', mod)
    # 标签归一化
    mod = mod.replace('【白话译文】', '【正文】').replace('【译文】', '【正文】').replace('【今译】', '【正文】')
    mod = mod.replace('【要旨】', '【义解】').replace('【题解】', '【义解】').replace('【提要】', '【义解】')
    mod = mod.replace('【说明】', '【义解】').replace('【科判】', '【义解】').replace('【总标】', '【义解】')
    mod = mod.replace('【章节】', '【小标题】').replace('【标题】', '【小标题】').replace('【品节】', '【小标题】')
    # 半角→全角
    mod = re.sub(r'(?<=[\u4e00-\u9fff]),(?=[\u4e00-\u9fff])', '，', mod)
    mod = re.sub(r'(?<=[\u4e00-\u9fff])\?(?=[\u4e00-\u9fff])', '？', mod)
    mod = re.sub(r'(?<=[\u4e00-\u9fff])!(?=[\u4e00-\u9fff])', '！', mod)
    mod = re.sub(r'(?<=[\u4e00-\u9fff]):(?=[\u4e00-\u9fff])', '：', mod)
    mod = re.sub(r'(?<=[\u4e00-\u9fff]);(?=[\u4e00-\u9fff])', '；', mod)
    # 清理末尾空占位
    lines = mod.split('\n')
    cleaned = []
    for l in lines:
        l = l.rstrip()
        # 去掉末尾纯省略/待续
        if re.fullmatch(r'【正文】\s*(?:待续|未完|略|（略）|\(略\)|…+|。\s*。+|[\s…]+)', l):
            l = '【正文】'
        cleaned.append(l)
    mod = '\n'.join(cleaned)
    return mod

def process_file(tid):
    fpath = os.path.join(TRANS_DIR, f'{tid}.json')
    if not os.path.exists(fpath):
        return False
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return False
    
    if 'title' in data:
        data['title'] = to_simp(data['title'])
    
    for t in data.get('translations', []):
        if 'modern' not in t and 'explanation' in t:
            t['modern'] = t.pop('explanation')
        if 'section' in t:
            t['section'] = to_simp(t['section']).strip('【】')
        if 'modern' in t:
            t['modern'] = fix_modern(t['modern'])
    
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

if __name__ == '__main__':
    batch_start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    
    all_tids = sorted([f.replace('.json','') for f in os.listdir(TRANS_DIR) if f.endswith('.json') and f != 'tree.json'])
    all_tids = [t for t in all_tids if re.match(r'^t\d+[a-z]?$', t)]
    
    batch = all_tids[batch_start:batch_start+batch_size]
    t0 = time.time()
    ok = 0
    for tid in batch:
        if process_file(tid):
            ok += 1
    print(f'批次[{batch_start}:{batch_start+batch_size}] 完成 {ok}/{len(batch)} 用时{time.time()-t0:.1f}s')

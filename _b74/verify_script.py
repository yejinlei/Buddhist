# -*- coding: utf-8 -*-
import json, re, unicodedata

IDS = ['t2865','t2839','t2784','t2855','t2882','t1275']

def load(p):
    return json.load(open(p, encoding='utf-8'))

def nospace(s):
    return re.sub(r'\s+','',s)

# half-width quotes and ascii punctuation
def check_ascii_quotes(s):
    hits=[]
    for ch in ['"',"'",'`']:
        if ch in s: hits.append(ch)
    return hits

results={}
for sid in IDS:
    mt=load(f'data/modern-translation/{sid}.json')
    bt=load(f'data/baihua-tasks/{sid}.json')
    su=load(f'sutras/{sid}.json')
    orig_full=''.join(c['text'] for c in su['content'])
    orig_ns=nospace(orig_full)
    trans=mt['translations']
    btrans=bt['translations']
    info={'id':sid,'n_mt':len(trans),'n_bt':len(btrans)}
    # 1. preview matches skeleton
    diff_seg=[]
    for i,(t,b) in enumerate(zip(trans,btrans)):
        if t['original_preview']!=b['original_preview']:
            diff_seg.append(i)
    info['preview_mismatch_seg']=diff_seg
    info['n_match']=(len(trans)==len(btrans))
    # 2. concat preview (non-space) is substring of original (non-space)
    cat_ns=nospace(''.join(t['original_preview'] for t in trans))
    info['concat_is_substr_orig_ns']= (cat_ns in orig_ns)
    # also concat with whitespace vs original with whitespace
    cat=''.join(t['original_preview'] for t in trans)
    info['concat_is_substr_orig_raw']= (cat in orig_full)
    # find longest common / position
    idx=orig_ns.find(cat_ns)
    info['concat_start']=idx
    info['concat_len']=len(cat_ns)
    info['orig_len']=len(orig_ns)
    # 3. modern format
    bad_title=[]
    bad_yijie=[]
    for i,t in enumerate(trans):
        m=t['modern']
        if not m.startswith('【'):
            bad_title.append(i)
        if '【义解】' not in m:
            bad_yijie.append(i)
        # ensure 义解 non-empty after marker
        mm=m.split('【义解】')
        if len(mm)>1 and mm[1].strip()=='':
            bad_yijie.append(('empty',i))
    info['modern_not_start_bracket']=bad_title
    info['modern_no_yijie']=bad_yijie
    # 4. ascii quotes anywhere in modern
    aq={}
    for i,t in enumerate(trans):
        h=check_ascii_quotes(t['modern'])
        if h: aq[i]=h
    info['ascii_quotes']=aq
    # 5. 咒文照录区 - identify segments/yijie portions. We'll just collect all traditional chars.
    # Build traditional char set (common) - use hant2simp mapping if available
    results[sid]=info

for sid in IDS:
    print('='*30, sid)
    print(json.dumps(results[sid], ensure_ascii=False, indent=1))

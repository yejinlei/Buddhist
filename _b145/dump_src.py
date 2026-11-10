import json,os,glob,re
root='.'
def norm(s):
    return re.sub(r'\s+','',s or '')
for tid in ['t0207']:
    sp=f'{root}/sutras/{tid}.json'
    s=json.load(open(sp,encoding='utf-8'))
    paras=[c.get('text','').strip() for c in s.get('content',[]) if c.get('text','').strip()]
    # 去掉卷号行
    paras=[p for p in paras if not re.match(r'^卷[上下一二三四五六七八九十百0-9]+', p)]
    out={'tid':tid,'title':s.get('title',''),'tr':s.get('translator',''),'paras':paras}
    with open(f'{root}/data/baihua-tasks/{tid}.json','w',encoding='utf-8') as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
    with open(f'_b145/{tid}.src.txt','w',encoding='utf-8') as f:
        for i,p in enumerate(paras,1):
            f.write(f'---[{i}]---\n{p}\n\n')
    # full text char count
    ft=norm(''.join(paras))
    print(tid, s.get('title'), 'paras', len(paras), 'chars', len(ft))

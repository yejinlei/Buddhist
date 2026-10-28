#!/usr/bin/env python3
"""保底策略：所有佛经原典都生成对齐，短经段级，长经按位置切分章级块"""
import json, os, re
from difflib import SequenceMatcher

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUTRA_DIR=os.path.join(ROOT,'sutras')
OUT_DIR=os.path.join(ROOT,'data','segment_alignments')
os.makedirs(OUT_DIR,exist_ok=True)

NON_SUTRA=re.compile(r'(疏$|義記$|义记$|目錄$|目录$|禮懺文|礼忏文|儀軌$|仪轨$|祈願|祈愿|戒本疏|律抄$)')
MAX_SEG=800

KEY_TERMS=sorted(set([
    '阿耨多羅三藐三菩提','須菩提','善男子','善女人','阿羅漢','辟支佛','如來','世尊','般若波羅蜜','波羅蜜',
    '布施','忍辱','持戒','精進','禪定','般若','須陀洹','斯陀含','阿那含','恒河沙','三千大千世界','七宝',
    '五眼','肉眼','天眼','慧眼','法眼','佛眼','滅度','無我相','四句偈','夢幻泡影','應無所住',
    '極樂世界','阿彌陀佛','觀世音菩薩','大勢至菩薩','一心不亂','阿鞞跋致','不退轉','莊嚴','功德',
    '涅槃','菩提','煩惱','生死','輪迴','緣起','性空','中道','真如','法身','無明','十二因緣','六波羅蜜',
    '四諦','八正道','六度','聲聞','緣覺','七寶池','八功德水','蓮華','信受奉行','皆大歡喜','陀羅尼','比丘',
    '菩薩','闡提','須彌山','忉利天','兜率天','閻浮提','舍利弗','目犍連','大迦葉','文殊師利','普賢菩薩',
    '梵王','帝釋','夜叉','羅刹','轉輪聖王','四天王','摩尼','旃檀','比丘尼','優婆塞','優婆夷',
]), key=lambda x:-len(x))

def load(sid):
    p=os.path.join(SUTRA_DIR,f'{sid}.json')
    return json.load(open(p,encoding='utf-8')) if os.path.exists(p) else None

def get_paras(d):
    ps=[]
    for ci,c in enumerate(d.get('content') or []):
        text=c.get('text') or ''
        for pi,p in enumerate(re.split(r'(?<=[。！？；])\s*|\n+', text)):
            p=p.strip()
            if p and len(p)>=2: ps.append((ci,pi,p))
    return ps

def extr_title(text,fb):
    if not text: return fb or '正文'
    first=text.strip().split('\n')[0][:80]
    m=re.search(r'([\u4e00-\u9fff]{2,12}品(?:第[一二三四五六七八九十百零〇\d]+)?(?:之[一二三四五六七八九十\d]+)?)',first)
    return m.group(1) if m else (fb or first[:20] or '正文')

def para_keys(p):
    ks=set()
    for k in KEY_TERMS:
        if k in p: ks.add(k)
    if len(ks)<2:
        for i in range(0,len(p)-1,3):
            ks.add('g'+p[i:i+2])
    return ks

def anchor_align(rps, ops):
    if not rps or not ops: return {}
    rk=[para_keys(p) for p in rps]; ok=[para_keys(p) for p in ops]
    n,m=len(rps),len(ops)
    pairs=[]
    for i in range(n):
        jlo=max(0,int(i*m/n)-20); jhi=min(m,int(i*m/n)+21)
        best=(0.05,-1)
        for j in range(jlo,jhi):
            a,b=rk[i],ok[j]
            if not a or not b: continue
            s=len(a&b)/len(a|b)+sum(0.3 for k in a&b if not k.startswith('g'))
            if s>best[0]: best=(s,j)
        if best[1]>=0: pairs.append((i,best[1],best[0]))
    pairs.sort(key=lambda x:-x[2])
    used_r=set(); used_o=set(); mp={i:[] for i in range(n)}
    for i,j,s in pairs:
        if i in used_r or j in used_o: continue
        mp[i].append(j); used_r.add(i); used_o.add(j)
    last_j=0
    for i in range(n):
        if not mp[i]:
            j=max(last_j,min(int((i+0.5)*m/n),m-1))
            mp[i].append(j); last_j=j
    return {i:sorted(js) for i,js in mp.items() if js}

def split_chunks(ps, n_chunks):
    """按段落位置均匀分成 n_chunks 块"""
    if not ps: return []
    n=len(ps); chunks=[]
    size=n/n_chunks
    for k in range(n_chunks):
        a=int(k*size); b=int((k+1)*size) if k<n_chunks-1 else n
        chunks.append((a,b))
    return chunks

def build_any(gid,title,slist):
    vs=[]
    for s in slist:
        d=load(s['id'])
        if not d: continue
        ps=[p for _,_,p in get_paras(d)]
        if ps: vs.append({'id':s['id'],'tr':s.get('translator','失译'),'ti':s.get('title',''),'ps':ps,
                         'd':d})
    if len(vs)<2: return None
    # 选最短为参考
    vs.sort(key=lambda x:len(x['ps']))
    ref=vs[0]; oths=vs[1:]
    n_ref=len(ref['ps'])
    use_chapter = n_ref>MAX_SEG
    if use_chapter:
        # 按参考长度切 n_chunks ≈ n_ref/200 块
        n_chunks=max(8,min(80, n_ref//200))
        ref_chunks=split_chunks(ref['ps'],n_chunks)
        # 其他译本按比例也切 n_chunks 块
        als=[]
        for ci,(ra,rb) in enumerate(ref_chunks):
            refs={ref['id']:list(range(ra,rb))}
            for o in oths:
                n_oth=len(o['ps'])
                oa=int(ra/n_ref*n_oth); ob=int(rb/n_ref*n_oth)
                if ob<=oa: ob=oa+1
                ob=min(ob,n_oth)
                refs[o['id']]=list(range(oa,ob))
            # 取块首句作为keyword
            kw=ref['ps'][ra][:14] if ra<len(ref['ps']) else f'第{ci+1}段'
            als.append({'id':ci+1,'refs':refs,'keyword':kw})
        return {'group_id':gid,'group_title':title,'mode':'chapter','n_chunks':n_chunks,
                'versions':[{'id':v['id'],'translator':v['tr'],'title':v['ti'],'n_paras':len(v['ps'])} for v in vs],
                'alignments':als,'_paras':{v['id']:list(v['ps']) for v in vs}}
    else:
        omaps=[(o,anchor_align(ref['ps'],o['ps'])) for o in oths]
        als=[]
        for ri,rp in enumerate(ref['ps']):
            refs={ref['id']:[ri]}
            for o,m in omaps:
                if ri in m: refs[o['id']]=m[ri]
            als.append({'id':ri+1,'refs':refs,'keyword':rp[:12]})
        return {'group_id':gid,'group_title':title,'mode':'segment',
                'versions':[{'id':v['id'],'translator':v['tr'],'title':v['ti'],'n_paras':len(v['ps'])} for v in vs],
                'alignments':als,'_paras':{v['id']:list(v['ps']) for v in vs}}

def mkid(t,ids):
    return re.sub(r'[^\w]','',t)[:14]+'_'+'_'.join(ids[:2])

def main():
    par=json.load(open(os.path.join(ROOT,'ontology/parallel_translations.json'),encoding='utf-8'))
    mf=[]; kept=[]; dropped=[]
    for g in par:
        title=g.get('title',''); sl=g.get('sutras',[])
        if len(sl)<2: continue
        if NON_SUTRA.search(title):
            dropped.append(title); continue
        cm=max((s.get('actual_char_count') or s.get('official_char_count') or 0) for s in sl)
        if cm<500: dropped.append(title+'(过短)'); continue
        gid=mkid(title,[s['id'] for s in sl])
        res=build_any(gid,title,sl)
        if not res: kept.append(gid); continue
        with open(os.path.join(OUT_DIR,gid+'.json'),'w',encoding='utf-8') as f:
            json.dump(res,f,ensure_ascii=False,indent=2)
        n=len(res['alignments']); m=res['mode']
        mf.append({'group_id':gid,'group_title':title,'mode':m,'n_alignments':n,'n_versions':len(res['versions']),
                   'versions':[{'id':v['id'],'translator':v['translator'],'title':v['title']} for v in res['versions']]})
        kept.append(gid)
        print(f'[OK] {title} → {m} ({n}组, {len(sl)}译)')
    with open(os.path.join(OUT_DIR,'manifest.json'),'w',encoding='utf-8') as f:
        json.dump(mf,f,ensure_ascii=False,indent=2)
    print(f'\n=== 汇总 ===')
    print(f'对齐成功：{len(mf)} 组（段级 {sum(1 for x in mf if x["mode"]=="segment")}, 章级 {sum(1 for x in mf if x["mode"]=="chapter")}）')
    print(f'过滤非原典：{len(dropped)}: {dropped}')
    if kept: print(f'失败：{len(kept)}: {kept}')

if __name__=='__main__':
    main()

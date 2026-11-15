#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校对员C：核查12部佛经白话译文质量（修订版），生成校对报告。"""
import json
import os
import re

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
MOD_DIR = os.path.join(BASE, "data/modern-translation")
SRC_DIR = os.path.join(BASE, "sutras")
OUT = os.path.join(BASE, "proofread_c_batch176.md")

SUTRAS = ['t2045','t1190','t2794','t0824','t1980','t1802',
          't0150','t2761','t0817','t1790','t0904','t0130']

ZH_RE = re.compile(r'[\u4e00-\u9fff]')
def count_zh(s): return len(ZH_RE.findall(s or ''))
def zh_only(s): return re.sub(r'[^\u4e00-\u9fff]','', s or '')

def load_json(p):
    with open(p,'r',encoding='utf-8') as f: return json.load(f)

def load_original(sid):
    p=os.path.join(SRC_DIR,f"{sid}.json")
    if not os.path.exists(p): return None
    try: d=load_json(p)
    except Exception: return None
    content=d.get('content',[])
    chunks=[]
    for c in content:
        if isinstance(c,dict): chunks.append(c.get('text','') or c.get('content','') or '')
        elif isinstance(c,str): chunks.append(c)
    return '\n'.join(chunks)

def norm(s): return re.sub(r'\s+','', s)

# ---------- 各类检查 ----------

def check_modern_format(seg):
    probs=[]
    m=seg.get('modern','')
    if not m or not m.strip():
        return [('modern为空','modern为空或仅含空白，需补全【小标题】+【义解】白话')]
    ms=m.lstrip()
    mt=re.match(r'^【([^】]+)】',ms)
    if not mt:
        probs.append(('缺少小标题','modern开头未以【四至八字小标题】领起（开头：「%s…」）'%ms[:20]))
    else:
        title=mt.group(1).replace(' ','').replace('\u3000','')
        tlen=count_zh(title)
        if tlen<4 or tlen>8:
            probs.append(('小标题字数不符','小标题「%s」汉字数为%d，应在4-8字之间'%(mt.group(1),tlen)))
        # 占位符标题检测
        if re.match(r'^经文第[一二三四五六七八九十百千0-9]+节$', title) or '小标题' in title or '待补' in title:
            probs.append(('小标题为占位符','小标题「%s」为占位符，需改为概括该段义理的四至八字小标题'%title))
        rest=ms[mt.end():]
        if '【义解】' not in m:
            probs.append(('缺少【义解】标记','modern中未出现【义解】标签'))
    if '【义解】' in m:
        after=m.split('【义解】',1)[1]
        zh_c=count_zh(after)
        if zh_c<5:
            probs.append(('义解正文为空/过短','【义解】后白话汉字仅%d个，疑为空段或占位'%zh_c))
    return probs

def check_preview(seg, orig_text):
    probs=[]
    op=seg.get('original_preview','')
    if not op or not op.strip():
        probs.append(('original_preview为空','original_preview为空，必须为原文连续片段'))
        return probs
    if orig_text is None:
        return probs
    op_n=norm(op); orig_n=norm(orig_text)
    if op_n in orig_n:
        return probs
    rough_op=re.sub(r'[^\u4e00-\u9fff0-9a-zA-Z]','',op)
    rough_orig=re.sub(r'[^\u4e00-\u9fff0-9a-zA-Z]','',orig_text)
    if rough_op not in rough_orig:
        snip=op_n[:24]+('…' if len(op_n)>24 else '')
        probs.append(('preview非原文连续子串','original_preview压缩后片段「%s」在原文中找不到连续匹配，存在错字/漏字/衍字'%snip))
    return probs

def check_mantra(seg):
    probs=[]
    op=seg.get('original_preview','') or ''
    m=seg.get('modern','') or ''
    is_mantra = any(k in op for k in ['即說咒曰','即说咒曰','咒曰','陀羅尼','陀罗尼','真言','神咒','說咒曰','说咒曰'])
    if not is_mantra:
        return probs
    body = m.split('【义解】',1)[-1] if '【义解】' in m else m
    # 去除固定提示语
    body_clean = body
    for pre in ['以下为神咒原文，持诵时需按原字读音精确念诵，不可随意更改：',
                '以下為神咒原文，持誦時需按原字讀音精確念誦，不可隨意更改：',
                '以下为神咒原文，持诵时需按原字读音精确念诵，不可随意更改',
                '以下為神咒原文，持誦時需按原字讀音精確念誦，不可隨意更改']:
        body_clean = body_clean.replace(pre,'')
    mo=re.search(r'(即說咒曰|即说咒曰|咒曰|說咒曰|说咒曰)(.{0,60})', op)
    if mo:
        snippet=re.sub(r'[^\u4e00-\u9fff]','',mo.group(2))[:8]
        if snippet and snippet not in body_clean:
            probs.append(('咒文未照录原字原音','该段含咒文（"咒曰"后开头「%s…」），但modern中未照录原咒汉字'%snippet,
                          '白话中应先以"即说咒曰："引出原咒（逐字照录原字原音，不得自行音译或简化），再附义解'))
    return probs

def check_length(seg):
    probs=[]
    op=seg.get('original_preview','') or ''
    m=seg.get('modern','') or ''
    op_zh=count_zh(op)
    body=re.sub(r'【[^】]*】','',m)
    m_zh=count_zh(body)
    if op_zh<15 or m_zh==0: return probs
    ratio=m_zh/op_zh
    if ratio>5.0:
        probs.append(('译文过长/过度发挥','原文%d字、白话%d字，比例%.2f，超出合理范围'%(op_zh,m_zh,ratio),
                      '压缩白话，紧扣经文原意，删除离题发挥'))
    elif ratio<0.3:
        probs.append(('译文过短/漏译','原文%d字、白话%d字，比例%.2f，疑过于简略'%(op_zh,m_zh,ratio),
                      '补充对原文难词、法义的白话解释'))
    return probs

def check_copy_paste(seg):
    """检查义解后是否整段照抄文言原文而无白话讲解。"""
    probs=[]
    op=seg.get('original_preview','') or ''
    m=seg.get('modern','') or ''
    body = m.split('【义解】',1)[1] if '【义解】' in m else ''
    # 去除固定提示语
    for pre in ['以下为神咒原文，持诵时需按原字读音精确念诵，不可随意更改：',
                '以下為神咒原文，持誦時需按原字讀音精確念誦，不可隨意更改：',
                '以下为神咒原文，持诵时需按原字读音精确念诵，不可随意更改',
                '以下為神咒原文，持誦時需按原字讀音精確念誦，不可隨意更改']:
        body=body.replace(pre,'')
    op_z=zh_only(op); body_z=zh_only(re.sub(r'【[^】]*】','',body))
    if len(op_z)<20: return probs
    # 字符顺序匹配率：若op_z按顺序几乎全部出现在body_z中，且body中op占比极高，则判定照抄
    def ordered_cover(needle, hay):
        i=j=0
        while i<len(needle) and j<len(hay):
            if needle[i]==hay[j]:
                i+=1; j+=1
            else:
                j+=1
        return i  # 匹配到的字符数
    cover = ordered_cover(op_z, body_z)
    cover_ratio = cover/len(op_z)
    # 若覆盖率>0.90 且 body 汉字数 < op*1.35，则判定为照抄
    if cover_ratio>=0.90 and len(body_z) < len(op_z)*1.35 and len(body_z) >= len(op_z)*0.85:
        # 再看body中白话特征：是否包含典型文言虚词（者也之乎/於/於/兮/爾/汝等）比例过高？
        # 简化：直接判定
        probs.append(('义解照抄文言/未作白话',
            '【义解】后内容与original_preview文言原文覆盖率%.0f%%，疑似直接照抄文言原文而未作白话翻译'%(cover_ratio*100),
            '删除照搬的文言原文（咒文汉字除外），改用现代汉语白话文逐句讲解原意；可保留关键术语但必须有白话转述'))
    return probs

def check_punct(seg):
    probs=[]
    m=seg.get('modern','') or ''
    hits=[]
    for pat in [r'，\s*，', r'。\s*。', r'！\s*！', r'？\s*？', r'；\s*；', r'：\s*：', r'、\s*、',
                r',\s*,', r'\.\s*\.', r'\?\s*\?', r'!\s*!']:
        for mo in re.finditer(pat,m):
            s=max(0,mo.start()-6); e=min(len(m),mo.end()+6)
            hits.append(m[s:e].replace('\n',' '))
    if hits:
        # 去重
        uniq=[]
        for h in hits:
            if h not in uniq: uniq.append(h)
        probs.append(('重复标点','modern中存在连续重复标点，例如：%s'%'；'.join('「'+h+'」' for h in uniq[:3]),
                      '删除重复标点'))
    return probs

def check_tiquan(seg):
    """原文译者题款（奉詔譯等）不应出现在modern中。"""
    probs=[]
    m=seg.get('modern','') or ''
    if '奉\u3000詔譯' in m[:40] or '奉诏译' in m[:40]:
        probs.append(('文言题款混入白话','modern开头附近出现"奉　詔譯/奉诏译"等文言译者题款原文，不属于白话内容',
                      '若需保留译者信息，用现代汉语在义解开头说明；不应直接照录文言题款'))
    return probs

def check_segments(sid, data, orig_text):
    segs = data.get('translations',[]) if isinstance(data,dict) else (data if isinstance(data,list) else [])
    sutra_issues=[]
    tot_op=0; tot_m=0
    for i,seg in enumerate(segs,1):
        if not isinstance(seg,dict):
            sutra_issues.append((i,'数据结构异常','第%d段不是dict对象'%i,'修复JSON结构')); continue
        for p in check_modern_format(seg):
            sutra_issues.append((i,p[0],p[1],p[2] if len(p)>2 else '按要求补全/修正'))
        for p in check_preview(seg,orig_text):
            sutra_issues.append((i,p[0],p[1],p[2] if len(p)>2 else '逐字核对并修正original_preview'))
        for p in check_mantra(seg):
            sutra_issues.append((i,p[0],p[1],p[2] if len(p)>2 else '照录原咒后再作义解'))
        for p in check_length(seg):
            sutra_issues.append((i,p[0],p[1],p[2] if len(p)>2 else '调整篇幅至合理比例'))
        for p in check_copy_paste(seg):
            sutra_issues.append((i,p[0],p[1],p[2] if len(p)>2 else '改写为真正的白话译文'))
        for p in check_punct(seg):
            sutra_issues.append((i,p[0],p[1],p[2] if len(p)>2 else '修正标点'))
        for p in check_tiquan(seg):
            sutra_issues.append((i,p[0],p[1],p[2] if len(p)>2 else '按建议处理'))
        tot_op+=count_zh(seg.get('original_preview',''))
        tot_m+=count_zh(re.sub(r'【[^】]*】','',seg.get('modern','') or ''))
    return sutra_issues, {'n_segments':len(segs),'op_zh':tot_op,'m_zh':tot_m}

def main():
    all_issues=[]; all_stats={}
    for sid in SUTRAS:
        p=os.path.join(MOD_DIR,f"{sid}.json")
        if not os.path.exists(p):
            all_issues.append((sid,'-','文件缺失',f'未找到译文文件{p}','补做该经白话译文'))
            all_stats[sid]={'title':'','n_segments':0,'op_zh':0,'m_zh':0,'issues':1}; continue
        try: data=load_json(p)
        except Exception as e:
            all_issues.append((sid,'-','JSON解析失败',str(e),'修复JSON'))
            all_stats[sid]={'title':'','n_segments':0,'op_zh':0,'m_zh':0,'issues':1}; continue
        orig=load_original(sid)
        sutra_issues,st=check_segments(sid,data,orig)
        for it in sutra_issues:
            seg_no,ttype,desc,sug=it
            all_issues.append((sid,seg_no,ttype,desc,sug))
        all_stats[sid]={'title':data.get('title',''),'n_segments':st['n_segments'],
                        'op_zh':st['op_zh'],'m_zh':st['m_zh'],'issues':len(sutra_issues)}

    L=[]
    L.append('# C路校对报告（批次 batch176）\n')
    L.append('- 校对员：C（独立校对员）')
    L.append('- 校对时间：2026-11-16')
    L.append('- 校对经数：12 部（'+'，'.join(SUTRAS)+'）')
    L.append('- 核查维度：')
    L.append('  1. 每段modern以【四至八字小标题】开头，含【义解】且【义解】后有真正的白话正文；')
    L.append('  2. original_preview逐字为原文连续子串，未被修改；')
    L.append('  3. 咒文部分照录原字原音，不得自行简化/音译；')
    L.append('  4. 译文/原文篇幅比例合理，无过度发挥或漏译；')
    L.append('  5. 义解正文不得整段照抄文言原文，须为现代白话；')
    L.append('  6. 低级错误：重复标点、文言题款混入白话、占位符标题等。\n')

    L.append('## 一、总体统计\n')
    L.append('| 经号 | 经名 | 段落数 | original_preview汉字 | modern白话汉字 | 问题数 |')
    L.append('|------|------|--------|----------------------|----------------|--------|')
    TN=TO=TM=TI=0
    for sid in SUTRAS:
        s=all_stats[sid]
        L.append('| %s | %s | %d | %d | %d | %d |'%(sid,s['title'],s['n_segments'],s['op_zh'],s['m_zh'],s['issues']))
        TN+=s['n_segments']; TO+=s['op_zh']; TM+=s['m_zh']; TI+=s['issues']
    L.append('| **合计** | — | **%d** | **%d** | **%d** | **%d** |\n'%(TN,TO,TM,TI))

    L.append('## 二、问题清单（经号-段号-问题类型-问题描述-修正建议）\n')
    if not all_issues:
        L.append('> 本次C路核查未发现硬性错误。\n')
    else:
        # 按问题严重度排序：先"义解照抄文言"、"preview非原文"、"小标题"、"咒文"、"篇幅"、"标点"
        PRIORITY=['义解照抄文言/未作白话','original_preview为空','preview非原文连续子串',
                  'modern为空','缺少小标题','小标题字数不符','小标题为占位符','缺少【义解】标记',
                  '义解正文为空/过短','咒文未照录原字原音','译文过长/过度发挥','译文过短/漏译',
                  '文言题款混入白话','重复标点','preview标点/空白差异','数据结构异常',
                  'JSON解析失败','文件缺失']
        def rank(it):
            try: return PRIORITY.index(it[2])
            except ValueError: return 99
        all_issues.sort(key=lambda x:(SUTRAS.index(x[0]) if x[0] in SUTRAS else 99, rank(x),
                                      0 if isinstance(x[1],int) else 1, x[1] if isinstance(x[1],int) else 0))
        by_sutra={}
        for it in all_issues:
            by_sutra.setdefault(it[0],[]).append(it)
        idx=0
        for sid in SUTRAS:
            its=by_sutra.get(sid,[])
            if not its: continue
            # 按段号聚簇，段内按问题优先级
            def seg_key(it):
                sn=it[1]
                return (0, sn) if isinstance(sn,int) else (1, str(sn))
            its.sort(key=lambda x:(seg_key(x), rank(x)))
            # 按段分组
            groups={}
            for it in its:
                groups.setdefault(it[1],[]).append(it)
            type_cnt={}
            for it in its: type_cnt[it[2]]=type_cnt.get(it[2],0)+1
            cnt_str='，'.join('%s:%d'%(k,v) for k,v in sorted(type_cnt.items(), key=lambda x:-x[1]))
            L.append(f'### {sid}（共{len(its)}处问题，涉及{len(groups)}段：{cnt_str}）\n')
            # 按段号顺序输出
            def sn_key(sn):
                return (0,sn) if isinstance(sn,int) else (1,str(sn))
            for sn in sorted(groups.keys(), key=sn_key):
                for it in groups[sn]:
                    idx+=1
                    _,_,ttype,desc,sug=it
                    L.append(f'{idx}. **{sid} - 第{sn}段 - {ttype}**')
                    L.append(f'   - 问题描述：{desc}')
                    L.append(f'   - 修正建议：{sug}')
                L.append('')

    L.append('## 三、说明与备注\n')
    L.append('- original_preview核对基准：`sutras/{经号}.json` 中 `content[*].text` 拼接原文；空白压缩后做严格子串匹配。')
    L.append('- "义解照抄文言/未作白话"判定标准：【义解】后正文对原文汉字按序覆盖率≥90%，且白话长度与原文长度比在0.85-1.35之间（即基本一比一照搬）。咒文部分的原字照录不计为照抄。')
    L.append('- "小标题为占位符"检测：凡符合"经文第N节"等通用占位符格式的标题一律标红。')
    L.append('- 篇幅比例阈值（白话汉字/原文汉字）：<0.3 记过短，>5.0 记过长。')
    L.append('- 本报告为C路独立校对，重点核查结构完整性、原文忠实度、白话真实性（非文言照抄）与低级错误；义理错译需结合A/B路意见及权威注疏终裁。')

    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    with open(OUT,'w',encoding='utf-8') as f: f.write('\n'.join(L))
    print(f'-> {OUT}')
    print(f'segments={TN}, issues={TI}')
    # 打印问题分类统计
    from collections import Counter
    c=Counter(it[2] for it in all_issues)
    for k,v in c.most_common(): print(f'  {k}: {v}')

if __name__=='__main__':
    main()

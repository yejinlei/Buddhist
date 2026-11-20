#!/usr/bin/env python3
"""全量线上经本校验：批量探测原文 + 白话 JSON 的可访问性与字段完整性。"""
import json, urllib.request, urllib.error, ssl, time, sys, os

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def jget(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Cache-Control':'no-cache'})
    return urllib.request.urlopen(req, timeout=timeout, context=CTX).read().decode('utf-8')

def check_one(tid):
    r = {"id": tid}
    # 原文
    try:
        raw = jget(f"https://yejinlei.github.io/Buddhist/sutras/{tid}.json")
    except urllib.error.HTTPError as e:
        r['orig_cat']='http_err'; r['orig_code']=e.code; return r
    except Exception as e:
        r['orig_cat']='http_err'; r['orig_msg']=str(e)[:100]; return r
    try:
        j = json.loads(raw)
    except Exception as e:
        r['orig_cat']='json_err'; r['orig_msg']=str(e)[:100]; return r
    if not isinstance(j, dict):
        r['orig_cat']='field_err'; r['orig_msg']='not dict'; return r
    for k in ('id','title'):
        if k not in j:
            r['orig_cat']='field_err'; r['orig_msg']=f'missing {k}'; return r
    orig = j.get('orig') or j.get('paragraphs')
    if not isinstance(orig, list):
        r['orig_cat']='orig_nonlist'; r['orig_msg']=f'orig type={type(orig).__name__}'; return r
    if len(orig)==0:
        r['orig_cat']='empty_orig'; return r
    r['orig_len']=len(orig)
    # 白话
    try:
        mraw = jget(f"https://yejinlei.github.io/Buddhist/data/modern-translation/{tid}.json", timeout=8)
    except urllib.error.HTTPError as e:
        r['mod_cat']='modern_404' if e.code==404 else 'modern_http_err'; r['mod_code']=e.code; return r
    except Exception as e:
        r['mod_cat']='modern_http_err'; r['mod_msg']=str(e)[:80]; return r
    try:
        mj = json.loads(mraw)
    except Exception as e:
        r['mod_cat']='modern_json_err'; r['mod_msg']=str(e)[:100]; return r
    if not isinstance(mj, dict):
        r['mod_cat']='modern_field_err'; r['mod_msg']='not dict'; return r
    segs = mj.get('moderns')
    if not isinstance(segs, list):
        r['mod_cat']='modern_field_err'; r['mod_msg']=f'moderns type={type(segs).__name__}'; return r
    bad = []
    for i,m in enumerate(segs):
        if not isinstance(m, dict):
            bad.append(f'[{i}] not dict'); break
        for k in ('xiaobiaoti','yijie','zhengwen'):
            if k not in m:
                bad.append(f'[{i}] missing {k}'); break
        if bad: break
        if not (m.get('zhengwen') or '').strip():
            bad.append(f'[{i}] zhengwen empty'); break
    r['mod_len']=len(segs)
    if not segs:
        r['mod_cat']='modern_empty'; return r
    if bad:
        r['mod_cat']='modern_field_err'; r['mod_msg']=bad[0]; return r
    r['mod_cat']='modern_ok'
    return r

def main():
    idx = json.loads(jget("https://yejinlei.github.io/Buddhist/sutras/index-light.json"))
    items = idx['items'] if isinstance(idx, dict) else idx
    ids = [it['id'] for it in items if 'id' in it]
    print(f"待校验: {len(ids)} 部", flush=True)

    import concurrent.futures
    results = []
    t0 = time.time()
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(check_one, tid): tid for tid in ids}
        for fut in concurrent.futures.as_completed(futs):
            try:
                r = fut.result()
            except Exception as e:
                r = {"id":futs[fut],"orig_cat":"exception","orig_msg":str(e)[:100]}
            results.append(r)
            done += 1
            if done % 200 == 0:
                print(f"  已完成 {done}/{len(ids)}  耗时 {time.time()-t0:.1f}s", flush=True)

    # 统计
    stats = {}
    errs = {}
    for r in results:
        for k in ('orig_cat','mod_cat'):
            v = r.get(k)
            if v:
                stats[v] = stats.get(v,0)+1
                if v not in ('ok','modern_ok','modern_404'):
                    errs.setdefault(v,[]).append(r)

    out = {'total':len(ids),'stats':stats,'results':results,'errs':{k:[{'id':x['id'],'msg':x.get('orig_msg') or x.get('mod_msg')} for x in v[:20]] for k,v in errs.items()}}
    with open('/tmp/audit_full.json','w',encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n=== 完成 {len(ids)} 部，总耗时 {time.time()-t0:.1f}s ===")
    for k,v in sorted(stats.items(), key=lambda x:-x[1]):
        print(f"  {k}: {v}")
    for k,v in errs.items():
        print(f"  ERR {k} 示例: {[x['id'] for x in v[:5]]}")

if __name__ == '__main__':
    main()

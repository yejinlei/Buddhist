#!/usr/bin/env python3
"""Quick finalize: aggregate figures/doctrines top-level, re-shard, update manifest."""
import json, os, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INST_DIR = ROOT/'ontology'/'instances'
SHARD_DIR = INST_DIR/'shards'
os.makedirs(SHARD_DIR, exist_ok=True)

# Load events
ev = json.load(open(INST_DIR/'events.json',encoding='utf-8'))
story_src_to_ids = {}
for se in ev['story_events']:
    sid = se['source_sutra']
    story_src_to_ids.setdefault(sid, []).append(se['id'])

# Aggregate per-instance and update
items = json.load(open(ROOT/'sutras'/'index-light.json',encoding='utf-8'))['items']
fixed_f=fixed_d=fixed_s=0
alias_map = {
    'xinjing_xuanzang':'t0251','xinjing_jiumo':'t0250','xinjing_fayue':'t0252',
    'jingang_jiumo':'t0235','amituo_jiumo':'t0366','yaoshi_xuanzang':'t0450',
    'yulan_pen':'t0685','fo_yijiao':'t0389','bada_renjue':'t0779',
    'sishi_erzhang':'t0784','puxian_xingyuan':'t0293',
}
all_ids = [it['id'] for it in items] + list(alias_map.keys())

for sid in all_ids:
    # if alias, copy from master
    if sid in alias_map:
        mid = alias_map[sid]
        mfp = INST_DIR/f'{mid}.json'; afp = INST_DIR/f'{sid}.json'
        if mfp.exists() and afp.exists():
            m=json.load(open(mfp,encoding='utf-8'))
            d=json.load(open(afp,encoding='utf-8'))
            for f in ('dharma_assembly','councils','transmission_events','story_events',
                     'figures','doctrines','figure_mentions','doctrine_mentions','gathas','mantras'):
                if m.get(f): d[f]=m[f]
            d['id']=sid; d['alias_of']=mid
            json.dump(d, open(afp,'w',encoding='utf-8'),ensure_ascii=False)
        continue
    fp = INST_DIR/f'{sid}.json'
    if not fp.exists(): continue
    try:
        d = json.load(open(fp,encoding='utf-8'))
    except: continue
    figs=[]; docs=[]
    for ch in d.get('chapters',[]):
        figs.extend(ch.get('figures') or [])
        docs.extend(ch.get('doctrines') or [])
    figset=sorted(set(figs)); docset=sorted(set(docs))
    if figset and d.get('figures')!=figset:
        d['figures']=figset; fixed_f+=1
    if docset and d.get('doctrines')!=docset:
        d['doctrines']=docset; fixed_d+=1
    # story events back-link
    if sid in story_src_to_ids:
        wants = sorted(set(story_src_to_ids[sid]))
        if d.get('story_events')!=wants:
            d['story_events']=wants; fixed_s+=1
    json.dump(d, open(fp,'w',encoding='utf-8'),ensure_ascii=False)

print(f'fix figures:{fixed_f} doctrines:{fixed_d} story_links:{fixed_s}')

# Collect all text instances
all_insts=[]
for fp in glob.glob(str(INST_DIR/'*.json')):
    n=os.path.basename(fp)
    if n in ('manifest.json','events.json','instance-links.json','dharma_assemblies.json'): continue
    if 'shard' in n: continue
    try:
        d=json.load(open(fp,encoding='utf-8'))
        if d.get('type')=='Text': all_insts.append(d)
    except: continue
all_insts.sort(key=lambda x:x['id'])
print(f'total instances: {len(all_insts)}')

# Reshard
for sp in glob.glob(str(SHARD_DIR/'shard-*.json')):
    os.remove(sp)
SHARD_SIZE=25
shard_manifest=[]
for i in range(0,len(all_insts),SHARD_SIZE):
    idx=i//SHARD_SIZE
    chunk=all_insts[i:i+SHARD_SIZE]
    fn=f'shard-{idx:03d}.json'
    json.dump(chunk, open(SHARD_DIR/fn,'w',encoding='utf-8'),ensure_ascii=False)
    shard_manifest.append({"file":f"ontology/instances/shards/{fn}",
                           "start":chunk[0]['id'],"end":chunk[-1]['id'],"count":len(chunk)})
print(f'shards: {len(shard_manifest)}')

# Build manifest stats
stats={
    "version":"3.1.0-m4",
    "total":len(all_insts),
    "chapters":sum(len(x.get('chapters',[])) for x in all_insts),
    "paragraphs":sum(sum(len(ch.get('paragraphs',[])) for ch in x.get('chapters',[])) for x in all_insts),
    "gathas":sum(len(x.get('gathas',[])) for x in all_insts),
    "mantras":sum(len(x.get('mantras',[])) for x in all_insts),
    "with_figures":sum(1 for x in all_insts if x.get('figures')),
    "with_doctrines":sum(1 for x in all_insts if x.get('doctrines')),
    "sutras_with_dharma_assembly":sum(1 for x in all_insts if x.get('dharma_assembly')),
    "sutras_with_council":sum(1 for x in all_insts if x.get('councils')),
    "sutras_with_transmission":sum(1 for x in all_insts if x.get('transmission_events')),
    "sutras_with_story":sum(1 for x in all_insts if x.get('story_events')),
    "dharma_assemblies":len(set(x.get('dharma_assembly','') for x in all_insts if x.get('dharma_assembly'))),
    "councils_total_refs":sum(len(x.get('councils',[])) for x in all_insts if x.get('councils')),
    "transmission_total_refs":sum(len(x.get('transmission_events',[])) for x in all_insts if x.get('transmission_events')),
    "story_total_refs":sum(len(x.get('story_events',[])) for x in all_insts if x.get('story_events')),
    "shards":shard_manifest,
}
json.dump(stats, open(INST_DIR/'manifest.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
for k,v in stats.items():
    if k!='shards': print(f'  {k}: {v}')

# Update instance-links with councils/trans/stories aggregated reverse
try:
    links=json.load(open(INST_DIR/'instance-links.json',encoding='utf-8'))
except: links={"meta":{}}
links['councils']={c['id']:{"label":c['label_zh'],"sutras":[s for s in c.get('related_sutras',[]) if s in {x['id'] for x in all_insts}]} for c in ev['councils']}
links['transmission_events']={t['id']:{"label":t['label_zh'],"subtype":t.get('subtype',''),"sutras":[s for s in t.get('related_sutras',[]) if s in {x['id'] for x in all_insts}]} for t in ev['translation_events']}
links['story_events']={se['id']:{"label":se['label_zh'],"subtype":se.get('subtype',''),"source_sutra":se['source_sutra']} for se in ev['story_events']}
links['meta']={"version":"3.1.0-m4","total":len(all_insts),"councils":len(ev['councils']),
              "translation_events":len(ev['translation_events']),"story_events":len(ev['story_events']),
              "dharma_assemblies":32}
json.dump(links, open(INST_DIR/'instance-links.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('instance-links updated.')

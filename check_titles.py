#!/usr/bin/env python3
import json, os
BASE='/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks'
b=json.load(open(os.path.join(BASE,'t1994b.json')))
for i,t in enumerate(b['translations']):
    o=t['original_preview']
    if '璉三生至' in o[:30]: print('璉三生 b', i, 'g', 108+i, repr(o[:60]))
    if o.lstrip().startswith('口似乞兒'): print('口似 b', i, 'g', 108+i, repr(o[:60]))
    if '勘辯' in o[:15]: print('勘辯 b', i, 'g', 108+i, repr(o[:60]))
    if '自術' in o[:15]: print('自術 b', i, 'g', 108+i, repr(o[:60]))

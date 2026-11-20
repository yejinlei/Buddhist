#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
with open('/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/t2075.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for i, t in enumerate(data['translations']):
    if i >= 95:
        print(f'=== {i+1} ===')
        print(t['original_preview'])

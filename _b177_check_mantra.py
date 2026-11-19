import json
d = json.load(open('/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/t1185b.json', encoding='utf-8'))
for i, seg in enumerate(d['translations']):
    m = seg['modern']
    if any(k in m for k in ['唵', '曩莫', '薩', '萨', '訶', '诃']):
        for line in m.split('\n'):
            s = line.strip()
            if len(s) > 20 and '【' not in s and '义解' not in s:
                print(i, repr(s[:120]))
                break

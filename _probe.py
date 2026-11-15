import json, os, sys

base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/'
files = ['t0818.json','t1278.json','t1185b.json','t1154.json','t0339.json','t1659.json','t0327.json','t0843.json','t2818.json','t1737.json','t0652.json','t0405.json']

for f in files:
    path = os.path.join(base, f)
    if not os.path.exists(path):
        print(f'=== MISSING: {f} ===')
        continue
    with open(path, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    print(f'=== {f} ===  type={type(data).__name__}')
    if isinstance(data, list):
        print(f'  segments: {len(data)}')
        if len(data) > 0:
            if isinstance(data[0], dict):
                print(f'  first seg keys: {list(data[0].keys())}')
                # show first segment summary
                for k, v in data[0].items():
                    s = str(v)[:80].replace('\n','\\n')
                    print(f'    {k}: {s}')
            else:
                print(f'  first seg type: {type(data[0]).__name__}')
    elif isinstance(data, dict):
        print(f'  top keys: {list(data.keys())}')
        for k in data.keys():
            v = data[k]
            if isinstance(v, list):
                print(f'  key={k}, len={len(v)}')
                if len(v) > 0 and isinstance(v[0], dict):
                    print(f'    first item keys: {list(v[0].keys())}')
                    for kk, vv in v[0].items():
                        s = str(vv)[:80].replace('\n','\\n')
                        print(f'      {kk}: {s}')

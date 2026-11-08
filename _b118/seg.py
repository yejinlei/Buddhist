import json,sys
tid=sys.argv[1]; idx=int(sys.argv[2])
d=json.load(open(f'data/baihua-tasks/{tid}.json',encoding='utf-8'))
print(repr(d['translations'][idx]['original_preview'])[:600])

import json,sys
tid=sys.argv[1]
d=json.load(open(f'data/baihua-tasks/{tid}.json',encoding='utf-8'))
ps=d.get('paragraphs',[])
open(f'_b144/{tid}.src.txt','w',encoding='utf-8').write('\n\n'.join(p['text'] for p in ps))
print(f'{tid} paragraphs={len(ps)}')

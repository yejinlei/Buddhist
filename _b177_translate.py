import json, os, sys
sys.path.insert(0, '/home/user/workspace/13511660557912876654/buddhist-ontology')
from translate_baihua import translate_segment

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/"
batch = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659", "t0327", "t0843", "t2818", "t1737", "t0652", "t0405"]

for tid in batch:
    fp = os.path.join(base_dir, tid + ".json")
    with open(fp, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['baihua_translator'] = "白話文編譯組"
    cnt = 0
    for seg in data['translations']:
        original = seg['original_preview']
        if not seg.get('modern', '').strip():
            seg['modern'] = translate_segment(original, tid)
            cnt += 1
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{tid}: translated {cnt}/{len(data['translations'])} segments")
print("Batch 177 translation done.")

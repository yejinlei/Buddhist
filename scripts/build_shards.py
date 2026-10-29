#!/usr/bin/env python3
"""把 ontology/instances/*.json（除 events/manifest）按 id 升序分桶打包为分片。"""
import json, os, glob, re

D = 'ontology/instances'
OUT = os.path.join(D, 'shards')
os.makedirs(OUT, exist_ok=True)
MAX_BYTES = 20 * 1024 * 1024  # 20MB 单文件硬上限

# 只收集 t#### / t####[a-z] / 已知中文别名 id 的实例文件
INSTANCE_ID_RE = re.compile(r'^(t\d{4}[a-z]?|amituo_jiumo|bada_renjue|fo_yijiao|jingang_jiumo|puxian_xingyuan|sishi_erzhang|xinjing_fayue|xinjing_jiumo|xinjing_xuanzang|yaoshi_xuanzang|yulan_pen)$')

def main():
    files = sorted(
        fp for fp in glob.glob(D + '/*.json')
        if INSTANCE_ID_RE.match(os.path.basename(fp)[:-5])
        and os.path.getsize(fp) > 0
    )
    # 清理旧分片
    old = glob.glob(os.path.join(OUT, 'shard-*.json'))
    for f in old:
        os.remove(f)


    # 按文件大小贪心分桶（首次适配递减）
    items = []
    for fp in files:
        sid = os.path.basename(fp)[:-5]
        sz = os.path.getsize(fp)
        with open(fp, encoding='utf-8') as fh:
            obj = json.load(fh)
        items.append((sid, sz, obj))

    # 大文件优先
    items.sort(key=lambda x: -x[1])
    bins = []  # [(total_size, [objs])]
    for sid, sz, obj in items:
        placed = False
        for b in bins:
            if b[0] + sz <= MAX_BYTES:
                b[1].append((sid, obj))
                b[0] += sz
                placed = True
                break
        if not placed:
            bins.append([sz, [(sid, obj)]])

    # 最后按片内首 id 排序（读经页 fetch 顺序友好）
    shard_map = {}
    for i, b in enumerate(bins):
        b[1].sort(key=lambda x: x[0])
        shard_id = f'shard-{i:03d}'
        payload = {'meta': {'shard_id': shard_id, 'count': len(b[1])}, 'instances': {}}
        for sid, obj in b[1]:
            payload['instances'][sid] = obj
            shard_map[sid] = shard_id
        # 序列化
        data = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
        fp_out = os.path.join(OUT, f'{shard_id}.json')
        with open(fp, 'wb') as fh:
            pass
        with open(fp_out, 'w', encoding='utf-8') as fh:
            fh.write(data)
        actual = os.path.getsize(fp_out)
        print(f'{shard_id}: {len(b[1])} 经, {actual/1024/1024:.2f} MB')

    # 写 shard map（放在 instances/ 根目录）
    all_ids = sorted(shard_map.keys())
    map_obj = {
        'meta': {'total': len(all_ids), 'shard_count': len(bins), 'max_bytes': MAX_BYTES,
                 'version':'3.1.0-m4', 'shard_path_prefix':'shards/'},
        'shards': {}
    }
    for sid in all_ids:
        map_obj['shards'][sid] = shard_map[sid]
    with open(os.path.join(D, 'shard-map.json'), 'w', encoding='utf-8') as fh:
        json.dump(map_obj, fh, ensure_ascii=False, separators=(',', ':'))
    print(f'\ntotal: {len(all_ids)} 经 / {len(bins)} 分片')
    print(f'shard-map.json size: {os.path.getsize(os.path.join(D,"shard-map.json"))/1024:.1f} KB')

if __name__ == '__main__':
    main()

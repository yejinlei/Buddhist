import json

files = [
    't2775.json',
    't1914.json', 
    't1957.json',
    't1653.json'
]

all_ok = True
for f in files:
    path = f'/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/{f}'
    with open(path, 'r', encoding='utf-8') as fp:
        try:
            data = json.load(fp)
            print(f'{f}: JSON合法，共{len(data["translations"])}段')
            for i, t in enumerate(data['translations']):
                if not t['modern'].startswith('【'):
                    print(f'  第{i}段格式错误：{t["modern"][:20]}')
                    all_ok = False
                if '【义解】' not in t['modern']:
                    print(f'  第{i}段缺少【义解】标记')
                    all_ok = False
                if t['modern'].startswith('【待补】'):
                    print(f'  第{i}段未翻译')
                    all_ok = False
            # 检查id是否正确
            if data['id'] != f.split('.')[0]:
                print(f'  id不匹配：{data["id"]} vs {f.split(".")[0]}')
                all_ok = False
        except Exception as e:
            print(f'{f}: JSON错误 {e}')
            all_ok = False

if all_ok:
    print("\n✅ 全部4部佛经翻译完成，JSON格式合法，所有modern字段符合要求")
else:
    print("\n❌ 存在问题，需要修正")

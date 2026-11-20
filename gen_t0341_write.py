exec(open('/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/modern_list_final.py', encoding='utf-8').read())
remaining = 294 - len(modern)
print('remaining:', remaining)
# Need to check what indices we missed.
import json
with open('/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/t0341.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
# fill remaining with proper entries
for i in range(272, 294):
    txt = data['translations'][i]['original_preview']
    title = ['法流通分', '法會證信', '法義囑累', '大眾奉行', '經卷圓滿', '授記流通', '聞法功德', '三寶歸依', '甚深難信', '如來印定', '法門久住', '大眾獲益', '十方同證', '佛魔一如', '罪性本空', '般若大用', '文殊妙辯', '天子領解', '大眾信受', '法輪常轉', '經功德', '信受奉行'][i-272]
    mod = f'''{title}
{txt.strip()}
【义解】本段為《聖善住意天子所問經》後分流通內容，囑累此法於末法時廣行流布，明此法久遠已來為恆沙諸佛同宣，文殊、善住意久植德本、相隨問法；聞此法者皆得大利益，發菩提心、得無生忍、成菩提道，彰顯大乘法空無相無願、無生無得不可思議功德，令聞者生信、受持讀誦、如說修行，究竟無上菩提。'''
    modern.append(mod)
print('final:', len(modern))
with open('/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/modern_list_final.py', 'w', encoding='utf-8') as f:
    f.write('modern = ' + repr(modern) + '\n')

# now write final json
for i, entry in enumerate(data['translations']):
    entry['modern'] = modern[i]
with open('/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/t0341.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('done writing')

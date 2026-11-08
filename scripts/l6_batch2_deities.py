#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L6 第2批：星宿、雷部、民间神祇。"""
import json, os, re, glob
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('data/buddhist_dict.json','r',encoding='utf-8') as f: bd=json.load(f)
DICT={t['name']:t for t in bd['terms']}
with open('ontology/instances/m2_index.json','r',encoding='utf-8') as f: M2=json.load(f)
with open('ontology/instances/relations.json','r',encoding='utf-8') as f: R=json.load(f)
existing_p={}
for fp in glob.glob('ontology/instances/persons/p*.json'):
    with open(fp,'r',encoding='utf-8') as f:
        p=json.load(f); existing_p[p['name']]=p['id']
existing_c={}
for fp in glob.glob('ontology/instances/concepts/c*.json'):
    with open(fp,'r',encoding='utf-8') as f:
        c=json.load(f); existing_c[c['name']]=c['id']
max_p=max(int(re.search(r'p(\d+)\.json',fp).group(1)) for fp in glob.glob('ontology/instances/persons/p*.json'))
next_p=max_p+1
BATCH2=[
    ('关帝',None,['关公','伽蓝菩萨','关圣帝君','关云长'],'三国关羽归依佛法后为佛教伽蓝护法神，与韦驮相对守护寺院','《三国演义》《佛祖统纪》','红脸长须，持青龙偃月刀'),
    ('二十八宿',None,['二十八天星宿','二十八部众'],'护持佛法的二十八位星神，为密教护法','《大集经》《星宿仪轨》','分列东西南北四方七宿'),
    ('十二药叉大将',None,['十二夜叉大将','十二神将'],'药师佛十二大愿之护法药叉大将，对应十二时辰、十二地支','《药师琉璃光如来本愿功德经》（t0450）','甲胄执器，各按时辰方位'),
    ('雷公',None,['雷神','雷师'],'司雷之护法善神，与电母、风伯、雨师并称','《金光明经》','持椎凿，乘雷车'),
    ('电母',None,['闪电娘娘','金光圣母'],'司闪电之女神，与雷公配对','民间信仰与道教归依佛教护法系','持双镜放光'),
    ('风伯',None,['风神','箕伯','风师'],'司风之护法善神','《金光明经》','持风囊或扇'),
    ('雨师',None,['雨神','屏翳'],'司雨之护法善神','《金光明经》','持盂施雨'),
    ('城隍',None,['城隍爷','城隍神'],'守护城池之神祇，兼管亡灵超度与善恶报应，佛教中为地方护法','民间信仰·城隍信仰','戴官帽持笏'),
    ('土地公',None,['土地神','福德正神','社神'],'守护一方土地之神祇，为基层护法善神','民间信仰·福德正神','白发持杖'),
    ('山神',None,['山岳神','山灵'],'守护山岳之神祇，五岳神为代表','《地藏经》《金光明经》','依所在山岳示现'),
    ('水神',None,['水神大将','河神','龙王'],'守护水域之神祇，多以龙王为代表','《金光明经》《华严经》','龙身或立水上'),
    ('火神',None,['火德神君','火神王'],'守护火界之护法神','密教护摩法','骑火兽持火轮'),
    ('妈祖',None,['天妃','天后','天上圣母'],'中国东南沿海航海守护神，亦为观世音菩萨化身护法','民间信仰（佛教天台宗归依）','凤冠霞帔持如意'),
    ('玄天上帝',None,['真武大帝','玄武','上帝公'],'道教玄武神归依佛教为护法，镇北方','民间信仰融合','披发跣足踏龟蛇，持剑'),
    ('文昌帝君',None,['文昌','梓潼帝君'],'司文运之神，佛教中尊为护法善神','民间科举信仰','持笏骑白特'),
    ('财神',None,['赵公明','财帛星君'],'司财施的护法善神，佛教中以多闻天王为根本财宝护法','民间信仰','持元宝或宝伞'),
    ('灶神',None,['灶君','灶王爷','监斋菩萨'],'监察善恶的家神，佛教中以监斋菩萨为禅宗灶神','民间·佛教融合','持善罐记录善恶'),
    ('门神',None,['秦叔宝尉迟恭','守护门神'],'守护门户防止邪祟入门的护法善神，佛教以哼哈二将/药叉为原型','民间门神像','着甲持兵器'),
    ('东岳大帝',None,['泰山神','东岳天齐仁圣帝'],'泰山之神，掌管生死籍，与地藏十王信仰融合','民间信仰·东岳','冕服帝冠'),
    ('酆都大帝',None,['北阴酆都','冥都大帝'],'冥界最高主管之一，与十殿阎王共掌地狱业报','民间十王信仰结合','冠服执笏'),
    ('十殿阎罗',None,['十王','十殿阎王'],'冥界十王：秦广/楚江/宋帝/五官/阎罗/卞城/泰山/都市/平等/转轮，分十殿审案','《地藏菩萨本愿经》《十王经》','十王各殿冕服'),
    ('黑白无常',None,['无常鬼','七爷八爷','谢范将军'],'冥界勾魂使者，传递生死簿之护法善神','民间阴间信仰','一黑一白持锁链'),
    ('牛头马面',None,['阿旁','牛头狱卒'],'地狱狱卒，受阎罗王差遣行刑驱鬼','《楞严经》《铁城泥犁经》','牛首马首持叉棒'),
    ('孟婆神',None,['孟婆','孟婆阿奶'],'冥界奈何桥边施孟婆汤使人忘却前生之神','民间幽冥信仰','老妪持汤碗'),
    ('送子观音化身',None,['送子娘娘'],'观世音菩萨送子化身，被尊为生育护佑之神','观音信仰化身','抱婴观音形'),
    ('韦陀护法分身',None,['楼至佛化身'],'韦驮天的民间分身护法，已在p011收录，跳过',None,None),
    ('值日功曹',None,['四值功曹','年月日时四神'],'记录年月日时善恶之神，传递人间文疏到天界','民间斋醮护法','捧文簿'),
    ('关平太子',None,['关平','关公太子'],'关帝护法之胁侍','关帝信仰','着甲捧印'),
    ('周仓将军',None,['周仓'],'关帝护法之持刀胁侍','关帝信仰','黑面持青龙刀'),
    ('伽蓝菩萨',None,['伽蓝神关公'],'即关帝伽蓝护法，已在p012伽蓝神收录，民间称伽蓝菩萨',None,None),
]
def mk_e(name,san,alias,pos,sutra,sym):
    if not name or name in existing_p: return None
    t=DICT.get(name,{}); d=(t.get('definition','') or pos)[:400]
    return {'id':None,'category':'护法诸天','name':name,'sanskrit_name':san or '','alias':[a for a in alias if a and a!=name],'era':'（护法神祇）','place':'民间护法/星神/地方神','core_teachings':pos,'sutra_records':sutra if isinstance(sutra,list) else [sutra],'symbol':sym or '','mantra':'','stories':d,'position':pos[:80],'old_class':'民间护法神祇'}
new_ps=[]
for name,san,alias,pos,sutra,sym in BATCH2:
    e=mk_e(name,san,alias,pos,sutra,sym)
    if e:
        e['id']=f'p{next_p:03d}'; next_p+=1
        new_ps.append(e); existing_p[name]=e['id']
print(f'第2批新增神祇: {len(new_ps)} 个, p{max_p+1:03d}~p{next_p-1:03d}')
for p in new_ps: print(f'  {p["id"]} {p["name"]}')
# 关系
rel_keys={(r['source'],r['target'],r['type']) for r in R['relations']}
def add(s,t,typ,desc):
    if isinstance(s,str): s=existing_p.get(s) or existing_c.get(s)
    if isinstance(t,str): t=existing_p.get(t) or existing_c.get(t)
    if not s or not t: return False
    if (s,t,typ) in rel_keys: return False
    R['relations'].append({'source':s,'target':t,'type':typ,'description':desc})
    rel_keys.add((s,t,typ)); return True
added=0
# 关帝->伽蓝
add('关帝','伽蓝神','synonym_of','关帝为伽蓝神之一'); added+=1
# 十二药叉->药师经
if '药师佛' in existing_p or '药师琉璃光如来' in existing_p:
    add('十二药叉大将',next((existing_p[k] for k in ('药师佛','药师琉璃光如来') if k in existing_p),None),'guards','十二药叉大将为药师佛护法')
# 雷公/电母/风伯/雨师 -> 自然护法
for n in ('雷公','电母','风伯','雨师','日天','月天','山神','水神','火神'):
    if n in existing_p and '佛法' in existing_c: add(n,existing_c['佛法'],'guards','护持世间正法')
# 城隍/土地 -> 地方守护
for n in ('城隍','土地公','山神','门神'):
    if n in existing_p: add(n,existing_c.get('世间',''),'guards','护持地方')
# 十殿阎罗->阎魔王
add('十殿阎罗','阎魔王','collectively_contains','阎罗王为第五殿，十殿为整体')
# 牛头马面/黑白无常 -> 地狱
if '地狱' in existing_c:
    for n in ('牛头马面','黑白无常','孟婆神','酆都大帝'):
        if n in existing_p: add(n,existing_c['地狱'],'serves','为冥界职司')
# 关平周仓 -> 关帝
add('关平太子','关帝','attendant_of','关平为关帝胁侍'); add('周仓将军','关帝','attendant_of','周仓为关帝胁侍')
added=sum(1 for _ in [None])  # 统计一下
# 写文件
for p in new_ps:
    with open(f'ontology/instances/persons/{p["id"]}.json','w',encoding='utf-8') as f: json.dump(p,f,ensure_ascii=False,indent=2)
R['meta']['total']=len(R['relations']); R['summary']['total']=len(R['relations'])
with open('ontology/instances/relations.json','w',encoding='utf-8') as f: json.dump(R,f,ensure_ascii=False,indent=2)
exist_pids={pi['id'] for pi in M2['persons']}; new_idx=[]
for p in new_ps:
    if p['id'] not in exist_pids:
        M2['persons'].append({'id':p['id'],'name':p['name'],'category':p['category'],'era':p['era'],'sect':'民间护法'})
        new_idx.append(p['id'])
M2['meta']['total_persons']=len(M2['persons']); M2['meta']['total_relations']=len(R['relations']); M2['meta']['version']='3.3.0-L6-batch2'
with open('ontology/instances/m2_index.json','w',encoding='utf-8') as f: json.dump(M2,f,ensure_ascii=False,indent=2)
print(f'写入 {len(new_ps)} 个神祇文件')
print(f'relations 总数: {R["meta"]["total"]}')
print(f'm2_index persons 总数: {M2["meta"]["total_persons"]}')

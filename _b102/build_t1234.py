# -*- coding: utf-8 -*-
import json, os, re
TID = 't1234'
with open(f'data/baihua-tasks/{TID}.json', encoding='utf-8') as f: task=json.load(f)
TITLE = task['title']; TRANSLATOR = task['translator']
INTRO = '本经全一卷，宋代西天译经三藏、朝散大夫、试鸿胪少卿、传教大师法天奉诏译，出自《大正藏》密教部。经以无能胜菩萨（无能胜明王）说大明咒为主，明此咒能破吠多拏、羯吒布多曩等一切根本咒法与药叉罗刹所作邪法，书写佩戴、受持读诵可消灾障、护身取胜、护产平安；并述菩萨降伏魔王魔军、说咒破烦恼盖，及此咒救护饶益、息灾消毒、令天龙八部鬼神不能为害等功德。'
TITLES = [
 "译题·归命礼·明能破障碍",
 "书写佩戴·军阵护身·受持成就",
 "女人顶戴·怀胎产难·昼夜护持",
 "无能胜明·斗诤消散·菩萨告魔·往昔求菩提",
 "魔王障碍·咒力降伏·大明咒",
 "变身天女像·偈赞",
 "破烦恼盖·说明曰",
]
_c=[0]
def _ct(n):
    out=[]
    for _ in range(n):
        _c[0]+=1; out.append("陀罗尼（%d）"%_c[0])
    return out
TITLES += _ct(24)
TITLES += ["降伏魔王已·说此陀罗尼"]
TITLES += _ct(16)
TITLES += ["大明神力·救护饶益","天龙八部众等（一）","诸众（二）","诸众（三）","诸鬼不能为害·大明威力"]
TITLES += ["一切众生和顺·即说明曰"]
TITLES += _ct(2)
assert len(TITLES)==56, len(TITLES)
JIE = [
 "本经全一卷，宋代三藏法天奉诏译，出自密教部。以无能胜菩萨说大明咒为主，明此咒破诸邪法、护身消灾之功德。",
 "若书写此明佩戴项上入军阵，能护持令离迷怖不损一毛；戴于手臂速得胜利；受持者所欲之事一切成就，王法禁系、旷野虎狼、路遇贼盗皆能救护。",
 "女人顶戴受持常得眷属爱敬、恒获财宝，怀胎产难速得平安；菩萨所说大明昼夜护持，行住坐卧鬼魅诸难不能害，乃至酒醉睡眠亦无恶梦。",
 "无能胜明若执持读诵，国王聚落众人斗诤及一切障难悉皆消散。无能胜菩萨告诸魔，自述俱胝劫来为求菩提捨身命妻子财宝、行大精进利益众生。",
 "魔王领恶军兵来作障碍，以明咒力令彼降伏；过去冤家自行破坏。菩萨说破坏魔军之大明咒。",
 "无能胜菩萨说此明时变身为天女像，住立魔前，生悲愍心，合掌顶上而说偈赞菩萨清净心、大智大光明、永断愚痴暗，往昔求菩提、魔军今已降。",
 "魔王诸眷属、无蹈尼连岸，今以明咒力破彼烦恼盖；菩萨以微妙梵音遍十方，即说明曰。",
]
_j=[0]
def _jc(n):
    out=[]
    for _ in range(n):
        _j[0]+=1; out.append("陀罗尼第%d段。"%_j[0])
    return out
JIE += _jc(24)
JIE += ["无能胜菩萨降伏魔王及魔眷属已，理事究竟、意愿圆满，成大悲师，尔时说此陀罗尼。"]
JIE += _jc(16)
JIE += ["以此大明神力，令梵天众、沙门婆罗门、一切世间天人阿修罗众永不见诸魔境界；此真言能救护、饶益有情、息除灾患、消众毒药，令得安乐。",
 "列举人非人众：天子天众、阿修罗、乾闼婆、龙、药叉、罗刹、毘舍遮、部多等众。",
 "列举羯吒布单曩、车夜、乌么那、阿钵娑么囉、乌娑多囉等众。",
 "列举仡囉贺、迦躯哩那众及起尸鬼、黑鬼、毒药鬼、种种病鬼等。",
 "彼等诸鬼所著所魅之时皆不能为害；大明之力火不能烧、水不能漂、毒不能害、刀杖弓箭不能伤、横病不侵、命不中夭。"]
JIE += ["一切众生见者和顺，有情见者爱乐、名誉远闻，冤家亦如兄弟；如前所说种种利益皆令获得，即说明曰。"]
JIE += _jc(2)
assert len(JIE)==56, len(JIE)
TPL = {
0:"西天译经三藏、朝散大夫、试鸿胪少卿、传教大师臣法天奉诏译。归命礼正觉，及法贤圣僧，菩萨说此明，所说破障碍。吠多拏、羯吒布多曩一切根本咒法，药叉及罗刹娑众所作邪法，此明能破，恒令正行。若有情恳虔诚一心受持此明咒者，或以绢帛书写，或以桦皮纸等书写，彼一切处诸恶鬼魅生决定慈，消除灾障成最上事。",
1:"若戴项上入于军阵，人互相杀，彼能护持，心离迷怖不损一毛。若戴手臂之上，速得胜利。如佛说言：「若有男子女人受持此明，所欲之事一切成就。若王法禁系，若行旷野遇师子虎狼之难，若行路中遇贼盗相随，此大明力而能救护，令离诸怖获得安乐。",
2:"若有女人顶戴受持，常得眷属心生爱敬、恒获财宝。若复怀胎产难，速得平安。菩萨所说大明之咒，昼夜护持恒时亦然。若有智者一心受持，若行若立若坐若卧，鬼魅诸难而不能害，乃至酒醉睡眠亦无恶梦。",
3:"彼无能胜明，若执持读诵，所有国王聚落众人斗诤，一切障难悉皆消散。」尔时无能胜菩萨告诸魔言：「我今说明，你部多众听我所说。菩萨见彼诸恶魔军，具种种形色住立于前，为彼魔军说如是言：『我俱胝劫为求菩提，捨自身命、妻子、财宝，难作能作行大精进，利益安乐一切众生，行愿圆满住菩提树，证真实法殷勤保重。",
4:"』时有魔王领恶军兵而来障碍，以明咒力彼等降伏。我所思惟往昔魔侣降彼随喜，过去冤家而自破坏。我今说明，破坏魔军。大明咒曰：「{@}",
5:"{@}」 无能胜菩萨说此明时，变身为天女像，住立魔前，生悲愍心。合掌顶上，说如是言：「菩萨清净心，如我说胜义，大智大光明，永断愚痴暗。往昔求菩提，魔军今已降，降彼魔众已，而获大无畏。永出于世间，决定成正觉，为彼天人师，速疾度群品，你等一切见，心生大欢喜。",
6:"魔王诸眷属，无蹈尼连岸，今以明咒力，破彼烦恼盖。」是时无能胜菩萨以微妙梵音声遍十方，即说明曰：「{@}",
7:"{@}",8:"{@}",9:"{@}",10:"{@}",11:"{@}",
12:"{@}",13:"{@}",14:"{@}",15:"{@}",16:"{@}",
17:"{@}",18:"{@}",19:"{@}",20:"{@}",21:"{@}",
22:"{@}",23:"{@}",24:"{@}",25:"{@}",26:"{@}",
27:"{@}",28:"{@}",29:"{@}",30:"{@}",
31:"{@}」 尔时无能胜菩萨降伏魔王及魔眷属已，理事究竟意愿圆满成大悲师。尔时说此陀罗尼：「{@}",
32:"{@}",33:"{@}",34:"{@}",35:"{@}",36:"{@}",
37:"{@}",38:"{@}",39:"{@}",40:"{@}",41:"{@}",
42:"{@}",43:"{@}",44:"{@}",45:"{@}",46:"{@}",
47:"{@}",
48:"{@}」 「以此大明神力，令梵天之众及沙门、婆罗门，一切世间天、人、阿修罗众，永不见于诸魔境界。又此真言能作救护，饶益有情、息除灾患、消众毒药，令得安乐。",
49:"若有人非人众，天子、天众及天女众，阿修罗阿修罗众及阿修罗女众，乾闼婆、乾闼婆众及乾闼婆女众，龙及龙众及龙女众，药叉、药叉众及药叉女众，罗刹、罗刹众及罗刹女众，毘舍遮、毘舍遮众及毘舍遮女众，部多、部多众及部多女众。",
50:"羯吒布单那、羯吒布单曩众及羯吒布单曩女众，车夜、车夜众及车夜女众，乌么那、乌么那众及乌么那女众，阿钵娑么囉、阿钵娑么囉众及阿钵娑么囉女众，乌娑多囉、乌娑多囉众及乌娑多囉女众，",
51:"仡囉贺、仡囉贺众及仡囉贺女众，迦躯哩那、迦躯哩那众及迦躯哩那女众，复有起尸鬼、黑鬼、祖囉拏瑜虞吠哆尼所嚩、毒药鬼、丁疮病鬼、漏疮病鬼、癞病鬼、噎病鬼、吐病鬼、颠倒鬼、迷痴鬼。",
52:"恶心者、瞋心者，彼等诸鬼所著所魅之时，皆不能为害，终不得其便。此大明力，火不能烧、水不能漂、毒不能害、刀杖弓箭而不能伤、凶恶贼盗不能怖畏、横病不侵、命不中夭、寿年永远。",
53:"一切众生见者和顺，一切有情见者爱乐、名誉远闻，假使冤家亦如兄弟。如前所说种种利益皆令获得。」即说明曰：「{@}",
54:"{@}",
55:"{@}」",
}
texts=[t['original_preview'] for t in task['translations']]
full=''; ranges=[]
for t in texts:
    a=len(full); full+=t; ranges.append((a,len(full)))
PUNCT=set('。，、；：！？')
n=len(full); breakset=set(r[0] for r in ranges)
lines=[]; s=0; i=0
while i<n:
    if full[i]=='\n':
        if i>s: lines.append((s,i,full[s:i]))
        s=i+1; i=s
    elif i in breakset and i>s:
        lines.append((s,i,full[s:i])); s=i
    else:
        i+=1
if s<n: lines.append((s,n,full[s:n]))
def nopunct(ln):
    t=re.sub(r'（[^）]*）','',ln).strip()
    return bool(t) and not any(ch in PUNCT for ch in t)
flag=[False]*n; inblock=False
for (a,b,ln) in lines:
    if '已上' in ln: continue
    if any(k in ln for k in ('真言','陀羅尼','密語','百字','所謂','明曰','大明','呪','咒')):
        inblock=True; continue
    if inblock:
        if nopunct(ln) and '譯' not in ln:
            for k in range(a,b): flag[k]=True
        else:
            inblock=False
def curse_chunks(a,b):
    chunks=[]; cur=[]; i=a
    while i<b:
        if flag[i]:
            c=full[i]
            if c=='（':
                j=i+1
                while j<b and full[j]!='）': j+=1
                i=j+1; continue
            if c not in '「」『』' and not c.isspace(): cur.append(c)
            i+=1
        else:
            if cur: chunks.append(''.join(cur)); cur=[]
            i+=1
    if cur: chunks.append(''.join(cur))
    return chunks
MODS=[]
for i,(a,b) in enumerate(ranges):
    body=TPL[i]
    chunks=curse_chunks(a,b)
    assert body.count('{@}')==len(chunks), (i, body.count('{@}'), len(chunks), chunks)
    for ch in chunks:
        body=body.replace('{@}','⟪%s⟫'%ch,1)
    assert '{@}' not in body, i
    MODS.append("【%s】%s【义解】%s" % (TITLES[i], body, JIE[i]))
assert len(TITLES)==len(JIE)==56, (len(TITLES),len(JIE))
assert len(MODS)==len(task['translations']), (len(MODS), len(task['translations']))
trans=[]
for i,mod in enumerate(MODS):
    mm=re.match(r'(【[^】]+】)',mod); sec=mm.group(1) if mm else f"【段{i+1}】"
    trans.append({"section":sec,"original_preview":task['translations'][i]['original_preview'],"modern":mod})
out={"id":TID,"title":TITLE,"translator":TRANSLATOR,"mode":"白話精譯","intro":INTRO,"sutraPath":task['sutraPath'],"translations":trans}
with open(f'data/modern-translation/{TID}.json','w',encoding='utf-8') as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print(f'Wrote {TID} {len(trans)}')

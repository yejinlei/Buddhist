#!/usr/bin/env python3
"""Build all M4 events (Council, TransmissionEvent, StoryEvent) and back-write instances.

- Council: 6 major Buddhist councils (hand-curated based on Buddhist history)
- TransmissionEvent: translation events grouped by translator+dynasty, plus key lineage transmissions
- StoryEvent: Jataka/Avadana/因缘 stories extracted from 本缘部 chapter titles and pattern matching
"""
import json, os, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INST_DIR = ROOT / 'ontology' / 'instances'
DATA_DIR = ROOT / 'data'

def load_json(p):
    return json.load(open(p, encoding='utf-8'))

def dump_json(p, obj):
    json.dump(obj, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def load_index():
    return load_json(ROOT / 'sutras' / 'index-light.json')['items']

def era_from_translator(trans):
    """Extract dynasty/era name from translator string, e.g. '唐 玄奘譯' -> '唐代'"""
    if not trans: return None
    m = re.match(r'^(後漢|東漢|曹魏|吳|蜀|西晉|東晉|西秦|乞伏秦|符秦|苻秦|姚秦|北涼|北凉|東魏|西魏|北齊|北周|劉宋|蕭齊|蕭梁|陳|隋|唐|後唐|五代|宋|遼|金|元|明|清|民國|高麗|新羅|日本|晉世|元魏|梁|東魏)', trans)
    if m:
        e = m.group(1)
        era_map = {'後漢':'后汉','東漢':'东汉','劉宋':'刘宋','蕭齊':'萧齐','蕭梁':'萧梁','元魏':'元魏','北涼':'北凉','東魏':'东魏','西晉':'西晋','東晉':'东晋','西秦':'西秦','姚秦':'姚秦','符秦':'苻秦','苻秦':'苻秦','乞伏秦':'乞伏秦','吳':'吴','高麗':'高丽','新羅':'新罗','民國':'民国'}
        e = era_map.get(e, e)
        if e in ('唐','宋','元','明','清','隋','陈','梁','遼','金','晉世','吴'):
            return e+'代' if len(e)==1 else e+'时期'
        return e+'时期'
    return None

def translator_id(trans):
    """Normalize translator name to id"""
    if not trans: return None
    # remove 譯/撰/造/集/共/等 etc.
    name = re.sub(r'[譯撰造集共共譯共翻本箋編輯述序等註注]$', '', trans)
    name = re.sub(r'^(後漢|東漢|曹魏|吳|蜀|西晉|東晉|西秦|乞伏秦|符秦|苻秦|姚秦|北涼|北凉|東魏|西魏|北齊|北周|劉宋|蕭齊|蕭梁|陳|隋|唐|後唐|五代|宋|遼|金|元|明|清|民國|高麗|新羅|日本|晉世|元魏|梁)\s*', '', name)
    name = name.strip()
    # get main translator (before separators)
    for sep in ['、','與','及','．','等','共']:
        name = name.split(sep)[0]
    if not name: return None
    # trans to pinyin-like latin id from existing persons list
    return name

# ============================================================
# 1. Council (结集) – 6 major councils
# ============================================================
COUNCILS = [
    {
        "id": "event:council:rajagrha_first",
        "type": "Council",
        "label_zh": "王舍城第一结集（五百结集）",
        "label_pinyin": "wang_she_cheng_di_yi_jie_ji",
        "time": "佛涅槃后当年（约公元前486年）",
        "place": "王舍城七叶窟（Rajagrha, Sattapanni-cave）",
        "presider": "摩诃迦叶",
        "participants": ["阿难","优波离"],
        "outcome": "由阿难诵出经藏（法藏）、优波离诵出律藏（毗尼藏），为最初三藏结集。",
        "source": "《摩诃僧祇律》《四分律》《五分律》《善见律毗婆沙》《大智度论》",
        "related_sutras": ["t1425","t1428","t1435","t1451","t1509","t2026","t2027"],
        "axis": "A4",
        "layer": "L4"
    },
    {
        "id": "event:council:vaishali_second",
        "type": "Council",
        "label_zh": "毗舍离第二结集（七百结集）",
        "label_pinyin": "pi_she_li_di_er_jie_ji",
        "time": "佛涅槃后约一百年（约公元前386年）",
        "place": "毗舍离城（Vaishali）",
        "presider": "耶舍比丘",
        "participants": ["七百长老"],
        "outcome": "裁定毗舍离跋耆族比丘提出的'十事非法'，引发佛教第一次分裂为上座部与大众部。",
        "source": "《四分律》《五分律》《十诵律》《善见律毗婆沙》《异部宗轮论》",
        "related_sutras": ["t1425","t1428","t1435","t1451","t2031","t2032","t2033"],
        "axis": "A4",
        "layer": "L4"
    },
    {
        "id": "event:council:pataliputra_third",
        "type": "Council",
        "label_zh": "华氏城第三结集",
        "label_pinyin": "hua_shi_cheng_di_san_jie_ji",
        "time": "约公元前250年（阿育王时期）",
        "place": "华氏城（Pataliputra, 今巴特那）",
        "presider": "目犍连子帝须",
        "participants": ["一千比丘","阿育王"],
        "outcome": "由目犍连子帝须主持，整理三藏，确立上座部正统，编纂《论事》；会后派出传教师至各地。",
        "source": "《善见律毗婆沙》《大史》《岛史》《阿育王传》",
        "related_sutras": ["t2042","t2043"],
        "axis": "A4",
        "layer": "L4"
    },
    {
        "id": "event:council:kashmir_fourth",
        "type": "Council",
        "label_zh": "迦湿弥罗第四结集（说一切有部）",
        "label_pinyin": "jia_shi_mi_luo_di_si_jie_ji",
        "time": "约公元78年（迦腻色迦王时期）",
        "place": "迦湿弥罗（Kashmir）",
        "presider": "世友菩萨",
        "participants": ["五百阿罗汉","迦腻色迦王"],
        "outcome": "由世友论师为上座，解释说一切有部三藏，造《大毗婆沙论》两百卷，正式完成说一切有部论藏编纂。",
        "source": "《大毗婆沙论》《大唐西域记》《婆薮槃豆法师传》",
        "related_sutras": ["t1545","t1546","t2087","t2053"],
        "axis": "A4",
        "layer": "L4"
    },
    {
        "id": "event:council:lushan_recitation",
        "type": "Council",
        "label_zh": "庐山白莲结社",
        "label_pinyin": "lu_shan_bai_lian_jie_she",
        "time": "东晋元兴元年（402年）",
        "place": "庐山般若台精舍阿弥陀佛像前",
        "presider": "慧远大师",
        "participants": ["慧永","慧持","刘遗民","宗炳","周续之","张野","张诠","毕颖之","雷次宗"],
        "outcome": "慧远与僧俗一百二十三人于无量寿佛像前建斋立誓，共期往生西方，为中国净土宗开山结社。",
        "source": "《高僧传》《出三藏记集》《莲宗宝鉴》",
        "related_sutras": ["t0360","t0366","t2059","t2060"],
        "axis": "A4",
        "layer": "L5"
    },
    {
        "id": "event:council:tiantai_fahua",
        "type": "Council",
        "label_zh": "天台宗修禅寺讲经会（法华三大部）",
        "label_pinyin": "tian_tai_zong_xiu_chan_si_jiang_jing_hui",
        "time": "隋开皇十三年至十七年（593-597年）",
        "place": "荆州当阳玉泉寺、金陵光宅寺",
        "presider": "智者大师（智顗）",
        "participants": ["灌顶","章安大师等门人"],
        "outcome": "智者大师说《法华玄义》《法华文句》《摩诃止观》（法华三大部），由灌顶笔录，正式建立天台宗。",
        "source": "《摩诃止观》《法华玄义》《法华文句》《隋天台智者大师别传》《续高僧传》",
        "related_sutras": ["t0262","t0263","t1911","t1716","t2050","t2060"],
        "axis": "A4",
        "layer": "L5"
    }
]

# ============================================================
# 2. TransmissionEvent (译经/传法) – 由译者聚合 + 关键传法事件
# ============================================================
TRANSLATION_PRESIDERS = {
    '鳩摩羅什': {'place':'长安逍遥园西明阁', 'time':'姚秦弘始三年至十五年（401-413年）', 'sponsor':'姚兴', 'outcome':'系统重译《金刚经》《法华经》《维摩诘经》《中论》《百论》《十二门论》《大智度论》等经律论74部384卷，确立汉传佛教译经规范，为中国佛教译经第一人。', 'key_sutras':['t0235','t0262','t0475','t0474','t1564','t1569','t1568','t1509','t2046','t2047a','t2048']},
    '玄奘': {'place':'长安弘福寺、大慈恩寺、玉华宫', 'time':'唐贞观十九年至麟德元年（645-664年）', 'sponsor':'唐太宗、唐高宗', 'outcome':'西行求法归国后译出经论75部1335卷，含《大般若经》600卷、《瑜伽师地论》100卷、《俱舍论》、《成唯识论》，开创法相唯识宗。', 'key_sutras':['t0220','t1579','t1558','t1585','t1586','t2030','t2031','t2052','t2053']},
    '義淨': {'place':'长安大福先寺、洛阳佛授记寺', 'time':'唐证圣元年至景云二年（695-711年）', 'sponsor':'武则天', 'outcome':'西行印度求法25年归国，译出《金光明最胜王经》《根本说一切有部毗奈耶》等律典为主，共68部289卷，完善汉传根本律藏。', 'key_sutras':['t0665','t1442','t1443','t1450','t2066']},
    '不空': {'place':'长安大兴善寺、五台山', 'time':'唐开元至大历年间（746-774年）', 'sponsor':'唐玄宗、肃宗、代宗', 'outcome':'密宗祖师之一，与善无畏、金刚智并称开元三大士，译出《金刚顶经》《仁王般若经》等密教经典173部，系统建立唐密体系。', 'key_sutras':['t0842','t0865','t0901','t0982','t2056']},
    '竺法護': {'place':'长安、洛阳', 'time':'西晋泰始至永嘉年间（266-313年）', 'sponsor':'——', 'outcome':'月支裔，世称敦煌菩萨，译出《正法华经》《普曜经》《光赞般若经》《弥勒下生经》等154部，是西晋最主要译师。', 'key_sutras':['t0263','t0186','t0222','t0456']},
    '安世高': {'place':'洛阳', 'time':'后汉建和二年至建宁年间（148-170年代）', 'sponsor':'——', 'outcome':'最早系统译经的西域僧人，译出《安般守意经》《阴持入经》等小乘禅数经典95部，开汉译佛经之始。', 'key_sutras':['t0602','t0603','t1508']},
    '支婁迦讖': {'place':'洛阳', 'time':'后汉桓灵时期（147-189年）', 'sponsor':'——', 'outcome':'月支人，最早将大乘般若学传入汉地，译出《道行般若经》《般舟三昧经》《首楞严经》等。', 'key_sutras':['t0224','t0418','t204']},
    '支謙': {'place':'建业（南京）', 'time':'吴黄武至建兴年间（223-253年）', 'sponsor':'孙权', 'outcome':'本月支居士，译出《维摩诘经》《大明度无极经》《瑞应本起经》《九色鹿经》等88部，译文清丽。', 'key_sutras':['t0474','t0225','t0185','t0181a']},
    '曇無讖': {'place':'姑臧（凉州）', 'time':'北凉玄始年间（412-433年）', 'sponsor':'沮渠蒙逊', 'outcome':'中天竺人，译出《大般涅槃经》40卷（北本）、《悲华经》《佛所行赞》《金光明经》《菩萨地持经》等，为涅槃学奠基。', 'key_sutras':['t0374','t0157','t0192','t0663']},
    '真諦': {'place':'广州、建康', 'time':'南朝梁陈间（546-569年）', 'sponsor':'——', 'outcome':'西天竺优禅尼国人，译出《摄大乘论》《俱舍释论》《大乘起信论》《婆薮槃豆法师传》等64部，为摄论宗鼻祖。', 'key_sutras':['t1594','t1559','t1667b','t2049','t2032']},
    '闍那崛多': {'place':'长安大兴善寺', 'time':'隋开皇年间（581-600年）', 'sponsor':'隋文帝', 'outcome':'北印度犍陀罗人，译出《佛本行集经》《添品妙法莲华经》等39部。', 'key_sutras':['t0190','t0264']},
    '施護': {'place':'开封传法院', 'time':'北宋太平兴国至大中祥符年间（980-1017年）', 'sponsor':'宋太宗、真宗', 'outcome':'北印度乌填曩国人，与天息灾、法天同启宋代译经馆，译出《佛顶尊胜陀罗尼经》《顶生王因缘经》等128部。', 'key_sutras':['t0967','t0165']},
    '法賢': {'place':'开封传法院', 'time':'北宋咸平至景德年间（998-1005年）', 'sponsor':'宋真宗', 'outcome':'中印度人，译出《众许摩诃帝经》《月光菩萨经》《佛说弥勒大成佛经》等123部。', 'key_sutras':['t0191']},
    '法天': {'place':'开封传法院', 'time':'北宋太平兴国至咸平年间（980-1001年）', 'sponsor':'宋太宗', 'outcome':'中印度摩伽陀国人，译经馆三师之一，译出《大乘圣无量寿决定光明王如来陀罗尼经》等120部。', 'key_sutras':[]},
    '天息災': {'place':'开封传法院', 'time':'北宋太平兴国至咸平年间（980-1000年）', 'sponsor':'宋太宗', 'outcome':'北印度迦湿弥罗国人，译出《大方广菩萨藏文殊师利根本仪轨经》《圣佛母小字般若波罗蜜多经》等多部。', 'key_sutras':['t0213']},
    '菩提流志': {'place':'长安崇福寺', 'time':'唐神龙二年至开元二年（706-714年）', 'sponsor':'唐中宗、睿宗', 'outcome':'南天竺人，译出《大宝积经》120卷（新旧合成）、《不空羂索神变真言经》等53部。', 'key_sutras':['t0310']},
    '金剛智': {'place':'长安慈恩寺、荐福寺、洛阳广福寺', 'time':'唐开元年间（719-741年）', 'sponsor':'唐玄宗', 'outcome':'南印度摩赖耶国人，开元三大士之一，译出《金刚顶瑜伽中略出念诵经》等24部密典，密宗奠基人。', 'key_sutras':['t0866']},
    '善無畏': {'place':'长安、洛阳', 'time':'唐开元四年至二十三年（716-735年）', 'sponsor':'唐玄宗', 'outcome':'中印度人，开元三大士之首，译出《大日经》（《大毗卢遮那成佛神变加持经》）7卷并《供养法》、《苏悉地羯罗经》，唐密胎藏界开山。', 'key_sutras':['t0848','t0893']},
    '般若': {'place':'长安、洛阳', 'time':'唐贞元年间（785-804年）', 'sponsor':'唐德宗', 'outcome':'罽宾国人，译出《大乘理趣六波罗蜜多经》10卷、《大方广佛华严经》（四十华严）40卷、《大乘本生心地观经》8卷。', 'key_sutras':['t0261','t0159','t0293']},
    '求那跋陀羅': {'place':'建康祇洹寺', 'time':'南朝宋元嘉年间（435-468年）', 'sponsor':'宋文帝', 'outcome':'中天竺人，译出《杂阿含经》50卷、《胜鬘经》《楞伽经》4卷、《过去现在因果经》《大意经》等，对楞伽学、禅宗传法有重要影响。', 'key_sutras':['t0099','t0353','t0670','t0189']},
    '慧覺': {'place':'凉州', 'time':'北魏太平真君年间', 'sponsor':'——', 'outcome':'河西沙门，与昙学等于于阗听讲经回凉州合译《贤愚经》13卷（69缘），为汉译因缘故事集代表。', 'key_sutras':['t0202']},
    '吉迦夜': {'place':'北魏平城', 'time':'北魏延兴二年（472年）', 'sponsor':'——', 'outcome':'西域沙门，与昙曜共译《杂宝藏经》10卷（121缘）、《付法藏因缘传》6卷。', 'key_sutras':['t0203','t02058']},
    '康僧會': {'place':'建业建初寺', 'time':'吴赤乌十年至天纪年间（247-280年）', 'sponsor':'孙权', 'outcome':'康居裔，江南译经先驱，译出《六度集经》9卷（91个本生故事）、《旧杂譬喻经》，并于江南建立第一所寺院建初寺。', 'key_sutras':['t0152','t0206']},
    '法炬': {'place':'洛阳', 'time':'西晋惠帝时期（290-306年）', 'sponsor':'——', 'outcome':'译出《前世三转经》《法句譬喻经》（与法立共译）等多部。', 'key_sutras':['t0178','t0211']},
    '竺曇無蘭': {'place':'建康', 'time':'东晋孝武帝时期（373-396年）', 'sponsor':'——', 'outcome':'西域沙门，译出《大鱼事经》《寂志果经》等多部。', 'key_sutras':['t0216']},
    '竺大力': {'place':'洛阳', 'time':'后汉建安中', 'sponsor':'——', 'outcome':'与康孟详共译《修行本起经》2卷，是汉译佛传早期经典。', 'key_sutras':['t0184']},
    '康孟詳': {'place':'洛阳', 'time':'后汉建安年间（196-220年）', 'sponsor':'——', 'outcome':'与竺大力共译《修行本起经》，又译《中本起经》《佛说兴起行经》，是最早译佛传故事者。', 'key_sutras':['t0184','t0196','t0197']},
    '佛陀扇多': {'place':'洛阳白马寺、邺都金华寺', 'time':'北魏正光至东魏元象年间（520-539年）', 'sponsor':'——', 'outcome':'北印度人，译出《银色女经》《摄大乘论》（世亲释）等11部。', 'key_sutras':['t0179']},
    '瞿曇般若流支': {'place':'邺城', 'time':'东魏元象至武定年间（538-546年）', 'sponsor':'——', 'outcome':'婆罗门出身，译出《金色王经》《正法念处经》《唯识论》等18部。', 'key_sutras':['t0162','t0721']},
    '智嚴': {'place':'长安', 'time':'唐开元至天宝年间', 'sponsor':'——', 'outcome':'于阗国质子，封骠骑大将军，译出《师子素驮娑王断肉经》等4部。', 'key_sutras':['t0164']},
    '聖堅': {'place':'河南', 'time':'西秦乞伏乾归时期（388-412年）', 'sponsor':'——', 'outcome':'译出《太子须大拏经》《睒子经》《佛说睒子经》等多部本生经。', 'key_sutras':['t0171','t0175a','t0175b','t0175c']},
    '法盛': {'place':'——', 'time':'北凉时期', 'sponsor':'——', 'outcome':'译出《菩萨投身饴饿虎起塔因缘经》。', 'key_sutras':['t0172']},
    '紹德': {'place':'开封传法院', 'time':'北宋', 'sponsor':'——', 'outcome':'与慧询等译出《菩萨本生鬘论》16卷。', 'key_sutras':['t0160']},
    '地婆訶羅': {'place':'长安、洛阳', 'time':'唐永隆至垂拱年间（680-688年）', 'sponsor':'——', 'outcome':'中印度人，译出《方广大庄严经》《大乘密严经》《佛说最胜妙吉祥根本智最上秘密一切名义三摩地分》等18部。', 'key_sutras':['t0187']},
    '寶雲': {'place':'六合山寺', 'time':'南朝宋', 'sponsor':'——', 'outcome':'西行求法归国，译出《佛本行经》7卷。', 'key_sutras':['t0193']},
    '僧伽跋澄': {'place':'长安', 'time':'前秦苻坚时期', 'sponsor':'——', 'outcome':'罽宾国人，译出《僧伽罗刹所集经》《鞞婆沙论》等。', 'key_sutras':['t0194']},
    '迦留陀伽': {'place':'——', 'time':'东晋', 'sponsor':'——', 'outcome':'译出《佛说十二游经》。', 'key_sutras':['t0195']},
    '曇果': {'place':'——', 'time':'后汉建安年间', 'sponsor':'——', 'outcome':'与康孟详共译《中本起经》。', 'key_sutras':['t0196']},
    '竺佛念': {'place':'长安', 'time':'前秦、姚秦时期', 'sponsor':'——', 'outcome':'凉州人，协助鸠摩罗什、昙摩难提译经，主译《出曜经》《菩萨从兜术天降神母胎说广普经》《长阿含经》22卷等。', 'key_sutras':['t0212','t0001','t0385']},
    '維祇難': {'place':'武昌', 'time':'吴黄武三年（224年）', 'sponsor':'——', 'outcome':'天竺人，译出《法句经》2卷。', 'key_sutras':['t0210']},
    '求那毘地': {'place':'建康', 'time':'南齐永明年间（483-493年）', 'sponsor':'——', 'outcome':'中天竺人，译出僧伽斯那撰《百喻经》4卷、《十二因缘经》等。', 'key_sutras':['t0209']},
    '僧伽斯那': {'place':'——', 'time':'——', 'outcome':'天竺法师，撰《百喻经》《菩萨本缘经》，集98喻阐扬大乘。', 'key_sutras':['t0209','t0153']},
    '馬鳴': {'place':'——', 'time':'约公元1-2世纪', 'outcome':'天竺大乘论师，造《佛所行赞》《大庄严论经》《大乘起信论》（有争议）。', 'key_sutras':['t0192','t0201','t1667a']},
    '吉藏': {'place':'长安日严寺、延兴寺', 'time':'隋至唐初', 'sponsor':'——', 'outcome':'三论宗实际创始人，嘉祥大师，著《三论玄义》《中观论疏》《法华玄论》《金刚经义疏》等。', 'key_sutras':['t1824','t1825']},
    '道略': {'place':'——', 'time':'——', 'outcome':'集《杂譬喻经》。', 'key_sutras':['t0207','t0208']},
    '法救': {'place':'——', 'time':'——', 'outcome':'说一切有部四大论师之一，集《法句经》。', 'key_sutras':['t0210','t0213']},
    '世親': {'place':'阿逾陀国', 'time':'约公元4世纪', 'outcome':'无著之弟，瑜伽行派创始人之一，初于说一切有部出家造《俱舍论》，后转大乘造《唯识三十颂》《摄大乘论释》等，被尊为千部论主。', 'key_sutras':['t1558','t1594','t1587','t2049','t2031']},
    '慧遠': {'place':'庐山', 'time':'东晋太元至义熙年间（381-416年）', 'outcome':'净土宗初祖，庐山白莲社创立者，提倡念佛往生，著《沙门不敬王者论》。', 'key_sutras':['t2059']},
    '智者': {'place':'当阳玉泉寺、天台', 'time':'陈隋之际', 'outcome':'天台宗实际创始人，人称东土小释迦，说三大部（玄义、文句、止观）。', 'key_sutras':['t1716','t1911','t1931','t2050']},
    '灌頂': {'place':'天台', 'time':'隋唐之际', 'outcome':'章安大师，智者大师门人，笔录天台三大部，天台宗五祖。', 'key_sutras':['t1911','t1716','t2050']},
    '道宣': {'place':'长安终南山', 'time':'唐', 'outcome':'南山律宗开山，著《四分律行事钞》《续高僧传》《广弘明集》《释迦氏谱》。', 'key_sutras':['t1804','t2060','t2041','t2103']},
    '法藏': {'place':'长安大荐福寺', 'time':'唐', 'outcome':'华严宗三祖，贤首大师，著《华严经探玄记》《华严五教章》《华严金师子章》。', 'key_sutras':['t1881','t2054','t2073']},
    '契嵩': {'place':'杭州灵隐寺', 'time':'北宋', 'outcome':'云门宗禅僧，著《传法正宗记》《传法正宗定祖图》《传法正宗论》《镡津文集》，倡三教合一。', 'key_sutras':['t2078','t2079','t2080']},
    '慧皎': {'place':'会稽嘉祥寺', 'time':'南朝梁', 'outcome':'撰《高僧传》14卷（南朝梁以前257人正传）。', 'key_sutras':['t2059']},
    '道原': {'place':'——', 'time':'北宋景德年间', 'outcome':'法眼宗禅僧，撰《景德传灯录》30卷。', 'key_sutras':['t2076']},
    '贊寧': {'place':'开封', 'time':'北宋', 'outcome':'撰《宋高僧传》30卷、《大宋僧史略》。', 'key_sutras':['t2061','t2126']},
    '志磐': {'place':'四明东湖', 'time':'南宋', 'outcome':'天台宗僧，撰《佛祖统纪》54卷。', 'key_sutras':['t2035']},
    '費長房': {'place':'长安', 'time':'隋开皇年间', 'outcome':'撰《历代三宝纪》15卷。', 'key_sutras':['t2034']},
    '僧祐': {'place':'建康', 'time':'南朝梁', 'outcome':'律宗巨匠，撰《出三藏记集》《弘明集》《释迦谱》。', 'key_sutras':['t2040','t2102','t2145']},
}

# Lineage transmission events (key Chinese/Zen lineage transmission events)
LINEAGE_EVENTS = [
    {
        "id": "event:transmission:dharmaputra_vulture_peak",
        "type": "TransmissionEvent",
        "subtype": "传法·佛印迦叶",
        "label_zh": "灵山会世尊拈花、迦叶微笑（禅宗西天初祖传法）",
        "time": "佛说法华会前后（灵山会上）",
        "place": "王舍城灵鹫山",
        "presider": "释迦牟尼佛",
        "participants": ["摩诃迦叶"],
        "outcome": "世尊于灵山会上拈花示众，摩诃迦叶破颜微笑，佛曰'吾有正法眼藏，涅槃妙心，实相无相，微妙法门，不立文字，教外别传，付嘱摩诃迦叶'，是为禅宗西天第一祖付法。",
        "source": "《大梵天王问佛决疑经》《五灯会元》《景德传灯录》",
        "related_sutras": ["t2076","t2077"],
        "axis": "A4",
        "layer": "L5"
    },
    {
        "id": "event:transmission:bodhidharma_china",
        "type": "TransmissionEvent",
        "subtype": "传法·东土初祖",
        "label_zh": "菩提达摩东渡嵩山传法慧可（禅宗东土初祖传法）",
        "time": "梁普通年间（约520-536年）",
        "place": "少室山面壁九年、后于嵩山少林寺",
        "presider": "菩提达摩",
        "participants": ["慧可"],
        "outcome": "达摩西来，面壁九年，付法慧可（二祖）并传《楞伽经》四卷，为禅宗东土开山，立'二入四行'。",
        "source": "《续高僧传》《景德传灯录》《五灯会元》《宝林传》",
        "related_sutras": ["t0670","t2076","t2060","t2075"],
        "axis": "A4",
        "layer": "L5"
    },
    {
        "id": "event:transmission:huineng_dharma",
        "type": "TransmissionEvent",
        "subtype": "传法·六祖得法",
        "label_zh": "弘忍三更密付慧能衣钵（六祖得法）",
        "time": "唐龙朔元年（661年）",
        "place": "黄梅冯茂山（五祖寺）",
        "presider": "弘忍（五祖）",
        "participants": ["慧能（六祖）"],
        "outcome": "慧能书偈'菩提本无树，明镜亦非台；本来无一物，何处惹尘埃'，得五祖半夜密授《金刚经》与衣钵，南遁岭南，开南宗顿教。",
        "source": "《六祖坛经》《宋高僧传》《景德传灯录》",
        "related_sutras": ["t2008","t2076","t2061"],
        "axis": "A4",
        "layer": "L5"
    },
    {
        "id": "event:transmission:xuanzang_return",
        "type": "TransmissionEvent",
        "subtype": "求法归国",
        "label_zh": "玄奘西行求法归国译经",
        "time": "唐贞观十九年（645年）至麟德元年（664年）",
        "place": "长安",
        "presider": "玄奘",
        "participants": ["辩机","窥基","神昉","嘉尚","普光","玄应"],
        "outcome": "贞观三年（629）玄奘西行印度，贞观十九年（645）携经论520夹657部归长安，唐太宗于朱雀大街亲迎，后在弘福寺、慈恩寺、玉华宫组织译场20年，译出经论75部1335卷，为中国佛教译经史上最伟大的译事。",
        "source": "《大唐大慈恩寺三藏法师传》《大唐西域记》《续高僧传》",
        "related_sutras": ["t0220","t1579","t1558","t1585","t1586","t2053","t2087"],
        "axis": "A4",
        "layer": "L5"
    },
    {
        "id": "event:transmission:fajing_tiantai",
        "type": "TransmissionEvent",
        "subtype": "传法·天台付法",
        "label_zh": "慧文→慧思→智者，天台法脉确立",
        "time": "北齐至隋（约550-597年）",
        "place": "南岳、金陵、天台山",
        "presider": "慧思",
        "participants": ["智者大师"],
        "outcome": "北齐慧文读《大智度论》《中论》悟一心三观，传南岳慧思，慧思传智者大师；智者于天台山讲法华三大部，正式立宗。",
        "source": "《摩诃止观》《佛祖统纪》《续高僧传》",
        "related_sutras": ["t1911","t1716","t1931","t2035"],
        "axis": "A4",
        "layer": "L5"
    }
]

# ============================================================
# 3. StoryEvent (本生/本事/因缘/譬喻)
# ============================================================
STORY_KEYWORDS = ['本生','本事','因緣','緣起','授記','譬喻','喻經','故事','出家','成道','降魔','涅槃','本行','遊經','本起','因由']
def is_story_sutra(meta):
    if not meta.get('category'): return False
    cat = meta['category']
    # 本缘部全算
    if '本緣' in cat: return True
    # 史传部里单独的菩萨/祖师传不算"故事"，但付法藏/阿育王故事算
    if '史傳' in cat:
        t = meta.get('title','')
        for kw in ['阿育王','付法藏','高僧','往生','感應','感應傳','冥報']:
            if kw in t: return True
        return False
    return False

# Famous jataka/avadana stories hand-curated
FAMOUS_STORIES = [
    {'sutra':'t0181a','title':'九色鹿本生（修凡鹿王本生）','chapter_pattern':'九色鹿|鹿王','figure':['九色鹿'],'description':'九色鹿救起溺水人，反被其所卖，国王得知后惩恶扬善，为敦煌壁画著名题材。'},
    {'sutra':'t0171','title':'须大拏太子本生','chapter_pattern':'須大拏','figure':['须大拏太子'],'description':'太子须大拏乐善好施，将国宝白象施与敌国，被父王驱逐入山，终以布施圆满佛道。'},
    {'sutra':'t0174','title':'睒子本生','chapter_pattern':'睒子','figure':['睒摩迦（睒子）'],'description':'睒子孝养父母于山中，被国王误射，天帝感其孝感救活之，为著名孝亲本生。'},
    {'sutra':'t0172','title':'萨埵太子舍身饲虎','chapter_pattern':'飴餓虎|投身|薩埵','figure':['摩诃萨埵太子'],'description':'三王子入山，萨埵见饿虎将食其子，投身饲虎；父王收骨起塔。为敦煌壁画著名题材。'},
    {'sutra':'t0161','title':'长寿王本生','chapter_pattern':'長壽王|長生','figure':['长寿王','长生太子'],'description':'长寿王仁恕不战而国亡，长生太子报仇后止杀，以德报怨。'},
    {'sutra':'t0162','title':'金色王本生','chapter_pattern':'金色王','figure':['金色王'],'description':'金色王布施辟支佛，感得金轮王果报。'},
    {'sutra':'t0165','title':'顶生王因缘','chapter_pattern':'頂生王','figure':['顶生王'],'description':'顶生王由贪心升天、贪享天福最终坠地，说贪欲过患。'},
    {'sutra':'t0163','title':'妙色王因缘','chapter_pattern':'妙色王','figure':['妙色王'],'description':'妙色王为求法舍妻子亲子，终得佛授记。'},
    {'sutra':'t0209','title':'百喻经九十八喻（选典型）','chapter_pattern':'三重樓|愚人食鹽|貧人燒粗褐|估客偷金|婦詐稱死','figure':[],'description':'僧伽斯那集98则寓言，如愚人食盐、三重楼喻、杀子求子等，以比喻开示佛法。'},
    {'sutra':'t0202','title':'贤愚经·摩诃萨埵以身施虎缘','chapter_pattern':'摩訶薩埵|薩埵','figure':['摩诃萨埵太子'],'description':'（同t0172）《贤愚经》版本。'},
    {'sutra':'t0202','title':'贤愚经·善事太子入海缘','chapter_pattern':'善事太子|善事','figure':['善事太子'],'description':'善事太子为救济众生入海求摩尼宝珠，历经艰险。'},
    {'sutra':'t0202','title':'贤愚经·须达起精舍缘','chapter_pattern':'須達|祇樹|給孤獨','figure':['须达多长者（给孤独长者）'],'description':'须达多长者为佛购祇陀太子园起祇树给孤独精舍。'},
    {'sutra':'t0203','title':'杂宝藏经·弃老国缘','chapter_pattern':'棄老|棄老國','figure':['弃老国大臣父'],'description':'国王曾令弃老，一大臣密养其父，以父智解邻国难题，遂令全国敬老。'},
    {'sutra':'t0203','title':'杂宝藏经·波罗奈王闻偈悟解缘','chapter_pattern':'波羅奈|半偈|聞偈','figure':['波罗奈王'],'description':'国王为闻半偈不惜舍身。'},
    {'sutra':'t0197','title':'兴起行经·孙陀利宿缘','chapter_pattern':'孫陀利|宿緣','figure':['孙陀利'],'description':'佛说本生谤孙陀利宿缘，示因果不虚。'},
    {'sutra':'t0152','title':'六度集经·猴王本生','chapter_pattern':'猴王|獼猴王','figure':['猕猴王'],'description':'猴王为救群猴自以身为桥，身折而群猴得活。'},
    {'sutra':'t0152','title':'六度集经·九色鹿王本生','chapter_pattern':'九色鹿|鹿王','figure':['九色鹿'],'description':'（同t0181a）《六度集经》版本。'},
    {'sutra':'t0156','title':'大方便佛报恩经·须阇提太子本生','chapter_pattern':'須闍提','figure':['须阇提太子'],'description':'须阇提太子割肉奉养父母，示至孝报恩。'},
    {'sutra':'t0184','title':'修行本起经·菩萨降魔成道','chapter_pattern':'降魔|成道|菩提','figure':['释迦牟尼佛','魔王波旬'],'description':'释迦菩萨于菩提树下降魔成道。'},
    {'sutra':'t0189','title':'过去现在因果经·树下诞生','chapter_pattern':'誕生|降誕|藍毗尼','figure':['释迦牟尼佛','摩耶夫人'],'description':'释迦太子于蓝毗尼园无忧树下诞生。'},
    {'sutra':'t0189','title':'过去现在因果经·出游四门','chapter_pattern':'四門|出遊|老病死','figure':['释迦太子','净饭王'],'description':'太子出四门见老病死沙门，决意出家。'},
    {'sutra':'t0189','title':'过去现在因果经·夜半逾城','chapter_pattern':'逾城|夜半|出家','figure':['释迦太子','车匿','犍陟'],'description':'太子半夜逾城出家。'},
    {'sutra':'t0190','title':'佛本行集经·六年苦行','chapter_pattern':'苦行|六年|尼連禪','figure':['释迦菩萨'],'description':'菩萨六年苦行，后受乳糜、沐浴于尼连禅河。'},
    {'sutra':'t0200','title':'撰集百缘经·善恶因果百缘','chapter_pattern':'緣$','figure':[],'description':'集百个善恶因果缘故事。'},
    {'sutra':'t0217','title':'譬喻经·医喻等','chapter_pattern':'醫|藥','figure':[],'description':'义净译《譬喻经》集短小譬喻故事。'},
    {'sutra':'t0450','title':'盂兰盆经·目连救母','chapter_pattern':'目連|目犍連|盂蘭','figure':['摩诃目犍连','目连母青提夫人'],'description':'目连观见母亲堕饿鬼道，佛告以七月十五僧自恣日设盂兰盆供僧救度七世父母，为盂兰盆节来源。'},
    {'sutra':'t2042','title':'阿育王传·阿育王起八万四千塔','chapter_pattern':'八萬四千|起塔','figure':['阿育王'],'description':'阿育王归信佛教后于阎浮提起八万四千宝塔。'},
    {'sutra':'t2045','title':'阿育王息坏目因缘经','chapter_pattern':'壞目|拘那羅|須那拘多羅','figure':['阿育王','驹那罗太子'],'description':'阿育王太子驹那罗被抉双眼而后以佛法复明之因缘。'},
]


def build_all():
    items = load_index()
    id_to_meta = {it['id']:it for it in items}

    # ---------- Build translation events by translator ----------
    trans_groups = collections.defaultdict(list)
    trans_eras = {}
    trans_dynasties = {}
    for it in items:
        t = it.get('translator','') or ''
        if not t: continue
        if any(skip in t for skip in ['失譯','失译','——']): continue
        name = translator_id(t)
        if not name: continue
        trans_groups[name].append(it['id'])
        era = era_from_translator(t)
        if era:
            trans_eras[name] = era
            # dynasty
            d = re.match(r'([\u4e00-\u9fa5]{1,2})[代時]', era)
            if d: trans_dynasties[name] = d.group(1)

    translation_events = []
    tid_count = collections.Counter()
    for name, sutra_ids in sorted(trans_groups.items(), key=lambda x:-len(x[1])):
        if len(sutra_ids) < 1: continue
        era = trans_eras.get(name,'不明')
        info = TRANSLATION_PRESIDERS.get(name, {})
        tid = f"event:translation:{name}"
        # ensure id unique if conflict
        while tid_count[tid]:
            tid = f"event:translation:{name}_{tid_count[tid]}"
            tid_count[tid]+=1
        tid_count[tid]=1
        key_sutras = info.get('key_sutras', [])
        # intersect with actual sutras we have
        key_sutras = [s for s in key_sutras if s in id_to_meta]
        ev = {
            "id": tid,
            "type": "TransmissionEvent",
            "subtype": "译经",
            "label_zh": f"{name}译经（{era}）",
            "time": info.get('time', era),
            "place": info.get('place',''),
            "presider": name,
            "participants": [],
            "outcome": info.get('outcome', f"译经{len(sutra_ids)}部。"),
            "source": info.get('source','《历代三宝纪》《开元释教录》《出三藏记集》'),
            "related_sutras": sutra_ids,
            "key_sutras": key_sutras[:8],
            "total_translated": len(sutra_ids),
            "dynasty": trans_dynasties.get(name,''),
            "sponsor": info.get('sponsor',''),
            "axis": "A4",
            "layer": "L4"
        }
        translation_events.append(ev)

    # ---------- Build story events ----------
    story_events = []
    # 1. famous stories
    for fs in FAMOUS_STORIES:
        if fs['sutra'] not in id_to_meta: continue
        story_events.append({
            "id": f"event:story:{fs['sutra']}_{fs['title'][:10]}",
            "type": "StoryEvent",
            "subtype": "本生/因缘",
            "label_zh": fs['title'],
            "figure": fs['figure'],
            "source_sutra": fs['sutra'],
            "source_title": id_to_meta[fs['sutra']]['title'],
            "chapter_pattern": fs['chapter_pattern'],
            "description": fs['description'],
            "axis": "A4",
            "layer": "L3"
        })

    # 2. scan chapters in 本缘部 for additional stories
    # load instances via manifest shards
    try:
        manifest = load_json(INST_DIR / 'manifest.json')
    except:
        manifest = {'files': []}
    inst_data = {}
    import glob
    # load all shards
    SHARD_DIR = INST_DIR / 'shards'
    if SHARD_DIR.exists():
        for sp in sorted(glob.glob(str(SHARD_DIR / 'shard-*.json'))):
            try:
                sh = load_json(sp)
                for e in sh:
                    inst_data[e['id']] = e
            except: pass
    # also standalone files
    for fp in glob.glob(str(INST_DIR / 't*.json')):
        try:
            d = load_json(fp)
            inst_data[d['id']] = d
        except: pass

    # add 本缘部 经 that contain 品 with 因緣/本生/授記
    auto_story_count = 0
    added = set(s['source_sutra']+'_'+s['label_zh'] for s in story_events)
    for sid, meta in id_to_meta.items():
        if not is_story_sutra(meta): continue
        inst = inst_data.get(sid)
        if not inst: continue
        for ch in inst.get('chapters', []):
            title = ch.get('chapter_title','')
            if not title: continue
            has_kw = any(kw in title for kw in STORY_KEYWORDS)
            if has_kw and len(title) < 30:
                # avoid duplicate with famous stories
                key = sid + '_' + title
                if key in added: continue
                # avoid 序品/流通品
                if re.match(r'^(序|序品|流通|第一|初品|緣起)', title): continue
                story_events.append({
                    "id": f"event:story:{sid}_ch{ch.get('chapter_no',0)}",
                    "type": "StoryEvent",
                    "subtype": "品目·本生因缘",
                    "label_zh": f"{meta['title']}·{title}",
                    "source_sutra": sid,
                    "source_title": meta['title'],
                    "chapter_title": title,
                    "chapter_no": ch.get('chapter_no'),
                    "description": f"出自{meta['title']}（{meta.get('translator','')}）",
                    "axis": "A4",
                    "layer": "L3"
                })
                added.add(key)
                auto_story_count += 1

    print(f"[councils] {len(COUNCILS)}")
    print(f"[translation_events] {len(translation_events)} (+ {len(LINEAGE_EVENTS)} lineage)")
    print(f"[story_events] famous={len(FAMOUS_STORIES)}, auto_chapter={auto_story_count}, total={len(story_events)}")

    # ---------- Back-write dharma assemblies ----------
    try:
        da = load_json(ROOT / 'ontology' / 'dharma_assemblies.json')
        da_map = da['assemblies']
    except Exception as e:
        print(f'[warn] dharma_assemblies not loaded: {e}')
        da_map = {}
    sutra_to_da = collections.defaultdict(list)
    for da_id, da_entry in da_map.items():
        for sid in da_entry.get('sutras', []):
            if sid in id_to_meta:
                sutra_to_da[sid].append(da_id)
    print(f"[dharma_assemblies] {len(da_map)} assemblies, {len(sutra_to_da)} sutras linked")

    # ---------- Back-write to instances ----------
    # Build reverse index
    sutra_to_councils = collections.defaultdict(list)
    for c in COUNCILS:
        for sid in c['related_sutras']:
            if sid in id_to_meta:
                sutra_to_councils[sid].append(c['id'])

    sutra_to_trans = collections.defaultdict(list)
    for te in translation_events + LINEAGE_EVENTS:
        for sid in te['related_sutras']:
            if sid in id_to_meta:
                sutra_to_trans[sid].append(te['id'])

    sutra_to_stories = collections.defaultdict(list)
    for se in story_events:
        sid = se['source_sutra']
        if sid in id_to_meta:
            sutra_to_stories[sid].append(se['id'])

    # Add events to instances
    mod_count = 0
    for sid in id_to_meta:
        inst = inst_data.get(sid)
        if not inst: continue
        changes = 0
        if sid in sutra_to_da:
            inst['dharma_assembly'] = sutra_to_da[sid][0]  # one primary
            changes+=1
        if sid in sutra_to_councils:
            inst['councils'] = sorted(set(sutra_to_councils[sid]))
            changes+=1
        if sid in sutra_to_trans:
            inst['transmission_events'] = sorted(set(sutra_to_trans[sid]))
            changes+=1
        if sid in sutra_to_stories:
            inst['story_events'] = sorted(set(sutra_to_stories[sid]))
            changes+=1
        if changes: mod_count+=1
        # also write back standalone json immediately
        sp_file = INST_DIR / f'{sid}.json'
        with open(sp_file,'w',encoding='utf-8') as f:
            json.dump(inst,f,ensure_ascii=False,indent=2)

    print(f"[instances_updated] {mod_count} / {len(id_to_meta)}")

    # ---------- Write events JSON ----------
    events_meta = {
        "version": "3.1.0-m4",
        "councils": len(COUNCILS),
        "translation_events": len(translation_events)+len(LINEAGE_EVENTS),
        "story_events": len(story_events),
        "dharma_assemblies_ref": "ontology/dharma_assemblies.json",
    }
    all_events = {
        "councils": COUNCILS,
        "translation_events": LINEAGE_EVENTS + translation_events,
        "story_events": story_events,
        "_meta": events_meta
    }
    dump_json(INST_DIR / 'events.json', all_events)

    # ---------- Re-build shards ----------
    # re-collect all instance files in a flat list
    all_insts = []
    # first add standalone json (they take priority)
    standalone = {}
    for fp in glob.glob(str(INST_DIR / 't*.json')):
        try:
            d = load_json(fp)
            standalone[d['id']] = d
        except: pass
    for sid, d in inst_data.items():
        if sid in standalone: d = standalone[sid]
        all_insts.append(d)
    all_insts.sort(key=lambda x: x['id'])

    SHARD_SIZE = 55
    os.makedirs(SHARD_DIR, exist_ok=True)
    # remove old shards
    for sp in glob.glob(str(SHARD_DIR / 'shard-*.json')):
        os.remove(sp)
    shard_manifest = []
    for i in range(0, len(all_insts), SHARD_SIZE):
        shard_idx = i // SHARD_SIZE
        chunk = all_insts[i:i+SHARD_SIZE]
        fn = f"shard-{shard_idx:03d}.json"
        dump_json(SHARD_DIR / fn, chunk)
        shard_manifest.append({
            "file": f"ontology/instances/shards/{fn}",
            "start": chunk[0]['id'],
            "end": chunk[-1]['id'],
            "count": len(chunk)
        })
    new_manifest = {
        "version": "3.1.0-m4",
        "total": len(all_insts),
        "total_chars": sum(len(json.dumps(x,ensure_ascii=False)) for x in all_insts),
        "chapters": sum(len(x.get('chapters',[])) for x in all_insts),
        "paragraphs": sum(
            sum(len(ch.get('paragraphs',[])) for ch in x.get('chapters',[]))
            for x in all_insts
        ),
        "gathas": sum(len(x.get('gathas',[])) for x in all_insts),
        "mantras": sum(len(x.get('mantras',[])) for x in all_insts),
        "dharma_assemblies": len(set(x.get('dharma_assembly','') for x in all_insts if x.get('dharma_assembly'))),
        "councils": sum(len(x.get('councils',[])) for x in all_insts),
        "transmission_events": sum(len(x.get('transmission_events',[])) for x in all_insts),
        "story_events": sum(len(x.get('story_events',[])) for x in all_insts),
        "with_figures": sum(1 for x in all_insts if x.get('figures')),
        "with_doctrines": sum(1 for x in all_insts if x.get('doctrines')),
        "shards": shard_manifest
    }
    # recompute per-shard derived stats
    new_manifest['sutras_with_dharma_assembly'] = sum(1 for x in all_insts if x.get('dharma_assembly'))
    new_manifest['sutras_with_council'] = sum(1 for x in all_insts if x.get('councils'))
    new_manifest['sutras_with_transmission'] = sum(1 for x in all_insts if x.get('transmission_events'))
    new_manifest['sutras_with_story'] = sum(1 for x in all_insts if x.get('story_events'))
    dump_json(INST_DIR / 'manifest.json', new_manifest)
    print(json.dumps(new_manifest, ensure_ascii=False, indent=2))

    # ---------- Update instance-links ----------
    try:
        links = load_json(INST_DIR / 'instance-links.json')
    except:
        links = {"concepts":{},"figures":{},"schools":{},"categories":{},"meta":{}}
    # add councils
    links['councils'] = {}
    for c in COUNCILS:
        links['councils'][c['id']] = {
            "label": c['label_zh'],
            "sutras": [s for s in c['related_sutras'] if s in id_to_meta]
        }
    links['transmission_events'] = {}
    for te in translation_events + LINEAGE_EVENTS:
        links['transmission_events'][te['id']] = {
            "label": te['label_zh'],
            "subtype": te.get('subtype',''),
            "sutras": [s for s in te['related_sutras'] if s in id_to_meta]
        }
    links['story_events'] = {}
    for se in story_events:
        links['story_events'][se['id']] = {
            "label": se['label_zh'],
            "subtype": se.get('subtype',''),
            "source_sutra": se['source_sutra']
        }
    links['meta']['version'] = '3.1.0-m4'
    links['meta']['councils'] = len(COUNCILS)
    links['meta']['translation_events'] = len(translation_events)+len(LINEAGE_EVENTS)
    links['meta']['story_events'] = len(story_events)
    dump_json(INST_DIR / 'instance-links.json', links)

if __name__ == '__main__':
    build_all()

// 佛学本体论完整数据 v2.0
// 共 216 个义理概念、100 位人物、100 部核心经典、984 条本体关系
const ontologyData = {
  concepts: [
  {
    "id": "c001",
    "name": "法界",
    "layer": "L1",
    "definition": "一切诸法的总体，含摄万有的真实理体",
    "sect": "通途"
  },
  {
    "id": "c002",
    "name": "真如",
    "layer": "L1",
    "definition": "诸法的真实本性，非有非无，不变随缘",
    "sect": "通途"
  },
  {
    "id": "c003",
    "name": "佛性",
    "layer": "L1",
    "definition": "一切众生本具的成佛可能性",
    "sect": "大乘通途"
  },
  {
    "id": "c004",
    "name": "阿赖耶识",
    "layer": "L1",
    "definition": "唯识宗核心概念，含藏一切业种的根本识",
    "sect": "唯识宗"
  },
  {
    "id": "c005",
    "name": "空性",
    "layer": "L1",
    "definition": "一切法缘起无自性，是诸法实相",
    "sect": "中观/三论"
  },
  {
    "id": "c006",
    "name": "缘起",
    "layer": "L1",
    "definition": "一切法因缘和合而生，因缘分散而灭",
    "sect": "通途"
  },
  {
    "id": "c007",
    "name": "涅槃",
    "layer": "L1",
    "definition": "烦恼灭尽、超脱生死轮回的终极解脱境界",
    "sect": "通途"
  },
  {
    "id": "c008",
    "name": "如来藏",
    "layer": "L1",
    "definition": "一切众生身中潜藏的如来智慧德相，众生成佛的根据",
    "sect": "如来藏系"
  },
  {
    "id": "c009",
    "name": "菩提",
    "layer": "L1",
    "definition": "无上正等正觉，佛陀所证得的究竟觉悟",
    "sect": "通途"
  },
  {
    "id": "c010",
    "name": "法身",
    "layer": "L1",
    "definition": "佛的三身之一，以诸法实相为体，遍一切处",
    "sect": "大乘通途"
  },
  {
    "id": "c011",
    "name": "解脱",
    "layer": "L1",
    "definition": "脱离烦恼业报束缚，超越生死轮回的自由境界",
    "sect": "通途"
  },
  {
    "id": "c012",
    "name": "般若",
    "layer": "L1",
    "definition": "通达诸法实相的究竟智慧，六度之核心",
    "sect": "般若系"
  },
  {
    "id": "c013",
    "name": "无明",
    "layer": "L1",
    "definition": "对诸法实相的迷惑，是生死轮回的根本",
    "sect": "通途"
  },
  {
    "id": "c014",
    "name": "种子",
    "layer": "L1",
    "definition": "阿赖耶识中含藏的能生起现行诸法的功能",
    "sect": "唯识宗"
  },
  {
    "id": "c015",
    "name": "一真法界",
    "layer": "L1",
    "definition": "华严宗核心本体，唯一真实、融摄万有的绝对理体",
    "sect": "华严宗"
  },
  {
    "id": "c016",
    "name": "自性",
    "layer": "L1",
    "definition": "诸法本具的本性，禅宗指众生本具的自心本性",
    "sect": "禅宗"
  },
  {
    "id": "c017",
    "name": "实相",
    "layer": "L1",
    "definition": "诸法的真实相状，离一切言说分别",
    "sect": "大乘通途"
  },
  {
    "id": "c018",
    "name": "佛",
    "layer": "L1",
    "definition": "觉者，圆满觉悟宇宙人生真理的圣者",
    "sect": "通途"
  },
  {
    "id": "c019",
    "name": "法",
    "layer": "L1",
    "definition": "佛法、教法、一切存在的事物",
    "sect": "通途"
  },
  {
    "id": "c020",
    "name": "僧",
    "layer": "L1",
    "definition": "依佛法修行的和合众，三宝之一",
    "sect": "通途"
  },
  {
    "id": "c021",
    "name": "五蕴",
    "layer": "L2",
    "definition": "构成众生身心的五种积聚：色受想行识",
    "sect": "通途"
  },
  {
    "id": "c022",
    "name": "十二处",
    "layer": "L2",
    "definition": "六根加六境，是认识发生的处所",
    "sect": "通途"
  },
  {
    "id": "c023",
    "name": "十八界",
    "layer": "L2",
    "definition": "六根、六境、六识合为十八界，涵盖一切法",
    "sect": "通途"
  },
  {
    "id": "c024",
    "name": "十二缘起",
    "layer": "L2",
    "definition": "众生生死轮回的十二个环节：无明缘行，行缘识……生缘老死",
    "sect": "通途"
  },
  {
    "id": "c025",
    "name": "四圣谛",
    "layer": "L2",
    "definition": "苦集灭道，佛陀初转法轮核心教义",
    "sect": "通途"
  },
  {
    "id": "c026",
    "name": "八正道",
    "layer": "L2",
    "definition": "达到涅槃的八种正确方法：正见正思惟正语正业正命正精进正念正定",
    "sect": "通途"
  },
  {
    "id": "c027",
    "name": "三法印",
    "layer": "L2",
    "definition": "诸行无常、诸法无我、涅槃寂静，印证是否佛法的标准",
    "sect": "通途"
  },
  {
    "id": "c028",
    "name": "六度",
    "layer": "L2",
    "definition": "菩萨修行的六种法门：布施、持戒、忍辱、精进、禅定、般若",
    "sect": "大乘通途"
  },
  {
    "id": "c029",
    "name": "四念处",
    "layer": "L2",
    "definition": "观身不净、观受是苦、观心无常、观法无我，三十七道品之一",
    "sect": "通途"
  },
  {
    "id": "c030",
    "name": "四正勤",
    "layer": "L2",
    "definition": "已生恶令断、未生恶令不生、未生善令生、已生善令增长",
    "sect": "通途"
  },
  {
    "id": "c031",
    "name": "四如意足",
    "layer": "L2",
    "definition": "欲如意足、精进如意足、心如意足、观如意足",
    "sect": "通途"
  },
  {
    "id": "c032",
    "name": "五根",
    "layer": "L2",
    "definition": "信根、进根、念根、定根、慧根，修行的根本",
    "sect": "通途"
  },
  {
    "id": "c033",
    "name": "五力",
    "layer": "L2",
    "definition": "信力、进力、念力、定力、慧力，五根增长产生的力量",
    "sect": "通途"
  },
  {
    "id": "c034",
    "name": "七觉支",
    "layer": "L2",
    "definition": "念觉支、择法觉支、精进觉支、喜觉支、轻安觉支、定觉支、舍觉支",
    "sect": "通途"
  },
  {
    "id": "c035",
    "name": "三学",
    "layer": "L2",
    "definition": "戒、定、慧三学，佛教修行的总纲",
    "sect": "通途"
  },
  {
    "id": "c036",
    "name": "六根",
    "layer": "L2",
    "definition": "眼耳鼻舌身意六种认识器官",
    "sect": "通途"
  },
  {
    "id": "c037",
    "name": "六尘",
    "layer": "L2",
    "definition": "色声香味触法六种认识对象，又名六境",
    "sect": "通途"
  },
  {
    "id": "c038",
    "name": "六识",
    "layer": "L2",
    "definition": "眼识耳识鼻识舌识身识意识六种认识作用",
    "sect": "通途"
  },
  {
    "id": "c039",
    "name": "烦恼",
    "layer": "L2",
    "definition": "扰乱众生身心、障碍觉悟的心理作用",
    "sect": "通途"
  },
  {
    "id": "c040",
    "name": "贪",
    "layer": "L2",
    "definition": "三毒之一，对顺境的贪爱执著",
    "sect": "通途"
  },
  {
    "id": "c041",
    "name": "嗔",
    "layer": "L2",
    "definition": "三毒之一，对逆境的忿怒憎恨",
    "sect": "通途"
  },
  {
    "id": "c042",
    "name": "痴",
    "layer": "L2",
    "definition": "三毒之一，对实相的愚痴迷惑，即无明",
    "sect": "通途"
  },
  {
    "id": "c043",
    "name": "慢",
    "layer": "L2",
    "definition": "六根本烦恼之一，自恃凌他的傲慢心",
    "sect": "通途"
  },
  {
    "id": "c044",
    "name": "疑",
    "layer": "L2",
    "definition": "六根本烦恼之一，对佛法真理的疑惑",
    "sect": "通途"
  },
  {
    "id": "c045",
    "name": "恶见",
    "layer": "L2",
    "definition": "六根本烦恼之一，颠倒错误的见解",
    "sect": "通途"
  },
  {
    "id": "c046",
    "name": "业",
    "layer": "L2",
    "definition": "众生的身口意行为，能招感未来果报",
    "sect": "通途"
  },
  {
    "id": "c047",
    "name": "轮回",
    "layer": "L2",
    "definition": "众生在六道中生死轮转，无有出期",
    "sect": "通途"
  },
  {
    "id": "c048",
    "name": "六道",
    "layer": "L2",
    "definition": "天、人、阿修罗、畜生、饿鬼、地狱六种众生生存境界",
    "sect": "通途"
  },
  {
    "id": "c049",
    "name": "三世因果",
    "layer": "L2",
    "definition": "过去世、现在世、未来世，善因得善果，恶因得恶果",
    "sect": "通途"
  },
  {
    "id": "c050",
    "name": "三宝",
    "layer": "L2",
    "definition": "佛宝、法宝、僧宝，佛教的核心归依对象",
    "sect": "通途"
  },
  {
    "id": "c051",
    "name": "三归依",
    "layer": "L2",
    "definition": "归依佛、归依法、归依僧，进入佛门的根本仪式",
    "sect": "通途"
  },
  {
    "id": "c052",
    "name": "五戒",
    "layer": "L2",
    "definition": "在家信众应持的五条根本戒律：不杀生、不偷盗、不邪淫、不妄语、不饮酒",
    "sect": "通途"
  },
  {
    "id": "c053",
    "name": "八戒",
    "layer": "L2",
    "definition": "在家信众一日一夜受持的八种斋戒",
    "sect": "通途"
  },
  {
    "id": "c054",
    "name": "十善",
    "layer": "L2",
    "definition": "身三善、口四善、意三善，共十种善业",
    "sect": "通途"
  },
  {
    "id": "c055",
    "name": "四摄",
    "layer": "L2",
    "definition": "菩萨摄受众生的四种方法：布施、爱语、利行、同事",
    "sect": "大乘通途"
  },
  {
    "id": "c056",
    "name": "四无量心",
    "layer": "L2",
    "definition": "慈、悲、喜、舍四种广大的利他心",
    "sect": "大乘通途"
  },
  {
    "id": "c057",
    "name": "三十七道品",
    "layer": "L2",
    "definition": "通往涅槃的三十七种修行方法总称",
    "sect": "通途"
  },
  {
    "id": "c058",
    "name": "择灭",
    "layer": "L2",
    "definition": "以智慧简择力断灭烦恼，证得涅槃",
    "sect": "说一切有部"
  },
  {
    "id": "c059",
    "name": "无我",
    "layer": "L2",
    "definition": "一切法无有恒常不变、独立存在的自性",
    "sect": "通途"
  },
  {
    "id": "c060",
    "name": "无常",
    "layer": "L2",
    "definition": "一切法都在刹那生灭变化，没有恒常不变的事物",
    "sect": "通途"
  },
  {
    "id": "c061",
    "name": "苦",
    "layer": "L2",
    "definition": "三法印之一，三界无安，犹如火宅",
    "sect": "通途"
  },
  {
    "id": "c062",
    "name": "中道",
    "layer": "L2",
    "definition": "远离二边极端的中正之道",
    "sect": "通途"
  },
  {
    "id": "c063",
    "name": "因缘",
    "layer": "L2",
    "definition": "诸法生起的条件，因是主要条件，缘是辅助条件",
    "sect": "通途"
  },
  {
    "id": "c064",
    "name": "果报",
    "layer": "L2",
    "definition": "业力所招感的异熟果",
    "sect": "通途"
  },
  {
    "id": "c065",
    "name": "众生",
    "layer": "L2",
    "definition": "一切有情识的生命",
    "sect": "通途"
  },
  {
    "id": "c066",
    "name": "佛土",
    "layer": "L2",
    "definition": "佛所教化的国土世界",
    "sect": "大乘通途"
  },
  {
    "id": "c067",
    "name": "娑婆世界",
    "layer": "L2",
    "definition": "释迦牟尼佛所教化的现实世界",
    "sect": "通途"
  },
  {
    "id": "c068",
    "name": "西方极乐世界",
    "layer": "L2",
    "definition": "阿弥陀佛所摄受的净土，念佛众生往生之处",
    "sect": "净土宗"
  },
  {
    "id": "c069",
    "name": "东方净琉璃世界",
    "layer": "L2",
    "definition": "药师佛所摄受的净土",
    "sect": "通途"
  },
  {
    "id": "c070",
    "name": "兜率天",
    "layer": "L2",
    "definition": "弥勒菩萨所在的天界，未来将下生成佛",
    "sect": "通途"
  },
  {
    "id": "c071",
    "name": "三科",
    "layer": "L3",
    "definition": "五蕴、十二处、十八界，是部派佛教对一切法的分类",
    "sect": "部派佛教"
  },
  {
    "id": "c072",
    "name": "五位七十五法",
    "layer": "L3",
    "definition": "说一切有部对一切法的分类：色法11、心法1、心所法46、心不相应行法14、无为法3",
    "sect": "说一切有部"
  },
  {
    "id": "c073",
    "name": "我空法有",
    "layer": "L3",
    "definition": "说一切有部核心主张：人我是空，但法体实有",
    "sect": "说一切有部"
  },
  {
    "id": "c074",
    "name": "三世实有",
    "layer": "L3",
    "definition": "说一切有部主张：过去、现在、未来三世法体真实存在",
    "sect": "说一切有部"
  },
  {
    "id": "c075",
    "name": "法体恒有",
    "layer": "L3",
    "definition": "一切法的体性恒常存在，作用有生灭",
    "sect": "说一切有部"
  },
  {
    "id": "c076",
    "name": "六因四缘",
    "layer": "L3",
    "definition": "说一切有部的缘起理论：能作因、俱有因、同类因、相应因、遍行因、异熟因；因缘、等无间缘、所缘缘、增上缘",
    "sect": "说一切有部"
  },
  {
    "id": "c077",
    "name": "五果",
    "layer": "L3",
    "definition": "异熟果、等流果、士用果、增上果、离系果",
    "sect": "说一切有部"
  },
  {
    "id": "c078",
    "name": "有漏",
    "layer": "L3",
    "definition": "含有烦恼的法，能招感三界生死果报",
    "sect": "通途"
  },
  {
    "id": "c079",
    "name": "无漏",
    "layer": "L3",
    "definition": "断离烦恼的法，能证得涅槃",
    "sect": "通途"
  },
  {
    "id": "c080",
    "name": "见道",
    "layer": "L3",
    "definition": "以无漏智亲证四圣谛理，断除见惑，进入圣者之流",
    "sect": "通途"
  },
  {
    "id": "c081",
    "name": "修道",
    "layer": "L3",
    "definition": "见道后继续修行，渐次断除修惑",
    "sect": "通途"
  },
  {
    "id": "c082",
    "name": "无学道",
    "layer": "L3",
    "definition": "烦恼断尽，无需再学，即阿罗汉果",
    "sect": "通途"
  },
  {
    "id": "c083",
    "name": "四向四果",
    "layer": "L3",
    "definition": "须陀洹向/果、斯陀含向/果、阿那含向/果、阿罗汉向/果",
    "sect": "声闻乘"
  },
  {
    "id": "c084",
    "name": "阿罗汉",
    "layer": "L3",
    "definition": "声闻乘最高果位，烦恼断尽，应受人天供养",
    "sect": "声闻乘"
  },
  {
    "id": "c085",
    "name": "辟支佛",
    "layer": "L3",
    "definition": "缘觉，无佛出世时观十二缘起自觉悟道者",
    "sect": "缘觉乘"
  },
  {
    "id": "c086",
    "name": "菩萨",
    "layer": "L3",
    "definition": "上求佛道、下化众生的大乘修行者",
    "sect": "大乘通途"
  },
  {
    "id": "c087",
    "name": "佛果",
    "layer": "L3",
    "definition": "菩萨修行圆满所证得的究竟佛位",
    "sect": "大乘通途"
  },
  {
    "id": "c088",
    "name": "三乘",
    "layer": "L3",
    "definition": "声闻乘、缘觉乘、菩萨乘",
    "sect": "通途"
  },
  {
    "id": "c089",
    "name": "一乘",
    "layer": "L3",
    "definition": "唯一佛乘，三乘皆是方便，最终皆归于佛道",
    "sect": "法华宗"
  },
  {
    "id": "c090",
    "name": "化城",
    "layer": "L3",
    "definition": "法华经中比喻：佛陀以方便力设立三乘化城，引导众生趋向一乘",
    "sect": "法华宗"
  },
  {
    "id": "c091",
    "name": "有余涅槃",
    "layer": "L3",
    "definition": "烦恼已断，但色身果报尚存",
    "sect": "通途"
  },
  {
    "id": "c092",
    "name": "无余涅槃",
    "layer": "L3",
    "definition": "色身果报亦尽，究竟寂灭",
    "sect": "通途"
  },
  {
    "id": "c093",
    "name": "自性涅槃",
    "layer": "L3",
    "definition": "一切法本性清净，自性本自涅槃",
    "sect": "大乘通途"
  },
  {
    "id": "c094",
    "name": "无住涅槃",
    "layer": "L3",
    "definition": "不住生死、不住涅槃，大乘菩萨的究竟涅槃",
    "sect": "唯识宗"
  },
  {
    "id": "c095",
    "name": "四谛十六行相",
    "layer": "L3",
    "definition": "观苦谛四行相：苦、空、无常、无我；集谛四行相：因、集、生、缘；灭谛四行相：灭、静、妙、离；道谛四行相：道、如、行、出",
    "sect": "部派佛教"
  },
  {
    "id": "c096",
    "name": "八忍八智",
    "layer": "L3",
    "definition": "见道位所生的十六种无漏心",
    "sect": "说一切有部"
  },
  {
    "id": "c097",
    "name": "见惑",
    "layer": "L3",
    "definition": "见道位所断的烦恼，共八十八使",
    "sect": "通途"
  },
  {
    "id": "c098",
    "name": "修惑",
    "layer": "L3",
    "definition": "修道位所断的烦恼，共八十一品",
    "sect": "通途"
  },
  {
    "id": "c099",
    "name": "习气",
    "layer": "L3",
    "definition": "烦恼断后残留的余习",
    "sect": "大乘通途"
  },
  {
    "id": "c100",
    "name": "无为法",
    "layer": "L3",
    "definition": "非因缘和合而生、无生灭变化的法",
    "sect": "通途"
  },
  {
    "id": "c101",
    "name": "八不中道",
    "layer": "L3",
    "definition": "不生亦不灭，不常亦不断，不一亦不异，不来亦不去，破一切边见",
    "sect": "三论宗"
  },
  {
    "id": "c102",
    "name": "二谛",
    "layer": "L3",
    "definition": "世俗谛和胜义谛：随顺世俗说有，依胜义说空",
    "sect": "三论宗"
  },
  {
    "id": "c103",
    "name": "缘起性空",
    "layer": "L3",
    "definition": "一切法皆由因缘生起，故无自性，无自性即是空",
    "sect": "三论宗"
  },
  {
    "id": "c104",
    "name": "性空幻有",
    "layer": "L3",
    "definition": "自性是空，但因缘所生的幻相宛然存在",
    "sect": "三论宗"
  },
  {
    "id": "c105",
    "name": "破邪显正",
    "layer": "L3",
    "definition": "三论宗方法论：破斥一切错误见解，真理自然显现",
    "sect": "三论宗"
  },
  {
    "id": "c106",
    "name": "四重二谛",
    "layer": "L3",
    "definition": "吉藏将二谛分为四层，层层递进，最终归于绝待",
    "sect": "三论宗"
  },
  {
    "id": "c107",
    "name": "于谛教谛",
    "layer": "L3",
    "definition": "于谛是于情为实，教谛是佛陀方便言教",
    "sect": "三论宗"
  },
  {
    "id": "c108",
    "name": "中道实相",
    "layer": "L3",
    "definition": "远离空有二边，即是诸法实相",
    "sect": "三论宗"
  },
  {
    "id": "c109",
    "name": "诸法无生",
    "layer": "L3",
    "definition": "一切法因缘生，自性无生",
    "sect": "三论宗"
  },
  {
    "id": "c110",
    "name": "毕竟空",
    "layer": "L3",
    "definition": "一切法究竟皆空，连空的概念也不可执著",
    "sect": "三论宗"
  },
  {
    "id": "c111",
    "name": "假名",
    "layer": "L3",
    "definition": "诸法因缘和合，只有假名施设，无有实体",
    "sect": "三论宗"
  },
  {
    "id": "c112",
    "name": "中观",
    "layer": "L3",
    "definition": "龙树菩萨创立的大乘学派，主张缘起性空、八不中道",
    "sect": "三论宗"
  },
  {
    "id": "c113",
    "name": "三论",
    "layer": "L3",
    "definition": "《中论》《百论》《十二门论》，三论宗所依根本经典",
    "sect": "三论宗"
  },
  {
    "id": "c114",
    "name": "二智",
    "layer": "L3",
    "definition": "根本智与后得智：根本智证真如，后得智度众生",
    "sect": "三论宗"
  },
  {
    "id": "c115",
    "name": "三是偈",
    "layer": "L3",
    "definition": "众因缘生法，我说即是空，亦为是假名，亦是中道义",
    "sect": "三论宗"
  },
  {
    "id": "c116",
    "name": "空亦复空",
    "layer": "L3",
    "definition": "不仅法是空，空这个概念本身也是空",
    "sect": "三论宗"
  },
  {
    "id": "c117",
    "name": "无所得",
    "layer": "L3",
    "definition": "三论宗修行旨归：于一切法无执著、无所得",
    "sect": "三论宗"
  },
  {
    "id": "c118",
    "name": "四句百非",
    "layer": "L3",
    "definition": "破斥一切有、无、亦有亦无、非有非无四句，穷尽一切戏论",
    "sect": "三论宗"
  },
  {
    "id": "c119",
    "name": "一异",
    "layer": "L3",
    "definition": "诸法是一是异的边见，为八不中道所破",
    "sect": "三论宗"
  },
  {
    "id": "c120",
    "name": "断常",
    "layer": "L3",
    "definition": "断见与常见两种极端边见",
    "sect": "三论宗"
  },
  {
    "id": "c121",
    "name": "生灭",
    "layer": "L3",
    "definition": "诸法有生有灭的妄见，为八不中道所破",
    "sect": "三论宗"
  },
  {
    "id": "c122",
    "name": "如来藏缘起",
    "layer": "L3",
    "definition": "一切法依如来藏而缘起",
    "sect": "如来藏系"
  },
  {
    "id": "c123",
    "name": "真如缘起",
    "layer": "L3",
    "definition": "一切法由真如随缘而生起",
    "sect": "大乘起信论"
  },
  {
    "id": "c124",
    "name": "一心二门",
    "layer": "L3",
    "definition": "《大乘起信论》核心：一心开真如门与生灭门",
    "sect": "大乘起信论"
  },
  {
    "id": "c125",
    "name": "阿黎耶识",
    "layer": "L3",
    "definition": "《大乘起信论》中与如来藏和合的阿赖耶识",
    "sect": "大乘起信论"
  },
  {
    "id": "c126",
    "name": "本觉",
    "layer": "L3",
    "definition": "众生本具的觉悟本性，不假修行",
    "sect": "大乘起信论"
  },
  {
    "id": "c127",
    "name": "三自性",
    "layer": "L3",
    "definition": "遍计所执性、依他起性、圆成实性，唯识宗核心理论",
    "sect": "唯识宗"
  },
  {
    "id": "c128",
    "name": "遍计所执性",
    "layer": "L3",
    "definition": "凡夫虚妄分别，执著诸法实有，如绳以为蛇",
    "sect": "唯识宗"
  },
  {
    "id": "c129",
    "name": "依他起性",
    "layer": "L3",
    "definition": "一切法依因缘而生起，如绳依麻等缘而有",
    "sect": "唯识宗"
  },
  {
    "id": "c130",
    "name": "圆成实性",
    "layer": "L3",
    "definition": "诸法的真实本性，即二空所显真如",
    "sect": "唯识宗"
  },
  {
    "id": "c131",
    "name": "三无性",
    "layer": "L3",
    "definition": "相无性、生无性、胜义无性，是对三自性的无性解说",
    "sect": "唯识宗"
  },
  {
    "id": "c132",
    "name": "五位百法",
    "layer": "L3",
    "definition": "唯识宗对一切法的分类：心法8、心所法51、色法11、心不相应行法24、无为法6",
    "sect": "唯识宗"
  },
  {
    "id": "c133",
    "name": "八识",
    "layer": "L3",
    "definition": "眼耳鼻舌身意六识、第七末那识、第八阿赖耶识",
    "sect": "唯识宗"
  },
  {
    "id": "c134",
    "name": "末那识",
    "layer": "L3",
    "definition": "第七识，恒审思量，执阿赖耶识为我",
    "sect": "唯识宗"
  },
  {
    "id": "c135",
    "name": "转识成智",
    "layer": "L3",
    "definition": "转有漏八识为无漏四智：成所作智、妙观察智、平等性智、大圆镜智",
    "sect": "唯识宗"
  },
  {
    "id": "c136",
    "name": "四智",
    "layer": "L3",
    "definition": "转前五识为成所作智，转第六识为妙观察智，转第七识为平等性智，转第八识为大圆镜智",
    "sect": "唯识宗"
  },
  {
    "id": "c137",
    "name": "种子生现行",
    "layer": "L3",
    "definition": "阿赖耶识中的种子生起现行诸法",
    "sect": "唯识宗"
  },
  {
    "id": "c138",
    "name": "现行熏种子",
    "layer": "L3",
    "definition": "现行诸法反过来熏习阿赖耶识，形成新种子",
    "sect": "唯识宗"
  },
  {
    "id": "c139",
    "name": "种现互生",
    "layer": "L3",
    "definition": "种子生现行，现行熏种子，刹那同时，因果同时",
    "sect": "唯识宗"
  },
  {
    "id": "c140",
    "name": "等流种子",
    "layer": "L3",
    "definition": "能生起同类果的种子",
    "sect": "唯识宗"
  },
  {
    "id": "c141",
    "name": "异熟种子",
    "layer": "L3",
    "definition": "能招感异熟果报的善恶业种子",
    "sect": "唯识宗"
  },
  {
    "id": "c142",
    "name": "习气种子",
    "layer": "L3",
    "definition": "由现行熏习而成的种子，即名言种子",
    "sect": "唯识宗"
  },
  {
    "id": "c143",
    "name": "我执",
    "layer": "L3",
    "definition": "执著有实我存在，为末那识所执",
    "sect": "唯识宗"
  },
  {
    "id": "c144",
    "name": "法执",
    "layer": "L3",
    "definition": "执著有实法存在",
    "sect": "唯识宗"
  },
  {
    "id": "c145",
    "name": "二障",
    "layer": "L3",
    "definition": "烦恼障与所知障，障碍解脱与菩提",
    "sect": "唯识宗"
  },
  {
    "id": "c146",
    "name": "烦恼障",
    "layer": "L3",
    "definition": "由我执生起的烦恼，障碍涅槃解脱",
    "sect": "唯识宗"
  },
  {
    "id": "c147",
    "name": "所知障",
    "layer": "L3",
    "definition": "由法执生起的障碍，障碍无上菩提",
    "sect": "唯识宗"
  },
  {
    "id": "c148",
    "name": "四分",
    "layer": "L3",
    "definition": "相分、见分、自证分、证自证分，唯识宗对认识结构的分析",
    "sect": "唯识宗"
  },
  {
    "id": "c149",
    "name": "相分",
    "layer": "L3",
    "definition": "认识时心中显现的影像相状",
    "sect": "唯识宗"
  },
  {
    "id": "c150",
    "name": "见分",
    "layer": "L3",
    "definition": "能缘虑、认识相分的作用",
    "sect": "唯识宗"
  },
  {
    "id": "c151",
    "name": "五重唯识观",
    "layer": "L3",
    "definition": "窥基大师提出的修行观法：遣虚存实识、舍滥留纯识、摄末归本识、隐劣显胜识、遣相证性识",
    "sect": "唯识宗"
  },
  {
    "id": "c152",
    "name": "唯识无境",
    "layer": "L3",
    "definition": "只有内在的心识，没有心外独立存在的外境",
    "sect": "唯识宗"
  },
  {
    "id": "c153",
    "name": "万法唯识",
    "layer": "L3",
    "definition": "宇宙万有皆是阿赖耶识所变现",
    "sect": "唯识宗"
  },
  {
    "id": "c154",
    "name": "三类境",
    "layer": "L3",
    "definition": "性境、独影境、带质境",
    "sect": "唯识宗"
  },
  {
    "id": "c155",
    "name": "性境",
    "layer": "L3",
    "definition": "有真实体性的境界，如前五识所缘的色声香味触",
    "sect": "唯识宗"
  },
  {
    "id": "c156",
    "name": "带质境",
    "layer": "L3",
    "definition": "缘有体法时兼带其相分的境界",
    "sect": "唯识宗"
  },
  {
    "id": "c157",
    "name": "三谛圆融",
    "layer": "L3",
    "definition": "空谛、假谛、中谛三谛互摄互融，一即三、三即一",
    "sect": "天台宗"
  },
  {
    "id": "c158",
    "name": "一心三观",
    "layer": "L3",
    "definition": "于一心中同时观照空、假、中三谛",
    "sect": "天台宗"
  },
  {
    "id": "c159",
    "name": "一念三千",
    "layer": "L3",
    "definition": "一念心中具足三千世间、三千诸法",
    "sect": "天台宗"
  },
  {
    "id": "c160",
    "name": "圆教",
    "layer": "L3",
    "definition": "天台宗判教中最究竟圆满的教法",
    "sect": "天台宗"
  },
  {
    "id": "c161",
    "name": "五时八教",
    "layer": "L3",
    "definition": "天台宗判教体系：华严时、阿含时、方等时、般若时、法华涅槃时；化仪四教、化法四教",
    "sect": "天台宗"
  },
  {
    "id": "c162",
    "name": "化法四教",
    "layer": "L3",
    "definition": "藏、通、别、圆四教，根据教法内容深浅划分",
    "sect": "天台宗"
  },
  {
    "id": "c163",
    "name": "化仪四教",
    "layer": "L3",
    "definition": "顿、渐、秘密、不定四教，根据佛陀说法形式划分",
    "sect": "天台宗"
  },
  {
    "id": "c164",
    "name": "性具善恶",
    "layer": "L3",
    "definition": "天台宗核心义理：佛性本具善、恶两种性德",
    "sect": "天台宗"
  },
  {
    "id": "c165",
    "name": "性具实相",
    "layer": "L3",
    "definition": "一切法自性本具，法尔自然即是实相",
    "sect": "天台宗"
  },
  {
    "id": "c166",
    "name": "十界互具",
    "layer": "L3",
    "definition": "十法界中每一界都互具其余九界",
    "sect": "天台宗"
  },
  {
    "id": "c167",
    "name": "十如是",
    "layer": "L3",
    "definition": "相、性、体、力、作、因、缘、果、报、本末究竟等，诸法本具的十种如是",
    "sect": "天台宗"
  },
  {
    "id": "c168",
    "name": "三世间",
    "layer": "L3",
    "definition": "五阴世间、众生世间、国土世间",
    "sect": "天台宗"
  },
  {
    "id": "c169",
    "name": "三千世间",
    "layer": "L3",
    "definition": "十界×十界×十如是×三世间=三千世间，一念具足",
    "sect": "天台宗"
  },
  {
    "id": "c170",
    "name": "六即佛",
    "layer": "L3",
    "definition": "理即佛、名字即佛、观行即佛、相似即佛、分证即佛、究竟即佛，修行成佛的六个阶位",
    "sect": "天台宗"
  },
  {
    "id": "c171",
    "name": "二十五方便",
    "layer": "L3",
    "definition": "天台宗止观修行前的二十五种预备方便",
    "sect": "天台宗"
  },
  {
    "id": "c172",
    "name": "止观",
    "layer": "L3",
    "definition": "天台宗核心修行方法：止是定，观是慧，止观双运",
    "sect": "天台宗"
  },
  {
    "id": "c173",
    "name": "圆顿止观",
    "layer": "L3",
    "definition": "天台宗圆教的止观，当下即观诸法实相，不历阶梯",
    "sect": "天台宗"
  },
  {
    "id": "c174",
    "name": "一念无明法性心",
    "layer": "L3",
    "definition": "一念心同时具足无明与法性",
    "sect": "天台宗"
  },
  {
    "id": "c175",
    "name": "无情有性",
    "layer": "L3",
    "definition": "不仅有情众生有佛性，无情草木瓦石也有佛性",
    "sect": "天台宗"
  },
  {
    "id": "c176",
    "name": "五重玄义",
    "layer": "L3",
    "definition": "天台宗解经体例：释名、辨体、明宗、论用、判教相",
    "sect": "天台宗"
  },
  {
    "id": "c177",
    "name": "法界缘起",
    "layer": "L3",
    "definition": "华严宗核心义理：以一真法界为本体，一切法互为缘起、重重无尽",
    "sect": "华严宗"
  },
  {
    "id": "c178",
    "name": "四法界",
    "layer": "L3",
    "definition": "事法界、理法界、理事无碍法界、事事无碍法界",
    "sect": "华严宗"
  },
  {
    "id": "c179",
    "name": "事法界",
    "layer": "L3",
    "definition": "差别事相的世界，一一事法各有差别",
    "sect": "华严宗"
  },
  {
    "id": "c180",
    "name": "理法界",
    "layer": "L3",
    "definition": "诸法平等的真如理体",
    "sect": "华严宗"
  },
  {
    "id": "c181",
    "name": "理事无碍",
    "layer": "L3",
    "definition": "理体与事相互相融摄，理不碍事、事不碍理",
    "sect": "华严宗"
  },
  {
    "id": "c182",
    "name": "事事无碍",
    "layer": "L3",
    "definition": "一一事法之间互相融通、相即相入、重重无尽",
    "sect": "华严宗"
  },
  {
    "id": "c183",
    "name": "六相圆融",
    "layer": "L3",
    "definition": "总相、别相、同相、异相、成相、坏相，六相互相融通，一法之中具六相",
    "sect": "华严宗"
  },
  {
    "id": "c184",
    "name": "十玄门",
    "layer": "L3",
    "definition": "华严宗事事无碍的十种玄妙门径，一即一切、一切即一",
    "sect": "华严宗"
  },
  {
    "id": "c185",
    "name": "一多相即",
    "layer": "L3",
    "definition": "一即多、多即一，相即相入",
    "sect": "华严宗"
  },
  {
    "id": "c186",
    "name": "因陀罗网",
    "layer": "L3",
    "definition": "帝释天宫殿中的宝珠网，珠珠相映，一珠现一切珠影，比喻重重无尽",
    "sect": "华严宗"
  },
  {
    "id": "c187",
    "name": "性起",
    "layer": "L3",
    "definition": "法性自然而起，一切法都是真如本性的显现",
    "sect": "华严宗"
  },
  {
    "id": "c188",
    "name": "五教十宗",
    "layer": "L3",
    "definition": "华严宗判教体系：小、始、终、顿、圆五教，分判佛教各宗派浅深",
    "sect": "华严宗"
  },
  {
    "id": "c189",
    "name": "六相",
    "layer": "L3",
    "definition": "总别同异成坏六相，华严宗观察诸法圆融的视角",
    "sect": "华严宗"
  },
  {
    "id": "c190",
    "name": "广狭自在",
    "layer": "L3",
    "definition": "十玄门之一，一法可摄一切法而不坏本位",
    "sect": "华严宗"
  },
  {
    "id": "c191",
    "name": "主伴圆明",
    "layer": "L3",
    "definition": "一法为主，一切法为伴，主伴交辉，圆满具足",
    "sect": "华严宗"
  },
  {
    "id": "c192",
    "name": "托事显法",
    "layer": "L3",
    "definition": "依托具体事相显发圆融佛法",
    "sect": "华严宗"
  },
  {
    "id": "c193",
    "name": "华严三圣",
    "layer": "L3",
    "definition": "毗卢遮那佛、文殊菩萨、普贤菩萨",
    "sect": "华严宗"
  },
  {
    "id": "c194",
    "name": "菩萨行位",
    "layer": "L3",
    "definition": "菩萨修行的五十二位：十信、十住、十行、十回向、十地、等觉、妙觉",
    "sect": "华严宗"
  },
  {
    "id": "c195",
    "name": "十地",
    "layer": "L3",
    "definition": "菩萨修行的十个阶位：欢喜地、离垢地、发光地、焰慧地、难胜地、现前地、远行地、不动地、善慧地、法云地",
    "sect": "华严宗"
  },
  {
    "id": "c196",
    "name": "圆融",
    "layer": "L3",
    "definition": "诸法互摄互入，不相妨碍",
    "sect": "华严宗"
  },
  {
    "id": "c197",
    "name": "明心见性",
    "layer": "L3",
    "definition": "禅宗核心：明了自心，见到本具佛性，当下成佛",
    "sect": "禅宗"
  },
  {
    "id": "c198",
    "name": "不立文字",
    "layer": "L3",
    "definition": "禅宗宗旨：以心传心，不依赖文字语言，教外别传",
    "sect": "禅宗"
  },
  {
    "id": "c199",
    "name": "教外别传",
    "layer": "L3",
    "definition": "禅宗自称是佛陀在经教之外单独传付的心印法门",
    "sect": "禅宗"
  },
  {
    "id": "c200",
    "name": "直指人心",
    "layer": "L3",
    "definition": "直接指示学人当下反观自心，见性成佛",
    "sect": "禅宗"
  },
  {
    "id": "c201",
    "name": "见性成佛",
    "layer": "L3",
    "definition": "见到自性本来面目，即是成佛",
    "sect": "禅宗"
  },
  {
    "id": "c202",
    "name": "本来面目",
    "layer": "L3",
    "definition": "众生本具的自性真心，未被烦恼污染的本来状态",
    "sect": "禅宗"
  },
  {
    "id": "c203",
    "name": "无念为宗",
    "layer": "L3",
    "definition": "六祖坛经核心：于念而无念，不被境转",
    "sect": "禅宗"
  },
  {
    "id": "c204",
    "name": "无相为体",
    "layer": "L3",
    "definition": "于相而离相，不执著事相",
    "sect": "禅宗"
  },
  {
    "id": "c205",
    "name": "无住为本",
    "layer": "L3",
    "definition": "于诸法上念念不住，心不执著",
    "sect": "禅宗"
  },
  {
    "id": "c206",
    "name": "顿悟",
    "layer": "L3",
    "definition": "禅宗南宗主张：无需渐次修行，当下明心见性，豁然开悟",
    "sect": "禅宗"
  },
  {
    "id": "c207",
    "name": "渐修",
    "layer": "L3",
    "definition": "禅宗北宗主张：通过渐次修行，逐步断惑证真",
    "sect": "禅宗"
  },
  {
    "id": "c208",
    "name": "公案",
    "layer": "L3",
    "definition": "禅宗祖师用以接引学人的机锋问答、机缘故事",
    "sect": "禅宗"
  },
  {
    "id": "c209",
    "name": "机锋",
    "layer": "L3",
    "definition": "禅师接引学人时含蓄锋利、不落痕迹的语言或动作",
    "sect": "禅宗"
  },
  {
    "id": "c210",
    "name": "棒喝",
    "layer": "L3",
    "definition": "德山棒、临济喝，禅师以极端手段打断学人情识分别",
    "sect": "禅宗"
  },
  {
    "id": "c211",
    "name": "平常心是道",
    "layer": "L3",
    "definition": "马祖道一提出：日常穿衣吃饭、运水搬柴皆是道",
    "sect": "禅宗"
  },
  {
    "id": "c212",
    "name": "信愿行",
    "layer": "L3",
    "definition": "净土宗三资粮：真信、切愿、持名念佛",
    "sect": "净土宗"
  },
  {
    "id": "c213",
    "name": "持名念佛",
    "layer": "L3",
    "definition": "念诵「南无阿弥陀佛」名号，求生西方极乐世界",
    "sect": "净土宗"
  },
  {
    "id": "c214",
    "name": "往生",
    "layer": "L3",
    "definition": "命终时蒙阿弥陀佛接引，往生西方极乐世界",
    "sect": "净土宗"
  },
  {
    "id": "c215",
    "name": "九品往生",
    "layer": "L3",
    "definition": "根据修行深浅，往生分三辈九品",
    "sect": "净土宗"
  },
  {
    "id": "c216",
    "name": "他力本愿",
    "layer": "L3",
    "definition": "依靠阿弥陀佛四十八大愿的他力救度，而非仅靠自力修行",
    "sect": "净土宗"
  }
],
  persons: [
  {
    "id": "p001",
    "class": "buddha",
    "name": "释迦牟尼佛"
  },
  {
    "id": "p002",
    "class": "buddha",
    "name": "阿弥陀佛"
  },
  {
    "id": "p003",
    "class": "buddha",
    "name": "药师佛"
  },
  {
    "id": "p004",
    "class": "buddha",
    "name": "毗卢遮那佛"
  },
  {
    "id": "p005",
    "class": "buddha",
    "name": "卢舍那佛"
  },
  {
    "id": "p006",
    "class": "buddha",
    "name": "燃灯佛"
  },
  {
    "id": "p007",
    "class": "buddha",
    "name": "弥勒佛"
  },
  {
    "id": "p008",
    "class": "buddha",
    "name": "不动佛"
  },
  {
    "id": "p009",
    "class": "buddha",
    "name": "宝生佛"
  },
  {
    "id": "p010",
    "class": "buddha",
    "name": "不空成就佛"
  },
  {
    "id": "p011",
    "class": "bodhisattva",
    "name": "文殊菩萨"
  },
  {
    "id": "p012",
    "class": "bodhisattva",
    "name": "普贤菩萨"
  },
  {
    "id": "p013",
    "class": "bodhisattva",
    "name": "观音菩萨"
  },
  {
    "id": "p014",
    "class": "bodhisattva",
    "name": "地藏菩萨"
  },
  {
    "id": "p015",
    "class": "bodhisattva",
    "name": "大势至菩萨"
  },
  {
    "id": "p016",
    "class": "bodhisattva",
    "name": "弥勒菩萨"
  },
  {
    "id": "p017",
    "class": "bodhisattva",
    "name": "虚空藏菩萨"
  },
  {
    "id": "p018",
    "class": "bodhisattva",
    "name": "除盖障菩萨"
  },
  {
    "id": "p019",
    "class": "bodhisattva",
    "name": "药王菩萨"
  },
  {
    "id": "p020",
    "class": "bodhisattva",
    "name": "韦驮菩萨"
  },
  {
    "id": "p021",
    "class": "bodhisattva",
    "name": "伽蓝菩萨"
  },
  {
    "id": "p022",
    "class": "bodhisattva",
    "name": "地藏王菩萨"
  },
  {
    "id": "p023",
    "class": "bodhisattva",
    "name": "文殊师利菩萨"
  },
  {
    "id": "p024",
    "class": "bodhisattva",
    "name": "普贤王菩萨"
  },
  {
    "id": "p025",
    "class": "bodhisattva",
    "name": "大势至菩萨"
  },
  {
    "id": "p026",
    "class": "arhat",
    "name": "大迦叶尊者"
  },
  {
    "id": "p027",
    "class": "arhat",
    "name": "阿难尊者"
  },
  {
    "id": "p028",
    "class": "arhat",
    "name": "舍利弗尊者"
  },
  {
    "id": "p029",
    "class": "arhat",
    "name": "目犍连尊者"
  },
  {
    "id": "p030",
    "class": "arhat",
    "name": "须菩提尊者"
  },
  {
    "id": "p031",
    "class": "arhat",
    "name": "富楼那尊者"
  },
  {
    "id": "p032",
    "class": "arhat",
    "name": "迦旃延尊者"
  },
  {
    "id": "p033",
    "class": "arhat",
    "name": "阿那律尊者"
  },
  {
    "id": "p034",
    "class": "arhat",
    "name": "优波离尊者"
  },
  {
    "id": "p035",
    "class": "arhat",
    "name": "罗睺罗尊者"
  },
  {
    "id": "p036",
    "class": "arhat",
    "name": "宾头卢尊者"
  },
  {
    "id": "p037",
    "class": "arhat",
    "name": "降龙罗汉"
  },
  {
    "id": "p038",
    "class": "arhat",
    "name": "伏虎罗汉"
  },
  {
    "id": "p039",
    "class": "arhat",
    "name": "十八罗汉"
  },
  {
    "id": "p040",
    "class": "arhat",
    "name": "五百罗汉"
  },
  {
    "id": "p041",
    "class": "master",
    "name": "安世高"
  },
  {
    "id": "p042",
    "class": "master",
    "name": "支娄迦谶"
  },
  {
    "id": "p043",
    "class": "master",
    "name": "支谦"
  },
  {
    "id": "p044",
    "class": "master",
    "name": "竺法护"
  },
  {
    "id": "p045",
    "class": "master",
    "name": "鸠摩罗什"
  },
  {
    "id": "p046",
    "class": "master",
    "name": "佛驮跋陀罗"
  },
  {
    "id": "p047",
    "class": "master",
    "name": "法显"
  },
  {
    "id": "p048",
    "class": "master",
    "name": "昙无谶"
  },
  {
    "id": "p049",
    "class": "master",
    "name": "菩提流支"
  },
  {
    "id": "p050",
    "class": "master",
    "name": "真谛"
  },
  {
    "id": "p051",
    "class": "master",
    "name": "达摩笈多"
  },
  {
    "id": "p052",
    "class": "master",
    "name": "玄奘法师"
  },
  {
    "id": "p053",
    "class": "master",
    "name": "义净法师"
  },
  {
    "id": "p054",
    "class": "master",
    "name": "实叉难陀"
  },
  {
    "id": "p055",
    "class": "master",
    "name": "善无畏"
  },
  {
    "id": "p056",
    "class": "master",
    "name": "金刚智"
  },
  {
    "id": "p057",
    "class": "master",
    "name": "不空三藏"
  },
  {
    "id": "p058",
    "class": "master",
    "name": "般若三藏"
  },
  {
    "id": "p059",
    "class": "master",
    "name": "法成法师"
  },
  {
    "id": "p060",
    "class": "master",
    "name": "施护法师"
  },
  {
    "id": "p061",
    "class": "master",
    "name": "道安法师"
  },
  {
    "id": "p062",
    "class": "master",
    "name": "慧远大师"
  },
  {
    "id": "p063",
    "class": "master",
    "name": "道生法师"
  },
  {
    "id": "p064",
    "class": "master",
    "name": "僧肇大师"
  },
  {
    "id": "p065",
    "class": "master",
    "name": "达摩祖师"
  },
  {
    "id": "p066",
    "class": "master",
    "name": "慧可大师"
  },
  {
    "id": "p067",
    "class": "master",
    "name": "僧璨大师"
  },
  {
    "id": "p068",
    "class": "master",
    "name": "道信大师"
  },
  {
    "id": "p069",
    "class": "master",
    "name": "弘忍大师"
  },
  {
    "id": "p070",
    "class": "master",
    "name": "神秀大师"
  },
  {
    "id": "p071",
    "class": "master",
    "name": "惠能大师"
  },
  {
    "id": "p072",
    "class": "master",
    "name": "吉藏大师"
  },
  {
    "id": "p073",
    "class": "master",
    "name": "智顗大师"
  },
  {
    "id": "p074",
    "class": "master",
    "name": "灌顶大师"
  },
  {
    "id": "p075",
    "class": "master",
    "name": "杜顺大师"
  },
  {
    "id": "p076",
    "class": "master",
    "name": "智俨大师"
  },
  {
    "id": "p077",
    "class": "master",
    "name": "法藏大师"
  },
  {
    "id": "p078",
    "class": "master",
    "name": "澄观大师"
  },
  {
    "id": "p079",
    "class": "master",
    "name": "宗密大师"
  },
  {
    "id": "p080",
    "class": "master",
    "name": "道宣律师"
  },
  {
    "id": "p081",
    "class": "master",
    "name": "善导大师"
  },
  {
    "id": "p082",
    "class": "master",
    "name": "窥基大师"
  },
  {
    "id": "p083",
    "class": "master",
    "name": "惠果阿阇梨"
  },
  {
    "id": "p084",
    "class": "master",
    "name": "一行禅师"
  },
  {
    "id": "p085",
    "class": "master",
    "name": "百丈怀海"
  },
  {
    "id": "p086",
    "class": "master",
    "name": "马祖道一"
  },
  {
    "id": "p087",
    "class": "master",
    "name": "临济义玄"
  },
  {
    "id": "p088",
    "class": "master",
    "name": "洞山良价"
  },
  {
    "id": "p089",
    "class": "master",
    "name": "永明延寿"
  },
  {
    "id": "p090",
    "class": "master",
    "name": "蕅益大师"
  },
  {
    "id": "p091",
    "class": "scholar",
    "name": "杨文会"
  },
  {
    "id": "p092",
    "class": "scholar",
    "name": "欧阳竟无"
  },
  {
    "id": "p093",
    "class": "scholar",
    "name": "太虚大师"
  },
  {
    "id": "p094",
    "class": "scholar",
    "name": "吕澂"
  },
  {
    "id": "p095",
    "class": "scholar",
    "name": "印顺法师"
  },
  {
    "id": "p096",
    "class": "scholar",
    "name": "汤用彤"
  },
  {
    "id": "p097",
    "class": "scholar",
    "name": "南怀瑾"
  },
  {
    "id": "p098",
    "class": "folk",
    "name": "济公活佛"
  },
  {
    "id": "p099",
    "class": "folk",
    "name": "布袋和尚"
  },
  {
    "id": "p100",
    "class": "scholar",
    "name": "彦琮法师"
  }
],
  sects: [
  {
    "id": "sect001",
    "name": "三论宗",
    "founder": "吉藏",
    "core_doctrine": "缘起性空，八不中道",
    "period": "隋代"
  },
  {
    "id": "sect002",
    "name": "天台宗",
    "founder": "智顗",
    "core_doctrine": "三谛圆融，一念三千",
    "period": "隋代"
  },
  {
    "id": "sect003",
    "name": "唯识宗",
    "founder": "玄奘/窥基",
    "core_doctrine": "万法唯识，转识成智",
    "period": "唐代"
  },
  {
    "id": "sect004",
    "name": "华严宗",
    "founder": "法藏",
    "core_doctrine": "法界缘起，六相圆融",
    "period": "唐代"
  },
  {
    "id": "sect005",
    "name": "禅宗",
    "founder": "达摩/惠能",
    "core_doctrine": "明心见性，不立文字",
    "period": "唐代"
  },
  {
    "id": "sect006",
    "name": "净土宗",
    "founder": "善导",
    "core_doctrine": "信愿念佛，往生净土",
    "period": "唐代"
  },
  {
    "id": "sect007",
    "name": "律宗",
    "founder": "道宣",
    "core_doctrine": "严持戒律，以戒为师",
    "period": "唐代"
  },
  {
    "id": "sect008",
    "name": "密宗",
    "founder": "善无畏/不空",
    "core_doctrine": "三密相应，即身成佛",
    "period": "唐代"
  }
],
  core_sutras: [
  {
    "id": "s001",
    "sutra_id": "t0001",
    "name": "长阿含经",
    "translator": "佛陀耶舍、竺佛念",
    "vol": "T01",
    "category": "阿含部"
  },
  {
    "id": "s002",
    "sutra_id": "t0026",
    "name": "中阿含经",
    "translator": "瞿昙僧伽提婆",
    "vol": "T01",
    "category": "阿含部"
  },
  {
    "id": "s003",
    "sutra_id": "t0099",
    "name": "杂阿含经",
    "translator": "求那跋陀罗",
    "vol": "T02",
    "category": "阿含部"
  },
  {
    "id": "s004",
    "sutra_id": "t0125",
    "name": "增一阿含经",
    "translator": "瞿昙僧伽提婆",
    "vol": "T02",
    "category": "阿含部"
  },
  {
    "id": "s005",
    "sutra_id": "t0001",
    "name": "四十二章经",
    "translator": "迦叶摩腾、竺法兰",
    "vol": "T17",
    "category": "阿含部"
  },
  {
    "id": "s006",
    "sutra_id": "t0110",
    "name": "八大人觉经",
    "translator": "安世高",
    "vol": "T17",
    "category": "阿含部"
  },
  {
    "id": "s007",
    "sutra_id": "t0001",
    "name": "佛遗教经",
    "translator": "鸠摩罗什",
    "vol": "T12",
    "category": "阿含部"
  },
  {
    "id": "s008",
    "sutra_id": "t0001",
    "name": "起世经",
    "translator": "阇那崛多",
    "vol": "T01",
    "category": "阿含部"
  },
  {
    "id": "s009",
    "sutra_id": "t0001",
    "name": "楞伽经",
    "translator": "求那跋陀罗",
    "vol": "T16",
    "category": "阿含部"
  },
  {
    "id": "s010",
    "sutra_id": "t0001",
    "name": "法句经",
    "translator": "维只难、竺将炎",
    "vol": "T04",
    "category": "阿含部"
  },
  {
    "id": "s011",
    "sutra_id": "t0220",
    "name": "大般若波罗蜜多经",
    "translator": "玄奘",
    "vol": "T05-T07",
    "category": "般若部"
  },
  {
    "id": "s012",
    "sutra_id": "t0221",
    "name": "放光般若经",
    "translator": "无罗叉、竺叔兰",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s013",
    "sutra_id": "t0223",
    "name": "摩诃般若波罗蜜经",
    "translator": "鸠摩罗什",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s014",
    "sutra_id": "t0235",
    "name": "金刚般若波罗蜜经",
    "translator": "鸠摩罗什",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s015",
    "sutra_id": "t0250",
    "name": "般若波罗蜜多心经",
    "translator": "玄奘",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s016",
    "sutra_id": "t0251",
    "name": "般若波罗蜜多心经",
    "translator": "鸠摩罗什",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s017",
    "sutra_id": "t0227",
    "name": "小品般若经",
    "translator": "鸠摩罗什",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s018",
    "sutra_id": "t0225",
    "name": "道行般若经",
    "translator": "支娄迦谶",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s019",
    "sutra_id": "t0236",
    "name": "仁王护国般若经",
    "translator": "鸠摩罗什",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s020",
    "sutra_id": "t0245",
    "name": "文殊师利所说摩诃般若波罗蜜经",
    "translator": "曼陀罗仙",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s021",
    "sutra_id": "t0246",
    "name": "般若波罗蜜多心经",
    "translator": "法月",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s022",
    "sutra_id": "t0247",
    "name": "般若波罗蜜多心经",
    "translator": "般若共利言",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s023",
    "sutra_id": "t0248",
    "name": "般若波罗蜜多心经",
    "translator": "智慧轮",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s024",
    "sutra_id": "t0249",
    "name": "般若波罗蜜多心经",
    "translator": "法成",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s025",
    "sutra_id": "t0252",
    "name": "般若波罗蜜多心经",
    "translator": "施护",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s026",
    "sutra_id": "t0232",
    "name": "金刚般若波罗蜜经",
    "translator": "菩提流支",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s027",
    "sutra_id": "t0233",
    "name": "金刚般若波罗蜜经",
    "translator": "真谛",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s028",
    "sutra_id": "t0234",
    "name": "金刚能断般若波罗蜜经",
    "translator": "达摩笈多",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s029",
    "sutra_id": "t0239",
    "name": "能断金刚般若波罗蜜多经",
    "translator": "玄奘",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s030",
    "sutra_id": "t0237",
    "name": "能断金刚般若波罗蜜多经",
    "translator": "义净",
    "vol": "T08",
    "category": "般若部"
  },
  {
    "id": "s031",
    "sutra_id": "t0262",
    "name": "妙法莲华经",
    "translator": "鸠摩罗什",
    "vol": "T09",
    "category": "法华部"
  },
  {
    "id": "s032",
    "sutra_id": "t0263",
    "name": "正法华经",
    "translator": "竺法护",
    "vol": "T09",
    "category": "法华部"
  },
  {
    "id": "s033",
    "sutra_id": "t0264",
    "name": "添品妙法莲华经",
    "translator": "阇那崛多、达摩笈多",
    "vol": "T09",
    "category": "法华部"
  },
  {
    "id": "s034",
    "sutra_id": "t0278",
    "name": "大方广佛华严经(六十华严)",
    "translator": "佛驮跋陀罗",
    "vol": "T09",
    "category": "华严部"
  },
  {
    "id": "s035",
    "sutra_id": "t0279",
    "name": "大方广佛华严经(八十华严)",
    "translator": "实叉难陀",
    "vol": "T10",
    "category": "华严部"
  },
  {
    "id": "s036",
    "sutra_id": "t0293",
    "name": "大方广佛华严经入不思议解脱境界普贤行愿品",
    "translator": "般若",
    "vol": "T10",
    "category": "华严部"
  },
  {
    "id": "s037",
    "sutra_id": "t0272",
    "name": "大方广圆觉修多罗了义经",
    "translator": "佛陀多罗",
    "vol": "T17",
    "category": "华严部"
  },
  {
    "id": "s038",
    "sutra_id": "t0266",
    "name": "维摩诘所说经",
    "translator": "鸠摩罗什",
    "vol": "T14",
    "category": "华严部"
  },
  {
    "id": "s039",
    "sutra_id": "t0265",
    "name": "维摩诘经",
    "translator": "支谦",
    "vol": "T14",
    "category": "华严部"
  },
  {
    "id": "s040",
    "sutra_id": "t0277",
    "name": "维摩诘所说经",
    "translator": "玄奘",
    "vol": "T14",
    "category": "华严部"
  },
  {
    "id": "s041",
    "sutra_id": "t0291",
    "name": "大方广如来秘密藏经",
    "translator": "法护",
    "vol": "T11",
    "category": "华严部"
  },
  {
    "id": "s042",
    "sutra_id": "t0275",
    "name": "楞伽阿跋多罗宝经",
    "translator": "求那跋陀罗",
    "vol": "T16",
    "category": "华严部"
  },
  {
    "id": "s043",
    "sutra_id": "t0276",
    "name": "入楞伽经",
    "translator": "菩提流支",
    "vol": "T16",
    "category": "华严部"
  },
  {
    "id": "s044",
    "sutra_id": "t0276a",
    "name": "大乘入楞伽经",
    "translator": "实叉难陀",
    "vol": "T16",
    "category": "华严部"
  },
  {
    "id": "s045",
    "sutra_id": "t0285",
    "name": "解深密经",
    "translator": "玄奘",
    "vol": "T16",
    "category": "华严部"
  },
  {
    "id": "s046",
    "sutra_id": "t0374",
    "name": "大般涅槃经(北本)",
    "translator": "昙无谶",
    "vol": "T12",
    "category": "涅槃部"
  },
  {
    "id": "s047",
    "sutra_id": "t0375",
    "name": "大般涅槃经(南本)",
    "translator": "慧严、慧观、谢灵运",
    "vol": "T12",
    "category": "涅槃部"
  },
  {
    "id": "s048",
    "sutra_id": "t0376",
    "name": "佛般泥洹经",
    "translator": "白法祖",
    "vol": "T01",
    "category": "涅槃部"
  },
  {
    "id": "s049",
    "sutra_id": "t0310",
    "name": "大宝积经",
    "translator": "菩提流志等",
    "vol": "T11",
    "category": "宝积部"
  },
  {
    "id": "s050",
    "sutra_id": "t0350",
    "name": "大方便佛报恩经",
    "translator": "失译",
    "vol": "T03",
    "category": "宝积部"
  },
  {
    "id": "s051",
    "sutra_id": "t0366",
    "name": "菩萨本缘经",
    "translator": "支谦",
    "vol": "T03",
    "category": "宝积部"
  },
  {
    "id": "s052",
    "sutra_id": "t0365",
    "name": "菩萨本生鬘论",
    "translator": "绍德、慧询等",
    "vol": "T03",
    "category": "宝积部"
  },
  {
    "id": "s053",
    "sutra_id": "t0412",
    "name": "金光明最胜王经",
    "translator": "义净",
    "vol": "T16",
    "category": "宝积部"
  },
  {
    "id": "s054",
    "sutra_id": "t0665",
    "name": "优婆塞戒经",
    "translator": "昙无谶",
    "vol": "T24",
    "category": "宝积部"
  },
  {
    "id": "s055",
    "sutra_id": "t0387",
    "name": "大方等大集经",
    "translator": "昙无谶等",
    "vol": "T13",
    "category": "宝积部"
  },
  {
    "id": "s056",
    "sutra_id": "t0402",
    "name": "地藏菩萨本愿经",
    "translator": "实叉难陀",
    "vol": "T13",
    "category": "大集部"
  },
  {
    "id": "s057",
    "sutra_id": "t0416",
    "name": "药师琉璃光如来本愿功德经",
    "translator": "玄奘",
    "vol": "T14",
    "category": "大集部"
  },
  {
    "id": "s058",
    "sutra_id": "t0450",
    "name": "佛说阿弥陀经",
    "translator": "鸠摩罗什",
    "vol": "T12",
    "category": "净土部"
  },
  {
    "id": "s059",
    "sutra_id": "t0451",
    "name": "称赞净土佛摄受经",
    "translator": "玄奘",
    "vol": "T12",
    "category": "净土部"
  },
  {
    "id": "s060",
    "sutra_id": "t0360",
    "name": "佛说无量寿经",
    "translator": "康僧铠",
    "vol": "T12",
    "category": "净土部"
  },
  {
    "id": "s061",
    "sutra_id": "t2008",
    "name": "六祖大师法宝坛经",
    "translator": "法海记录",
    "vol": "T48",
    "category": "禅宗部"
  },
  {
    "id": "s062",
    "sutra_id": "t2007",
    "name": "南宗顿教最上大乘摩诃般若波罗蜜经六祖惠能大师于韶州大梵寺施法坛经(敦煌本)",
    "translator": "法海记录",
    "vol": "T48",
    "category": "禅宗部"
  },
  {
    "id": "s063",
    "sutra_id": "t1509",
    "name": "中论",
    "translator": "鸠摩罗什",
    "vol": "T30",
    "category": "论部"
  },
  {
    "id": "s064",
    "sutra_id": "t1569",
    "name": "大智度论",
    "translator": "鸠摩罗什",
    "vol": "T25",
    "category": "论部"
  },
  {
    "id": "s065",
    "sutra_id": "t1565",
    "name": "成唯识论",
    "translator": "玄奘",
    "vol": "T31",
    "category": "论部"
  },
  {
    "id": "s066",
    "sutra_id": "t1585",
    "name": "瑜伽师地论",
    "translator": "玄奘",
    "vol": "T30",
    "category": "论部"
  },
  {
    "id": "s067",
    "sutra_id": "t1521",
    "name": "百论",
    "translator": "鸠摩罗什",
    "vol": "T30",
    "category": "论部"
  },
  {
    "id": "s068",
    "sutra_id": "t1522",
    "name": "十二门论",
    "translator": "鸠摩罗什",
    "vol": "T30",
    "category": "论部"
  },
  {
    "id": "s069",
    "sutra_id": "t1506",
    "name": "俱舍论",
    "translator": "玄奘",
    "vol": "T29",
    "category": "论部"
  },
  {
    "id": "s070",
    "sutra_id": "t1646",
    "name": "大乘起信论",
    "translator": "真谛",
    "vol": "T32",
    "category": "论部"
  },
  {
    "id": "s071",
    "sutra_id": "t1851",
    "name": "摩诃止观",
    "translator": "智顗说、灌顶记",
    "vol": "T46",
    "category": "论部"
  },
  {
    "id": "s072",
    "sutra_id": "t1816",
    "name": "华严经探玄记",
    "translator": "法藏",
    "vol": "T35",
    "category": "论部"
  },
  {
    "id": "s073",
    "sutra_id": "t1802",
    "name": "法华玄义",
    "translator": "智顗说、灌顶记",
    "vol": "T33",
    "category": "论部"
  },
  {
    "id": "s074",
    "sutra_id": "t1911",
    "name": "肇论",
    "translator": "僧肇",
    "vol": "T45",
    "category": "论部"
  },
  {
    "id": "s075",
    "sutra_id": "t1510",
    "name": "般若灯论释",
    "translator": "波罗颇蜜多罗",
    "vol": "T30",
    "category": "论部"
  },
  {
    "id": "s076",
    "sutra_id": "t0945",
    "name": "大佛顶如来密因修证了义诸菩萨万行首楞严经",
    "translator": "般剌蜜帝",
    "vol": "T19",
    "category": "密教部"
  },
  {
    "id": "s077",
    "sutra_id": "t0848",
    "name": "大毗卢遮那成佛神变加持经",
    "translator": "善无畏、一行",
    "vol": "T18",
    "category": "密教部"
  },
  {
    "id": "s078",
    "sutra_id": "t0865",
    "name": "金刚顶一切如来真实摄大乘现证大教王经",
    "translator": "不空",
    "vol": "T18",
    "category": "密教部"
  },
  {
    "id": "s079",
    "sutra_id": "t1425",
    "name": "四分律",
    "translator": "佛陀耶舍、竺佛念",
    "vol": "T22",
    "category": "律部"
  },
  {
    "id": "s080",
    "sutra_id": "t1488",
    "name": "梵网经卢舍那佛说菩萨心地戒品第十",
    "translator": "鸠摩罗什",
    "vol": "T24",
    "category": "律部"
  },
  {
    "id": "s081",
    "sutra_id": "t0366",
    "name": "观无量寿佛经",
    "translator": "畺良耶舍",
    "vol": "T12",
    "category": "净土部"
  },
  {
    "id": "s082",
    "sutra_id": "t0415",
    "name": "佛说弥勒上生经",
    "translator": "沮渠京声",
    "vol": "T14",
    "category": "净土部"
  },
  {
    "id": "s083",
    "sutra_id": "t0453",
    "name": "佛说弥勒大成佛经",
    "translator": "鸠摩罗什",
    "vol": "T14",
    "category": "净土部"
  },
  {
    "id": "s084",
    "sutra_id": "t0475",
    "name": "佛说盂兰盆经",
    "translator": "竺法护",
    "vol": "T16",
    "category": "经集部"
  },
  {
    "id": "s085",
    "sutra_id": "t0474",
    "name": "佛说父母恩难报经",
    "translator": "安世高",
    "vol": "T16",
    "category": "经集部"
  },
  {
    "id": "s086",
    "sutra_id": "t0685",
    "name": "佛说十善业道经",
    "translator": "实叉难陀",
    "vol": "T15",
    "category": "经集部"
  },
  {
    "id": "s087",
    "sutra_id": "t0666",
    "name": "优婆夷戒经",
    "translator": "失译",
    "vol": "T24",
    "category": "律部"
  },
  {
    "id": "s088",
    "sutra_id": "t1442",
    "name": "五分律",
    "translator": "佛陀什、竺道生",
    "vol": "T22",
    "category": "律部"
  },
  {
    "id": "s089",
    "sutra_id": "t1428",
    "name": "十诵律",
    "translator": "弗若多罗、鸠摩罗什",
    "vol": "T23",
    "category": "律部"
  },
  {
    "id": "s090",
    "sutra_id": "t1421",
    "name": "摩诃僧祇律",
    "translator": "佛陀跋陀罗、法显",
    "vol": "T22",
    "category": "律部"
  },
  {
    "id": "s091",
    "sutra_id": "t1804",
    "name": "观无量寿佛经疏",
    "translator": "善导",
    "vol": "T37",
    "category": "论部"
  },
  {
    "id": "s092",
    "sutra_id": "t1985",
    "name": "往生论注",
    "translator": "昙鸾",
    "vol": "T40",
    "category": "论部"
  },
  {
    "id": "s093",
    "sutra_id": "t0585",
    "name": "佛说观普贤菩萨行法经",
    "translator": "昙摩密多",
    "vol": "T09",
    "category": "法华部"
  },
  {
    "id": "s094",
    "sutra_id": "t0273",
    "name": "大方广圆觉经",
    "translator": "佛陀多罗",
    "vol": "T17",
    "category": "华严部"
  },
  {
    "id": "s095",
    "sutra_id": "t0428",
    "name": "佛说大乘圣无量寿决定光明王如来陀罗尼经",
    "translator": "法天",
    "vol": "T19",
    "category": "密教部"
  },
  {
    "id": "s096",
    "sutra_id": "t1331",
    "name": "佛顶尊胜陀罗尼经",
    "translator": "佛陀波利",
    "vol": "T19",
    "category": "密教部"
  },
  {
    "id": "s097",
    "sutra_id": "t1083",
    "name": "千手千眼观世音菩萨广大圆满无碍大悲心陀罗尼经",
    "translator": "伽梵达摩",
    "vol": "T20",
    "category": "密教部"
  },
  {
    "id": "s098",
    "sutra_id": "t1430",
    "name": "梵网经",
    "translator": "鸠摩罗什",
    "vol": "T24",
    "category": "律部"
  },
  {
    "id": "s099",
    "sutra_id": "t2035",
    "name": "禅源诸诠集都序",
    "translator": "宗密",
    "vol": "T48",
    "category": "禅宗部"
  },
  {
    "id": "s100",
    "sutra_id": "t2024",
    "name": "六祖坛经",
    "translator": "宗宝编",
    "vol": "T48",
    "category": "禅宗部"
  }
],
  relations: [
  {
    "id": "r001",
    "source": "c007",
    "target": "c026",
    "relation": "摄属"
  },
  {
    "id": "r002",
    "source": "c012",
    "target": "c028",
    "relation": "摄属"
  },
  {
    "id": "r003",
    "source": "c013",
    "target": "c024",
    "relation": "摄属"
  },
  {
    "id": "r004",
    "source": "c016",
    "target": "c059",
    "relation": "摄属"
  },
  {
    "id": "r005",
    "source": "c017",
    "target": "c042",
    "relation": "摄属"
  },
  {
    "id": "r006",
    "source": "c018",
    "target": "c025",
    "relation": "摄属"
  },
  {
    "id": "r007",
    "source": "c019",
    "target": "c023",
    "relation": "摄属"
  },
  {
    "id": "r008",
    "source": "c020",
    "target": "c050",
    "relation": "摄属"
  },
  {
    "id": "r009",
    "source": "c021",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r010",
    "source": "c021",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r011",
    "source": "c021",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r012",
    "source": "c021",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r013",
    "source": "c021",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r014",
    "source": "c021",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r015",
    "source": "c021",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r016",
    "source": "c021",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r017",
    "source": "c021",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r018",
    "source": "c021",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r019",
    "source": "c021",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r020",
    "source": "c021",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r021",
    "source": "c021",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r022",
    "source": "c021",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r023",
    "source": "c021",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r024",
    "source": "c022",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r025",
    "source": "c022",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r026",
    "source": "c022",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r027",
    "source": "c022",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r028",
    "source": "c022",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r029",
    "source": "c022",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r030",
    "source": "c022",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r031",
    "source": "c022",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r032",
    "source": "c022",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r033",
    "source": "c022",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r034",
    "source": "c022",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r035",
    "source": "c022",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r036",
    "source": "c022",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r037",
    "source": "c022",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r038",
    "source": "c022",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r039",
    "source": "c023",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r040",
    "source": "c023",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r041",
    "source": "c023",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r042",
    "source": "c023",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r043",
    "source": "c023",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r044",
    "source": "c023",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r045",
    "source": "c023",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r046",
    "source": "c023",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r047",
    "source": "c023",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r048",
    "source": "c023",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r049",
    "source": "c023",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r050",
    "source": "c023",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r051",
    "source": "c023",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r052",
    "source": "c023",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r053",
    "source": "c023",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r054",
    "source": "c024",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r055",
    "source": "c024",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r056",
    "source": "c024",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r057",
    "source": "c024",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r058",
    "source": "c024",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r059",
    "source": "c024",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r060",
    "source": "c024",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r061",
    "source": "c024",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r062",
    "source": "c024",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r063",
    "source": "c024",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r064",
    "source": "c024",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r065",
    "source": "c024",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r066",
    "source": "c024",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r067",
    "source": "c024",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r068",
    "source": "c024",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r069",
    "source": "c025",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r070",
    "source": "c025",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r071",
    "source": "c025",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r072",
    "source": "c025",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r073",
    "source": "c025",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r074",
    "source": "c025",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r075",
    "source": "c025",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r076",
    "source": "c025",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r077",
    "source": "c025",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r078",
    "source": "c025",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r079",
    "source": "c025",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r080",
    "source": "c025",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r081",
    "source": "c025",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r082",
    "source": "c025",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r083",
    "source": "c025",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r084",
    "source": "c026",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r085",
    "source": "c026",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r086",
    "source": "c026",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r087",
    "source": "c026",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r088",
    "source": "c026",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r089",
    "source": "c026",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r090",
    "source": "c026",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r091",
    "source": "c026",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r092",
    "source": "c026",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r093",
    "source": "c026",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r094",
    "source": "c026",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r095",
    "source": "c026",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r096",
    "source": "c026",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r097",
    "source": "c026",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r098",
    "source": "c026",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r099",
    "source": "c027",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r100",
    "source": "c027",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r101",
    "source": "c027",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r102",
    "source": "c027",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r103",
    "source": "c027",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r104",
    "source": "c027",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r105",
    "source": "c027",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r106",
    "source": "c027",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r107",
    "source": "c027",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r108",
    "source": "c027",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r109",
    "source": "c027",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r110",
    "source": "c027",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r111",
    "source": "c027",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r112",
    "source": "c027",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r113",
    "source": "c027",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r114",
    "source": "c028",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r115",
    "source": "c028",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r116",
    "source": "c028",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r117",
    "source": "c028",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r118",
    "source": "c029",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r119",
    "source": "c029",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r120",
    "source": "c029",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r121",
    "source": "c029",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r122",
    "source": "c029",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r123",
    "source": "c029",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r124",
    "source": "c029",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r125",
    "source": "c029",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r126",
    "source": "c029",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r127",
    "source": "c029",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r128",
    "source": "c029",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r129",
    "source": "c029",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r130",
    "source": "c029",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r131",
    "source": "c029",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r132",
    "source": "c029",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r133",
    "source": "c030",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r134",
    "source": "c030",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r135",
    "source": "c030",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r136",
    "source": "c030",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r137",
    "source": "c030",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r138",
    "source": "c030",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r139",
    "source": "c030",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r140",
    "source": "c030",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r141",
    "source": "c030",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r142",
    "source": "c030",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r143",
    "source": "c030",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r144",
    "source": "c030",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r145",
    "source": "c030",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r146",
    "source": "c030",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r147",
    "source": "c030",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r148",
    "source": "c031",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r149",
    "source": "c031",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r150",
    "source": "c031",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r151",
    "source": "c031",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r152",
    "source": "c031",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r153",
    "source": "c031",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r154",
    "source": "c031",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r155",
    "source": "c031",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r156",
    "source": "c031",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r157",
    "source": "c031",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r158",
    "source": "c031",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r159",
    "source": "c031",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r160",
    "source": "c031",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r161",
    "source": "c031",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r162",
    "source": "c031",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r163",
    "source": "c032",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r164",
    "source": "c032",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r165",
    "source": "c032",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r166",
    "source": "c032",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r167",
    "source": "c032",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r168",
    "source": "c032",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r169",
    "source": "c032",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r170",
    "source": "c032",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r171",
    "source": "c032",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r172",
    "source": "c032",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r173",
    "source": "c032",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r174",
    "source": "c032",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r175",
    "source": "c032",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r176",
    "source": "c032",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r177",
    "source": "c032",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r178",
    "source": "c033",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r179",
    "source": "c033",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r180",
    "source": "c033",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r181",
    "source": "c033",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r182",
    "source": "c033",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r183",
    "source": "c033",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r184",
    "source": "c033",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r185",
    "source": "c033",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r186",
    "source": "c033",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r187",
    "source": "c033",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r188",
    "source": "c033",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r189",
    "source": "c033",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r190",
    "source": "c033",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r191",
    "source": "c033",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r192",
    "source": "c033",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r193",
    "source": "c034",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r194",
    "source": "c034",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r195",
    "source": "c034",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r196",
    "source": "c034",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r197",
    "source": "c034",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r198",
    "source": "c034",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r199",
    "source": "c034",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r200",
    "source": "c034",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r201",
    "source": "c034",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r202",
    "source": "c034",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r203",
    "source": "c034",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r204",
    "source": "c034",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r205",
    "source": "c034",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r206",
    "source": "c034",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r207",
    "source": "c034",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r208",
    "source": "c035",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r209",
    "source": "c035",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r210",
    "source": "c035",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r211",
    "source": "c035",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r212",
    "source": "c035",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r213",
    "source": "c035",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r214",
    "source": "c035",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r215",
    "source": "c035",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r216",
    "source": "c035",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r217",
    "source": "c035",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r218",
    "source": "c035",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r219",
    "source": "c035",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r220",
    "source": "c035",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r221",
    "source": "c035",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r222",
    "source": "c035",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r223",
    "source": "c036",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r224",
    "source": "c036",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r225",
    "source": "c036",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r226",
    "source": "c036",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r227",
    "source": "c036",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r228",
    "source": "c036",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r229",
    "source": "c036",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r230",
    "source": "c036",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r231",
    "source": "c036",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r232",
    "source": "c036",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r233",
    "source": "c036",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r234",
    "source": "c036",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r235",
    "source": "c036",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r236",
    "source": "c036",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r237",
    "source": "c036",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r238",
    "source": "c037",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r239",
    "source": "c037",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r240",
    "source": "c037",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r241",
    "source": "c037",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r242",
    "source": "c037",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r243",
    "source": "c037",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r244",
    "source": "c037",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r245",
    "source": "c037",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r246",
    "source": "c037",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r247",
    "source": "c037",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r248",
    "source": "c037",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r249",
    "source": "c037",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r250",
    "source": "c037",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r251",
    "source": "c037",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r252",
    "source": "c037",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r253",
    "source": "c038",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r254",
    "source": "c038",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r255",
    "source": "c038",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r256",
    "source": "c038",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r257",
    "source": "c038",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r258",
    "source": "c038",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r259",
    "source": "c038",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r260",
    "source": "c038",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r261",
    "source": "c038",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r262",
    "source": "c038",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r263",
    "source": "c038",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r264",
    "source": "c038",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r265",
    "source": "c038",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r266",
    "source": "c038",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r267",
    "source": "c038",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r268",
    "source": "c039",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r269",
    "source": "c039",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r270",
    "source": "c039",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r271",
    "source": "c039",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r272",
    "source": "c039",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r273",
    "source": "c039",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r274",
    "source": "c039",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r275",
    "source": "c039",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r276",
    "source": "c039",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r277",
    "source": "c039",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r278",
    "source": "c039",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r279",
    "source": "c039",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r280",
    "source": "c039",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r281",
    "source": "c039",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r282",
    "source": "c039",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r283",
    "source": "c040",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r284",
    "source": "c040",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r285",
    "source": "c040",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r286",
    "source": "c040",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r287",
    "source": "c040",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r288",
    "source": "c040",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r289",
    "source": "c040",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r290",
    "source": "c040",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r291",
    "source": "c040",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r292",
    "source": "c040",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r293",
    "source": "c040",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r294",
    "source": "c040",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r295",
    "source": "c040",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r296",
    "source": "c040",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r297",
    "source": "c040",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r298",
    "source": "c041",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r299",
    "source": "c041",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r300",
    "source": "c041",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r301",
    "source": "c041",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r302",
    "source": "c041",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r303",
    "source": "c041",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r304",
    "source": "c041",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r305",
    "source": "c041",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r306",
    "source": "c041",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r307",
    "source": "c041",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r308",
    "source": "c041",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r309",
    "source": "c041",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r310",
    "source": "c041",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r311",
    "source": "c041",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r312",
    "source": "c041",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r313",
    "source": "c042",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r314",
    "source": "c042",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r315",
    "source": "c042",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r316",
    "source": "c042",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r317",
    "source": "c042",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r318",
    "source": "c042",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r319",
    "source": "c042",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r320",
    "source": "c042",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r321",
    "source": "c042",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r322",
    "source": "c042",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r323",
    "source": "c042",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r324",
    "source": "c042",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r325",
    "source": "c042",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r326",
    "source": "c042",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r327",
    "source": "c042",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r328",
    "source": "c043",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r329",
    "source": "c043",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r330",
    "source": "c043",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r331",
    "source": "c043",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r332",
    "source": "c043",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r333",
    "source": "c043",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r334",
    "source": "c043",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r335",
    "source": "c043",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r336",
    "source": "c043",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r337",
    "source": "c043",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r338",
    "source": "c043",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r339",
    "source": "c043",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r340",
    "source": "c043",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r341",
    "source": "c043",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r342",
    "source": "c043",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r343",
    "source": "c044",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r344",
    "source": "c044",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r345",
    "source": "c044",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r346",
    "source": "c044",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r347",
    "source": "c044",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r348",
    "source": "c044",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r349",
    "source": "c044",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r350",
    "source": "c044",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r351",
    "source": "c044",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r352",
    "source": "c044",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r353",
    "source": "c044",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r354",
    "source": "c044",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r355",
    "source": "c044",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r356",
    "source": "c044",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r357",
    "source": "c044",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r358",
    "source": "c045",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r359",
    "source": "c045",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r360",
    "source": "c045",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r361",
    "source": "c045",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r362",
    "source": "c045",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r363",
    "source": "c045",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r364",
    "source": "c045",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r365",
    "source": "c045",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r366",
    "source": "c045",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r367",
    "source": "c045",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r368",
    "source": "c045",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r369",
    "source": "c045",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r370",
    "source": "c045",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r371",
    "source": "c045",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r372",
    "source": "c045",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r373",
    "source": "c046",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r374",
    "source": "c046",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r375",
    "source": "c046",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r376",
    "source": "c046",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r377",
    "source": "c046",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r378",
    "source": "c046",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r379",
    "source": "c046",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r380",
    "source": "c046",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r381",
    "source": "c046",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r382",
    "source": "c046",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r383",
    "source": "c046",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r384",
    "source": "c046",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r385",
    "source": "c046",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r386",
    "source": "c046",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r387",
    "source": "c046",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r388",
    "source": "c047",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r389",
    "source": "c047",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r390",
    "source": "c047",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r391",
    "source": "c047",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r392",
    "source": "c047",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r393",
    "source": "c047",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r394",
    "source": "c047",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r395",
    "source": "c047",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r396",
    "source": "c047",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r397",
    "source": "c047",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r398",
    "source": "c047",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r399",
    "source": "c047",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r400",
    "source": "c047",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r401",
    "source": "c047",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r402",
    "source": "c047",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r403",
    "source": "c048",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r404",
    "source": "c048",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r405",
    "source": "c048",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r406",
    "source": "c048",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r407",
    "source": "c048",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r408",
    "source": "c048",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r409",
    "source": "c048",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r410",
    "source": "c048",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r411",
    "source": "c048",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r412",
    "source": "c048",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r413",
    "source": "c048",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r414",
    "source": "c048",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r415",
    "source": "c048",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r416",
    "source": "c048",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r417",
    "source": "c048",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r418",
    "source": "c049",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r419",
    "source": "c049",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r420",
    "source": "c049",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r421",
    "source": "c049",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r422",
    "source": "c049",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r423",
    "source": "c049",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r424",
    "source": "c049",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r425",
    "source": "c049",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r426",
    "source": "c049",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r427",
    "source": "c049",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r428",
    "source": "c049",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r429",
    "source": "c049",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r430",
    "source": "c049",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r431",
    "source": "c049",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r432",
    "source": "c049",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r433",
    "source": "c050",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r434",
    "source": "c050",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r435",
    "source": "c050",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r436",
    "source": "c050",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r437",
    "source": "c050",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r438",
    "source": "c050",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r439",
    "source": "c050",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r440",
    "source": "c050",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r441",
    "source": "c050",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r442",
    "source": "c050",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r443",
    "source": "c050",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r444",
    "source": "c050",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r445",
    "source": "c050",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r446",
    "source": "c050",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r447",
    "source": "c050",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r448",
    "source": "c051",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r449",
    "source": "c051",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r450",
    "source": "c051",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r451",
    "source": "c051",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r452",
    "source": "c051",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r453",
    "source": "c051",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r454",
    "source": "c051",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r455",
    "source": "c051",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r456",
    "source": "c051",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r457",
    "source": "c051",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r458",
    "source": "c051",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r459",
    "source": "c051",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r460",
    "source": "c051",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r461",
    "source": "c051",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r462",
    "source": "c051",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r463",
    "source": "c052",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r464",
    "source": "c052",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r465",
    "source": "c052",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r466",
    "source": "c052",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r467",
    "source": "c052",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r468",
    "source": "c052",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r469",
    "source": "c052",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r470",
    "source": "c052",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r471",
    "source": "c052",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r472",
    "source": "c052",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r473",
    "source": "c052",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r474",
    "source": "c052",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r475",
    "source": "c052",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r476",
    "source": "c052",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r477",
    "source": "c052",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r478",
    "source": "c053",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r479",
    "source": "c053",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r480",
    "source": "c053",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r481",
    "source": "c053",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r482",
    "source": "c053",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r483",
    "source": "c053",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r484",
    "source": "c053",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r485",
    "source": "c053",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r486",
    "source": "c053",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r487",
    "source": "c053",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r488",
    "source": "c053",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r489",
    "source": "c053",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r490",
    "source": "c053",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r491",
    "source": "c053",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r492",
    "source": "c053",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r493",
    "source": "c054",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r494",
    "source": "c054",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r495",
    "source": "c054",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r496",
    "source": "c054",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r497",
    "source": "c054",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r498",
    "source": "c054",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r499",
    "source": "c054",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r500",
    "source": "c054",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r501",
    "source": "c054",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r502",
    "source": "c054",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r503",
    "source": "c054",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r504",
    "source": "c054",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r505",
    "source": "c054",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r506",
    "source": "c054",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r507",
    "source": "c054",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r508",
    "source": "c055",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r509",
    "source": "c055",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r510",
    "source": "c055",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r511",
    "source": "c055",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r512",
    "source": "c056",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r513",
    "source": "c056",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r514",
    "source": "c056",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r515",
    "source": "c056",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r516",
    "source": "c057",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r517",
    "source": "c057",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r518",
    "source": "c057",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r519",
    "source": "c057",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r520",
    "source": "c057",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r521",
    "source": "c057",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r522",
    "source": "c057",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r523",
    "source": "c057",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r524",
    "source": "c057",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r525",
    "source": "c057",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r526",
    "source": "c057",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r527",
    "source": "c057",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r528",
    "source": "c057",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r529",
    "source": "c057",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r530",
    "source": "c057",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r531",
    "source": "c058",
    "target": "c072",
    "relation": "细分"
  },
  {
    "id": "r532",
    "source": "c058",
    "target": "c073",
    "relation": "细分"
  },
  {
    "id": "r533",
    "source": "c058",
    "target": "c074",
    "relation": "细分"
  },
  {
    "id": "r534",
    "source": "c058",
    "target": "c075",
    "relation": "细分"
  },
  {
    "id": "r535",
    "source": "c058",
    "target": "c076",
    "relation": "细分"
  },
  {
    "id": "r536",
    "source": "c058",
    "target": "c077",
    "relation": "细分"
  },
  {
    "id": "r537",
    "source": "c058",
    "target": "c096",
    "relation": "细分"
  },
  {
    "id": "r538",
    "source": "c059",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r539",
    "source": "c059",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r540",
    "source": "c059",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r541",
    "source": "c059",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r542",
    "source": "c059",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r543",
    "source": "c059",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r544",
    "source": "c059",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r545",
    "source": "c059",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r546",
    "source": "c059",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r547",
    "source": "c059",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r548",
    "source": "c059",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r549",
    "source": "c059",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r550",
    "source": "c059",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r551",
    "source": "c059",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r552",
    "source": "c059",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r553",
    "source": "c060",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r554",
    "source": "c060",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r555",
    "source": "c060",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r556",
    "source": "c060",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r557",
    "source": "c060",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r558",
    "source": "c060",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r559",
    "source": "c060",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r560",
    "source": "c060",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r561",
    "source": "c060",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r562",
    "source": "c060",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r563",
    "source": "c060",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r564",
    "source": "c060",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r565",
    "source": "c060",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r566",
    "source": "c060",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r567",
    "source": "c060",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r568",
    "source": "c061",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r569",
    "source": "c061",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r570",
    "source": "c061",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r571",
    "source": "c061",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r572",
    "source": "c061",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r573",
    "source": "c061",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r574",
    "source": "c061",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r575",
    "source": "c061",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r576",
    "source": "c061",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r577",
    "source": "c061",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r578",
    "source": "c061",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r579",
    "source": "c061",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r580",
    "source": "c061",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r581",
    "source": "c061",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r582",
    "source": "c061",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r583",
    "source": "c062",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r584",
    "source": "c062",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r585",
    "source": "c062",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r586",
    "source": "c062",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r587",
    "source": "c062",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r588",
    "source": "c062",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r589",
    "source": "c062",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r590",
    "source": "c062",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r591",
    "source": "c062",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r592",
    "source": "c062",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r593",
    "source": "c062",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r594",
    "source": "c062",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r595",
    "source": "c062",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r596",
    "source": "c062",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r597",
    "source": "c062",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r598",
    "source": "c063",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r599",
    "source": "c063",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r600",
    "source": "c063",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r601",
    "source": "c063",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r602",
    "source": "c063",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r603",
    "source": "c063",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r604",
    "source": "c063",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r605",
    "source": "c063",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r606",
    "source": "c063",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r607",
    "source": "c063",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r608",
    "source": "c063",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r609",
    "source": "c063",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r610",
    "source": "c063",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r611",
    "source": "c063",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r612",
    "source": "c063",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r613",
    "source": "c064",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r614",
    "source": "c064",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r615",
    "source": "c064",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r616",
    "source": "c064",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r617",
    "source": "c064",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r618",
    "source": "c064",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r619",
    "source": "c064",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r620",
    "source": "c064",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r621",
    "source": "c064",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r622",
    "source": "c064",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r623",
    "source": "c064",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r624",
    "source": "c064",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r625",
    "source": "c064",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r626",
    "source": "c064",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r627",
    "source": "c064",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r628",
    "source": "c065",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r629",
    "source": "c065",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r630",
    "source": "c065",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r631",
    "source": "c065",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r632",
    "source": "c065",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r633",
    "source": "c065",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r634",
    "source": "c065",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r635",
    "source": "c065",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r636",
    "source": "c065",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r637",
    "source": "c065",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r638",
    "source": "c065",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r639",
    "source": "c065",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r640",
    "source": "c065",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r641",
    "source": "c065",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r642",
    "source": "c065",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r643",
    "source": "c066",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r644",
    "source": "c066",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r645",
    "source": "c066",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r646",
    "source": "c066",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r647",
    "source": "c067",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r648",
    "source": "c067",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r649",
    "source": "c067",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r650",
    "source": "c067",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r651",
    "source": "c067",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r652",
    "source": "c067",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r653",
    "source": "c067",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r654",
    "source": "c067",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r655",
    "source": "c067",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r656",
    "source": "c067",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r657",
    "source": "c067",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r658",
    "source": "c067",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r659",
    "source": "c067",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r660",
    "source": "c067",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r661",
    "source": "c067",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r662",
    "source": "c068",
    "target": "c212",
    "relation": "细分"
  },
  {
    "id": "r663",
    "source": "c068",
    "target": "c213",
    "relation": "细分"
  },
  {
    "id": "r664",
    "source": "c068",
    "target": "c214",
    "relation": "细分"
  },
  {
    "id": "r665",
    "source": "c068",
    "target": "c215",
    "relation": "细分"
  },
  {
    "id": "r666",
    "source": "c068",
    "target": "c216",
    "relation": "细分"
  },
  {
    "id": "r667",
    "source": "c069",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r668",
    "source": "c069",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r669",
    "source": "c069",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r670",
    "source": "c069",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r671",
    "source": "c069",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r672",
    "source": "c069",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r673",
    "source": "c069",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r674",
    "source": "c069",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r675",
    "source": "c069",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r676",
    "source": "c069",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r677",
    "source": "c069",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r678",
    "source": "c069",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r679",
    "source": "c069",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r680",
    "source": "c069",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r681",
    "source": "c069",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r682",
    "source": "c070",
    "target": "c078",
    "relation": "细分"
  },
  {
    "id": "r683",
    "source": "c070",
    "target": "c079",
    "relation": "细分"
  },
  {
    "id": "r684",
    "source": "c070",
    "target": "c080",
    "relation": "细分"
  },
  {
    "id": "r685",
    "source": "c070",
    "target": "c081",
    "relation": "细分"
  },
  {
    "id": "r686",
    "source": "c070",
    "target": "c082",
    "relation": "细分"
  },
  {
    "id": "r687",
    "source": "c070",
    "target": "c086",
    "relation": "细分"
  },
  {
    "id": "r688",
    "source": "c070",
    "target": "c087",
    "relation": "细分"
  },
  {
    "id": "r689",
    "source": "c070",
    "target": "c088",
    "relation": "细分"
  },
  {
    "id": "r690",
    "source": "c070",
    "target": "c091",
    "relation": "细分"
  },
  {
    "id": "r691",
    "source": "c070",
    "target": "c092",
    "relation": "细分"
  },
  {
    "id": "r692",
    "source": "c070",
    "target": "c093",
    "relation": "细分"
  },
  {
    "id": "r693",
    "source": "c070",
    "target": "c097",
    "relation": "细分"
  },
  {
    "id": "r694",
    "source": "c070",
    "target": "c098",
    "relation": "细分"
  },
  {
    "id": "r695",
    "source": "c070",
    "target": "c099",
    "relation": "细分"
  },
  {
    "id": "r696",
    "source": "c070",
    "target": "c100",
    "relation": "细分"
  },
  {
    "id": "r697",
    "source": "c005",
    "target": "c006",
    "relation": "相即"
  },
  {
    "id": "r698",
    "source": "c006",
    "target": "c005",
    "relation": "蕴含"
  },
  {
    "id": "r699",
    "source": "c001",
    "target": "c002",
    "relation": "即"
  },
  {
    "id": "r700",
    "source": "c002",
    "target": "c003",
    "relation": "即"
  },
  {
    "id": "r701",
    "source": "c003",
    "target": "c008",
    "relation": "即"
  },
  {
    "id": "r702",
    "source": "c005",
    "target": "c012",
    "relation": "所显"
  },
  {
    "id": "r703",
    "source": "c007",
    "target": "c011",
    "relation": "体"
  },
  {
    "id": "r704",
    "source": "c010",
    "target": "c002",
    "relation": "即"
  },
  {
    "id": "r705",
    "source": "c013",
    "target": "c042",
    "relation": "即"
  },
  {
    "id": "r706",
    "source": "c006",
    "target": "c063",
    "relation": "即"
  },
  {
    "id": "r707",
    "source": "c015",
    "target": "c001",
    "relation": "即"
  },
  {
    "id": "r708",
    "source": "c016",
    "target": "c003",
    "relation": "即"
  },
  {
    "id": "r709",
    "source": "c007",
    "target": "c025",
    "relation": "灭谛"
  },
  {
    "id": "r710",
    "source": "c024",
    "target": "c013",
    "relation": "为始"
  },
  {
    "id": "r711",
    "source": "c047",
    "target": "c007",
    "relation": ""
  },
  {
    "id": "r712",
    "source": "c021",
    "target": "c036",
    "relation": "含"
  },
  {
    "id": "r713",
    "source": "c021",
    "target": "c037",
    "relation": "含"
  },
  {
    "id": "r714",
    "source": "c022",
    "target": "c036",
    "relation": "含"
  },
  {
    "id": "r715",
    "source": "c022",
    "target": "c037",
    "relation": "含"
  },
  {
    "id": "r716",
    "source": "c023",
    "target": "c022",
    "relation": "含"
  },
  {
    "id": "r717",
    "source": "c023",
    "target": "c038",
    "relation": "含"
  },
  {
    "id": "r718",
    "source": "c025",
    "target": "c007",
    "relation": "为灭"
  },
  {
    "id": "r719",
    "source": "c026",
    "target": "c025",
    "relation": "道谛"
  },
  {
    "id": "r720",
    "source": "c027",
    "target": "c060",
    "relation": "无常印"
  },
  {
    "id": "r721",
    "source": "c027",
    "target": "c059",
    "relation": "无我印"
  },
  {
    "id": "r722",
    "source": "c027",
    "target": "c007",
    "relation": "涅槃印"
  },
  {
    "id": "r723",
    "source": "c028",
    "target": "c012",
    "relation": "为导"
  },
  {
    "id": "r724",
    "source": "c035",
    "target": "c026",
    "relation": "含"
  },
  {
    "id": "r725",
    "source": "c029",
    "target": "c057",
    "relation": ""
  },
  {
    "id": "r726",
    "source": "c030",
    "target": "c057",
    "relation": ""
  },
  {
    "id": "r727",
    "source": "c031",
    "target": "c057",
    "relation": ""
  },
  {
    "id": "r728",
    "source": "c032",
    "target": "c057",
    "relation": ""
  },
  {
    "id": "r729",
    "source": "c033",
    "target": "c057",
    "relation": ""
  },
  {
    "id": "r730",
    "source": "c034",
    "target": "c057",
    "relation": ""
  },
  {
    "id": "r731",
    "source": "c040",
    "target": "c039",
    "relation": "根本"
  },
  {
    "id": "r732",
    "source": "c041",
    "target": "c039",
    "relation": "根本"
  },
  {
    "id": "r733",
    "source": "c042",
    "target": "c039",
    "relation": "根本"
  },
  {
    "id": "r734",
    "source": "c046",
    "target": "c047",
    "relation": "牵引"
  },
  {
    "id": "r735",
    "source": "c048",
    "target": "c046",
    "relation": "感"
  },
  {
    "id": "r736",
    "source": "c050",
    "target": "c027",
    "relation": "印证"
  },
  {
    "id": "r737",
    "source": "c052",
    "target": "c035",
    "relation": "戒学"
  },
  {
    "id": "r738",
    "source": "c055",
    "target": "c028",
    "relation": "施度"
  },
  {
    "id": "r739",
    "source": "c056",
    "target": "c028",
    "relation": "含"
  },
  {
    "id": "r740",
    "source": "c101",
    "target": "c062",
    "relation": "体现"
  },
  {
    "id": "r741",
    "source": "c102",
    "target": "c005",
    "relation": "胜义"
  },
  {
    "id": "r742",
    "source": "c102",
    "target": "c111",
    "relation": "世俗"
  },
  {
    "id": "r743",
    "source": "c103",
    "target": "c005",
    "relation": "核心"
  },
  {
    "id": "r744",
    "source": "c103",
    "target": "c104",
    "relation": ""
  },
  {
    "id": "r745",
    "source": "c105",
    "target": "c117",
    "relation": "为归"
  },
  {
    "id": "r746",
    "source": "c109",
    "target": "c110",
    "relation": ""
  },
  {
    "id": "r747",
    "source": "c115",
    "target": "c103",
    "relation": "总纲"
  },
  {
    "id": "r748",
    "source": "c118",
    "target": "c101",
    "relation": "破"
  },
  {
    "id": "r749",
    "source": "c127",
    "target": "c133",
    "relation": "所依"
  },
  {
    "id": "r750",
    "source": "c128",
    "target": "c144",
    "relation": "执"
  },
  {
    "id": "r751",
    "source": "c129",
    "target": "c137",
    "relation": "缘起"
  },
  {
    "id": "r752",
    "source": "c130",
    "target": "c002",
    "relation": "即"
  },
  {
    "id": "r753",
    "source": "c131",
    "target": "c127",
    "relation": "对"
  },
  {
    "id": "r754",
    "source": "c132",
    "target": "c023",
    "relation": "含"
  },
  {
    "id": "r755",
    "source": "c133",
    "target": "c004",
    "relation": "为体"
  },
  {
    "id": "r756",
    "source": "c134",
    "target": "c143",
    "relation": "执"
  },
  {
    "id": "r757",
    "source": "c135",
    "target": "c136",
    "relation": "成"
  },
  {
    "id": "r758",
    "source": "c137",
    "target": "c138",
    "relation": "互熏"
  },
  {
    "id": "r759",
    "source": "c145",
    "target": "c146",
    "relation": "含"
  },
  {
    "id": "r760",
    "source": "c145",
    "target": "c147",
    "relation": "含"
  },
  {
    "id": "r761",
    "source": "c148",
    "target": "c149",
    "relation": "含"
  },
  {
    "id": "r762",
    "source": "c148",
    "target": "c150",
    "relation": "含"
  },
  {
    "id": "r763",
    "source": "c152",
    "target": "c153",
    "relation": "义"
  },
  {
    "id": "r764",
    "source": "c157",
    "target": "c158",
    "relation": "观行"
  },
  {
    "id": "r765",
    "source": "c157",
    "target": "c159",
    "relation": "义"
  },
  {
    "id": "r766",
    "source": "c159",
    "target": "c166",
    "relation": ""
  },
  {
    "id": "r767",
    "source": "c161",
    "target": "c162",
    "relation": "化法"
  },
  {
    "id": "r768",
    "source": "c161",
    "target": "c163",
    "relation": "化仪"
  },
  {
    "id": "r769",
    "source": "c164",
    "target": "c003",
    "relation": "性具"
  },
  {
    "id": "r770",
    "source": "c166",
    "target": "c167",
    "relation": "相"
  },
  {
    "id": "r771",
    "source": "c166",
    "target": "c168",
    "relation": "间"
  },
  {
    "id": "r772",
    "source": "c169",
    "target": "c159",
    "relation": "一念具"
  },
  {
    "id": "r773",
    "source": "c170",
    "target": "c007",
    "relation": "阶位"
  },
  {
    "id": "r774",
    "source": "c172",
    "target": "c035",
    "relation": "定慧"
  },
  {
    "id": "r775",
    "source": "c175",
    "target": "c003",
    "relation": "阐发"
  },
  {
    "id": "r776",
    "source": "c177",
    "target": "c178",
    "relation": "四法界"
  },
  {
    "id": "r777",
    "source": "c178",
    "target": "c181",
    "relation": "含"
  },
  {
    "id": "r778",
    "source": "c178",
    "target": "c182",
    "relation": "含"
  },
  {
    "id": "r779",
    "source": "c183",
    "target": "c177",
    "relation": "义"
  },
  {
    "id": "r780",
    "source": "c184",
    "target": "c182",
    "relation": "体现"
  },
  {
    "id": "r781",
    "source": "c185",
    "target": "c184",
    "relation": "门"
  },
  {
    "id": "r782",
    "source": "c186",
    "target": "c182",
    "relation": "喻"
  },
  {
    "id": "r783",
    "source": "c188",
    "target": "c160",
    "relation": "判"
  },
  {
    "id": "r784",
    "source": "c195",
    "target": "c194",
    "relation": "位"
  },
  {
    "id": "r785",
    "source": "c197",
    "target": "c201",
    "relation": "旨归"
  },
  {
    "id": "r786",
    "source": "c198",
    "target": "c199",
    "relation": ""
  },
  {
    "id": "r787",
    "source": "c200",
    "target": "c197",
    "relation": ""
  },
  {
    "id": "r788",
    "source": "c202",
    "target": "c016",
    "relation": "即"
  },
  {
    "id": "r789",
    "source": "c203",
    "target": "c204",
    "relation": "宗"
  },
  {
    "id": "r790",
    "source": "c203",
    "target": "c205",
    "relation": "本"
  },
  {
    "id": "r791",
    "source": "c206",
    "target": "c197",
    "relation": "法"
  },
  {
    "id": "r792",
    "source": "c208",
    "target": "c209",
    "relation": "用"
  },
  {
    "id": "r793",
    "source": "c210",
    "target": "c209",
    "relation": "机用"
  },
  {
    "id": "r794",
    "source": "c211",
    "target": "c197",
    "relation": "体现"
  },
  {
    "id": "r795",
    "source": "c212",
    "target": "c213",
    "relation": "资粮"
  },
  {
    "id": "r796",
    "source": "c213",
    "target": "c214",
    "relation": "行"
  },
  {
    "id": "r797",
    "source": "c214",
    "target": "c068",
    "relation": "生处"
  },
  {
    "id": "r798",
    "source": "c216",
    "target": "c068",
    "relation": "本愿"
  },
  {
    "id": "r799",
    "source": "sect001",
    "target": "s011",
    "relation": "宗依"
  },
  {
    "id": "r800",
    "source": "sect001",
    "target": "s012",
    "relation": "宗依"
  },
  {
    "id": "r801",
    "source": "sect001",
    "target": "s013",
    "relation": "宗依"
  },
  {
    "id": "r802",
    "source": "sect001",
    "target": "s014",
    "relation": "宗依"
  },
  {
    "id": "r803",
    "source": "sect001",
    "target": "s015",
    "relation": "宗依"
  },
  {
    "id": "r804",
    "source": "sect001",
    "target": "s063",
    "relation": "宗依"
  },
  {
    "id": "r805",
    "source": "sect001",
    "target": "s067",
    "relation": "宗依"
  },
  {
    "id": "r806",
    "source": "sect001",
    "target": "s068",
    "relation": "宗依"
  },
  {
    "id": "r807",
    "source": "sect002",
    "target": "s031",
    "relation": "宗依"
  },
  {
    "id": "r808",
    "source": "sect002",
    "target": "s032",
    "relation": "宗依"
  },
  {
    "id": "r809",
    "source": "sect002",
    "target": "s033",
    "relation": "宗依"
  },
  {
    "id": "r810",
    "source": "sect002",
    "target": "s071",
    "relation": "宗依"
  },
  {
    "id": "r811",
    "source": "sect002",
    "target": "s073",
    "relation": "宗依"
  },
  {
    "id": "r812",
    "source": "sect003",
    "target": "s011",
    "relation": "宗依"
  },
  {
    "id": "r813",
    "source": "sect003",
    "target": "s029",
    "relation": "宗依"
  },
  {
    "id": "r814",
    "source": "sect003",
    "target": "s045",
    "relation": "宗依"
  },
  {
    "id": "r815",
    "source": "sect003",
    "target": "s065",
    "relation": "宗依"
  },
  {
    "id": "r816",
    "source": "sect003",
    "target": "s066",
    "relation": "宗依"
  },
  {
    "id": "r817",
    "source": "sect003",
    "target": "s069",
    "relation": "宗依"
  },
  {
    "id": "r818",
    "source": "sect004",
    "target": "s034",
    "relation": "宗依"
  },
  {
    "id": "r819",
    "source": "sect004",
    "target": "s035",
    "relation": "宗依"
  },
  {
    "id": "r820",
    "source": "sect004",
    "target": "s036",
    "relation": "宗依"
  },
  {
    "id": "r821",
    "source": "sect004",
    "target": "s037",
    "relation": "宗依"
  },
  {
    "id": "r822",
    "source": "sect004",
    "target": "s072",
    "relation": "宗依"
  },
  {
    "id": "r823",
    "source": "sect005",
    "target": "s061",
    "relation": "宗依"
  },
  {
    "id": "r824",
    "source": "sect005",
    "target": "s062",
    "relation": "宗依"
  },
  {
    "id": "r825",
    "source": "sect005",
    "target": "s076",
    "relation": "宗依"
  },
  {
    "id": "r826",
    "source": "sect006",
    "target": "s058",
    "relation": "宗依"
  },
  {
    "id": "r827",
    "source": "sect006",
    "target": "s059",
    "relation": "宗依"
  },
  {
    "id": "r828",
    "source": "sect006",
    "target": "s060",
    "relation": "宗依"
  },
  {
    "id": "r829",
    "source": "sect006",
    "target": "s081",
    "relation": "宗依"
  },
  {
    "id": "r830",
    "source": "sect006",
    "target": "s091",
    "relation": "宗依"
  },
  {
    "id": "r831",
    "source": "sect006",
    "target": "s092",
    "relation": "宗依"
  },
  {
    "id": "r832",
    "source": "sect007",
    "target": "s079",
    "relation": "宗依"
  },
  {
    "id": "r833",
    "source": "sect007",
    "target": "s080",
    "relation": "宗依"
  },
  {
    "id": "r834",
    "source": "sect007",
    "target": "s087",
    "relation": "宗依"
  },
  {
    "id": "r835",
    "source": "sect007",
    "target": "s088",
    "relation": "宗依"
  },
  {
    "id": "r836",
    "source": "sect007",
    "target": "s089",
    "relation": "宗依"
  },
  {
    "id": "r837",
    "source": "sect007",
    "target": "s090",
    "relation": "宗依"
  },
  {
    "id": "r838",
    "source": "sect007",
    "target": "s098",
    "relation": "宗依"
  },
  {
    "id": "r839",
    "source": "sect008",
    "target": "s076",
    "relation": "宗依"
  },
  {
    "id": "r840",
    "source": "sect008",
    "target": "s077",
    "relation": "宗依"
  },
  {
    "id": "r841",
    "source": "sect008",
    "target": "s078",
    "relation": "宗依"
  },
  {
    "id": "r842",
    "source": "sect008",
    "target": "s095",
    "relation": "宗依"
  },
  {
    "id": "r843",
    "source": "sect008",
    "target": "s096",
    "relation": "宗依"
  },
  {
    "id": "r844",
    "source": "sect008",
    "target": "s097",
    "relation": "宗依"
  },
  {
    "id": "r845",
    "source": "p045",
    "target": "s013",
    "relation": "译出/著"
  },
  {
    "id": "r846",
    "source": "p045",
    "target": "s014",
    "relation": "译出/著"
  },
  {
    "id": "r847",
    "source": "p045",
    "target": "s016",
    "relation": "译出/著"
  },
  {
    "id": "r848",
    "source": "p045",
    "target": "s031",
    "relation": "译出/著"
  },
  {
    "id": "r849",
    "source": "p045",
    "target": "s038",
    "relation": "译出/著"
  },
  {
    "id": "r850",
    "source": "p045",
    "target": "s058",
    "relation": "译出/著"
  },
  {
    "id": "r851",
    "source": "p045",
    "target": "s063",
    "relation": "译出/著"
  },
  {
    "id": "r852",
    "source": "p045",
    "target": "s064",
    "relation": "译出/著"
  },
  {
    "id": "r853",
    "source": "p045",
    "target": "s067",
    "relation": "译出/著"
  },
  {
    "id": "r854",
    "source": "p045",
    "target": "s068",
    "relation": "译出/著"
  },
  {
    "id": "r855",
    "source": "p045",
    "target": "s080",
    "relation": "译出/著"
  },
  {
    "id": "r856",
    "source": "p045",
    "target": "s083",
    "relation": "译出/著"
  },
  {
    "id": "r857",
    "source": "p052",
    "target": "s011",
    "relation": "译出/著"
  },
  {
    "id": "r858",
    "source": "p052",
    "target": "s015",
    "relation": "译出/著"
  },
  {
    "id": "r859",
    "source": "p052",
    "target": "s029",
    "relation": "译出/著"
  },
  {
    "id": "r860",
    "source": "p052",
    "target": "s040",
    "relation": "译出/著"
  },
  {
    "id": "r861",
    "source": "p052",
    "target": "s045",
    "relation": "译出/著"
  },
  {
    "id": "r862",
    "source": "p052",
    "target": "s057",
    "relation": "译出/著"
  },
  {
    "id": "r863",
    "source": "p052",
    "target": "s059",
    "relation": "译出/著"
  },
  {
    "id": "r864",
    "source": "p052",
    "target": "s065",
    "relation": "译出/著"
  },
  {
    "id": "r865",
    "source": "p052",
    "target": "s066",
    "relation": "译出/著"
  },
  {
    "id": "r866",
    "source": "p052",
    "target": "s069",
    "relation": "译出/著"
  },
  {
    "id": "r867",
    "source": "p044",
    "target": "s032",
    "relation": "译出/著"
  },
  {
    "id": "r868",
    "source": "p044",
    "target": "s084",
    "relation": "译出/著"
  },
  {
    "id": "r869",
    "source": "p046",
    "target": "s034",
    "relation": "译出/著"
  },
  {
    "id": "r870",
    "source": "p048",
    "target": "s046",
    "relation": "译出/著"
  },
  {
    "id": "r871",
    "source": "p048",
    "target": "s054",
    "relation": "译出/著"
  },
  {
    "id": "r872",
    "source": "p048",
    "target": "s055",
    "relation": "译出/著"
  },
  {
    "id": "r873",
    "source": "p049",
    "target": "s026",
    "relation": "译出/著"
  },
  {
    "id": "r874",
    "source": "p049",
    "target": "s043",
    "relation": "译出/著"
  },
  {
    "id": "r875",
    "source": "p050",
    "target": "s027",
    "relation": "译出/著"
  },
  {
    "id": "r876",
    "source": "p050",
    "target": "s070",
    "relation": "译出/著"
  },
  {
    "id": "r877",
    "source": "p051",
    "target": "s028",
    "relation": "译出/著"
  },
  {
    "id": "r878",
    "source": "p051",
    "target": "s033",
    "relation": "译出/著"
  },
  {
    "id": "r879",
    "source": "p053",
    "target": "s030",
    "relation": "译出/著"
  },
  {
    "id": "r880",
    "source": "p053",
    "target": "s053",
    "relation": "译出/著"
  },
  {
    "id": "r881",
    "source": "p054",
    "target": "s035",
    "relation": "译出/著"
  },
  {
    "id": "r882",
    "source": "p054",
    "target": "s044",
    "relation": "译出/著"
  },
  {
    "id": "r883",
    "source": "p054",
    "target": "s056",
    "relation": "译出/著"
  },
  {
    "id": "r884",
    "source": "p054",
    "target": "s086",
    "relation": "译出/著"
  },
  {
    "id": "r885",
    "source": "p057",
    "target": "s078",
    "relation": "译出/著"
  },
  {
    "id": "r886",
    "source": "p058",
    "target": "s036",
    "relation": "译出/著"
  },
  {
    "id": "r887",
    "source": "p071",
    "target": "s061",
    "relation": "译出/著"
  },
  {
    "id": "r888",
    "source": "p071",
    "target": "s062",
    "relation": "译出/著"
  },
  {
    "id": "r889",
    "source": "p073",
    "target": "s071",
    "relation": "译出/著"
  },
  {
    "id": "r890",
    "source": "p073",
    "target": "s073",
    "relation": "译出/著"
  },
  {
    "id": "r891",
    "source": "p077",
    "target": "s072",
    "relation": "译出/著"
  },
  {
    "id": "r892",
    "source": "p081",
    "target": "s091",
    "relation": "译出/著"
  },
  {
    "id": "r893",
    "source": "p041",
    "target": "s006",
    "relation": "译出/著"
  },
  {
    "id": "r894",
    "source": "p041",
    "target": "s085",
    "relation": "译出/著"
  },
  {
    "id": "r895",
    "source": "p042",
    "target": "s018",
    "relation": "译出/著"
  },
  {
    "id": "r896",
    "source": "p026",
    "target": "p027",
    "relation": "付法"
  },
  {
    "id": "r897",
    "source": "p001",
    "target": "p026",
    "relation": "付法"
  },
  {
    "id": "r898",
    "source": "p027",
    "target": "p065",
    "relation": "付法"
  },
  {
    "id": "r899",
    "source": "p065",
    "target": "p066",
    "relation": "付法"
  },
  {
    "id": "r900",
    "source": "p066",
    "target": "p067",
    "relation": "付法"
  },
  {
    "id": "r901",
    "source": "p067",
    "target": "p068",
    "relation": "付法"
  },
  {
    "id": "r902",
    "source": "p068",
    "target": "p069",
    "relation": "付法"
  },
  {
    "id": "r903",
    "source": "p069",
    "target": "p070",
    "relation": "付法"
  },
  {
    "id": "r904",
    "source": "p069",
    "target": "p071",
    "relation": "付法"
  },
  {
    "id": "r905",
    "source": "p061",
    "target": "p062",
    "relation": "门人"
  },
  {
    "id": "r906",
    "source": "p061",
    "target": "p064",
    "relation": "门人"
  },
  {
    "id": "r907",
    "source": "p073",
    "target": "p074",
    "relation": "付法"
  },
  {
    "id": "r908",
    "source": "p075",
    "target": "p076",
    "relation": "付法"
  },
  {
    "id": "r909",
    "source": "p076",
    "target": "p077",
    "relation": "付法"
  },
  {
    "id": "r910",
    "source": "p077",
    "target": "p078",
    "relation": "付法"
  },
  {
    "id": "r911",
    "source": "p078",
    "target": "p079",
    "relation": "付法"
  },
  {
    "id": "r912",
    "source": "p080",
    "target": "p080",
    "relation": "开宗"
  },
  {
    "id": "r913",
    "source": "p082",
    "target": "p052",
    "relation": "门人"
  },
  {
    "id": "r914",
    "source": "p071",
    "target": "p086",
    "relation": "付法"
  },
  {
    "id": "r915",
    "source": "p086",
    "target": "p087",
    "relation": "付法"
  },
  {
    "id": "r916",
    "source": "p085",
    "target": "p086",
    "relation": "弟子"
  },
  {
    "id": "r917",
    "source": "p098",
    "target": "p037",
    "relation": "化身"
  },
  {
    "id": "r918",
    "source": "p099",
    "target": "p007",
    "relation": "化身"
  },
  {
    "id": "r919",
    "source": "p021",
    "target": "p001",
    "relation": "护法"
  },
  {
    "id": "r920",
    "source": "p072",
    "target": "sect001",
    "relation": "开宗/弘传"
  },
  {
    "id": "r921",
    "source": "p073",
    "target": "sect002",
    "relation": "开宗/弘传"
  },
  {
    "id": "r922",
    "source": "p052",
    "target": "sect003",
    "relation": "开宗/弘传"
  },
  {
    "id": "r923",
    "source": "p082",
    "target": "sect003",
    "relation": "开宗/弘传"
  },
  {
    "id": "r924",
    "source": "p075",
    "target": "sect004",
    "relation": "开宗/弘传"
  },
  {
    "id": "r925",
    "source": "p076",
    "target": "sect004",
    "relation": "开宗/弘传"
  },
  {
    "id": "r926",
    "source": "p077",
    "target": "sect004",
    "relation": "开宗/弘传"
  },
  {
    "id": "r927",
    "source": "p078",
    "target": "sect004",
    "relation": "开宗/弘传"
  },
  {
    "id": "r928",
    "source": "p079",
    "target": "sect004",
    "relation": "开宗/弘传"
  },
  {
    "id": "r929",
    "source": "p065",
    "target": "sect005",
    "relation": "开宗/弘传"
  },
  {
    "id": "r930",
    "source": "p066",
    "target": "sect005",
    "relation": "开宗/弘传"
  },
  {
    "id": "r931",
    "source": "p067",
    "target": "sect005",
    "relation": "开宗/弘传"
  },
  {
    "id": "r932",
    "source": "p068",
    "target": "sect005",
    "relation": "开宗/弘传"
  },
  {
    "id": "r933",
    "source": "p069",
    "target": "sect005",
    "relation": "开宗/弘传"
  },
  {
    "id": "r934",
    "source": "p070",
    "target": "sect005",
    "relation": "开宗/弘传"
  },
  {
    "id": "r935",
    "source": "p071",
    "target": "sect005",
    "relation": "开宗/弘传"
  },
  {
    "id": "r936",
    "source": "p062",
    "target": "sect006",
    "relation": "开宗/弘传"
  },
  {
    "id": "r937",
    "source": "p081",
    "target": "sect006",
    "relation": "开宗/弘传"
  },
  {
    "id": "r938",
    "source": "p080",
    "target": "sect007",
    "relation": "开宗/弘传"
  },
  {
    "id": "r939",
    "source": "p055",
    "target": "sect008",
    "relation": "开宗/弘传"
  },
  {
    "id": "r940",
    "source": "p056",
    "target": "sect008",
    "relation": "开宗/弘传"
  },
  {
    "id": "r941",
    "source": "p057",
    "target": "sect008",
    "relation": "开宗/弘传"
  },
  {
    "id": "r942",
    "source": "p083",
    "target": "sect008",
    "relation": "开宗/弘传"
  },
  {
    "id": "r943",
    "source": "p084",
    "target": "sect008",
    "relation": "开宗/弘传"
  },
  {
    "id": "r944",
    "source": "p001",
    "target": "p011",
    "relation": "胁侍"
  },
  {
    "id": "r945",
    "source": "p001",
    "target": "p012",
    "relation": "胁侍"
  },
  {
    "id": "r946",
    "source": "p002",
    "target": "p013",
    "relation": "胁侍"
  },
  {
    "id": "r947",
    "source": "p002",
    "target": "p015",
    "relation": "胁侍"
  },
  {
    "id": "r948",
    "source": "p004",
    "target": "p011",
    "relation": "胁侍"
  },
  {
    "id": "r949",
    "source": "p004",
    "target": "p012",
    "relation": "胁侍"
  },
  {
    "id": "r950",
    "source": "p003",
    "target": "p011",
    "relation": "胁侍"
  },
  {
    "id": "r951",
    "source": "p003",
    "target": "p017",
    "relation": "胁侍"
  },
  {
    "id": "r952",
    "source": "p001",
    "target": "p014",
    "relation": "护法"
  },
  {
    "id": "r953",
    "source": "p020",
    "target": "p001",
    "relation": "护法"
  },
  {
    "id": "r954",
    "source": "p021",
    "target": "p001",
    "relation": "护法"
  },
  {
    "id": "r955",
    "source": "p001",
    "target": "p026",
    "relation": "弟子"
  },
  {
    "id": "r956",
    "source": "p001",
    "target": "p027",
    "relation": "弟子"
  },
  {
    "id": "r957",
    "source": "p001",
    "target": "p028",
    "relation": "弟子"
  },
  {
    "id": "r958",
    "source": "p001",
    "target": "p029",
    "relation": "弟子"
  },
  {
    "id": "r959",
    "source": "s015",
    "target": "s016",
    "relation": "同经异译"
  },
  {
    "id": "r960",
    "source": "s015",
    "target": "s021",
    "relation": "同经异译"
  },
  {
    "id": "r961",
    "source": "s015",
    "target": "s022",
    "relation": "同经异译"
  },
  {
    "id": "r962",
    "source": "s015",
    "target": "s023",
    "relation": "同经异译"
  },
  {
    "id": "r963",
    "source": "s015",
    "target": "s024",
    "relation": "同经异译"
  },
  {
    "id": "r964",
    "source": "s015",
    "target": "s025",
    "relation": "同经异译"
  },
  {
    "id": "r965",
    "source": "s014",
    "target": "s026",
    "relation": "同经异译"
  },
  {
    "id": "r966",
    "source": "s014",
    "target": "s027",
    "relation": "同经异译"
  },
  {
    "id": "r967",
    "source": "s014",
    "target": "s028",
    "relation": "同经异译"
  },
  {
    "id": "r968",
    "source": "s014",
    "target": "s029",
    "relation": "同经异译"
  },
  {
    "id": "r969",
    "source": "s014",
    "target": "s030",
    "relation": "同经异译"
  },
  {
    "id": "r970",
    "source": "s031",
    "target": "s032",
    "relation": "同经异译"
  },
  {
    "id": "r971",
    "source": "s031",
    "target": "s033",
    "relation": "同经异译"
  },
  {
    "id": "r972",
    "source": "s035",
    "target": "s034",
    "relation": "同经异译"
  },
  {
    "id": "r973",
    "source": "s035",
    "target": "s036",
    "relation": "同经异译"
  },
  {
    "id": "r974",
    "source": "s046",
    "target": "s047",
    "relation": "同经异译"
  },
  {
    "id": "r975",
    "source": "s046",
    "target": "s048",
    "relation": "同经异译"
  },
  {
    "id": "r976",
    "source": "s038",
    "target": "s039",
    "relation": "同经异译"
  },
  {
    "id": "r977",
    "source": "s038",
    "target": "s040",
    "relation": "同经异译"
  },
  {
    "id": "r978",
    "source": "s042",
    "target": "s043",
    "relation": "同经异译"
  },
  {
    "id": "r979",
    "source": "s042",
    "target": "s044",
    "relation": "同经异译"
  },
  {
    "id": "r980",
    "source": "s058",
    "target": "s059",
    "relation": "同经异译"
  },
  {
    "id": "r981",
    "source": "s061",
    "target": "s062",
    "relation": "同经异译"
  },
  {
    "id": "r982",
    "source": "s061",
    "target": "s100",
    "relation": "同经异译"
  },
  {
    "id": "r983",
    "source": "s080",
    "target": "s098",
    "relation": "同经异译"
  },
  {
    "id": "r984",
    "source": "s037",
    "target": "s094",
    "relation": "同经异译"
  }
]
};

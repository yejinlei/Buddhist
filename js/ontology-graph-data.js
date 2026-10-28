/**
 * 佛学本体论 · 义理图谱数据
 * 包含五类节点：义理概念、经典、佛菩萨、祖师、宗派、部类
 */
const ontologyGraphData = (function() {
  // ==== 节点 ====
  const nodes = [];
  const edges = [];

  function addNode(id, name, cat, size, desc) {
    nodes.push({ id, name, category: cat, symbolSize: size || 20, desc: desc || '' });
  }
  function addEdge(s, t, label, type) {
    edges.push({ source: s, target: t, label: label ? { show: true, formatter: label, fontSize: 10, color: '#8B7355' } : undefined,
                 lineStyle: { type: type || 'solid', color: '#c9b99a', width: 1.2 } });
  }

  // 0. 核心义理概念
  const concepts = [
    // 核心法义
    ['缘起','诸法因因缘和合而生，无自性','c_dep_orig'],
    ['性空','一切法无自性，空即缘起','c_sunyata'],
    ['中道','离二边之见，不落空有','c_madhyama'],
    ['无我','诸法无我，无独立自性','c_anatman'],
    ['无常','诸行无常，刹那生灭','c_anitya'],
    ['涅槃','不生不灭之解脱境界','c_nirvana'],
    ['实相','诸法真实相','c_tathata'],
    ['如来藏','一切众生本具成佛之性','c_tathagatagarbha'],
    ['佛性','众生本具觉悟之体','c_buddhata'],
    ['阿赖耶识','第八识，含藏种子','c_alaya'],
    ['真如','诸法真实本性，如其本来','c_tathata2'],
    // 修行法门
    ['六度','布施、持戒、忍辱、精进、禅定、般若','c_paramita'],
    ['布施','财施、法施、无畏施','c_dana'],
    ['持戒','律仪戒、摄善法戒、饶益有情戒','c_sila'],
    ['忍辱','生忍、法忍、无生法忍','c_ksanti'],
    ['精进','断恶修善不懈怠','c_virya'],
    ['禅定','止观双修、心一境性','c_dhyana'],
    ['般若','通达诸法实相之智','c_prajna'],
    ['四谛','苦集灭道','c_aryasatya'],
    ['苦谛','三苦八苦','c_duhkha'],
    ['集谛','烦恼业之集起','c_samudaya'],
    ['灭谛','涅槃解脱','c_nirodha'],
    ['道谛','八正道','c_marga'],
    ['八正道','正见正思惟正语正业正命正精进正念正定','c_aryastangika'],
    ['十二因缘','无明缘行…生缘老死','c_pratitya'],
    ['无明','十二因缘之首，烦恼根本','c_avidya'],
    ['五蕴','色受想行识','c_skandha'],
    ['色蕴','物质现象','c_rupa'],
    ['三法印','诸行无常、诸法无我、涅槃寂静','c_trilaksana'],
    ['一实相印','大乘究竟法印','c_ekamudra'],
    // 宗派核心教义
    ['八不中道','不生不灭不常不断不一不异不来不出','c_astanasta'],
    ['二谛','世俗谛、胜义谛','c_satya'],
    ['唯识无境','万法唯识，外境非有','c_vijnaptimatra'],
    ['三自性','遍计所执、依他起、圆成实','c_trisvabhava'],
    ['转识成智','转八识成四智','c_asraya'],
    ['一心二门','心真如门、心生灭门','c_ekacitta'],
    ['本觉','众生本具之觉性','c_prakrti'],
    // 禅宗
    ['明心见性','直指人心见性成佛','c_dhyana_sight'],
    ['不立文字','教外别传，以心传心','c_buliwenzi'],
    // 净土
    ['往生净土','持名念佛往生西方极乐','c_wangsheng'],
    ['他力本愿','靠阿弥陀佛本愿他力','c_tali'],
    ['称名念佛','南无阿弥陀佛名号','c_nianfo'],
    // 密宗
    ['三密相应','身口意三密与佛相应','c_sanmi'],
    ['即身成佛','现身证得佛果','c_jishen'],
    // 天台
    ['一心三观','于一心中观空假中三谛','c_yixinsanguan'],
    ['一念三千','一念具足三千诸法','c_yiniansanqian'],
    ['五时八教','天台判教体系','c_wushi'],
    // 华严
    ['法界缘起','一切法互为缘起，一即一切','c_fajie'],
    ['六相圆融','总别同异成坏六相','c_liuxiang'],
    ['十玄门','华严十种玄妙缘起','c_shixuan'],
    ['四法界','事、理、理事无碍、事事无碍','c_sifajie'],
  ];
  concepts.forEach(c=>addNode(c[2], c[0], '概念', Math.min(40, Math.max(16, c[1].length/2+10)), c[1]));

  // 1. 佛菩萨
  const buddhas = [
    ['释迦牟尼佛','b_sakyamuni','本师，娑婆世界教主'],
    ['阿弥陀佛','b_amita','西方极乐世界教主'],
    ['药师佛','b_bhaisajya','东方净琉璃世界教主'],
    ['弥勒菩萨','b_maitreya','当来下生佛，兜率天'],
    ['观世音菩萨','b_avalokita','大悲菩萨，西方三圣'],
    ['大势至菩萨','b_mahasthama','大智菩萨，西方三圣'],
    ['文殊菩萨','b_manjusri','大智菩萨'],
    ['普贤菩萨','b_samantabhadra','大行菩萨'],
    ['地藏菩萨','b_ksitigarbha','大愿菩萨，地狱不空誓不成佛'],
    ['虚空藏菩萨','b_akasagarbha'],
    ['维摩诘居士','b_vimalakirti','在家菩萨'],
    ['金刚手菩萨','b_vajrapani','密宗护法'],
  ];
  buddhas.forEach(b=>addNode(b[1],b[0],'佛菩萨',25,b[2]||''));

  // 2. 经典
  const sutras = [
    ['阿含经','s_agama','四部阿含，根本佛法'],
    ['般若经','s_prajna','大品/小品/金刚/心经'],
    ['金刚经','s_vajra','般若系核心，应无所住'],
    ['心经','s_hrdaya','般若心要，色即是空'],
    ['法华经','s_lotus','会三归一，一乘实教'],
    ['华严经','s_avatamsaka','法界缘起，事事无碍'],
    ['涅槃经','s_nirvana_s','佛性常住，一阐提成佛'],
    ['维摩诘经','s_vimalakirti_s','不二法门，在家居士'],
    ['楞伽经','s_lankavatara','如来藏与唯识'],
    ['解深密经','s_samdhinirmocana','唯识三性三无性'],
    ['楞严经','s_surangama','大佛顶首，耳根圆通'],
    ['圆觉经','s_sutra_p','圆觉妙心'],
    ['阿弥陀经','s_amita_s','持名念佛'],
    ['无量寿经','s_sukhavati','阿弥陀佛四十八愿'],
    ['观无量寿经','s_amitayurdhyana','十六观门'],
    ['药师经','s_bhaisajya_s','药师佛十二大愿'],
    ['地藏经','s_ksitigarbha_s','孝亲救拔，幽冥教主'],
    ['金光明经','s_suvarnaprabhasa','护国经典'],
    ['大集经','s_mahasannipata'],
    ['大宝积经','s_maharatnakuta','方等核心'],
    ['梵网经','s_brahmajala','菩萨戒本'],
    ['优婆塞戒经','s_upasaka'],
    ['六祖坛经','s_platform','慧能所述，禅宗要典'],
    ['大乘起信论','s_dachengqixin','马鸣菩萨造，一心二门'],
    ['俱舍论','s_abhidharma','说一切有部'],
    ['大智度论','s_mahaprajnaparamita','龙树造论'],
    ['中论','s_madhyamaka','龙树造，八不中道'],
    ['瑜伽师地论','s_yogacara','弥勒说，唯识根本'],
    ['成唯识论','s_vijnaptimatrata','护法造，玄奘译'],
    ['大乘密严经','s_ghana'],
    ['摄大乘论','s_mahayanasamgraha','无著造'],
    ['法华玄义','s_fahuaxuan','天台三大部'],
    ['摩诃止观','s_mohezhiguan'],
    ['华严五教章','s_wujiaozhang'],
    ['五灯会元','s_wudenghuiyuan','禅宗灯史'],
    ['指月录','s_zhiyuelu','禅宗公案集'],
    ['大日经','s_mahavairocana','密宗胎藏界'],
    ['金刚顶经','s_vajrasekhara','密宗金刚界'],
    ['苏悉地经','s_susiddhi'],
  ];
  sutras.forEach(s=>addNode(s[1],s[0],'经典',22,s[2]||''));

  // 3. 祖师译师
  const masters = [
    ['鸠摩罗什','m_kumarajiva','344-413，姚秦译经大师，译金刚、法华、维摩、中论'],
    ['玄奘','m_xuanzang','602-664，大唐三藏，取经译经，成唯识论'],
    ['真谛','m_paramartha','499-569，摄论宗始祖，译摄大乘论'],
    ['义净','m_yijing','635-713，南海取经，译有部律典'],
    ['不空','m_amoghavajra','705-774，开元三大士之三，密宗金刚顶经'],
    ['善无畏','m_subhakara','637-735，开元三大士之一，大日经'],
    ['金刚智','m_vajrabodhi','669-741，开元三大士之二'],
    ['菩提流支','m_bodhiruci','北朝译师，译楞伽、金刚仙论'],
    ['竺法护','m_dharmaraksa','231-308，西晋译经最多之一'],
    ['支娄迦谶','m_lokaksema','东汉末，译道行般若'],
    ['安世高','m_shigao','东汉，译小乘禅数经'],
    ['支谦','m_zhiqian','三国吴，译维摩诘、阿弥陀经'],
    ['康僧会','m_samghavarman','三国吴'],
    ['法显','m_faxian','337-422，西行求法先驱'],
    ['昙无谶','m_dharmaksema','385-433，北凉译涅槃经'],
    ['佛陀跋陀罗','m_buddhabhadra','译华严经'],
    ['般若','m_prajna','唐，译心经另一本'],
    ['法成','m_facheng','唐，译经敦煌'],
    // 汉地祖师
    ['智者大师','m_zhizhe','智顗yǐ，538-597，天台宗实际创始人'],
    ['湛然','m_zhanran','天台九祖'],
    ['杜顺','m_dushun','华严初祖'],
    ['智俨','m_zhiyan','华严二祖'],
    ['法藏','m_fazang','643-712，华严三祖，贤首大师'],
    ['澄观','m_chengguan','738-839，华严四祖，清凉国师'],
    ['宗密','m_zongmi','780-841，华严五祖，圭峰大师'],
    ['慧能','m_huineng','638-713，禅宗六祖，南宗顿门'],
    ['神秀','m_shenxiu','606-706，北宗渐门'],
    ['菩提达摩','m_bodhidharma','？-536，禅宗初祖，西来大意'],
    ['慧可','m_huike','487-593，二祖'],
    ['僧璨','m_sengcan','三祖，信心铭'],
    ['道信','m_daoxin','580-651，四祖'],
    ['弘忍','m_hongren','601-674，五祖'],
    ['马祖道一','m_mazu','709-788，洪州宗，平常心是道'],
    ['百丈怀海','m_baizhang','749-814，立丛林清规'],
    ['临济义玄','m_linji','临济宗开祖'],
    ['洞山良价','m_dongshan','曹洞宗'],
    ['云门文偃','m_yunmen','云门宗'],
    ['法眼文益','m_fayan','法眼宗'],
    ['沩山灵佑','m_weishan','沩仰宗'],
    ['慧远','m_huiyuan','334-416，庐山结莲社，净土初祖'],
    ['善导','m_shandao','613-681，净土宗集大成'],
    ['道绰','m_daochuo','净土二祖'],
    ['昙鸾','m_tanluan','476-542，净土初祖'],
    ['道宣','m_daoxuan','596-667，律宗南山宗'],
    ['一行','m_yixing','683-727，密宗，大衍历'],
    ['惠果','m_huiguo','746-805，密宗七祖，空海之师'],
    // 印度
    ['龙树','m_nagarjuna','150-250，大乘中观始祖'],
    ['提婆','m_arya_deva','圣天，中观派'],
    ['无著','m_asanga','310-390，瑜伽行派始祖'],
    ['世亲','m_vasubandhu','320-400，唯识学大师'],
    ['马鸣','m_asvaghosa','大乘起信论'],
    // 近代
    ['印光','m_yiguang','1861-1940，净土十三祖'],
    ['太虚','m_taixu','1890-1947，人生佛教，僧伽改革'],
    ['印顺','m_yinshun','1906-2005，佛法概论'],
    ['弘一','m_hongyi','1880-1942，律宗中兴'],
    ['虚云','m_xuyun','1840-1959，禅宗泰斗'],
  ];
  masters.forEach(m=>addNode(m[1],m[0],'祖师译师',22,m[2]||''));

  // 4. 宗派
  const schools = [
    ['天台宗','sc_tiantai','智者大师创立，五时八教，一心三观一念三千'],
    ['华严宗','sc_huayan','贤首法藏创立，法界缘起，六相圆融，五教十宗'],
    ['三论宗','sc_sanlun','龙树中论为宗，八不中道，二谛'],
    ['唯识宗','sc_weishi','玄奘窥基创立，万法唯识，三自性，转识成智'],
    ['禅宗','sc_chan','达摩东传，慧能六祖，明心见性，教外别传'],
    ['净土宗','sc_jingtu','慧远善导，持名念佛，往生净土'],
    ['律宗','sc_lu','道宣，四分律南山宗'],
    ['密宗','sc_mi','开元三大士，三密相应，即身成佛'],
  ];
  schools.forEach(s=>addNode(s[1],s[0],'宗派',30,s[2]));

  // 5. 部类
  const cats = [
    ['阿含部类','cat_agama'],
    ['般若部类','cat_prajna'],
    ['法华部类','cat_lotus'],
    ['华严部类','cat_avatamsaka'],
    ['涅槃部类','cat_nirvana'],
    ['宝积部类','cat_ratnakuta'],
    ['大集部类','cat_mahasannipata'],
    ['经集部类','cat_sutra'],
    ['密教部类','cat_mantra'],
    ['律部类','cat_vinaya'],
    ['释经论部类','cat_shastra_up'],
    ['毗昙部类','cat_abhidharma_up'],
    ['中观部类','cat_madhyamaka'],
    ['瑜伽部类','cat_yoga'],
    ['论集部类','cat_shastra'],
    ['史传部类','cat_history'],
    ['事汇部类','cat_cyclopedia'],
    ['目录部类','cat_catalog'],
    ['疑似部类','cat_doubtful'],
    ['律宗相关','cat_vinaya_school'],
  ];
  cats.forEach(c=>addNode(c[1],c[0],'部类',18,c[2]||''));

  // ==== 关系（边）====
  // 义理内部
  addEdge('c_dep_orig','c_sunyata','即色即空');
  addEdge('c_sunyata','c_madhyama','不落二边');
  addEdge('c_anatman','c_anitya','共印三法印');
  addEdge('c_anitya','c_trilaksana','法印之一');
  addEdge('c_anatman','c_trilaksana');
  addEdge('c_nirvana','c_trilaksana');
  addEdge('c_dep_orig','c_tathata','缘起即实相');
  addEdge('c_tathata','c_tathata2','同体异名');
  addEdge('c_tathagatagarbha','c_buddhata','同体异名');
  addEdge('c_buddhata','c_alaya','性相合会');
  addEdge('c_paramita','c_dana'); addEdge('c_paramita','c_sila'); addEdge('c_paramita','c_ksanti');
  addEdge('c_paramita','c_virya'); addEdge('c_paramita','c_dhyana'); addEdge('c_paramita','c_prajna');
  addEdge('c_prajna','c_sunyata','般若照见五蕴皆空');
  addEdge('c_aryasatya','c_duhkha'); addEdge('c_aryasatya','c_samudaya');
  addEdge('c_aryasatya','c_nirodha'); addEdge('c_aryasatya','c_marga');
  addEdge('c_marga','c_aryastangika');
  addEdge('c_skandha','c_rupa','五蕴之首');
  addEdge('c_avidya','c_pratitya','十二因缘之首');
  addEdge('c_pratitya','c_dep_orig','具体展开');

  // 宗派-教义
  addEdge('sc_tiantai','c_yixinsanguan','核心观法');
  addEdge('sc_tiantai','c_yiniansanqian');
  addEdge('sc_tiantai','c_wushi','判教');
  addEdge('sc_tiantai','c_madhyama','圆顿');
  addEdge('sc_huayan','c_fajie','法界缘起');
  addEdge('sc_huayan','c_liuxiang','六相');
  addEdge('sc_huayan','c_shixuan','十玄');
  addEdge('sc_huayan','c_sifajie','四法界');
  addEdge('sc_sanlun','c_astanasta','八不中道');
  addEdge('sc_sanlun','c_satya','二谛');
  addEdge('sc_sanlun','c_madhyama','中道');
  addEdge('sc_weishi','c_vijnaptimatra','唯识无境');
  addEdge('sc_weishi','c_alaya','八识');
  addEdge('sc_weishi','c_asraya','转识成智');
  addEdge('sc_chan','c_dhyana_sight','明心见性');
  addEdge('sc_chan','c_buddhata','见性成佛');
  addEdge('sc_jingtu','c_wangsheng','往生');
  addEdge('sc_jingtu','c_tali','他力');
  addEdge('sc_jingtu','c_nianfo','持名');
  addEdge('sc_mi','c_sanmi','三密');
  addEdge('sc_mi','c_jishen','即身成佛');

  // 佛-净土
  addEdge('b_amita','sc_jingtu','本尊');
  addEdge('b_avalokita','b_amita','胁侍');
  addEdge('b_mahasthama','b_amita','胁侍');
  addEdge('b_sakyamuni','sc_chan','本师');
  addEdge('b_manjusri','sc_huayan','胁侍');
  addEdge('b_samantabhadra','sc_huayan','胁侍');
  addEdge('b_maitreya','c_tathagatagarbha');
  addEdge('b_ksitigarbha','b_sakyamuni','托举');

  // 经典-宗派
  addEdge('s_lotus','sc_tiantai','依止');
  addEdge('s_nirvana_s','sc_tiantai');
  addEdge('s_avatamsaka','sc_huayan','依止');
  addEdge('s_madhyamaka','sc_sanlun','依止');
  addEdge('s_vijnaptimatrata','sc_weishi');
  addEdge('s_yogacara','sc_weishi');
  addEdge('s_platform','sc_chan');
  addEdge('s_amita_s','sc_jingtu');
  addEdge('s_sukhavati','sc_jingtu');
  addEdge('s_amitayurdhyana','sc_jingtu');
  addEdge('s_brahmajala','sc_lu','菩萨戒');
  addEdge('s_mahavairocana','sc_mi');
  addEdge('s_vajrasekhara','sc_mi');
  addEdge('s_vajra','c_prajna','阐发');
  addEdge('s_hrdaya','c_prajna','心要');
  addEdge('s_prajna','c_prajna','系统经');
  addEdge('s_agama','c_aryasatya','原始教法');
  addEdge('s_dachengqixin','c_ekacitta','一心二门');
  addEdge('s_dachengqixin','c_tathagatagarbha');

  // 经典-部类
  addEdge('s_agama','cat_agama');
  addEdge('s_vajra','cat_prajna'); addEdge('s_hrdaya','cat_prajna'); addEdge('s_prajna','cat_prajna');
  addEdge('s_lotus','cat_lotus');
  addEdge('s_avatamsaka','cat_avatamsaka');
  addEdge('s_nirvana_s','cat_nirvana');
  addEdge('s_maharatnakuta','cat_ratnakuta');
  addEdge('s_mahasannipata','cat_mahasannipata');
  addEdge('s_vimalakirti_s','cat_sutra'); addEdge('s_lankavatara','cat_sutra');
  addEdge('s_samdhinirmocana','cat_sutra'); addEdge('s_surangama','cat_sutra');
  addEdge('s_amita_s','cat_sutra'); addEdge('s_ksitigarbha_s','cat_sutra');
  addEdge('s_mahavairocana','cat_mantra'); addEdge('s_vajrasekhara','cat_mantra');
  addEdge('s_madhyamaka','cat_madhyamaka');
  addEdge('s_mahaprajnaparamita','cat_madhyamaka');
  addEdge('s_yogacara','cat_yoga'); addEdge('s_vijnaptimatrata','cat_yoga');
  addEdge('s_dachengqixin','cat_shastra_up');

  // 祖师-宗派
  addEdge('m_kumarajiva','s_vajra','译'); addEdge('m_kumarajiva','s_lotus','译');
  addEdge('m_kumarajiva','s_vimalakirti_s','译'); addEdge('m_kumarajiva','s_madhyamaka','译');
  addEdge('m_xuanzang','s_vijnaptimatrata','编译');
  addEdge('m_xuanzang','sc_weishi','创宗');
  addEdge('m_xuanzang','s_hrdaya','译');
  addEdge('m_faxian','s_mahaparinirvana','取经');
  addEdge('m_amoghavajra','s_vajrasekhara','译');
  addEdge('m_subhakara','s_mahavairocana','译');
  addEdge('m_dharmaksema','s_nirvana_s','译');
  addEdge('m_buddhabhadra','s_avatamsaka','译');
  addEdge('m_zhizhe','sc_tiantai','创宗');
  addEdge('m_fazang','sc_huayan','创宗');
  addEdge('m_bodhidharma','sc_chan','初祖');
  addEdge('m_huineng','sc_chan','六祖');
  addEdge('m_huineng','s_platform','说法');
  addEdge('m_huiyuan','sc_jingtu','初祖');
  addEdge('m_shandao','sc_jingtu','集大成');
  addEdge('m_daoxuan','sc_lu','南山宗');
  addEdge('m_huiguo','sc_mi','七祖');
  addEdge('m_nagarjuna','s_madhyamaka','造');
  addEdge('m_nagarjuna','s_mahaprajnaparamita','造');
  addEdge('m_asanga','s_yogacara','说');
  addEdge('m_asanga','s_mahayanasamgraha','造');
  addEdge('m_vasubandhu','sc_weishi','鼻祖');
  addEdge('m_asvaghosa','s_dachengqixin','造');

  // 祖师之间
  addEdge('m_bodhidharma','m_huike','传');
  addEdge('m_huike','m_sengcan','传');
  addEdge('m_sengcan','m_daoxin','传');
  addEdge('m_daoxin','m_hongren','传');
  addEdge('m_hongren','m_huineng','传');
  addEdge('m_hongren','m_shenxiu','传');
  addEdge('m_mazu','m_huineng','下传');
  addEdge('m_baizhang','m_mazu','嗣法');
  addEdge('m_dushun','m_zhiyan','传');
  addEdge('m_zhiyan','m_fazang','传');
  addEdge('m_fazang','m_chengguan','传');
  addEdge('m_chengguan','m_zongmi','传');
  addEdge('m_yiguang','sc_jingtu','十三祖');
  addEdge('m_hongyi','sc_lu','中兴');
  addEdge('m_xuyun','sc_chan','续法');
  addEdge('m_taixu','sc_weishi','弘扬');
  addEdge('m_yinshun','c_dep_orig','中观见');

  return { nodes, edges };
})();

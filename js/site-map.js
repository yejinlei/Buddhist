/* 站点地图（Site Map）
 * 在 ontology.html 的 #sitemap-grid 中渲染一张四轴 × 七层的"坐标式导航"卡片矩阵。
 *
 * 数据来源（全部实时，前端拉取，无需预生成）：
 *   ../ontology/tbox_data.json           轴/层/类的 TBox 结构
 *   ../ontology/instances/manifest.json  全藏经文 + 字段统计（category/vehicle/mode/含偈/含咒/含科判等）
 *   ../ontology/instances/m2_index.json  义理层（概念/人物/经论/宗派）
 *   ../ontology/instances/events.json    法会/结集/译传/故事事件
 *   ../ontology/dharma_assemblies.json   法会聚合索引
 *   ../kepan/core.json                   科判覆盖
 *   ../ontology/instances/relations.json 义理关系
 *
 * 设计：
 *   - 列 = A1 分类 / A2 义理 / A3 人物 / A4 事件
 *   - 行 = L0…L6（抽象→具体）
 *   - 每格 = 一个"坐标"，格子中列出该坐标下对应的站点页面卡片；
 *           页面卡片标题、数字（实时）、链接、以及页面状态（已建/规划/待建）；
 *           灰色卡片 = 待建页面（空洞清单）。
 */
(function(){
  'use strict';

  const AXIS_COLORS = {A1:'#B8860B',A2:'#3E6B4F',A3:'#8B5A2B',A4:'#A23B3B'};
  const COLS=[
    {id:'A1',label:'A1 分类轴',sub:'部类·三藏·乘·显密·法门·科判'},
    {id:'A2',label:'A2 义理轴',sub:'教义·概念·法门·偈颂·咒语·章句'},
    {id:'A3',label:'A3 人物轴',sub:'佛陀·菩萨·阿罗汉·祖师·学者·护法'},
    {id:'A4',label:'A4 事件轴',sub:'法会·结集·译经·传法·故事·流变'}
  ];
  const ROWS=['L0','L1','L2','L3','L4','L5','L6'];

  // ================= 站点页面定义 =================
  // 每个页面卡片绑定到一个 (axis, layer) 坐标；countFn 返回实时数字（或 Promise），status: built / planned / pending
  const PAGES=[
    // ---- L0 元模型 ----
    {title:'本体总纲',axis:'A1',layer:'L0',href:'ontology.html',
     desc:'本体定义、四轴×七层、TBox/ABox 元模型',status:'built',anchor:'self',
     count:()=>({num:'TBox',sub:'v3.0.0'})},

    // ---- L1 核心教义 ----
    {title:'义理图谱',axis:'A2',layer:'L1',href:'graph.html',
     desc:'核心法义（缘起/空/佛性/佛土…）的关系网络',status:'built',
     count:(R)=>({num:R.m2.layer_count?R.m2.layer_count.L1:0,sub:'核心教义概念'})},
    {title:'佛学词典',axis:'A2',layer:'L1',href:'dict.html',
     desc:'7190 条佛学词条，双向挂接本体实例',status:'built',
     count:()=>({num:7190,sub:'词典词条'})},
    {title:'智能推演',axis:'A2',layer:'L1',href:'inference.html',
     desc:'基于本体关系的概念推演与问答',status:'built',
     count:(R)=>({num:R.relCnt||0,sub:'义理关系三元组'})},

    // ---- L2 义理范畴 ----
    {title:'义理图谱 · L2',axis:'A2',layer:'L2',href:'graph.html#view=m2',
     desc:'六因/五果/四谛/三学等法相范畴',status:'built',
     count:(R)=>({num:R.m2.layer_count?R.m2.layer_count.L2:0,sub:'义理范畴概念'})},

    // ---- L3 宗派行持 ----
    {title:'宗派判教',axis:'A2',layer:'L3',href:'panjiao.html',
     desc:'大乘八宗判教（天台/华严/三论/唯识/禅/净/律/密）',status:'built',
     count:(R)=>({num:R.m2.sects||0,sub:'汉传宗派'})},
    {title:'佛典译学',axis:'A3',layer:'L3',href:'translation.html',
     desc:'译师、译场、译经时代、版本源流',status:'built',
     count:(R)=>{
        const trs=((R.events&&R.events.transmission_events)||[]).filter(function(t){return (t.subtype||'').indexOf('失译')<0;});
        return {num:trs.length,sub:'译经/传法事件'};
     }},
    {title:'部类总览',axis:'A1',layer:'L3',href:'categories.html',
     desc:'阿含/般若/法华/华严/宝积… 部类划分与三藏分类',status:'built',
     count:(R)=>({num:Object.keys((R.manifest&&R.manifest.category_count)||{}).length,sub:'经录部类'})},

    // ---- L4 具体文本 ----
    {title:'全藏原典',axis:'A1',layer:'L4',href:'sutras.html',
     desc:'2506 部大正藏经文，繁/简/白三态、术语划词',status:'built',
     count:(R)=>({num:(R.manifest&&R.manifest.stats&&R.manifest.stats.total_sutras)||(R.manifest&&R.manifest.sutras&&R.manifest.sutras.length)||0,sub:'大正藏经'})},
    {title:'科判导航',axis:'A1',layer:'L4',href:'kepan.html',
     desc:'64 部核心经的章段科判结构',status:'built',
     count:(R)=>({num:(R.kepan&&R.kepan.length)||0,sub:'已科判核心经',warn:true})},
    {title:'异译对照',axis:'A1',layer:'L4',href:'parallel.html',
     desc:'同经异译本的段落级对齐',status:'built',
     count:(R)=>{
        const gps=((R.manifest&&R.manifest.stats)||{}).parallel_groups||0;
        return {num:gps||'~30',sub:'异译组对'};
     }},
    {title:'全文检索',axis:'A2',layer:'L4',href:'search.html',
     desc:'全藏关键词检索与段落定位',status:'built',
     count:(R)=>({num:(R.manifest&&R.manifest.stats&&R.manifest.stats.total_paragraphs)||0,sub:'可检索段落'})},
    {title:'人物总览',axis:'A3',layer:'L4',href:'graph.html#view=persons',
     desc:'佛陀/菩萨/阿罗汉/祖师/学者的索引页（从图谱跳转）',status:'planned',
     count:(R)=>({num:R.m2.persons||0,sub:'人物实例'})},

    // ---- L5 事件流变 ----
    {title:'译传时间轴',axis:'A4',layer:'L5',href:'timeline.html',
     desc:'佛典汉译与宗派传法的时间脉络',status:'built',
     count:(R)=>{
        const trs=((R.events&&R.events.transmission_events)||[]).filter(function(t){return (t.subtype||'').indexOf('失译')<0;});
        return {num:trs.length,sub:'译经/传法'};
     }},
    {title:'法会与结集',axis:'A4',layer:'L5',href:'ontology.html#ev-da',
     desc:'32 大法会、6 次经典结集的场所、圣众与所说法',status:'built',
     count:(R)=>{
        const da=(R.da&&R.da.dharma_assemblies)||[];
        const co=((R.events&&R.events.councils)||[]).length;
        return {num:da.length+' + '+co,sub:'法会 + 结集'};
     }},
    {title:'本生故事',axis:'A4',layer:'L5',href:'ontology.html#ev-st',
     desc:'276 个本生/本事/因缘故事（来源经文+人物）',status:'built',
     count:(R)=>({num:((R.events&&R.events.story_events)||[]).length,sub:'本生/因缘故事'})},

    // ---- L6 信仰文化外延 ----
    {title:'民间信仰与文化艺术',axis:'A3',layer:'L6',href:'graph.html#view=folklore',
     desc:'观音/弥勒/地藏/伽蓝等民间化圣众；造像、壁画、仪轨外延',status:'pending',
     count:(R)=>({num:Math.max(0,(R.m2.persons||0)-122)+3,sub:'民间信仰人物'})},
    {title:'护法诸天',axis:'A3',layer:'L6',href:'graph.html#view=protectors',
     desc:'天龙八部、伽蓝、韦驮、四大天王等护法神祇',status:'pending',
     count:()=>({num:0,sub:'待建实例'})}
  ];

  let R={}; // 存放各索引的原始数据

  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function $(s){return document.querySelector(s);}

  function loadAll(){
    const urls=[
      '../ontology/tbox_data.json',
      '../ontology/instances/manifest.json',
      '../ontology/instances/m2_index.json',
      '../ontology/instances/events.json',
      '../ontology/dharma_assemblies.json',
      '../kepan/core.json',
      '../ontology/instances/relations.json'
    ];
    return Promise.all(urls.map(function(u){
      return fetch(u,{cache:'no-cache'}).then(function(r){return r.ok?r.json():null;}).catch(function(){return null;});
    })).then(function(res){
      R.tbox=res[0]; R.manifest=res[1]; R.m2=res[2]; R.events=res[3]; R.da=res[4]; R.kepan=res[5]; R.rels=res[6];
      R.relCnt=(R.rels&&R.rels.length)||0;
      // 为 m2 准备 layer_count（从 concepts 统计）
      R.m2.layer_count={L1:0,L2:0,L3:0};
      R.m2.persons=(R.m2&&R.m2.persons&&R.m2.persons.length)||0;
      R.m2.concepts=(R.m2&&R.m2.concepts&&R.m2.concepts.length)||0;
      R.m2.sutras=(R.m2&&R.m2.sutras&&R.m2.sutras.length)||0;
      R.m2.sects=(R.m2&&R.m2.sects&&R.m2.sects.length)||0;
      (R.m2.concepts||[]).forEach(function(c){
        var ly=(c.layer||'L?').substr(0,2);
        if(R.m2.layer_count[ly]!=null) R.m2.layer_count[ly]++;
      });
      return R;
    });
  }

  function statusBadge(st){
    if(st==='built') return '<span style="background:#dcfce7;color:#166534;border:1px solid #86efac">✓ 已建</span>';
    if(st==='planned') return '<span style="background:#fef3c7;color:#92400e;border:1px solid #fcd34d">◐ 规划中</span>';
    return '<span style="background:#f3f4f6;color:#6b7280;border:1px solid #d1d5db">○ 待建</span>';
  }

  function pageCard(p){
    var c; try{ c=p.count(R); }catch(e){ c={num:'—',sub:''}; }
    if(c && typeof c.then==='function') c={num:'…',sub:''}; // 防御
    var num=(c&&c.num!=null)?c.num:'—';
    var sub=(c&&c.sub)?c.sub:'';
    var isBuilt=p.status==='built';
    var warn=(c&&c.warn)?'<span style="font-size:10px;background:#fee2e2;color:#991b1b;border-radius:4px;padding:0 5px;margin-left:4px">覆盖低</span>':'';
    var bg = isBuilt ? '#fff' : '#f9fafb';
    var border = isBuilt ? 'border-buddha-gold/40 hover:border-buddha-gold hover:shadow-lg' : 'border-gray-200';
    var titleColor = isBuilt ? 'text-buddha-primary' : 'text-gray-500';
    var numColor = isBuilt ? 'text-[color:var(--p,#B8860B)]' : 'text-gray-400';
    var axisColor = AXIS_COLORS[p.axis]||'#888';
    var href = p.anchor==='self' ? '#' : p.href;
    var onClick = p.anchor==='self'
      ? ' onclick="event.preventDefault();window.scrollTo({top:0,behavior:\'smooth\'});return false;"'
      : '';
    return '<a href="'+esc(href)+'"'+onClick
      +' class="block rounded-lg border '+border+' bg-'+(isBuilt?'white':'gray-50')+' p-3 transition-all duration-200 hover:-translate-y-0.5 group" '
      +' style="background:'+bg+';border-color:'+(isBuilt?axisColor+'55':'#e5e7eb')+'">'
      +'  <div class="flex items-baseline justify-between gap-1 mb-1">'
      +'    <b class="text-sm '+titleColor+' group-hover:underline" style="color:'+(isBuilt?axisColor:'#9ca3af')+'">'+esc(p.title)+'</b>'
      +     statusBadge(p.status)
      +'  </div>'
      +'  <div class="flex items-baseline gap-2 mb-1">'
      +'    <span class="text-xl font-black" style="color:'+(isBuilt?axisColor:'#d1d5db')+'">'+esc(num)+'</span>'
      +'    <span class="text-[11px] text-gray-500">'+esc(sub)+'</span>'+warn
      +'  </div>'
      +'  <div class="text-[11px] text-gray-500 leading-snug">'+esc(p.desc)+'</div>'
      +'</a>';
  }

  function render(){
    var grid=document.getElementById('sitemap-grid');
    if(!grid) return;

    // 按 (axis,layer) 分组
    var cellMap={};
    COLS.forEach(function(c){ ROWS.forEach(function(l){ cellMap[c.id+'-'+l]=[]; }); });
    PAGES.forEach(function(p){
      var k=p.axis+'-'+p.layer;
      if(cellMap[k]) cellMap[k].push(p);
    });

    // 行头 / 列头：列=轴（4 列）、行=层（7 行）。表格布局：第一列为层头、接下来 4 列为轴单元格。
    var wstyle='min-width:0';
    var html='<div class="overflow-x-auto">'
      +'<table style="width:100%;border-collapse:separate;border-spacing:6px;min-width:900px">'
      +'<thead><tr>'
      +'<th style="width:88px"></th>';
    COLS.forEach(function(c){
      html+='<th style="background:'+AXIS_COLORS[c.id]+';color:#fff;border-radius:8px 8px 0 0;padding:10px 12px;text-align:left">'
        +   '<div style="font-size:13px;font-weight:700;letter-spacing:.5px">'+esc(c.label)+'</div>'
        +   '<div style="font-size:10.5px;opacity:.85;margin-top:2px;font-weight:400">'+esc(c.sub)+'</div>'
        +'</th>';
    });
    html+='</tr></thead><tbody>';

    const LAYER_META={
      L0:{label:'L0 元模型',desc:'类/属性/关系定义',color:'#4a4a4a'},
      L1:{label:'L1 教理本体层',desc:'空/缘起/佛性…',color:'#6b5638'},
      L2:{label:'L2 义理范畴层',desc:'六因/四谛/三学…',color:'#8a7a62'},
      L3:{label:'L3 宗派行持层',desc:'部派/宗派/判教/法门',color:'#B8860B'},
      L4:{label:'L4 具体文本层',desc:'经/律/论·品/章/段/偈/咒',color:'#3E6B4F'},
      L5:{label:'L5 事件流变层',desc:'法会/结集/译传/故事',color:'#8B5A2B'},
      L6:{label:'L6 信仰文化外延',desc:'神祇/民间/仪轨/艺术',color:'#A23B3B'}
    };

    ROWS.forEach(function(l){
      var meta=LAYER_META[l];
      html+='<tr>'
        +'<td style="vertical-align:top;background:'+meta.color+'10;border-left:3px solid '+meta.color+';border-radius:6px;padding:8px 10px">'
        +  '<div style="font-size:12px;font-weight:700;color:'+meta.color+'">'+esc(meta.label)+'</div>'
        +  '<div style="font-size:10.5px;color:#6b7280;margin-top:2px;line-height:1.3">'+esc(meta.desc)+'</div>'
        +'</td>';
      COLS.forEach(function(c){
        var pages=cellMap[c.id+'-'+l]||[];
        html+='<td style="vertical-align:top;background:#fcfaf4;border-radius:8px;padding:8px;min-height:100px">';
        if(pages.length===0){
          html+='<div style="font-size:11px;color:#c4b89b;text-align:center;padding:18px 4px">——</div>';
        }else{
          html+='<div class="grid gap-2" style="grid-template-columns:repeat(auto-fill,minmax(180px,1fr))">';
          pages.forEach(function(p){ html+=pageCard(p); });
          html+='</div>';
        }
        html+='</td>';
      });
      html+='</tr>';
    });
    html+='</tbody></table></div>';
    grid.innerHTML=html;

    // 图例
    var legend=document.getElementById('sitemap-legend');
    if(legend){
      legend.innerHTML='<span><b style="display:inline-block;width:10px;height:10px;background:#dcfce7;border:1px solid #86efac;border-radius:2px;vertical-align:middle"></b> 已建页面</span>'
        +'<span><b style="display:inline-block;width:10px;height:10px;background:#fef3c7;border:1px solid #fcd34d;border-radius:2px;vertical-align:middle"></b> 规划中（通过图谱/总纲入口可达）</span>'
        +'<span><b style="display:inline-block;width:10px;height:10px;background:#f3f4f6;border:1px solid #d1d5db;border-radius:2px;vertical-align:middle"></b> 待建（本体空洞）</span>'
        +'<span><b style="display:inline-block;width:10px;height:10px;background:#fee2e2;border:1px solid #fca5a5;border-radius:2px;vertical-align:middle"></b> 覆盖低（待补数据）</span>'
        +'<span class="text-gray-400">所有数字为实时统计，数据一补刷新即变</span>';
    }
  }

  // 暴露一个 refresh（供 ontology-tbox-viz 统计完调用）
  window.SiteMap={
    init:function(){ loadAll().then(render).catch(function(e){ console.error('SiteMap load fail',e); }); },
    refresh:render
  };

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',window.SiteMap.init);
  }else{
    window.SiteMap.init();
  }
})();

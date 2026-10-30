/* 本体总纲 · 四轴 × 七层 属性正交交互图（D3.js v7）
 * 可视化表达本体论核心：
 *   1) 正交矩阵热力图：列=四轴（分类/内容/人物/事件），行=七层（元模型→外延）
 *      每个格子展示该(轴,层)组合下的本体类数 + 实例数热力值
 *   2) 关系弧线网络：用贝塞尔曲线连接 domain→range，体现"对象属性"
 *      不同 group（分类/文本/宗派/义理/人物/事件）用不同颜色
 *   3) 数据属性覆盖矩阵：切换视图显示每类挂接的数据属性（名称/梵名/译者/经号…）
 *   4) 交互：hover tooltip、点击高亮节点及其全部邻接、按关系组筛选、缩放平移、
 *      点击节点在下方展开详情卡（实例数/定义/子父类/数据来源）
 */
(function(){
  'use strict';

  const AXIS_COLORS = {A1:'#B8860B', A2:'#3E6B4F', A3:'#8B5A2B', A4:'#A23B3B'};
  const LAYER_COLORS = {L0:'#4a4a4a',L1:'#6b5638',L2:'#8a7a62',L3:'#B8860B',L4:'#3E6B4F',L5:'#8B5A2B',L6:'#A23B3B'};
  const GROUP_COLORS = {
    '分类关系类（A1 横向分类轴）':'#B8860B',
    '文本结构关系类（A2 纵向内容轴）':'#3E6B4F',
    '宗派判教关系类（A1 / L3）':'#C07830',
    '义理关系类（A2 / L1–L2）':'#5A7FA8',
    '人物关系类（A3 人物传承轴）':'#8B5A2B',
    '事件关系类（A4 事件缘起轴）':'#A23B3B'
  };
  const COLS=['A1','A2','A3','A4'];
  const ROWS=['L0','L1','L2','L3','L4','L5','L6'];

  // ===== 全局状态 =====
  let D=null, SRC=null, RAW={}, LIVE={};
  let mode='objects'; // objects | dataprops
  let enabledGroups=null; // Set of group names (null=全选)
  let hoverId=null, selectedId=null;
  let svg, gRoot, zoomBeh;
  let dims={};
  let nodePos={}; // clsId -> {x,y}
  let tooltip, detailHost;

  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function q(s){return document.querySelector(s);}

  // ===== 数据加载 =====
  function loadAll(cb){
    const SPEC=[
      ['../ontology/tbox_data.json',           'tbox'],
      ['../ontology/ontology-index.json',      'index'],
      ['../ontology/instances/manifest.json',  'manifest'],
      ['../ontology/instances/m2_index.json',  'm2'],
      ['../ontology/instances/events.json',    'events'],
      ['../ontology/dharma_assemblies.json',   'da'],
      ['../kepan/core.json',                   'kepan'],
      ['../ontology/instances/relations.json', 'rels']
    ];
    Promise.all(SPEC.map(sp=>fetch(sp[0],{cache:'no-cache'}).then(r=>r.ok?r.json():null).catch(()=>null)))
      .then(res=>{
        const R={}; SPEC.forEach((sp,i)=>R[sp[1]]=res[i]);
        D=R.tbox; SRC=R.index||{}; RAW=R;
        LIVE=computeLive(R);
        cb();
      });
  }

  function computeLive(R){
    const out={};
    const m=R.manifest||{}, ms=m.stats||{}, su=m.sutras||[];
    const has=(s,kws)=>{const c=(s&&s.category)||''; return kws.some(k=>c.indexOf(k)>=0);};
    out.Text=su.length;
    out.Sutra=su.filter(s=>has(s,['經','经','阿含','般若','法華','华严','華嚴','寶積','涅槃','大集','密','淨土','净土'])).length;
    out.Vinaya=su.filter(s=>has(s,['律'])).length;
    out.Sastra=su.filter(s=>has(s,['論','论','釋','释','疏','鈔'])).length;
    out.Chapter=ms.total_chapters; out.Section=ms.total_paragraphs;
    out.Gatha=ms.total_gathas; out.Mantra=ms.total_mantras;
    out.Kepan=R.kepan?Object.keys(R.kepan).length:null;
    const m2=R.m2||{}; const cs=m2.concepts||[], ps=m2.persons||[], ss=m2.sects||[];
    out.Concept=cs.length; out.Doctrine=cs.filter(c=>c.layer==='L2').length;
    out.Practice=cs.filter(c=>c.layer==='L3').length;
    out.School=ss.length; out.PanjiaoSystem=ss.length; out.Person=ps.length;
    const pc=k=>ps.filter(p=>(p.category||'')===k).length;
    out.Buddha=pc('佛陀'); out.Bodhisattva=pc('菩萨'); out.Arhat=pc('阿罗汉');
    out.Patriarch=pc('祖师译经师')+pc('祖师');
    out.ModernScholar=pc('学者')+pc('现代学者');
    out.Deity=pc('神祇')+pc('护法诸天'); out.FolkFigure=pc('民间信仰');
    out.Protector=pc('护法');
    const ev=R.events||{};
    out.Council=(ev.councils||[]).length;
    out.TransmissionEvent=(ev.transmission_events||[]).length;
    out.StoryEvent=(ev.story_events||[]).length;
    out.DharmaAssembly=R.da?Object.keys(R.da.assemblies||{}).length:null;
    out.Event=(out.Council||0)+(out.TransmissionEvent||0)+(out.StoryEvent||0)+(out.DharmaAssembly||0);
    return out;
  }
  function liveOf(cid){
    if(LIVE[cid]!=null) return LIVE[cid];
    const s=SRC.classes&&SRC.classes[cid];
    return s&&s.count!=null?s.count:null;
  }

  // ===== 主入口 =====
  function init(){
    loadAll(()=>{
      buildToolbar();
      buildSvg();
      layoutAndRender();
      renderLegend();
    });
  }

  // ===== 顶部工具条（视图切换 + 关系组过滤 + 重置） =====
  function buildToolbar(){
    const host=q('#ortho-toolbar'); if(!host) return;
    host.innerHTML='';

    // 视图切换
    const viewBox=document.createElement('div');
    viewBox.style.cssText='display:flex;gap:6px;align-items:center;flex-wrap:wrap';
    viewBox.innerHTML=
      '<span style="font-size:12px;color:#8a7a62;margin-right:4px">视图：</span>'+
      '<button data-v="objects" class="ov-btn active">对象属性（跨类关系）</button>'+
      '<button data-v="dataprops" class="ov-btn">数据属性（字段覆盖）</button>'+
      '<button data-v="isa" class="ov-btn">继承层级（subClassOf）</button>';
    host.appendChild(viewBox);

    // 关系组过滤
    const relBar=document.createElement('div');
    relBar.id='ortho-relfilter';
    relBar.style.cssText='display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:8px';
    host.appendChild(relBar);

    // 重置/提示
    const meta=document.createElement('div');
    meta.id='ortho-meta';
    meta.style.cssText='margin-left:auto;font-size:11px;color:#a2906a;text-align:right';
    host.appendChild(meta);

    // 绑定视图切换
    viewBox.querySelectorAll('.ov-btn').forEach(b=>{
      b.style.cssText='font-size:12px;padding:4px 12px;border-radius:9999px;border:1px solid #e0d4b0;background:#fffdf6;color:#6b5638;cursor:pointer';
      b.addEventListener('click',()=>{
        viewBox.querySelectorAll('.ov-btn').forEach(x=>{x.classList.remove('active');x.style.background='#fffdf6';x.style.color='#6b5638';});
        b.classList.add('active'); b.style.background='#B8860B'; b.style.color='#fff';
        mode=b.dataset.v;
        renderRelFilter(); layoutAndRender();
      });
    });
    viewBox.querySelector('.ov-btn.active').style.background='#B8860B';
    viewBox.querySelector('.ov-btn.active').style.color='#fff';

    renderRelFilter();
  }

  function renderRelFilter(){
    const host=q('#ortho-relfilter'); if(!host) return;
    host.innerHTML='';
    if(mode!=='objects'){ host.innerHTML='<span style="font-size:12px;color:#8a7a62">当前视图无对象属性关系</span>'; renderMeta(); return; }
    host.innerHTML='<span style="font-size:12px;color:#8a7a62;margin-right:2px">关系组：</span>';
    const groups=Array.from(new Set(D.relations.map(r=>r.group).filter(Boolean)));
    enabledGroups=new Set(groups);
    groups.forEach(g=>{
      const col=GROUP_COLORS[g]||'#888';
      const b=document.createElement('button');
      b.style.cssText=`font-size:11.5px;padding:3px 10px;border-radius:9999px;border:1px solid ${col}55;background:${col}15;color:${col};cursor:pointer;display:inline-flex;align-items:center;gap:5px`;
      b.innerHTML=`<span style="width:8px;height:8px;border-radius:50%;background:${col};display:inline-block"></span>${esc(g.replace(/（.*?）/g,''))}`;
      b.title=g;
      b.addEventListener('click',()=>{
        if(enabledGroups.has(g)){ enabledGroups.delete(g); b.style.opacity=0.35; b.style.filter='grayscale(0.6)'; }
        else{ enabledGroups.add(g); b.style.opacity=1; b.style.filter='none'; }
        renderEdges();
      });
      host.appendChild(b);
    });
    const allb=document.createElement('button');
    allb.style.cssText='font-size:11.5px;padding:3px 10px;border-radius:9999px;border:1px solid #c9bda5;background:#f7f1e3;color:#8a7a62;cursor:pointer;margin-left:8px';
    allb.textContent='全选/全不选';
    allb.addEventListener('click',()=>{
      const all=enabledGroups.size===0;
      enabledGroups=all?new Set(groups):new Set();
      host.querySelectorAll('button[data-g]').forEach(()=>{});
      Array.from(host.children).forEach((ch,idx)=>{ if(idx>0&&idx<=groups.length){ ch.style.opacity=all?1:0.35; ch.style.filter=all?'none':'grayscale(0.6)'; }});
      renderEdges();
    });
    host.appendChild(allb);
    renderMeta();
  }

  function renderMeta(){
    const host=q('#ortho-meta'); if(!host) return;
    const nCls=D.classes.length, nRel=D.relations.length, nProp=D.properties.length;
    host.innerHTML=`<span class="ortho-chip">本体类 <b>${nCls}</b></span><span class="ortho-chip">对象属性 <b>${nRel}</b></span><span class="ortho-chip">数据属性 <b>${nProp}</b></span>`;
    // 动态插入 chip 样式
    if(!q('#ortho-chip-style')){
      const st=document.createElement('style'); st.id='ortho-chip-style';
      st.textContent='.ortho-chip{display:inline-block;background:#fbf6ea;border:1px solid #ece2ca;border-radius:9999px;padding:1px 9px;margin:2px 0 2px 6px;font-size:11px;color:#5a3e1b}.ortho-chip b{color:#8a6d2f}';
      document.head.appendChild(st);
    }
  }

  // ===== SVG 画布 + zoom =====
  function buildSvg(){
    const host=q('#ortho-graph'); host.innerHTML='';
    const W=host.clientWidth||1100, H=Math.max(680, Math.min(800, window.innerHeight-300));
    dims={W,H,pad:{t:70,r:60,b:70,l:160}, cellW:0, cellH:0};

    svg=d3.select(host).append('svg')
      .attr('width','100%').attr('viewBox',`0 0 ${W} ${H}`)
      .attr('style','background:#fffdf8;border-radius:12px;max-height:800px;cursor:grab');
    gRoot=svg.append('g').attr('class','root');

    // defs：箭头
    const defs=gRoot.append('defs');
    Object.entries(GROUP_COLORS).forEach(([g,col])=>{
      defs.append('svg:marker')
        .attr('id','arr-'+hash(g)).attr('viewBox','0 -5 10 10')
        .attr('refX',22).attr('refY',0).attr('markerWidth',7).attr('markerHeight',7)
        .attr('orient','auto')
        .append('svg:path').attr('d','M0,-4L10,0L0,4Z').attr('fill',col).attr('opacity',0.85);
    });
    defs.append('svg:marker')
      .attr('id','arr-isa').attr('viewBox','0 -5 10 10')
      .attr('refX',22).attr('refY',0).attr('markerWidth',7).attr('markerHeight',7)
      .attr('orient','auto')
      .append('svg:path').attr('d','M0,-4L10,0L0,4Z').attr('fill','#9e8c6a');

    // 背景格（用于点击空白重置选中）
    gRoot.append('rect').attr('class','bg').attr('x',0).attr('y',0).attr('width',W).attr('height',H).attr('fill','transparent');

    // zoom
    zoomBeh=d3.zoom().scaleExtent([0.5,3]).on('zoom',(ev)=>{
      gRoot.selectAll('.zoomable').attr('transform',ev.transform);
    });
    svg.call(zoomBeh);
    svg.on('dblclick.zoom',null); // 禁用双击缩放，让双击可用于重置

    // 点击背景重置
    gRoot.select('.bg').on('click',()=>{ selectedId=null; updateHighlight(); renderDetail(null); });

    // tooltip
    tooltip=d3.select('#ortho-tip');
    if(tooltip.empty()){
      tooltip=d3.select('body').append('div').attr('id','ortho-tip');
    }
    tooltip.style('position','fixed').style('pointer-events','none')
      .style('background','rgba(43,30,12,0.96)').style('color','#fdf6e3')
      .style('padding','9px 13px').style('border-radius','9px').style('font-size','12px')
      .style('line-height','1.55').style('max-width','360px').style('z-index','99999')
      .style('box-shadow','0 10px 30px rgba(0,0,0,0.28)').style('display','none');

    detailHost=q('#ortho-detail');
  }

  // ===== 布局计算 + 渲染 =====
  function layoutAndRender(){
    if(!gRoot) return;
    gRoot.selectAll('.zoomable').remove();
    const z=gRoot.append('g').attr('class','zoomable');
    const {W,H,pad}=dims;
    const cw=(W-pad.l-pad.r)/4;
    const ch=(H-pad.t-pad.b)/7;
    dims.cw=cw; dims.cellH=ch;

    // 1) 网格背景
    const gGrid=z.append('g').attr('class','grid');
    // 列背景（按轴着色淡底）
    COLS.forEach((a,i)=>{
      gGrid.append('rect')
        .attr('x',pad.l+i*cw).attr('y',pad.t).attr('width',cw).attr('height',ch*7)
        .attr('fill',AXIS_COLORS[a]).attr('opacity',0.045).attr('rx',8);
    });
    // 行虚线分隔
    ROWS.forEach((l,j)=>{
      gGrid.append('line')
        .attr('x1',pad.l).attr('x2',W-pad.r).attr('y1',pad.t+j*ch).attr('y2',pad.t+j*ch)
        .attr('stroke','#ece2ca').attr('stroke-dasharray','3 4').attr('stroke-width',1);
    });
    COLS.forEach((a,i)=>{
      gGrid.append('line')
        .attr('x1',pad.l+i*cw).attr('x2',pad.l+i*cw).attr('y1',pad.t).attr('y2',pad.t+ch*7)
        .attr('stroke','#ece2ca').attr('stroke-dasharray','3 4').attr('stroke-width',1);
    });

    // 2) 轴头（列标签）
    const gAxisH=z.append('g').attr('class','axis-heads');
    D.axes.forEach((a,i)=>{
      const x=pad.l+i*cw+cw/2;
      const g=gAxisH.append('g').style('cursor','pointer')
        .on('click',()=>{ selectAxis(a.id); });
      g.append('rect').attr('x',pad.l+i*cw+8).attr('y',pad.t-44).attr('width',cw-16).attr('height',32)
        .attr('rx',10).attr('fill',AXIS_COLORS[a.id]+'22').attr('stroke',AXIS_COLORS[a.id]).attr('stroke-width',1.2);
      g.append('text').attr('x',x).attr('y',pad.t-23).attr('text-anchor','middle')
        .attr('font-size',14).attr('font-weight',700).attr('fill',AXIS_COLORS[a.id]).text(a.label);
      g.append('text').attr('x',x).attr('y',pad.t-9).attr('text-anchor','middle')
        .attr('font-size',10.5).attr('fill','#8a7a62').text(a.id);
    });

    // 3) 层头（行标签）
    const gLayH=z.append('g').attr('class','layer-heads');
    D.layers.forEach((l,j)=>{
      const y=pad.t+j*ch+ch/2;
      const g=gLayH.append('g').style('cursor','pointer')
        .on('click',()=>{ selectLayer(l.id); });
      g.append('rect').attr('x',pad.l-130).attr('y',pad.t+j*ch+8).attr('width',120).attr('height',ch-16)
        .attr('rx',8).attr('fill',LAYER_COLORS[l.id]+'18').attr('stroke',LAYER_COLORS[l.id]).attr('stroke-width',1);
      g.append('text').attr('x',pad.l-70).attr('y',y-3).attr('text-anchor','middle')
        .attr('font-size',12).attr('font-weight',600).attr('fill',LAYER_COLORS[l.id]).text(l.label);
      g.append('text').attr('x',pad.l-70).attr('y',y+12).attr('text-anchor','middle')
        .attr('font-size',10).attr('fill','#a2906a').text(l.id+' · 抽象度 '+(6-j)+'/6');
    });

    // 4) 热力格（展示类数/实例数）
    nodePos={};
    const cellData=[];
    const byCell={};
    D.classes.forEach(c=>{
      (c.axes||[]).forEach(a=>{
        const k=a+'|'+c.layer;
        if(!byCell[k]) byCell[k]=[];
        byCell[k].push(c);
      });
    });
    let maxInst=1;
    Object.values(byCell).forEach(arr=>{
      let s=0; arr.forEach(c=>{const n=liveOf(c.id); if(n!=null&&isFinite(n)) s+=n;});
      if(s>maxInst) maxInst=s;
    });
    const gCells=z.append('g').attr('class','cells');
    COLS.forEach((a,i)=>{
      ROWS.forEach((l,j)=>{
        const k=a+'|'+l; const cs=byCell[k]||[];
        const x=pad.l+i*cw, y=pad.t+j*ch;
        let instSum=0; cs.forEach(c=>{const n=liveOf(c.id); if(n!=null&&isFinite(n)) instSum+=n;});
        const nCls=cs.length;
        const ratio=instSum?Math.min(1, 0.15+0.85*(instSum/maxInst)):0;
        const bg=nCls?d3.interpolateRgb('#f7edcf',AXIS_COLORS[a])(ratio):'#f8f4ea';
        cellData.push({a,l,cs,nCls,instSum,x,y});
        const gc=gCells.append('g').attr('class','cell').attr('data-key',k).style('cursor','pointer');
        gc.append('rect')
          .attr('x',x+4).attr('y',y+4).attr('width',cw-8).attr('height',ch-8)
          .attr('rx',8).attr('fill',bg).attr('stroke','#d9cdb4').attr('stroke-width',1);
        if(nCls){
          gc.append('text').attr('x',x+cw/2).attr('y',y+ch/2-6).attr('text-anchor','middle')
            .attr('font-size',nCls>=6?22:18).attr('font-weight',800)
            .attr('fill',instSum>maxInst*0.4?'#fff':'#5a3e1b').text(nCls+' 类');
          const lab=cs.slice(0,3).map(c=>c.label).join('、')+(cs.length>3?'…':'');
          gc.append('text').attr('x',x+cw/2).attr('y',y+ch/2+14).attr('text-anchor','middle')
            .attr('font-size',10.5).attr('fill',instSum>maxInst*0.4?'#fff8e0':'#8a7a62').text(lab);
          if(instSum>0){
            gc.append('text').attr('x',x+cw/2).attr('y',y+ch-10).attr('text-anchor','middle')
              .attr('font-size',9.5).attr('fill',instSum>maxInst*0.4?'#ffe9a8':'#a2906a')
              .text('实例 '+instSum.toLocaleString());
          }
        }else{
          gc.append('text').attr('x',x+cw/2).attr('y',y+ch/2+4).attr('text-anchor','middle')
            .attr('font-size',12).attr('fill','#c9bda5').text('—');
        }
        // 计算节点坐标（类在格内水平排开）
        const nArr=cs.length;
        const spread=Math.min(cw-20, Math.max(40, 24*nArr));
        const startX=x+cw/2-spread/2;
        cs.forEach((c,ci)=>{
          const cx=nArr===1?x+cw/2:startX+(spread/(nArr===1?1:nArr-1))*ci;
          const cy=y+ch-18;  // 节点放在格子底部（和热力文字错位）
          if(!nodePos[c.id]) nodePos[c.id]={x:cx,y:cy,c};
          else { /* 一个类跨轴时保留第一次位置（主位置），其他位置不重叠 */ }
        });
        // hover/click
        gc.on('mouseenter',(ev)=>{
            const ax=D.axes.find(x=>x.id===a), ly=D.layers.find(x=>x.id===l);
            showTip(ev,`<div style="font-weight:700;color:#D4AF37;margin-bottom:4px">${esc(ax.label)} × ${esc(ly.label)}</div>
              <div style="opacity:.8;margin-bottom:4px">${esc(ly.desc||'')}</div>
              ${nCls?`<div>共 <b>${nCls}</b> 个本体类：${cs.map(c=>esc(c.label)).join('、')}</div>`:'<div style="opacity:.6">此格无直接定义类（类通过 axes 字段落在其他格）</div>'}
              ${instSum?`<div style="margin-top:4px;opacity:.85">实例合计 <b style="color:#D4AF37">${instSum.toLocaleString()}</b></div>`:''}`);
          })
          .on('mousemove',moveTip)
          .on('mouseleave',hideTip)
          .on('click',()=>{
            // 点击格子高亮该格所有类
            if(cs.length===1){ selectId(cs[0].id); }
            else { hoverId='__cell__:'+k; selectedId=null; updateHighlight(); renderDetail(null,cs,a,l); }
          });
      });
    });

    // 5) 节点层（类节点）
    const gNodes=z.append('g').attr('class','nodes');
    D.classes.forEach(c=>{
      const p=nodePos[c.id]; if(!p) return;
      const ax=(c.axes&&c.axes[0])||'A1';
      const col=AXIS_COLORS[ax]||'#888';
      const r=c.parent?11:13;
      const cnt=liveOf(c.id);
      const g=gNodes.append('g').attr('class','cls-node').attr('data-id',c.id)
        .attr('transform',`translate(${p.x},${p.y})`).style('cursor','pointer');
      g.append('circle').attr('r',r).attr('fill',c.parent?col+'dd':col).attr('stroke','#fff').attr('stroke-width',2);
      if(!c.parent) g.append('circle').attr('r',r+4).attr('fill','none').attr('stroke',col).attr('stroke-width',1).attr('opacity',0.5);
      g.append('text').attr('y',r+12).attr('text-anchor','middle').attr('font-size',10).attr('font-weight',c.parent?500:700).attr('fill','#4a3a1e').text(c.label);
      if(cnt!=null && cnt>0){
        const bw=Math.max(26,String(cnt).length*7+10);
        const bg=g.append('g').attr('transform',`translate(0,${r+22})`);
        bg.append('rect').attr('x',-bw/2).attr('y',0).attr('width',bw).attr('height',13).attr('rx',6).attr('fill','#fdf6e3').attr('stroke','#d9cdb4');
        bg.append('text').attr('y',10).attr('text-anchor','middle').attr('font-size',9).attr('font-weight',700).attr('fill','#8a6d2f').text(cnt>=10000?(cnt/10000).toFixed(1)+'w':cnt);
      }
      // 多轴标记（右上角小三角）
      if(c.axes && c.axes.length>1){
        g.append('circle').attr('cx',r-3).attr('cy',-r+3).attr('r',3).attr('fill','#D4AF37').attr('stroke','#fff').attr('stroke-width',1);
      }
      g.on('mouseenter',(ev)=>{
          d3.select(g.select('circle').node()).attr('r',r+3);
          const axs=(c.axes||[]).map(a=>{const x=D.axes.find(y=>y.id===a);return x?`<span style="color:${x.color};font-weight:600">${esc(x.label)}</span>`:a;}).join(' / ');
          const ly=D.layers.find(x=>x.id===c.layer);
          const cntLine=(cnt!=null&&cnt>0)?`<div style="margin-top:3px">实例：<b style="color:#D4AF37">${cnt.toLocaleString()}</b></div>`:'';
          showTip(ev,`<div style="font-weight:700;color:#D4AF37">${esc(c.label)} <span style="color:#b4a77a;font-weight:400;font-size:11px">(${esc(c.id)})</span></div>
            <div style="opacity:.85;margin-bottom:3px">轴：${axs} ｜ 层：<b style="color:${ly?ly.color:'#aaa'}">${esc(ly?ly.label:c.layer)}</b>${c.parent?'｜ 父类：'+esc(parentLabel(c.parent)):''}</div>
            <div style="opacity:.85">${esc(c.desc||'')}</div>${cntLine}
            <div style="opacity:.6;margin-top:6px;font-size:11px">点击节点高亮关联关系并展开详情</div>`);
        })
        .on('mousemove',moveTip)
        .on('mouseleave',()=>{d3.select(g.select('circle').node()).attr('r',r); hideTip();})
        .on('click',(ev)=>{ ev.stopPropagation(); selectId(c.id); });
    });

    // 6) 边层（根据 mode 渲染对象属性/继承/数据属性）
    const gEdges=z.insert('g','.nodes').attr('class','edges');
    renderEdges();
  }

  function renderEdges(){
    if(!gRoot) return;
    const z=gRoot.select('.zoomable'); if(z.empty()) return;
    z.selectAll('.edges').remove();
    const gEdges=z.insert('g','.nodes').attr('class','edges');

    if(mode==='objects'){
      const edges=[];
      D.relations.forEach(r=>{
        if(enabledGroups && !enabledGroups.has(r.group)) return;
        (r.domain||[]).forEach(d=>{
          (r.range||[]).forEach(ra=>{
            if(nodePos[d]&&nodePos[ra]&&d!==ra) edges.push({from:d,to:ra,rel:r});
          });
        });
      });
      // 曲线
      edges.forEach(e=>{
        const a=nodePos[e.from], b=nodePos[e.to];
        const col=GROUP_COLORS[e.rel.group]||'#888';
        const dx=b.x-a.x, dy=b.y-a.y;
        const dr=Math.sqrt(dx*dx+dy*dy)*1.2;
        const path=gEdges.append('path')
          .attr('d',`M${a.x+10},${a.y}A${dr},${dr} 0 0,1 ${b.x-10},${b.y}`)
          .attr('fill','none').attr('stroke',col).attr('stroke-width',1.4)
          .attr('stroke-dasharray','5 3').attr('opacity',0.45)
          .attr('marker-end',`url(#arr-${hash(e.rel.group)})`)
          .attr('data-from',e.from).attr('data-to',e.to).attr('data-group',e.rel.group)
          .attr('data-rel',e.rel.id)
          .style('cursor','pointer');
        path.on('mouseenter',(ev)=>{
            path.attr('stroke-width',2.4).attr('opacity',0.95);
            showTip(ev,`<b style="color:${col}">${esc(e.rel.label)}</b> <span style="opacity:.7">（${esc(e.rel.group)}）</span><br>
              ${esc(parentLabel(e.from))} → ${esc(parentLabel(e.to))}<br>
              <div style="opacity:.75;margin-top:3px;font-size:11px">${esc(e.rel.id)} ｜ 点击查看该对象属性详情</div>`);
          })
          .on('mousemove',moveTip)
          .on('mouseleave',()=>{path.attr('stroke-width',1.4).attr('opacity',0.45); hideTip();})
          .on('click',(ev)=>{ev.stopPropagation(); selectRel(e.rel.id);});
      });
    } else if(mode==='isa'){
      D.classes.forEach(c=>{
        if(c.parent && nodePos[c.parent] && nodePos[c.id]){
          const a=nodePos[c.parent], b=nodePos[c.id];
          const path=gEdges.append('path')
            .attr('d',`M${a.x},${a.y+12} C${a.x},${(a.y+b.y)/2} ${b.x},${(a.y+b.y)/2} ${b.x},${b.y-13}`)
            .attr('fill','none').attr('stroke','#9e8c6a').attr('stroke-width',1.6)
            .attr('marker-end','url(#arr-isa)')
            .attr('data-from',c.parent).attr('data-to',c.id);
        }
      });
    } else if(mode==='dataprops'){
      // 右侧加一列数据属性矩阵
      renderDataPropMatrix(z,gEdges);
    }
    updateHighlight();
  }

  // 数据属性覆盖矩阵：右边加一栏显示每类有哪些字段（小方块）
  function renderDataPropMatrix(z,gEdges){
    const {W,pad,cw,cellH:Hc}=dims;
    const ps=D.properties||[];
    const dpX0=W-pad.r+20;
    const colW=60, rowH=18;
    const totalW=dpX0+colW*ps.length+60;
    // 扩展svg
    svg.attr('viewBox',`0 0 ${Math.max(totalW,W)} ${dims.H}`);
    // 标题
    gEdges.append('text').attr('x',dpX0+30).attr('y',pad.t-22).attr('text-anchor','middle')
      .attr('font-size',12).attr('font-weight',700).attr('fill','#5a3e1b').text('数据属性覆盖（字段矩阵）');
    // 属性列头（竖排）
    ps.forEach((p,pi)=>{
      const x=dpX0+colW*(pi+0.5);
      const t=gEdges.append('text').attr('x',x).attr('y',pad.t-6)
        .attr('text-anchor','end').attr('font-size',9.5).attr('fill','#8a7a62')
        .attr('transform',`rotate(-60,${x},${pad.t-6})`).text(p.label)
        .attr('data-prop',p.id).style('cursor','pointer')
        .on('mouseenter',(ev)=>showTip(ev,`<b>${esc(p.label)}</b> <span style="opacity:.7">（${esc(p.id)}）</span><br>值域：${esc(p.range)}<br><span style="opacity:.7;font-size:11px">点击查看该数据属性详情</span>`))
        .on('mousemove',moveTip).on('mouseleave',hideTip)
        .on('click',(ev)=>{ev.stopPropagation(); selectProp(p.id);});
    });
    // 左括号装饰
    gEdges.append('text').attr('x',dpX0-10).attr('y',pad.t+Hc*3.5).attr('text-anchor','middle')
      .attr('font-size',30).attr('fill','#d9cdb4').text('▸');
    // 逐类逐属性画方块
    D.classes.forEach(c=>{
      const p=nodePos[c.id]; if(!p) return;
      ps.forEach((pr,pi)=>{
        let on=false;
        if(pr.domain && pr.domain[0]==='所有类') on=true;
        else if(pr.domain && pr.domain.indexOf(c.id)>=0) on=true;
        const x=dpX0+colW*pi+colW/2-6;
        const y=p.y-6;
        const ax=(c.axes&&c.axes[0])||'A1';
        const col=AXIS_COLORS[ax]||'#888';
        gEdges.append('rect')
          .attr('x',x).attr('y',y).attr('width',12).attr('height',12).attr('rx',2)
          .attr('fill',on?col:'transparent')
          .attr('stroke',on?'#fff':'#e5dcc6').attr('stroke-width',1)
          .attr('opacity',on?0.85:0.6)
          .attr('data-prop',pr.id)
          .style('cursor','pointer')
          .on('mouseenter',(ev)=>{showTip(ev,`<b>${esc(c.label)}</b> · ${esc(pr.label)}<br><span style="opacity:.7;font-size:11px">${esc(pr.id)} → ${esc(pr.range)} ｜ 点击查看该数据属性详情</span>`);})
          .on('mousemove',moveTip).on('mouseleave',hideTip)
          .on('click',(ev)=>{ev.stopPropagation(); selectProp(pr.id);});
      });
    });
  }

  // ===== 交互高亮 =====
  function selectId(id){
    selectedId=(selectedId===id)?null:id;
    hoverId=null;
    updateHighlight(); renderDetail(selectedId);
  }
  function selectRel(id){
    const key='__rel__:'+id;
    selectedId=(selectedId===key)?null:key;
    hoverId=null; updateHighlight();
    if(selectedId) renderRelDetail(id); else if(detailHost) detailHost.innerHTML='';
  }
  function selectProp(id){
    const key='__prop__:'+id;
    selectedId=(selectedId===key)?null:key;
    hoverId=null; updateHighlight();
    if(selectedId) renderPropDetail(id); else if(detailHost) detailHost.innerHTML='';
  }
  function selectAxis(a){
    // 轴筛选：保留该轴所有节点+相邻边，其它淡化
    selectedId='__axis__:'+a;
    updateHighlight(); renderDetail(null,null,a,null);
  }
  function selectLayer(l){
    selectedId='__layer__:'+l;
    updateHighlight(); renderDetail(null,null,null,l);
  }
  function updateHighlight(){
    if(!gRoot) return;
    const nodes=gRoot.selectAll('.cls-node');
    const edges=gRoot.selectAll('.edges path');
    nodes.attr('opacity',1);
    edges.attr('opacity',function(){ return d3.select(this).attr('data-group')?0.45:0.6; }).attr('stroke-width',function(){ return d3.select(this).attr('data-group')?1.4:1.6; });

    if(!selectedId){ return; }
    if(selectedId.startsWith('__rel__:')){
      const rid=selectedId.slice(8);
      nodes.attr('opacity',0.25);
      edges.each(function(){
        const el=d3.select(this);
        if(el.attr('data-rel')===rid){
          el.attr('opacity',0.98).attr('stroke-width',2.6);
          const fr=el.attr('data-from'), to=el.attr('data-to');
          nodes.filter(function(){const q=d3.select(this).attr('data-id');return q===fr||q===to;}).attr('opacity',1);
        } else el.attr('opacity',0.05);
      });
      return;
    }
    if(selectedId.startsWith('__prop__:')){
      const pid=selectedId.slice(9);
      nodes.attr('opacity',0.3);
      gRoot.selectAll('.edges [data-prop]').each(function(){
        const el=d3.select(this);
        el.attr('opacity', el.attr('data-prop')===pid?0.98:0.12);
      });
      return;
    }
    if(selectedId.startsWith('__axis__:')){
      const a=selectedId.split(':')[1];
      nodes.each(function(){
        const cid=d3.select(this).attr('data-id');
        const c=D.classes.find(x=>x.id===cid);
        const on=(c.axes||[]).indexOf(a)>=0;
        d3.select(this).attr('opacity',on?1:0.15);
      });
      edges.attr('opacity',0.06);
      return;
    }
    if(selectedId.startsWith('__layer__:')){
      const l=selectedId.split(':')[1];
      nodes.each(function(){
        const cid=d3.select(this).attr('data-id');
        const c=D.classes.find(x=>x.id===cid);
        d3.select(this).attr('opacity',c.layer===l?1:0.15);
      });
      edges.attr('opacity',0.06);
      return;
    }
    // 节点聚焦：高亮直接相连的节点和边
    const neighbors=new Set([selectedId]);
    const edgesOn=new Set();
    edges.each(function(){
      const f=d3.select(this).attr('data-from'), t=d3.select(this).attr('data-to');
      if(f===selectedId||t===selectedId){ neighbors.add(f); neighbors.add(t); edgesOn.add(this); }
    });
    nodes.each(function(){
      const cid=d3.select(this).attr('data-id');
      d3.select(this).attr('opacity',neighbors.has(cid)?1:0.15);
      if(cid===selectedId){ d3.select(this).raise(); }
    });
    edges.each(function(){
      if(edgesOn.has(this)){ d3.select(this).attr('opacity',0.95).attr('stroke-width',2.4).raise(); }
      else d3.select(this).attr('opacity',0.05);
    });
  }

  // ===== 详情卡 =====
  function renderDetail(cid, multiCells, axisSel, layerSel){
    if(!detailHost) return;
    if(multiCells && multiCells.length){
      const ax=D.axes.find(x=>x.id===axisSel), ly=D.layers.find(x=>x.id===layerSel);
      let rows=multiCells.map(c=>{
        const cnt=liveOf(c.id);
        const s=SRC.classes&&SRC.classes[c.id]||{};
        return `<tr><td><code style="background:#f4efe3;border-radius:4px;padding:1px 5px;font-size:11px;color:#5a3e1b">${esc(c.id)}</code></td>
          <td><b style="color:#5a3e1b">${esc(c.label)}</b></td>
          <td style="color:#6b6152;font-size:12px">${esc((c.desc||s.note||'').slice(0,60))}${(c.desc||'').length>60?'…':''}</td>
          <td style="text-align:right;color:#8a6d2f"><b>${cnt!=null?cnt.toLocaleString():'—'}</b></td></tr>`;
      }).join('');
      detailHost.innerHTML=`<div style="border:1px solid #ece2ca;border-radius:10px;background:#fffdf7;padding:14px 16px">
        <div style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap">
          <span style="font-weight:800;color:#5a3e1b;font-size:15px">${esc(ax.label)} × ${esc(ly.label)}</span>
          <span style="font-size:11px;background:${ax.color}22;color:${ax.color};border-radius:9999px;padding:1px 8px">${esc(axisSel)}</span>
          <span style="font-size:11px;background:${ly.color}22;color:${ly.color};border-radius:9999px;padding:1px 8px">${esc(layerSel)}</span>
          <span class="ortho-chip">类数 <b>${multiCells.length}</b></span>
        </div>
        <div style="font-size:12px;color:#8a7a62;margin-top:6px">${esc(ly.desc||'')}</div>
        <table style="width:100%;border-collapse:collapse;margin-top:10px;font-size:12.5px">
          <thead><tr style="background:#f7f1e3;color:#6b5638"><th style="text-align:left;padding:6px 8px;border-bottom:1px solid #e7ddc8">ID</th><th style="text-align:left;padding:6px 8px;border-bottom:1px solid #e7ddc8">类名</th><th style="text-align:left;padding:6px 8px;border-bottom:1px solid #e7ddc8">说明</th><th style="text-align:right;padding:6px 8px;border-bottom:1px solid #e7ddc8">实例</th></tr></thead>
          <tbody>${rows}</tbody>
        </table></div>`;
      return;
    }
    if(!cid){ detailHost.innerHTML=''; return; }
    const c=D.classes.find(x=>x.id===cid); if(!c){ detailHost.innerHTML=''; return; }
    const s=(SRC.classes&&SRC.classes[c.id])||{};
    const cnt=liveOf(c.id);
    const axs=(c.axes||[]).map(a=>{const x=D.axes.find(y=>y.id===a);return x?`<span style="font-size:11px;background:${x.color}22;color:${x.color};border-radius:9999px;padding:1px 8px;margin-right:4px">${esc(x.label)}</span>`:'';}).join('');
    const ly=D.layers.find(x=>x.id===c.layer);
    // 数据属性
    const matchedProps=(D.properties||[]).filter(p=>{
      if(p.domain&&p.domain[0]==='所有类') return true;
      return p.domain&&p.domain.indexOf(c.id)>=0;
    });
    // 父/子类
    const children=D.classes.filter(x=>x.parent===c.id);
    const parent=c.parent?D.classes.find(x=>x.id===c.parent):null;
    // 关系（in/out）
    const relsOut=D.relations.filter(r=>(r.domain||[]).indexOf(c.id)>=0);
    const relsIn=D.relations.filter(r=>(r.range||[]).indexOf(c.id)>=0);
    const origins=(s.origin||[]).map(o=>`<code style="background:#f4efe3;border-radius:4px;padding:1px 5px;font-size:11px;color:#5a3e1b;margin-right:4px">${esc(o)}</code>`).join('');
    const nav=classNavLinks(c);
    const navHtml=nav.length?'<div style="margin-top:10px"><div style="font-size:11px;color:#8a7a62;margin-bottom:4px">🌐 跳转至站点页面查看实例</div>'
      +'<div style="display:flex;flex-wrap:wrap;gap:6px">'+nav.map(n=>`<a href="${esc(n.href)}" style="display:inline-flex;align-items:center;gap:4px;background:#fff7e0;border:1px solid #e8d08a;border-radius:6px;padding:4px 10px;font-size:12px;color:#8a6d2f;text-decoration:none">→ ${esc(n.label)}</a>`).join('')+'</div></div>':'';

    detailHost.innerHTML=`<div style="border:1px solid #ece2ca;border-radius:10px;background:#fffdf7;padding:14px 16px" class="grid md:grid-cols-2 gap-5">
      <div>
        <div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap">
          <span style="font-weight:800;color:#5a3e1b;font-size:16px">${esc(c.label)}</span>
          <code style="font-size:11px;color:#a2906a">${esc(c.id)}</code>${axs}
          <span style="font-size:11px;background:${ly.color}22;color:${ly.color};border-radius:9999px;padding:1px 8px">${esc(ly.label)}</span>
        </div>
        <div style="font-size:12.5px;color:#6b6152;margin-top:6px;line-height:1.6">${esc(c.desc||s.note||'')}</div>
        ${cnt!=null?`<div style="margin-top:10px;font-size:24px;font-weight:800;color:#8a6d2f;line-height:1">${cnt.toLocaleString()}<span style="font-size:12px;font-weight:500;color:#8a7a62;margin-left:4px">实例</span></div>`:'<div style="margin-top:10px;font-size:12px;color:#8a7a62">结构性/抽象类，无独立实例</div>'}
        ${s.samples&&s.samples.length?'<div style="margin-top:8px"><div style="font-size:11px;color:#8a7a62;margin-bottom:3px">样例</div>'+s.samples.slice(0,8).map(x=>{
          const linkable=['Kepan','Sutra','Vinaya','Sastra','Text'].indexOf(c.id)>=0;
          return linkable?`<a href="sutras.html?load=${esc(x)}" style="text-decoration:none;background:#fbf6ea;border:1px solid #ece2ca;border-radius:6px;padding:2px 8px;margin:2px 4px 2px 0;font-size:11.5px;color:#3E6B4F;display:inline-block">${esc(x)}</a>`:`<span style="background:#fbf6ea;border:1px solid #ece2ca;border-radius:6px;padding:2px 8px;margin:2px 4px 2px 0;font-size:11.5px;color:#5a3e1b;display:inline-block">${esc(x)}</span>`;
        }).join('')+'</div>':''}
        ${navHtml}
        <div style="margin-top:12px">
          ${parent?`<div style="font-size:12px;margin-top:4px"><span style="color:#8a7a62">父类：</span><a href="javascript:void(0)" data-pick="${esc(parent.id)}" style="color:#8a6d2f;text-decoration:underline">${esc(parent.label)}</a> <code style="font-size:10px;color:#a2906a">${esc(parent.id)}</code></div>`:''}
          ${children.length?`<div style="font-size:12px;margin-top:4px"><span style="color:#8a7a62">子类(${children.length})：</span>${children.map(ch=>`<a href="javascript:void(0)" data-pick="${esc(ch.id)}" style="color:#8a6d2f;text-decoration:underline;margin-right:10px">${esc(ch.label)}</a>`).join('')}</div>`:''}
        </div>
      </div>
      <div style="border-left:1px dashed #ece2ca;padding-left:18px">
        <div style="font-size:11px;color:#8a7a62;margin-bottom:3px">数据属性（字段）${matchedProps.length?`<b style="color:#8a6d2f"> ${matchedProps.length}</b> 项`:'（无专属字段）'}</div>
        <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px">
          ${matchedProps.map(p=>`<span title="${esc(p.id)} → ${esc(p.range)}" style="display:inline-block;background:#f4efe3;border-radius:4px;padding:2px 7px;font-size:11px;color:#5a3e1b">${esc(p.label)}<span style="color:#a2906a;font-size:10px;margin-left:3px">${esc(p.range.replace('xsd:',''))}</span></span>`).join('')}
        </div>
        ${relsOut.length?`<div style="font-size:11px;color:#8a7a62;margin-bottom:3px">作为 domain 关联（${relsOut.length}）</div><div style="margin-bottom:8px">${relsOut.map(r=>{const col=GROUP_COLORS[r.group]||'#888';return `<div style="font-size:12px;margin-bottom:3px"><span style="color:${col};font-weight:600">${esc(r.label)}</span> → ${(r.range||[]).map(t=>`<a href="javascript:void(0)" data-pick="${esc(t)}" style="color:#5a3e1b;text-decoration:underline;margin:0 3px">${esc(parentLabel(t))}</a>`).join('')}</div>`;}).join('')}</div>`:''}
        ${relsIn.length?`<div style="font-size:11px;color:#8a7a62;margin-bottom:3px">作为 range 被关联（${relsIn.length}）</div><div>${relsIn.slice(0,8).map(r=>{const col=GROUP_COLORS[r.group]||'#888';return `<div style="font-size:12px;margin-bottom:3px">${(r.domain||[]).map(t=>`<a href="javascript:void(0)" data-pick="${esc(t)}" style="color:#5a3e1b;text-decoration:underline;margin:0 3px">${esc(parentLabel(t))}</a>`).join('')}<span style="color:${col};font-weight:600"> —${esc(r.label)}→</span> <b>${esc(c.label)}</b></div>`;}).join('')}${relsIn.length>8?`<div style="font-size:11px;color:#a2906a">…等 ${relsIn.length} 条</div>`:''}</div>`:''}
        <div style="margin-top:10px"><div style="font-size:11px;color:#8a7a62;margin-bottom:3px">数据来源</div><div>${origins||'<span style="font-size:12px;color:#a2906a">—</span>'}</div></div>
        <div style="margin-top:8px"><div style="font-size:11px;color:#8a7a62;margin-bottom:3px">存放位置</div><div style="font-size:12px;color:#5a3e1b">${esc(s.storage||'—')}</div></div>
        ${s.generator?`<div style="margin-top:6px"><div style="font-size:11px;color:#8a7a62;margin-bottom:3px">生成脚本</div><div style="font-size:12px;color:#5a3e1b">${esc(s.generator)}</div></div>`:''}
      </div>
    </div>`;
    // 绑定点击跳转
    detailHost.querySelectorAll('a[data-pick]').forEach(a=>{
      a.addEventListener('click',()=>{ selectId(a.dataset.pick); });
    });
  }

  // ===== 属性节点详情卡（对象属性 / 数据属性） =====
  const CODE='display:inline-block;background:#f4efe3;border-radius:4px;padding:1px 6px;font-size:11px;color:#5a3e1b;margin:2px 2px 2px 0;word-break:break-all';
  const PICK='color:#8a6d2f;text-decoration:underline;margin:0 3px';
  const NODE_LINK='display:inline-block;background:#fff7e0;border:1px solid #e8d08a;border-radius:6px;padding:2px 9px;font-size:11.5px;color:#8a6d2f;text-decoration:none;margin:2px 4px 2px 0';

  function renderRelDetail(relId){
    if(!detailHost) return;
    const r=D.relations.find(x=>x.id===relId);
    if(!r){ detailHost.innerHTML=''; return; }
    const col=GROUP_COLORS[r.group]||'#888';
    const ax=D.axes.find(a=>a.id===r.axis);
    const link=(t)=>`<a href="javascript:void(0)" data-pick="${esc(t)}" style="${PICK}">${esc(parentLabel(t))}</a>`;
    const domLinks=(r.domain||[]).map(link).join(' ');
    const rngLinks=(r.range||[]).map(link).join(' ');
    const aliases=(r.aliases&&r.aliases.length)?r.aliases.map(a=>`<code style="${CODE}">${esc(a)}</code>`).join(''):'<span style="font-size:12px;color:#a2906a">—</span>';
    const origins=(r.origin||[]).map(o=>`<code style="${CODE}">${esc(o)}</code>`).join('');
    const sameGroup=D.relations.filter(x=>x.group===r.group && x.id!==r.id);
    const sameHtml=sameGroup.map(x=>`<a href="javascript:void(0)" data-relpick="${esc(x.id)}" style="${NODE_LINK}">${esc(x.label)}</a>`).join('')||'<span style="font-size:12px;color:#a2906a">—</span>';
    detailHost.innerHTML=`<div style="border:1px solid #ece2ca;border-radius:10px;background:#fffdf7;padding:14px 16px" class="grid md:grid-cols-2 gap-5">
      <div>
        <div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap">
          <span style="font-weight:800;color:#5a3e1b;font-size:16px">${esc(r.label)}</span>
          <code style="font-size:11px;color:#a2906a">${esc(r.id)}</code>
          <span style="font-size:11px;background:${col}22;color:${col};border-radius:9999px;padding:1px 8px">对象属性</span>
          ${ax?`<span style="font-size:11px;background:${ax.color}22;color:${ax.color};border-radius:9999px;padding:1px 8px">${esc(ax.id)} · ${esc(ax.label)}</span>`:''}
        </div>
        <div style="font-size:12.5px;color:#6b6152;margin-top:6px;line-height:1.6">${esc(r.description||'（未收录释义）')}</div>
        <div style="margin-top:10px;font-size:12.5px;line-height:2">
          <div><span style="color:#8a7a62">关系组：</span><span style="color:${col};font-weight:600">${esc(r.group)}</span></div>
          <div><span style="color:#8a7a62">定义域 domain：</span>${domLinks||'<span style="color:#a2906a">待定义</span>'}</div>
          <div><span style="color:#8a7a62">值域 range：</span>${rngLinks||'<span style="color:#a2906a">待定义</span>'}</div>
          <div><span style="color:#8a7a62">逆向属性 inverse：</span>${r.inverse?`<code style="${CODE}">${esc(r.inverse)}</code>`:'<span style="color:#a2906a">—</span>'} ｜ <span style="color:#8a7a62">对称 symmetric：</span>${r.symmetric?'<b style="color:#3E6B4F">是</b>':'否'}</div>
          <div><span style="color:#8a7a62">别名 aliases：</span>${aliases}</div>
        </div>
      </div>
      <div style="border-left:1px dashed #ece2ca;padding-left:18px">
        <div style="font-size:11px;color:#8a7a62;margin-bottom:3px">同组对象属性（${sameGroup.length}）</div>
        <div style="margin-bottom:10px">${sameHtml}</div>
        <div style="font-size:11px;color:#8a7a62;margin-bottom:3px">数据来源</div>
        <div style="margin-bottom:8px">${origins||'<span style="font-size:12px;color:#a2906a">—</span>'}</div>
        <div style="font-size:11px;color:#8a7a62;margin-bottom:3px">存放位置</div>
        <div style="font-size:12px;color:#5a3e1b;margin-bottom:8px">${esc(r.storage||'—')}</div>
        <div style="font-size:11px;color:#8a7a62;margin-bottom:3px">生成脚本</div>
        <div style="font-size:12px;color:#5a3e1b">${esc(r.generator||'—')}</div>
      </div>
    </div>`;
    detailHost.querySelectorAll('a[data-pick]').forEach(a=>a.addEventListener('click',()=>selectId(a.dataset.pick)));
    detailHost.querySelectorAll('a[data-relpick]').forEach(a=>a.addEventListener('click',()=>selectRel(a.dataset.relpick)));
  }

  function renderPropDetail(propId){
    if(!detailHost) return;
    const p=(D.properties||[]).find(x=>x.id===propId);
    if(!p){ detailHost.innerHTML=''; return; }
    const domAll=(p.domain||[]).some(d=>d==='all'||d==='所有类');
    const domClasses=(p.domain||[]).filter(d=>d!=='all'&&d!=='所有类');
    const covered=domAll?D.classes.length:domClasses.filter(d=>D.classes.some(c=>c.id===d)).length;
    const domLinks=domAll?'<span style="font-size:12px;color:#5a3e1b;font-weight:600">全部本体类（通用字段）</span>'
      :(domClasses.map(d=>`<a href="javascript:void(0)" data-pick="${esc(d)}" style="${PICK}">${esc(parentLabel(d))}</a>`).join(' ')||'<span style="color:#a2906a">—</span>');
    const origins=(p.origin||[]).map(o=>`<code style="${CODE}">${esc(o)}</code>`).join('');
    const AXMAP={Text:'A1',Edition:'A1',SourceLanguage:'A1',TranslationEra:'A1',Vehicle:'A1',Mode:'A1',School:'A1',ThreeBaskets:'A1',CanonCategory:'A1',Division:'A1',Genre:'A1',
      Chapter:'A2',Section:'A2',Gatha:'A2',Mantra:'A2',Concept:'A2',Doctrine:'A2',Practice:'A2',Kepan:'A2',Commentary:'A2',
      Person:'A3',Buddha:'A3',Bodhisattva:'A3',Translator:'A3',Protector:'A3',Deity:'A3',
      Event:'A4',DharmaAssembly:'A4',Council:'A4',TransmissionEvent:'A4',StoryEvent:'A4'};
    const axis=D.axes.find(a=>AXMAP[domClasses[0]]===a.id);
    detailHost.innerHTML=`<div style="border:1px solid #ece2ca;border-radius:10px;background:#fffdf7;padding:14px 16px" class="grid md:grid-cols-2 gap-5">
      <div>
        <div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap">
          <span style="font-weight:800;color:#5a3e1b;font-size:16px">${esc(p.label)}</span>
          <code style="font-size:11px;color:#a2906a">${esc(p.id)}</code>
          <span style="font-size:11px;background:#5A7FA822;color:#5A7FA8;border-radius:9999px;padding:1px 8px">数据属性</span>
          ${axis?`<span style="font-size:11px;background:${axis.color}22;color:${axis.color};border-radius:9999px;padding:1px 8px">${esc(axis.id)} · ${esc(axis.label)}</span>`:''}
        </div>
        <div style="font-size:12.5px;color:#6b6152;margin-top:6px;line-height:1.6">${esc(p.description||'（未收录释义）')}</div>
        <div style="margin-top:10px;font-size:12.5px;line-height:2">
          <div><span style="color:#8a7a62">挂接类 domain：</span>${domLinks}</div>
          <div><span style="color:#8a7a62">值域 range：</span><code style="${CODE}">${esc(String(p.range))}</code></div>
          <div><span style="color:#8a7a62">覆盖本体类：</span><b style="color:#8a6d2f">${covered}</b> 类</div>
        </div>
      </div>
      <div style="border-left:1px dashed #ece2ca;padding-left:18px">
        <div style="font-size:11px;color:#8a7a62;margin-bottom:3px">数据来源</div>
        <div style="margin-bottom:8px">${origins||'<span style="font-size:12px;color:#a2906a">—</span>'}</div>
        <div style="font-size:11px;color:#8a7a62;margin-bottom:3px">存放位置</div>
        <div style="font-size:12px;color:#5a3e1b;margin-bottom:8px">${esc(p.storage||'—')}</div>
        <div style="font-size:11px;color:#8a7a62;margin-bottom:3px">生成脚本</div>
        <div style="font-size:12px;color:#5a3e1b">${esc(p.generator||'—')}</div>
        <div style="margin-top:8px;font-size:11px;color:#a2906a">提示：切换到「数据属性（字段覆盖）」视图，可查看每类挂接了本字段的矩阵。</div>
      </div>
    </div>`;
    detailHost.querySelectorAll('a[data-pick]').forEach(a=>a.addEventListener('click',()=>selectId(a.dataset.pick)));
  }

  function parentLabel(pid){const p=D.classes.find(x=>x.id===pid); return p?p.label:pid;}

  // ===== 类 → 页面跳转映射 =====
  function classNavLinks(c){
    const id=c.id, ax=(c.axes&&c.axes[0])||'';
    const map={
      CanonCategory:[{href:'categories.html',label:'部类总览'},{href:'sutras.html',label:'全藏原典'}],
      ThreeBaskets:[{href:'categories.html',label:'三藏分类'}],
      Tripitaka:[{href:'categories.html',label:'三藏分类'}],
      Vehicle:[{href:'panjiao.html',label:'乘与判教'}],
      Mode:[{href:'panjiao.html',label:'显密判教'}],
      Genre:[{href:'categories.html',label:'十二分教'}],
      Division:[{href:'sutras.html',label:'三分结构'}],
      Edition:[{href:'translation.html',label:'版本源流'}],
      SourceLanguage:[{href:'translation.html',label:'译学·原典语言'}],
      TranslationEra:[{href:'translation.html',label:'译学·时代'}],
      School:[{href:'panjiao.html',label:'宗派判教'}],
      Sect:[{href:'panjiao.html',label:'汉传八宗'}],
      Practice:[{href:'graph.html#view=m2',label:'法门行持'}],
      PanjiaoSystem:[{href:'panjiao.html',label:'判教体系'}],
      Kepan:[{href:'kepan.html',label:'科判导航'}],
      Text:[{href:'sutras.html',label:'全藏原典'}],
      Sutra:[{href:'sutras.html',label:'经藏'}],
      Vinaya:[{href:'sutras.html',label:'律藏'}],
      Sastra:[{href:'sutras.html',label:'论藏'}],
      Chapter:[{href:'sutras.html',label:'章节浏览'}],
      Section:[{href:'search.html',label:'段落检索'}],
      Gatha:[{href:'sutras.html',label:'偈颂浏览'}],
      Mantra:[{href:'sutras.html',label:'咒语浏览'}],
      Doctrine:[{href:'graph.html',label:'义理图谱'},{href:'dict.html',label:'佛学词典'}],
      CoreDoctrine:[{href:'graph.html',label:'核心教义'},{href:'inference.html',label:'概念推演'}],
      Pratitya:[{href:'inference.html',label:'缘起推演'}],
      Sunyata:[{href:'inference.html',label:'空性推演'}],
      BuddhaNature:[{href:'inference.html',label:'佛性推演'}],
      Person:[{href:'graph.html#view=m2',label:'人物索引'},{href:'timeline.html',label:'译传时间轴'}],
      Buddha:[{href:'graph.html#view=m2',label:'佛陀'}],
      Bodhisattva:[{href:'graph.html#view=m2',label:'菩萨'}],
      Arhat:[{href:'graph.html#view=m2',label:'阿罗汉'}],
      Patriarch:[{href:'timeline.html',label:'祖师传法'},{href:'translation.html',label:'译师'}],
      Translator:[{href:'translation.html',label:'译师'},{href:'timeline.html',label:'时间轴'}],
      ModernScholar:[{href:'graph.html#view=m2',label:'学者'}],
      Protector:[{href:'graph.html#view=m2',label:'护法诸天'}],
      Deity:[{href:'graph.html#view=m2',label:'神祇'}],
      Event:[{href:'timeline.html',label:'事件时间轴'}],
      DharmaAssembly:[{href:'timeline.html',label:'法会'}],
      Council:[{href:'timeline.html',label:'结集'}],
      TransmissionEvent:[{href:'timeline.html',label:'译经传法'}],
      StoryEvent:[{href:'timeline.html',label:'本生故事'}],
      FolkFigure:[{href:'graph.html#view=folklore',label:'民间信仰'}]
    };
    if(map[id]) return map[id];
    const fb=[];
    if(ax==='A1') fb.push({href:'categories.html',label:'部类'});
    if(ax==='A2') fb.push({href:'graph.html',label:'义理图谱'});
    if(ax==='A3') fb.push({href:'graph.html#view=m2',label:'人物'});
    if(ax==='A4') fb.push({href:'timeline.html',label:'时间轴'});
    const seen={}; return fb.filter(x=>!seen[x.href]&&(seen[x.href]=1)).slice(0,3);
  }

  // ===== tooltip helpers =====
  function showTip(ev,html){tooltip.style('display','block').html(html); moveTip(ev);}
  function moveTip(ev){let x=ev.clientX+16,y=ev.clientY+16; if(x+370>window.innerWidth)x=ev.clientX-380; if(y+220>window.innerHeight)y=ev.clientY-230; tooltip.style('left',x+'px').style('top',y+'px');}
  function hideTip(){tooltip.style('display','none');}

  function renderLegend(){
    const host=q('#ortho-legend'); if(!host) return;
    host.innerHTML=`<div class="flex flex-wrap gap-3 text-[11px] text-buddha-dark/70 items-center" style="justify-content:center">
      <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#B8860B;margin-right:3px"></span>分类轴(A1)</span>
      <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#3E6B4F;margin-right:3px"></span>内容轴(A2)</span>
      <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#8B5A2B;margin-right:3px"></span>人物轴(A3)</span>
      <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#A23B3B;margin-right:3px"></span>事件轴(A4)</span>
      <span style="margin-left:8px"><span style="display:inline-block;width:26px;height:0;border-top:2px dashed #888;margin-right:3px;vertical-align:middle"></span>对象属性（domain→range）</span>
      <span><span style="display:inline-block;width:14px;height:14px;border:2px solid #fff;box-shadow:0 0 0 1px #888;border-radius:50%;margin-right:3px;vertical-align:middle"></span>本体类（大=顶层 小=子类）</span>
      <span>🖱 点击任一<b>彩色虚线</b>查看该<b>对象属性</b>详情；切到「数据属性」视图点击<b>列头 / 方块</b>查看<b>数据属性</b>详情</span>
      <span>🔍 鼠标滚轮缩放 · 拖拽平移 · 点击节点/轴/层高亮 · 双击空白重置</span>
    </div>`;
  }

  function hash(s){let h=0;for(let i=0;i<s.length;i++){h=((h<<5)-h)+s.charCodeAt(i);h|=0;}return 'g'+Math.abs(h).toString(36);}

  // 暴露
  window.OntologyOrtho={init};
  // 暴露原 OntologyTBox 的空壳以防其他地方调用报错（但页面里 setTimeout 要改成调用新的）
  window.OntologyTBox={init(opts){OntologyOrtho.init();}};
})();

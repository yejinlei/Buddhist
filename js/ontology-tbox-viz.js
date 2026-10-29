/* 本体总纲 TBox 正交矩阵 + 类关系网络图
 * 纯 SVG/JS 实现，零依赖。
 */
(function(){
  'use strict';

  const COLORS = {
    A1:'#B8860B', A2:'#3E6B4F', A3:'#8B5A2B', A4:'#A23B3B',
    L0:'#4a4a4a', L1:'#6b5638', L2:'#8a7a62', L3:'#B8860B',
    L4:'#3E6B4F', L5:'#8B5A2B', L6:'#A23B3B'
  };
  const LAYER_Y = {L0:70,L1:150,L2:230,L3:310,L4:420,L5:520,L6:600};
  const AXIS_X  = {A1:200,A2:470,A3:740,A4:1010};
  const COLS=['A1','A2','A3','A4'];
  const ROWS=['L0','L1','L2','L3','L4','L5','L6'];

  let D=null;       // tbox data
  let state={filterAxis:null,filterLayer:null,filterClass:null,hoverCell:null,hoverNode:null,hoverRel:null};
  let onFilterCb=null;

  function q(s){return document.querySelector(s)}

  // ========== 1) 加载数据 ==========
  function loadData(cb){
    fetch('../ontology/tbox_data.json')
      .then(r=>r.json())
      .then(d=>{D=d;cb(d)})
      .catch(e=>{ console.error('tbox_data.json 加载失败',e); });
  }

  // ========== 2) 正交矩阵热力图 ==========
  function renderMatrix(){
    const root=q('#tbox-matrix'); if(!root) return;
    const W=680,H=380,pad={t:60,r:40,b:80,l:120};
    root.innerHTML='';
    const svg=ns('svg',{width:W,height:H,viewBox:`0 0 ${W} ${H}`});
    root.appendChild(svg);

    const cw=(W-pad.l-pad.r)/4;
    const ch=(H-pad.t-pad.b)/7;

    // 标题
    svg.appendChild(ns('text',{x:W/2,y:24,'text-anchor':'middle','font-size':15,'font-weight':700,fill:'#5a3e1b'}))
       .textContent='四轴 × 七层 正交矩阵（格子颜色/数字 = 该格所定义的本体类数）';
    svg.appendChild(ns('text',{x:W/2,y:44,'text-anchor':'middle','font-size':11.5,fill:'#8a7a62'}))
       .textContent='点击行/列/格可筛选下方类树；再次点击取消筛选';

    // 轴头（上）
    D.axes.forEach((a,i)=>{
      const x=pad.l+i*cw+cw/2;
      const g=ns('g',{class:'axis-head','data-axis':a.id,cursor:'pointer'});
      g.appendChild(rect(pad.l+i*cw+4,pad.t-38,cw-8,30,8,a.color+'22',a.color));
      g.appendChild(text(x,pad.t-19,a.label,13,'700',a.color,'middle'));
      svg.appendChild(g);
      g.addEventListener('click',()=>toggleFilter('filterAxis',a.id));
    });
    // 层头（左）
    D.layers.forEach((l,i)=>{
      const y=pad.t+i*ch+ch/2;
      const g=ns('g',{class:'layer-head','data-layer':l.id,cursor:'pointer'});
      g.appendChild(rect(pad.l-100,pad.t+i*ch+4,96,ch-8,6,l.color+'22',l.color));
      g.appendChild(text(pad.l-52,y,l.label,12,'600',l.color,'middle'));
      svg.appendChild(g);
      g.addEventListener('click',()=>toggleFilter('filterLayer',l.id));
    });

    // 构建格子：统计每个(ax,ly)的类
    const cellMap={};
    D.classes.forEach(c=>{
      (c.axes||[]).forEach(a=>{
        const k=a+'|'+c.layer;
        if(!cellMap[k]) cellMap[k]=[];
        cellMap[k].push(c);
      });
    });
    let maxN=1;
    Object.values(cellMap).forEach(arr=>{if(arr.length>maxN)maxN=arr.length});

    // 画格子
    COLS.forEach((a,i)=>{
      ROWS.forEach((l,j)=>{
        const k=a+'|'+l, cs=cellMap[k]||[];
        const x=pad.l+i*cw, y=pad.t+j*ch;
        const n=cs.length;
        const ratio=n?0.22+0.78*(n/maxN):0;
        const bg=n?hexMix('#f5ead2',COLORS[a],ratio):'#f7f3ea';
        const stroke='#d9cdb4';
        const g=ns('g',{class:'cell','data-key':k,cursor:'pointer'});
        g.appendChild(rect(x+2,y+2,cw-4,ch-4,6,bg,stroke));
        if(n){
          g.appendChild(text(x+cw/2,y+ch/2-2,String(n),n>=5?20:16,'800',n>=3?'#fff':'#5a3e1b','middle'));
          // 类名列
          const lab=cs.slice(0,2).map(c=>c.label).join('、')+(cs.length>2?' …':'');
          const t=text(x+cw/2,y+ch/2+14,lab,10,'500',n>=3?'#fff8e0':'#8a7a62','middle');
          g.appendChild(t);
        }else{
          g.appendChild(text(x+cw/2,y+ch/2,'—',14,'400','#c9bda5','middle'));
        }
        g.addEventListener('mouseenter',()=>showTooltip(k,cs));
        g.addEventListener('mousemove',moveTooltip);
        g.addEventListener('mouseleave',hideTooltip);
        g.addEventListener('click',()=>{
          if(state.filterAxis===a && state.filterLayer===l){
            state.filterAxis=null;state.filterLayer=null;
          }else{state.filterAxis=a; state.filterLayer=l;}
          state.filterClass=null;
          applyFilter();
        });
        svg.appendChild(g);
      });
    });

    // 图例
    const lg=ns('g');
    for(let k=0;k<=4;k++){
      const xx=pad.l+k*32;
      const yy=H-22;
      const ratio=k/4;
      lg.appendChild(rect(xx,yy,30,12,2,hexMix('#f5ead2','#B8860B',ratio),'none'));
    }
    lg.appendChild(text(pad.l,H-8,'空',10,'400','#8a7a62','middle'));
    lg.appendChild(text(pad.l+4*32,H-8,'密集',10,'400','#8a7a62','middle'));
    svg.appendChild(lg);

    // 重置按钮
    const rst=ns('g',{cursor:'pointer'});
    rst.appendChild(rect(W-100,H-42,80,24,12,'#fff6e0','#B8860B'));
    rst.appendChild(text(W-60,H-25,'重置筛选',11,'600','#B8860B','middle'));
    rst.addEventListener('click',()=>{state.filterAxis=null;state.filterLayer=null;state.filterClass=null;applyFilter();});
    svg.appendChild(rst);
  }

  // ========== 3) 类关系网络图（分轴分层布局） ==========
  function renderGraph(){
    const root=q('#tbox-graph'); if(!root) return;
    const W=1240,H=720,pad={t:50,r:40,b:40,l:160};
    root.innerHTML='';
    const svg=ns('svg',{width:'100%',viewBox:`0 0 ${W} ${H}`,style:'max-height:720px'});
    root.appendChild(svg);

    // 背景层/轴参考线
    ROWS.forEach((l,i)=>{
      const y=LAYER_Y[l];
      const line=ns('line',{x1:pad.l,x2:W-pad.r,y1:y,y2:y,stroke:'#ece2ca','stroke-dasharray':'4 4','stroke-width':1});
      svg.appendChild(line);
      const t=ns('text',{x:pad.l-12,y:y+4,'text-anchor':'end','font-size':11.5,fill:COLORS[l],'font-weight':600});
      t.textContent=D.layers.find(x=>x.id===l).label;
      svg.appendChild(t);
    });
    COLS.forEach((a,i)=>{
      const x=AXIS_X[a];
      const t=ns('text',{x:x,y:pad.t-20,'text-anchor':'middle','font-size':13,fill:COLORS[a],'font-weight':700});
      t.textContent=D.axes.find(x=>x.id===a).label;
      svg.appendChild(t);
      const rect_bg=ns('rect',{x:x-120,y:pad.t-8,width:240,height:H-pad.t-pad.b,rx:12,fill:COLORS[a]+'08'});
      svg.insertBefore(rect_bg,svg.firstChild);
    });

    // 给每个类分配坐标（同轴同层内横向错位）
    const byCell={};
    D.classes.forEach(c=>{
      (c.axes||[]).forEach(a=>{
        if(!AXIS_X[a])return;
        const k=a+'|'+c.layer;
        if(!byCell[k]) byCell[k]=[];
        byCell[k].push(c);
      });
    });
    const nodes={};
    Object.keys(byCell).forEach(k=>{
      const arr=byCell[k];
      const [a,l]=k.split('|');
      const x0=AXIS_X[a];
      const y0=LAYER_Y[l];
      const span=Math.min(220, 30*arr.length+20);
      arr.forEach((c,i)=>{
        if(nodes[c.id]) return;
        const x=x0-span/2 + (span/(arr.length||1))*(i+0.5);
        const y=y0 + (arr.length%2===0? (i-arr.length/2+0.5)*6 : (i-Math.floor(arr.length/2))*6);
        nodes[c.id]={x,y,c};
      });
    });

    // 画连线：先画 subclassOf/is-a 继承链（深灰实线），再画 object 关系（彩色虚线/贝塞尔）
    const edges=[];
    // 1. 继承 parent→child
    D.classes.forEach(c=>{
      if(c.parent && nodes[c.parent] && nodes[c.id]){
        edges.push({type:'isa',from:c.parent,to:c.id,label:'subClassOf'});
      }
    });
    // 2. 属性/关系：domain/range 连线（只对顶层已实例节点）
    function resolveCls(n){ return nodes[n]?n:null; }
    D.relations.forEach(r=>{
      r.domain.forEach(d=>{
        r.range.forEach(ra=>{
          const dN=resolveCls(d), raN=resolveCls(ra);
          if(dN && raN && dN!==raN){
            edges.push({type:'rel',from:dN,to:raN,rel:r,label:r.label});
          }
        });
      });
    });

    const edgeG=ns('g');
    edges.forEach(e=>{
      const a=nodes[e.from], b=nodes[e.to];
      if(!a||!b)return;
      const p=ns('path');
      if(e.type==='isa'){
        p.setAttribute('d',`M${a.x},${a.y+12} C${a.x},${(a.y+b.y)/2} ${b.x},${(a.y+b.y)/2} ${b.x},${b.y-14}`);
        p.setAttribute('stroke','#9e8c6a');
        p.setAttribute('stroke-width','1.5');
        p.setAttribute('fill','none');
        p.setAttribute('stroke-dasharray','none');
      }else{
        const col=relColor(e.rel.group);
        p.setAttribute('d',`M${a.x+10},${a.y} Q${(a.x+b.x)/2},${(a.y+b.y)/2-18} ${b.x-10},${b.y}`);
        p.setAttribute('stroke',col);
        p.setAttribute('stroke-width','1.3');
        p.setAttribute('fill','none');
        p.setAttribute('stroke-dasharray','4 3');
        p.setAttribute('opacity','0.55');
      }
      p.dataset.from=e.from; p.dataset.to=e.to; p.dataset.type=e.type;
      if(e.rel) p.dataset.group=e.rel.group;
      p.style.cursor='pointer';
      p.addEventListener('mouseenter',()=>{p.setAttribute('stroke-width','2.6');p.setAttribute('opacity','0.95');showRelTip(e,a,b);});
      p.addEventListener('mousemove',moveTooltip);
      p.addEventListener('mouseleave',()=>{p.setAttribute('stroke-width',e.type==='isa'?'1.5':'1.3');p.setAttribute('opacity',e.type==='isa'?'1':'0.55');hideTooltip();});
      edgeG.appendChild(p);
    });
    svg.appendChild(edgeG);

    // 画节点
    const nodeG=ns('g');
    D.classes.forEach(c=>{
      const n=nodes[c.id]; if(!n) return;
      const ax=(c.axes&&c.axes[0])||'A1';
      const col=COLORS[ax]||'#888';
      const r=c.parent?11:13;
      const g=ns('g',{cursor:'pointer','data-cls':c.id,transform:`translate(${n.x},${n.y})`});
      const circle=ns('circle',{cx:0,cy:0,r,fill:c.parent?col+'cc':col,stroke:'#fff','stroke-width':2});
      if(!c.parent) circle.setAttribute('stroke-dasharray','0');
      g.appendChild(circle);
      const lbl=ns('text',{x:0,y:r+12,'text-anchor':'middle','font-size':10.5,fill:'#4a3a1e','font-weight':c.parent?500:700});
      lbl.textContent=c.label;
      g.appendChild(lbl);
      g.addEventListener('mouseenter',()=>{circle.setAttribute('r',r+3);showClsTip(c,n);});
      g.addEventListener('mousemove',moveTooltip);
      g.addEventListener('mouseleave',()=>{circle.setAttribute('r',r);hideTooltip();});
      g.addEventListener('click',()=>{state.filterClass=(state.filterClass===c.id?null:c.id);applyFilter();});
      nodeG.appendChild(g);
    });
    svg.appendChild(nodeG);

    // 图例（关系颜色）
    const groups={};
    edges.filter(e=>e.type==='rel').forEach(e=>{if(e.rel)groups[e.rel.group]=relColor(e.rel.group)});
    let lgx=pad.l+20, lgy=H-20;
    Object.keys(groups).forEach((g,i)=>{
      const col=groups[g];
      svg.appendChild(lineE(lgx,lgy,lgx+24,lgy,col,'4 3',1.6));
      const t=ns('text',{x:lgx+28,y:lgy+4,'font-size':10.5,fill:'#5a3e1b'});
      t.textContent=g;
      svg.appendChild(t);
      lgx += 28+ g.length*11 + 24;
    });
    // isa 图例
    svg.appendChild(lineE(lgx,lgy,lgx+24,lgy,'#9e8c6a','none',1.6));
    const isaT=ns('text',{x:lgx+28,y:lgy+4,'font-size':10.5,fill:'#5a3e1b'});
    isaT.textContent='subClassOf（继承）';
    svg.appendChild(isaT);
  }

  function relColor(g){
    if(!g) return '#888';
    if(g.includes('分类'))return '#B8860B';
    if(g.includes('文本'))return '#3E6B4F';
    if(g.includes('宗派'))return '#C07830';
    if(g.includes('人物'))return '#8B5A2B';
    if(g.includes('事件'))return '#A23B3B';
    return '#7a6a52';
  }

  // ========== 筛选联动 ==========
  function toggleFilter(key,val){
    state[key]=(state[key]===val?null:val);
    state.filterClass=null;
    applyFilter();
  }
  function applyFilter(){
    // 高亮矩阵格
    document.querySelectorAll('#tbox-matrix .cell rect').forEach(r=>{r.setAttribute('opacity','1')});
    document.querySelectorAll('#tbox-matrix .cell text').forEach(t=>{t.setAttribute('opacity','1')});
    document.querySelectorAll('#tbox-matrix .cell').forEach(g=>{
      const k=g.dataset.key; const [a,l]=k.split('|');
      let show=true;
      if(state.filterAxis && a!==state.filterAxis) show=false;
      if(state.filterLayer && l!==state.filterLayer) show=false;
      g.setAttribute('opacity',show?'1':'0.2');
    });
    // 高亮轴/层头
    document.querySelectorAll('#tbox-matrix .axis-head').forEach(g=>{
      const a=g.dataset.axis;
      g.querySelector('rect').setAttribute('stroke-width',state.filterAxis===a?'2.5':'1');
    });
    document.querySelectorAll('#tbox-matrix .layer-head').forEach(g=>{
      const l=g.dataset.layer;
      g.querySelector('rect').setAttribute('stroke-width',state.filterLayer===l?'2.5':'1');
    });
    // 图节点高亮
    document.querySelectorAll('#tbox-graph [data-cls]').forEach(g=>{
      const cid=g.dataset.cls;
      const c=D.classes.find(x=>x.id===cid); if(!c)return;
      let show=true;
      if(state.filterAxis && !(c.axes||[]).includes(state.filterAxis)) show=false;
      if(state.filterLayer && c.layer!==state.filterLayer) show=false;
      if(state.filterClass && cid!==state.filterClass && c.parent!==state.filterClass){
        // 仍显示，但淡化（除非是选中或其子类）
        // 进一步：保留直接连线的节点
        const connected=isConnected(cid,state.filterClass);
        show=connected;
      }
      g.setAttribute('opacity',show?'1':'0.15');
    });
    document.querySelectorAll('#tbox-graph path').forEach(p=>{
      let show=true;
      if(state.filterClass){
        show=(p.dataset.from===state.filterClass||p.dataset.to===state.filterClass);
      }
      p.setAttribute('opacity',show?(p.dataset.type==='isa'?'1':'0.55'):'0.06');
    });
    // 通知外部（筛选下方类树）
    if(onFilterCb) onFilterCb(state);
  }
  function isConnected(a,b){
    if(a===b)return true;
    // 简化：查找是否有边直接相连
    const edges=document.querySelectorAll('#tbox-graph path');
    for(const p of edges){
      if((p.dataset.from===a&&p.dataset.to===b)||(p.dataset.from===b&&p.dataset.to===a))return true;
    }
    return false;
  }

  // ========== 提示 ==========
  let tip;
  function ensureTip(){
    tip=q('#tbox-tip');
    if(!tip){
      tip=document.createElement('div');
      tip.id='tbox-tip';
      Object.assign(tip.style,{
        position:'fixed',pointerEvents:'none',background:'rgba(43,30,12,0.95)',color:'#fdf6e3',
        padding:'8px 12px',borderRadius:'8px',fontSize:'12.5px',maxWidth:'320px',lineHeight:'1.5',
        boxShadow:'0 8px 20px rgba(0,0,0,0.25)',zIndex:9999,display:'none'
      });
      document.body.appendChild(tip);
    }
    return tip;
  }
  function showTooltip(k,cs){
    const [a,l]=k.split('|');
    const ax=D.axes.find(x=>x.id===a),ly=D.layers.find(x=>x.id===l);
    const t=ensureTip();
    t.innerHTML=`<div style="font-weight:700;color:#D4AF37;margin-bottom:4px">${ax.label} × ${ly.label}</div>
      <div style="opacity:.8;margin-bottom:4px">${ly.desc}</div>
      ${cs.length?`<div>共 <b>${cs.length}</b> 个类：${cs.map(c=>c.label).join('、')}</div>`:'<div style="opacity:.6">（此格无直接定义类）</div>'}`;
    t.style.display='block';
  }
  function showClsTip(c,n){
    const t=ensureTip();
    const axs=(c.axes||[]).map(a=>{
      const ax=D.axes.find(x=>x.id===a);return ax?`<span style="color:${ax.color};font-weight:600">${ax.label}</span>`:a;
    }).join(' / ');
    const ly=D.layers.find(x=>x.id===c.layer);
    t.innerHTML=`<div style="font-weight:700;color:#D4AF37;margin-bottom:4px">${c.label} <span style="color:#b4a77a;font-weight:400;font-size:11px">(${c.id})</span></div>
      <div style="opacity:.85;margin-bottom:4px">轴：${axs} ｜ 层：<b style="color:${ly?ly.color:'#aaa'}">${ly?ly.label:c.layer}</b>${c.parent?`｜ 父类：${parentLabel(c.parent)}`:''}</div>
      <div style="opacity:.9">${c.desc||''}</div>
      <div style="opacity:.6;margin-top:6px;font-size:11px">点击高亮该节点及其直接连线</div>`;
    t.style.display='block';
  }
  function showRelTip(e,a,b){
    const t=ensureTip();
    if(e.type==='isa'){
      t.innerHTML=`<b style="color:#D4AF37">继承（subClassOf）</b><br><span>${b.c.label}</span> 是 <span>${a.c.label}</span> 的子类`;
    }else{
      const col=relColor(e.rel.group);
      t.innerHTML=`<b style="color:${col}">${e.rel.label}</b> <span style="opacity:.7">（${e.rel.group||'关系'}）</span><br>
        domain: <b>${e.from}</b> → range: <b>${e.to}</b><br>
        <div style="opacity:.8;margin-top:4px">${e.rel.id}</div>`;
    }
    t.style.display='block';
  }
  function parentLabel(pid){
    const p=D.classes.find(x=>x.id===pid); return p?p.label:pid;
  }
  function moveTooltip(ev){
    const t=ensureTip();
    let x=ev.clientX+16,y=ev.clientY+16;
    if(x+330>window.innerWidth) x=ev.clientX-340;
    if(y+200>window.innerHeight) y=ev.clientY-210;
    t.style.left=x+'px'; t.style.top=y+'px';
  }
  function hideTooltip(){ const t=ensureTip(); t.style.display='none'; }

  // ========== SVG helper ==========
  function ns(tag,attrs){
    const el=document.createElementNS('http://www.w3.org/2000/svg',tag);
    if(attrs) for(const k in attrs) el.setAttribute(k,attrs[k]);
    return el;
  }
  function rect(x,y,w,h,rx,fill,stroke){
    return ns('rect',{x,y,width:w,height:h,rx:rx||0,ry:rx||0,fill:fill||'none',stroke:stroke||'none','stroke-width':1});
  }
  function text(x,y,txt,fs,w,fill,anchor){
    const el=ns('text',{x,y,'font-size':fs||12,'font-weight':w||500,fill:fill||'#333','text-anchor':anchor||'start'});
    el.textContent=txt; return el;
  }
  function lineE(x1,y1,x2,y2,stroke,dash,w){
    return ns('line',{x1,y1,x2,y2,stroke:stroke||'#888','stroke-dasharray':dash||'none','stroke-width':w||1});
  }
  function hexMix(h1,h2,t){
    // t:0→h1, 1→h2
    function p(h){h=h.replace('#','');return [parseInt(h.substr(0,2),16),parseInt(h.substr(2,2),16),parseInt(h.substr(4,2),16)];}
    const c1=p(h1),c2=p(h2);
    const m=c1.map((v,i)=>Math.round(v+(c2[i]-v)*t));
    return '#'+m.map(x=>x.toString(16).padStart(2,'0')).join('');
  }

  // ========== 对外 ==========
  window.OntologyTBox={
    init(opts){
      onFilterCb=opts&&opts.onFilter;
      loadData(()=>{
        renderMatrix();
        renderGraph();
        applyFilter();
        // 暴露给外部：把筛选态应用到页面已有筛选器
        applyToPageFilters();
      });
    }
  };

  function applyToPageFilters(){
    // 页面已有 #axis-filter / #layer-filter 按钮。
    // 让外部 applyFilter 触发时同步点击已有按钮（如果存在）。
    const old=onFilterCb;
    onFilterCb=function(st){
      syncAxisLayerButtons(st);
      if(old) old(st);
    };
  }
  function syncAxisLayerButtons(st){
    function clickButton(containerSel,dataKey,target){
      const btns=document.querySelectorAll(containerSel+' button');
      btns.forEach(b=>{
        if(b.dataset[dataKey]===target){
          if(!b.classList.contains('active')) b.click();
        }else{
          if(b.classList.contains('active')) b.click();
        }
      });
    }
    if(st.filterAxis){
      clickButton('#axis-filter','axis',st.filterAxis);
    }else{
      // 若当前有激活按钮，清除
      document.querySelectorAll('#axis-filter button.active').forEach(b=>b.click());
    }
    if(st.filterLayer){
      clickButton('#layer-filter','layer',st.filterLayer);
    }else{
      document.querySelectorAll('#layer-filter button.active').forEach(b=>b.click());
    }
  }
})();

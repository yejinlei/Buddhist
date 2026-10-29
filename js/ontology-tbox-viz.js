/* 本体总纲 TBox 正交矩阵 + 类关系网络图
 * 纯 SVG/JS 实现，零依赖。
 *
 * v2：数据实时化
 *   - 结构读 ontology/tbox_data.json（TBox：轴/层/类/关系）
 *   - 来源与存放位置读 ontology/ontology-index.json（由 scripts/build_ontology_index.py 生成）
 *   - 各类实例数由前端【实时】读取原始索引重算：
 *       manifest.json / m2_index.json / events.json / dharma_assemblies.json /
 *       kepan/core.json / relations.json
 *     数据一补全，刷新页面数字即变，无需重新构建页面。
 *   - 点击任意类节点 → 下方详情面板显示：实例数 / 覆盖率 / 数据来源 /
 *     存放位置 / 生成脚本 / 更新方式 / 样例 / 更新时间。
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

  let D=null;          // tbox 结构数据
  let SRC=null;        // ontology-index.json（来源元数据 + 快照统计）
  let LIVE={};         // 前端实时统计的各类实例数
  let RAWMETA={};      // 各源文件 mtime 等
  let state={filterAxis:null,filterLayer:null,filterClass:null,hoverCell:null,hoverNode:null,hoverRel:null};
  let onFilterCb=null;

  function q(s){return document.querySelector(s)}
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}

  // ========== 1) 加载数据（结构 + 来源 + 原始索引，全部并行） ==========
  function loadData(cb){
    const SPEC=[
      ['../ontology/tbox_data.json',            'tbox'],
      ['../ontology/ontology-index.json',       'index'],
      ['../ontology/instances/manifest.json',   'manifest'],
      ['../ontology/instances/m2_index.json',   'm2'],
      ['../ontology/instances/events.json',     'events'],
      ['../ontology/dharma_assemblies.json',    'da'],
      ['../kepan/core.json',                    'kepan'],
      ['../ontology/instances/relations.json',  'relations']
    ];
    Promise.all(SPEC.map(function(sp){
      return fetch(sp[0],{cache:'no-cache'})
        .then(function(r){ return r.ok? r.json():null; })
        .catch(function(){ return null; });
    })).then(function(res){
      const R={};
      SPEC.forEach(function(sp,i){ R[sp[1]]=res[i]; });
      if(!R.tbox){ console.error('tbox_data.json 加载失败'); return; }
      D=R.tbox;
      SRC=R.index||null;
      RAWMETA=R;
      LIVE=computeLive(R);
      cb(D);
    });
  }

  // ========== 1.1) 前端实时统计（数据一变，刷新即变） ==========
  function computeLive(R){
    const out={};
    const m=R.manifest||{}, ms=m.stats||{}, su=m.sutras||[];
    const has=function(s,kw){ const c=(s&&s.category)||''; return kw.some(function(k){return c.indexOf(k)>=0;}); };

    // —— M3 文本层 ——
    out['Text']            = su.length;
    out['Sutra']           = su.filter(function(s){return has(s,['經','经','阿含','般若','法華','华严','華嚴','寶積','涅槃','大集','密','淨土','净土']);}).length;
    out['Vinaya']          = su.filter(function(s){return has(s,['律']);}).length;
    out['Sastra']          = su.filter(function(s){return has(s,['論','论','釋','释','疏','鈔']);}).length;
    out['Chapter']         = ms.total_chapters;
    out['Section']         = ms.total_paragraphs;
    out['Gatha']           = ms.total_gathas;
    out['Mantra']          = ms.total_mantras;
    out['Kepan']           = R.kepan? Object.keys(R.kepan).length : null;

    // —— M2 义理层 ——
    const m2=R.m2||{}, cs=m2.concepts||[], ps=m2.persons||[], ss=m2.sects||[];
    out['Concept']         = cs.length;
    out['Doctrine']        = cs.filter(function(c){return c.layer==='L2';}).length;
    out['Practice']        = cs.filter(function(c){return c.layer==='L3';}).length;
    out['School']          = ss.length;
    out['PanjiaoSystem']   = ss.length;
    out['Person']          = ps.length;
    const pc=function(k){ return ps.filter(function(p){return (p.category||'')===k;}).length; };
    out['Buddha']          = pc('佛陀');
    out['Bodhisattva']     = pc('菩萨');
    out['Arhat']           = pc('阿罗汉');
    out['Patriarch']       = pc('祖师译经师')+pc('祖师');
    out['ModernScholar']   = pc('学者')+pc('现代学者');
    out['Deity']           = pc('神祇')+pc('护法诸天');
    out['FolkFigure']      = pc('民间信仰');
    out['Protector']       = pc('护法');

    // —— M4 事件层 ——
    const ev=R.events||{};
    out['Council']            = (ev.councils||[]).length;
    out['TransmissionEvent']  = (ev.transmission_events||[]).length;
    out['StoryEvent']         = (ev.story_events||[]).length;
    out['DharmaAssembly']     = R.da? Object.keys(R.da.assemblies||{}).length : null;
    out['Event'] = (out['Council']||0)+(out['TransmissionEvent']||0)+(out['StoryEvent']||0)+(out['DharmaAssembly']||0);

    return out;
  }

  // 取某类的实例数：优先实时值，回退到索引快照
  function liveCount(cid){
    const s=(SRC&&SRC.classes&&SRC.classes[cid])||{};
    if(LIVE[cid]!=null) return LIVE[cid];
    if(s.count!=null) return s.count;
    return null;
  }

  // ========== 2) 正交矩阵热力图 ==========
  function renderMatrix(){
    const root=q('#tbox-matrix'); if(!root) return;
    const W=680,H=380,pad={t:60,r:40,b:80,l:120};
    root.innerHTML='';
    const svg=ns('svg',{width:'100%',height:H,viewBox:'0 0 '+W+' '+H,style:'max-height:380px'});
    root.appendChild(svg);

    const cw=(W-pad.l-pad.r)/4;
    const ch=(H-pad.t-pad.b)/7;

    svg.appendChild(ns('text',{x:W/2,y:24,'text-anchor':'middle','font-size':15,'font-weight':700,fill:'#5a3e1b'}))
       .textContent='四轴 × 七层 正交矩阵（格子数字 = 该格所定义的本体类数）';
    svg.appendChild(ns('text',{x:W/2,y:44,'text-anchor':'middle','font-size':11.5,fill:'#8a7a62'}))
       .textContent='点击行/列/格可筛选下方类树；再次点击取消筛选';

    D.axes.forEach(function(a,i){
      const x=pad.l+i*cw+cw/2;
      const g=ns('g',{class:'axis-head','data-axis':a.id,cursor:'pointer'});
      g.appendChild(rect(pad.l+i*cw+4,pad.t-38,cw-8,30,8,a.color+'22',a.color));
      g.appendChild(text(x,pad.t-19,a.label,13,'700',a.color,'middle'));
      svg.appendChild(g);
      g.addEventListener('click',function(){toggleFilter('filterAxis',a.id);});
    });
    D.layers.forEach(function(l,i){
      const y=pad.t+i*ch+ch/2;
      const g=ns('g',{class:'layer-head','data-layer':l.id,cursor:'pointer'});
      g.appendChild(rect(pad.l-100,pad.t+i*ch+4,96,ch-8,6,l.color+'22',l.color));
      g.appendChild(text(pad.l-52,y,l.label,12,'600',l.color,'middle'));
      svg.appendChild(g);
      g.addEventListener('click',function(){toggleFilter('filterLayer',l.id);});
    });

    const cellMap={};
    D.classes.forEach(function(c){
      (c.axes||[]).forEach(function(a){
        const k=a+'|'+c.layer;
        if(!cellMap[k]) cellMap[k]=[];
        cellMap[k].push(c);
      });
    });
    let maxN=1;
    Object.keys(cellMap).forEach(function(k){ if(cellMap[k].length>maxN)maxN=cellMap[k].length; });

    COLS.forEach(function(a,i){
      ROWS.forEach(function(l,j){
        const k=a+'|'+l, cs=cellMap[k]||[];
        const x=pad.l+i*cw, y=pad.t+j*ch;
        const n=cs.length;
        const ratio=n?0.22+0.78*(n/maxN):0;
        const bg=n?hexMix('#f5ead2',COLORS[a],ratio):'#f7f3ea';
        const g=ns('g',{class:'cell','data-key':k,cursor:'pointer'});
        g.appendChild(rect(x+2,y+2,cw-4,ch-4,6,bg,'#d9cdb4'));
        if(n){
          g.appendChild(text(x+cw/2,y+ch/2-2,String(n),n>=5?20:16,'800',n>=3?'#fff':'#5a3e1b','middle'));
          const lab=cs.slice(0,2).map(function(c){return c.label;}).join('、')+(cs.length>2?' …':'');
          g.appendChild(text(x+cw/2,y+ch/2+14,lab,10,'500',n>=3?'#fff8e0':'#8a7a62','middle'));
        }else{
          g.appendChild(text(x+cw/2,y+ch/2,'—',14,'400','#c9bda5','middle'));
        }
        g.addEventListener('mouseenter',function(){showTooltip(k,cs);});
        g.addEventListener('mousemove',moveTooltip);
        g.addEventListener('mouseleave',hideTooltip);
        g.addEventListener('click',function(){
          if(state.filterAxis===a && state.filterLayer===l){
            state.filterAxis=null;state.filterLayer=null;
          }else{state.filterAxis=a; state.filterLayer=l;}
          state.filterClass=null;
          applyFilter();
        });
        svg.appendChild(g);
      });
    });

    const lg=ns('g');
    for(let k=0;k<=4;k++){
      const xx=pad.l+k*32, yy=H-22, ratio=k/4;
      lg.appendChild(rect(xx,yy,30,12,2,hexMix('#f5ead2','#B8860B',ratio),'none'));
    }
    lg.appendChild(text(pad.l,H-8,'空',10,'400','#8a7a62','middle'));
    lg.appendChild(text(pad.l+4*32,H-8,'密集',10,'400','#8a7a62','middle'));
    svg.appendChild(lg);

    const rst=ns('g',{cursor:'pointer'});
    rst.appendChild(rect(W-100,H-42,80,24,12,'#fff6e0','#B8860B'));
    rst.appendChild(text(W-60,H-25,'重置筛选',11,'600','#B8860B','middle'));
    rst.addEventListener('click',function(){state.filterAxis=null;state.filterLayer=null;state.filterClass=null;applyFilter();});
    svg.appendChild(rst);
  }

  // ========== 3) 类关系网络图（分轴分层布局 + 实时实例数徽标） ==========
  function renderGraph(){
    const root=q('#tbox-graph'); if(!root) return;
    const W=1240,H=720,pad={t:50,r:40,b:40,l:160};
    root.innerHTML='';
    const svg=ns('svg',{width:'100%',viewBox:'0 0 '+W+' '+H,style:'max-height:640px'});
    root.appendChild(svg);

    ROWS.forEach(function(l){
      const y=LAYER_Y[l];
      svg.appendChild(ns('line',{x1:pad.l,x2:W-pad.r,y1:y,y2:y,stroke:'#ece2ca','stroke-dasharray':'4 4','stroke-width':1}));
      const t=ns('text',{x:pad.l-12,y:y+4,'text-anchor':'end','font-size':11.5,fill:COLORS[l],'font-weight':600});
      const ly=D.layers.find(function(x){return x.id===l;});
      t.textContent=ly?ly.label:l;
      svg.appendChild(t);
    });
    COLS.forEach(function(a){
      const x=AXIS_X[a];
      const ax=D.axes.find(function(x){return x.id===a;});
      const t=ns('text',{x:x,y:pad.t-20,'text-anchor':'middle','font-size':13,fill:COLORS[a],'font-weight':700});
      t.textContent=ax?ax.label:a;
      svg.appendChild(t);
      const rect_bg=ns('rect',{x:x-120,y:pad.t-8,width:240,height:H-pad.t-pad.b,rx:12,fill:COLORS[a]+'08'});
      svg.insertBefore(rect_bg,svg.firstChild);
    });

    const byCell={};
    D.classes.forEach(function(c){
      (c.axes||[]).forEach(function(a){
        if(!AXIS_X[a])return;
        const k=a+'|'+c.layer;
        if(!byCell[k]) byCell[k]=[];
        byCell[k].push(c);
      });
    });
    const nodes={};
    Object.keys(byCell).forEach(function(k){
      const arr=byCell[k];
      const parts=k.split('|'), a=parts[0], l=parts[1];
      const x0=AXIS_X[a], y0=LAYER_Y[l];
      const span=Math.min(220, 30*arr.length+20);
      arr.forEach(function(c,i){
        if(nodes[c.id]) return;
        const x=x0-span/2 + (span/(arr.length||1))*(i+0.5);
        const y=y0 + (arr.length%2===0? (i-arr.length/2+0.5)*6 : (i-Math.floor(arr.length/2))*6);
        nodes[c.id]={x:x,y:y,c:c};
      });
    });

    const edges=[];
    D.classes.forEach(function(c){
      if(c.parent && nodes[c.parent] && nodes[c.id]){
        edges.push({type:'isa',from:c.parent,to:c.id,label:'subClassOf'});
      }
    });
    function resolveCls(n){ return nodes[n]?n:null; }
    D.relations.forEach(function(r){
      (r.domain||[]).forEach(function(d){
        (r.range||[]).forEach(function(ra){
          const dN=resolveCls(d), raN=resolveCls(ra);
          if(dN && raN && dN!==raN){
            edges.push({type:'rel',from:dN,to:raN,rel:r,label:r.label});
          }
        });
      });
    });

    const edgeG=ns('g');
    edges.forEach(function(e){
      const a=nodes[e.from], b=nodes[e.to];
      if(!a||!b)return;
      const p=ns('path');
      if(e.type==='isa'){
        p.setAttribute('d','M'+a.x+','+(a.y+12)+' C'+a.x+','+((a.y+b.y)/2)+' '+b.x+','+((a.y+b.y)/2)+' '+b.x+','+(b.y-14));
        p.setAttribute('stroke','#9e8c6a');
        p.setAttribute('stroke-width','1.5');
        p.setAttribute('fill','none');
        p.setAttribute('stroke-dasharray','none');
      }else{
        const col=relColor(e.rel.group);
        p.setAttribute('d','M'+(a.x+10)+','+a.y+' Q'+((a.x+b.x)/2)+','+((a.y+b.y)/2-18)+' '+(b.x-10)+','+b.y);
        p.setAttribute('stroke',col);
        p.setAttribute('stroke-width','1.3');
        p.setAttribute('fill','none');
        p.setAttribute('stroke-dasharray','4 3');
        p.setAttribute('opacity','0.55');
      }
      p.dataset.from=e.from; p.dataset.to=e.to; p.dataset.type=e.type;
      if(e.rel) p.dataset.group=e.rel.group;
      p.style.cursor='pointer';
      p.addEventListener('mouseenter',function(){p.setAttribute('stroke-width','2.6');p.setAttribute('opacity','0.95');showRelTip(e,a,b);});
      p.addEventListener('mousemove',moveTooltip);
      p.addEventListener('mouseleave',function(){p.setAttribute('stroke-width',e.type==='isa'?'1.5':'1.3');p.setAttribute('opacity',e.type==='isa'?'1':'0.55');hideTooltip();});
      edgeG.appendChild(p);
    });
    svg.appendChild(edgeG);

    const nodeG=ns('g');
    D.classes.forEach(function(c){
      const n=nodes[c.id]; if(!n) return;
      const ax=(c.axes&&c.axes[0])||'A1';
      const col=COLORS[ax]||'#888';
      const cnt=liveCount(c.id);
      const r=c.parent?11:13;
      const g=ns('g',{cursor:'pointer','data-cls':c.id,transform:'translate('+n.x+','+n.y+')'});
      const circle=ns('circle',{cx:0,cy:0,r:r,fill:c.parent?col+'cc':col,stroke:'#fff','stroke-width':2});
      g.appendChild(circle);
      const lbl=ns('text',{x:0,y:r+12,'text-anchor':'middle','font-size':10.5,fill:'#4a3a1e','font-weight':c.parent?500:700});
      lbl.textContent=c.label;
      g.appendChild(lbl);
      // 实时实例数徽标
      if(cnt!=null){
        const bw=String(cnt).length*6.4+12;
        const badge=ns('g',{transform:'translate(0,'+(r+16)+')'});
        badge.appendChild(rect(-bw/2,0,bw,13,6.5,'#fdf6e3','#d9cdb4'));
        badge.appendChild(text(0,9.6,String(cnt),9.5,'700','#8a6d2f','middle'));
        g.appendChild(badge);
      }
      g.addEventListener('mouseenter',function(){circle.setAttribute('r',r+3);showClsTip(c,n);});
      g.addEventListener('mousemove',moveTooltip);
      g.addEventListener('mouseleave',function(){circle.setAttribute('r',r);hideTooltip();});
      g.addEventListener('click',function(){ state.filterClass=(state.filterClass===c.id?null:c.id); applyFilter(); renderDetail(c); });
      nodeG.appendChild(g);
    });
    svg.appendChild(nodeG);

    const groups={};
    edges.filter(function(e){return e.type==='rel';}).forEach(function(e){if(e.rel)groups[e.rel.group]=relColor(e.rel.group);});
    let lgx=pad.l+20, lgy=H-20;
    Object.keys(groups).forEach(function(g){
      const col=groups[g];
      svg.appendChild(lineE(lgx,lgy,lgx+24,lgy,col,'4 3',1.6));
      const t=ns('text',{x:lgx+28,y:lgy+4,'font-size':10.5,fill:'#5a3e1b'});
      t.textContent=g;
      svg.appendChild(t);
      lgx += 28+ g.length*11 + 24;
    });
    svg.appendChild(lineE(lgx,lgy,lgx+24,lgy,'#9e8c6a','none',1.6));
    const isaT=ns('text',{x:lgx+28,y:lgy+4,'font-size':10.5,fill:'#5a3e1b'});
    isaT.textContent='subClassOf（继承）';
    svg.appendChild(isaT);
  }

  function relColor(g){
    if(!g) return '#888';
    if(g.indexOf('分类')>=0)return '#B8860B';
    if(g.indexOf('文本')>=0)return '#3E6B4F';
    if(g.indexOf('宗派')>=0)return '#C07830';
    if(g.indexOf('人物')>=0)return '#8B5A2B';
    if(g.indexOf('事件')>=0)return '#A23B3B';
    return '#7a6a52';
  }

  // ========== 3.1) 类详情面板（来源 / 存放位置 / 实例数 / 覆盖率） ==========
  function renderDetail(c){
    let host=q('#tbox-detail');
    if(!host){
      host=document.createElement('div');
      host.id='tbox-detail';
      const g=q('#tbox-graph');
      if(g && g.parentNode) g.parentNode.appendChild(host);
      else return;
    }
    const s=(SRC&&SRC.classes&&SRC.classes[c.id])||{};
    const cnt=liveCount(c.id);
    const axs=(c.axes||[]).map(function(a){const ax=D.axes.find(function(x){return x.id===a;});return ax?a.label:a;}).join(' / ');
    const ly=D.layers.find(function(x){return x.id===c.layer;});
    const cov=s.coverage||null;

    // 实例统计区块
    let statHtml;
    if(cnt!=null){
      let covBar='';
      if(cov && cov.total){
        const pct=Math.max(0,Math.min(100,cov.pct||0));
        covBar='<div style="margin-top:6px">'
          + '<div style="display:flex;justify-content:space-between;font-size:11px;color:#8a7a62;margin-bottom:3px">'
          + '<span>覆盖度</span><span>'+esc(cov.have)+' / '+esc(cov.total)+'（'+pct+'%）</span></div>'
          + '<div style="height:7px;background:#f0e7d4;border-radius:4px;overflow:hidden">'
          + '<div style="height:100%;width:'+pct+'%;background:linear-gradient(90deg,#D4AF37,#B8860B)"></div></div>'
          + '</div>';
      }
      let bd='';
      if(s.breakdown && Object.keys(s.breakdown).length){
        const items=Object.keys(s.breakdown).slice(0,10).map(function(k){
          const v=s.breakdown[k];
          return '<span style="display:inline-block;background:#fbf6ea;border:1px solid #ece2ca;border-radius:6px;padding:2px 8px;margin:2px 4px 2px 0;font-size:11.5px;color:#5a3e1b">'+esc(k)+' <b style="color:#8a6d2f">'+(v==null?'—':v)+'</b></span>';
        }).join('');
        bd='<div style="margin-top:8px"><div style="font-size:11px;color:#8a7a62;margin-bottom:3px">细分</div>'+items+'</div>';
      }
      statHtml='<div style="font-size:22px;font-weight:800;color:#8a6d2f;line-height:1.1">'+cnt
        +'<span style="font-size:12px;font-weight:500;color:#8a7a62;margin-left:4px">'+esc(s.unit||'')+'</span></div>'
        + covBar + bd;
    }else{
      statHtml='<div style="font-size:12.5px;color:#8a7a62">结构性 / 抽象类，无独立实例（由字段或子类承载）</div>';
    }

    // 来源与存放
    const origins=(s.origin||[]).map(function(o){return '<code style="background:#f4efe3;border-radius:4px;padding:1px 5px;font-size:11.5px;color:#5a3e1b">'+esc(o)+'</code>';}).join(' ');
    let samples='';
    if(s.samples && s.samples.length){
      const linkable=(c.id==='Kepan'||c.id==='Sutra'||c.id==='Vinaya'||c.id==='Sastra');
      samples='<div style="margin-top:8px"><div style="font-size:11px;color:#8a7a62;margin-bottom:3px">样例</div>'
        + s.samples.slice(0,8).map(function(x){
            if(linkable){ return '<a href="sutras.html?load='+esc(x)+'" style="text-decoration:none;background:#fbf6ea;border:1px solid #ece2ca;border-radius:6px;padding:2px 8px;margin:2px 4px 2px 0;font-size:11.5px;color:#3E6B4F;display:inline-block">'+esc(x)+'</a>'; }
            return '<span style="background:#fbf6ea;border:1px solid #ece2ca;border-radius:6px;padding:2px 8px;margin:2px 4px 2px 0;font-size:11.5px;color:#5a3e1b;display:inline-block">'+esc(x)+'</span>';
          }).join('')
        + '</div>';
    }

    const upd=(s.update_cmd)? '<div style="margin-top:8px"><div style="font-size:11px;color:#8a7a62;margin-bottom:3px">更新方式</div>'
      + '<code style="display:block;background:#2b1e0c;color:#f3e6c8;border-radius:6px;padding:6px 9px;font-size:11px;white-space:pre-wrap;word-break:break-all">'+esc(s.update_cmd)+'</code></div>' : '';

    const mt=(s.origin&&s.origin.length&&RAWMETA.__mtime)? '' : '';

    host.innerHTML=''
      + '<div style="border:1px solid #ece2ca;border-radius:10px;background:#fffdf7;padding:14px 16px" class="grid md:grid-cols-2 gap-5">'
      +   '<div>'
      +     '<div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap">'
      +       '<span style="font-weight:800;color:#5a3e1b;font-size:15px">'+esc(c.label)+'</span>'
      +       '<code style="font-size:11px;color:#a2906a">'+esc(c.id)+'</code>'
      +       '<span style="font-size:11px;background:'+COLORS[(c.axes||[])[0]]+'1a;color:'+COLORS[(c.axes||[])[0]]+';border-radius:9999px;padding:1px 8px">'+esc(axs)+'</span>'
      +       '<span style="font-size:11px;background:'+(ly?ly.color:'#888')+'1a;color:'+(ly?ly.color:'#888')+';border-radius:9999px;padding:1px 8px">'+esc(ly?ly.label:c.layer)+'</span>'
      +     '</div>'
      +     '<div style="font-size:12px;color:#6b6152;margin-top:6px">'+esc(c.desc||s.note||'')+'</div>'
      +     (s.note && c.desc!==s.note ? '<div style="font-size:11.5px;color:#8a7a62;margin-top:4px">'+esc(s.note)+'</div>' : '')
      +     '<div style="margin-top:10px">'+statHtml+'</div>'
      +     samples
      +   '</div>'
      +   '<div style="border-left:1px dashed #ece2ca;padding-left:18px">'
      +     '<div style="font-size:11px;color:#8a7a62;margin-bottom:3px">数据来源</div>'
      +     '<div>'+ (origins||'<span style="font-size:12px;color:#a2906a">—</span>') +'</div>'
      +     '<div style="margin-top:10px"><div style="font-size:11px;color:#8a7a62;margin-bottom:3px">存放位置</div>'
      +       '<div style="font-size:12px;color:#5a3e1b;line-height:1.5">'+esc(s.storage||'—')+'</div></div>'
      +     '<div style="margin-top:10px"><div style="font-size:11px;color:#8a7a62;margin-bottom:3px">生成脚本</div>'
      +       '<div style="font-size:12px;color:#5a3e1b">'+esc(s.generator||'—')+'</div></div>'
      +     upd
      +   '</div>'
      + '</div>';
    host.style.display='block';
    if(host.scrollIntoView) try{ host.scrollIntoView({behavior:'smooth',block:'nearest'}); }catch(e){}
  }

  // ========== 筛选联动 ==========
  function toggleFilter(key,val){
    state[key]=(state[key]===val?null:val);
    state.filterClass=null;
    applyFilter();
  }
  function applyFilter(){
    document.querySelectorAll('#tbox-matrix .cell rect').forEach(function(r){r.setAttribute('opacity','1');});
    document.querySelectorAll('#tbox-matrix .cell text').forEach(function(t){t.setAttribute('opacity','1');});
    document.querySelectorAll('#tbox-matrix .cell').forEach(function(g){
      const k=g.dataset.key, parts=k.split('|'), a=parts[0], l=parts[1];
      let show=true;
      if(state.filterAxis && a!==state.filterAxis) show=false;
      if(state.filterLayer && l!==state.filterLayer) show=false;
      g.setAttribute('opacity',show?'1':'0.2');
    });
    document.querySelectorAll('#tbox-matrix .axis-head').forEach(function(g){
      const a=g.dataset.axis;
      g.querySelector('rect').setAttribute('stroke-width',state.filterAxis===a?'2.5':'1');
    });
    document.querySelectorAll('#tbox-matrix .layer-head').forEach(function(g){
      const l=g.dataset.layer;
      g.querySelector('rect').setAttribute('stroke-width',state.filterLayer===l?'2.5':'1');
    });
    document.querySelectorAll('#tbox-graph [data-cls]').forEach(function(g){
      const cid=g.dataset.cls;
      const c=D.classes.find(function(x){return x.id===cid;}); if(!c)return;
      let show=true;
      if(state.filterAxis && (c.axes||[]).indexOf(state.filterAxis)<0) show=false;
      if(state.filterLayer && c.layer!==state.filterLayer) show=false;
      if(state.filterClass && cid!==state.filterClass && c.parent!==state.filterClass){
        show=isConnected(cid,state.filterClass);
      }
      g.setAttribute('opacity',show?'1':'0.15');
    });
    document.querySelectorAll('#tbox-graph path').forEach(function(p){
      let show=true;
      if(state.filterClass){
        show=(p.dataset.from===state.filterClass||p.dataset.to===state.filterClass);
      }
      p.setAttribute('opacity',show?(p.dataset.type==='isa'?'1':'0.55'):'0.06');
    });
    if(onFilterCb) onFilterCb(state);
  }
  function isConnected(a,b){
    if(a===b)return true;
    const edges=document.querySelectorAll('#tbox-graph path');
    for(let i=0;i<edges.length;i++){
      const p=edges[i];
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
      tip.style.position='fixed'; tip.style.pointerEvents='none';
      tip.style.background='rgba(43,30,12,0.95)'; tip.style.color='#fdf6e3';
      tip.style.padding='8px 12px'; tip.style.borderRadius='8px'; tip.style.fontSize='12.5px';
      tip.style.maxWidth='340px'; tip.style.lineHeight='1.5';
      tip.style.boxShadow='0 8px 20px rgba(0,0,0,0.25)'; tip.style.zIndex='9999'; tip.style.display='none';
      document.body.appendChild(tip);
    }
    return tip;
  }
  function showTooltip(k,cs){
    const parts=k.split('|'), a=parts[0], l=parts[1];
    const ax=D.axes.find(function(x){return x.id===a;}), ly=D.layers.find(function(x){return x.id===l;});
    let inst=0, hasInst=false;
    cs.forEach(function(c){ const n=liveCount(c.id); if(n!=null){inst+=n;hasInst=true;} });
    const t=ensureTip();
    t.innerHTML='<div style="font-weight:700;color:#D4AF37;margin-bottom:4px">'+esc(ax.label)+' × '+esc(ly.label)+'</div>'
      + '<div style="opacity:.8;margin-bottom:4px">'+esc(ly.desc)+'</div>'
      + (cs.length?'<div>共 <b>'+cs.length+'</b> 个类：'+cs.map(function(c){return esc(c.label);}).join('、')+'</div>':'<div style="opacity:.6">（此格无直接定义类）</div>')
      + (hasInst?'<div style="margin-top:4px;opacity:.85">实例合计 <b style="color:#D4AF37">'+inst+'</b></div>':'');
    t.style.display='block';
  }
  function showClsTip(c,n){
    const t=ensureTip();
    const axs=(c.axes||[]).map(function(a){
      const ax=D.axes.find(function(x){return x.id===a;});return ax?'<span style="color:'+ax.color+';font-weight:600">'+esc(ax.label)+'</span>':esc(a);
    }).join(' / ');
    const ly=D.layers.find(function(x){return x.id===c.layer;});
    const s=(SRC&&SRC.classes&&SRC.classes[c.id])||{};
    const cnt=liveCount(c.id);
    const cntLine=(cnt!=null)?'<div style="margin-top:3px">实例：<b style="color:#D4AF37">'+cnt+'</b> '+esc(s.unit||'')+'</div>':'';
    const srcLine=(s.origin&&s.origin.length)?'<div style="opacity:.75;margin-top:3px;font-size:11px">来源：'+esc((s.origin||[]).slice(0,2).join('、'))+'</div>':'';
    t.innerHTML='<div style="font-weight:700;color:#D4AF37;margin-bottom:4px">'+esc(c.label)+' <span style="color:#b4a77a;font-weight:400;font-size:11px">('+esc(c.id)+')</span></div>'
      + '<div style="opacity:.85;margin-bottom:4px">轴：'+axs+' ｜ 层：<b style="color:'+(ly?ly.color:'#aaa')+'">'+esc(ly?ly.label:c.layer)+'</b>'+(c.parent?'｜ 父类：'+esc(parentLabel(c.parent)):'')+'</div>'
      + '<div style="opacity:.9">'+esc(c.desc||'')+'</div>'
      + cntLine + srcLine
      + '<div style="opacity:.6;margin-top:6px;font-size:11px">点击查看数据来源与存放位置</div>';
    t.style.display='block';
  }
  function showRelTip(e,a,b){
    const t=ensureTip();
    if(e.type==='isa'){
      t.innerHTML='<b style="color:#D4AF37">继承（subClassOf）</b><br><span>'+esc(b.c.label)+'</span> 是 <span>'+esc(a.c.label)+'</span> 的子类';
    }else{
      const col=relColor(e.rel.group);
      t.innerHTML='<b style="color:'+col+'">'+esc(e.rel.label)+'</b> <span style="opacity:.7">（'+esc(e.rel.group||'关系')+'）</span><br>'
        + 'domain: <b>'+esc(e.from)+'</b> → range: <b>'+esc(e.to)+'</b><br>'
        + '<div style="opacity:.8;margin-top:4px">'+esc(e.rel.id)+'</div>';
    }
    t.style.display='block';
  }
  function parentLabel(pid){
    const p=D.classes.find(function(x){return x.id===pid;}); return p?p.label:pid;
  }
  function moveTooltip(ev){
    const t=ensureTip();
    let x=ev.clientX+16,y=ev.clientY+16;
    if(x+350>window.innerWidth) x=ev.clientX-360;
    if(y+220>window.innerHeight) y=ev.clientY-230;
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
    return ns('rect',{x:x,y:y,width:w,height:h,rx:rx||0,ry:rx||0,fill:fill||'none',stroke:stroke||'none','stroke-width':1});
  }
  function text(x,y,txt,fs,w,fill,anchor){
    const el=ns('text',{x:x,y:y,'font-size':fs||12,'font-weight':w||500,fill:fill||'#333','text-anchor':anchor||'start'});
    el.textContent=txt; return el;
  }
  function lineE(x1,y1,x2,y2,stroke,dash,w){
    return ns('line',{x1:x1,y1:y1,x2:x2,y2:y2,stroke:stroke||'#888','stroke-dasharray':dash||'none','stroke-width':w||1});
  }
  function hexMix(h1,h2,t){
    function p(h){h=h.replace('#','');return [parseInt(h.substr(0,2),16),parseInt(h.substr(2,2),16),parseInt(h.substr(4,2),16)];}
    const c1=p(h1),c2=p(h2);
    const m=c1.map(function(v,i){return Math.round(v+(c2[i]-v)*t);});
    return '#'+m.map(function(x){return x.toString(16).padStart(2,'0');}).join('');
  }

  // ========== 顶部数据快照信息 ==========
  function renderMeta(){
    const host=q('#tbox-meta'); if(!host) return;
    const m=(SRC&&SRC.meta)||{};
    const g=(SRC&&SRC.global)||{};
    let chips=[];
    if(g.sutras!=null) chips.push(['经文实例', g.sutras]);
    if(g.concepts!=null) chips.push(['义理概念', g.concepts]);
    if(g.persons!=null) chips.push(['人物', g.persons]);
    if(g.events!=null) chips.push(['事件', g.events]);
    if(g.kepan!=null) chips.push(['科判', g.kepan]);
    const html=chips.map(function(c){
      return '<span style="display:inline-block;background:#fbf6ea;border:1px solid #ece2ca;border-radius:9999px;padding:1px 9px;margin:2px 4px 2px 0;font-size:11px;color:#5a3e1b">'+esc(c[0])+' <b style="color:#8a6d2f">'+c[1]+'</b></span>';
    }).join('');
    host.innerHTML='<div style="font-size:11px;color:#a2906a;margin-bottom:3px">数据实时汇总自 6 个索引文件'
      + (m.generated_at?' · 快照 '+esc(m.generated_at):'')+'</div>'+html;
  }

  // ========== 对外 ==========
  window.OntologyTBox={
    init(opts){
      onFilterCb=opts&&opts.onFilter;
      loadData(function(){
        renderMeta();
        renderMatrix();
        renderGraph();
        applyFilter();
        applyToPageFilters();
      });
    }
  };

  function applyToPageFilters(){
    const old=onFilterCb;
    onFilterCb=function(st){
      syncAxisLayerButtons(st);
      if(old) old(st);
    };
  }
  function syncAxisLayerButtons(st){
    function clickButton(containerSel,dataKey,target){
      const btns=document.querySelectorAll(containerSel+' button');
      btns.forEach(function(b){
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
      document.querySelectorAll('#axis-filter button.active').forEach(function(b){b.click();});
    }
    if(st.filterLayer){
      clickButton('#layer-filter','layer',st.filterLayer);
    }else{
      document.querySelectorAll('#layer-filter button.active').forEach(function(b){b.click();});
    }
  }
})();

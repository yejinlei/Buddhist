/* 读经辅助：繁/简/白切换 + 生僻字注音 + 术语白话注释
   通过 body class 控制模式切换，不重新渲染经文，性能好 */
(function(){
  const TRAD_KEY = 'buddhist_read_trad';
  const BAIHUA_KEY = 'buddhist_read_baihua';
  const PINYIN_KEY = 'buddhist_read_pinyin';
  let H2S_FULL={}, PRON={}, VERN={};
  let _origTextMap = new Map(); // pid -> 原始繁体原文

  // 多字词注音优先，先匹配长词，再单字
  let PRON_WORDS=[], PRON_CHARS={};
  // 白话术语按长度降序
  let VERN_WORDS=[];

  // ============ 数据加载 ============
  async function init() {
    try {
      const [h, p, v] = await Promise.all([
        fetch('../data/hant2simp_full.json').then(r=>r.json()).catch(()=>({})),
        fetch('../data/pronunciation.json').then(r=>r.json()).catch(()=>({})),
        fetch('../data/vernacular_terms.json').then(r=>r.json()).catch(()=>({}))
      ]);
      H2S_FULL = {...(window.H2S||{}), ...h};
      PRON = p; VERN = v;
      // 注音词按长度降序
      PRON_WORDS = Object.keys(PRON).filter(k=>k.length>=2).sort((a,b)=>b.length-a.length);
      PRON_CHARS = {};
      Object.keys(PRON).forEach(k=>{ if(k.length===1) PRON_CHARS[k]=PRON[k]; });
      // 白话语词按长度降序
      VERN_WORDS = Object.keys(VERN).sort((a,b)=>b.length-a.length);
      injectToolbar();
      applyInitialState();
    } catch(e){ console.warn('读经辅助初始化失败', e); }
  }

  // ============ 注入工具条按钮 ============
  function injectToolbar(){
    const tb = document.querySelector('.read-toolbar');
    if(!tb) return;
    // 找到"字号"前面或书签按钮前插入分隔与按钮
    const style = document.createElement('style');
    style.textContent = `
      .read-toolbar .rt-sep { width:1px; height:20px; background:#e5d9c3; margin:0 4px; align-self:center; }
      body.mode-trad .simp-text { display:none; }
      body.mode-trad .trad-text { display:inline; }
      body:not(.mode-trad) .trad-text { display:none; }
      body:not(.mode-trad) .simp-text { display:inline; }
      .vern-term { border-bottom: 1px dashed rgba(24,100,0,.4); cursor:help; }
      body.mode-baihua .vern-term { background: rgba(132,204,22,.18); border-bottom-color: #65a30d; border-radius: 2px; padding: 0 1px; }
      .vern-term::after { content: attr(data-baihua); position: absolute; background: #2C1810; color: #F5F0E1;
        padding: 6px 10px; border-radius: 6px; font-size: 13px; line-height: 1.6; max-width: 300px;
        white-space: normal; z-index: 100; display: none; pointer-events: none; box-shadow: 0 4px 14px rgba(0,0,0,.2);
        margin-top: 22px; margin-left: -8px; }
      .vern-term { position: relative; }
      body.mode-baihua .vern-term:hover::after { display: block; }
      ruby.reading-pinyin { ruby-position: over; }
      ruby.reading-pinyin rt { font-size: 10px; color: #8B4513; font-weight: normal; line-height: 1; opacity: .8; }
      body:not(.mode-pinyin) ruby.reading-pinyin rt { display: none; }
      body.mode-pinyin ruby.reading-pinyin rt { display: block; }
      .rt-hint { font-size: 11px; color: #8B4513; background: #fdf8ec; padding: 2px 8px; border-radius: 4px; margin-left: 4px; }
    `;
    document.head.appendChild(style);

    const group = document.createElement('span');
    group.style.cssText = 'display:flex;align-items:center;gap:4px;margin-left:.5rem';
    group.innerHTML = `
      <span class="rt-sep"></span>
      <span class="rt-label">显示</span>
      <button data-mode="trad" id="rt-trad">繁体</button>
      <button data-mode="simp" id="rt-simp" class="active">简体</button>
      <span class="rt-sep"></span>
      <button data-mode="pinyin" id="rt-pinyin" title="给佛经生僻字/专用词加注音">🔤 注音</button>
      <button data-mode="baihua" id="rt-baihua" title="给佛学名词加白话释义">💡 白话注释</button>
    `;
    // 插入到"学术工具"按钮前
    const studyBtn = document.getElementById('study-btn');
    if(studyBtn) tb.insertBefore(group, studyBtn);
    else tb.appendChild(group);

    group.querySelectorAll('button[data-mode]').forEach(btn => {
      btn.addEventListener('click', () => toggleMode(btn.dataset.mode));
    });
  }

  function applyInitialState(){
    try {
      if(localStorage.getItem(TRAD_KEY)==='1') document.body.classList.add('mode-trad');
      if(localStorage.getItem(BAIHUA_KEY)==='1') document.body.classList.add('mode-baihua');
      if(localStorage.getItem(PINYIN_KEY)==='1') document.body.classList.add('mode-pinyin');
    } catch(e){}
    syncBtnState();
    // MutationObserver监听经文段落新增，后处理DOM
    observeContent();
  }

  function toggleMode(mode){
    if(mode==='trad'){
      document.body.classList.toggle('mode-trad');
      try { localStorage.setItem(TRAD_KEY, document.body.classList.contains('mode-trad')?'1':'0'); } catch(e){}
    } else if(mode==='baihua'){
      document.body.classList.toggle('mode-baihua');
      try { localStorage.setItem(BAIHUA_KEY, document.body.classList.contains('mode-baihua')?'1':'0'); } catch(e){}
      if(document.body.classList.contains('mode-baihua')) ensureAnnotated();
    } else if(mode==='pinyin'){
      document.body.classList.toggle('mode-pinyin');
      try { localStorage.setItem(PINYIN_KEY, document.body.classList.contains('mode-pinyin')?'1':'0'); } catch(e){}
      if(document.body.classList.contains('mode-pinyin')) ensureAnnotated();
    } else if(mode==='simp'){
      document.body.classList.remove('mode-trad');
      try { localStorage.setItem(TRAD_KEY,'0'); } catch(e){}
    }
    syncBtnState();
  }

  function syncBtnState(){
    document.querySelectorAll('.read-toolbar button[data-mode]').forEach(b=>{
      const m = b.dataset.mode;
      let on = false;
      if(m==='trad') on = document.body.classList.contains('mode-trad');
      else if(m==='simp') on = !document.body.classList.contains('mode-trad');
      else if(m==='baihua') on = document.body.classList.contains('mode-baihua');
      else if(m==='pinyin') on = document.body.classList.contains('mode-pinyin');
      b.classList.toggle('active', on);
    });
  }

  // ============ DOM观察与后处理 ============
  let _annotated = false;
  function observeContent(){
    const textEl = document.getElementById('sutra-text');
    if(!textEl){ setTimeout(observeContent, 300); return; }
    // 初次处理
    annotateAll();
    const mo = new MutationObserver(() => {
      annotateAll();
    });
    mo.observe(textEl, { childList:true, subtree:true });
  }

  function ensureAnnotated(){
    if(!_annotated) annotateAll();
  }

  function annotateAll(){
    const textEl = document.getElementById('sutra-text');
    if(!textEl) return;
    const ps = textEl.querySelectorAll('p.sutra-content');
    ps.forEach(p => {
      if(p.dataset.annotated==='1') return;
      annotatePara(p);
      p.dataset.annotated='1';
    });
    _annotated = true;
  }

  // 给段落做三件事：①包一层simp-text/trad-text双态 ②白话注释span ③生僻字ruby注音
  function annotatePara(p){
    const pid = p.id;
    // 保存原始内容（简体+词典链接版）作为simp内容——我们不需要另生成繁体HTML，繁体模式用原始繁体原文
    // 但当前renderParagraph已输出简体，我们需要找回原始繁体文本：从currentSutra.content里按pid定位
    const origTrad = getOrigTrad(pid);
    const simpHtml = p.innerHTML;
    // 对simpHtml做术语注释+注音注入
    const enriched = enrichHtml(simpHtml);
    if(origTrad){
      const tradHtml = enrichPlain(origTrad);
      p.innerHTML = `<span class="simp-text">${enriched}</span><span class="trad-text">${tradHtml}</span>`;
    } else {
      p.innerHTML = `<span class="simp-text">${enriched}</span>`;
    }
  }

  function getOrigTrad(pid){
    if(_origTextMap.has(pid)) return _origTextMap.get(pid);
    if(!window.currentSutra) return null;
    const m = pid.match(/c(\d+)-p(\d+)/);
    if(!m){ _origTextMap.set(pid,null); return null; }
    const ci = parseInt(m[1]), pi = parseInt(m[2]);
    const chap = window.currentSutra.content && window.currentSutra.content[ci];
    if(!chap){ _origTextMap.set(pid,null); return null; }
    const paras = (chap.text||'').split(/\n+/).filter(Boolean).map(x=>x.trim());
    const raw = paras[pi] || null;
    _origTextMap.set(pid, raw);
    return raw;
  }

  // 在已渲染好的HTML字符串中插入白话注释和ruby注音（要小心不破坏已有的HTML标签）
  function enrichHtml(html){
    // 简单策略：用DOM解析再对文本节点处理
    const tpl = document.createElement('div');
    tpl.innerHTML = html;
    processNode(tpl);
    return tpl.innerHTML;
  }
  function enrichPlain(text){
    // 纯文本转HTML：做注音+白话注释，保留escape
    const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    return insertMarks(esc(text));
  }

  function processNode(node){
    if(node.nodeType === 3){ // 文本节点
      const t = node.nodeValue;
      if(!t || !t.trim()) return;
      const html = insertMarks(t
        .replace(/&/g,'&amp;')
        .replace(/</g,'&lt;')
        .replace(/>/g,'&gt;'));
      const tpl = document.createElement('span');
      tpl.innerHTML = html;
      const frag = document.createDocumentFragment();
      while(tpl.firstChild) frag.appendChild(tpl.firstChild);
      node.parentNode.replaceChild(frag, node);
      return;
    }
    // 跳过已处理的ruby/span.vern-term
    const tag = node.tagName;
    if(tag==='RUBY' || (tag==='SPAN' && node.classList && node.classList.contains('vern-term'))) return;
    // 子节点递归
    const children = Array.from(node.childNodes);
    children.forEach(c => processNode(c));
  }

  // 在纯文本中插入注音ruby + 白话注释span（使用最长匹配）
  function insertMarks(text){
    if(!text) return text;
    // 第一步：标记位置：用区间数组，最长优先、不重叠
    const marks = []; // {s,e,type,data}
    // 白话术语
    if(document.body.classList.contains('mode-baihua') || true){
      // 始终加span，用CSS控制hover显示
      for(const w of VERN_WORDS){
        let from=0, idx;
        while((idx=text.indexOf(w, from)) !== -1){
          // 检查是否与已有重叠
          if(!overlaps(marks, idx, idx+w.length)){
            marks.push({s:idx, e:idx+w.length, type:'vern', word:w});
          }
          from = idx+w.length;
        }
      }
    }
    // 注音：多字词优先
    if(document.body.classList.contains('mode-pinyin') || true){
      for(const w of PRON_WORDS){
        let from=0, idx;
        while((idx=text.indexOf(w, from)) !== -1){
          if(!overlaps(marks, idx, idx+w.length)){
            marks.push({s:idx, e:idx+w.length, type:'pron', word:w});
          }
          from = idx+w.length;
        }
      }
    }
    // 按位置排序
    marks.sort((a,b)=>a.s-b.s);
    // 第二步：从前往后拼接，严格保持原文顺序
    let out = '';
    let cur = 0;
    for(const m of marks){
      if(m.s < cur) continue; // 与已处理区间重叠，跳过
      out += text.slice(cur, m.s);
      const mid = text.slice(m.s, m.e);
      if(m.type==='vern'){
        out += `<span class="vern-term" data-baihua="${esc_attr(VERN[m.word])}">${mid}</span>`;
      } else if(m.type==='pron'){
        const py = PRON[m.word];
        const py_short = py.split('（')[0]; // 去括号注释
        out += `<ruby class="reading-pinyin">${mid}<rt>${esc_attr(py_short)}</rt></ruby>`;
      }
      cur = m.e;
    }
    out += text.slice(cur);
    return out;
  }

  function overlaps(marks, s, e){
    for(const m of marks){
      if(!(e<=m.s || s>=m.e)) return true;
    }
    return false;
  }
  function esc_attr(s){
    return String(s||'').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  // 每次loadSutra完成时，清空origTextMap以便重新抓取
  window.__readingAid = {
    reset() { _origTextMap.clear(); _annotated=false; },
    annotateAll
  };
  // Hook loadSutra完成事件
  const _origLoadSutra = window.loadSutra;
  window.addEventListener('load', ()=>{
    setTimeout(init, 500);
    // 观察body上sutra加载：sutra-text重建时重新处理
    const watcher = setInterval(()=>{
      const t = document.getElementById('sutra-text');
      if(t && !t.__readingAidBound){
        t.__readingAidBound = true;
        const mo = new MutationObserver(() => {
          // 当整个sutra-text被替换（新经加载）
          annotateAll();
        });
        mo.observe(t, {childList:true, subtree:true});
      }
    }, 500);
  });
})();

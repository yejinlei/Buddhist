# ⚠️ 此脚本已作废：会覆盖项目标准样式，请勿运行。统一使用 build_sutra_pages.py。
import sys; sys.exit("此脚本已作废，请使用 build_sutra_pages.py");
#!/usr/bin/env python3
"""重建 pages/sutras.html：恢复原版三栏布局（左分类+搜索+经目，右内嵌阅读），经目列表取2043条带（译），并兼容 translations 字段格式。"""
import json, os, re
from pathlib import Path

ROOT = Path("/home/user/workspace/13511660557912876654/buddhist-ontology")
TRANS = ROOT / "data" / "modern-translation"
SUTRAS_TXT = ROOT / "sutras"

# 卷次映射：按经号范围归到11类
def vol_of(tid):
    m = re.match(r't(\d+)', tid)
    if not m: return "其他"
    n = int(m.group(1))
    # 阿含部 t0001-t0151
    if 1 <= n <= 151: return "阿含部"
    # 本缘·般若 (t0152-t0263)
    if 152 <= n <= 263: return "本缘·般若"
    # 般若部 t0220-t0263 实际重复，这里统一法华华严起始
    # 法华·华严 t0262-t0320
    if 262 <= n <= 320: return "法华·华严"
    # 宝积·涅槃·大集 t0310-t0397
    if 310 <= n <= 397: return "宝积·涅槃·大集"
    # 经集部 t0398-t0591
    if 398 <= n <= 591: return "经集部"
    # 密教部 t0848-t1420
    if 848 <= n <= 1420: return "密教部"
    # 律部 t1421-t1459
    if 1421 <= n <= 1459: return "律部"
    # 释经论·毗昙 t1505-t1563
    if 1505 <= n <= 1563: return "释经论·毗昙"
    # 中观·瑜伽·论集 t1564-t1878
    if 1564 <= n <= 1878: return "中观·瑜伽·论集"
    # 诸宗·史传·目录·事汇·外教·索引 t1879+
    if n >= 1879: return "诸宗·史传·目录·事汇·外教·索引"
    return "其他"

# 读 plan.json 获取 author
plan_path = ROOT / "_b198" / "plan.json"
plan = {}
if plan_path.exists():
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)

def find_title_author(tid):
    # 优先用 JSON 内的 title/translator
    jp = TRANS / f"{tid}.json"
    title = ""
    author = ""
    if jp.exists():
        with open(jp, encoding="utf-8") as f:
            d = json.load(f)
        title = d.get("title", "") or ""
        author = d.get("translator", "") or ""
    if not title and tid in plan:
        title = plan[tid].get("title", "")
    if not title:
        title = tid
    return title, author

entries = []
for fn in sorted(os.listdir(TRANS)):
    if not fn.endswith(".json"): continue
    tid = fn[:-5]
    title, author = find_title_author(tid)
    entries.append({
        "id": tid,
        "title": title,
        "author": author,
        "n": 0,
        "vol": vol_of(tid)
    })
print(f"entries={len(entries)}")

# 排序：按数字经号排
def sort_key(e):
    m = re.match(r't(\d+)([a-z]?)$', e["id"])
    if m:
        return (int(m.group(1)), m.group(2))
    return (9999, e["id"])
entries.sort(key=sort_key)

VOLS = ['阿含部','本缘·般若','般若部','法华·华严','宝积·涅槃·大集',
        '经集部','密教部','律部','释经论·毗昙','中观·瑜伽·论集','诸宗·史传·目录·事汇·外教·索引']

sutras_json = json.dumps(entries, ensure_ascii=False)
vols_json = json.dumps(VOLS, ensure_ascii=False)

HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全藏原典 · 佛学本体论</title>
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<link rel="stylesheet" href="../css/tailwind.min.css">
<link rel="stylesheet" href="../css/tailwind-extra.css">
<link rel="stylesheet" href="../css/custom.css">
<link rel="stylesheet" href="../css/mobile.css">
<link rel="stylesheet" href="../css/font-awesome.min.css">
<style>
  body{{font-family:"Noto Serif SC","Source Han Serif SC",serif;background:#F8F4E9;}}
  .scroll-thin::-webkit-scrollbar{{width:6px;height:6px;}}
  .scroll-thin::-webkit-scrollbar-thumb{{background:rgba(139,90,43,.3);border-radius:3px;}}
  .vol-tag{{display:inline-block;padding:2px 8px;border-radius:4px;background:#8B5A2B;color:white;font-size:12px;margin-right:6px;}}
  .yi-badge{{display:inline-block;color:#c8350d;font-weight:bold;margin-left:4px;font-size:0.85em;}}
  .sutra-item{{padding:6px 8px;border-bottom:1px dashed #ece1ca;cursor:pointer;font-size:13px;transition:background .15s;}}
  .sutra-item:hover{{background:#fff3e8;}}
  .sutra-item.active{{background:#fbe9cc;border-left:3px solid #D4AF37;}}
  .sutra-item .sid{{color:#8B5A2B;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:11px;margin-right:6px;}}
  .vol-filter{{transition:all .15s;}}
  .vol-filter.active{{background:#8B5A2B;color:#fff;border-color:#8B5A2B;}}
</style>
</head>
<body class="text-buddha-dark">

<!-- 顶部导航 -->
<nav class="bg-white shadow-md sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between flex-wrap gap-2">
    <a href="../index.html" class="text-xl font-bold text-buddha-primary flex items-center gap-2">
      <i class="fa fa-dharma-wheel text-buddha-secondary"></i>佛学本体论
    </a>
    <div class="flex gap-4 text-xs flex-wrap">
      <a href="../index.html" class="hover:text-buddha-secondary">首页</a>
      <a href="ontology.html" class="hover:text-buddha-secondary">本体总纲</a>
      <a href="sutras.html" class="text-buddha-primary font-bold">全藏原典</a>
      <a href="search.html" class="hover:text-buddha-secondary">全文检索</a>
      <a href="dict.html" class="hover:text-buddha-secondary">佛学词典</a>
      <a href="parallel.html" class="hover:text-buddha-secondary">异译对照</a>
      <a href="graph.html" class="hover:text-buddha-secondary">义理图谱</a>
      <a href="kepan.html" class="hover:text-buddha-secondary">科判导航</a>
      <div class="nav-dropdown">
        <a href="javascript:void(0)" class="hover:text-buddha-secondary nav-dropdown-toggle">佛学知识<span class="nav-caret">▾</span></a>
        <div class="nav-dropdown-menu">
          <a href="panjiao.html">宗派判教</a>
          <a href="translation.html">佛典译学</a>
          <a href="timeline.html">译传时间轴</a>
        </div>
      </div>
      <a href="inference.html" class="hover:text-buddha-secondary">概念推演</a>
    </div>
  </div>
</nav>

<div class="max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-4 gap-6">

  <!-- 左侧：分类筛选 + 搜索 + 经目 -->
  <aside class="lg:col-span-1">
    <div class="bg-white rounded-lg shadow p-4 sticky top-20 max-h-[calc(100vh-100px)] overflow-auto scroll-thin">
      <h3 class="font-bold text-buddha-primary mb-3 flex items-center gap-2">
        <i class="fa fa-book"></i>
        <span>大正藏经目</span>
        <span id="totalBadge" class="ml-auto text-xs bg-buddha-primary/10 text-buddha-primary px-2 py-0.5 rounded"></span>
      </h3>

      <div class="mb-3">
        <input id="searchInput" type="text" placeholder="搜索经名 / 译者 / 经号…"
               class="w-full px-3 py-2 border border-buddha-primary/20 rounded text-sm focus:outline-none focus:border-buddha-primary">
      </div>

      <div class="mb-3 flex flex-wrap gap-1 text-xs" id="volFilters">
        <button class="vol-filter px-2 py-1 rounded border border-buddha-primary/30 hover:bg-buddha-primary/10 active" data-vol="">全部</button>
      </div>

      <div id="sutraList" class="space-y-0 text-sm"></div>
    </div>
  </aside>

  <!-- 右侧：经文阅读区 -->
  <main class="lg:col-span-3">
    <div id="welcome" class="bg-white rounded-lg shadow p-8">
      <div class="text-center mb-6">
        <i class="fa fa-book text-buddha-primary text-5xl mb-4 opacity-30"></i>
        <h2 class="text-2xl font-serif font-bold mb-3">大正藏白话原典库</h2>
        <p class="text-buddha-dark/60 max-w-2xl mx-auto leading-relaxed">
          左侧按大正藏册次筛选，已完成白话精译
          <span class="text-buddha-primary font-bold" id="welcomeCount">2043</span>部，
          每部经名均带 <span class="yi-badge">（译）</span> 标记，点击经名即在右侧加载白话译文，
          点"打开独立阅读页"可在新页按原版单列样式查看原文对照。
        </p>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-3xl mx-auto text-sm">
        <div class="p-3 bg-buddha-paper rounded"><div class="font-bold text-buddha-primary">T01-T02</div><div class="text-xs text-buddha-dark/60">阿含部</div></div>
        <div class="p-3 bg-buddha-paper rounded"><div class="font-bold text-buddha-primary">T04-T08</div><div class="text-xs text-buddha-dark/60">本缘·般若</div></div>
        <div class="p-3 bg-buddha-paper rounded"><div class="font-bold text-buddha-primary">T09-T10</div><div class="text-xs text-buddha-dark/60">法华·华严</div></div>
        <div class="p-3 bg-buddha-paper rounded"><div class="font-bold text-buddha-primary">T11-T14</div><div class="text-xs text-buddha-dark/60">宝积·涅槃·大集</div></div>
        <div class="p-3 bg-buddha-paper rounded"><div class="font-bold text-buddha-primary">T18-T21</div><div class="text-xs text-buddha-dark/60">密教部</div></div>
        <div class="p-3 bg-buddha-paper rounded"><div class="font-bold text-buddha-primary">T22-T24</div><div class="text-xs text-buddha-dark/60">律部</div></div>
        <div class="p-3 bg-buddha-paper rounded"><div class="font-bold text-buddha-primary">T25-T27</div><div class="text-xs text-buddha-dark/60">释经论·毗昙</div></div>
        <div class="p-3 bg-buddha-paper rounded"><div class="font-bold text-buddha-primary">T28-T32</div><div class="text-xs text-buddha-dark/60">中观·瑜伽·论集·诸宗</div></div>
      </div>
    </div>

    <article id="sutraView" class="hidden bg-white rounded-lg shadow">
      <header class="p-6 border-b border-buddha-primary/10">
        <div class="flex items-center gap-2 text-xs text-buddha-dark/50 mb-2 flex-wrap">
          <span id="sVol" class="vol-tag"></span>
          <span id="sId"></span><span>·</span><span id="sAuthor"></span>
        </div>
        <div class="flex items-center justify-between flex-wrap gap-3">
          <h2 id="sTitle" class="text-xl font-serif font-bold text-buddha-primary"></h2>
          <a id="sOpenLink" href="#" target="_blank"
             class="text-xs px-3 py-1.5 bg-buddha-primary text-white rounded hover:bg-buddha-primary/90">
            <i class="fa fa-external-link mr-1"></i>打开独立阅读页
          </a>
        </div>
      </header>
      <div id="sutraContent" class="p-6 max-h-[75vh] overflow-auto scroll-thin"></div>
    </article>
  </main>
</div>

<script>
function parseModern(m){{
  if(!m) return {{xbt:"", zw:"", yj:""}};
  let xbt="", yj="", body=m;
  const mx = body.match(/^【([^】]+)】/);
  if(mx){{ xbt=mx[1].trim(); body=body.slice(mx[0].length); }}
  const my = body.match(/【(?:义解|义贯|释义|义理|要义|解说)】([\\s\\S]*)$/);
  if(my){{ yj=my[1].trim(); body=body.slice(0,my.index).trim(); }}
  return {{xbt, zw:body, yj}};
}}

const SUTRAS = {sutras_json};
const VOLS = {vols_json};

const listEl = document.getElementById('sutraList');
const volFiltersEl = document.getElementById('volFilters');
const searchInput = document.getElementById('searchInput');
const totalBadge = document.getElementById('totalBadge');
const welcomeCount = document.getElementById('welcomeCount');
const welcome = document.getElementById('welcome');
const view = document.getElementById('sutraView');

let currentVol = '';
let currentKw = '';

VOLS.forEach(v => {{
  const btn = document.createElement('button');
  btn.className = 'vol-filter px-2 py-1 rounded border border-buddha-primary/30 hover:bg-buddha-primary/10';
  btn.dataset.vol = v; btn.textContent = v;
  volFiltersEl.appendChild(btn);
}});
volFiltersEl.addEventListener('click', e => {{
  const btn = e.target.closest('.vol-filter'); if(!btn) return;
  currentVol = btn.dataset.vol;
  [...volFiltersEl.children].forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  renderList();
}});

function renderList(){{
  const kw = currentKw.trim().toLowerCase();
  const filtered = SUTRAS.filter(s=>{{
    if(currentVol && s.vol!==currentVol) return false;
    if(kw && !(s.id.toLowerCase().includes(kw)
               || (s.title||'').toLowerCase().includes(kw)
               || (s.author||'').toLowerCase().includes(kw))) return false;
    return true;
  }});
  totalBadge.textContent = filtered.length + ' / ' + SUTRAS.length;
  listEl.innerHTML = filtered.map(s=>{{
    return `<div class="sutra-item" data-id="${{s.id}}"><span class="sid">${{s.id}}</span>${{s.title}}<span class="yi-badge">（译）</span></div>`;
  }}).join('');
}}

listEl.addEventListener('click', e=>{{
  const it = e.target.closest('.sutra-item'); if(!it) return;
  [...listEl.children].forEach(c=>c.classList.remove('active'));
  it.classList.add('active');
  loadSutra(it.dataset.id);
}});

searchInput.addEventListener('input', e=>{{ currentKw=e.target.value; renderList(); }});

function loadSutra(id){{
  fetch(`../data/modern-translation/${{id}}.json`)
    .then(r=>r.json())
    .then(data=>{{
      welcome.classList.add('hidden');
      view.classList.remove('hidden');
      const s = SUTRAS.find(x=>x.id===id);
      document.getElementById('sVol').textContent = s.vol;
      document.getElementById('sId').textContent = id;
      document.getElementById('sAuthor').textContent = (data.translator||s.author||'');
      document.getElementById('sTitle').textContent = '《'+(data.title||s.title||id)+'》';
      document.getElementById('sOpenLink').href = '../'+id+'.html';
      const c = document.getElementById('sutraContent');
      const segs = data.translations || data.segments || [];
      c.innerHTML = segs.map((seg,i)=>{{
        let sub, exp, tr, orig;
        if(seg.modern !== undefined){{
          const p = parseModern(seg.modern);
          sub = p.xbt; exp = p.yj; tr = p.zw; orig = seg.original_preview || '';
        }} else {{
          sub = seg.subtitle || seg.subheading || '';
          exp = seg.explanation || '';
          tr = seg.modern || seg.translation || '';
          orig = seg.original || seg.original_preview || '';
        }}
        return `
        <div class="mb-6 pb-4 border-b border-dashed border-buddha-primary/20">
          ${{sub?`<div class="font-bold text-buddha-primary mb-2">【${{sub}}】</div>`:''}}
          ${{exp?`<div class="bg-buddha-light/60 p-3 mb-2 border-l-4 border-buddha-primary/40 text-sm leading-relaxed"><strong>【义解】</strong>${{exp}}</div>`:''}}
          ${{tr?`<div class="leading-loose text-[15px]" style="text-indent:2em;">${{tr}}</div>`:''}}
          ${{orig?`<details class="mt-2 text-sm text-buddha-dark/60"><summary>查看原文</summary><pre class="whitespace-pre-wrap bg-buddha-light/30 p-3 mt-1 border-l-2 border-gray-300 leading-relaxed" style="font-family:inherit;">${{orig}}</pre></details>`:''}}
        </div>`;
      }}).join('');
      c.scrollTop = 0;
    }});
}}

welcomeCount.textContent = SUTRAS.length;
renderList();
</script>
</body>
</html>
'''

out_pages = ROOT / "pages" / "sutras.html"
out_root = ROOT / "sutras.html"
with open(out_pages, "w", encoding="utf-8") as f:
    f.write(HTML)
# 根目录 sutras.html 重定向到 pages/sutras.html
with open(out_root, "w", encoding="utf-8") as f:
    f.write('<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=pages/sutras.html"><title>全藏原典</title></head><body>跳转中…若未跳转，请<a href="pages/sutras.html">点此进入经目</a>。</body></html>')

print(f"pages/sutras.html written: {len(entries)} entries, {len(HTML)} bytes")
print(f"root sutras.html redirect written")

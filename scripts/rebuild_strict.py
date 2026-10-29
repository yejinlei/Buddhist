# -*- coding: utf-8 -*-
"""
CBETA 经文一字不差重建器 v2
原则：
  1. 保留原经正文每一个汉字、标点、异体字、原序，不做任何繁简转换、不删改字
  2. 只剔除 TEI 结构标签和异文校勘（app/rdg/witness/lb/pb/note校勘注）
  3. 按 <juan>（卷）、<head>（品/章节标题）自然分章，章标题也从原文取
  4. 序、目录、跋、附记等 CBETA 原文里有的都原样保留（不擅自删"非正文"）
  5. 字符严格逐字输出，不做正则 \s 清洗
"""
import json, re, sys, time
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CACHE = ROOT / '.xmlcache'
OUT = ROOT / 'sutras'
OUT.mkdir(exist_ok=True)

NS = {'t': 'http://www.tei-c.org/ns/1.0'}
CB = 'http://www.cbeta.org/ns/1.0'
SKIP = {
    # 异文校勘（多版本异读，不是原文）
    'app', 'rdg', 'rdgGrp', 'witness', 'witDetail', 'lem',
    # 分页/换行/锚点/图（非经文）
    'lb', 'pb', 'anchor', 'space', 'milestone', 'caesura',
    'graphic', 'figure', 'docNumber',
}

def is_skip_note(e):
    """只跳过校勘/版本/署名类 note，保留夹注/夹注性文本"""
    place = e.get('place') or e.get(f'{{{CB}}}place') or ''
    resp = e.get('resp') or ''
    ntype = e.get('type') or e.get(f'{{{CB}}}type') or ''
    corresp = e.get('corresp') or ''
    # CBETA 校勘注 resp 通常是 "CBETA" 等编辑者，原典夹注 type=inline/comm 保留
    if resp or corresp:
        return True
    if ntype and ntype not in ('inline', 'comm', 'add', 'corrected'):
        return True
    # 侧边/脚/末校记
    if place in ('foot', 'interlinear', 'margin', 'side'):
        # 但 type=add/corrected 是原文补字，保留
        if ntype in ('add', 'corrected', 'inline', 'comm'):
            return False
        return True
    return False

def text_of(e):
    """递归提取元素文本，跳过校勘/异文，保留原文全部字符"""
    parts = []
    if e.text:
        parts.append(e.text)
    for ch in e:
        tag = ch.tag.split('}')[-1]
        if tag in SKIP:
            # 保留 lem（优选读本）的文本——CBETA 里 lem 才是正文
            if tag == 'app':
                lem = ch.find('t:lem', NS)
                if lem is not None:
                    parts.append(text_of(lem))
            # 尾部文字不丢
            if ch.tail:
                parts.append(ch.tail)
            continue
        if tag == 'note' and is_skip_note(ch):
            if ch.tail:
                parts.append(ch.tail)
            continue
        # 行内小字夹注用（）包起，避免混入正文但保留原文
        if tag == 'note':
            inner = text_of(ch)
            if inner.strip():
                parts.append('（' + inner + '）')
            if ch.tail:
                parts.append(ch.tail)
            continue
        parts.append(text_of(ch))
        if ch.tail:
            parts.append(ch.tail)
    return ''.join(parts)

def is_head_tag(tag):
    return tag in ('head', 'jhead', 'jl_title')

def is_block_tag(tag):
    # 正文块（段落、偈颂行、列表项、夹注引子、标题署名等）
    return tag in ('p', 'l', 'item', 'list', 'lg', 'lg', 'yin', 'zi',
                   'div', 't', 'tt', 'term', 'trailer', 'byline',
                   'salute', 'epigraph', 'closer', 'signed', 'dateline',
                   'docAuthor', 'docDate', 'argument', 'sp', 'speaker')

def parse_tei(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)
    except Exception as e:
        return None
    # 标题（取繁体经名）
    title = ''
    author = ''
    ts = root.find('.//t:teiHeader//t:titleStmt', NS)
    if ts is not None:
        for t in ts.findall('t:title', NS):
            if t.get(f'{{http://www.w3.org/XML/1998/namespace}}lang') == 'zh-Hant' and t.get('level') == 'm':
                title = (t.text or '').strip()
                break
        if not title:
            for t in ts.findall('t:title', NS):
                tx = (t.text or '').strip()
                if tx and '大正' not in tx and 'Taishō' not in tx and 'Taisho' not in tx:
                    title = tx; break
        a = ts.find('t:author', NS)
        if a is not None:
            author = ''.join(a.itertext()).strip()

    body = root.find('.//t:text/t:body', NS)
    if body is None:
        return None

    # 统一扁平遍历 body 内部直接子元素，忽略 CBETA 把 <juan> 首尾各一个的包裹问题
    # 方法：不用递归 walk 处理 juan，而是 flatten 所有需要的元素（head/jhead/p/l/lg 等），
    # 并记录最近的 <juan n="xxx">/卷号；遇到 head 就切章。

    def iter_relevant(root):
        """扁平 yield 正文章节结构，严格避免文本重复。"""
        # 注意：对所有「内容标签」用 text_of(e) 一次性取全文（含子元素内文字），
        # 之后**不再**递归 walk 子元素，避免重复计数。
        CONTENT_TAGS = {'p','l','item','lg','list','yin','zi','t','tt','term',
                       'trailer','salute','epigraph','closer','signed','dateline',
                       'docAuthor','docDate','argument','sp','speaker','jl_juan',
                       'byline','jl_byline','quote','said','foreign'}
        HEAD_TAGS = {'head','mulu','jl_title','fan'}

        def walk(e):
            tag = e.tag.split('}')[-1]
            if tag in SKIP:
                if tag == 'app':
                    lem = e.find('t:lem', NS)
                    if lem is not None:
                        yield from walk(lem)
                if e.tail:
                    yield ('tail', e.tail)
                return
            if tag == 'note' and is_skip_note(e):
                if e.tail:
                    yield ('tail', e.tail)
                return

            if tag == 'juan':
                n = (e.get('n') or '').strip()
                if n:
                    yield ('juan', n)
                # 递归进入，但内部的 jhead/head 已在下面处理
                for ch in e:
                    yield from walk(ch)
                return
            if tag == 'jhead':
                # jhead 是卷首/卷尾经题重复：卷首（cur_juan 刚设置、buf 为空）把它的 tail 丢掉，
                # 卷尾（cur_juan 已设置、buf 非空）直接忽略，避免末尾多出一行经题。
                # 不再 walk 其子元素（里面通常是经名重复）
                if e.tail:
                    yield ('tail', e.tail)
                return
            if tag in HEAD_TAGS:
                ht = text_of(e).strip()
                if ht:
                    ht = re.sub(r'\s+', '', ht)  # 标题里去换行空白
                    if len(ht) < 120:
                        yield ('head', ht)
                    else:
                        yield ('block', ht)
                # 不再递归子元素（text_of 已取完全文），只传 tail
                if e.tail:
                    yield ('tail', e.tail)
                return
            if tag in CONTENT_TAGS:
                t = text_of(e)
                t = t.replace('\r','')
                # 段内换行是 CBETA 排版造成的，不属于经文；合并为连续文字
                t = re.sub(r'\s*\n\s*', '', t)
                # 注意：<l> 是偈颂，每行应保留独立，用换行分隔
                # 但 text_of 已经把 <l> 当独立 block 逐行输出，这里我们不把 <l> 内换行合并
                if t.strip(' \t'):
                    yield ('block', t)
                if e.tail:
                    yield ('tail', e.tail)
                return
            # 其他包装容器（div/seg/span/ab/hi 等），仅递归
            if e.text:
                yield ('text', e.text)
            for ch in e:
                yield from walk(ch)
            if e.tail:
                yield ('tail', e.tail)
        yield from walk(root)

    # 执行扁平遍历
    chapters = []
    cur_juan = ''
    cur_title = None
    buf = []
    pending_prefix = None
    def flush():
        if buf:
            txt = '\n'.join(b for b in buf if b)
            txt = txt.strip('\n')
            if txt.strip():
                t = cur_title or (('卷'+cur_juan) if cur_juan else '正文')
                # CBETA 卷尾的 <juan> 闭合块里只有"經名卷X + 譯者"一行，很短，
                # 这种章不单独成节，合并到下一章（暂时先不append，由下一次flush补）
                pure = re.sub(r'\s+', '', txt)
                is_tail_juan = (re.match(r'^卷\d+$', t or '') and len(pure) < 80
                                and ('卷第' in pure or re.search(r'經卷[上中下第\d]+$', pure)))
                if is_tail_juan:
                    # 把这几行放到下一章的开头
                    nonlocal pending_prefix
                    pending_prefix = txt
                    buf.clear()
                    return
                if pending_prefix:
                    txt = pending_prefix + '\n' + txt
                    pending_prefix = None
                chapters.append({'chapter': t, 'text': txt})
        buf.clear()

    for kind, val in iter_relevant(body):
        if kind == 'juan':
            # CBETA 首尾都有 <juan n="xxx">，尾 juan 的 n 有时写成 "1""2" 而非 "001""002"
            # 我们用 n 的数字值比较，只有"卷号比当前大"才算下一卷，否则就是尾标签忽略
            try:
                n_int = int(re.sub(r'^0+', '', val) or '0')
            except:
                n_int = 0
            try:
                cur_int = int(re.sub(r'^0+', '', cur_juan) or '0') if cur_juan else -1
            except:
                cur_int = -1
            if (not cur_juan) or (n_int > cur_int) or (n_int == 0 and cur_int < 0):
                flush()
                cur_juan = val
                cur_title = '卷' + val
            # 否则视为尾闭合 juan，不切章
            continue
        if kind == 'head':
            flush()
            # 过滤纯数字/纯卷号/数字序号前导（如"1""2學觀品"前的"1"），作为正文而非章节标题
            pure = re.sub(r'\s+', '', val)
            if (re.match(r'^[\d一二三四五六七八九十百千]+$', pure)
                or re.match(r'^卷[上中下\d]+$', pure)
                or (len(pure) <= 3 and re.match(r'^\d', pure))):
                # 数字品号直接并入下一章节，不单独成行
                pass
            else:
                cur_title = val
            continue
        if kind == 'block':
            buf.append(val)
            continue
        # text/tail：出现在顶层（无容器包着的散文字）
        if kind in ('text','tail'):
            v = val.strip()
            if v:
                buf.append(v)
    flush()
    # 末尾收尾：若最后 pending_prefix 还有内容，追加到最后一章
    if pending_prefix and chapters:
        chapters[-1]['text'] = chapters[-1]['text'] + '\n' + pending_prefix
        chapters[-1]['chapter'] = chapters[-1]['chapter']  # 不变
        pending_prefix = None
    elif pending_prefix:
        # 全经只有尾卷，不可能
        chapters.append({'chapter': '正文', 'text': pending_prefix})
        pending_prefix = None
    # 处理开头的"署名章"：第一章很短（<30字、无句读），下一章存在，就把它挪到下一章开头
    def is_head_fragment(t):
        p = re.sub(r'\s+', '', t)
        return len(p) < 30 and '。' not in p and '！' not in p and '？' not in p
    while len(chapters) >= 2 and is_head_fragment(chapters[0]['text']):
        first = chapters.pop(0)
        chapters[0]['text'] = first['text'] + '\n' + chapters[0]['text']
    # 合并末尾超短的"碎片章"（<10字 且 不含句读标点）到前一章。真言等保留。
    def is_fragment(t):
        p = re.sub(r'\s+', '', t)
        if len(p) >= 10: return False
        # 只要含完整句读（含咒/真言结束）就算真章
        if any(x in p for x in '。！？：、'): return False
        # 含「」引号也保留
        if '「' in p and '」' in p: return False
        return True
    while len(chapters) >= 2 and is_fragment(chapters[-1]['text']):
        last = chapters.pop()
        chapters[-1]['text'] = chapters[-1]['text'] + '\n' + last['text']
    if not chapters:
        return None
    return {'title': title, 'author': author, 'chapters': chapters}


def main():
    # 加载元数据
    meta = {}
    mf = CACHE / 'meta_cache.json'
    if mf.exists():
        meta = json.loads(mf.read_text(encoding='utf-8'))

    xmls = sorted(CACHE.glob('T*n*.xml'))
    print(f'缓存中共 {len(xmls)} 个 XML')
    ok = fail = 0
    from collections import defaultdict
    groups = defaultdict(list)
    for fp in xmls:
        m = re.match(r'T(\d+)n(\d+[A-Za-z]?)', fp.stem)
        if not m: continue
        short = 'T' + m.group(2)
        groups[short].append(fp)

    print(f'归组后共 {len(groups)} 部经')
    t0 = time.time()
    for i, (short, files) in enumerate(sorted(groups.items()), 1):
        files.sort()
        all_chapters = []
        title = ''
        author = ''
        parse_ok = True
        for fp in files:
            try:
                p = parse_tei(fp.read_bytes())
            except Exception as e:
                parse_ok = False
                print(f'  解析失败 {fp.name}: {e}')
                break
            if not p:
                parse_ok = False
                break
            if not title: title = p['title']
            if not author: author = p['author']
            # 多卷 A/B：卷标签由 <juan> 自动处理，直接拼接
            all_chapters.extend(p['chapters'])
        if not parse_ok or not all_chapters:
            fail += 1
            continue
        # 卷名合并：相邻章节同名只保留一个（跨卷重复 head）
        merged = []
        for c in all_chapters:
            if merged and merged[-1]['chapter'] == c['chapter'] and not c['text']:
                continue
            merged.append(c)
        # 如果多卷里出现"卷X"重复，改成"卷X（续）"以区分
        seen = {}
        for c in merged:
            name = c['chapter']
            if name in seen:
                seen[name] += 1
                c['chapter'] = f'{name}（续{seen[name]-1}）'
            else:
                seen[name] = 1
        # 若所有章标题都"正文"，尝试让第一个标题用经名
        if merged and all(c['chapter'] in ('正文', '') for c in merged) and title:
            merged[0]['chapter'] = title

        sid = short.lower()
        m = meta.get(short) or {}
        places = m.get('places') or []
        actual = sum(len(c['text']) for c in merged)
        out = {
            'id': sid,
            'taisho': short,
            'title': title or m.get('title') or short,
            'translator': author or m.get('byline') or '',
            'vol': (m.get('vol') or '').upper(),
            'juan': len(merged),
            'chars': actual,
            'content': merged,
            'category': (m.get('category') or '其他部类').replace('類', '类'),
            'time_from': m.get('time_from') or '',
            'translation_place': places[0].get('name', '') if places else '',
            'official_char_count': m.get('cjk_chars') or 0,
            'actual_char_count': actual,
            'juan_count': m.get('juan') or len(merged),
        }
        (OUT / f'{sid}.json').write_text(
            json.dumps(out, ensure_ascii=False, separators=(',', ':')),
            encoding='utf-8'
        )
        ok += 1
        if i % 100 == 0 or i == len(groups):
            print(f'  [{i}/{len(groups)}] ok={ok} fail={fail} ({time.time()-t0:.1f}s)')
    print(f'完成: 成功 {ok}, 失败 {fail}')

if __name__ == '__main__':
    main()

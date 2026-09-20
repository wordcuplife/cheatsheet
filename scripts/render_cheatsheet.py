#!/usr/bin/env python3
"""Render reviewed study notes into a dense, three-column A4 PDF.

Python dependencies: reportlab, matplotlib, fonttools. See references/renderer.md.
"""
import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape


def arguments():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--title', default='Cheatsheet')
    p.add_argument('--legend', default='★ Exam focus / p.: lecture PDF page')
    p.add_argument('--sources', default='Supplied course materials')
    p.add_argument('--pages', type=int, default=2)
    p.add_argument('--font', type=Path)
    p.add_argument('--font-index', type=int, default=0)
    p.add_argument('--font-size', type=float, default=6.15)
    p.add_argument('--min-font-size', type=float, default=5.0)
    p.add_argument('--overwrite', action='store_true')
    a = p.parse_args()
    if a.pages < 1 or not 0 < a.min_font_size <= a.font_size or a.font_index < 0:
        p.error('Require pages >= 1 and 0 < min-font-size <= font-size, font-index >= 0')
    if a.output.suffix.lower() != '.pdf':
        p.error('Output must end in .pdf')
    if a.input.resolve() == a.output.resolve():
        p.error('Input and output must differ')
    for path in [a.output, a.output.with_suffix('.audit.json')]:
        if path.exists() and not a.overwrite:
            p.error(f'File already exists: {path}; choose another name or use --overwrite')
    return a


def read_modules(text):
    modules = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith('@'):
            parts = line[1:].split('|', 2)
            if len(parts) != 3 or not parts[0].isdigit() or not parts[1].strip():
                raise ValueError(f'Line {n}: expected @integer|Module title|Subtitle')
            modules.append({'number': parts[0], 'title': parts[1], 'subtitle': parts[2], 'items': []})
        else:
            if not modules:
                raise ValueError(f'Line {n}: content must follow a module header')
            kind, value = 'p', line
            for prefix, k in [('!=', 'rf'), ('=', 'f'), ('#', 'h'), (':', 's'), ('!', 'r')]:
                if line.startswith(prefix):
                    kind, value = k, line[len(prefix):]
                    break
            if not value.strip():
                raise ValueError(f'Line {n}: empty block')
            modules[-1]['items'].append({'kind': kind, 'text': value, 'id': n})
    if not modules or any(not m['items'] for m in modules):
        raise ValueError('Provide at least one nonempty module; empty modules are not allowed')
    if len({m['number'] for m in modules}) != len(modules):
        raise ValueError('Module sequence numbers must be unique')
    return modules


def render(a, work):
    # Cache stays in task scratch space, not in the installed skill or user home.
    os.environ.setdefault('MPLCONFIGDIR', str(a.output.parent / '.cheatsheet-cache' / 'mpl'))
    os.environ.setdefault('XDG_CACHE_HOME', str(a.output.parent / '.cheatsheet-cache'))
    import matplotlib
    from matplotlib.mathtext import MathTextParser
    from matplotlib.font_manager import FontProperties, findfont
    from fontTools.ttLib import TTFont
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont as RLFont
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph
    from reportlab.lib.pagesizes import A4

    text = a.input.read_text(encoding='utf-8')
    modules = read_modules(text)
    warnings = []
    symbols = Path(findfont('DejaVu Sans'))
    source = a.font
    if source is None:
        candidates = sorted(Path('/System/Library/AssetsV2').glob('com_apple_MobileAsset_Font*/*/AssetData/[Hh]anzi[Pp]en.ttc'))
        candidates += [Path('/System/Library/Fonts/Supplemental/HanziPen.ttc')]
        source = next((p for p in candidates if p.is_file()), None)
        if source is None:
            source = symbols
            warnings.append('No handwriting font discovered; using DejaVu Sans. Confirm fallback with user.')
    if not source.is_file():
        raise ValueError(f'Font not found: {source}')
    src = TTFont(str(source), fontNumber=a.font_index)
    fs_type = src['OS/2'].fsType if 'OS/2' in src else 0
    if fs_type & (0x2 | 0x100 | 0x200):
        raise ValueError('Font license flags restrict embedding/subsetting; provide a suitable licensed font')
    chars = set(text + a.title + a.legend + a.sources + ' A4 / 100% / continued 0123456789')
    cmap = src.getBestCmap()
    symchars = set(TTFont(str(symbols)).getBestCmap())
    missing = sorted(c for c in chars if not c.isspace() and ord(c) not in cmap and ord(c) not in symchars)
    if missing:
        raise ValueError('Unsupported characters; supply a covering font: ' + repr(''.join(missing)))
    # Convert outlines to an embeddable TrueType subset; also supports CFF collections.
    chosen = {ord(c): cmap[ord(c)] for c in chars if ord(c) in cmap}
    order = ['.notdef'] + sorted(set(chosen.values()) - {'.notdef'})
    glyphset = src.getGlyphSet()
    glyphs = {}
    for name in order:
        rec = DecomposingRecordingPen(glyphset)
        glyphset[name].draw(rec)
        pen = TTGlyphPen(None)
        rec.replay(Cu2QuPen(pen, 1.0, reverse_direction=True))
        glyphs[name] = pen.glyph()
    fb = FontBuilder(src['head'].unitsPerEm, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(chosen)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({n: src['hmtx'].metrics[n] for n in order})
    fb.setupHorizontalHeader(ascent=src['hhea'].ascent, descent=src['hhea'].descent)
    fb.setupNameTable({'familyName': 'Cheatsheet Hand', 'styleName': 'Regular', 'uniqueFontIdentifier': 'CheatsheetHand', 'fullName': 'Cheatsheet Hand', 'psName': 'CheatsheetHand'})
    fb.setupOS2(sTypoAscender=src['hhea'].ascent, sTypoDescender=src['hhea'].descent,
                usWinAscent=src['OS/2'].usWinAscent, usWinDescent=src['OS/2'].usWinDescent)
    fb.setupPost()
    fb.setupMaxp()
    subset = work / 'hand.ttf'
    fb.save(str(subset))
    pdfmetrics.registerFont(RLFont('Hand', str(subset)))
    pdfmetrics.registerFont(RLFont('Symbols', str(symbols)))

    def rich(s):
        runs, buf, last = [], '', None
        for ch in s:
            font = 'Hand' if ord(ch) in cmap else 'Symbols'
            if last != font and buf:
                runs.append(f'<font name="{last}">{escape(buf)}</font>')
                buf = ''
            last, buf = font, buf + ch
        if buf:
            runs.append(f'<font name="{last}">{escape(buf)}</font>')
        return ''.join(runs)

    colors = {'h': '#087bff', 's': '#b924db', 'r': '#e9322a', 'p': '#141414'}
    W, H = A4
    margin, gap, top, bottom = 17., 10., H - 38., 31.
    width = (W - 2 * margin - 2 * gap) / 3
    available = top - bottom
    parser, mathcache, mathfonts = MathTextParser('path'), {}, {}
    matplotlib.rcParams.update({'mathtext.fontset': 'stix', 'mathtext.default': 'it'})

    def mathtext(s, size):
        def matrix(m):
            rows = m.group(1).split(r'\\')
            if len(rows) != 2:
                raise ValueError('smallmatrix helper requires exactly two rows; split larger matrices')
            return r'\genfrac{}{}{0}{}{' + rows[0].replace('&', r'\quad ') + '}{' + rows[1].replace('&', r'\quad ') + '}'
        s = re.sub(r'\\begin\{smallmatrix\}(.*?)\\end\{smallmatrix\}', matrix, s)
        key = (s, size)
        if key not in mathcache:
            fm = parser.parse('$' + s + '$', dpi=72, prop=FontProperties(size=size))
            for font, fs, ch, x, y in fm.glyphs:
                if font.fname not in mathfonts:
                    name = 'Math' + str(len(mathfonts))
                    pdfmetrics.registerFont(RLFont(name, font.fname))
                    mathfonts[font.fname] = name
            mathcache[key] = fm
        return mathcache[key]

    def para(s, size, color, w=width - 7):
        p = Paragraph(rich(s), ParagraphStyle('note', fontName='Hand', fontSize=size,
                      leading=size * 1.22, textColor=HexColor(color), wordWrap='CJK', splitLongWords=True))
        _, height = p.wrap(w, 10000)
        return p, height

    def makeblock(item, size):
        k, s = item['kind'], item['text']
        if k in ('f', 'rf'):
            fm = mathtext(s, size + .65)
            scale = min(1., (width - 3) / max(1, fm.width))
            if (size + .65) * scale < a.min_font_size - .001:
                raise ValueError(f'Formula on line {item["id"]} too wide; split it into shorter display lines')
            return dict(item, obj=fm, scale=scale, height=fm.height * scale + 2.6,
                        font_size=(size + .65) * scale)
        fs = size + (1.25 if k == 'h' else .5 if k == 's' else 0)
        p, ph = para(s, fs, colors[k])
        pad = 3.2 if k == 'h' else 1.4 if k == 's' else .4
        return dict(item, obj=p, pad=pad, ph=ph, height=ph + pad + .4, font_size=fs)

    def header(m, continuation):
        title = m['title'] + (' (continued)' if continuation else '')
        p, ph = para(title, 10.5, '#64ba48', width - 20)
        sub, sh = para(m['subtitle'], 6.8, '#64ba48')
        return {'kind': 'module', 'obj': (p, ph, sub, sh, m['number']), 'height': max(15, ph) + sh + 5,
                'text': title, 'font_size': 10.5, 'id': None}

    def pack(size):
        blocks = [[makeblock(i, size) for i in m['items']] for m in modules]
        # Preserve original one-module-per-column style when it fits the requested slots.
        if len(modules) == a.pages * 3:
            columns = [[header(m, False)] + b for m, b in zip(modules, blocks)]
            if all(sum(x['height'] for x in col) <= available for col in columns):
                return columns
        columns, col, used = [], [], 0.
        for m, items in zip(modules, blocks):
            groups, i = [], 0
            while i < len(items):
                group = [items[i]]
                while group[-1]['kind'] in ('h', 's') and i + 1 < len(items):
                    i += 1
                    group.append(items[i])
                groups.append(group)
                i += 1
            head = header(m, False)
            if col and used + head['height'] + sum(b['height'] for b in groups[0]) > available:
                columns.append(col)
                col, used = [], 0.
            col.append(head)
            used += head['height']
            for group in groups:
                need = sum(b['height'] for b in group)
                if used + need > available:
                    columns.append(col)
                    head = header(m, True)
                    col, used = [head], head['height']
                if used + need > available:
                    return None
                col.extend(group)
                used += need
        if col:
            columns.append(col)
        return columns if len(columns) <= a.pages * 3 else None

    size, columns = a.font_size, None
    # In the six-module/two-page case, size each module independently before
    # allowing flow. This preserves clean module boundaries and larger type.
    if len(modules) == a.pages * 3:
        independent, sizes = [], []
        for m in modules:
            local = a.font_size
            while True:
                col = [header(m, False)] + [makeblock(i, local) for i in m['items']]
                fits = sum(b['height'] for b in col) <= available
                if fits or local <= a.min_font_size:
                    break
                local = max(a.min_font_size, round(local - .05, 4))
            if not fits:
                break
            independent.append(col)
            sizes.append(local)
        if len(independent) == len(modules):
            columns, size = independent, min(sizes)
    if columns is None:
        size = a.font_size
        while True:
            columns = pack(size)
            if columns is not None or size <= a.min_font_size:
                break
            size = max(a.min_font_size, round(size - .05, 4))
    if columns is None:
        raise ValueError('Content exceeds page budget at minimum font size; revise concision, split oversized blocks, or agree on more pages/smaller type. Nothing was dropped.')
    expected = [i['id'] for m in modules for i in m['items']]
    actual = [b['id'] for col in columns for b in col if b['id'] is not None]
    if actual != expected:
        raise ValueError('Internal error: content blocks missing, duplicated, or reordered')
    tempout = work / 'result.pdf'
    c = canvas.Canvas(str(tempout), pagesize=A4, pageCompression=1, initialFontName='Hand')
    c.setTitle(a.title)
    c.setSubject('Three-column printable study notes from supplied course materials')
    c.setViewerPreference('PrintScaling', 'None')
    c.setViewerPreference('Duplex', 'DuplexFlipLongEdge')
    audit = {'pages': a.pages, 'page_size_pt': [W, H], 'columns_per_page': 3,
             'body_font_pt': size, 'font_source': str(source), 'font_index': a.font_index,
             'content_sha256': hashlib.sha256(text.encode()).hexdigest(), 'warnings': warnings,
             'expected_blocks': len(expected), 'rendered_blocks': len(actual), 'placements': []}
    for pg in range(a.pages):
        c.setFillColor(HexColor('#ffffff'))
        c.rect(0, 0, W, H, fill=1, stroke=0)
        for s, fs, color, x, w in [(a.title, 9.2, '#141414', margin, 285),
                                  (a.legend, 5.6, '#e9322a', 320, W - 320 - margin)]:
            p, ph = para(s, fs, color, w)
            if ph > 12:
                raise ValueError('Header too long; shorten title/legend')
            p.drawOn(c, x, H - 25)
        c.setStrokeColor(HexColor('#909090'))
        c.setLineWidth(.35)
        c.line(margin, H - 29, W - margin, H - 29)
        for colno in range(3):
            idx = pg * 3 + colno
            if idx >= len(columns):
                continue
            col = columns[idx]
            stretch = min(1.08, available / sum(b['height'] for b in col))
            x, y = margin + colno * (width + gap), top
            for b in col:
                h, k = b['height'], b['kind']
                if k == 'module':
                    p, ph, sub, sh, num = b['obj']
                    c.setStrokeColor(HexColor('#64ba48'))
                    c.setFillColor(HexColor('#64ba48'))
                    c.setLineWidth(.65)
                    c.circle(x + 6, y - 7, 5.6, stroke=1, fill=0)
                    c.setFont('Hand', 9 if len(num) == 1 else 6.5)
                    c.drawCentredString(x + 6, y - 10, num)
                    p.drawOn(c, x + 16, y - ph)
                    sub.drawOn(c, x, y - max(15, ph) - sh)
                    c.setStrokeColor(HexColor('#087bff'))
                    c.setLineWidth(.45)
                    c.line(x, y - h + 1, x + width, y - h + 1)
                elif k in ('f', 'rf'):
                    fm, scale = b['obj'], b['scale']
                    c.saveState()
                    c.translate(x + .5, y - fm.height * scale - 1)
                    c.scale(scale, scale)
                    c.setFillColor(HexColor('#e9322a' if k == 'rf' else '#141414'))
                    for font, fs, ch, gx, gy in fm.glyphs:
                        c.setFont(mathfonts[font.fname], fs)
                        c.drawString(gx, gy + fm.depth, chr(ch))
                    for rx, ry, rw, rh in fm.rects:
                        c.rect(rx, ry + fm.depth, rw, rh, stroke=0, fill=1)
                    c.restoreState()
                else:
                    b['obj'].drawOn(c, x, y - b['pad'] - b['ph'])
                    if k == 'h':
                        c.setStrokeColor(HexColor('#bbbbbb'))
                        c.setLineWidth(.2)
                        c.line(x, y - h, x + width, y - h)
                audit['placements'].append({'page': pg + 1, 'column': colno + 1, 'id': b['id'],
                                            'kind': k, 'text': b['text'], 'font_pt': b['font_size'],
                                            'bounds_pt': [x, y - h, x + width, y]})
                y -= h * stretch
        p, ph = para(a.sources, 5., '#777777', W - 2 * margin - 110)
        if ph > 7:
            raise ValueError('Source footer too long; shorten the source label')
        p.drawOn(c, margin, 17)
        c.setFont('Hand', 5)
        c.setFillColor(HexColor('#777777'))
        c.drawRightString(W - margin, 18, f'A4 / 100% / {pg + 1} of {a.pages}')
        c.showPage()
    c.save()
    audit['pdf_sha256'] = hashlib.sha256(tempout.read_bytes()).hexdigest()
    tempaudit = work / 'audit.json'
    tempaudit.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tempout, a.output)
    os.replace(tempaudit, a.output.with_suffix('.audit.json'))
    print(json.dumps({'output': str(a.output.resolve()), 'pages': a.pages, 'modules': len(modules),
                      'blocks': len(actual), 'body_font_pt': size, 'warnings': warnings}, ensure_ascii=False))


def main():
    a = arguments()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='.cheatsheet-', dir=a.output.parent) as tmp:
            render(a, Path(tmp))
    except (ValueError, ImportError, OSError) as exc:
        raise SystemExit(f'cheatsheet: {exc}') from exc


if __name__ == '__main__':
    main()

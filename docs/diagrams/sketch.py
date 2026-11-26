#!/usr/bin/env python3
"""Draw the documentation diagrams in a hand-drawn (Excalidraw-like) style.

    python3 docs/diagrams/sketch.py            # all five, from the repository root
    python3 docs/diagrams/sketch.py top        # one of them

Reads   docs/diagrams/src/<name>.svg           plain boxes, straight connectors, text
Writes  analog/PAM4SerDes/docs/img/<name>.svg  the same drawing, sketched

The source keeps every box and connector straight and on its grid, so it stays easy to
edit by hand. This script only changes how things are drawn:

  - every box outline and every connector becomes a slightly wobbly pen stroke, and the
    longer ones are drawn twice, the way Excalidraw / rough.js does it
  - box fills become loose hachure over a faint wash
  - arrowheads become open, drawn V shapes
  - text is copied as it is, into its own group on top; so are the marks that carry a
    quantity (lane strips, bars drawn to scale)

The wobble is written into the path coordinates. There is no SVG filter, no marker, no
pattern and no gradient in the output, so every renderer draws the same picture (an
feDisplacementMap filter would be shorter, but resvg 0.47 displaces by scale squared and
tears the drawing apart). The random numbers are seeded per element: running the script
again without changing a source changes nothing.

What a source file may contain: <rect>, <path> made of M / L / H / V commands, <circle>,
<text>, and <g> around them (with a translate() or a class). The classes are the ones
in KINDS and WIRES below. Standard library only.
"""
import math
import os
import random
import re
import sys
import xml.etree.ElementTree as ET
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'analog', 'PAM4SerDes', 'docs', 'img'))
NAMES = ['top', 'biasing', 'clocking', 'transmitter', 'receiver']
NS = '{http://www.w3.org/2000/svg}'

# Handwriting faces that ship with common systems; nothing is downloaded. Comic Sans MS is
# on both Windows and macOS. The last entry is a plain face on purpose: the generic
# "cursive" is an ornate script on stock Linux and Android, and labels must stay readable.
FONT = "'Comic Sans MS', 'Chalkboard SE', 'Comic Neue', 'Bradley Hand', casual, sans-serif"

# One colour per kind of thing: (outline, hachure, wash). Excalidraw's palette.
KINDS = {
    'cmos': ('#1971c2', '#74c0fc', '#a5d8ff'),   # CMOS logic, single-ended 0 / 0.7 V
    'cml':  ('#e8590c', '#ffa94d', '#ffd8a8'),   # CML, differential
    'ana':  ('#2f9e44', '#69db7c', '#b2f2bb'),   # analog
    'clk':  ('#6741d9', '#b197fc', '#d0bfff'),   # clock generation
    'ext':  ('#868e96', '#ced4da', '#e9ecef'),   # not on the chip, or ideal glue
}
# Two-kind boxes: (first half, second half, split left|right or top|bottom).
MIXED = {'mix': ('cmos', 'cml', 'lr'), 'mixr': ('cml', 'cmos', 'lr'),
         'url(#cmos2cml_down)': ('cmos', 'cml', 'tb'), 'url(#cml2cmos_down)': ('cml', 'cmos', 'tb')}
# Connector classes in a source -> classes in the output.
WIRES = {'w': 'wire e-ink', 'wd': 'wire thick e-ink', 'wc': 'wire e-clk', 'wb': 'wire e-bias dash', 'ph': 'wire e-ph dashph'}
SOURCE_FILL = {'#1f2328': 'ink', '#7e22ce': 'clk', '#1d4ed8': 'cmos', '#c2410c': 'cml'}

STYLE = """  <style>
    text    { fill: #1e1e1e; }
    .title  { font-size: 22px; }
    .name   { font-size: 14px; }
    .note   { fill: #495057; }
    .ck     { fill: #6741d9; }
    .warn   { fill: #c92a2a; }
    .mid    { text-anchor: middle; }
    .end    { text-anchor: end; }

    .wash   { stroke: none; fill-opacity: 0.3; }
    .hach   { fill: none; stroke-width: 1.3; stroke-linecap: round; stroke-opacity: 0.75; }
    .edge   { fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
    .wire   { fill: none; stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; }
    .thick  { stroke-width: 2.8; }
    .light  { stroke-width: 1.3; }
    .rail   { fill: none; stroke-width: 5; stroke-linecap: round; stroke-opacity: 0.75; }
    .dash   { stroke-dasharray: 6 5; }
    .dashph { stroke-width: 2.2; stroke-dasharray: 7 6; }
    .again  { stroke-opacity: 0.55; }   /* the second pass of a pen stroke */
    .dot    { stroke: none; }
    .solid  { stroke: none; fill-opacity: 0.75; }

    .e-cmos { stroke: #1971c2; }  .h-cmos { stroke: #74c0fc; }  .f-cmos { fill: #a5d8ff; }  /* CMOS logic */
    .e-cml  { stroke: #e8590c; }  .h-cml  { stroke: #ffa94d; }  .f-cml  { fill: #ffd8a8; }  /* CML */
    .e-ana  { stroke: #2f9e44; }  .h-ana  { stroke: #69db7c; }  .f-ana  { fill: #b2f2bb; }  /* analog */
    .e-clk  { stroke: #6741d9; }  .h-clk  { stroke: #b197fc; }  .f-clk  { fill: #d0bfff; }  /* clocking */
    .e-ext  { stroke: #868e96; }  .h-ext  { stroke: #ced4da; }  .f-ext  { fill: #e9ecef; }  /* off chip, ideal glue */
    .e-ink  { stroke: #1e1e1e; }  .e-bias { stroke: #2f9e44; }  .e-ph   { stroke: #e03131; }
    .e-box  { stroke: #868e96; }  .e-chip { stroke: #343a40; stroke-width: 2.4; }
    .e-mix  { stroke: #495057; }  .e-tag  { stroke: #adb5bd; }  .e-pick { stroke: #d9480f; }
    .f-ink  { fill: #1e1e1e; }    .f-dotc { fill: #6741d9; }    .f-tag  { fill: #e9ecef; }
    .f-p0   { fill: #ced4da; }    .f-pick { fill: #fd7e14; }

    .lane   { fill: none; stroke-width: 20; }
    .lc     { stroke: #a5d8ff; }  /* CMOS lanes */
    .ll     { stroke: #ffd8a8; }  /* CML lanes */
    .amp    { fill: #2f9e44; fill-opacity: 0.85; }  /* a current, drawn to scale */
  </style>"""


# ---------------------------------------------------------------------------
# Pen strokes
# ---------------------------------------------------------------------------

def fmt(p):
    return f'{p[0]:.1f},{p[1]:.1f}'


def drift(p, e, rng, amp):
    """Curve commands from the current point p to e: a line that wanders a little off straight."""
    length = math.hypot(e[0] - p[0], e[1] - p[1])
    if length < 6:
        return ' L' + fmt(e)
    ux, uy = (e[0] - p[0]) / length, (e[1] - p[1]) / length
    n = max(1, round(length / 80))                # one bend per 80 units or so
    a = min(amp, 0.5 + length / 70)               # short strokes stay nearly straight
    bends = []
    for i in range(n):
        t = (i + 0.5 + rng.uniform(-0.15, 0.15)) / n
        off = rng.uniform(-1, 1) * a
        bends.append((p[0] + ux * length * t - uy * off, p[1] + uy * length * t + ux * off))
    out = ''
    for i, c in enumerate(bends):
        end = e if i == n - 1 else ((c[0] + bends[i + 1][0]) / 2, (c[1] + bends[i + 1][1]) / 2)
        out += f' Q{fmt(c)} {fmt(end)}'
    return out


def stroke(p, e, rng, amp):
    """One pen stroke from p to e. The ends land within half a unit of where they should."""
    j = lambda: rng.uniform(-0.5, 0.5) * min(1.0, amp)
    a = (p[0] + j(), p[1] + j())
    b = (e[0] + j(), e[1] + j())
    return 'M' + fmt(a) + drift(a, b, rng, amp)


def outline(x, y, w, h, r, rng, amp):
    """A rounded box in one pen stroke. It runs a little past its start instead of closing."""
    r = max(0.01, min(r, w / 2, h / 2))
    amp *= min(1.0, min(w, h) / 36)               # small boxes get a steadier hand
    j = lambda s: rng.uniform(-1, 1) * amp * s
    starts = [(x + r, y), (x + w, y + r), (x + w - r, y + h), (x, y + h - r)]
    ends = [(x + w - r, y), (x + w, y + h - r), (x + r, y + h), (x, y + r)]
    corners = [(x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    p = (starts[0][0] + j(0.4), starts[0][1] + j(0.4))
    d = 'M' + fmt(p)
    for k in range(4):
        e = (ends[k][0] + j(0.4), ends[k][1] + j(0.4))
        d += drift(p, e, rng, amp)
        c = (corners[k][0] + j(0.5), corners[k][1] + j(0.5))
        if k < 3:
            p = (starts[k + 1][0] + j(0.4), starts[k + 1][1] + j(0.4))
        else:
            p = (starts[0][0] + rng.uniform(1, 4) * min(1.0, w / 60), starts[0][1] + j(0.5))
        d += f' Q{fmt(c)} {fmt(p)}'
    return d


def hachure(x, y, w, h, rng):
    """Loose diagonal strokes filling a box, clipped to it."""
    gap = 7.0 if min(w, h) >= 20 else 4.5
    inset = min(2.0, w / 8, h / 8)
    x0, y0, x1, y1 = x + inset, y + inset, x + w - inset, y + h - inset
    angle = math.radians(-41)
    dx, dy = math.cos(angle), math.sin(angle)
    nx, ny = -dy, dx
    span = [nx * cx + ny * cy for cx in (x0, x1) for cy in (y0, y1)]
    c, out = min(span) + gap * rng.uniform(0.3, 0.8), []
    while c < max(span):
        px, py = nx * c, ny * c                   # a point on the stroke's line; then clip it to the box
        lo, hi = -1e9, 1e9
        for origin, step, low, high in ((px, dx, x0, x1), (py, dy, y0, y1)):
            ta, tb = (low - origin) / step, (high - origin) / step
            lo, hi = max(lo, min(ta, tb)), min(hi, max(ta, tb))
        if hi - lo > 2:
            j = lambda: rng.uniform(-0.6, 0.6)
            out.append(f'M{fmt((px + dx * lo + j(), py + dy * lo + j()))} L{fmt((px + dx * hi + j(), py + dy * hi + j()))}')
        c += gap * rng.uniform(0.82, 1.18)
    return ' '.join(out)


def half(x, y, w, h, r, which):
    """Outline of one half of a rounded box, for the wash of a two-kind box."""
    r = min(r, w / 2, h / 2)
    if which == 'left':
        return f'M{x + r},{y} H{x + w / 2} V{y + h} H{x + r} Q{x},{y + h} {x},{y + h - r} V{y + r} Q{x},{y} {x + r},{y} Z'
    if which == 'right':
        return f'M{x + w / 2},{y} H{x + w - r} Q{x + w},{y} {x + w},{y + r} V{y + h - r} Q{x + w},{y + h} {x + w - r},{y + h} H{x + w / 2} Z'
    if which == 'top':
        return f'M{x},{y + h / 2} V{y + r} Q{x},{y} {x + r},{y} H{x + w - r} Q{x + w},{y} {x + w},{y + r} V{y + h / 2} Z'
    return f'M{x},{y + h / 2} V{y + h - r} Q{x},{y + h} {x + r},{y + h} H{x + w - r} Q{x + w},{y + h} {x + w},{y + h - r} V{y + h / 2} Z'


def arrowhead(tip, back, size, rng):
    """An open V at `tip`, for a stroke that arrives from `back`."""
    length = math.hypot(tip[0] - back[0], tip[1] - back[1]) or 1
    ux, uy = (tip[0] - back[0]) / length, (tip[1] - back[1]) / length
    size = min(size, max(6.0, length * 0.45))     # a short stub gets a smaller head
    j = lambda: rng.uniform(-0.5, 0.5)
    bx, by = tip[0] - ux * size, tip[1] - uy * size
    spread = size * 0.46
    a = (bx - uy * spread + j(), by + ux * spread + j())
    b = (bx + uy * spread + j(), by - ux * spread + j())
    return f'M{fmt(a)} L{fmt(tip)} L{fmt(b)}'


# ---------------------------------------------------------------------------
# Source elements -> sketched elements
# ---------------------------------------------------------------------------

def tag(el):
    return el.tag.replace(NS, '') if isinstance(el.tag, str) else None


def num(el, name, default=0.0):
    return float(el.attrib.get(name, default))


def sketch_rect(el, classes, rng):
    x, y, w, h, r = num(el, 'x'), num(el, 'y'), num(el, 'width'), num(el, 'height'), num(el, 'rx')
    out = []
    fill = el.attrib.get('fill', '')
    box = f'x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"' + (f' rx="{r:g}"' if r else '')

    if not classes and fill in SOURCE_FILL:        # a plain coloured bar: one thick stroke down its middle
        vertical = h >= w
        a, b = ((x + w / 2, y), (x + w / 2, y + h)) if vertical else ((x, y + h / 2), (x + w, y + h / 2))
        return [f'<path class="rail e-{SOURCE_FILL[fill]}" d="{stroke(a, b, rng, 1.2)}"/>']

    mixed = next((MIXED[k] for k in list(classes) + [fill] if k in MIXED), None)
    kind = next((k for k in KINDS if k in classes), None)
    edge = None
    if mixed:
        first, second, split = mixed
        sides = ('left', 'right') if split == 'lr' else ('top', 'bottom')
        halves = ((x, y, w / 2, h), (x + w / 2, y, w / 2, h)) if split == 'lr' else ((x, y, w, h / 2), (x, y + h / 2, w, h / 2))
        for k, side, part in zip((first, second), sides, halves):
            out.append(f'<path class="wash f-{k}" d="{half(x, y, w, h, r, side)}"/>')
            out.append(f'<path class="hach h-{k}" d="{hachure(*part, rng)}"/>')
        edge = 'e-mix'
    elif kind:
        out.append(f'<rect class="wash f-{kind}" {box}/>')
        out.append(f'<path class="hach h-{kind}" d="{hachure(x, y, w, h, rng)}"/>')
        edge = f'e-{kind}'
    elif 'pick' in classes:
        out.append(f'<rect class="solid f-pick" {box}/>')
        edge = 'e-pick'
    elif 'tag' in classes:
        out.append(f'<rect class="wash f-tag" {box}/>')
        edge = 'e-tag light'
    elif 'p0' in classes:
        out.append(f'<rect class="solid f-p0" {box}/>')
        edge = 'e-mix light'
    elif 'p1' in classes:
        edge = 'e-mix light'
    elif fill == '#f6f8fa' or 'chip' in classes:
        edge = 'e-chip'
    elif 'box' in classes:
        edge = 'e-box'

    if 'ph' in classes:                            # a placeholder: one dashed red pass over whatever fill it has
        out.append(f'<path class="edge e-ph dashph" d="{outline(x, y, w, h, r, rng, 1.0)}"/>')
    elif edge:
        out.append(f'<path class="edge {edge}" d="{outline(x, y, w, h, r, rng, 1.5)}"/>')
        if min(w, h) >= 20:                        # and once more, as a pen going round twice
            out.append(f'<path class="edge {edge} again" d="{outline(x, y, w, h, r, rng, 2.4)}"/>')
    return out


def sketch_path(el, classes, rng):
    cls = next((WIRES[k] for k in WIRES if k in classes), None)
    if cls is None:                                # a hand-placed mark with its own stroke colour
        cls = 'wire e-ph' if el.attrib.get('stroke') == '#dc2626' else 'wire e-ink'
    # the source's straight pieces, as lists of points
    runs, x, y = [], 0.0, 0.0
    for cmd, a, b in re.findall(r'([MLHV])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?', el.attrib['d']):
        if cmd in 'ML':
            x, y = float(a), float(b)
        elif cmd == 'H':
            x = float(a)
        else:
            y = float(a)
        if cmd == 'M':
            runs.append([])
        runs[-1].append((x, y))
    dashed = 'dash' in cls
    first, second = [], []
    for run in runs:
        for p, e in zip(run, run[1:]):
            first.append(stroke(p, e, rng, 1.4))
            if not dashed and math.hypot(e[0] - p[0], e[1] - p[1]) >= 40:   # long strokes are drawn twice
                second.append(stroke(p, e, rng, 2.1))
    out = [f'<path class="{cls}" d="{" ".join(first)}"/>']
    if second:
        out.append(f'<path class="{cls} again" d="{" ".join(second)}"/>')
    if 'marker-end' in el.attrib:
        size = 11.0 if 'wd' in classes else 9.0
        head = cls.replace(' dashph', '').replace(' dash', '')
        out.append(f'<path class="{head}" d="{arrowhead(runs[-1][-1], runs[-1][-2], size, rng)}"/>')
    return out


def esc(s, attr=False):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return s.replace('"', '&quot;') if attr else s


def inline(el):
    """An element with its children on one line: text with its tspans."""
    attrs = ''.join(f' {k}="{esc(v, True)}"' for k, v in el.attrib.items() if k not in ('font-size', 'font-weight'))
    if len(el) == 0 and not (el.text or '').strip():
        return f'<{tag(el)}{attrs}/>'
    body = esc(el.text or '') + ''.join(inline(c) + esc(c.tail or '') for c in el)
    return f'<{tag(el)}{attrs}>{body}</{tag(el)}>'


def layer_of(el, classes):
    """'labels' for text, 'exact' for marks that carry a quantity, 'ink' for everything drawn."""
    if tag(el) == 'text':
        return 'labels'
    return 'exact' if classes & {'lane', 'amp'} else 'ink'


def convert(el, layer, inherited, rng, indent):
    """Lines of output for one source element in one layer (a group gives each layer its part)."""
    pad = ' ' * indent
    classes = set(el.attrib.get('class', '').split()) | inherited
    if tag(el) == 'g':
        inner = []
        for child in el:
            if isinstance(child.tag, str):
                inner += convert(child, layer, classes if layer == 'ink' else set(), rng, indent + 2)
        if not inner:
            return []
        keep = {k: v for k, v in el.attrib.items()
                if k == 'transform' or (layer == 'labels' and k in ('class', 'text-anchor') and v not in KINDS and v != 'pick')}
        if not keep:                               # nothing the children need: no wrapper
            return [line[2:] for line in inner]
        attrs = ''.join(f' {k}="{esc(v, True)}"' for k, v in keep.items())
        return [f'{pad}<g{attrs}>'] + inner + [f'{pad}</g>']
    if layer_of(el, classes) != layer:
        return []
    if layer == 'labels':
        return [pad + inline(el)]
    if layer == 'exact':
        return [pad + inline(el)]
    if tag(el) == 'rect':
        return [pad + line for line in sketch_rect(el, classes, rng)]
    if tag(el) == 'path':
        return [pad + line for line in sketch_path(el, classes, rng)]
    if tag(el) == 'circle':
        fill = 'f-dotc' if el.attrib.get('fill') == '#7e22ce' else 'f-ink'
        return [f'{pad}<circle class="dot {fill}" cx="{el.attrib["cx"]}" cy="{el.attrib["cy"]}" r="{el.attrib["r"]}"/>']
    raise SystemExit(f'sketch.py: cannot draw <{tag(el)}> (see the list of supported elements at the top of this file)')


def sketch(name):
    src = os.path.join(SRC, name + '.svg')
    root = ET.parse(src, ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))).getroot()
    height = root.attrib['height']
    title, desc = root.find(NS + 'title'), root.find(NS + 'desc')

    layers = {'ink': [], 'exact': [], 'labels': []}
    pending = dict.fromkeys(layers)
    seen_panel = False
    for index, el in enumerate(root):
        if el.tag is ET.Comment:
            if seen_panel:                         # a section comment: repeat it in each layer that has something under it
                pending = dict.fromkeys(layers, el.text)
            continue
        if tag(el) in ('title', 'desc', 'style', 'defs'):
            continue
        if not seen_panel:                         # the first rect is the background panel
            seen_panel = True
            continue
        for layer, lines in layers.items():
            rng = random.Random(zlib.crc32(f'{name}:{index}'.encode()))   # the same wobble on every run
            new = convert(el, layer, set(), rng, 4)
            if new:
                if pending[layer] is not None:
                    lines += ['', f'    <!--{pending[layer]}-->']
                    pending[layer] = None
                lines += new

    def group(cls, comment, lines):
        return ['', f'  <!-- ===== {comment} ===== -->', f'  <g class="{cls}">', '\n'.join(lines).lstrip('\n'), '  </g>'] if lines else []

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {height}" width="1000" height="{height}" role="img" aria-labelledby="t d"',
        f'     font-family="{FONT}" font-size="12.5">',
        '  ' + inline(title),
        '  ' + inline(desc),
        '',
        f'  <!-- Generated by docs/diagrams/sketch.py from docs/diagrams/src/{name}.svg. Do not edit this file:',
        '       edit the source, where every box and connector is straight and on its grid, and run the',
        '       script again. It draws the outlines and connectors as slightly wobbly pen strokes, fills',
        '       the boxes with hachure and leaves the text alone. No filter, marker, pattern, gradient',
        '       or font is loaded or referenced, so every renderer shows the same picture. Colours are',
        '       fixed and the white panel keeps the drawing readable on a dark page. -->',
        STYLE,
        '',
        f'  <rect x="0.5" y="0.5" width="999" height="{int(height) - 1}" rx="8" fill="#ffffff" stroke="#ced4da"/>',
        *group('ink', 'ink: boxes and connectors, as pen strokes', layers['ink']),
        *group('exact', 'exact: marks that carry a quantity, drawn true to size', layers['exact']),
        *group('labels', 'labels: all text', layers['labels']),
        '</svg>',
        '',
    ]
    text = '\n'.join(out)
    ET.fromstring(text)                            # the output must be well-formed
    assert 'url(' not in text and 'href' not in text, 'the output must not reference anything'
    with open(os.path.join(OUT, name + '.svg'), 'w') as f:
        f.write(text)
    print(f'{name}.svg: {text.count("<path")} strokes, {text.count("<text")} labels, {len(text) // 1024} KB')


if __name__ == '__main__':
    for n in sys.argv[1:] or NAMES:
        sketch(n)

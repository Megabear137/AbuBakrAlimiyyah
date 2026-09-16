#!/usr/bin/env python3
"""The shelf wall at 1920px, where the full-bleed wood shows ~370px of bare
margin either side of the bays - and three ways to fill it:

    Margins now        the wall as the site draws it today
    Cabinet (2)        a tall manuscript cabinet in each margin
    Calligraphy (4)    a gilt calligraphy panel in each margin
    Overflow (6)       the planks run out onto the wall as ledges of loose books

Unlike the older generators this one reads the live site: the tokens and the
shelf/spine CSS come from assets/css/styles.css and the books from
content/curriculum.json, so the bays match the real page exactly.

    python3 generate_margins.py [outdir] [--preview]
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = next((a for a in sys.argv[1:] if not a.startswith("--")), HERE)
PREVIEW = "--preview" in sys.argv

# ---------------------------------------------------------------- the site
CSS = open(os.path.join(ROOT, "assets/css/styles.css")).read()

def section(n):
    """The text of numbered section n of styles.css, up to the next one."""
    m = re.search(r"/\* -+ %d\. .*?\*/(.*?)(?=/\* -+ \d+\. )" % n, CSS, re.S)
    return m.group(1)

SITE_CSS = section(1) + section(3) + section(7) + section(8)
CURRICULUM = json.load(open(os.path.join(ROOT, "content/curriculum.json")))

# mirrored from assets/js/curriculum.js
BINDINGS = [("#4a1813", "#1a1210"), ("#2c1d13", "#5a1916"), ("#1c2a22", "#4a1813"),
            ("#5e3b1f", "#1c2a22"), ("#16120f", "#5a1916"), ("#3b2416", "#16120f")]
WIDTHS = [48, 54, 48, 52, 46, 50, 46, 52]
HEIGHTS = [254, 268, 262, 256, 240, 250, 236, 260]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]

esc = html.escape
ROW = 370 + 16          # a bay (10 + 300 well + 14 plank + 46 year) and the gap under it

def spine_vars(i):
    c, lab = BINDINGS[i % len(BINDINGS)]
    return f"--w:{WIDTHS[i % 8]}px;--h:{HEIGHTS[i % 8]}px;--c:{c};--lab:{lab};"

def spine(book, i):
    if re.match(r"\s*TODO", book["title"], re.I):
        return f'<div class="spine spine--todo" style="{spine_vars(i)}"><span class="spine__title">TODO</span></div>'
    subj = f'<span class="spine__subject gilt-text">{esc(book["subject"])}</span>' if book.get("subject") else ""
    return (f'<div class="spine" style="{spine_vars(i)}"><span class="spine__fin"></span>'
            f'<span class="spine__cart"><span class="spine__cart-in"><span class="spine__title gilt-text">{esc(book["title"])}</span></span></span>'
            f'<span class="spine__fin spine__fin--foot"></span>{subj}<span class="spine__medal"></span></div>')

def loose(i, cls="", title=""):
    """A spare book for the wall: the same binding, no title, never clickable."""
    t = f'<span class="spine__title gilt-text">{esc(title)}</span>' if title else ""
    return (f'<div class="spine spine--loose {cls}" style="{spine_vars(i)}"><span class="spine__fin"></span>'
            f'<span class="spine__cart"><span class="spine__cart-in">{t}</span></span>'
            f'<span class="spine__fin spine__fin--foot"></span><span class="spine__medal"></span></div>')

def case():
    years, rows = CURRICULUM["years"], []
    for i in range(0, len(years), 2):
        pair = years[i:i + 2]
        bays = "".join(
            f'<div class="bay"><div class="bay__well">{"".join(spine(b, k) for k, b in enumerate(y["books"]))}</div>'
            f'<div class="bay__plank"></div><p class="bay__year"><span class="bay__numeral">{ROMAN[i + j]}</span>{esc(y["name"])}</p></div>'
            for j, y in enumerate(pair))
        rows.append(f'<div class="shelf{" shelf--single" if len(pair) == 1 else ""}">{bays}</div>')
    return "".join(rows)

def wall(margins=""):
    c = CURRICULUM
    return ('<section class="shelf-wall"><div class="wrap">'
            f'<div class="shelf-wall__head"><div><p class="kicker kicker--on-wood">{esc(c["kicker"])}</p>'
            f'<h2 class="shelf-wall__title">{esc(c["label"])}</h2></div><p class="shelf-wall__intro">{esc(c["intro"])}</p></div>'
            f'<div class="case">{case()}{margins}</div></div></section>')

# ----------------------------------------------------------- illustration
GILT = "#c9a457"
DEFS = ('<defs><linearGradient id="shade" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#ffebc8" stop-opacity=".16"/><stop offset=".45" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient>'
        '<linearGradient id="giltg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f0d69a"/>'
        '<stop offset=".55" stop-color="#c79d4c"/><stop offset="1" stop-color="#e6c687"/></linearGradient>'
        '<radialGradient id="scroll" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#fbf3dc"/>'
        '<stop offset="1" stop-color="#cdbb90"/></radialGradient></defs>')

def svg(body, w=210, h=300):
    return (f'<svg class="art" viewBox="0 0 {w} {h}" width="{w}" height="{h}" preserveAspectRatio="xMidYMax meet" '
            f'aria-hidden="true">{DEFS}{body}</svg>')

def flat_stack(books, cx, base):
    """Books lying flat, spine to the viewer. books: (width, thickness, binding, dx)."""
    out, y = [], base
    for w, t, b, dx in books:
        leather, lab = BINDINGS[b]
        x, y = cx - w / 2 + dx, y - t
        cw, mid = min(58, w * .42), y + t / 2
        l, r = cx + dx - cw / 2, cx + dx + cw / 2
        out.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{t}" rx="1.5" fill="{leather}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{t}" rx="1.5" fill="url(#shade)"/>'
            f'<path d="M{x+6} {y+3}V{y+t-3}M{x+9} {y+3}V{y+t-3}M{x+w-6} {y+3}V{y+t-3}M{x+w-9} {y+3}V{y+t-3}" stroke="{GILT}" stroke-width="1" opacity=".75"/>'
            f'<polygon points="{l},{mid} {l+7},{y+3} {r-7},{y+3} {r},{mid} {r-7},{y+t-3} {l+7},{y+t-3}" fill="{lab}" stroke="{GILT}" stroke-width="1.2"/>'
            f'<rect x="{x}" y="{y+t-1}" width="{w}" height="1" fill="#000" opacity=".45"/>')
    return "".join(out), y

def inkwell(x, base):
    return (f'<path d="M{x+40} {base-58}L{x+19} {base-4}" stroke="#b58a4a" stroke-width="3.2" stroke-linecap="round"/>'
            f'<path d="M{x+19} {base-4}l-2 4" stroke="#2a1a0c" stroke-width="2.4" stroke-linecap="round"/>'
            f'<path d="M{x} {base}c-2-12 0-22 7-26v-6h18v6c7 4 9 14 7 26z" fill="#10231a"/>'
            f'<path d="M{x+6} {base-4}c-1-9 1-16 5-19" stroke="#fff" stroke-opacity=".18" stroke-width="2" fill="none"/>'
            f'<rect x="{x+5}" y="{base-36}" width="22" height="6" rx="1.5" fill="url(#giltg)"/>'
            f'<path d="M{x+46} {base-50}L{x+30} {base-2}" stroke="#8a6a38" stroke-width="2.6" stroke-linecap="round"/>')

def pen_box(cx, base, w=96):
    x, y = cx - w / 2, base - 17
    return (f'<rect x="{x}" y="{y}" width="{w}" height="17" rx="8.5" fill="#5a1916"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="17" rx="8.5" fill="url(#shade)"/>'
            f'<rect x="{x+5}" y="{y+3.5}" width="{w-10}" height="10" rx="5" fill="none" stroke="{GILT}" stroke-width="1"/>'
            f'<circle cx="{cx}" cy="{y+8.5}" r="2.6" fill="url(#giltg)"/>'
            f'<circle cx="{cx-20}" cy="{y+8.5}" r="1.4" fill="{GILT}"/><circle cx="{cx+20}" cy="{y+8.5}" r="1.4" fill="{GILT}"/>')

def rehal(cx, base):
    """A folding Qur'an stand, seen from the front, holding an open book."""
    top = base - 132
    return (f'<polygon points="{cx-52},{base} {cx-38},{base} {cx+62},{top} {cx+50},{top-4}" fill="#6b4f2c"/>'
            f'<polygon points="{cx+52},{base} {cx+38},{base} {cx-62},{top} {cx-50},{top-4}" fill="#5b4627"/>'
            f'<polygon points="{cx+52},{base} {cx+38},{base} {cx-62},{top} {cx-50},{top-4}" fill="url(#shade)"/>'
            f'<polygon points="{cx-7},{base-70} {cx+7},{base-70} {cx+5},{base-58} {cx-5},{base-58}" fill="#3a2c16"/>'
            f'<circle cx="{cx}" cy="{base-64}" r="3" fill="url(#giltg)"/>'
            # the open book: covers, then page blocks fanned in the V
            f'<path d="M{cx} {top+22}L{cx-74} {top-16}L{cx-72} {top-24}L{cx} {top+12}L{cx+72} {top-24}L{cx+74} {top-16}Z" fill="#4a1813"/>'
            f'<path d="M{cx} {top+14}L{cx-70} {top-22}Q{cx-40} {top-40} {cx-2} {top-18}Z" fill="#efe6cf"/>'
            f'<path d="M{cx} {top+14}L{cx+70} {top-22}Q{cx+40} {top-40} {cx+2} {top-18}Z" fill="#e6dbbf"/>'
            f'<path d="M{cx-58} {top-22}Q{cx-36} {top-34} {cx-8} {top-16}M{cx-50} {top-16}Q{cx-32} {top-26} {cx-10} {top-10}" stroke="#9a7a2e" stroke-width=".9" fill="none" opacity=".6"/>'
            f'<path d="M{cx+58} {top-22}Q{cx+36} {top-34} {cx+8} {top-16}M{cx+50} {top-16}Q{cx+32} {top-26} {cx+10} {top-10}" stroke="#9a7a2e" stroke-width=".9" fill="none" opacity=".6"/>'
            f'<path d="M{cx} {top+14}V{top-18}" stroke="#b9a27a" stroke-width="1"/>'
            f'<path d="M{cx+2} {top+14}v26" stroke="#8a2a20" stroke-width="2"/>')

def scroll_rack(base, cols=3, rows=4, fill=None):
    """Pigeonholes of rolled manuscripts, seen end-on."""
    cell, bar, out = 58, 7, []
    w = cols * cell + (cols + 1) * bar
    h = rows * cell + (rows + 1) * bar
    x0, y0 = (210 - w) / 2, base - h
    out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#45351e"/>'
               f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#shade)" opacity=".5"/>')
    layouts = fill or [[(0, 0, 13)], [(-11, 6, 10), (11, 6, 10), (0, -12, 10)], [(-8, 0, 11), (10, 3, 9)],
                       [(0, 2, 12), (-14, -12, 7)], [(-11, 6, 10), (11, 6, 10)], [(0, 0, 13)],
                       [(-10, 5, 10), (10, 5, 10), (0, -12, 10)], [(-9, 2, 12), (13, 6, 8)], [(0, 3, 12)],
                       [(-11, 6, 10), (11, 6, 10), (0, -12, 9)], [(0, 0, 13)], [(-9, 3, 11), (11, 5, 9)]]
    for r in range(rows):
        for c in range(cols):
            cx0 = x0 + bar + c * (cell + bar)
            cy0 = y0 + bar + r * (cell + bar)
            out.append(f'<rect x="{cx0}" y="{cy0}" width="{cell}" height="{cell}" fill="#120d07"/>'
                       f'<rect x="{cx0}" y="{cy0}" width="{cell}" height="8" fill="#000" opacity=".35"/>')
            for k, (dx, dy, rad) in enumerate(layouts[(r * cols + c) % len(layouts)]):
                sx, sy = cx0 + cell / 2 + dx, cy0 + cell - rad - 4 - (0 if dy >= 0 else -dy - rad * .2)
                sy = cy0 + cell - rad - 3 if dy >= 0 else sy - rad * 1.7
                out.append(f'<circle cx="{sx}" cy="{sy}" r="{rad}" fill="url(#scroll)"/>'
                           f'<circle cx="{sx}" cy="{sy}" r="{rad*.62}" fill="none" stroke="#a8906a" stroke-width=".8"/>'
                           f'<circle cx="{sx}" cy="{sy}" r="{rad*.28}" fill="none" stroke="#a8906a" stroke-width=".8"/>')
                if (r + c + k) % 3 == 0:   # a silk tag on a few
                    out.append(f'<path d="M{sx+rad*.6} {sy+rad*.6}l3 9" stroke="#8a2a20" stroke-width="1.2"/>'
                               f'<rect x="{sx+rad*.6+1}" y="{sy+rad*.6+8}" width="6" height="8" fill="#8a2a20"/>')
    return "".join(out)

def rosette():
    return ('<svg width="22" height="22" viewBox="-11 -11 22 22" aria-hidden="true">'
            f'<rect x="-6" y="-6" width="12" height="12" fill="none" stroke="{GILT}" stroke-width="1.2"/>'
            f'<rect x="-6" y="-6" width="12" height="12" fill="none" stroke="{GILT}" stroke-width="1.2" transform="rotate(45)"/>'
            f'<circle r="2.2" fill="{GILT}"/></svg>')

# ---------------------------------------------------------------- options
FRAME_CSS = """
*,*::before,*::after{box-sizing:border-box;}
h1,h2,h3,h4,p{margin:0;}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--ui);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased;}
a{color:var(--gold-ink);} a:hover{color:var(--green);}
.stage{width:1920px;padding:64px 0;}
.shelf-wall{margin-top:0;}
.case{position:relative;}
.art{display:block;}
"""

def now():
    return wall()

CABINET_CSS = """
/* A tall cabinet in each margin, built from the bay's own parts: the same
   frame, green well and plank, one compartment per row of the shelf. */
.cab{position:absolute;top:0;bottom:0;width:230px;padding:10px 10px 0;border-radius:18px;
  display:flex;flex-direction:column;gap:26px;
  background:linear-gradient(180deg,var(--wood-hi),var(--wood) 50%,var(--wood-lo));
  box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 12px 24px -12px rgba(0,0,0,.6);}
.cab--l{right:calc(100% + 70px);} .cab--r{left:calc(100% + 70px);}
.cab__cell{flex:none;height:360px;display:flex;flex-direction:column;}
.cab__well{height:300px;display:flex;align-items:flex-end;justify-content:center;border-radius:10px 10px 0 0;overflow:hidden;
  background:radial-gradient(60% 70% at 50% 0%,rgba(255,222,150,.14),transparent 70%),linear-gradient(180deg,#0b2410,var(--green-deep));
  box-shadow:inset 0 10px 24px rgba(0,0,0,.6),inset 0 -2px 0 rgba(0,0,0,.4);}
.cab__plank{height:14px;margin-inline:-10px;background:linear-gradient(180deg,#7a5e36,var(--wood-hi) 40%,#3a2c16);box-shadow:inset 0 1px 0 rgba(255,255,255,.18);}
.cab__foot{height:46px;display:flex;align-items:center;justify-content:center;opacity:.8;}
"""

def cabinet():
    s1, top1 = flat_stack([(150, 24, 0, 0), (136, 20, 3, -6), (142, 26, 1, 4), (118, 18, 4, -2), (126, 22, 5, 6)], 105, 300)
    s2, top2 = flat_stack([(160, 26, 2, 0), (140, 22, 0, 5), (128, 20, 3, -4)], 105, 300)
    s3, top3 = flat_stack([(146, 22, 5, 0), (150, 26, 1, -4), (130, 18, 3, 6), (138, 24, 0, -2)], 105, 300)
    s4, top4 = flat_stack([(154, 24, 4, 0), (132, 22, 2, -5)], 105, 300)
    left = [svg(s1 + inkwell(112, top1)), svg(rehal(105, 300)), svg(scroll_rack(300)), svg(s2 + pen_box(102, top2))]
    right = [svg(scroll_rack(300, fill=[[(-11, 6, 10), (11, 6, 10)], [(0, 0, 13)], [(-10, 5, 10), (10, 5, 10), (0, -12, 10)],
                                      [(0, 2, 12)], [(-9, 3, 11), (11, 5, 9)], [(-11, 6, 10), (11, 6, 10), (0, -12, 9)]])),
             svg(s3 + pen_box(108, top3, 84)), svg(rehal(105, 300)), svg(s4 + inkwell(70, top4))]
    def cab(side, cells):
        body = "".join(f'<div class="cab__cell"><div class="cab__well">{c}</div><div class="cab__plank"></div>'
                       f'<div class="cab__foot">{rosette()}</div></div>' for c in cells)
        return f'<div class="cab cab--{side}" aria-hidden="true">{body}</div>'
    return wall(cab("l", left) + cab("r", right))

CALLIG_CSS = """
/* A gilt calligraphy panel in each margin, drawn as one very tall kitab
   spine: the bay's frame and green well, a double gilt rule, the phrase in a
   pointed cartouche between finials, then a medallion and the translation. */
.cal{position:absolute;top:0;bottom:0;width:156px;padding:10px;border-radius:18px;
  background:linear-gradient(180deg,var(--wood-hi),var(--wood) 50%,var(--wood-lo));
  box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 12px 24px -12px rgba(0,0,0,.6);}
.cal--l{right:calc(100% + 107px);} .cal--r{left:calc(100% + 107px);}
.cal__well{position:relative;height:100%;border-radius:10px;display:flex;flex-direction:column;align-items:center;gap:10px;padding:34px 0 30px;
  background:radial-gradient(70% 40% at 50% 0%,rgba(255,222,150,.14),transparent 70%),linear-gradient(180deg,#0b2410,var(--green-deep) 60%,#0b2410);
  box-shadow:inset 0 10px 24px rgba(0,0,0,.6),inset 0 -10px 24px rgba(0,0,0,.45);}
.cal__well::after{content:"";position:absolute;inset:12px;border:1px solid var(--gilt);opacity:.6;border-radius:4px;
  box-shadow:inset 0 0 0 3px transparent,inset 0 0 0 4px rgba(201,164,87,.45);pointer-events:none;}
.cal .spine__fin{transform:scale(1.6);margin:8px 0;}
.cal .spine__fin--foot{transform:scale(1.6) scaleY(-1);}
.cal__cart{--cart:polygon(50% 0,100% 5%,100% 95%,50% 100%,0 95%,0 5%);position:relative;flex:1 1 auto;width:92px;background:var(--gilt);clip-path:var(--cart);}
.cal__cart-in{position:absolute;inset:2px;display:flex;align-items:center;justify-content:center;clip-path:var(--cart);
  background:linear-gradient(90deg,rgba(0,0,0,.35),rgba(255,235,200,.05) 45%,rgba(0,0,0,.3)),#3a120e;}
.cal__cart-in::before{content:"";position:absolute;inset:5px;border:1px solid var(--gilt);opacity:.5;clip-path:var(--cart);}
.cal__ar{writing-mode:vertical-rl;text-orientation:sideways;font-family:"Amiri",serif;font-weight:700;font-size:var(--fs);line-height:1;white-space:nowrap;padding-top:.1em;}
.cal .spine__medal{transform:scale(1.5);margin:10px 0 6px;}
.cal__en{width:112px;text-align:center;color:rgba(244,239,226,.7);font-family:var(--display);font-style:italic;font-size:17px;line-height:1.25;text-wrap:balance;}
.cal__ref{color:var(--gold);font-size:10.5px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;text-align:center;}
"""

def calligraphy():
    def panel(side, ar, en, ref, fs):
        return (f'<div class="cal cal--{side}" style="--fs:{fs}px"><div class="cal__well"><span class="spine__fin"></span>'
                f'<div class="cal__cart"><div class="cal__cart-in"><span class="cal__ar gilt-text" lang="ar" dir="rtl">{ar}</span></div></div>'
                f'<span class="spine__fin spine__fin--foot"></span><span class="spine__medal"></span>'
                f'<p class="cal__en">{en}</p><p class="cal__ref">{ref}</p></div></div>')
    return wall(panel("l", "رَبِّ زِدْنِي عِلْمًا", "“My Lord, increase me in knowledge.”", "Ṭā Hā · 20:114", 84)
                + panel("r", "طَلَبُ الْعِلْمِ فَرِيضَةٌ عَلَى كُلِّ مُسْلِمٍ", "“Seeking knowledge is an obligation upon every Muslim.”", "Ibn Mājah · 224", 60))

OVERFLOW_CSS = """
/* Some planks run on past the bay and out onto the wall as a bracketed ledge,
   holding a few spare books. The ledges alternate sides row by row, and the
   books are dimmed and inert so they never read as part of the curriculum. */
.ledge{position:absolute;width:268px;height:14px;
  background:linear-gradient(180deg,#7a5e36,var(--wood-hi) 40%,#3a2c16);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.18),0 14px 20px -10px rgba(0,0,0,.7);}
.ledge--l{right:100%;border-radius:3px 0 0 3px;} .ledge--r{left:100%;border-radius:0 3px 3px 0;}
.ledge__bracket{position:absolute;top:14px;width:22px;height:54px;}
.ledge--l .ledge__bracket{left:34px;} .ledge--r .ledge__bracket{right:34px;transform:scaleX(-1);}
.ledge__items{position:absolute;bottom:14px;height:300px;width:248px;display:flex;align-items:flex-end;gap:3px;}
.ledge--l .ledge__items{right:6px;justify-content:flex-end;} .ledge--r .ledge__items{left:6px;justify-content:flex-start;}
.spine--loose{filter:brightness(.8) saturate(.85);pointer-events:none;}
.lean-r{transform-origin:0 100%;transform:rotate(9deg);margin-right:38px;}
.lean-l{transform-origin:100% 100%;transform:rotate(-9deg);margin-left:38px;}
.ledge .art{filter:brightness(.85) saturate(.9);}
"""

BRACKET = ('<svg class="ledge__bracket" viewBox="0 0 22 54" aria-hidden="true">'
           '<path d="M0 0h22v8C22 30 12 44 3 54H0z" fill="#45351e"/>'
           '<path d="M0 0h22v8C22 30 12 44 3 54H0z" fill="url(#shade)"/>'
           '<path d="M16 6C16 26 9 38 2 48" stroke="#c9a457" stroke-width="1" fill="none" opacity=".45"/>'
           '<circle cx="11" cy="5" r="3" fill="url(#giltg)"/></svg>')

def overflow():
    def ledge(side, row, items):
        return (f'<div class="ledge ledge--{side}" style="top:{row * ROW + 310}px">{BRACKET}'
                f'<div class="ledge__items">{items}</div></div>')
    s1, t1 = flat_stack([(132, 22, 2, 0), (118, 18, 0, 5), (126, 24, 4, -4)], 70, 300)
    s2, t2 = flat_stack([(140, 24, 5, 0), (124, 20, 3, -5), (132, 22, 1, 4), (112, 18, 0, 0)], 76, 300)
    rows = [
        ledge("l", 0, loose(1, cls="lean-r") + loose(3) + loose(0) + loose(5)),
        ledge("r", 1, loose(2) + svg(s2 + inkwell(58, t2), 150, 300)),
        ledge("l", 2, svg(s1 + pen_box(70, t1, 80), 140, 300) + loose(4) + loose(1)),
        ledge("r", 3, loose(0) + loose(2, cls="lean-l")),
    ]
    return wall("".join(rows))

# ------------------------------------------------------------------ files
def doc(css, body):
    head = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600'
            '&family=Instrument+Sans:wght@400;500;600&family=Amiri:wght@400;700&display=swap">\n'
            '<style>' + SITE_CSS + FRAME_CSS + css + '</style>')
    body = f'<div class="stage">{body}</div>'
    if PREVIEW:
        return f'<!doctype html><html><head><meta charset="utf-8">{head}</head><body>{body}</body></html>\n'
    return ('<!doctype html>\n<html>\n<head>\n<meta charset="utf-8">\n<script src="./support.js"></script>\n</head>\n<body>\n<x-dc>\n'
            f'<helmet>\n{head}\n</helmet>\n{body}\n</x-dc>\n</body>\n</html>\n')

def main():
    files = {
        "MarginsNow.dc.html": doc("", now()),
        "MarginsCabinet.dc.html": doc(CABINET_CSS, cabinet()),
        "MarginsCalligraphy.dc.html": doc(CALLIG_CSS, calligraphy()),
        "MarginsOverflow.dc.html": doc(OVERFLOW_CSS, overflow()),
    }
    os.makedirs(OUT, exist_ok=True)
    for name, src in files.items():
        open(os.path.join(OUT, name.replace(".dc.html", ".html") if PREVIEW else name), "w").write(src)
    print("wrote", len(files), "to", OUT)

if __name__ == "__main__":
    main()

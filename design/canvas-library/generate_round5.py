#!/usr/bin/env python3
"""The bookstore, round 5: ten mockups made for the masjid's photographs.

Rounds 1-4 were drawn before there were pictures, around drawn bindings.
The books now have photographs (assets/img/books/), and they share a look:
studio shots of the real covers - saturated teals, greens, navies, browns,
gold-blocked frames - lying on a pale grey table, soft-lit, a small margin
of grey around each book. Every option here is built around that: either it
keeps the grey and makes it part of the design (a seamless card, a mat, a
light box), or it takes the colour out of the cover and lets the page wear
it. The ideas:

   1. Studio      - each card is the colour of its own photo's table, so the
                    grey runs on past the picture's edge and the book seems
                    to lie on the card itself. A lead card, a dark tile.
   2. Mounted prints - every photograph matted in cream behind a bevel, in a
                    thin walnut frame hung from a nail, the title and price
                    pencilled on the mat as a print's edition is.
   3. Face-out ledge - books standing face out on oak picture ledges, the
                    site's wood, each with a shelf-talker clipped to the lip.
   4. Price list  - a feature spread for the lead book, then the books as a
                    typeset list with dotted leaders; on the page, pointing at
                    a line floats its photograph beside the pointer.
   5. Lookbook    - big photographs in a run that scrolls sideways, captions
                    set like a magazine's. The page: a year at a time, its
                    first book large.
   6. Cover tint  - each tile washed in the colour taken from its own cover
                    (measured from the photograph), the book floating on it.
   7. Plinths     - a gallery display: the books on stone plinths of
                    stepped heights, the tallest in the middle, the label cut
                    into each plinth's face.
   8. Index cards - a library catalogue: ruled cards, typed, each with its
                    photograph paper-clipped on; the page is a drawer per year.
   9. Showroom    - one book large with everything about it, the others as
                    thumbnails beside it to choose from; on the page the
                    viewer stays put while the thumbnails scroll.
  10. Receipt     - a till receipt slips out from under each photograph with
                    the title, the years and the total: the receipt is what a
                    buyer brings to the masjid to collect the book.

The same file also writes the best options of the earlier rounds, redone
with the photographs, as their own set (best-*.html, "Best" in the
switcher): 1. Objects (round 2, option 2), 2. Bento (round 3, option 1) and
3. Accordion (round 3, option 9); and 4. Colour stage (round 6, option 2),
which generate_round6.py writes.

Content is the real content/bookstore.json: titles, editions, years,
prices, descriptions and photographs; books without one wear their drawn
binding (round 1's drawnCover). The page's lede is still TODO. The colours
of options 1 and 6 are measured from the photographs, which needs Pillow
(without it they fall back to a plain grey and the binding's colour).

No star patterns, no arches, no invented copy.

Edit this file, not the output:  python3 generate_round5.py
"""
import colorsys
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
_spec = importlib.util.spec_from_file_location("round3", HERE / "generate_round3.py")
r3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r3)
r1, esc, ARROW = r3.r1, r3.esc, r3.ARROW

DATA = json.loads((ROOT / "content" / "bookstore.json").read_text())
BOOKS = DATA["books"]
for i, b in enumerate(BOOKS):
    b["i"] = i
LEDE = DATA["lede"]
VISIT_LABEL = DATA["visitLabel"]
YEARS = ["First Year", "Second Year", "Third Year", "Fourth Year", "Fifth Year", "Sixth Year", "Seventh Year"]
ROMAN = dict(zip(YEARS, ["I", "II", "III", "IV", "V", "VI", "VII"]))
HOME = [b for b in BOOKS if b.get("featured")] + [b for b in BOOKS if not b.get("featured")]
HOME = HOME[:7]
# The best options' home sections show only books with a photograph, in the same order.
HOME_C = [b for b in BOOKS if b.get("featured") and b.get("cover")] + [b for b in BOOKS if not b.get("featured") and b.get("cover")]
HOME_C = HOME_C[:7]
COUNT = len(BOOKS)
PAGE = ' aria-current="page"'

# ---------------------------------------------------------------------------
# Pictures, and the two colours measured from each: its table, its cover.
# ---------------------------------------------------------------------------
TONES = {"lapis": "#1c3f7a", "ink": "#2e2c33", "petrol": "#0f5560", "oxblood": "#6e1a1f",
         "aubergine": "#4b2458", "slate": "#39434e"}


def binding(b):
    c = b.get("color") or "lapis"
    return c.replace("-silver", "") if c.replace("-silver", "") in r1.BINDINGS else "lapis"


def hexc(c):
    return "#%02x%02x%02x" % tuple(int(v) for v in c[:3])


# The cover's colours and the tight crops come from tools/covers.py, which
# makes the same for the site.
_cs = importlib.util.spec_from_file_location("covers", ROOT / "tools" / "covers.py")
covers = importlib.util.module_from_spec(_cs)
_cs.loader.exec_module(covers)
measure = covers.measure

for b in BOOKS:
    b["bg"], b["tint"] = "#dedbd5", TONES[binding(b)]
    if b.get("cover"):
        b["src"] = "../../" + b["cover"]
        try:
            b["bg"], b["tint"] = measure(ROOT / b["cover"])
        except Exception:
            pass
    else:
        b["src"] = r1.drawn_cover(b["title"], binding(b), b["i"])


# ---------------------------------------------------------------------------
# Tight crops: the book alone, without the table around it. The photographs
# are not framed alike (some books fill the frame, others sit off-centre with
# a margin of table and paper), so one zoom can't fit them all: each book's
# edges are found from the photograph - the outermost long straight edge on
# each side - and cut to crops/<name>.jpg, a little inside them. Where the
# finding is wrong, CROP_FIX in tools/covers.py gives the box by hand.
# ---------------------------------------------------------------------------
CROPS = HERE / "crops"
CROP_FIX, find_edges = covers.CROP_FIX, covers.find_edges


def tight(b):
    """crops/<name>.jpg and its height over width, made when missing or stale."""
    from PIL import Image
    src = ROOT / b["cover"]
    stem = src.stem
    out = CROPS / f"{stem}.jpg"
    x0, y0, x1, y1 = CROP_FIX.get(stem) or find_edges(src)
    pad = 0.022
    x0, y0, x1, y1 = x0 + pad, y0 + pad, x1 - pad, y1 - pad
    im = Image.open(src)
    W, H = im.size
    box = (round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H))
    if not out.exists() or out.stat().st_mtime < max(src.stat().st_mtime, Path(__file__).stat().st_mtime):
        CROPS.mkdir(exist_ok=True)
        im.convert("RGB").crop(box).save(out, quality=88, optimize=True)
    return f"crops/{stem}.jpg", (box[3] - box[1]) / (box[2] - box[0])


for b in BOOKS:
    if b.get("cover"):
        try:
            b["crop"], b["crop_ar"] = tight(b)
        except Exception:
            pass


def deep(c, top=0.36):
    """The colour, darkened until cream text reads on it."""
    r, g, b_ = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, sat = colorsys.rgb_to_hls(r, g, b_)
    if l > top:
        l, sat = top, min(1, sat * 1.25)
    return hexc([v * 255 for v in colorsys.hls_to_rgb(h, l, sat)])


def tsrc(b):
    """The tight crop where there is one (see crops/ below), else the picture."""
    return b.get("crop") or b["src"]


def pic(b, cls="", lazy=True, tight=False):
    """The book's picture; tight=True takes its tight crop, shown unzoomed."""
    cls = (cls + " is-drawn").strip() if not b.get("cover") else cls
    if tight and b.get("crop"):
        return f'<img class="{(cls + " is-crop").strip()}" src="{b["crop"]}" width="600" height="800" alt=""{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""}>'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{b["src"]}" width="600" height="800" alt=""{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""}>'


def yrs(b, sep=" · "):
    return sep.join(ROMAN.get(y, y) for y in b["years"])


def years_line(b):
    n = len(b["years"])
    return ("Years " if n > 1 else "Year ") + yrs(b, " & " if n == 2 else ", ")


def ed(b, cls):
    return f'<p class="{cls}">{esc(b["edition"])}</p>' if b.get("edition") else ""


def style(b, *keys):
    return "--bg:{};--t:{}".format(b["bg"], b["tint"])


def data_attrs(b):
    return (f'data-src="{esc(b["src"])}" data-title="{esc(b["title"])}" data-ed="{esc(b.get("edition") or "")}" '
            f'data-sub="{esc(b.get("subject") or "")}" data-years="{esc(years_line(b))}" data-price="{esc(b.get("price") or "")}" '
            f'data-desc="{esc(b.get("description") or "")}" style="{style(b)}"')


# ---------------------------------------------------------------------------
# The frame: round 3's page, header, footer and theme; a switcher for round 5.
# ---------------------------------------------------------------------------
OPTIONS = [
    ("r5-01-studio", "Studio"),
    ("r5-02-prints", "Mounted prints"),
    ("r5-03-ledge", "Face-out ledge"),
    ("r5-04-pricelist", "Price list"),
    ("r5-05-lookbook", "Lookbook"),
    ("r5-06-tint", "Cover tint"),
    ("r5-07-plinths", "Plinths"),
    ("r5-08-cards", "Index cards"),
    ("r5-09-showroom", "Showroom"),
    ("r5-10-receipt", "Receipt"),
]


def switcher(slug, is_page):
    sfx = "-page" if is_page else ""
    best = slug.startswith("best-")
    group = BEST if best else OPTIONS
    links = "".join(
        f'<a href="{s}{sfx}.html" title="{n}"{PAGE if s == slug else ""}>{i + 1}</a>'
        for i, (s, n) in enumerate(group))
    return f"""
<nav class="m-switch" aria-label="Mockups">
  <a href="1-shelf{sfx}.html">R1</a><a href="r2-1-window{sfx}.html">R2</a><a href="r3-01-bento{sfx}.html">R3</a><a href="r4-01-hashiya{sfx}.html">R4</a><a href="r5-01-studio{sfx}.html"{"" if best else PAGE}>R5</a><a href="best-1-objects{sfx}.html"{PAGE if best else ""}>Best</a><a href="r6-01-spines{sfx}.html">R6</a><i></i>{links}<i></i>
  <a href="{slug}.html"{"" if is_page else PAGE}>Home</a><a href="{slug}-page.html"{PAGE if is_page else ""}>Page</a><i></i>
  <button type="button" data-set-theme="light">Light</button>
  <button type="button" data-set-theme="dark">Dark</button>
</nav>"""


# The best options, taken out of the rounds and redone with the photographs:
# round 2's option 2, round 3's options 1 and 9. Their own set, best-*.html.
BEST = []


SHARED_CSS = """
.r5-sub { color: var(--g-accent); font: 600 0.6rem/1.3 var(--sans); letter-spacing: 0.24em; text-transform: uppercase; }
.r5-title { color: var(--g-text); font-family: var(--display); font-size: 1.3rem; font-weight: 600; line-height: 1.1; }
.r5-ed { color: var(--g-muted); font-family: var(--display); font-size: 1rem; font-style: italic; line-height: 1.2; }
.r5-price { font-family: var(--display); font-size: 1.3rem; font-weight: 700; font-variant-numeric: lining-nums tabular-nums; }
.r5-link { color: inherit; text-decoration: none; }
.r5-link::after { content: ""; position: absolute; inset: 0; z-index: 2; }
.r5-foot { margin-top: clamp(2rem, 4vw, 3rem); text-align: center; }
.r5-filter { display: flex; justify-content: center; margin: -0.5rem 0 clamp(2.4rem, 5vw, 3.6rem); }
.r5-filter .seg { flex-wrap: wrap; justify-content: center; }
.r5-filter .seg__btn { min-width: 3rem; }
[data-theme="dark"] .r5-filter .seg { border-color: var(--g-line); background: var(--g-card); box-shadow: none; }
[data-theme="dark"] .r5-filter .seg__btn { color: var(--g-muted); }
[data-theme="dark"] .r5-filter .seg__btn[aria-pressed="true"] { color: var(--espresso); }
.r5-group + .r5-group { margin-top: clamp(3.2rem, 6vw, 5rem); }
.r5-gh { display: flex; align-items: baseline; gap: 0.9rem; margin-bottom: clamp(1.4rem, 3vw, 2rem); padding-bottom: 0.8rem; border-bottom: 1px solid var(--g-line);
  color: var(--g-text); font-family: var(--title); font-size: clamp(1.35rem, 1rem + 1vw, 1.9rem); font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase; }
.r5-gh b { color: var(--g-accent); font-family: var(--display); font-weight: 600; letter-spacing: 0.04em; }
.r5-gh em { margin-left: auto; color: var(--g-muted); font-family: var(--display); font-size: 1.05rem; letter-spacing: 0; text-transform: none; }
img.is-drawn, img.is-crop { transform: none !important; }
.r3-page .section__head { margin-bottom: clamp(1.6rem, 3vw, 2.4rem); }
"""

FILTER_JS = """
<script>
  document.querySelectorAll(".r5-filter [data-year]").forEach(function (b) {
    b.addEventListener("click", function () {
      var y = b.dataset.year;
      document.querySelectorAll(".r5-filter [data-year]").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      document.querySelectorAll("[data-group]").forEach(function (g) { g.hidden = y !== "all" && g.dataset.group !== y; });
    });
  });
</script>"""


def page(fname, slug, name, blurb, css, main, js=""):
    r3.switcher = switcher
    is_page = fname.endswith("-page.html")
    out = r3.page(fname, slug, name, blurb, SHARED_CSS + css, main, (FILTER_JS if is_page else "") + js)
    return (out.replace("<!-- Round 3, option", "<!-- Best options, option" if slug.startswith("best-") else "<!-- Round 5, option")
               .replace("styles.css?v=60", "styles.css?v=76")
               .replace("family=Instrument+Sans", "family=Courier+Prime:wght@400;700&family=Instrument+Sans"))


def home(inner):
    return f"""
<main id="main" class="r3-home">
  <hr class="section-rule">
  <section class="section" id="bookstore" aria-labelledby="bookstore-heading">
    <div class="wrap">
      <div class="section__head"><h2 class="section__heading" id="bookstore-heading">Bookstore</h2></div>
{inner.rstrip()}
    </div>
  </section>
  <hr class="section-rule">
</main>"""


def filter_bar():
    btns = '<button class="seg__btn" type="button" data-year="all" aria-pressed="true">All</button>' + "".join(
        f'<button class="seg__btn" type="button" data-year="{y}" aria-pressed="false" title="{y}">{ROMAN[y]}</button>' for y in YEARS)
    return f'<div class="r5-filter"><div class="seg" role="group" aria-label="Year">{btns}</div></div>'


def page_main(body, before_filter=""):
    return f"""
<main id="main" class="r3-page">
  <div class="r3-wrap">
    <a class="r3-back" href="#">← Home</a>
    <div class="section__head"><h1 class="section__heading">Bookstore</h1><p class="section__lede">{esc(LEDE)}</p></div>
{before_filter}{filter_bar()}
{body.rstrip()}
  </div>
</main>"""


def groups(render, head=None):
    out = []
    for y in YEARS:
        bs = [b for b in BOOKS if y in b["years"]]
        h = head(y, bs) if head else f'<h2 class="r5-gh"><b>{ROMAN[y]}</b> {y} <em>{len(bs)} books</em></h2>'
        out.append(f'<section class="r5-group" data-group="{y}">{h}{render(bs)}</section>')
    return "\n".join(out)


def visit(cls="btn btn--gold"):
    return f'<a class="{cls}" href="#">{esc(VISIT_LABEL)} {ARROW}</a>'


BUILDS = []

# ============================================================================
# 1. Studio. Each card takes its photo's own table colour, measured from the
#    picture's corners, and the picture's edge fades into it - so the book
#    seems to lie on the card. The lead card is four cells and carries the
#    description; a board tile closes the grid.
# ============================================================================
CSS_1 = """
.st-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-auto-flow: dense; gap: 18px; }
.st-card { position: relative; display: flex; flex-direction: column; overflow: hidden; border-radius: 18px;
  background: radial-gradient(120% 80% at 50% 30%, color-mix(in srgb, var(--bg), #fff 12%), var(--bg) 60%, color-mix(in srgb, var(--bg), #000 6%));
  color: #2a1c10; box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6), 0 26px 40px -30px rgba(50, 28, 8, 0.55); transition: transform 0.45s var(--ease-out), box-shadow 0.45s; }
.st-card:hover { transform: translateY(-5px); box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6), 0 36px 50px -30px rgba(50, 28, 8, 0.7); }
.st-shot { padding: 7% 9% 0; }
.st-shot img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 4; object-fit: cover; transition: transform 0.6s var(--ease-out);
  -webkit-mask: linear-gradient(90deg, transparent, #000 6%, #000 94%, transparent), linear-gradient(transparent, #000 6%, #000 94%, transparent);
  -webkit-mask-composite: source-in; mask: linear-gradient(90deg, transparent, #000 6%, #000 94%, transparent), linear-gradient(transparent, #000 6%, #000 94%, transparent); mask-composite: intersect; }
.st-card:hover .st-shot img { transform: scale(1.025); }
.st-body { display: flex; flex: 1; flex-direction: column; gap: 0.2rem; padding: 0.9rem 1.2rem 1.15rem; }
.st-body .r5-sub { color: rgba(42, 28, 16, 0.62); }
.st-body .r5-title { color: #2a1c10; font-size: 1.2rem; }
.st-body .r5-ed { color: rgba(42, 28, 16, 0.7); font-size: 0.95rem; }
.st-desc { margin-top: 0.4rem; color: rgba(42, 28, 16, 0.78); font-size: 0.86rem; line-height: 1.6; }
.st-row { display: flex; align-items: center; justify-content: space-between; gap: 0.6rem; margin-top: auto; padding-top: 0.7rem; }
.st-yr { color: rgba(42, 28, 16, 0.6); font: 500 0.7rem var(--sans); letter-spacing: 0.08em; }
.st-row .r5-price { padding: 0.12rem 0.75rem 0.05rem; border-radius: 99px; background: rgba(255, 255, 255, 0.6); color: #2a1c10; font-size: 1.15rem; }
.st-lead { grid-column: span 2; grid-row: span 2; }
.st-lead .st-shot { padding: 5% 12% 0; }
.st-lead .r5-title { font-family: var(--title); font-size: clamp(1.6rem, 1.2rem + 1vw, 2.1rem); font-weight: 400; letter-spacing: 0.04em; }
.st-lead .st-body { padding: 1rem 1.8rem 1.6rem; }
.st-tile { grid-column: span 2; display: flex; flex-direction: column; justify-content: center; gap: 0.8rem; padding: 2rem 2.2rem; border-radius: 18px;
  background: linear-gradient(160deg, var(--board), var(--board-deep)); color: var(--gold-pale); box-shadow: inset 0 1px 0 rgba(227, 179, 74, 0.35), 0 26px 40px -30px rgba(50, 28, 8, 0.7); }
.st-tile p { font-family: var(--display); font-size: 1.25rem; font-style: italic; line-height: 1.3; }
.st-tile b { display: block; color: var(--gold); font-family: var(--title); font-size: 2.4rem; font-style: normal; font-weight: 400; letter-spacing: 0.08em; line-height: 1; }
.st-tile .btn { align-self: flex-start; }
[data-theme="dark"] .st-card { box-shadow: inset 0 0 0 1px rgba(227, 179, 74, 0.25), 0 30px 46px -30px rgba(0, 0, 0, 0.9); filter: brightness(0.93); }
[data-theme="dark"] .st-tile { background: var(--g-card); border: 1px solid var(--g-line); box-shadow: inset 0 1px 0 rgba(227, 179, 74, 0.4); }
.st-page { grid-template-columns: repeat(4, minmax(0, 1fr)); }
@media (max-width: 980px) { .st-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .st-lead { grid-row: auto; } }
@media (max-width: 480px) { .st-grid { gap: 12px; } .st-body { padding: 0.7rem 0.85rem 0.9rem; } .st-body .r5-title { font-size: 1.05rem; } .st-yr { display: none; } }
"""


def st_card(b, lead=False):
    desc = f'<p class="st-desc">{esc(b["description"])}</p>' if lead and b.get("description") else ""
    sub = f'<p class="r5-sub">{esc(b["subject"])}</p>' if b.get("subject") else ""
    price = f'<span class="r5-price">{esc(b["price"])}</span>' if b.get("price") else ""
    return (f'<article class="st-card{" st-lead" if lead else ""}" style="{style(b)}"><div class="st-shot">{pic(b, lazy=not lead)}</div>'
            f'<div class="st-body">{sub}<h3 class="r5-title"><a class="r5-link" href="#">{esc(b["title"])}</a></h3>{ed(b, "r5-ed")}{desc}'
            f'<div class="st-row"><span class="st-yr">{years_line(b)}</span>{price}</div></div></article>')


st_home = home(f"""
      <div class="st-grid">
        {st_card(HOME[0], True)}
        {"".join(st_card(b) for b in HOME[1:])}
        <div class="st-tile"><p><b>{COUNT}</b>books for all seven years</p>{visit()}</div>
      </div>""")
st_page = page_main(groups(lambda bs: f'<div class="st-grid st-page">{"".join(st_card(b) for b in bs)}</div>'))
BUILDS.append(("r5-01-studio", "Studio", "Cards in each photo's own table colour, so the book lies on the card.", CSS_1, st_home, st_page, ""))

# ============================================================================
# 2. Mounted prints. The photograph behind a bevelled cream mat in a thin
#    walnut frame, hung from a nail on two cords; title and price pencilled
#    on the mat. The lead print is larger.
# ============================================================================
CORD = ("data:image/svg+xml," + r1.quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 40" preserveAspectRatio="none">'
        '<path d="M2 40L50 3L98 40" fill="none" stroke="#6b5640" stroke-width="1.2" vector-effect="non-scaling-stroke"/></svg>', safe=""))
CSS_2 = """
.pr-wall { display: flex; flex-wrap: wrap; align-items: flex-start; justify-content: center; gap: 72px clamp(28px, 3.5vw, 48px); padding-top: 54px; }
.pr { position: relative; flex: none; width: 214px; padding: 9px; border-radius: 2px;
  background: linear-gradient(135deg, #5a3722, #3b2213 55%, #4d2e1b); box-shadow: inset 0 0 0 1px rgba(255, 220, 180, 0.12), inset 0 0 0 3px rgba(0, 0, 0, 0.25), 0 34px 40px -26px rgba(40, 18, 4, 0.6), 0 6px 10px -6px rgba(40, 18, 4, 0.4);
  transition: transform 0.6s var(--ease-out); transform-origin: 50% -46px; }
.pr::before { content: ""; position: absolute; bottom: 100%; left: 18%; right: 18%; height: 46px; background: url("CORD") no-repeat center / 100% 100%; }
.pr::after { content: ""; position: absolute; bottom: calc(100% + 40px); left: calc(50% - 5px); width: 10px; height: 10px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #e9d3a0, #8a6a30 70%); box-shadow: 0 2px 3px rgba(0, 0, 0, 0.4); }
.pr:hover { transform: rotate(-1.2deg); }
.pr-mat { padding: 18px 18px 12px; background: #f6f1e7; box-shadow: inset 0 0 0 1px rgba(80, 60, 30, 0.08), inset 0 2px 5px rgba(60, 40, 15, 0.12); }
.pr-bevel { padding: 4px; background: linear-gradient(135deg, #fff, #e3dccd); box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.8); }
.pr-bevel img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 4; object-fit: cover; }
.pr-t { display: block; margin-top: 11px; color: #4f463c; font-family: var(--display); font-size: 1.08rem; font-style: italic; line-height: 1.15; }
.pr-pencil { display: flex; align-items: baseline; justify-content: space-between; gap: 0.6rem; margin-top: 4px; }
.pr-pencil .p { flex: none; color: #4f463c; font-family: var(--display); font-size: 1.1rem; font-style: italic; font-weight: 600; font-variant-numeric: lining-nums; }
.pr-meta { color: #8f8576; font: 500 0.56rem var(--sans); letter-spacing: 0.2em; text-transform: uppercase; }
.pr--lead { width: 300px; }
.pr--lead .pr-mat { padding: 26px 26px 16px; }
.pr--lead .pr-t { font-size: 1.3rem; }
[data-theme="dark"] .pr { background: linear-gradient(135deg, #1d120a, #0e0805 55%, #1a100a); box-shadow: inset 0 0 0 1px rgba(227, 179, 74, 0.45), inset 0 0 0 3px rgba(0, 0, 0, 0.5), 0 34px 44px -26px rgba(0, 0, 0, 0.9); }
[data-theme="dark"] .pr::before { filter: invert(0.75) sepia(0.6); }
[data-theme="dark"] .pr-mat { background: #ece5d6; }
@media (max-width: 560px) { .pr-wall { gap: 64px 16px; } .pr { width: calc(50% - 8px); padding: 6px; } .pr--lead { width: 82%; } .pr-mat { padding: 10px 10px 8px; } .pr-pencil { flex-direction: column; gap: 0; } }
""".replace("CORD", CORD)


def pr(b, lead=False):
    price = f'<span class="p">{esc(b["price"])}</span>' if b.get("price") else ""
    return (f'<article class="pr{" pr--lead" if lead else ""}"><div class="pr-mat"><div class="pr-bevel">{pic(b, lazy=not lead)}</div>'
            f'<a class="pr-t r5-link" href="#">{esc(b["title"])}</a>'
            f'<div class="pr-pencil"><span class="pr-meta">{esc(b.get("subject") or "")}{" · " if b.get("subject") else ""}{yrs(b)}</span>{price}</div></div></article>')


pr_home = home(f"""
      <div class="pr-wall">{pr(HOME[1])}{pr(HOME[0], True)}{pr(HOME[2])}</div>
      <div class="pr-wall">{"".join(pr(b) for b in HOME[3:])}</div>
      <p class="r5-foot">{visit()}</p>""")
pr_page = page_main(groups(lambda bs: f'<div class="pr-wall">{"".join(pr(b) for b in bs)}</div>'))
BUILDS.append(("r5-02-prints", "Mounted prints", "Each photograph matted and framed, hung from a nail, pencilled.", CSS_2, pr_home, pr_page, ""))

# ============================================================================
# 3. Face-out ledge. Oak picture ledges in the site's wood; the books stand
#    face out on them (the photo cropped to the cover, a spine shade down its
#    left), each with a cream shelf-talker clipped over the ledge's lip.
#    Each book carries its own length of ledge, so a wrapped row gets its own.
# ============================================================================
CSS_3 = """
.lg-row { --gap: clamp(22px, 3vw, 40px); display: flex; flex-wrap: wrap; justify-content: center; gap: 160px var(--gap); padding: 0 calc(var(--gap) / 2) 140px; }
.lg-book { position: relative; flex: none; width: 168px; }
.lg-book::before { content: ""; position: absolute; top: 100%; left: calc(var(--gap) / -2); right: calc(var(--gap) / -2); height: 22px; border-radius: 2px;
  background: var(--grain), linear-gradient(180deg, #c48a62, var(--wood) 22%, #8a5233 70%, #6e3f25); background-size: var(--grain-size), auto;
  box-shadow: inset 0 1px 0 rgba(255, 230, 200, 0.4), 0 20px 22px -12px rgba(40, 18, 4, 0.55); }
.lg-book::after { content: ""; position: absolute; top: calc(100% - 4px); left: calc(var(--gap) / -2); right: calc(var(--gap) / -2); height: 4px; background: linear-gradient(180deg, rgba(0, 0, 0, 0), rgba(40, 18, 4, 0.25)); }
.lg-cover { position: relative; overflow: hidden; aspect-ratio: 3 / 4; border-radius: 2px 5px 5px 2px; transform-origin: 50% 100%;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.15) inset, -8px 4px 14px -6px rgba(30, 12, 2, 0.35), 0 18px 16px -14px rgba(30, 12, 2, 0.8); transition: transform 0.45s var(--ease-out), box-shadow 0.45s; }
.lg-cover img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.16); }
.lg-cover::after { content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0) 5%, rgba(255, 255, 255, 0.14) 7%, rgba(0, 0, 0, 0) 12%, rgba(0, 0, 0, 0) 88%, rgba(0, 0, 0, 0.12)); pointer-events: none; }
.lg-book:hover .lg-cover { transform: translateY(-10px) rotate(-2deg); box-shadow: 0 1px 0 rgba(255, 255, 255, 0.15) inset, -8px 4px 14px -6px rgba(30, 12, 2, 0.35), 0 30px 24px -16px rgba(30, 12, 2, 0.6); }
.lg-tag { position: absolute; z-index: 1; top: calc(100% + 9px); left: 8px; right: 8px; padding: 0.55rem 0.6rem 0.6rem; border-top: 2px solid var(--rust); background: #fffaf1; color: #2a1c10; text-align: center;
  box-shadow: 0 10px 14px -8px rgba(40, 18, 4, 0.45); }
.lg-tag::before { content: ""; position: absolute; top: -8px; left: calc(50% - 11px); width: 22px; height: 9px; border-radius: 2px 2px 0 0; background: linear-gradient(#e9d39b, #a77a2c); }
.lg-tag .r5-title { color: #2a1c10; font-size: 0.98rem; }
.lg-tag .r5-price { display: block; margin-top: 0.15rem; color: var(--rust-ink); font-size: 1.05rem; }
.lg-tag .yr { display: block; color: #8a7a66; font: 500 0.55rem var(--sans); letter-spacing: 0.2em; text-transform: uppercase; }
.lg-book--lead { width: 168px; }
[data-theme="dark"] .lg-tag { background: #2c1c0f; border-top-color: var(--gold); color: var(--g-text); box-shadow: inset 0 0 0 1px rgba(227, 179, 74, 0.25), 0 12px 16px -8px rgba(0, 0, 0, 0.8); }
[data-theme="dark"] .lg-tag .r5-title { color: var(--g-text); }
[data-theme="dark"] .lg-tag .r5-price { color: var(--gold-light); }
[data-theme="dark"] .lg-tag .yr { color: var(--g-muted); }
[data-theme="dark"] .lg-book::before { filter: brightness(0.8); }
@media (max-width: 560px) { .lg-row { --gap: 14px; row-gap: 140px; } .lg-book, .lg-book--lead { width: calc(50% - var(--gap)); } }
"""


def lg(b, lead=False):
    price = f'<span class="r5-price">{esc(b["price"])}</span>' if b.get("price") else ""
    return (f'<article class="lg-book{" lg-book--lead" if lead else ""}"><div class="lg-cover">{pic(b, tight=True)}</div>'
            f'<div class="lg-tag"><span class="yr">{years_line(b)}</span><h3 class="r5-title"><a class="r5-link" href="#">{esc(b["title"])}</a></h3>{price}</div></article>')


lg_home = home(f"""
      <div class="lg-row">{"".join(lg(b) for b in HOME[:4])}</div>
      <div class="lg-row">{"".join(lg(b) for b in HOME[4:])}</div>
      <p class="r5-foot" style="margin-top:0">{visit()}</p>""")
lg_page = page_main(groups(lambda bs: f'<div class="lg-row">{"".join(lg(b) for b in bs)}</div>'))
BUILDS.append(("r5-03-ledge", "Face-out ledge", "Books standing face out on oak ledges, a shelf-talker on each.", CSS_3, lg_home, lg_page, ""))

# ============================================================================
# 4. Price list. A feature spread for the lead book - its photograph large,
#    its description and price set like a magazine's - over the rest as a
#    typeset list: thumbnail, title, edition, a dotted leader, the price.
#    On the page every book is a line, and pointing at one floats its photo.
# ============================================================================
CSS_4 = """
.pl-feature { display: grid; grid-template-columns: minmax(0, 400px) minmax(0, 1fr); align-items: center; gap: clamp(2rem, 5vw, 4.5rem); margin-bottom: clamp(2.6rem, 5vw, 4rem); }
.pl-shot { position: relative; }
.pl-shot img { display: block; width: 100%; height: auto; border-radius: 4px; box-shadow: 0 40px 60px -40px rgba(40, 18, 4, 0.7), 0 3px 8px rgba(40, 18, 4, 0.12); }
.pl-shot::before { content: ""; position: absolute; inset: 22px -22px -22px 22px; z-index: -1; border: 1px solid var(--g-line); }
.pl-copy .r5-sub { margin-bottom: 0.8rem; }
.pl-copy h3 { color: var(--g-text); font-family: var(--title); font-size: clamp(2rem, 1.4rem + 2vw, 3.2rem); font-weight: 400; letter-spacing: 0.04em; line-height: 1.02; }
.pl-copy .r5-ed { margin-top: 0.4rem; font-size: 1.2rem; }
.pl-copy .desc { max-width: 34rem; margin: 1.3rem 0 1.6rem; color: var(--g-text); font-family: var(--display); font-size: 1.3rem; line-height: 1.45; }
.pl-copy .desc::first-letter { float: left; margin: 0.08em 0.1em 0 0; color: var(--g-accent); font-family: var(--title); font-size: 3.4em; line-height: 0.8; }
.pl-buy { display: flex; flex-wrap: wrap; align-items: center; gap: 1rem 1.6rem; padding-top: 1.2rem; border-top: 1px solid var(--g-line); }
.pl-buy .r5-price { color: var(--g-text); font-size: 2rem; }
.pl-buy .yr { color: var(--g-muted); font: 500 0.7rem var(--sans); letter-spacing: 0.16em; text-transform: uppercase; }
.pl-buy .btn { margin-left: auto; }
.pl-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: clamp(2rem, 5vw, 4rem); list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--g-line); }
.pl-row { position: relative; display: flex; align-items: center; gap: 1rem; padding: 0.75rem 0.2rem; border-bottom: 1px solid var(--g-line); transition: background 0.3s; }
.pl-row:hover { background: color-mix(in srgb, var(--g-text) 5%, transparent); }
.pl-row img { flex: none; width: 46px; height: 61px; object-fit: cover; border-radius: 2px; box-shadow: 0 6px 10px -6px rgba(40, 18, 4, 0.6); }
.pl-row .n { flex: none; width: 1.6rem; color: var(--g-accent); font-family: var(--display); font-size: 1rem; font-variant-numeric: lining-nums; }
.pl-row .tx { min-width: 0; }
.pl-row .r5-title { font-size: 1.15rem; }
.pl-row .r5-ed { font-size: 0.92rem; }
.pl-row .lead { flex: 1; min-width: 1.5rem; align-self: flex-end; margin-bottom: 0.95rem; border-bottom: 2px dotted color-mix(in srgb, var(--g-text) 35%, transparent); }
.pl-row .r5-price { flex: none; color: var(--g-text); font-size: 1.2rem; }
.pl-peek { position: fixed; z-index: 50; top: 0; left: 0; width: 210px; pointer-events: none; opacity: 0; transition: opacity 0.2s; }
.pl-peek.on { opacity: 1; }
.pl-peek img { display: block; width: 100%; border-radius: 4px; box-shadow: 0 30px 50px -20px rgba(20, 8, 0, 0.6); transform: rotate(2deg); }
.pl-page .r5-gh { margin-bottom: 0; border-bottom: 0; }
@media (max-width: 880px) { .pl-feature { grid-template-columns: 1fr; } .pl-shot { max-width: 340px; } .pl-list { grid-template-columns: 1fr; } }
"""


def sub_ed(b):
    return f'<p class="r5-ed">{esc(b.get("subject") or "")}</p>'


def pl_row(b, n):
    price = f'<span class="r5-price">{esc(b["price"])}</span>' if b.get("price") else ""
    return (f'<li class="pl-row" data-src="{esc(b["src"])}"><span class="n">{n:02d}</span>{pic(b)}<div class="tx"><h3 class="r5-title"><a class="r5-link" href="#">{esc(b["title"])}</a></h3>'
            f'{ed(b, "r5-ed") or sub_ed(b)}</div><span class="lead"></span>{price}</li>')


L = HOME[0]
pl_home = home(f"""
      <article class="pl-feature">
        <div class="pl-shot">{pic(L, lazy=False)}</div>
        <div class="pl-copy">
          <p class="r5-sub">{esc(L["subject"])} · {years_line(L)}</p>
          <h3>{esc(L["title"])}</h3>{ed(L, "r5-ed")}
          <p class="desc">{esc(L["description"])}</p>
          <div class="pl-buy"><span class="r5-price">{esc(L["price"])}</span><span class="yr">Collected at the masjid</span><a class="btn btn--gold" href="#">View the book {ARROW}</a></div>
        </div>
      </article>
      <ol class="pl-list">{"".join(pl_row(b, n + 2) for n, b in enumerate(HOME[1:]))}</ol>
      <p class="r5-foot">{visit()}</p>""")
pl_page = page_main('<div class="pl-page">' + groups(lambda bs: f'<ol class="pl-list">{"".join(pl_row(b, n + 1) for n, b in enumerate(bs))}</ol>') + '</div><div class="pl-peek" aria-hidden="true"><img alt=""></div>')
PL_JS = """
<script>
  (function () {
    var peek = document.querySelector(".pl-peek");
    if (!peek) return;
    var img = peek.querySelector("img");
    document.querySelectorAll(".pl-row").forEach(function (r) {
      r.addEventListener("pointerenter", function (e) { if (e.pointerType === "touch") return; img.src = r.dataset.src; peek.classList.add("on"); });
      r.addEventListener("pointerleave", function () { peek.classList.remove("on"); });
      r.addEventListener("pointermove", function (e) {
        var x = e.clientX + 28, y = Math.min(e.clientY - 140, innerHeight - 300);
        if (x + 230 > innerWidth) x = e.clientX - 240;
        peek.style.transform = "translate(" + x + "px," + Math.max(10, y) + "px)";
      });
    });
  })();
</script>"""
BUILDS.append(("r5-04-pricelist", "Price list", "A feature spread, then a typeset list with leaders; photos float on hover.", CSS_4, pl_home, pl_page, PL_JS))

# ============================================================================
# 5. Lookbook. Big photographs in a run that scrolls sideways out to the
#    page's edges, captions under them set like a magazine's, an intro panel
#    first. The page: a year at a time, its first book twice the size.
# ============================================================================
CSS_5 = """
.lb { position: relative; margin-inline: calc(50% - 50vw); }
.lb-run { display: flex; gap: clamp(18px, 2.4vw, 32px); overflow-x: auto; padding: 10px max(var(--gutter), calc(50vw - 590px)) 30px; scroll-snap-type: x mandatory; scroll-padding-inline: max(var(--gutter), calc(50vw - 590px)); scrollbar-width: none; }
.lb-run::-webkit-scrollbar { display: none; }
.lb-intro { flex: none; display: flex; flex-direction: column; justify-content: flex-end; gap: 1rem; width: 280px; padding-bottom: 5.4rem; scroll-snap-align: start; }
.lb-intro .big { color: var(--g-text); font-family: var(--title); font-size: 4.4rem; line-height: 0.9; }
.lb-intro p { color: var(--g-muted); font-family: var(--display); font-size: 1.3rem; font-style: italic; line-height: 1.35; }
.lb-intro .btn { align-self: flex-start; }
.lb-item { position: relative; flex: none; width: clamp(240px, 26vw, 340px); scroll-snap-align: start; }
.lb-item img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 4; object-fit: cover; border-radius: 3px; box-shadow: 0 30px 40px -32px rgba(40, 18, 4, 0.7); transition: transform 0.6s var(--ease-out); }
.lb-item:hover img { transform: translateY(-6px); }
.lb-cap { display: grid; grid-template-columns: auto 1fr auto; align-items: baseline; gap: 0.2rem 0.8rem; margin-top: 1rem; padding-top: 0.7rem; border-top: 1px solid var(--g-text); }
.lb-cap .n { color: var(--g-muted); font: 500 0.66rem var(--sans); letter-spacing: 0.14em; }
.lb-cap .r5-title { font-size: 1.3rem; }
.lb-cap .r5-price { color: var(--g-text); font-size: 1.15rem; }
.lb-cap .r5-ed, .lb-cap .r5-sub { grid-column: 2 / -1; }
.lb-cap .r5-sub { color: var(--g-muted); }
.lb-arrows { display: flex; justify-content: flex-end; gap: 0.6rem; width: min(100% - 2 * var(--gutter), 1180px); margin: 0 auto; }
.lb-arrows button { display: grid; place-items: center; width: 46px; height: 46px; border: 1px solid var(--g-line); border-radius: 50%; background: transparent; color: var(--g-text); cursor: pointer; transition: background 0.3s; }
.lb-arrows button:hover { background: color-mix(in srgb, var(--g-text) 8%, transparent); }
.lb-arrows svg { width: 22px; }
.lb-arrows button:first-child svg { transform: scaleX(-1); }
.lb-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: clamp(28px, 3vw, 40px) clamp(18px, 2.4vw, 32px); }
.lb-grid .lb-item { width: auto; }
.lb-grid .lb-item:first-child { grid-column: span 2; grid-row: span 2; }
.lb-grid .lb-item:first-child .r5-title { font-family: var(--title); font-size: 1.9rem; font-weight: 400; }
@media (max-width: 980px) { .lb-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .lb-grid .lb-item:first-child { grid-row: auto; } }
@media (max-width: 560px) { .lb-intro { width: 220px; } .lb-intro .big { font-size: 3.2rem; } }
"""


def lb_item(b, n, total):
    price = f'<span class="r5-price">{esc(b["price"])}</span>' if b.get("price") else "<span></span>"
    sub = f'<p class="r5-sub">{esc(b.get("subject") or "")} · {years_line(b)}</p>'
    return (f'<article class="lb-item">{pic(b)}<div class="lb-cap"><span class="n">{n:02d} / {total:02d}</span>'
            f'<h3 class="r5-title"><a class="r5-link" href="#">{esc(b["title"])}</a></h3>{price}{ed(b, "r5-ed")}{sub}</div></article>')


lb_home = home(f"""
      <div class="lb">
        <div class="lb-run" tabindex="0" aria-label="Books">
          <div class="lb-intro"><span class="big">{COUNT}</span><p>books for all seven years</p>{visit()}</div>
          {"".join(lb_item(b, n + 1, len(HOME)) for n, b in enumerate(HOME))}
        </div>
        <div class="lb-arrows"><button type="button" aria-label="Back">{ARROW}</button><button type="button" aria-label="Forward">{ARROW}</button></div>
      </div>""")
lb_page = page_main(groups(lambda bs: f'<div class="lb-grid">{"".join(lb_item(b, n + 1, len(bs)) for n, b in enumerate(bs))}</div>'))
LB_JS = """
<script>
  document.querySelectorAll(".lb").forEach(function (lb) {
    var run = lb.querySelector(".lb-run"), b = lb.querySelectorAll(".lb-arrows button");
    b[0].addEventListener("click", function () { run.scrollBy({ left: -run.clientWidth * 0.7, behavior: "smooth" }); });
    b[1].addEventListener("click", function () { run.scrollBy({ left: run.clientWidth * 0.7, behavior: "smooth" }); });
  });
</script>"""
BUILDS.append(("r5-05-lookbook", "Lookbook", "Big photographs in a sideways run with magazine captions.", CSS_5, lb_home, lb_page, LB_JS))

# ============================================================================
# 6. Cover tint. Each tile is washed in the colour measured from its own
#    cover; the photograph floats on it with a shadow of the same colour, and
#    the price is a chip of it. The lead book gets a wide tile.
# ============================================================================
CSS_6 = """
.tn-wide { position: relative; display: grid; grid-template-columns: minmax(0, 0.6fr) minmax(0, 1.4fr); align-items: center; gap: clamp(1.6rem, 4vw, 3.6rem); margin-bottom: 18px; padding: clamp(1.6rem, 4vw, 3.2rem) clamp(1.6rem, 5vw, 4.4rem); }
.tn-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 18px; }
.tn { --wash: color-mix(in oklab, var(--t) 20%, #fbf5ec); --wash-2: color-mix(in oklab, var(--t) 34%, #f3e6d2); --ink: color-mix(in oklab, var(--t) 40%, #1d120a);
  position: relative; overflow: hidden; border-radius: 16px; background: radial-gradient(120% 90% at 50% 20%, var(--wash), var(--wash-2)); color: var(--ink); transition: transform 0.45s var(--ease-out); }
.tn:hover { transform: translateY(-4px); }
.tn:hover .tn-shot img { transform: translateY(-4px) rotate(-1.5deg); }
.tn-shot { padding: 12% 15% 0; }
.tn-shot img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 4; object-fit: cover; border-radius: 4px; transition: transform 0.5s var(--ease-out);
  box-shadow: 0 26px 30px -18px color-mix(in oklab, var(--t) 70%, #000), 0 2px 5px rgba(0, 0, 0, 0.12); }
.tn-body { display: flex; flex-direction: column; gap: 0.25rem; padding: 1rem 1.1rem 1.15rem; }
.tn .r5-sub, .tn .r5-ed { color: color-mix(in oklab, var(--ink) 75%, transparent); }
.tn .r5-title { color: var(--ink); font-size: 1.1rem; }
.tn .r5-price { align-self: flex-start; margin-top: 0.5rem; padding: 0.1rem 0.7rem 0; border-radius: 99px; background: color-mix(in oklab, var(--t) 85%, #000); color: #fff; font-size: 1.05rem; }
.tn-wide .tn-shot { max-width: 300px; justify-self: center; padding: 0; }
.tn-wide .r5-title { font-family: var(--title); font-size: clamp(1.8rem, 1.2rem + 2vw, 3rem); font-weight: 400; letter-spacing: 0.04em; }
.tn-wide .r5-ed { font-size: 1.2rem; }
.tn-wide .desc { max-width: 32rem; margin: 0.9rem 0 0.4rem; color: var(--ink); font-family: var(--display); font-size: 1.25rem; line-height: 1.45; }
.tn-wide .r5-price { font-size: 1.4rem; }
.tn-wide .tn-body { padding: 0; }
[data-theme="dark"] .tn { --wash: color-mix(in oklab, var(--t) 42%, #1f1108); --wash-2: color-mix(in oklab, var(--t) 22%, #140a04); --ink: color-mix(in oklab, var(--t) 18%, #f6ead8);
  box-shadow: inset 0 1px 0 rgba(255, 236, 210, 0.08); }
[data-theme="dark"] .tn .r5-price { background: color-mix(in oklab, var(--t) 50%, #f6ead8); color: #1d120a; }
.tn-page { grid-template-columns: repeat(4, minmax(0, 1fr)); }
@media (max-width: 1040px) { .tn-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 720px) { .tn-wide { grid-template-columns: 1fr; } .tn-wide .tn-shot { max-width: 260px; } .tn-grid, .tn-page { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; } }
"""


def tn(b, wide=False):
    price = f'<span class="r5-price">{esc(b["price"])}</span>' if b.get("price") else ""
    desc = f'<p class="desc">{esc(b["description"])}</p>' if wide else ""
    sub = f'<p class="r5-sub">{esc(b.get("subject") or "")}{" · " + years_line(b) if wide else ""}</p>'
    return (f'<article class="tn{" tn-wide" if wide else ""}" style="{style(b)}"><div class="tn-shot">{pic(b, lazy=not wide, tight=True)}</div>'
            f'<div class="tn-body">{sub}<h3 class="r5-title"><a class="r5-link" href="#">{esc(b["title"])}</a></h3>{ed(b, "r5-ed")}{desc}{price}</div></article>')


tn_home = home(f"""
      {tn(HOME[0], True)}
      <div class="tn-grid">{"".join(tn(b) for b in HOME[1:])}</div>
      <p class="r5-foot">{visit()}</p>""")
tn_page = page_main(groups(lambda bs: f'<div class="tn-grid tn-page">{"".join(tn(b) for b in bs)}</div>'))
BUILDS.append(("r5-06-tint", "Cover tint", "Each tile washed in the colour measured from its own cover.", CSS_6, tn_home, tn_page, ""))

# ============================================================================
# 7. Plinths. A gallery display: each book standing on a stone plinth, the
#    heights stepping up to the lead book in the middle, the title and price
#    cut into the plinth's face. On the page, a row of even plinths a year.
# ============================================================================
CSS_7 = """
.pn-stage { display: flex; align-items: flex-end; justify-content: safe center; gap: clamp(8px, 1.2vw, 16px); overflow-x: auto; padding: 30px 6px 0; scrollbar-width: thin;
  background: radial-gradient(60% 70% at 50% 100%, color-mix(in srgb, var(--gold-light) 18%, transparent), transparent 70%); }
.pn { position: relative; flex: none; display: flex; flex-direction: column; align-items: center; width: 136px; }
.pn-book { position: relative; width: 82%; margin-bottom: -1px; overflow: hidden; aspect-ratio: 3 / 4; border-radius: 2px 4px 4px 2px; transition: transform 0.5s var(--ease-out);
  box-shadow: -6px 0 12px -6px rgba(30, 12, 2, 0.4), 0 16px 12px -12px rgba(30, 12, 2, 0.75); }
.pn-book img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.14); }
.pn-book::after { content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(0, 0, 0, 0.32), rgba(0, 0, 0, 0) 5%, rgba(255, 255, 255, 0.12) 7%, rgba(0, 0, 0, 0) 12%); }
.pn:hover .pn-book { transform: translateY(-8px); }
.pn-top { width: 100%; height: 12px; background: linear-gradient(180deg, #fbf6ec, #e7dccb); clip-path: polygon(5% 0, 95% 0, 100% 100%, 0 100%); }
.pn-face { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; gap: 0.3rem; width: 100%; height: var(--h, 150px); padding: 1rem 0.6rem 0;
  background: linear-gradient(90deg, #d6c8b2, #ece2d2 30%, #e4d8c5 70%, #cbbca4); box-shadow: inset 0 -30px 40px -30px rgba(80, 55, 20, 0.35), 0 20px 30px -20px rgba(40, 18, 4, 0.3); text-align: center; }
.pn-face .r5-title { color: #3c2a18; font-family: var(--title); font-size: 0.86rem; font-weight: 400; letter-spacing: 0.08em; line-height: 1.25; text-transform: uppercase; text-shadow: 0 1px 0 rgba(255, 255, 255, 0.7); }
.pn-face .r5-price { color: #8a5f12; font-size: 1.05rem; text-shadow: 0 1px 0 rgba(255, 255, 255, 0.6); }
.pn-face .yr { color: #8a7a66; font: 500 0.52rem var(--sans); letter-spacing: 0.22em; text-transform: uppercase; }
.pn-face::before { content: ""; width: 24px; height: 1px; margin-bottom: 0.2rem; background: #b28a3e; }
.pn--lead { width: 176px; }
.pn--lead .r5-title { font-size: 1rem; }
.pn-floor { height: 2px; margin-top: -1px; background: linear-gradient(90deg, transparent, var(--g-line), transparent); }
.pn-row { display: flex; flex-wrap: wrap; justify-content: center; gap: 46px clamp(10px, 1.6vw, 22px); }
.pn-row .pn { --h: 112px; }
[data-theme="dark"] .pn-top { background: linear-gradient(180deg, #5a3a22, #3a2414); }
[data-theme="dark"] .pn-face { background: linear-gradient(90deg, #1e1209, #3a2414 30%, #321e10 70%, #1a0f07); box-shadow: inset 0 1px 0 rgba(227, 179, 74, 0.4), 0 20px 30px -20px rgba(0, 0, 0, 0.8); }
[data-theme="dark"] .pn-face .r5-title { color: var(--gold-pale); text-shadow: none; }
[data-theme="dark"] .pn-face .r5-price { color: var(--gold); text-shadow: none; }
[data-theme="dark"] .pn-face .yr { color: var(--g-muted); }
@media (max-width: 560px) { .pn-row .pn { width: calc(50% - 8px); } }
"""
PN_H = [120, 165, 205, 240, 205, 165, 120]


def pn(b, h=None, lead=False):
    price = f'<span class="r5-price">{esc(b["price"])}</span>' if b.get("price") else ""
    st = f' style="--h:{h}px"' if h else ""
    return (f'<article class="pn{" pn--lead" if lead else ""}"{st}><div class="pn-book">{pic(b, tight=True)}</div><div class="pn-top"></div>'
            f'<div class="pn-face"><h3 class="r5-title"><a class="r5-link" href="#">{esc(b["title"])}</a></h3><span class="yr">{years_line(b)}</span>{price}</div></article>')


ORDER = [HOME[5], HOME[3], HOME[1], HOME[0], HOME[2], HOME[4], HOME[6]]
pn_home = home(f"""
      <div class="pn-stage">{"".join(pn(b, h, b is HOME[0]) for b, h in zip(ORDER, PN_H))}</div>
      <div class="pn-floor"></div>
      <p class="r5-foot">{visit()}</p>""")
pn_page = page_main(groups(lambda bs: f'<div class="pn-row">{"".join(pn(b) for b in bs)}</div>'))
BUILDS.append(("r5-07-plinths", "Plinths", "A gallery display on stepped stone plinths, labels cut into them.", CSS_7, pn_home, pn_page, ""))

# ============================================================================
# 8. Index cards. A library catalogue card for each book - ruled, typed in
#    Courier, a call mark in the corner and a punched hole - with its
#    photograph paper-clipped on. The page opens a drawer per year.
# ============================================================================
CLIP = ("data:image/svg+xml," + r1.quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 60">'
        '<path d="M15 14V46a6 6 0 0 1-12 0V8a5 5 0 0 1 10 0v34a2.5 2.5 0 0 1-5 0V14" fill="none" stroke="#9aa1a8" stroke-width="2.2" stroke-linecap="round"/>'
        '<path d="M15 14V46a6 6 0 0 1-12 0V8a5 5 0 0 1 10 0v34a2.5 2.5 0 0 1-5 0V14" fill="none" stroke="#eef1f4" stroke-width="0.8" stroke-linecap="round" transform="translate(-0.6 -0.4)"/></svg>', safe=""))
CSS_8 = """
.ic-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: clamp(22px, 2.6vw, 34px) clamp(18px, 2.2vw, 28px); }
.ic { position: relative; display: grid; grid-template-columns: 40% 1fr; gap: 1rem; min-height: 210px; padding: 1.4rem 1.2rem 1.6rem 1.1rem; border-radius: 3px;
  background: linear-gradient(#fbf8f1 0 2.4rem, #c9473b 2.4rem 2.5rem, transparent 2.5rem), repeating-linear-gradient(#fbf8f1 0 1.3rem, #b9cbe0 1.3rem calc(1.3rem + 1px)) 0 2.5rem / 100% 100% no-repeat, #fbf8f1;
  color: #2b2a2e; font-family: "Courier Prime", "Courier New", monospace; box-shadow: 0 1px 0 rgba(255, 255, 255, 0.9) inset, 0 18px 26px -18px rgba(40, 18, 4, 0.45), 0 1px 2px rgba(40, 18, 4, 0.15);
  transition: transform 0.4s var(--ease-out); }
.ic:nth-child(3n + 1) { transform: rotate(-0.5deg); }
.ic:nth-child(3n + 2) { transform: rotate(0.4deg); }
.ic:hover { transform: translateY(-4px) rotate(0deg); }
.ic::after { content: ""; position: absolute; bottom: 0.55rem; left: calc(50% - 6px); width: 12px; height: 12px; border-radius: 50%; background: var(--ground-hole, #e9cdae); box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3); }
.ic-photo { position: relative; align-self: start; margin: -0.4rem 0 0 -0.2rem; transform: rotate(-3deg); }
.ic-photo img { display: block; width: 100%; height: auto; border: 4px solid #fff; box-shadow: 0 8px 12px -6px rgba(0, 0, 0, 0.4); }
.ic-photo::before { content: ""; position: absolute; z-index: 1; top: -14px; left: 22%; width: 13px; height: 38px; background: url("CLIP") no-repeat center / contain; }
.ic-call { position: absolute; top: 0.75rem; right: 1rem; color: #c9473b; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; }
.ic-txt { display: flex; flex-direction: column; padding-top: 1.55rem; font-size: 0.8rem; line-height: 1.3rem; }
.ic-txt h3 { font-size: 0.92rem; font-weight: 700; line-height: 1.3rem; }
.ic-txt a { color: inherit; text-decoration: none; }
.ic-txt .ed { font-style: italic; }
.ic-txt .pr { margin-top: auto; font-weight: 700; font-size: 0.95rem; }
.ic-txt .pr::before { content: "Price "; color: #6b6a70; font-weight: 400; font-size: 0.8rem; }
.ic-drawer { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem; grid-column: span 2; min-height: 210px; border-radius: 4px; text-align: center;
  background: var(--grain), linear-gradient(180deg, #b57b55, var(--wood) 40%, #84502f); background-size: var(--grain-size), auto; box-shadow: inset 0 2px 0 rgba(255, 230, 200, 0.3), inset 0 -10px 16px rgba(40, 18, 4, 0.35), 0 20px 30px -20px rgba(40, 18, 4, 0.6); }
.ic-label { padding: 0.5rem 1.4rem; border: 3px solid #c9a24f; border-radius: 3px; background: #f6efe0; box-shadow: inset 0 0 0 1px #8a6a2a, 0 2px 3px rgba(0, 0, 0, 0.35); color: #2b2a2e; font: 700 0.95rem "Courier Prime", monospace; letter-spacing: 0.06em; }
.ic-pull { width: 70px; height: 18px; border-radius: 0 0 40px 40px; border: 4px solid #c9a24f; border-top: 0; box-shadow: 0 3px 4px rgba(0, 0, 0, 0.35); }
.ic-drawer .btn { margin-top: 0.2rem; }
.ic-dhead { display: flex; flex-direction: column; align-items: center; gap: 0.7rem; margin: 0 auto clamp(1.6rem, 3vw, 2.2rem); padding: 1.1rem 2rem; max-width: 420px; border-radius: 4px;
  background: var(--grain), linear-gradient(180deg, #b57b55, var(--wood) 40%, #84502f); background-size: var(--grain-size), auto; box-shadow: inset 0 2px 0 rgba(255, 230, 200, 0.3), inset 0 -8px 12px rgba(40, 18, 4, 0.35), 0 16px 24px -16px rgba(40, 18, 4, 0.6); }
.ic-dhead .ic-label { font-size: 1.05rem; }
.ic-dhead .ic-label small { display: block; color: #6b6a70; font-weight: 400; font-size: 0.72rem; }
[data-theme="dark"] .ic { --ground-hole: #1d0f05; box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.3), 0 24px 30px -18px rgba(0, 0, 0, 0.9); }
[data-theme="dark"] .ic-drawer, [data-theme="dark"] .ic-dhead { filter: brightness(0.75); }
@media (max-width: 1040px) { .ic-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) { .ic-grid { grid-template-columns: 1fr; } .ic-drawer { grid-column: auto; } }
""".replace("CLIP", CLIP)


def call(b):
    s = (b.get("subject") or "BK").upper().replace(" ", "")[:3]
    return f"{s} {b['i'] + 1:03d}"


def ic(b):
    price = f'<p class="pr">{esc(b["price"])}</p>' if b.get("price") else ""
    ed_ = f'<p class="ed">{esc(b["edition"])}</p>' if b.get("edition") else ""
    return (f'<article class="ic"><span class="ic-call">{call(b)}</span><div class="ic-photo">{pic(b)}</div>'
            f'<div class="ic-txt"><h3><a class="r5-link" href="#">{esc(b["title"])}</a></h3>{ed_}<p>{esc(b.get("subject") or "")}</p><p>{years_line(b)}</p>{price}</div></article>')


ic_home = home(f"""
      <div class="ic-grid">
        {"".join(ic(b) for b in HOME)}
        <div class="ic-drawer"><span class="ic-label">BOOKSTORE · {COUNT} CARDS</span><span class="ic-pull"></span>{visit()}</div>
      </div>""")
ic_page = page_main(groups(lambda bs: f'<div class="ic-grid">{"".join(ic(b) for b in bs)}</div>',
                           lambda y, bs: f'<div class="ic-dhead"><span class="ic-label">{y.upper()}<small>{len(bs)} cards</small></span><span class="ic-pull"></span></div>'))
BUILDS.append(("r5-08-cards", "Index cards", "Typed catalogue cards with the photographs clipped on; a drawer a year.", CSS_8, ic_home, ic_page, ""))

# ============================================================================
# 9. Showroom. One book large - photograph, title, edition, description,
#    years, price, a button - and the others as thumbnails to choose from.
#    On the page the viewer is sticky on the left and the thumbnails of
#    every year scroll past it on the right.
# ============================================================================
CSS_9 = """
.sr { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 0.75fr); gap: clamp(1.8rem, 4vw, 3.6rem); align-items: start; }
.sr-view { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr); gap: clamp(1.2rem, 2.5vw, 2rem); align-items: end; }
.sr-photo { position: relative; padding: 8%; border-radius: 20px; background: radial-gradient(110% 90% at 50% 25%, color-mix(in srgb, var(--bg, #ddd) 70%, #fff), var(--bg, #ddd)); transition: background 0.5s;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6), 0 30px 46px -32px rgba(40, 18, 4, 0.6); }
.sr-photo img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 4; object-fit: cover; border-radius: 4px; box-shadow: 0 24px 30px -20px rgba(30, 12, 2, 0.6); }
.sr-info { display: flex; flex-direction: column; gap: 0.3rem; }
.sr-info h3 { color: var(--g-text); font-family: var(--title); font-size: clamp(1.6rem, 1.1rem + 1.4vw, 2.4rem); font-weight: 400; letter-spacing: 0.04em; line-height: 1.05; }
.sr-info .r5-ed { font-size: 1.1rem; }
.sr-info .desc { margin: 0.8rem 0; color: var(--g-text); font-size: 0.9rem; line-height: 1.7; }
.sr-info .yr { color: var(--g-muted); font: 500 0.7rem var(--sans); letter-spacing: 0.16em; text-transform: uppercase; }
.sr-info .r5-price { margin: 0.3rem 0 1rem; color: var(--g-text); font-size: 2rem; }
.sr-info .btn { align-self: flex-start; }
.sr-swap { animation: sr-in 0.5s var(--ease-out); }
@keyframes sr-in { from { opacity: 0; transform: translateY(8px); } }
.sr-thumbs { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px 12px; }
.sr-thumb { display: flex; flex-direction: column; gap: 0.5rem; padding: 0; border: 0; background: none; color: var(--g-text); font: inherit; text-align: left; cursor: pointer; }
.sr-thumb .ph { padding: 9%; border-radius: 12px; background: var(--bg); box-shadow: inset 0 0 0 2px transparent; transition: box-shadow 0.3s, transform 0.4s var(--ease-out); }
.sr-thumb img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 4; object-fit: cover; border-radius: 2px; }
.sr-thumb:hover .ph { transform: translateY(-3px); }
.sr-thumb[aria-pressed="true"] .ph { box-shadow: inset 0 0 0 2px var(--g-mark), 0 0 0 3px color-mix(in srgb, var(--g-mark) 25%, transparent); }
.sr-thumb .t { font-family: var(--display); font-size: 1rem; font-weight: 600; line-height: 1.15; }
.sr-thumb .p { color: var(--g-muted); font-family: var(--display); font-size: 0.95rem; }
.sr-more { display: flex; align-items: center; justify-content: center; border: 1px dashed var(--g-line); border-radius: 12px; color: var(--g-text); font-family: var(--display); font-size: 1.15rem; font-style: italic; text-decoration: none; }
.sr-more:hover { background: color-mix(in srgb, var(--g-text) 5%, transparent); }
.sr--page { grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr); }
.sr--page .sr-stick { position: sticky; top: 24px; }
.sr--page .sr-view { grid-template-columns: 1fr; }
.sr--page .sr-photo { max-width: 360px; }
.sr--page .sr-thumbs { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.sr--page .r5-filter { justify-content: flex-start; margin: 0 0 2rem; }
[data-theme="dark"] .sr-photo, [data-theme="dark"] .sr-thumb .ph { filter: brightness(0.93); }
@media (max-width: 1040px) { .sr { grid-template-columns: 1fr; } .sr-view { grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr); } .sr--page .sr-stick { position: static; } .sr--page .sr-view { grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr); } }
@media (max-width: 560px) { .sr-view, .sr--page .sr-view { grid-template-columns: 1fr; } .sr-thumbs, .sr--page .sr-thumbs { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
"""


def sr_view(b):
    return (f'<div class="sr-view" data-view><div class="sr-photo" style="{style(b)}"><img data-f="src" src="{b["src"]}" width="600" height="800" alt=""></div>'
            f'<div class="sr-info"><p class="r5-sub" data-f="sub">{esc(b.get("subject") or "")}</p><h3 data-f="title">{esc(b["title"])}</h3>'
            f'<p class="r5-ed" data-f="ed">{esc(b.get("edition") or "")}</p><p class="desc" data-f="desc">{esc(b.get("description") or "")}</p>'
            f'<p class="yr" data-f="years">{years_line(b)}</p><p class="r5-price" data-f="price">{esc(b.get("price") or "")}</p>'
            f'<a class="btn btn--gold" href="#">View the book {ARROW}</a></div></div>')


def sr_thumb(b, on=False):
    return (f'<button class="sr-thumb" type="button" aria-pressed="{str(on).lower()}" {data_attrs(b)}><span class="ph">{pic(b)}</span>'
            f'<span class="t">{esc(b["title"])}</span><span class="p">{esc(b.get("price") or "")}</span></button>')


sr_home = home(f"""
      <div class="sr">
        {sr_view(HOME[0])}
        <div class="sr-thumbs">{"".join(sr_thumb(b, i == 0) for i, b in enumerate(HOME[:5]))}<a class="sr-more" href="#">{COUNT - 5} more books →</a></div>
      </div>
      <p class="r5-foot">{visit()}</p>""")
sr_page = f"""
<main id="main" class="r3-page">
  <div class="r3-wrap">
    <a class="r3-back" href="#">← Home</a>
    <div class="section__head"><h1 class="section__heading">Bookstore</h1><p class="section__lede">{esc(LEDE)}</p></div>
    <div class="sr sr--page">
      <div class="sr-stick">{sr_view(BOOKS[0])}</div>
      <div>{filter_bar()}{groups(lambda bs: f'<div class="sr-thumbs">{"".join(sr_thumb(b, b is BOOKS[0]) for b in bs)}</div>')}</div>
    </div>
  </div>
</main>"""
SR_JS = """
<script>
  (function () {
    var view = document.querySelector("[data-view]");
    var map = { src: "src", sub: "sub", title: "title", ed: "ed", desc: "desc", years: "years", price: "price" };
    document.querySelectorAll(".sr-thumb").forEach(function (t) {
      t.addEventListener("click", function () {
        document.querySelectorAll(".sr-thumb").forEach(function (x) { x.setAttribute("aria-pressed", String(x.dataset.title === t.dataset.title && x.dataset.ed === t.dataset.ed)); });
        view.querySelectorAll("[data-f]").forEach(function (n) {
          var v = t.dataset[map[n.dataset.f]];
          if (n.tagName === "IMG") n.src = v; else n.textContent = v;
        });
        view.querySelector(".sr-photo").setAttribute("style", t.getAttribute("style"));
        view.classList.remove("sr-swap"); void view.offsetWidth; view.classList.add("sr-swap");
        if (view.getBoundingClientRect().top < 0) view.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  })();
</script>"""
BUILDS.append(("r5-09-showroom", "Showroom", "One book large with everything about it; thumbnails beside to choose.", CSS_9, sr_home, sr_page, SR_JS))

# ============================================================================
# 10. Receipt. Under each photograph a till receipt slips out - the masjid's
#     name, the title, the edition, the years, a dashed rule, the total and a
#     barcode, torn off at the foot. Pointing at a book pulls it further out.
#     The receipt is what a buyer brings to the masjid to collect the book.
# ============================================================================
CSS_10 = """
.rc-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: clamp(26px, 3vw, 40px) clamp(18px, 2.4vw, 30px); align-items: start; }
.rc { position: relative; }
.rc-photo { position: relative; z-index: 1; transition: transform 0.45s var(--ease-out); }
.rc-photo img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 4; object-fit: cover; border-radius: 4px; box-shadow: 0 22px 30px -20px rgba(40, 18, 4, 0.65), 0 2px 4px rgba(40, 18, 4, 0.12); }
.rc-slip { position: relative; width: 84%; margin: -18px auto 0; padding: 30px 0.9rem 22px; background: #fdfcf7; color: #2a2a2a; font: 400 0.72rem/1.5 "Courier Prime", "Courier New", monospace; text-transform: uppercase;
  -webkit-mask: conic-gradient(from -45deg at bottom, #0000, #000 1deg 89deg, #0000 90deg) 50% / 10px 100%; mask: conic-gradient(from -45deg at bottom, #0000, #000 1deg 89deg, #0000 90deg) 50% / 10px 100%;
  filter: drop-shadow(0 6px 6px rgba(40, 18, 4, 0.18)); box-shadow: 0 10px 14px -10px rgba(40, 18, 4, 0.3); transition: transform 0.45s var(--ease-out); }
.rc:hover .rc-slip { transform: translateY(10px); }
.rc:hover .rc-photo { transform: translateY(-4px); }
.rc-slip .hd { color: #777; font-size: 0.62rem; letter-spacing: 0.08em; text-align: center; }
.rc-slip hr { margin: 0.45rem 0; border: 0; border-top: 1px dashed #9a9a9a; }
.rc-slip h3 { font-size: 0.8rem; font-weight: 700; line-height: 1.35; }
.rc-slip h3 a { color: inherit; text-decoration: none; }
.rc-slip .ln { display: flex; justify-content: space-between; gap: 0.5rem; }
.rc-slip .tot { font-size: 0.86rem; font-weight: 700; }
.rc-slip .bar { height: 26px; margin-top: 0.55rem; background: repeating-linear-gradient(90deg, #2a2a2a 0 2px, transparent 2px 3px, #2a2a2a 3px 4px, transparent 4px 7px, #2a2a2a 7px 10px, transparent 10px 11px); }
.rc-tile { display: flex; flex-direction: column; justify-content: center; gap: 1rem; align-self: stretch; padding: 1.8rem; border-radius: 6px; background: linear-gradient(160deg, var(--board), var(--board-deep)); color: var(--gold-pale);
  box-shadow: inset 0 1px 0 rgba(227, 179, 74, 0.35), 0 22px 30px -20px rgba(40, 18, 4, 0.6); }
.rc-tile b { color: var(--gold); font-family: var(--title); font-size: 3rem; font-weight: 400; line-height: 1; }
.rc-tile p { font-family: var(--display); font-size: 1.2rem; font-style: italic; line-height: 1.35; }
.rc-tile .btn { align-self: flex-start; }
[data-theme="dark"] .rc-tile { background: var(--g-card); border: 1px solid var(--g-line); }
[data-theme="dark"] .rc-slip { background: #f3eee2; }
@media (max-width: 1040px) { .rc-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 720px) { .rc-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .rc-slip { width: 92%; padding-inline: 0.6rem; font-size: 0.64rem; } }
"""


def rc(b):
    ed_ = f'<p>{esc(b["edition"])}</p>' if b.get("edition") else ""
    price = esc(b.get("price") or "—")
    return (f'<article class="rc"><div class="rc-photo">{pic(b)}</div><div class="rc-slip"><p class="hd">Abu Bakr · Bookstore</p><hr>'
            f'<h3><a class="r5-link" href="#">{esc(b["title"])}</a></h3>{ed_}<p class="ln"><span>{esc(b.get("subject") or "")}</span><span>{yrs(b)}</span></p><hr>'
            f'<p class="ln tot"><span>Total</span><span>{price}</span></p><div class="bar"></div></div></article>')


rc_home = home(f"""
      <div class="rc-grid">
        {"".join(rc(b) for b in HOME)}
        <div class="rc-tile"><b>{COUNT}</b><p>books for all seven years</p>{visit("btn btn--gold btn--sm")}</div>
      </div>""")
rc_page = page_main(groups(lambda bs: f'<div class="rc-grid">{"".join(rc(b) for b in bs)}</div>'))
BUILDS.append(("r5-10-receipt", "Receipt", "A till receipt slips out from under each photograph.", CSS_10, rc_home, rc_page, ""))

# ============================================================================
# 11. Objects, with photographs: round 2's option 2 redone on the real stock.
#     Each book is a 3D object - the photo on its face (zoomed past the grey
#     table margin), a page block down its fore-edge, a back cover in the
#     colour measured from the photo - turned to show its pages and turning
#     to face you when pointed at; the price set under its name.
#     The head is set left beside four books. The page filters by bookmarks
#     hanging from a rail, one per year, in that year's binding.
# ============================================================================
_spec2 = importlib.util.spec_from_file_location("round2", HERE / "generate_round2.py")
r2 = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(r2)

CSS_11 = r2.CSS_2.replace(".r2-wrap", ".r3-wrap") + """
.r3-wrap { width: min(100% - 2 * var(--gutter), 1180px); margin-inline: auto; }
.ob-home-sec { padding-block: clamp(4rem, 8vw, 110px); }
.ob { --w: 168px; --h: 224px; --t: 28px; }
.ob-face { position: absolute; inset: 0; overflow: hidden; border-radius: 1px 4px 4px 1px; transform: translateZ(calc(var(--t) / 2)); background: var(--back); }
.ob-face img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.16); }
.ob-face img.is-crop { transform: none; }
.ob-item .ob-stage { height: calc(var(--w) * 1.5 + 40px); place-items: end center; padding-bottom: 20px; }
.ob-face::after { content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(90deg, rgba(0, 0, 0, 0.32), rgba(0, 0, 0, 0) 5%, rgba(255, 255, 255, 0.14) 7%, rgba(0, 0, 0, 0) 13%, rgba(0, 0, 0, 0) 80%, rgba(255, 255, 255, 0.08)); }
.ob-book::after { background: var(--back); }
.ob-name { font-size: 1.2rem; }
.ob-ed { margin-top: 0.15rem; color: var(--g-muted); font-family: var(--display); font-size: 0.95rem; font-style: italic; line-height: 1.2; }
.ob-price { margin-top: 0.45rem; color: var(--g-text); font-family: var(--display); font-size: 1.2rem; font-weight: 700; font-variant-numeric: lining-nums tabular-nums; }
.ob-price--out { color: var(--rust-ink); font-family: var(--sans); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; }
[data-theme="dark"] .ob-price { color: var(--gold-light); }
[data-theme="dark"] .ob-price--out { color: #f3a08a; }
.ob-row--page { --n: 5; gap: 3rem 1rem; }
.ob-mark { min-width: 64px; }
.ob-rail { justify-content: flex-start; }
@media (max-width: 1100px) { .ob-row--page { --n: 4; } }
"""
YEAR_MARKS = dict(zip(YEARS, ["#1c3f7a", "#0f5560", "#2e2c33", "#6e1a1f", "#4b2458", "#3c3f46", "#0f5560"]))


def ob_ed(b):
    return f'<span class="ob-ed">{esc(b["edition"])}</span>' if b.get("edition") else ""


def ob_item(b):
    price = ('<span class="ob-price ob-price--out">Sold out</span>' if b.get("soldOut")
             else f'<span class="ob-price">{esc(b["price"])}</span>' if b.get("price") else "")
    back = f"color-mix(in oklab, {b['tint']} 70%, #120804)"
    if b.get("crop"):   # the tight crop, and the book drawn in its own proportions
        img = f'<img class="is-crop" src="{b["crop"]}" alt="" loading="lazy">'
        back += f";--h:calc(var(--w) * {min(1.5, max(1.15, b['crop_ar'])):.3f})"
    else:
        img = pic(b)
    return (f'<a class="ob-item" href="#" data-years="{esc("|".join(b["years"]))}" style="--back:{back}"><span class="ob-stage"><span class="ob-book">'
            f'<span class="ob-face">{img}</span></span></span>'
            f'<span class="ob-name">{esc(b["title"])}</span>{ob_ed(b)}'
            f'<span class="ob-sub">{esc(b.get("subject") or "")}{" · " if b.get("subject") else ""}{yrs(b)}</span>{price}</a>')


ob_home = f"""
<main id="main" class="r3-home">
  <hr class="section-rule">
  <section class="ob ob-home-sec" aria-labelledby="bs-h">
    <div class="r3-wrap ob-home">
      <div class="ob-head">
        <h2 id="bs-h">The <em>Bookstore</em></h2>
        <p>{COUNT} books for all seven years</p>
        <a class="ob-link" href="#">{esc(VISIT_LABEL)} {r2.LONG_ARROW}</a>
      </div>
      <div class="ob-row" style="--n:4">{"".join(ob_item(b) for b in HOME_C[:4])}</div>
    </div>
  </section>
  <hr class="section-rule">
</main>"""

ob_marks = f'<button class="ob-mark" type="button" data-f="" aria-pressed="true" style="--c:#3a2212">All<span>{COUNT}</span></button>' + "".join(
    f'<button class="ob-mark" type="button" data-f="{y}" aria-pressed="false" title="{y}" style="--c:{YEAR_MARKS[y]}">Year {ROMAN[y]}'
    f'<span>{sum(1 for b in BOOKS if y in b["years"])}</span></button>' for y in YEARS)
ob_page = f"""
<main id="main" class="r3-page">
  <section class="ob" aria-labelledby="bs-h">
    <div class="r3-wrap">
      <div class="ob-pagehead ob-head">
        <div><a class="ob-link" href="#" style="margin:0 0 1.4rem;flex-direction:row-reverse">Home <span style="display:inline-block;transform:scaleX(-1)">{r2.LONG_ARROW}</span></a>
        <h1 id="bs-h">The <em>Bookstore</em></h1><p>{esc(LEDE)}</p></div>
      </div>
      <div class="ob-rail" role="group" aria-label="Year">{ob_marks}</div>
      <div class="ob-row ob-row--page">{"".join(ob_item(b) for b in BOOKS)}</div>
    </div>
  </section>
</main>"""
OB_JS = """
<script>
  // The bookmarks filter the books by year.
  document.querySelectorAll(".ob-mark").forEach(function (m) {
    m.addEventListener("click", function () {
      var f = m.dataset.f;
      document.querySelectorAll(".ob-mark").forEach(function (x) { x.setAttribute("aria-pressed", String(x === m)); });
      document.querySelectorAll(".ob-item").forEach(function (b) { b.hidden = !!f && b.dataset.years.split("|").indexOf(f) < 0; });
    });
  });
</script>"""
BEST.append(("best-1-objects", "Objects"))
BUILDS.append(("best-1-objects", "Objects", "Round 2's 3D book objects, redone with the photographs.", CSS_11, ob_home, ob_page, OB_JS))

# ============================================================================
# 12. Bento, with photographs: round 3's option 1 redone on the real stock.
#     Tiles of different sizes in one grid, each washed in the colour measured
#     from its own cover; the photograph (zoomed past the grey table margin)
#     leans out of the tile's corner and straightens when pointed at. A large
#     tile for the lead book, one for the name and count, one for the years.
#     The page: every book, every seventh large, with year chips.
# ============================================================================
CSS_12 = r3.CSS_1 + """
.bn-tile .bn-pic { position: absolute; z-index: -1; right: -2%; bottom: -9%; width: 44%; aspect-ratio: 3 / 4; overflow: hidden; border-radius: 3px 6px 6px 3px;
  transform: rotate(9deg); box-shadow: -10px 16px 26px -10px rgba(20, 8, 2, 0.6); transition: transform 0.6s var(--ease-out); }
.bn-tile .bn-pic img { position: absolute; inset: 0; z-index: auto; width: 100%; height: 100%; object-fit: cover; border-radius: 0; box-shadow: none; transform: scale(1.16); transition: none; }
.bn-tile .bn-pic::after { content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0) 5%, rgba(255, 255, 255, 0.12) 7%, rgba(0, 0, 0, 0) 12%); }
a.bn-tile:hover .bn-pic, a.bn-tile:focus-visible .bn-pic { transform: rotate(2deg) translateY(-14px); }
a.bn-tile:hover img, a.bn-tile:focus-visible img { transform: scale(1.16); }
.bn-lead .bn-pic { right: 7%; bottom: 9%; width: 40%; transform: rotate(-5deg); box-shadow: -18px 30px 44px -14px rgba(0, 0, 0, 0.6); }
.bn-lead:hover .bn-pic { transform: rotate(0) translateY(-10px) scale(1.02); }
.bn-tile .bn-ed { max-width: 58%; margin-top: 0.3rem; font-family: var(--display); font-size: 0.95rem; font-style: italic; line-height: 1.15; opacity: 0.75; }
.bn-lead .bn-ed { max-width: 52%; font-size: 1.15rem; }
.bn-lead .bn-desc { max-width: 50%; margin-top: 1rem; font-family: var(--display); font-size: 1.15rem; line-height: 1.4; opacity: 0.9; }
.bn-yr { margin-top: 0.4rem; font-size: 0.66rem; font-weight: 500; letter-spacing: 0.1em; opacity: 0.7; }
.bn-price { margin-top: auto; }
.bn-title { font-size: 1.35rem; }
.bn-lead .bn-title { font-size: clamp(1.9rem, 1.3rem + 1.8vw, 2.8rem); }
@media (max-width: 560px) { .bn-lead .bn-desc { display: none; } }
"""


def bn_book(b, lead=False):
    cls = "bn-tile bn-lead" if lead else "bn-tile"
    flag = '<span class="bn-flag">Featured</span>' if lead and b.get("featured") else ""
    desc = f'<span class="bn-desc">{esc(b["description"])}</span>' if lead and b.get("description") else ""
    edn = f'<span class="bn-ed">{esc(b["edition"])}</span>' if b.get("edition") else ""
    price = f'<span class="bn-price">{esc(b["price"])}</span>' if b.get("price") else ""
    return (f'<a class="{cls}" href="#" style="--tone:{deep(b["tint"]) if lead else b["tint"]}" data-years="{esc("|".join(b["years"]))}">{flag}'
            f'<span class="bn-sub">{esc(b.get("subject") or "")}</span><span class="bn-title">{esc(b["title"])}</span>{edn}'
            f'<span class="bn-yr">{years_line(b)}</span>{desc}{price}<span class="bn-pic">{pic(b, tight=True)}</span></a>')


BN_YEARS = "".join(f'<a href="#">{y}<span>{sum(1 for b in BOOKS if y in b["years"])}</span></a>' for y in YEARS)
bn_home = f"""
<main id="main" class="r3-home">
  <hr class="section-rule">
  <section aria-labelledby="bs-h">
    <div class="r3-wrap bn-grid">
      {bn_book(HOME_C[0], True)}
      <div class="bn-tile bn-name">
        <h2 id="bs-h">The <em>Book</em>store</h2>
        <div class="bn-name__foot"><p class="bn-count"><b>{COUNT}</b> books</p><a class="bn-go" href="#">{esc(VISIT_LABEL)} {ARROW}</a></div>
      </div>
      {"".join(bn_book(b) for b in HOME_C[1:6])}
      <div class="bn-tile bn-cats"><p>Browse by year</p>{BN_YEARS}</div>
    </div>
  </section>
  <hr class="section-rule">
</main>"""
bn_page = f"""
<main id="main" class="r3-page">
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="bn-chips" role="group" aria-label="Year">
        <button type="button" aria-pressed="true" data-f="all">All<sup>{COUNT}</sup></button>
        {"".join(f'<button type="button" aria-pressed="false" data-f="{y}">{y}<sup>{sum(1 for b in BOOKS if y in b["years"])}</sup></button>' for y in YEARS)}
      </div>
      <div class="bn-grid">
        <div class="bn-tile bn-name">
          <h1 id="bs-h">The <em>Book</em>store</h1>
          <p class="bn-lede">{esc(LEDE)}</p>
          <div class="bn-name__foot"><p class="bn-count"><b>{COUNT}</b> books</p></div>
        </div>
        {"".join(bn_book(b, i % 7 == 0) for i, b in enumerate(BOOKS))}
      </div>
    </div>
  </section>
</main>"""
BN_JS = """
<script>
  // The chips thin the grid out by year; the dense flow closes the gaps.
  (function () {
    var chips = document.querySelectorAll(".bn-chips button");
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        chips.forEach(function (x) { x.setAttribute("aria-pressed", String(x === c)); });
        document.querySelectorAll(".bn-grid a.bn-tile").forEach(function (t) {
          t.hidden = c.dataset.f !== "all" && t.dataset.years.split("|").indexOf(c.dataset.f) < 0;
        });
      });
    });
  })();
</script>"""
BEST.append(("best-2-bento", "Bento"))
BUILDS.append(("best-2-bento", "Bento", "Round 3's bento grid, redone with the photographs and their colours.", CSS_12, bn_home, bn_page, BN_JS))

# ============================================================================
# 13. Accordion, with photographs: round 3's option 9 redone on the real
#     stock. The books stand as tall strips in the colour measured from their
#     covers, the name running up each; the open one widens to show the
#     photograph (zoomed past the grey margin), subject, title, edition, years
#     and price. Pointing at a strip or focusing it opens it; on phones the
#     strips lie down. The page is one row per year.
# ============================================================================
CSS_13 = r3.CSS_9 + """
.ac-pic { position: relative; width: clamp(150px, 15vw, 210px); aspect-ratio: 3 / 4; overflow: hidden; border-radius: 3px 6px 6px 3px; box-shadow: -14px 26px 40px -14px rgba(0, 0, 0, 0.6); }
.ac-pic img, .ac-strip__body .ac-pic img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; border-radius: 0; box-shadow: none; transform: scale(1.16); }
.ac-pic::after { content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0) 5%, rgba(255, 255, 255, 0.12) 7%, rgba(0, 0, 0, 0) 12%); }
.ac-strip__body i { display: block; margin-top: 0.4rem; font-family: var(--display); font-size: 1.15rem; opacity: 0.8; }
.ac-strip__body em { display: block; margin-top: 0.8rem; font-size: 0.66rem; font-style: normal; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; opacity: 0.75; }
.ac-strip__body b { margin-top: 0.9rem; }
.ac-strip__body b.out { border-color: #f3a08a; color: #ffd5c8; }
.r3-page .ac-strip { min-width: 46px; }
.r3-page .ac-strip__spine { font-size: 1.05rem; }
@media (max-width: 760px) { .ac-pic { width: 120px; } .r3-page .ac-strip { min-width: 0; } }
"""


def ac_strip(b, n, on=False):
    edn = f'<i>{esc(b["edition"])}</i>' if b.get("edition") else ""
    price = ('<b class="out">Sold out</b>' if b.get("soldOut") else f'<b>{esc(b["price"])}</b>' if b.get("price") else "")
    return (f'<a class="ac-strip{" on" if on else ""}" href="#" style="--tone:{deep(b["tint"])}"><span class="ac-strip__n">{n:02d}</span>'
            f'<span class="ac-strip__spine">{esc(b["title"])}</span>'
            f'<span class="ac-strip__body"><span class="ac-pic">{pic(b, tight=True)}</span><span><small>{esc(b.get("subject") or "")}</small>'
            f'<strong>{esc(b["title"])}</strong>{edn}<em>{years_line(b)}</em>{price}</span></span></a>')


ac_home = f"""
<main id="main" class="r3-home">
  <hr class="section-rule">
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <div class="ac-head"><div><h2 id="bs-h">Bookstore</h2></div><p>{COUNT} books &nbsp; <a href="#">{esc(VISIT_LABEL)} {ARROW}</a></p></div>
      <div class="ac">{"".join(ac_strip(b, i + 1, i == 0) for i, b in enumerate(HOME_C))}</div>
    </div>
  </section>
  <hr class="section-rule">
</main>"""
ac_rows = "".join(
    f'<section data-group="{y}"><h2 class="ac-cat">{y}<span>{len(bs)} books</span></h2><div class="ac">{"".join(ac_strip(b, k + 1, k == 0) for k, b in enumerate(bs))}</div></section>'
    for y in YEARS for bs in [[b for b in BOOKS if y in b["years"]]])
ac_page = f"""
<main id="main" class="r3-page">
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="ac-head"><div><h1 id="bs-h">Bookstore</h1><p class="ac-lede">{esc(LEDE)}</p></div></div>
      {ac_rows}
    </div>
  </section>
</main>"""
BEST.append(("best-3-accordion", "Accordion"))
BEST.append(("best-4-stage", "Colour stage"))   # round 6's option 2, written by generate_round6.py
BUILDS.append(("best-3-accordion", "Accordion", "Round 3's accordion strips, redone with the photographs and their colours.", CSS_13, ac_home, ac_page, r3.JS_9))


if __name__ == "__main__":
    for slug, name, blurb, css, h, p, js in BUILDS:
        (HERE / f"{slug}.html").write_text(page(f"{slug}.html", slug, name, blurb, css, h, js))
        (HERE / f"{slug}-page.html").write_text(page(f"{slug}-page.html", slug, name, blurb, css, p, js))
    print("wrote", len(BUILDS) * 2, "files")

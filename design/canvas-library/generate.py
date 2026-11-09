#!/usr/bin/env python3
"""The library: five mockups, each a home-page section and a full page.

The masjid wants to sell books on the site - for now only to show them:
a picture, the name and the price, with no buying online. Each option is two
files: N-name.html, the "Library" section of the home page showing a few
featured books with a way through to the rest, and N-name-page.html, the
library page itself with every book.

Every file loads the site's styles.css and the article canvas's mockup.css
(the switcher, the header's round buttons on the ground) and borrows that
canvas's header, menu and footer.

Content: there is no stock list yet. The titles are books the curriculum
teaches (content/curriculum.json), standing in for real stock; the prices
are $00.00 and the page's lede is TODO, at the shape of real ones. No book
has a photograph, so each wears its binding drawn face-on - the folio's
drawnCover, ported from curriculum.js - where a photograph will go.

Edit this file, not the output:  python3 generate.py
"""
import importlib.util
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).parent

_spec = importlib.util.spec_from_file_location("article", HERE.parent / "canvas-article" / "generate.py")
art = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(art)

ARROW = art.ARROW
PAGE = ' aria-current="page"'
PRICE = "$00.00"
LEDE = "TODO: A line about the library: what it stocks, and where and when the books can be bought."

# ---------------------------------------------------------------------------
# The stand-in stock: (title, subject, shelf, binding). The first six are the
# featured books. Shelves group subjects for the options that group.
# ---------------------------------------------------------------------------
BOOKS = [
    ("Tashīl al-Naḥw", "Nahw", "Arabic", "petrol"),
    ("Riyāḍ al-Ṣāliḥīn", "Hadith", "Hadith", "aubergine"),
    ("Tafsīr al-Jalālayn", "Tafseer", "Qur'an", "ink"),
    ("Durūs al-Lugha 1", "Arabic", "Arabic", "lapis"),
    ("Al-ʿAqīda al-Ṭaḥāwiyya", "Aqidah", "Aqidah & Sira", "oxblood"),
    ("Qaṣaṣ al-Nabiyyīn 1", "Arabic", "Arabic", "slate"),
    ("Tashīl al-Ṣarf", "Sarf", "Arabic", "petrol"),
    ("Durūs al-Balāgha", "Balagha", "Arabic", "aubergine"),
    ("Achchhī Bāteṉ", "Urdu", "Arabic", "oxblood"),
    ("Mishkāt al-Maṣābīḥ", "Hadith", "Hadith", "ink"),
    ("Ṣaḥīḥ al-Bukhārī", "Hadith", "Hadith", "petrol"),
    ("Shamāʾil al-Tirmidhī", "Hadith", "Hadith", "lapis"),
    ("Al-Fawz al-Kabīr", "Usul Tafsir", "Qur'an", "slate"),
    ("Al-Muqaddima al-Jazariyya", "Tajwid", "Qur'an", "lapis"),
    ("Al-Hidāya", "Fiqh", "Fiqh", "aubergine"),
    ("Uṣūl al-Shāshī", "Usul Fiqh", "Fiqh", "petrol"),
    ("Muʿīn al-Farāʾiḍ", "Mirath", "Fiqh", "ink"),
    ("Nūr al-Yaqīn", "Sira", "Aqidah & Sira", "lapis"),
]
FEATURED = BOOKS[:6]
SHELVES = ["Arabic", "Qur'an", "Hadith", "Fiqh", "Aqidah & Sira"]


def shelf(name):
    return [b for b in BOOKS if b[2] == name]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


# ---------------------------------------------------------------------------
# drawnCover, ported from assets/js/curriculum.js: the spine's binding laid
# out face-on at 300x400 - braid, panel, pendant, cartouche, lozenge.
# ---------------------------------------------------------------------------
METALS = {
    "gold":   {"line": "#d9aa48", "grad": ["#f7e2a2", "#d9aa48", "#a9792a", "#e8c778"], "ink": "#f4dfa2"},
    "silver": {"line": "#b8c0c7", "grad": ["#f5f7f9", "#c4cbd1", "#848d95", "#dfe4e8"], "ink": "#eef1f4"},
    "copper": {"line": "#c98a5c", "grad": ["#f6d6ba", "#cc8c5c", "#8a5230", "#e5b08a"], "ink": "#f5dac4"},
}
BINDINGS = {
    "lapis":     ("gold", [["#07142b", "#1c3f7a"], ["#0a1a36", "#23498a"], ["#050f22", "#18376c"]]),
    "ink":       ("gold", [["#0b0b0d", "#2a2a30"], ["#111013", "#34303a"], ["#08090b", "#23262c"]]),
    "petrol":    ("gold", [["#03191d", "#0f5560"], ["#04222a", "#136170"], ["#021417", "#0c4a54"]]),
    "oxblood":   ("gold", [["#2a0709", "#6e1a1f"], ["#330a0d", "#7a2126"], ["#240507", "#611619"]]),
    "aubergine": ("gold", [["#1c0b22", "#4b2458"], ["#230d2a", "#582a66"], ["#16081b", "#40204c"]]),
    "slate":     ("copper", [["#14181d", "#39434e"], ["#181c20", "#434c55"], ["#101418", "#313a44"]]),
}


def num(n):
    return f"{round(n * 100) / 100:g}"


def dot(x, y, r, fill):
    return f'<circle cx="{num(x)}" cy="{num(y)}" r="{r}" fill="{fill}"/>'


def ogee(x0, x1, yt, yb, e):
    cx = (x0 + x1) / 2
    k = (x1 - cx) * 0.18
    n = num
    return (f"M{n(cx)} {n(yt)} C{n(cx + k)} {n(yt + e * .55)} {n(x1)} {n(yt + e * .3)} {n(x1)} {n(yt + e)}"
            f" L{n(x1)} {n(yb - e)} C{n(x1)} {n(yb - e * .3)} {n(cx + k)} {n(yb - e * .55)} {n(cx)} {n(yb)}"
            f" C{n(cx - k)} {n(yb - e * .55)} {n(x0)} {n(yb - e * .3)} {n(x0)} {n(yb - e)}"
            f" L{n(x0)} {n(yt + e)} C{n(x0)} {n(yt + e * .3)} {n(cx - k)} {n(yt + e * .55)} {n(cx)} {n(yt)} Z")


def drawn_cover(title, binding, i):
    metal_name, shades = BINDINGS[binding]
    m = METALS[metal_name]
    edge, panel = shades[i % len(shades)]
    G, g = m["line"], m["grad"]
    lines, line = [], ""
    for word in title.split():
        if line and len(line + " " + word) > 10:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        lines.append(line)
    lines = lines[:3]
    size = 20 if len(lines) > 2 else 23
    lead = size + 5
    top = 205 - (len(lines) - 1) * lead / 2 + size * .35
    text = "".join(
        f'<text x="150" y="{num(top + n * lead)}" text-anchor="middle" fill="{m["ink"]}" '
        f'font-family="Georgia, serif" font-size="{size}" font-weight="600">{esc(l)}</text>'
        for n, l in enumerate(lines))
    cx, y = 0, 18
    pend = (f'<line x1="0" y1="{y - 5.5}" x2="0" y2="{y}" stroke="{G}" stroke-width=".8"/>' + dot(0, y - 3.5, 1.3, "url(#gv)") +
            f'<path d="M0 {y}C7 {y + 6} 7 {y + 13} 0 {y + 18.5}C-7 {y + 13} -7 {y + 6} 0 {y}Z" fill="url(#gv)"/>'
            f'<path d="M0 {y + 5.5}C3.2 {y + 8.5} 3.2 {y + 12} 0 {y + 14.5}C-3.2 {y + 12} -3.2 {y + 8.5} 0 {y + 5.5}Z" fill="{edge}"/>'
            + dot(0, y + 10.3, .9, "url(#gv)"))
    cart = (f'<path d="{ogee(82, 218, 104, 306, 30)}" fill="{edge}" stroke="url(#gv)" stroke-width="1.3"/>'
            f'<path d="{ogee(84.6, 215.4, 107.6, 302.4, 28)}" fill="none" stroke="{G}" stroke-width=".55" opacity=".75"/>'
            + dot(150, 101.4, 1.3, "url(#gv)") + dot(150, 308.6, 1.3, "url(#gv)"))
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" width="300" height="400"><defs>'
        f'<linearGradient id="gv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{g[0]}"/><stop offset=".45" stop-color="{g[1]}"/>'
        f'<stop offset=".8" stop-color="{g[2]}"/><stop offset="1" stop-color="{g[3]}"/></linearGradient></defs>'
        '<filter id="n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" stitchTiles="stitch"/>'
        '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.5 0 0 0 -0.22"/></filter>'
        '<linearGradient id="l" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-opacity="0.4"/><stop offset="0.16" stop-opacity="0.04"/>'
        '<stop offset="0.5" stop-color="#fff" stop-opacity="0.07"/><stop offset="1" stop-opacity="0.28"/></linearGradient>'
        f'<pattern id="b" width="8" height="14" patternUnits="userSpaceOnUse" y="12"><path d="M1.2 0C6.8 3.5 6.8 10.5 1.2 14M6.8 0C1.2 3.5 1.2 10.5 6.8 14" stroke="{G}" stroke-width="1.3" fill="none"/></pattern>'
        f'<rect width="300" height="400" fill="{edge}"/>'
        f'<rect x="12" y="12" width="276" height="376" fill="none" stroke="{G}" stroke-width="1.8"/>'
        '<rect x="17" y="16" width="8" height="368" fill="url(#b)"/><rect x="275" y="16" width="8" height="368" fill="url(#b)"/>'
        f'<rect x="31" y="20" width="238" height="360" fill="{panel}" fill-opacity=".55" stroke="{G}"/>'
        f'<g transform="translate(150 0) scale(2.2)">{pend}</g>' + cart +
        '<g transform="translate(150 326) scale(2.2)"><path d="M0 0L3.5 4L0 8L-3.5 4Z" fill="url(#gv)"/></g>' + text +
        '<rect width="300" height="400" filter="url(#n)"/><rect width="300" height="400" fill="url(#l)"/></svg>')
    return "data:image/svg+xml," + quote(svg, safe="")


COVERS = {b[0]: drawn_cover(b[0], b[3], i) for i, b in enumerate(BOOKS)}


def cover(book, cls="cover"):
    """The book's picture: a photograph later, its drawn binding now."""
    return f'<img class="{cls}" src="{COVERS[book[0]]}" width="300" height="400" alt="" loading="lazy">'


# ---------------------------------------------------------------------------
# The page shell and the switcher (option number, Home | Page, Light | Dark).
# ---------------------------------------------------------------------------
OPTIONS = [
    ("1-shelf", "Face-out shelf"),
    ("2-cards", "Cream cards"),
    ("3-spotlight", "Spotlight"),
    ("4-niches", "Mihrab niches"),
    ("5-catalogue", "Catalogue leaf"),
]


def switcher(slug, is_page):
    links = "".join(
        f'<a href="{s}{"-page" if is_page else ""}.html" title="{n}"{PAGE if s == slug else ""}>{i + 1}</a>'
        for i, (s, n) in enumerate(OPTIONS))
    return f"""
<nav class="m-switch" aria-label="Mockups">
  <a href="1-shelf{"-page" if is_page else ""}.html"{PAGE}>Round 1</a><a href="r2-1-window{"-page" if is_page else ""}.html">Round 2</a><a href="r3-01-bento{"-page" if is_page else ""}.html">Round 3</a><a href="r4-01-hashiya{"-page" if is_page else ""}.html">Round 4</a><i></i>{links}<i></i>
  <a href="{slug}.html"{"" if is_page else PAGE}>Home</a><a href="{slug}-page.html"{PAGE if is_page else ""}>Page</a><i></i>
  <button type="button" data-set-theme="light">Light</button>
  <button type="button" data-set-theme="dark">Dark</button>
</nav>"""


VISIT = f'<a class="btn btn--gold" href="#">Visit the Library {ARROW}</a>'
BACK = f'<a class="back" href="#">{ARROW} Home</a>'


def section_head(heading="Library", hid="library-heading", lede=False, back=False):
    return f"""
      <div class="section__head">
        {BACK if back else ""}
        <h2 class="section__heading" id="{hid}">{heading}</h2>
        {f'<p class="section__lede">{LEDE}</p>' if lede else ""}
      </div>"""


def home(main):
    """The home page's section, between the rules it would sit between."""
    return f"""
<main id="main" class="lib-home">
  <hr class="section-rule">
  <section class="section" id="library" aria-labelledby="library-heading">
    <div class="wrap">{section_head()}
{main.rstrip()}
    </div>
  </section>
  <hr class="section-rule">
</main>"""


SHARED_CSS = """
/* The home section stands alone here, as if between Teachers and Articles. */
.lib-home { padding-top: 110px; }
.lib-page { padding-top: 130px; }
.section__head .back { margin-bottom: 1.4rem; }
.lib-foot { margin-top: clamp(2.2rem, 4vw, 3rem); text-align: center; }

/* A book's picture: the cover with a page edge and a soft shadow, so a flat
   photograph reads as a book. */
.cover {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 3 / 4;
  object-fit: cover;
  border-radius: 2px 5px 5px 2px;
  box-shadow: 1px 0 0 rgba(255, 255, 255, 0.25) inset, 0 18px 28px -14px rgba(30, 12, 2, 0.75), 0 2px 4px rgba(30, 12, 2, 0.35);
}

/* The name and the price, the two things every option shows. */
.b-subject { color: var(--g-accent); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.b-title { color: var(--g-text); font-family: var(--display); font-size: 1.3rem; font-weight: 600; line-height: 1.15; }
.b-price { color: var(--rust-ink); font-family: var(--display); font-size: 1.35rem; font-weight: 700; font-variant-numeric: lining-nums tabular-nums; letter-spacing: 0.02em; }
[data-theme="dark"] .b-price { color: var(--gold-light); }

/* A row of subject filters, the Articles switch's look. */
.filters { display: flex; justify-content: center; margin: 0 0 clamp(2rem, 4vw, 3rem); }
.filters .seg { flex-wrap: wrap; justify-content: center; border-radius: 26px; }
[data-theme="dark"] .seg { border-color: var(--g-line); background: var(--g-card); box-shadow: none; }
[data-theme="dark"] .seg__btn { color: var(--g-muted); }
[data-theme="dark"] .seg__btn[aria-pressed="true"] { color: var(--espresso); }
[hidden] { display: none !important; }
"""

FILTER_JS = """
<script>
  // The subject filter: shows the books of one shelf, or all.
  document.querySelectorAll("[data-filter]").forEach(function (b) {
    b.addEventListener("click", function () {
      var f = b.getAttribute("data-filter");
      document.querySelectorAll("[data-filter]").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      document.querySelectorAll("[data-shelf]").forEach(function (el) {
        el.hidden = f !== "all" && el.getAttribute("data-shelf") !== f;
      });
    });
  });
</script>"""


def filters():
    btns = '<button class="seg__btn" type="button" data-filter="all" aria-pressed="true">All</button>' + "".join(
        f'<button class="seg__btn" type="button" data-filter="{esc(s)}" aria-pressed="false">{esc(s)}</button>' for s in SHELVES)
    return f'<div class="filters"><div class="seg" role="group" aria-label="Subject">{btns}</div></div>'


def page(fname, slug, name, blurb, css, main, body_class="on-ground", extra=""):
    is_page = fname.endswith("-page.html")
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Library · {name}{" · page" if is_page else ""}</title>
  <meta name="color-scheme" content="light dark">
  <script>
    (function () {{
      var t = null;
      try {{ t = localStorage.getItem("alimiyyah.theme"); }} catch (e) {{}}
      if (t !== "light" && t !== "dark") {{
        t = window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }}
      document.documentElement.setAttribute("data-theme", t);
    }})();
  </script>
  <link rel="icon" href="../../assets/img/logo_gold_web.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Gilda+Display&family=Instrument+Sans:wght@400;500;600&family=Amiri:wght@400;700&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../assets/css/styles.css?v=59">
  <link rel="stylesheet" href="../canvas-article/mockup.css">
<!-- Option {slug}: {name}. {blurb} -->
<style>
{SHARED_CSS.strip()}

{css.strip()}
</style>
</head>
<body id="top" class="{body_class}">
{art.HEADER}
{main.rstrip()}
{art.FOOTER}
{switcher(slug, is_page)}
{art.SCRIPTS}
{extra}
</body>
</html>
"""


# ============================================================================
# 1. Face-out shelf: the curriculum's bay - wood frame, dark well, glowing
#    plank - with the books standing face-out on it, as a shop shelves its
#    best books. The name and price are lettered on the wood beneath each.
#    The page is a bay per shelf of subjects.
# ============================================================================
CSS_1 = """
.fo { padding: 12px 12px 0; }
.fo .bay__well {
  height: auto;
  min-height: 0;
  align-items: flex-end;
  gap: clamp(14px, 2.4vw, 34px);
  padding: 46px clamp(18px, 3vw, 40px) 0;
  overflow-x: auto;
  scrollbar-width: thin;
}
.fo__book { flex: none; width: 138px; transition: transform 0.4s var(--ease-out); }
.fo__book:hover { transform: translateY(-8px); }
.fo__book .cover { box-shadow: 0 1px 0 rgba(255,255,255,.2) inset, 0 14px 20px -8px rgba(0,0,0,.8), 0 0 0 1px rgba(0,0,0,.3); }
.fo__labels {
  display: flex;
  justify-content: center;
  justify-content: safe center;
  gap: clamp(14px, 2.4vw, 34px);
  padding: 16px clamp(18px, 3vw, 40px) 22px;
  overflow: hidden;
}
.fo__label { flex: none; display: flex; flex-direction: column; justify-content: space-between; width: 138px; text-align: center; }
.fo__label .b-title { color: #fbeedd; font-size: 1.05rem; text-shadow: 0 1px 2px rgba(40, 18, 4, 0.5); }
.fo__label .b-price { margin-top: 0.3rem; color: var(--gold-pale); font-size: 1.15rem; text-shadow: 0 1px 2px rgba(40, 18, 4, 0.6); }
.fo .bay__year { height: auto; padding-bottom: 18px; }

/* The well and the labels scroll together on narrow screens: one strip. */
.fo__strip { overflow-x: auto; scrollbar-width: thin; }
.fo__strip .bay__well, .fo__strip .fo__labels { width: max-content; min-width: 100%; overflow: visible; }

.fo-page { display: grid; gap: clamp(1.6rem, 3vw, 2.4rem); }
@media (max-width: 640px) { .fo__book, .fo__label { width: 112px; } .fo__label .b-title { font-size: 0.95rem; } }
"""


def bay(books, year=None):
    tiles = "".join(f'<a class="fo__book" href="#" aria-label="{esc(b[0])}, {PRICE}">{cover(b)}</a>' for b in books)
    labels = "".join(
        f'<div class="fo__label"><p class="b-title">{esc(b[0])}</p><p class="b-price">{PRICE}</p></div>' for b in books)
    yr = f'<p class="bay__year">{esc(year)}</p>' if year else ""
    return f"""
      <div class="bay fo">
        <div class="fo__strip">
          <div class="bay__well">{tiles}</div>
          <div class="bay__plank"></div>
          <div class="fo__labels">{labels}</div>
        </div>{yr}
      </div>"""


HOME_1 = bay(FEATURED) + f'\n      <p class="lib-foot">{VISIT}</p>'
PAGE_1 = f"""
<main id="main" class="lib-page">
  <section class="section" aria-labelledby="library-heading">
    <div class="wrap">{section_head("Library", lede=True, back=True)}
      <div class="fo-page">{"".join(bay(shelf(s), s) for s in SHELVES)}
      </div>
    </div>
  </section>
</main>"""

# ============================================================================
# 2. Cream cards: each book a card cut like the teachers' - cream in a double
#    gold frame (a board tile in dark) - the cover standing in it, then the
#    subject, the name and the price. Four across. The page adds a subject
#    filter in the Articles switch's look.
# ============================================================================
CSS_2 = """
.cards { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1.4rem; }
.card-b {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 1.8rem 1.5rem 1.4rem;
  border-radius: 18px;
  background: linear-gradient(160deg, #fffaf0, #f3e2c3);
  box-shadow:
    inset 0 0 0 1px var(--gold),
    inset 0 0 0 5px #fbf3e2,
    inset 0 0 0 6px rgba(201, 164, 87, 0.8),
    0 24px 40px -24px rgba(40, 18, 4, 0.7);
  color: inherit;
  text-decoration: none;
  transition: transform 0.4s var(--ease-out);
}
.card-b:hover { transform: translateY(-5px); }
.card-b .cover { width: 72%; margin: 0 auto 1.4rem; }
.card-b .b-subject { color: #7d5006; }
.card-b .b-title { margin-top: 0.4rem; color: var(--brown-ink); }
.card-b__foot {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 0.9rem;
  border-top: 1px solid rgba(154, 101, 8, 0.3);
}
.card-b__body { margin-bottom: 1rem; }
.card-b__foot > span:first-child { color: rgba(70, 44, 22, 0.7); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.24em; text-transform: uppercase; }

[data-theme="dark"] .card-b {
  border: 1px solid var(--g-line);
  background:
    radial-gradient(120% 90% at 20% 10%, rgba(238, 194, 90, 0.18), transparent 60%),
    linear-gradient(180deg, transparent 55%, rgba(20, 9, 2, 0.45)),
    linear-gradient(155deg, var(--board), var(--board-deep));
  box-shadow: 0 30px 50px -30px rgba(0, 0, 0, 0.9);
}
[data-theme="dark"] .card-b .b-subject { color: var(--gold); }
[data-theme="dark"] .card-b .b-title { color: #fff6ea; }
[data-theme="dark"] .card-b__foot { border-top-color: var(--g-line); }
[data-theme="dark"] .card-b__foot > span:first-child { color: var(--g-muted); }

@media (max-width: 1040px) { .cards { grid-template-columns: repeat(3, minmax(0, 1fr)); } .lib-home .cards > :nth-child(4) { display: none; } }
@media (max-width: 760px)  { .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; } .lib-home .cards > :nth-child(4) { display: flex; } .card-b { padding: 1.4rem 1.1rem 1.1rem; } .card-b .b-title { font-size: 1.15rem; } }
@media (max-width: 420px)  { .card-b .cover { width: 86%; } }
"""


def card(b):
    return (f'<a class="card-b" href="#" data-shelf="{esc(b[2])}">{cover(b)}'
            f'<div class="card-b__body"><p class="b-subject">{esc(b[1])}</p><h3 class="b-title">{esc(b[0])}</h3></div>'
            f'<div class="card-b__foot"><span>Price</span><span class="b-price">{PRICE}</span></div></a>')


HOME_2 = f"""
      <div class="cards">{"".join(card(b) for b in FEATURED[:4])}</div>
      <p class="lib-foot">{VISIT}</p>"""
PAGE_2 = f"""
<main id="main" class="lib-page">
  <section class="section" aria-labelledby="library-heading">
    <div class="wrap">{section_head("Library", lede=True, back=True)}
      {filters()}
      <div class="cards">{"".join(card(b) for b in BOOKS)}</div>
    </div>
  </section>
</main>"""

# ============================================================================
# 3. Spotlight: the Articles pattern. One book featured large - its cover on
#    the rust board, beside it the subject, the name and the price - and the
#    rest in the site's carousel of board cards beneath; a card features its
#    book. The page opens on the article page's banner and sets the books out
#    under a heading per shelf, as board cards.
# ============================================================================
CSS_3 = """
.spot {
  display: grid;
  grid-template-columns: minmax(0, 340px) minmax(0, 1fr);
  gap: clamp(1.6rem, 4vw, 4rem);
  align-items: center;
  max-width: 980px;
  margin: 0 auto clamp(2rem, 4vw, 3rem);
}
.spot__art {
  display: grid;
  place-items: center;
  padding: 2.6rem 3.4rem;
  border-radius: var(--radius);
  border: 1px solid rgba(189, 93, 15, 0.6);
  box-shadow: 0 30px 50px -28px rgba(50, 22, 4, 0.8);
}
.spot__art .cover { max-width: 230px; }
.spot__title { margin: 1rem 0 0.8rem; color: var(--g-text); font-family: var(--display); font-size: clamp(2.2rem, 1.6rem + 1.8vw, 3.4rem); font-weight: 600; line-height: 1.05; }
.spot__price { display: flex; align-items: baseline; gap: 0.8rem; margin-bottom: 1.8rem; }
.spot__price .b-price { font-size: 2.2rem; }
.spot__price small { color: var(--g-muted); font-size: 0.62rem; font-weight: 600; letter-spacing: 0.26em; text-transform: uppercase; }
.spot .chip { color: var(--g-accent); font-size: 0.62rem; font-weight: 600; letter-spacing: 0.26em; text-transform: uppercase; }

/* The carousel's cards: board, cover beside the name and price. */
.bk {
  position: relative;
  display: grid;
  grid-template-columns: 74px minmax(0, 1fr);
  gap: 1rem;
  align-items: center;
  width: 100%;
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid rgba(189, 93, 15, 0.6);
  color: #fbeedd;
  text-align: left;
  text-decoration: none;
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s;
}
.bk:hover { transform: translateY(-4px); }
.bk[aria-current="true"] { box-shadow: 0 0 0 2px var(--gold-light), 0 18px 30px -18px rgba(50, 22, 4, 0.8); }
.bk .cover { box-shadow: 0 10px 16px -8px rgba(0, 0, 0, 0.8); }
.bk .b-subject { color: var(--gold); font-size: 0.56rem; }
.bk .b-title { margin: 0.3rem 0 0.35rem; color: #fff6ea; font-size: 1.12rem; }
.bk .b-price { color: var(--gold-pale); font-size: 1.15rem; }
[data-theme="dark"] .bk { border-color: var(--g-line); }

.shelf-h {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin: clamp(2.4rem, 5vw, 3.6rem) 0 1.2rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--g-line);
}
.shelf-h h2 { color: var(--g-text); font-family: var(--title); font-size: clamp(1.4rem, 1.1rem + 1vw, 2rem); font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase; }
.shelf-h span { margin-left: auto; color: var(--g-muted); font-size: 0.62rem; font-weight: 600; letter-spacing: 0.26em; text-transform: uppercase; }
.bks { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.1rem; }
.a-hero .section__lede { color: rgba(255, 246, 234, 0.85); }

@media (max-width: 1000px) { .bks { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 760px) {
  .spot { grid-template-columns: minmax(0, 1fr); text-align: center; }
  .spot__art { padding: 2rem; }
  .spot__price { justify-content: center; }
}
@media (max-width: 600px) { .bks { grid-template-columns: minmax(0, 1fr); } }
"""


def bk(b, j, tag="a"):
    href = ' href="#"' if tag == "a" else ' type="button"'
    return (f'<{tag} class="bk board{" board--rust" if j % 2 else ""}"{href}>{cover(b)}'
            f'<span><span class="b-subject">{esc(b[1])}</span><span class="b-title" style="display:block">{esc(b[0])}</span>'
            f'<span class="b-price">{PRICE}</span></span></{tag}>')


def spot_main(b):
    return f"""
      <div class="spot">
        <div class="spot__art board board--rust">{cover(b)}</div>
        <div class="spot__text">
          <span class="chip" data-s="subject">{esc(b[1])}</span>
          <h3 class="spot__title" data-s="title">{esc(b[0])}</h3>
          <p class="spot__price"><small>Price</small><span class="b-price">{PRICE}</span></p>
          {VISIT}
        </div>
      </div>"""


import json
SPOT_DATA = json.dumps([{"t": b[0], "s": b[1], "c": COVERS[b[0]], "j": i} for i, b in enumerate(FEATURED)])

HOME_3 = spot_main(FEATURED[0]) + """
      <div class="spot-list"></div>"""

SPOT_JS = """
<script src="../../assets/js/carousel.js?v=5"></script>
<script>
  // The featured books in the site's carousel; a card features its book.
  (function () {
    var books = %s, PRICE = "%s";
    var mount = document.querySelector(".spot-list");
    var spot = document.querySelector(".spot");
    function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); }
    function feature(b) {
      spot.querySelector(".cover").src = b.c;
      spot.querySelector('[data-s="title"]').textContent = b.t;
      spot.querySelector('[data-s="subject"]').textContent = b.s;
      mount.querySelectorAll(".bk").forEach(function (x, i) { x.setAttribute("aria-current", String(i === b.j)); });
    }
    createCarousel({
      mount: mount, items: books, label: "Featured books",
      perView: function () { var w = window.innerWidth; return w < 600 ? 1 : w < 1000 ? 2 : 3; },
      render: function (b, j) {
        var el = document.createElement("button");
        el.type = "button";
        el.className = "bk board" + (j %% 2 ? " board--rust" : "");
        el.setAttribute("aria-current", String(j === 0));
        el.innerHTML = '<img class="cover" src="' + b.c + '" width="300" height="400" alt="">' +
          '<span><span class="b-subject">' + esc(b.s) + '</span><span class="b-title" style="display:block">' + esc(b.t) +
          '</span><span class="b-price">' + PRICE + "</span></span>";
        el.addEventListener("click", function () { feature(b); });
        return el;
      }
    });
  })();
</script>""" % (SPOT_DATA, PRICE)

PAGE_3 = f"""
<main id="main">
  <section class="hero a-hero" aria-labelledby="library-heading">
    <div class="hero__img" aria-hidden="true"></div>
    <div class="wrap hero__body">
      <p class="in">{BACK}</p>
      <h1 class="hero__title in" id="library-heading">Library</h1>
      <p class="section__lede in">{LEDE}</p>
    </div>
  </section>
  <section class="section" style="padding-top: clamp(1.5rem, 3vw, 2.5rem)" aria-label="Books">
    <div class="wrap">
      {"".join(f'<div class="shelf-h"><h2>{esc(s)}</h2><span>{len(shelf(s))} books</span></div><div class="bks">' + "".join(bk(b, j) for j, b in enumerate(shelf(s))) + "</div>" for s in SHELVES)}
    </div>
  </section>
</main>"""

# ============================================================================
# 4. Mihrab niches: each book stands in one of the Alumni section's niches -
#    moulding, dark recess, sill - lit from below, its name and price
#    beneath it in the recess. Three to a page in the site's carousel at
#    home; a grid of niches, four across, with the subject filter on the page.
# ============================================================================
CSS_4 = """
.nb .niche-slot { height: 470px; }
.nb .niche__recess { justify-content: flex-end; padding-bottom: 1.5rem; color: #fbeedd; }
.nb .cover { width: min(62%, 170px); margin: 0 auto 1.4rem; box-shadow: 0 0 0 1px rgba(0,0,0,.4), 0 22px 30px -12px rgba(0,0,0,.9), 0 0 60px -10px rgba(255, 206, 130, 0.25); }
.nb .b-subject { color: var(--gold); font-size: 0.56rem; }
.nb .b-title { margin: 0.35rem 0 0.5rem; color: #fff6ea; font-size: 1.2rem; }
.nb .b-price { color: var(--gold-light); font-size: 1.3rem; }
.nb a { color: inherit; text-decoration: none; }
.nb a::after { content: ""; position: absolute; inset: 0; }
.nb .niche-slot { position: relative; transition: transform 0.4s var(--ease-out); }
.nb .niche-slot:hover { transform: translateY(-6px); }
.nb-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1.6rem 1.4rem; }
.nb-grid .niche-slot { height: 430px; }
@media (max-width: 1100px) { .nb-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 800px)  { .nb-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .nb .niche__recess { padding-inline: 0.9rem; } .nb .b-title { font-size: 1.05rem; } }
@media (max-width: 480px)  { .nb-grid { grid-template-columns: minmax(0, 1fr); } .nb-grid .niche-slot { height: 440px; width: min(100%, 300px); margin-inline: auto; } }
"""


def niche(b):
    return (f'<figure class="niche-slot" data-shelf="{esc(b[2])}"><div class="niche"><div class="niche__recess">{cover(b)}'
            f'<p class="b-subject">{esc(b[1])}</p><h3 class="b-title"><a href="#">{esc(b[0])}</a></h3>'
            f'<p class="b-price">{PRICE}</p></div></div><div class="niche__sill"></div></figure>')


NICHE_DATA = json.dumps([niche(b) for b in FEATURED])
HOME_4 = f"""
      <div class="nb nb-list"></div>
      <p class="lib-foot">{VISIT}</p>"""
NICHE_JS = """
<script src="../../assets/js/carousel.js?v=5"></script>
<script>
  // The featured books' niches, three to a page, as Alumni pages its niches.
  (function () {
    var html = %s;
    createCarousel({
      mount: document.querySelector(".nb-list"), items: html, label: "Featured books",
      perView: function () { var w = window.innerWidth; return w < 700 ? 1 : w < 1040 ? 2 : 3; },
      render: function (h) { var d = document.createElement("div"); d.innerHTML = h; d.style.height = "100%%"; return d.firstChild; }
    });
  })();
</script>""" % NICHE_DATA

PAGE_4 = f"""
<main id="main" class="lib-page">
  <section class="section" aria-labelledby="library-heading">
    <div class="wrap">{section_head("Library", lede=True, back=True)}
      {filters()}
      <div class="nb nb-grid">{"".join(niche(b) for b in BOOKS)}</div>
    </div>
  </section>
</main>"""

# ============================================================================
# 5. Catalogue leaf: the folio's jadwal - an aged leaf ruled in gold, ink
#    and red - as a bookseller's price list. At home, three featured covers
#    fanned on the left and the six featured books listed on the leaf, the
#    name, a dotted leader and the price. The page is the whole catalogue,
#    a heading per shelf in red, each entry with a small cover.
# ============================================================================
CSS_5 = """
.leaf {
  position: relative;
  padding: clamp(1.8rem, 4vw, 3rem) clamp(1.4rem, 4vw, 3.2rem);
  border-radius: 6px;
  background: linear-gradient(170deg, #fdf6e7, #f4e6c8);
  box-shadow:
    inset 0 0 0 10px #fdf6e7,
    inset 0 0 0 11px #b8862c,
    inset 0 0 0 14px #fdf6e7,
    inset 0 0 0 15px #a8321e,
    0 30px 50px -30px rgba(50, 22, 4, 0.8);
  color: #3a2410;
}
.leaf__head { margin-bottom: 1.2rem; color: #a8321e; font-family: var(--display); font-size: 1.05rem; font-style: italic; text-align: center; }
.entries { list-style: none; margin: 0; padding: 0; }
.entry { display: grid; grid-template-columns: auto minmax(0, auto) 1fr auto; align-items: end; gap: 0.7rem; padding: 0.75rem 0; border-bottom: 1px solid rgba(184, 134, 44, 0.35); }
.entry:last-child { border-bottom: 0; }
.entry__n { padding-bottom: 0.2rem; color: #a8321e; font-family: var(--display); font-size: 1rem; font-weight: 700; font-variant-numeric: lining-nums; }
.entry__t { color: #2c1a0a; font-family: var(--display); font-size: 1.3rem; font-weight: 600; line-height: 1.2; }
.entry__t small { display: block; color: #7d5006; font-family: var(--sans); font-size: 0.56rem; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; }
.entry__lead { margin-bottom: 0.45rem; border-bottom: 2px dotted rgba(58, 36, 16, 0.4); }
.entry .b-price { color: #2c1a0a; }
.entry a { color: inherit; text-decoration: none; }
.entry a:hover { text-decoration: underline; text-decoration-color: #b8862c; text-underline-offset: 4px; }

.cat-home { display: grid; grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr); gap: clamp(2rem, 5vw, 4.5rem); align-items: center; max-width: 1060px; margin: 0 auto; }
.fan { position: relative; height: 380px; }
.fan .cover { position: absolute; top: 50%; left: 50%; width: 200px; }
.fan .cover:nth-child(1) { transform: translate(-108%, -48%) rotate(-9deg); }
.fan .cover:nth-child(2) { transform: translate(8%, -48%) rotate(8deg); }
.fan .cover:nth-child(3) { z-index: 1; transform: translate(-50%, -54%); }

/* The page: the entries with a small cover each, two columns. */
.cat-page .entry { grid-template-columns: 54px minmax(0, auto) 1fr auto; align-items: center; }
.cat-page .entry .cover { width: 54px; box-shadow: 0 6px 10px -5px rgba(30, 12, 2, 0.7); }
.cat-page .entry__lead { align-self: center; margin: 0.8rem 0 0; }
.cat-cols { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 clamp(2rem, 4vw, 3.5rem); }
.cat-shelf { break-inside: avoid; margin-bottom: 1.8rem; }
.cat-shelf h2 { margin-bottom: 0.2rem; padding-bottom: 0.5rem; border-bottom: 2px solid #a8321e; color: #a8321e; font-family: var(--title); font-size: 1.25rem; font-weight: 400; letter-spacing: 0.14em; text-transform: uppercase; }

[data-theme="dark"] .leaf {
  background: linear-gradient(170deg, #2a170b, #1e0f06);
  box-shadow:
    inset 0 0 0 10px #251409,
    inset 0 0 0 11px rgba(227, 179, 74, 0.6),
    inset 0 0 0 14px #251409,
    inset 0 0 0 15px rgba(93, 140, 220, 0.55),
    0 30px 50px -30px rgba(0, 0, 0, 0.9);
  color: var(--g-text);
}
[data-theme="dark"] .leaf__head, [data-theme="dark"] .entry__n { padding-bottom: 0.2rem; color: #8fb0ea; }
[data-theme="dark"] .entry { border-bottom-color: var(--g-line); }
[data-theme="dark"] .entry__t { color: #fff6ea; }
[data-theme="dark"] .entry__t small { color: var(--gold); }
[data-theme="dark"] .entry__lead { border-bottom-color: rgba(243, 230, 211, 0.3); }
[data-theme="dark"] .entry .b-price { color: var(--gold-light); }
[data-theme="dark"] .cat-shelf h2 { border-bottom-color: rgba(93, 140, 220, 0.6); color: #8fb0ea; }

@media (max-width: 880px) {
  .cat-home { grid-template-columns: minmax(0, 1fr); }
  .fan { height: 300px; }
  .fan .cover { width: 150px; }
  .cat-cols { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 480px) {
  .fan { height: 250px; }
  .fan .cover { width: 118px; }
  .entry { grid-template-columns: auto minmax(0, 1fr) auto; }
  .cat-page .entry { grid-template-columns: 46px minmax(0, 1fr) auto; }
  .cat-page .entry .cover { width: 46px; }
  .entry__lead { display: none; }
  .entry__t { font-size: 1.15rem; }
}
"""


def entry(b, n=None, thumb=False):
    lead = f'<span class="entry__n">{n:02d}</span>' if n else cover(b) if thumb else ""
    return (f'<li class="entry">{lead}<span class="entry__t"><small>{esc(b[1])}</small><a href="#">{esc(b[0])}</a></span>'
            f'<span class="entry__lead" aria-hidden="true"></span><span class="b-price">{PRICE}</span></li>')


HOME_5 = f"""
      <div class="cat-home">
        <div class="fan" aria-hidden="true">{cover(FEATURED[1])}{cover(FEATURED[2])}{cover(FEATURED[0])}</div>
        <div class="leaf">
          <p class="leaf__head">Featured books</p>
          <ol class="entries">{"".join(entry(b, i + 1) for i, b in enumerate(FEATURED))}</ol>
        </div>
      </div>
      <p class="lib-foot">{VISIT}</p>"""
PAGE_5 = f"""
<main id="main" class="lib-page">
  <section class="section" aria-labelledby="library-heading">
    <div class="wrap">{section_head("Library", lede=True, back=True)}
      <div class="leaf cat-page">
        <div class="cat-cols">
          <div>{"".join(f'<div class="cat-shelf"><h2>{esc(s)}</h2><ul class="entries">' + "".join(entry(b, thumb=True) for b in shelf(s)) + "</ul></div>" for s in SHELVES[:2])}</div>
          <div>{"".join(f'<div class="cat-shelf"><h2>{esc(s)}</h2><ul class="entries">' + "".join(entry(b, thumb=True) for b in shelf(s)) + "</ul></div>" for s in SHELVES[2:])}</div>
        </div>
      </div>
    </div>
  </section>
</main>"""

BUILDS = [
    (CSS_1, home(HOME_1), PAGE_1, "", "", "on-ground",
     "The curriculum's bay with the books standing face-out on the plank; name and price lettered on the wood. The page is a bay per shelf."),
    (CSS_2, home(HOME_2), PAGE_2, "", FILTER_JS, "on-ground",
     "Cream cards cut like the teachers', cover, subject, name and price; the page adds a subject filter."),
    (CSS_3, home(HOME_3), PAGE_3, SPOT_JS, "", "",
     "The Articles pattern: one book featured large on the rust board, the rest in the carousel; the page under the banner, by shelf."),
    (CSS_4, home(HOME_4), PAGE_4, NICHE_JS, FILTER_JS, "on-ground",
     "Each book in an Alumni mihrab niche, lit from below, name and price in the recess; a grid of niches on the page."),
    (CSS_5, home(HOME_5), PAGE_5, "", "", "on-ground",
     "The folio's jadwal as a bookseller's price list: fanned covers and a ruled leaf at home, the whole catalogue on the page."),
]

if __name__ == "__main__":
    for (slug, name), (css, h, p, hjs, pjs, pcls, blurb) in zip(OPTIONS, BUILDS):
        (HERE / f"{slug}.html").write_text(page(f"{slug}.html", slug, name, blurb, css, h, "on-ground", hjs))
        (HERE / f"{slug}-page.html").write_text(page(f"{slug}-page.html", slug, name, blurb, css, p, pcls, pjs))
        print("wrote", slug)

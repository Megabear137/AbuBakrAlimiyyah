#!/usr/bin/env python3
"""The bookstore, round 2: five new mockups, each a home-page section and a
full page, owing nothing to the site's components.

Round 1 (generate.py) dressed the books in the site's own pieces - the bay,
the teacher card, the article board, the niche, the jadwal - and option 2 was
built. This round starts again: no card, panel, switch, section head or
button of styles.css is used for the bookstore itself. Only the frame stays
the site's - header, menu, ground, the logo rules either side of the home
section, footer - so each option is seen where it would sit, in both modes.
Each one is a bookshop idea:

  1. Shop window   - a striped awning over a lit window; the books on a
                     plinth with paper price tags on strings. The page is the
                     shop's aisles, with a sticky aisle index.
  2. Objects       - the books as 3D objects, page block and all, turning
                     to face you; a round price sticker on each cover. The
                     page filters by bookmarks hanging from a rail.
  3. Card catalogue - the library's index cards, typed, with a stamped price,
                     fanned like a hand. The page is a cabinet of drawers,
                     one per category, that pull out.
  4. Coverflow     - the covers in a turning 3D strip on a dark stage, the
                     centred book's name and price beneath. The page has a
                     grid | list view switch.
  5. Index         - an editorial price list: big italic type, numbered
                     rows, and the cover following the pointer over a row.
                     The page is the whole index by category.

Content as round 1's: curriculum titles stand in for stock, $00.00 for
prices, a TODO intro, and the drawn bindings where photographs will go.

Edit this file, not the output:  python3 generate_round2.py
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("round1", HERE / "generate.py")
r1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r1)

art, esc = r1.art, r1.esc
BOOKS, FEATURED, SHELVES, COVERS = r1.BOOKS, r1.FEATURED, r1.SHELVES, r1.COVERS
PRICE = "$00.00"
LEDE = "TODO: A line about the bookstore: what it stocks, and where and when the books can be bought."
PAGE = ' aria-current="page"'
LONG_ARROW = '<svg viewBox="0 0 40 12" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M0 6h38M33 1l5 5-5 5"/></svg>'


def shelf(name):
    return [b for b in BOOKS if b[2] == name]


def img(b, cls=""):
    return f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="{COVERS[b[0]]}" width="300" height="400" alt="" loading="lazy">'


OPTIONS = [
    ("r2-1-window", "Shop window"),
    ("r2-2-objects", "Objects"),
    ("r2-3-catalogue", "Card catalogue"),
    ("r2-4-coverflow", "Coverflow"),
    ("r2-5-index", "Index"),
]


def switcher(slug, is_page):
    links = "".join(
        f'<a href="{s}{"-page" if is_page else ""}.html" title="{n}"{PAGE if s == slug else ""}>{i + 1}</a>'
        for i, (s, n) in enumerate(OPTIONS))
    return f"""
<nav class="m-switch" aria-label="Mockups">
  <a href="1-shelf{"-page" if is_page else ""}.html">Round 1</a><a href="r2-1-window{"-page" if is_page else ""}.html"{PAGE}>Round 2</a><a href="r3-01-bento{"-page" if is_page else ""}.html">Round 3</a><a href="r4-01-hashiya{"-page" if is_page else ""}.html">Round 4</a><i></i>{links}<i></i>
  <a href="{slug}.html"{"" if is_page else PAGE}>Home</a><a href="{slug}-page.html"{PAGE if is_page else ""}>Page</a><i></i>
  <button type="button" data-set-theme="light">Light</button>
  <button type="button" data-set-theme="dark">Dark</button>
</nav>"""


FRAME_CSS = """
/* The frame: the home section between the site's rules; the page under the header. */
.r2-home { padding-top: 110px; }
.r2-home > section { padding-block: clamp(4rem, 8vw, 110px); }
.r2-page { padding: 120px 0 clamp(4rem, 8vw, 110px); }
.r2-wrap { width: min(100% - 2 * var(--gutter), 1180px); margin-inline: auto; }
[hidden] { display: none !important; }
"""


def page(fname, slug, name, blurb, css, main, js=""):
    is_page = fname.endswith("-page.html")
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bookstore · {name}{" · page" if is_page else ""}</title>
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
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Gilda+Display&family=Instrument+Sans:wght@400;500;600&family=Courier+Prime:wght@400;700&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../assets/css/styles.css?v=60">
  <link rel="stylesheet" href="../canvas-article/mockup.css">
<!-- Round 2, option {slug}: {name}. {blurb} -->
<style>
{FRAME_CSS.strip()}

{css.strip()}
</style>
</head>
<body id="top" class="on-ground">
{art.HEADER}
{main.rstrip()}
{art.FOOTER}
{switcher(slug, is_page)}
{art.SCRIPTS}
{js}
</body>
</html>
"""


def home(section):
    return f"""
<main id="main" class="r2-home">
  <hr class="section-rule">
{section.rstrip()}
  <hr class="section-rule">
</main>"""


def page_main(inner):
    return f"""
<main id="main" class="r2-page">
{inner.rstrip()}
</main>"""


# ============================================================================
# 1. Shop window: a striped awning with a scalloped edge over a lit window;
#    the books stand on a plinth with paper price tags hung on strings, the
#    names lettered beneath. A painted sign hangs above. The page is the
#    shop's aisles: a sticky aisle index on the left that follows the scroll.
# ============================================================================
CSS_1 = """
.sw { --awning: #b4521a; --awning-2: #fbf1e0; --frame: #3a2212; --glass: linear-gradient(180deg, #fff9ee, #f4e3c8); --ink: var(--brown-ink); --tag: #ecd7a6; }
[data-theme="dark"] .sw { --awning: #8e3a10; --awning-2: #e9d6b4; --frame: #0f0702; --glass: radial-gradient(90% 120% at 50% 0%, #4a2c15, #1d0e05 75%); --ink: #fbeedd; --tag: #e6cd94; }

/* The sign: a painted board hung on two cords. */
.sw-sign { position: relative; width: max-content; margin: 0 auto 2.4rem; padding: 0.9rem 2.6rem 1rem; border-radius: 10px;
  background: linear-gradient(180deg, #4c2b16, #2c180b); box-shadow: inset 0 0 0 3px #2c180b, inset 0 0 0 4px rgba(238, 194, 90, 0.7), 0 16px 26px -14px rgba(30, 12, 2, 0.8); }
.sw-sign::before, .sw-sign::after { content: ""; position: absolute; bottom: 100%; width: 2px; height: 44px; background: linear-gradient(var(--g-line), #7a5a3a); }
.sw-sign::before { left: 18%; transform: skewX(14deg); }
.sw-sign::after { right: 18%; transform: skewX(-14deg); }
.sw-sign h2, .sw-sign h1 { color: #f6dc9c; font-family: var(--display); font-size: clamp(1.8rem, 1.3rem + 1.6vw, 2.6rem); font-weight: 700; letter-spacing: 0.22em; line-height: 1; text-transform: uppercase; }
.sw-lede { max-width: 36rem; margin: -1rem auto 2.4rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; text-align: center; }

/* The awning: stripes, then a scalloped edge in the same stripes. */
.sw-awning { position: relative; z-index: 1; height: 46px; margin-inline: -18px; border-radius: 8px 8px 0 0;
  background: repeating-linear-gradient(90deg, var(--awning) 0 56px, var(--awning-2) 56px 112px);
  box-shadow: inset 0 10px 14px -8px rgba(255, 255, 255, 0.35), inset 0 -8px 12px -8px rgba(0, 0, 0, 0.25); }
.sw-awning::after { content: ""; position: absolute; top: 100%; left: 0; right: 0; height: 28px;
  background:
    radial-gradient(circle at 28px 0, var(--awning) 27px, transparent 28px) 0 0 / 112px 28px repeat-x,
    radial-gradient(circle at 84px 0, var(--awning-2) 27px, transparent 28px) 0 0 / 112px 28px repeat-x;
  filter: drop-shadow(0 8px 6px rgba(30, 12, 2, 0.28)); }

.sw-window { position: relative; padding: 70px clamp(1rem, 3vw, 2.4rem) 0; border: 14px solid var(--frame); border-top: 0; border-radius: 0 0 6px 6px;
  background: var(--glass); box-shadow: 0 40px 60px -40px rgba(30, 12, 2, 0.8); overflow: hidden; }
.sw-window::after { content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(115deg, transparent 30%, rgba(255, 255, 255, 0.32) 38%, transparent 46%, transparent 62%, rgba(255, 255, 255, 0.16) 66%, transparent 70%); }
[data-theme="dark"] .sw-window::after { opacity: 0.25; }

/* The books on the plinth: each cell carries its piece of it, so the plinth runs on unbroken. */
.sw-row { display: grid; grid-template-columns: repeat(var(--n, 4), minmax(0, 1fr)); }
.sw-book { position: relative; display: flex; flex-direction: column; align-items: center; padding: 0 1rem; color: var(--ink); text-align: center; text-decoration: none; }
.sw-book__stand { position: relative; width: min(100%, 150px); margin-bottom: -2px; transform: rotate(var(--tilt, 0deg)); transform-origin: 50% 100%; transition: transform 0.5s var(--ease-out); }
.sw-book:hover .sw-book__stand { transform: rotate(0deg) translateY(-6px); }
.sw-book__stand img { display: block; width: 100%; height: auto; border-radius: 2px 4px 4px 2px; box-shadow: 0 1px 0 rgba(255, 255, 255, 0.2) inset, 8px 14px 18px -8px rgba(30, 12, 2, 0.7); }
.sw-book__plinth { align-self: stretch; height: 22px; margin-inline: -1rem; background: linear-gradient(180deg, #fffaf0, #e6d1b0); box-shadow: 0 1px 0 rgba(255, 255, 255, 0.8) inset, 0 10px 14px -10px rgba(30, 12, 2, 0.6); }
[data-theme="dark"] .sw-book__plinth { background: linear-gradient(180deg, #5a3a22, #2d190c); box-shadow: 0 1px 0 rgba(238, 194, 90, 0.4) inset; }
.sw-book__name { margin: 1rem 0 1.8rem; font-family: var(--display); font-size: 1.15rem; font-weight: 600; line-height: 1.2; }
.sw-book__name small { display: block; margin-bottom: 0.3rem; color: var(--g-accent); font-family: var(--sans); font-size: 0.56rem; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; }

/* The tag: a manila ticket on a string from the cover's corner, notched, with a hole. */
.sw-tag { position: absolute; top: 14%; right: -14px; z-index: 2; padding: 0.35rem 0.6rem 0.35rem 1.2rem; transform: rotate(9deg); transform-origin: 0 50%;
  background: radial-gradient(circle at 9px 50%, transparent 3px, var(--tag) 3.5px); color: #3a2410;
  clip-path: polygon(10px 0, 100% 0, 100% 100%, 10px 100%, 0 50%); filter: drop-shadow(2px 3px 2px rgba(30, 12, 2, 0.35));
  font-family: var(--display); font-size: 1.05rem; font-weight: 700; font-variant-numeric: lining-nums; white-space: nowrap; transition: transform 0.5s var(--ease-out); }
.sw-tag::before { content: ""; position: absolute; right: 100%; top: 50%; width: 22px; height: 1px; background: #6b5030; transform: rotate(-20deg); transform-origin: 100% 0; }
.sw-book:hover .sw-tag { transform: rotate(-4deg); }

.sw-foot { margin-top: 2.4rem; text-align: center; }
.sw-btn { display: inline-flex; align-items: center; gap: 0.9rem; padding: 0.85rem 1.4rem; border-radius: 4px; background: var(--awning); color: #fff6ea;
  font-family: var(--display); font-size: 1.15rem; font-weight: 700; letter-spacing: 0.08em; text-decoration: none; box-shadow: 0 4px 0 #6e2f0c; transition: transform 0.2s, box-shadow 0.2s; }
.sw-btn svg { width: 30px; }
.sw-btn:hover { transform: translateY(2px); box-shadow: 0 2px 0 #6e2f0c; }

/* The page: aisles, with their index. */
.sw-shop { display: grid; grid-template-columns: 200px minmax(0, 1fr); gap: clamp(1.5rem, 4vw, 3.5rem); align-items: start; }
.sw-index { position: sticky; top: 2rem; display: grid; gap: 0.2rem; padding: 1.2rem 0; list-style: none; border-left: 2px solid var(--g-line); }
.sw-index a { display: flex; justify-content: space-between; padding: 0.5rem 1rem; color: var(--g-muted); font-family: var(--display); font-size: 1.15rem; font-weight: 600; text-decoration: none; transition: color 0.2s; }
.sw-index a span { font-family: var(--sans); font-size: 0.7rem; opacity: 0.7; }
.sw-index a[aria-current="true"] { margin-left: -2px; border-left: 2px solid var(--awning); color: var(--g-text); }
.sw-aisle + .sw-aisle { margin-top: clamp(3rem, 6vw, 4.5rem); }
.sw-aisle__name { display: flex; align-items: center; gap: 1rem; margin-bottom: 0; padding-left: 0.2rem; color: var(--g-text); font-family: var(--display); font-size: 1.6rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; scroll-margin-top: 2rem; }
.sw-aisle__name::after { content: ""; flex: 1; height: 1px; background: var(--g-line); }
.sw-aisle .sw-awning { height: 26px; margin-inline: 0; margin-top: 1rem; border-radius: 4px 4px 0 0; }
.sw-aisle .sw-awning::after { height: 16px; background:
    radial-gradient(circle at 28px 0, var(--awning) 27px, transparent 28px) 0 0 / 112px 16px repeat-x,
    radial-gradient(circle at 84px 0, var(--awning-2) 27px, transparent 28px) 0 0 / 112px 16px repeat-x; }
.sw-aisle .sw-window { padding-top: 46px; border-width: 10px; }

@media (max-width: 900px) {
  .sw-shop { grid-template-columns: minmax(0, 1fr); }
  .sw-index { position: static; display: flex; flex-wrap: wrap; border-left: 0; padding: 0; gap: 0.4rem; }
  .sw-index a { padding: 0.4rem 0.8rem; border: 1px solid var(--g-line); border-radius: 4px; gap: 0.6rem; font-size: 1rem; }
  .sw-index a[aria-current="true"] { margin: 0; border: 1px solid var(--awning); }
  .sw-row { --n: 3 !important; }
}
@media (max-width: 640px) { .sw-awning { margin-inline: -6px; } .sw-row { --n: 2 !important; } .sw-tag { font-size: 0.9rem; right: -8px; } .sw-sign { padding-inline: 1.6rem; } }
"""

TILTS = ["-2deg", "1.5deg", "-1deg", "2deg", "-1.5deg", "1deg"]


def sw_book(b, i):
    return (f'<a class="sw-book" href="#" style="--tilt:{TILTS[i % 6]}"><span class="sw-book__stand">{img(b)}'
            f'<span class="sw-tag">{PRICE}</span></span><span class="sw-book__plinth"></span>'
            f'<span class="sw-book__name"><small>{esc(b[1])}</small>{esc(b[0])}</span></a>')


def sw_window(books, n):
    return (f'<div class="sw-awning"></div><div class="sw-window"><div class="sw-row" style="--n:{n}">'
            + "".join(sw_book(b, i) for i, b in enumerate(books)) + "</div></div>")


HOME_1 = home(f"""
  <section class="sw" aria-labelledby="bs-h">
    <div class="r2-wrap">
      <div class="sw-sign"><h2 id="bs-h">Bookstore</h2></div>
      {sw_window(FEATURED[:4], 4)}
      <p class="sw-foot"><a class="sw-btn" href="#">Visit the Bookstore {LONG_ARROW}</a></p>
    </div>
  </section>""")

PAGE_1 = page_main(f"""
  <section class="sw" aria-labelledby="bs-h">
    <div class="r2-wrap">
      <div class="sw-sign"><h1 id="bs-h">Bookstore</h1></div>
      <p class="sw-lede">{LEDE}</p>
      <div class="sw-shop">
        <nav aria-label="Aisles"><ul class="sw-index">{"".join(f'<li><a href="#aisle-{i}" data-aisle="{i}"{" aria-current=" + chr(34) + "true" + chr(34) if i == 0 else ""}>{esc(s)}<span>{len(shelf(s))}</span></a></li>' for i, s in enumerate(SHELVES))}</ul></nav>
        <div>{"".join(f'<section class="sw-aisle" aria-labelledby="aisle-{i}"><h2 class="sw-aisle__name" id="aisle-{i}">{esc(s)}</h2>{sw_window(shelf(s), 4)}</section>' for i, s in enumerate(SHELVES))}</div>
      </div>
    </div>
  </section>""")

JS_1 = """
<script>
  // The aisle index follows the scroll.
  (function () {
    var links = document.querySelectorAll("[data-aisle]");
    var heads = Array.prototype.map.call(links, function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
    function spy() {
      var at = 0;
      heads.forEach(function (h, i) { if (h.getBoundingClientRect().top < window.innerHeight * 0.4) at = i; });
      links.forEach(function (a, i) { a.setAttribute("aria-current", String(i === at)); });
    }
    addEventListener("scroll", spy, { passive: true });
    spy();
  })();
</script>"""

# ============================================================================
# 2. Objects: the books as 3D objects - cover, page block and back - turned
#    to show their pages and turning to face you when pointed at; a round
#    price sticker on each cover, as a bookshop prices a book. The head is
#    set left beside them. The page filters by bookmarks hanging from a rail.
# ============================================================================
CSS_2 = """
.ob { --w: 170px; --h: 227px; --t: 30px; --back: #2a160a; }
.ob-home { display: grid; grid-template-columns: minmax(0, 0.8fr) minmax(0, 2.2fr); gap: clamp(2rem, 5vw, 4rem); align-items: center; }
.ob-head__kicker { color: var(--g-accent); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.ob-head h2, .ob-head h1 { margin: 0.6rem 0 1.4rem; color: var(--g-text); font-family: var(--display); font-size: clamp(2.8rem, 2rem + 2.6vw, 4.6rem); font-weight: 500; line-height: 0.95; }
.ob-head h2 em, .ob-head h1 em { color: var(--rust-ink); }
[data-theme="dark"] .ob-head h2 em, [data-theme="dark"] .ob-head h1 em { color: var(--gold-light); }
.ob-head p { max-width: 24rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; line-height: 1.4; }
.ob-link { display: inline-flex; align-items: center; gap: 1rem; margin-top: 1.8rem; padding-bottom: 0.4rem; border-bottom: 1px solid currentColor; color: var(--g-text);
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.26em; text-decoration: none; text-transform: uppercase; }
.ob-link svg { width: 36px; transition: transform 0.3s var(--ease-out); }
.ob-link:hover svg { transform: translateX(6px); }

.ob-row { display: grid; grid-template-columns: repeat(var(--n, 4), minmax(0, 1fr)); gap: 2.4rem 1rem; }
.ob-item { display: flex; flex-direction: column; align-items: center; color: var(--g-text); text-align: center; text-decoration: none; }
.ob-stage { position: relative; display: grid; place-items: center; width: 100%; height: calc(var(--h) + 40px); perspective: 900px; }
.ob-stage::after { content: ""; position: absolute; bottom: 4px; left: 50%; width: calc(var(--w) * 1.1); height: 22px; transform: translateX(-50%); border-radius: 50%;
  background: radial-gradient(closest-side, rgba(40, 18, 4, 0.45), transparent); transition: transform 0.6s var(--ease-out), opacity 0.6s; }
.ob-book { position: relative; width: var(--w); height: var(--h); transform-style: preserve-3d; transform: rotateY(-32deg) rotateX(4deg); transition: transform 0.7s var(--ease-out); }
.ob-item:hover .ob-book, .ob-item:focus-visible .ob-book { transform: rotateY(-6deg) translateY(-10px); }
.ob-item:hover .ob-stage::after { transform: translateX(-50%) scale(0.85); opacity: 0.7; }
.ob-book > img { position: absolute; inset: 0; width: 100%; height: 100%; border-radius: 1px 4px 4px 1px; transform: translateZ(calc(var(--t) / 2)); }
.ob-book::before { content: ""; position: absolute; top: 3px; left: 0; width: calc(var(--t) - 2px); height: calc(var(--h) - 6px);
  transform: translateX(calc(var(--w) - var(--t) / 2 - 3px)) rotateY(90deg);
  background: repeating-linear-gradient(90deg, #fbf5e8 0 1px, #e2d4b9 1px 2px), #f3e9d6; }
.ob-book::after { content: ""; position: absolute; inset: 0; border-radius: 1px 4px 4px 1px; transform: translateZ(calc(var(--t) / -2)); background: var(--back);
  box-shadow: -14px 6px 40px 4px rgba(30, 12, 2, 0.45); }
/* The sticker: a round label on the cover's lower corner. */
.ob-sticker { position: absolute; right: 12px; bottom: 16px; z-index: 1; display: grid; place-items: center; width: 64px; height: 64px; border-radius: 50%;
  transform: translateZ(calc(var(--t) / 2 + 1px)) rotate(-12deg); background: radial-gradient(circle at 35% 30%, #f9df97, #e0a937 70%); color: #2b1606;
  box-shadow: 0 0 0 2px #fff8e6, 0 0 0 3px rgba(150, 100, 20, 0.6), 2px 4px 8px rgba(30, 12, 2, 0.4);
  font-family: var(--display); font-size: 1rem; font-weight: 700; font-variant-numeric: lining-nums; line-height: 1; }
.ob-name { margin-top: 0.9rem; font-family: var(--display); font-size: 1.3rem; font-weight: 600; line-height: 1.15; }
.ob-sub { margin-top: 0.3rem; color: var(--g-muted); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; }

/* The page: bookmarks hanging from a rail, the chosen one pulled longer. */
.ob-pagehead { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 2rem; align-items: end; margin-bottom: 2.2rem; }
.ob-rail { position: relative; display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: clamp(2.5rem, 5vw, 4rem); padding-top: 6px; }
.ob-rail::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 6px; border-radius: 3px; background: linear-gradient(180deg, #6a4325, #3a2212); }
.ob-mark { position: relative; padding: 1rem 0.9rem 1.6rem; min-width: 84px; border: 0; background: var(--c, #8a4009); color: #fff6ea;
  clip-path: polygon(0 0, 100% 0, 100% 100%, 50% calc(100% - 12px), 0 100%); font: 600 0.62rem/1 var(--sans); letter-spacing: 0.22em; text-transform: uppercase;
  cursor: pointer; transform: translateY(-14px); transition: transform 0.35s var(--ease-out), filter 0.2s; filter: saturate(0.75) brightness(0.92); }
.ob-mark:hover { transform: translateY(-6px); }
.ob-mark[aria-pressed="true"] { transform: translateY(0); filter: none; }
.ob-mark span { display: block; margin-top: 0.4rem; font-family: var(--display); font-size: 1rem; letter-spacing: 0; text-transform: none; opacity: 0.8; }

@media (max-width: 1100px) { .ob-home { grid-template-columns: minmax(0, 1fr); text-align: center; } .ob-head p { margin-inline: auto; } }
@media (max-width: 900px) { .ob-row { --n: 3 !important; } }
@media (max-width: 720px) { .ob { --w: 128px; --h: 171px; --t: 24px; } .ob-row { --n: 2 !important; } .ob-sticker { width: 52px; height: 52px; font-size: 0.82rem; right: 8px; bottom: 10px; } .ob-pagehead { grid-template-columns: minmax(0, 1fr); } }
"""

MARK_COLOURS = ["#9b3d10", "#0f5560", "#4b2458", "#1c3f7a", "#6e1a1f", "#3c3f46"]


def ob_item(b):
    return (f'<a class="ob-item" href="#" data-cat="{esc(b[2])}"><span class="ob-stage"><span class="ob-book">{img(b)}'
            f'<span class="ob-sticker">{PRICE}</span></span></span>'
            f'<span class="ob-name">{esc(b[0])}</span><span class="ob-sub">{esc(b[1])}</span></a>')


HOME_2 = home(f"""
  <section class="ob" aria-labelledby="bs-h">
    <div class="r2-wrap ob-home">
      <div class="ob-head">
        <h2 id="bs-h">The <em>Bookstore</em></h2>
        <a class="ob-link" href="#">Visit the Bookstore {LONG_ARROW}</a>
      </div>
      <div class="ob-row" style="--n:4">{"".join(ob_item(b) for b in FEATURED[:4])}</div>
    </div>
  </section>""")

marks = f'<button class="ob-mark" type="button" data-f="" aria-pressed="true" style="--c:#3a2212">All<span>{len(BOOKS)}</span></button>' + "".join(
    f'<button class="ob-mark" type="button" data-f="{esc(s)}" aria-pressed="false" style="--c:{MARK_COLOURS[i]}">{esc(s)}<span>{len(shelf(s))}</span></button>'
    for i, s in enumerate(SHELVES))
PAGE_2 = page_main(f"""
  <section class="ob" aria-labelledby="bs-h">
    <div class="r2-wrap">
      <div class="ob-pagehead ob-head">
        <div><a class="ob-link" href="#" style="margin:0 0 1.4rem;flex-direction:row-reverse">Home <span style="display:inline-block;transform:scaleX(-1)">{LONG_ARROW}</span></a>
        <h1 id="bs-h">The <em>Bookstore</em></h1><p>{LEDE}</p></div>
      </div>
      <div class="ob-rail" role="group" aria-label="Category">{marks}</div>
      <div class="ob-row">{"".join(ob_item(b) for b in BOOKS)}</div>
    </div>
  </section>""")

JS_2 = """
<script>
  // The bookmarks filter the books.
  document.querySelectorAll(".ob-mark").forEach(function (m) {
    m.addEventListener("click", function () {
      var f = m.dataset.f;
      document.querySelectorAll(".ob-mark").forEach(function (x) { x.setAttribute("aria-pressed", String(x === m)); });
      document.querySelectorAll(".ob-item").forEach(function (b) { b.hidden = !!f && b.dataset.cat !== f; });
    });
  });
</script>"""

# ============================================================================
# 3. Card catalogue: each book an index card from a library's catalogue -
#    ruled, red top line, punched at the foot, the title typed, a call mark
#    from its category, the price stamped in red ink. At home they fan like
#    a hand of cards; the page is a cabinet of drawers that pull out.
# ============================================================================
CSS_3 = """
.cc { --card: #fdf8ec; --rule: rgba(80, 120, 190, 0.22); --red: #c0392b; --stamp: #b8321f; --type: #2b2118; }
[data-theme="dark"] .cc { --card: #f1e7d0; }
.cc-label { width: max-content; margin: 0 auto 3rem; padding: 6px; border-radius: 4px; background: linear-gradient(180deg, #c9a45a, #8f6a2b); box-shadow: 0 6px 14px -6px rgba(30, 12, 2, 0.6); }
.cc-label > * { padding: 0.7rem 2rem 0.6rem; background: var(--card); color: var(--type); font-family: "Courier Prime", monospace; font-size: clamp(1.4rem, 1rem + 1.4vw, 2rem); font-weight: 700;
  letter-spacing: 0.3em; text-transform: uppercase; box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.25); }

.cc-card { position: relative; display: grid; grid-template-columns: 68px minmax(0, 1fr); align-content: start; gap: 0 1rem; width: 290px; aspect-ratio: 5 / 3; padding: 14px 18px 30px;
  background:
    linear-gradient(var(--red), var(--red)) 0 46px / 100% 1.5px no-repeat,
    repeating-linear-gradient(180deg, transparent 0 21px, var(--rule) 21px 22px) 0 47px / 100% calc(100% - 47px) no-repeat,
    var(--card);
  -webkit-mask: radial-gradient(circle 7px at 50% calc(100% - 13px), transparent 97%, #000);
          mask: radial-gradient(circle 7px at 50% calc(100% - 13px), transparent 97%, #000);
  color: var(--type); font-family: "Courier Prime", monospace; text-decoration: none; box-shadow: 0 1px 0 rgba(0, 0, 0, 0.06); }
.cc-wrap { filter: drop-shadow(0 14px 16px rgba(30, 12, 2, 0.35)); }
.cc-call { grid-column: 1 / -1; display: flex; justify-content: space-between; height: 32px; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.1em; }
.cc-card img { grid-row: 2 / span 2; width: 68px; height: auto; margin-top: 10px; box-shadow: 2px 3px 6px rgba(30, 12, 2, 0.4); }
.cc-title { margin-top: 12px; font-size: 1.12rem; font-weight: 700; line-height: 22px; }
.cc-sub { font-size: 0.85rem; line-height: 22px; opacity: 0.75; }
.cc-stamp { position: absolute; right: 16px; bottom: 26px; padding: 0.2rem 0.6rem; border: 2.5px solid var(--stamp); border-radius: 3px; color: var(--stamp);
  font-size: 1.15rem; font-weight: 700; letter-spacing: 0.06em; transform: rotate(-9deg); opacity: 0.85; mix-blend-mode: multiply;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='60'%3E%3Cfilter id='f'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3CfeColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -2.2 1.7'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23f)'/%3E%3C/svg%3E");
          mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='60'%3E%3Cfilter id='f'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3CfeColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -2.2 1.7'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23f)'/%3E%3C/svg%3E"); }

/* The hand: cards fanned from a point below, one lifted on hover. */
.cc-hand { display: flex; justify-content: center; padding: 40px 0 20px; }
.cc-hand .cc-wrap { margin-left: -18px; transform: rotate(var(--r)) translateY(var(--y)); transform-origin: 50% 220%; transition: transform 0.45s var(--ease-out); }
.cc-hand .cc-wrap:first-child { margin-left: 0; }
.cc-hand .cc-wrap:hover, .cc-hand .cc-wrap:focus-within { z-index: 5; transform: rotate(var(--r)) translateY(calc(var(--y) - 46px)); }
.cc-foot { margin-top: 2.6rem; text-align: center; }
.cc-btn { display: inline-flex; align-items: center; gap: 0.9rem; padding: 0.8rem 1.4rem; border: 2px solid var(--g-text); color: var(--g-text);
  font: 700 0.95rem/1 "Courier Prime", monospace; letter-spacing: 0.16em; text-decoration: none; text-transform: uppercase; box-shadow: 4px 4px 0 var(--g-line); transition: transform 0.2s, box-shadow 0.2s; }
.cc-btn svg { width: 30px; }
.cc-btn:hover { transform: translate(2px, 2px); box-shadow: 2px 2px 0 var(--g-line); }

/* The page: the cabinet, a drawer per category; the open one stands out. */
.cc-lede { max-width: 36rem; margin: -1.6rem auto 2.6rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; text-align: center; }
.cc-cabinet { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; max-width: 900px; margin: 0 auto 3rem; padding: 10px; border-radius: 8px;
  background: linear-gradient(180deg, #4a2d18, #2a170a); box-shadow: 0 30px 40px -26px rgba(30, 12, 2, 0.8); }
.cc-drawer { position: relative; display: grid; justify-items: center; gap: 10px; padding: 14px 6px 12px; border: 0; border-radius: 4px; cursor: pointer;
  background: linear-gradient(180deg, #7b5130, #5b3a21); box-shadow: inset 0 1px 0 rgba(255, 230, 190, 0.25), inset 0 -2px 4px rgba(0, 0, 0, 0.3);
  transition: transform 0.35s var(--ease-out), box-shadow 0.35s; }
.cc-drawer__label { width: 100%; padding: 5px 4px; border: 2px solid #c9a45a; background: var(--card); color: var(--type); font: 700 0.62rem/1.2 "Courier Prime", monospace;
  letter-spacing: 0.08em; text-transform: uppercase; overflow-wrap: anywhere; }
.cc-drawer__pull { width: 34px; height: 12px; border: 3px solid #c9a45a; border-top: 0; border-radius: 0 0 18px 18px; }
.cc-drawer[aria-pressed="true"] { transform: translateY(10px) scale(1.04); box-shadow: inset 0 1px 0 rgba(255, 230, 190, 0.3), 0 16px 18px -8px rgba(0, 0, 0, 0.7); }
.cc-drawer[aria-pressed="true"]::after { content: ""; position: absolute; top: 100%; left: 50%; border: 8px solid transparent; border-top-color: #5b3a21; transform: translateX(-50%); }
.cc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.6rem; justify-items: center; }
.cc-grid .cc-card { width: 100%; max-width: 360px; }
.cc-grid .cc-wrap { width: 100%; display: flex; justify-content: center; }

@media (max-width: 1240px) { .cc-hand .cc-wrap:nth-child(4) { display: none; } }
@media (max-width: 960px) {
  .cc-hand .cc-wrap:nth-child(4) { display: block; }
  .cc-hand { flex-direction: column; align-items: center; gap: 0; }
  .cc-hand .cc-wrap { margin: -40px 0 0; transform: rotate(calc(var(--r) / 3)); }
  .cc-hand .cc-wrap:first-child { margin-top: 0; }
  .cc-hand .cc-wrap:hover { transform: rotate(0) translateY(-10px); }
}
@media (max-width: 720px) { .cc-cabinet { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 420px) {
  .cc-card { width: min(340px, calc(100vw - 2 * var(--gutter))); grid-template-columns: 54px minmax(0, 1fr); aspect-ratio: auto; min-height: 190px; }
  .cc-card img { width: 54px; }
  .cc-hand .cc-wrap { transform: none; }
  .cc-grid { grid-template-columns: minmax(0, 1fr); }
  .cc-label > * { padding-inline: 1rem; letter-spacing: 0.18em; }
}
"""

CODES = {"Arabic": "ARB", "Qur'an": "QUR", "Hadith": "HAD", "Fiqh": "FIQ", "Aqidah & Sira": "AQD"}


def cc_card(b, r="0deg", y="0px"):
    n = shelf(b[2]).index(b) + 1
    return (f'<div class="cc-wrap" data-cat="{esc(b[2])}" style="--r:{r};--y:{y}"><a class="cc-card" href="#">'
            f'<span class="cc-call"><span>{CODES[b[2]]} {n:03d}</span><span>{esc(b[2])}</span></span>{img(b)}'
            f'<span class="cc-title">{esc(b[0])}</span><span class="cc-sub">{esc(b[1])}</span>'
            f'<span class="cc-stamp">{PRICE}</span></a></div>')


FAN = [("-7deg", "18px"), ("-2.5deg", "2px"), ("2.5deg", "2px"), ("7deg", "18px")]
HOME_3 = home(f"""
  <section class="cc" aria-labelledby="bs-h">
    <div class="r2-wrap">
      <div class="cc-label"><h2 id="bs-h">Bookstore</h2></div>
      <div class="cc-hand">{"".join(cc_card(b, *FAN[i]) for i, b in enumerate(FEATURED[:4]))}</div>
      <p class="cc-foot"><a class="cc-btn" href="#">Visit the Bookstore {LONG_ARROW}</a></p>
    </div>
  </section>""")

drawers = f'<button class="cc-drawer" type="button" data-f="" aria-pressed="true"><span class="cc-drawer__label">All</span><span class="cc-drawer__pull"></span></button>' + "".join(
    f'<button class="cc-drawer" type="button" data-f="{esc(s)}" aria-pressed="false"><span class="cc-drawer__label">{CODES[s]}<br>{esc(s)}</span><span class="cc-drawer__pull"></span></button>'
    for s in SHELVES)
PAGE_3 = page_main(f"""
  <section class="cc" aria-labelledby="bs-h">
    <div class="r2-wrap">
      <div class="cc-label"><h1 id="bs-h">Bookstore</h1></div>
      <p class="cc-lede">{LEDE}</p>
      <div class="cc-cabinet" role="group" aria-label="Category">{drawers}</div>
      <div class="cc-grid">{"".join(cc_card(b) for b in BOOKS)}</div>
    </div>
  </section>""")

JS_3 = """
<script>
  // A drawer pulled out shows its cards.
  document.querySelectorAll(".cc-drawer").forEach(function (d) {
    d.addEventListener("click", function () {
      var f = d.dataset.f;
      document.querySelectorAll(".cc-drawer").forEach(function (x) { x.setAttribute("aria-pressed", String(x === d)); });
      document.querySelectorAll(".cc-grid .cc-wrap").forEach(function (c) { c.hidden = !!f && c.dataset.cat !== f; });
    });
  });
</script>"""

# ============================================================================
# 4. Coverflow: a dark stage across the page, the covers in a strip that
#    turns in 3D as it scrolls (drag, swipe, arrows or keys), the centred
#    book facing out over its reflection, its name and price beneath. The
#    page: a toolbar with a category menu and a grid | list view switch.
# ============================================================================
CSS_4 = """
.cf { position: relative; padding-block: clamp(3rem, 6vw, 5rem); background: radial-gradient(60% 70% at 50% 35%, #4a2a13, #1b0d04 70%); color: #fbeedd; overflow: hidden; }
[data-theme="dark"] .cf { background: radial-gradient(60% 70% at 50% 35%, #3a200e, #0d0602 70%); border-block: 1px solid rgba(227, 179, 74, 0.18); }
.cf-title { margin-bottom: clamp(1.5rem, 3vw, 2.5rem); text-align: center; }
.cf-title h2, .cf-title h1 { display: inline-flex; align-items: center; gap: 1.2rem; color: #f6dc9c; font-family: var(--display); font-size: clamp(2rem, 1.4rem + 2vw, 3rem); font-style: italic; font-weight: 500; }
.cf-title > *::before, .cf-title > *::after { content: ""; width: clamp(30px, 8vw, 90px); height: 1px; background: linear-gradient(90deg, transparent, rgba(246, 220, 156, 0.7)); }
.cf-title > *::after { transform: scaleX(-1); }

.cf-track { display: flex; align-items: center; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; padding: 30px calc(50% - 100px) 90px; outline: none; cursor: grab; }
.cf-track::-webkit-scrollbar { display: none; }
.cf-item { flex: none; width: 200px; margin-inline: -28px; scroll-snap-align: center; transform-style: preserve-3d; transition: transform 0.12s linear, opacity 0.12s linear; border: 0; padding: 0; background: none; cursor: pointer; }
.cf-item img { display: block; width: 100%; height: auto; border-radius: 2px 4px 4px 2px; box-shadow: 0 30px 40px -20px rgba(0, 0, 0, 0.9);
  -webkit-box-reflect: below 4px linear-gradient(transparent 62%, rgba(255, 255, 255, 0.22)); }
.cf-cap { position: relative; z-index: 1; min-height: 6.4rem; margin-top: -40px; text-align: center; }
.cf-cap__sub { color: rgba(246, 220, 156, 0.75); font-size: 0.62rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.cf-cap__name { margin: 0.4rem 0 0.2rem; font-family: var(--display); font-size: clamp(1.6rem, 1.3rem + 1vw, 2.2rem); font-weight: 600; line-height: 1.1; }
.cf-cap__price { color: #f6dc9c; font-family: var(--display); font-size: 1.4rem; font-weight: 700; font-variant-numeric: lining-nums; }
.cf-nav { display: flex; align-items: center; justify-content: center; gap: 1.4rem; margin-top: 1.4rem; }
.cf-arrow { display: grid; place-items: center; width: 40px; height: 40px; border: 1px solid rgba(246, 220, 156, 0.4); border-radius: 0; background: none; color: #f6dc9c; cursor: pointer; transition: background 0.2s; }
.cf-arrow:hover { background: rgba(246, 220, 156, 0.12); }
.cf-arrow svg { width: 18px; }
.cf-bar { position: relative; width: min(240px, 40vw); height: 2px; background: rgba(246, 220, 156, 0.2); }
.cf-bar i { position: absolute; top: -1px; height: 4px; background: #f6dc9c; transition: left 0.2s, width 0.2s; }
.cf-more { display: inline-block; margin-top: 2rem; padding: 0.9rem 1.6rem; border: 1px solid #f6dc9c; color: #f6dc9c; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.28em; text-decoration: none; text-transform: uppercase; transition: background 0.2s, color 0.2s; }
.cf-more:hover { background: #f6dc9c; color: #1b0d04; }

/* The page: toolbar, then the grid or the list. */
.cf-page .cf { padding-bottom: 2.5rem; }
.vw-bar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem; margin: 2.6rem 0 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--g-line); }
.vw-bar p { color: var(--g-muted); font-family: var(--display); font-size: 1.15rem; font-style: italic; }
.vw-tools { display: flex; align-items: center; gap: 0.8rem; }
.vw-select { position: relative; }
.vw-select select { appearance: none; min-height: 40px; padding: 0 2.4rem 0 1rem; border: 1px solid var(--g-line); border-radius: 0; background: transparent; color: var(--g-text); font: 500 0.82rem var(--sans); cursor: pointer; }
.vw-select select option { background: #fffaf2; color: #462c16; }
.vw-select::after { content: ""; position: absolute; right: 14px; top: 50%; width: 7px; height: 7px; border: solid var(--g-text); border-width: 0 1.5px 1.5px 0; transform: translateY(-70%) rotate(45deg); pointer-events: none; }
.vw-switch { display: flex; border: 1px solid var(--g-line); }
.vw-switch button { display: grid; place-items: center; width: 40px; height: 38px; border: 0; background: none; color: var(--g-muted); cursor: pointer; }
.vw-switch button[aria-pressed="true"] { background: var(--g-text); color: var(--bg-color, #f2dec6); }
.vw-switch svg { width: 18px; }
.vw { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 2.4rem 1.6rem; }
.vw-book { display: grid; gap: 0.2rem; color: var(--g-text); text-decoration: none; }
.vw-book img { width: 100%; height: auto; margin-bottom: 0.8rem; border-radius: 2px 4px 4px 2px; box-shadow: 0 16px 24px -14px rgba(30, 12, 2, 0.8); transition: transform 0.4s var(--ease-out); }
.vw-book:hover img { transform: translateY(-6px); }
.vw-book__name { font-family: var(--display); font-size: 1.2rem; font-weight: 600; line-height: 1.15; }
.vw-book__sub { color: var(--g-muted); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.24em; text-transform: uppercase; }
.vw-book__cat { display: none; }
.vw-book__price { margin-top: 0.3rem; color: var(--rust-ink); font-family: var(--display); font-size: 1.2rem; font-weight: 700; font-variant-numeric: lining-nums; }
[data-theme="dark"] .vw-book__price { color: var(--gold-light); }
.vw--list { grid-template-columns: minmax(0, 1fr); gap: 0; }
.vw--list .vw-book { grid-template-columns: 56px minmax(0, 2fr) minmax(0, 1fr) minmax(0, 1fr) auto; align-items: center; gap: 1.4rem; padding: 0.8rem 0; border-bottom: 1px solid var(--g-line); }
.vw--list .vw-book img { grid-row: auto; margin: 0; }
.vw--list .vw-book:hover img { transform: none; }
.vw--list .vw-book__cat { display: block; color: var(--g-muted); font-size: 0.85rem; }
.vw--list .vw-book__price { margin: 0; }
@media (max-width: 1100px) { .vw { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (max-width: 800px) { .vw { grid-template-columns: repeat(3, minmax(0, 1fr)); } .vw--list .vw-book { grid-template-columns: 48px minmax(0, 1fr) auto; } .vw--list .vw-book__sub, .vw--list .vw-book__cat { display: none; } }
@media (max-width: 560px) { .vw { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2rem 1rem; } .cf-item { width: 150px; margin-inline: -22px; } .cf-track { padding-inline: calc(50% - 75px); } }
"""

CHEV = '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 4l-6 6 6 6"/></svg>'


def cf_stage(books, heading_tag, more):
    data = json.dumps([{"t": b[0], "s": b[1]} for b in books])
    items = "".join(f'<button class="cf-item" type="button" aria-label="{esc(b[0])}">{img(b)}</button>' for b in books)
    return f"""
  <section class="cf" aria-labelledby="bs-h">
    <div class="cf-title"><{heading_tag} id="bs-h">Bookstore</{heading_tag}></div>
    <div class="cf-track" tabindex="0" data-books='{esc(data)}'>{items}</div>
    <div class="r2-wrap cf-cap" aria-live="polite">
      <p class="cf-cap__sub"></p><p class="cf-cap__name"></p><p class="cf-cap__price">{PRICE}</p>
      <div class="cf-nav"><button class="cf-arrow" type="button" data-step="-1" aria-label="Previous book">{CHEV}</button>
        <span class="cf-bar"><i></i></span>
        <button class="cf-arrow" type="button" data-step="1" aria-label="Next book" style="transform:scaleX(-1)">{CHEV}</button></div>
      {more}
    </div>
  </section>"""


HOME_4 = f"""
<main id="main" class="r2-home" style="padding-bottom:0">
  <hr class="section-rule">
  <div style="height:clamp(3rem,6vw,5rem)"></div>
{cf_stage(FEATURED, "h2", '<a class="cf-more" href="#">Visit the Bookstore</a>')}
  <div style="height:clamp(3rem,6vw,5rem)"></div>
  <hr class="section-rule">
</main>"""

GRID_I = '<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><rect x="2" y="2" width="7" height="7"/><rect x="11" y="2" width="7" height="7"/><rect x="2" y="11" width="7" height="7"/><rect x="11" y="11" width="7" height="7"/></svg>'
LIST_I = '<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><rect x="2" y="3" width="16" height="2.5"/><rect x="2" y="8.75" width="16" height="2.5"/><rect x="2" y="14.5" width="16" height="2.5"/></svg>'
PAGE_4 = f"""
<main id="main" class="r2-page cf-page" style="padding-top:110px">
{cf_stage(FEATURED, "h1", "")}
  <div class="r2-wrap">
    <div class="vw-bar"><p>{LEDE}</p>
      <div class="vw-tools">
        <label class="vw-select"><span class="visually-hidden" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Category</span>
          <select data-cat-select><option value="">All categories</option>{"".join(f'<option>{esc(s)}</option>' for s in SHELVES)}</select></label>
        <div class="vw-switch" role="group" aria-label="View"><button type="button" data-view="grid" aria-pressed="true" aria-label="Grid">{GRID_I}</button><button type="button" data-view="list" aria-pressed="false" aria-label="List">{LIST_I}</button></div>
      </div>
    </div>
    <div class="vw">{"".join(f'<a class="vw-book" href="#" data-cat="{esc(b[2])}">{img(b)}<span class="vw-book__name">{esc(b[0])}</span><span class="vw-book__sub">{esc(b[1])}</span><span class="vw-book__cat">{esc(b[2])}</span><span class="vw-book__price">{PRICE}</span></a>' for b in BOOKS)}</div>
  </div>
</main>"""

JS_4 = """
<script>
  // The coverflow: the strip scrolls natively (wheel, drag on touch, keys);
  // each cover turns by its distance from the centre, the centred one named.
  (function () {
    var track = document.querySelector(".cf-track");
    var items = Array.prototype.slice.call(track.children);
    var books = JSON.parse(track.dataset.books);
    var cap = { sub: document.querySelector(".cf-cap__sub"), name: document.querySelector(".cf-cap__name") };
    var bar = document.querySelector(".cf-bar i"), current = -1;
    function layout() {
      var mid = track.scrollLeft + track.clientWidth / 2, best = 0, bestD = 1e9;
      items.forEach(function (it, i) {
        var c = it.offsetLeft + it.offsetWidth / 2, d = (c - mid) / it.offsetWidth;
        var a = Math.max(-1, Math.min(1, d)), ad = Math.min(Math.abs(d), 4);
        it.style.transform = "perspective(900px) translateX(" + (-a * 34) + "px) rotateY(" + (-a * 52) + "deg) translateZ(" + (-ad * 90) + "px)";
        it.style.zIndex = String(100 - Math.round(ad * 10));
        it.style.opacity = String(Math.max(0.25, 1 - ad * 0.18));
        if (Math.abs(d) < bestD) { bestD = Math.abs(d); best = i; }
      });
      if (best !== current) {
        current = best;
        cap.sub.textContent = books[best].s;
        cap.name.textContent = books[best].t;
        bar.style.width = (100 / items.length) + "%";
        bar.style.left = (best * 100 / items.length) + "%";
      }
    }
    function go(i, now) {
      i = Math.max(0, Math.min(items.length - 1, i));
      var it = items[i];
      track.scrollTo({ left: it.offsetLeft + it.offsetWidth / 2 - track.clientWidth / 2, behavior: now ? "instant" : "smooth" });
    }
    track.addEventListener("scroll", function () { requestAnimationFrame(layout); }, { passive: true });
    addEventListener("resize", layout);
    items.forEach(function (it, i) { it.addEventListener("click", function () { go(i); }); });
    document.querySelectorAll(".cf-arrow").forEach(function (b) { b.addEventListener("click", function () { go(current + +b.dataset.step); }); });
    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); go(current + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(current - 1); }
    });
    // A mouse drags the strip too.
    var down = null;
    track.addEventListener("pointerdown", function (e) { if (e.pointerType === "mouse") down = { x: e.clientX, s: track.scrollLeft }; });
    addEventListener("pointermove", function (e) { if (down) { track.style.scrollSnapType = "none"; track.scrollLeft = down.s - (e.clientX - down.x); } });
    addEventListener("pointerup", function () { if (!down) return; down = null; track.style.scrollSnapType = ""; go(current); });
    layout();
    go(Math.floor(items.length / 2) - (items.length % 2 ? 0 : 1), true);
    layout();

    // The page's toolbar: a category menu and the grid | list switch.
    var grid = document.querySelector(".vw");
    if (!grid) return;
    document.querySelector("[data-cat-select]").addEventListener("change", function (e) {
      grid.querySelectorAll(".vw-book").forEach(function (b) { b.hidden = !!e.target.value && b.dataset.cat !== e.target.value; });
    });
    document.querySelectorAll("[data-view]").forEach(function (b) {
      b.addEventListener("click", function () {
        document.querySelectorAll("[data-view]").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        grid.classList.toggle("vw--list", b.dataset.view === "list");
      });
    });
  })();
</script>"""

# ============================================================================
# 5. Index: an editorial price list. The name in very large italic type
#    with the count of titles, and the books as numbered rows - name,
#    subject, price in tabular figures - the cover appearing beside the
#    pointer over a row (on touch screens, a small cover in the row). The
#    page is the whole index, the category held at the left as it scrolls.
# ============================================================================
CSS_5 = """
.ix-home { display: grid; grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.4fr); gap: clamp(2rem, 6vw, 6rem); align-items: start; }
.ix-mast h2, .ix-mast h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(3.6rem, 2rem + 6vw, 8rem); font-style: italic; font-weight: 400; letter-spacing: -0.02em; line-height: 0.85; }
.ix-mast__count { display: flex; align-items: baseline; gap: 0.8rem; margin-top: 1.6rem; color: var(--g-muted); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.ix-mast__count b { color: var(--rust-ink); font-family: var(--display); font-size: 3rem; font-weight: 600; letter-spacing: 0; line-height: 1; }
[data-theme="dark"] .ix-mast__count b { color: var(--gold-light); }
.ix-mast p.ix-lede { max-width: 30rem; margin-top: 1.4rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; }
.ix-go { display: inline-flex; align-items: center; gap: 1rem; margin-top: 2.2rem; color: var(--g-text); font-family: var(--display); font-size: 1.4rem; font-style: italic; font-weight: 600; text-decoration: none; }
.ix-go svg { width: 46px; transition: transform 0.3s var(--ease-out); }
.ix-go:hover svg { transform: translateX(8px); }

.ix-list { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--g-text); }
.ix-row { position: relative; display: grid; grid-template-columns: 3.2rem minmax(0, 1fr) auto; align-items: baseline; gap: 1rem; padding: 1.15rem 0.2rem; border-bottom: 1px solid var(--g-line); color: var(--g-text); text-decoration: none; }
.ix-row__n { color: var(--g-muted); font-size: 0.72rem; font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: 0.1em; }
.ix-row__name { font-family: var(--display); font-size: clamp(1.5rem, 1.2rem + 1vw, 2.1rem); font-weight: 500; line-height: 1.05; transition: transform 0.35s var(--ease-out), color 0.2s; }
.ix-row__name small { display: block; margin-top: 0.3rem; color: var(--g-muted); font-family: var(--sans); font-size: 0.58rem; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; }
.ix-row__price { font-family: var(--display); font-size: 1.4rem; font-weight: 600; font-variant-numeric: lining-nums tabular-nums; }
.ix-row::after { content: ""; position: absolute; left: 0; bottom: -1px; width: 0; height: 2px; background: var(--rust); transition: width 0.45s var(--ease-out); }
[data-theme="dark"] .ix-row::after { background: var(--gold); }
.ix-row:hover::after { width: 100%; }
.ix-row:hover .ix-row__name { transform: translateX(10px); }
.ix-row img { display: none; }

/* The cover that follows the pointer. */
.ix-peek { position: fixed; z-index: 30; top: 0; left: 0; width: 170px; pointer-events: none; opacity: 0; transform: translate(-50%, -50%) rotate(-5deg) scale(0.9);
  transition: opacity 0.25s, transform 0.35s var(--ease-out); }
.ix-peek.on { opacity: 1; transform: translate(-50%, -50%) rotate(-3deg) scale(1); }
.ix-peek img { display: block; width: 100%; height: auto; border-radius: 2px 4px 4px 2px; box-shadow: 0 30px 40px -18px rgba(30, 12, 2, 0.8); }

/* The page: categories held at the left. */
.ix-pagehead { margin-bottom: clamp(3rem, 6vw, 5rem); }
.ix-pagehead .back-x { display: inline-block; margin-bottom: 1.6rem; color: var(--g-muted); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.3em; text-decoration: none; text-transform: uppercase; }
.ix-jump { display: flex; flex-wrap: wrap; gap: 0.2rem 0; margin-top: 2rem; font-family: var(--display); font-size: 1.25rem; font-style: italic; }
.ix-jump a { color: var(--g-text); text-decoration: none; }
.ix-jump a:hover { text-decoration: underline; text-underline-offset: 4px; }
.ix-jump a + a::before { content: "/"; margin: 0 0.8rem; color: var(--g-muted); }
.ix-cat { display: grid; grid-template-columns: 220px minmax(0, 1fr); gap: 2rem; margin-top: clamp(2.5rem, 5vw, 4rem); scroll-margin-top: 2rem; }
.ix-cat h2 { position: sticky; top: 2rem; align-self: start; color: var(--g-text); font-family: var(--display); font-size: 2.2rem; font-style: italic; font-weight: 500; line-height: 1; }
.ix-cat h2 span { display: block; margin-top: 0.6rem; color: var(--g-muted); font-family: var(--sans); font-size: 0.62rem; font-style: normal; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; }

@media (hover: none), (max-width: 700px) {
  .ix-row { grid-template-columns: 44px minmax(0, 1fr) auto; }
  .ix-row img { display: block; width: 44px; height: auto; align-self: center; box-shadow: 0 6px 10px -5px rgba(30, 12, 2, 0.7); }
  .ix-row__n { display: none; }
  .ix-peek { display: none; }
}
@media (max-width: 900px) {
  .ix-home { grid-template-columns: minmax(0, 1fr); }
  .ix-cat { grid-template-columns: minmax(0, 1fr); gap: 1rem; }
  .ix-cat h2 { position: static; }
}
"""


def ix_row(b, n):
    return (f'<li><a class="ix-row" href="#" data-cover="{COVERS[b[0]]}">{img(b)}<span class="ix-row__n">{n:02d}</span>'
            f'<span class="ix-row__name">{esc(b[0])}<small>{esc(b[1])}</small></span><span class="ix-row__price">{PRICE}</span></a></li>')


HOME_5 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r2-wrap ix-home">
      <div class="ix-mast">
        <h2 id="bs-h">Book&shy;store</h2>
        <p class="ix-mast__count"><b>{len(BOOKS)}</b> titles</p>
        <a class="ix-go" href="#">Visit the Bookstore {LONG_ARROW}</a>
      </div>
      <ol class="ix-list">{"".join(ix_row(b, i + 1) for i, b in enumerate(FEATURED))}</ol>
    </div>
    <div class="ix-peek" aria-hidden="true"><img alt=""></div>
  </section>""")

n = 0
cats = []
for s in SHELVES:
    rows = []
    for b in shelf(s):
        n += 1
        rows.append(ix_row(b, n))
    cats.append(f'<section class="ix-cat" id="cat-{SHELVES.index(s)}" aria-labelledby="cat-h-{SHELVES.index(s)}"><h2 id="cat-h-{SHELVES.index(s)}">{esc(s)}<span>{len(shelf(s))} titles</span></h2><ol class="ix-list">{"".join(rows)}</ol></section>')
PAGE_5 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r2-wrap">
      <div class="ix-pagehead ix-mast">
        <a class="back-x" href="#">← Home</a>
        <h1 id="bs-h">Bookstore</h1>
        <p class="ix-mast__count"><b>{len(BOOKS)}</b> titles</p>
        <p class="ix-lede">{LEDE}</p>
        <nav class="ix-jump" aria-label="Categories">{"".join(f'<a href="#cat-{i}">{esc(s)}</a>' for i, s in enumerate(SHELVES))}</nav>
      </div>
      {"".join(cats)}
    </div>
    <div class="ix-peek" aria-hidden="true"><img alt=""></div>
  </section>""")

JS_5 = """
<script>
  // Over a row, its cover follows the pointer (not on touch screens).
  (function () {
    var peek = document.querySelector(".ix-peek"), pic = peek.querySelector("img");
    if (!matchMedia("(hover: hover)").matches) return;
    document.querySelectorAll(".ix-row").forEach(function (r) {
      r.addEventListener("pointerenter", function () { pic.src = r.dataset.cover; peek.classList.add("on"); });
      r.addEventListener("pointerleave", function () { peek.classList.remove("on"); });
      r.addEventListener("pointermove", function (e) { peek.style.left = (e.clientX + 120) + "px"; peek.style.top = e.clientY + "px"; });
    });
  })();
</script>"""

BUILDS = [
    (CSS_1, HOME_1, PAGE_1, "", JS_1, "A striped awning over a lit window, books on a plinth with paper price tags; the page is the shop's aisles with a sticky index."),
    (CSS_2, HOME_2, PAGE_2, JS_2, JS_2, "The books as 3D objects that turn to face you, a round price sticker on each; the page filters by hanging bookmarks."),
    (CSS_3, HOME_3, PAGE_3, "", JS_3, "Typed index cards from a card catalogue with a stamped price, fanned like a hand; the page is a cabinet of drawers."),
    (CSS_4, HOME_4, PAGE_4, JS_4, JS_4, "A 3D coverflow on a dark stage with the centred book's name and price; the page adds a grid | list switch."),
    (CSS_5, HOME_5, PAGE_5, JS_5, JS_5, "An editorial price list in large italic type; the cover follows the pointer over a row; the page is the whole index."),
]

if __name__ == "__main__":
    for (slug, name), (css, h, p, hjs, pjs, blurb) in zip(OPTIONS, BUILDS):
        (HERE / f"{slug}.html").write_text(page(f"{slug}.html", slug, name, blurb, css, h, hjs))
        (HERE / f"{slug}-page.html").write_text(page(f"{slug}-page.html", slug, name, blurb, css, p, pjs))
        print("wrote", slug)

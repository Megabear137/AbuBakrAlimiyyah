#!/usr/bin/env python3
"""The bookstore, round 3: ten more mockups, each a home-page section and a
full page, drawn from research into how shops, publishers and museums show
things online - none of them reuses a component of styles.css or of rounds
1 and 2.

Only the frame stays the site's - header, menu, ground, the logo rules either
side of the home section, footer - so each option is seen where it would sit,
in both modes. The ideas, and where they come from:

   1. Bento        - a modular grid of tiles, each tinted with its book's
                     binding (Apple's bento layouts; covers tinting their UI as
                     reading apps do). The page is the same grid, filterable.
   2. Reading table - the books lying on a cloth at angles, as if photographed
                     from above, lifting when pointed at (Sternberg Press's
                     books "lying flat on a table"). The page is a table to
                     drag around, the books in heaps by category.
   3. Chroma       - a list of titles beside a stage that takes the colour of
                     the book under the pointer. On the page the stage is
                     sticky and changes as the list scrolls past it.
   4. The pile     - the books lying in a pile, spine out; pointing at one
                     slides it out and props its cover against the pile.
                     The page is a pile per category.
   5. Pinned run   - the section holds still while scrolling moves a row of
                     books across it, a huge word drifting behind (scroll-
                     linked storytelling). The page is a rail per category.
   6. Opening books - books with depth whose covers swing open to show the
                     title page with the price written in (Codrops' 3D book
                     showcase). The page filters with a sliding underline.
   7. Marquee      - two rows of covers drifting in opposite directions,
                     pausing under the pointer. The page has the marquee as a
                     band over a filterable grid that rises into view.
   8. Salon wall   - covers framed and hung like pictures, numbered on the
                     wall with a key beside them (museum hangs and wall
                     labels). The page is one wall of every book.
   9. Accordion    - tall strips in each book's colour, one opened to show
                     its cover and price. Upright on phones.
  10. Deck         - the covers as a stack of cards to throw through, by
                     drag, button or arrow key. The page adds a contact strip
                     and a Deck | Spread switch.

Content as rounds 1 and 2: curriculum titles stand in for stock, $00.00 for
prices, a TODO intro, and the drawn bindings where photographs will go.

Edit this file, not the output:  python3 generate_round3.py
"""
import importlib.util
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
COUNT = len(BOOKS)
ARROW = '<svg viewBox="0 0 40 12" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M0 6h38M33 1l5 5-5 5"/></svg>'

# The middle shade of each binding: what a book tints its surroundings with.
TONES = {"lapis": "#1c3f7a", "ink": "#2e2c33", "petrol": "#0f5560", "oxblood": "#6e1a1f",
         "aubergine": "#4b2458", "slate": "#39434e"}


def tone(b):
    return TONES[b[3]]


def shelf(name):
    return [b for b in BOOKS if b[2] == name]


def cat_id(name):
    return "c" + str(SHELVES.index(name))


def img(b, cls="", lazy=True):
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{COVERS[b[0]]}" width="300" height="400" alt=""{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""}>'


OPTIONS = [
    ("r3-01-bento", "Bento"),
    ("r3-02-table", "Reading table"),
    ("r3-03-chroma", "Chroma"),
    ("r3-04-pile", "The pile"),
    ("r3-05-pinned", "Pinned run"),
    ("r3-06-open", "Opening books"),
    ("r3-07-marquee", "Marquee"),
    ("r3-08-salon", "Salon wall"),
    ("r3-09-accordion", "Accordion"),
    ("r3-10-deck", "Deck"),
]


def switcher(slug, is_page):
    sfx = "-page" if is_page else ""
    links = "".join(
        f'<a href="{s}{sfx}.html" title="{n}"{PAGE if s == slug else ""}>{i + 1}</a>'
        for i, (s, n) in enumerate(OPTIONS))
    return f"""
<nav class="m-switch" aria-label="Mockups">
  <a href="1-shelf{sfx}.html">R1</a><a href="r2-1-window{sfx}.html">R2</a><a href="r3-01-bento{sfx}.html"{PAGE}>R3</a><a href="r4-01-hashiya{sfx}.html">R4</a><i></i>{links}<i></i>
  <a href="{slug}.html"{"" if is_page else PAGE}>Home</a><a href="{slug}-page.html"{PAGE if is_page else ""}>Page</a><i></i>
  <button type="button" data-set-theme="light">Light</button>
  <button type="button" data-set-theme="dark">Dark</button>
</nav>"""


FRAME_CSS = """
/* The frame: the home section between the site's rules; the page under the header. */
.r3-home { padding-top: 110px; }
.r3-home > section { padding-block: clamp(4rem, 8vw, 110px); }
.r3-page { padding: 120px 0 clamp(4rem, 8vw, 110px); }
.r3-wrap { width: min(100% - 2 * var(--gutter), 1180px); margin-inline: auto; }
.r3-back { display: inline-block; margin-bottom: 1.4rem; color: var(--g-muted); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.3em; text-decoration: none; text-transform: uppercase; }
.r3-back:hover { color: var(--g-text); }
.m-switch { font-size: 0.72rem; }
.m-switch a, .m-switch button { min-width: 26px; padding: 0.5rem 0.55rem; }
[hidden] { display: none !important; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
@property --tone { syntax: "<color>"; inherits: true; initial-value: #1c3f7a; }
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
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Gilda+Display&family=Instrument+Sans:wght@400;500;600&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../assets/css/styles.css?v=60">
  <link rel="stylesheet" href="../canvas-article/mockup.css">
<!-- Round 3, option {slug}: {name}. {blurb} -->
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
<main id="main" class="r3-home">
  <hr class="section-rule">
{section.rstrip()}
  <hr class="section-rule">
</main>"""


def page_main(inner):
    return f"""
<main id="main" class="r3-page">
{inner.rstrip()}
</main>"""


BUILDS = []

# ============================================================================
# 1. Bento: tiles of different sizes in one grid, each washed with its book's
#    binding. A large tile for the lead book, one for the name and count,
#    one for the categories. The cover leans out of a tile's corner and
#    straightens when pointed at. The page: the same grid of every book,
#    every seventh large, with category chips that thin it out.
# ============================================================================
CSS_1 = """
.bn-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-auto-rows: minmax(220px, auto); grid-auto-flow: dense; gap: 14px; }
.bn-tile { --wash: color-mix(in oklab, var(--tone, #a16541) 13%, #fdf6ec);
  position: relative; isolation: isolate; overflow: hidden; display: flex; flex-direction: column; min-width: 0; padding: 1.5rem;
  border-radius: 24px; background: var(--wash); color: var(--brown-ink); text-decoration: none;
  box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--tone, #a16541) 20%, transparent), 0 1px 2px rgba(60, 30, 10, 0.06);
  transition: transform 0.45s var(--ease-out), box-shadow 0.45s var(--ease-out); }
[data-theme="dark"] .bn-tile { --wash: color-mix(in oklab, var(--tone, #a16541) 42%, #150a03); color: #f3e6d3;
  box-shadow: inset 0 0 0 1px rgba(255, 236, 210, 0.08); }
a.bn-tile:hover, a.bn-tile:focus-visible { transform: translateY(-5px); box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--tone) 30%, transparent), 0 26px 40px -26px rgba(40, 18, 4, 0.7); }
a.bn-tile:focus-visible { outline: 2px solid var(--rust); outline-offset: 3px; }

.bn-sub { color: color-mix(in oklab, var(--tone, #7d5006) 70%, #7d5006); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.26em; text-transform: uppercase; }
[data-theme="dark"] .bn-sub { color: var(--gold-pale); opacity: 0.8; }
.bn-title { max-width: 58%; margin-top: 0.5rem; font-family: var(--display); font-size: 1.5rem; font-weight: 600; line-height: 1.08; }
.bn-price { margin-top: auto; width: max-content; padding: 0.4rem 0.8rem; border-radius: 999px; background: rgba(255, 255, 255, 0.72); font-size: 0.78rem; font-weight: 600; font-variant-numeric: tabular-nums; }
[data-theme="dark"] .bn-price { background: rgba(255, 236, 210, 0.1); }
.bn-tile img { position: absolute; z-index: -1; right: -2%; bottom: -9%; width: 44%; height: auto; border-radius: 3px 6px 6px 3px;
  transform: rotate(9deg); box-shadow: -10px 16px 26px -10px rgba(20, 8, 2, 0.6); transition: transform 0.6s var(--ease-out); }
a.bn-tile:hover img, a.bn-tile:focus-visible img { transform: rotate(2deg) translateY(-14px); }

/* The lead book: two by two, in its binding's own colour. */
.bn-lead { grid-column: span 2; grid-row: span 2; padding: clamp(1.6rem, 3vw, 2.4rem); color: #fbeedd;
  background: radial-gradient(120% 90% at 85% 20%, color-mix(in oklab, var(--tone) 70%, #fff), transparent 60%), var(--tone); }
[data-theme="dark"] .bn-lead { background: radial-gradient(120% 90% at 85% 20%, color-mix(in oklab, var(--tone) 85%, #fff), transparent 60%), color-mix(in oklab, var(--tone) 80%, #000); }
.bn-lead .bn-sub { color: var(--gold-pale); }
.bn-lead .bn-title { max-width: 52%; font-size: clamp(2rem, 1.4rem + 2vw, 3.1rem); font-weight: 500; }
.bn-lead .bn-price { background: rgba(255, 255, 255, 0.14); color: #fbeedd; font-size: 0.9rem; }
.bn-lead img { right: 7%; bottom: 9%; width: 40%; transform: rotate(-5deg); box-shadow: -18px 30px 44px -14px rgba(0, 0, 0, 0.6); }
.bn-lead:hover img { transform: rotate(0) translateY(-10px) scale(1.02); }
.bn-flag { margin-bottom: 1.2rem; width: max-content; padding: 0.35rem 0.75rem; border: 1px solid rgba(251, 238, 221, 0.4); border-radius: 999px; font-size: 0.6rem; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; }

/* The name tile and the categories tile. */
.bn-name { grid-column: span 2; justify-content: space-between; --wash: transparent; box-shadow: inset 0 0 0 1px var(--g-line); }
[data-theme="dark"] .bn-name { --wash: rgba(255, 236, 210, 0.03); }
.bn-name h2, .bn-name h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(2.6rem, 1.8rem + 3vw, 4.4rem); font-weight: 500; letter-spacing: -0.01em; line-height: 0.9; }
.bn-name h2 em, .bn-name h1 em { color: var(--rust); font-weight: 500; }
[data-theme="dark"] .bn-name h2 em, [data-theme="dark"] .bn-name h1 em { color: var(--gold); }
.bn-name__foot { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 1rem; }
.bn-count { color: var(--g-muted); font-size: 0.8rem; }
.bn-count b { display: block; color: var(--g-text); font-family: var(--display); font-size: 2.6rem; font-weight: 600; line-height: 1; }
.bn-go { display: inline-flex; align-items: center; gap: 0.7rem; padding: 0.85rem 1.3rem; border-radius: 999px; background: var(--brown-ink); color: #fbeedd; font-size: 0.8rem; font-weight: 500; text-decoration: none; transition: gap 0.3s var(--ease-out); }
[data-theme="dark"] .bn-go { background: var(--gold); color: var(--espresso); }
.bn-go svg { width: 26px; }
.bn-go:hover { gap: 1.1rem; }
.bn-lede { max-width: 30rem; margin-top: 1rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; }

.bn-cats { --wash: transparent; box-shadow: inset 0 0 0 1px var(--g-line); gap: 0.4rem; }
[data-theme="dark"] .bn-cats { --wash: rgba(255, 236, 210, 0.03); }
.bn-cats p { margin-bottom: 0.6rem; color: var(--g-muted); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.26em; text-transform: uppercase; }
.bn-cats a { display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px solid var(--g-line); color: var(--g-text); font-family: var(--display); font-size: 1.15rem; font-weight: 600; text-decoration: none; }
.bn-cats a span { color: var(--g-muted); font-family: var(--sans); font-size: 0.72rem; font-weight: 500; }
.bn-cats a:hover { color: var(--rust); }

/* The page: chips over the grid. */
.bn-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0 0 1.4rem; }
.bn-chips button { padding: 0.6rem 1.05rem; border: 1px solid var(--g-line); border-radius: 999px; background: transparent; color: var(--g-text); font: 500 0.8rem var(--sans); cursor: pointer; transition: background 0.2s, color 0.2s; }
.bn-chips button:hover { border-color: var(--g-text); }
.bn-chips button[aria-pressed="true"] { border-color: var(--brown-ink); background: var(--brown-ink); color: #fbeedd; }
[data-theme="dark"] .bn-chips button[aria-pressed="true"] { border-color: var(--gold); background: var(--gold); color: var(--espresso); }
.bn-chips sup { margin-left: 0.25rem; opacity: 0.6; font-size: 0.62rem; }

@media (max-width: 980px) {
  .bn-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 560px) {
  .bn-grid { grid-template-columns: minmax(0, 1fr); grid-auto-rows: minmax(200px, auto); }
  .bn-lead, .bn-name { grid-column: auto; }
  .bn-lead { min-height: 420px; }
}
"""


def bn_book(b, lead=False):
    if lead:
        return (f'<a class="bn-tile bn-lead" href="#" style="--tone:{tone(b)}" data-cat="{cat_id(b[2])}"><span class="bn-flag">Featured</span>'
                f'<span class="bn-sub">{esc(b[1])}</span><span class="bn-title">{esc(b[0])}</span><span class="bn-price">{PRICE}</span>{img(b)}</a>')
    return (f'<a class="bn-tile" href="#" style="--tone:{tone(b)}" data-cat="{cat_id(b[2])}"><span class="bn-sub">{esc(b[1])}</span>'
            f'<span class="bn-title">{esc(b[0])}</span><span class="bn-price">{PRICE}</span>{img(b)}</a>')


BN_CATS = "".join(f'<a href="#">{esc(s)}<span>{len(shelf(s))}</span></a>' for s in SHELVES)

HOME_1 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap bn-grid">
      {bn_book(FEATURED[0], True)}
      <div class="bn-tile bn-name">
        <h2 id="bs-h">The <em>Book</em>store</h2>
        <div class="bn-name__foot"><p class="bn-count"><b>{COUNT}</b> titles in stock</p><a class="bn-go" href="#">Visit the Bookstore {ARROW}</a></div>
      </div>
      {"".join(bn_book(b) for b in FEATURED[1:6])}
      <div class="bn-tile bn-cats"><p>Browse by category</p>{BN_CATS}</div>
    </div>
  </section>""")

PAGE_1 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="bn-chips" role="group" aria-label="Category">
        <button type="button" aria-pressed="true" data-f="all">All<sup>{COUNT}</sup></button>
        {"".join(f'<button type="button" aria-pressed="false" data-f="{cat_id(s)}">{esc(s)}<sup>{len(shelf(s))}</sup></button>' for s in SHELVES)}
      </div>
      <div class="bn-grid">
        <div class="bn-tile bn-name">
          <h1 id="bs-h">The <em>Book</em>store</h1>
          <p class="bn-lede">{LEDE}</p>
          <div class="bn-name__foot"><p class="bn-count"><b>{COUNT}</b> titles in stock</p></div>
        </div>
        {"".join(bn_book(b, i % 7 == 0) for i, b in enumerate(BOOKS))}
      </div>
    </div>
  </section>""")

JS_1P = """
<script>
  // The chips thin the grid out; the dense flow closes the gaps.
  (function () {
    var chips = document.querySelectorAll(".bn-chips button");
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        chips.forEach(function (x) { x.setAttribute("aria-pressed", String(x === c)); });
        document.querySelectorAll(".bn-grid a.bn-tile").forEach(function (t) {
          t.hidden = c.dataset.f !== "all" && t.dataset.cat !== c.dataset.f;
        });
      });
    });
  })();
</script>"""

BUILDS.append((CSS_1, HOME_1, PAGE_1, "", JS_1P,
               "A bento grid of tiles washed in each book's binding, a large lead tile; the page is the whole grid with category chips."))

# ============================================================================
# 2. Reading table: the books lie on a cloth at angles, overlapping, shot
#    from above. Pointing at one lifts it off the cloth (it straightens, its
#    shadow deepens) and its name and price show on a paper tag. A note on
#    the cloth names the shop. The page is a wide table to drag around (or
#    scroll), the books in a heap per category, each heap with its slip;
#    buttons carry you to a heap.
# ============================================================================
CSS_2 = """
.tb { --cloth: #efe3cf; --weave: rgba(120, 80, 40, 0.07); --tag: #fffaf1; --tag-ink: var(--brown-ink); }
[data-theme="dark"] .tb { --cloth: #2a170b; --weave: rgba(255, 220, 170, 0.035); --tag: #f3e3c6; }
.tb-cloth { position: relative; height: clamp(560px, 50vw, 640px); border-radius: 18px;
  background:
    radial-gradient(120% 90% at 50% 40%, transparent 55%, rgba(60, 30, 10, 0.16)),
    repeating-linear-gradient(0deg, var(--weave) 0 1px, transparent 1px 4px),
    repeating-linear-gradient(90deg, var(--weave) 0 1px, transparent 1px 4px),
    var(--cloth);
  box-shadow: inset 0 0 0 1px rgba(120, 80, 40, 0.12), 0 30px 60px -40px rgba(40, 18, 4, 0.6); }
[data-theme="dark"] .tb-cloth { box-shadow: inset 0 0 0 1px rgba(227, 179, 74, 0.12), inset 0 0 120px rgba(0, 0, 0, 0.5); }

.tb-book { position: absolute; left: var(--x); top: var(--y); z-index: var(--z, 1); width: clamp(110px, 13vw, 160px); color: var(--tag-ink); text-decoration: none;
  transform: rotate(var(--r)); transition: transform 0.5s var(--ease-out); }
.tb-book img { display: block; width: 100%; height: auto; border-radius: 2px 5px 5px 2px;
  box-shadow: 0 1px 1px rgba(30, 12, 2, 0.4), 4px 8px 10px -4px rgba(30, 12, 2, 0.45); transition: box-shadow 0.5s var(--ease-out); }
.tb-book:hover, .tb-book:focus-visible { z-index: 20; transform: rotate(calc(var(--r) * 0.2)) translateY(-10px) scale(1.07); outline: none; }
.tb-book:hover img, .tb-book:focus-visible img { box-shadow: 0 2px 2px rgba(30, 12, 2, 0.2), 18px 34px 34px -10px rgba(30, 12, 2, 0.55); }
.tb-book:focus-visible img { outline: 2px solid var(--rust); outline-offset: 4px; }
.tb-tag { position: absolute; left: 50%; top: calc(100% + 10px); width: max-content; max-width: 200px; padding: 0.45rem 0.75rem 0.5rem; border-radius: 3px;
  background: var(--tag); text-align: center; box-shadow: 0 6px 14px -6px rgba(30, 12, 2, 0.5);
  opacity: 0; transform: translate(-50%, -6px) rotate(calc(var(--r) * -1)); transition: opacity 0.25s, transform 0.4s var(--ease-out); }
.tb-tag b { display: block; font-family: var(--display); font-size: 1.05rem; font-weight: 600; line-height: 1.15; }
.tb-tag span { display: block; margin-top: 0.15rem; color: var(--rust-ink); font-size: 0.72rem; font-weight: 600; font-variant-numeric: tabular-nums; }
.tb-book:hover .tb-tag, .tb-book:focus-visible .tb-tag { opacity: 1; transform: translate(-50%, 0) rotate(calc(var(--r) * -0.2)); }

/* The note: a sheet of paper on the cloth. */
.tb-note { position: absolute; left: var(--x); top: var(--y); z-index: 5; width: min(300px, 30%); padding: 1.6rem 1.6rem 1.4rem; border-radius: 2px;
  background: linear-gradient(180deg, #fffdf8, #f8f0e1); color: var(--brown-ink); transform: rotate(var(--r));
  box-shadow: 0 1px 1px rgba(30, 12, 2, 0.25), 6px 12px 18px -8px rgba(30, 12, 2, 0.4); }
.tb-note h2, .tb-note h1 { font-family: var(--display); font-size: 2.5rem; font-style: italic; font-weight: 500; line-height: 1; }
.tb-note p { margin-top: 0.7rem; color: rgba(70, 44, 22, 0.8); font-size: 0.82rem; }
.tb-note a { display: inline-flex; align-items: center; gap: 0.6rem; margin-top: 1.1rem; color: var(--rust-ink); font-weight: 600; font-size: 0.85rem; text-decoration: none; }
.tb-note a svg { width: 28px; transition: transform 0.3s var(--ease-out); }
.tb-note a:hover svg { transform: translateX(5px); }
.tb-hint { margin-top: 1rem; color: var(--g-muted); font-size: 0.75rem; text-align: center; }

/* The page: a table bigger than the screen. */
.tb-bar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; }
.tb-bar h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(2.4rem, 1.8rem + 2vw, 3.4rem); font-style: italic; font-weight: 500; line-height: 1; }
.tb-bar p { max-width: 34rem; margin-top: 0.6rem; color: var(--g-muted); font-size: 0.85rem; }
.tb-go { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tb-go button { padding: 0.55rem 0.95rem; border: 1px solid var(--g-line); border-radius: 999px; background: transparent; color: var(--g-text); font: 500 0.78rem var(--sans); cursor: pointer; }
.tb-go button:hover { border-color: var(--g-text); }
.tb-view { position: relative; height: min(76vh, 760px); overflow: auto; border-radius: 18px; cursor: grab; scrollbar-width: none; overscroll-behavior: contain; }
.tb-view::-webkit-scrollbar { display: none; }
.tb-view.dragging { cursor: grabbing; }
.tb-view.dragging .tb-book { pointer-events: none; }
.tb-view .tb-cloth { width: 2300px; height: 1500px; border-radius: 0; }
.tb-view .tb-note { width: 230px; padding: 1.1rem 1.2rem; }
.tb-view .tb-note h2 { font-size: 1.9rem; }
.tb-map { position: absolute; right: 14px; bottom: 14px; z-index: 30; width: 138px; height: 90px; border-radius: 8px; background: rgba(36, 18, 5, 0.55); backdrop-filter: blur(6px); pointer-events: none; }
.tb-map i { position: absolute; border: 1.5px solid #f7e0a4; border-radius: 3px; }
.tb-map b { position: absolute; width: 4px; height: 5px; background: rgba(247, 224, 164, 0.55); }
.tb-wrapview { position: relative; }

@media (max-width: 760px) {
  .r3-home .tb-cloth { display: grid; grid-template-columns: 1fr 1fr; gap: 2.6rem 1.4rem; height: auto; padding: 1.6rem 1.2rem 3.6rem; }
  .r3-home .tb-book, .r3-home .tb-note { position: relative; left: auto; top: auto; width: auto; }
  .r3-home .tb-note { grid-column: 1 / -1; order: -1; }
  .r3-home .tb-book .tb-tag, .tb-view .tb-tag { opacity: 1; transform: translate(-50%, 0); }
}
@media (hover: none) { .tb-tag { opacity: 1; transform: translate(-50%, 0) rotate(calc(var(--r) * -1)); } }
"""

TB_SPOTS = [("3%", "8%", -8), ("18%", "42%", 6), ("31%", "5%", -3), ("44%", "44%", 9), ("5%", "57%", 4), ("60%", "6%", -11)]


def tb_book(b, x, y, r, z=1):
    return (f'<a class="tb-book" href="#" style="--x:{x};--y:{y};--r:{r}deg;--z:{z}">{img(b)}'
            f'<span class="tb-tag"><b>{esc(b[0])}</b><span>{PRICE}</span></span></a>')


HOME_2 = home(f"""
  <section class="tb" aria-labelledby="bs-h">
    <div class="r3-wrap">
      <div class="tb-cloth">
        {"".join(tb_book(b, x, y, r, i + 1) for i, (b, (x, y, r)) in enumerate(zip(FEATURED, TB_SPOTS)))}
        <div class="tb-note" style="--x:66%;--y:48%;--r:3deg">
          <h2 id="bs-h">Bookstore</h2>
          <p>{COUNT} titles on the table, from the masjid's bookstore.</p>
          <a href="#">Visit the Bookstore {ARROW}</a>
        </div>
      </div>
    </div>
  </section>""")

# The heaps: a centre per category, books laid round it at fixed angles.
import math
TB_CENTRES = [(420, 380), (1150, 330), (1880, 420), (700, 1080), (1560, 1100)]
TB_TURNS = [-9, 7, -4, 11, -6, 3, -12, 8]
heaps = []
for ci, s in enumerate(SHELVES):
    cx, cy = TB_CENTRES[ci]
    books = shelf(s)
    parts = [f'<div class="tb-note" id="{cat_id(s)}" style="--x:{cx - 115}px;--y:{cy - 230}px;--r:{-2 + ci * 1.5}deg"><h2>{esc(s)}</h2><p>{len(books)} titles</p></div>']
    for k, b in enumerate(books):
        a = -0.6 + k * (2 * math.pi / max(len(books), 3)) * 0.8
        rad = 210
        x, y = cx + math.cos(a) * rad - 80, cy + math.sin(a) * rad * 0.7 - 60
        parts.append(tb_book(b, f"{x:.0f}px", f"{y:.0f}px", TB_TURNS[(k + ci) % len(TB_TURNS)], k + 2))
    heaps.append("".join(parts))

PAGE_2 = page_main(f"""
  <section class="tb" aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="tb-bar">
        <div><h1 id="bs-h">The Bookstore</h1><p>{LEDE}</p></div>
        <div class="tb-go" role="group" aria-label="Go to a category">{"".join(f'<button type="button" data-go="{cat_id(s)}">{esc(s)}</button>' for s in SHELVES)}</div>
      </div>
      <div class="tb-wrapview">
        <div class="tb-view" tabindex="0" aria-label="The bookstore's table: drag or scroll to look around">
          <div class="tb-cloth">{"".join(heaps)}</div>
        </div>
        <div class="tb-map" aria-hidden="true">{"".join(f'<b style="left:{c[0] / 2300 * 100:.1f}%;top:{c[1] / 1500 * 100:.1f}%"></b>' for c in TB_CENTRES)}<i></i></div>
      </div>
      <p class="tb-hint">Drag the table to look around; point at a book to pick it up.</p>
    </div>
  </section>""")

JS_2P = """
<script>
  // Drag the table with a mouse (touch scrolls it natively); a drag swallows the click after it.
  (function () {
    var v = document.querySelector(".tb-view"), map = document.querySelector(".tb-map i"), cloth = v.querySelector(".tb-cloth");
    var down = null, moved = false;
    v.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      down = { x: e.clientX, y: e.clientY, l: v.scrollLeft, t: v.scrollTop }; moved = false;
    });
    addEventListener("pointermove", function (e) {
      if (!down) return;
      var dx = e.clientX - down.x, dy = e.clientY - down.y;
      if (!moved && Math.hypot(dx, dy) > 6) { moved = true; v.classList.add("dragging"); }
      if (moved) { v.scrollLeft = down.l - dx; v.scrollTop = down.t - dy; }
    });
    addEventListener("pointerup", function () { down = null; setTimeout(function () { v.classList.remove("dragging"); }, 0); });
    v.addEventListener("click", function (e) { if (moved) { e.preventDefault(); moved = false; } }, true);
    function mapIt() {
      var W = cloth.offsetWidth, H = cloth.offsetHeight;
      map.style.left = v.scrollLeft / W * 100 + "%"; map.style.top = v.scrollTop / H * 100 + "%";
      map.style.width = v.clientWidth / W * 100 + "%"; map.style.height = v.clientHeight / H * 100 + "%";
    }
    v.addEventListener("scroll", mapIt, { passive: true }); addEventListener("resize", mapIt);
    function goTo(el, smooth) {
      v.scrollTo({ left: el.offsetLeft + 115 - v.clientWidth / 2, top: el.offsetTop + 200 - v.clientHeight / 2, behavior: smooth ? "smooth" : "auto" });
    }
    document.querySelectorAll(".tb-go button").forEach(function (b) {
      b.addEventListener("click", function () { goTo(document.getElementById(b.dataset.go), true); });
    });
    goTo(document.getElementById("c0"), false); mapIt();
  })();
</script>"""

BUILDS.append((CSS_2, HOME_2, PAGE_2, "", JS_2P,
               "The books lying on a cloth, lifted when pointed at with a paper tag; the page is a table to drag around, a heap per category."))

# ============================================================================
# 3. Chroma: the titles as a list in large type; beside it a stage that
#    takes the colour of the book under the pointer (or the keyboard) and
#    shows its cover, subject and price. On the page the stage is sticky and
#    the book crossing the middle of the screen takes it as the list scrolls.
# ============================================================================
CSS_3 = """
.ch-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr); gap: clamp(2rem, 5vw, 4.5rem); align-items: start; }
.ch-head h2, .ch-head h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(2.8rem, 2rem + 3vw, 4.6rem); font-weight: 500; letter-spacing: -0.01em; line-height: 0.9; }
.ch-head p { margin-top: 1rem; color: var(--g-muted); font-size: 0.85rem; }
.ch-head p b { color: var(--g-text); }
.ch-list { list-style: none; margin: 2.2rem 0 0; padding: 0; counter-reset: ch; }
.ch-row { --tone: #a16541; position: relative; display: grid; grid-template-columns: 2.4rem minmax(0, 1fr) auto; align-items: center; gap: 0.8rem; padding: 0.95rem 0.2rem;
  border-top: 1px solid var(--g-line); color: var(--g-muted); text-decoration: none; transition: color 0.3s, padding 0.45s var(--ease-out); }
.ch-row__n { font-size: 0.7rem; font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: 0.12em; }
.ch-row__name { font-family: var(--display); font-size: clamp(1.45rem, 1.15rem + 0.9vw, 1.95rem); font-weight: 500; line-height: 1.1; }
.ch-row__dot { width: 12px; height: 12px; border-radius: 50%; background: var(--tone); box-shadow: 0 0 0 3px color-mix(in oklab, var(--tone) 20%, transparent); transform: scale(0.4); opacity: 0.5; transition: transform 0.35s var(--ease-out), opacity 0.3s; }
.ch-row img { display: none; }
.ch-row.on, .ch-row:hover, .ch-row:focus-visible { color: var(--g-text); padding-left: 0.9rem; outline: none; }
.ch-row.on .ch-row__dot { transform: scale(1); opacity: 1; }
.ch-row:focus-visible .ch-row__name { text-decoration: underline; text-underline-offset: 5px; text-decoration-thickness: 1px; }
.ch-more { display: inline-flex; align-items: center; gap: 0.8rem; margin-top: 1.8rem; color: var(--g-text); font-family: var(--display); font-size: 1.3rem; font-style: italic; font-weight: 600; text-decoration: none; }
.ch-more svg { width: 40px; transition: transform 0.3s var(--ease-out); }
.ch-more:hover svg { transform: translateX(6px); }

/* The stage: a field of the book's colour, lit from above. */
.ch-stage { --tone: #1c3f7a; position: relative; display: grid; grid-template-rows: 1fr auto; min-height: 600px; padding: clamp(1.6rem, 3vw, 2.6rem); overflow: hidden; border-radius: 28px; color: #fbeedd;
  background:
    radial-gradient(70% 55% at 50% 30%, color-mix(in oklab, var(--tone) 55%, #fff4dc), transparent 72%),
    linear-gradient(180deg, var(--tone), color-mix(in oklab, var(--tone) 70%, #000));
  transition: --tone 0.7s var(--ease-out); box-shadow: 0 40px 70px -40px color-mix(in oklab, var(--tone) 70%, #000); }
.ch-stage__pic { position: relative; display: grid; place-items: center; }
.ch-stage__pic img { grid-area: 1 / 1; width: min(52%, 250px); height: auto; border-radius: 3px 6px 6px 3px;
  box-shadow: 0 2px 0 rgba(255, 255, 255, 0.08) inset, -24px 40px 50px -18px rgba(0, 0, 0, 0.65);
  transition: opacity 0.45s, transform 0.6s var(--ease-out); }
.ch-stage__pic img.out { opacity: 0; transform: translateY(18px) rotate(-3deg) scale(0.96); }
.ch-stage__pic::after { content: ""; position: absolute; left: 22%; right: 22%; bottom: -6px; height: 18px; border-radius: 50%; background: rgba(0, 0, 0, 0.35); filter: blur(10px); z-index: -1; }
.ch-stage__cap { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 1rem; margin-top: 1.8rem; padding-top: 1.2rem; border-top: 1px solid rgba(251, 238, 221, 0.22); }
.ch-stage__cap small { display: block; color: var(--gold-pale); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; }
.ch-stage__cap strong { display: block; margin-top: 0.35rem; font-family: var(--display); font-size: clamp(1.5rem, 1.2rem + 1vw, 2.1rem); font-weight: 500; line-height: 1.05; }
.ch-stage__price { font-family: var(--display); font-size: 2rem; font-weight: 600; font-variant-numeric: lining-nums tabular-nums; line-height: 1; }

/* The page: categories in the list, the stage held on screen. */
.ch-cat { margin-top: 2.6rem; color: var(--g-accent); font-size: 0.62rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.r3-page .ch-stage { position: sticky; top: 2rem; min-height: 0; height: calc(100vh - 4rem); max-height: 760px; }
.ch-lede { max-width: 30rem; margin-top: 1rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; }

@media (max-width: 880px) {
  .ch-grid { grid-template-columns: minmax(0, 1fr); }
  .ch-stage { display: none; }
  .ch-row { grid-template-columns: 52px minmax(0, 1fr) auto; }
  .ch-row img { display: block; width: 52px; height: auto; border-radius: 2px 3px 3px 2px; box-shadow: 0 6px 10px -5px rgba(30, 12, 2, 0.6); }
  .ch-row__n { display: none; }
  .ch-row__dot { display: none; }
  .ch-row::after { content: attr(data-price); color: var(--g-text); font-family: var(--display); font-size: 1.15rem; font-weight: 600; }
}
"""


def ch_row(b, n):
    return (f'<li><a class="ch-row" href="#" style="--tone:{tone(b)}" data-tone="{tone(b)}" data-cover="{COVERS[b[0]]}" '
            f'data-title="{esc(b[0])}" data-sub="{esc(b[1])}" data-price="{PRICE}">{img(b)}<span class="ch-row__n">{n:02d}</span>'
            f'<span class="ch-row__name">{esc(b[0])}</span><span class="ch-row__dot"></span></a></li>')


def ch_stage(b):
    return f"""<div class="ch-stage" style="--tone:{tone(b)}" aria-hidden="true">
        <div class="ch-stage__pic">{img(b, lazy=False)}</div>
        <div class="ch-stage__cap"><div><small>{esc(b[1])}</small><strong>{esc(b[0])}</strong></div><span class="ch-stage__price">{PRICE}</span></div>
      </div>"""


HOME_3 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap ch-grid">
      <div>
        <div class="ch-head"><h2 id="bs-h">Bookstore</h2><p><b>{COUNT}</b> titles · sold at the masjid</p></div>
        <ol class="ch-list">{"".join(ch_row(b, i + 1) for i, b in enumerate(FEATURED))}</ol>
        <a class="ch-more" href="#">Visit the Bookstore {ARROW}</a>
      </div>
      {ch_stage(FEATURED[0])}
    </div>
  </section>""")

n = 0
ch_cats = []
for s in SHELVES:
    rows = []
    for b in shelf(s):
        n += 1
        rows.append(ch_row(b, n))
    ch_cats.append(f'<h2 class="ch-cat">{esc(s)}</h2><ol class="ch-list" style="margin-top:0.8rem">{"".join(rows)}</ol>')

PAGE_3 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap ch-grid">
      <div>
        <a class="r3-back" href="#">← Home</a>
        <div class="ch-head"><h1 id="bs-h">Bookstore</h1><p class="ch-lede">{LEDE}</p></div>
        {"".join(ch_cats)}
      </div>
      {ch_stage(BOOKS[0])}
    </div>
  </section>""")

JS_3 = """
<script>
  // A row under the pointer, or focused, gives the stage its colour and cover.
  (function () {
    var stage = document.querySelector(".ch-stage"), rows = [].slice.call(document.querySelectorAll(".ch-row"));
    var pic = stage.querySelector(".ch-stage__pic"), cap = stage.querySelector(".ch-stage__cap"), current = null, timer;
    function show(r) {
      if (r === current) return;
      rows.forEach(function (x) { x.classList.toggle("on", x === r); });
      current = r;
      stage.style.setProperty("--tone", r.dataset.tone);
      var old = pic.querySelector("img:not(.out)"), next = document.createElement("img");
      next.src = r.dataset.cover; next.alt = ""; next.className = "out";
      pic.appendChild(next);
      if (old) old.classList.add("out");
      requestAnimationFrame(function () { requestAnimationFrame(function () { next.classList.remove("out"); }); });
      clearTimeout(timer);
      timer = setTimeout(function () { pic.querySelectorAll("img.out").forEach(function (i) { i.remove(); }); }, 700);
      cap.querySelector("small").textContent = r.dataset.sub;
      cap.querySelector("strong").textContent = r.dataset.title;
      cap.querySelector(".ch-stage__price").textContent = r.dataset.price;
    }
    rows.forEach(function (r) {
      r.addEventListener("pointerenter", function () { show(r); });
      r.addEventListener("focus", function () { show(r); });
    });
    show(rows[0]);
    window.chShow = show;
  })();
</script>"""

JS_3P = JS_3 + """
<script>
  // On the page, the row crossing the middle of the screen takes the stage as it scrolls.
  (function () {
    if (!("IntersectionObserver" in window)) return;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) window.chShow(e.target); });
    }, { rootMargin: "-48% 0px -48% 0px" });
    document.querySelectorAll(".ch-row").forEach(function (r) { io.observe(r); });
  })();
</script>"""

BUILDS.append((CSS_3, HOME_3, PAGE_3, JS_3, JS_3P,
               "A list of titles beside a stage that takes the colour of the book pointed at; on the page the stage is sticky and follows the scroll."))

# ============================================================================
# 4. The pile: the books lie one on another, spine out, each a plain band of
#    its colour with the name in small capitals. Pointing at one slides it
#    out of the pile, and its cover is propped up beside the pile with its
#    name and price. The page is a pile per category, alternating sides.
# ============================================================================
CSS_4 = """
.pl-top { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 1rem 2rem; margin-bottom: clamp(2rem, 4vw, 3rem); }
.pl-top h2, .pl-top h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(2.8rem, 2rem + 3vw, 4.4rem); font-weight: 500; line-height: 0.9; }
.pl-top p { color: var(--g-muted); font-size: 0.85rem; }
.pl-top a { display: inline-flex; align-items: center; gap: 0.7rem; margin-left: 1.2rem; color: var(--g-text); font-weight: 600; text-decoration: none; }
.pl-top a svg { width: 30px; transition: transform 0.3s var(--ease-out); }
.pl-top a:hover svg { transform: translateX(5px); }
.pl-lede { max-width: 34rem; margin-top: 1rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; }

.pl-scene { position: relative; display: grid; grid-template-columns: minmax(0, 0.9fr) minmax(150px, 0.55fr) minmax(0, 1.15fr); align-items: end; gap: clamp(1rem, 3vw, 2.5rem); padding-bottom: 18px; }
.pl-scene::after { content: ""; position: absolute; left: -2%; right: -2%; bottom: 0; height: 18px; border-radius: 3px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--g-text) 16%, transparent), color-mix(in oklab, var(--g-text) 6%, transparent));
  box-shadow: 0 1px 0 color-mix(in oklab, var(--g-text) 22%, transparent) inset, 0 22px 30px -20px rgba(40, 18, 4, 0.5); }
.pl-scene + .pl-scene { margin-top: clamp(4rem, 7vw, 6rem); }

/* The caption: what is propped up now. */
.pl-cap { padding-bottom: 1.6rem; color: var(--g-text); }
.pl-cap small { display: block; color: var(--g-accent); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.pl-cap strong { display: block; margin-top: 0.5rem; font-family: var(--display); font-size: clamp(1.8rem, 1.4rem + 1.4vw, 2.6rem); font-weight: 500; line-height: 1.02; }
.pl-cap span { display: block; margin-top: 0.9rem; font-family: var(--display); font-size: 1.6rem; font-weight: 600; font-variant-numeric: lining-nums; }
.pl-cap em { display: block; margin-bottom: 1.2rem; color: var(--g-muted); font-family: var(--display); font-size: 1.15rem; }

/* The cover, leaning on the pile. */
.pl-prop { position: relative; align-self: end; transform-origin: 100% 100%; transform: rotate(5deg); }
.pl-prop img { display: block; width: 100%; height: auto; border-radius: 3px 6px 6px 3px; box-shadow: 14px 18px 26px -10px rgba(30, 12, 2, 0.55); transition: opacity 0.3s, transform 0.5s var(--ease-out); }
.pl-prop img.out { opacity: 0; transform: translateY(-14px); }

/* The pile itself. */
.pl-pile { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; align-items: stretch; }
.pl-pile > li { display: flex; }
.pl-scene--flip .pl-pile > li { justify-content: flex-end; }
.pl-bar { --tone: #1c3f7a; position: relative; display: flex; align-items: center; justify-content: space-between; gap: 1rem; width: var(--w, 90%); height: var(--h, 36px); padding: 0 1.1rem;
  border-radius: 3px 4px 4px 3px; color: #fbeedd; text-decoration: none; transform: translateX(var(--o, 0)); transition: transform 0.45s var(--ease-out), filter 0.3s;
  background: linear-gradient(180deg, color-mix(in oklab, var(--tone) 70%, #fff) 0, var(--tone) 22%, var(--tone) 70%, color-mix(in oklab, var(--tone) 70%, #000));
  box-shadow: inset 6px 0 0 color-mix(in oklab, var(--tone) 60%, #000), inset -6px 0 0 color-mix(in oklab, var(--tone) 60%, #000), 0 2px 3px -1px rgba(20, 8, 2, 0.45); }
.pl-bar b { overflow: hidden; font-family: var(--ui); font-size: 0.74rem; font-weight: 600; letter-spacing: 0.16em; text-overflow: ellipsis; text-transform: uppercase; white-space: nowrap; }
.pl-bar span { flex: none; color: var(--gold-pale); font-size: 0.7rem; font-weight: 600; font-variant-numeric: tabular-nums; opacity: 0; transition: opacity 0.3s; }
.pl-bar:hover, .pl-bar:focus-visible, .pl-bar.on { transform: translateX(calc(var(--o, 0px) + 30px)); outline: none; }
.pl-bar.on span, .pl-bar:hover span, .pl-bar:focus-visible span { opacity: 1; }
.pl-bar:focus-visible { box-shadow: inset 6px 0 0 color-mix(in oklab, var(--tone) 60%, #000), 0 0 0 2px var(--gold); }
.pl-pile:hover .pl-bar:not(:hover) { filter: saturate(0.6) brightness(0.92); }

.pl-scene--flip { grid-template-columns: minmax(0, 1.15fr) minmax(150px, 0.55fr) minmax(0, 0.9fr); }
.pl-scene--flip .pl-pile { order: -2; align-items: flex-end; }
.pl-scene--flip .pl-prop { order: -1; transform-origin: 0 100%; transform: rotate(-5deg); }
.pl-scene--flip .pl-bar:hover, .pl-scene--flip .pl-bar:focus-visible, .pl-scene--flip .pl-bar.on { transform: translateX(calc(var(--o, 0px) - 30px)); }
.pl-scene--flip .pl-cap { text-align: right; }

@media (max-width: 760px) {
  .pl-scene, .pl-scene--flip { grid-template-columns: 120px minmax(0, 1fr); }
  .pl-pile, .pl-scene--flip .pl-pile { grid-column: 1 / -1; order: -2; align-items: stretch; }
  .pl-bar { width: calc(var(--w) + 4%); max-width: calc(100% - 34px); }
  .pl-prop, .pl-scene--flip .pl-prop { order: 0; transform: rotate(-3deg); }
  .pl-scene--flip .pl-cap { text-align: left; }
  .pl-scene--flip .pl-bar:hover, .pl-scene--flip .pl-bar.on { transform: translateX(calc(var(--o, 0px) + 30px)); }
}
"""

PL_W = ["92%", "80%", "96%", "85%", "76%", "89%", "82%"]
PL_H = [50, 40, 58, 44, 54, 42, 48]
PL_O = [0, 12, -4, 16, 6, -2, 10]


def pl_scene(books, title_html="", flip=False, cap_head=""):
    bars = "".join(
        f'<li><a class="pl-bar{" on" if k == 0 else ""}" href="#" style="--tone:{tone(b)};--w:{PL_W[k % 7]};--h:{PL_H[k % 7]}px;--o:{PL_O[k % 7]}px" '
        f'data-cover="{COVERS[b[0]]}" data-title="{esc(b[0])}" data-sub="{esc(b[1])}"><b>{esc(b[0])}</b><span>{PRICE}</span></a></li>'
        for k, b in enumerate(books))
    b = books[0]
    return f"""<div class="pl-scene{" pl-scene--flip" if flip else ""}">
        <div class="pl-cap" aria-hidden="true">{cap_head}<small>{esc(b[1])}</small><strong>{esc(b[0])}</strong><span>{PRICE}</span></div>
        <div class="pl-prop" aria-hidden="true">{img(b, lazy=False)}</div>
        <ol class="pl-pile">{bars}</ol>
      </div>"""


HOME_4 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <div class="pl-top"><h2 id="bs-h">Bookstore</h2><p>{COUNT} titles <a href="#">Visit the Bookstore {ARROW}</a></p></div>
      {pl_scene(FEATURED)}
    </div>
  </section>""")

PAGE_4 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="pl-top"><div><h1 id="bs-h">Bookstore</h1><p class="pl-lede">{LEDE}</p></div><p>{COUNT} titles</p></div>
      {"".join(f'<h2 class="sr-only">{esc(s)}</h2>' + pl_scene(shelf(s), flip=i % 2 == 1, cap_head=f"<em>{esc(s)} · {len(shelf(s))}</em>") for i, s in enumerate(SHELVES))}
    </div>
  </section>""")

JS_4 = """
<script>
  // A band pointed at, or focused, slides out and is propped up beside its pile.
  (function () {
    document.querySelectorAll(".pl-scene").forEach(function (sc) {
      var bars = sc.querySelectorAll(".pl-bar"), prop = sc.querySelector(".pl-prop"), cap = sc.querySelector(".pl-cap");
      function show(b) {
        if (b.classList.contains("on")) return;
        bars.forEach(function (x) { x.classList.toggle("on", x === b); });
        var im = prop.querySelector("img");
        im.classList.add("out");
        setTimeout(function () { im.src = b.dataset.cover; im.classList.remove("out"); }, 220);
        cap.querySelector("small").textContent = b.dataset.sub;
        cap.querySelector("strong").textContent = b.dataset.title;
      }
      bars.forEach(function (b) {
        b.addEventListener("pointerenter", function () { show(b); });
        b.addEventListener("focus", function () { show(b); });
      });
    });
  })();
</script>"""

BUILDS.append((CSS_4, HOME_4, PAGE_4, JS_4, JS_4,
               "The books lying in a pile, spine out; the one pointed at slides out and its cover is propped beside the pile. A pile per category on the page."))

# ============================================================================
# 5. Pinned run: the section holds still on the screen while scrolling
#    carries a row of books across it, the word BOOKSTORE drifting slowly
#    behind in outline, a counter and a line keeping count. It ends on a card
#    to the bookstore. Below 760px, or with reduced motion, it is a plain
#    sideways rail. The page: a rail per category, its name drifting behind.
# ============================================================================
CSS_5 = """
.ps { overflow-x: clip; }
.ps-stick { position: relative; display: flex; flex-direction: column; justify-content: center; gap: clamp(1.5rem, 3vh, 2.5rem); }
.ps-word { position: absolute; top: 50%; left: 0; z-index: -1; color: transparent; font-family: var(--display); font-size: clamp(9rem, 22vw, 20rem); font-style: italic; font-weight: 500; line-height: 1;
  white-space: nowrap; -webkit-text-stroke: 1.2px color-mix(in oklab, var(--g-text) 34%, transparent); transform: translate(0, -50%); pointer-events: none; }
.ps-head { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 1rem; }
.ps-head h2, .ps-head h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(2.4rem, 1.8rem + 2.4vw, 3.8rem); font-weight: 500; line-height: 0.9; }
.ps-head p { color: var(--g-muted); font-size: 0.8rem; font-variant-numeric: tabular-nums; letter-spacing: 0.14em; }
.ps-head p b { color: var(--g-text); font-family: var(--display); font-size: 2rem; letter-spacing: 0; }

.ps-track { display: flex; align-items: flex-start; gap: clamp(1.4rem, 3vw, 3rem); padding: 1rem max(var(--gutter), (100vw - 1180px) / 2) 2rem; will-change: transform;
  overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; overscroll-behavior-x: contain; }
.ps-track::-webkit-scrollbar { display: none; }
.ps-card { flex: none; width: clamp(200px, 21vw, 280px); color: var(--g-text); text-decoration: none; scroll-snap-align: start; }
.ps-card:nth-child(even) { margin-top: clamp(2rem, 6vh, 4.5rem); }
.ps-card img { display: block; width: 100%; height: auto; border-radius: 3px 7px 7px 3px; box-shadow: -14px 24px 34px -18px rgba(30, 12, 2, 0.65); transition: transform 0.5s var(--ease-out); }
.ps-card:hover img, .ps-card:focus-visible img { transform: translateY(-8px) rotate(-1.5deg); }
.ps-card:focus-visible { outline: none; }
.ps-card:focus-visible img { outline: 2px solid var(--rust); outline-offset: 5px; }
.ps-card__cap { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid var(--g-line); }
.ps-card__cap small { display: block; color: var(--g-accent); font-size: 0.58rem; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; }
.ps-card__cap strong { display: block; margin-top: 0.25rem; font-family: var(--display); font-size: 1.35rem; font-weight: 600; line-height: 1.1; }
.ps-card__cap span { flex: none; font-family: var(--display); font-size: 1.2rem; font-weight: 600; font-variant-numeric: lining-nums; }
.ps-card__n { display: block; margin-bottom: 0.7rem; color: var(--g-muted); font-size: 0.65rem; font-weight: 600; letter-spacing: 0.2em; }

.ps-end { flex: none; align-self: center; display: grid; place-content: center; gap: 1rem; width: clamp(220px, 22vw, 290px); aspect-ratio: 3 / 4; padding: 2rem; border-radius: 50% 50% 8px 8px / 30% 30% 8px 8px;
  background: var(--brown-ink); color: #fbeedd; text-align: center; text-decoration: none; scroll-snap-align: start; transition: transform 0.4s var(--ease-out); }
[data-theme="dark"] .ps-end { background: var(--gold); color: var(--espresso); }
.ps-end b { font-family: var(--display); font-size: 2rem; font-style: italic; font-weight: 500; line-height: 1.05; }
.ps-end span { font-size: 0.75rem; opacity: 0.75; }
.ps-end svg { width: 48px; margin-inline: auto; transition: transform 0.3s var(--ease-out); }
.ps-end:hover svg { transform: translateX(8px); }

.ps-bar { position: relative; height: 2px; background: var(--g-line); }
.ps-bar i { position: absolute; inset: 0 auto 0 0; width: 0; background: var(--rust); }
[data-theme="dark"] .ps-bar i { background: var(--gold); }

/* Pinned: the script sizes the run so its height pays for the row's width. */
.ps--pinned .ps-stick { position: sticky; top: 0; height: 100vh; overflow: hidden; }
.ps--pinned .ps-track { overflow: visible; scroll-snap-type: none; }
.r3-home > section.ps--pinned { padding-block: 0; }

/* The page: a rail per category. */
.ps-rail { position: relative; margin-top: clamp(3.5rem, 7vw, 6rem); }
.ps-rail .ps-word { font-size: clamp(6rem, 14vw, 12rem); top: 46%; }
.ps-rail .ps-track { cursor: grab; }
.ps-rail .ps-track.dragging { cursor: grabbing; scroll-snap-type: none; }
.ps-rail .ps-track.dragging a { pointer-events: none; }
.ps-rail h2 { color: var(--g-text); font-family: var(--display); font-size: 2.2rem; font-weight: 500; }
.ps-rail h2 span { margin-left: 0.8rem; color: var(--g-muted); font-family: var(--sans); font-size: 0.7rem; font-weight: 600; letter-spacing: 0.2em; }
.ps-lede { max-width: 34rem; margin-top: 1rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; }
"""


def ps_card(b, n):
    return (f'<a class="ps-card" href="#"><span class="ps-card__n">{n:02d}</span>{img(b)}<span class="ps-card__cap"><span style="font:inherit">'
            f'<small>{esc(b[1])}</small><strong>{esc(b[0])}</strong></span><span>{PRICE}</span></span></a>')


HOME_5 = home(f"""
  <section class="ps" aria-labelledby="bs-h">
    <div class="ps-run">
      <div class="ps-stick">
        <div class="ps-word" aria-hidden="true">Bookstore · Bookstore ·</div>
        <div class="r3-wrap ps-head"><h2 id="bs-h">Bookstore</h2><p><b class="ps-at">01</b> / {len(FEATURED):02d}</p></div>
        <div class="ps-track">{"".join(ps_card(b, i + 1) for i, b in enumerate(FEATURED))}
          <a class="ps-end" href="#"><b>Visit the Bookstore</b><span>{COUNT} titles</span>{ARROW}</a></div>
        <div class="r3-wrap ps-bar"><i></i></div>
      </div>
    </div>
  </section>""")

n = 0
ps_rails = []
for s in SHELVES:
    cards = []
    for b in shelf(s):
        n += 1
        cards.append(ps_card(b, n))
    ps_rails.append(f"""<section class="ps-rail" aria-labelledby="{cat_id(s)}">
        <div class="ps-word" aria-hidden="true">{esc(s)} · {esc(s)} ·</div>
        <div class="r3-wrap"><h2 id="{cat_id(s)}">{esc(s)}<span>{len(shelf(s))} titles</span></h2></div>
        <div class="ps-track">{"".join(cards)}</div>
        <div class="r3-wrap ps-bar"><i></i></div>
      </section>""")

PAGE_5 = page_main(f"""
  <div class="ps">
    <div class="r3-wrap ps-head" style="display:block"><a class="r3-back" href="#">← Home</a><h1 id="bs-h">Bookstore</h1><p class="ps-lede">{LEDE}</p></div>
    {"".join(ps_rails)}
  </div>""")

JS_5 = """
<script>
  // Pin the run: its height is the screen plus the row's overflow, and the
  // scroll through it moves the row, the word, the line and the count.
  (function () {
    var sec = document.querySelector("section.ps"), run = sec.querySelector(".ps-run"), track = sec.querySelector(".ps-track");
    var word = sec.querySelector(".ps-word"), bar = sec.querySelector(".ps-bar i"), at = sec.querySelector(".ps-at");
    var cards = track.querySelectorAll(".ps-card"), mq = matchMedia("(min-width: 761px) and (prefers-reduced-motion: no-preference)"), dist = 0;
    function size() {
      sec.classList.toggle("ps--pinned", mq.matches);
      track.style.transform = "";
      if (!mq.matches) { run.style.height = ""; tick(); return; }
      var last = track.lastElementChild;
      dist = Math.max(0, last.offsetLeft + last.offsetWidth + parseFloat(getComputedStyle(track).paddingRight) - innerWidth);
      run.style.height = innerHeight + dist + "px";
      tick();
    }
    function tick() {
      var p;
      if (mq.matches) {
        p = Math.min(1, Math.max(0, -run.getBoundingClientRect().top / Math.max(1, run.offsetHeight - innerHeight)));
        track.style.transform = "translateX(" + (-p * dist) + "px)";
        word.style.transform = "translate(" + (-p * 35) + "%, -50%)";
      } else {
        p = track.scrollLeft / Math.max(1, track.scrollWidth - track.clientWidth);
      }
      bar.style.width = p * 100 + "%";
      at.textContent = String(Math.min(cards.length, Math.floor(p * cards.length) + 1)).padStart(2, "0");
    }
    // A card reached by Tab is brought on screen by scrolling the page to its place in the run.
    track.addEventListener("focusin", function (e) {
      if (!mq.matches) return;
      var c = e.target.closest("a"); if (!c) return;
      var p = Math.min(1, Math.max(0, (c.offsetLeft - innerWidth * 0.3) / Math.max(1, dist)));
      scrollTo(0, run.getBoundingClientRect().top + scrollY + p * (run.offsetHeight - innerHeight));
    });
    addEventListener("scroll", tick, { passive: true }); track.addEventListener("scroll", tick, { passive: true });
    addEventListener("resize", size); mq.addEventListener("change", size);
    document.fonts && document.fonts.ready.then(size);
    size();
  })();
</script>"""

JS_5P = """
<script>
  // Each rail: a mouse drags it, the line under it keeps its place, the word behind drifts with it.
  (function () {
    document.querySelectorAll(".ps-rail").forEach(function (r) {
      var t = r.querySelector(".ps-track"), bar = r.querySelector(".ps-bar i"), word = r.querySelector(".ps-word"), down = null, moved = false;
      function tick() {
        var p = t.scrollLeft / Math.max(1, t.scrollWidth - t.clientWidth);
        bar.style.width = Math.max(8, p * 100) + "%";
        word.style.transform = "translate(" + (-p * 25) + "%, -50%)";
      }
      t.addEventListener("scroll", tick, { passive: true }); tick();
      t.addEventListener("pointerdown", function (e) { if (e.pointerType === "mouse" && e.button === 0) { down = { x: e.clientX, l: t.scrollLeft }; moved = false; } });
      addEventListener("pointermove", function (e) {
        if (!down) return;
        var dx = e.clientX - down.x;
        if (!moved && Math.abs(dx) > 6) { moved = true; t.classList.add("dragging"); }
        if (moved) t.scrollLeft = down.l - dx;
      });
      addEventListener("pointerup", function () { if (down) { down = null; t.classList.remove("dragging"); } });
      t.addEventListener("click", function (e) { if (moved) { e.preventDefault(); moved = false; } }, true);
    });
  })();
</script>"""

BUILDS.append((CSS_5, HOME_5, PAGE_5, JS_5, JS_5P,
               "The section holds still while scrolling carries a row of books across it, a huge word drifting behind; the page is a rail per category."))

# ============================================================================
# 6. Opening books: each book has pages behind its cover. Pointing at it (or
#    focusing it) swings the cover open toward you, showing the endpaper in
#    its binding's colour and the title page, where the subject, the name and
#    the price are set. On a touch screen the first tap opens it. The page
#    filters by category under a sliding underline that sticks to the top.
# ============================================================================
CSS_6 = """
.ob-head { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 1rem 2rem; margin-bottom: clamp(2.5rem, 5vw, 4rem); }
.ob-head h2, .ob-head h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(2.6rem, 1.9rem + 2.6vw, 4.2rem); font-weight: 500; line-height: 0.9; }
.ob-head h2 i, .ob-head h1 i { color: var(--g-muted); font-weight: 400; }
.ob-head a { display: inline-flex; align-items: center; gap: 0.7rem; padding-bottom: 0.3rem; border-bottom: 1px solid currentColor; color: var(--g-text); font-weight: 600; font-size: 0.85rem; text-decoration: none; }
.ob-head a svg { width: 28px; }
.ob-lede { max-width: 34rem; margin-top: 1rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; }

.ob-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: clamp(2.5rem, 5vw, 4rem) clamp(1rem, 3vw, 2.5rem); }
.ob { display: block; color: var(--g-text); text-decoration: none; perspective: 1600px; -webkit-tap-highlight-color: transparent; }
.ob:focus-visible { outline: none; }
.ob-book { position: relative; display: block; width: 58%; margin-left: 37%; aspect-ratio: 3 / 4; transform-style: preserve-3d; transform: rotateY(-26deg) rotateX(4deg); transition: transform 1s cubic-bezier(0.3, 0.7, 0.2, 1); }
.ob-book::before { content: ""; position: absolute; top: 3px; bottom: 3px; left: calc(100% - 2px); width: 22px; transform-origin: 0 50%; transform: rotateY(90deg);
  background: linear-gradient(90deg, rgba(0, 0, 0, 0.18), transparent 40%), repeating-linear-gradient(90deg, #f6eedf 0 1px, #dccdb1 1px 2px); }
.ob-book::after { content: ""; position: absolute; left: 6%; right: 2%; bottom: -14px; height: 22px; border-radius: 50%; background: rgba(40, 18, 4, 0.35); filter: blur(10px); transform: translateZ(-30px); }
.ob:hover .ob-book, .ob:focus-visible .ob-book, .ob.open .ob-book { transform: rotateY(-8deg) rotateX(2deg); }

/* The title page, with the block of pages showing at its edges. */
.ob-page { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.5rem; padding: 12% 10%;
  border-radius: 2px 5px 5px 2px; background: linear-gradient(90deg, rgba(60, 30, 10, 0.14), transparent 14%), #fbf5ea; color: var(--brown-ink); text-align: center;
  box-shadow: inset 0 0 0 1px rgba(120, 80, 40, 0.12); }
.ob-page small { color: color-mix(in oklab, var(--tone) 60%, #7d5006); font-size: 0.55rem; font-weight: 600; letter-spacing: 0.26em; text-transform: uppercase; }
.ob-page strong { font-family: var(--display); font-size: clamp(1rem, 0.85rem + 0.5vw, 1.3rem); font-weight: 600; line-height: 1.1; }
.ob-page hr { width: 34px; height: 1px; margin: 0.3rem 0; border: 0; background: color-mix(in oklab, var(--tone) 50%, #c9a457); }
.ob-page b { font-family: var(--display); font-size: clamp(1.3rem, 1rem + 0.8vw, 1.7rem); font-weight: 600; font-variant-numeric: lining-nums; }
.ob-page em { color: rgba(70, 44, 22, 0.7); font-family: var(--display); font-size: 0.9rem; }

/* The cover: turns on its left edge; its back is the endpaper. */
.ob-cover { position: absolute; inset: 0; transform-origin: 0 50%; transform: translateZ(1px); transform-style: preserve-3d; transition: transform 1s cubic-bezier(0.3, 0.7, 0.2, 1); }
.ob-cover img, .ob-cover__back { position: absolute; inset: 0; width: 100%; height: 100%; border-radius: 2px 5px 5px 2px; backface-visibility: hidden; }
.ob-cover img { box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.2), 10px 16px 26px -12px rgba(30, 12, 2, 0.55); }
.ob-cover__back { transform: rotateY(180deg); border-radius: 5px 2px 2px 5px;
  background: linear-gradient(270deg, rgba(0, 0, 0, 0.3), transparent 18%), radial-gradient(120% 80% at 30% 20%, color-mix(in oklab, var(--tone) 75%, #fff), var(--tone)); }
.ob:hover .ob-cover, .ob:focus-visible .ob-cover, .ob.open .ob-cover { transform: translateZ(1px) rotateY(-128deg); }
.ob:focus-visible .ob-page { outline: 2px solid var(--rust); outline-offset: 6px; }
.ob-name { display: block; width: 58%; margin: 1.1rem 0 0 37%; font-family: var(--display); font-size: 1.15rem; font-weight: 600; line-height: 1.15; }
.ob-name small { display: block; margin-top: 0.2rem; color: var(--g-muted); font-family: var(--sans); font-size: 0.7rem; font-weight: 500; }

/* The page: categories with a sliding underline, stuck to the top. */
.ob-tabs { position: sticky; top: 0; z-index: 20; display: flex; gap: clamp(1rem, 3vw, 2.4rem); margin: 0 0 clamp(2rem, 4vw, 3rem); padding: 1rem 0 0; overflow-x: auto; scrollbar-width: none;
  background: linear-gradient(180deg, var(--bg-color) 70%, transparent); border-bottom: 1px solid var(--g-line); }
.ob-tabs button { position: relative; flex: none; padding: 0.4rem 0 0.9rem; border: 0; background: none; color: var(--g-muted); font: 500 0.88rem var(--sans); cursor: pointer; }
.ob-tabs button[aria-pressed="true"], .ob-tabs button:hover { color: var(--g-text); }
.ob-tabs i { position: absolute; bottom: -1px; left: 0; height: 2px; background: var(--rust); transition: transform 0.45s var(--ease-out), width 0.45s var(--ease-out); }
[data-theme="dark"] .ob-tabs i { background: var(--gold); }

@media (max-width: 900px) { .ob-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) { .ob-grid { grid-template-columns: minmax(0, 1fr); } .ob-book, .ob-name { width: 52%; margin-left: 40%; } }
@media (prefers-reduced-motion: reduce) { .ob-cover { transition: none; } }
"""


def ob_book(b):
    return (f'<a class="ob" href="#" style="--tone:{tone(b)}" data-cat="{cat_id(b[2])}"><span class="ob-book">'
            f'<span class="ob-page"><small>{esc(b[1])}</small><strong>{esc(b[0])}</strong><hr><b>{PRICE}</b><em>{esc(b[2])}</em></span>'
            f'<span class="ob-cover">{img(b)}<span class="ob-cover__back"></span></span></span>'
            f'<span class="ob-name">{esc(b[0])}<small>{esc(b[1])}</small></span></a>')


HOME_6 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <div class="ob-head"><h2 id="bs-h">Bookstore <i>· {COUNT} titles</i></h2><a href="#">Visit the Bookstore {ARROW}</a></div>
      <div class="ob-grid">{"".join(ob_book(b) for b in FEATURED)}</div>
    </div>
  </section>""")

PAGE_6 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="ob-head"><div><h1 id="bs-h">Bookstore</h1><p class="ob-lede">{LEDE}</p></div></div>
      <div class="ob-tabs" role="group" aria-label="Category"><button type="button" aria-pressed="true" data-f="all">All</button>{"".join(f'<button type="button" aria-pressed="false" data-f="{cat_id(s)}">{esc(s)}</button>' for s in SHELVES)}<i></i></div>
      <div class="ob-grid">{"".join(ob_book(b) for b in BOOKS)}</div>
    </div>
  </section>""")

JS_6 = """
<script>
  // On a touch screen the first tap opens a book and the second follows it.
  (function () {
    if (matchMedia("(hover: hover)").matches) return;
    document.querySelectorAll(".ob").forEach(function (b) {
      b.addEventListener("click", function (e) {
        if (b.classList.contains("open")) return;
        e.preventDefault();
        document.querySelectorAll(".ob.open").forEach(function (o) { o.classList.remove("open"); });
        b.classList.add("open");
      });
    });
  })();
</script>"""

JS_6P = JS_6 + """
<script>
  // The tabs filter the books; the underline slides to the pressed one.
  (function () {
    var tabs = document.querySelectorAll(".ob-tabs button"), line = document.querySelector(".ob-tabs i");
    function place(t) { line.style.width = t.offsetWidth + "px"; line.style.transform = "translateX(" + t.offsetLeft + "px)"; }
    tabs.forEach(function (t) {
      t.addEventListener("click", function () {
        tabs.forEach(function (x) { x.setAttribute("aria-pressed", String(x === t)); });
        place(t);
        document.querySelectorAll(".ob-grid .ob").forEach(function (b) { b.hidden = t.dataset.f !== "all" && b.dataset.cat !== t.dataset.f; });
      });
    });
    place(tabs[0]);
    document.fonts && document.fonts.ready.then(function () { place(document.querySelector('.ob-tabs [aria-pressed="true"]')); });
  })();
</script>"""

BUILDS.append((CSS_6, HOME_6, PAGE_6, JS_6, JS_6P,
               "Books with pages behind their covers, which swing open to show the endpaper and a title page with the price; the page filters under a sliding underline."))

# ============================================================================
# 7. Marquee: two rows of covers drift in opposite directions, every book
#    passing by; the edges fade. Pointing at a row stops it, the cover under
#    the pointer comes forward and the others dim. Focus stops it too. With
#    reduced motion the rows are still and scroll sideways. The page has one
#    marquee as a band over a grid that rises into view, with category chips.
# ============================================================================
CSS_7 = """
.mq-head { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: end; gap: 1rem 2rem; margin-bottom: clamp(2rem, 4vw, 3rem); }
.mq-head h2, .mq-head h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(3rem, 2rem + 4vw, 5.6rem); font-weight: 500; letter-spacing: -0.015em; line-height: 0.85; }
.mq-head h2 span, .mq-head h1 span { display: block; color: var(--g-muted); font-size: 0.4em; font-style: italic; letter-spacing: 0; }
.mq-go { display: inline-flex; align-items: center; gap: 0.8rem; padding: 0.95rem 1.4rem; border-radius: 999px; background: var(--brown-ink); color: #fbeedd; font-size: 0.82rem; font-weight: 500; text-decoration: none; }
[data-theme="dark"] .mq-go { background: var(--gold); color: var(--espresso); }
.mq-go svg { width: 26px; transition: transform 0.3s var(--ease-out); }
.mq-go:hover svg { transform: translateX(5px); }

.mq-row { --speed: 70s; overflow: hidden; padding-block: 1.2rem 0.6rem;
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 9%, #000 91%, transparent); mask-image: linear-gradient(90deg, transparent, #000 9%, #000 91%, transparent); }
.mq-row + .mq-row { margin-top: 0.6rem; }
.mq-track { display: flex; gap: clamp(1rem, 2vw, 1.8rem); width: max-content; animation: mq var(--speed) linear infinite; }
.mq-row--back .mq-track { animation-direction: reverse; }
.mq-row:hover .mq-track, .mq-row:focus-within .mq-track { animation-play-state: paused; }
@keyframes mq { to { transform: translateX(calc(-50% - clamp(1rem, 2vw, 1.8rem) / 2)); } }

.mq-item { flex: none; width: clamp(130px, 13vw, 170px); color: var(--g-text); text-decoration: none; transition: opacity 0.35s, transform 0.45s var(--ease-out); }
.mq-item img { display: block; width: 100%; height: auto; border-radius: 3px 6px 6px 3px; box-shadow: 0 16px 24px -14px rgba(30, 12, 2, 0.65); }
.mq-item b { display: block; margin-top: 0.75rem; overflow: hidden; font-family: var(--display); font-size: 1.02rem; font-weight: 600; line-height: 1.15; text-overflow: ellipsis; white-space: nowrap; }
.mq-item span { display: block; margin-top: 0.15rem; color: var(--g-muted); font-size: 0.72rem; font-variant-numeric: tabular-nums; }
.mq-row:hover .mq-item:not(:hover), .mq-row:focus-within .mq-item:not(:focus-visible) { opacity: 0.45; }
.mq-item:hover, .mq-item:focus-visible { transform: translateY(-8px) scale(1.06); outline: none; }
.mq-item:focus-visible img { outline: 2px solid var(--rust); outline-offset: 4px; }

/* The page: a band, then the grid. */
.mq-band { margin-bottom: clamp(3rem, 6vw, 5rem); }
.mq-band .mq-item { width: clamp(100px, 9vw, 130px); }
.mq-band .mq-item b, .mq-band .mq-item span { display: none; }
.mq-lede { max-width: 34rem; margin-top: 1.2rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; }
.mq-chips { display: flex; flex-wrap: wrap; gap: 0.3rem 1.6rem; margin-bottom: 2.2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--g-line); }
.mq-chips button { padding: 0.3rem 0; border: 0; background: none; color: var(--g-muted); font-family: var(--display); font-size: 1.4rem; font-weight: 500; cursor: pointer; }
.mq-chips button sup { margin-left: 0.2rem; font-family: var(--sans); font-size: 0.6rem; }
.mq-chips button[aria-pressed="true"] { color: var(--g-text); font-style: italic; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 6px; }
.mq-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 2.6rem clamp(1rem, 2.5vw, 2rem); }
.mq-grid .mq-item { width: auto; }
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .mq-grid .mq-item { animation: mq-rise linear both; animation-timeline: view(); animation-range: entry 0% entry 70%; }
  }
}
@keyframes mq-rise { from { opacity: 0; transform: translateY(40px) scale(0.96); } }

@media (prefers-reduced-motion: reduce) {
  .mq-track { animation: none; }
  .mq-row { overflow-x: auto; -webkit-mask-image: none; mask-image: none; }
  .mq-track [aria-hidden="true"] { display: none; }
}
@media (max-width: 600px) { .mq-head { grid-template-columns: minmax(0, 1fr); } }
"""


def mq_item(b, hidden=False):
    h = ' aria-hidden="true" tabindex="-1"' if hidden else ""
    return f'<a class="mq-item" href="#" data-cat="{cat_id(b[2])}"{h}>{img(b)}<b>{esc(b[0])}</b><span>{esc(b[1])} · {PRICE}</span></a>'


def mq_row(books, back=False, speed=70):
    # Each set twice, the second hidden, so the loop is seamless.
    return (f'<div class="mq-row{" mq-row--back" if back else ""}" style="--speed:{speed}s"><div class="mq-track">'
            + "".join(mq_item(b) for b in books) + "".join(mq_item(b, True) for b in books) + "</div></div>")


HOME_7 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap mq-head"><h2 id="bs-h">Bookstore<span>{COUNT} titles, sold at the masjid</span></h2><a class="mq-go" href="#">Visit the Bookstore {ARROW}</a></div>
    {mq_row(BOOKS[:9], speed=60)}
    {mq_row(BOOKS[9:], back=True, speed=72)}
  </section>""")

PAGE_7 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap"><a class="r3-back" href="#">← Home</a></div>
    <div class="r3-wrap mq-head"><div><h1 id="bs-h">Bookstore</h1><p class="mq-lede">{LEDE}</p></div></div>
    <div class="mq-band" aria-hidden="true">{mq_row(BOOKS, speed=90).replace('class="mq-item" href="#"', 'class="mq-item" tabindex="-1" href="#"')}</div>
    <div class="r3-wrap">
      <div class="mq-chips" role="group" aria-label="Category"><button type="button" aria-pressed="true" data-f="all">All<sup>{COUNT}</sup></button>{"".join(f'<button type="button" aria-pressed="false" data-f="{cat_id(s)}">{esc(s)}<sup>{len(shelf(s))}</sup></button>' for s in SHELVES)}</div>
      <div class="mq-grid">{"".join(mq_item(b) for b in BOOKS)}</div>
    </div>
  </section>""")

JS_7P = """
<script>
  (function () {
    var chips = document.querySelectorAll(".mq-chips button");
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        chips.forEach(function (x) { x.setAttribute("aria-pressed", String(x === c)); });
        document.querySelectorAll(".mq-grid .mq-item").forEach(function (b) { b.hidden = c.dataset.f !== "all" && b.dataset.cat !== c.dataset.f; });
      });
    });
  })();
</script>"""

BUILDS.append((CSS_7, HOME_7, PAGE_7, "", JS_7P,
               "Two rows of covers drifting in opposite directions, stopping under the pointer; the page has the marquee as a band over a grid that rises into view."))

# ============================================================================
# 8. Salon wall: the covers framed and mounted, hung on wires at three sizes
#    about one centre line, each numbered on the wall; beside the wall is the
#    key, as in a gallery: number, name, subject and price. Pointing at a
#    picture lights it and its line in the key, and the other way round.
#    Black frames in light, gilt in dark. The page is one wall of every book,
#    the key held beside it by category.
# ============================================================================
CSS_8 = """
.sw { --mount: #fbf7ef; --mould: #24150a; --mould-2: #5a3b24; --wire: rgba(70, 44, 22, 0.55); --disc: var(--brown-ink); --disc-ink: #fbeedd; --glow: rgba(255, 214, 140, 0.55); }
[data-theme="dark"] .sw { --mount: #efe4cf; --mould: #b98b3c; --mould-2: #5e4013; --wire: rgba(227, 179, 74, 0.5); --disc: var(--gold); --disc-ink: var(--espresso); --glow: rgba(255, 196, 100, 0.28); }
.sw-grid { display: grid; grid-template-columns: minmax(0, 1fr) 290px; gap: clamp(2rem, 4vw, 4rem); align-items: start; }

.sw-wall { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 70px 48px; padding: 48px 0 20px; }
.sw-frame { --fw: 170px; position: relative; z-index: 0; display: block; width: var(--fw); padding: calc(var(--fw) * 0.11); background: var(--mount); text-decoration: none;
  box-shadow: 0 0 0 7px var(--mould), 0 0 0 8px var(--mould-2), 0 26px 34px -16px rgba(30, 12, 2, 0.6); transition: transform 0.45s var(--ease-out); }
.sw-frame--l { --fw: 220px; }
.sw-frame--s { --fw: 136px; }
.sw-frame img { display: block; width: 100%; height: auto; box-shadow: 0 0 0 3px #fff, 0 0 0 4px rgba(60, 40, 20, 0.18); }
[data-theme="dark"] .sw-frame img { box-shadow: 0 0 0 3px #faf3e4, 0 0 0 4px rgba(60, 40, 20, 0.25); }
/* The wire to its hook, and the light that comes on. */
.sw-frame::before { content: ""; position: absolute; bottom: calc(100% + 7px); left: 22%; right: 22%; height: 34px; background: var(--wire);
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 34' preserveAspectRatio='none'%3E%3Cpath d='M0 34 50 1 100 34' fill='none' stroke='%23000' stroke-width='1.6' vector-effect='non-scaling-stroke'/%3E%3C/svg%3E") 0 0 / 100% 100%;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 34' preserveAspectRatio='none'%3E%3Cpath d='M0 34 50 1 100 34' fill='none' stroke='%23000' stroke-width='1.6' vector-effect='non-scaling-stroke'/%3E%3C/svg%3E") 0 0 / 100% 100%; }
.sw-frame::after { content: ""; position: absolute; bottom: calc(100% + 38px); left: 50%; width: 7px; height: 7px; margin-left: -3.5px; border-radius: 50%; background: var(--wire); }
.sw-light { position: absolute; inset: -45% -40%; z-index: -1; background: radial-gradient(closest-side, var(--glow), transparent); opacity: 0; transition: opacity 0.5s; pointer-events: none; }
.sw-num { position: absolute; right: -24px; bottom: -24px; display: grid; place-items: center; width: 26px; height: 26px; border-radius: 50%; background: var(--disc); color: var(--disc-ink); font-size: 0.66rem; font-weight: 600; font-variant-numeric: tabular-nums; }
.sw-frame:hover, .sw-frame:focus-visible, .sw-frame.hi { transform: translateY(-4px); outline: none; }
.sw-frame:hover .sw-light, .sw-frame:focus-visible .sw-light, .sw-frame.hi .sw-light { opacity: 1; }
.sw-frame:focus-visible { box-shadow: 0 0 0 7px var(--mould), 0 0 0 8px var(--mould-2), 0 0 0 11px var(--rust), 0 26px 34px -16px rgba(30, 12, 2, 0.6); }

/* The key. */
.sw-key h2, .sw-key h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(2.4rem, 1.8rem + 2vw, 3.4rem); font-weight: 500; line-height: 0.95; }
.sw-key > p { margin: 0.6rem 0 1.4rem; color: var(--g-muted); font-size: 0.78rem; }
.sw-key ol { list-style: none; margin: 0; padding: 0; }
.sw-key li a { display: grid; grid-template-columns: 26px minmax(0, 1fr); gap: 0.8rem; padding: 0.7rem 0.4rem; border-top: 1px solid var(--g-line); color: var(--g-text); text-decoration: none; transition: background 0.25s; }
.sw-key li a span:first-child { display: grid; place-items: center; width: 22px; height: 22px; margin-top: 2px; border: 1px solid var(--g-line); border-radius: 50%; font-size: 0.6rem; font-weight: 600; }
.sw-key li a b { display: block; font-family: var(--display); font-size: 1.15rem; font-style: italic; font-weight: 600; line-height: 1.15; }
.sw-key li a small { display: block; margin-top: 0.15rem; color: var(--g-muted); font-size: 0.72rem; }
.sw-key li a:hover, .sw-key li a:focus-visible, .sw-key li a.hi { background: color-mix(in oklab, var(--g-text) 7%, transparent); outline: none; }
.sw-key li a.hi span:first-child, .sw-key li a:hover span:first-child { background: var(--disc); border-color: var(--disc); color: var(--disc-ink); }
.sw-key h3 { margin: 1.6rem 0 0.4rem; color: var(--g-accent); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.sw-visit { display: inline-flex; align-items: center; gap: 0.7rem; margin-top: 1.4rem; color: var(--g-text); font-family: var(--display); font-size: 1.25rem; font-style: italic; font-weight: 600; text-decoration: none; }
.sw-visit svg { width: 34px; transition: transform 0.3s var(--ease-out); }
.sw-visit:hover svg { transform: translateX(6px); }
.r3-page .sw-grid > .sw-key { position: sticky; top: 1.5rem; max-height: calc(100vh - 3rem); overflow-y: auto; scrollbar-width: thin; }
.sw-lede { max-width: 40rem; margin: 0.8rem 0 2.4rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; }

@media (max-width: 900px) {
  .sw-grid { grid-template-columns: minmax(0, 1fr); }
  .r3-page .sw-grid > .sw-key { position: static; max-height: none; }
  .sw-home .sw-key { order: -1; }
}
@media (max-width: 560px) {
  .sw-wall { gap: 64px 40px; }
  .sw-frame { --fw: 132px; } .sw-frame--l { --fw: 168px; } .sw-frame--s { --fw: 112px; }
}
"""

SW_SIZES = ["l", "s", "m", "m", "l", "s", "m", "s", "l", "m", "s", "m"]


def sw_frame(b, n):
    sz = SW_SIZES[(n - 1) % len(SW_SIZES)]
    return (f'<a class="sw-frame sw-frame--{sz}" href="#" data-n="{n}" aria-label="{n}. {esc(b[0])}, {PRICE}"><span class="sw-light"></span>{img(b)}'
            f'<span class="sw-num" aria-hidden="true">{n}</span></a>')


def sw_key_row(b, n):
    return f'<li><a href="#" data-n="{n}"><span>{n}</span><span><b>{esc(b[0])}</b><small>{esc(b[1])} · {PRICE}</small></span></a></li>'


HOME_8 = home(f"""
  <section class="sw" aria-labelledby="bs-h">
    <div class="r3-wrap sw-grid sw-home">
      <div class="sw-wall">{"".join(sw_frame(b, i + 1) for i, b in enumerate(FEATURED))}</div>
      <div class="sw-key">
        <h2 id="bs-h">Bookstore</h2><p>On the wall: {len(FEATURED)} of {COUNT} titles</p>
        <ol>{"".join(sw_key_row(b, i + 1) for i, b in enumerate(FEATURED))}</ol>
        <a class="sw-visit" href="#">Visit the Bookstore {ARROW}</a>
      </div>
    </div>
  </section>""")

n = 0
sw_frames, sw_keys = [], []
for s in SHELVES:
    rows = []
    for b in shelf(s):
        n += 1
        sw_frames.append(sw_frame(b, n))
        rows.append(sw_key_row(b, n))
    sw_keys.append(f'<h3>{esc(s)}</h3><ol>{"".join(rows)}</ol>')

PAGE_8 = page_main(f"""
  <section class="sw" aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="sw-grid">
        <div><div class="sw-key"><h1 id="bs-h">Bookstore</h1></div><p class="sw-lede">{LEDE}</p>
          <div class="sw-wall">{"".join(sw_frames)}</div></div>
        <div class="sw-key"><p>The key: {COUNT} titles</p>{"".join(sw_keys)}</div>
      </div>
    </div>
  </section>""")

JS_8 = """
<script>
  // A picture and its line in the key light together.
  (function () {
    var all = document.querySelectorAll(".sw [data-n]");
    function hi(n) { all.forEach(function (x) { x.classList.toggle("hi", x.dataset.n === n); }); }
    all.forEach(function (x) {
      x.addEventListener("pointerenter", function () { hi(x.dataset.n); });
      x.addEventListener("pointerleave", function () { hi(null); });
      x.addEventListener("focus", function () { hi(x.dataset.n); });
      x.addEventListener("blur", function () { hi(null); });
    });
  })();
</script>"""

BUILDS.append((CSS_8, HOME_8, PAGE_8, JS_8, JS_8,
               "The covers framed and hung on wires like a gallery wall, numbered, with a key beside them; pointing lights a picture and its line."))

# ============================================================================
# 9. Accordion: the books stand as tall strips of their colour, the name
#    running up each; the open one widens to show its cover, subject, name
#    and price. Pointing at a strip or focusing it opens it. On phones the
#    strips lie down and open downward. The page is one per category.
# ============================================================================
CSS_9 = """
.ac-head { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 1rem 2rem; margin-bottom: clamp(2rem, 4vw, 3rem); }
.ac-head h2, .ac-head h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(2.6rem, 1.9rem + 2.6vw, 4.2rem); font-weight: 500; line-height: 0.9; }
.ac-head p { color: var(--g-muted); font-size: 0.85rem; }
.ac-head a { display: inline-flex; align-items: center; gap: 0.7rem; color: var(--g-text); font-weight: 600; font-size: 0.85rem; text-decoration: none; }
.ac-head a svg { width: 30px; transition: transform 0.3s var(--ease-out); }
.ac-head a:hover svg { transform: translateX(5px); }
.ac-lede { max-width: 34rem; margin-top: 1rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; }

.ac { display: flex; gap: 8px; height: clamp(420px, 40vw, 500px); }
.ac-strip { --tone: #1c3f7a; position: relative; flex: 1 1 0; min-width: 62px; overflow: hidden; border-radius: 18px; color: #fbeedd; text-decoration: none;
  background: linear-gradient(160deg, color-mix(in oklab, var(--tone) 72%, #fff), var(--tone) 40%, color-mix(in oklab, var(--tone) 70%, #000));
  transition: flex-grow 0.7s var(--ease-out), box-shadow 0.4s; }
.ac-strip.on { flex-grow: 6; box-shadow: 0 30px 50px -30px color-mix(in oklab, var(--tone) 80%, #000); }
.ac-strip:focus-visible { outline: 2px solid var(--rust); outline-offset: 3px; }
/* Closed: a number at the head, the name running up. */
.ac-strip__n { position: absolute; top: 1.1rem; left: 0; right: 0; text-align: center; font-size: 0.66rem; font-weight: 600; letter-spacing: 0.12em; opacity: 0.75; }
.ac-strip__spine { position: absolute; bottom: 1.3rem; left: 50%; max-height: calc(100% - 4.5rem); overflow: hidden; font-family: var(--display); font-size: 1.2rem; font-weight: 600; white-space: nowrap; text-overflow: ellipsis;
  writing-mode: vertical-rl; transform: translateX(-50%) rotate(180deg); transition: opacity 0.3s; }
.ac-strip.on .ac-strip__spine { opacity: 0; }
/* Open: the cover and the words. */
.ac-strip__body { position: absolute; inset: 0; display: grid; grid-template-columns: auto minmax(0, 1fr); align-items: end; gap: clamp(1.2rem, 3vw, 2.4rem); padding: clamp(1.4rem, 3vw, 2.6rem);
  opacity: 0; transform: translateY(12px); transition: opacity 0.3s, transform 0.5s var(--ease-out); pointer-events: none; }
.ac-strip.on .ac-strip__body { opacity: 1; transform: none; transition-delay: 0.25s; }
.ac-strip__body img { width: clamp(150px, 15vw, 210px); height: auto; border-radius: 3px 6px 6px 3px; box-shadow: -14px 26px 40px -14px rgba(0, 0, 0, 0.6); }
.ac-strip__body small { display: block; color: var(--gold-pale); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.ac-strip__body strong { display: block; margin-top: 0.5rem; font-family: var(--display); font-size: clamp(1.7rem, 1.2rem + 1.6vw, 2.8rem); font-weight: 500; line-height: 1.02; }
.ac-strip__body b { display: inline-block; margin-top: 1.2rem; padding: 0.45rem 0.9rem; border: 1px solid rgba(251, 238, 221, 0.4); border-radius: 999px; font-size: 0.85rem; font-weight: 600; font-variant-numeric: tabular-nums; }
.ac-strip__body span { min-width: 0; }

.ac-cat { margin: clamp(3rem, 6vw, 4.5rem) 0 1rem; color: var(--g-text); font-family: var(--display); font-size: 2rem; font-weight: 500; }
.ac-cat span { margin-left: 0.7rem; color: var(--g-muted); font-family: var(--sans); font-size: 0.68rem; font-weight: 600; letter-spacing: 0.2em; }
.r3-page .ac { height: clamp(380px, 34vw, 440px); }

@media (max-width: 760px) {
  .ac, .r3-page .ac { flex-direction: column; height: auto; }
  .ac-strip { flex: none; min-width: 0; height: 58px; transition: height 0.6s var(--ease-out); }
  .ac-strip.on { height: 340px; }
  .ac-strip__n { top: 50%; left: 1.1rem; right: auto; transform: translateY(-50%); }
  .ac-strip__spine { top: 50%; bottom: auto; left: 3.2rem; right: 1rem; max-height: none; writing-mode: horizontal-tb; transform: translateY(-50%); }
  .ac-strip__body { grid-template-columns: 120px minmax(0, 1fr); }
  .ac-strip__body img { width: 120px; }
}
"""


def ac_strip(b, n, on=False):
    return (f'<a class="ac-strip{" on" if on else ""}" href="#" style="--tone:{tone(b)}"><span class="ac-strip__n">{n:02d}</span>'
            f'<span class="ac-strip__spine">{esc(b[0])}</span>'
            f'<span class="ac-strip__body">{img(b)}<span><small>{esc(b[1])}</small><strong>{esc(b[0])}</strong><b>{PRICE}</b></span></span></a>')


HOME_9 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <div class="ac-head"><div><h2 id="bs-h">Bookstore</h2></div><p>{COUNT} titles &nbsp; <a href="#">Visit the Bookstore {ARROW}</a></p></div>
      <div class="ac">{"".join(ac_strip(b, i + 1, i == 0) for i, b in enumerate(FEATURED))}</div>
    </div>
  </section>""")

n = 0
ac_cats = []
for s in SHELVES:
    strips = []
    for k, b in enumerate(shelf(s)):
        n += 1
        strips.append(ac_strip(b, n, k == 0))
    ac_cats.append(f'<h2 class="ac-cat">{esc(s)}<span>{len(shelf(s))} titles</span></h2><div class="ac">{"".join(strips)}</div>')

PAGE_9 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="ac-head"><div><h1 id="bs-h">Bookstore</h1><p class="ac-lede">{LEDE}</p></div></div>
      {"".join(ac_cats)}
    </div>
  </section>""")

JS_9 = """
<script>
  // The strip pointed at, or focused, opens; the others in its row close.
  (function () {
    document.querySelectorAll(".ac").forEach(function (row) {
      var strips = row.querySelectorAll(".ac-strip");
      function open(s) { strips.forEach(function (x) { x.classList.toggle("on", x === s); }); }
      strips.forEach(function (s) {
        s.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse") open(s); });
        s.addEventListener("focus", function () { open(s); });
        s.addEventListener("click", function (e) { if (!s.classList.contains("on")) { e.preventDefault(); open(s); } });
      });
    });
  })();
</script>"""

BUILDS.append((CSS_9, HOME_9, PAGE_9, JS_9, JS_9,
               "Tall strips in each book's colour with the name running up; the open one widens to show its cover and price. One per category on the page."))

# ============================================================================
# 10. Deck: the covers as a stack of cards, each the whole cover with its
#     name and price over its foot. Throw the top one away (drag it, use the
#     arrows or the arrow keys) and it tucks in at the back. The page deals a
#     deck per category, has a contact strip of the deck to jump through it,
#     and a Deck | Spread switch that lays every card out.
# ============================================================================
CSS_10 = """
.dk-grid { display: grid; grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr); gap: clamp(2rem, 5vw, 4rem); align-items: center; }
.dk-intro h2, .dk-intro h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(3rem, 2rem + 3.6vw, 5.2rem); font-weight: 500; letter-spacing: -0.01em; line-height: 0.88; }
.dk-intro > p { margin-top: 1rem; color: var(--g-muted); font-size: 0.85rem; }
.dk-lede { max-width: 30rem; font-family: var(--display); font-size: 1.2rem; font-style: italic; }
.dk-now { margin-top: 2rem; padding-top: 1.2rem; border-top: 1px solid var(--g-line); color: var(--g-text); }
.dk-now small { color: var(--g-muted); font-size: 0.7rem; font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: 0.16em; }
.dk-now strong { display: block; margin-top: 0.4rem; font-family: var(--display); font-size: 1.6rem; font-weight: 600; line-height: 1.1; }
.dk-ctrl { display: flex; align-items: center; gap: 0.6rem; margin-top: 1.4rem; }
.dk-ctrl button { display: grid; place-items: center; width: 52px; height: 52px; border: 1px solid var(--g-line); border-radius: 50%; background: transparent; color: var(--g-text); cursor: pointer; transition: background 0.2s, color 0.2s, border-color 0.2s; }
.dk-ctrl button:hover { border-color: var(--brown-ink); background: var(--brown-ink); color: #fbeedd; }
[data-theme="dark"] .dk-ctrl button:hover { border-color: var(--gold); background: var(--gold); color: var(--espresso); }
.dk-ctrl svg { width: 18px; height: 18px; }
.dk-ctrl a { display: inline-flex; align-items: center; gap: 0.7rem; margin-left: 1rem; color: var(--g-text); font-weight: 600; font-size: 0.85rem; text-decoration: none; }
.dk-ctrl a svg { width: 30px; }

.dk { position: relative; height: clamp(440px, 42vw, 540px); outline: none; touch-action: pan-y; }
.dk:focus-visible { outline: 2px dashed var(--g-line); outline-offset: 8px; border-radius: 20px; }
.dk-card { position: absolute; top: 50%; left: 50%; width: min(300px, 64%); aspect-ratio: 3 / 4; margin: 0; overflow: hidden; border-radius: 16px; color: #fbeedd; text-decoration: none;
  box-shadow: 0 30px 50px -28px rgba(30, 12, 2, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.06) inset; user-select: none; -webkit-user-drag: none;
  transform: translate(-50%, -50%) translate(calc(var(--d, 0) * 18px), calc(var(--d, 0) * -10px)) rotate(calc(var(--d, 0) * 3.5deg)) scale(calc(1 - var(--d, 0) * 0.05));
  transition: transform 0.55s var(--ease-out), opacity 0.4s; }
.dk-card img { width: 100%; height: 100%; object-fit: cover; pointer-events: none; }
.dk-card__cap { position: absolute; inset: auto 0 0; display: flex; align-items: end; justify-content: space-between; gap: 1rem; padding: 3rem 1.2rem 1.1rem;
  background: linear-gradient(180deg, transparent, rgba(10, 4, 0, 0.82)); }
.dk-card__cap small { display: block; color: var(--gold-pale); font-size: 0.55rem; font-weight: 600; letter-spacing: 0.26em; text-transform: uppercase; }
.dk-card__cap strong { display: block; margin-top: 0.3rem; font-family: var(--display); font-size: 1.35rem; font-weight: 600; line-height: 1.05; }
.dk-card__cap b { flex: none; padding: 0.35rem 0.65rem; border-radius: 999px; background: rgba(251, 238, 221, 0.16); font-size: 0.75rem; font-variant-numeric: tabular-nums; backdrop-filter: blur(4px); }
.dk-card.deep { opacity: 0; }
.dk-card.top { cursor: grab; }
.dk-card.dragging { cursor: grabbing; transition: none; }
.dk-card.thrown { transform: translate(-50%, -50%) translate(var(--tx, -120%), 30px) rotate(var(--tr, -16deg)); }

/* The page: chips, the contact strip and the spread. */
.dk-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1.6rem; }
.dk-chips button, .dk-view button { padding: 0.55rem 1rem; border: 1px solid var(--g-line); border-radius: 999px; background: transparent; color: var(--g-text); font: 500 0.78rem var(--sans); cursor: pointer; }
.dk-chips button[aria-pressed="true"], .dk-view button[aria-pressed="true"] { border-color: var(--brown-ink); background: var(--brown-ink); color: #fbeedd; }
[data-theme="dark"] .dk-chips button[aria-pressed="true"], [data-theme="dark"] .dk-view button[aria-pressed="true"] { border-color: var(--gold); background: var(--gold); color: var(--espresso); }
.dk-view { display: inline-flex; gap: 0.3rem; margin-top: 1.2rem; }
.dk-strip { display: flex; gap: 8px; margin-top: 1.6rem; overflow-x: auto; scrollbar-width: none; padding: 4px; }
.dk-strip button { flex: none; width: 46px; padding: 0; border: 0; border-radius: 4px; background: none; cursor: pointer; opacity: 0.5; transition: opacity 0.2s, transform 0.3s var(--ease-out); }
.dk-strip button img { display: block; width: 100%; height: auto; border-radius: 4px; }
.dk-strip button[aria-current="true"] { opacity: 1; transform: translateY(-4px); box-shadow: 0 0 0 2px var(--rust); }
[data-theme="dark"] .dk-strip button[aria-current="true"] { box-shadow: 0 0 0 2px var(--gold); }
.dk.spread { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 1.2rem; height: auto; }
.dk.spread .dk-card { position: relative; top: auto; left: auto; width: auto; transform: none; opacity: 1; animation: dk-deal 0.5s var(--ease-out) both; animation-delay: calc(var(--i) * 40ms); }
.dk.spread .dk-card.top { cursor: pointer; }
@keyframes dk-deal { from { opacity: 0; transform: translateY(30px) rotate(4deg); } }
.r3-page .dk-grid { align-items: start; }
.r3-page .dk-grid.is-spread { grid-template-columns: minmax(0, 1fr); }
.r3-page .dk-grid.is-spread .dk-strip, .r3-page .dk-grid.is-spread .dk-ctrl button, .r3-page .dk-grid.is-spread .dk-now { display: none; }

@media (max-width: 820px) { .dk-grid { grid-template-columns: minmax(0, 1fr); } .dk { height: 460px; } }
@media (prefers-reduced-motion: reduce) { .dk-card { transition: none; } }
"""

DK_PREV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>'
DK_NEXT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>'


def dk_card(b, i):
    return (f'<a class="dk-card" href="#" draggable="false" style="--i:{i}" data-cat="{cat_id(b[2])}" data-title="{esc(b[0])}" data-cover="{COVERS[b[0]]}">{img(b)}'
            f'<span class="dk-card__cap"><span><small>{esc(b[1])}</small><strong>{esc(b[0])}</strong></span><b>{PRICE}</b></span></a>')


def dk_controls(link=True):
    go = f'<a href="#">Visit the Bookstore {ARROW}</a>' if link else ""
    return f"""<div class="dk-now" aria-live="polite"><small class="dk-at">01 / 06</small><strong class="dk-title"></strong></div>
          <div class="dk-ctrl"><button type="button" class="dk-prev" aria-label="Previous book">{DK_PREV}</button><button type="button" class="dk-next" aria-label="Next book">{DK_NEXT}</button>{go}</div>"""


HOME_10 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap dk-grid">
      <div class="dk-intro">
        <h2 id="bs-h">Book&shy;store</h2><p>{COUNT} titles · drag the top card away, or use the arrows</p>
        {dk_controls()}
      </div>
      <div class="dk" tabindex="0" aria-label="The featured books, a deck: left and right arrows go through it">{"".join(dk_card(b, i) for i, b in enumerate(FEATURED))}</div>
    </div>
  </section>""")

PAGE_10 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="dk-grid">
        <div class="dk-intro">
          <h1 id="bs-h">Book&shy;store</h1><p class="dk-lede">{LEDE}</p>
          <div class="dk-chips" role="group" aria-label="Category"><button type="button" aria-pressed="true" data-f="all">All {COUNT}</button>{"".join(f'<button type="button" aria-pressed="false" data-f="{cat_id(s)}">{esc(s)}</button>' for s in SHELVES)}</div>
          <div class="dk-view" role="group" aria-label="View"><button type="button" aria-pressed="true" data-v="deck">Deck</button><button type="button" aria-pressed="false" data-v="spread">Spread</button></div>
          {dk_controls(False)}
          <div class="dk-strip" aria-label="Jump to a book"></div>
        </div>
        <div class="dk" tabindex="0" aria-label="The books, a deck: left and right arrows go through it">{"".join(dk_card(b, i) for i, b in enumerate(BOOKS))}</div>
      </div>
    </div>
  </section>""")

JS_10 = """
<script>
  // The deck: an order of the cards in play, the first on top. Next throws the
  // top card away and tucks it in at the back; previous brings the back one up.
  (function () {
    var deck = document.querySelector(".dk"), all = [].slice.call(deck.querySelectorAll(".dk-card"));
    var at = document.querySelector(".dk-at"), title = document.querySelector(".dk-title"), strip = document.querySelector(".dk-strip");
    var order = all.slice(), busy = false;
    function lay() {
      all.forEach(function (c) { c.hidden = order.indexOf(c) < 0; });
      order.forEach(function (c, d) {
        c.style.setProperty("--d", d); c.style.zIndex = 100 - d;
        c.classList.toggle("top", d === 0); c.classList.toggle("deep", d > 3);
        var live = deck.classList.contains("spread") || d === 0;
        c.tabIndex = live ? 0 : -1; c.setAttribute("aria-hidden", String(!live));
      });
      var top = order[0]; if (!top) return;
      var i = parseInt(top.dataset.pos, 10);
      at.textContent = String(i + 1).padStart(2, "0") + " / " + String(order.length).padStart(2, "0");
      title.textContent = top.dataset.title;
      if (strip) strip.querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-current", String(b.dataset.pos === top.dataset.pos)); });
    }
    function number() { order.forEach(function (c, i) { c.dataset.pos = i; }); }
    function next(dir) {
      if (busy || order.length < 2) return;
      busy = true;
      var top = order[0];
      top.style.setProperty("--tx", dir > 0 ? "-125%" : "25%"); top.style.setProperty("--tr", dir > 0 ? "-16deg" : "16deg");
      top.classList.add("thrown");
      setTimeout(function () {
        top.classList.remove("thrown"); top.style.transform = "";
        order.push(order.shift()); lay(); busy = false;
      }, 320);
    }
    function prev() { if (order.length < 2) return; order.unshift(order.pop()); lay(); }
    function jump(pos) { while (order[0].dataset.pos !== String(pos)) order.push(order.shift()); lay(); }
    document.querySelector(".dk-next").addEventListener("click", function () { next(1); });
    document.querySelector(".dk-prev").addEventListener("click", prev);
    deck.addEventListener("keydown", function (e) {
      if (deck.classList.contains("spread")) return;
      if (e.key === "ArrowRight") { e.preventDefault(); next(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
    });
    // Drag the top card: past 90px it is thrown that way; short of it, it settles back.
    var drag = null, moved = false;
    deck.addEventListener("pointerdown", function (e) {
      var c = e.target.closest(".dk-card.top");
      if (!c || deck.classList.contains("spread") || e.button !== 0) return;
      drag = { c: c, x: e.clientX, dx: 0 }; moved = false;
      c.setPointerCapture(e.pointerId);
    });
    deck.addEventListener("pointermove", function (e) {
      if (!drag) return;
      drag.dx = e.clientX - drag.x;
      if (!moved && Math.abs(drag.dx) > 6) { moved = true; drag.c.classList.add("dragging"); }
      if (moved) drag.c.style.transform = "translate(-50%, -50%) translateX(" + drag.dx + "px) rotate(" + drag.dx / 18 + "deg)";
    });
    function release() {
      if (!drag) return;
      var c = drag.c, dx = drag.dx; drag = null;
      c.classList.remove("dragging");
      if (Math.abs(dx) > 90) { c.style.transform = ""; next(dx < 0 ? 1 : -1); }
      else c.style.transform = "";
    }
    deck.addEventListener("pointerup", release); deck.addEventListener("pointercancel", release);
    deck.addEventListener("click", function (e) { if (moved) { e.preventDefault(); moved = false; } }, true);

    // The page: chips deal a category's deck; the strip jumps; Spread lays it out.
    function deal(f) {
      order = all.filter(function (c) { return f === "all" || c.dataset.cat === f; });
      number();
      if (strip) strip.innerHTML = order.map(function (c, i) {
        return '<button type="button" data-pos="' + i + '" aria-label="' + c.dataset.title.replace(/"/g, "&quot;") + '"><img src="' + c.dataset.cover + '" alt=""></button>';
      }).join("");
      order.forEach(function (c, i) { c.style.setProperty("--i", i); });
      lay();
    }
    if (strip) strip.addEventListener("click", function (e) { var b = e.target.closest("button"); if (b) jump(b.dataset.pos); });
    var chips = document.querySelectorAll(".dk-chips button");
    chips.forEach(function (c) {
      c.addEventListener("click", function () { chips.forEach(function (x) { x.setAttribute("aria-pressed", String(x === c)); }); deal(c.dataset.f); });
    });
    var views = document.querySelectorAll(".dk-view button");
    views.forEach(function (v) {
      v.addEventListener("click", function () {
        views.forEach(function (x) { x.setAttribute("aria-pressed", String(x === v)); });
        var spread = v.dataset.v === "spread";
        deck.classList.toggle("spread", spread); deck.closest(".dk-grid").classList.toggle("is-spread", spread);
        lay();
      });
    });
    deal("all");
  })();
</script>"""

BUILDS.append((CSS_10, HOME_10, PAGE_10, JS_10, JS_10,
               "The covers as a stack of cards to throw through by drag, button or arrow key; the page deals a deck per category with a contact strip and a spread view."))


if __name__ == "__main__":
    for (slug, name), (css, h, p, hjs, pjs, blurb) in zip(OPTIONS, BUILDS):
        (HERE / f"{slug}.html").write_text(page(f"{slug}.html", slug, name, blurb, css, h, hjs))
        (HERE / f"{slug}-page.html").write_text(page(f"{slug}-page.html", slug, name, blurb, css, p, pjs))
        print("wrote", slug)

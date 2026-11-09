#!/usr/bin/env python3
"""The bookstore, round 4: ten mockups for a shop that sells academic Islamic
books, each a home-page section and a full page. Where round 3 borrowed from
shops and museums in general, every idea here comes from how Islamic books
themselves were made, kept, catalogued and taught from:

   1. Hashiya      - the page of a commentary: the lead book is the matn in
                     the middle of a ruled leaf, the others are glosses written
                     diagonally in its margins. Choosing a gloss swaps it into
                     the matn. The page: a leaf per category.
   2. Khizana      - books kept as Islamic libraries kept them, lying flat in
                     stacks with the fore-edge flap facing out and the title on
                     a label there. Pointing at one draws it out and shows it
                     on a card. The page: a cubby per category.
   3. Rahle        - the folding stand of the teaching circle: the chosen book
                     lies open on it, cover on one page and particulars on the
                     other; choosing another turns the page. The page keeps
                     the stand on screen beside the whole list.
   4. Fihrist      - a classical catalogue: an illuminated headpiece (unwan),
                     the categories as red rubrics, entries numbered in
                     Arabic-Indic numerals in verse-marker roundels, dotted
                     leaders to the price. Pointing at one shows its cover.
   5. Envelope flap - each book wears the pentagonal flap of an Islamic
                     binding, folded over its cover; it swings open to show its
                     lining, where the subject and price are written.
   6. Colophon     - each book's particulars set as a colophon, tapering to a
                     point and closed with three dots, under its cover on a
                     ruled leaf.
   7. Ebru         - the books mounted like album pages in borders of marbled
                     paper, marbled in each binding's colours; the marbling
                     drifts when pointed at.
   8. Tree of sciences - the stock drawn as a branching diagram of the
                     disciplines (tashjir, the tree of the sciences): the
                     bookstore at the root, the categories as branches, the
                     books as leaves.
   9. The volume   - the catalogue as a bound book that opens and turns from
                     right to left, as an Arabic book does: a cover on the
                     right-hand page, its particulars on the left.
  10. Study circle - the halaqa: the chosen book sits on the dais, the rest in
                     a half-circle before it, facing in. The page seats each
                     category in its own ring.

No star patterns: the ornament is vine scrolls, rules, roundels and marbling.
Content as rounds 1-3: curriculum titles stand in for stock, $00.00 for
prices, a TODO intro, and the drawn bindings where photographs will go. The
Arabic-Indic numerals number things; no Arabic words are added.

Edit this file, not the output:  python3 generate_round4.py
"""
import importlib.util
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("round3", HERE / "generate_round3.py")
r3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r3)

esc, BOOKS, FEATURED, SHELVES, COVERS = r3.esc, r3.BOOKS, r3.FEATURED, r3.SHELVES, r3.COVERS
tone, shelf, cat_id, img, home, page_main = r3.tone, r3.shelf, r3.cat_id, r3.img, r3.home, r3.page_main
PRICE, LEDE, PAGE, COUNT, ARROW = r3.PRICE, r3.LEDE, r3.PAGE, r3.COUNT, r3.ARROW

AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def ar(n):
    return str(n).translate(AR)


def bdata(b):
    """A book's particulars as data attributes, for the scripts that show it elsewhere."""
    return (f'data-t="{esc(b[0])}" data-s="{esc(b[1])}" data-c="{esc(b[2])}" data-p="{PRICE}" '
            f'data-img="{COVERS[b[0]]}" data-tone="{tone(b)}"')


OPTIONS = [
    ("r4-01-hashiya", "Hashiya"),
    ("r4-02-khizana", "Khizana"),
    ("r4-03-rahle", "Rahle"),
    ("r4-04-fihrist", "Fihrist"),
    ("r4-05-flap", "Envelope flap"),
    ("r4-06-colophon", "Colophon"),
    ("r4-07-ebru", "Ebru"),
    ("r4-08-tree", "Tree of sciences"),
    ("r4-09-volume", "The volume"),
    ("r4-10-circle", "Study circle"),
]


def switcher(slug, is_page):
    sfx = "-page" if is_page else ""
    links = "".join(
        f'<a href="{s}{sfx}.html" title="{n}"{PAGE if s == slug else ""}>{i + 1}</a>'
        for i, (s, n) in enumerate(OPTIONS))
    return f"""
<nav class="m-switch" aria-label="Mockups">
  <a href="1-shelf{sfx}.html">R1</a><a href="r2-1-window{sfx}.html">R2</a><a href="r3-01-bento{sfx}.html">R3</a><a href="r4-01-hashiya{sfx}.html"{PAGE}>R4</a><i></i>{links}<i></i>
  <a href="{slug}.html"{"" if is_page else PAGE}>Home</a><a href="{slug}-page.html"{PAGE if is_page else ""}>Page</a><i></i>
  <button type="button" data-set-theme="light">Light</button>
  <button type="button" data-set-theme="dark">Dark</button>
</nav>"""


# The leaf every option writes on: paper and ink, a rubric red, a ruling gold.
SHARED_CSS = """
:root { --lf: #f8efdd; --lf-2: #efe1c4; --lf-ink: #2c1a0d; --lf-muted: rgba(44, 26, 13, 0.7); --rubric: #a3301c;
  --lf-gold: #b07f22; --lf-line: rgba(160, 110, 30, 0.42); --r4-shadow: 0 34px 50px -32px rgba(60, 30, 8, 0.6), 0 2px 4px rgba(60, 30, 8, 0.08); }
[data-theme="dark"] { --lf: #2c1c0f; --lf-2: #21140a; --lf-ink: #f1e3c9; --lf-muted: rgba(241, 227, 201, 0.64); --rubric: #e8906a;
  --lf-gold: #d9aa48; --lf-line: rgba(217, 170, 72, 0.3); --r4-shadow: 0 34px 50px -30px rgba(0, 0, 0, 0.85), inset 0 1px 0 rgba(255, 236, 210, 0.06); }
.r4-leaf { background: radial-gradient(130% 100% at 50% 30%, var(--lf), var(--lf-2)); color: var(--lf-ink); box-shadow: var(--r4-shadow); }
/* The jadwal: a gold rule and a red one, inside the leaf's edge. */
.r4-jadwal { position: relative; }
.r4-jadwal::before, .r4-jadwal::after { content: ""; position: absolute; inset: 9px; border: 1px solid var(--lf-gold); pointer-events: none; }
.r4-jadwal::after { inset: 13px; border-color: var(--rubric); }
.r4-kick { color: var(--rubric); font: 600 0.6rem/1.3 var(--sans); letter-spacing: 0.26em; text-transform: uppercase; }
.r4-head { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 0.6rem 1.5rem; margin-bottom: clamp(1.6rem, 3vw, 2.4rem); padding-bottom: 1rem; border-bottom: 1px solid var(--g-line); }
.r4-h { font-family: var(--title); font-size: clamp(1.9rem, 1.2rem + 2vw, 2.9rem); font-weight: 400; letter-spacing: 0.1em; line-height: 1.05; text-transform: uppercase;
  background: var(--g-title); -webkit-background-clip: text; background-clip: text; color: transparent; }
.r4-count { color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; }
.r4-lede { max-width: 40rem; margin: -0.8rem 0 2.2rem; color: var(--g-muted); font-family: var(--display); font-size: 1.25rem; font-style: italic; }
.r4-go { display: inline-flex; align-items: center; gap: 0.7rem; color: var(--rubric); font: 600 0.72rem var(--sans); letter-spacing: 0.2em; text-decoration: none; text-transform: uppercase; transition: gap 0.3s var(--ease-out); }
.r4-go svg { width: 28px; }
.r4-go:hover { gap: 1.1rem; }
.r4-roundel { display: inline-grid; flex: none; place-items: center; width: 2.2rem; height: 2.2rem; padding-top: 0.2rem; border: 1px solid var(--lf-gold); border-radius: 50%;
  box-shadow: inset 0 0 0 2px var(--lf), inset 0 0 0 3px var(--lf-gold); color: var(--lf-ink); font: 700 1rem/1 var(--urdu); }
.r4-in { animation: r4-in 0.55s var(--ease-out) both; }
@keyframes r4-in { from { opacity: 0; transform: translateY(10px); } }
@media (prefers-reduced-motion: reduce) { .r4-in { animation: none; } }
"""

# Fills every [data-f] inside root from a book's data attributes.
FILL_JS = """
  function fill(root, el) {
    root.querySelectorAll("[data-f]").forEach(function (n) {
      var v = el.dataset[n.dataset.f];
      if (n.tagName === "IMG") n.src = v; else n.textContent = v;
    });
    root.style.setProperty("--tone", el.dataset.tone);
    root.classList.remove("r4-in"); void root.offsetWidth; root.classList.add("r4-in");
  }"""


def page(fname, slug, name, blurb, css, main, js=""):
    r3.switcher = switcher
    out = r3.page(fname, slug, name, blurb, SHARED_CSS + css, main, js)
    return (out.replace("<!-- Round 3, option", "<!-- Round 4, option")
               .replace("family=Instrument+Sans", "family=Amiri:wght@400;700&family=Instrument+Sans"))


def head(level="h2", count=True):
    c = f'<p class="r4-count">{COUNT} titles</p>' if count else ""
    return f'<header class="r4-head"><{level} id="bs-h" class="r4-h">The Bookstore</{level}>{c}</header>'


def page_head():
    return f'<a class="r3-back" href="#">← Home</a>{head("h1")}<p class="r4-lede">{LEDE}</p>'


VISIT = f'<a class="r4-go" href="#">Visit the Bookstore {ARROW}</a>'
BUILDS = []

# ============================================================================
# 1. Hashiya: a ruled leaf. The lead book is the matn, the text block in the
#    middle; the other books are glosses written diagonally in the margins,
#    as the hashiya runs round a matn. Choosing a gloss swaps it with the
#    matn. The page: a leaf per category, its books listed in the matn, the
#    cover of the one pointed at in the margin, the category as its gloss.
# ============================================================================
CSS_1 = """
.hs-leaf { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 2.4fr) minmax(0, 1fr); gap: clamp(0.8rem, 2vw, 1.8rem);
  padding: clamp(1.2rem, 3vw, 2.8rem); border-radius: 3px; }
.hs-margin { display: grid; grid-template-rows: repeat(3, minmax(0, 1fr)); gap: 0.6rem; align-items: center; }
.hs-note { display: grid; place-items: center; width: 100%; aspect-ratio: 5 / 4; padding: 0; border: 0; background: none; color: inherit; font: inherit; text-decoration: none; cursor: pointer; }
.hs-note > span { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; width: 118%; padding: 0.55rem 0; border-block: 1px solid var(--lf-line);
  transform: rotate(-45deg); text-align: center; transition: color 0.25s, border-color 0.25s; }
.hs-note--r > span { transform: rotate(45deg); }
.hs-note small { color: var(--rubric); font: 600 0.55rem/1 var(--sans); letter-spacing: 0.24em; text-transform: uppercase; }
.hs-note i { font-family: var(--display); font-size: clamp(0.95rem, 0.7rem + 0.6vw, 1.22rem); font-weight: 600; line-height: 1.1; }
.hs-note b { color: var(--lf-muted); font: 500 0.7rem var(--sans); }
.hs-note:hover > span, .hs-note:focus-visible > span { border-color: var(--rubric); color: var(--rubric); }
.hs-note:focus-visible { outline: 2px solid var(--rubric); outline-offset: -4px; }
.hs-visit i { color: var(--rubric); font-style: normal; }
.hs-matn { display: grid; grid-template-columns: minmax(0, 0.9fr) minmax(0, 1fr); gap: clamp(1rem, 2.5vw, 2.2rem); align-items: center;
  padding: clamp(2rem, 3.5vw, 3.2rem); background: color-mix(in oklab, var(--tone, #a16541) 5%, transparent); }
.hs-cover { width: 100%; height: auto; border-radius: 2px 5px 5px 2px; box-shadow: -12px 18px 30px -14px rgba(30, 12, 2, 0.6); }
.hs-title { margin: 0.5rem 0 0.5rem; font-family: var(--display); font-size: clamp(1.7rem, 1.1rem + 1.8vw, 2.7rem); font-weight: 600; line-height: 1.05; }
.hs-cat { color: var(--lf-muted); font-family: var(--display); font-size: 1.15rem; font-style: italic; }
.hs-price { margin-top: 1.2rem; padding-top: 0.8rem; border-top: 1px solid var(--lf-line); font: 600 0.9rem var(--sans); }

/* The page: the matn is a numbered list, the margins a cover and a gloss. */
.hs-leaf--cat { margin-bottom: 2.6rem; }
.hs-leaf--cat .hs-margin { grid-template-rows: none; }
.hs-matn--list { display: block; }
.hs-list { margin: 0.8rem 0 0; padding: 0; list-style: none; }
.hs-row { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; gap: 1rem; align-items: center; padding: 0.8rem 0.2rem; border-bottom: 1px solid var(--lf-line); color: inherit; text-decoration: none; transition: color 0.2s; }
.hs-list li:last-child .hs-row { border-bottom: 0; }
.hs-row__t { font-family: var(--display); font-size: 1.32rem; font-weight: 600; line-height: 1.1; }
.hs-row__t small { display: block; margin-top: 0.25rem; color: var(--lf-muted); font: 500 0.6rem var(--sans); letter-spacing: 0.2em; text-transform: uppercase; }
.hs-row__p { font: 600 0.8rem var(--sans); }
.hs-row:hover, .hs-row:focus-visible { color: var(--rubric); }
.hs-peek { margin: 0; transform: rotate(-6deg); transition: transform 0.4s var(--ease-out); }
.hs-peek img { display: block; width: 100%; height: auto; border-radius: 2px 5px 5px 2px; box-shadow: -10px 16px 26px -12px rgba(30, 12, 2, 0.6); }
.hs-gloss { margin: 0; }
.hs-gloss > span { cursor: default; }

@media (max-width: 820px) {
  .hs-leaf { grid-template-columns: minmax(0, 1fr); }
  .hs-margin { grid-template-rows: none; grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .hs-margin:first-child { order: 2; }
  .hs-note { aspect-ratio: auto; }
  .hs-note > span, .hs-note--r > span { width: 100%; transform: none; }
  .hs-matn { grid-template-columns: minmax(0, 1fr); }
  .hs-cover { max-width: 220px; }
  .hs-leaf--cat .hs-margin:first-child { display: none; }
  .hs-leaf--cat .hs-margin { grid-template-columns: minmax(0, 1fr); }
}
"""


def hs_note(b, side):
    return (f'<button type="button" class="hs-note hs-note--{side}" {bdata(b)}><span><small>{esc(b[1])}</small>'
            f'<i>{esc(b[0])}</i><b>{PRICE}</b></span></button>')


L = FEATURED[0]
HOME_1 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      {head()}
      <div class="hs-leaf r4-leaf">
        <div class="hs-margin">{"".join(hs_note(b, "l") for b in FEATURED[1:4])}</div>
        <div class="hs-matn r4-jadwal" data-matn {bdata(L)} style="--tone:{tone(L)}" aria-live="polite">
          <img class="hs-cover" data-f="img" src="{COVERS[L[0]]}" width="300" height="400" alt="">
          <div>
            <p class="r4-kick" data-f="s">{esc(L[1])}</p>
            <h3 class="hs-title" data-f="t">{esc(L[0])}</h3>
            <p class="hs-cat" data-f="c">{esc(L[2])}</p>
            <p class="hs-price" data-f="p">{PRICE}</p>
          </div>
        </div>
        <div class="hs-margin">{"".join(hs_note(b, "r") for b in FEATURED[4:6])}<a class="hs-note hs-note--r hs-visit" href="#"><span><small>{COUNT} titles</small><i>Visit the Bookstore</i></span></a></div>
      </div>
    </div>
  </section>""")

JS_1 = f"""
<script>
  // A gloss chosen trades places with the matn.
  (function () {{{FILL_JS}
    var keys = ["t", "s", "c", "p", "img", "tone"];
    document.querySelectorAll(".hs-leaf").forEach(function (leaf) {{
      var matn = leaf.querySelector("[data-matn]");
      leaf.addEventListener("click", function (e) {{
        var n = e.target.closest("button.hs-note");
        if (!n) return;
        keys.forEach(function (k) {{ var v = matn.dataset[k]; matn.dataset[k] = n.dataset[k]; n.dataset[k] = v; }});
        fill(matn, matn);
        n.querySelector("small").textContent = n.dataset.s;
        n.querySelector("i").textContent = n.dataset.t;
      }});
    }});
  }})();
</script>"""


def hs_cat(s):
    bs = shelf(s)
    rows = "".join(
        f'<li><a class="hs-row" href="#" {bdata(b)}><span class="r4-roundel">{ar(i + 1)}</span>'
        f'<span class="hs-row__t">{esc(b[0])}<small>{esc(b[1])}</small></span><span class="hs-row__p">{PRICE}</span></a></li>'
        for i, b in enumerate(bs))
    return f"""
      <article class="hs-leaf hs-leaf--cat r4-leaf" id="{cat_id(s)}">
        <div class="hs-margin"><figure class="hs-peek"><img data-f="img" src="{COVERS[bs[0][0]]}" width="300" height="400" alt=""></figure></div>
        <div class="hs-matn hs-matn--list r4-jadwal"><h2 class="r4-kick">{esc(s)}</h2><ol class="hs-list">{rows}</ol></div>
        <div class="hs-margin"><p class="hs-note hs-note--r hs-gloss"><span><small>{len(bs)} titles</small><i>{esc(s)}</i></span></p></div>
      </article>"""


PAGE_1 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      {page_head()}
      {"".join(hs_cat(s) for s in SHELVES)}
    </div>
  </section>""")

JS_1P = f"""
<script>
  // The margin shows the cover of the book pointed at in the matn.
  (function () {{{FILL_JS}
    document.querySelectorAll(".hs-leaf--cat").forEach(function (leaf) {{
      var peek = leaf.querySelector(".hs-peek");
      leaf.querySelectorAll(".hs-row").forEach(function (r) {{
        function show() {{ fill(peek, r); }}
        r.addEventListener("pointerenter", show); r.addEventListener("focus", show);
      }});
    }});
  }})();
</script>"""

BUILDS.append((CSS_1, HOME_1, PAGE_1, JS_1, JS_1P,
               "The page of a commentary: the lead book is the matn on a ruled leaf, the others glosses written diagonally in its margins."))

# ============================================================================
# 2. Khizana: a cabinet of cubbies in the site's wood, the books lying flat in
#    stacks with the fore-edge flap facing out, a paper label on each flap
#    giving the title - Islamic libraries shelved books flat, fore-edge out.
#    Pointing at one draws it out and its card beside the cabinet shows the
#    cover, subject, name and price. The page: a cubby per category.
# ============================================================================
CSS_2 = """
.kz { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(0, 1fr); gap: clamp(1.5rem, 4vw, 3.5rem); align-items: start; }
.kz-cab { display: grid; grid-template-columns: repeat(var(--cols, 2), minmax(0, 1fr)); gap: 16px; padding: 18px 18px 22px; border-radius: 10px 10px 4px 4px;
  background: var(--grain), linear-gradient(180deg, var(--wood-hi), var(--wood) 30%, var(--wood-lo)); background-size: var(--grain-size), auto;
  box-shadow: inset 0 2px 0 rgba(255, 240, 220, 0.25), inset 0 -3px 0 rgba(0, 0, 0, 0.2), 0 34px 50px -30px rgba(40, 18, 4, 0.8); }
[data-theme="dark"] .kz-cab { filter: brightness(0.82); }
.kz-cubby { display: flex; flex-direction: column; min-width: 0; }
.kz-stack { display: flex; flex: 1; flex-direction: column; justify-content: flex-end; align-items: center; min-height: 230px; padding: 18px 14px 6px; border-radius: 3px;
  background: linear-gradient(180deg, #25130a, #3a2213 70%, #2c180c); box-shadow: inset 0 12px 20px rgba(0, 0, 0, 0.6), inset 0 -2px 0 rgba(255, 240, 220, 0.1); }
.kz-plate { align-self: center; margin-top: 10px; padding: 0.3rem 0.9rem; border-radius: 2px; background: linear-gradient(180deg, #f2d48a, #c99a3e); color: #3a2410;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6), 0 2px 3px rgba(0, 0, 0, 0.35); font: 600 0.58rem var(--sans); letter-spacing: 0.22em; text-transform: uppercase; }
.kz-book { position: relative; display: block; flex: none; width: var(--w); height: var(--h); margin: 0 0 0 var(--o); padding: 0; border: 0; border-radius: 3px 7px 7px 3px; cursor: pointer;
  background: linear-gradient(180deg, color-mix(in oklab, var(--tone) 60%, #000) 0 5px, transparent 5px calc(100% - 5px), color-mix(in oklab, var(--tone) 60%, #000) calc(100% - 5px)),
    linear-gradient(180deg, rgba(255, 255, 255, 0.12), rgba(0, 0, 0, 0.18)), var(--tone);
  box-shadow: 0 2px 0 rgba(0, 0, 0, 0.45), 0 -1px 0 rgba(255, 240, 220, 0.06); transition: transform 0.35s var(--ease-out), box-shadow 0.35s; }
.kz-book + .kz-book { margin-top: 1px; }
.kz-label { position: absolute; inset: 20% 8%; display: grid; place-items: center; overflow: hidden; padding: 0 0.6rem; border-radius: 1px; background: #efe0c0; color: #2c1a0d;
  box-shadow: inset 0 0 0 1px rgba(120, 80, 20, 0.3); font: italic 600 min(0.95rem, calc(var(--h) * 0.31)) / 1 var(--display); white-space: nowrap; text-overflow: ellipsis; }
.kz-book:hover, .kz-book:focus-visible, .kz-book.on { z-index: 1; transform: translateY(-2px) scale(1.06); box-shadow: 0 14px 18px -8px rgba(0, 0, 0, 0.7); }
.kz-book:focus-visible { outline: 2px solid var(--gold); outline-offset: 2px; }
.kz-card { position: sticky; top: 100px; display: grid; grid-template-columns: minmax(0, 0.8fr) minmax(0, 1fr); gap: 1.2rem; align-items: end; padding: 2rem; border-radius: 3px; }
.kz-card img { width: 100%; height: auto; border-radius: 2px 5px 5px 2px; box-shadow: -10px 16px 26px -12px rgba(30, 12, 2, 0.6); }
.kz-card h3 { margin: 0.4rem 0; font-family: var(--display); font-size: clamp(1.5rem, 1.1rem + 1vw, 2rem); font-weight: 600; line-height: 1.05; }
.kz-card__c { color: var(--lf-muted); font-family: var(--display); font-style: italic; }
.kz-card__p { margin-top: 0.9rem; padding-top: 0.7rem; border-top: 1px solid var(--lf-line); font: 600 0.85rem var(--sans); }
.kz-card .r4-go { grid-column: 1 / -1; margin-top: 0.4rem; }
.kz-hint { grid-column: 1 / -1; color: var(--lf-muted); font: 500 0.7rem var(--sans); }
@media (max-width: 880px) {
  .kz { grid-template-columns: minmax(0, 1fr); }
  .kz-card { position: relative; top: 0; }
  .kz-cab { --cols: 2 !important; }
}
@media (max-width: 520px) { .kz-cab { --cols: 1 !important; } }
"""
KZ_W = [94, 84, 98, 88, 80, 96]
KZ_H = [48, 40, 56, 44, 52, 42]
KZ_O = [0, 10, -6, 12, 4, -8]


def kz_book(b, i):
    return (f'<button type="button" class="kz-book" style="--tone:{tone(b)};--w:{KZ_W[i % 6]}%;--h:{KZ_H[i % 6]}px;--o:{KZ_O[i % 6]}px" '
            f'{bdata(b)}><span class="kz-label">{esc(b[0])}</span></button>')


def kz_cubby(books, plate=""):
    p = f'<p class="kz-plate">{esc(plate)}</p>' if plate else ""
    return f'<div class="kz-cubby"><div class="kz-stack">{"".join(kz_book(b, i) for i, b in enumerate(books))}</div>{p}</div>'


def kz_card(b, go=True):
    return f"""<aside class="kz-card r4-leaf r4-jadwal" data-card style="--tone:{tone(b)}" aria-live="polite">
          <img data-f="img" src="{COVERS[b[0]]}" width="300" height="400" alt="">
          <div><p class="r4-kick" data-f="s">{esc(b[1])}</p><h3 data-f="t">{esc(b[0])}</h3><p class="kz-card__c" data-f="c">{esc(b[2])}</p><p class="kz-card__p" data-f="p">{PRICE}</p></div>
          {VISIT if go else '<p class="kz-hint">Point at a book to draw it out.</p>'}
        </aside>"""


HOME_2 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      {head()}
      <div class="kz">
        <div class="kz-cab" style="--cols:2">{kz_cubby(FEATURED[0:3])}{kz_cubby(FEATURED[3:6])}</div>
        {kz_card(FEATURED[0])}
      </div>
    </div>
  </section>""")

PAGE_2 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      {page_head()}
      <div class="kz">
        <div class="kz-cab" style="--cols:3">{"".join(kz_cubby(shelf(s), s) for s in SHELVES)}</div>
        {kz_card(BOOKS[0], False)}
      </div>
    </div>
  </section>""")

JS_2 = f"""
<script>
  // The book pointed at (or focused) is drawn out and shown on the card.
  (function () {{{FILL_JS}
    var card = document.querySelector("[data-card]"), on = null;
    document.querySelectorAll(".kz-book").forEach(function (b) {{
      function show(e) {{
        if (e.pointerType === "touch") return;
        if (on) on.classList.remove("on");
        on = b; b.classList.add("on"); fill(card, b);
      }}
      b.addEventListener("pointerenter", show); b.addEventListener("focus", show); b.addEventListener("click", show);
    }});
  }})();
</script>"""

BUILDS.append((CSS_2, HOME_2, PAGE_2, JS_2, JS_2,
               "Books lying flat in a cabinet's cubbies, fore-edge flaps out with title labels; the one pointed at is drawn out onto a card."))

# ============================================================================
# 3. Rahle: the folding stand, seen from the front - the open book lies in
#    its V, the carved front plank below. The cover is on one page, the
#    particulars on the other; choosing another book turns the page. The
#    page keeps the stand on screen beside every book, by category.
# ============================================================================
RH_STAND = """<svg class="rh-stand" viewBox="0 0 1000 400" aria-hidden="true">
  <defs>
    <linearGradient id="rh-front" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b47a50"/><stop offset="1" stop-color="#7a4528"/></linearGradient>
    <linearGradient id="rh-back" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6e3f22"/><stop offset="1" stop-color="#43250f"/></linearGradient>
    <radialGradient id="rh-shadow"><stop offset="0" stop-color="rgba(30,12,2,0.45)"/><stop offset="1" stop-color="rgba(30,12,2,0)"/></radialGradient>
  </defs>
  <ellipse cx="500" cy="392" rx="330" ry="16" fill="url(#rh-shadow)"/>
  <path fill="url(#rh-back)" fill-rule="evenodd" d="M300 140H700L770 392H230Z M372 392V270Q372 210 500 160Q628 210 628 270V392Z"/>
  <path fill="#8a5334" d="M140 106H860L842 134H158Z"/><path fill="rgba(255,235,205,0.3)" d="M140 106H860V109H140Z"/>
  <path fill="url(#rh-front)" fill-rule="evenodd" d="M335 128H665L705 392H295Z M398 392V262Q398 214 500 172Q602 214 602 262V392Z"/>
  <path fill="none" stroke="#5a3119" stroke-width="3" d="M380 392V258Q380 202 500 154Q620 202 620 258V392"/>
  <path fill="none" stroke="rgba(255,235,205,0.35)" stroke-width="2" d="M340 132H660"/>
  <rect x="472" y="100" width="56" height="44" rx="10" fill="#6e3f22"/>
  <circle cx="500" cy="122" r="7" fill="#d9aa48"/>
</svg>"""

CSS_3 = """
.rh { display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(0, 1fr); gap: clamp(1.5rem, 4vw, 3.5rem); align-items: center; }
.rh-stage { position: relative; container-type: inline-size; aspect-ratio: 1000 / 800; perspective: 1500px; perspective-origin: 50% 20%; }
.rh-stand { position: absolute; left: 0; bottom: 0; width: 100%; height: 50%; }
.rh-page { position: absolute; top: 8.75%; width: 33%; height: 55%; border-radius: 2px; background: var(--lf); color: var(--lf-ink);
  box-shadow: 0 18px 30px -16px rgba(30, 12, 2, 0.6); }
.rh-page--l { left: 17%; transform-origin: 100% 100%; transform: rotateY(22deg);
  background: linear-gradient(to left, rgba(60, 30, 8, 0.22), transparent 14%), radial-gradient(120% 90% at 40% 30%, var(--lf), var(--lf-2)); }
.rh-page--r { left: 50%; transform-origin: 0 100%; transform: rotateY(-22deg);
  background: linear-gradient(to right, rgba(60, 30, 8, 0.22), transparent 14%), radial-gradient(120% 90% at 60% 30%, var(--lf), var(--lf-2)); }
.rh-page::before, .rh-page::after { content: ""; position: absolute; inset: 3cqi; border: 1px solid var(--lf-gold); pointer-events: none; }
.rh-page::after { inset: 3.5cqi; border-color: var(--rubric); }
.rh-page--l img { position: absolute; inset: 6.5cqi 6cqi; width: calc(100% - 12cqi); height: calc(100% - 13cqi); object-fit: contain; filter: drop-shadow(-4px 6px 8px rgba(30, 12, 2, 0.4)); }
.rh-text { position: absolute; inset: 6cqi 5.5cqi; display: flex; flex-direction: column; justify-content: center; text-align: center; }
.rh-text .r4-kick { font-size: max(0.5rem, 1.3cqi); }
.rh-text h3 { margin: 1.4cqi 0; font-family: var(--display); font-size: max(1rem, 3.6cqi); font-weight: 600; line-height: 1.05; }
.rh-text p.rh-c { color: var(--lf-muted); font-family: var(--display); font-size: max(0.8rem, 2cqi); font-style: italic; }
.rh-text p.rh-p { margin-top: 2.4cqi; padding-top: 1.6cqi; border-top: 1px solid var(--lf-line); font: 600 max(0.66rem, 1.6cqi) var(--sans); }
.rh-page--r.turn { animation: rh-turn 0.6s var(--ease-out); }
@keyframes rh-turn { 0% { transform: rotateY(-22deg); } 45% { transform: rotateY(-110deg); } 100% { transform: rotateY(-22deg); } }
.rh-page--l.turn img { animation: r4-in 0.6s var(--ease-out); }

.rh-side .r4-head { margin-bottom: 1.4rem; }
.rh-picks { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.8rem; margin-bottom: 1.6rem; }
.rh-pick { display: grid; gap: 0.5rem; padding: 0; border: 0; background: none; color: var(--g-text); font: inherit; text-align: left; cursor: pointer; }
.rh-pick img { width: 100%; height: auto; border-radius: 2px 4px 4px 2px; box-shadow: 0 10px 18px -12px rgba(30, 12, 2, 0.7); transition: transform 0.3s var(--ease-out); }
.rh-pick span { font-family: var(--display); font-size: 0.98rem; font-weight: 600; line-height: 1.1; }
.rh-pick:hover img, .rh-pick:focus-visible img { transform: translateY(-4px); }
.rh-pick[aria-pressed="true"] img { outline: 2px solid var(--rubric); outline-offset: 3px; }
[data-theme="dark"] .rh-pick[aria-pressed="true"] img { outline-color: var(--gold); }

/* The page: the stand stays on screen; the list beside it. */
.rh--page { align-items: start; }
.rh--page .rh-stage { position: sticky; top: 90px; }
.rh-cat { margin-bottom: 1.8rem; }
.rh-cat h2 { margin-bottom: 0.4rem; color: var(--rubric); font: italic 600 1.35rem var(--display); }
[data-theme="dark"] .rh-cat h2 { color: var(--gold); }
.rh-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 1rem; width: 100%; padding: 0.65rem 0; border: 0; border-bottom: 1px solid var(--g-line); background: none;
  color: var(--g-text); font: inherit; text-align: left; cursor: pointer; }
.rh-row b { font-family: var(--display); font-size: 1.2rem; font-weight: 600; }
.rh-row small { display: block; color: var(--g-muted); font: 500 0.6rem var(--sans); letter-spacing: 0.2em; text-transform: uppercase; }
.rh-row span:last-child { align-self: center; font: 600 0.78rem var(--sans); }
.rh-row:hover b, .rh-row[aria-pressed="true"] b { color: var(--rubric); }
[data-theme="dark"] .rh-row:hover b, [data-theme="dark"] .rh-row[aria-pressed="true"] b { color: var(--gold); }
@media (max-width: 880px) {
  .rh { grid-template-columns: minmax(0, 1fr); }
  .rh--page .rh-stage { position: relative; top: 0; }
}
@media (prefers-reduced-motion: reduce) { .rh-page--r.turn, .rh-page--l.turn img { animation: none; } }
"""


def rh_stage(b):
    return f"""<div class="rh-stage" data-stage {bdata(b)} aria-live="polite">
          {RH_STAND}
          <div class="rh-page rh-page--l"><img data-f="img" src="{COVERS[b[0]]}" width="300" height="400" alt=""></div>
          <div class="rh-page rh-page--r"><div class="rh-text"><p class="r4-kick" data-f="s">{esc(b[1])}</p><h3 data-f="t">{esc(b[0])}</h3><p class="rh-c" data-f="c">{esc(b[2])}</p><p class="rh-p" data-f="p">{PRICE}</p></div></div>
        </div>"""


HOME_3 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap rh">
      {rh_stage(FEATURED[0])}
      <div class="rh-side">
        {head()}
        <div class="rh-picks">{"".join(f'<button type="button" class="rh-pick" aria-pressed="{str(i == 0).lower()}" {bdata(b)}>{img(b)}<span>{esc(b[0])}</span></button>' for i, b in enumerate(FEATURED))}</div>
        {VISIT}
      </div>
    </div>
  </section>""")

PAGE_3 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      {page_head()}
      <div class="rh rh--page">
        {rh_stage(BOOKS[0])}
        <div class="rh-side">{"".join(f'<div class="rh-cat"><h2>{esc(s)}</h2>' + "".join(f'<button type="button" class="rh-pick rh-row" aria-pressed="{str(b == BOOKS[0]).lower()}" {bdata(b)}><span><b>{esc(b[0])}</b><small>{esc(b[1])}</small></span><span>{PRICE}</span></button>' for b in shelf(s)) + '</div>' for s in SHELVES)}</div>
      </div>
    </div>
  </section>""")

JS_3 = f"""
<script>
  // Choosing a book lays it on the stand: the right-hand page turns over to it.
  (function () {{{FILL_JS}
    var stage = document.querySelector("[data-stage]"), picks = document.querySelectorAll(".rh-pick");
    var pr = stage.querySelector(".rh-page--r"), pl = stage.querySelector(".rh-page--l"), t = 0;
    var still = matchMedia("(prefers-reduced-motion: reduce)").matches;
    picks.forEach(function (p) {{
      p.addEventListener("click", function () {{
        picks.forEach(function (x) {{ x.setAttribute("aria-pressed", String(x === p)); }});
        [pr, pl].forEach(function (x) {{ x.classList.remove("turn"); void x.offsetWidth; x.classList.add("turn"); }});
        clearTimeout(t);
        t = setTimeout(function () {{ fill(stage, p); }}, still ? 0 : 260);
        if (innerWidth < 880) stage.scrollIntoView({{ behavior: still ? "auto" : "smooth", block: "center" }});
      }});
    }});
  }})();
</script>"""

BUILDS.append((CSS_3, HOME_3, PAGE_3, JS_3, JS_3,
               "The chosen book lies open on a rahle, cover on one page and particulars on the other; choosing another turns the page."))

# ============================================================================
# 4. Fihrist: the catalogue as a manuscript would set it. An unwan - a band
#    of gold vine scroll on lapis, a cartouche for the name, a scalloped
#    crest - heads a ruled leaf; the categories are red rubrics, every entry
#    numbered in a verse-marker roundel, a dotted leader to its price.
#    Pointing at an entry floats its cover beside the pointer. The page: the
#    whole fihrist in two columns with an index of rubrics in the margin.
# ============================================================================
VINE = ("data:image/svg+xml," + quote(
    "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='80'>"
    "<g fill='none' stroke='#d9aa48' stroke-width='2' stroke-linecap='round'>"
    "<path d='M0 40C40 2 80 2 80 40S120 78 160 40'/>"
    "<path d='M42 19c-13-6-23 3-16 13c5 6 13 3 11-3'/><path d='M118 61c13 6 23-3 16-13c-5-6-13-3-11 3'/></g>"
    "<g fill='#d9aa48'><path d='M58 13q11-13 24-6q-11 13-24 6z'/><path d='M102 67q-11 13-24 6q11-13 24-6z'/>"
    "<circle cx='80' cy='40' r='3.2'/><circle cx='0' cy='40' r='3.2'/><circle cx='160' cy='40' r='3.2'/></g></svg>", safe=""))

CSS_4 = """
.fh-book { border-radius: 3px; overflow: hidden; }
.fh-unwan { position: relative; display: grid; place-items: center; padding: clamp(1.6rem, 3vw, 2.4rem) 1rem; margin: 0 clamp(1.2rem, 3vw, 2.6rem);
  background: url("VINE") center / 120px 60px, linear-gradient(180deg, #23498a, #1c3f7a 60%, #163265);
  box-shadow: inset 0 0 0 4px #1c3f7a, inset 0 0 0 5px var(--gold), inset 0 0 0 7px #1c3f7a, inset 0 0 0 8px var(--gold); }
.fh-unwan::before { content: ""; position: absolute; left: 8px; right: 8px; bottom: 100%; height: 14px;
  background: radial-gradient(circle at 50% 100%, var(--gold) 0 6px, transparent 6.5px) 0 0 / 20px 14px repeat-x; }
.fh-cart { padding: 0.9rem clamp(1.6rem, 5vw, 3.6rem); border-radius: 999px; background: var(--lf); box-shadow: 0 0 0 2px var(--gold), 0 0 0 5px #1c3f7a, 0 0 0 6px var(--gold); text-align: center; }
.fh-cart .r4-h { font-size: clamp(1.5rem, 1rem + 1.6vw, 2.3rem); background: none; color: var(--lf-ink); }
.fh-top { padding-top: clamp(1.8rem, 3vw, 2.6rem); }
.fh-body { padding: clamp(1.6rem, 3vw, 2.6rem) clamp(1.6rem, 4vw, 3.4rem) clamp(1.8rem, 3vw, 2.6rem); }
.fh-cols { columns: 2; column-gap: clamp(2rem, 5vw, 4rem); column-rule: 1px solid var(--lf-line); }
.fh-group { break-inside: avoid; margin-bottom: 1.6rem; }
.fh-rubric { display: flex; align-items: baseline; gap: 0.6rem; margin-bottom: 0.4rem; color: var(--rubric); font: italic 600 1.45rem var(--display); }
.fh-rubric small { color: var(--lf-muted); font: 500 0.66rem var(--sans); font-style: normal; letter-spacing: 0.18em; }
.fh-list { margin: 0; padding: 0; list-style: none; }
.fh-entry { display: grid; grid-template-columns: auto auto minmax(1rem, 1fr) auto; gap: 0.75rem; align-items: center; padding: 0.5rem 0; color: inherit; text-decoration: none; }
.fh-entry__t { font-family: var(--display); font-size: 1.22rem; font-weight: 600; line-height: 1.1; }
.fh-entry__t small { display: block; color: var(--lf-muted); font: 500 0.58rem var(--sans); letter-spacing: 0.2em; text-transform: uppercase; }
.fh-dots { align-self: end; margin-bottom: 0.55rem; border-bottom: 2px dotted var(--lf-line); }
.fh-entry__p { font: 600 0.8rem var(--sans); }
.fh-entry:hover .fh-entry__t, .fh-entry:focus-visible .fh-entry__t { color: var(--rubric); }
.fh-entry:hover .r4-roundel, .fh-entry:focus-visible .r4-roundel { background: var(--lf-gold); color: var(--lf); }
.fh-foot { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem; margin-top: 0.6rem; padding-top: 1.2rem; border-top: 1px solid var(--lf-line); }
.fh-foot p { color: var(--lf-muted); font-family: var(--display); font-style: italic; font-size: 1.1rem; }
.fh-glance { position: fixed; z-index: 50; top: 0; left: 0; width: 150px; height: auto; border-radius: 2px 5px 5px 2px; pointer-events: none; opacity: 0;
  box-shadow: -12px 18px 30px -12px rgba(30, 12, 2, 0.7); transform: rotate(-4deg) scale(0.92); transition: opacity 0.2s, transform 0.25s var(--ease-out); }
.fh-glance.on { opacity: 1; transform: rotate(-4deg); }

/* The page: an index of the rubrics beside the fihrist. */
.fh-layout { display: grid; grid-template-columns: 200px minmax(0, 1fr); gap: clamp(1.5rem, 3vw, 2.6rem); align-items: start; }
.fh-index { position: sticky; top: 100px; display: grid; gap: 0.2rem; }
.fh-index p { margin-bottom: 0.5rem; color: var(--g-muted); font: 600 0.6rem var(--sans); letter-spacing: 0.26em; text-transform: uppercase; }
.fh-index a { display: flex; justify-content: space-between; padding: 0.45rem 0; border-bottom: 1px solid var(--g-line); color: var(--g-text); font: italic 600 1.15rem var(--display); text-decoration: none; }
.fh-index a span { font-family: var(--urdu); font-style: normal; }
.fh-index a:hover { color: var(--rubric); }
@media (max-width: 820px) {
  .fh-cols { columns: 1; }
  .fh-layout { grid-template-columns: minmax(0, 1fr); }
  .fh-index { position: static; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); column-gap: 1rem; }
  .fh-index p { grid-column: 1 / -1; }
}
""".replace("VINE", VINE)


def fh_groups(books):
    out, n = [], 0
    for s in SHELVES:
        bs = [b for b in books if b[2] == s]
        if not bs:
            continue
        rows = []
        for b in bs:
            n += 1
            rows.append(f'<li><a class="fh-entry" href="#" {bdata(b)}><span class="r4-roundel">{ar(n)}</span>'
                        f'<span class="fh-entry__t">{esc(b[0])}<small>{esc(b[1])}</small></span><span class="fh-dots"></span>'
                        f'<span class="fh-entry__p">{PRICE}</span></a></li>')
        out.append(f'<div class="fh-group" id="{cat_id(s)}"><h3 class="fh-rubric">{esc(s)} <small>{ar(len(shelf(s)))}</small></h3>'
                   f'<ol class="fh-list">{"".join(rows)}</ol></div>')
    return "".join(out)


def fh_unwan(level):
    return f'<div class="fh-unwan"><div class="fh-cart"><{level} id="bs-h" class="r4-h">The Bookstore</{level}></div></div>'


HOME_4 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <div class="fh-book r4-leaf fh-top">
        {fh_unwan("h2")}
        <div class="fh-body">
          <div class="fh-cols">{fh_groups(FEATURED)}</div>
          <div class="fh-foot"><p>{COUNT} titles in the whole fihrist</p>{VISIT}</div>
        </div>
      </div>
    </div>
    <img class="fh-glance" alt="" width="300" height="400" src="{COVERS[BOOKS[0][0]]}">
  </section>""")

PAGE_4 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="fh-layout">
        <nav class="fh-index" aria-label="Categories"><p>Rubrics</p>{"".join(f'<a href="#{cat_id(s)}">{esc(s)}<span>{ar(len(shelf(s)))}</span></a>' for s in SHELVES)}</nav>
        <div class="fh-book r4-leaf fh-top">
          {fh_unwan("h1")}
          <div class="fh-body"><p class="r4-lede" style="margin:0 0 2rem;color:var(--lf-muted)">{LEDE}</p><div class="fh-cols">{fh_groups(BOOKS)}</div></div>
        </div>
      </div>
    </div>
    <img class="fh-glance" alt="" width="300" height="400" src="{COVERS[BOOKS[0][0]]}">
  </section>""")

JS_4 = """
<script>
  // The cover of the entry pointed at floats beside the pointer (or beside the
  // entry, from the keyboard).
  (function () {
    var g = document.querySelector(".fh-glance");
    function put(x, y) {
      var w = g.offsetWidth || 150, h = w * 4 / 3;
      x = x + w + 40 > innerWidth ? x - w - 30 : x + 30;
      g.style.left = x + "px"; g.style.top = Math.max(10, Math.min(innerHeight - h - 10, y - h / 2)) + "px";
    }
    document.querySelectorAll(".fh-entry").forEach(function (a) {
      a.addEventListener("pointerenter", function (e) {
        if (e.pointerType !== "mouse") return;
        g.src = a.dataset.img; g.classList.add("on"); put(e.clientX, e.clientY);
      });
      a.addEventListener("pointermove", function (e) { if (e.pointerType === "mouse") put(e.clientX, e.clientY); });
      a.addEventListener("pointerleave", function () { g.classList.remove("on"); });
      a.addEventListener("focus", function () { var r = a.getBoundingClientRect(); g.src = a.dataset.img; g.classList.add("on"); put(r.right, r.top + r.height / 2); });
      a.addEventListener("blur", function () { g.classList.remove("on"); });
    });
  })();
</script>"""

BUILDS.append((CSS_4, HOME_4, PAGE_4, JS_4, JS_4,
               "A classical catalogue under an illuminated unwan: red rubrics, entries numbered in roundels, dotted leaders to the price."))

# ============================================================================
# 5. Envelope flap: each book wears the pentagonal flap of an Islamic
#    binding, in its own leather with a tooled line, folded over its cover.
#    Pointing at the book (or focusing it; the first tap on a touch screen)
#    swings the flap open to show its paper lining, on which the subject,
#    the category and the price are written.
# ============================================================================
FLAP_OUT = "data:image/svg+xml," + quote(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'>"
    "<polygon points='44,5 95,5 95,95 44,95 7,50' fill='none' stroke='#d9aa48' stroke-width='1.4' vector-effect='non-scaling-stroke'/>"
    "<polygon points='47,9 91,9 91,91 47,91 13,50' fill='none' stroke='#d9aa48' stroke-width='0.7' vector-effect='non-scaling-stroke'/></svg>", safe="")
FLAP_IN = "data:image/svg+xml," + quote(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'>"
    "<polygon points='5,5 56,5 93,50 56,95 5,95' fill='none' stroke='#b07f22' stroke-width='1' vector-effect='non-scaling-stroke'/></svg>", safe="")

CSS_5 = """
.lf-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: clamp(2.4rem, 4vw, 3.4rem) clamp(1.5rem, 3vw, 2.5rem); }
.lf-card { display: block; color: var(--g-text); text-decoration: none; }
.lf-book { position: relative; display: block; width: 64%; perspective: 1400px; }
.lf-book > img { display: block; width: 100%; height: auto; border-radius: 2px 3px 3px 2px; box-shadow: -10px 16px 26px -12px rgba(30, 12, 2, 0.65); }
.lf-flap { position: absolute; z-index: 2; top: 0; left: 100%; width: 46%; height: 100%; transform-origin: 0 50%; transform: rotateY(-179.5deg); transform-style: preserve-3d;
  transition: transform 0.85s var(--ease-out); }
.lf-flap > span { position: absolute; inset: 0; backface-visibility: hidden; }
.lf-out { transform: rotateY(180deg); clip-path: polygon(40% 0, 100% 0, 100% 100%, 40% 100%, 0 50%);
  background: url("OUT") 0 0 / 100% 100%, linear-gradient(90deg, rgba(0, 0, 0, 0.32), rgba(255, 255, 255, 0.08) 40%, rgba(0, 0, 0, 0.12)), var(--tone); }
.lf-in { display: flex; flex-direction: column; justify-content: center; gap: 0.4rem; padding: 0 34% 0 12%; clip-path: polygon(0 0, 60% 0, 100% 50%, 60% 100%, 0 100%);
  background: url("IN") 0 0 / 100% 100%, linear-gradient(90deg, rgba(60, 30, 8, 0.18), transparent 20%), color-mix(in oklab, var(--tone) 8%, #f1e3c4); color: #2c1a0d; }
.lf-in small { color: #a3301c; font: 600 0.52rem/1.3 var(--sans); letter-spacing: 0.2em; text-transform: uppercase; }
.lf-in i { font-family: var(--display); font-size: 0.95rem; line-height: 1.1; }
.lf-in b { margin-top: 0.3rem; font: 600 0.78rem var(--sans); }
.lf-card:hover .lf-flap, .lf-card:focus-visible .lf-flap, .lf-card.open .lf-flap { transform: rotateY(0); }
.lf-card:focus-visible { outline: none; }
.lf-card:focus-visible .lf-book > img { outline: 2px solid var(--rubric); outline-offset: 4px; }
.lf-t { display: block; margin-top: 1.1rem; font-family: var(--display); font-size: 1.35rem; font-weight: 600; line-height: 1.1; }
.lf-lead { grid-column: span 2; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 2rem; align-items: center; }
.lf-intro { display: flex; flex-direction: column; justify-content: center; gap: 1.2rem; }
.lf-intro .r4-head { margin-bottom: 0; }
.lf-intro p.lf-how { color: var(--g-muted); font-family: var(--display); font-size: 1.15rem; font-style: italic; }
.lf-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2.2rem; }
.lf-chips button { padding: 0.55rem 1rem; border: 1px solid var(--g-line); border-radius: 2px; background: none; color: var(--g-text); font: 500 0.8rem var(--sans); cursor: pointer; }
.lf-chips button[aria-pressed="true"] { border-color: var(--rubric); background: var(--rubric); color: #fbeedd; }
[data-theme="dark"] .lf-chips button[aria-pressed="true"] { border-color: var(--gold); background: var(--gold); color: var(--espresso); }
.lf-grid--page { grid-template-columns: repeat(4, minmax(0, 1fr)); }
@media (max-width: 980px) { .lf-grid, .lf-grid--page { grid-template-columns: repeat(2, minmax(0, 1fr)); } .lf-intro { grid-column: 1 / -1; } }
@media (max-width: 560px) { .lf-grid, .lf-grid--page { grid-template-columns: minmax(0, 1fr); } .lf-book { width: 56%; } }
@media (prefers-reduced-motion: reduce) { .lf-flap { transition: none; } }
""".replace("OUT", FLAP_OUT).replace("IN\"", FLAP_IN + "\"")


def lf_card(b):
    return (f'<a class="lf-card" href="#" style="--tone:{tone(b)}" data-cat="{cat_id(b[2])}"><span class="lf-book">{img(b)}'
            f'<span class="lf-flap"><span class="lf-out"></span><span class="lf-in"><small>{esc(b[1])}</small><i>{esc(b[2])}</i><b>{PRICE}</b></span></span></span>'
            f'<span class="lf-t">{esc(b[0])}</span></a>')


HOME_5 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap lf-grid">
      <div class="lf-intro">{head()}<p class="lf-how">Open a book's flap to see its price.</p>{VISIT}</div>
      {"".join(lf_card(b) for b in FEATURED[:5])}
    </div>
  </section>""")

PAGE_5 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      {page_head()}
      <div class="lf-chips" role="group" aria-label="Category"><button type="button" aria-pressed="true" data-f="all">All</button>{"".join(f'<button type="button" aria-pressed="false" data-f="{cat_id(s)}">{esc(s)}</button>' for s in SHELVES)}</div>
      <div class="lf-grid lf-grid--page">{"".join(lf_card(b) for b in BOOKS)}</div>
    </div>
  </section>""")

JS_5 = """
<script>
  // On a touch screen the first tap opens the flap, the second follows the link.
  (function () {
    document.querySelectorAll(".lf-card").forEach(function (c) {
      var touch = false;
      c.addEventListener("pointerdown", function (e) { touch = e.pointerType === "touch"; });
      c.addEventListener("click", function (e) {
        if (touch && !c.classList.contains("open")) {
          e.preventDefault();
          document.querySelectorAll(".lf-card.open").forEach(function (o) { o.classList.remove("open"); });
          c.classList.add("open");
        }
      });
    });
    var chips = document.querySelectorAll(".lf-chips button");
    chips.forEach(function (b) {
      b.addEventListener("click", function () {
        chips.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        document.querySelectorAll(".lf-grid .lf-card").forEach(function (c) { c.hidden = b.dataset.f !== "all" && c.dataset.cat !== b.dataset.f; });
      });
    });
  })();
</script>"""

BUILDS.append((CSS_5, HOME_5, PAGE_5, JS_5, JS_5,
               "Each book wears an Islamic binding's pentagonal envelope flap, which swings open to show the subject and price on its lining."))

# ============================================================================
# 6. Colophon: each book on a ruled leaf, its particulars set beneath the
#    cover as a colophon is often set - lines narrowing to a point, closed by
#    three dots. The lead book's leaf is laid sideways, its colophon large.
#    The page: a leaf for every book, the categories as tapered rubrics.
# ============================================================================
CSS_6 = """
.cl-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: clamp(1rem, 2vw, 1.6rem); }
.cl-leaf { display: flex; flex-direction: column; align-items: center; padding: 2.1rem 1.6rem 1.8rem; border-radius: 3px; color: var(--lf-ink); text-align: center; text-decoration: none;
  transition: transform 0.4s var(--ease-out); }
a.cl-leaf:hover, a.cl-leaf:focus-visible { transform: translateY(-5px); }
a.cl-leaf:focus-visible { outline: 2px solid var(--rubric); outline-offset: 3px; }
.cl-leaf img { width: 66%; height: auto; border-radius: 2px 4px 4px 2px; box-shadow: -8px 12px 20px -10px rgba(30, 12, 2, 0.6); }
/* The taper: each line under a rule shorter than the last, down to the three dots. */
.cl-col { display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: 1.3rem; font-family: var(--display); font-size: 1.05rem; line-height: 1.2; }
.cl-col > span + span::before { content: ""; display: block; width: var(--rw); height: 1px; margin: 0.55em auto; background: var(--lf-gold); opacity: 0.6; }
.cl-col > span { display: block; width: 100%; }
.cl-col > span:nth-child(2) { --rw: 72%; } .cl-col > span:nth-child(3) { --rw: 48%; } .cl-col > span:nth-child(4) { --rw: 26%; }
.cl-col b { font-size: 1.32em; font-weight: 600; }
.cl-col em { color: var(--rubric); font: 600 0.62em var(--sans); letter-spacing: 0.24em; text-transform: uppercase; }
.cl-col i { color: var(--lf-muted); }
.cl-col strong { font: 600 0.76em var(--sans); }
.cl-dots { width: 22px; height: 18px; margin-top: 0.4rem;
  background: radial-gradient(circle, var(--rubric) 2.4px, transparent 3px) 50% 0 / 8px 8px no-repeat, radial-gradient(circle, var(--rubric) 2.4px, transparent 3px) 0 100% / 8px 8px no-repeat,
    radial-gradient(circle, var(--rubric) 2.4px, transparent 3px) 100% 100% / 8px 8px no-repeat; }
.cl-lead { grid-column: span 2; flex-direction: row; align-items: center; gap: 1.8rem; padding: 2.6rem 2.4rem; text-align: center; }
.cl-lead img { width: 46%; }
.cl-lead .cl-body { flex: 1; display: flex; flex-direction: column; align-items: center; }
.cl-lead .cl-col { font-size: 1.45rem; margin-top: 0; }
.cl-intro { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem; padding: 1.8rem 1rem; border: 1px solid var(--g-line); border-radius: 3px; text-align: center; }
.cl-intro .r4-h { font-size: clamp(1.5rem, 1rem + 1.4vw, 2.1rem); }
.cl-intro .r4-count { font-size: 1.05rem; }
.cl-rubric { grid-column: 1 / -1; display: flex; flex-direction: column; align-items: center; margin: 1.6rem 0 0.2rem; }
.cl-rubric h2 { color: var(--rubric); font: italic 600 1.7rem var(--display); }
[data-theme="dark"] .cl-rubric h2 { color: var(--gold); }
.cl-rubric p { width: 9rem; padding-top: 0.3rem; border-top: 1px solid var(--g-line); color: var(--g-muted); font: 500 0.66rem var(--sans); letter-spacing: 0.2em; text-align: center; text-transform: uppercase; }
.cl-rubric .cl-dots { margin-top: 0.5rem; }
@media (max-width: 980px) { .cl-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) {
  .cl-grid { grid-template-columns: minmax(0, 1fr); }
  .cl-lead { grid-column: auto; flex-direction: column; }
  .cl-lead .cl-col { font-size: 1.1rem; }
}
"""


def cl_col(b):
    return (f'<p class="cl-col"><span><b>{esc(b[0])}</b></span><span><em>{esc(b[1])}</em></span><span><i>{esc(b[2])}</i></span><span><strong>{PRICE}</strong></span></p>'
            f'<span class="cl-dots" aria-hidden="true"></span>')


def cl_leaf(b):
    return f'<a class="cl-leaf r4-leaf r4-jadwal" href="#">{img(b)}{cl_col(b)}</a>'


L = FEATURED[0]
HOME_6 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap cl-grid">
      <a class="cl-leaf cl-lead r4-leaf r4-jadwal" href="#">{img(L)}<span class="cl-body">{cl_col(L)}</span></a>
      <div class="cl-intro"><h2 id="bs-h" class="r4-h">The Bookstore</h2><p class="r4-count">{COUNT} titles</p>{VISIT}</div>
      {"".join(cl_leaf(b) for b in FEATURED[1:6])}
    </div>
  </section>""")

PAGE_6 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      {page_head()}
      <div class="cl-grid">{"".join(f'<div class="cl-rubric"><h2>{esc(s)}</h2><p>{len(shelf(s))} titles</p><span class="cl-dots" aria-hidden="true"></span></div>' + "".join(cl_leaf(b) for b in shelf(s)) for s in SHELVES)}</div>
    </div>
  </section>""")

BUILDS.append((CSS_6, HOME_6, PAGE_6, "", "",
               "Each book on a ruled leaf, its particulars set beneath the cover as a colophon narrowing to a point and closed by three dots."))

# ============================================================================
# 7. Ebru: the books mounted as album pages in borders of marbled paper -
#    combed and swirled, in each binding's colours with the paper and gold -
#    a gilt rule between the marbling and the page. Pointing at one sets its
#    marbling drifting. The page: an album, each category opened by a band
#    of marbling.
# ============================================================================


def mix(a, b, t):
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


def marble(c, seed):
    cols = [c, "#ecdcb9", mix(c, "#000000", 0.25), "#c89c48", mix(c, "#ffffff", 0.45), "#e4d0a8"]
    widths = [30, 12, 20, 6, 16, 10]
    x, bands = 0, []
    for col, w in zip(cols, widths):
        bands.append(f"<rect x='{x}' width='{w}' height='600' fill='{col}'/>")
        x += w
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='420' height='420'><defs>"
           f"<pattern id='p' width='{x}' height='600' patternUnits='userSpaceOnUse'>{''.join(bands)}</pattern>"
           f"<filter id='f' x='-100' y='-100' width='620' height='620' filterUnits='userSpaceOnUse'>"
           f"<feTurbulence type='turbulence' baseFrequency='0.0035 0.011' numOctaves='2' seed='{seed}' result='a'/>"
           f"<feDisplacementMap in='SourceGraphic' in2='a' scale='170' xChannelSelector='R' yChannelSelector='G' result='b'/>"
           f"<feTurbulence type='fractalNoise' baseFrequency='0.014' numOctaves='1' seed='{seed + 7}' result='c'/>"
           f"<feDisplacementMap in='b' in2='c' scale='22' xChannelSelector='R' yChannelSelector='G'/></filter></defs>"
           f"<rect x='-100' y='-100' width='620' height='620' fill='url(#p)' filter='url(#f)' transform='rotate(-8 210 210)'/></svg>")
    return "data:image/svg+xml," + quote(svg, safe="")


EB_CLASSES = "\n".join(f".eb-{k} {{ --marble: url(\"{marble(v, i + 3)}\"); }}" for i, (k, v) in enumerate(r3.TONES.items()))
EB_BAND = marble("#8a5f38", 21)

CSS_7 = """
.eb-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: clamp(1rem, 2.2vw, 1.8rem); }
.eb-page { display: block; padding: clamp(12px, 1.6vw, 18px); border-radius: 2px; background: var(--marble) 0 0 / 420px 420px, var(--tone); color: var(--lf-ink); text-decoration: none;
  box-shadow: 0 26px 40px -26px rgba(40, 18, 4, 0.75); transition: background-position 6s linear, transform 0.4s var(--ease-out); }
a.eb-page:hover, a.eb-page:focus-visible { background-position: -160px 120px; transform: translateY(-4px); }
a.eb-page:focus-visible { outline: 2px solid var(--rubric); outline-offset: 4px; }
.eb-inner { display: flex; flex-direction: column; height: 100%; padding: 1.4rem 1.3rem 1.3rem; background: radial-gradient(130% 100% at 50% 30%, var(--lf), var(--lf-2));
  box-shadow: 0 0 0 1px #b07f22, 0 0 0 3px #e8cf8e, 0 0 0 4px #b07f22, inset 0 0 18px rgba(80, 50, 10, 0.12); }
.eb-inner img { width: 72%; height: auto; margin: 0 auto 1.1rem; border-radius: 2px 4px 4px 2px; box-shadow: -8px 12px 20px -10px rgba(30, 12, 2, 0.6); }
.eb-t { font-family: var(--display); font-size: 1.3rem; font-weight: 600; line-height: 1.1; }
.eb-p { margin-top: auto; padding-top: 0.7rem; border-top: 1px solid var(--lf-line); display: flex; justify-content: space-between; font: 600 0.78rem var(--sans); }
.eb-p span { color: var(--lf-muted); font-weight: 500; }
.eb-inner .r4-kick { margin-bottom: 0.35rem; }
.eb-lead { grid-column: span 2; grid-row: span 2; }
.eb-lead .eb-inner { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 1.6rem; align-items: center; padding: 2rem; }
.eb-lead .eb-inner img { width: 100%; margin: 0; }
.eb-lead .eb-t { font-size: clamp(1.8rem, 1.2rem + 1.6vw, 2.5rem); }
.eb-lead .eb-p { margin-top: 1.4rem; }
.eb-intro { grid-column: span 2; display: flex; flex-direction: column; justify-content: center; gap: 1.1rem; }
.eb-intro .r4-head { margin-bottom: 0; }
.eb-band { grid-column: 1 / -1; display: flex; align-items: center; justify-content: center; margin-top: 1.4rem; padding: 14px; border-radius: 2px; background: url("BAND") 0 0 / 420px 420px; }
.eb-band h2 { padding: 0.5rem 1.8rem; background: var(--lf); color: var(--lf-ink); box-shadow: 0 0 0 1px #b07f22, 0 0 0 3px #e8cf8e, 0 0 0 4px #b07f22; font: italic 600 1.5rem var(--display); }
.eb-band h2 small { margin-left: 0.6rem; color: var(--lf-muted); font: 500 0.66rem var(--sans); font-style: normal; letter-spacing: 0.2em; }
@media (max-width: 980px) { .eb-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) {
  .eb-grid { grid-template-columns: minmax(0, 1fr); }
  .eb-lead, .eb-intro { grid-column: auto; }
  .eb-lead .eb-inner { grid-template-columns: minmax(0, 1fr); }
}
@media (prefers-reduced-motion: reduce) { .eb-page { transition: none; } }
""".replace("BAND", EB_BAND) + EB_CLASSES


def eb_page(b, lead=False):
    inner = (f'{img(b)}<span><p class="r4-kick">{esc(b[1])}</p><span class="eb-t">{esc(b[0])}</span>'
             f'<span class="eb-p"><span>{esc(b[2])}</span>{PRICE}</span></span>') if lead else (
        f'{img(b)}<p class="r4-kick">{esc(b[1])}</p><span class="eb-t">{esc(b[0])}</span><span class="eb-p"><span>{esc(b[2])}</span>{PRICE}</span>')
    return f'<a class="eb-page eb-{b[3]}{" eb-lead" if lead else ""}" href="#" style="--tone:{tone(b)}"><span class="eb-inner">{inner}</span></a>'


HOME_7 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap eb-grid">
      {eb_page(FEATURED[0], True)}
      <div class="eb-intro">{head()}{VISIT}</div>
      {"".join(eb_page(b) for b in FEATURED[1:3])}
    </div>
  </section>""")

PAGE_7 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      {page_head()}
      <div class="eb-grid">{"".join(f'<div class="eb-band"><h2>{esc(s)}<small>{len(shelf(s))} titles</small></h2></div>' + "".join(eb_page(b) for b in shelf(s)) for s in SHELVES)}</div>
    </div>
  </section>""")

BUILDS.append((CSS_7, HOME_7, PAGE_7, "", "",
               "The books mounted like album pages in borders of marbled paper in each binding's colours; the marbling drifts when pointed at."))

# ============================================================================
# 8. Tree of sciences: the stock drawn as the branching diagrams that
#    classified the sciences - the bookstore at the root, a branch for each
#    category, the books as its leaves, joined by gold brackets. On the home
#    page the featured books hang from their branches and the other branches
#    give their count. The page is the whole tree.
# ============================================================================
CSS_8 = """
.sj { padding: clamp(1.6rem, 3vw, 2.8rem); border-radius: 3px; overflow-x: auto; }
.sj-tree { --c: var(--lf-gold); display: flex; align-items: center; min-width: 760px; }
.sj-root { flex: none; display: flex; flex-direction: column; align-items: center; gap: 0.6rem; width: 240px; padding: 1.6rem 1.2rem; border-radius: 999px / 40%;
  background: var(--lf); box-shadow: 0 0 0 1px var(--c), 0 0 0 4px var(--lf), 0 0 0 5px var(--c); text-align: center; }
.sj-root .r4-h { font-size: 1.5rem; background: none; color: var(--lf-ink); }
.sj-root .r4-go { font-size: 0.6rem; }
.sj-root .r4-count { font-size: 1rem; }
.sj ul { position: relative; display: flex; flex-direction: column; justify-content: center; margin: 0; padding: 0 0 0 44px; list-style: none; }
.sj ul::before { content: ""; position: absolute; left: 0; top: 50%; width: 22px; border-top: 1.5px solid var(--c); }
.sj li { position: relative; display: flex; align-items: center; padding: 5px 0; }
.sj li::before { content: ""; position: absolute; left: -22px; top: 0; bottom: 0; width: 22px; border-left: 1.5px solid var(--c); }
.sj li::after { content: ""; position: absolute; left: -22px; top: 50%; width: 22px; border-top: 1.5px solid var(--c); }
.sj li:first-child::before { top: 50%; border-top: 1.5px solid var(--c); border-top-left-radius: 14px; }
.sj li:last-child::before { bottom: 50%; border-bottom: 1.5px solid var(--c); border-bottom-left-radius: 14px; }
.sj li:first-child::after, .sj li:last-child::after { display: none; }
.sj li:only-child::before { top: 50%; bottom: auto; border-left: 0; border-radius: 0; }
.sj-node { flex: none; width: 170px; padding: 0.7rem 1rem; border-radius: 999px; background: var(--lf); box-shadow: inset 0 0 0 1px var(--c); text-align: center; }
.sj-node b { display: block; color: var(--rubric); font: italic 600 1.25rem/1.1 var(--display); }
.sj-node small { color: var(--lf-muted); font: 500 0.58rem var(--sans); letter-spacing: 0.2em; text-transform: uppercase; }
.sj-leaf { display: grid; grid-template-columns: 44px minmax(0, 1fr) auto; gap: 0.9rem; align-items: center; width: 470px; max-width: 100%; padding: 0.45rem 1rem 0.45rem 0.45rem;
  border-radius: 6px 30px 30px 6px; background: color-mix(in oklab, var(--tone) 7%, var(--lf)); box-shadow: inset 0 0 0 1px var(--lf-line); color: var(--lf-ink); text-decoration: none;
  transition: transform 0.3s var(--ease-out), box-shadow 0.3s; }
.sj-leaf img { width: 44px; height: auto; border-radius: 1px 3px 3px 1px; box-shadow: -3px 4px 8px -3px rgba(30, 12, 2, 0.6); }
.sj-leaf b { display: block; font-family: var(--display); font-size: 1.12rem; font-weight: 600; line-height: 1.1; }
.sj-leaf small { color: var(--lf-muted); font: 500 0.58rem var(--sans); letter-spacing: 0.2em; text-transform: uppercase; }
.sj-leaf > span:last-child { font: 600 0.76rem var(--sans); }
.sj-leaf:hover, .sj-leaf:focus-visible { transform: translateX(6px); box-shadow: inset 0 0 0 1px var(--rubric); }
.sj-leaf:focus-visible { outline: 2px solid var(--rubric); outline-offset: 2px; }
.sj-more { color: var(--rubric); font: 600 0.62rem var(--sans); letter-spacing: 0.2em; text-decoration: none; text-transform: uppercase; }
@media (max-width: 760px) {
  .sj-tree { flex-direction: column; align-items: stretch; min-width: 0; }
  .sj-root { width: auto; border-radius: 3px; }
  .sj ul { padding: 0.8rem 0 0 18px; border-left: 1.5px solid var(--c); margin-left: 12px; }
  .sj ul::before, .sj li::before, .sj li::after { display: none; }
  .sj li { flex-direction: column; align-items: stretch; }
  .sj-node { width: auto; text-align: left; border-radius: 3px; }
  .sj-leaf { width: auto; }
}
"""


def sj_tree(books, level, go):
    branches = []
    for s in SHELVES:
        bs = [b for b in books if b[2] == s]
        if bs:
            leaves = "".join(f'<li><a class="sj-leaf" href="#" style="--tone:{tone(b)}">{img(b)}<span><b>{esc(b[0])}</b><small>{esc(b[1])}</small></span><span>{PRICE}</span></a></li>' for b in bs)
        else:
            leaves = f'<li><a class="sj-more" href="#">See all {len(shelf(s))} →</a></li>'
        branches.append(f'<li><div class="sj-node"><b>{esc(s)}</b><small>{len(shelf(s))} titles</small></div><ul>{leaves}</ul></li>')
    return f"""<div class="sj r4-leaf"><div class="sj-tree">
          <div class="sj-root"><{level} id="bs-h" class="r4-h">The Bookstore</{level}><p class="r4-count">{COUNT} titles</p>{VISIT if go else ""}</div>
          <ul>{"".join(branches)}</ul>
        </div></div>"""


HOME_8 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">{sj_tree(FEATURED, "h2", True)}</div>
  </section>""")

PAGE_8 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <p class="r4-lede" style="margin-top:0">{LEDE}</p>
      {sj_tree(BOOKS, "h1", False)}
    </div>
  </section>""")

BUILDS.append((CSS_8, HOME_8, PAGE_8, "", "",
               "The stock as a tree of the sciences: the bookstore at the root, the categories as branches, the books as leaves, joined by gold brackets."))

# ============================================================================
# 9. The volume: the catalogue is a bound book in leather. It opens and turns
#    from right to left, as an Arabic book does: each leaf turns over onto
#    the right, where a book's cover lies, its particulars on the page
#    facing. Turn by the buttons, by clicking a page, or by the arrow keys
#    (left onwards). The page has every book and a contents strip that turns
#    straight to a category.
# ============================================================================
CSS_9 = """
.vl { display: grid; justify-items: center; gap: 1.6rem; overflow-x: clip; padding-block: 12px; }
.vl-book { position: relative; width: min(100%, 940px); aspect-ratio: 3 / 2; container-type: inline-size; perspective: 2600px; transition: transform 0.9s var(--ease-out); outline: none; }
.vl-book.closed { transform: translateX(25%); }
.vl-book.ended { transform: translateX(-25%); }
.vl-book:focus-visible { outline: 2px dashed var(--g-line); outline-offset: 10px; }
.vl-base { position: absolute; top: 0; width: 50%; height: 100%; border-radius: 4px; background: var(--wood-dark); box-shadow: 0 30px 40px -24px rgba(30, 12, 2, 0.8); transition: opacity 0.6s; }
.vl-base--l { left: 0; border-radius: 6px 0 0 6px; }
.vl-base--r { right: 0; border-radius: 0 6px 6px 0; }
.vl-book.closed .vl-base--r, .vl-book.ended .vl-base--l { opacity: 0; }
.vl-leaf { position: absolute; top: 0; left: 0; width: 50%; height: 100%; transform-origin: 100% 50%; transform-style: preserve-3d; transition: transform 1s var(--ease-out); cursor: pointer; }
.vl-leaf.turned { transform: rotateY(180deg); }
.vl-leaf.moving { z-index: 99 !important; }
.vl-face { position: absolute; inset: 0; overflow: hidden; backface-visibility: hidden; background: radial-gradient(130% 100% at 50% 30%, var(--lf), var(--lf-2)); color: var(--lf-ink); }
.vl-front { border-radius: 4px 0 0 4px; box-shadow: inset -14px 0 18px -12px rgba(60, 30, 8, 0.35); }
.vl-back { transform: rotateY(180deg); border-radius: 0 4px 4px 0; box-shadow: inset 14px 0 18px -12px rgba(60, 30, 8, 0.35); }
.vl-frame { position: absolute; inset: 3.4cqi 3cqi; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1.2cqi; padding: 2cqi; text-align: center;
  border: 1px solid var(--lf-gold); outline: 1px solid var(--rubric); outline-offset: -5px; }
.vl-frame img { width: 62%; height: auto; border-radius: 2px 4px 4px 2px; box-shadow: -8px 12px 20px -10px rgba(30, 12, 2, 0.6); }
.vl-frame .r4-kick { font-size: max(0.5rem, 1.15cqi); }
.vl-frame h3 { font-family: var(--display); font-size: max(1rem, 3.4cqi); font-weight: 600; line-height: 1.05; }
.vl-frame .vl-c { color: var(--lf-muted); font-family: var(--display); font-size: max(0.8rem, 1.9cqi); font-style: italic; }
.vl-frame .vl-p { margin-top: 1.4cqi; padding-top: 1.2cqi; border-top: 1px solid var(--lf-line); font: 600 max(0.66rem, 1.5cqi) var(--sans); }
.vl-n { position: absolute; bottom: 1.2cqi; left: 50%; transform: translateX(-50%); color: var(--lf-muted); font: 700 max(0.7rem, 1.5cqi) var(--urdu); }
/* The cover: leather, a tooled frame, a cartouche - no medallion. */
.vl-cover { border-radius: 4px 10px 10px 4px; background: linear-gradient(90deg, rgba(0, 0, 0, 0.3), transparent 8%), linear-gradient(160deg, #6e1a1f, #4a0f13); color: var(--gold-pale);
  box-shadow: inset 0 0 0 2.4cqi #5a1418, inset 0 0 0 calc(2.4cqi + 1px) var(--gold), inset 0 0 0 calc(2.4cqi + 4px) #5a1418, inset 0 0 0 calc(2.4cqi + 5px) var(--gold); }
.vl-cover .vl-cart { position: absolute; left: 14%; right: 14%; top: 50%; transform: translateY(-50%); padding: 3cqi 1cqi; border-radius: 999px; box-shadow: 0 0 0 1px var(--gold), inset 0 0 0 3px #5a1418, inset 0 0 0 4px var(--gold); text-align: center; }
.vl-cover .r4-h { font-size: max(1.1rem, 3.2cqi); background: none; color: var(--gold-pale); }
.vl-cover p { margin-top: 1cqi; font: italic 500 max(0.8rem, 1.8cqi) var(--display); opacity: 0.85; }
.vl-end .r4-lede { margin: 0; font-size: max(0.85rem, 1.9cqi); color: var(--lf-muted); }
.vl-ctl { display: flex; align-items: center; gap: 1.2rem; }
.vl-ctl button { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.7rem 1.1rem; border: 1px solid var(--g-line); border-radius: 999px; background: none; color: var(--g-text); font: 500 0.8rem var(--sans); cursor: pointer; }
.vl-ctl button:hover:not(:disabled) { border-color: var(--g-text); }
.vl-ctl button:disabled { opacity: 0.4; cursor: default; }
.vl-count { min-width: 8rem; color: var(--g-muted); font-family: var(--display); font-size: 1.1rem; font-style: italic; text-align: center; }
.vl-toc { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.4rem 1.4rem; }
.vl-toc button { padding: 0.3rem 0; border: 0; border-bottom: 1px solid transparent; background: none; color: var(--g-text); font: italic 600 1.15rem var(--display); cursor: pointer; }
.vl-toc button:hover { border-color: var(--rubric); color: var(--rubric); }
.vl-toc span { margin-left: 0.4rem; color: var(--g-muted); font: 700 0.9rem var(--urdu); font-style: normal; }
@media (prefers-reduced-motion: reduce) { .vl-book, .vl-leaf { transition: none; } }
"""


def vl_book(books, cover_level, end_html):
    n = len(books)
    leaves = []
    for i in range(n + 1):
        if i == 0:
            front = (f'<div class="vl-face vl-front vl-cover"><div class="vl-cart"><{cover_level} id="bs-h" class="r4-h">The Bookstore</{cover_level}>'
                     f'<p>{COUNT} titles</p></div></div>')
        else:
            b = books[i - 1]
            front = (f'<div class="vl-face vl-front"><div class="vl-frame"><p class="r4-kick">{esc(b[1])}</p><h3>{esc(b[0])}</h3>'
                     f'<p class="vl-c">{esc(b[2])}</p><p class="vl-p">{PRICE}</p></div><span class="vl-n">{ar(2 * i + 1)}</span></div>')
        if i < n:
            back = f'<div class="vl-face vl-back"><div class="vl-frame">{img(books[i])}</div><span class="vl-n">{ar(2 * i + 2)}</span></div>'
        else:
            back = f'<div class="vl-face vl-back vl-end"><div class="vl-frame">{end_html}</div></div>'
        leaves.append(f'<div class="vl-leaf" style="z-index:{n + 1 - i}">{front}{back}</div>')
    return (f'<div class="vl-book closed" tabindex="0" aria-label="The catalogue, a book to turn. Left arrow turns on, right arrow turns back.">'
            f'<div class="vl-base vl-base--l"></div><div class="vl-base vl-base--r"></div>{"".join(leaves)}</div>')


VL_CTL = ('<div class="vl-ctl"><button type="button" data-dir="next">← Turn on</button><span class="vl-count" aria-live="polite">Closed</span>'
          '<button type="button" data-dir="prev">Turn back →</button></div>')

HOME_9 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap vl" data-vl>
      {vl_book(FEATURED, "h2", f'<p class="r4-kick">{COUNT} titles</p>{VISIT}')}
      {VL_CTL}
    </div>
  </section>""")

VL_ALL = [b for s in SHELVES for b in shelf(s)]
toc, k = [], 0
for s in SHELVES:
    toc.append(f'<button type="button" data-to="{k + 1}">{esc(s)}<span>{ar(len(shelf(s)))}</span></button>')
    k += len(shelf(s))

PAGE_9 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      <a class="r3-back" href="#">← Home</a>
      <div class="vl" data-vl>
        <nav class="vl-toc" aria-label="Contents">{"".join(toc)}</nav>
        {vl_book(VL_ALL, "h1", f'<p class="r4-lede">{LEDE}</p>')}
        {VL_CTL}
      </div>
    </div>
  </section>""")

JS_9 = """
<script>
  // Turned leaves lie on the right; the top unturned leaf is on the left.
  (function () {
    document.querySelectorAll("[data-vl]").forEach(function (vl) {
      var book = vl.querySelector(".vl-book"), leaves = [].slice.call(vl.querySelectorAll(".vl-leaf")), n = leaves.length, at = 0;
      var count = vl.querySelector(".vl-count"), prev = vl.querySelector("[data-dir=prev]"), next = vl.querySelector("[data-dir=next]");
      function set(k) {
        k = Math.max(0, Math.min(n, k));
        leaves.forEach(function (l, i) {
          var t = i < k;
          if (t !== l.classList.contains("turned")) {
            l.classList.add("moving");
            setTimeout(function () { l.classList.remove("moving"); }, 1000);
          }
          l.classList.toggle("turned", t);
          l.style.zIndex = t ? i + 1 : n - i;
          l.querySelectorAll("a").forEach(function (a) { a.tabIndex = t && i === k - 1 ? 0 : -1; });
        });
        at = k;
        book.classList.toggle("closed", k === 0);
        book.classList.toggle("ended", k === n);
        prev.disabled = k === 0; next.disabled = k === n;
        count.textContent = k === 0 ? "Closed" : k === n ? "The end" : "Book " + k + " of " + (n - 1);
      }
      next.addEventListener("click", function () { set(at + 1); });
      prev.addEventListener("click", function () { set(at - 1); });
      book.addEventListener("click", function (e) {
        if (e.target.closest("a")) return;
        var l = e.target.closest(".vl-leaf");
        if (l) set(l.classList.contains("turned") ? at - 1 : at + 1);
      });
      book.addEventListener("keydown", function (e) {
        if (e.key === "ArrowLeft") { e.preventDefault(); set(at + 1); }
        if (e.key === "ArrowRight") { e.preventDefault(); set(at - 1); }
      });
      vl.querySelectorAll("[data-to]").forEach(function (b) { b.addEventListener("click", function () { set(+b.dataset.to); }); });
      set(0);
    });
  })();
</script>"""

BUILDS.append((CSS_9, HOME_9, PAGE_9, JS_9, JS_9,
               "The catalogue as a leather-bound volume that turns from right to left as an Arabic book does, a cover on one page and its particulars facing."))

# ============================================================================
# 10. Study circle: the halaqa - the teacher on a dais, the students in a
#     half-circle before him. The chosen book sits on the dais with its
#     particulars; the others sit round it, facing in. Choosing one seats it
#     on the dais. The page seats each category in its own ring, the label
#     written along the ring's end. Below 760px the rings become rows.
# ============================================================================
import math

CSS_10 = """
.hq { position: relative; width: 100%; aspect-ratio: var(--ar); margin-inline: auto; }
.hq-ring { position: absolute; left: 50%; top: var(--cy); width: var(--d); aspect-ratio: 1; border-radius: 50%; transform: translate(-50%, -50%); border: 1px solid var(--g-line); clip-path: inset(50% 0 0 0); pointer-events: none; }
.hq-seat { position: absolute; left: var(--x); top: var(--y); width: var(--w); padding: 0; border: 0; background: none; cursor: pointer; transform: translate(-50%, -50%) rotate(var(--r)); transition: transform 0.4s var(--ease-out); }
.hq-seat img { display: block; width: 100%; height: auto; border-radius: 2px 4px 4px 2px; box-shadow: 0 10px 18px -10px rgba(30, 12, 2, 0.7); transition: box-shadow 0.3s; }
.hq-seat:hover, .hq-seat:focus-visible { transform: translate(-50%, -50%) rotate(var(--r)) scale(1.1); }
.hq-seat:focus-visible { outline: none; }
.hq-seat:focus-visible img { outline: 2px solid var(--rubric); outline-offset: 3px; }
.hq-seat[aria-pressed="true"] img { opacity: 0.35; }
.hq-label { position: absolute; left: var(--x); top: var(--y); transform: translate(-50%, -50%) rotate(var(--r)); color: var(--rubric); font: italic 600 1.05rem var(--display); white-space: nowrap; }
[data-theme="dark"] .hq-label { color: var(--gold); }
.hq-dais { position: absolute; left: 0; right: 0; top: 0; margin-inline: auto; display: grid; grid-template-columns: 96px minmax(0, 1fr); gap: 1.1rem; align-items: center;
  width: min(100%, 400px); padding: 1rem 1.3rem 1rem 1rem; border-radius: 3px 3px 40px 40px; text-align: left; }
.hq-dais img { width: 100%; height: auto; border-radius: 2px 4px 4px 2px; box-shadow: -6px 10px 16px -8px rgba(30, 12, 2, 0.6); }
.hq-dais h3 { margin: 0.25rem 0; font-family: var(--display); font-size: 1.45rem; font-weight: 600; line-height: 1.05; }
.hq-dais .hq-c { color: var(--lf-muted); font-family: var(--display); font-style: italic; }
.hq-dais .hq-p { margin-top: 0.5rem; font: 600 0.8rem var(--sans); }
.hq-foot { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem; margin-top: 1rem; }
@media (max-width: 760px) {
  .hq { aspect-ratio: auto; display: flex; flex-wrap: wrap; justify-content: center; gap: 0.8rem; }
  .hq-ring { display: none; }
  .hq-dais { position: relative; flex: 1 1 100%; margin-bottom: 0.6rem; }
  .hq-seat { position: relative; left: 0; top: 0; width: 78px; transform: none; }
  .hq-seat:hover, .hq-seat:focus-visible { transform: none; }
  .hq-label { position: relative; left: 0; top: 0; flex: 1 1 100%; transform: none; text-align: center; margin-top: 0.8rem; }
}
"""


def hq_seats(books, r, cy, W, H, angles, w):
    out = []
    for t, b in zip(angles, books):
        x = W / 2 + r * math.cos(math.radians(t))
        y = cy + r * math.sin(math.radians(t))
        out.append(f'<button type="button" class="hq-seat" style="--x:{x / W * 100:.2f}%;--y:{y / H * 100:.2f}%;--r:{t - 90:.1f}deg;--w:{w / W * 100:.2f}%" '
                   f'aria-pressed="false" aria-label="{esc(b[0])}" {bdata(b)}>{img(b)}</button>')
    return "".join(out)


def spread(k, a0, a1):
    return [(a0 + a1) / 2] if k == 1 else [a0 + (a1 - a0) * j / (k - 1) for j in range(k)]


def hq_dais(b):
    return f"""<div class="hq-dais r4-leaf" data-dais style="--tone:{tone(b)}" aria-live="polite">
          <img data-f="img" src="{COVERS[b[0]]}" width="300" height="400" alt="">
          <div><p class="r4-kick" data-f="s">{esc(b[1])}</p><h3 data-f="t">{esc(b[0])}</h3><p class="hq-c" data-f="c">{esc(b[2])}</p><p class="hq-p" data-f="p">{PRICE}</p></div>
        </div>"""


W, H, CY = 1000, 600, 150
HOME_10 = home(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      {head()}
      <div class="hq" style="--ar:{W}/{H}">
        <span class="hq-ring" style="--cy:{CY / H * 100:.2f}%;--d:{2 * 330 / W * 100:.2f}%"></span>
        <span class="hq-ring" style="--cy:{CY / H * 100:.2f}%;--d:{2 * 420 / W * 100:.2f}%"></span>
        {hq_dais(FEATURED[0])}
        {hq_seats(FEATURED, 330, CY, W, H, spread(6, 12, 168), 92)}
      </div>
      <div class="hq-foot"><p class="r4-count">Choose a book to seat it on the dais.</p>{VISIT}</div>
    </div>
  </section>""")

PW, PH, PCY = 1200, 820, 170
# Rings alternate odd and even counts, so no two books sit one behind the other.
RING_ORDER = ["Aqidah & Sira", "Qur'an", "Hadith", "Fiqh", "Arabic"]
RADII = [210, 300, 390, 480, 570]
rings = []
for s_, rr in zip(RING_ORDER, RADII):
    step = math.degrees(150 / rr)
    k = len(shelf(s_))
    angles = [90 + (j - (k - 1) / 2) * step for j in range(k)]
    rings.append(f'<span class="hq-ring" style="--cy:{PCY / PH * 100:.2f}%;--d:{2 * rr / PW * 100:.2f}%"></span>')
    rings.append(hq_seats(shelf(s_), rr, PCY, PW, PH, angles, 66))
    t = angles[0] - step * 0.95
    lx, ly = PW / 2 + rr * math.cos(math.radians(t)), PCY + rr * math.sin(math.radians(t))
    rings.append(f'<span class="hq-label" style="--x:{lx / PW * 100:.2f}%;--y:{ly / PH * 100:.2f}%;--r:{t - 90:.1f}deg">{esc(s_)}</span>')

PAGE_10 = page_main(f"""
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
      {page_head()}
      <div class="hq" style="--ar:{PW}/{PH}">
        {hq_dais(BOOKS[0])}
        {"".join(rings)}
      </div>
    </div>
  </section>""")

JS_10 = f"""
<script>
  // A book chosen takes the dais; its seat is left marked.
  (function () {{{FILL_JS}
    var dais = document.querySelector("[data-dais]"), seats = document.querySelectorAll(".hq-seat");
    seats.forEach(function (s) {{
      s.addEventListener("click", function () {{
        seats.forEach(function (x) {{ x.setAttribute("aria-pressed", String(x === s)); }});
        fill(dais, s);
      }});
    }});
    var first = [].find.call(seats, function (s) {{ return s.dataset.t === dais.querySelector("h3").textContent; }});
    if (first) first.setAttribute("aria-pressed", "true");
  }})();
</script>"""

BUILDS.append((CSS_10, HOME_10, PAGE_10, JS_10, JS_10,
               "The halaqa: the chosen book on the dais, the others seated in a half-circle before it; the page seats each category in its own ring."))


if __name__ == "__main__":
    for (slug, name), (css, h, p, hjs, pjs, blurb) in zip(OPTIONS, BUILDS):
        (HERE / f"{slug}.html").write_text(page(f"{slug}.html", slug, name, blurb, css, h, hjs))
        (HERE / f"{slug}-page.html").write_text(page(f"{slug}-page.html", slug, name, blurb, css, p, pjs))
        print("wrote", slug)

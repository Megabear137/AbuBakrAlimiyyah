#!/usr/bin/env python3
"""The bookstore, round 6: ten mockups drawn from the three chosen as best
(best-*.html: Objects, Bento and Accordion, all with the photographs).

What those three share, and what every option here keeps:

  - The book is a thing, not a picture. It has depth (a page block, a back
    board, a spine), it leans, turns or straightens, and pointing at it is
    what makes it move. Photographs are zoomed past their grey table margin
    so only the cover shows.
  - Colour comes from the cover. Surfaces are washed in the colour measured
    from each photograph (darkened where cream text has to sit on it), so
    the page changes colour with the books instead of wearing a frame.
  - One thing opens while the rest wait: a strip widens, a tile lifts, a
    book turns to face you.
  - Editorial type: a large Cormorant head set left, "The Bookstore" with the
    second word in italic rust (gold in dark), small spaced capitals for
    subject and years, the price plain or in a pill. Rounded, borderless
    surfaces; no rules, frames, jadwal or ornament.
  - The page filters by year with chips.

The ten:

   1. Spines        - a shelf of spines in each cover's colour; the one
                      pointed at pulls out and turns to show its face.
   2. Colour stage  - a full-width band in the chosen book's colour, the book
                      large and turning on it; choosing another re-colours it.
   3. Year strips   - the seven years as tall strips in their bindings; the
                      open year shows its books standing in it. The page is
                      the years as bands that open downward.
   4. Opening books - 3D books whose covers swing open to show a first page
                      with the particulars written on it.
   5. The stack     - the books lying in a pile, spine out; the one pointed
                      at slides out and stands up beside the pile.
   6. Fan           - the covers fanned like a hand of cards on a panel that
                      takes the colour of the card pointed at.
   7. Spectrum      - every book on one wall, sorted by the colour of its
                      cover, tile against tile.
   8. Swatches      - each book as a paint-swatch card: a block of its colour,
                      the cover over it, three lighter shades beneath.
   9. Table         - the books lying on a table seen in perspective; the one
                      pointed at lifts off it.
  10. Display cases - lit cases in each cover's colour, a book standing in
                      each, turning to face you; the lead case is four cells.

Content is the real content/bookstore.json and its photographs (see round 5,
whose data and helpers this reuses; the colours need Pillow). The page's
lede is still TODO. No star patterns, no arches, no invented copy.

Option 2 is also written as best-4-stage(-page).html, the fourth of the best
options (best-*.html, round 5's switcher).

Edit this file, not the output:  python3 generate_round6.py
"""
import colorsys
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("round5", HERE / "generate_round5.py")
r5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r5)

esc, ARROW, BOOKS, HOME, YEARS, ROMAN, COUNT, LEDE = r5.esc, r5.ARROW, r5.BOOKS, r5.HOME, r5.YEARS, r5.ROMAN, r5.COUNT, r5.LEDE
VISIT_LABEL, deep, yrs, years_line = r5.VISIT_LABEL, r5.deep, r5.yrs, r5.years_line


def pic(b, cls="", lazy=True):
    """Every picture here is the book's tight crop (round 5's crops/)."""
    return r5.pic(b, cls, lazy, tight=True)
PAGE = ' aria-current="page"'
YEAR_TONES = dict(zip(YEARS, ["#1c3f7a", "#0f5560", "#2e2c33", "#6e1a1f", "#4b2458", "#39434e", "#0c4a54"]))
MORE = HOME + [b for b in BOOKS if b not in HOME]


def in_year(y):
    return [b for b in BOOKS if y in b["years"]]


def back(b):
    return deep(b["tint"], 0.26)


OPTIONS = [
    ("r6-01-spines", "Spines"),
    ("r6-02-stage", "Colour stage"),
    ("r6-03-years", "Year strips"),
    ("r6-04-opening", "Opening books"),
    ("r6-05-stack", "The stack"),
    ("r6-06-fan", "Fan"),
    ("r6-07-spectrum", "Spectrum"),
    ("r6-08-swatches", "Swatches"),
    ("r6-09-table", "Table"),
    ("r6-10-cases", "Display cases"),
]


def switcher(slug, is_page):
    sfx = "-page" if is_page else ""
    links = "".join(f'<a href="{s}{sfx}.html" title="{n}"{PAGE if s == slug else ""}>{i + 1}</a>' for i, (s, n) in enumerate(OPTIONS))
    return f"""
<nav class="m-switch" aria-label="Mockups">
  <a href="1-shelf{sfx}.html">R1</a><a href="r2-1-window{sfx}.html">R2</a><a href="r3-01-bento{sfx}.html">R3</a><a href="r4-01-hashiya{sfx}.html">R4</a><a href="r5-01-studio{sfx}.html">R5</a><a href="best-1-objects{sfx}.html">Best</a><a href="r6-01-spines{sfx}.html"{PAGE}>R6</a><i></i>{links}<i></i>
  <a href="{slug}.html"{"" if is_page else PAGE}>Home</a><a href="{slug}-page.html"{PAGE if is_page else ""}>Page</a><i></i>
  <button type="button" data-set-theme="light">Light</button>
  <button type="button" data-set-theme="dark">Dark</button>
</nav>"""


# ---------------------------------------------------------------------------
# Shared: the editorial head, the chips, the 3D book, the viewer that a
# picker fills, the opener for rows where one item opens at a time.
# ---------------------------------------------------------------------------
SHARED = """
@property --c { syntax: "<color>"; inherits: true; initial-value: #1c3f7a; }
.r6-head h2, .r6-head h1 { color: var(--g-text); font-family: var(--display); font-size: clamp(2.8rem, 2rem + 2.6vw, 4.6rem); font-weight: 500; line-height: 0.95; }
.r6-head em { color: var(--rust-ink); }
[data-theme="dark"] .r6-head em { color: var(--gold-light); }
.r6-head p { max-width: 26rem; margin-top: 0.9rem; color: var(--g-muted); font-family: var(--display); font-size: 1.2rem; font-style: italic; line-height: 1.4; }
.r6-head--row { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 1rem 2rem; margin-bottom: clamp(2rem, 4vw, 3rem); }
.r6-head--row .r6-link { margin-top: 0; }
.r6-link { display: inline-flex; align-items: center; gap: 1rem; margin-top: 1.6rem; padding-bottom: 0.4rem; border-bottom: 1px solid currentColor; color: var(--g-text);
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.26em; text-decoration: none; text-transform: uppercase; }
.r6-link svg { width: 36px; transition: transform 0.3s var(--ease-out); }
.r6-link:hover svg { transform: translateX(6px); }
.r6-side { display: grid; grid-template-columns: minmax(0, 0.8fr) minmax(0, 2.2fr); gap: clamp(2rem, 5vw, 4rem); align-items: center; }
.r6-back { display: inline-block; margin-bottom: 1.2rem; color: var(--g-muted); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.3em; text-decoration: none; text-transform: uppercase; }
.r6-head--page { margin-bottom: 2rem; }
.r6-sub { font-size: 0.6rem; font-weight: 600; letter-spacing: 0.26em; text-transform: uppercase; }
.r6-pill { display: inline-block; width: max-content; padding: 0.35rem 0.8rem; border-radius: 999px; background: rgba(255, 255, 255, 0.72); color: #2a1c10; font: 600 0.8rem var(--sans); font-variant-numeric: tabular-nums; }
.r6-pill--on-dark { background: rgba(255, 255, 255, 0.14); color: #fbeedd; }
.r6-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0 0 clamp(2rem, 4vw, 3rem); }
.r6-chips button { padding: 0.6rem 1.05rem; border: 1px solid var(--g-line); border-radius: 999px; background: transparent; color: var(--g-text); font: 500 0.8rem var(--sans); cursor: pointer; transition: background 0.2s, color 0.2s; }
.r6-chips button:hover { border-color: var(--g-text); }
.r6-chips button[aria-pressed="true"] { border-color: var(--brown-ink); background: var(--brown-ink); color: #fbeedd; }
[data-theme="dark"] .r6-chips button[aria-pressed="true"] { border-color: var(--gold); background: var(--gold); color: var(--espresso); }
.r6-chips sup { margin-left: 0.25rem; font-size: 0.62rem; opacity: 0.6; }
.r6-gh { display: flex; align-items: baseline; gap: 0.8rem; margin: 0 0 1.4rem; color: var(--g-text); font-family: var(--display); font-size: 2rem; font-weight: 500; }
.r6-gh span { color: var(--g-muted); font-family: var(--sans); font-size: 0.68rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; }
.r6-group + .r6-group { margin-top: clamp(3rem, 6vw, 4.5rem); }

/* The book as an object: a face, a page block, a back board, a spine. */
.bk { --w: 150px; --h: 200px; --t: 24px; position: relative; display: block; width: var(--w); height: var(--h); transform-style: preserve-3d; transition: transform 0.7s var(--ease-out); }
.bk__face { position: absolute; inset: 0; overflow: hidden; border-radius: 1px 3px 3px 1px; background: var(--back); transform: translateZ(calc(var(--t) / 2)); }
.bk__face img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.16); }
.bk__face::after { content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(90deg, rgba(0, 0, 0, 0.32), rgba(0, 0, 0, 0) 5%, rgba(255, 255, 255, 0.14) 7%, rgba(0, 0, 0, 0) 13%, rgba(0, 0, 0, 0) 82%, rgba(255, 255, 255, 0.08)); }
.bk::before { content: ""; position: absolute; top: 3px; left: calc(var(--w) - var(--t) / 2 - 2px); width: calc(var(--t) - 2px); height: calc(var(--h) - 6px); transform: rotateY(90deg);
  background: repeating-linear-gradient(90deg, #fbf5e8 0 1px, #e2d4b9 1px 2px), #f3e9d6; }
.bk::after { content: ""; position: absolute; inset: 0; border-radius: 1px 3px 3px 1px; background: var(--back); transform: translateZ(calc(var(--t) / -2)); }
.bk__spine { --band: rgba(227, 179, 74, 0.75); position: absolute; top: 0; left: calc(var(--t) / -2); display: flex; align-items: center; justify-content: center; width: var(--t); height: 100%; overflow: hidden; transform: rotateY(-90deg);
  background: linear-gradient(transparent 7%, var(--band) 7% 7.6%, transparent 7.6% 9%, var(--band) 9% 9.6%, transparent 9.6% 90.4%, var(--band) 90.4% 91%, transparent 91% 92.4%, var(--band) 92.4% 93%, transparent 93%),
    linear-gradient(90deg, rgba(0, 0, 0, 0.4), rgba(255, 255, 255, 0.1) 35%, rgba(0, 0, 0, 0.05) 65%, rgba(0, 0, 0, 0.4)), var(--back); }
.bk__spine span { max-height: 78%; overflow: hidden; color: var(--gold-pale); font-family: var(--display); font-size: 0.82rem; font-weight: 600; line-height: 1; text-overflow: ellipsis; white-space: nowrap; writing-mode: vertical-rl; }
.bk-floor { position: absolute; left: 50%; bottom: -12px; width: 115%; height: 24px; transform: translateX(-50%); border-radius: 50%; background: radial-gradient(closest-side, rgba(30, 12, 2, 0.45), transparent); pointer-events: none; }
.r6-swap { animation: r6-in 0.55s var(--ease-out); }
@keyframes r6-in { from { opacity: 0; transform: translateY(8px); } }
@media (max-width: 1100px) { .r6-side { grid-template-columns: minmax(0, 1fr); } }
@media (prefers-reduced-motion: reduce) { .r6-swap { animation: none; } }
"""

SHARED_JS = """
<script>
  (function () {
    // Year chips: hide the groups of other years and the items not in it.
    document.querySelectorAll(".r6-chips [data-year]").forEach(function (b) {
      b.addEventListener("click", function () {
        var y = b.dataset.year;
        document.querySelectorAll(".r6-chips [data-year]").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        document.querySelectorAll("[data-group]").forEach(function (g) { g.hidden = y !== "all" && g.dataset.group !== y; });
        document.querySelectorAll("[data-in]").forEach(function (t) { t.hidden = y !== "all" && t.dataset.in.split("|").indexOf(y) < 0; });
      });
    });
    // Rows where one item opens at a time: pointing, focus or a first tap.
    document.querySelectorAll("[data-acc]").forEach(function (row) {
      var items = row.querySelectorAll("[data-acc-item]");
      function open(s) { items.forEach(function (x) { x.classList.toggle("on", x === s); }); }
      items.forEach(function (s) {
        s.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse") open(s); });
        s.addEventListener("focusin", function () { open(s); });
        s.addEventListener("click", function (e) { if (!s.classList.contains("on")) { e.preventDefault(); open(s); } });
      });
    });
    // Pickers fill the nearest viewer with a book's particulars.
    function fill(view, d) {
      view.querySelectorAll("[data-f]").forEach(function (n) {
        var v = d[n.dataset.f] || "";
        if (n.tagName === "IMG") { n.src = v; n.classList.remove("is-drawn"); } else { n.textContent = v; n.hidden = !v; }
      });
      if (d.back) view.style.setProperty("--back", d.back);
      if (d.c) view.style.setProperty("--c", d.c);
      var a = view.querySelector("[data-anim]") || view;
      a.classList.remove("r6-swap"); void a.offsetWidth; a.classList.add("r6-swap");
    }
    document.querySelectorAll("[data-pick]").forEach(function (p) {
      var view = p.closest("[data-view]") || document.querySelector("[data-view]");
      function go() {
        document.querySelectorAll("[data-pick]").forEach(function (x) { if ((x.closest("[data-view]") || view) === view) x.classList.toggle("on", x === p); });
        fill(view, p.dataset);
      }
      p.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse") go(); });
      p.addEventListener("focus", go);
      p.addEventListener("click", function (e) { if (p.tagName === "BUTTON") { go(); if (view.getBoundingClientRect().top < 0) view.scrollIntoView({ behavior: "smooth", block: "start" }); } });
    });
  })();
</script>"""


def head(level="h2", row=False, link=True, lede=None):
    p = f"<p>{esc(lede)}</p>" if lede else f"<p>{COUNT} books for all seven years</p>"
    a = f'<a class="r6-link" href="#">{esc(VISIT_LABEL)} {ARROW}</a>' if link else ""
    if row:
        return f'<div class="r6-head r6-head--row"><div><{level} id="bs-h">The <em>Bookstore</em></{level}>{p}</div>{a}</div>'
    return f'<div class="r6-head"><{level} id="bs-h">The <em>Bookstore</em></{level}>{p}{a}</div>'


def chips():
    btns = f'<button type="button" data-year="all" aria-pressed="true">All<sup>{COUNT}</sup></button>' + "".join(
        f'<button type="button" data-year="{y}" aria-pressed="false">{y}<sup>{len(in_year(y))}</sup></button>' for y in YEARS)
    return f'<div class="r6-chips" role="group" aria-label="Year">{btns}</div>'


def home(inner):
    return f"""
<main id="main" class="r3-home">
  <hr class="section-rule">
  <section aria-labelledby="bs-h">
    <div class="r3-wrap">
{inner.rstrip()}
    </div>
  </section>
  <hr class="section-rule">
</main>"""


def page_main(body, with_chips=True, top=""):
    return f"""
<main id="main" class="r3-page">
  <div class="r3-wrap">
    <a class="r6-back" href="#">← Home</a>
    {head("h1", link=False, lede=LEDE).replace('class="r6-head"', 'class="r6-head r6-head--page"')}
    {top}{chips() if with_chips else ""}
{body.rstrip()}
  </div>
</main>"""


def groups(render):
    return "\n".join(
        f'<section class="r6-group" data-group="{y}"><h2 class="r6-gh">{y}<span>{len(in_year(y))} books</span></h2>{render(in_year(y))}</section>'
        for y in YEARS)


def bk(b, cls="", style="", img_f=False):
    img = (f'<img class="is-crop" data-f="src" src="{esc(r5.tsrc(b))}" width="600" height="800" alt="">' if img_f else pic(b))
    ar = f"--h:calc(var(--w) * {min(1.5, max(1.15, b['crop_ar'])):.3f});" if b.get("crop") and not img_f else ""
    return (f'<span class="bk {cls}" style="--back:{back(b)};{ar}{style}"><span class="bk__face">{img}</span>'
            f'<span class="bk__spine"><span>{esc(b["title"])}</span></span></span>')


def price(b, cls="r6-pill"):
    if b.get("soldOut"):
        return f'<span class="{cls}">Sold out</span>'
    return f'<span class="{cls}">{esc(b["price"])}</span>' if b.get("price") else ""


def d_attrs(b):
    return (f'data-src="{esc(r5.tsrc(b))}" data-title="{esc(b["title"])}" data-ed="{esc(b.get("edition") or "")}" '
            f'data-sub="{esc(b.get("subject") or "")}" data-years="{esc(years_line(b))}" data-price="{esc(b.get("price") or "")}" '
            f'data-desc="{esc(b.get("description") or "")}" data-back="{back(b)}" data-c="{deep(b["tint"], 0.4)}"')


def copy(b, cls=""):
    """The particulars of a viewer, each filled by a picker."""
    ed_ = esc(b.get("edition") or "")
    return (f'<div class="{cls}" data-anim><p class="r6-sub" data-f="sub">{esc(b.get("subject") or "")}</p><h3 data-f="title">{esc(b["title"])}</h3>'
            f'<p class="ed" data-f="ed"{"" if ed_ else " hidden"}>{ed_}</p><p class="desc" data-f="desc">{esc(b.get("description") or "")}</p>'
            f'<p class="yr" data-f="years">{years_line(b)}</p><p class="pr" data-f="price">{esc(b.get("price") or "")}</p>'
            f'<a class="r6-link" href="#">View the book {ARROW}</a></div>')


R5_SWITCHER = r5.switcher   # round 5's own, which knows the Best set


def page(fname, slug, name, blurb, css, main, js=""):
    r5.switcher = R5_SWITCHER if slug.startswith("best-") else switcher
    out = r5.page(fname, slug, name, blurb, SHARED + css, main, SHARED_JS + js)
    return out.replace("<!-- Round 5, option", "<!-- Round 6, option")


BUILDS = []

# ============================================================================
# 1. Spines: a shelf of books standing spine out, each spine in its cover's
#    colour with gilt bands and the title down it. The one pointed at pulls
#    out, its slot widening, and turns to show its face; its name and price
#    show under the shelf. The page: a shelf a year.
# ============================================================================
CSS_1 = """
.sp-shelf { position: relative; display: flex; align-items: flex-end; justify-content: center; gap: 3px; padding-bottom: 96px; perspective: 1600px; }
.sp-shelf::before { content: ""; position: absolute; left: -10px; right: -10px; bottom: 84px; height: 12px; border-radius: 3px;
  background: linear-gradient(180deg, color-mix(in srgb, var(--g-text) 22%, transparent), color-mix(in srgb, var(--g-text) 8%, transparent)); box-shadow: 0 14px 20px -12px rgba(40, 18, 4, 0.5); }
.sp { position: relative; flex: none; width: var(--t); height: var(--h); margin-bottom: 12px; outline: none; color: var(--g-text); text-decoration: none; transition: width 0.6s var(--ease-out); }
.sp .bk { --w: 168px; position: absolute; bottom: 0; left: 50%; margin-left: calc(var(--w) / -2); transform: translateZ(calc(var(--w) / -2)) rotateY(90deg); }
.sp.on { width: 200px; }
.sp.on .bk { transform: translateZ(0) rotateY(16deg); }
.sp:focus-visible .bk__spine { outline: 2px solid var(--rust); }
.sp-cap { position: absolute; top: calc(100% + 26px); left: 50%; width: 210px; transform: translateX(-50%); text-align: center; opacity: 0; pointer-events: none; transition: opacity 0.3s; }
.sp.on .sp-cap { opacity: 1; transition-delay: 0.2s; }
.sp-cap b { display: block; font-family: var(--display); font-size: 1.15rem; font-weight: 600; line-height: 1.15; }
.sp-cap small { display: block; margin: 0.25rem 0 0.4rem; color: var(--g-muted); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; }
@media (max-width: 720px) { .sp-shelf { justify-content: flex-start; overflow-x: auto; padding-inline: 12px; } }
"""
SP_H = [232, 216, 244, 222, 208, 238]
SP_T = [40, 46, 52, 38, 44, 48]


def sp(b, k, on=False):
    return (f'<a class="sp{" on" if on else ""}" href="#" data-acc-item data-in="{esc("|".join(b["years"]))}" style="--t:{SP_T[k % 6]}px;--h:{SP_H[k % 6]}px">'
            f'{bk(b, style=f"--t:{SP_T[k % 6]}px;--h:{SP_H[k % 6]}px")}'
            f'<span class="sp-cap"><b>{esc(b["title"])}</b><small>{esc(b.get("subject") or "")} · {yrs(b)}</small>{price(b)}</span></a>')


sp_home = home(f"""
      <div class="r6-side">{head()}<div class="sp-shelf" data-acc>{"".join(sp(b, k, k == 0) for k, b in enumerate(MORE[:14]))}</div></div>""")
sp_page = page_main(groups(lambda bs: f'<div class="sp-shelf" data-acc>{"".join(sp(b, k, k == 0) for k, b in enumerate(bs))}</div>'))
BUILDS.append(("r6-01-spines", "Spines", "A shelf of spines in each cover's colour; the one pointed at pulls out and turns.", CSS_1, sp_home, sp_page, ""))

# ============================================================================
# 2. Colour stage: a band the width of the screen in the chosen book's
#    colour, the book large and swaying on it, its particulars beside it.
#    Thumbnails beneath choose another; the band re-colours as it changes.
#    The page keeps the stage on top and every book beneath it by year.
# ============================================================================
CSS_2 = """
.cs-band { --c: #1c3f7a; margin-inline: calc(50% - 50vw); padding: clamp(2.6rem, 5vw, 4rem) 0; color: #fbeedd; transition: --c 0.8s var(--ease-out);
  background: radial-gradient(55% 90% at 74% 50%, color-mix(in oklab, var(--c) 70%, #fff), transparent 70%), linear-gradient(160deg, var(--c), color-mix(in oklab, var(--c) 65%, #000)); }
.cs-inner { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr); align-items: center; gap: clamp(2rem, 5vw, 4rem); width: min(100% - 2 * var(--gutter), 1180px); margin-inline: auto; }
.cs-copy .r6-sub { color: var(--gold-pale); }
.cs-copy h3 { margin-top: 0.6rem; font-family: var(--display); font-size: clamp(2.2rem, 1.5rem + 2.4vw, 3.8rem); font-weight: 500; line-height: 1; }
.cs-copy .ed { margin-top: 0.4rem; font-family: var(--display); font-size: 1.25rem; font-style: italic; opacity: 0.8; }
.cs-copy .desc { max-width: 34rem; margin-top: 1.1rem; font-size: 0.92rem; line-height: 1.7; opacity: 0.88; }
.cs-copy .yr { margin-top: 1.1rem; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; opacity: 0.75; }
.cs-copy .pr { margin-top: 0.3rem; font-family: var(--display); font-size: 2.2rem; font-weight: 600; }
.cs-copy .r6-link { color: #fbeedd; }
.cs-obj { position: relative; display: grid; place-items: center; height: 380px; perspective: 1200px; }
.cs-obj .bk { --w: 236px; --h: 315px; --t: 34px; animation: cs-sway 7s ease-in-out infinite alternate; }
.cs-obj .bk::after { box-shadow: -20px 30px 60px 0 rgba(0, 0, 0, 0.45); }
@keyframes cs-sway { from { transform: rotateY(-28deg) rotateX(3deg); } to { transform: rotateY(-12deg) rotateX(1deg); } }
.cs-thumbs { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 14px; margin-top: 1.6rem; }
.cs-thumb { display: flex; flex-direction: column; gap: 0.45rem; padding: 0; border: 0; background: none; color: var(--g-text); font: inherit; text-align: left; cursor: pointer; }
.cs-thumb .ph { position: relative; overflow: hidden; aspect-ratio: 3 / 4; border-radius: 8px; box-shadow: 0 14px 20px -14px rgba(40, 18, 4, 0.6); transition: transform 0.4s var(--ease-out), box-shadow 0.3s; }
.cs-thumb .ph img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.16); }
.cs-thumb:hover .ph { transform: translateY(-4px); }
.cs-thumb.on .ph { box-shadow: 0 0 0 2px var(--g-bg, #f2dec6), 0 0 0 4px var(--g-mark); }
.cs-thumb .t { font-family: var(--display); font-size: 1rem; font-weight: 600; line-height: 1.15; }
.cs-thumb .p { color: var(--g-muted); font-size: 0.74rem; }
.cs-page .cs-thumbs { grid-template-columns: repeat(8, minmax(0, 1fr)); margin-top: 0; }
.cs-page .cs-band { margin-bottom: clamp(2.4rem, 5vw, 3.6rem); }
@media (max-width: 980px) { .cs-inner { grid-template-columns: 1fr; } .cs-obj { height: 340px; order: -1; } .cs-thumbs, .cs-page .cs-thumbs { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (prefers-reduced-motion: reduce) { .cs-obj .bk { animation: none; transform: rotateY(-20deg); } }
"""


def cs_band(b):
    return (f'<div class="cs-band" data-view style="--c:{deep(b["tint"], 0.4)};--back:{back(b)}"><div class="cs-inner">{copy(b, "cs-copy")}'
            f'<div class="cs-obj">{bk(b, img_f=True)}</div></div></div>')


def cs_thumb(b, on=False):
    return (f'<button class="cs-thumb{" on" if on else ""}" type="button" data-pick data-in="{esc("|".join(b["years"]))}" {d_attrs(b)}><span class="ph">{pic(b)}</span>'
            f'<span class="t">{esc(b["title"])}</span><span class="p">{esc(b.get("price") or "")}</span></button>')


cs_home = home(f"""
      {head(row=True)}
      {cs_band(HOME[0])}
      <div class="cs-thumbs">{"".join(cs_thumb(b, i == 0) for i, b in enumerate(HOME))}</div>""")
cs_page = page_main(f'<div class="cs-page">{cs_band(BOOKS[0])}' + chips() + groups(lambda bs: f'<div class="cs-thumbs">{"".join(cs_thumb(b, b is BOOKS[0]) for b in bs)}</div>') + "</div>", with_chips=False)
# The best set's copy shows only books with a photograph on the home page.
best_cs_home = home(f"""
      {head(row=True)}
      {cs_band(r5.HOME_C[0])}
      <div class="cs-thumbs">{"".join(cs_thumb(b, i == 0) for i, b in enumerate(r5.HOME_C))}</div>""")
BUILDS.append(("r6-02-stage", "Colour stage", "A full-width band in the chosen book's colour, the book large and turning on it.", CSS_2, cs_home, cs_page, ""))

# ============================================================================
# 3. Year strips: the seven years as tall strips, each in its year's
#    binding, the numeral at the head and the name running up. The open year
#    widens to show its books standing in it. The page lays the years down as
#    bands that open downward, as many open as you like.
# ============================================================================
CSS_3 = """
.ys { display: flex; gap: 8px; height: clamp(440px, 40vw, 500px); }
.ys-strip { --c: #1c3f7a; position: relative; flex: 1 1 0; min-width: 64px; overflow: hidden; border-radius: 20px; outline: none; color: #fbeedd; cursor: pointer;
  background: radial-gradient(90% 60% at 50% 0%, color-mix(in oklab, var(--c) 65%, #fff), transparent 70%), linear-gradient(170deg, var(--c), color-mix(in oklab, var(--c) 60%, #000));
  transition: flex-grow 0.7s var(--ease-out), box-shadow 0.4s; }
.ys-strip.on { flex-grow: 9; box-shadow: 0 30px 50px -30px color-mix(in oklab, var(--c) 80%, #000); cursor: default; }
.ys-strip:focus-visible { outline: 2px solid var(--rust); outline-offset: 3px; }
.ys-num { position: absolute; top: 1.1rem; left: 0; right: 0; font-family: var(--title); font-size: 1.5rem; text-align: center; color: var(--gold-pale); transition: opacity 0.3s; }
.ys-name { position: absolute; bottom: 1.3rem; left: 50%; font-family: var(--display); font-size: 1.25rem; font-weight: 600; white-space: nowrap; writing-mode: vertical-rl; transform: translateX(-50%) rotate(180deg); transition: opacity 0.3s; }
.ys-name small { margin-top: 0.6rem; font-family: var(--sans); font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase; opacity: 0.7; }
.ys-strip.on .ys-num, .ys-strip.on .ys-name { opacity: 0; }
.ys-body { position: absolute; inset: 0; display: flex; flex-direction: column; padding: clamp(1.4rem, 3vw, 2.2rem); opacity: 0; pointer-events: none; transform: translateY(10px); transition: opacity 0.3s, transform 0.5s var(--ease-out); }
.ys-strip.on .ys-body { opacity: 1; pointer-events: auto; transform: none; transition-delay: 0.25s; }
.ys-top { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; }
.ys-top h3 { font-family: var(--display); font-size: clamp(1.8rem, 1.3rem + 1.4vw, 2.6rem); font-weight: 500; }
.ys-top h3 span { margin-left: 0.6rem; font-family: var(--sans); font-size: 0.66rem; letter-spacing: 0.2em; text-transform: uppercase; opacity: 0.7; }
.ys-top a { color: #fbeedd; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.2em; text-decoration: none; text-transform: uppercase; white-space: nowrap; }
.ys-books { display: flex; align-items: flex-end; gap: clamp(14px, 2vw, 26px); margin-top: auto; perspective: 1000px; }
.ys-book { flex: none; width: 112px; color: #fbeedd; text-decoration: none; }
.ys-book .bk { --w: 112px; --h: 150px; --t: 18px; transform: rotateY(-26deg); }
.ys-book:hover .bk { transform: rotateY(-4deg) translateY(-8px); }
.ys-book b { display: block; margin-top: 0.9rem; font-family: var(--display); font-size: 1rem; font-weight: 600; line-height: 1.15; }
.ys-book small { display: block; margin-top: 0.2rem; font-size: 0.74rem; opacity: 0.75; }
/* The page: bands that open downward. */
.yb { --c: #1c3f7a; margin-bottom: 10px; overflow: hidden; border-radius: 20px; color: #fbeedd;
  background: radial-gradient(60% 120% at 0% 0%, color-mix(in oklab, var(--c) 60%, #fff), transparent 70%), linear-gradient(170deg, var(--c), color-mix(in oklab, var(--c) 60%, #000)); }
.yb summary { display: flex; align-items: center; gap: 1.2rem; padding: 1.2rem 1.6rem; cursor: pointer; list-style: none; }
.yb summary::-webkit-details-marker { display: none; }
.yb summary b { width: 3rem; color: var(--gold-pale); font-family: var(--title); font-size: 1.6rem; font-weight: 400; }
.yb summary span { font-family: var(--display); font-size: 1.6rem; font-weight: 500; }
.yb summary small { margin-left: auto; font-size: 0.66rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; opacity: 0.75; }
.yb summary::after { content: "+"; width: 2rem; font-size: 1.6rem; text-align: center; transition: transform 0.3s; }
.yb[open] summary::after { transform: rotate(45deg); }
.yb .ys-books { flex-wrap: wrap; gap: 2.2rem clamp(14px, 2vw, 26px); padding: 0.6rem 1.6rem 2rem; }
.yb .ys-book { width: 120px; }
.yb .ys-book .bk { --w: 120px; --h: 160px; }
@media (max-width: 760px) { .ys { flex-direction: column; height: auto; } .ys-strip { flex: none; height: 64px; min-width: 0; transition: height 0.6s var(--ease-out); }
  .ys-strip.on { height: 420px; } .ys-num { top: 50%; left: 1.2rem; right: auto; transform: translateY(-50%); } .ys-name { top: 50%; bottom: auto; left: 4rem; writing-mode: horizontal-tb; transform: translateY(-50%); } .ys-books { overflow-x: auto; } }
"""


def ys_book(b):
    return (f'<a class="ys-book" href="#">{bk(b)}<b>{esc(b["title"])}</b><small>{esc(b.get("price") or "")}</small></a>')


def ys_strip(y, on=False):
    bs = in_year(y)
    return (f'<div class="ys-strip{" on" if on else ""}" tabindex="0" data-acc-item style="--c:{YEAR_TONES[y]}"><span class="ys-num">{ROMAN[y]}</span>'
            f'<span class="ys-name">{y}<small>{len(bs)} books</small></span>'
            f'<div class="ys-body"><div class="ys-top"><h3>{y}<span>{len(bs)} books</span></h3><a href="#">All of {y} →</a></div>'
            f'<div class="ys-books">{"".join(ys_book(b) for b in bs[:5])}</div></div></div>')


ys_home = home(f"""
      {head(row=True)}
      <div class="ys" data-acc>{"".join(ys_strip(y, i == 0) for i, y in enumerate(YEARS))}</div>""")
ys_page = page_main("".join(
    f'<details class="yb" style="--c:{YEAR_TONES[y]}"{" open" if i == 0 else ""}><summary><b>{ROMAN[y]}</b><span>{y}</span><small>{len(in_year(y))} books</small></summary>'
    f'<div class="ys-books">{"".join(ys_book(b) for b in in_year(y))}</div></details>' for i, y in enumerate(YEARS)), with_chips=False)
BUILDS.append(("r6-03-years", "Year strips", "The seven years as tall strips in their bindings; the open one shows its books.", CSS_3, ys_home, ys_page, ""))

# ============================================================================
# 4. Opening books: each book a 3D object whose cover swings open when
#    pointed at, showing a first page washed in the cover's colour with the
#    particulars written on it, as a bookseller pencils the price inside.
# ============================================================================
CSS_4 = """
.op-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 2.6rem 1.2rem; }
.op { position: relative; display: flex; flex-direction: column; align-items: center; color: var(--g-text); text-align: center; text-decoration: none; }
.op:hover, .op:focus-visible { z-index: 2; }
.op-book { --w: 150px; --h: 200px; position: relative; width: var(--w); height: var(--h); perspective: 1300px; }
.op-page { position: absolute; inset: 0; display: flex; flex-direction: column; gap: 0.3rem; padding: 1rem 0.9rem 0.9rem 1.1rem; border-radius: 0 4px 4px 0; text-align: left; color: #2a1c10;
  background: linear-gradient(90deg, rgba(60, 30, 8, 0.18), rgba(60, 30, 8, 0) 10%), color-mix(in oklab, var(--wash) 16%, #fbf6ec);
  box-shadow: inset 0 0 0 1px rgba(60, 30, 8, 0.08), 4px 0 0 -1px #efe5d2, 6px 0 0 -2px #e2d6bf, 0 22px 30px -20px rgba(40, 18, 4, 0.7); }
.op-page .r6-sub { color: color-mix(in oklab, var(--wash) 60%, #5a3a16); }
.op-page b { font-family: var(--display); font-size: 1.12rem; font-weight: 600; line-height: 1.1; }
.op-page i { font-family: var(--display); font-size: 0.88rem; line-height: 1.15; opacity: 0.75; }
.op-page em { margin-top: auto; font-size: 0.6rem; font-style: normal; font-weight: 600; letter-spacing: 0.16em; text-transform: uppercase; opacity: 0.65; }
.op-page .r6-pill { background: color-mix(in oklab, var(--wash) 80%, #000); color: #fff; }
.op-cover { position: absolute; inset: 0; transform-origin: 0 50%; transform-style: preserve-3d; transition: transform 0.9s var(--ease-out); }
.op:hover .op-cover, .op:focus-visible .op-cover { transform: rotateY(-152deg); }
.op-front, .op-inner { position: absolute; inset: 0; overflow: hidden; border-radius: 1px 4px 4px 1px; backface-visibility: hidden; }
.op-front { box-shadow: 0 22px 30px -18px rgba(40, 18, 4, 0.75); }
.op-front img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.16); }
.op-front::after { content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0) 5%, rgba(255, 255, 255, 0.14) 7%, rgba(0, 0, 0, 0) 12%); }
.op-inner { transform: rotateY(180deg); background: radial-gradient(120% 90% at 30% 20%, color-mix(in oklab, var(--back) 70%, #fff), var(--back)); box-shadow: inset 0 0 0 8px rgba(255, 255, 255, 0.06); }
.op-name { margin-top: 1rem; font-family: var(--display); font-size: 1.12rem; font-weight: 600; line-height: 1.15; }
.op-hint { margin-top: 0.25rem; color: var(--g-muted); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; }
@media (max-width: 1100px) { .op-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (max-width: 720px) { .op-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .op-book { --w: 130px; --h: 173px; } }
"""


def op(b):
    edn = f'<i>{esc(b["edition"])}</i>' if b.get("edition") else ""
    return (f'<a class="op" href="#" data-in="{esc("|".join(b["years"]))}" style="--wash:{b["tint"]};--back:{back(b)}"><span class="op-book">'
            f'<span class="op-page"><span class="r6-sub">{esc(b.get("subject") or "")}</span><b>{esc(b["title"])}</b>{edn}<em>{years_line(b)}</em>{price(b)}</span>'
            f'<span class="op-cover"><span class="op-front">{pic(b)}</span><span class="op-inner"></span></span></span>'
            f'<span class="op-name">{esc(b["title"])}</span><span class="op-hint">{esc(b.get("subject") or "")}</span></a>')


op_home = home(f"""
      {head(row=True)}
      <div class="op-grid">{"".join(op(b) for b in HOME[:6])}</div>""")
op_page = page_main(groups(lambda bs: f'<div class="op-grid">{"".join(op(b) for b in bs)}</div>'))
BUILDS.append(("r6-04-opening", "Opening books", "3D books whose covers swing open to a first page with the particulars.", CSS_4, op_home, op_page, ""))

# ============================================================================
# 5. The stack: the books lying in a pile, spine out, each spine in its
#    cover's colour with the title gilt along it. The one pointed at slides
#    out of the pile and the book stands up beside it, turned to show its
#    face, with its particulars. The page: a pile a year, the book standing
#    in a column that stays on screen.
# ============================================================================
CSS_5 = """
.sk { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr); align-items: end; gap: clamp(2rem, 5vw, 4rem); }
.sk-pile { display: flex; flex-direction: column; align-items: flex-start; padding-bottom: 6px; border-bottom: 2px solid var(--g-line); }
.sk-bar { --band: rgba(227, 179, 74, 0.7); position: relative; display: flex; align-items: center; justify-content: space-between; gap: 1rem; width: var(--len); height: var(--th); margin-left: var(--off);
  padding: 0 1rem 0 1.4rem; border: 0; border-radius: 3px 6px 6px 3px; color: var(--gold-pale); font: inherit; text-align: left; cursor: pointer;
  background: linear-gradient(90deg, transparent 0.7rem, var(--band) 0.7rem calc(0.7rem + 1.5px), transparent calc(0.7rem + 1.5px)),
    linear-gradient(180deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0) 35%, rgba(0, 0, 0, 0.25)), var(--back);
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.25), 0 8px 10px -8px rgba(20, 8, 2, 0.6); transition: transform 0.45s var(--ease-out), filter 0.3s; }
.sk-bar:hover, .sk-bar.on { transform: translateX(28px); filter: brightness(1.12); }
.sk-bar b { overflow: hidden; font-family: var(--display); font-size: 1.05rem; font-weight: 600; text-overflow: ellipsis; white-space: nowrap; }
.sk-bar small { flex: none; font-size: 0.72rem; opacity: 0.8; }
.sk-view { display: grid; grid-template-columns: auto minmax(0, 1fr); align-items: end; gap: 1.8rem; }
.sk-obj { position: relative; perspective: 1100px; }
.sk-obj .bk { --w: 200px; --h: 267px; --t: 30px; transform: rotateY(-24deg) rotateZ(-2deg); }
.sk-obj .bk::after { box-shadow: -18px 26px 40px -6px rgba(30, 12, 2, 0.45); }
.sk-copy h3 { color: var(--g-text); font-family: var(--display); font-size: clamp(1.6rem, 1.2rem + 1.2vw, 2.3rem); font-weight: 500; line-height: 1.05; }
.sk-copy .r6-sub { color: var(--g-accent); }
.sk-copy .ed { margin-top: 0.3rem; color: var(--g-muted); font-family: var(--display); font-style: italic; }
.sk-copy .desc { display: none; }
.sk-copy .yr { margin-top: 0.8rem; color: var(--g-muted); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; }
.sk-copy .pr { margin-top: 0.2rem; color: var(--g-text); font-family: var(--display); font-size: 1.9rem; font-weight: 600; }
.sk-copy .r6-link { margin-top: 0.8rem; }
.sk--page { align-items: start; }
.sk--page .sk-view { position: sticky; top: 24px; grid-template-columns: 1fr; }
.sk--page .sk-copy .desc { display: block; margin-top: 0.8rem; color: var(--g-text); font-size: 0.88rem; line-height: 1.7; }
@media (max-width: 900px) { .sk { grid-template-columns: 1fr; } .sk--page .sk-view { position: static; order: -1; } .sk-view { grid-template-columns: 1fr; } }
"""
SK_LEN = [88, 80, 92, 76, 84, 90, 78, 86]
SK_TH = [44, 38, 50, 36, 46, 40, 52, 42]
SK_OFF = [4, 0, 2, 6, 1, 5, 0, 3]


def sk_bar(b, k, on=False):
    return (f'<button class="sk-bar{" on" if on else ""}" type="button" data-pick data-in="{esc("|".join(b["years"]))}" {d_attrs(b)} '
            f'style="--back:{back(b)};--len:{SK_LEN[k % 8]}%;--th:{SK_TH[k % 8]}px;--off:{SK_OFF[k % 8]}%"><b>{esc(b["title"])}</b><small>{esc(b.get("price") or "")}</small></button>')


def sk_view(b):
    return f'<div class="sk-view" data-view style="--back:{back(b)}"><div class="sk-obj">{bk(b, img_f=True)}<span class="bk-floor"></span></div>{copy(b, "sk-copy")}</div>'


sk_home = home(f"""
      {head(row=True)}
      <div class="sk"><div class="sk-pile">{"".join(sk_bar(b, k, k == 0) for k, b in enumerate(MORE[:9]))}</div>{sk_view(MORE[0])}</div>""")
sk_page = page_main(f'<div class="sk sk--page"><div>{groups(lambda bs: chr(10).join(["<div class=sk-pile>" + "".join(sk_bar(b, k, b is BOOKS[0]) for k, b in enumerate(bs)) + "</div>"]))}</div>{sk_view(BOOKS[0])}</div>')
BUILDS.append(("r6-05-stack", "The stack", "A pile of spines in their colours; the one pointed at slides out and stands up beside it.", CSS_5, sk_home, sk_page, ""))

# ============================================================================
# 6. Fan: the covers fanned like a hand of cards on a rounded panel that
#    takes the colour of the card pointed at; that card rises and its name
#    and price show beneath the fan. The page: a hand a year.
# ============================================================================
CSS_6 = """
.fn-panel { --c: #1c3f7a; position: relative; overflow: hidden; padding: 2.4rem 1rem 1.8rem; border-radius: 28px; transition: --c 0.7s var(--ease-out);
  background: radial-gradient(70% 90% at 50% 110%, color-mix(in oklab, var(--c) 34%, #fff8ee), color-mix(in oklab, var(--c) 18%, #fbf3e6)); }
[data-theme="dark"] .fn-panel { background: radial-gradient(70% 90% at 50% 110%, color-mix(in oklab, var(--c) 60%, #1a0d05), color-mix(in oklab, var(--c) 28%, #140a04)); }
.fn { position: relative; height: 400px; }
.fn-card { --w: 186px; position: absolute; left: calc(50% - var(--w) / 2); bottom: 56px; width: var(--w); aspect-ratio: 3 / 4; overflow: hidden; border-radius: 6px;
  transform-origin: 50% 230%; transform: rotate(var(--a)); box-shadow: -6px 14px 24px -10px rgba(30, 12, 2, 0.55); transition: transform 0.45s var(--ease-out); }
.fn-card img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.16); }
.fn-card:hover, .fn-card.on { z-index: 50 !important; transform: rotate(var(--a)) translateY(-34px); }
.fn-card:focus-visible { outline: 2px solid var(--rust); outline-offset: 3px; }
.fn-cap { margin-top: 1.6rem; color: var(--g-text); text-align: center; }
.fn-cap h3 { font-family: var(--display); font-size: 1.6rem; font-weight: 500; }
.fn-cap .r6-sub { margin-top: 0.3rem; color: var(--g-muted); }
.fn-cap .pr { margin-top: 0.3rem; font-family: var(--display); font-size: 1.4rem; font-weight: 600; }
.fn-cap .ed, .fn-cap .desc, .fn-cap .r6-link, .fn-cap > div > p:first-child { display: none; }
.fn--many .fn-card { --w: 150px; transform-origin: 50% 300%; }
@media (max-width: 720px) { .fn-card, .fn--many .fn-card { --w: 110px; bottom: 30px; } .fn { height: 260px; } }
"""


def fn_hand(bs, on=0, many=False):
    n = len(bs)
    spread = 84 if many else 56
    step = spread / max(1, n - 1)
    cards = "".join(
        f'<a class="fn-card{" on" if i == on else ""}" href="#" data-pick {d_attrs(b)} style="--a:{-spread / 2 + i * step:.1f}deg;z-index:{i}">{pic(b)}</a>'
        for i, b in enumerate(bs))
    b = bs[on]
    cap = (f'<div class="fn-cap"><div data-anim><p class="r6-sub" data-f="sub"></p><h3 data-f="title">{esc(b["title"])}</h3>'
           f'<p class="r6-sub" data-f="years">{years_line(b)}</p><p class="pr" data-f="price">{esc(b.get("price") or "")}</p></div></div>')
    return f'<div class="fn-panel" data-view style="--c:{deep(b["tint"], 0.4)}"><div class="fn{" fn--many" if many else ""}">{cards}</div>{cap}</div>'


fn_home = home(f"""
      <div class="r6-side">{head()}{fn_hand(HOME, 3)}</div>""")
fn_page = page_main(groups(lambda bs: fn_hand(bs, len(bs) // 2, many=len(bs) > 8)))
BUILDS.append(("r6-06-fan", "Fan", "The covers fanned like a hand of cards on a panel that takes the colour of the card pointed at.", CSS_6, fn_home, fn_page, ""))

# ============================================================================
# 7. Spectrum: the books on one wall, tile against tile, in the order of
#    their covers' colours - blues into teals, greens, golds, reds, purples,
#    then the greys and blacks by lightness. Pointing at a tile lifts its
#    book. The page is the whole stock as one wall; the chips thin it out.
# ============================================================================
def hue_key(b):
    c = b["tint"]
    r, g, b_ = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b_)
    return (1, l) if s < 0.14 else (0, (h + 0.42) % 1)


CSS_7 = """
.sw-wall { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); overflow: hidden; border-radius: 26px; box-shadow: 0 30px 50px -36px rgba(40, 18, 4, 0.7); }
.sw-tile { --t: #555; position: relative; display: flex; flex-direction: column; align-items: center; justify-content: space-between; gap: 0.9rem; padding: 1.4rem 1rem 1.1rem; color: #fbeedd; text-decoration: none;
  background: linear-gradient(180deg, color-mix(in oklab, var(--t) 85%, #fff), var(--t)); transition: filter 0.3s; }
.sw-tile:hover { z-index: 1; filter: brightness(1.08); }
.sw-pic { position: relative; width: 66%; aspect-ratio: 3 / 4; overflow: hidden; border-radius: 3px 5px 5px 3px; box-shadow: -8px 16px 24px -10px rgba(0, 0, 0, 0.55); transition: transform 0.5s var(--ease-out); }
.sw-pic img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.16); }
.sw-tile:hover .sw-pic { transform: translateY(-8px) rotate(-2deg); }
.sw-cap { width: 100%; text-align: center; }
.sw-cap b { display: block; font-family: var(--display); font-size: 1.02rem; font-weight: 600; line-height: 1.15; }
.sw-cap small { display: block; margin-top: 0.2rem; font-size: 0.72rem; opacity: 0.8; }
.sw-foot { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-top: 1.4rem; color: var(--g-muted); font-family: var(--display); font-size: 1.1rem; font-style: italic; }
.sw-foot .r6-link { margin-top: 0; font-style: normal; }
.sw-band { height: 8px; margin-top: 0.8rem; border-radius: 4px; }
@media (max-width: 1040px) { .sw-wall { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (max-width: 640px) { .sw-wall { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
"""


def sw_tile(b):
    return (f'<a class="sw-tile" href="#" data-in="{esc("|".join(b["years"]))}" style="--t:{deep(b["tint"], 0.42)}"><span class="sw-pic">{pic(b)}</span>'
            f'<span class="sw-cap"><b>{esc(b["title"])}</b><small>{esc(b.get("price") or "")}</small></span></a>')


SW_HOME = sorted(MORE[:12], key=hue_key)
SW_ALL = sorted(BOOKS, key=hue_key)
sw_strip = "linear-gradient(90deg, " + ", ".join(deep(b["tint"], 0.42) for b in SW_ALL) + ")"
sw_home = home(f"""
      {head(row=True, link=False)}
      <div class="sw-wall">{"".join(sw_tile(b) for b in SW_HOME)}</div>
      <div class="sw-band" style="background:{sw_strip}"></div>
      <p class="sw-foot">Every book, in the order of its cover's colour<a class="r6-link" href="#">{esc(VISIT_LABEL)} {ARROW}</a></p>""")
sw_page = page_main(f'<div class="sw-wall">{"".join(sw_tile(b) for b in SW_ALL)}</div>')
BUILDS.append(("r6-07-spectrum", "Spectrum", "Every book on one wall, sorted by the colour of its cover.", CSS_7, sw_home, sw_page, ""))

# ============================================================================
# 8. Swatches: each book a paint-swatch card - a block of its cover's colour
#    with the cover laid over it at a slant, three lighter shades beneath,
#    a number, the name and the price as a chip's label. Pointing at one
#    straightens the cover.
# ============================================================================
CSS_8 = """
.wc-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: clamp(18px, 2.2vw, 28px); }
.wc { position: relative; display: flex; flex-direction: column; overflow: hidden; border-radius: 10px; background: #fbf8f2; color: #2a1c10; text-decoration: none;
  box-shadow: 0 1px 2px rgba(40, 18, 4, 0.1), 0 24px 34px -26px rgba(40, 18, 4, 0.6); transition: transform 0.4s var(--ease-out); }
.wc:hover { transform: translateY(-5px); }
.wc-block { position: relative; display: grid; place-items: center; aspect-ratio: 1 / 0.92; background: linear-gradient(170deg, color-mix(in oklab, var(--t) 80%, #fff), var(--t)); }
.wc-pic { position: relative; width: 54%; aspect-ratio: 3 / 4; overflow: hidden; border-radius: 3px 5px 5px 3px; transform: rotate(-6deg) translateY(8%); box-shadow: -10px 18px 26px -10px rgba(0, 0, 0, 0.55); transition: transform 0.5s var(--ease-out); }
.wc-pic img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.16); }
.wc:hover .wc-pic { transform: rotate(0) translateY(2%); }
.wc-shades { display: grid; grid-template-columns: repeat(3, 1fr); height: 22px; }
.wc-shades i:nth-child(1) { background: color-mix(in oklab, var(--t) 62%, #fff); }
.wc-shades i:nth-child(2) { background: color-mix(in oklab, var(--t) 38%, #fff); }
.wc-shades i:nth-child(3) { background: color-mix(in oklab, var(--t) 18%, #fff); }
.wc-label { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 0.15rem 0.8rem; padding: 0.9rem 1rem 1.05rem; }
.wc-no { grid-column: 1 / -1; color: #8a7a66; font: 600 0.58rem var(--sans); letter-spacing: 0.22em; text-transform: uppercase; }
.wc-label b { font-family: var(--display); font-size: 1.15rem; font-weight: 600; line-height: 1.12; }
.wc-label .r6-pill { align-self: start; background: color-mix(in oklab, var(--t) 12%, #f3ece0); }
.wc-label small { grid-column: 1 / -1; color: #7a6a58; font-size: 0.7rem; }
.wc-headcell { align-self: center; }
[data-theme="dark"] .wc { background: #f1e9db; box-shadow: 0 30px 40px -26px rgba(0, 0, 0, 0.9); }
@media (max-width: 1040px) { .wc-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 640px) { .wc-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .wc-headcell { grid-column: 1 / -1; } }
"""


def wc(b):
    return (f'<a class="wc" href="#" data-in="{esc("|".join(b["years"]))}" style="--t:{deep(b["tint"], 0.45)}"><span class="wc-block"><span class="wc-pic">{pic(b)}</span></span>'
            f'<span class="wc-shades"><i></i><i></i><i></i></span><span class="wc-label"><span class="wc-no">No. {b["i"] + 1:03d} · {esc(b.get("subject") or "")}</span>'
            f'<b>{esc(b["title"])}</b>{price(b)}<small>{years_line(b)}</small></span></a>')


wc_home = home(f"""
      <div class="wc-grid"><div class="wc-headcell">{head()}</div>{"".join(wc(b) for b in HOME)}</div>""")
wc_page = page_main(groups(lambda bs: f'<div class="wc-grid">{"".join(wc(b) for b in bs)}</div>'))
BUILDS.append(("r6-08-swatches", "Swatches", "Each book a paint-swatch card in its cover's colour, three lighter shades beneath.", CSS_8, wc_home, wc_page, ""))

# ============================================================================
# 9. Table: the books lying on a table seen in perspective, each a little
#    askew, its name and price printed on the cloth beneath it. The one
#    pointed at lifts off the table toward you.
# ============================================================================
CSS_9 = """
.tb-scene { perspective: 1500px; perspective-origin: 50% 0%; padding: 10px 0 0; }
.tb-plane { display: grid; grid-template-columns: repeat(var(--n, 3), minmax(0, 1fr)); gap: 2.4rem 2rem; padding: 2.6rem 2.6rem 3.2rem; border-radius: 26px; transform: rotateX(38deg) rotateZ(-6deg) scale(0.94); transform-style: preserve-3d;
  background: radial-gradient(80% 70% at 40% 30%, #f6ead6, #e6d1b2); box-shadow: inset 0 0 0 1px rgba(120, 80, 30, 0.12), 0 60px 60px -40px rgba(40, 18, 4, 0.55); }
[data-theme="dark"] .tb-plane { background: radial-gradient(80% 70% at 40% 30%, #4a2d18, #2a180c); box-shadow: inset 0 0 0 1px rgba(227, 179, 74, 0.2), 0 60px 60px -40px rgba(0, 0, 0, 0.9); }
.tb-item { display: flex; flex-direction: column; align-items: center; color: var(--g-text); text-align: center; text-decoration: none; transform: rotate(var(--r)); transform-style: preserve-3d; }
.tb-pic { position: relative; width: 70%; aspect-ratio: 3 / 4; overflow: hidden; border-radius: 2px 4px 4px 2px; transform-style: preserve-3d;
  box-shadow: 1px 0 0 #efe4cf, 2px 0 0 #e3d5bb, 3px 1px 0 #d8c8aa, 4px 6px 8px rgba(30, 12, 2, 0.45); transition: transform 0.5s var(--ease-out), box-shadow 0.5s; }
.tb-pic img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform: scale(1.16); }
.tb-item:hover .tb-pic, .tb-item:focus-visible .tb-pic { transform: translateZ(60px) rotateX(-18deg); box-shadow: 1px 0 0 #efe4cf, 2px 0 0 #e3d5bb, 3px 1px 0 #d8c8aa, 18px 40px 40px rgba(30, 12, 2, 0.3); }
.tb-item b { margin-top: 0.9rem; font-family: var(--display); font-size: 1.1rem; font-weight: 600; line-height: 1.12; }
.tb-item small { margin-top: 0.15rem; color: var(--g-muted); font-size: 0.75rem; }
@media (max-width: 760px) { .tb-plane { --n: 2 !important; transform: rotateX(28deg) scale(0.96); padding: 1.6rem; } }
"""
TB_R = [-3, 2, -1, 3, -2, 1, 2, -3]


def tb(b, k):
    return (f'<a class="tb-item" href="#" data-in="{esc("|".join(b["years"]))}" style="--r:{TB_R[k % 8]}deg"><span class="tb-pic">{pic(b)}</span>'
            f'<b>{esc(b["title"])}</b><small>{esc(b.get("price") or "")}</small></a>')


tb_home = home(f"""
      <div class="r6-side">{head()}<div class="tb-scene"><div class="tb-plane" style="--n:3">{"".join(tb(b, k) for k, b in enumerate(HOME[:6]))}</div></div></div>""")
tb_page = page_main(groups(lambda bs: f'<div class="tb-scene"><div class="tb-plane" style="--n:5">{"".join(tb(b, k) for k, b in enumerate(bs))}</div></div>'))
BUILDS.append(("r6-09-table", "Table", "The books lying on a table in perspective; the one pointed at lifts off it.", CSS_9, tb_home, tb_page, ""))

# ============================================================================
# 10. Display cases: lit cases in each cover's colour, a book standing in
#     each, turned to show its pages, turning to face you when pointed at;
#     the name and price on the case's sill. The lead case is four cells and
#     carries the description.
# ============================================================================
CSS_10 = """
.dc-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-auto-flow: dense; gap: 16px; }
.dc { --t: #555; position: relative; display: flex; flex-direction: column; overflow: hidden; border-radius: 22px; color: #fbeedd; text-decoration: none;
  background: radial-gradient(70% 55% at 50% 0%, color-mix(in oklab, var(--t) 45%, #fff), transparent 75%), linear-gradient(180deg, var(--t), color-mix(in oklab, var(--t) 70%, #000));
  box-shadow: inset 0 18px 30px -18px rgba(0, 0, 0, 0.45), inset 0 0 0 1px rgba(255, 255, 255, 0.08), 0 24px 36px -28px rgba(40, 18, 4, 0.7); }
.dc-stage { position: relative; display: grid; place-items: end center; height: 270px; padding-bottom: 26px; perspective: 1000px; }
.dc-stage::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 30px; background: linear-gradient(180deg, rgba(255, 255, 255, 0.12), rgba(0, 0, 0, 0.12)); box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25); }
.dc .bk { --w: 138px; --h: 184px; --t: 22px; z-index: 1; transform: rotateY(-30deg); }
.dc:hover .bk, .dc:focus-visible .bk { transform: rotateY(-6deg) translateY(-8px); }
.dc .bk-floor { bottom: -8px; }
.dc-sill { display: flex; align-items: flex-end; justify-content: space-between; gap: 0.8rem; padding: 0.9rem 1.2rem 1.2rem; }
.dc-sill b { display: block; font-family: var(--display); font-size: 1.15rem; font-weight: 600; line-height: 1.12; }
.dc-sill small { display: block; margin-top: 0.2rem; font-size: 0.6rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; opacity: 0.7; }
.dc--lead { grid-column: span 2; grid-row: span 2; }
.dc--lead .dc-stage { flex: 1; height: auto; min-height: 380px; }
.dc--lead .bk { --w: 220px; --h: 293px; --t: 32px; }
.dc--lead .dc-sill b { font-size: 1.8rem; font-weight: 500; }
.dc-desc { max-width: 30rem; margin-top: 0.5rem; font-size: 0.86rem; line-height: 1.6; opacity: 0.85; }
.dc-go { grid-column: span 2; display: flex; flex-direction: column; justify-content: center; gap: 0.4rem; padding: 2rem; border-radius: 22px; box-shadow: inset 0 0 0 1px var(--g-line); }
.dc-go b { color: var(--g-text); font-family: var(--display); font-size: 3rem; font-weight: 500; line-height: 1; }
.dc-go p { color: var(--g-muted); font-family: var(--display); font-size: 1.15rem; font-style: italic; }
@media (max-width: 980px) { .dc-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .dc--lead { grid-row: auto; } }
@media (max-width: 560px) { .dc-grid { grid-template-columns: 1fr; } .dc--lead, .dc-go { grid-column: auto; } }
"""


def dc(b, lead=False):
    desc = f'<span class="dc-desc">{esc(b["description"])}</span>' if lead and b.get("description") else ""
    return (f'<a class="dc{" dc--lead" if lead else ""}" href="#" data-in="{esc("|".join(b["years"]))}" style="--t:{deep(b["tint"], 0.36)}">'
            f'<span class="dc-stage">{bk(b)}<span class="bk-floor"></span></span>'
            f'<span class="dc-sill"><span><b>{esc(b["title"])}</b><small>{esc(b.get("subject") or "")} · {yrs(b)}</small>{desc}</span>{price(b, "r6-pill r6-pill--on-dark")}</span></a>')


dc_home = home(f"""
      {head(row=True, link=False)}
      <div class="dc-grid">{dc(HOME[0], True)}{"".join(dc(b) for b in HOME[1:7])}
        <div class="dc-go"><b>{COUNT}</b><p>books for all seven years</p><a class="r6-link" href="#">{esc(VISIT_LABEL)} {ARROW}</a></div></div>""")
dc_page = page_main(groups(lambda bs: f'<div class="dc-grid">{"".join(dc(b, k == 0) for k, b in enumerate(bs))}</div>'))
BUILDS.append(("r6-10-cases", "Display cases", "Lit cases in each cover's colour, a book standing in each; the lead case is four cells.", CSS_10, dc_home, dc_page, ""))


if __name__ == "__main__":
    for slug, name, blurb, css, h, p, js in BUILDS:
        (HERE / f"{slug}.html").write_text(page(f"{slug}.html", slug, name, blurb, css, h, js))
        (HERE / f"{slug}-page.html").write_text(page(f"{slug}-page.html", slug, name, blurb, css, p, js))
    # Option 2 is also one of the best options: best-4-stage, in that set.
    for slug, name, blurb, css, h, p, js in BUILDS:
        if slug == "r6-02-stage":
            for sfx, main in (("", best_cs_home), ("-page", p)):
                (HERE / f"best-4-stage{sfx}.html").write_text(page(f"best-4-stage{sfx}.html", "best-4-stage", name, blurb, css, main, js))
    print("wrote", len(BUILDS) * 2 + 2, "files")

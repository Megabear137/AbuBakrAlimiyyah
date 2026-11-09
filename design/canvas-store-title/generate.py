#!/usr/bin/env python3
"""The bookstore page's title: seven ways to head bookstore.html in place of
the outlined tile in the grid (heading, lede and a count of the books).
None shows the count.

Each mockup is bookstore.html itself (its styles, header, footer, filters
and grid, drawn by the site's own bookstore.js) with the heading tile
hidden and an option's title above the grid. The title's slots carry the
page's data-slot names (bookstore-kicker, -heading, -lede), which come
before the tile's, so bookstore.js fills them from bookstore.json. A
`<base href="../../">` lets the pages run from here: serve the repository
root and open http://127.0.0.1:8000/design/canvas-store-title/

The content is the JSON's: heading "Bookstore", the lede (still TODO), the
kicker (empty, so hidden). No new copy, no stars.

   1. Section head - the home page's centred head: Gilda capitals in the
                     title gradient, the italic lede, the logo rule, the
                     groups centred under it.
   2. Masthead     - a very large Cormorant "Bookstore" set left, the lede in
                     a column beside it, a hairline under both.
   3. Banner       - the article page's banner, the masjid photograph, the
                     title and lede centred over it.
   4. Board        - a panel of the Details' dark board, gold title, the
                     lede in cream and the subject groups inside it.
   5. Lead tile    - the tile kept in the grid, but solid brown (glass in
                     dark) with cream type, and the groups at its foot.
   6. With covers  - the title and lede beside a fan of the featured books'
                     photographs, which spread when pointed at.
   7. One line     - the smallest: "Bookstore" and the groups on one line,
                     the lede under it.

Edit this file, not the output:  python3 generate.py
"""
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
SRC = (ROOT / "bookstore.html").read_text(encoding="utf-8")


def cut(start, end):
    i = SRC.index(start)
    return SRC[i:SRC.index(end, i)]


HEADER = cut('<header class="site-header">', "<main")
FOOTER = cut('<footer class="site-footer"', "<script src=")
SCRIPTS = SRC[SRC.index('<script src="assets/js/nav.js'):SRC.index("</body>")]
HEAD_LINKS = cut('<link rel="icon"', "</head>")

BACK = '<a class="back" href="index.html#bookstore"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg> Home</a>'
FILTERS = '<div class="store-filters" data-slot="bookstore-filters" hidden></div>'
GRID = '<div class="store" data-slot="bookstore"></div>'


def slots(kicker="", heading="", lede=""):
    return {
        "k": '<p class="%s" data-slot="bookstore-kicker"></p>' % kicker,
        "h": '<h1 class="%s" id="bookstore-heading" data-slot="bookstore-heading">Bookstore</h1>' % heading,
        "l": '<p class="%s" data-slot="bookstore-lede"></p>' % lede,
    }


OPTIONS = []


def option(slug, name, blurb, main, css, js="", body="on-ground", hide_tile=True):
    OPTIONS.append(dict(slug=slug, name=name, blurb=blurb, main=main, css=css, js=js, body=body, hide_tile=hide_tile))


# ---------------------------------------------------------------- 1
s = slots("section__eyebrow", "section__heading", "section__lede t1__lede")
option("1-section-head", "Section head",
       "The home page's own section head, centred: Gilda capitals in the title gradient, the italic lede, then the logo rule. The subject groups are centred beneath it.",
       f"""{BACK}
      <div class="section__head t1">{s['k']}{s['h']}{s['l']}</div>
      <hr class="section-rule t1__rule">
      {FILTERS}
      {GRID}""",
       """
.t1 { margin-bottom: 0; }
.t1 .section__heading { font-size: clamp(2.6rem, 1.6rem + 4vw, 4.6rem); }
.t1__lede { font-family: var(--display); font-size: 1.3rem; font-style: italic; }
.t1__rule { margin-block: 1.4rem 1.6rem; }
.store-filters { text-align: center; }
.store-groups { justify-content: center; }
""")

# ---------------------------------------------------------------- 2
s = slots("t2__kicker", "t2__title", "t2__lede")
option("2-masthead", "Masthead",
       "A very large Cormorant “Bookstore” set left like a magazine's masthead, the lede in a narrow column beside it on its baseline, a hairline under both, the groups under the line.",
       f"""{BACK}
      <div class="t2"><div>{s['k']}{s['h']}</div>{s['l']}</div>
      {FILTERS}
      {GRID}""",
       """
.t2 { display: grid; grid-template-columns: auto minmax(0, 22rem); align-items: end; justify-content: space-between; gap: 1rem 3rem; margin: 0 0 1.6rem; padding-bottom: 1.4rem; border-bottom: 1px solid var(--g-line); }
.t2__kicker { margin-bottom: 0.4rem; color: var(--g-accent); font: 600 0.62rem var(--sans); letter-spacing: 0.26em; text-transform: uppercase; }
.t2__kicker:empty, .t2__lede:empty { display: none; }
.t2__title { color: var(--g-text); font: 500 clamp(4rem, 2rem + 8vw, 9.5rem) var(--display); letter-spacing: -0.03em; line-height: 0.8; }
.t2__lede { padding-bottom: 0.4rem; color: var(--g-muted); font: italic 1.25rem/1.45 var(--display); }
@media (max-width: 760px) { .t2 { grid-template-columns: minmax(0, 1fr); } }
""")

# ---------------------------------------------------------------- 3
s = slots("", "hero__title in", "in t3__lede")
option("3-banner", "Banner",
       "The article page's banner: the masjid photograph, evenly darkened, the title and the lede centred over it, “← Home” above them. The groups and grid follow on the ground.",
       "",
       """
.t3.a-hero { min-height: max(420px, 52vh); }
.t3.a-hero .hero__title { margin-bottom: 1rem; }
.t3__lede { max-width: 34rem; margin: 0 auto; color: rgba(255, 246, 234, 0.9); font: italic 1.3rem/1.5 var(--display); }
.t3__lede:empty { display: none; }
.t3-page { padding-top: clamp(2.4rem, 5vw, 3.4rem); }
""", body="")
OPTIONS[-1]["pre"] = f"""<section class="hero a-hero t3" aria-labelledby="bookstore-heading">
    <div class="hero__img" aria-hidden="true"></div>
    <div class="wrap hero__body">
      <p class="in">{BACK}</p>
      {s['h']}
      {s['l']}
    </div>
  </section>"""
OPTIONS[-1]["main"] = f"""{FILTERS}
      {GRID}"""
OPTIONS[-1]["section"] = "section t3-page"

# ---------------------------------------------------------------- 4
s = slots("t4__kicker", "panel__title t4__title", "t4__lede")
option("4-board", "Board",
       "A panel cut from the Details' dark board (dark glass in dark), its gold line along the top: the title in bright gold, the lede in cream, and the subject groups inside it at its foot.",
       f"""{BACK}
      <div class="panel t4">{s['k']}{s['h']}{s['l']}{FILTERS}</div>
      {GRID}""",
       """
.t4 { margin-bottom: 1.8rem; padding: clamp(1.8rem, 4vw, 3rem); }
.t4__kicker { color: var(--gold); font: 600 0.62rem var(--sans); letter-spacing: 0.26em; text-transform: uppercase; }
.t4__kicker:empty, .t4__lede:empty { display: none; }
.t4 .t4__title { margin: 0 0 0.6rem; font-size: clamp(2.8rem, 1.8rem + 3.4vw, 4.6rem); line-height: 1; }
.t4__lede { max-width: 36rem; color: rgba(251, 238, 221, 0.85); font: italic 1.25rem/1.5 var(--display); }
.t4 .store-filters { margin: 1.8rem 0 0; padding-top: 1.2rem; border-top: 1px solid rgba(227, 179, 74, 0.25); }
.t4 .store-filter__label { color: var(--gold); }
.t4 .store-groups__btn { color: rgba(251, 238, 221, 0.62); }
.t4 .store-groups__btn:hover, .t4 .store-groups__btn[aria-pressed="true"] { color: #fbeedd; }
.t4 .store-groups__btn[aria-pressed="true"] { border-bottom-color: var(--gold); }
[data-theme="dark"] .t4 .t4__title { color: var(--gold-light); }
""")

# ---------------------------------------------------------------- 5
option("5-lead-tile", "Lead tile",
       "The tile stays first in the grid, but solid: brown with cream type in light, gold-edged glass in dark. No count; the subject groups sit at its foot, so the title and the filter are one object.",
       f"""{BACK}
      {FILTERS}
      {GRID}""",
       """
.store-name { background: linear-gradient(160deg, #5a3a1e, var(--brown-ink)); box-shadow: 0 24px 40px -26px rgba(40, 18, 4, 0.8); color: #fbeedd; }
.store-name__heading { color: #fbeedd; }
.store-name__kicker { color: var(--gold); }
.store-name__lede { color: rgba(251, 238, 221, 0.78); }
.store-name__count { display: none; }
.store-name .store-filters { margin: 0; }
.store-name .store-filter__label { color: var(--gold); }
.store-name .store-groups { gap: 0.2rem 1.2rem; }
.store-name .store-groups__btn { color: rgba(251, 238, 221, 0.6); font-size: 1.2rem; }
.store-name .store-groups__btn:hover, .store-name .store-groups__btn[aria-pressed="true"] { color: #fbeedd; }
.store-name .store-groups__btn[aria-pressed="true"] { border-bottom-color: var(--gold); }
[data-theme="dark"] .store-name { background: linear-gradient(160deg, rgba(255, 236, 210, 0.08), rgba(255, 236, 210, 0.02)); box-shadow: inset 0 0 0 1px var(--g-line); }
[data-theme="dark"] .store-name__heading { color: var(--gold-pale); }
""",
       js="""
// The filters move into the tile's foot each time the grid is drawn.
var grid = document.querySelector('[data-slot="bookstore"]'), f = document.querySelector('[data-slot="bookstore-filters"]');
function put() { var foot = grid.querySelector(".store-name__foot"); if (foot && f.parentNode !== foot) foot.appendChild(f); }
new MutationObserver(put).observe(grid, { childList: true }); put();
""", hide_tile=False)

# ---------------------------------------------------------------- 6
s = slots("t6__kicker", "t6__title", "t6__lede")
option("6-covers", "With covers",
       "The title and lede on the left; on the right a fan of the featured books' own photographs, overlapping and turned, which spread apart when pointed at. The groups run under both.",
       f"""{BACK}
      <div class="t6"><div class="t6__text">{s['k']}{s['h']}{s['l']}</div><div class="t6__fan" aria-hidden="true"></div></div>
      {FILTERS}
      {GRID}""",
       """
.t6 { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); align-items: center; gap: 2rem; margin: 0 0 1.4rem; }
.t6__kicker { color: var(--g-accent); font: 600 0.62rem var(--sans); letter-spacing: 0.26em; text-transform: uppercase; }
.t6__kicker:empty, .t6__lede:empty { display: none; }
.t6__title { color: var(--g-text); font: 500 clamp(3.2rem, 2rem + 4.4vw, 6rem) var(--display); letter-spacing: -0.02em; line-height: 0.9; }
.t6__lede { max-width: 28rem; margin-top: 1rem; color: var(--g-muted); font: italic 1.25rem/1.5 var(--display); }
.t6__fan { position: relative; height: 300px; }
.t6__fan img { position: absolute; left: 50%; bottom: 0; width: 150px; aspect-ratio: 3 / 4; object-fit: cover; border-radius: 3px 6px 6px 3px; box-shadow: -10px 22px 36px -14px rgba(40, 18, 4, 0.6); transform-origin: 50% 120%; transform: translateX(calc(-50% + var(--x) * var(--spread, 1))) rotate(var(--r)); transition: transform 0.5s var(--ease-out); }
.t6:hover .t6__fan img { transform: translateX(calc(-50% + var(--x) * var(--spread, 1) * 1.6)) rotate(calc(var(--r) * 1.4)) translateY(-6px); }
@media (max-width: 760px) { .t6 { grid-template-columns: minmax(0, 1fr); } .t6__fan { height: 220px; } .t6__fan { --spread: 0.5; } .t6__fan img { width: 110px; } }
""",
       js="""
// The fan: the first five featured books with a photograph, their tight crops.
Promise.all([
  fetch("content/bookstore.json", { cache: "no-cache" }).then(function (r) { return r.json(); }),
  fetch("assets/img/books/tight/covers.json", { cache: "no-cache" }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; })
]).then(function (res) {
  var books = res[0].books || [], covers = res[1];
  var pick = books.filter(function (b) { return b.featured && b.cover; }).concat(books.filter(function (b) { return !b.featured && b.cover; })).slice(0, 5);
  var fan = document.querySelector(".t6__fan"), n = pick.length;
  pick.forEach(function (b, i) {
    var img = new Image();
    img.src = (covers[b.cover] && covers[b.cover].tight) || b.cover;
    img.alt = "";
    var k = i - (n - 1) / 2;
    img.style.setProperty("--r", (k * 9) + "deg");
    img.style.setProperty("--x", (k * 58) + "px");
    img.style.zIndex = String(10 - Math.abs(Math.round(k)));
    fan.appendChild(img);
  });
});
""")

# ---------------------------------------------------------------- 7
s = slots("t7__kicker", "t7__title", "t7__lede")
option("7-one-line", "One line",
       "The smallest: “Bookstore” in Gilda capitals and the subject groups on one line, parted by a gold hairline, the lede under them in italic. The grid starts almost at once.",
       f"""{BACK}
      <div class="t7"><div class="t7__row">{s['h']}{FILTERS}</div>{s['k']}{s['l']}</div>
      {GRID}""",
       """
.t7 { margin: 0 0 1.6rem; }
.t7__row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.8rem 2rem; }
.t7__title { padding-right: 2rem; border-right: 1px solid var(--g-line); background: var(--g-title); -webkit-background-clip: text; background-clip: text; color: transparent; font: 400 clamp(1.8rem, 1.4rem + 1.4vw, 2.6rem) var(--title); letter-spacing: 0.14em; text-transform: uppercase; }
.t7 .store-filters { margin: 0; }
.t7 .store-filter__label { display: none; }
.t7__kicker, .t7__lede { margin-top: 0.6rem; color: var(--g-muted); font: italic 1.15rem var(--display); }
.t7__kicker:empty, .t7__lede:empty { display: none; }
@media (max-width: 640px) { .t7__title { padding-right: 0; border-right: 0; } }
""")


PAGE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="../../">
  <title>Bookstore title · {num}. {name}</title>
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
  {head}
<!-- Bookstore title, option {num}: {name}. {blurb} Generated by design/canvas-store-title/generate.py. -->
<style>
.store-page {{ padding-top: 130px; }}
.store-page .back {{ margin-bottom: 1.6rem; }}
{hide}
.mock-tag {{ position: fixed; z-index: 50; left: 16px; bottom: 16px; display: flex; align-items: center; gap: 0.6rem; padding: 0.5rem 0.9rem; border-radius: 999px; background: rgba(36, 18, 5, 0.88); color: #f7e0a4; font: 500 0.72rem var(--sans); letter-spacing: 0.04em; box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5); }}
.mock-tag a {{ color: inherit; opacity: 0.75; text-decoration: none; }}
.mock-tag a:hover {{ opacity: 1; }}
{css}</style>
</head>
<body id="top" class="{body}">

{header}
<main id="main">
  {pre}
  <section class="{section}" aria-labelledby="bookstore-heading">
    <div class="wrap">
      {main}
    </div>
  </section>
</main>

{footer}
{scripts}<script>
{js}</script>
<p class="mock-tag"><a href="design/canvas-store-title/{prev}">&larr;</a> Option {num} &middot; {name} <a href="design/canvas-store-title/index.html">All</a> <a href="design/canvas-store-title/{next}">&rarr;</a></p>
</body>
</html>
"""

INDEX = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="../../">
  <title>Bookstore title · seven options</title>
  <script>
    (function () {{
      var t = null;
      try {{ t = localStorage.getItem("alimiyyah.theme"); }} catch (e) {{}}
      if (t !== "light" && t !== "dark") t = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", t);
    }})();
  </script>
  {head}
<style>
.ix {{ padding: 90px 0 120px; }}
.ix h1 {{ color: var(--g-text); font: 500 clamp(2.4rem, 5vw, 3.6rem) var(--display); }}
.ix > .wrap > p {{ max-width: 44rem; margin: 0.8rem 0 2.4rem; color: var(--g-muted); font: italic 1.25rem var(--display); }}
.ix ol {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 14px; padding: 0; list-style: none; }}
.ix li a {{ display: block; height: 100%; padding: 1.5rem; border-radius: 24px; box-shadow: inset 0 0 0 1px var(--g-line); color: var(--g-text); text-decoration: none; transition: box-shadow 0.2s; }}
.ix li a:hover {{ box-shadow: inset 0 0 0 1px var(--g-text); }}
.ix li b {{ display: block; margin-bottom: 0.5rem; font: 500 1.6rem var(--display); }}
.ix li b span {{ color: var(--g-accent); font: 400 1.1rem var(--title); margin-right: 0.5rem; }}
.ix li p {{ color: var(--g-muted); font-size: 0.86rem; line-height: 1.6; }}
.ix .now {{ margin-top: 2rem; font-size: 0.85rem; color: var(--g-muted); }}
.ix .now a {{ color: var(--g-text); }}
</style>
</head>
<body class="on-ground">
<main class="ix"><div class="wrap">
  <h1>Bookstore title</h1>
  <p>Seven ways to head the bookstore page, none with the count of books. Each is the real page with the real books and filters; only the title differs.</p>
  <ol>
{items}
  </ol>
  <p class="now">For comparison: <a href="bookstore.html">the bookstore as it is now</a>.</p>
</div></main>
</body>
</html>
"""

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]


def main():
    n = len(OPTIONS)
    items = []
    for k, o in enumerate(OPTIONS):
        out = HERE / (o["slug"] + ".html")
        out.write_text(PAGE.format(
            num=k + 1, name=o["name"], blurb=o["blurb"], head=HEAD_LINKS.strip(), css=o["css"],
            hide=".store-name { display: none !important; }" if o["hide_tile"] else "",
            body=o["body"], header=HEADER.strip(), pre=o.get("pre", ""),
            section=o.get("section", "section store-page"), main=o["main"],
            footer=FOOTER.strip(), scripts=SCRIPTS, js=o["js"],
            prev=OPTIONS[(k - 1) % n]["slug"] + ".html", next=OPTIONS[(k + 1) % n]["slug"] + ".html",
        ), encoding="utf-8")
        items.append('    <li><a href="design/canvas-store-title/%s.html"><b><span>%s</span>%s</b><p>%s</p></a></li>'
                     % (o["slug"], ROMAN[k], o["name"], o["blurb"]))
        print("wrote", out.name)
    (HERE / "index.html").write_text(INDEX.format(head=HEAD_LINKS.strip(), items="\n".join(items)), encoding="utf-8")
    print("wrote index.html")


if __name__ == "__main__":
    main()

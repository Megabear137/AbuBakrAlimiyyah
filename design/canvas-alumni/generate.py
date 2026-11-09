#!/usr/bin/env python3
"""The alumni page: every testimony on one page, and the button that opens it.

`0-button.html` is the home page's Alumni section - the site's own carousel of
mihrab niches - with three ways to put a "See all testimonies" button on it,
one under another (A, B, C). Options 1-4 are the page the button opens.

Each option loads the site's styles.css and the article canvas's mockup.css
(the switcher, the header's round buttons on the ground, .back), and borrows
that canvas's header, menu and footer, so only the page itself differs.

Content is content/testimonies.json's as it stands: two real testimonies and
two TODO ones. So that the layouts can be judged at the length the page is
for, five more TODO testimonies follow them, marked as such; nothing is made up.

Edit this file, not the output:  python3 generate.py
"""
import html
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

_spec = importlib.util.spec_from_file_location("article", HERE.parent / "canvas-article" / "generate.py")
art = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(art)

ARROW = art.ARROW
QUOTE = art.QUOTE
PAGE = ' aria-current="page"'

DATA = json.loads((ROOT / "content" / "testimonies.json").read_text())
REAL = DATA["testimonies"]
EXTRA = [{"quote": "TODO: Another alumni testimony, standing in for one of the many the page will hold.",
          "name": "TODO: Name", "graduated": "TODO: Year"} for _ in range(5)]
ALL = REAL + EXTRA
COUNT = len(ALL)

BACK = f'<a class="back" href="../../index.html#alumni">{ARROW} Alumni</a>'
MARK = QUOTE.replace("<svg ", '<svg class="testimony__mark" ', 1)

OPTIONS = [
    ("0-button.html", "The button"),
    ("1-arcade.html", "Arcade"),
    ("2-by-year.html", "Banner, by class"),
    ("3-reading.html", "Reading column"),
    ("4-lead-cards.html", "Lead niche & cards"),
]


def e(s):
    return html.escape(s or "", quote=True)


def is_todo(s):
    return (s or "").startswith("TODO")


def cite(t):
    year = f"Class of {e(t['graduated'])}" if t.get("graduated") else ""
    return f"<b>{e(t['name'])}</b>{year}"


def niche(t, extra=""):
    """The home page's niche, exactly as main.js's renderTestimonies draws it."""
    return (f'<figure class="niche-slot{extra}"><div class="niche"><div class="niche__recess">{MARK}'
            f'<blockquote class="testimony__quote">{e(t["quote"])}</blockquote>'
            f'<figcaption class="testimony__cite">{cite(t)}</figcaption>'
            f'</div></div><div class="niche__sill"></div></figure>')


def switcher(current):
    links = "".join(
        f'<a href="{f}" title="{name}"{PAGE if f == current else ""}>{i}</a>'
        for i, (f, name) in enumerate(OPTIONS))
    return f"""
<nav class="m-switch" aria-label="Mockups">
  <span>Alumni</span>{links}<i></i>
  <button type="button" data-set-theme="light">Light</button>
  <button type="button" data-set-theme="dark">Dark</button>
</nav>"""


def head(title, eyebrow="", count=True):
    """A site section head: the ✦ eyebrow, the Gilda title, the italic lede."""
    lede = f'<p class="section__lede">{COUNT} testimonies from our graduates</p>' if count else ""
    return f"""
      <div class="section__head">
        <p class="section__eyebrow">{eyebrow}</p>
        <h1 class="section__heading">{title}</h1>
        {lede}
      </div>"""


SHARED_CSS = """
/* A niche outside the carousel: tall enough for the arch and a short quote. */
.niche-slot { min-height: 440px; }
.al-top { padding-top: 130px; }
.al-top .back { display: flex; justify-content: center; margin-bottom: 2rem; }
"""


def page(fname, name, blurb, css, main, body_class="on-ground", scripts=""):
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Alumni · {name}</title>
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
  <link rel="stylesheet" href="../../assets/css/styles.css?v=57">
  <link rel="stylesheet" href="../canvas-article/mockup.css">
<!-- Option: {name}. {blurb} -->
<style>
{SHARED_CSS.strip()}

{css.strip()}
</style>
</head>
<body id="top" class="{body_class}">
{art.HEADER}

<main id="main">
{main.rstrip()}
</main>
{art.FOOTER}
{switcher(fname)}
{art.SCRIPTS}
{scripts}
</body>
</html>
"""


# ----------------------------------------------------------------------------
# 0. The button: the home page's Alumni section, three times, with the button
#    in a different place each time. The carousel is the site's carousel.js
#    with main.js's niche, so it pages and drags as it does on the site.
#      A  under the page dots - a gold button, the section's last word
#      B  in the section head, under the title - the "All …" more-link the
#         Articles and Videos heads already have, as a small outline pill
#      C  a last niche at the end of the carousel, its recess an open arch
#         holding the count and the link
# ----------------------------------------------------------------------------
CSS_0 = """
.variant { position: relative; }
.variant__tag {
  display: table;
  margin: 0 auto 1.4rem;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  background: rgba(26, 13, 4, 0.88);
  color: #fbeedd;
  font: 600 0.66rem/1 var(--sans);
  letter-spacing: 0.12em;
}
.alumni-all { margin-top: 2.4rem; text-align: center; }
.alumni-all .btn svg { width: 16px; height: 16px; }

/* B: a small outline pill under the heading. */
.head-link {
  display: inline-flex; align-items: center; gap: 0.5rem;
  margin-top: 1.1rem; padding: 0.55rem 1.1rem;
  border: 1px solid var(--gilt-edge); border-radius: 999px;
  background: rgba(255, 251, 244, 0.7);
  color: var(--brown-ink); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.24em;
  text-decoration: none; text-transform: uppercase;
}
.head-link svg { width: 14px; height: 14px; }
.head-link:hover { background: var(--gold-light); color: var(--espresso); }
[data-theme="dark"] .head-link { border-color: rgba(227, 179, 74, 0.35); background: rgba(26, 13, 4, 0.3); color: var(--gold-pale); }

/* C: the last niche is an open arch - the moulding with no recess dark in it,
   only the gold edge, and the link at its heart. */
.niche-slot--all .niche__recess { justify-content: center; gap: 1rem; text-decoration: none; }
.niche-slot--all .niche__recess::before { opacity: 1; background: radial-gradient(80% 60% at 50% 60%, rgba(255, 206, 130, 0.28), transparent 75%); }
.all-niche__count { color: var(--gold-light); font-family: var(--title); font-size: 4rem; line-height: 1; }
.all-niche__label { color: var(--on-choc); font-family: var(--display); font-size: 1.5rem; font-style: italic; }
.niche-slot--all .btn { margin-top: 0.6rem; }
"""

BUTTON = f'<a class="btn btn--gold" href="1-arcade.html">See all testimonies {ARROW}</a>'

MAIN_0 = f"""
  <div class="al-top"></div>
  <section class="section variant" aria-labelledby="a-h">
    <div class="wrap">
      <p class="variant__tag">A · A gold button under the dots</p>
      <div class="section__head">
        <h2 class="section__heading" id="a-h">{e(DATA["heading"])}</h2>
      </div>
      <div class="niches" data-carousel></div>
      <p class="alumni-all">{BUTTON}</p>
    </div>
  </section>

  <hr class="section-rule">
  <section class="section variant" aria-labelledby="b-h">
    <div class="wrap">
      <p class="variant__tag">B · A small link in the head</p>
      <div class="section__head">
        <h2 class="section__heading" id="b-h">{e(DATA["heading"])}</h2>
        <a class="head-link" href="1-arcade.html">All {COUNT} testimonies {ARROW}</a>
      </div>
      <div class="niches" data-carousel></div>
    </div>
  </section>

  <hr class="section-rule">
  <section class="section variant" aria-labelledby="c-h">
    <div class="wrap">
      <p class="variant__tag">C · A last niche that opens the page</p>
      <div class="section__head">
        <h2 class="section__heading" id="c-h">{e(DATA["heading"])}</h2>
      </div>
      <div class="niches" data-carousel data-all-niche></div>
    </div>
  </section>
"""

SCRIPTS_0 = f"""
<script src="../../assets/js/carousel.js?v=5"></script>
<script>
  (function () {{
    var items = {json.dumps(REAL)};
    var MARK = {json.dumps(MARK)};
    var ARROW = {json.dumps(ARROW)};
    function esc(s) {{ var d = document.createElement("div"); d.textContent = s || ""; return d.innerHTML; }}
    function niche(t) {{
      var f = document.createElement("figure");
      f.className = "niche-slot";
      if (t.all) {{
        f.className += " niche-slot--all";
        f.innerHTML = '<div class="niche"><a class="niche__recess" href="1-arcade.html">' +
          '<span class="all-niche__count">{COUNT}</span><span class="all-niche__label">testimonies from our graduates</span>' +
          '<span class="btn btn--gold btn--sm">See them all ' + ARROW + '</span></a></div><div class="niche__sill"></div>';
        return f;
      }}
      f.innerHTML = '<div class="niche"><div class="niche__recess">' + MARK +
        '<blockquote class="testimony__quote">' + esc(t.quote) + '</blockquote>' +
        '<figcaption class="testimony__cite"><b>' + esc(t.name) + '</b>' +
        (t.graduated ? "Class of " + esc(t.graduated) : "") + '</figcaption></div></div><div class="niche__sill"></div>';
      return f;
    }}
    document.querySelectorAll("[data-carousel]").forEach(function (mount) {{
      createCarousel({{
        mount: mount,
        items: mount.hasAttribute("data-all-niche") ? items.concat([{{ all: true }}]) : items,
        label: "Alumni testimonies",
        perView: function () {{ return window.innerWidth < 700 ? 1 : window.innerWidth < 1040 ? 2 : 3; }},
        render: niche
      }});
    }});
  }})();
</script>"""

# ----------------------------------------------------------------------------
# 1. Arcade: the carousel unrolled. The section head, then every niche three
#    across; each row stands on one continuous sill, so a row reads as an
#    arcade in the wall rather than separate frames.
# ----------------------------------------------------------------------------
CSS_1 = """
.arcade { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 3.2rem 1.4rem; }
.arcade .niche-slot { padding-inline: 0; }
.arcade .niche__sill { margin-inline: -0.7rem; border-radius: 0; }
.arcade .niche-slot:nth-child(3n + 1) .niche__sill { border-radius: 2px 0 0 2px; margin-left: -8px; }
.arcade .niche-slot:nth-child(3n) .niche__sill,
.arcade .niche-slot:last-child .niche__sill { border-radius: 0 2px 2px 0; margin-right: -8px; }
@media (max-width: 1040px) {
  .arcade { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .arcade .niche__sill { margin-inline: -8px !important; border-radius: 2px !important; }
}
@media (max-width: 700px) { .arcade { grid-template-columns: minmax(0, 1fr); } .arcade .niche-slot { min-height: 400px; } }
.al-foot { margin-top: 3.5rem; text-align: center; }
"""

MAIN_1 = f"""
  <section class="section al-top" aria-label="Alumni testimonies">
    <div class="wrap">
      {BACK}
      {head(e(DATA["heading"]))}
      <div class="arcade">{"".join(niche(t) for t in ALL)}</div>
      <p class="al-foot">{BACK}</p>
    </div>
  </section>
"""

# ----------------------------------------------------------------------------
# 2. Banner, by class: the article page's banner, carrying the title and the
#    count, then the niches grouped under their class year, newest first, each
#    group under a small centred year line. Years not yet given come last.
# ----------------------------------------------------------------------------
CSS_2 = """
.a-hero .hero__title { max-width: 16ch; }
.a-hero .hero__sub { max-width: 30rem; margin: 0 auto; color: rgba(255, 246, 234, 0.88); font-family: var(--display); font-size: 1.4rem; font-style: italic; }
.class-group + .class-group { margin-top: clamp(3.5rem, 7vw, 5.5rem); }
.class-year {
  display: flex; align-items: center; gap: 1.2rem;
  margin-bottom: 2.2rem;
  color: var(--g-accent); font-size: 0.7rem; font-weight: 600; letter-spacing: 0.34em; text-transform: uppercase;
}
.class-year::before, .class-year::after { content: ""; flex: 1; height: 1px; background: var(--g-line); }
.class-year b { font-family: var(--title); font-size: 1.9rem; font-weight: 400; letter-spacing: 0.1em; color: var(--brown-ink); }
[data-theme="dark"] .class-year b { color: var(--gold-light); }
.class-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 340px)); justify-content: center; gap: 2.4rem 1.4rem; }
.al-foot { margin-top: 3.5rem; text-align: center; }
"""


def groups():
    by = {}
    for t in ALL:
        by.setdefault(t.get("graduated") or "", []).append(t)
    years = sorted((y for y in by if not is_todo(y) and y), reverse=True)
    years += [y for y in by if y not in years]
    out = []
    for y in years:
        label = f"Class of <b>{e(y)}</b>" if not is_todo(y) else "<b>TODO</b> Year to come"
        out.append(f'<div class="class-group"><h2 class="class-year"><span>{label}</span></h2>'
                   f'<div class="class-row">{"".join(niche(t) for t in by[y])}</div></div>')
    return "".join(out)


MAIN_2 = f"""
  <section class="hero a-hero" aria-labelledby="al-title">
    <div class="hero__img" aria-hidden="true"></div>
    <div class="wrap hero__body">
      <p class="in">{BACK}</p>
      <h1 class="hero__title in" id="al-title">{e(DATA["heading"])}</h1>
      <p class="hero__sub in">{COUNT} graduates, in their own words</p>
    </div>
  </section>

  <section class="section" aria-label="By class">
    <div class="wrap">
      {groups()}
      <p class="al-foot">{BACK}</p>
    </div>
  </section>
"""

# ----------------------------------------------------------------------------
# 3. Reading column: no frames. The testimonies as the article page sets a
#    quotation - large italic lines between hairlines parted by the quote
#    mark - one after another in the 680px column. Suits long testimonies,
#    which a niche has to cut short.
# ----------------------------------------------------------------------------
CSS_3 = """
.read { max-width: calc(680px + 2 * var(--gutter)); }
.quotes { list-style: none; margin: 0; padding: 0; }
.quotes li {
  position: relative;
  padding: 2.6rem 0 2.2rem;
  background:
    linear-gradient(var(--g-line), var(--g-line)) left top / calc(50% - 30px) 1px no-repeat,
    linear-gradient(var(--g-line), var(--g-line)) right top / calc(50% - 30px) 1px no-repeat;
  text-align: center;
}
.quotes li:last-child { border-bottom: 1px solid var(--g-line); }
.quotes svg { position: absolute; top: -12px; left: 50%; width: 30px; height: 24px; transform: translateX(-50%); color: var(--g-mark); }
.quotes blockquote { margin: 0; color: var(--g-text); font-family: var(--display); font-size: clamp(1.45rem, 1.2rem + 0.8vw, 1.85rem); font-style: italic; line-height: 1.35; }
.quotes figcaption { margin-top: 1.2rem; color: var(--g-accent); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.quotes figcaption b { display: block; margin-bottom: 0.35rem; color: var(--g-text); font-family: var(--display); font-size: 1.3rem; font-weight: 600; letter-spacing: 0; text-transform: none; }
.quotes li.todo blockquote { opacity: 0.6; }
.al-foot { margin-top: 3rem; text-align: center; }
"""


def quote_item(t):
    todo = ' class="todo"' if is_todo(t["quote"]) else ""
    return (f'<li{todo}>{QUOTE}<figure>'
            f'<blockquote>{e(t["quote"])}</blockquote>'
            f'<figcaption>{cite(t)}</figcaption></figure></li>')


MAIN_3 = f"""
  <section class="section al-top" aria-label="Alumni testimonies">
    <div class="wrap">
      {BACK}
      {head(e(DATA["heading"]))}
    </div>
    <div class="wrap read">
      <ul class="quotes">{"".join(quote_item(t) for t in ALL)}</ul>
      <p class="al-foot">{BACK}</p>
    </div>
  </section>
"""

# ----------------------------------------------------------------------------
# 4. Lead niche & cards: the first testimony in one tall niche, held still on
#    the left; the rest beside it as the teachers' cream cards in their double
#    gold frame (board tiles in dark), flowing in two columns so quotes of any
#    length sit without gaps. On phones the niche heads the list.
# ----------------------------------------------------------------------------
CSS_4 = """
.lead-split { display: grid; grid-template-columns: 340px minmax(0, 1fr); gap: clamp(2rem, 4vw, 3.5rem); align-items: start; }
.lead-split > .niche-slot { position: sticky; top: 2rem; min-height: 560px; }
.lead-split > .niche-slot .testimony__quote { font-size: 1.75rem; }
.cards { columns: 2; column-gap: 1.2rem; }
.q-card {
  break-inside: avoid;
  margin: 0 0 1.2rem;
  padding: 1.8rem 1.8rem 1.5rem;
  border-radius: 18px;
  background: linear-gradient(160deg, #fffaf0, #f3e2c3);
  box-shadow:
    inset 0 0 0 1px var(--gold),
    inset 0 0 0 6px #fbf3e2,
    inset 0 0 0 7px rgba(201, 164, 87, 0.8),
    0 24px 40px -30px rgba(40, 18, 4, 0.7);
  color: var(--brown-ink);
}
.q-card svg { width: 26px; height: 21px; color: var(--g-mark); }
.q-card blockquote { margin: 0.8rem 0 1.2rem; font-family: var(--display); font-size: 1.35rem; font-style: italic; line-height: 1.35; }
.q-card figcaption { padding-top: 0.9rem; border-top: 1px solid rgba(154, 101, 8, 0.3); color: #7d5006; font-size: 0.85rem; }
.q-card figcaption b { display: block; color: var(--brown-ink); font-family: var(--display); font-size: 1.25rem; font-weight: 600; }
.q-card--todo { background: transparent; box-shadow: inset 0 0 0 1px var(--gilt-edge); }
.q-card--todo blockquote { opacity: 0.65; }
[data-theme="dark"] .q-card {
  border: 1px solid var(--g-line);
  background: linear-gradient(180deg, transparent 55%, rgba(20, 9, 2, 0.45)), linear-gradient(155deg, var(--board), var(--board-deep));
  box-shadow: 0 24px 40px -30px rgba(0, 0, 0, 0.9);
  color: var(--g-text);
}
[data-theme="dark"] .q-card--todo { background: transparent; }
[data-theme="dark"] .q-card figcaption { border-top-color: var(--g-line); color: var(--g-muted); }
[data-theme="dark"] .q-card figcaption b { color: var(--gold-light); }
@media (max-width: 1040px) { .cards { columns: 1; } }
@media (max-width: 760px) {
  .lead-split { grid-template-columns: minmax(0, 1fr); }
  .lead-split > .niche-slot { position: static; width: min(100%, 340px); margin: 0 auto; min-height: 480px; }
}
.al-foot { margin-top: 3rem; text-align: center; }
"""


def q_card(t):
    todo = " q-card--todo" if is_todo(t["quote"]) else ""
    return (f'<figure class="q-card{todo}">{QUOTE}<blockquote>{e(t["quote"])}</blockquote>'
            f'<figcaption>{cite(t)}</figcaption></figure>')


MAIN_4 = f"""
  <section class="section al-top" aria-label="Alumni testimonies">
    <div class="wrap">
      {BACK}
      {head(e(DATA["heading"]))}
      <div class="lead-split">
        {niche(ALL[0])}
        <div class="cards">{"".join(q_card(t) for t in ALL[1:])}</div>
      </div>
      <p class="al-foot">{BACK}</p>
    </div>
  </section>
"""

BUILDS = [
    (CSS_0, MAIN_0, "on-ground", "The home page's Alumni carousel with three placements of a See-all button.", SCRIPTS_0),
    (CSS_1, MAIN_1, "on-ground", "The carousel unrolled: every niche three across, each row on one continuous sill.", ""),
    (CSS_2, MAIN_2, "", "The article page's banner with the title and count; the niches grouped by class year.", ""),
    (CSS_3, MAIN_3, "on-ground", "No frames: each testimony set as the article page's quotation, in the 680px column.", ""),
    (CSS_4, MAIN_4, "on-ground", "The first testimony in a tall sticky niche; the rest as cream cards in two columns.", ""),
]

if __name__ == "__main__":
    for (fname, name), (css, main, cls, blurb, scripts) in zip(OPTIONS, BUILDS):
        (HERE / fname).write_text(page(fname, name, blurb, css, main, cls, scripts))
        print("wrote", fname)

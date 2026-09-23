#!/usr/bin/env python3
"""The article page, round 2: option 1 (Banner) with its empty sides filled.

Round 1 (generate.py) chose option 1: the banner over a single 680px column.
On a wide screen that column leaves a broad empty margin either side. Each
option here keeps option 1's banner, text and quotation and fills the margins
a different way, using only what the article and the site already have.

Edit this file, not the output:  python3 generate_sides.py
"""
from generate import (HERE, A, BACK, BODY, CSS_1, MAIN_1, QUOTE,
                      page, switcher)

OPTIONS = [
    ("sides-1-marginalia.html", "Marginalia"),
    ("sides-2-rails.html", "Two rails"),
    ("sides-3-contents.html", "Contents"),
    ("sides-4-bay.html", "Bay"),
    ("sides-5-breakouts.html", "Breakouts"),
]

HERO = MAIN_1.split("<article")[0].rstrip()          # option 1's banner, as built
LEDE = f'<p class="lede">{A["excerpt"]}</p>'

# The body with ids on its headings, so a contents list can point at them.
HEADS = ["s-1", "s-2"]
BODY_IDS = BODY
for h in HEADS:
    BODY_IDS = BODY_IDS.replace("<h2>", f'<h2 id="{h}">', 1)
BODY_Q = BODY_IDS.replace("<blockquote>", "<blockquote>" + QUOTE)

META_ROWS = f"""
<dl class="facts">
  <div><dt>Subject</dt><dd>{A["subject"]}</dd></div>
  <div><dt>Author</dt><dd>{A["author"]}</dd></div>
  <div><dt>Reading</dt><dd>{A["read"]}</dd></div>
</dl>"""

# A few other articles, as the home page's carousel holds them.
def mini_cards(n=3):
    return "".join(
        f'<a class="slider__card board{" board--rust" if i % 2 else ""}" href="#top">'
        f'<b>{i + 2:02d}</b><em>TODO: Subject</em><span>TODO: Article title</span></a>'
        for i in range(n))

# Shared by every option: the facts list and a rail's small heading.
BASE = CSS_1 + """
.facts { margin: 0; display: grid; gap: 1rem; }
.facts dt { color: var(--g-accent); font-size: 0.6rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.facts dd { margin: 0.2rem 0 0; color: var(--g-text); font-family: var(--display); font-size: 1.2rem; font-style: italic; line-height: 1.25; }
.rail__head {
  margin-bottom: 1rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid var(--g-line);
  color: var(--g-text);
  font-family: var(--title);
  font-size: 0.95rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}
"""

# ----------------------------------------------------------------------------
# 1. Marginalia: as a kitab's hawashi, the headings, the facts and the
#    quotation hang out in the margins beside the text they belong to.
#    Floats with a negative margin as wide as themselves, so the column's
#    text runs on untouched. Below 1300px they come back into the column.
# ----------------------------------------------------------------------------
CSS_S1 = BASE + """
.read { max-width: calc(680px + 2 * var(--gutter)); }
.note { float: left; width: 200px; margin: 0.3rem 0 0 -250px; text-align: right; }
.note .facts dd { font-size: 1.1rem; }
.note::after { content: ""; display: block; width: 36px; height: 2px; margin: 1.2rem 0 0 auto; background: var(--g-mark); }
@media (min-width: 1300px) {
  .prose h2 {
    float: left;
    clear: left;
    width: 200px;
    margin: 0.35rem 0 0 -250px;
    padding-top: 0.9rem;
    border-top: 1px solid var(--g-line);
    font-size: 1.45rem;
    text-align: right;
  }
  .prose h2 + p { margin-top: 2.2em; }
  .prose blockquote {
    float: right;
    clear: right;
    width: 260px;
    margin: 0.3rem -310px 1rem 0;
    padding: 1.2rem 0 1rem;
    text-align: left;
  }
  .prose blockquote svg { left: 0; transform: none; padding: 0 8px 0 0; }
  .prose blockquote p { font-size: 1.45rem; }
}
@media (max-width: 1299px) {
  .note { float: none; width: auto; margin: 0 0 2rem; text-align: center; }
  .note .facts { grid-template-columns: repeat(3, auto); justify-content: center; gap: 1rem 2rem; }
  .note::after { margin-inline: auto; }
}
@media (max-width: 560px) { .note .facts { grid-template-columns: minmax(0, 1fr); } }
"""

MAIN_S1 = f"""{HERO}

  <article class="wrap read">
    {LEDE}
    <div class="prose">
<aside class="note" aria-label="About this article">{META_ROWS}</aside>
{BODY_Q}
    </div>
  </article>
"""

# ----------------------------------------------------------------------------
# 2. Two rails: the facts and the way back on the left, the other articles
#    on the right as the home page's board cards. Both stay in view as the
#    text scrolls.
# ----------------------------------------------------------------------------
CSS_S2 = BASE + """
.read3 {
  display: grid;
  grid-template-columns: 220px minmax(0, 680px) 240px;
  justify-content: center;
  gap: clamp(2rem, 4vw, 4.5rem);
  align-items: start;
  padding-top: clamp(1rem, 3vw, 2rem);
}
.read3 > aside { position: sticky; top: 2rem; }
.rail--facts .back { display: inline-flex; margin-top: 1.6rem; }
.rail--facts .facts { padding-top: 1.2rem; border-top: 1px solid var(--g-line); }
.rail--more { display: grid; gap: 0.8rem; }
.rail--more .rail__head { margin-bottom: 0.2rem; }
.rail--more .slider__card { min-height: 116px; padding-top: 2.6rem; text-decoration: none; }
.rail--more .slider__card span { font-size: 1.05rem; }
@media (max-width: 1240px) {
  .read3 { grid-template-columns: minmax(0, 680px) 220px; }
  .rail--facts { display: none; }
}
@media (max-width: 900px) {
  .read3 { grid-template-columns: minmax(0, 1fr); }
  .rail--more { display: none; }                         /* the Articles row below the text does it here */
}
"""

MAIN_S2 = f"""{HERO}

  <div class="wrap read3">
    <aside class="rail rail--facts" aria-label="About this article">
      <p class="rail__head">This article</p>
      {META_ROWS}
      {BACK}
    </aside>
    <article>
      {LEDE}
      <div class="prose">
{BODY_Q}
      </div>
    </article>
    <aside class="rail rail--more" aria-label="Other articles">
      <p class="rail__head">Articles</p>
      {mini_cards(3)}
    </aside>
  </div>
"""

# ----------------------------------------------------------------------------
# 3. Contents: the article's own headings down the left, the one being read
#    marked with the carousel's active dash; on the right, the facts on Our
#    Program's cream panel. Only useful where an article has headings.
# ----------------------------------------------------------------------------
CSS_S3 = BASE + """
.read3 {
  display: grid;
  grid-template-columns: 220px minmax(0, 680px) 220px;
  justify-content: center;
  gap: clamp(2rem, 4vw, 4.5rem);
  align-items: start;
  padding-top: clamp(1rem, 3vw, 2rem);
}
.read3 > aside { position: sticky; top: 2rem; }
.toc { margin: 0; padding: 0; list-style: none; border-left: 1px solid var(--g-line); }
.toc a {
  position: relative;
  display: block;
  padding: 0.55rem 0 0.55rem 1.1rem;
  color: var(--g-muted);
  font-family: var(--display);
  font-size: 1.1rem;
  line-height: 1.25;
  text-decoration: none;
  transition: color 0.2s;
}
.toc a::before {
  content: "";
  position: absolute;
  left: -1px;
  top: 0.5rem;
  bottom: 0.5rem;
  width: 3px;
  border-radius: 2px;
  background: var(--g-mark);
  transform: scaleY(0);
  transition: transform 0.3s var(--ease-out);
}
.toc a:hover { color: var(--g-text); }
.toc a[aria-current="true"] { color: var(--g-text); font-weight: 600; }
.toc a[aria-current="true"]::before { transform: none; }
.card {
  position: relative;
  padding: 1.5rem 1.4rem;
  border-radius: 18px;
  border: 1px solid var(--gilt-edge);
  background: rgba(255, 251, 244, 0.96);
  box-shadow: 0 24px 44px -28px rgba(70, 34, 6, 0.6);
}
.card::before { content: ""; position: absolute; top: -1px; left: 12%; right: 12%; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }
.card .facts dt { color: var(--gold-ink); }
.card .facts dd { color: var(--brown-ink); }
.card .back { margin-top: 1.4rem; padding-top: 1rem; border-top: 1px solid var(--g-line); width: 100%; color: var(--gold-ink); }
[data-theme="dark"] .card { border-color: var(--g-line); background: var(--g-card); box-shadow: none; }
[data-theme="dark"] .card .facts dt,
[data-theme="dark"] .card .back { color: var(--gold); }
[data-theme="dark"] .card .facts dd { color: var(--g-text); }
@media (max-width: 1240px) {
  .read3 { grid-template-columns: 200px minmax(0, 680px); }
  .rail--facts { display: none; }
}
@media (max-width: 900px) {
  .read3 { grid-template-columns: minmax(0, 1fr); }
  .read3 > aside { position: static; }
}
"""

TOC = "".join(f'<li><a href="#{h}">TODO: Section heading</a></li>' for h in HEADS)
MAIN_S3 = f"""{HERO}

  <div class="wrap read3">
    <aside class="rail rail--toc" aria-label="In this article">
      <p class="rail__head">In this article</p>
      <ol class="toc">{TOC}</ol>
    </aside>
    <article>
      {LEDE}
      <div class="prose">
{BODY_Q}
      </div>
    </article>
    <aside class="rail rail--facts" aria-label="About this article">
      <div class="card">{META_ROWS}{BACK}</div>
    </aside>
  </div>
  <script>
    // Mark the heading being read: the last one above the top third of the screen.
    (function () {{
      var links = [].slice.call(document.querySelectorAll(".toc a"));
      var heads = links.map(function (a) {{ return document.querySelector(a.getAttribute("href")); }});
      function mark() {{
        var at = -1;
        heads.forEach(function (h, i) {{ if (h.getBoundingClientRect().top < innerHeight / 3) at = i; }});
        links.forEach(function (a, i) {{ a.setAttribute("aria-current", String(i === Math.max(at, 0))); }});
      }}
      addEventListener("scroll", mark, {{ passive: true }});
      mark();
    }})();
  </script>
"""

# ----------------------------------------------------------------------------
# 4. Bay: the text stands in one of the bookshelf's bays - the wooden frame
#    with the gold line along its top - on a cream leaf, so the wood takes up
#    the margin instead of the bare ground. Glass in dark, as the bays are.
# ----------------------------------------------------------------------------
CSS_S4 = BASE + """
.frame {
  position: relative;
  max-width: 1000px;
  margin: 0 auto;
  padding: clamp(10px, 4vw, 56px);
  border-radius: 26px;
  border: 1px solid rgba(70, 40, 20, 0.5);
  background: var(--grain), linear-gradient(180deg, var(--wood-hi), var(--wood) 30%, var(--wood-lo));
  background-size: var(--grain-size), 100% 100%;
  box-shadow: inset 0 1px 0 rgba(255, 228, 184, 0.3), 0 40px 60px -36px rgba(40, 18, 4, 0.8);
}
.frame::before { content: ""; position: absolute; top: -1px; left: 12%; right: 12%; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }
.frame .leaf {
  padding: clamp(2rem, 5vw, 4rem) clamp(1.3rem, 6vw, 5rem);
  border-radius: 14px;
  background: rgba(255, 251, 244, 0.98);
  box-shadow: inset 0 2px 10px rgba(70, 34, 6, 0.25), 0 0 0 1px rgba(40, 20, 6, 0.4);
  color: var(--brown-ink);
}
.frame .lede,
.frame .prose,
.frame .prose h2 { color: var(--brown-ink); }
.frame .prose blockquote svg { background: #fffbf4; }
[data-theme="dark"] .frame {
  border-color: var(--g-line);
  background: linear-gradient(160deg, rgba(255, 236, 210, 0.06), rgba(255, 236, 210, 0.015));
  box-shadow: 0 30px 60px -30px rgba(0, 0, 0, 0.8);
}
[data-theme="dark"] .frame .leaf { background: rgba(10, 5, 1, 0.55); box-shadow: inset 0 1px 0 rgba(227, 179, 74, 0.12), inset 0 12px 30px rgba(0, 0, 0, 0.5); }
[data-theme="dark"] .frame .lede,
[data-theme="dark"] .frame .prose { color: var(--g-text); }
[data-theme="dark"] .frame .prose h2 { color: var(--gold-light); }
[data-theme="dark"] .frame .prose blockquote svg { background: #150a03; }
.frame .lede::after { margin-bottom: 2rem; }
"""

MAIN_S4 = f"""{HERO}

  <div class="wrap">
    <article class="frame">
      <div class="leaf">
        {LEDE}
        <div class="prose">
{BODY_Q}
        </div>
      </div>
    </article>
  </div>
"""

# ----------------------------------------------------------------------------
# 5. Breakouts: the column stays narrow, but the parts that aren't running
#    text break out to the page's full width - the lede as large as the home
#    page's introduction, each heading across a gold rule, the quotation on a
#    wide board panel - so the width is used at intervals down the page.
# ----------------------------------------------------------------------------
CSS_S5 = BASE + """
.read { max-width: none; }
.read > .lede,
.prose > * { max-width: 680px; margin-inline: auto; }
.read > .lede {
  max-width: 980px;
  font-size: clamp(1.7rem, 1.2rem + 1.6vw, 2.6rem);
  font-style: normal;
  line-height: 1.3;
  text-wrap: pretty;
}
.prose__first::first-letter {
  float: left;
  margin: 0.08em 0.14em 0 0;
  font-family: var(--title);
  font-size: 4.6em;
  line-height: 0.8;
  background: var(--g-title);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.prose > h2 {
  display: flex;
  align-items: center;
  gap: 1.6rem;
  max-width: 1180px;
  margin-top: 2.4em;
  font-family: var(--title);
  font-size: clamp(1.3rem, 1rem + 1vw, 1.8rem);
  font-weight: 400;
  letter-spacing: 0.14em;
  text-align: center;
  text-transform: uppercase;
  background: var(--g-title);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.prose > h2::before,
.prose > h2::after { content: ""; flex: 1; height: 2px; background: linear-gradient(90deg, transparent, var(--gold-ink)); }
.prose > h2::after { transform: scaleX(-1); }
.prose > blockquote {
  position: relative;
  max-width: 1000px;
  margin: 2.4em auto;
  padding: clamp(2rem, 5vw, 3.4rem) clamp(1.4rem, 6vw, 5rem);
  border-radius: 22px;
  border: 1px solid rgba(189, 93, 15, 0.75);
  background:
    radial-gradient(70% 90% at 80% 0%, rgba(238, 194, 90, 0.16), transparent 60%),
    var(--grain),
    linear-gradient(160deg, var(--board), var(--board-deep));
  background-size: 100% 100%, var(--grain-size), 100% 100%;
  box-shadow: 0 30px 50px -30px rgba(40, 18, 4, 0.85);
}
.prose > blockquote::before { content: ""; position: absolute; top: -1px; left: 12%; right: 12%; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }
.prose > blockquote svg { position: static; display: block; width: 40px; height: 32px; margin: 0 auto 1rem; padding: 0; transform: none; background: none; color: var(--gold); }
.prose > blockquote p { color: var(--gold-light); font-size: clamp(1.8rem, 1.3rem + 1.6vw, 2.6rem); }
.prose > blockquote cite { color: rgba(251, 238, 221, 0.78); }
[data-theme="dark"] .prose > h2 { color: transparent; }
[data-theme="dark"] .prose > h2::before,
[data-theme="dark"] .prose > h2::after { height: 1px; background: linear-gradient(90deg, transparent, var(--gold)); }
[data-theme="dark"] .prose > blockquote { border-color: var(--g-line); background: var(--g-card); box-shadow: none; }
"""

MAIN_S5 = f"""{HERO}

  <article class="wrap read">
    {LEDE}
    <div class="prose">
{BODY_Q}
    </div>
  </article>
"""

BUILDS = [
    (CSS_S1, MAIN_S1, "Marginalia: the headings, the facts and the quotation hang in the margins beside their text."),
    (CSS_S2, MAIN_S2, "Two rails: the facts and the way back on the left, other articles on the right."),
    (CSS_S3, MAIN_S3, "Contents: the article's headings down the left, the facts on a cream card on the right."),
    (CSS_S4, MAIN_S4, "Bay: the text on a cream leaf in the bookshelf's wooden frame."),
    (CSS_S5, MAIN_S5, "Breakouts: the lede, the headings and the quotation break out to the full width."),
]

if __name__ == "__main__":
    for (fname, name), (css, main, blurb) in zip(OPTIONS, BUILDS):
        nav = switcher(fname, OPTIONS, "Sides")
        (HERE / fname).write_text(page(fname, name, blurb, css, main, "", nav))
        print("wrote", fname)

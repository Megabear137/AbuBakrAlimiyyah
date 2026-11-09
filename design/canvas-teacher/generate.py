#!/usr/bin/env python3
"""The teacher page: four mockups, one HTML file each.

The page a teacher's card on the home page opens. Each option loads the
site's styles.css and the article canvas's mockup.css (the switcher, the
header's round buttons on the ground, .back and the reading text), and borrows
that canvas's header, menu and footer, so only the head of the page and the
way the bio is laid out differ.

Content is content/teachers.json's as it stands: the first teacher's
honorific, name and one-line bio, and the others as the mosaic's cards. The
long bio the page exists for isn't in the JSON yet, so it is TODO paragraphs
at the length of real ones (it would take the articles' block shape:
paragraphs and headings).

Edit this file, not the output:  python3 generate.py
"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent

_spec = importlib.util.spec_from_file_location("article", HERE.parent / "canvas-article" / "generate.py")
art = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(art)

ARROW = art.ARROW
PAGE = ' aria-current="page"'

TEACHERS = [
    ("Moulana", "Kasim Ingar", "Imam of our masjid, and teacher for over 36 years"),
    ("Moulana", "Salim Chauhan", ""),
    ("Moulana", "Zuber Motala", ""),
    ("Mufti", "Ayoub Degya", "TODO: Short line about this teacher."),
    ("Moulana", "Omer Khurshid", "TODO: Short line about this teacher."),
    ("Moulana", "TODO: Sixth teacher", "TODO: Short line about this teacher."),
    ("Moulana", "TODO: Seventh teacher", "TODO: Short line about this teacher."),
]
HON, NAME, BIO = TEACHERS[0]

BACK = f'<a class="back" href="../../index.html#teachers">{ARROW} Teachers</a>'

BODY = """\
<p class="prose__first">TODO: The teacher's biography, in the masjid's words. This paragraph stands in for it at the length of a real one: where the teacher studied, and under whom, so that the width of the column and the size of the type can be judged as they will read.</p>
<p>TODO: Biography. A second paragraph, a little shorter: the teacher's years of teaching, at this masjid and before it.</p>
<h2>TODO: Section heading</h2>
<p>TODO: Biography. Under a heading the text carries on at the same measure. A long biography may be broken up by headings like the one above; a short one may be a single paragraph, and the page reads the same.</p>
<p>TODO: Biography. A closing paragraph. Where it ends, the page offers the other teachers as the home page shows them, then the footer.</p>
"""

OPTIONS = [
    ("1-banner.html", "Banner"),
    ("2-card.html", "The card, opened"),
    ("3-board-sheet.html", "Board & sheet"),
    ("4-niche.html", "Mihrab niche"),
]


def switcher(current):
    links = "".join(
        f'<a href="{f}" title="{name}"{PAGE if f == current else ""}>{i + 1}</a>'
        for i, (f, name) in enumerate(OPTIONS))
    return f"""
<nav class="m-switch" aria-label="Mockups">
  <span>Teacher</span>{links}<i></i>
  <button type="button" data-set-theme="light">Light</button>
  <button type="button" data-set-theme="dark">Dark</button>
</nav>"""


def others():
    """The other teachers, as the mosaic's small cards, each opening its page."""
    cards = "".join(
        f'<a class="teacher{" teacher--todo" if n.startswith("TODO") else ""}" href="#top">'
        f'<p class="teacher__honorific">{h}</p><h3 class="teacher__name">{n}</h3>'
        + (f'<p class="teacher__bio">{b}</p>' if b else "") + "</a>"
        for h, n, b in TEACHERS[1:])
    return f"""
  <hr class="section-rule">
  <section class="section" aria-labelledby="others-heading">
    <div class="wrap">
      <div class="section__head">
        <h2 class="section__heading" id="others-heading">Our Teachers</h2>
      </div>
      <div class="others">{cards}</div>
      <p class="more__foot">{BACK}</p>
    </div>
  </section>"""


SHARED_CSS = """
/* The other teachers: the mosaic's cards, three across, as links. */
.others { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-auto-rows: 200px; gap: 1.2rem; }
.others .teacher { color: inherit; text-decoration: none; }
@media (max-width: 880px) { .others { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .others { grid-template-columns: minmax(0, 1fr); grid-auto-rows: auto; } .others .teacher { min-height: 160px; } }

.read { max-width: calc(680px + 2 * var(--gutter)); }
.prose h2 { color: var(--g-text); }
[data-theme="dark"] .prose h2 { color: var(--gold-light); font-weight: 500; }
"""


def page(fname, name, blurb, css, main, body_class=""):
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Teacher · {name}</title>
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
  <link rel="stylesheet" href="../../assets/css/styles.css?v=55">
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
{others()}
</main>
{art.FOOTER}
{switcher(fname)}
{art.SCRIPTS}
</body>
</html>
"""


# ----------------------------------------------------------------------------
# 1. Banner: the article page's banner - the photograph, shorter, carrying the
#    honorific, the name and the one-line bio - over one 680px column.
# ----------------------------------------------------------------------------
CSS_1 = """
.a-hero .hero__title { max-width: 14ch; }
.t-bio { max-width: 34rem; margin: 0 auto; color: rgba(255, 246, 234, 0.9); font-family: var(--display); font-size: 1.4rem; font-style: italic; line-height: 1.35; }
.read { padding-top: clamp(1rem, 3vw, 2rem); }
"""

MAIN_1 = f"""
  <section class="hero a-hero" aria-labelledby="t-name">
    <div class="hero__img" aria-hidden="true"></div>
    <div class="wrap hero__body">
      <p class="in">{BACK}</p>
      <p class="in"><span class="chip">{HON}</span></p>
      <h1 class="hero__title in" id="t-name">{NAME}</h1>
      <p class="t-bio in">{BIO}</p>
    </div>
  </section>

  <article class="wrap read">
    <div class="prose">
{BODY}
    </div>
  </article>
"""

# ----------------------------------------------------------------------------
# 2. The card, opened: no photograph. The teacher's own mosaic card - cream in
#    its double gold frame, board in dark - grown into the head of the page,
#    then the logo rule and the bio in one column with a drop cap.
# ----------------------------------------------------------------------------
CSS_2 = """
.t-head { padding-top: 130px; }
.t-card {
  max-width: 900px;
  margin: 0 auto;
  padding: clamp(2.4rem, 6vw, 4.2rem) clamp(1.6rem, 6vw, 5rem);
  border-radius: 24px;
  background: linear-gradient(160deg, #fffaf0, #f3e2c3);
  box-shadow:
    inset 0 0 0 1px var(--gold),
    inset 0 0 0 7px #fbf3e2,
    inset 0 0 0 8px rgba(201, 164, 87, 0.8),
    0 40px 60px -36px rgba(40, 18, 4, 0.7);
  color: var(--brown-ink);
  text-align: center;
}
.t-card .back { margin-bottom: 2.2rem; color: #7d5006; }
.t-card__honorific { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.34em; text-transform: uppercase; }
.t-card__name {
  margin-top: 0.8rem;
  font-family: var(--title);
  font-size: clamp(2.3rem, 1.3rem + 3.4vw, 4.2rem);
  font-weight: 400;
  letter-spacing: 0.08em;
  line-height: 1.05;
  text-transform: uppercase;
}
.t-card__bio {
  max-width: 30rem;
  margin: 1.6rem auto 0;
  padding-top: 1.4rem;
  border-top: 1px solid rgba(154, 101, 8, 0.3);
  font-family: var(--display);
  font-size: 1.45rem;
  font-style: italic;
  line-height: 1.35;
}
.t-head + .section-rule { margin-top: clamp(2.5rem, 5vw, 4rem); }

.read { padding-top: clamp(3.5rem, 7vw, 5rem); }
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

[data-theme="dark"] .t-card {
  border: 1px solid var(--g-line);
  background:
    radial-gradient(120% 90% at 20% 10%, rgba(238, 194, 90, 0.22), transparent 60%),
    linear-gradient(180deg, transparent 55%, rgba(20, 9, 2, 0.45)),
    linear-gradient(155deg, var(--board), var(--board-deep));
  box-shadow: 0 40px 70px -40px rgba(0, 0, 0, 0.9);
  color: #fff6ea;
}
[data-theme="dark"] .t-card .back { color: var(--gold); }
[data-theme="dark"] .t-card__name {
  background: var(--g-title);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
[data-theme="dark"] .t-card__bio { border-top-color: var(--g-line); color: var(--g-text); font-weight: 400; }
"""

MAIN_2 = f"""
  <header class="wrap t-head">
    <div class="t-card">
      {BACK}
      <p class="t-card__honorific">{HON}</p>
      <h1 class="t-card__name">{NAME}</h1>
      <p class="t-card__bio">{BIO}</p>
    </div>
  </header>
  <hr class="section-rule">

  <article class="wrap read">
    <div class="prose">
{BODY}
    </div>
  </article>
"""

# ----------------------------------------------------------------------------
# 3. Board & sheet: a band of the dark board (the Details panels' board, gold
#    title, rust edge) carrying the name, and the bio on a cream sheet - Our
#    Program's panel at reading length - rising out of it.
# ----------------------------------------------------------------------------
CSS_3 = """
.t-band {
  position: relative;
  padding: 150px 0 200px;
  border-bottom: 1px solid rgba(189, 93, 15, 0.8);
  background:
    radial-gradient(70% 90% at 50% 0%, rgba(238, 194, 90, 0.16), transparent 60%),
    var(--grain),
    linear-gradient(180deg, var(--board), var(--board-deep));
  background-size: 100% 100%, var(--grain-size), 100% 100%;
  color: var(--on-choc);
  text-align: center;
}
.t-band .back { color: var(--gold); }
.t-band__honorific { margin-top: 2rem; color: var(--gold); font-size: 0.72rem; font-weight: 600; letter-spacing: 0.34em; text-transform: uppercase; }
.t-band__honorific::before,
.t-band__honorific::after { content: "✦"; margin: 0 0.9em; font-size: 0.8em; }
.t-band h1 { margin: 0.8rem 0 1rem; color: var(--gold-light); font-family: var(--display); font-size: clamp(2.6rem, 1.5rem + 3.2vw, 4.6rem); font-weight: 600; line-height: 1.02; }
.t-band__bio { max-width: 32rem; margin: 0 auto; color: rgba(251, 238, 221, 0.82); font-family: var(--display); font-size: 1.35rem; font-style: italic; line-height: 1.35; }

.sheet {
  position: relative;
  max-width: 860px;
  margin: -130px auto 0;
  padding: clamp(2rem, 5vw, 4rem) clamp(1.4rem, 6vw, 5rem);
  border-radius: 22px;
  border: 1px solid var(--gilt-edge);
  background: rgba(255, 251, 244, 0.98);
  box-shadow: 0 40px 70px -40px rgba(40, 18, 4, 0.8);
}
.sheet::before { content: ""; position: absolute; top: -1px; left: 12%; right: 12%; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }
.sheet .prose { color: var(--brown-ink); }
.sheet .prose h2 { color: var(--gold-ink); font-size: 1.5rem; letter-spacing: 0.06em; text-transform: uppercase; }
.sheet-wrap { padding-inline: var(--gutter); }

[data-theme="dark"] .t-band { border-bottom-color: var(--g-line); background: radial-gradient(70% 90% at 50% 0%, rgba(227, 179, 74, 0.12), transparent 60%), rgba(10, 5, 1, 0.5); }
[data-theme="dark"] .sheet { border-color: var(--g-line); background: linear-gradient(160deg, #2a170b, #1e0f06); box-shadow: 0 40px 70px -40px rgba(0, 0, 0, 0.9); }
[data-theme="dark"] .sheet .prose { color: var(--g-text); }
[data-theme="dark"] .sheet .prose h2 { color: var(--gold); font-weight: 500; }
"""

MAIN_3 = f"""
  <header class="t-band">
    <div class="wrap">
      {BACK}
      <p class="t-band__honorific">{HON}</p>
      <h1>{NAME}</h1>
      <p class="t-band__bio">{BIO}</p>
    </div>
  </header>

  <div class="sheet-wrap">
    <article class="sheet">
      <div class="prose">
{BODY}
      </div>
    </article>
  </div>
"""

# ----------------------------------------------------------------------------
# 4. Mihrab niche: the teacher stands in one of the Alumni section's niches -
#    moulding, dark recess, sill - held still on the left while the bio
#    scrolls on the right. On phones the niche heads the page.
# ----------------------------------------------------------------------------
CSS_4 = """
.t-split {
  display: grid;
  grid-template-columns: 330px minmax(0, 680px);
  gap: clamp(2.5rem, 6vw, 5.5rem);
  justify-content: center;
  align-items: start;
  padding-top: 130px;
}
.t-split .niche-slot { position: sticky; top: 2rem; height: 540px; }
.t-split .niche__recess { justify-content: flex-end; }
.t-niche__honorific { color: var(--gold); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.34em; text-transform: uppercase; }
.t-niche__name { margin: 0.6rem 0 0; color: var(--gold-light); font-family: var(--display); font-size: 2.3rem; font-weight: 600; line-height: 1.05; }
.t-niche__bio {
  align-self: stretch;
  margin-top: 1.2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(238, 194, 90, 0.35);
  color: rgba(251, 238, 221, 0.8);
  font-family: var(--display);
  font-size: 1.15rem;
  font-style: italic;
  line-height: 1.35;
}
.t-split__text { padding-top: 1rem; }
.t-split__text .back { margin-bottom: 2rem; }
.t-split__title {
  margin-bottom: 2rem;
  font-family: var(--title);
  font-size: clamp(1.9rem, 1.2rem + 2vw, 2.8rem);
  font-weight: 400;
  letter-spacing: 0.08em;
  line-height: 1.1;
  text-transform: uppercase;
  background: var(--g-title);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.t-split__title::after { content: ""; display: block; width: 64px; height: 2px; margin-top: 1.4rem; background: linear-gradient(90deg, var(--gold-ink), transparent); }

@media (max-width: 880px) {
  .t-split { grid-template-columns: minmax(0, 1fr); }
  .t-split .niche-slot { position: static; width: min(100%, 330px); height: 460px; margin: 0 auto; }
  .t-split__text .back { display: none; }
}
"""

MAIN_4 = f"""
  <div class="wrap t-split">
    <figure class="niche-slot">
      <div class="niche">
        <div class="niche__recess">
          <p class="t-niche__honorific">{HON}</p>
          <h1 class="t-niche__name">{NAME}</h1>
          <p class="t-niche__bio">{BIO}</p>
        </div>
      </div>
      <div class="niche__sill"></div>
    </figure>

    <article class="t-split__text">
      {BACK}
      <p class="t-split__title" aria-hidden="true">{HON} {NAME}</p>
      <div class="prose">
{BODY}
      </div>
    </article>
  </div>
"""

BUILDS = [
    (CSS_1, MAIN_1, "", "The article page's banner, carrying the honorific, name and one-line bio; one column beneath."),
    (CSS_2, MAIN_2, "on-ground", "No photograph: the teacher's own mosaic card grown into the head of the page, then a drop cap."),
    (CSS_3, MAIN_3, "", "A band of the dark board with the name in gold; the bio on a cream sheet rising out of it."),
    (CSS_4, MAIN_4, "on-ground", "The teacher stands in an Alumni mihrab niche, held still on the left; the bio scrolls on the right."),
]

if __name__ == "__main__":
    for (fname, name), (css, main, cls, blurb) in zip(OPTIONS, BUILDS):
        (HERE / fname).write_text(page(fname, name, blurb, css, main, cls))
        print("wrote", fname)

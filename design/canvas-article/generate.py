#!/usr/bin/env python3
"""The article page: five mockups, one HTML file each.

Every page shares the site's header, menu and footer, the reading text and
the "More articles" row; each option differs in how the article is opened
(its head) and how the text is laid out. All content is the placeholder shape
of an article in content/media.json (title, subject, author, readMinutes,
excerpt) plus placeholder paragraphs for the body the JSON doesn't hold yet.

Edit this file, not the output:  python3 generate.py
"""
from pathlib import Path

HERE = Path(__file__).parent

ARROW = '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg>'
BOOK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M4 5.5C4 4.7 4.7 4 5.5 4H11v16H5.5C4.7 20 4 19.3 4 18.5v-13ZM20 5.5c0-.8-.7-1.5-1.5-1.5H13v16h5.5c.8 0 1.5-.7 1.5-1.5v-13Z"/></svg>'
QUOTE = '<svg viewBox="0 0 40 32" fill="currentColor" aria-hidden="true"><path d="M0 32V19C0 8 6 1.5 16 0l1.6 4C11.6 5.8 9 9.4 8.8 14H16v18H0zm22 0V19C22 8 28 1.5 38 0l1.6 4C33.6 5.8 31 9.4 30.8 14H38v18H22z"/></svg>'
HOME = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 11l8-7 8 7v9H4z"/></svg>'
MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3.5" y="5.5" width="17" height="13" rx="1.5"/><path d="M4 7l8 6 8-6"/></svg>'
PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg>'

CUR = ' aria-current="true"'
PAGE = ' aria-current="page"'

# The article, as content/media.json holds it.
A = {
    "title": "TODO: Article title",
    "subject": "TODO: Subject",
    "author": "TODO: Author",
    "read": "5 min read",
    "excerpt": "TODO: A sentence or two introducing the article.",
}

BACK = f'<a class="back" href="../../index.html#articles">{ARROW} Articles</a>'
META = (f'<p class="meta"><span>{A["author"]}</span><span class="meta__dot" aria-hidden="true"></span>'
        f'<span>{A["read"]}</span></p>')

# The body: placeholder text at the length of real paragraphs, so the measure
# and leading can be judged. Option 2 hangs a drop cap on .prose__first.
BODY = """\
<p class="prose__first">TODO: The article's opening paragraph. This text stands in for the article the masjid will send, at the length of a real paragraph, so that the width of the column, the size of the type and the space between the lines can be judged as they will read.</p>
<p>TODO: Article text. A second paragraph of placeholder, a little shorter than the first, to show how one paragraph follows another down the page and where the eye rests between them.</p>
<h2>TODO: Section heading</h2>
<p>TODO: Article text. Under a section heading the text carries on at the same measure. A long article is broken up by headings like the one above; a short one may have none at all, and the page reads the same without them.</p>
<p>TODO: Article text. A paragraph before a quotation, which the page sets apart from the running text so that it can be found again at a glance.</p>
<blockquote>
  <p>TODO: A quoted passage, set apart from the text.</p>
  <cite>TODO: Its source</cite>
</blockquote>
<p>TODO: Article text. After the quotation the text resumes at the same width as before, and the quotation's space above and below keeps it from crowding the paragraphs on either side.</p>
<h2>TODO: Section heading</h2>
<p>TODO: Article text. A closing paragraph of placeholder. Where the article ends, the page offers the other articles, then the footer, as the home page does.</p>
"""

def more():
    cards = "".join(
        f'<a class="slider__card board{" board--rust" if i % 2 else ""}" href="#top"{CUR if i == 0 else ""}>'
        f'<b>{i + 1:02d}</b><em>TODO: Subject</em><span>TODO: Article title</span></a>'
        for i in range(4))
    return f"""
  <hr class="section-rule">
  <section class="section more" aria-labelledby="more-heading">
    <div class="wrap">
      <div class="section__head">
        <h2 class="section__heading" id="more-heading">Articles</h2>
      </div>
      <div class="more__grid">{cards}</div>
      <p class="more__foot">{BACK}</p>
    </div>
  </section>"""


HEADER = """
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap site-header__inner">
    <button class="round" type="button" data-menu-open aria-controls="site-menu" aria-expanded="false" aria-label="Open menu">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <div class="site-header__end">
      <button class="round theme-toggle" type="button" data-theme-toggle aria-label="Switch to dark mode">
        <svg class="theme-toggle__moon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z"/></svg>
        <svg class="theme-toggle__sun" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
      <a class="btn btn--line btn--sm site-header__cta" href="../../index.html#curriculum">View Curriculum</a>
    </div>
  </div>
</header>
<nav class="menu" id="site-menu" aria-label="Primary">
  <button class="round menu__close" type="button" data-menu-close aria-label="Close menu">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
  </button>
  <ul class="menu__list">
    <li><a href="../../index.html#top">Home</a></li>
    <li><a href="../../index.html#about">About</a></li>
    <li><a href="../../index.html#program">Program</a></li>
    <li><a href="../../index.html#teachers">Teachers</a></li>
    <li><a href="../../index.html#articles">Articles</a></li>
    <li><a href="../../index.html#videos">Videos</a></li>
    <li><a href="../../index.html#alumni">Alumni</a></li>
    <li><a href="../../index.html#contact">Contact</a></li>
  </ul>
</nav>"""

FOOTER = f"""
<footer class="site-footer" id="contact">
  <div class="wrap">
    <div class="site-footer__grid">
      <a class="brand brand--footer" href="../../index.html#top">
        <img class="brand__mark" src="../../assets/img/logo_gold_web.png" alt="" width="80" height="58">
        <span class="brand__name">Jamiyah Islamiyyah Abu Bakr</span>
      </a>
      <div>
        <h2 class="site-footer__heading">Contact</h2>
        <address class="site-footer__contact">
          <span class="site-footer__line"><i aria-hidden="true">{HOME}</i>TODO: masjid street address, city, postal code</span>
          <span class="site-footer__line"><i aria-hidden="true">{MAIL}</i>TODO: info@example.org</span>
          <span class="site-footer__line"><i aria-hidden="true">{PHONE}</i>TODO: (000) 000-0000</span>
        </address>
      </div>
    </div>
    <p class="site-footer__legal">&copy; 2026 Jamiyah Islamiyyah Abu Bakr</p>
  </div>
</footer>"""

OPTIONS = [
    ("1-banner.html", "Banner"),
    ("2-section-head.html", "Section head"),
    ("3-board-sheet.html", "Board & sheet"),
    ("4-jadwal.html", "Jadwal leaf"),
    ("5-spread.html", "Spread"),
]


def switcher(current, options=None, label="Article"):
    links = "".join(
        f'<a href="{f}" title="{name}"{PAGE if f == current else ""}>{i + 1}</a>'
        for i, (f, name) in enumerate(options or OPTIONS))
    return f"""
<nav class="m-switch" aria-label="Mockups">
  <span>{label}</span>{links}<i></i>
  <button type="button" data-set-theme="light">Light</button>
  <button type="button" data-set-theme="dark">Dark</button>
</nav>"""


SCRIPTS = """
<script src="../../assets/js/nav.js?v=3"></script>
<script>
  // The switcher's Light | Dark, kept in step with the header's toggle.
  (function () {
    var root = document.documentElement;
    function mark() {
      var t = root.getAttribute("data-theme");
      document.querySelectorAll("[data-set-theme]").forEach(function (b) {
        b.setAttribute("aria-pressed", String(b.getAttribute("data-set-theme") === t));
      });
    }
    document.querySelectorAll("[data-set-theme]").forEach(function (b) {
      b.addEventListener("click", function () {
        var t = b.getAttribute("data-set-theme");
        root.setAttribute("data-theme", t);
        try { localStorage.setItem("alimiyyah.theme", t); } catch (e) {}
        mark();
      });
    });
    new MutationObserver(mark).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
    mark();
  })();
</script>"""


def page(fname, name, blurb, css, main, body_class="", nav=None):
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Article · {name}</title>
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
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Gilda+Display&family=Instrument+Sans:wght@400;500;600&family=Noto+Nastaliq+Urdu:wght@400;600&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../assets/css/styles.css?v=48">
  <link rel="stylesheet" href="mockup.css">
<!-- Option: {name}. {blurb} -->
<style>
{css.strip()}
</style>
</head>
<body id="top" class="{body_class}">
{HEADER}

<main id="main">
{main.rstrip()}
{more()}
</main>
{FOOTER}
{nav or switcher(fname)}
{SCRIPTS}
</body>
</html>
"""


# ----------------------------------------------------------------------------
# 1. Banner: the home page's hero, shorter, carrying the article's title; the
#    text in one column on the ground beneath it.
# ----------------------------------------------------------------------------
CSS_1 = """
.a-hero { min-height: max(520px, 68vh); align-items: flex-end; }
.a-hero .hero__img { inset: -20% 0 0; }
.a-hero .hero__img::after {
  background:
    linear-gradient(90deg, rgba(36, 18, 5, 0.55), rgba(36, 18, 5, 0.75) 50%, rgba(36, 18, 5, 0.55)),
    linear-gradient(180deg, rgba(36, 18, 5, 0.55), transparent 35%);
}
.a-hero .hero__body { padding-block: 140px clamp(4rem, 12vh, 9rem); text-align: center; }
.a-hero .back { color: var(--gold-pale); }
.a-hero .chip { margin-top: 1.6rem; border-color: rgba(227, 179, 74, 0.45); color: var(--gold-pale); font-size: 0.62rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.a-hero .chip::before { background: var(--gold); }
.a-hero .hero__title { max-width: 18ch; margin: 1.2rem auto 1.3rem; font-size: clamp(2.6rem, 1.4rem + 4vw, 5rem); }
.a-hero .meta { color: rgba(255, 246, 234, 0.9); font-family: var(--display); font-size: 1.3rem; font-style: italic; }
.a-hero .meta__dot { background: var(--gold); }

.read { max-width: calc(680px + 2 * var(--gutter)); padding-top: clamp(1rem, 3vw, 2rem); }
.lede { color: var(--g-text); font-family: var(--display); font-size: clamp(1.5rem, 1.2rem + 1vw, 1.9rem); font-style: italic; font-weight: 500; line-height: 1.4; text-align: center; }
.lede::after { content: ""; display: block; width: 64px; height: 2px; margin: 2rem auto 2.4rem; background: linear-gradient(90deg, transparent, var(--gold-ink), transparent); }
.prose h2 { color: var(--g-text); }
.prose blockquote {
  position: relative;
  margin-block: 2.4em;
  padding: 2rem 0 1.8rem;
  border-block: 1px solid var(--g-line);
  text-align: center;
}
.prose blockquote svg { position: absolute; top: -14px; left: 50%; width: 36px; height: 28px; padding: 0 8px; transform: translateX(-50%); background: var(--hero-fade); color: var(--g-mark); }
.prose blockquote p { font-family: var(--display); font-size: 1.7rem; font-style: italic; line-height: 1.35; }
.prose cite { color: var(--g-accent); }
[data-theme="dark"] .prose blockquote svg { background: #231208; }
[data-theme="dark"] .prose h2 { color: var(--gold-light); font-weight: 500; }
"""

MAIN_1 = f"""
  <section class="hero a-hero" aria-labelledby="a-title">
    <div class="hero__img" aria-hidden="true"></div>
    <div class="wrap hero__body">
      <p class="in">{BACK}</p>
      <p class="in"><span class="chip">{A["subject"]}</span></p>
      <h1 class="hero__title in" id="a-title">{A["title"]}</h1>
      <div class="in">{META}</div>
    </div>
  </section>

  <article class="wrap read">
    <p class="lede">{A["excerpt"]}</p>
    <div class="prose">
{BODY.replace("<blockquote>", "<blockquote>" + QUOTE)}
    </div>
  </article>
"""

# ----------------------------------------------------------------------------
# 2. Section head: no photograph. The title is set as the home page sets a
#    section's - ✦ eyebrow (the subject), Gilda capitals, italic lede (the
#    excerpt) - then the logo rule, and a single column with a drop cap.
# ----------------------------------------------------------------------------
CSS_2 = """
.a-head { padding-top: 150px; }
.a-head .section__head { margin-bottom: 0; }
.a-head .back { margin-bottom: 2.4rem; }
.a-head .section__heading { max-width: 16ch; margin-inline: auto; font-size: clamp(2.2rem, 1.2rem + 3.6vw, 4.4rem); }
.a-head .section__lede { max-width: 36rem; margin-top: 0.4rem; font-size: 1.35rem; }
.a-head .meta { margin-top: 1.4rem; color: var(--g-accent); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; }
.a-head + .section-rule { margin-top: clamp(2.5rem, 5vw, 4rem); }

.read { max-width: calc(700px + 2 * var(--gutter)); padding-top: clamp(4rem, 7vw, 5.5rem); }
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
.prose h2 {
  font-family: var(--title);
  font-size: 1.35rem;
  font-weight: 400;
  letter-spacing: 0.14em;
  text-align: center;
  text-transform: uppercase;
}
.prose h2::before,
.prose h2::after { content: "✦"; margin: 0 0.8em; color: var(--g-accent); font-size: 0.6em; vertical-align: 0.3em; }
/* The quotation: Our Program's cream panel in its gilt hairline. */
.prose blockquote {
  position: relative;
  margin-block: 2.4em;
  padding: 1.8rem 2.2rem;
  border-radius: 22px;
  border: 1px solid var(--gilt-edge);
  background: rgba(255, 251, 244, 0.96);
  box-shadow: 0 24px 44px -28px rgba(70, 34, 6, 0.6);
  color: var(--brown-ink);
  text-align: center;
}
.prose blockquote::before { content: ""; position: absolute; top: -1px; left: 12%; right: 12%; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }
.prose blockquote p { font-family: var(--display); font-size: 1.6rem; font-style: italic; font-weight: 500; line-height: 1.35; }
.prose cite { color: var(--gold-ink); }
[data-theme="dark"] .prose blockquote { border-color: var(--g-line); background: var(--g-card); box-shadow: none; color: var(--g-text); }
[data-theme="dark"] .prose cite { color: var(--gold); }
"""

MAIN_2 = f"""
  <header class="wrap a-head">
    <div class="section__head">
      {BACK}
      <p class="section__eyebrow">{A["subject"]}</p>
      <h1 class="section__heading">{A["title"]}</h1>
      <p class="section__lede">{A["excerpt"]}</p>
      {META}
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
#    title, rust edge) under the header, and the text on a cream sheet that
#    rises out of it - Our Program's panel, at reading length.
# ----------------------------------------------------------------------------
CSS_3 = """
.a-band {
  position: relative;
  padding: 150px 0 190px;
  border-bottom: 1px solid rgba(189, 93, 15, 0.8);
  background:
    radial-gradient(70% 90% at 80% 0%, rgba(238, 194, 90, 0.16), transparent 60%),
    var(--grain),
    linear-gradient(180deg, var(--board), var(--board-deep));
  background-size: 100% 100%, var(--grain-size), 100% 100%;
  color: var(--on-choc);
}
.a-band__inner { display: grid; grid-template-columns: minmax(0, 1fr) 220px; gap: 3rem; align-items: center; max-width: calc(980px + 2 * var(--gutter)); }
.a-band .back { color: var(--gold); }
.a-band .slider__tags { margin-top: 1.8rem; color: var(--gold); }
.a-band .chip { border-color: rgba(238, 194, 90, 0.4); }
.a-band .chip::before { background: var(--gold); }
.a-band h1 { margin: 1rem 0 0.6rem; color: var(--gold-light); font-family: var(--display); font-size: clamp(2.4rem, 1.5rem + 2.6vw, 4rem); font-weight: 600; line-height: 1.02; }
.a-band .slider__by { color: rgba(251, 238, 221, 0.78); }
.a-band .slider__art { width: 100%; }

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
.sheet__lede { color: var(--brown-ink); font-family: var(--display); font-size: 1.6rem; font-weight: 500; line-height: 1.4; }
.sheet__lede::after { content: ""; display: block; height: 1px; margin: 1.8rem 0 2rem; background: linear-gradient(90deg, var(--gilt-edge), transparent); }
.sheet .prose { color: var(--brown-ink); }
.sheet .prose h2 { color: var(--gold-ink); letter-spacing: 0.06em; text-transform: uppercase; font-size: 1.5rem; }
.sheet .prose blockquote {
  margin-block: 2.2em;
  padding: 1.6rem 1.8rem;
  border-radius: 16px;
  border: 1px solid rgba(189, 93, 15, 0.75);
  background: var(--grain), linear-gradient(160deg, var(--board), var(--board-deep));
  background-size: var(--grain-size), 100% 100%;
  color: var(--on-choc);
}
.sheet .prose blockquote p { color: var(--gold-light); font-family: var(--display); font-size: 1.55rem; font-style: italic; line-height: 1.35; }
.sheet .prose cite { color: rgba(251, 238, 221, 0.74); }

[data-theme="dark"] .a-band { border-bottom-color: var(--g-line); background: radial-gradient(70% 90% at 80% 0%, rgba(227, 179, 74, 0.1), transparent 60%), rgba(10, 5, 1, 0.5); }
[data-theme="dark"] .a-band .slider__art { border-color: var(--g-line); }
[data-theme="dark"] .sheet { border-color: var(--g-line); background: linear-gradient(160deg, #2a170b, #1e0f06); box-shadow: 0 40px 70px -40px rgba(0, 0, 0, 0.9); }
[data-theme="dark"] .sheet__lede,
[data-theme="dark"] .sheet .prose { color: var(--g-text); }
[data-theme="dark"] .sheet__lede::after { background: linear-gradient(90deg, var(--g-line), transparent); }
[data-theme="dark"] .sheet .prose h2 { color: var(--gold); font-weight: 500; }
[data-theme="dark"] .sheet .prose blockquote { border-color: var(--g-line); background: var(--g-card); }

@media (max-width: 880px) {
  .a-band__inner { grid-template-columns: minmax(0, 1fr); }
  .a-band .slider__art { display: none; }
}
"""

MAIN_3 = f"""
  <header class="a-band">
    <div class="wrap a-band__inner">
      <div>
        {BACK}
        <div class="slider__tags"><span class="chip">{A["subject"]}</span><span>{A["read"]}</span></div>
        <h1>{A["title"]}</h1>
        <p class="slider__by">{A["author"]}</p>
      </div>
      <div class="slider__art board board--rust" aria-hidden="true">{BOOK}</div>
    </div>
  </header>

  <div class="wrap">
    <article class="sheet">
      <p class="sheet__lede">{A["excerpt"]}</p>
      <div class="prose">
{BODY}
      </div>
    </article>
  </div>
"""

# ----------------------------------------------------------------------------
# 4. Jadwal leaf: the article as the folio shows a book - a ruled manuscript
#    leaf in gold, ink and red, with the slip's ribbon marker and a catchword
#    naming the next article at its foot.
# ----------------------------------------------------------------------------
CSS_4 = """
.a-top { padding-top: 140px; text-align: center; }
.leaf {
  position: relative;
  text-align: left;
  max-width: 860px;
  margin: 2rem auto 0;
  padding: clamp(2.4rem, 6vw, 4.6rem) clamp(1.6rem, 7vw, 5.2rem) clamp(2rem, 4vw, 3rem);
  border-radius: 10px;
  color: #3b2712;
  background:
    radial-gradient(circle at 14% 18%, rgba(150, 105, 45, 0.08) 0 14px, transparent 15px),
    radial-gradient(circle at 82% 44%, rgba(150, 105, 45, 0.07) 0 18px, transparent 19px),
    radial-gradient(circle at 36% 86%, rgba(150, 105, 45, 0.07) 0 12px, transparent 13px),
    linear-gradient(170deg, #f7edd6, #ead9b8);
  box-shadow: inset 0 0 60px rgba(120, 84, 34, 0.22), 0 30px 50px -26px rgba(40, 18, 4, 0.7);
}
.leaf::before {                          /* the jadwal: gold, ink, red */
  content: "";
  position: absolute;
  inset: 14px;
  border: 1px solid rgba(60, 38, 14, 0.55);
  box-shadow: 0 0 0 3px #f7edd6, 0 0 0 4.5px var(--gilt), inset 0 0 0 3px #f5ead1, inset 0 0 0 4px rgba(138, 42, 32, 0.55);
  pointer-events: none;
}
.leaf > * { position: relative; }
.leaf__ribbon {
  position: absolute;
  top: 0;
  right: 44px;
  width: 14px;
  height: 64px;
  background: linear-gradient(90deg, #6e1f17, #9a3326 50%, #6e1f17);
  clip-path: polygon(0 0, 100% 0, 100% 100%, 50% 82%, 0 100%);
}
.leaf__subject { color: #8a2a20; font-family: var(--ui); font-size: 0.72rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; }
.leaf h1 { margin: 0.4rem 0 0.3rem; font-family: var(--display); font-size: clamp(2.2rem, 1.4rem + 2.4vw, 3.4rem); font-weight: 600; line-height: 1.04; }
.leaf__author { color: #6a4a22; font-family: var(--display); font-size: 1.25rem; font-style: italic; }
.leaf__author span { margin-left: 0.6rem; color: #8a2a20; font-family: var(--ui); font-size: 0.66rem; font-style: normal; font-weight: 600; letter-spacing: 0.16em; text-transform: uppercase; }
.leaf__rule { display: block; height: 1px; margin: 1.3rem 0 1.6rem; background: repeating-linear-gradient(90deg, rgba(60, 38, 14, 0.5) 0 6px, transparent 6px 10px); }
.leaf__lede { font-family: var(--display); font-size: 1.45rem; font-style: italic; line-height: 1.4; }
.leaf .prose { margin-top: 1.4rem; color: #3b2712; font-family: var(--ui); font-size: 1.02rem; line-height: 1.85; }
.leaf .prose h2 { color: #8a2a20; font-size: 1.7rem; }
.leaf .prose blockquote {
  margin-block: 2em;
  padding: 1.4rem 1.6rem;
  border-block: 1px solid rgba(60, 38, 14, 0.45);
  box-shadow: 0 -4px 0 -3px var(--gilt), 0 4px 0 -3px var(--gilt);
  text-align: center;
}
.leaf .prose blockquote p { font-family: var(--display); font-size: 1.6rem; font-style: italic; line-height: 1.35; }
.leaf .prose cite { color: #8a2a20; font-family: var(--ui); letter-spacing: 0.16em; }
.leaf__catch { margin-top: 2.4rem; padding-top: 1rem; border-top: 1px dashed rgba(60, 38, 14, 0.4); text-align: right; }
.leaf__catch a { color: #8a2a20; font-family: var(--display); font-size: 1.2rem; font-style: italic; text-decoration: none; }
.leaf__catch a:hover { text-decoration: underline; }
.leaf__catch small { display: block; color: #6a4a22; font-family: var(--ui); font-size: 0.62rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; }

[data-theme="dark"] .leaf { background: linear-gradient(160deg, #2e190b, #1c0e05); color: var(--g-text); box-shadow: 0 0 0 1px rgba(227, 179, 74, 0.4), 0 30px 50px -26px rgba(0, 0, 0, 0.8); }
[data-theme="dark"] .leaf::before { border: 1px solid rgba(227, 179, 74, 0.25); border-radius: 6px; box-shadow: none; }
[data-theme="dark"] .leaf__ribbon { background: linear-gradient(90deg, #1c4670, #3574ad 50%, #1c4670); }
[data-theme="dark"] .leaf__subject,
[data-theme="dark"] .leaf__author span,
[data-theme="dark"] .leaf .prose cite,
[data-theme="dark"] .leaf__catch a { color: var(--gold); }
[data-theme="dark"] .leaf h1,
[data-theme="dark"] .leaf .prose h2 { color: var(--gold-light); font-weight: 500; }
[data-theme="dark"] .leaf__author,
[data-theme="dark"] .leaf__catch small { color: var(--g-muted); }
[data-theme="dark"] .leaf .prose { color: var(--g-text); }
[data-theme="dark"] .leaf__rule { background: linear-gradient(90deg, rgba(227, 179, 74, 0.5), transparent); }
[data-theme="dark"] .leaf .prose blockquote { border-color: rgba(227, 179, 74, 0.3); box-shadow: none; }
[data-theme="dark"] .leaf__catch { border-top-color: rgba(227, 179, 74, 0.25); }
"""

MAIN_4 = f"""
  <div class="wrap a-top">
    {BACK}
    <article class="leaf">
      <span class="leaf__ribbon" aria-hidden="true"></span>
      <p class="leaf__subject">{A["subject"]}</p>
      <h1>{A["title"]}</h1>
      <p class="leaf__author">{A["author"]}<span>{A["read"]}</span></p>
      <span class="leaf__rule" aria-hidden="true"></span>
      <p class="leaf__lede">{A["excerpt"]}</p>
      <div class="prose">
{BODY}
      </div>
      <p class="leaf__catch"><small>Next</small><a href="#top">TODO: Article title &rarr;</a></p>
    </article>
  </div>
"""

# ----------------------------------------------------------------------------
# 5. Spread: two pages side by side - the masjid photograph held still down
#    the left with the title over it, and the text scrolling on the right.
#    Below 980px it folds into a banner over the text.
# ----------------------------------------------------------------------------
CSS_5 = """
.spread { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 6fr); }
.spread__art {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 100vh;
  min-height: 560px;
  padding: 130px clamp(1.6rem, 4vw, 3.6rem) clamp(2.4rem, 6vh, 4rem);
  overflow: hidden;
  border-right: 1px solid rgba(189, 93, 15, 0.8);
  background:
    linear-gradient(180deg, rgba(36, 18, 5, 0.7), rgba(36, 18, 5, 0.2) 30%, rgba(36, 18, 5, 0.85) 75%, rgba(26, 13, 4, 0.95)),
    var(--choc-deep) url("../../assets/img/hero-masjid.jpg") 40% 70% / cover no-repeat;
  color: #fff6ea;
}
.spread__art .back { color: var(--gold-pale); margin-bottom: auto; }
.spread__art .slider__tags { color: var(--gold); }
.spread__art .chip { border-color: rgba(227, 179, 74, 0.45); }
.spread__art .chip::before { background: var(--gold); }
.spread__art h1 {
  margin: 1.1rem 0 1rem;
  font-family: var(--display);
  font-size: clamp(2.4rem, 1.2rem + 2.8vw, 4.4rem);
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.spread__art .slider__by { color: rgba(255, 246, 234, 0.85); }
.spread__art .slider__by::before { content: ""; display: block; width: 48px; height: 2px; margin-bottom: 1rem; background: var(--gold); }

/* The header's right-hand buttons stand on the ground here, not the photo. */
[data-theme="light"] .site-header__end .round { border-color: var(--gilt-edge); background: #fffaf2; color: var(--brown-ink); box-shadow: 0 10px 22px -14px rgba(70, 34, 6, 0.7); }
[data-theme="light"] .site-header__end .btn--line { border-color: var(--g-line); background: rgba(255, 250, 242, 0.6); color: var(--brown-ink); }
.spread__text { padding: 140px clamp(1.6rem, 5vw, 5rem) 0; }
.spread__text > * { max-width: 620px; }
.spread__lede { color: var(--g-text); font-family: var(--display); font-size: 1.7rem; font-weight: 500; line-height: 1.35; }
.spread__lede::after { content: ""; display: block; width: 100%; height: 1px; margin: 1.8rem 0 2rem; background: linear-gradient(90deg, var(--g-line), transparent); }
.spread .prose h2 { color: var(--g-text); }
.spread .prose h2::before { content: ""; display: block; width: 28px; height: 2px; margin-bottom: 0.9rem; background: var(--g-mark); }
.spread .prose blockquote { padding: 0.3rem 0 0.3rem 1.6rem; border-left: 3px solid var(--g-mark); }
.spread .prose blockquote p { font-family: var(--display); font-size: 1.65rem; font-style: italic; line-height: 1.35; }
.spread .prose cite { color: var(--g-accent); }
[data-theme="dark"] .spread__art { border-right-color: var(--g-line); }
[data-theme="dark"] .spread__art h1 { background: linear-gradient(180deg, #f7e0a4, #e3b34a 60%, #c48f2c); -webkit-background-clip: text; background-clip: text; color: transparent; }
[data-theme="dark"] .spread .prose h2 { color: var(--gold-light); font-weight: 500; }

@media (max-width: 980px) {
  .spread { grid-template-columns: minmax(0, 1fr); }
  .spread__art { position: relative; height: auto; min-height: 520px; border-right: 0; }
  /* The header's right-hand buttons stand on the ground here, not the photo. */
[data-theme="light"] .site-header__end .round { border-color: var(--gilt-edge); background: #fffaf2; color: var(--brown-ink); box-shadow: 0 10px 22px -14px rgba(70, 34, 6, 0.7); }
[data-theme="light"] .site-header__end .btn--line { border-color: var(--g-line); background: rgba(255, 250, 242, 0.6); color: var(--brown-ink); }
.spread__text { padding-top: 3rem; }
  .spread__text > * { margin-inline: auto; }
}
"""

MAIN_5 = f"""
  <div class="spread">
    <header class="spread__art">
      {BACK}
      <div class="slider__tags"><span class="chip">{A["subject"]}</span><span>{A["read"]}</span></div>
      <h1>{A["title"]}</h1>
      <p class="slider__by">{A["author"]}</p>
    </header>
    <article class="spread__text">
      <p class="spread__lede">{A["excerpt"]}</p>
      <div class="prose">
{BODY}
      </div>
    </article>
  </div>
"""

BUILDS = [
    (CSS_1, MAIN_1, "", "The home page's banner, shorter, with the title over the photograph; one column beneath."),
    (CSS_2, MAIN_2, "on-ground", "No photograph: the title set as a section head, the logo rule, a drop cap."),
    (CSS_3, MAIN_3, "", "A band of the dark board with the title in gold; the text on a cream sheet rising out of it."),
    (CSS_4, MAIN_4, "on-ground", "The folio's ruled manuscript leaf, a ribbon marker and a catchword to the next article."),
    (CSS_5, MAIN_5, "", "Two pages: the photograph held still on the left under the title, the text scrolling on the right."),
]

if __name__ == "__main__":
    for (fname, name), (css, main, cls, blurb) in zip(OPTIONS, BUILDS):
        (HERE / fname).write_text(page(fname, name, blurb, css, main, cls))
        print("wrote", fname)

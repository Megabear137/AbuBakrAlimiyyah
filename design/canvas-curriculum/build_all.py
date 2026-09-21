#!/usr/bin/env python3
"""Build all.html: the curriculum mockups still in the running, on one page.

The source pages listed in PAGES (index, modern, shelf) each carry
their own <style> and script, and reuse class names (.chip, .cover, .seg,
.road ...) with different definitions. So each page's CSS is scoped under a
wrapper class (.pg-<name>), its @keyframes renamed with that suffix, and its
script's data-mock / data-pile lookups limited to its own wrapper. The
per-page header, mode switch and foot-note are dropped for one of each, and
the options named in PAGES' skip sets are left out.

Edit the source pages, then rerun:  python3 build_all.py
"""
import re
from pathlib import Path

HERE = Path(__file__).parent

PAGES = [
    # (source page, part title, lede, ids of its options left out of all.html)
    ("index", "Round 1",
     "Your cover carousel and pile, and three other ways to show the seven years' books.", {"m4"}),
    ("modern", "Modern patterns",
     "Three current interface patterns in the site's brown and gold.", {"iii"}),
    ("shelf", "The shelf · One year at a time",
     "The live bookshelf cut into single years, unframed, on a wooden support.", set()),
]
# Dropped from all.html but kept as a record: pile.html and pile-islamic.html
# (the pile's spine variants A-H), round 1's Syllabus grid and Modern III, Library.


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def block_end(css, i):
    """Index just past the brace that closes the block opened at css[i] == '{'."""
    depth, q = 0, None
    while i < len(css):
        c = css[i]
        if q:
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced CSS")


def split_selectors(prelude):
    out, depth, cur = [], 0, ""
    for c in prelude:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if c == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += c
    out.append(cur)
    return [s.strip() for s in out if s.strip()]


def scope_selector(sel, cls):
    if sel.startswith("::view-transition"):
        return sel
    if sel.startswith(":root"):
        return "." + cls + sel[5:]
    m = re.match(r'(\[data-theme="dark"\])\s*(.*)$', sel, re.S)
    if m:
        return (m.group(1) + " ." + cls + (" " + m.group(2) if m.group(2) else "")).strip()
    return "." + cls + " " + sel


def scope_css(css, cls):
    out, i = [], 0
    while i < len(css):
        j = css.find("{", i)
        if j < 0:
            break
        prelude = css[i:j].strip()
        end = block_end(css, j)
        body = css[j + 1:end - 1]
        if prelude.startswith("@media") or prelude.startswith("@supports"):
            out.append(prelude + " {\n" + scope_css(body, cls) + "}\n")
        elif prelude.startswith("@"):
            out.append(prelude + " {" + body + "}\n")
        else:
            sels = ",\n".join(scope_selector(s, cls) for s in split_selectors(prelude))
            out.append(sels + " {" + body + "}\n")
        i = end
    return "".join(out)


def between(text, start, end):
    a = text.index(start) + len(start)
    return text[a:text.index(end, a)]


def page_parts(name, skip=()):
    html = (HERE / (name + ".html")).read_text()
    cls = "pg-" + name
    css = strip_comments(between(html, "<style>", "</style>"))
    # Keyframe names are global: give each page its own.
    for kf in set(re.findall(r"@keyframes\s+([\w-]+)", css)):
        css = re.sub(r"\b" + re.escape(kf) + r"\b", kf + "-" + name, css)
    css = scope_css(css, cls)

    main = between(html, "<main>", "</main>")
    main = re.sub(r'\s*<p class="foot-note">.*?</p>', "", main, flags=re.S)
    for sid in skip:
        main, n = re.subn(r'\s*<section class="mock" id="' + sid + r'">.*?</section>', "", main, count=1, flags=re.S)
        assert n == 1, "no option " + sid + " in " + name
    tail = html[html.index("</main>"):]
    dialogs = "".join(re.findall(r"<dialog\b.*?</dialog>", tail, re.S))

    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    js = scripts[-1]          # the first is the head's theme choice
    js = js.replace('document.querySelectorAll("[data-mock]")', 'document.querySelectorAll(".' + cls + ' [data-mock]")')
    js = js.replace('document.querySelectorAll("[data-pile]")', 'document.querySelectorAll(".' + cls + ' [data-pile]")')
    js = js.replace('document.querySelector("main")', 'document.querySelector(".' + cls + '")')
    return cls, css, main, dialogs, js


def option_links(main):
    """(id, label) for each mock section, from its number and title."""
    out = []
    for m in re.finditer(r'<section class="mock" id="([\w-]+)">.*?<span class="mock__num">(.*?)</span>.*?<h2 class="mock__title">(.*?)(?:<small>|</h2>)', main, re.S):
        out.append((m.group(1), m.group(2) + " · " + re.sub(r"<.*?>", "", m.group(3)).strip()))
    return out


def build():
    head = (HERE / "index.html").read_text()
    theme_script = re.findall(r"<script>(.*?)</script>", head, re.S)[0]
    fonts = re.search(r'<link href="https://fonts.googleapis.com/css2[^>]+>', head).group(0)

    styles, bodies, dialogs, scripts, nav = [], [], [], [], []
    for n, (name, title, lede, skip) in enumerate(PAGES):
        cls, css, main, dlg, js = page_parts(name, skip)
        styles.append("/* ======== " + name + ".html ======== */\n" + css)
        links = option_links(main)
        nav.append('<div class="all-nav__group"><a class="all-nav__round" href="design/canvas-curriculum/all.html#' + cls + '">' + title + "</a>" +
                   "".join('<a href="design/canvas-curriculum/all.html#' + i + '">' + l + "</a>" for i, l in links) + "</div>")
        bodies.append(
            '<div class="' + cls + ' all-group" id="' + cls + '">\n'
            '<header class="wrap all-round"><p class="all-round__n">Part ' + str(n + 1) + " of " + str(len(PAGES)) + '</p><h2 class="all-round__title">' + title +
            '</h2><p class="all-round__lede">' + lede + ' <a href="design/canvas-curriculum/' + name + '.html">Open on its own</a></p></header>\n' +
            main + "\n" + dlg + "\n</div>")
        scripts.append("<script>/* " + name + ".html */" + js + "</script>")

    total = sum(len(option_links(page_parts(p[0], p[3])[2])) for p in PAGES)
    page = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Generated by build_all.py from index, modern and shelf.html. Edit those and rerun. -->
<base href="../../">
<title>Curriculum, the options — mockups</title>
<script>""" + theme_script + """</script>
<link rel="icon" href="assets/img/logo_gold_web.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
""" + fonts + """
<link rel="stylesheet" href="assets/css/styles.css?v=37">
<style>
/* The combined page's own chrome */
.all-head { padding: 4.5rem 0 1rem; text-align: center; }
.all-head h1 { font-family: var(--title); font-weight: 400; font-size: clamp(2.2rem, 1.4rem + 3vw, 3.8rem); letter-spacing: 0.1em; text-transform: uppercase; line-height: 1.05; background: var(--g-title); -webkit-background-clip: text; background-clip: text; color: transparent; margin-top: 0.8rem; }
.all-head > p { max-width: 660px; margin: 1rem auto 0; color: var(--g-muted); font-family: var(--display); font-style: italic; font-size: 1.2rem; }
.all-nav { display: grid; gap: 10px; max-width: 1000px; margin: 2rem auto 0; text-align: left; }
.all-nav__group { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.all-nav a { padding: 0.35rem 0.85rem; border-radius: 999px; border: 1px solid var(--g-line); color: var(--g-text); font-size: 0.76rem; font-weight: 500; text-decoration: none; white-space: nowrap; }
.all-nav a:hover { border-color: var(--g-accent); color: var(--g-accent); }
.all-nav .all-nav__round { border: 0; padding-left: 0; min-width: 210px; font-family: var(--display); font-size: 1.05rem; font-weight: 600; color: var(--g-accent); }
.all-group { padding-top: clamp(3rem, 6vw, 5rem); }
.all-round { margin-top: clamp(2rem, 4vw, 3rem); padding: 2.4rem 0 0; border-top: 4px solid var(--gold-ink); text-align: center; }
[data-theme="dark"] .all-round { border-top: 1px solid var(--gold); }
.all-round__n { color: var(--g-accent); font-size: 0.66rem; font-weight: 600; letter-spacing: 0.4em; text-transform: uppercase; }
.all-round__title { margin-top: 0.6rem; font-family: var(--title); font-weight: 400; font-size: clamp(1.8rem, 1.2rem + 2vw, 2.8rem); letter-spacing: 0.08em; text-transform: uppercase; background: var(--g-title); -webkit-background-clip: text; background-clip: text; color: transparent; }
.all-round__lede { max-width: 620px; margin: 0.6rem auto 0; color: var(--g-muted); font-family: var(--display); font-style: italic; font-size: 1.15rem; }
.all-foot { padding: 5rem 0 6rem; text-align: center; color: var(--g-muted); font-family: var(--display); font-style: italic; }
.mode-switch { position: fixed; right: 16px; bottom: 16px; z-index: 60; display: flex; padding: 4px; border-radius: 999px; background: rgba(26, 13, 4, 0.82); border: 1px solid rgba(227, 179, 74, 0.35); backdrop-filter: blur(6px); }
.mode-switch button { padding: 0.45rem 1rem; border-radius: 999px; color: var(--gold-pale); font-size: 0.72rem; font-weight: 600; letter-spacing: 0.16em; text-transform: uppercase; }
.mode-switch button[aria-pressed="true"] { background: linear-gradient(180deg, #f3cf6e, #d49a2a); color: var(--espresso); }
@media (max-width: 640px) { .all-nav .all-nav__round { min-width: 100%; } }

""" + "\n".join(styles) + """
</style>
</head>
<body>

<div class="mode-switch" role="group" aria-label="Mockup mode">
  <button type="button" data-mode="light">Light</button>
  <button type="button" data-mode="dark">Dark</button>
</div>

<header class="wrap all-head">
  <p class="section__eyebrow">Curriculum</p>
  <h1>The options</h1>
  <p>All """ + str(total) + """ ways to replace the bookshelf, in """ + str(len(PAGES)) + """ parts, on one page. Everything reads content/curriculum.json and works as it does on its own page.</p>
  <nav class="all-nav" aria-label="Options">""" + "".join(nav) + """</nav>
</header>

<main>
""" + "\n".join(bodies) + """
</main>

<p class="all-foot">Only Second Year holds real books; the rest are the JSON's placeholders.</p>

<script src="assets/js/curriculum.js?v=7"></script>
""" + "\n".join(scripts) + """
</body>
</html>
"""
    (HERE / "all.html").write_text(page)
    print("wrote all.html:", total, "options")


if __name__ == "__main__":
    build()

#!/usr/bin/env python3
"""The bookstore's filters: six ways to choose books by year and subject
without bookstore.html's three rows of pills (8 by year, 19 by subject).

Each mockup is bookstore.html itself - the site's styles, header, footer and
its own bookstore.js drawing the real grid from content/bookstore.json - with
the pills hidden and an option's controls in their place (mock.js, mock.css).
They work: choose and the grid narrows. A `<base href="../../">` lets them
run from here, so serve the repository root and open
http://127.0.0.1:8000/design/canvas-filters/

What every option keeps: the same two filters, narrowing together; the
count beside a choice is what it would show given the other filter, and a
choice with none is greyed. No new copy beyond control labels, no stars.

   1. Numerals & menu  - one line: the years as a segmented bar of numerals,
                         the subjects in one menu beside it.
   2. Two menus        - a slim bar of two menus ("Year", "Subject"), the
                         choices as removable tokens, the count on the right.
   3. Sentence         - no bar at all: the heading tile says what is shown,
                         "67 books from every year, in every subject", and
                         each phrase opens its menu.
   4. Year tabs        - the years as large numerals like the shelf's year
                         labels; under them only the subjects of that year,
                         as plain words.
   5. Contents         - a fihrist down the left: years and subjects as a
                         table of contents with dotted leaders to the counts.
   6. Subject families - years as the numeral bar; the 18 subjects folded
                         into five groups, a group's subjects shown once it
                         is picked. (The grouping is a proposal.)

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

OPTIONS = []


def option(slug, name, blurb, main, css, js):
    OPTIONS.append(dict(slug=slug, name=name, blurb=blurb, main=main, css=css, js=js))


STORE = '<div class="store-chips" data-slot="bookstore-filters" hidden></div>\n      <div class="store" data-slot="bookstore"></div>'
BACK = '<a class="back" href="index.html#bookstore"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg> Home</a>'
PLAIN = BACK + '\n      <div id="mock-filter"></div>\n      ' + STORE

# ---------------------------------------------------------------- 1
option("1-numerals", "Numerals & menu",
       "One line. The years become a segmented bar of numerals (I to VII, with All), the subjects go into a single menu beside it, two columns, each with its count.",
       PLAIN,
       """
#mock-filter { display: flex; flex-wrap: wrap; align-items: end; gap: 1.2rem 2rem; margin: 0 0 1.6rem; }
#mock-filter .mm__btn { height: calc(2.5rem + 8px); }
@media (max-width: 560px) { #mock-filter .mm, #mock-filter .mm__btn { width: 100%; justify-content: space-between; } #mock-filter > div:last-child { flex: 1 1 100%; } }
""",
       """
MockFilter(function (api) {
  var m = document.getElementById("mock-filter"); m.textContent = "";
  var a = api.el("div", "", '<span class="mf-label">Year</span>'); a.appendChild(api.seg());
  var b = api.el("div", "", '<span class="mf-label">Subject</span>'); b.appendChild(api.subjectMenu());
  m.appendChild(a); m.appendChild(b);
});
""")

# ---------------------------------------------------------------- 2
option("2-menus", "Two menus",
       "A slim bar between two hairlines: two menus, Year and Subject. What is chosen shows as a token with a cross, with Clear; the number shown sits on the right.",
       PLAIN,
       """
#mock-filter { display: flex; flex-wrap: wrap; align-items: center; gap: 0.6rem; margin: 0 0 1.6rem; padding: 0.8rem 0; border-block: 1px solid var(--g-line); }
#mock-filter .mm__btn { height: 2.6rem; box-shadow: none; padding: 0 0.9rem; }
#mock-filter .mm__btn:hover, #mock-filter .mm--open .mm__btn { box-shadow: none; background: rgba(70, 44, 22, 0.07); }
[data-theme="dark"] #mock-filter .mm__btn:hover, [data-theme="dark"] #mock-filter .mm--open .mm__btn { background: rgba(255, 236, 210, 0.07); }
.m2__lead { margin-right: 0.2rem; color: var(--g-accent); font: 600 0.6rem var(--sans); letter-spacing: 0.26em; text-transform: uppercase; }
.m2__tok { display: inline-flex; align-items: center; gap: 0.45rem; height: 2rem; padding: 0 0.55rem 0 0.85rem; border: 0; border-radius: 999px; background: var(--brown-ink); color: #fbeedd; font: 500 0.75rem var(--sans); cursor: pointer; }
.m2__tok svg { width: 10px; height: 10px; opacity: 0.75; }
[data-theme="dark"] .m2__tok { background: var(--gold); color: var(--espresso); }
.m2__clear { border: 0; background: none; color: var(--g-muted); font: 500 0.75rem var(--sans); text-decoration: underline; text-underline-offset: 3px; cursor: pointer; }
.m2__count { margin-left: auto; color: var(--g-muted); font-size: 0.8rem; }
.m2__count b { color: var(--g-text); font-family: var(--display); font-size: 1.35rem; font-weight: 600; }
.m2__sep { width: 1px; height: 1.4rem; background: var(--g-line); }
""",
       """
var X = '<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M2 2l6 6M8 2 2 8" stroke="currentColor" stroke-width="1.5"/></svg>';
MockFilter(function (api) {
  var m = document.getElementById("mock-filter"); m.textContent = "";
  m.appendChild(api.el("span", "m2__lead", "Filter"));
  m.appendChild(api.yearMenu({ button: function () { return "Year"; } }));
  m.appendChild(api.subjectMenu({ button: function () { return "Subject"; } }));
  if (api.active()) {
    m.appendChild(api.el("span", "m2__sep"));
    [["year", api.state.year], ["subject", api.state.subject]].forEach(function (p) {
      if (!p[1]) return;
      var t = api.el("button", "m2__tok", api.esc(p[1]) + X);
      t.type = "button"; t.setAttribute("aria-label", "Remove " + p[1]);
      t.addEventListener("click", function () { var o = {}; o[p[0]] = ""; api.set(o); });
      m.appendChild(t);
    });
    var c = api.el("button", "m2__clear", "Clear"); c.type = "button";
    c.addEventListener("click", function () { api.set({ year: "", subject: "" }); });
    m.appendChild(c);
  }
  m.appendChild(api.el("span", "m2__count", "<b>" + api.shown() + "</b> of " + api.books.length + " books"));
});
""")

# ---------------------------------------------------------------- 3
option("3-sentence", "Sentence",
       "No bar at all. The heading tile already counts the books; the line under the count says what is shown, “from every year, in every subject”, and each phrase opens its menu.",
       BACK + '\n      ' + STORE,
       """
.store-name { position: relative; z-index: 3; }
.store-page .back { margin-bottom: 1.8rem; }
.m3 { margin-top: 0.4rem; color: var(--g-muted); font-family: var(--display); font-size: clamp(1.25rem, 1rem + 0.8vw, 1.6rem); font-style: italic; line-height: 1.5; }
.m3 .mm__btn { height: auto; padding: 0 0.1rem; border-radius: 0; box-shadow: none; background: none; color: var(--g-text); font: inherit; font-style: normal; font-weight: 600; border-bottom: 1.5px dashed var(--rust); gap: 0.3rem; }
.m3 .mm__btn:hover, .m3 .mm--open .mm__btn { box-shadow: none; border-bottom-style: solid; }
[data-theme="dark"] .m3 .mm__btn { border-bottom-color: var(--gold); }
.m3 .mm__caret { width: 10px; height: 10px; color: var(--rust); }
[data-theme="dark"] .m3 .mm__caret { color: var(--gold); }
.m3 .mm__pop { font-style: normal; line-height: 1.2; }
.m3__reset { margin-left: 0.6rem; border: 0; background: none; color: var(--g-accent); font: 600 0.6rem var(--sans); font-style: normal; letter-spacing: 0.2em; text-transform: uppercase; cursor: pointer; vertical-align: middle; }
.store-name__foot { flex-direction: column; align-items: start; gap: 0; }
""",
       """
function draw(api) {
  var foot = document.querySelector(".store-name__foot");
  if (!foot) return;
  var old = foot.querySelector(".m3"); if (old) old.remove();
  var p = api.el("p", "m3");
  var s = api.state;
  p.append(s.year ? "from the " : "from ");
  p.appendChild(api.yearMenu({ all: "Every year", button: function (v) { return v || "every year"; } }));
  p.append(", in ");
  p.appendChild(api.subjectMenu({ all: "Every subject", button: function (v) { return v || "every subject"; } }));
  p.append(".");
  if (api.active()) {
    var r = api.el("button", "m3__reset", "Show all"); r.type = "button";
    r.addEventListener("click", function () { api.set({ year: "", subject: "" }); });
    p.appendChild(r);
  }
  foot.appendChild(p);
}
MockFilter(draw, { onGrid: draw });
""")

# ---------------------------------------------------------------- 4
option("4-year-tabs", "Year tabs",
       "The year leads. Seven large numerals, like the shelf's year labels, each with its count, the chosen one underlined in brown. Beneath, only that year's subjects, as plain words rather than pills.",
       PLAIN,
       """
#mock-filter { margin: 0 0 1.8rem; }
.m4__years { display: flex; gap: clamp(0.4rem, 2vw, 1.6rem); overflow-x: auto; border-bottom: 1px solid var(--g-line); scrollbar-width: none; }
.m4__y { position: relative; flex: none; display: grid; justify-items: center; gap: 0.15rem; padding: 0.2rem 0.6rem 0.9rem; border: 0; background: none; color: var(--g-muted); cursor: pointer; }
.m4__y b { font: 400 clamp(1.6rem, 1.2rem + 1.4vw, 2.4rem) var(--title); letter-spacing: 0.04em; line-height: 1; color: var(--g-text); opacity: 0.55; transition: opacity 0.2s; }
.m4__y--all b { font: 500 clamp(1.1rem, 0.9rem + 0.8vw, 1.5rem) var(--display); font-style: italic; padding-top: 0.25em; }
.m4__y small { font: 500 0.62rem var(--sans); letter-spacing: 0.14em; text-transform: uppercase; }
.m4__y:hover b { opacity: 0.85; }
.m4__y[aria-pressed="true"] b { opacity: 1; }
.m4__y[aria-pressed="true"] { color: var(--g-text); }
.m4__y[aria-pressed="true"]::after { content: ""; position: absolute; left: 0.3rem; right: 0.3rem; bottom: -1px; height: 3px; border-radius: 3px 3px 0 0; background: var(--brown-ink); }
[data-theme="dark"] .m4__y[aria-pressed="true"]::after { background: var(--gold); }
[data-theme="dark"] .m4__y[aria-pressed="true"] b { color: var(--gold-pale); }
.m4__subs { display: flex; flex-wrap: wrap; gap: 0.3rem 1.3rem; margin-top: 1rem; }
.m4__s { padding: 0.2rem 0; border: 0; border-bottom: 1.5px solid transparent; background: none; color: var(--g-muted); font: 400 0.85rem var(--sans); cursor: pointer; }
.m4__s i { margin-left: 0.25rem; font-size: 0.68rem; font-style: normal; opacity: 0.7; }
.m4__s:hover { color: var(--g-text); }
.m4__s[aria-pressed="true"] { color: var(--g-text); font-weight: 600; border-bottom-color: var(--rust); }
[data-theme="dark"] .m4__s[aria-pressed="true"] { border-bottom-color: var(--gold); }
""",
       """
MockFilter(function (api) {
  var m = document.getElementById("mock-filter"); m.textContent = "";
  var ys = api.el("div", "m4__years"); ys.setAttribute("role", "group"); ys.setAttribute("aria-label", "Year");
  [""].concat(api.years).forEach(function (y) {
    var n = api.count({ year: y, subject: "" });
    var b = api.el("button", "m4__y" + (y ? "" : " m4__y--all"), "<b>" + (y ? api.roman(y) : "All") + "</b><small>" + n + " books</small>");
    b.type = "button"; b.title = y || "Every year";
    b.setAttribute("aria-pressed", String(y === api.state.year));
    b.addEventListener("click", function () { api.set({ year: y, subject: "" }); });
    ys.appendChild(b);
  });
  m.appendChild(ys);
  var ss = api.el("div", "m4__subs"); ss.setAttribute("role", "group"); ss.setAttribute("aria-label", "Subject");
  [""].concat(api.subjects).forEach(function (s) {
    var n = api.count({ subject: s });
    if (!n) return;
    var b = api.el("button", "m4__s", api.esc(s || "All subjects") + "<i>" + n + "</i>");
    b.type = "button";
    b.setAttribute("aria-pressed", String(s === api.state.subject));
    b.addEventListener("click", function () { api.set({ subject: s }); });
    ss.appendChild(b);
  });
  m.appendChild(ss);
});
""")

# ---------------------------------------------------------------- 5
option("5-contents", "Contents",
       "A fihrist down the left, sticky as the page scrolls: Year and Subject as a table of contents, dotted leaders running to each count. On phones it folds into one Filter button above the grid.",
       BACK + '\n      <div class="m5"><aside class="m5__side"><button class="m5__toggle" type="button" aria-expanded="false"></button><div id="mock-filter"></div></aside>\n      <div>' + STORE + '</div></div>',
       """
.m5 { display: grid; grid-template-columns: 210px minmax(0, 1fr); gap: 2.4rem; align-items: start; }
.m5__side { position: sticky; top: 1.5rem; max-height: calc(100vh - 3rem); overflow: auto; padding-right: 0.4rem; scrollbar-width: thin; }
.m5 .store { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.m5__toggle { display: none; }
.m5__h { margin: 0 0 0.5rem; color: var(--g-accent); font: 600 0.6rem var(--sans); letter-spacing: 0.26em; text-transform: uppercase; }
.m5__group + .m5__group { margin-top: 1.8rem; }
.m5__list { display: grid; }
.m5__i { position: relative; display: flex; align-items: baseline; width: 100%; padding: 0.32rem 0 0.32rem 0.8rem; border: 0; background: none; color: var(--g-text); font: 400 0.84rem var(--sans); text-align: left; cursor: pointer; }
.m5__i::after { content: ""; order: 1; flex: 1; min-width: 0.8rem; margin: 0 0.4rem; border-bottom: 1px dotted var(--g-dash); }
.m5__i i { order: 2; color: var(--g-muted); font-size: 0.72rem; font-style: normal; }
.m5__i:hover:not(:disabled) { color: var(--rust-ink); }
.m5__i[aria-pressed="true"] { font-weight: 600; }
.m5__i[aria-pressed="true"]::before { content: ""; position: absolute; left: 0; top: 0.45rem; bottom: 0.45rem; width: 2px; border-radius: 2px; background: var(--rust); }
.m5__i:disabled { opacity: 0.35; cursor: default; }
[data-theme="dark"] .m5__i:hover:not(:disabled) { color: var(--gold); }
[data-theme="dark"] .m5__i[aria-pressed="true"] { color: var(--gold-pale); }
[data-theme="dark"] .m5__i[aria-pressed="true"]::before { background: var(--gold); }
@media (max-width: 1100px) { .m5 .store { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 980px) {
  .m5 { grid-template-columns: minmax(0, 1fr); gap: 1.2rem; }
  .m5__side { position: static; max-height: none; overflow: visible; }
  .m5__toggle { display: flex; align-items: center; justify-content: space-between; width: 100%; height: 3.2rem; padding: 0 1.2rem; border: 0; border-radius: 999px; background: none; box-shadow: inset 0 0 0 1px var(--g-line); color: var(--g-text); font: 500 0.82rem var(--sans); cursor: pointer; }
  .m5__toggle span { color: var(--g-muted); font-weight: 400; }
  .m5__side:not(.is-open) #mock-filter { display: none; }
  .m5__side.is-open #mock-filter { display: grid; grid-template-columns: 1fr 1fr; gap: 0 1.6rem; margin-top: 1rem; }
  .m5__side.is-open .m5__h { margin-top: 0; }
}
@media (max-width: 560px) { .m5 .store { grid-template-columns: minmax(0, 1fr); } .m5__side.is-open #mock-filter { grid-template-columns: 1fr; } .m5__side.is-open .m5__group + .m5__group { margin-top: 1.4rem; } }
""",
       """
var side = document.querySelector(".m5__side"), tog = document.querySelector(".m5__toggle");
tog.addEventListener("click", function () { var o = side.classList.toggle("is-open"); tog.setAttribute("aria-expanded", String(o)); });
MockFilter(function (api) {
  var m = document.getElementById("mock-filter"); m.textContent = "";
  var s = api.state;
  tog.innerHTML = "Filter <span>" + api.esc([s.year, s.subject].filter(Boolean).join(" · ") || "All books") + " · " + api.shown() + "</span>";
  function group(title, key, all, values) {
    var g = api.el("div", "m5__group");
    g.appendChild(api.el("p", "m5__h", title));
    var l = api.el("div", "m5__list"); l.setAttribute("role", "group"); l.setAttribute("aria-label", title);
    [""].concat(values).forEach(function (v) {
      var o = {}; o[key] = v; var n = api.count(o);
      var b = api.el("button", "m5__i", "<span>" + api.esc(v || all) + "</span><i>" + n + "</i>");
      b.type = "button";
      b.setAttribute("aria-pressed", String(v === s[key]));
      if (!n && v !== s[key]) b.disabled = true;
      b.addEventListener("click", function () { api.set(o); });
      l.appendChild(b);
    });
    g.appendChild(l);
    m.appendChild(g);
  }
  group("Year", "year", "All years", api.years);
  group("Subject", "subject", "All subjects", api.subjects);
});
""")

# ---------------------------------------------------------------- 6
option("6-families", "Subject families",
       "Years as the numeral bar of option 1. The eighteen subjects fold into five groups (Language, Qur'an, Hadith, Fiqh, Other); a group's own subjects open beneath it once it is picked. The grouping is a proposal for the masjid to agree.",
       PLAIN,
       """
#mock-filter { display: grid; gap: 1.1rem; margin: 0 0 1.8rem; }
.m6__fams { display: flex; flex-wrap: wrap; gap: 0.2rem 1.6rem; }
.m6__f { padding: 0.1rem 0 0.35rem; border: 0; border-bottom: 2px solid transparent; background: none; color: var(--g-muted); font: 500 1.35rem var(--display); cursor: pointer; }
.m6__f i { margin-left: 0.3rem; font: 400 0.7rem var(--sans); font-style: normal; opacity: 0.7; vertical-align: 0.35em; }
.m6__f:hover:not(:disabled) { color: var(--g-text); }
.m6__f[aria-pressed="true"] { color: var(--g-text); font-weight: 600; border-bottom-color: var(--rust); }
.m6__f:disabled { opacity: 0.35; cursor: default; }
[data-theme="dark"] .m6__f[aria-pressed="true"] { border-bottom-color: var(--gold); color: var(--gold-pale); }
.m6__subs { display: flex; flex-wrap: wrap; gap: 0.4rem; padding: 0.7rem; border-radius: 18px; background: rgba(70, 44, 22, 0.06); }
[data-theme="dark"] .m6__subs { background: rgba(255, 236, 210, 0.05); }
.m6__subs .store-chip { padding: 0.45rem 0.9rem; }
.m6__subs .store-chip:disabled { opacity: 0.35; cursor: default; }
""",
       """
MockFilter(function (api) {
  var m = document.getElementById("mock-filter"); m.textContent = "";
  var s = api.state;
  var a = api.el("div", "", '<span class="mf-label">Year</span>'); a.appendChild(api.seg()); m.appendChild(a);
  var fams = api.FAMILIES.map(function (f) { return f[0]; }).filter(function (f) {
    return api.subjects.some(function (x) { return api.familyOf(x) === f; });
  });
  var b = api.el("div", "", '<span class="mf-label">Subject</span>');
  var row = api.el("div", "m6__fams"); row.setAttribute("role", "group"); row.setAttribute("aria-label", "Subject");
  [""].concat(fams).forEach(function (f) {
    var n = api.count({ family: f, subject: "" });
    var btn = api.el("button", "m6__f", api.esc(f || "All") + "<i>" + n + "</i>");
    btn.type = "button";
    btn.setAttribute("aria-pressed", String(f === s.family));
    if (!n && f !== s.family) btn.disabled = true;
    btn.addEventListener("click", function () { api.set({ family: f, subject: "" }); });
    row.appendChild(btn);
  });
  b.appendChild(row); m.appendChild(b);
  if (s.family) {
    var subs = api.subjects.filter(function (x) { return api.familyOf(x) === s.family; });
    if (subs.length > 1) {
      var w = api.el("div", "m6__subs"); w.setAttribute("role", "group"); w.setAttribute("aria-label", s.family);
      [""].concat(subs).forEach(function (x) {
        var n = api.count({ subject: x });
        var c = api.el("button", "store-chip", api.esc(x || "All " + s.family) + "<sup>" + n + "</sup>");
        c.type = "button";
        c.setAttribute("aria-pressed", String(x === s.subject));
        if (!n && x !== s.subject) c.disabled = true;
        c.addEventListener("click", function () { api.set({ subject: x }); });
        w.appendChild(c);
      });
      m.appendChild(w);
    }
  }
});
""")


PAGE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="../../">
  <title>Bookstore filters · {num}. {name}</title>
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
  <link rel="stylesheet" href="design/canvas-filters/mock.css">
<!-- Filters, option {num}: {name}. {blurb} Generated by design/canvas-filters/generate.py. -->
<style>{css}</style>
</head>
<body id="top" class="on-ground">

{header}
<main id="main">
  <section class="section store-page" aria-labelledby="bookstore-heading">
    <div class="wrap">
      {main}
    </div>
  </section>
</main>

{footer}
{scripts}<script src="design/canvas-filters/mock.js"></script>
<script>
{js}</script>
<p class="mock-tag"><a href="design/canvas-filters/{prev}">&larr;</a> Option {num} &middot; {name} <a href="design/canvas-filters/index.html">All</a> <a href="design/canvas-filters/{next}">&rarr;</a></p>
</body>
</html>
"""

INDEX = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="../../">
  <title>Bookstore filters · six options</title>
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
  <h1>Bookstore filters</h1>
  <p>Six ways to choose books by year and subject without the three rows of pills. Each is the real bookstore page and works: pick and the grid narrows. The site's light/dark toggle is in each page's corner.</p>
  <ol>
{items}
  </ol>
  <p class="now">For comparison: <a href="bookstore.html">the bookstore as it is now</a>.</p>
</div></main>
</body>
</html>
"""


def main():
    n = len(OPTIONS)
    items = []
    for k, o in enumerate(OPTIONS):
        num = k + 1
        out = HERE / (o["slug"] + ".html")
        out.write_text(PAGE.format(
            num=num, name=o["name"], blurb=o["blurb"], head=HEAD_LINKS.strip(), css=o["css"],
            header=HEADER.strip(), main=o["main"], footer=FOOTER.strip(), scripts=SCRIPTS, js=o["js"],
            prev=OPTIONS[(k - 1) % n]["slug"] + ".html", next=OPTIONS[(k + 1) % n]["slug"] + ".html",
        ), encoding="utf-8")
        items.append('    <li><a href="design/canvas-filters/%s.html"><b><span>%s</span>%s</b><p>%s</p></a></li>'
                     % (o["slug"], ["I", "II", "III", "IV", "V", "VI"][k], o["name"], o["blurb"]))
        print("wrote", out.name)
    (HERE / "index.html").write_text(INDEX.format(head=HEAD_LINKS.strip(), items="\n".join(items)), encoding="utf-8")
    print("wrote index.html")


if __name__ == "__main__":
    main()

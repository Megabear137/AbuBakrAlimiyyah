# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static informational website for the seven-year Alimiyyah program at Jamiyah Islamiyyah Abu Bakr
(a masjid). Plain HTML/CSS/vanilla JS — **no build step, no dependencies, no framework, no tests, no
package.json**.

Note: the repo lives on a WSL path accessed from Windows, so `git` may refuse it with "dubious
ownership". Fix with `git config --global --add safe.directory '%(prefix)///wsl.localhost/Ubuntu/home/zubai/projects/alimiyyah_website'`.

It may gain online enrolment/payment later, which is why content is data-driven rather than hardcoded.

## Running it

```sh
python3 -m http.server 8000     # then open http://localhost:8000
```

**A server is mandatory.** The page `fetch`es `content/*.json`, which browsers block on `file://` —
double-clicking `index.html` shows an error banner instead of the site. Any static server works.

There is nothing to build, lint or test. Deployment is uploading the folder as-is.

## The mockup is the specification

`design/wesbite_design.png` is the authoritative design. **Measure it, don't eyeball it** — colours and
border spacing have been matched to the pixel, and eyeballing has already produced wrong results once.

Two things to know about that file:

- It contains **two artboards side by side**: the main page occupies x `0–1465`, and a second artboard
  at x `>1660` shows the curriculum accordion with Second Year expanded.
- The page artboard renders at ~1465 px wide, so **mockup pixels map ~1:1 to CSS pixels** at a 1465px
  viewport. Render at that width to compare like for like.

Pixel-scan it with PIL rather than guessing:

```sh
python -c "
from PIL import Image
im = Image.open('design/wesbite_design.png').convert('RGB')
prev = None
for x in range(130, 260):
    p = im.getpixel((x, 1450))
    if p != prev: print(x, p); prev = p
"
```

## Architecture

### Content is data, markup is a shell

`index.html` contains no copy, no book lists, no teacher names. It provides empty elements tagged
`data-slot="…"`; `assets/js/main.js` fetches the four `content/*.json` files and fills them in. Adding a
book, teacher, testimony or price is a JSON edit only.

Changing what is displayed therefore usually means editing **both** the JSON shape and the matching
render function in `main.js` — not the HTML.

### Script load order matters

`carousel.js` and `curriculum.js` attach exactly one global each and must load before `main.js`, which
calls them:

- `carousel.js` → `window.createCarousel({mount, items, render, perView, label})`
- `curriculum.js` → `window.renderCurriculum(mountEl, data)`
- `nav.js` is self-contained (mobile drawer + IntersectionObserver scrollspy)

One carousel implementation serves both Teachers and Alumni; they differ only in the `render` callback
and the `perView` breakpoint function. It pages by whole screenfuls, sizes slides in px from a measured
viewport (so it re-layouts on resize and on `document.fonts.ready`), and sets `tabindex="-1"` on
off-screen slides to keep them out of the tab order.

### Reusable visual motifs in `styles.css`

The stylesheet is one file, numbered and commented by section. Four motifs recur; prefer extending them
over inventing new border treatments:

- **`.gilt`** — the signature double border: two gold hairlines with green showing *outside* the pair and
  between them, never flush with the edge. Implemented as four stacked `inset` box-shadows; shadows paint
  front-to-back, so each narrower ring masks the wider one behind it. Tune per element via
  `--gilt-inset` (green before the outer line), `--gilt-gap`, `--gilt-line`, and `--gilt-drop` (an outer
  drop shadow, which has to ride along because one element cannot have two `box-shadow` declarations).
  Current values, all measured from the mockup: panels `10px/5px`, teacher cards `17px/10px`,
  testimony cards `14px/6px`.
- **`.tabbed`** — a gold-outlined pill straddling the top edge of a panel. The pill carries the green
  background and a higher `z-index` so it masks the panel's rings behind it.
- **`.arch`** — mihrab card. `border-radius: 9999px 9999px 0 0` deliberately over-specifies the radii so
  CSS scales them down to exactly half the width, giving a true semicircular top at any size. Unlike the
  panels and cards, the arch has a **single** gold line (`.arch::before`, `inset: 14px`) — that matches
  the mockup, which shows one line at 24px.
- **`.stripe`** — the stacked gold lines under teacher and testimony cards, a single `linear-gradient`.

Colour tokens in `:root` were sampled from the mockup: `--green #134528`, `--green-deep #062707`,
`--gold #c9a961`, `--gold-light #d9be78`, `--mint #c9ebdd`.

**`--ground` vs `--paper` — do not conflate them.** `--ground #f5eee0` is the page; `--paper #ffffff`
is only ink-on-green (nav links, card body copy, the hamburger bars). The mockup's white page was
replaced by an aged-leaf ground chosen from a later design round.

### The page ground and the divider

Both are later additions, and neither is in `wesbite_design.png` — the mockup shows a plain white page
and a plain green rule. Don't "restore" them to match it.

- **The ground** is seven stacked `background-image` layers on `body`, topmost first: grain, two edge
  shadings, two gold-fleck (zarafshan) tiles, two age-bloom (foxing) tiles. The tiles live as real
  files in `assets/img/ground-*.svg` rather than data URIs, so they stay editable in a no-build project.
  Two details are load-bearing: the flecks use **two coprime tile sizes** (317px and 523px) at natural
  scale and the blooms reuse **one tile at two sizes with an offset**, because a single tile shows an
  obvious repeat down a 5000px page. The edge shading is horizontal only — a top/bottom vignette
  implies a page that ends, which an infinite scroll does not.
- **The divider** is a gold khatim medallion (`assets/img/divider-khatim.svg`) between hairlines that
  fade out at the outer ends. It is drawn entirely in `background` layers so the markup stays a plain
  `<hr class="rule">`; the two rules are each `calc(50% - 40px)` wide so nothing is drawn behind the
  medallion.
- **The hero uses `mix-blend-mode: multiply`** because the placeholder photo was cropped from the
  mockup and has a fade to *white* baked into its edges. Multiplying against the cream ground maps that
  white back onto the page exactly (white × ground = ground) instead of leaving a white halo. It fades
  out via `mask-image`, **not** an overlay — an overlay paints flat colour over the grain and flecks and
  leaves a visible seam where the hero ends. A replacement photo with no baked-in fade can drop the
  blend mode.

### Curriculum accordion

The most involved component. One year open at a time (opening one closes the rest). Years are
`<button aria-expanded>`; books within an open year are a proper `tablist`/`tab`/`tabpanel` group with
roving tabindex and arrow-key navigation. Opening a year auto-selects its first book.

## Verifying changes

Headless Chrome is the fastest way to check a visual change without a browser:

```sh
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu \
  --hide-scrollbars --window-size=1465,5200 --virtual-time-budget=12000 \
  --screenshot=out.png --user-data-dir=<scratch>/cprofile http://127.0.0.1:8000/
```

Two gotchas:

- **Headless Chrome clamps the window to ~485 CSS px minimum.** `--window-size=390` renders at 485 and
  crops the image to 390, which looks like broken layout but is not. To test true phone widths, load the
  page in an `<iframe>` of the target width inside a wrapper page and measure
  `contentDocument.documentElement.scrollWidth` vs `clientWidth`.
- `--screenshot` cannot run JS, so to capture an interactive state (an open accordion, a selected book)
  write a temporary `__preview.html` copy of `index.html` with a script appended that clicks the target
  after a delay. **Delete these harness files afterwards** — `__preview.html`, `__frame.html`.

Worth re-running after any layout change: the overflow sweep across
360/390/480/640/768/880/900/1024/1200/1440px. A fixed-width grid track has already caused a real overflow
bug in the band just above the mobile breakpoint.

## Known placeholder state

- `assets/img/logo.png` and `hero-masjid.jpg` are **low-resolution crops taken from the mockup PNG**,
  meant to be replaced with real files at the same paths.
- Anything in `content/*.json` marked `TODO:` is a placeholder awaiting real content from the masjid —
  most of the curriculum (only Second Year is specified in the mockup), teachers 4–7, testimonies 3–4,
  and the footer contact details. Do not invent curriculum book lists or teacher details.
- `fees.cta` in `program.json` is the hook for future purchasing: set it to
  `{"label": "…", "href": "…"}` and the Fees card renders a button; it stays hidden while `null`.

## Deviations from the mockup (deliberate, keep them)

- A footer was added; the mockup ends abruptly after the testimonies.
- Carousels have a left arrow, hidden at the start — which is why the mockup only shows a right one.
- `Articles` and `Videos` are placeholder sections so no nav link is dead.

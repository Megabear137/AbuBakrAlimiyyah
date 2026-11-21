# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static informational website for the seven-year Ālimiyyah program at Jāmiʿah Islāmiyah Abū Bakr
(a masjid). Plain HTML/CSS/vanilla JS — **no build step, no dependencies, no framework, no tests**.
Content is data-driven (`content/*.json`) so enrolment/payment can be added later.

## Running it

```sh
python3 -m http.server 8000     # http://localhost:8000
python3 tools/admin_server.py   # http://127.0.0.1:8001, the site plus its local editors
```

**A server is mandatory**: the pages `fetch` `content/*.json`, which `file://` blocks. Deployment: Cloudflare (Workers static assets) builds from GitHub; pushing to the
`production` branch publishes, and `main` is where work happens. `.assetsignore` keeps `tools/`, the
notes and other non-site files off the live site; add any new non-site file to it. Book reservations also need
the Apps Script in `tools/reserve/` deployed in a Google account (its README); that part runs at Google,
not on the host.

**Bump the `?v=` query on the CSS/JS links whenever you change those files** — in `index.html`,
`article.html`, `teacher.html`, `bookstore.html`, `book.html` and `graduates.html` (all load `styles.css`; check each
page's script tags). The static server sends no cache headers, and a stale JS under a new CSS renders
plausible-looking but wrong markup that has been mistaken for layout bugs. JSON is fetched with
`cache: "no-cache"` and needs no bump.

## Design

The design mockups (`design/`) were removed once the site was finished; they remain in the git
history before the commit that removed them. Comments in the code that name a
`design/canvas-*` option refer to that history. The site itself is now the reference: don't restore
superseded looks (aged-leaf ground, khatim dividers, plaques, arches, the green palette, the wall and
ledges).

### Look

- **Light** (default, no selector): a pale tint of the shelf's wood (#f2dec6 → #e9cdae, plain, no
  grain). **All text on the light ground and cream panels is `--brown-ink` #462c16** — its own token,
  never `--wood`. Section titles are a dark-brown gradient. Small labels on the ground are #7d5006.
  `--rust` rgb(189,93,15) for dots, active dash, chip bullets. Darker board (`--board` #6b3f26 →
  `--board-deep` #3c2213) carries the article panel, plain video tiles and the footer, with bright
  gold titles. Details has no panel: newspaper columns on the ground, double rules between them,
  italic names (brown-ink rules in light, gold in dark, `--tr-*` tokens).
- **Dark** (`[data-theme="dark"]`, tokens in section 1 of `styles.css`, panel overrides in section 12):
  espresso ground (#26140a → #1a0d04), gold gradient capitals, dark-glass panels edged in faint gold.
- **Every wooden surface is `--wood` rgb(161,101,65)** (bays, niche mouldings); text-bearing panels use
  the darker board (cream on raw wood is only 4.8:1). The shelf and book leathers are never recoloured.
- **Buttons** (`.btn--gold`, and the pressed `.seg__btn`) are cream pills in a gilt hairline with
  `--brown-ink`, as the round buttons are; dark glass
  with gold-pale ink in dark mode and over the banner photo (`.hero .btn--gold`), a shade whiter on
  the cream book leaf and cart slip. The colours are the `--btn-*` tokens in both theme blocks of
  section 1. The class keeps its old name.
- **Grain** is SVG noise in data URIs in `:root` (`--grain-*`, `--grain-v`), generated once
  (a walnut finish) and softened. A `background` using `var(--grain)` must
  list `var(--grain-size)` at the same position in `background-size`, or the gradient tiles.
- **Logo**: `assets/img/logo_{black,gold}_web.png` (520px trims of the 4236px masters). Black on the
  light ground (section dividers in light), gold on everything dark, including the footer in both modes.
  The header has no logo.
- Section titles are Gilda Display capitals (`--title`); other display text is Cormorant.
- **Fonts are self-hosted** in `assets/fonts/` (`fonts.css` + woff2, Google Fonts' own files split by
  script: latin, latin-ext, vietnamese, arabic), so no visitor request goes to Google. Don't link
  `fonts.googleapis.com` from the site. All six families are SIL OFL 1.1; keep `assets/fonts/licenses/`
  with the files. To add a weight or family, fetch Google's css2 URL with a current Chrome user agent,
  download the woff2 files it names, and add their `@font-face` blocks to `fonts.css`.
  `index.html`, `teacher.html` and `graduates.html` **preload** Cormorant's latin upright and italic files (and the italic latin-ext, for the ā of the hero's *Ālimiyyah* and the bios' transliterations): text a script
  fills in (the hero's italic `titleEmphasis`, the teacher card's italic bio) otherwise requests its
  face only after the JSON loads and swaps in visibly late. Rename a font file, update the preloads.

## Architecture

### Content is data, markup is a shell

Pages contain no copy; empty elements tagged `data-slot="…"` are filled by a script from
`content/*.json`. Changing what's displayed usually means editing **the JSON shape and its render
function**, not the HTML (the few strings in HTML are fallbacks).

| Page | Script | Data |
|---|---|---|
| `index.html` | `main.js` (+ `carousel.js`, `curriculum.js`, `bookstore.js`, `nav.js`, `cart.js`, `splash.js`) | all six JSON files |
| `article.html?id=` | `article.js` | `media.json` |
| `teacher.html?id=` | `teacher.js` | `teachers.json` |
| `graduates.html` | `graduates.js` | `graduates.json` |
| `bookstore.html?group=` | `bookstore.js` (after `curriculum.js`) | `bookstore.json` |
| `book.html?id=&print=` | `book.js` (after `curriculum.js` and `cart.js`) | `bookstore.json` |

Every page also loads `nav.js` and `cart.js` (the cart's bag button and slip, which fetch
`bookstore.json` when first opened).

**Duplicated code that must be kept in step** (the page scripts are self-contained on purpose):

- The header, menu and footer markup is copied across all six HTML pages. Change one, change all.
- The footer's contact lines are rendered by each page script: `main.js`, `article.js`, `teacher.js`, `bookstore.js`, `book.js`, `graduates.js`.
- `inline()` (the `**bold**`/`_italic_`/`[link](href)` renderer, web/mail/phone links only) lives in
  `article.js`, `teacher.js` and `tools/admin/editor.js` (with its inverse `toMarkup()`).
- `printsOf()` in `bookstore.js`, `book.js`, `cart.js` and `tools/reserve/Code.gs`.
- `cents()` (a price written like `$12.00`, else not reservable) in `cart.js` and `tools/reserve/Code.gs`.
- The bookstore's head fields (`STORE_HEAD`: … `pickup`, `hold`, `payWith`, `reserveTo`) in
  `tools/admin_server.py`, `tools/admin/bookstore.js` and `tools/admin/books.js`.
- `BINDINGS` in `curriculum.js`, `tools/admin/shelf.js`, `tools/admin/bookstore.js` and
  `tools/admin_server.py`. Add a binding in all four.
- The theme key `alimiyyah.theme`: the inline `<head>` script (sets `data-theme` before first paint)
  and `nav.js`.

### Script globals (load order matters)

- `carousel.js` → `window.createCarousel({mount, items, render, perView, label, controls})`, returns
  `{go, layout, destroy}`. Before `main.js`.
- `curriculum.js` → `window.renderCurriculum(mount, data)` and `renderCurriculum.drawnCover`. Before
  `main.js`, `bookstore.js`, `book.js`.
- `bookstore.js` → `window.renderBookstore(data, all)` (+ `.tab()`, `bookstore:tab` event). Before `main.js`.
- `main.js` exposes `renderTeachers`, `renderMedia`, `renderTestimonies` for the editors; calling them
  again destroys the previous carousels.
- `nav.js`: full-screen menu (focus trap, Escape), the theme toggle, and the fixed header's scroll
  state (`--stuck` once scrolled: shorter, CTA pill hidden; `--past` beyond a `.hero`: cream rounds in light).
  The header bar is `pointer-events: none`; only its links and buttons take clicks.
- `cart.js` → `window.cart` (`add(id, print)`, `has`, `count`, `open`, `cents`) and a `cart:change`
  event on `document`. Injects its bag button into `.site-header__end`. Before `book.js`.
- `splash.js` (home page only) → the loading splash. Listens for `content:ready`, which `main.js`
  fires on `document` once every JSON file is drawn (or has failed), so it loads **before** `main.js`.

### JSON fields that shape presentation

- Section heads: `kicker` (✦ eyebrow; empty hides) + `heading`/`label`, no lede.
- `testimonies.cta` (`{label, href}`, `null` hides): the cream button under the niches, to
  `graduates.html`. The testimonies editor reads it for its preview but never writes it.
- `graduates.json`: `titles` (`brothers` Maulānā, `sisters` ʿĀlimah, set in italic before every name) and
  `classes[]` oldest first (`year`, `label`, `brothers[]`, `sisters[]`, names without the title; an
  empty side drops its column). The count line and the row of years are worked out from the list;
  each class is `#class-<year>`. Hand-edited (no editor). From the masjid's Alumni/Graduates PDF,
  names as given, except its "Seventh Graduation" and "Eight" class labels were put right.
- `hero.ctaSecondary` (`{label, href}`, `null` hides): the banner's cream second button (the bookstore).
- `hero.kicker`: the masjid's name between gold rules over the title (empty hides).
  `hero.titleEmphasis`: the word of `hero.title` set very large in italic; the rest of the title
  becomes `.hero__rest` spans of spaced capitals. `hero.subtitle` is the line under the title
  (empty hides it). `introduction` (`label` "Our Program", `body`) is the section under the banner; the
  old `program` panel is gone.
- Details (`renderDetails`) is one panel with a column per track: `timings.groups[]` (`label`,
  optional `years`, a dotted-leader row per `rows[]` entry) paired with `fees.tiers[]` by `label` (else
  by position). An `amount`'s leading currency sign is drawn small and raised. `fees.heading` and
  `timings.heading` are no longer shown.
- `fees.discounts`: large percentages beneath the tracks (a `value` starting `N%` is split into the
  figure and the rest), absent without rows. `fees.cta` (`{label, href}`, `null` hides) is the hook for
  future enrolment, centred under the discounts.
- Teachers: `width` 1–4, `height` 1–3 (omitted at 1), `bioBeside` (width ≥2; honoured only where
  the card itself is ≥44rem, a container query on `.teacher`, else the bio sits under the name), `id` (slug → `teacher.html?id=`; the home page's cards don't link to it, by request, so the pages
  are reached only by address),
  `body` (strings = paragraphs, `{"heading"}`). Cards stand in list order, packed dense.
- Articles (`media.json` `articles.brothers`/`sisters`): `id` unique across both lists, `body` blocks
  (string, `{"heading"}`, `{"quote","source"}`), a non-empty `href` replaces the page. The article page
  opens with the basmalah (Amiri's U+FDFD, the font preloaded), not the `excerpt`, which is only the
  home page card's text. Videos are one
  list, `videos.items` (`title`, `duration`, `thumbnail`, `href`; no date or subject).
  An empty `thumbnail` takes a YouTube `href`'s own picture (maxres, else hqdefault). The site can't
  read a video's length; the videos editor fills `duration` from the link (`GET /__admin/duration`,
  which reads the YouTube page or Vimeo's oEmbed; a video file's metadata in the browser).
- Curriculum: each year's `color` (a binding) binds its books; a book's `book_size`
  small/medium/large picks from `SIZES`; `description` (slip, ~two sentences, clamped at six lines) vs
  `long` (folio only). A title starting `TODO` renders a dashed placeholder everywhere.
- Bookstore books: one posting per book (`years` lists every year it's taught), `subject`, `edition`,
  `price` (text), `description`, `cover`, `featured`, `size` (`large` 2×2 / `medium` 2×1), `tint`,
  `id`, `soldOut`. A book in several editions has `prints: [{edition, price, cover, soldOut}]`
  instead of those four fields. `subjectGroups` (hand-edited, not by the editor) makes the bookstore
  tabs; `layouts` gives a tab its own `order`/`large`/`medium`. Head fields `pickup`, `hold`, `payWith`
  (shown in the cart and the receipt) and `reserveTo` (the Apps Script URL).
- Bookstore `message` (`body`: paragraphs, `closing`: the du'a) is the librarian's message, a framed
  panel under `bookstore.html`'s masthead (`renderLetter` in `bookstore.js`, drawn once on load; an
  empty `body` hides it). Hand-edited like `subjectGroups`: it isn't in `STORE_HEAD`, so the editor
  neither shows nor overwrites it. Its wording is the librarian's; only two missing spaces after
  commas were put in.

### Reserving books

**Books are reserved, not bought; nothing on the site takes a payment.** A book's page adds the chosen
print to the cart (`localStorage["alimiyyah.cart"]`, `[{id, print, qty}]`, at most 5 copies and 20
lines). The cart's slip takes a name and email and POSTs `{name, email, website, items}` as
`text/plain` JSON (a simple request, so no CORS preflight) to `bookstore.json`'s `reserveTo`. That is
the Google Apps Script web app in `tools/reserve/Code.gs`, which:

- checks the books against the live site's `bookstore.json`, once its `site` setting is filled in;
- writes one row per book to the ledger sheet;
- emails the reader a receipt and the bookstore a copy;
- answers `{ok, ref}` or `{ok: false, message}`, and the message is shown as is.

The reader pays and collects at the masjid. `website` is a honeypot.

- **Add to cart** shows only with `reserveTo` set, a price written like `$12.00` and no `soldOut`.
  The cart drops lines that stop qualifying.
- Stock isn't counted (`soldOut` by hand).
- The script lives in the repo, but it is deployed by pasting it into Google: **after changing it,
  redeploy a new version** (README). It holds no secrets; it runs as the account that deploys it.
  For now that is a personal Google account until the masjid has its own.
- Policy shown in the receipt (`pickup`, `hold`, `payWith`) is left out of the email while it reads
  `TODO`.

### Book photographs

`tools/covers.py` (Pillow, numpy) cuts each photograph to the book and writes
`assets/img/books/tight/<name>.jpg` plus `tight/covers.json` (crop, aspect, colour). **Run it after
adding or replacing a photograph**, and deploy `tight/` after editing an image. Hand crops/rotations
from *Edit image* live in `tools/cover_edits.json`; the originals are never changed.

### The local editors (`tools/admin_server.py`)

Standard library only. It serves the site with `Cache-Control: no-store`, **injects** the editors
(`tools/admin/*.js`, `editor.css`) into pages as it sends them, and answers `GET`/`PUT
/__admin/<resource>` (the `RESOURCES` table: articles, curriculum, teachers, videos, testimonies,
bookstore, plus `/__admin/cover`). **The bookstore dashboard** is a page of the server's own,
`/__admin/books` (`tools/admin/books.{html,js,css}`, linked from the bookstore editor's launch
buttons): every book with each print on its own row, edited in a drawer and saved through
`/__admin/bookstore`. Its photo upload, `PUT /__admin/photo`, writes a new JPEG under an unused name
(`<id>.jpg`, else `<id>-v2.jpg`…, never over an existing photograph) and runs `covers.py` on it at once. **The public site must have no editor code: keep every admin line
out of the site's HTML and JS.** It binds 127.0.0.1 and rejects foreign `Host`/`Origin`.

Each save is validated, replaces only its own keys (keeping e.g. `note`, `subjectGroups`), backs up
to `.admin-backups/` (last 30), writes atomically as `json.dumps(indent=2, ensure_ascii=False)`, and
gets a 409 if the file's hash changed since load (articles and videos share `media.json`'s hash). Each
editor redraws with the site's own render function, so the preview is exact. On `bookstore.html` the
bookstore editor edits the open tab's layout.

## Things that bite

- **The banner blends into the ground**: `.hero::after` ends in exactly `--hero-fade`. Change a
  mode's ground, change `--hero-fade` with it.
- **Carousel**: don't give `.carousel__viewport` horizontal padding (slide widths are measured from
  its box). Its vertical padding (cancelled by negative margins) keeps hover shadows unclipped. Arrows
  flank the slides; the `controls` option is kept but unused. It drags (pointer), pages on horizontal
  wheel, and a >6px drag swallows the following click.
- **Bookshelf** (`curriculum.js`):
  - Years pair two to a row; seven years make four boards. Each well scrolls sideways, never wraps
    (`justify-content: safe center`).
  - The 300px well height is derived from the tallest spine (268) + headband + hover lift. Grow
    `SIZES` → grow the well.
  - Pointing at a spine shows the slip (one per shelf, appended to `<body>`, `aria-hidden`, ignores
    touch); clicking opens the folio in place of the well. Where bays pair (≥881px) the reading bay
    widens across the row — **881 must stay in step with the 880px breakpoint**.
  - Spines are SVG drawn at the book's exact size (`drawSpine`); titles are fitted by measuring
    (`fitText`/`widen`) after render and on `document.fonts.ready`.
  - Keyboard: each well is `role="group"` with a roving `tabindex`; arrows/Home/End move, Enter/Space
    opens, Escape closes. Don't reintroduce `tablist`/`tab`/`tabpanel`.
- **Niches**: the arch is one SVG path in four data-URI tokens on `.niche-slot` plus `--niche-pad`;
  change all five together. The drop shadow is a `filter` on the parent because a mask clips its own.
- **Bookstore medium tiles** use `contain: size` so they don't grow their row.
- **Teacher cards** grow to their text (`grid-auto-rows: minmax(180px, auto)` on `.mosaic` and
  `.t-others`); never give them a fixed row height again, the bios are paragraphs. Their markup is
  `.teacher > .teacher__in > (.teacher__head, .teacher__bio)`, built in both `main.js` and `teacher.js`;
  `.teacher__in` must stay unpositioned so the name's stretched link covers the card.
- **Motion**: `.rv` uses `animation-timeline: view()` inside `@supports`; `prefers-reduced-motion`
  switches all animation off.
- **The splash** (home page only) hides the page until the content, its fonts and the banner photo
  are in. `index.html`'s second `<head>` script sets `splash-on` and `splash-hold` on `<html>`
  before first paint, plus `splash-quick` (no logo, a short fade) if `sessionStorage["alimiyyah.splash"]`
  says this visit already saw it, and lifts everything after 10s should `splash.js` fail. Without JS
  there is no splash. `splash-hold` pauses the banner's entrance (`.hero .in`, `.hero__img`), so the
  title rises as the splash fades. The fill is `--splash-p` (a registered `@property`); its timings
  are in both the CSS and `splash.js` (`FILL`, `GLINT`, `FADE`). The bismillah over the logo (`.splash__bism`, Amiri's U+FDFD, the font preloaded) is
  written in the same way, a veil (`.splash__quill`) sliding off it to the left once `splash.js` sees
  Amiri loaded (`is-writing`, else after 1.2s); it is hidden on `splash-quick`. The fill is the still logo under a veil
  that slides up off it (`.splash__veil`, one `transform`, so it runs on the compositor while `main.js`
  blocks the main thread); the veil vanishes by blending (`--splash-blend`: multiply over white in light,
  lighten over black in dark). Never put a transform on `.splash__mark` itself: it would isolate the
  blend and show the veil as a box (the settle scales its children instead). Don't go back to a mask
  gradient (freezes) or a clipping box over a counter-moving logo (falls out of step). The first visit takes ~3.5s even on
  a fast load (at least 0.9s, then the fill, the glint and the fade); cap 8s.

## Verifying changes

Headless Chrome (Playwright's `chrome-headless-shell` on Linux):

```sh
chrome --headless=new --disable-gpu --hide-scrollbars --window-size=1440,5600 \
  --virtual-time-budget=12000 --screenshot=out.png http://127.0.0.1:8000/
```

- The hero animates in on load; a faint subtitle or missing CTA is usually a too-short
  `--virtual-time-budget`.
- **On the home page the splash comes first**, and the banner's entrance waits for it. Headless
  screenshots don't advance animations that were paused and resumed, so a home-page shot comes out
  washed and faint whatever the budget: shoot through an `<iframe>` harness that calls
  `getAnimations().forEach(a => a.finish())` on the page's document ~7s after load.
- The banner is `100vh`; for a full-page shot use a temporary copy with
  `.hero { min-height: 860px !important }`.
- The window is clamped to ~485px wide: test phone widths in an `<iframe>` inside a wrapper page.
- The theme follows the system when nothing is stored; set `localStorage["alimiyyah.theme"]` in a
  harness to shoot one mode.
- Interactive states (slip, folio, menu) need a temporary `__preview.html`/`__frame.html` harness that
  dispatches events (`--dump-dom` to assert classes, focus, `aria-expanded`). The animation clock
  doesn't advance under `--dump-dom`: call `getAnimations().forEach(a => a.finish())` before measuring.
  **Delete harness files afterwards.**
- After layout changes, sweep for overflow at 360/390/480/640/720/768/880/900/1024/1200/1440px.
  `.hero__img` always reports a few px over (its drift animation) and is not a fault.

## Known placeholder state

- `assets/img/hero-masjid.jpg` is a low-resolution placeholder; replace with a real photo (≥2400px)
  at the same path.
- Anything marked `TODO:` in `content/*.json` awaits the masjid: the teachers' page biographies (and the years still
  written `????` in their bios), testimonies 3–4, every article (ids `brothers-1`… are
  placeholders) and video (the bookstore's `lede` is left empty, which hides it). The footer
  contacts are from smacanada.ca (the program's own address, alimiyyah@smacanada.ca). **Do not invent
  books, teacher details, articles or videos.**
- The curriculum and bookstore follow `Madresa Book Price List 2024.xlsx`, except (as the masjid
  asked) Riyad al-Salihin and Tarjamat al-Qur'an in Fourth and Fifth, al-Fawa'id al-Makkiyya in Fifth, al-Hidaya in Fifth and
  Sixth, and without Bahishti Zewar. The book the list calls Khulāṣat al-Bayān ($5) is the main print of
  al-Muqaddima al-Jazariyya (the Qira'at Academy print carries both), not a book of its own; the
  Qadimi print ($3) is the second. Its photograph keeps the name `khulasat-al-bayan.jpg`.
  Tarjamat al-Qur'an and Shama'il al-Tirmidhi are taught but have no book of their own, so they aren't
  sold. The books the masjid photographed that aren't on the list are
  sold at the end of `books` with the price `TODO`, no `years` and (where unknown) a `TODO:`
  description. Don't add books beyond these.
- Covers in `assets/img/books/` are the masjid's photographs (600×800); books without one show the
  drawn binding. Extra editions are `<slug>-2.jpg`, ….
- `pickup`, `hold` and `payWith` are the masjid's policy (the office, 9 am to 7 pm; 14 days; cash or
  debit).

## Deliberate deviations from the mockup

- Videos and Alumni are carousels with page dots.
- Alumni keeps the mihrab niches, hung straight on the ground (no wooden wall).
- Content comes from the JSON, so `TODO:` placeholders show.

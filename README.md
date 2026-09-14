# Jamiyah Islamiyyah Abu Bakr — Alimiyyah Program

A static, information-only website for the masjid's seven-year Alimiyyah program.
Plain HTML, CSS and JavaScript — no build step, no dependencies, no framework.

## Running it locally

The page loads its content from JSON files, and browsers block `fetch` on `file://`,
so **it must be served over a local web server** — double-clicking `index.html` will show
an error banner.

```sh
cd alimiyyah_website
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

(Any static server works: `npx serve`, `php -S localhost:8000`, VS Code's Live Server, etc.)

## Editing the content

**You should never need to touch the HTML.** Everything visible on the page comes from the
four files in `content/`. Edit them in any text editor, save, and reload the browser.

Anything still marked `TODO` is a placeholder that needs your real text.

| File | Controls |
|---|---|
| `content/program.json` | Introduction paragraph, the "Our Program" text, class timings, fees, family discounts, footer contact details |
| `content/curriculum.json` | The seven years and the books taught in each |
| `content/teachers.json` | The teacher carousel |
| `content/testimonies.json` | The alumni testimonies carousel |

### Adding a book

Add an object to the right year's `books` array in `content/curriculum.json`:

```json
{
  "title": "Nur ul-Idah",
  "titleUrdu": "نور الإيضاح",
  "subject": "Fiqh",
  "author": "Hasan ash-Shurunbulali",
  "description": "The standard introductory text in Hanafi fiqh, covering purification, prayer, fasting and zakat."
}
```

`titleUrdu` and `author` may be left as empty strings (`""`) — the layout adapts.
There is no limit on the number of books; the row scrolls sideways if they do not fit.

### Adding a teacher

```json
{ "honorific": "Moulana", "name": "Yusuf Patel", "bio": "Teaches hadith in the final two years." }
```

### Adding a testimony

```json
{ "quote": "…", "name": "Full Name", "graduated": "2023" }
```

### Changing the fees

Prices live only in `content/program.json`, under `fees.tiers`. Change them there.

**After editing, check your JSON is still valid** — a stray comma will blank the section.
Paste it into <https://jsonlint.com> if a section disappears, and check the browser console.

## Placeholder assets to replace

Both images were cropped out of the design mockup and are low resolution. Replace them
with the real files, keeping the same paths:

- `assets/img/logo.png` — the SMA roundel. A transparent-background SVG or a 512px PNG is ideal.
- `assets/img/hero-masjid.jpg` — the prayer hall photograph. Aim for ~2400px wide.

## Adding online payment later

The site is deliberately structured so this does not require a rewrite:

1. Create a Stripe Payment Link (or equivalent) for enrolment.
2. Set the `cta` field in `content/program.json`:

   ```json
   "cta": { "label": "Enrol now", "href": "https://buy.stripe.com/..." }
   ```

The Fees card renders that button automatically and hides it while `cta` is `null`.
Anything beyond a hosted checkout link (accounts, carts, invoices) would need a backend,
at which point the existing HTML/CSS can be carried over into a framework unchanged.

## Deploying

The whole folder is static. Upload it as-is to GitHub Pages, Netlify, Cloudflare Pages,
or any web host — there is nothing to build.

## Layout

```
index.html                 markup and section order
assets/css/styles.css      all styling, commented by section
assets/js/main.js          loads the JSON and renders each section
assets/js/curriculum.js    the year accordion and book selector
assets/js/carousel.js      shared carousel used by teachers and testimonies
assets/js/nav.js           mobile menu and active-link highlighting
content/*.json             all site content
design/wesbite_design.png  the original design mockup, for reference
```

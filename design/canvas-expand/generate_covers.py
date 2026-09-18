"""Placeholder book covers for the canvas-expand mockups.

The real site will point `cover` in content/curriculum.json at a photograph or
scan of the book at assets/img/books/<slug>.jpg. Until the masjid sends those,
these stand in: the same kitab binding the spine wears, seen face-on, so the
mockups show a cover of the right shape and weight. Re-run after editing:

    python3 generate_covers.py
"""
import pathlib

W, H = 300, 400
OUT = pathlib.Path(__file__).parent / "covers"

# [slug, leather, cartouche, title lines] - leathers are BINDINGS in curriculum.js
COVERS = [
    ("achi-baatain", "#4a1813", "#1a1210", ["Achi", "Baatain"]),
    ("tasheel-nahwa", "#2c1d13", "#5a1916", ["Tasheel", "ul-Nahwa"]),
    ("duroos", "#1c2a22", "#4a1813", ["Duroos", "al-Lughah"]),
]

GILT = "#d9aa48"


def cartouche(cx, cy, w, h):
    """The spine's pointed cartouche, as a path rather than a clip-path."""
    x0, x1 = cx - w / 2, cx + w / 2
    y0, y1 = cy - h / 2, cy + h / 2
    d12, d88 = y0 + h * 0.12, y0 + h * 0.88
    return f"M{cx} {y0}L{x1} {d12}L{x1} {d88}L{cx} {y1}L{x0} {d88}L{x0} {d12}Z"


def finial(cx, y, flip=False):
    s = -1 if flip else 1
    return (f'<g transform="translate({cx} {y}) scale(1 {s})">'
            f'<path d="M0 0V16" stroke="{GILT}" stroke-width="1.4"/>'
            f'<rect x="-4" y="16" width="8" height="8" transform="rotate(45 0 20)" fill="{GILT}"/>'
            f'</g>')


for slug, leather, label, lines in COVERS:
    title = "".join(
        f'<text x="{W/2}" y="{168 + i * 30}" text-anchor="middle" fill="{GILT}" '
        f'font-family="Georgia, serif" font-size="25" font-weight="600" '
        f'letter-spacing="0.5">{line}</text>'
        for i, line in enumerate(lines)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" stitchTiles="stitch"/>
      <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.5 0 0 0 -0.22"/>
    </filter>
    <linearGradient id="light" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#000" stop-opacity="0.45"/>
      <stop offset="0.16" stop-color="#000" stop-opacity="0.05"/>
      <stop offset="0.5" stop-color="#fff" stop-opacity="0.09"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.3"/>
    </linearGradient>
  </defs>

  <rect width="{W}" height="{H}" fill="{leather}"/>
  <rect width="{W}" height="{H}" filter="url(#grain)"/>
  <rect width="{W}" height="{H}" fill="url(#light)"/>

  <!-- double gilt frame -->
  <rect x="14" y="14" width="{W-28}" height="{H-28}" fill="none" stroke="{GILT}" stroke-width="1.6" opacity="0.85"/>
  <rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="{GILT}" stroke-width="0.8" opacity="0.6"/>

  <!-- corner rosettes -->
  <g fill="{GILT}" opacity="0.8">
    <circle cx="30" cy="30" r="3.2"/><circle cx="{W-30}" cy="30" r="3.2"/>
    <circle cx="30" cy="{H-30}" r="3.2"/><circle cx="{W-30}" cy="{H-30}" r="3.2"/>
  </g>

  {finial(W/2, 62)}
  {finial(W/2, H-62, flip=True)}

  <!-- title cartouche -->
  <path d="{cartouche(W/2, 170, 196, 132)}" fill="{GILT}"/>
  <path d="{cartouche(W/2, 170, 190, 126)}" fill="{label}"/>
  <path d="{cartouche(W/2, 170, 176, 112)}" fill="none" stroke="{GILT}" stroke-width="0.9" opacity="0.55"/>
  {title}

  <!-- foot medallion -->
  <circle cx="{W/2}" cy="{H-104}" r="15" fill="none" stroke="{GILT}" stroke-width="1.2"/>
  <circle cx="{W/2}" cy="{H-104}" r="7" fill="{GILT}" opacity="0.9"/>
</svg>
"""
    (OUT / f"{slug}.svg").write_text(svg, encoding="utf-8")
    print("wrote", slug + ".svg")

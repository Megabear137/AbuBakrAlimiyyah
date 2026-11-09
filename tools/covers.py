#!/usr/bin/env python3
"""Tight crops and colours of the books' photographs, for the bookstore.

The photographs in assets/img/books/ are studio shots: the book on a grey
table, framed differently each time (some fill the frame, others sit
off-centre with table and paper around them). The bookstore shows the book
alone, washed in its cover's colour, so for each photograph this writes:

  assets/img/books/tight/<name>.jpg    the book alone, cut a little inside
                                       its edges so no table shows
  assets/img/books/tight/covers.json   for each cover path: the tight crop,
                                       its height over its width, and the
                                       cover's colour (the tile's tint)

Run it after adding or replacing a photograph:

    python3 tools/covers.py

A photograph without an entry still shows, zoomed instead of cropped and
tinted by its binding. Where a book's edges are found wrongly, give its box
by hand in CROP_FIX (left, top, right, bottom, as fractions of the photo).

The admin server's "Edit image" (on book.html) saves a hand edit in
tools/cover_edits.json: for a photograph's name, {"rotate": degrees
clockwise, "box": [left, top, right, bottom]}, the box in fractions of the
photograph as rotated (its bounding box grown to hold it, the corners filled
with the table's colour). An edit replaces the edges found and CROP_FIX, and
the photograph itself is never changed, so an edit can always be undone.

Needs Pillow and numpy. design/canvas-library/generate_round5.py uses the
same functions for the mockups.
"""
import colorsys
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "assets" / "img" / "books"
OUT = BOOKS / "tight"
PAD = 0.022
EDITS = Path(__file__).resolve().parent / "cover_edits.json"

CROP_FIX = {
    "ilm-al-sarf-akhirin": (0.135, 0.07, 0.905, 0.95),
    "ilm-al-sigha": (0.08, 0.095, 0.915, 0.905),
    "sharh-al-aqida-al-tahawiyya": (0.085, 0.09, 0.925, 0.91),
    "sunan-ibn-maja": (0.145, 0.07, 0.87, 0.80),
}


def hexc(c):
    return "#%02x%02x%02x" % tuple(int(v) for v in c[:3])


def measure(path):
    """(the table's colour, the cover's colour) of a photograph."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    W, H = im.size
    k = int(min(W, H) * 0.05)
    box_ = getattr(Image, "Resampling", Image).BOX
    corners = [im.crop(b).resize((1, 1), box_).getpixel((0, 0)) for b in
               ((0, 0, k, k), (W - k, 0, W, k), (0, H - k, k, H), (W - k, H - k, W, H))]
    corners.sort(key=sum)
    bg = [sum(c[j] for c in corners[1:3]) / 2 for j in range(3)]    # the middle two: no shadow, no glare
    c = im.crop((int(W * .15), int(H * .12), int(W * .85), int(H * .88))).resize((60, 80)).quantize(8).convert("RGB")
    best = None
    for n, col in c.getcolors():
        h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in col])
        if not .12 < l < .7:
            continue
        sc = n * (0.15 + s) ** 1.6
        if best is None or sc > best[0]:
            best = (sc, col)
    return hexc(bg), hexc(best[1]) if best else "#5a5048"


def find_edges(path):
    """The book's box: the outermost long straight edge on each side."""
    import numpy as np
    from PIL import Image, ImageFilter
    im = Image.open(path).convert("L").resize((300, 400)).filter(ImageFilter.GaussianBlur(1))
    a = np.asarray(im).astype(float)
    h, w = a.shape
    dx, dy = np.abs(np.diff(a, axis=1)), np.abs(np.diff(a, axis=0))
    cs = (dx[int(h * .25):int(h * .75)] > 7).mean(axis=0)    # columns crossed by a long upright edge
    rs = (dy[:, int(w * .25):int(w * .75)] > 7).mean(axis=1)  # rows crossed by a long level edge

    def outer(score, n, low):
        for i in (range(2, int(n * .3)) if low else range(n - 3, int(n * .7), -1)):
            if score[i] > 0.55:
                return (i + 1) / (n + 1)
        return 0.0 if low else 1.0
    return outer(cs, w - 1, True), outer(rs, h - 1, True), outer(cs, w - 1, False), outer(rs, h - 1, False)


def load_edits():
    """The hand edits, by photograph name (tools/cover_edits.json)."""
    return json.loads(EDITS.read_text()) if EDITS.exists() else {}


def auto_box(src):
    """The box the tight crop takes without a hand edit, in fractions."""
    x0, y0, x1, y1 = CROP_FIX.get(src.stem) or find_edges(src)
    return x0 + PAD, y0 + PAD, x1 - PAD, y1 - PAD


def rotated(im, degrees, fill):
    """im turned clockwise, on a canvas grown to hold it (as the editor draws it)."""
    from PIL import Image
    d = degrees % 360
    if d == 0:
        return im
    T = getattr(Image, "Transpose", Image)    # Pillow before 9.1 has no enums
    turns = {90: T.ROTATE_270, 180: T.ROTATE_180, 270: T.ROTATE_90}
    if d in turns:
        return im.transpose(turns[d])
    return im.rotate(-degrees, resample=getattr(Image, "Resampling", Image).BICUBIC, expand=True, fillcolor=fill)


def tight(src, out, stale_after=0.0, edit=None, force=False):
    """Cuts src to out (when missing, stale or forced); returns its height over width."""
    from PIL import Image, ImageOps
    im = Image.open(src)
    if edit:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im = rotated(im, float(edit.get("rotate", 0)), tuple(bytes.fromhex(measure(src)[0][1:])))
        x0, y0, x1, y1 = edit["box"]
    else:
        x0, y0, x1, y1 = auto_box(src)
    W, H = im.size
    box = (round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H))
    if force or not out.exists() or out.stat().st_mtime < max(src.stat().st_mtime, stale_after):
        out.parent.mkdir(parents=True, exist_ok=True)
        im.convert("RGB").crop(box).save(out, quality=88, optimize=True)
    return (box[3] - box[1]) / (box[2] - box[0])


def entry(src, edits=None, stale_after=0.0, force=False):
    """covers.json's entry for a photograph, making its tight crop first."""
    edits = load_edits() if edits is None else edits
    edit = edits.get(src.name)
    out = OUT / src.name
    ratio = tight(src, out, stale_after, edit, force)
    # An edited crop is coloured by what it shows; the rest by the photograph.
    _, tint = measure(out if edit else src)
    # The ?v= changes with the crop, so a browser never shows an old one.
    v = hashlib.sha1(out.read_bytes()).hexdigest()[:8]
    return {"tight": f"assets/img/books/tight/{src.name}?v={v}", "ratio": round(ratio, 3), "tint": tint}


def main():
    here = max(Path(__file__).stat().st_mtime, EDITS.stat().st_mtime if EDITS.exists() else 0)
    edits = load_edits()
    manifest = {}
    for src in sorted(BOOKS.glob("*.jpg")):
        manifest[f"assets/img/books/{src.name}"] = entry(src, edits, here)
    (OUT / "covers.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{len(manifest)} covers -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

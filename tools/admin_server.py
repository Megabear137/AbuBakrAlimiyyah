#!/usr/bin/env python3
"""The local admin server: the site as `python3 -m http.server` serves it,
plus the article editor, the bookshelf editor, the teachers editor, the
videos editor, the testimonies editor and the bookstore editor.

    python3 tools/admin_server.py            # http://127.0.0.1:8001/
    python3 tools/admin_server.py --port 9000

The editors live in tools/admin/ and nothing on the public site refers to
them. This server alone adds them to the pages, on the way out (the files on
disk are never touched): editor.js to article.html, shelf.js, teachers.js,
videos.js, testimonies.js and bookstore.js to index.html, bookstore.js
to bookstore.html, and cover.js (Edit image) to book.html. The bookstore
dashboard, /__admin/books (tools/admin/books.html), is a page of its own that
lists every book and print and edits them through the bookstore's address;
a photograph uploaded there is saved under a new name in assets/img/books/
(never over another) and cut by tools/covers.py at once.
It alone answers the addresses they save to, so an uploaded copy of the site
has no editor and nothing that can write. It listens on 127.0.0.1
only and refuses requests that name another host, so neither the network nor
another web page in the browser can reach it.

Saving articles replaces the article lists of content/media.json; saving the
shelf replaces the years of content/curriculum.json; saving the teachers
replaces the heading, kicker and teachers of content/teachers.json; saving the
videos replaces the heading, kicker and videos of media.json; saving the
testimonies replaces the heading, kicker and testimonies of
content/testimonies.json; saving the bookstore replaces the heading, kicker,
lede, visitLabel, pickup, hold, payWith, reserveTo, books and layouts (each subject
tab's order and large and medium cards) of content/bookstore.json. Everything
else in each file stays as it is. Editing a book's image (on book.html)
saves its rotation and crop in tools/cover_edits.json and remakes its tight
crop and its entry in assets/img/books/tight/covers.json with
tools/covers.py; that alone needs Pillow and numpy. The previous file is copied to .admin-backups/ first, and
a save is refused if the file changed on disk since the editor loaded it,
unless the editor asks to overwrite.

Standard library only, like the rest of the site.
"""
import argparse
import datetime
import hashlib
import http.server
import json
import os
import re
import sys
import tempfile
import threading
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
ADMIN = Path(__file__).resolve().parent / "admin"
BACKUPS = ROOT / ".admin-backups"
KEEP_BACKUPS = 30
MAX_REQUEST = 4 * 1024 * 1024

JS, CSS = "text/javascript; charset=utf-8", "text/css; charset=utf-8"
ASSETS = {"editor.js": JS, "shelf.js": JS, "teachers.js": JS, "videos.js": JS, "testimonies.js": JS,
          "bookstore.js": JS, "cover.js": JS, "editor.css": CSS, "books.js": JS, "books.css": CSS}
# The bookstore dashboard, a page of the admin server's own.
DASHBOARD = "/__admin/books"
MAX_PHOTO = 40 * 1024 * 1024
PHOTO_LONG_SIDE = 1600
# The page, and the editors added to it as it is sent.
HOME_EDITORS = ("shelf.js", "teachers.js", "videos.js", "testimonies.js", "bookstore.js")
PAGES = {"/article.html": ("editor.js",), "/bookstore.html": ("bookstore.js",), "/book.html": ("cover.js",),
         "/index.html": HOME_EDITORS, "/": HOME_EDITORS}
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TINT_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
ARTICLE_TEXT = ("title", "subject", "author", "excerpt", "href")
BOOK_TEXT = ("title", "titleUrdu", "subject", "author", "description", "long", "cover", "color")
BOOK_SIZES = ("small", "medium", "large")
TEACHER_TEXT = ("honorific", "name", "bio")
TESTIMONY_TEXT = ("quote", "name", "graduated")
VIDEO_TEXT = ("title", "duration", "thumbnail", "href")
YOUTUBE_RE = re.compile(r"^https?://(?:www\.|m\.)?(?:youtube\.com/(?:watch\?(?:[^#]*&)?v=|embed/|shorts/|live/)|youtu\.be/)([\w-]{11})", re.I)
VIMEO_RE = re.compile(r"^https?://(?:www\.|player\.)?vimeo\.com/(?:video/)?(\d+)", re.I)
STORE_HEAD = ("heading", "kicker", "lede", "visitLabel", "pickup", "hold", "payWith", "reserveTo")
STORE_TEXT = ("title", "edition", "subject", "price", "description", "cover", "color")
PRINT_TEXT = ("edition", "price", "cover")
# The bindings assets/js/curriculum.js draws (its BINDINGS); keep in step.
BINDINGS = ("lapis", "ink", "lapis-silver", "ink-silver", "petrol", "slate", "oxblood", "aubergine")

write_lock = threading.Lock()

# A book's photograph, as bookstore.json names it, for the image editor.
COVER_RE = re.compile(r"^assets/img/books/[a-z0-9]+(?:-[a-z0-9]+)*\.jpg$")


def covers_module():
    """tools/covers.py, which needs Pillow and numpy (imported only when used)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("covers", Path(__file__).resolve().parent / "covers.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def version_of(raw):
    return hashlib.sha256(raw).hexdigest()[:16]


def article_lists(articles):
    """The names of the lists in media.json's `articles` (brothers, sisters)."""
    return [k for k, v in articles.items() if isinstance(v, list)]


def check_articles(payload, data):
    """Returns the first problem with the edited article lists, or None."""
    return check_article_lists(payload.get("articles"), article_lists(data.get("articles", {})))


def apply_articles(payload, data):
    # Only the lists change; the kicker, the heading, the videos and the
    # note keep their places and their values.
    current = data.get("articles", {})
    names = article_lists(current)
    data["articles"] = {k: payload["articles"][k] if k in names else v for k, v in current.items()}


def check_curriculum(payload, data):
    """Returns the first problem with the edited years, or None."""
    years = payload.get("years")
    if not isinstance(years, list) or not years:
        return "expected a list of years"
    for y, year in enumerate(years, 1):
        if not isinstance(year, dict):
            return "year %d is not an object" % y
        if not isinstance(year.get("name"), str) or not year["name"].strip():
            return "year %d has no name" % y
        if "color" in year and not isinstance(year["color"], str):
            return year["name"] + ": color must be text"
        if not isinstance(year.get("books"), list):
            return year["name"] + ": books must be a list"
        for b, book in enumerate(year["books"], 1):
            where = "%s, book %d" % (year["name"], b)
            if not isinstance(book, dict):
                return where + " is not an object"
            if not isinstance(book.get("title"), str) or not book["title"].strip():
                return where + " has no title"
            for field in BOOK_TEXT:
                if field in book and not isinstance(book[field], str):
                    return where + ": %s must be text" % field
            if book.get("book_size", "medium") not in BOOK_SIZES:
                return where + ": book_size must be small, medium or large"
    return None


def apply_curriculum(payload, data):
    data["years"] = payload["years"]


def check_teachers(payload, data):
    """Returns the first problem with the edited teachers, or None."""
    for field in ("heading", "kicker"):
        if not isinstance(payload.get(field), str):
            return field + " must be text"
    teachers = payload.get("teachers")
    if not isinstance(teachers, list):
        return "expected a list of teachers"
    seen = set()
    for n, t in enumerate(teachers, 1):
        where = "teacher %d" % n
        if not isinstance(t, dict):
            return where + " is not an object"
        if not isinstance(t.get("name"), str) or not t["name"].strip():
            return where + " has no name"
        for field in TEACHER_TEXT:
            if field in t and not isinstance(t[field], str):
                return where + ": %s must be text" % field
        # The card's span: columns 1-4, rows 1-3.
        for field, top in (("width", 4), ("height", 3)):
            if field in t and (type(t[field]) is not int or not 1 <= t[field] <= top):
                return where + ": %s must be a whole number from 1 to %d" % (field, top)
        if "bioBeside" in t and not isinstance(t["bioBeside"], bool):
            return where + ": bioBeside must be true or false"
        # The id gives the teacher their page, teacher.html?id=<id>; optional.
        if "id" in t:
            if not isinstance(t["id"], str) or not ID_RE.match(t["id"]):
                return where + ": the id must be lowercase words joined by hyphens"
            if t["id"] in seen:
                return where + ": the id %r is used twice" % t["id"]
            seen.add(t["id"])
        # The page's biography: paragraphs and headings.
        body = t.get("body", [])
        if not isinstance(body, list):
            return where + ": body must be a list"
        for b, block in enumerate(body, 1):
            if not (isinstance(block, str) or (isinstance(block, dict) and set(block) == {"heading"}
                                               and isinstance(block["heading"], str))):
                return where + ": block %d is not a paragraph or heading" % b
    return None


def apply_teachers(payload, data):
    # The note keeps its place and its value.
    for field in ("heading", "kicker", "teachers"):
        data[field] = payload[field]


def check_testimonies(payload, data):
    """Returns the first problem with the edited testimonies, or None."""
    for field in ("heading", "kicker"):
        if not isinstance(payload.get(field), str):
            return field + " must be text"
    testimonies = payload.get("testimonies")
    if not isinstance(testimonies, list):
        return "expected a list of testimonies"
    for n, t in enumerate(testimonies, 1):
        where = "testimony %d" % n
        if not isinstance(t, dict):
            return where + " is not an object"
        if not isinstance(t.get("quote"), str) or not t["quote"].strip():
            return where + " has no quote"
        if not isinstance(t.get("name"), str) or not t["name"].strip():
            return where + " has no name"
        for field in TESTIMONY_TEXT:
            if field in t and not isinstance(t[field], str):
                return where + ": %s must be text" % field
    return None


def apply_testimonies(payload, data):
    # The note keeps its place and its value.
    for field in ("heading", "kicker", "testimonies"):
        data[field] = payload[field]


def check_bookstore(payload, data):
    """Returns the first problem with the edited bookstore, or None."""
    for field in STORE_HEAD:
        if not isinstance(payload.get(field), str):
            return field + " must be text"
    # Where the cart posts a reservation: the Google Apps Script web app
    # (tools/reserve/); empty, no book can be reserved.
    if payload["reserveTo"] and not payload["reserveTo"].startswith("https://"):
        return "the reservations address must start with https://"
    books = payload.get("books")
    if not isinstance(books, list):
        return "expected a list of books"
    seen = set()
    for n, b in enumerate(books, 1):
        where = "book %d" % n
        if not isinstance(b, dict):
            return where + " is not an object"
        if not isinstance(b.get("title"), str) or not b["title"].strip():
            return where + " has no title"
        for field in STORE_TEXT:
            if field in b and not isinstance(b[field], str):
                return where + ": %s must be text" % field
        if b.get("color") and b["color"] not in BINDINGS:
            return where + ": color must be one of " + ", ".join(BINDINGS)
        # The years it is taught in, which the Bookstore page filters by.
        if "years" in b and (not isinstance(b["years"], list)
                             or not all(isinstance(y, str) and y.strip() for y in b["years"])):
            return where + ": years must be a list of year names"
        if "featured" in b and not isinstance(b["featured"], bool):
            return where + ": featured must be true or false"
        if "soldOut" in b and not isinstance(b["soldOut"], bool):
            return where + ": soldOut must be true or false"
        # A book of several prints: each its own edition, price, picture
        # and soldOut.
        if "prints" in b:
            if not isinstance(b["prints"], list) or not b["prints"]:
                return where + ": prints must be a list of prints"
            for k, p in enumerate(b["prints"], 1):
                there = where + ", print %d" % k
                if not isinstance(p, dict):
                    return there + " is not an object"
                for field in PRINT_TEXT:
                    if field in p and not isinstance(p[field], str):
                        return there + ": %s must be text" % field
                if "soldOut" in p and not isinstance(p["soldOut"], bool):
                    return there + ": soldOut must be true or false"
        # The id gives the book its page, book.html?id=<id>; optional.
        if "id" in b:
            if not isinstance(b["id"], str) or not ID_RE.match(b["id"]):
                return where + ": the id must be lowercase words joined by hyphens"
            if b["id"] in seen:
                return where + ": the id %r is used twice" % b["id"]
            seen.add(b["id"])
        # The card's size: "large" (two by two), "medium" (two by one) or left
        # out; a large or medium card's own colour.
        if "size" in b and b["size"] not in ("normal", "medium", "large"):
            return where + ": size must be normal, medium or large"
        if "tint" in b and (not isinstance(b["tint"], str) or not TINT_RE.match(b["tint"])):
            return where + ": tint must be a colour like #1c3f7a"
    # Each subject tab's own layout: its cards' order and its large and medium ones, by id.
    layouts = payload.get("layouts", {})
    if not isinstance(layouts, dict):
        return "layouts must be an object"
    for tab, lay in layouts.items():
        if not isinstance(lay, dict):
            return "the layout of %r is not an object" % tab
        for field in ("order", "large", "medium"):
            ids = lay.get(field, [])
            if not isinstance(ids, list) or not all(isinstance(i, str) and i in seen for i in ids):
                return "the layout of %r: %s must be a list of the books' ids" % (tab, field)
    return None


def apply_bookstore(payload, data):
    # The note and the subject groups keep their places and values.
    for field in STORE_HEAD + ("books",):
        data[field] = payload[field]
    if payload.get("layouts"):
        data["layouts"] = payload["layouts"]
    else:
        data.pop("layouts", None)


def read_videos(data):
    videos = data.get("videos", {})
    return {k: videos.get(k, [] if k == "items" else "") for k in ("heading", "kicker", "items")}


def check_videos(payload, data):
    """Returns the first problem with the edited videos, or None."""
    for field in ("heading", "kicker"):
        if not isinstance(payload.get(field), str):
            return field + " must be text"
    items = payload.get("items")
    if not isinstance(items, list):
        return "items is not a list"
    for n, v in enumerate(items, 1):
        where = "video %d" % n
        if not isinstance(v, dict):
            return where + " is not an object"
        if not isinstance(v.get("title"), str) or not v["title"].strip():
            return where + " has no title"
        for field in VIDEO_TEXT:
            if field in v and not isinstance(v[field], str):
                return where + ": %s must be text" % field
    return None


def apply_videos(payload, data):
    # moreHref, moreLabel and anything else in `videos` keep their places and
    # values, as do the articles and the note.
    videos = data.setdefault("videos", {})
    for field in ("heading", "kicker", "items"):
        videos[field] = payload[field]


# What each editor reads and writes: its file, the part of it sent to the
# editor, and how a save is checked and applied.
RESOURCES = {
    "/__admin/articles": {
        "file": ROOT / "content" / "media.json",
        "read": lambda d: {"articles": d.get("articles", {})},
        "check": check_articles,
        "apply": apply_articles,
    },
    "/__admin/curriculum": {
        "file": ROOT / "content" / "curriculum.json",
        "read": lambda d: {"years": d.get("years", [])},
        "check": check_curriculum,
        "apply": apply_curriculum,
    },
    "/__admin/teachers": {
        "file": ROOT / "content" / "teachers.json",
        "read": lambda d: {k: d.get(k, [] if k == "teachers" else "") for k in ("heading", "kicker", "teachers")},
        "check": check_teachers,
        "apply": apply_teachers,
    },
    "/__admin/videos": {
        "file": ROOT / "content" / "media.json",
        "read": read_videos,
        "check": check_videos,
        "apply": apply_videos,
    },
    "/__admin/testimonies": {
        "file": ROOT / "content" / "testimonies.json",
        # `cta` (the way to graduates.html) is read so the preview draws it, never written.
        "read": lambda d: {**{k: d.get(k, [] if k == "testimonies" else "")
                              for k in ("heading", "kicker", "testimonies")}, "cta": d.get("cta")},
        "check": check_testimonies,
        "apply": apply_testimonies,
    },
    "/__admin/bookstore": {
        "file": ROOT / "content" / "bookstore.json",
        # subjectGroups goes along so the preview filters as the page does;
        # it is edited by hand and a save leaves it as it is. layouts (each
        # tab's order and large cards) is edited and saved.
        "read": lambda d: dict({k: d.get(k, [] if k == "books" else "") for k in STORE_HEAD + ("books",)},
                               subjectGroups=d.get("subjectGroups", []), layouts=d.get("layouts", {})),
        "check": check_bookstore,
        "apply": apply_bookstore,
    },
}


def check_article_lists(incoming, names):
    """Returns the first problem with the edited lists, or None."""
    if not isinstance(incoming, dict) or sorted(incoming) != sorted(names):
        return "expected the lists " + ", ".join(names)
    seen = set()
    for name in names:
        if not isinstance(incoming[name], list):
            return name + " is not a list"
        for n, a in enumerate(incoming[name], 1):
            where = "%s article %d" % (name, n)
            if not isinstance(a, dict):
                return where + " is not an object"
            if not isinstance(a.get("id"), str) or not ID_RE.match(a["id"]):
                return where + ": the id must be lowercase words joined by hyphens"
            if a["id"] in seen:
                return where + ": the id %r is used twice" % a["id"]
            seen.add(a["id"])
            if not isinstance(a.get("title"), str) or not a["title"].strip():
                return where + " has no title"
            for field in ARTICLE_TEXT:
                if field in a and not isinstance(a[field], str):
                    return where + ": %s must be text" % field
            minutes = a.get("readMinutes")
            if minutes is not None and (isinstance(minutes, bool) or not isinstance(minutes, int)
                                        or not 0 <= minutes <= 999):
                return where + ": readMinutes must be a whole number"
            body = a.get("body")
            if not isinstance(body, list):
                return where + ": body must be a list"
            for b, block in enumerate(body, 1):
                if isinstance(block, str):
                    continue
                ok = isinstance(block, dict) and (
                    (set(block) == {"heading"} and isinstance(block["heading"], str)) or
                    ("quote" in block and set(block) <= {"quote", "source"} and
                     all(isinstance(v, str) for v in block.values())))
                if not ok:
                    return where + ": block %d is not a paragraph, heading or quotation" % b
    return None


def backup(path, raw):
    BACKUPS.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    (BACKUPS / ("%s-%s.json" % (path.stem, stamp))).write_bytes(raw)
    for old in sorted(BACKUPS.glob(path.stem + "-*.json"))[:-KEEP_BACKUPS]:
        old.unlink()


def write_atomically(path, data):
    # mkstemp makes the file private (0600); give it the old file's mode, or
    # a host that keeps permissions on upload would refuse to serve it.
    mode = path.stat().st_mode & 0o777
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix="." + path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def write_new(path, data):
    """write_atomically, for a file that may not exist yet."""
    if not path.exists():
        path.write_bytes(b"")
        os.chmod(path, 0o644)
    write_atomically(path, data)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    # Nothing is cached, so edits to the CSS and JS show without a ?v= bump.
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def local(self):
        """Refuses any request whose Host (or Origin) is not this machine: a web
        page elsewhere that points a name of its own at 127.0.0.1 is kept out."""
        host = urlsplit("//" + (self.headers.get("Host") or "")).hostname
        origin = self.headers.get("Origin")
        if host not in LOCAL_HOSTS or (origin and urlsplit(origin).hostname not in LOCAL_HOSTS):
            self.send_error(403, "The admin server only answers this machine")
            return False
        return True

    def send_bytes(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_json(self, status, obj):
        self.send_bytes(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                        "application/json; charset=utf-8")

    def do_HEAD(self):
        if self.local():
            super().do_HEAD()

    def do_GET(self):
        if not self.local():
            return
        path = urlsplit(self.path).path
        if path == "/__admin/cover":
            return self.get_cover()
        if path == "/__admin/duration":
            return self.get_duration()
        if path in (DASHBOARD, DASHBOARD + "/"):
            return self.send_bytes(200, (ADMIN / "books.html").read_bytes(), "text/html; charset=utf-8")
        if path in RESOURCES:
            res = RESOURCES[path]
            raw = res["file"].read_bytes()
            return self.send_json(200, dict(res["read"](json.loads(raw)), version=version_of(raw)))
        if path.startswith("/__admin/"):
            name = path[len("/__admin/"):]
            if name not in ASSETS:
                return self.send_error(404)
            return self.send_bytes(200, (ADMIN / name).read_bytes(), ASSETS[name])
        if path in PAGES:
            page = (ROOT / (path.strip("/") or "index.html")).read_text(encoding="utf-8")
            tags = '<link rel="stylesheet" href="/__admin/editor.css">\n' + "".join(
                '<script src="/__admin/%s" defer></script>\n' % name for name in PAGES[path])
            at = page.rfind("</body>")
            page = page[:at] + tags + page[at:] if at >= 0 else page + tags
            return self.send_bytes(200, page.encode("utf-8"), "text/html; charset=utf-8")
        super().do_GET()

    def get_duration(self):
        """A YouTube or Vimeo video's length, as the videos editor shows it:
        {"duration": "10:09"}. Read from the video's own page at YouTube (no
        API key) or Vimeo's oEmbed; only the link is sent."""
        from urllib.parse import parse_qs, quote
        from urllib.request import Request, urlopen
        href = (parse_qs(urlsplit(self.path).query).get("href") or [""])[0].strip()
        yt, vimeo = YOUTUBE_RE.match(href), VIMEO_RE.match(href)
        if not yt and not vimeo:
            return self.send_json(400, {"error": "not a YouTube or Vimeo link"})
        try:
            if yt:
                url = "https://www.youtube.com/watch?v=" + yt.group(1)
            else:
                url = "https://vimeo.com/api/oembed.json?url=" + quote("https://vimeo.com/" + vimeo.group(1), safe="")
            req = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en"})
            with urlopen(req, timeout=15) as r:
                body = r.read(4 * 1024 * 1024).decode("utf-8", "replace")
        except OSError as err:
            return self.send_json(502, {"error": "couldn't reach the video (%s)" % err})
        seconds = None
        if yt:
            at = body.find('"videoDetails"')
            m = re.search(r'"lengthSeconds":"(\d+)"', body[at:] if at >= 0 else body)
            if m:
                seconds = int(m.group(1))
        else:
            try:
                seconds = int(json.loads(body).get("duration"))
            except (ValueError, TypeError, AttributeError):
                pass
        if not seconds:
            return self.send_json(404, {"error": "the video's length wasn't found (a live stream, or private?)"})
        h, rest = divmod(seconds, 3600)
        text = "%d:%02d:%02d" % (h, rest // 60, rest % 60) if h else "%d:%02d" % (rest // 60, rest % 60)
        self.send_json(200, {"duration": text, "seconds": seconds})

    def cover_source(self, name):
        """The photograph named, or None (and an error sent)."""
        if not isinstance(name, str) or not COVER_RE.match(name) or not (ROOT / name).is_file():
            self.send_json(400, {"error": "not a book's photograph: %r" % (name,)})
            return None
        return ROOT / name

    def get_cover(self):
        """A photograph's rotation and crop: its hand edit, else the crop found."""
        from urllib.parse import parse_qs
        name = (parse_qs(urlsplit(self.path).query).get("path") or [""])[0]
        src = self.cover_source(name)
        if not src:
            return
        try:
            covers = covers_module()
            edit = covers.load_edits().get(src.name)
            box = edit["box"] if edit else [round(v, 4) for v in covers.auto_box(src)]
            fill = covers.measure(src)[0]
        except ImportError as err:
            return self.send_json(500, {"error": "editing images needs Pillow and numpy (%s)" % err})
        self.send_json(200, {"path": name, "edited": bool(edit), "rotate": edit.get("rotate", 0) if edit else 0,
                             "box": box, "fill": fill})

    def put_cover(self, payload):
        """Saves a photograph's rotation and crop (or, with reset, drops it) and
        remakes its tight crop and covers.json entry."""
        src = self.cover_source(payload.get("path"))
        if not src:
            return
        edit = None
        if not payload.get("reset"):
            rotate, box = payload.get("rotate"), payload.get("box")
            num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
            if not num(rotate) or not -360 <= rotate <= 360:
                return self.send_json(400, {"error": "rotate must be degrees between -360 and 360"})
            if (not isinstance(box, list) or len(box) != 4 or not all(num(v) and 0 <= v <= 1 for v in box)
                    or box[2] - box[0] < 0.02 or box[3] - box[1] < 0.02):
                return self.send_json(400, {"error": "box must be [left, top, right, bottom] in fractions"})
            edit = {"rotate": round(rotate, 2), "box": [round(v, 4) for v in box]}
        try:
            covers = covers_module()
        except ImportError as err:
            return self.send_json(500, {"error": "editing images needs Pillow and numpy (%s)" % err})
        with write_lock:
            edits = covers.load_edits()
            changed = edits.get(src.name) != edit
            if edit:
                edits[src.name] = edit
            else:
                edits.pop(src.name, None)
            # The crop first: if it fails, nothing is saved.
            try:
                entry = covers.entry(src, edits, force=True)
            except Exception as err:
                return self.send_json(500, {"error": "the image could not be cut: %s" % err})
            if changed:
                if covers.EDITS.exists():
                    backup(covers.EDITS, covers.EDITS.read_bytes())
                write_new(covers.EDITS, (json.dumps(dict(sorted(edits.items())), indent=2) + "\n").encode("utf-8"))
            manifest_path = covers.OUT / "covers.json"
            manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
            manifest[payload["path"]] = entry
            write_new(manifest_path, (json.dumps(dict(sorted(manifest.items())), indent=2) + "\n").encode("utf-8"))
        self.send_json(200, {"entry": entry, "edited": bool(edit)})

    def put_photo(self, payload):
        """A new photograph for a book or print, from the dashboard: saved as a
        JPEG under a name not yet taken (assets/img/books/<name>.jpg, else
        <name>-v2.jpg, ...), its long side at most PHOTO_LONG_SIDE, then cut
        and entered in covers.json. bookstore.json is not touched: the
        dashboard points the book at the new path and saves that itself."""
        import base64
        import io
        name, data = payload.get("name"), payload.get("data")
        if not isinstance(name, str) or not ID_RE.match(name):
            return self.send_json(400, {"error": "the name must be lowercase words joined by hyphens"})
        if not isinstance(data, str) or not data:
            return self.send_json(400, {"error": "no image sent"})
        try:
            raw = base64.b64decode(data.split(",", 1)[-1], validate=True)
        except ValueError:
            return self.send_json(400, {"error": "the image is not valid base64"})
        try:
            from PIL import Image, ImageOps
            covers = covers_module()
        except ImportError as err:
            return self.send_json(500, {"error": "adding photographs needs Pillow and numpy (%s)" % err})
        try:
            im = Image.open(io.BytesIO(raw))
            im = ImageOps.exif_transpose(im).convert("RGB")
        except Exception as err:
            return self.send_json(400, {"error": "that file is not an image Pillow can read (%s)" % err})
        im.thumbnail((PHOTO_LONG_SIDE, PHOTO_LONG_SIDE), Image.LANCZOS)
        with write_lock:
            covers.BOOKS.mkdir(parents=True, exist_ok=True)
            stem, k = name, 1
            while (covers.BOOKS / (stem + ".jpg")).exists():
                k += 1
                stem = "%s-v%d" % (name, k)
            src = covers.BOOKS / (stem + ".jpg")
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=88, optimize=True, progressive=True)
            write_new(src, buf.getvalue())
            rel = "assets/img/books/" + src.name
            try:
                entry = covers.entry(src, force=True)
            except Exception as err:
                src.unlink()
                return self.send_json(500, {"error": "the photograph could not be cut: %s" % err})
            manifest_path = covers.OUT / "covers.json"
            manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
            manifest[rel] = entry
            write_new(manifest_path, (json.dumps(dict(sorted(manifest.items())), indent=2) + "\n").encode("utf-8"))
        self.send_json(200, {"path": rel, "entry": entry, "width": im.width, "height": im.height})

    def do_PUT(self):
        if not self.local():
            return
        path = urlsplit(self.path).path
        res = RESOURCES.get(path)
        if not res and path not in ("/__admin/cover", "/__admin/photo"):
            return self.send_error(404)
        if not (self.headers.get("Content-Type") or "").startswith("application/json"):
            return self.send_json(415, {"error": "send JSON"})
        length = int(self.headers.get("Content-Length") or 0)
        if not 0 < length <= (MAX_PHOTO if path == "/__admin/photo" else MAX_REQUEST):
            return self.send_json(413, {"error": "the request is empty or too large"})
        try:
            payload = json.loads(self.rfile.read(length))
        except ValueError:
            return self.send_json(400, {"error": "the request is not valid JSON"})
        if not isinstance(payload, dict):
            return self.send_json(400, {"error": "the request is not an object"})
        if path == "/__admin/photo":
            return self.put_photo(payload)
        if not res:
            return self.put_cover(payload)

        path = res["file"]
        with write_lock:
            raw = path.read_bytes()
            if not payload.get("force") and payload.get("version") != version_of(raw):
                return self.send_json(409, {"error": path.name + " changed on disk since it was loaded",
                                            "version": version_of(raw)})
            data = json.loads(raw)
            problem = res["check"](payload, data)
            if problem:
                return self.send_json(400, {"error": problem})
            res["apply"](payload, data)
            out = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            backup(path, raw)
            write_atomically(path, out)
        self.send_json(200, {"version": version_of(out)})


def main():
    parser = argparse.ArgumentParser(description="Serve the site with the article editor.")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print("Admin server on http://127.0.0.1:%d/" % args.port)
    print("  Edit curriculum, teachers, videos, testimonies, bookstore: the home page.  Edit article: any article's page.")
    print("  Edit bookstore: also on bookstore.html.  Edit image: any book's page.")
    print("  Saves go to content/*.json (backups in %s). Ctrl+C stops it." % BACKUPS.relative_to(ROOT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    sys.exit(main())

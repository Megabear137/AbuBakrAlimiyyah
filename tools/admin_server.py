#!/usr/bin/env python3
"""The local admin server: the site as `python3 -m http.server` serves it,
plus the article editor and the bookshelf editor.

    python3 tools/admin_server.py            # http://127.0.0.1:8001/
    python3 tools/admin_server.py --port 9000

The editors live in tools/admin/ and nothing on the public site refers to
them. This server alone adds them to the pages, on the way out (the files on
disk are never touched): editor.js to article.html, shelf.js to index.html.
It alone answers the addresses they save to, so an uploaded copy of the site
has no editor and nothing that can write. It listens on 127.0.0.1
only and refuses requests that name another host, so neither the network nor
another web page in the browser can reach it.

Saving articles replaces the article lists of content/media.json; saving the
shelf replaces the years of content/curriculum.json. Everything else in either
file stays as it is. The previous file is copied to .admin-backups/ first, and
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
ASSETS = {"editor.js": JS, "shelf.js": JS, "editor.css": CSS}
# The page, and the editor added to it as it is sent.
PAGES = {"/article.html": "editor.js", "/index.html": "shelf.js", "/": "shelf.js"}
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ARTICLE_TEXT = ("title", "subject", "author", "excerpt", "href")
BOOK_TEXT = ("title", "titleUrdu", "subject", "author", "description", "long", "cover", "color")
BOOK_SIZES = ("small", "medium", "large")

write_lock = threading.Lock()


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
            tags = ('<link rel="stylesheet" href="/__admin/editor.css">\n'
                    '<script src="/__admin/%s" defer></script>\n' % PAGES[path])
            at = page.rfind("</body>")
            page = page[:at] + tags + page[at:] if at >= 0 else page + tags
            return self.send_bytes(200, page.encode("utf-8"), "text/html; charset=utf-8")
        super().do_GET()

    def do_PUT(self):
        if not self.local():
            return
        res = RESOURCES.get(urlsplit(self.path).path)
        if not res:
            return self.send_error(404)
        if not (self.headers.get("Content-Type") or "").startswith("application/json"):
            return self.send_json(415, {"error": "send JSON"})
        length = int(self.headers.get("Content-Length") or 0)
        if not 0 < length <= MAX_REQUEST:
            return self.send_json(413, {"error": "the request is empty or too large"})
        try:
            payload = json.loads(self.rfile.read(length))
        except ValueError:
            return self.send_json(400, {"error": "the request is not valid JSON"})
        if not isinstance(payload, dict):
            return self.send_json(400, {"error": "the request is not an object"})

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
    print("  Edit curriculum: the home page.  Edit article: any article's page.")
    print("  Saves go to content/*.json (backups in %s). Ctrl+C stops it." % BACKUPS.relative_to(ROOT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    sys.exit(main())

/* =====================================================================
   shelf.js - the bookshelf editor. Only tools/admin_server.py serves this
   file and only it adds the tag that loads it to index.html, so the
   public site never carries it. "Edit curriculum" opens a panel beside
   the shelf: pick a book (click its spine, or choose it from its year's
   list) and edit it, add books, reorder them or move them to another
   year. Every change redraws the shelf with the site's own
   renderCurriculum, so the spines, the slip on hover and the folio show
   the edit as it will be published. Saving writes the years of
   content/curriculum.json through the server; nothing is written until
   Save.
   ===================================================================== */
(function () {
  "use strict";

  var API = "/__admin/curriculum";
  // The names BINDINGS in assets/js/curriculum.js knows; keep in step.
  var BINDINGS = ["lapis", "ink", "lapis-silver", "ink-silver", "petrol", "slate", "oxblood", "aubergine"];
  var SIZES = ["small", "medium", "large"];
  // Kept on a book only while they hold something.
  var OPTIONAL = ["long", "cover", "color"];

  var mount = document.querySelector('[data-slot="curriculum"]');
  var store = null;            // {version, years} as last loaded or saved
  var sel = { y: 0, b: -1 };   // the year shown in the panel, and its picked book (-1: none)
  var dirty = false, on = false, passClick = false, timer = 0;
  var ui = {};

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function el(tag, className, html) {
    var n = document.createElement(tag);
    if (className) n.className = className;
    if (html != null) n.innerHTML = html;
    return n;
  }

  function year() { return store.years[sel.y]; }
  function book() { return sel.b >= 0 ? year().books[sel.b] : null; }

  function load() {
    return fetch(API, { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }).then(function (d) { store = d; });
  }

  function status(text, bad) {
    ui.status.textContent = text;
    ui.status.classList.toggle("adm-status--bad", !!bad);
  }

  function changed() {
    if (!dirty) { dirty = true; status("Unsaved changes"); }
    clearTimeout(timer);
    timer = setTimeout(draw, 150);
  }

  /* ----------------------------- the shelf ------------------------------ */
  // Redraws the shelf from the edited years and marks the picked book.
  function draw() {
    clearTimeout(timer);
    window.renderCurriculum(mount, { years: store.years });
    var spine = spineOf(sel.y, sel.b);
    if (spine) spine.closest(".book").classList.add("adm-picked");
  }

  function spineOf(y, b) {
    var bay = mount.querySelectorAll(".bay")[y];
    var slot = bay && b >= 0 ? bay.querySelectorAll(".book")[b] : null;
    return slot ? slot.querySelector(".spine") : null;
  }

  // While editing, a spine picks its book instead of opening the folio.
  function onShelfClick(e) {
    if (!on || passClick) return;
    var slot = e.target.closest(".book");
    if (!slot) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    var bay = slot.closest(".bay");
    var y = Array.prototype.indexOf.call(mount.querySelectorAll(".bay"), bay);
    pick(y, Array.prototype.indexOf.call(bay.querySelectorAll(".book"), slot), false);
    var title = ui.panel.querySelector('[data-f="title"]');
    if (title) title.focus();
  }

  function pick(y, b, reveal) {
    sel = { y: y, b: b };
    mount.querySelectorAll(".adm-picked").forEach(function (n) { n.classList.remove("adm-picked"); });
    var spine = spineOf(y, b);
    if (spine) {
      spine.closest(".book").classList.add("adm-picked");
      if (reveal) spine.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
    }
    paintPanel();
  }

  // The folio for the picked book, as a reader would open it.
  function openFull() {
    var spine = spineOf(sel.y, sel.b);
    if (!spine) return;
    passClick = true;
    spine.click();
    passClick = false;
  }

  /* ------------------------------ the panel ----------------------------- */
  function options(values, current, labels) {
    return values.map(function (v, i) {
      return '<option value="' + esc(v) + '"' + (v === current ? " selected" : "") + ">" +
        esc(labels ? labels[i] : v) + "</option>";
    }).join("");
  }

  function paintPanel() {
    var y = year(), b = book();
    var yearNames = store.years.map(function (yr, i) { return (i + 1) + ". " + yr.name; });
    var yearIdx = store.years.map(function (yr, i) { return String(i); });
    var html =
      '<h2 class="adm-panel__head">Curriculum</h2>' +
      '<label class="adm-label">Year<select data-y="pick">' + options(yearIdx, String(sel.y), yearNames) + "</select></label>" +
      '<div class="adm-row adm-row--top">' +
      '<label class="adm-label">Name<input data-y="name" value="' + esc(y.name) + '"></label>' +
      '<label class="adm-label">Binding<select data-y="color">' + options(BINDINGS, y.color || "lapis") + "</select></label></div>" +
      '<div class="adm-label">Books<ol class="adm-books">' +
      y.books.map(function (bk, i) {
        return '<li class="adm-books__row' + (i === sel.b ? " is-picked" : "") + '">' +
          '<button class="adm-books__name" type="button" data-pick="' + i + '"' + (i === sel.b ? ' aria-current="true"' : "") + ">" +
          esc((i + 1) + ". " + (bk.title || "Untitled")) + "</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':-1" aria-label="Move earlier"' + (i === 0 ? " disabled" : "") + ">↑</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':1" aria-label="Move later"' + (i === y.books.length - 1 ? " disabled" : "") + ">↓</button></li>";
      }).join("") + "</ol>" +
      '<button class="adm-btn" type="button" data-p="add">+ Add a book to ' + esc(y.name) + "</button></div>";

    if (b) {
      html +=
        '<hr class="adm-hr"><h2 class="adm-panel__head">Book ' + (sel.b + 1) + " of " + esc(y.name) + "</h2>" +
        text("title", "Title", b.title) +
        text("titleUrdu", "Title in Urdu or Arabic", b.titleUrdu, ' dir="rtl" lang="ur" class="adm-urdu"') +
        '<div class="adm-row adm-row--top">' + text("subject", "Subject", b.subject) + text("author", "Author", b.author) + "</div>" +
        area("description", "Description", b.description, 4, "Shown on the slip beside the spine, which cuts it at six lines: keep to about two sentences.") +
        area("long", "Full description", b.long, 8, "Shown only in the full view, in place of the description. A blank line starts a new paragraph.") +
        '<div class="adm-row adm-row--top">' +
        '<label class="adm-label">Size<select data-f="book_size">' + options(SIZES, b.book_size || "medium") + "</select></label>" +
        '<label class="adm-label">Binding<select data-f="color">' +
        '<option value="">As the year (' + esc(y.color || "lapis") + ")</option>" + options(BINDINGS, b.color) + "</select></label></div>" +
        '<label class="adm-label">Cover photograph<input data-f="cover" value="' + esc(b.cover) + '" placeholder="assets/img/books/name.jpg" spellcheck="false">' +
        '<small data-cover-note>Ideally 3:4. Leave empty and the binding is drawn instead.</small></label>' +
        '<img class="adm-cover" alt="" hidden>' +
        '<label class="adm-label">Year<select data-p="move-year">' + options(yearIdx, String(sel.y), yearNames) + "</select>" +
        "<small>Another year moves the book to the end of that year’s shelf.</small></label>" +
        '<div class="adm-row adm-row--gap"><button class="adm-btn" type="button" data-p="full">Open full view</button>' +
        '<button class="adm-btn adm-btn--danger" type="button" data-p="delete">Delete book</button></div>';
    } else {
      html += '<hr class="adm-hr"><p class="adm-help">Click a spine on the shelf, or a title above, to edit that book.</p>';
    }
    html += '<hr class="adm-hr"><div class="adm-help">A title starting TODO stands as a dashed placeholder that can’t be opened. ' +
      "Changes show on the shelf as you type; hover a spine for its slip. Ctrl+S saves.</div>";
    ui.panel.innerHTML = html;
    showCover();
  }

  function text(f, label, value, extra) {
    return '<label class="adm-label">' + label + '<input data-f="' + f + '" value="' + esc(value) + '"' + (extra || "") + "></label>";
  }

  function area(f, label, value, rows, note) {
    return '<label class="adm-label">' + label + '<textarea data-f="' + f + '" rows="' + rows + '">' + esc(value) + "</textarea>" +
      "<small>" + note + "</small></label>";
  }

  // A thumbnail of the cover, or a word that the path finds nothing.
  function showCover() {
    var img = ui.panel.querySelector(".adm-cover");
    var note = ui.panel.querySelector("[data-cover-note]");
    var b = book();
    if (!img || !b) return;
    if (!b.cover) { img.hidden = true; note.classList.remove("adm-bad"); return; }
    img.onload = function () { img.hidden = false; note.classList.remove("adm-bad"); note.textContent = "Found."; };
    img.onerror = function () { img.hidden = true; note.classList.add("adm-bad"); note.textContent = "No image at that path yet."; };
    img.src = b.cover;
  }

  function onInput(e) {
    var t = e.target;
    if (t.dataset.y === "name") {
      year().name = t.value;
      var opt = ui.panel.querySelector('[data-y="pick"] option:checked');
      if (opt) opt.textContent = (sel.y + 1) + ". " + t.value;
      changed();
      return;
    }
    var f = t.dataset.f, b = book();
    if (!f || !b) return;
    if (OPTIONAL.indexOf(f) >= 0 && !t.value.trim()) delete b[f];
    else b[f] = f === "long" || f === "description" ? t.value : t.value.replace(/\s+/g, " ");
    if (f === "title") {
      var name = ui.panel.querySelector('[data-pick="' + sel.b + '"]');
      if (name) name.textContent = (sel.b + 1) + ". " + (t.value || "Untitled");
    }
    if (f === "cover") showCover();
    changed();
  }

  function onChange(e) {
    var t = e.target;
    if (t.dataset.y === "pick") return pick(+t.value, -1, true);
    if (t.dataset.y === "color") { year().color = t.value; changed(); paintPanel(); return; }
    if (t.dataset.p === "move-year") return moveToYear(+t.value);
  }

  function onClick(e) {
    var t = e.target.closest("button");
    if (!t) return;
    if (t.dataset.pick != null) return pick(sel.y, +t.dataset.pick, true);
    if (t.dataset.move) {
      var parts = t.dataset.move.split(":"), from = +parts[0], to = from + +parts[1];
      var books = year().books;
      books.splice(to, 0, books.splice(from, 1)[0]);
      if (sel.b === from) sel.b = to; else if (sel.b === to) sel.b = from;
      changed();
      draw();
      paintPanel();
      return;
    }
    var act = t.dataset.p;
    if (act === "add") addBook();
    else if (act === "delete") deleteBook();
    else if (act === "full") openFull();
  }

  function addBook() {
    var books = year().books;
    books.push({ title: "New book", titleUrdu: "", subject: "", author: "", description: "", book_size: "medium" });
    changed();
    draw();
    pick(sel.y, books.length - 1, true);
    var title = ui.panel.querySelector('[data-f="title"]');
    title.focus();
    title.select();
  }

  function deleteBook() {
    var b = book();
    if (!confirm("Delete “" + (b.title || "Untitled") + "” from " + year().name + "?\n\nIt goes from curriculum.json when you save.")) return;
    year().books.splice(sel.b, 1);
    changed();
    draw();
    pick(sel.y, Math.min(sel.b, year().books.length - 1), false);
  }

  function moveToYear(y) {
    if (y === sel.y) return;
    var b = year().books.splice(sel.b, 1)[0];
    store.years[y].books.push(b);
    changed();
    draw();
    pick(y, store.years[y].books.length - 1, true);
  }

  /* -------------------------------- saving ------------------------------ */
  function problem() {
    for (var y = 0; y < store.years.length; y++) {
      var yr = store.years[y];
      if (!String(yr.name || "").trim()) return "year " + (y + 1) + " has no name";
      for (var b = 0; b < yr.books.length; b++) {
        if (!String(yr.books[b].title || "").trim()) return yr.name + ", book " + (b + 1) + " has no title";
      }
    }
    return null;
  }

  function save(force) {
    if (ui.saving) return;
    var bad = problem();
    if (bad) { status("Not saved: " + bad, true); return; }
    ui.saving = true;
    status("Saving…");
    fetch(API, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: store.version, force: !!force, years: store.years })
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, ok: r.ok, json: j }; });
    }).then(function (res) {
      ui.saving = false;
      if (res.status === 409) {
        if (confirm("curriculum.json has changed on disk since the editor loaded it (edited by hand, or saved from another tab).\n\n" +
                    "OK overwrites it with what is here. Cancel keeps editing; Discard would load the newer file.")) {
          save(true);
        } else {
          status("Not saved: curriculum.json changed on disk", true);
        }
        return;
      }
      if (!res.ok) { status("Not saved: " + (res.json.error || "HTTP " + res.status), true); return; }
      store.version = res.json.version;
      dirty = false;
      status("Saved at " + new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    }).catch(function () {
      ui.saving = false;
      status("Not saved: is tools/admin_server.py still running?", true);
    });
  }

  function discard() {
    if (dirty && !confirm("Throw away every unsaved change to the shelf?")) return;
    load().then(function () {
      dirty = false;
      sel = { y: Math.min(sel.y, store.years.length - 1), b: -1 };
      draw();
      paintPanel();
      status("Changes discarded");
    }).catch(function () { status("Could not reload curriculum.json", true); });
  }

  // Leaving the editor reloads the page, so main.js draws what was saved.
  function done() {
    if (dirty && !confirm("Leave the editor without saving?")) return;
    dirty = false;
    location.reload();
  }

  /* -------------------------------- set-up ------------------------------ */
  function enter() {
    on = true;
    document.body.classList.add("adm-shelf");
    ui.launch.hidden = true;

    ui.panel = el("aside", "adm-panel adm-panel--shelf");
    ui.panel.setAttribute("aria-label", "Curriculum editor");
    ui.panel.addEventListener("input", onInput);
    ui.panel.addEventListener("change", onChange);
    ui.panel.addEventListener("click", onClick);
    document.body.appendChild(ui.panel);

    ui.bar = el("div", "adm-bar",
      '<span class="adm-status" role="status"></span>' +
      '<button class="adm-btn" type="button" data-bar="discard">Discard</button>' +
      '<button class="adm-btn" type="button" data-bar="done">Done</button>' +
      '<button class="adm-btn adm-btn--gold" type="button" data-bar="save" title="Save (Ctrl+S)">Save</button>');
    ui.bar.setAttribute("role", "toolbar");
    ui.bar.setAttribute("aria-label", "Curriculum editor");
    ui.bar.addEventListener("click", function (e) {
      var b = e.target.closest("[data-bar]");
      if (!b) return;
      if (b.dataset.bar === "discard") discard();
      else if (b.dataset.bar === "done") done();
      else if (b.dataset.bar === "save") save();
    });
    document.body.appendChild(ui.bar);
    ui.status = ui.bar.querySelector(".adm-status");
    status("Nothing changed yet");

    document.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") { e.preventDefault(); save(); }
    });
    window.addEventListener("beforeunload", function (e) {
      if (dirty) { e.preventDefault(); e.returnValue = ""; }
    });

    draw();
    paintPanel();
    // The panel takes the right of the screen; the page has narrowed for
    // it, so let the carousels measure again.
    window.dispatchEvent(new Event("resize"));
    document.getElementById("curriculum").scrollIntoView({ block: "start" });
  }

  // main.js draws the shelf from its own fetch; wait for it, or it could
  // draw over the editor once that has started.
  function drawn() {
    return new Promise(function (resolve) {
      var tries = 0;
      (function check() {
        if (mount.querySelector(".bay") || ++tries > 100) resolve(); else setTimeout(check, 50);
      })();
    });
  }

  function boot() {
    if (!mount || !window.renderCurriculum) return;
    mount.addEventListener("click", onShelfClick, true);
    Promise.all([load(), drawn()]).then(function () {
      ui.launch = el("button", "adm-btn adm-btn--gold adm-launch", "✎ Edit curriculum");
      ui.launch.type = "button";
      ui.launch.addEventListener("click", enter);
      document.body.appendChild(ui.launch);
    }).catch(function (err) {
      console.error("The bookshelf editor could not load curriculum.json.", err);
    });
  }

  boot();
})();

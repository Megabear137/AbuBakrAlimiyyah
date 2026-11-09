/* =====================================================================
   teachers.js - the teachers editor. Only tools/admin_server.py serves
   this file and only it adds the tag that loads it to index.html, so the
   public site never carries it. "Edit teachers" opens a panel beside the
   mosaic: pick a teacher (click their card, or choose them from the
   list) and edit them, set their card's width and height, add teachers, reorder
   them (drag a card onto another, or ↑/↓ in the list) or delete them. Every change redraws the mosaic with the site's
   own renderTeachers, so it shows the edit as it will be published.
   Each teacher's id names their page (teacher.html?id=<id>) and their
   biography is that page's text, written here as plain paragraphs split
   by blank lines, a paragraph starting "## " being a heading.
   Saving writes the heading, kicker and teachers of content/teachers.json
   through the server; nothing is written until Save.
   ===================================================================== */
(function () {
  "use strict";

  var API = "/__admin/teachers";

  var mount = document.querySelector('[data-slot="teachers"]');
  var store = null;            // {version, heading, kicker, teachers} as last loaded or saved
  var sel = -1;                // the picked teacher (-1: none)
  var dirty = false, on = false, timer = 0;
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

  function teacher() { return sel >= 0 ? store.teachers[sel] : null; }

  // An id from a name: lowercase words joined by hyphens.
  function slug(s) {
    return String(s || "").toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  }

  // The biography as the textarea shows it, and back: blocks split by a
  // blank line; {heading} is written "## heading".
  function bodyText(body) {
    return (body || []).map(function (b) { return typeof b === "string" ? b : "## " + b.heading; }).join("\n\n");
  }
  function textBody(text) {
    return text.split(/\n\s*\n/).map(function (p) { return p.replace(/\s+/g, " ").trim(); })
      .filter(Boolean).map(function (p) {
        return /^##\s/.test(p) ? { heading: p.replace(/^##\s+/, "") } : p;
      });
  }

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

  /* ----------------------------- the mosaic ----------------------------- */
  // Redraws the mosaic from the edited teachers and marks the picked one.
  function draw() {
    clearTimeout(timer);
    window.renderTeachers(store);
    // renderTeachers leaves an emptied heading or kicker as it was; show
    // them as a reader would.
    var heading = document.querySelector('[data-slot="teachers-heading"]');
    var kicker = document.querySelector('[data-slot="teachers-kicker"]');
    if (heading) heading.textContent = store.heading || "Our Teachers";
    if (kicker) kicker.textContent = store.kicker;
    var card = mount.children[sel];
    if (card) card.classList.add("adm-picked");
    // Cards drag to a new place; their links mustn't take the drag.
    Array.prototype.forEach.call(mount.children, function (c) {
      c.draggable = true;
      c.querySelectorAll("a").forEach(function (a) { a.draggable = false; });
    });
  }

  // Moves a teacher to another place in the list; the pick goes with it.
  function move(from, to) {
    var list = store.teachers, picked = teacher();
    if (to === from || to < 0 || to >= list.length) return;
    list.splice(to, 0, list.splice(from, 1)[0]);
    sel = picked ? list.indexOf(picked) : -1;
    changed();
    draw();
    paintPanel();
  }

  /* ---------------------------- dragging cards --------------------------- */
  // A card dropped on another goes before it, or after it when dropped on
  // its right half; a bar on that side shows where.
  var dragFrom = -1;

  function cardAt(e) {
    var c = e.target.closest && e.target.closest(".teacher");
    return c && c.parentNode === mount ? c : null;
  }
  function clearDrop() {
    mount.querySelectorAll(".adm-drop-before, .adm-drop-after").forEach(function (n) {
      n.classList.remove("adm-drop-before", "adm-drop-after");
    });
  }
  function dropSide(c, e) {
    var r = c.getBoundingClientRect();
    return e.clientX > r.left + r.width / 2 ? "after" : "before";
  }

  function onDragStart(e) {
    var c = on && cardAt(e);
    if (!c) return;
    dragFrom = Array.prototype.indexOf.call(mount.children, c);
    c.classList.add("adm-dragging");
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", String(dragFrom));
  }
  function onDragOver(e) {
    if (dragFrom < 0) return;
    var c = cardAt(e);
    if (!c) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    clearDrop();
    if (c !== mount.children[dragFrom]) c.classList.add("adm-drop-" + dropSide(c, e));
  }
  function onDrop(e) {
    if (dragFrom < 0) return;
    e.preventDefault();
    var c = cardAt(e), from = dragFrom;
    onDragEnd();
    if (!c) return;
    var to = Array.prototype.indexOf.call(mount.children, c) + (dropSide(c, e) === "after" ? 1 : 0);
    if (from < to) to--;
    move(from, to);
  }
  function onDragEnd() {
    dragFrom = -1;
    clearDrop();
    mount.querySelectorAll(".adm-dragging").forEach(function (n) { n.classList.remove("adm-dragging"); });
  }

  // While editing, a card picks its teacher.
  function onMosaicClick(e) {
    if (!on) return;
    var card = e.target.closest(".teacher");
    if (!card) return;
    e.preventDefault();
    pick(Array.prototype.indexOf.call(mount.children, card), false);
    var name = ui.panel.querySelector('[data-f="name"]');
    if (name) name.focus();
  }

  function pick(i, reveal) {
    sel = i;
    mount.querySelectorAll(".adm-picked").forEach(function (n) { n.classList.remove("adm-picked"); });
    var card = mount.children[i];
    if (card) {
      card.classList.add("adm-picked");
      if (reveal) card.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
    paintPanel();
  }

  /* ------------------------------ the panel ----------------------------- */
  function label(t, i) { return (i + 1) + ". " + (t.name || "Unnamed"); }

  function paintPanel() {
    var list = store.teachers, t = teacher();
    var html =
      '<h2 class="adm-panel__head">Teachers</h2>' +
      text("Heading", store.heading, ' data-s="heading"') +
      text("Kicker", store.kicker, ' data-s="kicker"', "The small line above the heading; empty hides it.") +
      '<div class="adm-label">Teachers<ol class="adm-books">' +
      list.map(function (tc, i) {
        return '<li class="adm-books__row' + (i === sel ? " is-picked" : "") + '">' +
          '<button class="adm-books__name" type="button" data-pick="' + i + '"' + (i === sel ? ' aria-current="true"' : "") + ">" +
          esc(label(tc, i)) + (tc.width > 1 || tc.height > 1
            ? ' <span class="adm-books__tag">' + (tc.width || 1) + "×" + (tc.height || 1) + "</span>" : "") + "</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':-1" aria-label="Move earlier"' + (i === 0 ? " disabled" : "") + ">↑</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':1" aria-label="Move later"' + (i === list.length - 1 ? " disabled" : "") + ">↓</button></li>";
      }).join("") + "</ol>" +
      '<button class="adm-btn" type="button" data-p="add">+ Add a teacher</button></div>';

    if (t) {
      html +=
        '<hr class="adm-hr"><h2 class="adm-panel__head">Teacher ' + (sel + 1) + "</h2>" +
        spans("width", "Width", 4, "columns") + spans("height", "Height", 3, "rows") +
        '<label class="adm-check"><input type="checkbox" data-f="bioBeside"' + (t.bioBeside ? " checked" : "") +
        ((t.width || 1) < 2 ? " disabled" : "") + "> Bio to the right of the name</label>" +
        '<p class="adm-help">For a card two or more columns wide; on phones the bio goes back underneath.</p>' +
        text("Honorific", t.honorific, ' data-f="honorific"', "The small line above the name, such as Moulana.") +
        text("Name", t.name, ' data-f="name"') +
        '<label class="adm-label">Bio<textarea data-f="bio" rows="4">' + esc(t.bio) + "</textarea>" +
        "<small>The short line on the card. May be left empty.</small></label>" +
        text("Page id", t.id, ' data-f="id"',
          "Their page is teacher.html?id=" + esc(t.id || "…") + ". Lowercase words joined by hyphens; empty: no page.") +
        '<label class="adm-label">Biography<textarea data-f="body" rows="12">' + esc(bodyText(t.body)) + "</textarea>" +
        "<small>The text of their page. A blank line starts a new paragraph; a paragraph starting ## is a heading. " +
        "**bold**, _italic_ and [words](address) work as in articles.</small></label>" +
        '<div class="adm-row adm-row--gap"><span></span>' +
        '<button class="adm-btn adm-btn--danger" type="button" data-p="delete">Delete teacher</button></div>';
    } else {
      html += '<hr class="adm-hr"><p class="adm-help">Click a card, or a name above, to edit that teacher.</p>';
    }
    html += '<hr class="adm-hr"><div class="adm-help">Drag a card onto another to move it there. A name starting TODO stands as a dashed placeholder. ' +
      "Changes show on the page as you type. Ctrl+S saves.</div>";
    ui.panel.innerHTML = html;
  }

  // A row of numbered buttons for the card's width or height in grid tracks.
  function spans(f, name, max, unit) {
    var now = teacher()[f] || 1, html = "";
    for (var n = 1; n <= max; n++) {
      html += '<button class="adm-btn" type="button" data-span="' + f + ":" + n + '" aria-pressed="' + (n === now) + '">' + n + "</button>";
    }
    return '<div class="adm-label">' + name + '<div class="adm-seg" role="group" aria-label="' + name + ' in ' + unit + '">' +
      html + "</div><small>In " + unit + (f === "width" ? " of four (two on tablets, one on phones)." : "; one on phones.") + "</small></div>";
  }

  function text(name, value, extra, note) {
    return '<label class="adm-label">' + name + '<input value="' + esc(value) + '"' + extra + ">" +
      (note ? "<small>" + note + "</small>" : "") + "</label>";
  }

  function onInput(e) {
    var t = e.target;
    if (t.dataset.s) { store[t.dataset.s] = t.value; changed(); return; }
    var f = t.dataset.f, tc = teacher();
    if (!f || !tc) return;
    if (f === "bioBeside") {
      if (t.checked) tc.bioBeside = true; else delete tc.bioBeside;
      changed();
      return;
    }
    if (f === "body") { tc.body = textBody(t.value); changed(); return; }
    if (f === "id") {
      tc.id = t.value.trim();
      if (!tc.id) delete tc.id;
      changed();
      return;
    }
    // An id that followed the name keeps following it.
    if (f === "name" && "id" in tc && (tc.id === "" || tc.id === slug(tc.name))) {
      tc.id = slug(t.value);
      var idBox = ui.panel.querySelector('[data-f="id"]');
      if (idBox) idBox.value = tc.id;
    }
    tc[f] = t.value.replace(/\s+/g, " ");
    if (f === "name") {
      var row = ui.panel.querySelector('[data-pick="' + sel + '"]');
      if (row) row.textContent = label(tc, sel);
    }
    changed();
  }

  function onClick(e) {
    var t = e.target.closest("button");
    if (!t) return;
    if (t.dataset.pick != null) return pick(+t.dataset.pick, true);
    if (t.dataset.move) {
      var parts = t.dataset.move.split(":");
      return move(+parts[0], +parts[0] + +parts[1]);
    }
    if (t.dataset.span) {
      // One is the default, so it is written by leaving the field out.
      var sp = t.dataset.span.split(":"), tc = teacher();
      if (+sp[1] > 1) tc[sp[0]] = +sp[1]; else delete tc[sp[0]];
      changed();
      draw();
      paintPanel();
      return;
    }
    if (t.dataset.p === "add") addTeacher();
    else if (t.dataset.p === "delete") deleteTeacher();
  }

  function addTeacher() {
    store.teachers.push({ id: "", honorific: "Moulana", name: "New teacher", bio: "", body: [] });
    changed();
    draw();
    pick(store.teachers.length - 1, true);
    var name = ui.panel.querySelector('[data-f="name"]');
    name.focus();
    name.select();
  }

  function deleteTeacher() {
    var t = teacher();
    if (!confirm("Delete “" + (t.name || "Unnamed") + "”?\n\nThey go from teachers.json when you save.")) return;
    store.teachers.splice(sel, 1);
    changed();
    draw();
    pick(Math.min(sel, store.teachers.length - 1), false);
  }

  /* -------------------------------- saving ------------------------------ */
  function problem() {
    var seen = {};
    for (var i = 0; i < store.teachers.length; i++) {
      var t = store.teachers[i], where = "teacher " + (i + 1);
      if (!String(t.name || "").trim()) return where + " has no name";
      if (t.id === "") delete t.id;
      if (t.id == null) continue;
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(t.id)) return where + ": the page id must be lowercase words joined by hyphens";
      if (seen[t.id]) return where + ": the page id “" + t.id + "” is used twice";
      seen[t.id] = true;
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
      body: JSON.stringify({ version: store.version, force: !!force,
                             heading: store.heading, kicker: store.kicker, teachers: store.teachers })
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, ok: r.ok, json: j }; });
    }).then(function (res) {
      ui.saving = false;
      if (res.status === 409) {
        if (confirm("teachers.json has changed on disk since the editor loaded it (edited by hand, or saved from another tab).\n\n" +
                    "OK overwrites it with what is here. Cancel keeps editing; Discard would load the newer file.")) {
          save(true);
        } else {
          status("Not saved: teachers.json changed on disk", true);
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
    if (dirty && !confirm("Throw away every unsaved change to the teachers?")) return;
    load().then(function () {
      dirty = false;
      sel = -1;
      draw();
      paintPanel();
      status("Changes discarded");
    }).catch(function () { status("Could not reload teachers.json", true); });
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
    document.body.classList.add("adm-side", "adm-teachers");
    ui.launches.hidden = true;

    ui.panel = el("aside", "adm-panel adm-panel--shelf");
    ui.panel.setAttribute("aria-label", "Teachers editor");
    ui.panel.addEventListener("input", onInput);
    ui.panel.addEventListener("click", onClick);
    document.body.appendChild(ui.panel);

    ui.bar = el("div", "adm-bar",
      '<span class="adm-status" role="status"></span>' +
      '<button class="adm-btn" type="button" data-bar="discard">Discard</button>' +
      '<button class="adm-btn" type="button" data-bar="done">Done</button>' +
      '<button class="adm-btn adm-btn--gold" type="button" data-bar="save" title="Save (Ctrl+S)">Save</button>');
    ui.bar.setAttribute("role", "toolbar");
    ui.bar.setAttribute("aria-label", "Teachers editor");
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
    // The page has narrowed for the panel; let the carousels measure again.
    window.dispatchEvent(new Event("resize"));
    document.getElementById("teachers").scrollIntoView({ block: "start" });
  }

  // main.js draws the mosaic from its own fetch; wait for it, or it could
  // draw over the editor once that has started.
  function drawn() {
    return new Promise(function (resolve) {
      var tries = 0;
      (function check() {
        if (mount.querySelector(".teacher") || ++tries > 100) resolve(); else setTimeout(check, 50);
      })();
    });
  }

  // The home page's editors share one stack of launch buttons.
  function launches() {
    return document.querySelector(".adm-launches") || document.body.appendChild(el("div", "adm-launches"));
  }

  function boot() {
    if (!mount || !window.renderTeachers) return;
    mount.addEventListener("click", onMosaicClick, true);
    mount.addEventListener("dragstart", onDragStart);
    mount.addEventListener("dragover", onDragOver);
    mount.addEventListener("drop", onDrop);
    mount.addEventListener("dragend", onDragEnd);
    Promise.all([load(), drawn()]).then(function () {
      ui.launches = launches();
      var launch = el("button", "adm-btn adm-btn--gold adm-launch", "✎ Edit teachers");
      launch.type = "button";
      launch.addEventListener("click", enter);
      ui.launches.appendChild(launch);
    }).catch(function (err) {
      console.error("The teachers editor could not load teachers.json.", err);
    });
  }

  boot();
})();

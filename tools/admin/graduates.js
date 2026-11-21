/* =====================================================================
   graduates.js - the graduates editor, on graduates.html. Only
   tools/admin_server.py serves this file and only it adds the tag that
   loads it to the page, so the public site never carries it. (It is not
   assets/js/graduates.js, the page's own script, whose renderGraduates it
   redraws with.)

   "Edit graduates" opens a panel beside the list: the heading, the titles
   set before the names, and the classes. Pick a class (click it on the
   page, or choose it from the list) to edit its year, its label and its
   brothers and sisters, one name per line, so a list can be pasted in.
   Classes can be added, reordered (oldest first) and deleted. Every change
   redraws the page as it will be published. Saving writes the heading,
   kicker, titles and classes of content/graduates.json through the
   server; nothing is written until Save.
   ===================================================================== */
(function () {
  "use strict";

  var API = "/__admin/graduates";
  var SIDES = [["brothers", "Brothers"], ["sisters", "Sisters"]];

  var mount = document.querySelector('[data-slot="graduates"]');
  var store = null;            // {version, heading, kicker, titles, classes} as last loaded or saved
  var sel = -1;                // the picked class (-1: none)
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

  function cls() { return sel >= 0 ? store.classes[sel] : null; }

  function load() {
    return fetch(API, { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }).then(function (d) {
      d.titles = d.titles || {};
      store = d;
    });
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

  /* ------------------------------ the page ------------------------------ */
  function sections() { return mount.querySelectorAll(".grad-class"); }

  // Redraws the list from the edited classes and marks the picked one.
  function draw() {
    clearTimeout(timer);
    window.renderGraduates(store);
    // renderGraduates leaves an emptied heading, or the count of an emptied
    // list, as it was; show them as a reader would.
    var heading = document.querySelector('[data-slot="graduates-heading"]');
    if (heading) heading.textContent = store.heading || "Graduates";
    if (!store.classes.length) document.querySelector('[data-slot="graduates-count"]').textContent = "";
    mark(false);
  }

  function mark(reveal) {
    mount.querySelectorAll(".adm-picked").forEach(function (n) { n.classList.remove("adm-picked"); });
    var sec = sections()[sel];
    if (!sec) return;
    sec.classList.add("adm-picked");
    if (reveal) sec.scrollIntoView({ block: "start", behavior: "smooth" });
  }

  // While editing, a class on the page picks it.
  function onPageClick(e) {
    if (!on) return;
    var sec = e.target.closest(".grad-class");
    if (!sec || !mount.contains(sec)) return;
    pick(Array.prototype.indexOf.call(sections(), sec), false);
  }

  function pick(i, reveal) {
    sel = i;
    mark(reveal);
    paintPanel();
  }

  /* ------------------------------ the panel ----------------------------- */
  function label(c) { return (c.year || "No year") + (c.label ? " · " + c.label : ""); }
  function count(n) { return n + (n === 1 ? " name" : " names"); }

  function paintPanel() {
    var list = store.classes, c = cls();
    var html =
      '<h2 class="adm-panel__head">Graduates</h2>' +
      text("Heading", store.heading, ' data-s="heading"') +
      text("Kicker", store.kicker, ' data-s="kicker"', "The small line above the heading; empty hides it.") +
      text("Brothers’ title", store.titles.brothers, ' data-t="brothers"', "Set in italic before every brother’s name.") +
      text("Sisters’ title", store.titles.sisters, ' data-t="sisters"', "Set in italic before every sister’s name.") +
      '<div class="adm-label">Classes, oldest first<ol class="adm-books">' +
      list.map(function (k, i) {
        return '<li class="adm-books__row' + (i === sel ? " is-picked" : "") + '">' +
          '<button class="adm-books__name" type="button" data-pick="' + i + '"' + (i === sel ? ' aria-current="true"' : "") + ">" +
          esc(label(k)) + "</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':-1" aria-label="Move earlier"' + (i === 0 ? " disabled" : "") + ">↑</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':1" aria-label="Move later"' + (i === list.length - 1 ? " disabled" : "") + ">↓</button></li>";
      }).join("") + "</ol>" +
      '<button class="adm-btn" type="button" data-p="add">+ Add a class</button></div>';

    if (c) {
      html +=
        '<hr class="adm-hr"><h2 class="adm-panel__head">The class of ' + esc(c.year || "…") + "</h2>" +
        text("Year", c.year, ' data-f="year" inputmode="numeric"', "Also the class’s link: graduates.html#class-" + esc(c.year || "year") + ".") +
        text("Label", c.label, ' data-f="label"', "The line under the year, e.g. “Twelfth Graduating Class”.") +
        SIDES.map(function (side) {
          var names = c[side[0]] || [];
          return '<label class="adm-label">' + side[1] +
            '<textarea data-n="' + side[0] + '" rows="' + Math.min(14, Math.max(4, names.length + 1)) + '" spellcheck="false">' +
            esc(names.join("\n")) + "</textarea>" +
            '<small data-count="' + side[0] + '">' + count(names.length) + ". One name per line, without the title; " +
            "an empty list drops the column.</small></label>";
        }).join("") +
        '<div class="adm-row adm-row--gap"><span></span>' +
        '<button class="adm-btn adm-btn--danger" type="button" data-p="delete">Delete class</button></div>';
    } else {
      html += '<hr class="adm-hr"><p class="adm-help">Click a class on the page, or a year above, to edit it.</p>';
    }
    html += '<hr class="adm-hr"><div class="adm-help">The count of graduates and the row of years are worked out from the classes. ' +
      "Changes show on the page as you type. Ctrl+S saves.</div>";
    ui.panel.innerHTML = html;
  }

  function text(name, value, extra, note) {
    return '<label class="adm-label">' + name + '<input value="' + esc(value) + '"' + extra + ">" +
      (note ? "<small>" + note + "</small>" : "") + "</label>";
  }

  function names(value) {
    return value.split("\n").map(function (n) { return n.replace(/\s+/g, " ").trim(); }).filter(Boolean);
  }

  function onInput(e) {
    var t = e.target, c = cls();
    if (t.dataset.s) { store[t.dataset.s] = t.value; changed(); return; }
    if (t.dataset.t) { store.titles[t.dataset.t] = t.value.replace(/\s+/g, " ").trim(); changed(); return; }
    if (!c) return;
    if (t.dataset.n) {
      c[t.dataset.n] = names(t.value);
      var small = ui.panel.querySelector('[data-count="' + t.dataset.n + '"]');
      if (small) small.firstChild.textContent = count(c[t.dataset.n].length) + ". One name per line, without the title; " +
        "an empty list drops the column.";
      changed();
      return;
    }
    var f = t.dataset.f;
    if (!f) return;
    c[f] = f === "year" ? t.value.replace(/\s+/g, "") : t.value.replace(/\s+/g, " ");
    var row = ui.panel.querySelector('[data-pick="' + sel + '"]');
    if (row) row.textContent = label(c);
    if (f === "year") ui.panel.querySelectorAll(".adm-panel__head")[1].textContent = "The class of " + (c.year || "…");
    changed();
  }

  function onClick(e) {
    var t = e.target.closest("button");
    if (!t) return;
    if (t.dataset.pick != null) return pick(+t.dataset.pick, true);
    if (t.dataset.move) {
      var parts = t.dataset.move.split(":"), from = +parts[0], to = from + +parts[1];
      var list = store.classes;
      list.splice(to, 0, list.splice(from, 1)[0]);
      if (sel === from) sel = to; else if (sel === to) sel = from;
      changed();
      draw();
      paintPanel();
      return;
    }
    if (t.dataset.p === "add") addClass();
    else if (t.dataset.p === "delete") deleteClass();
  }

  // A new class goes at the end, a year after the last; its label and names
  // are left for the masjid's list.
  function addClass() {
    var last = store.classes.length ? parseInt(store.classes[store.classes.length - 1].year, 10) : NaN;
    var year = isNaN(last) ? String(new Date().getFullYear()) : String(last + 1);
    store.classes.push({ year: year, label: "", brothers: [], sisters: [] });
    changed();
    draw();
    pick(store.classes.length - 1, true);
    var input = ui.panel.querySelector('[data-f="label"]');
    input.focus();
  }

  function deleteClass() {
    var c = cls(), n = (c.brothers || []).length + (c.sisters || []).length;
    if (!confirm("Delete the class of " + (c.year || "(no year)") + (n ? ", with its " + count(n) : "") +
                 "?\n\nIt goes from graduates.json when you save.")) return;
    store.classes.splice(sel, 1);
    changed();
    draw();
    pick(Math.min(sel, store.classes.length - 1), false);
  }

  /* -------------------------------- saving ------------------------------ */
  function problem() {
    var seen = {};
    for (var i = 0; i < store.classes.length; i++) {
      var y = store.classes[i].year;
      if (!y) return "class " + (i + 1) + " has no year";
      if (seen[y]) return "two classes have the year " + y;
      seen[y] = true;
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
      body: JSON.stringify({ version: store.version, force: !!force, heading: store.heading, kicker: store.kicker,
                             titles: store.titles, classes: store.classes })
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, ok: r.ok, json: j }; });
    }).then(function (res) {
      ui.saving = false;
      if (res.status === 409) {
        if (confirm("graduates.json has changed on disk since the editor loaded it (edited by hand, or saved from another tab).\n\n" +
                    "OK overwrites it with what is here. Cancel keeps editing; Discard would load the newer file.")) {
          save(true);
        } else {
          status("Not saved: graduates.json changed on disk", true);
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
    if (dirty && !confirm("Throw away every unsaved change to the graduates?")) return;
    load().then(function () {
      dirty = false;
      sel = -1;
      draw();
      paintPanel();
      status("Changes discarded");
    }).catch(function () { status("Could not reload graduates.json", true); });
  }

  // Leaving the editor reloads the page, so graduates.js draws what was saved.
  function done() {
    if (dirty && !confirm("Leave the editor without saving?")) return;
    dirty = false;
    location.reload();
  }

  /* -------------------------------- set-up ------------------------------ */
  function enter() {
    on = true;
    document.body.classList.add("adm-side", "adm-graduates");
    ui.launch.hidden = true;

    ui.panel = el("aside", "adm-panel adm-panel--shelf");
    ui.panel.setAttribute("aria-label", "Graduates editor");
    ui.panel.addEventListener("input", onInput);
    ui.panel.addEventListener("click", onClick);
    document.body.appendChild(ui.panel);

    ui.bar = el("div", "adm-bar",
      '<span class="adm-status" role="status"></span>' +
      '<button class="adm-btn" type="button" data-bar="discard">Discard</button>' +
      '<button class="adm-btn" type="button" data-bar="done">Done</button>' +
      '<button class="adm-btn adm-btn--gold" type="button" data-bar="save" title="Save (Ctrl+S)">Save</button>');
    ui.bar.setAttribute("role", "toolbar");
    ui.bar.setAttribute("aria-label", "Graduates editor");
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
  }

  // graduates.js draws the list from its own fetch; wait for it, or it could
  // draw over the editor once that has started.
  function drawn() {
    return new Promise(function (resolve) {
      var tries = 0;
      (function check() {
        if (mount.firstChild || ++tries > 100) resolve(); else setTimeout(check, 50);
      })();
    });
  }

  function boot() {
    if (!mount || !window.renderGraduates) return;
    mount.addEventListener("click", onPageClick);
    Promise.all([load(), drawn()]).then(function () {
      var box = document.querySelector(".adm-launches") || document.body.appendChild(el("div", "adm-launches"));
      ui.launch = el("button", "adm-btn adm-btn--gold adm-launch", "✎ Edit graduates");
      ui.launch.type = "button";
      ui.launch.addEventListener("click", enter);
      box.appendChild(ui.launch);
    }).catch(function (err) {
      console.error("The graduates editor could not load graduates.json.", err);
    });
  }

  boot();
})();

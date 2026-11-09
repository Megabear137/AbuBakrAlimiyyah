/* =====================================================================
   testimonies.js - the alumni testimonies editor. Only
   tools/admin_server.py serves this file and only it adds the tag that
   loads it to index.html, so the public site never carries it. "Edit
   testimonies" opens a panel beside the niches: pick a testimony (click
   its niche, or choose it from the list) and edit it, add testimonies,
   reorder them or delete them. Every change redraws the carousel with the
   site's own renderTestimonies, so it shows the edit as it will be
   published. Saving writes the heading, kicker and testimonies of
   content/testimonies.json through the server; nothing is written until
   Save.
   ===================================================================== */
(function () {
  "use strict";

  var API = "/__admin/testimonies";

  var mount = document.querySelector('[data-slot="testimonies"]');
  var store = null;            // {version, heading, kicker, testimonies} as last loaded or saved
  var sel = -1;                // the picked testimony (-1: none)
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

  function testimony() { return sel >= 0 ? store.testimonies[sel] : null; }

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

  /* ----------------------------- the section ---------------------------- */
  function slides() { return mount.querySelectorAll(".carousel__slide"); }

  function perView() {
    var w = window.innerWidth;           // as main.js's testimonies carousel
    return w < 700 ? 1 : w < 1040 ? 2 : 3;
  }

  // Redraws the carousel from the edited testimonies and marks the picked one.
  function draw() {
    clearTimeout(timer);
    ui.carousel = window.renderTestimonies(store);
    // renderTestimonies leaves an emptied heading or kicker as it was; show
    // them as a reader would.
    var heading = document.querySelector('[data-slot="testimonies-heading"]');
    var kicker = document.querySelector('[data-slot="testimonies-kicker"]');
    if (heading) heading.textContent = store.heading || "Alumni Testimonies";
    if (kicker) kicker.textContent = store.kicker;
    mark(true);
  }

  function mark(reveal) {
    mount.querySelectorAll(".adm-picked").forEach(function (n) { n.classList.remove("adm-picked"); });
    var slide = slides()[sel];
    if (!slide) return;
    slide.firstChild.classList.add("adm-picked");
    if (reveal && ui.carousel) ui.carousel.go(Math.floor(sel / perView()));
  }

  // While editing, a niche picks its testimony.
  function onSectionClick(e) {
    if (!on) return;
    var slide = e.target.closest(".carousel__slide");
    if (!slide || !mount.contains(slide)) return;
    e.preventDefault();
    pick(Array.prototype.indexOf.call(slides(), slide), false);
    var quote = ui.panel.querySelector('[data-f="quote"]');
    if (quote) quote.focus();
  }

  function pick(i, reveal) {
    sel = i;
    mark(reveal);
    if (reveal) document.getElementById("alumni").scrollIntoView({ block: "nearest", behavior: "smooth" });
    paintPanel();
  }

  /* ------------------------------ the panel ----------------------------- */
  function label(t, i) { return (i + 1) + ". " + (t.name || "Unnamed"); }

  function paintPanel() {
    var list = store.testimonies, t = testimony();
    var html =
      '<h2 class="adm-panel__head">Alumni testimonies</h2>' +
      text("Heading", store.heading, ' data-s="heading"') +
      text("Kicker", store.kicker, ' data-s="kicker"', "The small line above the heading; empty hides it.") +
      '<div class="adm-label">Testimonies<ol class="adm-books">' +
      list.map(function (tm, i) {
        return '<li class="adm-books__row' + (i === sel ? " is-picked" : "") + '">' +
          '<button class="adm-books__name" type="button" data-pick="' + i + '"' + (i === sel ? ' aria-current="true"' : "") + ">" +
          esc(label(tm, i)) + "</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':-1" aria-label="Move earlier"' + (i === 0 ? " disabled" : "") + ">↑</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':1" aria-label="Move later"' + (i === list.length - 1 ? " disabled" : "") + ">↓</button></li>";
      }).join("") + "</ol>" +
      '<button class="adm-btn" type="button" data-p="add">+ Add a testimony</button></div>';

    if (t) {
      html +=
        '<hr class="adm-hr"><h2 class="adm-panel__head">Testimony ' + (sel + 1) + "</h2>" +
        '<label class="adm-label">Quote<textarea data-f="quote" rows="6">' + esc(t.quote) + "</textarea>" +
        "<small>A few sentences; a long quote overflows its niche.</small></label>" +
        text("Name", t.name, ' data-f="name"') +
        text("Graduated", t.graduated, ' data-f="graduated"', "The year, shown as “Class of …”. May be left empty.") +
        '<div class="adm-row adm-row--gap"><span></span>' +
        '<button class="adm-btn adm-btn--danger" type="button" data-p="delete">Delete testimony</button></div>';
    } else {
      html += '<hr class="adm-hr"><p class="adm-help">Click a niche, or a name above, to edit that testimony.</p>';
    }
    html += '<hr class="adm-hr"><div class="adm-help">Three niches show at a time; the arrows page through the rest. ' +
      "Changes show on the page as you type. Ctrl+S saves.</div>";
    ui.panel.innerHTML = html;
  }

  function text(name, value, extra, note) {
    return '<label class="adm-label">' + name + '<input value="' + esc(value) + '"' + extra + ">" +
      (note ? "<small>" + note + "</small>" : "") + "</label>";
  }

  function onInput(e) {
    var t = e.target;
    if (t.dataset.s) { store[t.dataset.s] = t.value; changed(); return; }
    var f = t.dataset.f, tm = testimony();
    if (!f || !tm) return;
    tm[f] = t.value.replace(/\s+/g, " ");
    if (f === "name") {
      var row = ui.panel.querySelector('[data-pick="' + sel + '"]');
      if (row) row.textContent = label(tm, sel);
    }
    changed();
  }

  function onClick(e) {
    var t = e.target.closest("button");
    if (!t) return;
    if (t.dataset.pick != null) return pick(+t.dataset.pick, true);
    if (t.dataset.move) {
      var parts = t.dataset.move.split(":"), from = +parts[0], to = from + +parts[1];
      var list = store.testimonies;
      list.splice(to, 0, list.splice(from, 1)[0]);
      if (sel === from) sel = to; else if (sel === to) sel = from;
      changed();
      draw();
      paintPanel();
      return;
    }
    if (t.dataset.p === "add") addTestimony();
    else if (t.dataset.p === "delete") deleteTestimony();
  }

  function addTestimony() {
    store.testimonies.push({ quote: "New testimony.", name: "New name", graduated: "" });
    changed();
    draw();
    pick(store.testimonies.length - 1, true);
    var quote = ui.panel.querySelector('[data-f="quote"]');
    quote.focus();
    quote.select();
  }

  function deleteTestimony() {
    var t = testimony();
    if (!confirm("Delete the testimony of “" + (t.name || "Unnamed") + "”?\n\nIt goes from testimonies.json when you save.")) return;
    store.testimonies.splice(sel, 1);
    changed();
    draw();
    pick(Math.min(sel, store.testimonies.length - 1), false);
  }

  /* -------------------------------- saving ------------------------------ */
  function problem() {
    for (var i = 0; i < store.testimonies.length; i++) {
      var t = store.testimonies[i];
      if (!String(t.quote || "").trim()) return "testimony " + (i + 1) + " has no quote";
      if (!String(t.name || "").trim()) return "testimony " + (i + 1) + " has no name";
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
                             heading: store.heading, kicker: store.kicker, testimonies: store.testimonies })
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, ok: r.ok, json: j }; });
    }).then(function (res) {
      ui.saving = false;
      if (res.status === 409) {
        if (confirm("testimonies.json has changed on disk since the editor loaded it (edited by hand, or saved from another tab).\n\n" +
                    "OK overwrites it with what is here. Cancel keeps editing; Discard would load the newer file.")) {
          save(true);
        } else {
          status("Not saved: testimonies.json changed on disk", true);
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
    if (dirty && !confirm("Throw away every unsaved change to the testimonies?")) return;
    load().then(function () {
      dirty = false;
      sel = -1;
      draw();
      paintPanel();
      status("Changes discarded");
    }).catch(function () { status("Could not reload testimonies.json", true); });
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
    document.body.classList.add("adm-side", "adm-testimonies");
    ui.launches.hidden = true;

    ui.panel = el("aside", "adm-panel adm-panel--shelf");
    ui.panel.setAttribute("aria-label", "Testimonies editor");
    ui.panel.addEventListener("input", onInput);
    ui.panel.addEventListener("click", onClick);
    document.body.appendChild(ui.panel);

    ui.bar = el("div", "adm-bar",
      '<span class="adm-status" role="status"></span>' +
      '<button class="adm-btn" type="button" data-bar="discard">Discard</button>' +
      '<button class="adm-btn" type="button" data-bar="done">Done</button>' +
      '<button class="adm-btn adm-btn--gold" type="button" data-bar="save" title="Save (Ctrl+S)">Save</button>');
    ui.bar.setAttribute("role", "toolbar");
    ui.bar.setAttribute("aria-label", "Testimonies editor");
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
    document.getElementById("alumni").scrollIntoView({ block: "start" });
  }

  // main.js draws the carousel from its own fetch; wait for it, or it could
  // draw over the editor once that has started.
  function drawn() {
    return new Promise(function (resolve) {
      var tries = 0;
      (function check() {
        if (mount.firstChild || ++tries > 100) resolve(); else setTimeout(check, 50);
      })();
    });
  }

  // The home page's editors share one stack of launch buttons.
  function launches() {
    return document.querySelector(".adm-launches") || document.body.appendChild(el("div", "adm-launches"));
  }

  function boot() {
    if (!mount || !window.renderTestimonies) return;
    mount.addEventListener("click", onSectionClick, true);
    Promise.all([load(), drawn()]).then(function () {
      ui.launches = launches();
      var launch = el("button", "adm-btn adm-btn--gold adm-launch", "✎ Edit testimonies");
      launch.type = "button";
      launch.addEventListener("click", enter);
      ui.launches.appendChild(launch);
    }).catch(function (err) {
      console.error("The testimonies editor could not load testimonies.json.", err);
    });
  }

  boot();
})();

/* =====================================================================
   videos.js - the videos editor. Only tools/admin_server.py serves this
   file and only it adds the tag that loads it to index.html, so the
   public site never carries it. "Edit videos" opens a panel beside the
   videos: pick a video (click its card, or choose it from the list) and
   edit it, add videos, reorder them or delete one. Every change redraws
   the section with the site's own renderMedia, so it shows the edit as
   it will be published. Saving writes the heading, kicker and videos of
   content/media.json
   through the server; nothing is written until Save.
   ===================================================================== */
(function () {
  "use strict";

  var API = "/__admin/videos";

  var mount = document.querySelector('[data-slot="videos"]');
  var media = null;            // the rest of media.json, for renderMedia
  var store = null;            // {version, heading, kicker, items} as last loaded or saved
  var sel = -1;                // the picked video (-1: none)
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

  function list() { return store.items; }
  function video() { return sel >= 0 ? list()[sel] : null; }

  function load() {
    return Promise.all([
      fetch(API, { cache: "no-store" }).then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      }),
      fetch("content/media.json", { cache: "no-store" }).then(function (r) { return r.json(); })
    ]).then(function (d) {
      store = d[0];
      media = d[1];
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

  /* ----------------------------- the section ---------------------------- */
  function slides() { return mount.querySelectorAll(".carousel__slide"); }

  function perView() {
    var w = window.innerWidth;           // as main.js's videos carousel
    return w < 700 ? 1 : w < 1040 ? 2 : 3;
  }

  // Redraws both media sections with the edited videos (the articles as on
  // disk), and marks and brings round the picked video.
  function draw() {
    clearTimeout(timer);
    var videos = {};
    Object.keys(media.videos || {}).forEach(function (k) { videos[k] = media.videos[k]; });
    videos.heading = store.heading;
    videos.kicker = store.kicker;
    videos.items = store.items;
    var data = {};
    Object.keys(media).forEach(function (k) { data[k] = media[k]; });
    data.videos = videos;
    ui.handles = window.renderMedia(data);
    // renderMedia leaves an emptied heading or kicker as it was; show them
    // as a reader would.
    var heading = document.querySelector('[data-slot="videos-heading"]');
    var kicker = document.querySelector('[data-slot="videos-kicker"]');
    if (heading) heading.textContent = store.heading || "Videos";
    if (kicker) kicker.textContent = store.kicker;
    mark(true);
  }

  function mark(reveal) {
    mount.querySelectorAll(".adm-picked").forEach(function (n) { n.classList.remove("adm-picked"); });
    var slide = slides()[sel];
    if (!slide) return;
    slide.firstChild.classList.add("adm-picked");
    var carousel = ui.handles && ui.handles.videos;
    if (reveal && carousel) carousel.go(Math.floor(sel / perView()));
  }

  // While editing, a card picks its video instead of following its link.
  function onSectionClick(e) {
    if (!on) return;
    var slide = e.target.closest(".carousel__slide");
    if (!slide || !mount.contains(slide)) return;
    e.preventDefault();
    e.stopPropagation();
    pick(Array.prototype.indexOf.call(slides(), slide), false);
    var title = ui.panel.querySelector('[data-f="title"]');
    if (title) title.focus();
  }

  function pick(i, reveal) {
    sel = i;
    mark(reveal);
    if (reveal) document.getElementById("videos").scrollIntoView({ block: "nearest", behavior: "smooth" });
    paintPanel();
  }

  /* ------------------------------ the panel ----------------------------- */
  function label(v, i) { return (i + 1) + ". " + (v.title || "Untitled"); }

  function paintPanel() {
    var items = list(), v = video();
    var html =
      '<h2 class="adm-panel__head">Videos</h2>' +
      text("Heading", store.heading, ' data-s="heading"') +
      text("Kicker", store.kicker, ' data-s="kicker"', "The small line above the heading; empty hides it.") +
      '<div class="adm-label">Videos<ol class="adm-books">' +
      items.map(function (it, i) {
        return '<li class="adm-books__row' + (i === sel ? " is-picked" : "") + '">' +
          '<button class="adm-books__name" type="button" data-pick="' + i + '"' + (i === sel ? ' aria-current="true"' : "") + ">" +
          esc(label(it, i)) + "</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':-1" aria-label="Move earlier"' + (i === 0 ? " disabled" : "") + ">↑</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':1" aria-label="Move later"' + (i === items.length - 1 ? " disabled" : "") + ">↓</button></li>";
      }).join("") + "</ol>" +
      '<button class="adm-btn" type="button" data-p="add">+ Add a video</button></div>';

    if (v) {
      html +=
        '<hr class="adm-hr"><h2 class="adm-panel__head">Video ' + (sel + 1) + "</h2>" +
        text("Title", v.title, ' data-f="title"') +
        text("Subject", v.subject, ' data-f="subject"', "The line under the title.") +
        '<div class="adm-row adm-row--top">' +
          text("Date", v.date, ' data-f="date"') +
          text("Duration", v.duration, ' data-f="duration" placeholder="12:34"') +
        "</div>" +
        text("Link", v.href, ' data-f="href" placeholder="https://www.youtube.com/watch?v=…" spellcheck="false"',
          "Where the card goes, such as the video on YouTube. Empty: the card links nowhere.") +
        '<label class="adm-label">Thumbnail<input data-f="thumbnail" value="' + esc(v.thumbnail) + '" placeholder="assets/img/videos/name.jpg" spellcheck="false">' +
        "<small data-thumb-note>16:9. Leave empty for the masjid photo or a plain board.</small></label>" +
        '<img class="adm-cover adm-cover--wide" alt="" hidden>' +
        '<div class="adm-row adm-row--gap"><span></span>' +
        '<button class="adm-btn adm-btn--danger" type="button" data-p="delete">Delete video</button></div>';
    } else {
      html += '<hr class="adm-hr"><p class="adm-help">Click a card, or a title above, to edit that video.</p>';
    }
    html += '<hr class="adm-hr"><div class="adm-help">Put the newest first. A title starting TODO is a placeholder. ' +
      "Changes show on the page as you type. Ctrl+S saves.</div>";
    ui.panel.innerHTML = html;
    showThumb();
  }

  function text(name, value, extra, note) {
    return '<label class="adm-label">' + name + '<input value="' + esc(value) + '"' + extra + ">" +
      (note ? "<small>" + note + "</small>" : "") + "</label>";
  }

  // A preview of the thumbnail, or a word that the path finds nothing.
  function showThumb() {
    var img = ui.panel.querySelector(".adm-cover");
    var note = ui.panel.querySelector("[data-thumb-note]");
    var v = video();
    if (!img || !v) return;
    if (!v.thumbnail) { img.hidden = true; note.classList.remove("adm-bad"); return; }
    img.onload = function () { img.hidden = false; note.classList.remove("adm-bad"); note.textContent = "Found."; };
    img.onerror = function () { img.hidden = true; note.classList.add("adm-bad"); note.textContent = "No image at that path yet."; };
    img.src = v.thumbnail;
  }

  function onInput(e) {
    var t = e.target;
    if (t.dataset.s) { store[t.dataset.s] = t.value; changed(); return; }
    var f = t.dataset.f, v = video();
    if (!f || !v) return;
    v[f] = f === "href" || f === "thumbnail" ? t.value.trim() : t.value.replace(/\s+/g, " ");
    if (f === "title") {
      var row = ui.panel.querySelector('[data-pick="' + sel + '"]');
      if (row) row.textContent = label(v, sel);
    }
    if (f === "thumbnail") showThumb();
    changed();
  }

  function onClick(e) {
    var t = e.target.closest("button");
    if (!t) return;
    if (t.dataset.pick != null) return pick(+t.dataset.pick, true);
    if (t.dataset.move) {
      var parts = t.dataset.move.split(":"), from = +parts[0], to = from + +parts[1];
      var items = list();
      items.splice(to, 0, items.splice(from, 1)[0]);
      if (sel === from) sel = to; else if (sel === to) sel = from;
      changed();
      draw();
      paintPanel();
      return;
    }
    if (t.dataset.p === "add") addVideo();
    else if (t.dataset.p === "delete") deleteVideo();
  }

  // A new video goes first, where the newest belong.
  function addVideo() {
    list().unshift({ title: "New video", subject: "", duration: "", date: "", thumbnail: "", href: "" });
    changed();
    sel = 0;
    draw();
    pick(0, true);
    var title = ui.panel.querySelector('[data-f="title"]');
    title.focus();
    title.select();
  }

  function deleteVideo() {
    var v = video();
    if (!confirm("Delete “" + (v.title || "Untitled") + "”?\n\nIt goes from media.json when you save.")) return;
    list().splice(sel, 1);
    sel = Math.min(sel, list().length - 1);
    changed();
    draw();
    paintPanel();
  }

  /* -------------------------------- saving ------------------------------ */
  function problem() {
    var bad = null;
    store.items.some(function (v, i) {
      if (!String(v.title || "").trim()) bad = "video " + (i + 1) + " has no title";
      return bad;
    });
    return bad;
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
                             heading: store.heading, kicker: store.kicker, items: store.items })
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, ok: r.ok, json: j }; });
    }).then(function (res) {
      ui.saving = false;
      if (res.status === 409) {
        if (confirm("media.json has changed on disk since the editor loaded it (edited by hand, or saved from another tab or the article editor).\n\n" +
                    "OK overwrites its videos with what is here; its articles are kept. Cancel keeps editing; Discard would load the newer file.")) {
          save(true);
        } else {
          status("Not saved: media.json changed on disk", true);
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
    if (dirty && !confirm("Throw away every unsaved change to the videos?")) return;
    load().then(function () {
      dirty = false;
      sel = -1;
      draw();
      paintPanel();
      status("Changes discarded");
    }).catch(function () { status("Could not reload media.json", true); });
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
    document.body.classList.add("adm-side", "adm-videos");
    ui.launches.hidden = true;

    ui.panel = el("aside", "adm-panel adm-panel--shelf");
    ui.panel.setAttribute("aria-label", "Videos editor");
    ui.panel.addEventListener("input", onInput);
    ui.panel.addEventListener("click", onClick);
    document.body.appendChild(ui.panel);

    ui.bar = el("div", "adm-bar",
      '<span class="adm-status" role="status"></span>' +
      '<button class="adm-btn" type="button" data-bar="discard">Discard</button>' +
      '<button class="adm-btn" type="button" data-bar="done">Done</button>' +
      '<button class="adm-btn adm-btn--gold" type="button" data-bar="save" title="Save (Ctrl+S)">Save</button>');
    ui.bar.setAttribute("role", "toolbar");
    ui.bar.setAttribute("aria-label", "Videos editor");
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
    document.getElementById("videos").scrollIntoView({ block: "start" });
  }

  // main.js draws the section from its own fetch; wait for it, or it could
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
    if (!mount || !window.renderMedia) return;
    mount.addEventListener("click", onSectionClick, true);
    Promise.all([load(), drawn()]).then(function () {
      ui.launches = launches();
      var launch = el("button", "adm-btn adm-btn--gold adm-launch", "✎ Edit videos");
      launch.type = "button";
      launch.addEventListener("click", enter);
      ui.launches.appendChild(launch);
    }).catch(function (err) {
      console.error("The videos editor could not load media.json.", err);
    });
  }

  boot();
})();

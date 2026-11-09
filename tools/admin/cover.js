/* =====================================================================
   cover.js - "Edit image" on book.html, added by tools/admin_server.py
   only. It opens the photograph of the print that is showing (the book's
   own, for a book of one print) whole, as it is in assets/img/books/, with
   tools to turn it (a quarter at a time, and straightened by up to 45°
   either way) and to crop it (drag the frame, its edges and corners, or
   drag out a new one). Saving sends the turn and the crop to the server,
   which keeps them in tools/cover_edits.json and remakes the tight crop
   (tools/covers.py) that the bookstore's cards and this page show; the
   photograph itself is never changed. "Automatic" drops the edit and goes
   back to the crop covers.py finds. The page reloads to show the result.
   ===================================================================== */
(function () {
  "use strict";

  var API = "/__admin/cover";

  function el(tag, className, html) {
    var n = document.createElement(tag);
    if (className) n.className = className;
    if (html != null) n.innerHTML = html;
    return n;
  }

  function button(label, className, title) {
    var b = el("button", "adm-btn" + (className ? " " + className : ""), label);
    b.type = "button";
    if (title) { b.title = title; b.setAttribute("aria-label", title); }
    return b;
  }

  function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }

  function request(method, url, body) {
    return fetch(url, {
      method: method,
      cache: "no-store",
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) throw new Error(j.error || "HTTP " + r.status);
        return j;
      });
    });
  }

  /* ----------------------------- the book ------------------------------ */
  var book = null;

  // As book.js reads them; keep in step.
  function printsOf(b) {
    if (Array.isArray(b.prints) && b.prints.length) return b.prints;
    return [{ edition: b.edition, cover: b.cover }];
  }

  // The print showing: the pressed one in the row, else the address's ?print=.
  function current() {
    var k = (parseInt(new URLSearchParams(location.search).get("print"), 10) || 1) - 1;
    document.querySelectorAll(".b-print").forEach(function (btn, n) {
      if (btn.getAttribute("aria-pressed") === "true") k = n;
    });
    var prints = book ? printsOf(book) : [];
    return { index: k, print: prints[k] || {}, many: prints.length > 1 };
  }

  /* ----------------------------- the editor ---------------------------- */
  var MIN = 0.03;  // the smallest crop, as a fraction of a side
  var ui = {}, st = null;

  // The photograph turned clockwise by st.quarter * 90 + st.fine degrees,
  // on a canvas grown to hold it with the table's colour in the corners:
  // as tools/covers.py turns it.
  function turned() {
    var img = st.img, deg = st.quarter * 90 + st.fine, rad = deg * Math.PI / 180;
    var W = img.naturalWidth, H = img.naturalHeight;
    var c = Math.abs(Math.cos(rad)), s = Math.abs(Math.sin(rad));
    var w = Math.round(W * c + H * s), h = Math.round(W * s + H * c);
    var cv = document.createElement("canvas");
    cv.width = w; cv.height = h;
    var g = cv.getContext("2d");
    g.fillStyle = st.fill;
    g.fillRect(0, 0, w, h);
    g.translate(w / 2, h / 2);
    g.rotate(rad);
    g.imageSmoothingQuality = "high";
    g.drawImage(img, -W / 2, -H / 2);
    return cv;
  }

  function redraw() {
    st.src = turned();
    var room = ui.stage.getBoundingClientRect();
    var scale = Math.min((room.width - 24) / st.src.width, (room.height - 24) / st.src.height);
    var w = Math.max(1, Math.floor(st.src.width * scale)), h = Math.max(1, Math.floor(st.src.height * scale));
    var dpr = window.devicePixelRatio || 1;
    ui.canvas.width = Math.round(w * dpr);
    ui.canvas.height = Math.round(h * dpr);
    ui.canvas.style.width = w + "px";
    ui.canvas.style.height = h + "px";
    ui.canvas.getContext("2d").drawImage(st.src, 0, 0, ui.canvas.width, ui.canvas.height);
    ui.frame.style.width = w + "px";
    ui.frame.style.height = h + "px";
    ui.angle.value = String(st.fine);
    ui.angleOut.textContent = (st.fine > 0 ? "+" : "") + st.fine.toFixed(1) + "°";
    place();
  }

  function place() {
    var b = st.box;
    ui.crop.style.left = b[0] * 100 + "%";
    ui.crop.style.top = b[1] * 100 + "%";
    ui.crop.style.width = (b[2] - b[0]) * 100 + "%";
    ui.crop.style.height = (b[3] - b[1]) * 100 + "%";
    var pw = Math.round((b[2] - b[0]) * st.src.width), ph = Math.round((b[3] - b[1]) * st.src.height);
    ui.size.textContent = pw + " × " + ph + " px";
    // The result, as the bookstore will show it.
    var max = 150, k = Math.min(max / pw, max * 1.6 / ph);
    ui.preview.width = Math.max(1, Math.round(pw * k));
    ui.preview.height = Math.max(1, Math.round(ph * k));
    ui.preview.getContext("2d").drawImage(st.src, b[0] * st.src.width, b[1] * st.src.height, pw, ph,
      0, 0, ui.preview.width, ui.preview.height);
  }

  // A quarter turn carries the crop round with the picture.
  function quarter(dir) {
    var b = st.box;
    st.box = dir > 0 ? [1 - b[3], b[0], 1 - b[1], b[2]] : [b[1], 1 - b[2], b[3], 1 - b[0]];
    st.quarter = (st.quarter + dir + 4) % 4;
    redraw();
  }

  /* --------------------------- dragging the crop ------------------------ */
  // mode: "move", a side or corner ("n", "se", ...), or "new" (dragged out).
  function startDrag(e, mode) {
    if (e.button !== 0) return;
    e.preventDefault();
    e.stopPropagation();
    var r = ui.frame.getBoundingClientRect();
    var at = function (ev) {
      return [clamp((ev.clientX - r.left) / r.width, 0, 1), clamp((ev.clientY - r.top) / r.height, 0, 1)];
    };
    var p0 = at(e), b0 = st.box.slice();
    if (mode === "new") { b0 = [p0[0], p0[1], p0[0], p0[1]]; mode = "se"; }
    function move(ev) {
      var p = at(ev), dx = p[0] - p0[0], dy = p[1] - p0[1], b = b0.slice();
      if (mode === "move") {
        dx = clamp(dx, -b0[0], 1 - b0[2]);
        dy = clamp(dy, -b0[1], 1 - b0[3]);
        b = [b0[0] + dx, b0[1] + dy, b0[2] + dx, b0[3] + dy];
      } else {
        if (mode.indexOf("w") >= 0) b[0] = clamp(b0[0] + dx, 0, b0[2] - MIN);
        if (mode.indexOf("e") >= 0) b[2] = clamp(b0[2] + dx, b0[0] + MIN, 1);
        if (mode.indexOf("n") >= 0) b[1] = clamp(b0[1] + dy, 0, b0[3] - MIN);
        if (mode.indexOf("s") >= 0) b[3] = clamp(b0[3] + dy, b0[1] + MIN, 1);
      }
      st.box = b;
      place();
    }
    function up() {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      window.removeEventListener("pointercancel", up);
    }
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    window.addEventListener("pointercancel", up);
  }

  // Arrow keys nudge the crop (Shift: its far corner, to resize).
  function onCropKey(e) {
    var d = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[e.key];
    if (!d) return;
    e.preventDefault();
    var step = 0.005, b = st.box.slice();
    if (e.shiftKey) {
      b[2] = clamp(b[2] + d[0] * step, b[0] + MIN, 1);
      b[3] = clamp(b[3] + d[1] * step, b[1] + MIN, 1);
    } else {
      var dx = clamp(d[0] * step, -b[0], 1 - b[2]), dy = clamp(d[1] * step, -b[1], 1 - b[3]);
      b = [b[0] + dx, b[1] + dy, b[2] + dx, b[3] + dy];
    }
    st.box = b;
    place();
  }

  /* ------------------------------ the dialog ---------------------------- */
  function build() {
    ui.dialog = el("div", "adm-img");
    ui.dialog.setAttribute("role", "dialog");
    ui.dialog.setAttribute("aria-modal", "true");
    ui.dialog.setAttribute("aria-labelledby", "adm-img-title");
    var box = el("div", "adm-img__box");
    var head = el("div", "adm-img__head");
    ui.title = el("h2", "adm-img__title");
    ui.title.id = "adm-img-title";
    ui.close = button("✕", "adm-btn--sq", "Cancel");
    head.appendChild(ui.title);
    head.appendChild(ui.close);

    ui.stage = el("div", "adm-img__stage");
    ui.frame = el("div", "adm-img__frame");
    ui.canvas = el("canvas", "adm-img__canvas");
    ui.crop = el("div", "adm-img__crop");
    ui.crop.tabIndex = 0;
    ui.crop.setAttribute("aria-label", "Crop: drag to move, arrow keys to nudge, Shift and arrow keys to resize");
    ["n", "e", "s", "w", "ne", "se", "sw", "nw"].forEach(function (h) {
      var handle = el("span", "adm-img__handle adm-img__handle--" + h);
      handle.addEventListener("pointerdown", function (e) { startDrag(e, h); });
      ui.crop.appendChild(handle);
    });
    ui.crop.addEventListener("pointerdown", function (e) { startDrag(e, "move"); });
    ui.crop.addEventListener("keydown", onCropKey);
    ui.frame.addEventListener("pointerdown", function (e) { startDrag(e, "new"); });
    ui.frame.appendChild(ui.canvas);
    ui.frame.appendChild(ui.crop);
    ui.stage.appendChild(ui.frame);

    var side = el("div", "adm-img__side");
    side.appendChild(el("p", "adm-img__label", "Rotate"));
    var turns = el("div", "adm-img__row");
    ui.left = button("⟲ 90°", "", "Rotate left a quarter turn");
    ui.right = button("⟳ 90°", "", "Rotate right a quarter turn");
    turns.appendChild(ui.left);
    turns.appendChild(ui.right);
    side.appendChild(turns);
    var fine = el("label", "adm-img__label", "Straighten ");
    ui.angleOut = el("output", "adm-img__angle");
    fine.appendChild(ui.angleOut);
    side.appendChild(fine);
    ui.angle = el("input", "adm-img__range");
    ui.angle.type = "range";
    ui.angle.min = "-45";
    ui.angle.max = "45";
    ui.angle.step = "0.5";
    ui.angle.setAttribute("aria-label", "Straighten, in degrees");
    fine.appendChild(ui.angle);
    ui.level = button("Level", "", "Straighten back to 0°");
    side.appendChild(ui.level);

    side.appendChild(el("p", "adm-img__label", "Crop"));
    ui.whole = button("Whole picture");
    side.appendChild(ui.whole);
    ui.size = el("p", "adm-img__size");
    side.appendChild(ui.size);
    side.appendChild(el("p", "adm-img__label", "Result"));
    ui.preview = el("canvas", "adm-img__preview");
    side.appendChild(ui.preview);
    ui.state = el("p", "adm-img__state");
    side.appendChild(ui.state);

    var foot = el("div", "adm-img__foot");
    ui.auto = button("Automatic", "", "Drop this edit and use the crop found by tools/covers.py");
    ui.msg = el("p", "adm-img__msg");
    ui.msg.setAttribute("role", "status");
    ui.cancel = button("Cancel");
    ui.save = button("Save image", "adm-btn--gold");
    foot.appendChild(ui.auto);
    foot.appendChild(ui.msg);
    foot.appendChild(ui.cancel);
    foot.appendChild(ui.save);

    var body = el("div", "adm-img__body");
    body.appendChild(ui.stage);
    body.appendChild(side);
    box.appendChild(head);
    box.appendChild(body);
    box.appendChild(foot);
    ui.dialog.appendChild(box);
    document.body.appendChild(ui.dialog);

    ui.left.addEventListener("click", function () { quarter(-1); });
    ui.right.addEventListener("click", function () { quarter(1); });
    ui.angle.addEventListener("input", function () { st.fine = parseFloat(ui.angle.value) || 0; redraw(); });
    ui.level.addEventListener("click", function () { st.fine = 0; redraw(); });
    ui.whole.addEventListener("click", function () { st.box = [0, 0, 1, 1]; place(); });
    ui.close.addEventListener("click", close);
    ui.cancel.addEventListener("click", close);
    ui.save.addEventListener("click", function () {
      save({ path: st.path, rotate: st.quarter * 90 + st.fine, box: st.box.map(function (v) { return +v.toFixed(4); }) });
    });
    ui.auto.addEventListener("click", function () {
      if (confirm("Drop this edit and go back to the automatic crop?")) save({ path: st.path, reset: true });
    });
    ui.dialog.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { e.preventDefault(); close(); }
      if (e.key === "Tab") trap(e);
    });
    window.addEventListener("resize", function () { if (st) redraw(); });
  }

  function trap(e) {
    var items = [].filter.call(ui.dialog.querySelectorAll("button, input, [tabindex='0']"), function (n) {
      return !n.disabled && n.offsetParent !== null;
    });
    if (!items.length) return;
    var first = items[0], last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  function busy(on, text) {
    [ui.save, ui.auto, ui.cancel, ui.left, ui.right, ui.level, ui.whole].forEach(function (b) { b.disabled = on; });
    ui.angle.disabled = on;
    ui.msg.textContent = text || "";
  }

  function open() {
    var cur = current(), path = cur.print.cover;
    if (!path) return;
    if (!ui.dialog) build();
    ui.title.textContent = "Edit image: " + book.title +
      (cur.many ? " — " + (cur.print.edition || "print " + (cur.index + 1)) : "");
    ui.opener = document.activeElement;
    ui.dialog.classList.add("is-open");
    document.documentElement.classList.add("adm-img-lock");
    ui.canvas.style.width = ui.canvas.style.height = "0";
    ui.crop.hidden = true;
    busy(true, "Loading the photograph…");
    var img = new Image();
    var loaded = new Promise(function (resolve, reject) {
      img.onload = resolve;
      img.onerror = function () { reject(new Error("the photograph " + path + " did not load")); };
    });
    img.src = "/" + path + "?t=" + Date.now();
    Promise.all([request("GET", API + "?path=" + encodeURIComponent(path)), loaded]).then(function (got) {
      var info = got[0], r = info.rotate || 0, q = Math.round(r / 90);
      st = { path: path, index: cur.index, img: img, fill: info.fill || "#808080",
             quarter: ((q % 4) + 4) % 4, fine: r - q * 90, box: info.box.slice() };
      ui.state.textContent = info.edited ? "This picture has a saved edit." : "The crop found automatically.";
      busy(false);
      ui.auto.disabled = !info.edited;
      ui.crop.hidden = false;
      redraw();
      ui.crop.focus();
    }).catch(function (err) {
      busy(false, "Could not open the image: " + err.message);
      ui.save.disabled = ui.auto.disabled = true;
    });
  }

  function close() {
    if (!ui.dialog) return;
    ui.dialog.classList.remove("is-open");
    document.documentElement.classList.remove("adm-img-lock");
    st = null;
    if (ui.opener && ui.opener.focus) ui.opener.focus();
  }

  // Saved: reload on the same print, so the page shows book.js's own
  // rendering of the new crop.
  function save(body) {
    var k = st.index;
    busy(true, "Saving…");
    request("PUT", API, body).then(function () {
      try {
        var u = new URL(location.href);
        if (k > 0 || u.searchParams.has("print")) u.searchParams.set("print", String(k + 1));
        history.replaceState(null, "", u);
      } catch (e) {}
      location.reload();
    }).catch(function (err) {
      busy(false, "Not saved: " + err.message);
    });
  }

  /* -------------------------------- boot -------------------------------- */
  function launches() {
    return document.querySelector(".adm-launches") || document.body.appendChild(el("div", "adm-launches"));
  }

  // The launch button follows the print showing: off for one without a photograph.
  function sync() {
    var cur = current();
    ui.launch.disabled = !cur.print.cover;
    ui.launch.title = cur.print.cover ? "Crop and rotate " + cur.print.cover : "This print has no photograph to edit";
  }

  function boot() {
    var id = new URLSearchParams(location.search).get("id");
    if (!id) return;
    fetch("content/bookstore.json", { cache: "no-store" }).then(function (r) { return r.json(); }).then(function (data) {
      (data.books || []).forEach(function (b) { if (!book && b.id === id) book = b; });
      if (!book) return;
      ui.launch = el("button", "adm-btn adm-btn--gold adm-launch", "✎ Edit image");
      ui.launch.type = "button";
      ui.launch.addEventListener("click", open);
      launches().appendChild(ui.launch);
      sync();
      // A click on a print (book.js's own handler runs first) moves the button with it.
      document.addEventListener("click", function (e) {
        if (e.target.closest && e.target.closest(".b-print")) setTimeout(sync, 0);
      });
    }).catch(function (err) {
      console.error("The image editor could not load bookstore.json.", err);
    });
  }

  boot();
})();

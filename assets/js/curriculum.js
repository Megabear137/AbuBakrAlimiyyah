/* =====================================================================
   curriculum.js - the seven-year bookshelf.

   Years are paired two to a row, and a lone trailing year takes a whole
   row to itself - seven years therefore give the four boards of the
   mockup. Each bay is one year; every book in the course stands on the
   shelf at once as a spine.

   A book is a slot (.book) holding its spine, a <button>. Pointing at a
   spine (or tabbing to it) draws the slip out beside it: a ruled leaf
   with the book's subject, title, Urdu name and short description. The
   slip is only a preview - one element per shelf, laid over the page
   and never focused. Clicking the spine (Enter or Space) opens the folio.

   The folio is the book at full size across the whole bay, its cover
   down the left side and its description beside it, drawn as a ruled
   manuscript leaf (design/canvas-expand/widen.html). A photographed
   cover is shown as its tight crop (tools/covers.py, which applies the
   hand edits of tools/cover_edits.json), the whole photograph until the
   crops have loaded or where a photograph has none. Where bays are
   paired the reading bay widens across the row and its neighbour narrows.
   Arrows at its foot (and the arrow keys) turn to the shelf's other books,
   wrapping round; books still marked TODO are passed over. Closing it
   returns focus to the spine of the book last shown.

   Spines are Islamic bindings, the "emerald panel" of
   design/canvas-spines/goatskin.html: a braided gilt border, a lighter
   panel, a pendant, the title in an ogee cartouche. The leather and the
   metal of the tooling come from each year's `color` (the sets
   chosen in design/canvas-spines/colours.html). Their ornament is SVG drawn at each book's exact size; the
   title and subject are HTML over it. See "8. Kitab spines" in
   styles.css. The slip is option 3 of design/canvas-spines/hover.html.
   ===================================================================== */
(function (global) {
  "use strict";

  /* The tooling. line: the frame, braid and fillets; grad: the pendant,
     lozenge and cartouche edge, top to bottom; ink/sub: the title and
     subject lettering; band/pale: the headband's metal thread and ground. */
  var METALS = {
    gold:   { line: "#d9aa48", grad: ["#f7e2a2", "#d9aa48", "#a9792a", "#e8c778"], ink: "#f4dfa2", sub: "#eccb7d", band: "#c99a3e", pale: "#f0dca4" },
    silver: { line: "#b8c0c7", grad: ["#f5f7f9", "#c4cbd1", "#848d95", "#dfe4e8"], ink: "#eef1f4", sub: "#cbd2d8", band: "#a3acb4", pale: "#e6eaee" },
    copper: { line: "#c98a5c", grad: ["#f6d6ba", "#cc8c5c", "#8a5230", "#e5b08a"], ink: "#f5dac4", sub: "#e2ae88", band: "#b8784a", pale: "#f0cfb4" }
  };

  /* A year's `color` in curriculum.json (or a book's own, which wins)
     names one of these; anything
     missing or unrecognised is bound in lapis. Each has six shades of
     [the leather at the edges and in the cartouche, the lighter panel],
     taken by the book's position in its year, so neighbours bound alike
     still read as books rather than a bar chart, and a given book keeps
     its binding on every load. Options 1, 2, 3 (oxblood), 5, 7
     (aubergine), 8 and 9 of design/canvas-spines/colours.html. */
  var NAVY = [["#07142b", "#1c3f7a"], ["#0a1a36", "#23498a"], ["#050f22", "#18376c"],
              ["#0b1d3c", "#284f92"], ["#061228", "#1a3b74"], ["#0d2144", "#2b5599"]];
  var BLACK = [["#0b0b0d", "#2a2a30"], ["#111013", "#34303a"], ["#08090b", "#23262c"],
               ["#0e0d0f", "#2f2b2e"], ["#0a0b0d", "#282b31"], ["#131215", "#38343c"]];
  var BINDINGS = {
    "lapis":        { metal: METALS.gold,   shades: NAVY },
    "ink":          { metal: METALS.gold,   shades: BLACK },
    "lapis-silver": { metal: METALS.silver, shades: NAVY },
    "ink-silver":   { metal: METALS.silver, shades: BLACK },
    "petrol":       { metal: METALS.gold,   shades: [["#03191d", "#0f5560"], ["#04222a", "#136170"], ["#021417", "#0c4a54"],
                                                     ["#052026", "#16707a"], ["#031a1f", "#105a62"], ["#062830", "#1a7a84"]] },
    "oxblood":      { metal: METALS.gold,   shades: [["#2a0709", "#6e1a1f"], ["#330a0d", "#7a2126"], ["#240507", "#611619"],
                                                     ["#2e080b", "#721d22"], ["#27060a", "#66181d"], ["#380c10", "#82262b"]] },
    "aubergine":    { metal: METALS.gold,   shades: [["#1c0b22", "#4b2458"], ["#230d2a", "#582a66"], ["#16081b", "#40204c"],
                                                     ["#1f0c1f", "#552850"], ["#190a20", "#462654"], ["#260f2c", "#5e3070"]] },
    "slate":        { metal: METALS.copper, shades: [["#14181d", "#39434e"], ["#181c20", "#434c55"], ["#101418", "#313a44"],
                                                     ["#1a1e24", "#48525e"], ["#12161a", "#363f49"], ["#1c2026", "#4c5561"]] }
  };

  /* { edge, panel, metal } for the i-th book of its year. */
  function binding(data, i) {
    var b = BINDINGS[String(data.color || "").toLowerCase()] || BINDINGS.lapis;
    var shade = b.shades[i % b.shades.length];
    return { edge: shade[0], panel: shade[1], metal: b.metal };
  }
  /* A book's footprint on the shelf comes from `book_size` in
     curriculum.json; anything missing or unrecognised stands as medium.
     The large height has to clear .bay__well's 300px once its headband and
     the hover lift are counted - see "7. Curriculum bookshelf" in
     styles.css. The widths leave the title room to be read. */
  var SIZES = {
    small:  { w: 52, h: 236 },
    medium: { w: 56, h: 252 },
    large:  { w: 60, h: 268 }
  };

  /* A slot awaiting real content from the masjid. content/curriculum.json
     marks these by prefixing the copy with TODO:, so that is the test. */
  function isTodo(book) {
    return /^\s*TODO/i.test(String(book && book.title));
  }


  var uid = 0;          // ids for the gradients and patterns in each drawing
  var folioCount = 0;   // ids for the folio headings

  // The tight crops by photograph (assets/img/books/tight/covers.json),
  // fetched once, when the shelf is first drawn.
  var tight = null;
  function loadTight() {
    if (tight) return;
    tight = {};
    fetch("assets/img/books/tight/covers.json", { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (m) { tight = m || {}; })
      .catch(function () {});
  }

  function renderCurriculum(mount, data) {
    if (!mount || !data || !data.years) return;
    loadTight();
    mount.textContent = "";
    if (mount._slip) mount._slip.destroy();

    var slip = createSlip();
    mount._slip = slip;
    var folio = null;   // the open folio, shelf-wide

    function openFolio(book, keep) {
      slip.hide();
      var turning = !!(folio && keep);
      closeFolio(false);
      var bay = book.closest(".bay");
      var row = bay.parentNode;
      var well = bay.querySelector(".bay__well");
      // The books of this shelf that can be opened, for the arrows.
      var shelf = Array.prototype.filter.call(well.querySelectorAll(".book"), function (b) {
        return !isTodo(b._book);
      });
      var at = shelf.indexOf(book);
      var el = buildFolio(book._book, book._index, at, shelf.length);
      if (turning) el.classList.add("folio--turn");

      function step(by) {
        openFolio(shelf[(at + by + shelf.length) % shelf.length], by < 0 ? ".folio__prev" : ".folio__next");
      }
      el.querySelector(".folio__close").addEventListener("click", function () { closeFolio(true); });
      if (shelf.length > 1) {
        el.querySelector(".folio__prev").addEventListener("click", function () { step(-1); });
        el.querySelector(".folio__next").addEventListener("click", function () { step(1); });
      }
      el.addEventListener("keydown", function (e) {
        if (e.key === "Escape") { e.preventDefault(); closeFolio(true); }
        else if (shelf.length > 1 && (e.key === "ArrowLeft" || e.key === "ArrowRight") &&
                 !e.altKey && !e.ctrlKey && !e.metaKey) {
          e.preventDefault();
          step(e.key === "ArrowLeft" ? -1 : 1);
        }
      });

      well.hidden = true;
      bay.insertBefore(el, well);
      if (!row.classList.contains("shelf--single")) {
        row.classList.add(bay === row.firstElementChild ? "shelf--reading-l" : "shelf--reading-r");
      }
      // The roving tab stop follows the book, so closing returns to it.
      Array.prototype.forEach.call(well.querySelectorAll(".spine"), function (s) {
        s.tabIndex = s === book._spine ? 0 : -1;
      });
      book._spine.setAttribute("aria-expanded", "true");
      folio = { el: el, book: book, well: well, row: row };
      (el.querySelector(keep || ".folio__close") || el.querySelector(".folio__close")).focus({ preventScroll: turning });
    }

    function closeFolio(refocus) {
      if (!folio) return;
      folio.el.remove();
      folio.well.hidden = false;
      folio.row.classList.remove("shelf--reading-l", "shelf--reading-r");
      folio.book._spine.setAttribute("aria-expanded", "false");
      var book = folio.book;
      folio = null;
      if (refocus) book._spine.focus();
    }

    var ctl = { openFolio: openFolio, slip: slip };

    var years = data.years;
    for (var i = 0; i < years.length; i += 2) {
      var pair = years.slice(i, i + 2);
      var row = document.createElement("div");
      row.className = "shelf" + (pair.length === 1 ? " shelf--single" : "");
      pair.forEach(function (year, j) {
        row.appendChild(buildBay(year, i + j, ctl));
      });
      mount.appendChild(row);
    }

    // On a phone the seven shelves stacked ran to four screens, so one year
    // stands at a time under a row of wooden tabs (option A of
    // design/mobile-curriculum/, tabs of style 3). The tabs are always
    // drawn; the CSS shows them, and hides the other years, only at 640px
    // and below. They are pressed buttons in a group, not a tablist: the
    // wells keep their own arrow keys.
    var bays = mount.querySelectorAll(".bay");
    var tabs = document.createElement("div");
    tabs.className = "case__tabs";
    tabs.setAttribute("role", "group");
    tabs.setAttribute("aria-label", "Year");
    years.forEach(function (year, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "case__tab";
      b.textContent = String(i + 1);
      b.setAttribute("aria-label", year.name);
      tabs.appendChild(b);
    });
    function showYear(k) {
      closeFolio(false);
      slip.hide();
      Array.prototype.forEach.call(bays, function (bay, i) { bay.classList.toggle("is-current", i === k); });
      Array.prototype.forEach.call(tabs.children, function (b, i) { b.setAttribute("aria-pressed", i === k ? "true" : "false"); });
      // A shelf hidden until now was never measured.
      fitText(bays[k]);
      edges(mount);
    }
    tabs.addEventListener("click", function (e) {
      var b = e.target.closest(".case__tab");
      if (b) showYear(Array.prototype.indexOf.call(tabs.children, b));
    });
    mount.classList.add("case--tabs");
    mount.insertBefore(tabs, mount.firstChild);
    if (bays.length) showYear(0);

    // A shelf that runs on past its bay fades at the far edge.
    mount.addEventListener("scroll", function (e) {
      if (e.target.classList && e.target.classList.contains("bay__well")) edges(mount);
    }, true);
    if (!window._shelfEdges) {
      window._shelfEdges = true;
      window.addEventListener("resize", function () {
        document.querySelectorAll(".case--tabs").forEach(edges);
      });
    }

    // The titles are fitted to their spines by measuring, so again once
    // the display face has arrived.
    fitText(mount);
    edges(mount);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { fitText(mount); edges(mount); });
  }

  function edges(scope) {
    Array.prototype.forEach.call(scope.querySelectorAll(".bay__well"), function (w) {
      w.classList.toggle("bay__well--more", w.scrollWidth - w.clientWidth - w.scrollLeft > 4);
    });
  }


  function buildBay(year, index, ctl) {
    var bay = document.createElement("div");
    bay.className = "bay";

    var well = document.createElement("div");
    well.className = "bay__well";
    well.setAttribute("role", "group");
    well.setAttribute("aria-label", year.name);

    var books = year.books || [];
    if (books.length) {
      books.forEach(function (book, i) {
        // A year's `color` binds all its books; a book may name its own.
        var bound = Object.assign({}, book, { color: book.color || year.color });
        well.appendChild(buildBook(bound, i, ctl));
      });
      wireKeys(well, ctl.slip);
      // The slip is laid over the page, so it follows its book when the
      // well scrolls sideways under it.
      well.addEventListener("scroll", ctl.slip.follow, { passive: true });
    } else {
      var empty = document.createElement("p");
      empty.className = "bay__empty";
      empty.textContent = "Being finalised";
      well.appendChild(empty);
    }

    var plank = document.createElement("div");
    plank.className = "bay__plank";

    var label = document.createElement("p");
    label.className = "bay__year";
    label.innerHTML = '<span class="bay__numeral">' + (index + 1) + "</span>" + esc(year.name);

    bay.append(well, plank, label);
    return bay;
  }

  /* A slot and its spine. The slot keeps the spine's footprint and never
     moves, so the slip is placed against it rather than against the spine,
     which leans out on hover. */
  function buildBook(data, i, ctl) {
    var todo = isTodo(data);
    var dims = SIZES[String(data.book_size || "").toLowerCase()] || SIZES.medium;
    var bind = binding(data, i);

    var book = document.createElement("div");
    book.className = "book";
    book.style.setProperty("--w", dims.w + "px");
    book.style.setProperty("--h", dims.h + "px");

    var spine = document.createElement("button");
    spine.type = "button";
    spine.className = "spine" + (todo ? " spine--todo" : "");
    spine.tabIndex = i === 0 ? 0 : -1;   // one tab stop per bay; arrows do the rest
    book.appendChild(spine);

    book._book = data;
    book._index = i;
    book._spine = spine;
    book._dims = dims;
    book._bind = bind;
    book._w = dims.w;

    if (todo) {
      // Nothing to open yet: announce it as unavailable.
      spine.innerHTML = '<span class="spine__todo">TODO</span>';
      spine.setAttribute("aria-label", "A book still to be confirmed");
      spine.setAttribute("aria-disabled", "true");
      return book;
    }

    var m = bind.metal;
    spine.style.setProperty("--c", bind.edge);
    spine.style.setProperty("--hb", bind.panel);
    spine.style.setProperty("--hm", m.band);
    spine.style.setProperty("--hm-pale", m.pale);
    spine.style.setProperty("--ink", m.ink);
    spine.style.setProperty("--ink-sub", m.sub);
    spine.innerHTML = drawSpine(data, dims.w, dims.h, bind);
    // The spine reads vertically a letter at a time; give it a flat label.
    spine.setAttribute("aria-label", data.title + (data.subject ? ", " + data.subject : ""));
    spine.setAttribute("aria-expanded", "false");

    spine.addEventListener("click", function () { ctl.openFolio(book); });
    spine.addEventListener("pointerenter", function (e) {
      if (e.pointerType !== "touch") ctl.slip.point(book);
    });
    spine.addEventListener("pointerleave", function () { ctl.slip.leave(); });
    spine.addEventListener("focus", function () {
      if (focusVisible(spine)) ctl.slip.show(book, true);
    });
    spine.addEventListener("blur", function () { ctl.slip.hide(); });
    return book;
  }

  function focusVisible(el) {
    try { return el.matches(":focus-visible"); } catch (e) { return true; }
  }

  /* Roving tabindex within a bay: the group is one tab stop, arrows move
     between its spines, and the slip follows the focus. Opening is
     deliberate - Enter or Space, never an arrow. Escape puts the slip away. */
  function wireKeys(well, slip) {
    well.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { slip.hide(); return; }

      var spines = Array.prototype.slice.call(well.querySelectorAll(".spine"));
      var current = spines.indexOf(document.activeElement);
      if (current < 0) return;

      var next = null;
      if (e.key === "ArrowRight") next = (current + 1) % spines.length;
      else if (e.key === "ArrowLeft") next = (current - 1 + spines.length) % spines.length;
      else if (e.key === "Home") next = 0;
      else if (e.key === "End") next = spines.length - 1;
      else return;

      e.preventDefault();
      spines.forEach(function (s, i) { s.tabIndex = i === next ? 0 : -1; });
      // Scroll first, then focus, so the slip is placed where the book ends up.
      spines[next].scrollIntoView({ block: "nearest", inline: "nearest" });
      spines[next].focus({ preventScroll: true });
    });
  }


  /* ------------------------------ The slip ------------------------------ */
  /* One per shelf, appended to <body> and placed in page coordinates, so the
     well's sideways scroll can't clip it. It is drawn out from behind the
     book on the right, or on the left where the right is too near the edge
     of the screen. A short delay before the first one keeps a pointer
     crossing the shelf from flashing slips; moving along the shelf after
     that swaps them at once. */
  function createSlip() {
    var el = document.createElement("div");
    el.className = "slip";
    el.setAttribute("aria-hidden", "true");   // a preview; the folio carries the text
    document.body.appendChild(el);

    var current = null, showT = 0, hideT = 0;

    // As wide as its title and Urdu need on one line, from 252px up to 460px;
    // a longer title wraps.
    function width(vw) {
      var max = Math.min(460, vw - 16);
      var head = el.querySelector(".slip__head");
      el.style.width = max + "px";
      var pad = el.clientWidth - head.clientWidth;
      head.style.width = "max-content";
      var need = head.getBoundingClientRect().width + pad;
      head.style.width = "";
      return Math.min(max, Math.max(252, Math.ceil(need)));
    }

    function place() {
      var r = current.getBoundingClientRect();
      var vw = document.documentElement.clientWidth;
      var w = Math.min(width(vw), vw - 16);
      var right = vw - r.right >= w + 12 || r.left < w + 12;
      var left = right ? r.right - 4 : r.left + 4 - w;
      left = Math.max(8, Math.min(left, vw - w - 8));
      el.style.width = w + "px";
      el.style.left = (left + global.scrollX) + "px";
      el.style.top = (r.top + 16 + global.scrollY) + "px";
      el.classList.toggle("slip--left", !right);
    }

    function show(book, byKey) {
      clearTimeout(showT);
      clearTimeout(hideT);
      if (current === book) return;
      current = book;
      el.classList.remove("slip--on");
      el.innerHTML = slipHTML(book._book, byKey);
      place();
      void el.offsetWidth;                  // so it plays in from its start
      el.classList.add("slip--on");
    }

    function hide() {
      clearTimeout(showT);
      clearTimeout(hideT);
      current = null;
      el.classList.remove("slip--on");
    }

    function follow() { if (current) place(); }
    global.addEventListener("resize", follow);

    return {
      show: show,
      hide: hide,
      follow: follow,
      point: function (book) {
        clearTimeout(hideT);
        clearTimeout(showT);
        if (current) show(book);
        else showT = setTimeout(function () { show(book); }, 120);
      },
      leave: function () {
        clearTimeout(showT);
        hideT = setTimeout(hide, 90);
      },
      destroy: function () {
        hide();
        el.remove();
        global.removeEventListener("resize", follow);
      }
    };
  }

  function slipHTML(data, byKey) {
    var by = author(data);
    return '<span class="slip__ribbon"></span>' +
      (data.subject ? '<p class="slip__subject">' + esc(data.subject) + "</p>" : "") +
      '<p class="slip__head"><span class="slip__title">' + esc(data.title) + "</span>" +
        (data.titleUrdu ? '<span class="slip__urdu" lang="ur" dir="rtl">' + esc(data.titleUrdu) + "</span>" : "") +
      "</p>" +
      (by ? '<p class="slip__author">' + esc(by) + "</p>" : "") +
      '<span class="slip__rule"></span>' +
      '<p class="slip__body">' + esc(data.description || "") + "</p>" +
      '<p class="slip__hint">' + (byKey ? "Press Enter to see more" : "Click to see more") + "</p>";
  }


  /* ------------------------------ The spine ------------------------------ */
  /* Drawn at the book's own size, so no ornament stretches: a tooled frame
     with a braid down both edges, the lighter panel inside them, a pendant
     at the head, the title in a dark ogee cartouche with a double line and
     a finial at each point, a lozenge, the subject, and a fillet at the
     foot, all in the binding's metal. Returns the SVG and the two text boxes. */
  function drawSpine(data, w, h, bind) {
    var id = ++uid, cx = w / 2;
    var x0 = 12, x1 = w - 12, yt = 42, yb = h - 66, e = 12;
    var edge = bind.edge, panel = bind.panel, GOLD = bind.metal.line;
    var svg =
      '<svg class="spine__art" width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + " " + h + '" aria-hidden="true" focusable="false">' +
        goldDefs(id, bind.metal) +
        '<pattern id="br' + id + '" width="4" height="7" patternUnits="userSpaceOnUse" y="10">' +
          '<path d="M.6 0C3.4 1.75 3.4 5.25 .6 7M3.4 0C.6 1.75 .6 5.25 3.4 7" stroke="' + GOLD + '" stroke-width=".75" fill="none"/></pattern>' +
        '<rect x="3.5" y="7.5" width="' + (w - 7) + '" height="' + (h - 12) + '" fill="none" stroke="' + GOLD + '"/>' +
        '<rect x="5.5" y="10" width="4" height="' + (h - 17) + '" fill="url(#br' + id + ')" opacity=".9"/>' +
        '<rect x="' + (w - 9.5) + '" y="10" width="4" height="' + (h - 17) + '" fill="url(#br' + id + ')" opacity=".9"/>' +
        '<rect x="10.5" y="10.5" width="' + (w - 21) + '" height="' + (h - 18) + '" fill="' + panel + '" fill-opacity=".55" stroke="' + GOLD + '" stroke-width=".5" stroke-opacity=".55"/>' +
        pendant(cx, 18, "url(#gv" + id + ")", edge, GOLD) +
        cartouche(x0, x1, yt, yb, e, edge, "url(#gv" + id + ")", GOLD) +
        lozenge(cx, h - 60, "url(#gv" + id + ")") +
        '<line x1="14" y1="' + (h - 13) + '" x2="' + (w - 14) + '" y2="' + (h - 13) + '" stroke="' + GOLD + '" stroke-width=".6" opacity=".7"/>' +
      "</svg>";
    return svg +
      textBox("spine__title", [x0 + 2, yt + e - 1, x1 - x0 - 4, yb - yt - 2 * e + 2], data.title) +
      (data.subject ? textBox("spine__subject", [11, h - 50, w - 22, 36], data.subject) : "");
  }

  function textBox(cls, b, text) {
    return '<span class="spine__box ' + cls + '" style="left:' + num(b[0]) + "px;top:" + num(b[1]) +
      "px;width:" + num(b[2]) + "px;height:" + num(b[3]) + 'px"><span>' + esc(text) + "</span></span>";
  }

  /* Titles are set as large as they fit: one line if that can be had within
     1.5px of the full size, else two lines down the spine; one that would
     still go below 14px widens its book until it doesn't. A
     subject that won't fit on one line closes up its letter-spacing, then
     takes two lines. Boxes not laid out (a hidden well)
     are left for the next call. */
  function fitText(scope) {
    Array.prototype.forEach.call(scope.querySelectorAll(".book"), function (book) {
      var spine = book._spine;
      if (!spine || !spine.clientHeight || spine.classList.contains("spine--todo")) return;
      // Start from the book's own width each time, since the fonts may have changed.
      if (book._w !== book._dims.w) widen(book, book._dims.w);
      // A title that has to wrap widens its book until its lines can be read at
      // 14px, 2px at a time and by 32px at most. (Width can't help one line.)
      while (cramped(spine.querySelector(".spine__title")) && book._w < book._dims.w + 32) {
        widen(book, book._w + 2);
      }
      var sub = spine.querySelector(".spine__subject");
      if (sub) fitBox(sub);
    });
  }

  function cramped(box) {
    var size = fitBox(box);
    return box.firstChild.style.whiteSpace === "normal" && size < 14;
  }

  // Redraws a spine at another width; the slot follows through --w.
  function widen(book, w) {
    book._w = w;
    book.style.setProperty("--w", w + "px");
    book._spine.innerHTML = drawSpine(book._book, w, book._dims.h, book._bind);
  }

  // Sets a box's text as large as fits and returns that size (0 if it never fits).
  function fitBox(box) {
    var t = box.firstChild, isTitle = box.classList.contains("spine__title");
    var max = isTitle ? 14.5 : 8.5, min = isTitle ? 10.5 : 6.5;
    function fits() { return t.scrollHeight <= box.clientHeight + 0.5 && t.scrollWidth <= box.clientWidth + 0.5; }
    function down(from, to) {
      for (var size = from; size >= to; size -= 0.5) {
        t.style.fontSize = size + "px";
        if (fits()) return size;
      }
      return 0;
    }
    var size;
    t.style.whiteSpace = "nowrap";
    t.style.letterSpacing = "";
    t.style.lineHeight = "";
    if ((size = down(max, isTitle ? max - 1.5 : max - 3))) return size;
    if (!isTitle) {
      // A long subject closes up its spacing before anything else.
      t.style.letterSpacing = "0.04em";
      if ((size = down(max, 7))) return size;
    }
    t.style.whiteSpace = "normal";
    if (isTitle) t.style.lineHeight = "1.2";   // lines that don't touch
    return down(max, min);
  }

  /* The drawing's parts, shared with the folio's cover. */
  function goldDefs(id, metal) {
    var g = metal.grad;
    return "<defs>" +
      '<linearGradient id="gv' + id + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="' + g[0] + '"/><stop offset=".45" stop-color="' + g[1] + '"/><stop offset=".8" stop-color="' + g[2] + '"/><stop offset="1" stop-color="' + g[3] + '"/></linearGradient>' +
      "</defs>";
  }

  /* A cartouche with ogee-pointed ends, from x0 to x1 and yt to yb; e is how
     far each pointed end reaches. */
  function ogee(x0, x1, yt, yb, e) {
    var cx = (x0 + x1) / 2, k = (x1 - cx) * 0.18;
    return "M" + num(cx) + " " + num(yt) +
      " C" + num(cx + k) + " " + num(yt + e * 0.55) + " " + num(x1) + " " + num(yt + e * 0.3) + " " + num(x1) + " " + num(yt + e) +
      " L" + num(x1) + " " + num(yb - e) +
      " C" + num(x1) + " " + num(yb - e * 0.3) + " " + num(cx + k) + " " + num(yb - e * 0.55) + " " + num(cx) + " " + num(yb) +
      " C" + num(cx - k) + " " + num(yb - e * 0.55) + " " + num(x0) + " " + num(yb - e * 0.3) + " " + num(x0) + " " + num(yb - e) +
      " L" + num(x0) + " " + num(yt + e) +
      " C" + num(x0) + " " + num(yt + e * 0.3) + " " + num(cx - k) + " " + num(yt + e * 0.55) + " " + num(cx) + " " + num(yt) + " Z";
  }

  function cartouche(x0, x1, yt, yb, e, fill, edge, GOLD) {
    var cx = (x0 + x1) / 2;
    return '<path d="' + ogee(x0, x1, yt, yb, e) + '" fill="' + fill + '" stroke="' + edge + '" stroke-width="1.3"/>' +
      '<path d="' + ogee(x0 + 2.6, x1 - 2.6, yt + 3.6, yb - 3.6, e - 2) + '" fill="none" stroke="' + GOLD + '" stroke-width=".55" opacity=".75"/>' +
      dot(cx, yt - 2.6, 1.3, edge) + dot(cx, yb + 2.6, 1.3, edge);
  }

  /* A stem, a bead, and a metal drop with a leather heart. */
  function pendant(cx, y, gold, heart, GOLD) {
    return '<line x1="' + cx + '" y1="' + (y - 5.5) + '" x2="' + cx + '" y2="' + y + '" stroke="' + GOLD + '" stroke-width=".8"/>' +
      dot(cx, y - 3.5, 1.3, gold) +
      '<path d="M' + cx + " " + y + "C" + (cx + 7) + " " + (y + 6) + " " + (cx + 7) + " " + (y + 13) + " " + cx + " " + (y + 18.5) +
        "C" + (cx - 7) + " " + (y + 13) + " " + (cx - 7) + " " + (y + 6) + " " + cx + " " + y + 'Z" fill="' + gold + '"/>' +
      '<path d="M' + cx + " " + (y + 5.5) + "C" + (cx + 3.2) + " " + (y + 8.5) + " " + (cx + 3.2) + " " + (y + 12) + " " + cx + " " + (y + 14.5) +
        "C" + (cx - 3.2) + " " + (y + 12) + " " + (cx - 3.2) + " " + (y + 8.5) + " " + cx + " " + (y + 5.5) + 'Z" fill="' + heart + '"/>' +
      dot(cx, y + 10.3, 0.9, gold);
  }

  function lozenge(cx, y, gold) {
    return '<path d="M' + cx + " " + y + "L" + (cx + 3.5) + " " + (y + 4) + "L" + cx + " " + (y + 8) + "L" + (cx - 3.5) + " " + (y + 4) + 'Z" fill="' + gold + '"/>';
  }

  function dot(x, y, r, fill) {
    return '<circle cx="' + num(x) + '" cy="' + num(y) + '" r="' + r + '" fill="' + fill + '"/>';
  }

  function num(n) { return Math.round(n * 100) / 100; }


  /* ------------------------------ The folio ------------------------------ */
  /* The book at full size across the bay. A ruled manuscript leaf (the
     jadwal) with the cover running down the left side, and beside it the
     subject, the title with its Urdu or Arabic name on the same line, the
     author, the description and a catchword. The year is not repeated: the
     bay's label is right beneath it. */
  function buildFolio(data, i, at, count) {
    var id = "folio-title-" + (++folioCount);
    var el = document.createElement("section");
    el.className = "folio";
    el.setAttribute("aria-labelledby", id);

    var by = author(data);
    var catchword = String(data.title || "").split(/\s+/)[0];
    el.innerHTML =
      '<button type="button" class="folio__close" aria-label="Close ' + esc(data.title) + ' in full">' +
        '<span aria-hidden="true">✕</span></button>' +
      // width/height give the box its shape before the image decodes, so a
      // phone's stacked folio doesn't jump when the cover arrives.
      coverHTML(data, i) +
      '<div class="folio__text">' +
        (data.subject ? '<p class="folio__subject">' + esc(data.subject) + "</p>" : "") +
        '<div class="folio__head">' +
          '<h3 class="folio__title" id="' + id + '">' + esc(data.title) + "</h3>" +
          (data.titleUrdu
            ? '<p class="folio__urdu" lang="ur" dir="rtl">' + esc(data.titleUrdu) + "</p>"
            : "") +
        "</div>" +
        (by ? '<p class="folio__author">' + esc(by) + "</p>" : "") +
        '<span class="folio__rule"></span>' +
        String(data.long || data.description || "").split(/\n\s*\n/).map(function (para) {
          return '<p class="folio__body">' + esc(para) + "</p>";
        }).join("") +
        '<div class="folio__foot">' +
          (count > 1
            ? '<div class="folio__turn">' +
                '<button type="button" class="folio__prev" aria-label="Previous book on this shelf">' +
                  '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M10 3 5 8l5 5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>' +
                '<span class="folio__count">' + (at + 1) + " of " + count + "</span>" +
                '<button type="button" class="folio__next" aria-label="Next book on this shelf">' +
                  '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>' +
              "</div>"
            : "") +
          '<p class="folio__catch" aria-hidden="true">' + esc(catchword) + "</p>" +
        "</div>" +
      "</div>";
    return el;
  }

  /* The folio's cover: the tight crop at its own shape (the book whole,
     never trimmed), else the photograph or the drawn binding in a 3:4 box. */
  function coverHTML(data, i) {
    var t = data.cover && tight && tight[data.cover];
    var ratio = t && t.tight && +t.ratio > 0 ? +t.ratio : 0;
    var alt = data.cover ? "Cover of " + esc(data.title) : "";
    if (ratio) {
      return '<div class="folio__cover folio__cover--tight" style="--ratio: ' + ratio + '"><img src="' + esc(t.tight) +
        '" width="300" height="' + Math.round(300 * ratio) + '" alt="' + alt + '"></div>';
    }
    return '<div class="folio__cover"><img src="' + esc(data.cover || drawnCover(data, i)) +
      '" width="300" height="400" alt="' + alt + '"></div>';
  }

  /* An author still marked TODO is not shown at all. */
  function author(data) {
    var a = String(data.author || "").trim();
    return a && !/^TODO/i.test(a) ? a : "";
  }

  /* A book with no `cover` photograph yet shows its binding face-on instead,
     the spine's drawing at 300x400: the braid, the panel, the
     pendant, the title in the cartouche and the lozenge. It is decoration
     standing in for a photograph, so its <img> has an empty alt. Webfonts
     don't reach an SVG in an <img>, so the title is set in Georgia. */
  function drawnCover(data, i) {
    var bind = binding(data, i), id = ++uid, m = bind.metal, GOLD = m.line;

    // Break the title into lines of about ten letters for the cartouche.
    var lines = [], line = "";
    String(data.title || "").split(/\s+/).forEach(function (word) {
      if (line && (line + " " + word).length > 10) { lines.push(line); line = word; }
      else line = line ? line + " " + word : word;
    });
    if (line) lines.push(line);
    lines = lines.slice(0, 3);
    var size = lines.length > 2 ? 20 : 23, lead = size + 5;
    var top = 205 - ((lines.length - 1) * lead) / 2 + size * 0.35;
    var text = lines.map(function (l, n) {
      return '<text x="150" y="' + num(top + n * lead) + '" text-anchor="middle" fill="' + m.ink + '" font-family="Georgia, serif" font-size="' +
        size + '" font-weight="600">' + esc(l) + "</text>";
    }).join("");

    var svg =
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" width="300" height="400">' + goldDefs(id, m) +
        '<filter id="n" x="0" y="0" width="100%" height="100%">' +
          '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" stitchTiles="stitch"/>' +
          '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.5 0 0 0 -0.22"/></filter>' +
        '<linearGradient id="l" x1="0" y1="0" x2="1" y2="0">' +
          '<stop offset="0" stop-opacity="0.4"/><stop offset="0.16" stop-opacity="0.04"/>' +
          '<stop offset="0.5" stop-color="#fff" stop-opacity="0.07"/><stop offset="1" stop-opacity="0.28"/></linearGradient>' +
        '<pattern id="b" width="8" height="14" patternUnits="userSpaceOnUse" y="12">' +
          '<path d="M1.2 0C6.8 3.5 6.8 10.5 1.2 14M6.8 0C1.2 3.5 1.2 10.5 6.8 14" stroke="' + GOLD + '" stroke-width="1.3" fill="none"/></pattern>' +
        '<rect width="300" height="400" fill="' + bind.edge + '"/>' +
        '<rect x="12" y="12" width="276" height="376" fill="none" stroke="' + GOLD + '" stroke-width="1.8"/>' +
        '<rect x="17" y="16" width="8" height="368" fill="url(#b)"/><rect x="275" y="16" width="8" height="368" fill="url(#b)"/>' +
        '<rect x="31" y="20" width="238" height="360" fill="' + bind.panel + '" fill-opacity=".55" stroke="' + GOLD + '"/>' +
        '<g transform="translate(150 0) scale(2.2)">' + pendant(0, 18, "url(#gv" + id + ")", bind.edge, GOLD) + "</g>" +
        cartouche(82, 218, 104, 306, 30, bind.edge, "url(#gv" + id + ")", GOLD) +
        '<g transform="translate(150 326) scale(2.2)">' + lozenge(0, 0, "url(#gv" + id + ")") + "</g>" +
        text +
        '<rect width="300" height="400" filter="url(#n)"/>' +
        '<rect width="300" height="400" fill="url(#l)"/>' +
      "</svg>";
    return "data:image/svg+xml," + encodeURIComponent(svg);
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  global.renderCurriculum = renderCurriculum;
  // The bookstore draws a book without a photograph the same way.
  renderCurriculum.drawnCover = drawnCover;
})(window);

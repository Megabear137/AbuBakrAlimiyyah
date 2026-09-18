/* =====================================================================
   curriculum.js - the seven-year bookshelf.

   Years are paired two to a row, and a lone trailing year takes a whole
   row to itself - seven years therefore give the four boards of the
   mockup. Each bay is one year; every book in the course stands on the
   shelf at once as a spine.

   A book is a slot (.book) holding its spine, a <button>. Clicking the
   spine turns the book face-on in its slot: the slot becomes a small card
   with the book's text and two real buttons - "See more" and "Close". The
   Close button IS the spine, restyled, so focus never moves when a book
   opens or closes and aria-expanded stays on the one element. One book is
   open across the whole shelf.

   "See more" opens the folio: the book at full size across the whole bay,
   its cover down the left side and its description beside it, drawn as a
   ruled manuscript leaf (design/canvas-expand/widen.html). Where bays are
   paired the reading bay widens across the row and its neighbour narrows.
   Closing the folio returns to the small card.

   Spines are drawn as Islamic kitab bindings - see "8. Kitab spines" in
   styles.css for the parts.
   ===================================================================== */
(function (global) {
  "use strict";

  /* Bindings are varied so a bay reads as books rather than a bar chart,
     and are indexed by the book's position in its year - so a given book
     keeps the same binding on every load. Each is [leather, cartouche]. */
  var BINDINGS = [
    ["#4a1813", "#1a1210"],   // oxblood, black cartouche
    ["#2c1d13", "#5a1916"],   // dark brown, red
    ["#1c2a22", "#4a1813"],   // green-black, oxblood
    ["#5e3b1f", "#1c2a22"],   // tan, green-black
    ["#16120f", "#5a1916"],   // black, red
    ["#3b2416", "#16120f"]    // chestnut, black
  ];
  /* A book's footprint on the shelf comes from `book_size` in
     curriculum.json; anything missing or unrecognised stands as medium.
     The large height has to clear .bay__well's 300px once its headband and
     the hover lift are counted - see "7. Curriculum bookshelf" in styles.css -
     and the small one is the least an open book needs for its text. */
  var SIZES = {
    small:  { w: 46, h: 236 },
    medium: { w: 50, h: 252 },
    large:  { w: 54, h: 268 }
  };

  /* Wide screens only: some planks run on past the bays and out onto the wall
     as a ledge of spare books - one per row, alternating sides. Pure
     decoration, so it is keyed to the row, not the data, and hidden from
     assistive tech. Items are listed nearest the bay first; `fit` is the
     ledge width (see .ledge in styles.css) an item needs before it shows, so
     a narrower margin drops the outermost things rather than clipping them.
     A book gives the binding to borrow, its size and whether it leans; an image gives
     its file and width. */
  var LEDGES = [
    [{ book: 5, size: "medium" }, { book: 0, size: "medium" }, { book: 3, size: "medium", fit: 1 }, { book: 1, size: "large", lean: true, fit: 3 }],
    [{ book: 2, size: "large" }, { img: "ledge-stack-ink.svg", width: 124, fit: 2 }],
    [{ book: 1, size: "large" }, { book: 4, size: "small", fit: 1 }, { img: "ledge-stack-pens.svg", width: 124, fit: 3 }],
    [{ book: 0, size: "medium" }, { book: 2, size: "large", lean: true, fit: 1 }]
  ];

  var NUMERALS = [[10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]];

  function roman(n) {
    var out = "";
    NUMERALS.forEach(function (pair) {
      while (n >= pair[0]) { out += pair[1]; n -= pair[0]; }
    });
    return out;
  }

  /* A slot awaiting real content from the masjid. content/curriculum.json
     marks these by prefixing the copy with TODO:, so that is the test. */
  function isTodo(book) {
    return /^\s*TODO/i.test(String(book && book.title));
  }


  var folioCount = 0;   // ids for the folio headings

  function renderCurriculum(mount, data) {
    if (!mount || !data || !data.years) return;
    mount.textContent = "";

    var open = null;    // the one open slot, shelf-wide
    var folio = null;   // its folio, when "See more" has been taken

    function toggle(book) {
      closeFolio(false);
      if (open && open !== book) fill(open, false);
      var wasOpen = open === book;
      open = wasOpen ? null : book;
      fill(book, !wasOpen);
    }

    /* Escape: the folio first, then the small card. Focus lands on the spine
       each time - the card's Close button while it is open, the spine after. */
    function closeOpen() {
      if (folio) { closeFolio(true); return; }
      if (!open) return;
      fill(open, false);
      open._spine.focus();
      open = null;
    }

    function openFolio(book) {
      closeFolio(false);
      var bay = book.closest(".bay");
      var row = bay.parentNode;
      var well = bay.querySelector(".bay__well");
      var el = buildFolio(book._book, book._index);

      el.querySelector(".folio__close").addEventListener("click", function () { closeFolio(true); });
      el.addEventListener("keydown", function (e) {
        if (e.key === "Escape") { e.preventDefault(); closeFolio(true); }
      });

      well.hidden = true;
      bay.insertBefore(el, well);
      if (!row.classList.contains("shelf--single")) {
        row.classList.add(bay === row.firstElementChild ? "shelf--reading-l" : "shelf--reading-r");
      }
      book._more.setAttribute("aria-expanded", "true");
      folio = { el: el, book: book, well: well, row: row };
      el.querySelector(".folio__close").focus();
    }

    function closeFolio(refocus) {
      if (!folio) return;
      folio.el.remove();
      folio.well.hidden = false;
      folio.row.classList.remove("shelf--reading-l", "shelf--reading-r");
      if (folio.book._more) folio.book._more.setAttribute("aria-expanded", "false");
      var book = folio.book;
      folio = null;
      if (refocus) book._spine.focus();
    }

    var ctl = { toggle: toggle, closeOpen: closeOpen, openFolio: openFolio };

    var years = data.years;
    for (var i = 0; i < years.length; i += 2) {
      var pair = years.slice(i, i + 2);
      var row = document.createElement("div");
      row.className = "shelf" + (pair.length === 1 ? " shelf--single" : "");
      pair.forEach(function (year, j) {
        row.appendChild(buildBay(year, i + j, ctl));
      });
      row.appendChild(buildLedge(i / 2));
      mount.appendChild(row);
    }
  }

  function buildLedge(r) {
    var side = r % 2 ? "r" : "l";
    var ledge = document.createElement("div");
    ledge.className = "ledge ledge--" + side;
    ledge.setAttribute("aria-hidden", "true");

    var items = document.createElement("div");
    items.className = "ledge__items";
    LEDGES[r % LEDGES.length].forEach(function (item) {
      var el;
      if (item.img) {
        el = document.createElement("img");
        el.src = "assets/img/" + item.img;
        el.alt = "";
        el.width = item.width;
        el.className = "ledge__art";
      } else {
        // A spare binding: the spine's parts with an empty cartouche.
        el = document.createElement("div");
        el.className = "spine spine--loose" + (item.lean ? " spine--lean" : "");
        setBinding(el, item.book, item.size);
        el.innerHTML = '<span class="spine__fin"></span><span class="spine__cart"><span class="spine__cart-in"></span></span>' +
          '<span class="spine__fin spine__fin--foot"></span><span class="spine__medal"></span>';
      }
      if (item.fit) el.classList.add("ledge__far" + item.fit);
      items.appendChild(el);
    });

    ledge.appendChild(items);
    return ledge;
  }

  function setBinding(el, i, size) {
    var binding = BINDINGS[i % BINDINGS.length];
    var dims = SIZES[String(size || "").toLowerCase()] || SIZES.medium;
    el.style.setProperty("--w", dims.w + "px");
    el.style.setProperty("--h", dims.h + "px");
    el.style.setProperty("--c", binding[0]);
    el.style.setProperty("--lab", binding[1]);
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
        well.appendChild(buildBook(book, i, ctl));
      });
      wireKeys(well, ctl.closeOpen);
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
    label.innerHTML = '<span class="bay__numeral">' + roman(index + 1) + "</span>" + esc(year.name);

    bay.append(well, plank, label);
    return bay;
  }

  /* A slot and its spine. The binding's custom properties go on the slot, so
     the spine and, once it opens, the card both read them. */
  function buildBook(data, i, ctl) {
    var todo = isTodo(data);

    var book = document.createElement("div");
    book.className = "book";
    setBinding(book, i, data.book_size);

    var spine = document.createElement("button");
    spine.type = "button";
    spine.className = "spine" + (todo ? " spine--todo" : "");
    spine.tabIndex = i === 0 ? 0 : -1;   // one tab stop per bay; arrows do the rest
    book.appendChild(spine);

    book._book = data;
    book._index = i;
    book._todo = todo;
    book._spine = spine;
    fill(book, false);
    if (todo) {
      // Nothing to open yet: announce it as unavailable rather than collapsed.
      spine.removeAttribute("aria-expanded");
      spine.setAttribute("aria-disabled", "true");
    }

    spine.addEventListener("click", function () { if (!todo) ctl.toggle(book); });
    book._openFolio = function () { ctl.openFolio(book); };
    return book;
  }

  /* Roving tabindex within a bay: the group is one tab stop, arrows move
     between its spines (an open book's spine is its Close button). Opening
     is deliberate (Enter or Space), because it changes the width of the slot
     underneath the pointer. */
  function wireKeys(well, closeOpen) {
    well.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { closeOpen(); return; }

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
      spines[next].focus();
      spines[next].scrollIntoView({ block: "nearest", inline: "nearest" });
    });
  }

  /* Both faces of a slot. Closed it is a spine: a title read down it with the
     subject at its foot. Open it is a small card - the book's text, then "See
     more" and "Close" side by side at its foot - and the spine button, kept
     in place so focus stays on it, becomes that Close. */
  function fill(book, open) {
    var data = book._book;
    var spine = book._spine;
    book.classList.toggle("book--open", open);
    spine.classList.toggle("spine--open", open);
    spine.setAttribute("aria-expanded", open ? "true" : "false");

    if (book._face) { book._face.remove(); book._face = null; }
    if (book._more) { book._more.remove(); book._more = null; }

    if (!open) {
      spine.innerHTML = book._todo
        ? '<span class="spine__title">TODO</span>'
        : '<span class="spine__fin"></span>' +
          '<span class="spine__cart"><span class="spine__cart-in">' +
            '<span class="spine__title gilt-text">' + esc(data.title) + "</span>" +
          "</span></span>" +
          '<span class="spine__fin spine__fin--foot"></span>' +
          (data.subject ? '<span class="spine__subject gilt-text">' + esc(data.subject) + "</span>" : "") +
          '<span class="spine__medal"></span>';

      // The spine reads vertically a letter at a time; give it a flat label.
      spine.setAttribute("aria-label",
        book._todo
          ? "A book still to be confirmed"
          : data.title + (data.subject ? ", " + data.subject : ""));
      return;
    }

    var meta = [data.subject, author(data)].filter(Boolean).join(" · ");
    var face = document.createElement("div");
    face.className = "face";
    face.innerHTML =
      '<p class="face__head">' +
        '<span class="face__title">' + esc(data.title) + "</span>" +
        (data.titleUrdu
          ? '<span class="face__urdu" lang="ur" dir="rtl">' + esc(data.titleUrdu) + "</span>"
          : "") +
      "</p>" +
      (meta ? '<p class="face__meta">' + esc(meta) + "</p>" : "") +
      '<span class="face__rule"></span>' +
      '<p class="face__body">' + esc(data.description || "") + "</p>";

    var more = document.createElement("button");
    more.type = "button";
    more.className = "face__more";
    more.textContent = "See more";
    more.setAttribute("aria-expanded", "false");
    more.addEventListener("click", book._openFolio);

    // Before the spine, so a screen reader meets the text, then See more, then Close.
    book.insertBefore(face, spine);
    book.insertBefore(more, spine);
    book._face = face;
    book._more = more;

    spine.textContent = "Close";
    spine.setAttribute("aria-label", "Close " + data.title);
  }

  /* The folio: the book at full size across the bay. A ruled manuscript leaf
     (the jadwal) with the cover running down the left side, and beside it the
     subject, the title with its Urdu or Arabic name on the same line, the
     author, the description and a catchword. The year is not repeated: the
     bay's label is right beneath it. */
  function buildFolio(data, i) {
    var id = "folio-title-" + (++folioCount);
    var el = document.createElement("section");
    el.className = "folio";
    el.setAttribute("aria-labelledby", id);

    var by = author(data);
    var catchword = String(data.title || "").split(/\s+/)[0];
    el.innerHTML =
      '<button type="button" class="folio__close" aria-label="Close ' + esc(data.title) + ' in full">' +
        '<span aria-hidden="true">✕</span></button>' +
      // width/height give the 3:4 box before the image decodes, so a phone's
      // stacked folio doesn't jump when the cover arrives.
      '<div class="folio__cover"><img src="' + esc(data.cover || drawnCover(data, i)) +
        '" width="300" height="400" alt="' + (data.cover ? "Cover of " + esc(data.title) : "") + '"></div>' +
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
        '<p class="folio__catch" aria-hidden="true">' + esc(catchword) + "</p>" +
      "</div>";
    return el;
  }

  /* An author still marked TODO is not shown at all. */
  function author(data) {
    var a = String(data.author || "").trim();
    return a && !/^TODO/i.test(a) ? a : "";
  }

  /* A book with no `cover` photograph yet shows its binding face-on instead:
     the spine's leather and cartouche colours, a double gilt frame, the title
     in the pointed cartouche and the foot medallion. The same drawing as
     design/canvas-expand/generate_covers.py, as a 3:4 SVG. It is decoration
     standing in for a photograph, so its <img> has an empty alt. */
  function drawnCover(data, i) {
    var binding = BINDINGS[i % BINDINGS.length];
    var gilt = "#d9aa48";
    var W = 300, H = 400;

    function cart(cx, cy, w, h) {
      var x0 = cx - w / 2, x1 = cx + w / 2, y0 = cy - h / 2, y1 = cy + h / 2;
      return "M" + cx + " " + y0 + "L" + x1 + " " + (y0 + h * 0.12) + "L" + x1 + " " + (y0 + h * 0.88) +
             "L" + cx + " " + y1 + "L" + x0 + " " + (y0 + h * 0.88) + "L" + x0 + " " + (y0 + h * 0.12) + "Z";
    }
    function finial(y, flip) {
      return '<g transform="translate(150 ' + y + ") scale(1 " + (flip ? -1 : 1) + ')">' +
        '<path d="M0 0V16" stroke="' + gilt + '" stroke-width="1.4"/>' +
        '<rect x="-4" y="16" width="8" height="8" transform="rotate(45 0 20)" fill="' + gilt + '"/></g>';
    }

    // Break the title into lines of about eleven letters for the cartouche.
    var lines = [], line = "";
    String(data.title || "").split(/\s+/).forEach(function (word) {
      if (line && (line + " " + word).length > 11) { lines.push(line); line = word; }
      else line = line ? line + " " + word : word;
    });
    if (line) lines.push(line);
    lines = lines.slice(0, 3);
    var size = lines.length > 2 ? 21 : 25, lead = size + 5;
    var top = 170 - ((lines.length - 1) * lead) / 2 + size * 0.35;
    var text = lines.map(function (l, n) {
      return '<text x="150" y="' + (top + n * lead) + '" text-anchor="middle" fill="' + gilt +
        '" font-family="Georgia, serif" font-size="' + size + '" font-weight="600">' + esc(l) + "</text>";
    }).join("");

    var svg =
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + W + " " + H + '" width="' + W + '" height="' + H + '">' +
        '<defs><filter id="g" x="0" y="0" width="100%" height="100%">' +
          '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" stitchTiles="stitch"/>' +
          '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.5 0 0 0 -0.22"/></filter>' +
        '<linearGradient id="l" x1="0" y1="0" x2="1" y2="0">' +
          '<stop offset="0" stop-opacity="0.45"/><stop offset="0.16" stop-opacity="0.05"/>' +
          '<stop offset="0.5" stop-color="#fff" stop-opacity="0.09"/><stop offset="1" stop-opacity="0.3"/>' +
        "</linearGradient></defs>" +
        '<rect width="' + W + '" height="' + H + '" fill="' + binding[0] + '"/>' +
        '<rect width="' + W + '" height="' + H + '" filter="url(#g)"/>' +
        '<rect width="' + W + '" height="' + H + '" fill="url(#l)"/>' +
        '<rect x="14" y="14" width="272" height="372" fill="none" stroke="' + gilt + '" stroke-width="1.6" opacity="0.85"/>' +
        '<rect x="20" y="20" width="260" height="360" fill="none" stroke="' + gilt + '" stroke-width="0.8" opacity="0.6"/>' +
        '<g fill="' + gilt + '" opacity="0.8"><circle cx="30" cy="30" r="3.2"/><circle cx="270" cy="30" r="3.2"/>' +
          '<circle cx="30" cy="370" r="3.2"/><circle cx="270" cy="370" r="3.2"/></g>' +
        finial(62, false) + finial(338, true) +
        '<path d="' + cart(150, 170, 196, 132) + '" fill="' + gilt + '"/>' +
        '<path d="' + cart(150, 170, 190, 126) + '" fill="' + binding[1] + '"/>' +
        '<path d="' + cart(150, 170, 176, 112) + '" fill="none" stroke="' + gilt + '" stroke-width="0.9" opacity="0.55"/>' +
        text +
        '<circle cx="150" cy="296" r="15" fill="none" stroke="' + gilt + '" stroke-width="1.2"/>' +
        '<circle cx="150" cy="296" r="7" fill="' + gilt + '" opacity="0.9"/>' +
      "</svg>";
    return "data:image/svg+xml," + encodeURIComponent(svg);
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  global.renderCurriculum = renderCurriculum;
})(window);

/* =====================================================================
   curriculum.js - the seven-year bookshelf.

   Years are paired two to a row, and a lone trailing year takes a whole
   row to itself - seven years therefore give the four boards of the
   mockup. Each bay is one year; every book in the course stands on the
   shelf at once as a spine.

   Clicking a spine turns that book face-on in its own slot. The button
   IS the card, so focus never moves, aria-expanded carries the state and
   there is no panel to label. One book is open across the whole shelf.

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
  var WIDTHS = [48, 54, 48, 52, 46, 50, 46, 52];

  /* The tallest spine has to clear .bay__well's 300px once its headband and
     the hover lift are counted - see "7. Curriculum bookshelf" in styles.css. */
  var HEIGHTS = [254, 268, 262, 256, 240, 250, 236, 260];

  /* Wide screens only: some planks run on past the bays and out onto the wall
     as a ledge of spare books - one per row, alternating sides. Pure
     decoration, so it is keyed to the row, not the data, and hidden from
     assistive tech. Items are listed nearest the bay first; `fit` is the
     ledge width (see .ledge in styles.css) an item needs before it shows, so
     a narrower margin drops the outermost things rather than clipping them.
     A book gives the binding to borrow and whether it leans; an image gives
     its file and width. */
  var LEDGES = [
    [{ book: 5 }, { book: 0 }, { book: 3, fit: 1 }, { book: 1, lean: true, fit: 3 }],
    [{ book: 2 }, { img: "ledge-stack-ink.svg", width: 124, fit: 2 }],
    [{ book: 1 }, { book: 4, fit: 1 }, { img: "ledge-stack-pens.svg", width: 124, fit: 3 }],
    [{ book: 0 }, { book: 2, lean: true, fit: 1 }]
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

  function renderCurriculum(mount, data) {
    if (!mount || !data || !data.years) return;
    mount.textContent = "";

    var open = null;   // the one open spine, shelf-wide

    function toggle(spine) {
      if (open && open !== spine) fill(open, false);
      var wasOpen = open === spine;
      open = wasOpen ? null : spine;
      fill(spine, !wasOpen);
    }

    function closeOpen() {
      if (!open) return;
      fill(open, false);
      open.focus();
      open = null;
    }

    var years = data.years;
    for (var i = 0; i < years.length; i += 2) {
      var pair = years.slice(i, i + 2);
      var row = document.createElement("div");
      row.className = "shelf" + (pair.length === 1 ? " shelf--single" : "");
      pair.forEach(function (year, j) {
        row.appendChild(buildBay(year, i + j, toggle, closeOpen));
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
        setBinding(el, item.book);
        el.innerHTML = '<span class="spine__fin"></span><span class="spine__cart"><span class="spine__cart-in"></span></span>' +
          '<span class="spine__fin spine__fin--foot"></span><span class="spine__medal"></span>';
      }
      if (item.fit) el.classList.add("ledge__far" + item.fit);
      items.appendChild(el);
    });

    ledge.appendChild(items);
    return ledge;
  }

  function setBinding(el, i) {
    var binding = BINDINGS[i % BINDINGS.length];
    el.style.setProperty("--w", WIDTHS[i % WIDTHS.length] + "px");
    el.style.setProperty("--h", HEIGHTS[i % HEIGHTS.length] + "px");
    el.style.setProperty("--c", binding[0]);
    el.style.setProperty("--lab", binding[1]);
  }

  function buildBay(year, index, toggle, closeOpen) {
    var bay = document.createElement("div");
    bay.className = "bay";

    var well = document.createElement("div");
    well.className = "bay__well";
    well.setAttribute("role", "group");
    well.setAttribute("aria-label", year.name);

    var books = year.books || [];
    if (books.length) {
      books.forEach(function (book, i) {
        well.appendChild(buildSpine(book, i, toggle));
      });
      wireKeys(well, closeOpen);
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

  function buildSpine(book, i, toggle) {
    var todo = isTodo(book);

    var spine = document.createElement("button");
    spine.type = "button";
    spine.className = "spine" + (todo ? " spine--todo" : "");
    spine.setAttribute("aria-expanded", "false");
    spine.tabIndex = i === 0 ? 0 : -1;   // one tab stop per bay; arrows do the rest
    setBinding(spine, i);

    spine._book = book;
    spine._todo = todo;
    fill(spine, false);
    if (todo) {
      // Nothing to open yet: announce it as unavailable rather than collapsed.
      spine.removeAttribute("aria-expanded");
      spine.setAttribute("aria-disabled", "true");
    }

    spine.addEventListener("click", function () { if (!spine._todo) toggle(spine); });
    return spine;
  }

  /* Roving tabindex within a bay: the group is one tab stop, arrows move
     between its books. Opening is deliberate (Enter or Space), because it
     changes the width of the slot underneath the pointer. */
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

  /* Both faces of a spine. Closed it is a title read down the spine with the
     subject at its foot; open it is the same button turned to face the reader. */
  function fill(spine, open) {
    var book = spine._book;
    spine.setAttribute("aria-expanded", open ? "true" : "false");
    spine.classList.toggle("spine--open", open);

    if (!open) {
      spine.innerHTML = spine._todo
        ? '<span class="spine__title">TODO</span>'
        : '<span class="spine__fin"></span>' +
          '<span class="spine__cart"><span class="spine__cart-in">' +
            '<span class="spine__title gilt-text">' + esc(book.title) + "</span>" +
          "</span></span>" +
          '<span class="spine__fin spine__fin--foot"></span>' +
          (book.subject ? '<span class="spine__subject gilt-text">' + esc(book.subject) + "</span>" : "") +
          '<span class="spine__medal"></span>';

      // The spine reads vertically a letter at a time; give it a flat label.
      spine.setAttribute("aria-label",
        spine._todo
          ? "A book still to be confirmed"
          : book.title + (book.subject ? ", " + book.subject : ""));
      return;
    }

    var meta = [book.subject, book.author].filter(Boolean).join(" · ");
    spine.removeAttribute("aria-label");
    spine.innerHTML =
      '<span class="face__head">' +
        '<span class="face__title">' + esc(book.title) + "</span>" +
        (book.titleUrdu
          ? '<span class="face__urdu" lang="ur" dir="rtl">' + esc(book.titleUrdu) + "</span>"
          : "") +
      "</span>" +
      (meta ? '<span class="face__meta">' + esc(meta) + "</span>" : "") +
      '<span class="face__rule"></span>' +
      '<span class="face__body">' + esc(book.description || "") + "</span>";
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  global.renderCurriculum = renderCurriculum;
})(window);

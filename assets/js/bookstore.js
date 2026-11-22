/* =====================================================================
   bookstore.js - the books the masjid sells, from content/bookstore.json,
   as a bento grid: rounded tiles, each washed in the colour of its own
   cover, the book's photograph (cut to the book alone) leaning out of the
   tile's corner and straightening when pointed at. A book whose size is
   "large" takes a tile two by two, and one whose size is "medium" a tile
   two wide and one high, each in its cover's colour (or its own "tint"),
   with its description. A book with an id opens its own page,
   book.html?id=<id> (book.js), where it is bought. Option 2 of the best
   options of design/canvas-library/ (best-2-bento.html).

   The tight crops and the covers' colours are made by tools/covers.py into
   assets/img/books/tight/ (covers.json); a photograph without one is shown
   zoomed and tinted by its binding until the tool is run.

   Attaches one global, window.renderBookstore(data, all), used by both
   pages: main.js calls it for the home page's section (three rows of
   books with a photograph, the featured first), and on bookstore.html this
   file boots itself and calls it with every book, a tile with the heading,
   and a filter by subject group. Calling it again redraws the section,
   which is how the admin editor previews an edit. Needs curriculum.js
   loaded first for the drawn bindings of books without a photograph.
   ===================================================================== */
(function (global) {
  "use strict";

  var slot = function (name) { return document.querySelector('[data-slot="' + name + '"]'); };

  var ICONS = {
    home:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 11l8-7 8 7v9H4z"/></svg>',
    mail:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3.5" y="5.5" width="17" height="13" rx="1.5"/><path d="M4 7l8 6 8-6"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg>'
  };

  var HOME_CELLS = 12;   // the home page's books fill three rows of four (a large one is four cells, a medium one two)
  var filter = { group: "" };   // the subject group bookstore.html shows ("" = all)
  try {
    var q = new URLSearchParams(location.search);
    filter.group = q.get("group") || "";
  } catch (e) {}

  // A book without a measured photograph is tinted by its binding.
  var TONES = { "lapis": "#1c3f7a", "ink": "#2e2c33", "lapis-silver": "#1c3f7a", "ink-silver": "#2e2c33",
    "petrol": "#0f5560", "oxblood": "#6e1a1f", "aubergine": "#4b2458", "slate": "#39434e" };
  var ORDINALS = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh"];
  var ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"];

  // The tight crops and colours (tools/covers.py). The section is drawn at
  // once and again when they arrive.
  var covers = null, last = null;
  fetch("assets/img/books/tight/covers.json", { cache: "no-cache" })
    .then(function (r) { return r.ok ? r.json() : {}; })
    .catch(function () { return {}; })
    .then(function (m) { covers = m || {}; if (last) renderBookstore(last[0], last[1]); });

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

  function isTodo(s) { return /^\s*TODO\b/i.test(String(s || "")); }

  function setText(name, value) {
    var node = slot(name);
    if (node && value) node.textContent = value;
  }

  // The years a book is taught in, as a list.
  function yearsOf(b) {
    return (Array.isArray(b.years) ? b.years : []).map(function (y) { return String(y).trim(); })
      .filter(Boolean);
  }

  function subjectOf(b) { return String(b.subject || "").trim(); }

  // A book's prints: its "prints" (each an edition, price, cover and
  // soldOut of its own), or, without them, the book itself as its one
  // print. The first is the one the tile shows in front. (As book.js and
  // cart.js read them; keep the three in step.)
  var PRINT = ["edition", "price", "cover", "soldOut"];
  function printsOf(b) {
    if (Array.isArray(b.prints) && b.prints.length) return b.prints;
    var one = {};
    PRINT.forEach(function (f) { if (f in b) one[f] = b[f]; });
    return [one];
  }
  function hasCover(b) { return printsOf(b).some(function (p) { return p.cover; }); }

  // The price as the tile shows it: one price, or the lowest to the highest
  // of the prints still on sale ("$6.00 – $8.00"); null when all are sold out.
  function priceRange(prints) {
    var open = prints.filter(function (p) { return !p.soldOut; });
    if (!open.length) return null;
    var priced = open.filter(function (p) { return p.price; });
    var nums = priced.map(function (p) { return parseFloat(String(p.price).replace(/[^0-9.]/g, "")); });
    if (priced.length < 2 || nums.some(isNaN)) return priced.length ? priced[0].price : "";
    var lo = 0, hi = 0;
    nums.forEach(function (n, k) { if (n < nums[lo]) lo = k; if (n > nums[hi]) hi = k; });
    return nums[lo] === nums[hi] ? priced[lo].price : priced[lo].price + " – " + priced[hi].price;
  }
  // A card's size: "large" (two by two), "medium" (two by one) or "normal".
  function sizeOf(b) { return b.size === "large" || b.size === "medium" ? b.size : "normal"; }
  var CELLS = { large: 4, medium: 2, normal: 1 };

  // "Year VII", "Years V & VI": the course's years as numerals.
  function yearsLine(b) {
    var ys = yearsOf(b).map(function (y) {
      var k = ORDINALS.indexOf(y.replace(/\s+Year$/i, ""));
      return k >= 0 ? ROMAN[k] : y;
    });
    if (!ys.length) return "";
    return (ys.length > 1 ? "Years " : "Year ") + (ys.length === 2 ? ys.join(" & ") : ys.join(", "));
  }

  // The home page's books: those with a photograph, the featured first
  // (books without one only if there are too few), as many as fill three
  // rows of four - a large book takes four cells - and no more.
  function homeBooks(books) {
    var order = books.filter(function (b) { return b.featured; })
      .concat(books.filter(function (b) { return !b.featured; }));
    var withPic = order.filter(hasCover);
    var picked = [], cells = 0;
    withPic.concat(order.filter(function (b) { return !hasCover(b); })).forEach(function (b) {
      var n = CELLS[sizeOf(b)];
      if (cells + n <= HOME_CELLS) { picked.push(b); cells += n; }
    });
    return picked;
  }

  // A colour darkened until cream text reads on it (the lead tile).
  function deep(hex, top) {
    var m = /^#?([0-9a-f]{6})$/i.exec(hex || "");
    if (!m) return hex;
    var n = parseInt(m[1], 16), r = (n >> 16) / 255, g = (n >> 8 & 255) / 255, b = (n & 255) / 255;
    var max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2, h = 0, s = 0, d = max - min;
    if (d) {
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      h = max === r ? (g - b) / d + (g < b ? 6 : 0) : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
      h /= 6;
    }
    top = top || 0.36;
    if (l <= top) return hex;
    l = top; s = Math.min(1, s * 1.25);
    function f(t) {
      var q = l < 0.5 ? l * (1 + s) : l + s - l * s, p = 2 * l - q;
      t = (t + 1) % 1;
      var v = t < 1 / 6 ? p + (q - p) * 6 * t : t < 0.5 ? q : t < 2 / 3 ? p + (q - p) * (2 / 3 - t) * 6 : p;
      return ("0" + Math.round(v * 255).toString(16)).slice(-2);
    }
    return "#" + f(h + 1 / 3) + f(h) + f(h - 1 / 3);
  }

  /* A tile: subject, title (with its edition), years, price, the picture
     leaning out of the corner, washed in its cover's colour. A large book's
     tile is two by two, a medium one two by one (.store-card--wide), both
     in that colour itself (or the book's own tint) with the description. A
     book of several prints shows how many in place of the edition, their
     pictures fanned out from the corner (the first in front, up to three),
     and the range of their prices. A book with an id opens its page (the
     title is a stretched link). data-i is the book's place in the whole
     list, which the admin editor picks and drags by; keep the store-card
     class. size, when given, overrides the book's own (a tab's layout). */
  function card(book, i, size) {
    if (size == null) size = sizeOf(book);
    var lead = size !== "normal";
    var prints = printsOf(book), front = prints[0];
    var info = covers && front.cover ? covers[front.cover] : null;
    var tone = info ? info.tint : TONES[book.color] || TONES.lapis;
    var tint = /^#[0-9a-f]{6}$/i.test(book.tint || "") ? book.tint : "";
    var href = book.id ? "book.html?id=" + encodeURIComponent(book.id) : "";
    var years = yearsLine(book);
    var price = priceRange(prints);
    var many = prints.length > 1;
    var edition = many ? prints.length + " prints" : front.edition;
    var c = el("article", "store-card" + (lead ? " store-card--lead" : "") + (size === "medium" ? " store-card--wide" : "") + (href ? " store-card--link" : ""));
    c.dataset.i = i;
    c.dataset.years = yearsOf(book).join("|");
    c.style.setProperty("--tone", lead ? tint || deep(tone) : tone);
    c.innerHTML =
      (lead && book.featured ? '<p class="store-card__flag">Featured</p>' : "") +
      (book.subject ? '<p class="store-card__sub">' + esc(book.subject) + "</p>" : "") +
      '<h3 class="store-card__title">' +
        (href ? '<a class="stretched" href="' + esc(href) + '">' + esc(book.title) + "</a>" : esc(book.title)) + "</h3>" +
      (edition ? '<p class="store-card__edition">' + esc(edition) + "</p>" : "") +
      (years ? '<p class="store-card__years">' + esc(years) + "</p>" : "") +
      (lead && book.description ? '<p class="store-card__desc">' + esc(book.description) + "</p>" : "") +
      (price === null ? '<p class="store-card__price store-card__price--sold">Sold out</p>'
        : price ? '<p class="store-card__price' + (isTodo(price) ? " store-card__price--todo" : "") + '">' + esc(price) + "</p>" : "") +
      prints.slice(0, 3).map(function (p, k) { return pic(book, i, p, k, many); }).join("");
    return c;
  }

  // One print's picture. In a fan (f the place from the front) the front
  // comes first, so it is the one the admin editor finds, and stands on top.
  function pic(book, i, p, f, fan) {
    var info = covers && p.cover ? covers[p.cover] : null;
    var draw = global.renderCurriculum && global.renderCurriculum.drawnCover;
    var src = info ? info.tight : p.cover || (draw ? draw(book, i) : "");
    if (!src) return "";
    return '<span class="store-card__pic' + (fan ? " store-card__pic--fan" : "") + '"' +
      (fan ? ' style="--f: ' + f + "; z-index: " + (-1 - f) + '"' : "") + "><img" + (!info && p.cover ? ' class="is-zoom"' : "") +
      ' src="' + esc(src) + '" width="300" height="400" alt="' + (p.cover && !f ? "Cover of " + esc(book.title) : "") + '" loading="lazy"></span>';
  }

  // The group a book's subject is filed under (subjectGroups in the JSON);
  // a subject in no group falls into the last. "" without groups.
  function groupOf(b, groups) {
    if (!groups.length) return "";
    var s = subjectOf(b);
    for (var i = 0; i < groups.length - 1; i++) {
      if ((groups[i].subjects || []).indexOf(s) >= 0) return groups[i].name;
    }
    return groups[groups.length - 1].name;
  }

  function matches(b, group, groups) {
    return !group || groupOf(b, groups) === group;
  }

  // bookstore.html, option 6 of design/canvas-filters/ with only its
  // subject groups: words (All, then each group), each with its count, the
  // chosen one underlined. Hidden with fewer than two groups.
  function renderChips(mount, books, grid, data) {
    var groups = (data.subjectGroups || []).filter(function (g) { return g && g.name; });
    var names = groups.map(function (g) { return g.name; }).filter(function (n) {
      return books.some(function (b) { return groupOf(b, groups) === n; });
    });
    if (names.indexOf(filter.group) < 0) filter.group = "";
    function draw() {
      mount.textContent = "";
      mount.hidden = names.length < 2;
      if (mount.hidden) return;
      mount.appendChild(el("p", "store-filter__label", "Subject"));
      var row = el("div", "store-groups");
      row.setAttribute("role", "group");
      row.setAttribute("aria-label", "Subject");
      [""].concat(names).forEach(function (v) {
        var n = books.filter(function (b) { return matches(b, v, groups); }).length;
        var b = el("button", "store-groups__btn", esc(v || "All") + "<sup>" + n + "</sup>");
        b.type = "button";
        b.setAttribute("aria-pressed", String(v === filter.group));
        b.addEventListener("click", function () {
          filter.group = v;
          draw();
          renderAll(grid, books, data);
          // The admin editor follows the tab.
          mount.dispatchEvent(new CustomEvent("bookstore:tab", { bubbles: true, detail: { group: v } }));
        });
        row.appendChild(b);
      });
      mount.appendChild(row);
    }
    draw();
  }

  // bookstore.html: the books the filters let through (the masthead over
  // the grid is the page's own).
  // A tab's books and their sizes. All is the list's own order and each
  // book's size; a group with a layout (layouts[group] in the JSON: its
  // order and its large cards, by id) stands in that order, any of its books
  // the layout doesn't name after them in the list's order, and is large or
  // medium only where the layout says. A group without one follows All.
  function tabBooks(books, data, group) {
    var groups = (data.subjectGroups || []).filter(function (g) { return g && g.name; });
    var shown = books.filter(function (b) { return matches(b, group, groups); });
    var lay = group && data.layouts && data.layouts[group];
    if (!lay) return shown.map(function (b) { return { book: b, size: sizeOf(b) }; });
    var order = Array.isArray(lay.order) ? lay.order : [], large = Array.isArray(lay.large) ? lay.large : [],
      medium = Array.isArray(lay.medium) ? lay.medium : [];
    var rank = function (b) { var k = b.id ? order.indexOf(b.id) : -1; return k < 0 ? order.length + shown.indexOf(b) : k; };
    return shown.slice().sort(function (a, b) { return rank(a) - rank(b); }).map(function (b) {
      var size = !b.id ? "normal" : large.indexOf(b.id) >= 0 ? "large" : medium.indexOf(b.id) >= 0 ? "medium" : "normal";
      return { book: b, size: size };
    });
  }

  // bookstore.html on a phone: no tabs, but a row for each subject group,
  // swiped sideways, its books as bare covers (design/mobile-bookstore/,
  // option C with card 2). Each row keeps its tab's order; every book is
  // the same small size.
  var PHONE = global.matchMedia ? global.matchMedia("(max-width: 640px)") : { matches: false };
  function groupNames(books, data) {
    var groups = (data.subjectGroups || []).filter(function (g) { return g && g.name; });
    return groups.map(function (g) { return g.name; }).filter(function (n) {
      return books.some(function (b) { return groupOf(b, groups) === n; });
    });
  }
  function renderRows(grid, books, data, names) {
    names.forEach(function (name, k) {
      var shown = tabBooks(books, data, name);
      var sec = el("section", "store-row");
      var head = el("h2", "store-row__head", esc(name) + "<sup>" + shown.length + "</sup>");
      head.id = "store-row-" + k;
      sec.setAttribute("aria-labelledby", head.id);
      var row = el("div", "store-row__books");
      shown.forEach(function (t) { row.appendChild(card(t.book, books.indexOf(t.book), "normal")); });
      sec.append(head, row);
      grid.appendChild(sec);
    });
    // A link to one subject (bookstore.html?group=Fiqh) opens at its row.
    var at = names.indexOf(filter.group);
    if (at > 0 && !grid._rowsShown) {
      // Once the page has loaded (a load resets the scroll), and to the row
      // as it is then: the covers' arrival redraws them.
      var go = function () { var r = grid.querySelectorAll(".store-row")[at]; if (r) r.scrollIntoView({ block: "start", behavior: "instant" }); };
      if (document.readyState === "complete") setTimeout(go, 0); else global.addEventListener("load", function () { setTimeout(go, 0); });
    }
    grid._rowsShown = true;
  }

  function renderAll(grid, books, data) {
    grid.textContent = "";
    var names = groupNames(books, data);
    var rows = PHONE.matches && names.length > 1;
    grid.classList.toggle("store--rows", rows);
    if (rows) {
      renderRows(grid, books, data, names);
      setText("bookstore-kicker", data.kicker);
      setText("bookstore-heading", data.heading);
      setText("bookstore-lede", data.lede);
      return;
    }
    var shown = tabBooks(books, data, filter.group);
    shown.forEach(function (t) { grid.appendChild(card(t.book, books.indexOf(t.book), t.size)); });
    if (!shown.length) grid.appendChild(el("p", "media-empty", books.length ? "No books match." : "No books yet."));
    setText("bookstore-kicker", data.kicker);
    setText("bookstore-heading", data.heading);
    setText("bookstore-lede", data.lede);
  }

  // bookstore.html: the librarian's message under the masthead
  // (design/canvas-store-message/, option 2b): `message.body` is its
  // paragraphs, `message.closing` the du'a beneath. Hidden without a body.
  // Drawn once on load, not by renderAll: the bookstore editor redraws with
  // its own fields only, which leave the message out.
  function renderLetter(msg) {
    var mount = slot("bookstore-letter");
    if (!mount) return;
    var body = msg && Array.isArray(msg.body) ?
      msg.body.filter(function (p) { return typeof p === "string" && p.trim(); }) : [];
    mount.textContent = "";
    mount.hidden = !body.length;
    if (!body.length) return;
    var text = el("div", "store-letter__body");
    body.forEach(function (p) { text.appendChild(el("p", "", esc(p))); });
    text.id = "store-letter-body";
    mount.appendChild(text);
    if (msg.closing) mount.appendChild(el("p", "store-letter__closing", esc(msg.closing)));
    // On a phone the message runs to a screen; it opens on its first lines
    // and a button reads the rest (the CSS shows the button there only).
    var more = el("button", "store-letter__more", "Read more");
    more.type = "button";
    more.setAttribute("aria-controls", text.id);
    more.setAttribute("aria-expanded", "false");
    more.addEventListener("click", function () {
      var open = mount.classList.toggle("is-open");
      more.setAttribute("aria-expanded", open ? "true" : "false");
      more.textContent = open ? "Show less" : "Read more";
    });
    mount.appendChild(more);
  }

  function renderBookstore(data, all) {
    var grid = slot("bookstore");
    if (!grid) return;
    last = [data, all];
    var books = data.books || [];
    grid.classList.toggle("store--all", !!all);
    if (all) {
      // Crossing the phone width draws the page the other way.
      if (!grid._phoneWatch && PHONE.addEventListener) {
        grid._phoneWatch = true;
        PHONE.addEventListener("change", function () { if (last) renderBookstore(last[0], last[1]); });
      }
      var chips = slot("bookstore-filters");
      if (chips) renderChips(chips, books, grid, data);
      renderAll(grid, books, data);
      return;
    }
    // Three rows of the featured books; the section head and the button
    // to bookstore.html are the page's own.
    var shown = homeBooks(books);
    grid.textContent = "";
    shown.forEach(function (b) { grid.appendChild(card(b, books.indexOf(b))); });
    if (!shown.length) grid.appendChild(el("p", "media-empty", "No books yet."));
    setText("bookstore-kicker", data.kicker);
    setText("bookstore-heading", data.heading);
    setText("bookstore-visit-label", data.visitLabel || "Visit Bookstore");
  }
  global.renderBookstore = renderBookstore;
  // The tab bookstore.html shows ("" for All), for the admin editor.
  renderBookstore.tab = function () { return filter.group; };

  /* --------------------------- bookstore.html --------------------------- */
  if (!slot("bookstore-filters")) return;

  function loadJSON(path) {
    return fetch(path, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(path + " -> HTTP " + r.status);
      return r.json();
    });
  }

  // The footer's contact lines, as main.js draws them; keep the two in step.
  function renderFooter(footer) {
    var mount = slot("footer-contact");
    if (!mount || !footer) return;
    mount.textContent = "";
    function line(icon, html) {
      mount.appendChild(el("span", "site-footer__line", '<i aria-hidden="true">' + icon + "</i>" + html));
    }
    // The address opens the map and the number dials: on a phone these are
    // the two lines most people want to tap.
    if (footer.address) {
      line(ICONS.home, isTodo(footer.address) ? esc(footer.address)
        : '<a href="https://www.google.com/maps/search/?api=1&amp;query=' +
          encodeURIComponent(footer.address) + '" target="_blank" rel="noopener">' + esc(footer.address) + "</a>");
    }
    if (footer.email) {
      line(ICONS.mail, isTodo(footer.email) ? esc(footer.email)
        : '<a href="mailto:' + esc(footer.email) + '">' + esc(footer.email) + "</a>");
    }
    if (footer.phone) {
      line(ICONS.phone, isTodo(footer.phone) ? esc(footer.phone)
        : '<a href="tel:' + footer.phone.replace(/[^\d+]/g, "") + '">' + esc(footer.phone) + "</a>");
    }
  }

  var yearSlot = slot("year");
  if (yearSlot) yearSlot.textContent = String(new Date().getFullYear());

  Promise.all([
    loadJSON("content/bookstore.json").then(function (data) {
      renderLetter(data.message);
      renderBookstore(data, true);
    }),
    loadJSON("content/program.json").then(function (data) { renderFooter(data.footer); })
  ]).catch(function (err) {
    console.error("Content failed to load.", err);
    slot("bookstore").innerHTML =
      '<p class="media-empty">The books could not be loaded. If you opened this file directly, serve the folder over ' +
      "a local web server instead (see CLAUDE.md).</p>";
  });
})(window);

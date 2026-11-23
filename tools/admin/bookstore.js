/* =====================================================================
   bookstore.js (admin) - the bookstore editor. Only tools/admin_server.py
   serves this file and only it adds the tag that loads it, to index.html
   and to bookstore.html, so the public site never carries it. "Edit
   bookstore" opens a panel beside the cards: pick a book (click its card,
   or choose it from the list) and edit its name, edition, subject, years,
   price, description, page id, picture, binding (a
   book sold in several prints has an edition, price, picture, payment link
   and "sold out" for each, added, reordered and removed in the panel), its
   card's size (normal; medium: two by one; large: two by two) and a
   medium or large card's colour
   (a colour picker, or picked off the book's own picture), mark it featured
   for the home page or sold out, add books, reorder them (drag a card onto
   another, or ↑/↓ in the list) or delete them. Every change redraws the section with the
   site's own renderBookstore (assets/js/bookstore.js), so it shows the edit
   as it will be published. On bookstore.html each subject tab keeps its own
   layout: with a tab open (Language, Hadith, ...), dragging cards and the
   card size change only that tab (layouts[tab] in the JSON, by id), and
   All is the list's own order and sizes. Saving writes the heading,
   kicker, lede, visitLabel, pickup, hold, payWith, reserveTo, books and layouts of
   content/bookstore.json through the server; nothing is written until Save.
   ===================================================================== */
(function () {
  "use strict";

  var API = "/__admin/bookstore";
  // The names BINDINGS in assets/js/curriculum.js knows; keep in step.
  var BINDINGS = ["lapis", "ink", "lapis-silver", "ink-silver", "petrol", "slate", "oxblood", "aubergine"];
  // The program's years, offered for every book with any others in use.
  var YEARS = ["First Year", "Second Year", "Third Year", "Fourth Year", "Fifth Year", "Sixth Year", "Seventh Year"];

  var mount = document.querySelector('[data-slot="bookstore"]');
  // bookstore.html has the filter and shows every book; the home page, the featured.
  var all = !!document.querySelector('[data-slot="bookstore-filters"]');
  var store = null;            // {version, heading, kicker, lede, visitLabel, pickup, hold, payWith, reserveTo, books} as last loaded or saved
  var sel = -1;                // the picked book (-1: none)
  var selPrint = 0;            // the picked print of a book of several
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

  function book() { return sel >= 0 ? store.books[sel] : null; }

  /* -------------------------------- prints ------------------------------ */
  // A book of several prints keeps each one's edition, price, picture,
  // payment link and soldOut in "prints"; a book of one keeps them itself.
  // The fields the panel edits for a print are those of the picked print,
  // or of the book.
  var PRINT = ["edition", "price", "cover", "soldOut"];
  function target() {
    var b = book();
    if (!b) return null;
    if (!b.prints) return b;
    if (selPrint >= b.prints.length) selPrint = b.prints.length - 1;
    return b.prints[selPrint];
  }
  function addPrint() {
    var b = book();
    if (!b.prints) {
      var one = {};
      PRINT.forEach(function (f) { if (f in b) { one[f] = b[f]; delete b[f]; } });
      b.prints = [one];
    }
    var last = b.prints[b.prints.length - 1];
    b.prints.push({ edition: "", price: last.price || "", cover: "" });
    selPrint = b.prints.length - 1;
  }
  function removePrint() {
    var b = book(), p = target();
    if (!b.prints) return;
    if (!confirm("Remove the print “" + (p.edition || "Print " + (selPrint + 1)) + "” of " + (b.title || "Untitled") + "?")) return false;
    b.prints.splice(selPrint, 1);
    if (b.prints.length === 1) {
      // One print left: its fields go back to the book.
      var one = b.prints[0];
      delete b.prints;
      PRINT.forEach(function (f) { if (f in one) b[f] = one[f]; });
    }
    selPrint = Math.max(0, selPrint - 1);
    return true;
  }
  function movePrint(dir) {
    var list = book().prints, to = selPrint + dir;
    if (!list || to < 0 || to >= list.length) return;
    list.splice(to, 0, list.splice(selPrint, 1)[0]);
    selPrint = to;
  }

  /* ------------------------------ tab layouts --------------------------- */
  // The subject tab bookstore.html shows ("" for All, and on the home page).
  function tab() { return all && window.renderBookstore.tab ? window.renderBookstore.tab() : ""; }
  function layouts() { return store.layouts || (store.layouts = {}); }
  // The open tab's layout, made from the cards as they stand when it is
  // first changed (so it starts as the tab looked).
  function tabLayout() {
    var g = tab();
    if (!g) return null;
    var L = layouts();
    if (!L[g]) {
      var order = [], large = [], medium = [];
      mount.querySelectorAll(".store-card[data-i]").forEach(function (c) {
        var b = store.books[+c.dataset.i];
        if (!b || !b.id) return;
        order.push(b.id);
        if (c.classList.contains("store-card--wide")) medium.push(b.id);
        else if (c.classList.contains("store-card--lead")) large.push(b.id);
      });
      L[g] = { order: order, large: large, medium: medium };
    }
    if (!L[g].large) L[g].large = [];
    if (!L[g].medium) L[g].medium = [];
    return L[g];
  }
  // The size where it is seen: in the open tab's layout, else its own.
  function sizeHere(b) {
    var L = tab() && store.layouts && store.layouts[tab()];
    if (!L) return b.size === "large" || b.size === "medium" ? b.size : "normal";
    if (!b.id) return "normal";
    return (L.large || []).indexOf(b.id) >= 0 ? "large" : (L.medium || []).indexOf(b.id) >= 0 ? "medium" : "normal";
  }
  // A book's id changed (or went): its layouts follow.
  function renameId(from, to) {
    if (!from || !store.layouts) return;
    Object.keys(store.layouts).forEach(function (g) {
      ["order", "large", "medium"].forEach(function (f) {
        var list = store.layouts[g][f] || [], k = list.indexOf(from);
        if (k < 0) return;
        if (to) list[k] = to; else list.splice(k, 1);
      });
    });
  }
  // Only the ids of books that are still there, each once, are saved.
  function pruneLayouts() {
    var ids = {};
    store.books.forEach(function (b) { if (b.id) ids[b.id] = true; });
    Object.keys(layouts()).forEach(function (g) {
      ["order", "large", "medium"].forEach(function (f) {
        var seen = {};
        store.layouts[g][f] = (store.layouts[g][f] || []).filter(function (id) {
          if (!ids[id] || seen[id]) return false;
          return (seen[id] = true);
        });
      });
    });
  }

  // An id from a title: lowercase words joined by hyphens.
  function slug(s) {
    return String(s || "").toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  }
  function section() { return mount.closest("section"); }

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
  // Redraws the cards from the edited books and marks the picked one.
  function draw() {
    clearTimeout(timer);
    window.renderBookstore(store, all);
    // renderBookstore leaves an emptied heading or kicker as it was; show
    // them as a reader would.
    var heading = document.querySelector('[data-slot="bookstore-heading"]');
    var kicker = document.querySelector('[data-slot="bookstore-kicker"]');
    var lede = document.querySelector('[data-slot="bookstore-lede"]');
    var visit = document.querySelector('[data-slot="bookstore-visit-label"]');
    if (heading) heading.textContent = store.heading || "Bookstore";
    if (kicker) kicker.textContent = store.kicker;
    if (lede) lede.textContent = store.lede;
    if (visit) visit.textContent = store.visitLabel || "Visit Bookstore";
    decorate();
  }

  // The cards as the editor needs them: draggable, the picked one marked.
  function decorate() {
    // Cards drag to a new place; their links and pictures mustn't take the drag.
    mount.querySelectorAll(".store-card").forEach(function (c) {
      c.draggable = true;
      c.querySelectorAll("a, img").forEach(function (a) { a.draggable = false; });
    });
    mark();
  }

  function mark() {
    mount.querySelectorAll(".adm-picked").forEach(function (n) { n.classList.remove("adm-picked"); });
    var card = mount.querySelector('.store-card[data-i="' + sel + '"]');
    if (card) card.classList.add("adm-picked");
  }

  // Moves a book to another place in the list; the pick goes with it.
  function move(from, to) {
    var list = store.books, picked = book();
    if (to === from || to < 0 || to >= list.length) return;
    list.splice(to, 0, list.splice(from, 1)[0]);
    sel = picked ? list.indexOf(picked) : -1;
    changed();
    draw();
    paintPanel();
  }

  /* ---------------------------- dragging cards --------------------------- */
  // A card dropped on another goes before it, or after it when dropped on
  // its right half; a bar on that side shows where. The cards stand for
  // their books by data-i, so this works on the home page's few as well.
  var dragFrom = -1;

  function cardAt(e) {
    var c = e.target.closest && e.target.closest(".store-card");
    return c && mount.contains(c) ? c : null;
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
    dragFrom = +c.dataset.i;
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
    if (+c.dataset.i !== dragFrom) c.classList.add("adm-drop-" + dropSide(c, e));
  }
  function onDrop(e) {
    if (dragFrom < 0) return;
    e.preventDefault();
    var c = cardAt(e), from = dragFrom;
    onDragEnd();
    if (!c || +c.dataset.i === from) return;
    if (tab()) return moveInTab(from, +c.dataset.i, dropSide(c, e));
    var to = +c.dataset.i + (dropSide(c, e) === "after" ? 1 : 0);
    if (from < to) to--;
    move(from, to);
  }

  // In a subject tab a drop moves the card in that tab's layout only.
  function moveInTab(from, onto, side) {
    var a = store.books[from], b = store.books[onto];
    if (!a.id || !b.id) { status("Give the book a page id to place it in a tab", true); return; }
    var order = tabLayout().order;
    [a.id, b.id].forEach(function (id) { if (order.indexOf(id) < 0) order.push(id); });
    order.splice(order.indexOf(a.id), 1);
    order.splice(order.indexOf(b.id) + (side === "after" ? 1 : 0), 0, a.id);
    changed();
    draw();
    paintPanel();
  }
  function onDragEnd() {
    dragFrom = -1;
    clearDrop();
    mount.querySelectorAll(".adm-dragging").forEach(function (n) { n.classList.remove("adm-dragging"); });
  }

  // While editing, a card picks its book.
  function onSectionClick(e) {
    if (!on) return;
    var card = e.target.closest(".store-card");
    if (!card || !mount.contains(card)) return;
    e.preventDefault();
    pick(+card.dataset.i, false);
    var title = ui.panel.querySelector('[data-f="title"]');
    if (title) title.focus();
  }

  function pick(i, reveal) {
    if (i !== sel) selPrint = 0;
    sel = i;
    mark();
    if (reveal) {
      var card = mount.querySelector('.store-card[data-i="' + sel + '"]');
      (card || section()).scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
    paintPanel();
  }

  /* ------------------------------ the panel ----------------------------- */
  function label(b, i) {
    return (i + 1) + ". " + (b.featured ? "★ " : "") + (b.title || "Untitled") + (b.prints ? " (" + b.prints.length + " prints)" : "");
  }

  // The subjects in use, suggested for a book's subject; the years, offered as boxes.
  function subjects() {
    var seen = [];
    store.books.forEach(function (b) {
      var c = String(b.subject || "").trim();
      if (c && seen.indexOf(c) < 0) seen.push(c);
    });
    return seen;
  }
  function years() {
    var seen = YEARS.slice();
    store.books.forEach(function (b) {
      (b.years || []).forEach(function (y) { if (seen.indexOf(y) < 0) seen.push(y); });
    });
    return seen;
  }

  function paintPanel() {
    var list = store.books, b = book();
    var html =
      '<h2 class="adm-panel__head">Bookstore</h2>' +
      text("Heading", store.heading, ' data-s="heading"') +
      text("Kicker", store.kicker, ' data-s="kicker"', "The small line above the heading; empty hides it.") +
      '<label class="adm-label">Introduction<textarea data-s="lede" rows="3">' + esc(store.lede) + "</textarea>" +
      "<small>The line under the heading on the Bookstore page.</small></label>" +
      text("Button", store.visitLabel, ' data-s="visitLabel"', "The home page’s button to the Bookstore page.") +
      '<label class="adm-label">Collecting a book<textarea data-s="pickup" rows="3">' + esc(store.pickup) + "</textarea>" +
      "<small>On each book’s page and in the receipt: where and when reserved books are collected.</small></label>" +
      text("Held for", store.hold, ' data-s="hold" placeholder="14 days"', "How long a reserved book is kept; in the cart and the receipt. Empty hides it.") +
      text("Pay with", store.payWith, ' data-s="payWith" placeholder="Cash or card"', "How a reserved book is paid for at the masjid; in the cart and the receipt. Empty hides it.") +
      text("Reservations address", store.reserveTo, ' data-s="reserveTo" placeholder="https://script.google.com/macros/s/…/exec" spellcheck="false"', "The Apps Script web app the cart sends reservations to (tools/reserve/README.md). Empty: no book can be added to the cart.") +
      '<div class="adm-label">Books<ol class="adm-books">' +
      list.map(function (bk, i) {
        return '<li class="adm-books__row' + (i === sel ? " is-picked" : "") + '">' +
          '<button class="adm-books__name" type="button" data-pick="' + i + '"' + (i === sel ? ' aria-current="true"' : "") + ">" +
          esc(label(bk, i)) + (bk.size === "large" || bk.size === "medium" ? ' <span class="adm-books__tag">' + bk.size + "</span>" : "") + "</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':-1" aria-label="Move earlier"' + (i === 0 ? " disabled" : "") + ">↑</button>" +
          '<button class="adm-tool" type="button" data-move="' + i + ':1" aria-label="Move later"' + (i === list.length - 1 ? " disabled" : "") + ">↓</button></li>";
      }).join("") + "</ol>" +
      "<small>★ marks a featured book. The home page shows three rows of books with a picture, the featured first; a large card takes four places, a medium one two. Drag a card onto another to move it.</small>" +
      '<button class="adm-btn" type="button" data-p="add">+ Add a book</button></div>' +
      tabNote();

    if (b) {
      html +=
        '<hr class="adm-hr"><h2 class="adm-panel__head">Book ' + (sel + 1) + "</h2>" +
        text("Title", b.title, ' data-f="title"') +
        text("Author", b.author, ' data-f="author"', "On the book’s page under the title; the Bookstore page’s search finds books by it. Empty hides it.") +
        text("Subject", b.subject, ' data-f="subject" list="adm-store-subjects"',
          "The small line above the title. The Bookstore page filters by it.") +
        '<datalist id="adm-store-subjects">' + subjects().map(function (c) { return '<option value="' + esc(c) + '">'; }).join("") + "</datalist>" +
        '<div class="adm-label">Years' +
          years().map(function (y) {
            return '<label class="adm-check"><input type="checkbox" data-year="' + esc(y) + '"' +
              ((b.years || []).indexOf(y) >= 0 ? " checked" : "") + "> " + esc(y) + "</label>";
          }).join("") +
        "<small>The years it is taught in. The Bookstore page groups and filters by them.</small></div>" +
        '<label class="adm-label">Description<textarea data-f="description" rows="4">' + esc(b.description) + "</textarea>" +
        "<small>On the book’s page, under its years.</small></label>" +
        text("Page id", b.id, ' data-f="id" spellcheck="false"',
          "Its page is book.html?id=" + esc(b.id || "…") + ". Lowercase words joined by hyphens; empty: no page.") +
        '<label class="adm-check"><input type="checkbox" data-f="featured"' + (b.featured ? " checked" : "") + "> Featured on the home page</label>" +
        sizeAndTint(b) +
        printFields(b) +
        '<label class="adm-label">Binding<select data-f="color">' +
          BINDINGS.map(function (n) { return '<option' + (n === (b.color || "lapis") ? " selected" : "") + ">" + n + "</option>"; }).join("") +
        "</select><small>Drawn when there is no picture.</small></label>" +
        '<div class="adm-row adm-row--gap"><span></span>' +
        '<button class="adm-btn adm-btn--danger" type="button" data-p="delete">Delete book</button></div>';
    } else {
      html += '<hr class="adm-hr"><p class="adm-help">Click a card, or a title above, to edit that book.</p>';
    }
    html += '<hr class="adm-hr"><div class="adm-help">' +
      (all ? "This page shows every book." : "This section shows three rows of books with a picture, the featured first; the Bookstore page shows them all.") +
      " Changes show on the page as you type. Ctrl+S saves.</div>";
    ui.panel.innerHTML = html;
    showCover();
    showTintPick();
  }

  // The fields of one print: the book's own, or, for a book of several,
  // the picked print's, with the prints to pick between.
  function printFields(b) {
    var p = target(), many = !!b.prints, n = selPrint + 1;
    var head = '<div class="adm-label">Prints';
    if (many) {
      head += '<div class="adm-seg" role="group" aria-label="Print">' +
        b.prints.map(function (q, k) {
          return '<button class="adm-btn" type="button" data-print="' + k + '" aria-pressed="' + (k === selPrint) + '" title="' +
            esc(q.edition || "Print " + (k + 1)) + '">' + (k + 1) + "</button>";
        }).join("") + "</div>" +
        '<div class="adm-row adm-row--gap">' +
          '<button class="adm-tool" type="button" data-pmove="-1" aria-label="Move this print earlier"' + (selPrint === 0 ? " disabled" : "") + ">←</button>" +
          '<button class="adm-tool" type="button" data-pmove="1" aria-label="Move this print later"' + (selPrint === b.prints.length - 1 ? " disabled" : "") + ">→</button>" +
          '<button class="adm-btn" type="button" data-p="add-print">+ Add a print</button>' +
          '<button class="adm-btn adm-btn--danger" type="button" data-p="remove-print">Remove print ' + n + "</button></div>" +
        "<small>Each print has its own edition, price and picture, and is reserved on its own. The card fans out the first three pictures, the first in front, and shows the range of prices; the book’s page lets the buyer choose.</small></div>" +
        '<h3 class="adm-panel__head">Print ' + n + "</h3>";
    } else {
      head += '<button class="adm-btn" type="button" data-p="add-print">+ Add another print</button>' +
        "<small>For a book sold in more than one print (another edition or cover, perhaps at another price).</small></div>";
    }
    return head +
      text("Edition", p.edition, ' data-f="edition"', many ? "What tells this print from the others; on the book’s page under the title." : "The line under the title, telling one edition from another; empty hides it.") +
      text("Price", p.price, ' data-f="price" placeholder="$12.00"', "Written like $12.00; empty hides it. Only a print with a price can be reserved.") +
      '<label class="adm-check"><input type="checkbox" data-f="soldOut"' + (p.soldOut ? " checked" : "") + "> Sold out</label>" +
      '<label class="adm-label">Picture<input data-f="cover" value="' + esc(p.cover) + '" placeholder="assets/img/books/name.jpg" spellcheck="false">' +
      "<small data-cover-note>Ideally 3:4. Leave empty and the binding below is drawn instead.</small></label>" +
      '<img class="adm-cover" alt="" hidden>';
  }

  // Which layout the cards and the card size change: All's, or the open tab's.
  function tabNote() {
    if (!all) return "";
    var g = tab(), own = g && store.layouts && store.layouts[g];
    if (!g) {
      return '<div class="adm-label">Layout: All<small>Dragging cards and the card size change the All tab: the list’s own order and sizes. ' +
        "Open a subject tab above the cards to lay that tab out on its own.</small></div>";
    }
    return '<div class="adm-label">Layout: ' + esc(g) + "<small>" +
      (own ? "This tab has its own layout. " : "This tab follows All until a card in it is moved or resized. ") +
      "Dragging cards and the card size change this tab only; ↑/↓ in the list above move a book in All.</small>" +
      (own ? '<button class="adm-btn" type="button" data-p="reset-tab">Follow All again</button>' : "") + "</div>";
  }

  // The card's size (in the open tab, or in All), and a large card's colour:
  // its own, or its cover's.
  function sizeAndTint(b) {
    var size = sizeHere(b);
    var html = '<div class="adm-label">Card size' + (tab() ? " in " + esc(tab()) : "") +
      '<div class="adm-seg" role="group" aria-label="Card size">' +
      '<button class="adm-btn" type="button" data-size="normal" aria-pressed="' + (size === "normal") + '">Normal</button>' +
      '<button class="adm-btn" type="button" data-size="medium" aria-pressed="' + (size === "medium") + '">Medium</button>' +
      '<button class="adm-btn" type="button" data-size="large" aria-pressed="' + (size === "large") + '">Large</button></div>' +
      "<small>Medium: two columns wide and one row high; large: two wide and two high. Both are in the book’s colour, with its description." +
      (tab() ? " Only in this tab." : "") + "</small></div>";
    if (size === "normal") return html;
    var now = b.tint || coverTone();
    return html +
      '<div class="adm-label">Card colour' +
        '<div class="adm-tint"><input type="color" data-f="tint" value="' + esc(now) + '" aria-label="Card colour">' +
        '<code>' + esc(b.tint || "the cover’s") + "</code>" +
        (b.tint ? '<button class="adm-btn" type="button" data-tint="reset">Use the cover’s</button>' : "") +
        (window.EyeDropper ? '<button class="adm-btn" type="button" data-tint="screen" title="Pick a colour from anywhere on the screen">Pick from screen</button>' : "") +
        "</div>" +
        '<canvas class="adm-tintpick" hidden></canvas>' +
        "<small>Click the picture to take its colour from that spot, or choose one. Left alone, the card takes the colour measured from the cover.</small></div>";
  }

  // The colour the picked book's card has now (measured, or its binding's).
  function coverTone() {
    var card = mount.querySelector('.store-card[data-i="' + sel + '"]');
    var b = book(), keep = b && b.tint;
    var tone = card ? getComputedStyle(card).getPropertyValue("--tone").trim() : "";
    if (keep) tone = "";   // with a tint set, the card shows the tint, not the cover's
    return /^#[0-9a-f]{6}$/i.test(tone) ? tone : "#5a3a26";
  }

  // Draws the book's picture into the panel, to pick a colour off.
  function showTintPick() {
    var canvas = ui.panel.querySelector(".adm-tintpick");
    var card = mount.querySelector('.store-card[data-i="' + sel + '"]');
    var img = card && card.querySelector(".store-card__pic img");
    if (!canvas || !img) return;
    var pic = new Image();
    pic.onload = function () {
      var w = 220, h = Math.round(w * pic.naturalHeight / pic.naturalWidth);
      canvas.width = w;
      canvas.height = h;
      canvas.getContext("2d").drawImage(pic, 0, 0, w, h);
      canvas.hidden = false;
    };
    pic.src = img.currentSrc || img.src;
  }

  // The colour under a click on the picture, averaged over a few pixels.
  function pickTint(e) {
    var canvas = e.target, r = canvas.getBoundingClientRect();
    var x = Math.round((e.clientX - r.left) * canvas.width / r.width);
    var y = Math.round((e.clientY - r.top) * canvas.height / r.height);
    var d;
    try { d = canvas.getContext("2d").getImageData(Math.max(0, x - 2), Math.max(0, y - 2), 5, 5).data; } catch (err) { return; }
    var sum = [0, 0, 0], n = d.length / 4;
    for (var i = 0; i < d.length; i += 4) { sum[0] += d[i]; sum[1] += d[i + 1]; sum[2] += d[i + 2]; }
    setTint("#" + sum.map(function (v) { return ("0" + Math.round(v / n).toString(16)).slice(-2); }).join(""));
  }

  function setTint(hex) {
    var b = book();
    if (hex) b.tint = hex.toLowerCase(); else delete b.tint;
    changed();
    draw();
    paintPanel();
  }

  function text(name, value, extra, note) {
    return '<label class="adm-label">' + name + '<input value="' + esc(value) + '"' + extra + ">" +
      (note ? "<small>" + note + "</small>" : "") + "</label>";
  }

  // A thumbnail of the picture, or a word that the path finds nothing.
  function showCover() {
    var img = ui.panel.querySelector(".adm-cover");
    var note = ui.panel.querySelector("[data-cover-note]");
    var b = target();
    if (!img || !b) return;
    if (!b.cover) { img.hidden = true; note.classList.remove("adm-bad"); return; }
    img.onload = function () { img.hidden = false; note.classList.remove("adm-bad"); note.textContent = "Found."; };
    img.onerror = function () { img.hidden = true; note.classList.add("adm-bad"); note.textContent = "No image at that path yet."; };
    img.src = b.cover;
  }

  function relabel() {
    var row = ui.panel.querySelector('[data-pick="' + sel + '"]');
    if (row) row.textContent = label(book(), sel);
  }

  function onInput(e) {
    var t = e.target;
    if (t.dataset.s) { store[t.dataset.s] = /^(lede|pickup)$/.test(t.dataset.s) ? t.value.replace(/\s+/g, " ") : t.value; changed(); return; }
    var f = t.dataset.f, b = book();
    if (b && t.dataset.year != null) {
      // Kept in the order of the boxes.
      b.years = Array.prototype.filter.call(ui.panel.querySelectorAll("[data-year]"), function (box) {
        return box.checked;
      }).map(function (box) { return box.dataset.year; });
      changed();
      return;
    }
    if (!f || !b) return;
    // A print's fields go to the picked print (or the book of one).
    if (PRINT.indexOf(f) >= 0) {
      var p = target();
      if (f === "soldOut") { if (t.checked) p.soldOut = true; else delete p.soldOut; }
      else if (f === "cover") { p.cover = t.value.trim(); showCover(); }
      else p[f] = t.value.replace(/\s+/g, " ");
      if (f === "edition" && b.prints) {
        var tab = ui.panel.querySelector('[data-print="' + selPrint + '"]');
        if (tab) tab.title = p.edition || "Print " + (selPrint + 1);
      }
      changed();
      return;
    }
    // An id that followed the title keeps following it.
    if (f === "title" && "id" in b && (b.id === "" || b.id === slug(b.title))) {
      renameId(b.id, slug(t.value));
      b.id = slug(t.value);
      var idBox = ui.panel.querySelector('[data-f="id"]');
      if (idBox) idBox.value = b.id;
    }
    if (f === "featured") b.featured = t.checked;
    else if (f === "id") { renameId(b.id, t.value.trim()); b.id = t.value.trim(); }
    else if (f === "color") b.color = t.value;
    else if (f === "tint") { b.tint = t.value.toLowerCase(); var code = ui.panel.querySelector(".adm-tint code"); if (code) code.textContent = b.tint; changed(); return; }
    else b[f] = t.value.replace(/\s+/g, " ");
    if (f === "title" || f === "featured") relabel();
    changed();
    if (f === "featured") { draw(); mark(); }
  }

  function onClick(e) {
    var t = e.target.closest("button");
    if (!t) return;
    if (t.dataset.pick != null) return pick(+t.dataset.pick, true);
    if (t.dataset.move) {
      var parts = t.dataset.move.split(":"), from = +parts[0];
      move(from, from + +parts[1]);
      return;
    }
    if (t.dataset.size) {
      // Normal is the default, so it is written by leaving the field out.
      var b = book();
      if (tab()) {
        // Only this tab; the colour stays, for the tabs where it is large.
        if (!b.id) { status("Give the book a page id to size it in a tab", true); return; }
        var lay = tabLayout();
        ["large", "medium"].forEach(function (f) {
          var k = lay[f].indexOf(b.id);
          if (k >= 0) lay[f].splice(k, 1);
          if (f === t.dataset.size) lay[f].push(b.id);
        });
      } else if (t.dataset.size !== "normal") b.size = t.dataset.size; else { delete b.size; delete b.tint; }
      changed();
      draw();
      paintPanel();
      return;
    }
    if (t.dataset.print != null) { selPrint = +t.dataset.print; paintPanel(); return; }
    if (t.dataset.pmove) { movePrint(+t.dataset.pmove); changed(); draw(); paintPanel(); return; }
    if (t.dataset.p === "add-print" || t.dataset.p === "remove-print") {
      if (t.dataset.p === "add-print") addPrint(); else if (!removePrint()) return;
      changed();
      draw();
      paintPanel();
      relabel();
      return;
    }
    if (t.dataset.tint === "reset") return setTint("");
    if (t.dataset.tint === "screen" && window.EyeDropper) {
      new window.EyeDropper().open().then(function (r) { setTint(r.sRGBHex); }).catch(function () {});
      return;
    }
    if (t.dataset.p === "reset-tab") {
      delete layouts()[tab()];
      changed();
      draw();
      paintPanel();
      return;
    }
    if (t.dataset.p === "add") addBook();
    else if (t.dataset.p === "delete") deleteBook();
  }

  function addBook() {
    // Added from the home page, it is featured, so it shows there.
    store.books.push({ id: slug("New book"), title: "New book", subject: "", years: [], price: "", description: "", cover: "", color: "lapis", featured: !all });
    changed();
    draw();
    pick(store.books.length - 1, true);
    var title = ui.panel.querySelector('[data-f="title"]');
    title.focus();
    title.select();
  }

  function deleteBook() {
    var b = book();
    if (!confirm("Delete “" + (b.title || "Untitled") + "”?\n\nIt goes from bookstore.json when you save.")) return;
    renameId(b.id, "");
    store.books.splice(sel, 1);
    changed();
    draw();
    pick(Math.min(sel, store.books.length - 1), false);
  }

  /* -------------------------------- saving ------------------------------ */
  function problem() {
    var seen = {};
    for (var i = 0; i < store.books.length; i++) {
      var b = store.books[i], where = "book " + (i + 1);
      if (!String(b.title || "").trim()) return where + " has no title";
      if (store.reserveTo && store.reserveTo.indexOf("https://") !== 0) return "the reservations address must start with https://";
      if (b.id === "") delete b.id;
      if (b.id == null) continue;
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(b.id)) return where + ": the page id must be lowercase words joined by hyphens";
      if (seen[b.id]) return where + ": the page id “" + b.id + "” is used twice";
      seen[b.id] = true;
    }
    return null;
  }

  function save(force) {
    if (ui.saving) return;
    var bad = problem();
    if (bad) { status("Not saved: " + bad, true); return; }
    pruneLayouts();
    ui.saving = true;
    status("Saving…");
    fetch(API, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: store.version, force: !!force,
                             heading: store.heading, kicker: store.kicker, lede: store.lede,
                             visitLabel: store.visitLabel, pickup: store.pickup, hold: store.hold,
                             payWith: store.payWith, reserveTo: store.reserveTo, books: store.books, layouts: layouts() })
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, ok: r.ok, json: j }; });
    }).then(function (res) {
      ui.saving = false;
      if (res.status === 409) {
        if (confirm("bookstore.json has changed on disk since the editor loaded it (edited by hand, or saved from another tab).\n\n" +
                    "OK overwrites it with what is here. Cancel keeps editing; Discard would load the newer file.")) {
          save(true);
        } else {
          status("Not saved: bookstore.json changed on disk", true);
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
    if (dirty && !confirm("Throw away every unsaved change to the bookstore?")) return;
    load().then(function () {
      dirty = false;
      sel = -1;
      draw();
      paintPanel();
      status("Changes discarded");
    }).catch(function () { status("Could not reload bookstore.json", true); });
  }

  // Leaving the editor reloads the page, so the site draws what was saved.
  function done() {
    if (dirty && !confirm("Leave the editor without saving?")) return;
    dirty = false;
    location.reload();
  }

  /* -------------------------------- set-up ------------------------------ */
  function enter() {
    on = true;
    document.body.classList.add("adm-side", "adm-bookstore");
    ui.launches.hidden = true;

    ui.panel = el("aside", "adm-panel adm-panel--shelf");
    ui.panel.setAttribute("aria-label", "Bookstore editor");
    ui.panel.addEventListener("input", onInput);
    ui.panel.addEventListener("click", onClick);
    ui.panel.addEventListener("click", function (e) { if (e.target.classList.contains("adm-tintpick")) pickTint(e); });
    document.body.appendChild(ui.panel);

    ui.bar = el("div", "adm-bar",
      '<span class="adm-status" role="status"></span>' +
      '<button class="adm-btn" type="button" data-bar="discard">Discard</button>' +
      '<button class="adm-btn" type="button" data-bar="done">Done</button>' +
      '<button class="adm-btn adm-btn--gold" type="button" data-bar="save" title="Save (Ctrl+S)">Save</button>');
    ui.bar.setAttribute("role", "toolbar");
    ui.bar.setAttribute("aria-label", "Bookstore editor");
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
    // The site redraws the cards when a tab is chosen; the editor follows.
    document.addEventListener("bookstore:tab", function () { decorate(); paintPanel(); });
    window.addEventListener("beforeunload", function (e) {
      if (dirty) { e.preventDefault(); e.returnValue = ""; }
    });

    draw();
    paintPanel();
    // The page has narrowed for the panel; let the carousels measure again.
    window.dispatchEvent(new Event("resize"));
    section().scrollIntoView({ block: "start" });
  }

  // The site draws the cards from its own fetch; wait for it, or it could
  // draw over the editor once that has started.
  function drawn() {
    return new Promise(function (resolve) {
      var tries = 0;
      (function check() {
        if (mount.firstChild || ++tries > 100) resolve(); else setTimeout(check, 50);
      })();
    });
  }

  // The page's editors share one stack of launch buttons.
  function launches() {
    return document.querySelector(".adm-launches") || document.body.appendChild(el("div", "adm-launches"));
  }

  // A preview only, never saved: bookstore.html with 4, 5 or 6 books across,
  // the page widened so a column keeps its width. Remembered in this browser.
  var COLS_KEY = "alimiyyah.admin.storeCols";
  function widthButton() {
    var cols = 4;
    try { cols = +localStorage.getItem(COLS_KEY) || 4; } catch (e) {}
    var b = el("button", "adm-btn adm-btn--gold adm-launch", "");
    b.type = "button";
    b.title = "Preview the bookstore 4, 5 or 6 books across (not saved to the site)";
    function apply() {
      document.documentElement.setAttribute("data-adm-cols", cols);
      b.textContent = "⇔ " + cols + " across";
      try { localStorage.setItem(COLS_KEY, cols); } catch (e) {}
    }
    b.addEventListener("click", function () { cols = cols >= 6 ? 4 : cols + 1; apply(); });
    apply();
    return b;
  }

  function boot() {
    if (!mount || !window.renderBookstore) return;
    mount.addEventListener("click", onSectionClick, true);
    mount.addEventListener("dragstart", onDragStart);
    mount.addEventListener("dragover", onDragOver);
    mount.addEventListener("drop", onDrop);
    mount.addEventListener("dragend", onDragEnd);
    Promise.all([load(), drawn()]).then(function () {
      ui.launches = launches();
      var launch = el("button", "adm-btn adm-btn--gold adm-launch", "✎ Edit bookstore");
      launch.type = "button";
      launch.addEventListener("click", enter);
      ui.launches.appendChild(launch);
      if (all) ui.launches.appendChild(widthButton());
      // The bookstore dashboard (/__admin/books): every book and print in a list.
      var dash = el("a", "adm-btn adm-btn--gold adm-launch", "▤ Book dashboard");
      dash.href = "/__admin/books";
      ui.launches.appendChild(dash);
    }).catch(function (err) {
      console.error("The bookstore editor could not load bookstore.json.", err);
    });
  }

  boot();
})();

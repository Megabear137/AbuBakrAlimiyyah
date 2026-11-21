/* =====================================================================
   book.js - fills book.html: one book from content/bookstore.json, found
   by the ?id= in the address, as its bookstore leaf opened - the cover,
   the colophon (name, edition, years), its description, the price (and,
   for a book of several prints, the prints to choose between) - with
   the way to reserve it and how it is collected. Books are reserved, not
   bought: "Add to cart" puts the chosen print in the cart (cart.js, loaded
   first), whose slip takes the reader's name and email and sends the
   reservation; the book is paid for and collected at the masjid. A print
   can be added only when bookstore.json has "reserveTo" and the print has
   a price like $12.00 and isn't sold out. Needs curriculum.js loaded first
   for the drawn binding of a book without a photograph. The footer's
   contact lines come from program.json.
   ===================================================================== */
(function (global) {
  "use strict";

  var slot = function (name) { return document.querySelector('[data-slot="' + name + '"]'); };

  var ICONS = {
    home:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 11l8-7 8 7v9H4z"/></svg>',
    mail:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3.5" y="5.5" width="17" height="13" rx="1.5"/><path d="M4 7l8 6 8-6"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    arrow: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg>'
  };

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

  function loadJSON(path) {
    return fetch(path, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(path + " -> HTTP " + r.status);
      return r.json();
    });
  }

  /* ------------------------------- the book ----------------------------- */
  // A book's prints: its "prints", or the book itself as its one print (as
  // bookstore.js and cart.js read them; keep the three in step).
  var PRINT = ["edition", "price", "cover", "soldOut"];
  function printsOf(b) {
    if (Array.isArray(b.prints) && b.prints.length) return b.prints;
    var one = {};
    PRINT.forEach(function (f) { if (f in b) one[f] = b[f]; });
    return [one];
  }

  // The tight crops (tools/covers.py), loaded before the book is drawn so
  // the page never shows the uncut photograph first.
  var tight = {};

  // i is the book's place in the whole list, which picks the drawn
  // binding's shade, as on the bookstore's cards. A book of several prints
  // has a row of them to choose from (?print=<n> picks one on load, as the
  // cart's links carry); the cover, edition, price and the button are the
  // chosen print's.
  function renderBook(data, b, i, at) {
    document.title = b.title + " — Jāmiʿah Islāmiyah Abū Bakr";
    var draw = global.renderCurriculum && global.renderCurriculum.drawnCover;
    var drawn = draw ? draw(b, i) : "";
    var prints = printsOf(b);
    // A print's picture: its tight crop, else the whole photograph, else the binding drawn.
    function srcOf(p) { return p.cover ? (tight[p.cover] && tight[p.cover].tight) || p.cover : drawn; }
    slot("book-subject").textContent = b.subject || "";
    slot("book-title").textContent = b.title;
    slot("book-category").textContent = (Array.isArray(b.years) ? b.years : []).join(" · ");
    slot("book-description").textContent = b.description || "";
    slot("book-pickup").textContent = data.pickup || "";

    var chooser = slot("book-prints");
    if (prints.length > 1) {
      chooser.appendChild(el("p", "b-prints__label", prints.length + " prints"));
      var row = el("div", "b-prints");
      row.setAttribute("role", "group");
      row.setAttribute("aria-label", "Print");
      prints.forEach(function (p, k) {
        var btn = el("button", "b-print",
          '<span class="b-print__pic"><img' + (tight[p.cover] ? ' class="is-tight"' : "") + ' src="' + esc(srcOf(p)) + '" alt="" width="60" height="80"></span>' +
          '<span class="b-print__price">' + esc(p.soldOut ? "Sold out" : p.price || "") + "</span>");
        btn.type = "button";
        btn.setAttribute("aria-label", [p.edition || "Print " + (k + 1), p.soldOut ? "sold out" : p.price].filter(Boolean).join(", "));
        btn.addEventListener("click", function () { show(k, true); });
        row.appendChild(btn);
      });
      chooser.appendChild(row);
    }

    function show(k, chosen) {
      var p = prints[k];
      if (chooser.firstChild) {
        chooser.querySelectorAll(".b-print").forEach(function (btn, n) { btn.setAttribute("aria-pressed", String(n === k)); });
      }
      if (chosen) {
        try {
          var u = new URL(location.href);
          u.searchParams.set("print", String(k + 1));
          history.replaceState(null, "", u);
        } catch (e) {}
      }
      var src = srcOf(p);
      slot("book-cover").innerHTML = src ? '<span class="b-frame"><img class="store-card__cover' + (tight[p.cover] ? " store-card__cover--tight" : "") +
        '" src="' + esc(src) + '" width="300" height="400" alt="' +
        (p.cover ? "Cover of " + esc(b.title) + (p.edition ? ", " + esc(p.edition) : "") : "") + '"></span>' : "";
      slot("book-edition").textContent = p.edition || "";
      var price = slot("book-price");
      price.textContent = p.price || "";
      price.classList.toggle("b-leaf__price--todo", isTodo(p.price));

      current = k;
      drawBuy();
    }

    // The way to reserve the chosen print: "Add to cart", or, once it is
    // in the cart, a note saying so and the button that opens the cart.
    var current = 0, refocus = false;
    var buy = slot("book-buy");
    function drawBuy() {
      var p = prints[current], cart = global.cart;
      var had = refocus || buy.contains(document.activeElement);
      refocus = false;
      buy.textContent = "";
      if (p.soldOut) {
        buy.appendChild(el("p", "b-leaf__sold", "Sold out"));
        return;
      }
      if (!cart || !b.id || !data.reserveTo || cart.cents(p.price) == null) return;
      var inCart = cart.has(b.id, current);
      if (inCart) buy.appendChild(el("p", "b-leaf__added", '<i aria-hidden="true">' + ICONS.check + "</i> In your cart"));
      var btn = el("button", "btn btn--gold", inCart ? "View cart " + ICONS.arrow : "Add to cart");
      btn.type = "button";
      btn.addEventListener("click", function () {
        if (inCart) cart.open();
        else { refocus = true; cart.add(b.id, current); }   // cart:change redraws this
      });
      buy.appendChild(btn);
      buy.appendChild(el("p", "b-leaf__note", "Reserve now, pay at the masjid when you collect"));
      if (had) btn.focus();
    }
    document.addEventListener("cart:change", drawBuy);
    show(at >= 0 && at < prints.length ? at : 0, false);
  }

  function notFound() {
    slot("book-title").textContent = "Book not found";
    slot("book-pickup").textContent = "This page may have been moved or taken down.";
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

  /* -------------------------------- boot -------------------------------- */
  var yearSlot = slot("year");
  if (yearSlot) yearSlot.textContent = String(new Date().getFullYear());

  var params = new URLSearchParams(location.search);
  var id = params.get("id");

  Promise.all([
    Promise.all([
      loadJSON("content/bookstore.json"),
      loadJSON("assets/img/books/tight/covers.json").catch(function () { return {}; })
    ]).then(function (got) {
      var data = got[0];
      tight = got[1] || {};
      var books = data.books || [], at = -1;
      books.forEach(function (b, i) { if (at < 0 && id && b.id === id) at = i; });
      if (at < 0) return notFound();
      renderBook(data, books[at], at, (parseInt(params.get("print"), 10) || 1) - 1);
    }),
    loadJSON("content/program.json").then(function (data) { renderFooter(data.footer); })
  ]).catch(function (err) {
    console.error("Content failed to load.", err);
    slot("book-title").textContent = "Bookstore";
    slot("book-pickup").textContent =
      "The book could not be loaded. If you opened this file directly, serve the folder over " +
      "a local web server instead (see CLAUDE.md).";
  });
})(window);

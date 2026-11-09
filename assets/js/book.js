/* =====================================================================
   book.js - fills book.html: one book from content/bookstore.json, found
   by the ?id= in the address, as its bookstore leaf opened - the cover,
   the colophon (name, edition, years), its description, the price (and,
   for a book of several prints, the prints to choose between) - with
   the way to buy it and how it is collected. The Buy button is the book's Stripe Payment Link: Stripe
   takes the payment, emails the receipt and the order, and sends the buyer
   back here with &paid=1, which shows the thanks instead. Nothing on this
   page takes a payment or writes anything. Needs curriculum.js loaded
   first for the drawn binding of a book without a photograph. The footer's
   contact lines come from program.json.
   ===================================================================== */
(function (global) {
  "use strict";

  var slot = function (name) { return document.querySelector('[data-slot="' + name + '"]'); };

  var ICONS = {
    home:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 11l8-7 8 7v9H4z"/></svg>',
    mail:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3.5" y="5.5" width="17" height="13" rx="1.5"/><path d="M4 7l8 6 8-6"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
  };

  // Only a Stripe Payment Link is followed; anything else draws no button.
  var STRIPE = /^https:\/\/buy\.stripe\.com\//;

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
  // bookstore.js reads them; keep the two in step).
  var PRINT = ["edition", "price", "cover", "buyHref", "soldOut"];
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
  // has a row of them to choose from (?print=<n> picks one on load, which
  // a print's Stripe redirect carries); the cover, edition, price and Buy
  // button are the chosen print's.
  function renderBook(data, b, i, paid, at) {
    document.title = b.title + " — Jamiyah Islamiyyah Abu Bakr";
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

      var buy = slot("book-buy");
      buy.textContent = "";
      if (paid) {
        buy.appendChild(el("p", "b-leaf__thanks", '<i aria-hidden="true">' + ICONS.check + "</i><span>" +
          esc(data.thanks || "Thank you. Your receipt is on its way to your email.") + "</span>"));
      } else if (p.soldOut) {
        buy.appendChild(el("p", "b-leaf__sold", "Sold out"));
      } else if (STRIPE.test(p.buyHref || "")) {
        var a = el("a", "btn btn--gold", esc(data.buyLabel || "Buy") +
          ' <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg>');
        a.href = p.buyHref;
        buy.appendChild(a);
        buy.appendChild(el("p", "b-leaf__note", "Paid securely through Stripe"));
      }
    }
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
    if (footer.address) line(ICONS.home, esc(footer.address));
    if (footer.email) {
      line(ICONS.mail, isTodo(footer.email) ? esc(footer.email)
        : '<a href="mailto:' + esc(footer.email) + '">' + esc(footer.email) + "</a>");
    }
    if (footer.phone) line(ICONS.phone, esc(footer.phone));
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
      renderBook(data, books[at], at, params.get("paid") === "1", (parseInt(params.get("print"), 10) || 1) - 1);
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

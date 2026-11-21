/* =====================================================================
   cart.js - the bookstore's cart and the reservation slip, on every page.

   Books are reserved, not bought. A book's page adds a print to the cart
   (window.cart.add); the cart lives in this browser's localStorage under
   "alimiyyah.cart" as [{id, print, qty}] (print is the place in the book's
   prints, 0 for a book of one). The header gets a round button with the
   count, shown while the cart holds anything; it opens the slip: the books,
   each with its copies and price, the sum to pay at collection, then, below
   a perforation, the reader's name and email and the Reserve button.

   Reserve posts {name, email, items} as JSON to bookstore.json's
   "reserveTo", the Google Apps Script web app in tools/reserve/, which
   checks the books against bookstore.json, records them in the masjid's
   sheet, emails the reader a receipt and answers {ok, ref} or {ok: false,
   message}. Nothing is paid here: the reader pays at the masjid.

   window.cart: add(id, print), has(id, print), count(), open(); a
   "cart:change" event on document after every change (also from another
   tab). Uses renderCurriculum.drawnCover for a book without a photograph
   when curriculum.js is on the page.
   ===================================================================== */
(function (global) {
  "use strict";

  var KEY = "alimiyyah.cart";
  var MAX_QTY = 5, MAX_LINES = 20;
  var TIMEOUT = 25000;
  var root = document.documentElement;

  var ICONS = {
    bag:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M5 8h14l-1.2 12H6.2z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    arrow: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg>'
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // "$1,250.00" -> 125000 cents; anything not written like that -> null
  // (such a print can't be reserved).
  function cents(price) {
    var m = /^\$(\d{1,3}(?:,\d{3})*|\d+)\.(\d{2})$/.exec(String(price || "").trim());
    return m ? parseInt(m[1].replace(/,/g, ""), 10) * 100 + parseInt(m[2], 10) : null;
  }
  function money(c) {
    var s = String(Math.floor(c / 100)).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return "$" + s + "." + ("0" + (c % 100)).slice(-2);
  }

  /* ------------------------------ storage ------------------------------ */
  function read() {
    var v = [];
    try { v = JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) {}
    if (!Array.isArray(v)) return [];
    return v.filter(function (l) {
      return l && typeof l.id === "string" && l.print === (l.print | 0) && l.print >= 0 &&
        l.qty === (l.qty | 0) && l.qty >= 1;
    }).map(function (l) { return { id: l.id, print: l.print, qty: Math.min(l.qty, MAX_QTY) }; }).slice(0, MAX_LINES);
  }
  var lines = read();

  function changed() {
    syncButton();
    if (isOpen() && state !== "done" && state !== "sending") draw();
    document.dispatchEvent(new CustomEvent("cart:change"));
  }
  function write() {
    try { localStorage.setItem(KEY, JSON.stringify(lines)); } catch (e) { /* blocked: this page only */ }
    changed();
  }
  addEventListener("storage", function (e) {
    if (e.key === KEY) { lines = read(); changed(); }
  });
  // Back/forward restores a page from the browser's cache as it was left,
  // with the cart it had then; a storage event doesn't reach a cached page.
  addEventListener("pageshow", function (e) {
    if (e.persisted && JSON.stringify(read()) !== JSON.stringify(lines)) { lines = read(); changed(); }
  });

  function at(id, print) {
    for (var i = 0; i < lines.length; i++) if (lines[i].id === id && lines[i].print === print) return i;
    return -1;
  }
  function count() { return lines.reduce(function (n, l) { return n + l.qty; }, 0); }

  /* ------------------------------ the data ----------------------------- */
  // bookstore.json and the tight crops, fetched once, when first needed.
  var loading = null, store = null, tight = {};
  function load() {
    if (!loading) {
      var get = function (p) {
        return fetch(p, { cache: "no-cache" }).then(function (r) {
          if (!r.ok) throw new Error(p + " -> HTTP " + r.status);
          return r.json();
        });
      };
      loading = Promise.all([
        get("content/bookstore.json"),
        get("assets/img/books/tight/covers.json").catch(function () { return {}; })
      ]).then(function (got) { store = got[0]; tight = got[1] || {}; return store; });
      loading.catch(function () { loading = null; });
    }
    return loading;
  }

  // A book's prints (as bookstore.js and book.js read them; keep in step).
  var PRINT = ["edition", "price", "cover", "soldOut"];
  function printsOf(b) {
    if (Array.isArray(b.prints) && b.prints.length) return b.prints;
    var one = {};
    PRINT.forEach(function (f) { if (f in b) one[f] = b[f]; });
    return [one];
  }

  // Each line with its book and print; lines whose book or print has gone,
  // or that can no longer be reserved, are dropped from the cart.
  function resolve() {
    var books = (store && store.books) || [], out = [], kept = [];
    lines.forEach(function (l) {
      for (var i = 0; i < books.length; i++) {
        var b = books[i];
        if (b.id !== l.id) continue;
        var p = printsOf(b)[l.print];
        if (p && !p.soldOut && cents(p.price) != null) {
          out.push({ line: l, book: b, index: i, print: p, many: printsOf(b).length > 1, each: cents(p.price) });
          kept.push(l);
        }
        return;
      }
    });
    if (store && kept.length !== lines.length) {
      lines = kept;
      try { localStorage.setItem(KEY, JSON.stringify(lines)); } catch (e) {}
      syncButton();
      document.dispatchEvent(new CustomEvent("cart:change"));
    }
    return out;
  }

  function picture(r) {
    var p = r.print;
    if (p.cover) return { src: (tight[p.cover] && tight[p.cover].tight) || p.cover, tight: !!tight[p.cover] };
    var draw = global.renderCurriculum && global.renderCurriculum.drawnCover;
    return { src: draw ? draw(r.book, r.index) : "", tight: false };
  }

  /* --------------------------- header button --------------------------- */
  var button = null;
  function makeButton() {
    var end = document.querySelector(".site-header__end");
    if (!end) return;
    button = document.createElement("button");
    button.type = "button";
    button.className = "round cart-btn";
    button.setAttribute("aria-haspopup", "dialog");
    button.innerHTML = ICONS.bag + '<span class="cart-btn__n" aria-hidden="true"></span>';
    button.hidden = true;
    button.addEventListener("click", function () { open(); });
    end.insertBefore(button, end.firstChild);
  }
  function syncButton() {
    if (!button) return;
    var n = count();
    button.hidden = n === 0;
    button.querySelector(".cart-btn__n").textContent = n > 99 ? "99+" : String(n);
    button.setAttribute("aria-label", "Your books to reserve: " + n);
  }

  /* ------------------------------ the slip ----------------------------- */
  var dlg = null, slip = null, opener = null;
  var state = "edit";          // edit | sending | failed | done
  var failure = "";
  var done = null;             // {ref, email, rows, total} once reserved
  var form = { name: "", email: "" };
  var bad = {};                // field -> message

  function isOpen() { return !!dlg && !dlg.hidden; }

  function make() {
    dlg = document.createElement("div");
    dlg.className = "cart";
    dlg.hidden = true;
    dlg.setAttribute("role", "dialog");
    dlg.setAttribute("aria-modal", "true");
    dlg.setAttribute("aria-labelledby", "cart-title");
    dlg.innerHTML = '<div class="cart__scrim" data-cart-close></div><div class="cart__slip"></div>';
    slip = dlg.querySelector(".cart__slip");
    document.body.appendChild(dlg);

    dlg.addEventListener("click", function (e) {
      var t = e.target.closest("[data-cart-close],[data-step],[data-remove]");
      if (!t) return;
      if (t.hasAttribute("data-cart-close")) return close();
      var i = +t.getAttribute(t.hasAttribute("data-step") ? "data-step-at" : "data-remove");
      if (!lines[i]) return;
      if (t.hasAttribute("data-remove")) lines.splice(i, 1);
      else lines[i].qty = Math.max(1, Math.min(MAX_QTY, lines[i].qty + +t.getAttribute("data-step")));
      // Keep the focus on the stepper (or the list) through the redraw.
      var focusKey = t.hasAttribute("data-step") ? '[data-step="' + t.getAttribute("data-step") + '"][data-step-at="' + i + '"]' : null;
      write();
      var back = focusKey && slip.querySelector(focusKey);
      if (back && !back.disabled) back.focus();
      else if (!focusKey) (slip.querySelector("[data-remove]") || slip.querySelector(".cart__title")).focus();
    });
    dlg.addEventListener("input", function (e) {
      var f = e.target.name;
      if (f === "name" || f === "email") {
        form[f] = e.target.value;
        if (bad[f]) { delete bad[f]; e.target.removeAttribute("aria-invalid"); }
      }
    });
    dlg.addEventListener("submit", function (e) { e.preventDefault(); submit(); });
    document.addEventListener("keydown", function (e) {
      if (!isOpen()) return;
      if (e.key === "Escape") { e.preventDefault(); close(); return; }
      if (e.key === "Tab") {
        var stops = Array.prototype.filter.call(
          slip.querySelectorAll("button, a[href], input:not([tabindex='-1'])"),
          function (n) { return !n.disabled && n.offsetParent !== null; });
        if (!stops.length) return;
        var first = stops[0], last = stops[stops.length - 1];
        if (e.shiftKey && (document.activeElement === first || !slip.contains(document.activeElement))) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }

  function facts() {
    var rows = [["Collect", store.pickup], ["Held for", store.hold], ["Pay with", store.payWith]]
      .filter(function (r) { return String(r[1] || "").trim(); });
    if (!rows.length) return "";
    return '<dl class="cart__facts">' + rows.map(function (r) {
      return "<dt>" + r[0] + "</dt><dd>" + esc(r[1]) + "</dd>";
    }).join("") + "</dl>";
  }

  function lineHTML(r, k, fixed) {
    var pic = picture(r), l = r.line;
    var href = "book.html?id=" + encodeURIComponent(r.book.id) + (r.many ? "&print=" + (l.print + 1) : "");
    var sub = [r.print.edition, money(r.each) + (fixed ? "" : " each")].filter(Boolean).join(" · ");
    return '<li class="cart-line">' +
      '<span class="cart-line__pic">' + (pic.src ? '<img' + (pic.tight ? ' class="is-tight"' : "") + ' src="' + esc(pic.src) + '" alt="" width="44" height="58">' : "") + "</span>" +
      '<div class="cart-line__info"><a class="cart-line__title" href="' + esc(href) + '">' + esc(r.book.title) + "</a>" +
        '<span class="cart-line__sub">' + esc(sub) + "</span></div>" +
      (fixed
        ? '<span class="cart-line__qty cart-line__qty--fixed">× ' + l.qty + "</span>"
        : '<button class="cart-line__x" type="button" data-remove="' + k + '" aria-label="Remove ' + esc(r.book.title) + '">' + ICONS.close + "</button>" +
          '<div class="cart-line__qty qty" role="group" aria-label="Copies of ' + esc(r.book.title) + '">' +
            '<button type="button" data-step="-1" data-step-at="' + k + '" aria-label="One fewer"' + (l.qty <= 1 ? " disabled" : "") + ">−</button>" +
            '<output aria-live="polite">' + l.qty + "</output>" +
            '<button type="button" data-step="1" data-step-at="' + k + '" aria-label="One more"' + (l.qty >= MAX_QTY ? " disabled" : "") + ">+</button></div>") +
      '<span class="cart-line__sum">' + money(r.each * l.qty) + "</span>" +
      "</li>";
  }

  function head(kicker, meta) {
    return '<button class="round cart__close" type="button" data-cart-close aria-label="Close">' + ICONS.close + "</button>" +
      '<div class="cart__head"><p class="cart__kicker">' + kicker + "</p>" +
      '<h2 class="cart__title" id="cart-title" tabindex="-1">Your books</h2>' +
      (meta ? '<p class="cart__meta">' + meta + "</p>" : "") + "</div>";
  }

  function field(name, label, hint, attrs) {
    var err = bad[name];
    return '<label class="cart-field"><span class="cart-field__label">' + label + (hint ? " <em>· " + hint + "</em>" : "") + "</span>" +
      "<input name=\"" + name + '" value="' + esc(form[name]) + '" ' + attrs +
      (err ? ' aria-invalid="true" aria-describedby="cart-err-' + name + '"' : "") + ">" +
      (err ? '<small class="cart-field__err" id="cart-err-' + name + '">' + esc(err) + "</small>" : "") + "</label>";
  }

  function draw() {
    if (!slip) return;
    if (state === "done") return drawDone();
    if (!store) {
      slip.innerHTML = head("Reserve") + '<div class="cart__body"><p class="cart__empty">' +
        (loading ? "Loading…" : "The bookstore could not be loaded. Please try again later.") + "</p></div>";
      return;
    }
    var rows = resolve();
    if (!rows.length) {
      slip.innerHTML = head("Reserve") + '<div class="cart__body cart__body--empty"><p class="cart__empty">Nothing to reserve yet.</p>' +
        '<a class="btn btn--gold" href="bookstore.html">Visit Bookstore ' + ICONS.arrow + "</a></div>";
      return;
    }
    var n = rows.reduce(function (s, r) { return s + r.line.qty; }, 0);
    var total = rows.reduce(function (s, r) { return s + r.each * r.line.qty; }, 0);
    var sending = state === "sending";
    var open = !!store.reserveTo;
    slip.innerHTML = head("Reserve", n + (n === 1 ? " book" : " books") + " · " + money(total)) +
      '<ul class="cart__lines">' + rows.map(function (r) { return lineHTML(r, lines.indexOf(r.line), false); }).join("") + "</ul>" +
      '<p class="cart__sum"><span>To pay at collection</span><b>' + money(total) + "</b></p>" +
      '<div class="cart__perf" aria-hidden="true"></div>' +
      '<form class="cart__body cart__form' + (sending ? " is-sending" : "") + '" novalidate>' +
        field("name", "Your name", "", 'autocomplete="name" maxlength="100" placeholder="As we should greet you"') +
        field("email", "Email", "for the receipt", 'type="email" autocomplete="email" inputmode="email" maxlength="200" placeholder="name@example.com"') +
        // A field people never see: a form-filling robot fills it and is quietly ignored.
        '<input class="cart__trap" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">' +
        facts() +
        (state === "failed" ? '<p class="cart__fail" role="alert">' + esc(failure) + "</p>" : "") +
        (open
          ? '<button class="btn btn--gold cart__go" type="submit"' + (sending ? ' aria-busy="true" disabled' : "") + ">" +
              (sending ? '<span class="cart__spin" aria-hidden="true"></span> Reserving…' : "Reserve " + ICONS.arrow) + "</button>" +
            '<p class="cart__note">Nothing is paid now. We set the books aside and email you a receipt; pay at the masjid when you collect them.</p>'
          : '<p class="cart__fail">Reservations are closed for the moment.</p>') +
      "</form>";
  }

  function drawDone() {
    slip.innerHTML = head("Reserved") +
      '<ul class="cart__lines">' + done.rows.map(function (r) { return lineHTML(r, 0, true); }).join("") + "</ul>" +
      '<p class="cart__sum"><span>To pay at collection</span><b>' + money(done.total) + "</b></p>" +
      '<div class="cart__perf" aria-hidden="true"></div>' +
      '<div class="cart__body cart__done" role="status">' +
        '<span class="cart__seal">' + ICONS.check + "</span>" +
        '<p class="cart__ref">' + esc(done.ref) + "<small>Your reference</small></p>" +
        '<p class="cart__said">A receipt is on its way to ' + esc(done.email) + ". Show it, or give the reference, when you collect.</p>" +
        facts() +
        '<button class="cart__link" type="button" data-cart-close>Close</button>' +
      "</div>";
  }

  function check() {
    bad = {};
    var name = form.name.trim(), email = form.email.trim();
    if (!name) bad.name = "Please give your name.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) bad.email = "Enter an email address, like name@example.com.";
    return !bad.name && !bad.email;
  }

  function submit() {
    if (state === "sending" || !store || !store.reserveTo) return;
    if (!check()) {
      state = "edit";
      draw();
      var first = slip.querySelector('[aria-invalid="true"]');
      if (first) first.focus();
      return;
    }
    var rows = resolve();
    if (!rows.length) return draw();
    var trap = slip.querySelector('[name="website"]');
    var body = {
      name: form.name.trim(),
      email: form.email.trim(),
      website: trap ? trap.value : "",
      items: rows.map(function (r) {
        return { id: r.book.id, print: r.line.print, qty: r.line.qty,
                 title: r.book.title, edition: r.print.edition || "", price: r.print.price };
      })
    };
    state = "sending";
    draw();
    var ctl = global.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, TIMEOUT);
    // text/plain keeps it a simple request: Apps Script answers no preflight.
    fetch(store.reserveTo, {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify(body),
      redirect: "follow",
      signal: ctl ? ctl.signal : undefined
    }).then(function (r) {
      return r.json();
    }).then(function (j) {
      clearTimeout(timer);
      if (!j || !j.ok) throw new Error((j && j.message) || "");
      done = {
        ref: j.ref || "", email: body.email,
        rows: rows.map(function (r) { return { line: { id: r.line.id, print: r.line.print, qty: r.line.qty }, book: r.book, index: r.index, print: r.print, many: r.many, each: r.each }; }),
        total: rows.reduce(function (s, r) { return s + r.each * r.line.qty; }, 0)
      };
      state = "done";
      lines = [];
      write();
      drawDone();
      var t = isOpen() && slip.querySelector(".cart__title");
      if (t) t.focus();
    }).catch(function (err) {
      clearTimeout(timer);
      state = "failed";
      failure = (err && err.message && err.name !== "AbortError" && !/fetch|network|JSON/i.test(err.message))
        ? err.message
        : "The reservation couldn’t be confirmed. If no receipt reaches your email in the next few minutes, please try again.";
      draw();
      var go = isOpen() && slip.querySelector(".cart__go");
      if (go) go.focus();
    });
  }

  function open() {
    if (!dlg) make();
    // A reservation that finished while the slip was closed still shows its reference.
    if (state === "failed") state = "edit";
    opener = document.activeElement;
    dlg.hidden = false;
    root.classList.add("cart-lock");
    draw();
    var focus = function () {
      var t = slip.querySelector(".cart__title");
      if (t) t.focus();
    };
    focus();
    if (!store) load().then(function () { draw(); focus(); }, function () { draw(); });
  }

  function close() {
    if (!isOpen()) return;
    dlg.hidden = true;
    root.classList.remove("cart-lock");
    if (state === "done") { state = "edit"; done = null; }
    if (opener && document.contains(opener) && !opener.hidden && opener.focus) opener.focus();
  }

  /* ------------------------------- the API ----------------------------- */
  global.cart = {
    add: function (id, print) {
      print = print | 0;
      var i = at(id, print);
      if (i >= 0) lines[i].qty = Math.min(MAX_QTY, lines[i].qty + 1);
      else if (lines.length < MAX_LINES) lines.push({ id: id, print: print, qty: 1 });
      else return false;
      write();
      return true;
    },
    has: function (id, print) { return at(id, print | 0) >= 0; },
    count: count,
    open: open,
    cents: cents
  };

  makeButton();
  syncButton();
})(window);

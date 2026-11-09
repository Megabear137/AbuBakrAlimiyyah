/* The filter mockups' shared machinery. The page runs the site's own
   bookstore.js, which draws the grid (and its own pills, hidden here); this
   reads the same bookstore.json, draws an option's controls through
   MockFilter(render), and hides the tiles they leave out (.mock-out),
   matching each tile to its book by data-i. A redraw of the grid by
   bookstore.js (when covers.json arrives) is caught and filtered again.
   The counts beside every choice are of the books the *other* filter lets
   through, so a choice with none is greyed and can't be picked. */
(function () {
  var YEARS = ["First Year", "Second Year", "Third Year", "Fourth Year", "Fifth Year", "Sixth Year", "Seventh Year"];
  var ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"];
  // Option 6 only: a proposal for grouping the subjects. Anything not named
  // here falls into the last group.
  var FAMILIES = [
    ["Language", ["Arabic", "Nahwa", "Sarf", "Balagha", "Urdu"]],
    ["Qur'an", ["Tajwid", "Tafseer", "Usul Tafsir"]],
    ["Hadith", ["Hadith", "Usul Hadith"]],
    ["Fiqh", ["Fiqh", "Usul Fiqh", "Mirath"]],
    ["Other", []]
  ];
  var CARET = '<svg class="mm__caret" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>';

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  function familyOf(subject) {
    for (var i = 0; i < FAMILIES.length - 1; i++) if (FAMILIES[i][1].indexOf(subject) >= 0) return FAMILIES[i][0];
    return FAMILIES[FAMILIES.length - 1][0];
  }

  // A button that opens a list of choices beneath it. items: [{value, label,
  // count}]; a count of 0 disables the item.
  function menu(o) {
    var wrap = el("div", "mm" + (o.cls ? " " + o.cls : ""));
    var btn = el("button", "mm__btn", o.button + CARET);
    btn.type = "button";
    btn.setAttribute("aria-haspopup", "true");
    btn.setAttribute("aria-expanded", "false");
    var pop = el("div", "mm__pop" + (o.cols ? " mm__pop--cols" : ""));
    pop.hidden = true;
    o.items.forEach(function (it) {
      var b = el("button", "mm__item", '<span>' + esc(it.label) + "</span>" + (it.count != null ? "<i>" + it.count + "</i>" : ""));
      b.type = "button";
      b.setAttribute("aria-pressed", String(it.value === o.value));
      if (it.count === 0 && it.value !== o.value) b.disabled = true;
      b.addEventListener("click", function () { o.onPick(it.value); });
      pop.appendChild(b);
    });
    function set(open) {
      pop.hidden = !open;
      btn.setAttribute("aria-expanded", String(open));
      wrap.classList.toggle("mm--open", open);
      if (open) { var f = pop.querySelector('[aria-pressed="true"]') || pop.querySelector("button:not(:disabled)"); if (f) f.focus(); }
    }
    btn.addEventListener("click", function () {
      var open = pop.hidden;
      document.querySelectorAll(".mm--open").forEach(function (m) { if (m !== wrap) m._close(); });
      set(open);
    });
    wrap.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !pop.hidden) { set(false); btn.focus(); e.stopPropagation(); }
    });
    wrap._close = function () { set(false); };
    wrap.appendChild(btn);
    wrap.appendChild(pop);
    return wrap;
  }
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".mm--open").forEach(function (m) { if (!m.contains(e.target)) m._close(); });
  });

  window.MockFilter = function (render, hooks) {
    hooks = hooks || {};
    var api = { state: { year: "", subject: "", family: "" }, books: [], esc: esc, el: el, menu: menu, FAMILIES: FAMILIES, familyOf: familyOf };
    api.roman = function (y) { var i = YEARS.indexOf(y); return i < 0 ? y : ROMAN[i]; };
    api.match = function (b, s) {
      s = s || api.state;
      return (!s.year || (b.years || []).indexOf(s.year) >= 0) &&
        (!s.subject || b.subject === s.subject) &&
        (!s.family || familyOf(b.subject) === s.family);
    };
    api.count = function (patch) {
      var s = Object.assign({}, api.state, patch);
      return api.books.filter(function (b) { return api.match(b, s); }).length;
    };
    api.shown = function () { return api.count({}); };
    api.set = function (patch) { Object.assign(api.state, patch); apply(); render(api); };
    api.active = function () { return !!(api.state.year || api.state.subject || api.state.family); };

    // The years as a segmented bar of numerals.
    api.seg = function () {
      var bar = el("div", "seg");
      bar.setAttribute("role", "group");
      bar.setAttribute("aria-label", "Year");
      [""].concat(api.years).forEach(function (y) {
        var n = api.count({ year: y });
        var b = el("button", "seg__btn" + (y ? "" : " seg__btn--all"), y ? api.roman(y) : "All");
        b.type = "button";
        b.title = (y || "Every year") + " · " + n + (n === 1 ? " book" : " books");
        b.setAttribute("aria-label", (y || "All years") + ", " + n + " books");
        b.setAttribute("aria-pressed", String(y === api.state.year));
        if (!n && y !== api.state.year) b.disabled = true;
        b.addEventListener("click", function () { api.set({ year: y }); });
        bar.appendChild(b);
      });
      return bar;
    };
    api.yearMenu = function (o) {
      o = o || {};
      return menu({
        cls: o.cls, value: api.state.year,
        button: o.button ? o.button(api.state.year) : (api.state.year || "All years"),
        items: [{ value: "", label: o.all || "All years", count: api.count({ year: "" }) }].concat(api.years.map(function (y) {
          return { value: y, label: y, count: api.count({ year: y }) };
        })),
        onPick: function (v) { api.set({ year: v }); }
      });
    };
    api.subjectMenu = function (o) {
      o = o || {};
      return menu({
        cls: o.cls, cols: o.cols !== false, value: api.state.subject,
        button: o.button ? o.button(api.state.subject) : (api.state.subject || "All subjects"),
        items: [{ value: "", label: o.all || "All subjects", count: api.count({ subject: "" }) }].concat(api.subjects.map(function (s) {
          return { value: s, label: s, count: api.count({ subject: s }) };
        })),
        onPick: function (v) { api.set({ subject: v }); }
      });
    };

    var grid = document.querySelector('[data-slot="bookstore"]');
    var empty = el("p", "media-empty mock-empty", "No books match.");
    empty.hidden = true;
    grid.after(empty);

    function apply() {
      if (!api.books.length) return;
      var n = 0;
      grid.querySelectorAll(".store-card[data-i]").forEach(function (c) {
        var ok = api.match(api.books[+c.getAttribute("data-i")] || {});
        c.classList.toggle("mock-out", !ok);
        if (ok) n++;
      });
      empty.hidden = n > 0;
      var count = grid.querySelector(".store-name__count");
      if (count) count.innerHTML = "<b>" + n + "</b>" + (n === 1 ? "book" : "books") + (api.active() ? " of " + api.books.length : "");
      if (hooks.onGrid) hooks.onGrid(api);
    }

    fetch("content/bookstore.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (d) {
      api.books = d.books || [];
      var ys = {}, ss = {};
      api.books.forEach(function (b) { (b.years || []).forEach(function (y) { ys[y] = 1; }); if (b.subject) ss[b.subject] = 1; });
      api.years = YEARS.filter(function (y) { return ys[y]; }).concat(Object.keys(ys).filter(function (y) { return YEARS.indexOf(y) < 0; }));
      api.subjects = Object.keys(ss).sort();
      render(api);
      apply();
      new MutationObserver(apply).observe(grid, { childList: true });
    });
    return api;
  };
})();

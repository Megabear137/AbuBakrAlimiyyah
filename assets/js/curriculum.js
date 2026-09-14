/* =====================================================================
   curriculum.js - the seven-year accordion and its book selector.
   One year open at a time; opening a year selects its first book.
   ===================================================================== */
(function (global) {
  "use strict";

  var CHEVRON =
    '<svg class="acc__chevron" viewBox="0 0 24 24" aria-hidden="true"><polyline points="5 9 12 16 19 9"/></svg>';

  var uid = 0;

  function renderCurriculum(mount, data) {
    if (!mount || !data || !data.years) return;
    mount.textContent = "";

    data.years.forEach(function (year) {
      mount.appendChild(buildYear(year));
    });
  }

  function buildYear(year) {
    var id = "yr-" + ++uid;

    var item = document.createElement("div");
    item.className = "acc__item";

    var trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "acc__trigger";
    trigger.id = id + "-trigger";
    trigger.setAttribute("aria-expanded", "false");
    trigger.setAttribute("aria-controls", id + "-panel");
    trigger.innerHTML = "<span>" + esc(year.name) + "</span>" + CHEVRON;

    var panel = document.createElement("div");
    panel.className = "acc__panel";
    panel.id = id + "-panel";
    panel.setAttribute("role", "region");
    panel.setAttribute("aria-labelledby", id + "-trigger");
    panel.hidden = true;

    var books = year.books || [];
    if (books.length) {
      panel.appendChild(buildBooks(books, id));
    } else {
      panel.innerHTML = '<p class="book-detail__body">Curriculum for this year is being finalised.</p>';
    }

    trigger.addEventListener("click", function () {
      var isOpen = trigger.getAttribute("aria-expanded") === "true";
      closeAll(item.parentNode);
      if (!isOpen) {
        trigger.setAttribute("aria-expanded", "true");
        panel.hidden = false;
      }
    });

    item.append(trigger, panel);
    return item;
  }

  function closeAll(container) {
    if (!container) return;
    container.querySelectorAll(".acc__trigger").forEach(function (t) {
      t.setAttribute("aria-expanded", "false");
    });
    container.querySelectorAll(".acc__panel").forEach(function (p) {
      p.hidden = true;
    });
  }

  function buildBooks(books, id) {
    var frag = document.createDocumentFragment();

    var list = document.createElement("div");
    list.className = "books";
    list.setAttribute("role", "tablist");
    list.setAttribute("aria-label", "Books");

    var detail = document.createElement("div");
    detail.className = "book-detail";
    detail.id = id + "-detail";
    detail.setAttribute("role", "tabpanel");
    detail.setAttribute("tabindex", "0");

    var tabs = books.map(function (book, i) {
      var tab = document.createElement("button");
      tab.type = "button";
      tab.className = "book";
      tab.id = id + "-book-" + i;
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", detail.id);
      tab.setAttribute("aria-selected", i === 0 ? "true" : "false");
      tab.tabIndex = i === 0 ? 0 : -1;
      tab.innerHTML =
        '<span class="book__title">' + esc(book.title) + "</span>" +
        '<span class="book__divider"></span>' +
        '<span class="book__subject">' + esc(book.subject || "") + "</span>";

      tab.addEventListener("click", function () { select(i); });
      list.appendChild(tab);
      return tab;
    });

    // Roving tabindex: arrow keys move between book cards.
    list.addEventListener("keydown", function (e) {
      var current = tabs.findIndex(function (t) { return t === document.activeElement; });
      if (current < 0) return;
      var nextIndex = null;
      if (e.key === "ArrowRight") nextIndex = (current + 1) % tabs.length;
      if (e.key === "ArrowLeft")  nextIndex = (current - 1 + tabs.length) % tabs.length;
      if (e.key === "Home")       nextIndex = 0;
      if (e.key === "End")        nextIndex = tabs.length - 1;
      if (nextIndex === null) return;
      e.preventDefault();
      select(nextIndex);
      tabs[nextIndex].focus();
    });

    function select(i) {
      tabs.forEach(function (t, j) {
        t.setAttribute("aria-selected", j === i ? "true" : "false");
        t.tabIndex = j === i ? 0 : -1;
      });
      detail.setAttribute("aria-labelledby", tabs[i].id);
      fillDetail(detail, books[i]);
    }

    fillDetail(detail, books[0]);
    detail.setAttribute("aria-labelledby", tabs[0].id);

    frag.append(list, detail);
    return frag;
  }

  function fillDetail(el, book) {
    var meta = [book.subject, book.author].filter(Boolean).join(" - ");
    el.innerHTML =
      '<div class="book-detail__head">' +
        '<h4 class="book-detail__title">' + esc(book.title) + "</h4>" +
        (book.titleUrdu
          ? '<p class="book-detail__urdu" lang="ur" dir="rtl">' + esc(book.titleUrdu) + "</p>"
          : "") +
      "</div>" +
      (meta ? '<p class="book-detail__meta">' + esc(meta) + "</p>" : "") +
      '<hr class="book-detail__rule">' +
      '<p class="book-detail__body">' + esc(book.description || "") + "</p>";
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  global.renderCurriculum = renderCurriculum;
})(window);

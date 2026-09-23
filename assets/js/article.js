/* =====================================================================
   article.js - fills article.html: one article from content/media.json,
   found by the ?id= in the address, and beneath it the other articles of
   the same list. The footer's contact lines come from program.json.
   ===================================================================== */
(function () {
  "use strict";

  var slot = function (name) { return document.querySelector('[data-slot="' + name + '"]'); };

  var ICONS = {
    quote: '<svg viewBox="0 0 40 32" fill="currentColor" aria-hidden="true"><path d="M0 32V19C0 8 6 1.5 16 0l1.6 4C11.6 5.8 9 9.4 8.8 14H16v18H0zm22 0V19C22 8 28 1.5 38 0l1.6 4C33.6 5.8 31 9.4 30.8 14H38v18H22z"/></svg>',
    home:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 11l8-7 8 7v9H4z"/></svg>',
    mail:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3.5" y="5.5" width="17" height="13" rx="1.5"/><path d="M4 7l8 6 8-6"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg>'
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
  function pad(n) { return (n < 10 ? "0" : "") + n; }

  function loadJSON(path) {
    return fetch(path, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(path + " -> HTTP " + r.status);
      return r.json();
    });
  }

  // As main.js links them: the article's page, unless its href sends it elsewhere.
  function articleHref(a) {
    return a.href || (a.id ? "article.html?id=" + encodeURIComponent(a.id) : "");
  }

  /* ----------------------------- the article ---------------------------- */
  // Finds the article in either list; returns it with the list it came from.
  function find(articles, id) {
    var lists = ["brothers", "sisters"];
    for (var i = 0; i < lists.length; i++) {
      var list = articles[lists[i]] || [];
      for (var j = 0; j < list.length; j++) {
        if (list[j].id === id) return { article: list[j], list: list };
      }
    }
    return null;
  }

  // The body is a list: a string is a paragraph, {heading} a section
  // heading, {quote, source} a quotation set apart.
  function renderBody(mount, body) {
    mount.textContent = "";
    (body || []).forEach(function (block) {
      if (typeof block === "string") {
        mount.appendChild(el("p", "", esc(block)));
      } else if (block && block.heading) {
        mount.appendChild(el("h2", "", esc(block.heading)));
      } else if (block && block.quote) {
        mount.appendChild(el("blockquote", "",
          ICONS.quote + "<p>" + esc(block.quote) + "</p>" +
          (block.source ? "<cite>" + esc(block.source) + "</cite>" : "")));
      }
    });
  }

  function renderArticle(a) {
    document.title = a.title + " — Jamiyah Islamiyyah Abu Bakr";
    slot("article-title").textContent = a.title;
    if (a.subject) slot("article-subject").innerHTML = '<span class="chip">' + esc(a.subject) + "</span>";
    // Author and read time, a dot between them.
    var meta = [a.author, a.readMinutes ? a.readMinutes + " min read" : ""]
      .filter(Boolean)
      .map(function (s) { return "<span>" + esc(s) + "</span>"; });
    if (meta.length) {
      slot("article-meta").innerHTML = '<p class="meta">' +
        meta.join('<span class="meta__dot" aria-hidden="true"></span>') + "</p>";
    }
    if (a.excerpt) slot("article-lede").textContent = a.excerpt;
    renderBody(slot("article-body"), a.body);
  }

  // The rest of the article's list, as the home page's cards, each opening its page.
  function renderMore(list, current, heading) {
    var mount = slot("article-cards");
    var others = list.filter(function (a) { return a !== current && articleHref(a); });
    if (!others.length) return;
    if (heading) slot("articles-heading").textContent = heading;
    others.slice(0, 4).forEach(function (a, i) {
      var card = el("a", "slider__card board" + (i % 2 ? " board--rust" : ""),
        "<b>" + pad(list.indexOf(a) + 1) + "</b>" +
        (a.subject ? "<em>" + esc(a.subject) + "</em>" : "") +
        "<span>" + esc(a.title) + "</span>");
      card.href = articleHref(a);
      mount.appendChild(card);
    });
    slot("article-more").hidden = false;
  }

  function notFound() {
    slot("article-title").textContent = "Article not found";
    slot("article-lede").textContent = "This article may have been moved or taken down.";
  }

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

  var id = new URLSearchParams(location.search).get("id");

  Promise.all([
    loadJSON("content/media.json").then(function (data) {
      var articles = data.articles || {};
      var hit = id && find(articles, id);
      if (!hit) return notFound();
      renderArticle(hit.article);
      renderMore(hit.list, hit.article, articles.heading);
    }),
    loadJSON("content/program.json").then(function (data) { renderFooter(data.footer); })
  ]).catch(function (err) {
    console.error("Content failed to load.", err);
    slot("article-title").textContent = "Articles";
    slot("article-lede").textContent =
      "The article could not be loaded. If you opened this file directly, serve the folder over " +
      "a local web server instead (see CLAUDE.md).";
  });
})();

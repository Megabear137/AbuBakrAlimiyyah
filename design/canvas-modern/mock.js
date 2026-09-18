/* =====================================================================
   mock.js - shared by the four "modernise" mockups in this folder.

   Each mockup sets <base href="../../"> so the live stylesheet, the live
   curriculum.js, content/*.json and assets/img resolve from the site root:
   the bookshelf on every mockup IS the real shelf. The mockups restyle the
   site's existing content only. This file:

   - renders the shelf into [data-shelf] from content/curriculum.json;
   - keeps in-page #anchors on this page (the <base> would send them to
     the site root);
   - pages a scrolling row from [data-scroll-prev]/[data-scroll-next];
   - flips the Brothers/Sisters switch ([data-seg]), naming the chosen
     library in every [data-aud].
   ===================================================================== */
(function () {
  "use strict";

  /* In-page anchors: scroll, don't navigate to the root page. */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute("href").slice(1);
    var t = id ? document.getElementById(id) : document.body;
    if (!t) return;
    e.preventDefault();
    t.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  /* ---- The shelf ---- */
  var shelf = document.querySelector("[data-shelf]");
  if (shelf && window.renderCurriculum) {
    fetch("content/curriculum.json", { cache: "no-cache" })
      .then(function (r) { return r.json(); })
      .then(function (d) { window.renderCurriculum(shelf, d); });
  }

  /* ---- Sections fade in as they scroll into view ----
     Every section of the page (and the footer, and B's gold rules) starts
     hidden and fades up the first time a sliver of it is on screen. The class
     is added here, not in the markup, so without script everything shows;
     reduced motion is handled in mock.css. */
  var parts = document.querySelectorAll("main > section, main > .wrap > section, main > .b-rule, body > footer");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add("m-in");
        io.unobserve(en.target);
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -6% 0px" });
    parts.forEach(function (el) {
      el.classList.add("m-reveal");
      io.observe(el);
    });
  }

  /* ---- Scrolling rows ---- */
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-scroll-prev],[data-scroll-next]");
    if (!b) return;
    var row = document.getElementById(b.getAttribute("data-scroll-prev") || b.getAttribute("data-scroll-next"));
    if (!row) return;
    var dir = b.hasAttribute("data-scroll-prev") ? -1 : 1;
    row.scrollBy({ left: dir * row.clientWidth * 0.9, behavior: "smooth" });
  });

  /* ---- Brothers/Sisters: every switch on the page is one choice, as on the site ---- */
  var segs = document.querySelectorAll("[data-seg]");
  segs.forEach(function (group) {
    group.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      var label = b.getAttribute("data-label");
      segs.forEach(function (g) {
        g.querySelectorAll("button").forEach(function (x) {
          x.setAttribute("aria-pressed", String(x.getAttribute("data-label") === label));
        });
      });
      document.querySelectorAll("[data-aud]").forEach(function (x) { x.textContent = label; });
    });
  });
})();

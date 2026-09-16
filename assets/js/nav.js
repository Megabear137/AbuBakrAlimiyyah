/* =====================================================================
   nav.js - mobile drawer and the active-section highlight in the header.
   ===================================================================== */
(function () {
  "use strict";

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");
  if (!toggle || !nav) return;

  function setOpen(open) {
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    nav.dataset.open = String(open);
  }

  toggle.addEventListener("click", function () {
    setOpen(toggle.getAttribute("aria-expanded") !== "true");
  });

  // Tapping a link, or pressing Escape, closes the drawer.
  nav.addEventListener("click", function (e) {
    if (e.target.closest("a")) setOpen(false);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
      setOpen(false);
      toggle.focus();
    }
  });

  // Reset state when the drawer breakpoint is left behind.
  var wide = window.matchMedia("(min-width: 981px)");
  (wide.addEventListener ? wide.addEventListener.bind(wide, "change") : wide.addListener.bind(wide))(
    function () { setOpen(false); }
  );

  /* ---------------------- active-link scrollspy ---------------------- */
  var links = Array.prototype.slice.call(nav.querySelectorAll('a[href^="#"]'));
  var targets = links
    .map(function (a) {
      var id = a.getAttribute("href").slice(1);
      var el = id === "top" ? document.body : document.getElementById(id);
      return el ? { link: a, el: el } : null;
    })
    .filter(Boolean);

  if (!("IntersectionObserver" in window) || !targets.length) return;

  var visible = new Set();

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) visible.add(entry.target);
        else visible.delete(entry.target);
      });

      // Highlight the topmost section currently on screen.
      var best = null;
      targets.forEach(function (t) {
        if (!visible.has(t.el)) return;
        if (!best || t.el.getBoundingClientRect().top < best.el.getBoundingClientRect().top) best = t;
      });

      links.forEach(function (a) { a.removeAttribute("aria-current"); });
      if (best) best.link.setAttribute("aria-current", "true");
    },
    { rootMargin: "-30% 0px -55% 0px", threshold: 0 }
  );

  targets.forEach(function (t) {
    if (t.el !== document.body) observer.observe(t.el);
  });
})();

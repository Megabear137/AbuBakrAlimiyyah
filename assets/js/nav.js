/* =====================================================================
   nav.js - the header's two buttons: the full-screen menu, and the
   light/dark toggle. The inline script in index.html's <head> sets the
   theme before first paint from the same storage key.
   ===================================================================== */
(function () {
  "use strict";

  var root = document.documentElement;

  /* ------------------------------ theme ------------------------------ */
  var THEME_KEY = "alimiyyah.theme";
  var toggle = document.querySelector("[data-theme-toggle]");

  function label() {
    if (!toggle) return;
    var dark = root.getAttribute("data-theme") === "dark";
    toggle.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
  }

  if (toggle) {
    label();
    toggle.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* storage blocked: not remembered */ }
      label();
    });
  }

  /* ------------------------------ menu ------------------------------- */
  var menu = document.getElementById("site-menu");
  var opener = document.querySelector("[data-menu-open]");
  var closer = menu && menu.querySelector("[data-menu-close]");
  if (!menu || !opener) return;

  function isOpen() { return menu.classList.contains("menu--open"); }

  function setOpen(open, restoreFocus) {
    menu.classList.toggle("menu--open", open);
    opener.setAttribute("aria-expanded", String(open));
    root.classList.toggle("menu-lock", open);          // no page scroll behind the menu
    if (open && closer) closer.focus();
    else if (!open && restoreFocus) opener.focus();
  }

  opener.addEventListener("click", function () { setOpen(true); });
  if (closer) closer.addEventListener("click", function () { setOpen(false, true); });

  // Following a link closes the menu and lets the page scroll to it.
  menu.addEventListener("click", function (e) {
    if (e.target.closest("a")) setOpen(false);
  });

  document.addEventListener("keydown", function (e) {
    if (!isOpen()) return;
    if (e.key === "Escape") {
      setOpen(false, true);
      return;
    }
    // Keep Tab inside the open menu.
    if (e.key === "Tab") {
      var stops = menu.querySelectorAll("button, a[href]");
      var first = stops[0], last = stops[stops.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
})();

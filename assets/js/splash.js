/* =========================================================================
   splash.js - the home page's loading splash (design/canvas-splash/,
   option 6). The page waits behind the ground until it is ready: the
   content (main.js fires `content:ready` once every JSON file is drawn),
   the fonts that content uses, and the banner photo. Meanwhile the logo
   fills from its foot as they arrive; when full, one glint crosses it and
   the splash fades as the banner's title rises.

   index.html's <head> script decides before first paint: `splash-on` shows
   the splash, `splash-hold` holds the banner's entrance, `splash-quick` (a
   later home page in the same visit) shows the ground alone, with no logo,
   until ready. It also lifts the splash after 10s should this file fail.
   Loads before main.js, so the listener is in place first.
   ========================================================================= */
(function () {
  "use strict";

  var root = document.documentElement;
  var splash = document.querySelector(".splash");
  if (!splash || !root.classList.contains("splash-on")) return;

  var quick = root.classList.contains("splash-quick");
  var still = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var plain = quick || still;           // no fill, glint or settle: just wait, then go
  var started = Date.now();
  var MIN = plain ? 0 : 900;            // long enough for the fill to read
  var MAX = quick ? 4000 : 8000;        // a slow photo never holds the page longer
  var FILL = 900, GLINT = 1050, FADE = plain ? 450 : 950;   // as in the CSS

  function fill(p) { splash.style.setProperty("--splash-p", String(p)); }

  // The bismillah is written in once Amiri is in (preloaded), so it never
  // shows in a stand-in face; a font that won't come starts it after 1.2s.
  // Two frames on, so the unwritten state has been painted and it moves.
  function write() {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { splash.classList.add("is-writing"); });
    });
  }
  if (!quick) {
    if (document.fonts && document.fonts.load) {
      document.fonts.load('400 50px "Amiri"', "﷽").then(write, write);
      setTimeout(write, 1200);
    } else {
      write();
    }
  }

  // The parts the page waits for, each a share of the fill.
  var content = new Promise(function (res) { document.addEventListener("content:ready", res, { once: true }); });
  var fonts = content.then(function () {
    // The fonts the new text asks for start loading at its first layout.
    return new Promise(function (res) { requestAnimationFrame(res); });
  }).then(function () { return document.fonts ? document.fonts.ready : null; });
  var parts = [content, fonts, photo()];

  // The banner photo: the URL its CSS gives, loaded (from cache, as a rule).
  function photo() {
    var box = document.querySelector(".hero__img");
    var m = box && /url\(["']?(.*?)["']?\)/.exec(getComputedStyle(box).backgroundImage);
    if (!m) return Promise.resolve();
    return new Promise(function (res) {
      var img = new Image();
      img.onload = img.onerror = res;
      img.src = m[1];
    });
  }

  var arrived = 0, finished = false;
  requestAnimationFrame(function () { fill(0.08); });   // something moves at once
  parts.forEach(function (p) {
    p.then(step, step);
  });
  setTimeout(ready, MAX);

  function step() {
    arrived++;
    if (arrived < parts.length) fill(0.08 + 0.72 * arrived / parts.length);
    else ready();
  }

  function ready() {
    if (finished) return;
    finished = true;
    setTimeout(function () {
      fill(1);
      if (plain) return leave();
      setTimeout(function () {
        splash.classList.add("is-full");
        setTimeout(leave, GLINT);
      }, FILL);
    }, Math.max(0, MIN - (Date.now() - started)));
  }

  // The banner rises as the splash fades; then the splash is gone.
  function leave() {
    root.classList.remove("splash-hold");
    splash.classList.add("is-done");
    setTimeout(function () {
      root.classList.remove("splash-on", "splash-quick");
    }, FADE);
  }
})();

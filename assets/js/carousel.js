/* =====================================================================
   carousel.js - one sliding carousel used by both Teachers and Alumni.
   Pages by whole screenfuls; arrows hide at the ends; dots track pages.
   ===================================================================== */
(function (global) {
  "use strict";

  var CHEVRON =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="9 5 16 12 9 19"/></svg>';

  /**
   * @param {Object} opts
   * @param {HTMLElement} opts.mount     element to render into
   * @param {Array}       opts.items     data for the slides
   * @param {Function}    opts.render    (item, index) -> HTMLElement
   * @param {Function}    opts.perView   () -> how many slides fit at this width
   * @param {string}      opts.label     accessible name for the carousel
   * @param {HTMLElement} [opts.controls] where the arrows go - a section header,
   *                                      say; without it they flank the slides
   */
  function createCarousel(opts) {
    var items = opts.items || [];
    if (!opts.mount || !items.length) return null;

    var root = document.createElement("div");
    root.className = "carousel";
    root.setAttribute("role", "group");
    root.setAttribute("aria-roledescription", "carousel");
    root.setAttribute("aria-label", opts.label);

    var prev = arrowButton("prev", "Previous " + opts.label);
    var next = arrowButton("next", "Next " + opts.label);

    var viewport = document.createElement("div");
    viewport.className = "carousel__viewport";

    var track = document.createElement("div");
    track.className = "carousel__track";

    items.forEach(function (item, i) {
      var slide = document.createElement("div");
      slide.className = "carousel__slide";
      slide.setAttribute("role", "group");
      slide.setAttribute("aria-roledescription", "slide");
      slide.setAttribute("aria-label", i + 1 + " of " + items.length);
      slide.appendChild(opts.render(item, i));
      track.appendChild(slide);
    });

    viewport.appendChild(track);

    var dots = document.createElement("div");
    dots.className = "carousel__dots";

    if (opts.controls) {
      opts.controls.textContent = "";
      opts.controls.append(prev, next);
      root.append(viewport, dots);
    } else {
      root.append(prev, viewport, next, dots);
    }
    opts.mount.appendChild(root);

    var page = 0;
    var pageCount = 1;
    var baseShift = 0; // px the track is translated by at rest

    function slideWidth() {
      var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      var first = track.firstElementChild;
      return (first ? first.getBoundingClientRect().width : 0) + gap;
    }

    function layout() {
      var perView = Math.max(1, Math.min(opts.perView(), items.length));
      // Each slide is sized so `perView` of them plus the gaps fill the viewport.
      var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      var avail = viewport.getBoundingClientRect().width - gap * (perView - 1);
      var w = avail / perView;

      Array.prototype.forEach.call(track.children, function (slide) {
        slide.style.width = w + "px";
      });

      pageCount = Math.max(1, Math.ceil(items.length / perView));
      if (page > pageCount - 1) page = pageCount - 1;

      buildDots(perView);
      apply(perView);
    }

    function buildDots(perView) {
      if (dots.childElementCount === pageCount) return;
      dots.textContent = "";
      for (var i = 0; i < pageCount; i++) {
        var dot = document.createElement("button");
        dot.type = "button";
        dot.className = "carousel__dot";
        dot.setAttribute("aria-label", "Go to slide group " + (i + 1));
        dot.dataset.page = String(i);
        dot.addEventListener("click", function (e) {
          go(Number(e.currentTarget.dataset.page));
        });
        dots.appendChild(dot);
      }
      dots.hidden = pageCount < 2;
    }

    // Never scroll past the last slide.
    function maxShift() {
      return Math.max(0, slideWidth() * items.length - parseFloat(getComputedStyle(track).columnGap || 0) - viewport.getBoundingClientRect().width);
    }

    function apply(perView) {
      var step = slideWidth() * perView;
      var shift = Math.min(page * step, maxShift());
      baseShift = shift;
      track.style.transform = "translateX(" + -shift + "px)";

      prev.disabled = page === 0;
      next.disabled = page >= pageCount - 1;
      // Nothing to page through - nor to drag - when every slide already fits.
      prev.hidden = next.hidden = pageCount < 2;
      root.classList.toggle("carousel--draggable", pageCount > 1);

      Array.prototype.forEach.call(dots.children, function (dot, i) {
        if (i === page) dot.setAttribute("aria-current", "true");
        else dot.removeAttribute("aria-current");
      });

      // Slides scrolled out of view must not be reachable by keyboard.
      Array.prototype.forEach.call(track.children, function (slide, i) {
        var visible = i >= page * perView && i < (page + 1) * perView;
        slide.setAttribute("aria-hidden", visible ? "false" : "true");
        slide.querySelectorAll("a, button").forEach(function (el) {
          if (visible) el.removeAttribute("tabindex");
          else el.setAttribute("tabindex", "-1");
        });
      });
    }

    function go(n) {
      page = Math.max(0, Math.min(n, pageCount - 1));
      layout();
    }

    prev.addEventListener("click", function () { go(page - 1); });
    next.addEventListener("click", function () { go(page + 1); });

    root.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { go(page + 1); e.preventDefault(); }
      if (e.key === "ArrowLeft")  { go(page - 1); e.preventDefault(); }
    });

    /* -------------------------- drag to scroll ------------------------
       One pointer path for mouse, pen and finger: the track follows the
       drag live, then snaps to the nearest page. `touch-action: pan-y` on
       the viewport leaves vertical page scrolling to the browser. */
    var drag = null;
    var swallowClick = false;

    viewport.addEventListener("pointerdown", function (e) {
      swallowClick = false;
      if (pageCount < 2) return;
      if (e.pointerType === "mouse" && e.button !== 0) return;
      drag = { id: e.pointerId, x: e.clientX, y: e.clientY, dx: 0, axis: null };
    });

    viewport.addEventListener("pointermove", function (e) {
      if (!drag || e.pointerId !== drag.id) return;
      var dx = e.clientX - drag.x;
      var dy = e.clientY - drag.y;
      if (!drag.axis) {
        if (Math.abs(dx) < 6 && Math.abs(dy) < 6) return;
        // A first move that is mostly vertical is the page scrolling, not a swipe.
        if (Math.abs(dy) >= Math.abs(dx)) { drag = null; return; }
        drag.axis = "x";
        try { viewport.setPointerCapture(drag.id); } catch (err) { /* pointer already gone */ }
        track.classList.add("carousel__track--dragging");
      }
      if (e.cancelable) e.preventDefault();
      drag.dx = dx;
      var limit = maxShift();
      var shift = baseShift - dx;
      // Rubber band past either end, so the ends feel closed.
      if (shift < 0) shift *= 0.35;
      else if (shift > limit) shift = limit + (shift - limit) * 0.35;
      track.style.transform = "translateX(" + -shift + "px)";
    });

    function endDrag(e) {
      if (!drag || e.pointerId !== drag.id) return;
      var dx = drag.dx;
      var dragged = drag.axis === "x";
      drag = null;
      track.classList.remove("carousel__track--dragging");
      if (!dragged) return;
      swallowClick = Math.abs(dx) > 6; // a drag must not open the card under it
      if (Math.abs(dx) > Math.max(45, Math.min(slideWidth() * 0.4, 160))) {
        go(dx < 0 ? page + 1 : page - 1);
      } else {
        apply(Math.max(1, Math.min(opts.perView(), items.length)));
      }
    }
    viewport.addEventListener("pointerup", endDrag);
    viewport.addEventListener("pointercancel", endDrag);

    viewport.addEventListener("click", function (e) {
      if (!swallowClick) return;
      swallowClick = false;
      e.preventDefault();
      e.stopPropagation();
    }, true);

    // Horizontal wheel or trackpad (shift + wheel on a plain mouse) pages too.
    var wheelUntil = 0;
    viewport.addEventListener("wheel", function (e) {
      if (pageCount < 2 || Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return;
      e.preventDefault();
      var now = Date.now();
      if (now < wheelUntil || Math.abs(e.deltaX) < 8) return;
      wheelUntil = now + 420;
      go(e.deltaX > 0 ? page + 1 : page - 1);
    }, { passive: false });

    var resizeTimer;
    function onResize() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(layout, 120);
    }
    window.addEventListener("resize", onResize);

    layout();
    // Fonts land after first paint and change slide heights, so re-measure.
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);

    // Removes the carousel, its arrows and its resize listener, so a section
    // can rebuild it with different items (the Brothers / Sisters switch).
    function destroy() {
      window.removeEventListener("resize", onResize);
      clearTimeout(resizeTimer);
      root.remove();
      prev.remove();
      next.remove();
    }

    return { go: go, layout: layout, destroy: destroy };
  }

  function arrowButton(dir, label) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "carousel__arrow carousel__arrow--" + dir;
    b.setAttribute("aria-label", label);
    b.innerHTML = CHEVRON;
    return b;
  }

  global.createCarousel = createCarousel;
})(window);

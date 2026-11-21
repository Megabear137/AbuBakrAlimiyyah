/* =====================================================================
   graduates.js - graduates.html: every graduate, class by class, from
   content/graduates.json (option 1 of design/canvas-graduates/, the
   register). The footer's contact lines come from program.json.
   ===================================================================== */
(function () {
  "use strict";

  var slot = function (name) { return document.querySelector('[data-slot="' + name + '"]'); };

  var ICONS = {
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

  function loadJSON(path) {
    return fetch(path, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(path + " -> HTTP " + r.status);
      return r.json();
    });
  }

  /* ------------------------------ the list ----------------------------- */
  var SIDES = [["brothers", "Brothers"], ["sisters", "Sisters"]];

  function renderGraduates(data) {
    var classes = data.classes || [];
    var titles = data.titles || {};
    var kicker = slot("graduates-kicker");
    if (kicker) kicker.textContent = data.kicker || "";
    if (data.heading) slot("graduates-heading").textContent = data.heading;

    // The count, worked out from the list: "167 graduates · 59 brothers, 108 sisters · 2015–2026".
    var b = 0, s = 0;
    classes.forEach(function (c) { b += (c.brothers || []).length; s += (c.sisters || []).length; });
    if (classes.length) {
      var first = classes[0].year, last = classes[classes.length - 1].year;
      slot("graduates-count").textContent = (b + s) + " graduates · " + b + " brothers, " + s + " sisters · " +
        (first === last ? first : first + "–" + last);
    }

    // The row of years, each a jump to its class.
    var years = slot("graduates-years");
    years.textContent = "";
    classes.forEach(function (c) {
      var a = el("a", "", esc(c.year));
      a.href = "#class-" + encodeURIComponent(c.year);
      years.appendChild(a);
    });

    var mount = slot("graduates");
    mount.textContent = "";
    classes.forEach(function (c) {
      var sec = el("section", "grad-class");
      sec.id = "class-" + c.year;
      sec.setAttribute("aria-labelledby", "class-" + c.year + "-label");
      sec.appendChild(el("p", "grad-class__year", esc(c.year)));
      var label = el("h2", "grad-class__label", esc(c.label || c.year));
      label.id = "class-" + c.year + "-label";
      sec.appendChild(label);

      var sides = SIDES.filter(function (side) { return (c[side[0]] || []).length; });
      var cols = el("div", "grad-cols" + (sides.length === 1 ? " grad-cols--one" : ""));
      sides.forEach(function (side) {
        var col = el("div", "grad-col");
        col.appendChild(el("h3", "grad-col__head", side[1]));
        // Each name after its title, as the masjid's list has them: "Maulānā Zishan Khalid".
        var title = titles[side[0]] ? '<span class="grad-col__title">' + esc(titles[side[0]]) + "</span> " : "";
        col.appendChild(el("ul", "grad-col__names", c[side[0]].map(function (n) {
          return "<li>" + title + esc(n) + "</li>";
        }).join("")));
        cols.appendChild(col);
      });
      sec.appendChild(cols);
      mount.appendChild(sec);
    });

    // A link straight to a class (graduates.html#class-2019) lands once it is drawn.
    if (location.hash) {
      var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (target) target.scrollIntoView();
    }
  }

  /* ------------------------------ footer ------------------------------ */
  function renderFooter(footer) {
    var mount = slot("footer-contact");
    if (!mount || !footer) return;
    mount.textContent = "";
    function line(icon, html) {
      mount.appendChild(el("span", "site-footer__line", '<i aria-hidden="true">' + icon + "</i>" + html));
    }
    // The address opens the map and the number dials: on a phone these are
    // the two lines most people want to tap.
    if (footer.address) {
      line(ICONS.home, isTodo(footer.address) ? esc(footer.address)
        : '<a href="https://www.google.com/maps/search/?api=1&amp;query=' +
          encodeURIComponent(footer.address) + '" target="_blank" rel="noopener">' + esc(footer.address) + "</a>");
    }
    if (footer.email) {
      line(ICONS.mail, isTodo(footer.email) ? esc(footer.email)
        : '<a href="mailto:' + esc(footer.email) + '">' + esc(footer.email) + "</a>");
    }
    if (footer.phone) {
      line(ICONS.phone, isTodo(footer.phone) ? esc(footer.phone)
        : '<a href="tel:' + footer.phone.replace(/[^\d+]/g, "") + '">' + esc(footer.phone) + "</a>");
    }
  }

  /* -------------------------------- boot -------------------------------- */
  var yearSlot = slot("year");
  if (yearSlot) yearSlot.textContent = String(new Date().getFullYear());

  Promise.all([
    loadJSON("content/graduates.json").then(renderGraduates),
    loadJSON("content/program.json").then(function (data) { renderFooter(data.footer); })
  ]).catch(function (err) {
    console.error("Content failed to load.", err);
  });
})();

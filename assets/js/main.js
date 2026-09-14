/* =====================================================================
   main.js - loads content/*.json and renders every data-driven section.
   Everything on the page comes from those four files; edit them, not
   the HTML.
   ===================================================================== */
(function () {
  "use strict";

  var slot = function (name) { return document.querySelector('[data-slot="' + name + '"]'); };

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

  function loadJSON(path) {
    return fetch(path).then(function (r) {
      if (!r.ok) throw new Error(path + " -> HTTP " + r.status);
      return r.json();
    });
  }

  /* ----------------------------- program ---------------------------- */
  function renderProgram(data) {
    setText("intro-body", data.introduction && data.introduction.body);
    if (data.introduction && data.introduction.label) {
      var introLabel = document.getElementById("intro-label");
      if (introLabel) introLabel.textContent = data.introduction.label;
    }
    if (data.program) {
      setText("program-heading", data.program.heading);
      setText("program-body", data.program.body);
    }
    if (data.timings) {
      setText("timings-heading", data.timings.heading);
      renderTimings(data.timings);
    }
    if (data.fees) {
      setText("fees-heading", data.fees.heading);
      renderFees(data.fees);
    }
    renderFooter(data.footer);
  }

  function setText(name, value) {
    var node = slot(name);
    if (node && value) node.textContent = value;
  }

  function renderTimings(timings) {
    var mount = slot("timings");
    if (!mount) return;
    mount.textContent = "";

    (timings.groups || []).forEach(function (group) {
      var g = el("div", "timing-group");
      g.appendChild(el("p", "group__label", esc(group.label)));
      if (group.title) g.appendChild(el("p", "group__title", esc(group.title)));

      (group.rows || []).forEach(function (row) {
        g.appendChild(
          el("div", "datarow",
            '<span class="datarow__key">' + esc(row.days) + "</span>" +
            '<span class="datarow__value">' + esc(row.time) + "</span>")
        );
      });

      mount.appendChild(g);
    });
  }

  function renderFees(fees) {
    var mount = slot("fees");
    if (!mount) return;
    mount.textContent = "";

    (fees.tiers || []).forEach(function (tier) {
      var f = el("div", "fee");
      f.appendChild(el("p", "fee__label", esc(tier.label)));
      f.appendChild(
        el("p", "fee__amount",
          esc(tier.amount) + ' <span class="fee__period">' + esc(tier.period || "") + "</span>")
      );
      if (tier.note) f.appendChild(el("p", "fee__note", esc(tier.note)));
      f.appendChild(el("hr", "fee__hr"));
      mount.appendChild(f);
    });

    var d = fees.discounts;
    if (d && d.rows && d.rows.length) {
      var box = el("div", "discounts");
      box.appendChild(el("p", "discounts__label", esc(d.label || "Family discounts")));
      d.rows.forEach(function (row) {
        box.appendChild(
          el("div", "datarow",
            '<span class="datarow__key">' + esc(row.count) + "</span>" +
            '<span class="datarow__value">' + esc(row.value) + "</span>")
        );
      });
      mount.appendChild(box);
    }

    // Optional purchase / enrolment link - set `cta` in program.json when ready.
    if (fees.cta && fees.cta.href && fees.cta.label) {
      var a = el("a", "arch__cta", esc(fees.cta.label));
      a.href = fees.cta.href;
      mount.appendChild(a);
    }
  }

  function renderFooter(footer) {
    var mount = slot("footer-contact");
    if (!mount || !footer) return;
    var lines = [];
    if (footer.address) lines.push(esc(footer.address));
    if (footer.email) lines.push('<a href="mailto:' + esc(footer.email) + '">' + esc(footer.email) + "</a>");
    if (footer.phone) lines.push(esc(footer.phone));
    mount.innerHTML = lines.join("<br>");
  }

  /* ---------------------------- teachers ---------------------------- */
  function renderTeachers(data) {
    var mount = slot("teachers");
    if (!mount) return;
    setText("teachers-heading", data.heading);

    createCarousel({
      mount: mount,
      items: data.teachers || [],
      label: "Our teachers",
      perView: function () {
        var w = window.innerWidth;
        if (w < 620) return 1;
        if (w < 940) return 2;
        return 3;
      },
      render: function (t) {
        var card = el("article", "teacher");
        var frame = el("div", "teacher__frame gilt");
        if (t.honorific) frame.appendChild(el("p", "teacher__honorific", esc(t.honorific)));
        frame.appendChild(el("h3", "teacher__name", esc(t.name)));
        frame.appendChild(el("hr", "teacher__rule"));
        if (t.bio) frame.appendChild(el("p", "teacher__bio", esc(t.bio)));
        card.appendChild(frame);
        card.appendChild(el("div", "stripe"));
        return card;
      }
    });
  }

  /* --------------------------- testimonies -------------------------- */
  function renderTestimonies(data) {
    var mount = slot("testimonies");
    if (!mount) return;
    setText("testimonies-heading", data.heading);

    createCarousel({
      mount: mount,
      items: data.testimonies || [],
      label: "Alumni testimonies",
      perView: function () { return window.innerWidth < 760 ? 1 : 2; },
      render: function (t) {
        var card = el("figure", "testimony");
        var frame = el("div", "testimony__frame gilt");
        frame.appendChild(el("blockquote", "testimony__quote", '"' + esc(t.quote) + '"'));
        var cite = el("figcaption", "testimony__cite",
          "&ndash; " + esc(t.name) + (t.graduated ? ", graduated " + esc(t.graduated) : ""));
        frame.appendChild(cite);
        card.appendChild(frame);
        card.appendChild(el("div", "stripe"));
        return card;
      }
    });
  }

  /* ------------------------------ boot ------------------------------ */
  var yearSlot = slot("year");
  if (yearSlot) yearSlot.textContent = String(new Date().getFullYear());

  Promise.all([
    loadJSON("content/program.json").then(renderProgram),
    loadJSON("content/curriculum.json").then(function (data) {
      setText("curriculum-label", data.label);
      renderCurriculum(slot("curriculum"), data);
    }),
    loadJSON("content/teachers.json").then(renderTeachers),
    loadJSON("content/testimonies.json").then(renderTestimonies)
  ]).catch(function (err) {
    console.error("Content failed to load.", err);
    var banner = el("p", "section__body section__body--center",
      "Content could not be loaded. If you opened this file directly, serve the folder over " +
      "a local web server instead (see README.md).");
    banner.style.cssText = "padding:2rem 1rem;color:#8a2b2b";
    document.getElementById("main").prepend(banner);
  });
})();

/* =====================================================================
   main.js - loads content/*.json and renders every data-driven section.
   Everything on the page comes from those four files; edit them, not
   the HTML.
   ===================================================================== */
(function () {
  "use strict";

  var slot = function (name) { return document.querySelector('[data-slot="' + name + '"]'); };

  var ICONS = {
    arrow: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg>',
    clock: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10" cy="10" r="7.2"/><path d="M10 6v4.3l2.8 1.7"/></svg>',
    quote: '<svg class="testimony__mark" viewBox="0 0 40 32" fill="currentColor" aria-hidden="true"><path d="M0 32V19C0 8 6 1.5 16 0l1.6 4C11.6 5.8 9 9.4 8.8 14H16v18H0zm22 0V19C22 8 28 1.5 38 0l1.6 4C33.6 5.8 31 9.4 30.8 14H38v18H22z"/></svg>'
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

  function setText(name, value) {
    var node = slot(name);
    if (node && value) node.textContent = value;
  }

  function loadJSON(path) {
    // no-cache: revalidate every load, so an edited JSON file shows up without a hard refresh.
    return fetch(path, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(path + " -> HTTP " + r.status);
      return r.json();
    });
  }

  /* ------------------------------ hero ------------------------------- */
  function renderHero(hero) {
    setText("hero-eyebrow", hero.eyebrow);
    setText("hero-subtitle", hero.subtitle);

    // One word of the title can be set in gold italic - `titleEmphasis`.
    var title = slot("hero-title");
    if (title && hero.title) {
      var html = esc(hero.title);
      if (hero.titleEmphasis) {
        html = html.replace(esc(hero.titleEmphasis), "<em>" + esc(hero.titleEmphasis) + "</em>");
      }
      title.innerHTML = html;
    }

    var mount = slot("hero-cta");
    if (!mount) return;
    mount.textContent = "";
    var cta = hero.ctaPrimary;
    if (cta && cta.label && cta.href) {
      var a = el("a", "btn btn--gold", esc(cta.label) + " " + ICONS.arrow);
      a.href = cta.href;
      mount.appendChild(a);
    }
  }

  /* ----------------------------- program ---------------------------- */
  function renderProgram(data) {
    if (data.hero) renderHero(data.hero);
    if (data.introduction) {
      setText("intro-label", data.introduction.label);
      setText("intro-body", data.introduction.body);
    }
    if (data.program) {
      setText("program-heading", data.program.heading);
      setText("program-body", data.program.body);
    }
    if (data.details) {
      setText("details-heading", data.details.heading);
      setText("details-lede", data.details.lede);
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

  function renderTimings(timings) {
    var mount = slot("timings");
    if (!mount) return;
    mount.textContent = "";

    (timings.groups || []).forEach(function (group) {
      var g = el("div", "tgroup");
      g.appendChild(el("div", "tgroup__head",
        '<p class="tgroup__label">' + esc(group.label) + "</p>" +
        (group.years ? '<p class="tgroup__years">' + esc(group.years) + "</p>" : "")));
      (group.rows || []).forEach(function (row) {
        g.appendChild(el("div", "row",
          "<span>" + esc(row.days) + "</span>" +
          '<span class="row__value">' + ICONS.clock + esc(row.time) + "</span>"));
      });
      mount.appendChild(g);
    });
  }

  function renderFees(fees) {
    var mount = slot("fees");
    if (!mount) return;
    mount.textContent = "";

    var tiers = fees.tiers || [];
    if (tiers.length) {
      var box = el("div", "tiers");
      tiers.forEach(function (tier) {
        box.appendChild(el("div", "tier",
          '<p class="tier__label">' + esc(tier.label) + "</p>" +
          '<p class="tier__amount">' + esc(tier.amount) +
            '<span class="tier__period">' + esc(tier.period || "") + "</span></p>" +
          (tier.note ? '<p class="tier__note">' + esc(tier.note) + "</p>" : "")));
      });
      mount.appendChild(box);
    }

    var d = fees.discounts;
    if (d && d.rows && d.rows.length) {
      mount.appendChild(el("p", "card__kicker discounts__label", esc(d.label || "Family discounts")));
      d.rows.forEach(function (row) {
        mount.appendChild(el("div", "row row--rule",
          "<span>" + esc(row.count) + "</span>" +
          '<span class="row__value">' + esc(row.value) + "</span>"));
      });
    }

    // Optional purchase / enrolment link - set `cta` in program.json when ready.
    if (fees.cta && fees.cta.href && fees.cta.label) {
      var a = el("a", "btn btn--gold fees__cta", esc(fees.cta.label) + " " + ICONS.arrow);
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
    mount.innerHTML = lines.join(" &middot; ");
  }

  /* ---------------------------- teachers ---------------------------- */
  // Two initials for the monogram; a TODO placeholder gets none.
  function initials(name) {
    if (/^\s*TODO/i.test(name || "")) return "";
    return String(name || "").split(/\s+/).filter(Boolean)
      .map(function (w) { return w.charAt(0).toUpperCase(); })
      .slice(0, 2).join("");
  }

  function renderTeachers(data) {
    var mount = slot("teachers");
    if (!mount) return;
    setText("teachers-heading", data.heading);

    createCarousel({
      mount: mount,
      controls: slot("teachers-controls"),
      items: data.teachers || [],
      label: "Our teachers",
      perView: function () {
        var w = window.innerWidth;
        if (w < 620) return 1;
        if (w < 940) return 2;
        return 3;
      },
      render: function (t) {
        var card = el("article", "card teacher");
        card.appendChild(el("span", "teacher__mono", esc(initials(t.name))));
        if (t.honorific) card.appendChild(el("p", "teacher__honorific", esc(t.honorific)));
        card.appendChild(el("h3", "teacher__name", esc(t.name)));
        if (t.bio) card.appendChild(el("p", "teacher__bio", esc(t.bio)));
        return card;
      }
    });
  }

  /* --------------------------- testimonies -------------------------- */
  function renderTestimonies(data) {
    var mount = slot("testimonies");
    if (!mount) return;
    setText("testimonies-heading", data.heading);

    // "Alumni Testimonies" -> "Alumni <em>Testimonies</em>": the last word in gold.
    var heading = slot("testimonies-heading");
    if (heading) {
      var words = heading.textContent.trim().split(/\s+/);
      if (words.length > 1) {
        var last = words.pop();
        heading.innerHTML = esc(words.join(" ")) + " <em>" + esc(last) + "</em>";
      }
    }

    createCarousel({
      mount: mount,
      controls: slot("testimonies-controls"),
      items: data.testimonies || [],
      label: "Alumni testimonies",
      perView: function () { return window.innerWidth < 760 ? 1 : 2; },
      render: function (t) {
        var card = el("figure", "testimony");
        card.innerHTML = ICONS.quote;
        card.appendChild(el("blockquote", "testimony__quote", esc(t.quote)));
        card.appendChild(el("figcaption", "testimony__cite",
          "<b>" + esc(t.name) + "</b>" + (t.graduated ? " &middot; Class of " + esc(t.graduated) : "")));
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
      setText("curriculum-kicker", data.kicker);
      setText("curriculum-intro", data.intro);
      renderCurriculum(slot("curriculum"), data);
    }),
    loadJSON("content/teachers.json").then(renderTeachers),
    loadJSON("content/testimonies.json").then(renderTestimonies)
  ]).catch(function (err) {
    console.error("Content failed to load.", err);
    var banner = el("p", "",
      "Content could not be loaded. If you opened this file directly, serve the folder over " +
      "a local web server instead (see CLAUDE.md).");
    banner.style.cssText = "padding:8rem 1rem 2rem;text-align:center;color:#8a2b2b";
    document.getElementById("main").prepend(banner);
  });
})();

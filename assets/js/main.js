/* =====================================================================
   main.js - loads content/*.json and renders every data-driven section.
   Everything on the page comes from those five files; edit them, not
   the HTML.
   ===================================================================== */
(function () {
  "use strict";

  var slot = function (name) { return document.querySelector('[data-slot="' + name + '"]'); };

  var ICONS = {
    arrow: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg>',
    chev:  '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 5l5 5-5 5"/></svg>',
    book:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M4 5.5C4 4.7 4.7 4 5.5 4H11v16H5.5C4.7 20 4 19.3 4 18.5v-13ZM20 5.5c0-.8-.7-1.5-1.5-1.5H13v16h5.5c.8 0 1.5-.7 1.5-1.5v-13Z"/></svg>',
    quote: '<svg class="testimony__mark" viewBox="0 0 40 32" fill="currentColor" aria-hidden="true"><path d="M0 32V19C0 8 6 1.5 16 0l1.6 4C11.6 5.8 9 9.4 8.8 14H16v18H0zm22 0V19C22 8 28 1.5 38 0l1.6 4C33.6 5.8 31 9.4 30.8 14H38v18H22z"/></svg>',
    play:  '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>',
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

  function setText(name, value) {
    var node = slot(name);
    if (node && value) node.textContent = value;
  }

  // Placeholders in the JSON start with "TODO"; they render, but quieter.
  function isTodo(s) { return /^\s*TODO\b/i.test(String(s || "")); }

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

    // One word of the title can be set apart - `titleEmphasis` (gold italic in
    // light mode; in dark the whole title is gold).
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
      setText("details-kicker", data.details.kicker);
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
      renderDiscounts(data.fees.discounts);
    }
    renderFooter(data.footer);
  }

  // One tile per group, a row for each of its times, like a board of prayer times.
  function renderTimings(timings) {
    var mount = slot("timings");
    if (!mount) return;
    mount.textContent = "";

    (timings.groups || []).forEach(function (group) {
      mount.appendChild(el("div", "tile",
        (group.years ? '<p class="tile__years">' + esc(group.years) + "</p>" : "") +
        '<h4 class="tile__label">' + esc(group.label) + "</h4>" +
        (group.rows || []).map(function (row) {
          return '<p class="tile__row"><span>' + esc(row.days) + "</span><b>" + esc(row.time) + "</b></p>";
        }).join("")));
    });
  }

  function renderFees(fees) {
    var mount = slot("fees");
    if (!mount) return;
    mount.textContent = "";

    var tiers = fees.tiers || [];
    if (tiers.length) {
      var box = el("div", "fees");
      tiers.forEach(function (tier) {
        box.appendChild(el("div", "fee",
          '<p class="fee__label">' + esc(tier.label) + "</p>" +
          '<p class="fee__amount">' + esc(tier.amount) + "</p>" +
          '<p class="fee__note">' + esc([tier.period, tier.note].filter(Boolean).join(" · ")) + "</p>"));
      });
      mount.appendChild(box);
    }

    // Optional purchase / enrolment link - set `cta` in program.json when ready.
    if (fees.cta && fees.cta.href && fees.cta.label) {
      var a = el("a", "btn btn--gold fees__cta", esc(fees.cta.label) + " " + ICONS.arrow);
      a.href = fees.cta.href;
      mount.appendChild(a);
    }
  }

  function renderDiscounts(d) {
    var mount = slot("discounts");
    if (!mount || !d || !d.rows || !d.rows.length) return;
    mount.textContent = "";
    mount.appendChild(el("h3", "panel__title panel__title--sm", esc(d.label || "Family discounts")));
    var list = el("dl", "discounts");
    d.rows.forEach(function (row) {
      list.appendChild(el("div", "discounts__row",
        "<dt>" + esc(row.count) + "</dt><dd>" + esc(row.value) + "</dd>"));
    });
    mount.appendChild(list);
    mount.hidden = false;
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

  /* ---------------------------- teachers ---------------------------- */
  // A mosaic: the first teacher large, the rest in a grid beside and below.
  function renderTeachers(data) {
    var mount = slot("teachers");
    if (!mount) return;
    setText("teachers-heading", data.heading);
    setText("teachers-kicker", data.kicker);
    mount.textContent = "";

    (data.teachers || []).forEach(function (t, i) {
      var card = el("article", "teacher" + (i === 0 ? " teacher--lead" : "") + (isTodo(t.name) ? " teacher--todo" : ""));
      if (t.honorific) card.appendChild(el("p", "teacher__honorific", esc(t.honorific)));
      card.appendChild(el("h3", "teacher__name", esc(t.name)));
      if (t.bio) card.appendChild(el("p", "teacher__bio", esc(t.bio)));
      mount.appendChild(card);
    });
  }

  /* ------------------------ articles & videos ----------------------- */
  // Each section holds a brothers' and a sisters' list. The two sections share
  // one choice: either switch rebuilds both sections. The choice is remembered
  // per viewer, and the page works without storage.
  var AUDIENCE_KEY = "alimiyyah.audience";

  function savedAudience() {
    try {
      return localStorage.getItem(AUDIENCE_KEY) === "sisters" ? "sisters" : "brothers";
    } catch (e) {
      return "brothers";
    }
  }

  // A title links its whole card when there is an href (a stretched link).
  function linkedTitle(tag, className, title, href) {
    var text = esc(title);
    if (href) text = '<a class="stretched" href="' + esc(href) + '">' + text + "</a>";
    return "<" + tag + ' class="' + className + '">' + text + "</" + tag + ">";
  }

  function pad(n) { return (n < 10 ? "0" : "") + n; }

  // Articles: one at a time in a featured slider - a board panel, the article
  // beside it with prev/next, dashes and a count, and an "Up next" rail of the
  // following two. Returns a handle with destroy(), like a carousel.
  function renderArticles(mount, items) {
    var n = items.length;
    var at = 0;
    var slider = el("div", "slider" + (n > 1 ? "" : " slider--single"));
    var art = el("div", "slider__art board", ICONS.book);
    var main = el("div", "slider__main");
    var body = el("div", "slider__body");
    body.setAttribute("aria-live", "polite");
    main.appendChild(body);
    slider.append(art, main);

    var dashes, count, rail;
    if (n > 1) {
      var nav = el("div", "slider__nav");
      var prev = el("button", "round round--arrow round--prev", ICONS.chev);
      var next = el("button", "round round--arrow", ICONS.chev);
      prev.type = next.type = "button";
      prev.setAttribute("aria-label", "Previous article");
      next.setAttribute("aria-label", "Next article");
      prev.addEventListener("click", function () { show(at - 1); });
      next.addEventListener("click", function () { show(at + 1); });
      dashes = el("span", "slider__dashes");
      dashes.setAttribute("aria-hidden", "true");
      for (var i = 0; i < n; i++) dashes.appendChild(el("i"));
      count = el("span", "slider__count");
      nav.append(prev, next, dashes, count);
      main.appendChild(nav);

      rail = el("div", "slider__next");
      slider.appendChild(rail);
    }
    mount.appendChild(slider);

    function show(i) {
      at = (i + n) % n;
      var a = items[at];
      body.innerHTML =
        '<div class="slider__tags">' +
          (a.subject ? '<span class="chip">' + esc(a.subject) + "</span>" : "") +
          (a.readMinutes ? "<span>" + esc(a.readMinutes) + " min read</span>" : "") +
        "</div>" +
        linkedTitle("h3", "slider__title", a.title, a.href) +
        (a.author ? '<p class="slider__by">' + esc(a.author) + "</p>" : "") +
        (a.excerpt ? '<p class="slider__text">' + esc(a.excerpt) + "</p>" : "") +
        (a.href ? '<a class="btn btn--gold" href="' + esc(a.href) + '" tabindex="-1" aria-hidden="true">Read article ' + ICONS.arrow + "</a>" : "");
      body.classList.remove("media-swap");
      void body.offsetWidth;               // restart the animation
      body.classList.add("media-swap");
      if (n < 2) return;

      Array.prototype.forEach.call(dashes.children, function (d, j) { d.classList.toggle("on", j === at); });
      count.textContent = pad(at + 1) + " / " + pad(n);

      rail.innerHTML = '<p class="slider__next-label">Up next</p>';
      for (var k = 1; k <= Math.min(2, n - 1); k++) {
        var j = (at + k) % n;
        var card = el("button", "slider__card board" + (k % 2 ? " board--rust" : ""),
          "<b>" + (j + 1) + "</b><span>" + esc(items[j].title) + "</span>");
        card.type = "button";
        card.setAttribute("aria-label", "Show article " + (j + 1) + ": " + items[j].title);
        card.addEventListener("click", show.bind(null, j));
        rail.appendChild(card);
      }
    }

    show(0);
    return { destroy: function () { slider.remove(); } };
  }

  // Videos: a carousel of wide cards, the caption beneath the picture.
  function videoCard(v, i) {
    var card = el("article", "vid");
    // Without a thumbnail, alternate the masjid photo and a plain board.
    var thumb = el("div", "vid__art" + (v.thumbnail ? "" : i % 2 ? " board" + (i % 4 === 3 ? " board--rust" : "") : " vid__art--photo"),
      '<span class="vid__play">' + ICONS.play + "</span>" +
      (v.date || v.duration ? '<span class="vid__time">' + esc([v.date, v.duration].filter(Boolean).join(" · ")) + "</span>" : ""));
    if (v.thumbnail) thumb.style.backgroundImage = "url(" + JSON.stringify(v.thumbnail) + ")";
    card.appendChild(thumb);
    card.insertAdjacentHTML("beforeend",
      linkedTitle("h3", "vid__title", v.title, v.href) +
      (v.subject ? '<p class="vid__meta">' + esc(v.subject) + "</p>" : ""));
    return card;
  }

  function renderMedia(data) {
    var names = data.audiences || {};
    var audience = savedAudience();

    // `render` fills the mount and returns a handle to destroy on the next swap.
    var sections = [
      { key: "articles", noun: "articles", render: renderArticles },
      {
        key: "videos", noun: "videos",
        render: function (mount, items, label) {
          return createCarousel({
            mount: mount,
            items: items,
            label: label,
            perView: function () { var w = window.innerWidth; return w < 700 ? 1 : w < 1040 ? 2 : 3; },
            render: videoCard
          });
        }
      }
    ].filter(function (s) { return data[s.key] && slot(s.key); });

    // An optional link to the full list, e.g. "articles": {"moreHref": "articles/"}.
    sections.forEach(function (s) {
      setText(s.key + "-kicker", data[s.key].kicker);
      setText(s.key + "-heading", data[s.key].heading);
      var more = slot(s.key + "-more");
      if (more && data[s.key].moreHref) {
        more.href = data[s.key].moreHref;
        more.textContent = data[s.key].moreLabel || "All " + s.noun + " →";
        more.hidden = false;
      }
    });

    function name(id) { return names[id] || (id === "sisters" ? "Sisters" : "Brothers"); }

    function build(s, swap) {
      var mount = slot(s.key);
      if (s.handle) s.handle.destroy();
      s.handle = null;
      mount.textContent = "";

      var items = data[s.key][audience] || [];
      var label = name(audience) + "' " + s.noun;
      if (items.length) {
        s.handle = s.render(mount, items, label);
      } else {
        mount.appendChild(el("p", "media-empty", "No " + esc(label.toLowerCase()) + " yet."));
      }

      if (swap) {
        mount.classList.remove("media-swap");
        void mount.offsetWidth;            // restart the animation
        mount.classList.add("media-swap");
      }
    }

    // A two-button segmented control in each head; the pressed side is the library shown.
    var groups = sections.map(function (s) {
      var mount = slot(s.key + "-audience");
      if (!mount) return null;
      var g = el("div", "seg");
      g.setAttribute("role", "group");
      g.setAttribute("aria-label", "Library");
      ["brothers", "sisters"].forEach(function (id) {
        var b = el("button", "seg__btn", esc(name(id)));
        b.type = "button";
        b.dataset.aud = id;
        b.addEventListener("click", function () { setAudience(id); });
        g.appendChild(b);
      });
      mount.textContent = "";
      mount.appendChild(g);
      return g;
    }).filter(Boolean);

    function sync() {
      groups.forEach(function (g) {
        Array.prototype.forEach.call(g.children, function (b) {
          b.setAttribute("aria-pressed", String(b.dataset.aud === audience));
        });
      });
    }

    function setAudience(next) {
      if (next === audience) return;
      audience = next;
      try { localStorage.setItem(AUDIENCE_KEY, audience); } catch (e) { /* storage blocked: not remembered */ }
      sync();
      sections.forEach(function (s) { build(s, true); });
    }

    sync();
    sections.forEach(function (s) { build(s, false); });
  }

  /* --------------------------- testimonies -------------------------- */
  function renderTestimonies(data) {
    var mount = slot("testimonies");
    if (!mount) return;
    setText("testimonies-kicker", data.kicker);
    setText("testimonies-heading", data.heading);

    createCarousel({
      mount: mount,
      items: data.testimonies || [],
      label: "Alumni testimonies",
      perView: function () { return window.innerWidth < 700 ? 1 : window.innerWidth < 1040 ? 2 : 3; },
      // A mihrab niche: the moulding, the recess that holds the testimony, and a sill.
      render: function (t) {
        var slotEl = el("figure", "niche-slot");
        var niche = el("div", "niche");
        var recess = el("div", "niche__recess", ICONS.quote);
        recess.appendChild(el("blockquote", "testimony__quote", esc(t.quote)));
        recess.appendChild(el("figcaption", "testimony__cite",
          "<b>" + esc(t.name) + "</b>" + (t.graduated ? "Class of " + esc(t.graduated) : "")));
        niche.appendChild(recess);
        slotEl.appendChild(niche);
        slotEl.appendChild(el("div", "niche__sill"));
        return slotEl;
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
    loadJSON("content/media.json").then(renderMedia),
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

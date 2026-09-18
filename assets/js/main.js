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
    clock: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10" cy="10" r="7.2"/><path d="M10 6v4.3l2.8 1.7"/></svg>',
    quote: '<svg class="testimony__mark" viewBox="0 0 40 32" fill="currentColor" aria-hidden="true"><path d="M0 32V19C0 8 6 1.5 16 0l1.6 4C11.6 5.8 9 9.4 8.8 14H16v18H0zm22 0V19C22 8 28 1.5 38 0l1.6 4C33.6 5.8 31 9.4 30.8 14H38v18H22z"/></svg>',
    star:  '<svg class="article-feature__mark" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><rect x="8" y="8" width="16" height="16"/><rect x="8" y="8" width="16" height="16" transform="rotate(45 16 16)"/><circle cx="16" cy="16" r="3"/></svg>',
    play:  '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>'
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

  // "Alumni Testimonies" -> "Alumni <em>Testimonies</em>": the last word in gold.
  function emphasiseLastWord(name) {
    var heading = slot(name);
    if (!heading) return;
    var words = heading.textContent.trim().split(/\s+/);
    if (words.length < 2) return;
    var last = words.pop();
    heading.innerHTML = esc(words.join(" ")) + " <em>" + esc(last) + "</em>";
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
  function renderTeachers(data) {
    var mount = slot("teachers");
    if (!mount) return;
    setText("teachers-heading", data.heading);
    emphasiseLastWord("teachers-heading");
    setText("teachers-kicker", data.kicker);

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
        if (t.honorific) card.appendChild(el("p", "teacher__honorific", esc(t.honorific)));
        card.appendChild(el("h3", "teacher__name", esc(t.name)));
        if (t.bio) card.appendChild(el("p", "teacher__bio", esc(t.bio)));
        return card;
      }
    });
  }

  /* ------------------------ articles & videos ----------------------- */
  // Each section holds a brothers' and a sisters' list. The two sections share
  // one choice: flipping the switch in either head rebuilds both sections. The
  // choice is remembered per viewer, and the page works without storage.
  var AUDIENCE_KEY = "alimiyyah.audience";

  function savedAudience() {
    try {
      return localStorage.getItem(AUDIENCE_KEY) === "sisters" ? "sisters" : "brothers";
    } catch (e) {
      return "brothers";
    }
  }

  // The title links the whole card when there is an href (a stretched link).
  function cardTitle(className, title, href) {
    var text = esc(title);
    if (href) text = '<a class="stretched" href="' + esc(href) + '">' + text + "</a>";
    return '<h3 class="' + className + '">' + text + "</h3>";
  }

  // The first article is a full-width chocolate feature; the rest follow beneath it
  // in a carousel of white cards under their own small head, so the arrows sit
  // next to what they move rather than above the feature.
  function articleTile(a, feature) {
    var kicker = feature ? ["Featured", a.subject].filter(Boolean).join(" · ") : a.subject;
    return el("article", feature ? "article-feature" : "article-card",
      (feature ? ICONS.star : "") +
      (kicker ? '<p class="' + (feature ? "card__kicker" : "kicker") + '">' + esc(kicker) + "</p>" : "") +
      cardTitle("article__title", a.title, a.href) +
      (a.excerpt ? '<p class="article__excerpt">' + esc(a.excerpt) + "</p>" : "") +
      '<p class="article__meta"><b>' + esc(a.author) + "</b>" +
        (a.readMinutes ? " · " + esc(a.readMinutes) + " min read" : "") + "</p>" +
      // The stretched title link already covers the card; this only looks like a button.
      (feature && a.href ? '<span class="btn btn--gold btn--sm article-feature__cta" aria-hidden="true">Read article</span>' : ""));
  }

  function renderArticles(mount, items, label) {
    mount.appendChild(articleTile(items[0], true));
    if (items.length < 2) return null;

    var head = el("div", "articles__rest-head", '<p class="kicker">More articles</p>');
    var rest = el("div", "articles__rest");
    mount.append(head, rest);
    return createCarousel({
      mount: rest,
      items: items.slice(1),
      label: label,
      perView: function () {
        var w = window.innerWidth;
        if (w < 620) return 1;
        if (w < 940) return 2;
        return 3;
      },
      render: function (a) { return articleTile(a, false); }
    });
  }

  function videoCard(v, i) {
    var card = el("article", "video-card");
    // Without a thumbnail, alternate the masjid photo and the star lattice.
    var thumb = el("div", "video-card__thumb" +
      (v.thumbnail ? "" : i % 2 ? " video-card__thumb--pattern" : " video-card__thumb--photo"),
      '<span class="video-card__play">' + ICONS.play + "</span>" +
      (v.duration ? '<span class="video-card__dur">' + esc(v.duration) + "</span>" : ""));
    if (v.thumbnail) thumb.style.backgroundImage = "url(" + JSON.stringify(v.thumbnail) + ")";
    card.appendChild(thumb);
    card.appendChild(el("div", "video-card__cap",
      cardTitle("video-card__title", v.title, v.href) +
      '<p class="video-card__meta">' + esc([v.subject, v.date].filter(Boolean).join(" · ")) + "</p>"));
    return card;
  }

  function renderMedia(data) {
    var names = data.audiences || {};
    var audience = savedAudience();

    // `render` fills the mount and returns a carousel to destroy on the next swap, or null.
    var sections = [
      {
        key: "articles", noun: "articles",
        render: renderArticles
      },
      {
        key: "videos", noun: "videos",
        render: function (mount, items, label) {
          return createCarousel({
            mount: mount,
            items: items,
            label: label,
            perView: function () { return window.innerWidth < 760 ? 1 : 2; },
            render: videoCard
          });
        }
      }
    ].filter(function (s) { return data[s.key] && slot(s.key); });

    // An optional link to the full list, e.g. "articles": {"moreHref": "articles/"}.
    sections.forEach(function (s) {
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
      if (s.carousel) s.carousel.destroy();
      s.carousel = null;
      mount.textContent = "";

      var items = data[s.key][audience] || [];
      var label = name(audience) + "' " + s.noun;
      if (items.length) {
        s.carousel = s.render(mount, items, label);
      } else {
        mount.appendChild(el("p", "card media-empty", "No " + esc(label.toLowerCase()) + " yet."));
      }

      if (swap) {
        mount.classList.remove("media-swap");
        void mount.offsetWidth;            // restart the animation
        mount.classList.add("media-swap");
      }
    }

    // One button with role="switch"; checked means sisters. A click on either
    // side's label picks that side, a click anywhere else flips it.
    var switches = sections.map(function (s) {
      setText(s.key + "-heading", data[s.key].heading);
      var mount = slot(s.key + "-audience");
      if (!mount) return null;
      var b = el("button", "aud-toggle",
        '<span class="aud-toggle__side" data-aud="brothers">' + esc(name("brothers")) + "</span>" +
        '<span class="aud-toggle__track" aria-hidden="true"><span class="aud-toggle__knob"></span></span>' +
        '<span class="aud-toggle__side" data-aud="sisters">' + esc(name("sisters")) + "</span>");
      b.type = "button";
      b.setAttribute("role", "switch");
      b.setAttribute("aria-label", "Show " + name("sisters").toLowerCase() + "' articles and videos");
      b.addEventListener("click", function (e) {
        var side = e.target.closest(".aud-toggle__side");
        setAudience(side ? side.dataset.aud : audience === "sisters" ? "brothers" : "sisters");
      });
      mount.textContent = "";
      mount.appendChild(b);
      return b;
    }).filter(Boolean);

    function sync() {
      switches.forEach(function (b) { b.setAttribute("aria-checked", String(audience === "sisters")); });
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
    setText("testimonies-heading", data.heading);
    emphasiseLastWord("testimonies-heading");

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

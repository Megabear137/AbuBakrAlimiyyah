/* =====================================================================
   main.js - loads content/*.json and renders every data-driven section.
   Everything on the page comes from those six files; edit them, not
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
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
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
    // The small line over the title (the masjid's name); empty hides it.
    var kicker = slot("hero-kicker");
    if (kicker) kicker.textContent = hero.kicker || "";
    setText("hero-subtitle", hero.subtitle);

    // One word of the title can be set apart - `titleEmphasis` (italic; gold in
    // light mode, where in dark the whole title is gold).
    var title = slot("hero-title");
    if (title && hero.title) {
      // The rest of the title, around the emphasis, is its own span.
      var html = esc(hero.title), em = hero.titleEmphasis ? esc(hero.titleEmphasis) : "";
      var at = em ? html.indexOf(em) : -1;
      if (at >= 0) {
        var rest = function (t) { t = t.trim(); return t ? '<span class="hero__rest">' + t + "</span>" : ""; };
        html = rest(html.slice(0, at)) + "<em>" + em + "</em>" + rest(html.slice(at + em.length));
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
    // A second, cream button beside it (the bookstore); null hides it.
    var two = hero.ctaSecondary;
    if (two && two.label && two.href) {
      var b = el("a", "btn btn--cream", esc(two.label) + " " + ICONS.arrow);
      b.href = two.href;
      mount.appendChild(b);
    }
  }

  /* ----------------------------- program ---------------------------- */
  function renderProgram(data) {
    if (data.hero) renderHero(data.hero);
    if (data.introduction) {
      setText("intro-kicker", data.introduction.kicker);
      setText("intro-label", data.introduction.label);
      setText("intro-body", data.introduction.body);
    }
    if (data.details) {
      setText("details-kicker", data.details.kicker);
      setText("details-heading", data.details.heading);
    }
    renderDetails(data.fees, data.timings);
    renderFooter(data.footer);
  }

  // Details: newspaper columns, one per track (its years, its fee with the
  // currency sign raised small, its class times on dotted leaders), and the
  // family discounts beneath as large percentages. fees.tiers and
  // timings.groups are paired by label (else by position); a tier with no
  // group still gets a column. design/canvas-details-style/round-2.html, option 11 (Gazette).
  function renderDetails(fees, timings) {
    var mount = slot("details");
    if (!mount) return;
    mount.textContent = "";
    fees = fees || {};
    timings = timings || {};

    var groups = timings.groups || [], tiers = fees.tiers || [], used = [];
    function labelled(list, label) {
      for (var i = 0; i < list.length; i++) if (list[i] && list[i].label === label) return i;
      return -1;
    }
    var tracks = groups.map(function (g, i) {
      var k = labelled(tiers, g.label);
      if (k < 0 && tiers[i] && !used[i] && labelled(groups, tiers[i].label) < 0) k = i;
      if (k >= 0) used[k] = true;
      return { label: g.label, years: g.years, rows: g.rows || [], tier: tiers[k] };
    });
    tiers.forEach(function (t, k) { if (!used[k]) tracks.push({ label: t.label, rows: [], tier: t }); });

    // "$125" -> a small raised "$" before "125"; anything without a figure as is.
    function price(amount) {
      var m = /^([^\d\s]*)\s*(\d.*)$/.exec(String(amount || ""));
      return m && m[1] ? '<span class="track__cur">' + esc(m[1]) + "</span>" + esc(m[2]) : esc(amount);
    }

    if (tracks.length) {
      var cols = el("div", "tracks__cols");
      tracks.forEach(function (t) {
        var tier = t.tier || {}, html = "";
        if (t.years) html += '<p class="track__years">' + esc(t.years) + "</p>";
        html += '<h3 class="track__name">' + esc(t.label) + "</h3>";
        if (tier.amount) {
          html += '<p class="track__fee"><span class="track__amt">' + price(tier.amount) + "</span>" +
            '<span class="track__per">' + [tier.period, tier.note].filter(Boolean).map(esc).join("<br>") + "</span></p>";
        }
        if (t.rows.length) {
          html += '<ul class="track__rows">' + t.rows.map(function (row) {
            return "<li><span>" + esc(row.days) + '</span><i aria-hidden="true"></i><span>' + esc(row.time) + "</span></li>";
          }).join("") + "</ul>";
        }
        cols.appendChild(el("article", "track", html));
      });
      mount.appendChild(cols);
    }

    // The percentage is drawn above its count but read after it.
    var d = fees.discounts;
    if (d && d.rows && d.rows.length) {
      var disc = el("div", "tracks__disc", '<h3 class="tracks__disc-label">' + esc(d.label || "Family discounts") + "</h3>");
      var list = el("ul", "tracks__pcts");
      d.rows.forEach(function (row) {
        var m = /^\s*(\d+(?:\.\d+)?\s*%)\s*(.*)$/.exec(String(row.value || ""));
        list.appendChild(el("li", "", "<b>" + esc(row.count) + "</b>" + (m
          ? '<span class="tracks__pct">' + esc(m[1]) + '</span><span class="tracks__off">' + esc(m[2]) + "</span>"
          : '<span class="tracks__off">' + esc(row.value) + "</span>")));
      });
      disc.appendChild(list);
      mount.appendChild(disc);
    }

    // Optional enrolment link - set `cta` in program.json when ready.
    if (fees.cta && fees.cta.href && fees.cta.label) {
      var p = el("p", "tracks__cta");
      var a = el("a", "btn btn--gold", esc(fees.cta.label) + " " + ICONS.arrow);
      a.href = fees.cta.href;
      p.appendChild(a);
      mount.appendChild(p);
    }
    mount.hidden = !mount.firstChild;
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
  // A mosaic of cards in the order of the list; a card spans its teacher's
  // width in columns (1-4) and height in rows (1-3), one of each by default.
  // A card bigger than one cell is set like the lead (larger name, ruled bio);
  // one two or more wide may set its bio beside the name (bioBeside).
  function renderTeachers(data) {
    var mount = slot("teachers");
    if (!mount) return;
    setText("teachers-heading", data.heading);
    setText("teachers-kicker", data.kicker);
    mount.textContent = "";

    // The cards don't link: teacher.html isn't opened from the home page.
    (data.teachers || []).forEach(function (t) {
      var w = span(t.width, 4), h = span(t.height, 3);
      var card = el("article", "teacher" + (w > 1 ? " teacher--w" + w : "") + (h > 1 ? " teacher--h" + h : "") +
        (w > 1 || h > 1 ? " teacher--lead" : "") + (w > 1 && t.bioBeside ? " teacher--beside" : "") +
        (isTodo(t.name) ? " teacher--todo" : ""));
      // The card is a size container; its inner box is what the CSS lays out
      // (the name block beside the bio, or above it, by the card's width).
      var inner = el("div", "teacher__in"), head = el("div", "teacher__head");
      if (t.honorific) head.appendChild(el("p", "teacher__honorific", esc(t.honorific)));
      head.insertAdjacentHTML("beforeend", linkedTitle("h3", "teacher__name", t.name, ""));
      inner.appendChild(head);
      if (t.bio) inner.appendChild(el("p", "teacher__bio", esc(t.bio)));
      card.appendChild(inner);
      mount.appendChild(card);
    });
  }
  window.renderTeachers = renderTeachers;

  // A whole number of grid tracks, from 1 up to max.
  function span(n, max) {
    n = Math.round(+n) || 1;
    return Math.min(Math.max(n, 1), max);
  }

  /* ------------------------ articles & videos ----------------------- */
  // The articles hold a brothers' and a sisters' list, chosen by the switch in
  // their head; the videos are one list. The choice is remembered per viewer,
  // and the page works without storage.
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

  // An article opens on its own page (article.html, by its id) unless its
  // href sends it somewhere else.
  function articleHref(a) {
    return a.href || (a.id ? "article.html?id=" + encodeURIComponent(a.id) : "");
  }

  // Articles: the featured one on top - a board panel and the article beside
  // it - and beneath it a carousel of every article, the featured one marked;
  // clicking a card features it. Returns a handle with destroy(), like a carousel.
  function renderArticles(mount, items, label) {
    var n = items.length;
    var at = 0;
    var feature = el("div", "slider");
    var art = el("div", "slider__art board", ICONS.book);
    var body = el("div", "slider__body");
    body.setAttribute("aria-live", "polite");
    feature.append(art, body);
    mount.appendChild(feature);

    var cards = [];
    var carousel = null;
    if (n > 1) {
      var list = el("div", "slider__list");
      mount.appendChild(list);
      carousel = createCarousel({
        mount: list,
        items: items,
        label: label,
        perView: function () { var w = window.innerWidth; return w < 560 ? 1 : w < 880 ? 2 : w < 1200 ? 3 : 4; },
        render: function (a, j) {
          var card = el("button", "slider__card board" + (j % 2 ? " board--rust" : ""),
            "<b>" + pad(j + 1) + "</b>" +
            (a.subject ? "<em>" + esc(a.subject) + "</em>" : "") +
            "<span>" + esc(a.title) + "</span>");
          card.type = "button";
          card.setAttribute("aria-label", "Show article " + (j + 1) + ": " + a.title);
          card.addEventListener("click", function () {
            show(j);
            // On a phone the featured article may be scrolled away above the cards.
            if (feature.getBoundingClientRect().top < 0) {
              var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
              feature.scrollIntoView({ block: "start", behavior: still ? "auto" : "smooth" });
            }
          });
          cards.push(card);
          return card;
        }
      });
    }

    function show(i) {
      at = i;
      var a = items[at];
      var href = articleHref(a);
      body.innerHTML =
        '<div class="slider__tags">' +
          (a.subject ? '<span class="chip">' + esc(a.subject) + "</span>" : "") +
          (a.readMinutes ? "<span>" + esc(a.readMinutes) + " min read</span>" : "") +
          (n > 1 ? '<span class="slider__count">' + pad(at + 1) + " / " + pad(n) + "</span>" : "") +
        "</div>" +
        linkedTitle("h3", "slider__title", a.title, href) +
        (a.author ? '<p class="slider__by">' + esc(a.author) + "</p>" : "") +
        (a.excerpt ? '<p class="slider__text">' + esc(a.excerpt) + "</p>" : "") +
        (href ? '<a class="btn btn--gold" href="' + esc(href) + '" tabindex="-1" aria-hidden="true">Read article ' + ICONS.arrow + "</a>" : "");
      body.classList.remove("media-swap");
      void body.offsetWidth;               // restart the animation
      body.classList.add("media-swap");
      cards.forEach(function (c, j) { c.setAttribute("aria-current", j === at ? "true" : "false"); });
    }

    show(0);
    return {
      destroy: function () {
        if (carousel) carousel.destroy();
        mount.textContent = "";
      }
    };
  }

  // Videos: a carousel of wide cards, the caption beneath the picture.
  // Without a picture, alternate the masjid photo and a plain board.
  function videoArt(v, i) {
    return picture(v) ? "" : i % 2 ? " board" + (i % 4 === 3 ? " board--rust" : "") : " vid__art--photo";
  }

  // The picture: the thumbnail given, else a YouTube video's own. YouTube's
  // hqdefault always exists but is 480px and letterboxed (the cover crop
  // trims the bars); maxresdefault is sharper but missing on some videos,
  // where YouTube answers with a 120×90 grey stand-in, so it is tried first
  // and used only if it loads larger than that.
  var YOUTUBE = /^https?:\/\/(?:www\.|m\.)?(?:youtube\.com\/(?:watch\?(?:[^#]*&)?v=|embed\/|shorts\/|live\/)|youtu\.be\/)([\w-]{11})/i;
  var sharp = {};  // YouTube id → the sharpest picture found so far

  function youtubeId(href) {
    var m = String(href || "").trim().match(YOUTUBE);
    return m ? m[1] : "";
  }

  function picture(v) {
    if (v.thumbnail) return v.thumbnail;
    var id = youtubeId(v.href);
    return id ? sharp[id] || "https://i.ytimg.com/vi/" + id + "/hqdefault.jpg" : "";
  }

  // Shows v's picture on `node`, swapping in the sharper one when it arrives.
  function paint(node, v) {
    var src = picture(v);
    node.style.backgroundImage = src ? "url(" + JSON.stringify(src) + ")" : "";
    var id = !v.thumbnail && youtubeId(v.href);
    if (!id || sharp[id]) return;
    var was = node.style.backgroundImage;
    var big = new Image();
    big.onload = function () {
      if (big.naturalWidth <= 120) return;
      sharp[id] = big.src;
      // Only if the node still shows this video (the popup's poster is reused).
      if (node.style.backgroundImage === was) node.style.backgroundImage = "url(" + JSON.stringify(big.src) + ")";
    };
    big.src = "https://i.ytimg.com/vi/" + id + "/maxresdefault.jpg";
  }

  // A card plays its video in the popup when its href is one the popup can
  // play, or when it has none yet; any other href is a plain link.
  function videoCard(v, i) {
    var card = el("article", "vid");
    var thumb = el("div", "vid__art" + videoArt(v, i),
      '<span class="vid__play">' + ICONS.play + "</span>" +
      (v.duration ? '<span class="vid__time">' + esc(v.duration) + "</span>" : ""));
    paint(thumb, v);
    card.appendChild(thumb);
    if (v.href && !playable(v.href)) {
      card.insertAdjacentHTML("beforeend", linkedTitle("h3", "vid__title", v.title, v.href));
    } else {
      var title = el("h3", "vid__title");
      var play = el("button", "stretched", esc(v.title));
      play.type = "button";
      play.setAttribute("aria-haspopup", "dialog");
      play.addEventListener("click", function () { openVideo(v, i, thumb, play); });
      title.appendChild(play);
      card.appendChild(title);
    }
    return card;
  }

  /* --------------------------- video popup -------------------------- */
  // A video plays over the page: its card's picture grows out of the
  // carousel into a large frame on the dimmed ground, the caption beneath
  // it, and goes back into the card on close (option 4 of design/canvas-video/).
  // YouTube and Vimeo links play in their own player, a video file in the
  // browser's; a video without an href shows its picture.
  function playable(href) {
    var s = String(href || "").trim();
    var id = youtubeId(s);
    if (id) return { frame: "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0" };
    var m = s.match(/^https?:\/\/(?:www\.|player\.)?vimeo\.com\/(?:video\/)?(\d+)/i);
    if (m) return { frame: "https://player.vimeo.com/video/" + m[1] + "?autoplay=1" };
    if (/^(?!javascript:)[^<>"]+\.(mp4|webm|ogv|m4v)([?#].*)?$/i.test(s)) return { file: s };
    return null;
  }

  var player = null;   // the popup's elements, built on first use
  var playing = null;  // what it shows: { v, art, opener }
  var still = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  function buildPlayer() {
    var root = el("div", "vp");
    root.hidden = true;
    root.innerHTML =
      '<div class="vp__scrim" data-vp-close></div>' +
      '<div class="vp__box" role="dialog" aria-modal="true" aria-labelledby="vp-title">' +
        '<button class="round vp__close" type="button" data-vp-close aria-label="Close video">' + ICONS.close + "</button>" +
        '<div class="vp__frame"><div class="vp__poster"><span class="vid__play">' + ICONS.play + "</span></div></div>" +
        '<div class="vp__cap"><h2 class="vp__title" id="vp-title"></h2>' +
        '<p class="vp__meta"></p></div>' +
      "</div>";
    document.body.appendChild(root);
    root.addEventListener("click", function (e) {
      if (e.target.closest("[data-vp-close]")) closeVideo();
    });
    document.addEventListener("keydown", function (e) {
      if (playing && e.key === "Escape") closeVideo();
    });
    return {
      root: root,
      frame: root.querySelector(".vp__frame"),
      poster: root.querySelector(".vp__poster"),
      close: root.querySelector(".vp__close"),
      inert: []
    };
  }

  // Grows the frame out of `rect` (a card's picture), or shrinks it back into
  // it; calls `done` at once when there is nothing on screen to fly from.
  function fly(rect, back, done) {
    var to = player.frame.getBoundingClientRect();
    if (still || !rect || !rect.width || rect.bottom < 0 || rect.top > window.innerHeight || !player.frame.animate) {
      done(false);
      return;
    }
    var from = "translate(" + (rect.left - to.left) + "px, " + (rect.top - to.top) + "px) " +
      "scale(" + rect.width / to.width + ", " + rect.height / to.height + ")";
    var steps = [{ transform: from }, { transform: "none" }];
    var anim = player.frame.animate(back ? steps.reverse() : steps,
      { duration: back ? 320 : 520, easing: "cubic-bezier(0.2, 0.8, 0.2, 1)", fill: "both" });
    anim.onfinish = function () { done(true); anim.cancel(); };
  }

  function openVideo(v, i, art, opener) {
    if (playing || (player && !player.root.hidden)) return;
    player = player || buildPlayer();
    var rect = art.getBoundingClientRect();
    playing = { v: v, art: art, opener: opener };

    player.poster.className = "vp__poster" + videoArt(v, i);
    paint(player.poster, v);
    player.root.querySelector(".vp__title").textContent = v.title || "";
    player.root.querySelector(".vp__meta").textContent = v.duration || "";

    // The rest of the page is out of reach while the popup is open.
    player.inert = Array.prototype.filter.call(document.body.children, function (n) {
      return n !== player.root && !n.inert;
    });
    player.inert.forEach(function (n) { n.inert = true; });
    document.documentElement.classList.add("vp-lock");
    player.root.classList.remove("vp--closing", "vp--fading");
    player.root.hidden = false;
    player.close.focus({ preventScroll: true });

    // The player goes in once the frame has landed, so the picture is what flies.
    var src = playable(v.href);
    fly(rect, false, function () {
      if (!src || playing === null || playing.v !== v) return;
      var media;
      if (src.frame) {
        media = el("iframe", "vp__media");
        media.src = src.frame;
        media.title = v.title || "Video";
        media.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
        media.allowFullscreen = true;
        media.referrerPolicy = "strict-origin-when-cross-origin";
      } else {
        media = el("video", "vp__media");
        media.src = src.file;
        media.controls = true;
        media.autoplay = true;
        media.playsInline = true;
      }
      player.frame.appendChild(media);
    });
  }

  function closeVideo() {
    if (!playing) return;
    var was = playing;
    playing = null;
    var media = player.frame.querySelector(".vp__media");
    if (media) media.remove();                 // stops it; the picture flies back
    player.root.classList.add("vp--closing");

    function hide() {
      player.root.hidden = true;
      player.root.classList.remove("vp--closing", "vp--fading");
      player.inert.forEach(function (n) { n.inert = false; });
      player.inert = [];
      document.documentElement.classList.remove("vp-lock");
      if (was.opener.isConnected) was.opener.focus({ preventScroll: true });
    }
    if (still) { hide(); return; }
    fly(was.art.isConnected ? was.art.getBoundingClientRect() : null, true, function (flew) {
      if (flew) { hide(); return; }
      player.root.classList.add("vp--fading");  // the card is off screen: fade out instead
      setTimeout(hide, 220);
    });
  }

  // The carousels of the last renderMedia, destroyed when it runs again (the
  // videos editor redraws with it). `only` shows that library of articles
  // instead of the remembered one. Returns each section's current handle by key.
  var mediaSections = [];

  function renderMedia(data, only) {
    var names = data.audiences || {};
    var audience = only || savedAudience();
    var handles = {};
    mediaSections.forEach(function (s) { if (s.handle) s.handle.destroy(); });

    // `render` fills the mount and returns a handle to destroy on the next swap.
    // A section with `split` keeps a list per audience; the others keep `items`.
    var sections = [
      { key: "articles", noun: "articles", split: true, render: renderArticles },
      {
        key: "videos", noun: "videos",
        render: function (mount, items, label) {
          return createCarousel({
            mount: mount,
            items: items,
            label: label,
            perView: function () { return window.innerWidth < 700 ? 1 : 2; },
            render: videoCard
          });
        }
      }
    ].filter(function (s) { return data[s.key] && slot(s.key); });
    mediaSections = sections;

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

      var items = (s.split ? data[s.key][audience] : data[s.key].items) || [];
      var label = s.split ? name(audience) + "' " + s.noun : s.noun.charAt(0).toUpperCase() + s.noun.slice(1);
      if (items.length) {
        s.handle = s.render(mount, items, label);
      } else {
        mount.appendChild(el("p", "media-empty", "No " + esc(label.toLowerCase()) + " yet."));
      }

      handles[s.key] = s.handle;

      if (swap) {
        mount.classList.remove("media-swap");
        void mount.offsetWidth;            // restart the animation
        mount.classList.add("media-swap");
      }
    }

    // A two-button segmented control in each head; the pressed side is the library shown.
    var groups = sections.map(function (s) {
      var mount = s.split && slot(s.key + "-audience");
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
      sections.forEach(function (s) { if (s.split) build(s, true); });
    }

    sync();
    sections.forEach(function (s) { build(s, false); });
    return handles;
  }
  window.renderMedia = renderMedia;

  /* --------------------------- testimonies -------------------------- */
  // Calling it again replaces the carousel; it returns the carousel's handle.
  var testimoniesCarousel = null;

  function renderTestimonies(data) {
    var mount = slot("testimonies");
    if (!mount) return null;
    setText("testimonies-kicker", data.kicker);
    setText("testimonies-heading", data.heading);

    if (testimoniesCarousel) testimoniesCarousel.destroy();
    testimoniesCarousel = createCarousel({
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

    // The way to graduates.html under the niches; a null `cta` hides it.
    var ctaSlot = slot("testimonies-cta");
    if (ctaSlot) {
      ctaSlot.textContent = "";
      var cta = data.cta;
      ctaSlot.hidden = !(cta && cta.label && cta.href);
      if (!ctaSlot.hidden) {
        var a = el("a", "btn btn--gold", esc(cta.label) + " " + ICONS.arrow);
        a.href = cta.href;
        ctaSlot.appendChild(a);
      }
    }
    return testimoniesCarousel;
  }
  window.renderTestimonies = renderTestimonies;

  /* ------------------------------ boot ------------------------------ */
  var yearSlot = slot("year");
  if (yearSlot) yearSlot.textContent = String(new Date().getFullYear());

  Promise.all([
    loadJSON("content/program.json").then(renderProgram),
    loadJSON("content/curriculum.json").then(function (data) {
      setText("curriculum-label", data.label);
      setText("curriculum-kicker", data.kicker);
      setText("curriculum-hint", data.hint);
      setText("curriculum-hint-touch", data.hintTouch);
      renderCurriculum(slot("curriculum"), data);
    }),
    loadJSON("content/teachers.json").then(renderTeachers),
    // bookstore.js draws the featured books; it loads before this file.
    loadJSON("content/bookstore.json").then(function (data) {
      if (window.renderBookstore) window.renderBookstore(data, false);
    }),
    loadJSON("content/media.json").then(renderMedia),
    loadJSON("content/testimonies.json").then(renderTestimonies)
  ]).catch(function (err) {
    console.error("Content failed to load.", err);
    var banner = el("p", "",
      "Content could not be loaded. If you opened this file directly, serve the folder over " +
      "a local web server instead (see CLAUDE.md).");
    banner.style.cssText = "padding:8rem 1rem 2rem;text-align:center;color:#8a2b2b";
    document.getElementById("main").prepend(banner);
  }).then(function () {
    // Drawn (or failed): splash.js lifts the loading splash.
    document.dispatchEvent(new Event("content:ready"));
  });
})();

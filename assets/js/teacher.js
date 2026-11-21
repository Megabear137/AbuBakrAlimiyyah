/* =====================================================================
   teacher.js - fills teacher.html: one teacher from content/teachers.json,
   found by the ?id= in the address, their biography, and beneath it the
   other teachers as the home page's cards. The footer's contact lines
   come from program.json.
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

  // As main.js links them: a teacher with an id has a page; a placeholder doesn't.
  function teacherHref(t) {
    return t.id && !isTodo(t.name) ? "teacher.html?id=" + encodeURIComponent(t.id) : "";
  }

  // The formatting a paragraph may carry: **bold**, _italic_ and
  // [words](address); a backslash keeps \\ * _ [ ] as they are. Everything
  // else is escaped. The same as article.js's; keep the two in step.
  var LINK = /^\[((?:\\.|[^\\\]])*)\]\(([^()\s]+)\)/;
  function safeHref(u) { return !/^[a-z][a-z0-9+.-]*:/i.test(u) || /^(https?|mailto|tel):/i.test(u); }
  function inline(s) {
    s = String(s == null ? "" : s);
    var out = "", open = [], i = 0, m;
    function toggle(tag) {
      var at = open.lastIndexOf(tag);
      if (at < 0) { open.push(tag); out += "<" + tag + ">"; return; }
      var inner = open.splice(at);
      for (var k = inner.length - 1; k >= 0; k--) out += "</" + inner[k] + ">";
      inner.slice(1).forEach(function (t) { open.push(t); out += "<" + t + ">"; });
    }
    while (i < s.length) {
      var c = s.charAt(i);
      if (c === "\\" && /[\\*_\[\]]/.test(s.charAt(i + 1))) { out += esc(s.charAt(i + 1)); i += 2; }
      else if (s.substr(i, 2) === "**") { toggle("strong"); i += 2; }
      else if (c === "_") { toggle("em"); i += 1; }
      else if (c === "[" && (m = LINK.exec(s.slice(i))) && safeHref(m[2])) {
        out += '<a href="' + esc(m[2]) + '">' + inline(m[1]) + "</a>";
        i += m[0].length;
      }
      else { out += esc(c); i += 1; }
    }
    while (open.length) out += "</" + open.pop() + ">";
    return out;
  }

  /* ----------------------------- the teacher ---------------------------- */
  function renderTeacher(t) {
    document.title = [t.honorific, t.name].filter(Boolean).join(" ") + " — Jāmiʿah Islāmiyah Abū Bakr";
    slot("teacher-honorific").textContent = t.honorific || "";
    slot("teacher-name").textContent = t.name;
    slot("teacher-bio").textContent = t.bio || "";

    // The biography: a string is a paragraph, {heading} a section heading.
    var mount = slot("teacher-body");
    (t.body || []).forEach(function (block) {
      if (typeof block === "string") mount.appendChild(el("p", "", inline(block)));
      else if (block && block.heading) mount.appendChild(el("h2", "", esc(block.heading)));
    });
    slot("teacher-read").hidden = !mount.children.length;
  }

  // The other teachers, in their order, as the mosaic's small cards.
  function renderOthers(data, current) {
    var mount = slot("teacher-cards");
    var others = (data.teachers || []).filter(function (t) { return t !== current; });
    if (!others.length) return;
    if (data.heading) slot("teachers-heading").textContent = data.heading;
    others.forEach(function (t) {
      var href = teacherHref(t);
      var card = el("article", "teacher" + (isTodo(t.name) ? " teacher--todo" : "") + (href ? " teacher--link" : ""));
      // The mosaic's markup (main.js): the inner box, the name block, the bio.
      var inner = el("div", "teacher__in"), head = el("div", "teacher__head");
      if (t.honorific) head.appendChild(el("p", "teacher__honorific", esc(t.honorific)));
      head.appendChild(el("h3", "teacher__name",
        href ? '<a class="stretched" href="' + esc(href) + '">' + esc(t.name) + "</a>" : esc(t.name)));
      inner.appendChild(head);
      if (t.bio) inner.appendChild(el("p", "teacher__bio", esc(t.bio)));
      card.appendChild(inner);
      mount.appendChild(card);
    });
    slot("teacher-more").hidden = false;
  }

  function notFound() {
    slot("teacher-name").textContent = "Teacher not found";
    slot("teacher-bio").textContent = "This page may have been moved or taken down.";
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

  /* -------------------------------- boot -------------------------------- */
  var yearSlot = slot("year");
  if (yearSlot) yearSlot.textContent = String(new Date().getFullYear());

  var id = new URLSearchParams(location.search).get("id");

  Promise.all([
    loadJSON("content/teachers.json").then(function (data) {
      var hit = null;
      (data.teachers || []).forEach(function (t) { if (!hit && id && t.id === id && !isTodo(t.name)) hit = t; });
      if (!hit) return notFound();
      renderTeacher(hit);
      renderOthers(data, hit);
    }),
    loadJSON("content/program.json").then(function (data) { renderFooter(data.footer); })
  ]).catch(function (err) {
    console.error("Content failed to load.", err);
    slot("teacher-name").textContent = "Teachers";
    slot("teacher-bio").textContent =
      "The teacher could not be loaded. If you opened this file directly, serve the folder over " +
      "a local web server instead (see CLAUDE.md).";
  });
})();

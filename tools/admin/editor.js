/* =====================================================================
   editor.js - the article editor. Only tools/admin_server.py serves this
   file and only it adds the tag that loads it to article.html, so the
   public site never carries it. "Edit article" turns the page itself into
   the editor: the title, the excerpt and every block of the body become
   editable where they stand, a bar along the foot of the screen formats
   and saves, and a side panel holds the article's other fields and the
   list of articles. Saving writes the articles of content/media.json
   through the server; nothing is written until Save.
   ===================================================================== */
(function () {
  "use strict";

  var API = "/__admin/articles";
  var ID_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
  var QUOTE_ICON = '<svg viewBox="0 0 40 32" fill="currentColor" aria-hidden="true"><path d="M0 32V19C0 8 6 1.5 16 0l1.6 4C11.6 5.8 9 9.4 8.8 14H16v18H0zm22 0V19C22 8 28 1.5 38 0l1.6 4C33.6 5.8 31 9.4 30.8 14H38v18H22z"/></svg>';
  var TYPES = { p: "Paragraph", h: "Heading", quote: "Quotation" };

  var slot = function (name) { return document.querySelector('[data-slot="' + name + '"]'); };

  var store = null;      // {version, articles} as last loaded or saved
  var lists = [];        // the names of the article lists: brothers, sisters
  var current = null;    // the article being edited (an object inside store)
  var dirty = false;
  var ui = {};

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

  /* ------------------------ formatting, both ways ----------------------- */
  // Markup to HTML: the same as inline() in assets/js/article.js; keep the
  // two in step. **bold**, _italic_, [words](address), and a backslash
  // before \ * _ [ ] to keep it as it is.
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

  // HTML (as the browser's editing leaves it) back to markup. Bold and
  // italic are read from the tags or from inline styles, a style already
  // in force isn't opened twice, and anything else is reduced to its text.
  function escMark(t) { return t.replace(/[\\*_\[\]]/g, "\\$&"); }
  function toMarkup(node, ctx) {
    ctx = ctx || {};
    var out = "";
    Array.prototype.forEach.call(node.childNodes, function (n) {
      if (n.nodeType === 3) { out += escMark(n.nodeValue.replace(/\u00a0/g, " ")); return; }
      if (n.nodeType !== 1) return;
      if (n.tagName === "BR") { out += " "; return; }
      var st = n.style || {};
      var bold = !ctx.bold && (/^(B|STRONG)$/.test(n.tagName) || /^(bold|[6-9]00)$/.test(st.fontWeight));
      var ital = !ctx.ital && (/^(I|EM)$/.test(n.tagName) || st.fontStyle === "italic");
      var href = !ctx.link && n.tagName === "A" && n.getAttribute("href");
      var inner = toMarkup(n, { bold: ctx.bold || bold, ital: ctx.ital || ital, link: ctx.link || !!href });
      if (!inner.trim()) { out += inner; return; }
      if (href) inner = "[" + inner + "](" + href.replace(/[()\s]/g, function (c) {
        return c === "(" ? "%28" : c === ")" ? "%29" : "%20";
      }) + ")";
      if (ital) inner = "_" + inner + "_";
      if (bold) inner = "**" + inner + "**";
      out += inner;
    });
    return out;
  }
  function markupOf(field) { return toMarkup(field).replace(/\s+/g, " ").trim(); }
  function textOf(field) { return field.textContent.replace(/\s+/g, " ").trim(); }

  /* ------------------------------- carets ------------------------------- */
  function caretTo(field, atEnd) {
    field.focus();
    var r = document.createRange();
    r.selectNodeContents(field);
    r.collapse(!atEnd);
    var s = getSelection();
    s.removeAllRanges();
    s.addRange(r);
  }

  function caretAtStart(field) {
    var s = getSelection();
    if (!s.rangeCount || !s.isCollapsed || !field.contains(s.anchorNode)) return false;
    var r = document.createRange();
    r.selectNodeContents(field);
    r.setEnd(s.anchorNode, s.anchorOffset);
    return r.toString() === "";
  }

  // Cuts everything from the caret to the end of the field, keeping its
  // formatting, and returns it.
  function cutToEnd(field) {
    var r = getSelection().getRangeAt(0);
    r.deleteContents();
    var tail = document.createRange();
    tail.setStart(r.startContainer, r.startOffset);
    tail.setEnd(field, field.childNodes.length);
    return tail.extractContents();
  }

  function activeField() {
    var s = getSelection();
    return fieldOf(s.rangeCount ? s.anchorNode : null);
  }

  /* ------------------------------ the data ------------------------------ */
  function listOf(a) {
    for (var i = 0; i < lists.length; i++) {
      if (store.articles[lists[i]].indexOf(a) >= 0) return lists[i];
    }
    return null;
  }

  function findById(id) {
    for (var i = 0; i < lists.length; i++) {
      var hit = store.articles[lists[i]].filter(function (a) { return a.id === id; })[0];
      if (hit) return hit;
    }
    return null;
  }

  function allArticles() {
    return lists.reduce(function (all, name) { return all.concat(store.articles[name]); }, []);
  }

  function uniqueId(base) {
    base = base || "article";
    var id = base, n = 2;
    while (allArticles().some(function (a) { return a !== current && a.id === id; })) id = base + "-" + n++;
    return id;
  }

  function slugify(s) {
    return String(s).toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60).replace(/-+$/, "");
  }

  function load() {
    return fetch(API, { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }).then(function (d) {
      store = d;
      lists = Object.keys(d.articles).filter(function (k) { return Array.isArray(d.articles[k]); });
    });
  }

  function setDirty() {
    if (!dirty) { dirty = true; status("Unsaved changes"); }
  }

  function status(text, bad) {
    ui.status.textContent = text;
    ui.status.classList.toggle("adm-status--bad", !!bad);
  }

  /* ------------------------------- blocks ------------------------------- */
  // Plain fields take no formatting; a browser without plaintext-only
  // (Firefox before 136) gets an ordinary one, and Ctrl+B is refused there.
  function editable(f, rich) {
    try { f.contentEditable = rich ? "true" : "plaintext-only"; } catch (e) { f.contentEditable = "true"; }
  }

  function fieldOf(node) {
    node = node && (node.nodeType === 1 ? node : node.parentNode);
    return node && node.closest ? node.closest(".adm-field") : null;
  }

  function field(tag, rich, placeholder, content) {
    var f = el(tag, "adm-field " + (rich ? "adm-rich" : "adm-plain"));
    editable(f, rich);
    f.setAttribute("data-ph", placeholder);
    f.spellcheck = true;
    if (rich) f.innerHTML = content || ""; else f.textContent = content || "";
    return f;
  }

  // One block of the body: its tools, then the element as article.js
  // draws it, made editable. `block` is the JSON: a string, {heading} or
  // {quote, source}.
  function makeBlock(block) {
    var type = typeof block === "string" ? "p" : block && "heading" in block ? "h" : "quote";
    var wrap = el("div", "adm-block");
    wrap.dataset.type = type;

    var tools = el("div", "adm-block__tools");
    tools.contentEditable = "false";
    Object.keys(TYPES).forEach(function (t) {
      tools.appendChild(toolButton("type-" + t, t === "p" ? "¶" : t === "h" ? "H" : "❝",
        "Make this a " + TYPES[t].toLowerCase(), t === type));
    });
    tools.appendChild(toolButton("up", "↑", "Move up"));
    tools.appendChild(toolButton("down", "↓", "Move down"));
    tools.appendChild(toolButton("remove", "✕", "Delete this block"));
    wrap.appendChild(tools);

    if (type === "p") {
      wrap.appendChild(field("p", true, "Write a paragraph…", inline(block)));
    } else if (type === "h") {
      wrap.appendChild(field("h2", false, "Section heading", block.heading));
    } else {
      var q = el("blockquote", "", QUOTE_ICON);
      q.appendChild(field("p", true, "The quotation…", inline(block.quote)));
      q.appendChild(field("cite", false, "Source (optional)", block.source));
      wrap.appendChild(q);
    }
    return wrap;
  }

  function toolButton(act, label, title, pressed) {
    var b = el("button", "adm-tool", label);
    b.type = "button";
    b.dataset.act = act;
    b.title = title;
    b.setAttribute("aria-label", title);
    if (pressed != null) b.setAttribute("aria-pressed", String(pressed));
    return b;
  }

  function mainField(wrap) { return wrap.querySelector(".adm-field"); }
  function blocks() { return Array.prototype.slice.call(ui.body.querySelectorAll(":scope > .adm-block")); }

  function readBlock(wrap) {
    var f = mainField(wrap);
    if (wrap.dataset.type === "p") return markupOf(f) || null;
    if (wrap.dataset.type === "h") return textOf(f) ? { heading: textOf(f) } : null;
    var quote = markupOf(f), source = textOf(wrap.querySelector("cite"));
    if (!quote) return null;
    return source ? { quote: quote, source: source } : { quote: quote };
  }

  function addBlock(type, after, focus) {
    var b = makeBlock(type === "p" ? "" : type === "h" ? { heading: "" } : { quote: "" });
    if (after && after.parentNode) after.after(b); else ui.body.appendChild(b);
    if (focus !== false) caretTo(mainField(b), false);
    setDirty();
    return b;
  }

  // Changes a block's type in place, keeping its words (and a quotation's
  // source, in case it is changed back).
  function retype(wrap, type) {
    if (wrap.dataset.type === type) return;
    var f = mainField(wrap);
    var markup = wrap.dataset.type === "h" ? escMark(textOf(f)) : markupOf(f);
    var cite = wrap.querySelector("cite");
    var source = cite ? textOf(cite) : wrap.dataset.source || "";
    var next = makeBlock(type === "p" ? markup : type === "h" ? { heading: textOf(f) } : { quote: markup, source: source });
    if (source) next.dataset.source = source;
    wrap.replaceWith(next);
    caretTo(mainField(next), true);
    setDirty();
  }

  function renderBlocks(body) {
    ui.body.textContent = "";
    (body || []).forEach(function (b) { ui.body.appendChild(makeBlock(b)); });
    if (!ui.body.children.length) ui.body.appendChild(makeBlock(""));
  }

  /* ------------------------------ the page ------------------------------ */
  // Writes what is on the page into the article's JSON.
  function commit() {
    if (!current) return;
    current.title = textOf(ui.title);
    current.excerpt = textOf(ui.lede);
    current.body = blocks().map(readBlock).filter(function (b) { return b != null; });
  }

  // Subject, author and read time over the photograph, as article.js draws them.
  function paintHero() {
    var a = current;
    slot("article-subject").innerHTML = a.subject ? '<span class="chip">' + esc(a.subject) + "</span>" : "";
    var meta = [a.author, a.readMinutes ? a.readMinutes + " min read" : ""]
      .filter(Boolean)
      .map(function (s) { return "<span>" + esc(s) + "</span>"; });
    slot("article-meta").innerHTML = meta.length
      ? '<p class="meta">' + meta.join('<span class="meta__dot" aria-hidden="true"></span>') + "</p>" : "";
    document.title = "Editing: " + (textOf(ui.title) || "Untitled") + " — Jamiyah Islamiyyah Abu Bakr";
  }

  function paint() {
    ui.title.textContent = current.title || "";
    ui.lede.textContent = current.excerpt || "";
    renderBlocks(current.body);
    paintHero();
    paintPanel();
    history.replaceState(null, "", "?id=" + encodeURIComponent(current.id));
  }

  function openArticle(a) {
    commit();
    current = a;
    paint();
    window.scrollTo(0, 0);
  }

  function newArticle(list) {
    commit();
    var a = { id: "", title: "", subject: "", author: "", readMinutes: 5, excerpt: "", body: [], href: "" };
    store.articles[list || lists[0]].unshift(a);   // newest first: it becomes the featured one
    current = a;
    a.id = uniqueId("new-article");
    setDirty();
    paint();
    window.scrollTo(0, 0);
    caretTo(ui.title, true);
  }

  function deleteArticle() {
    var name = textOf(ui.title) || "this article";
    if (!confirm("Delete “" + name + "”?\n\nIt goes from media.json when you save.")) return;
    var list = store.articles[listOf(current)];
    var at = list.indexOf(current);
    list.splice(at, 1);
    current = null;
    setDirty();
    var next = list[Math.min(at, list.length - 1)] || allArticles()[0];
    if (next) openArticle(next); else newArticle(lists[0]);
  }

  function moveTo(list) {
    var from = store.articles[listOf(current)];
    from.splice(from.indexOf(current), 1);
    store.articles[list].unshift(current);
    setDirty();
    paintPanel();
  }

  function shift(by) {
    var list = store.articles[listOf(current)];
    var at = list.indexOf(current), to = at + by;
    if (to < 0 || to >= list.length) return;
    list.splice(at, 1);
    list.splice(to, 0, current);
    setDirty();
    paintPanel();
  }

  function estimateMinutes() {
    commit();
    var words = [current.title, current.excerpt].concat(current.body.map(function (b) {
      return typeof b === "string" ? b : (b.heading || b.quote || "") + " " + (b.source || "");
    })).join(" ").split(/\s+/).filter(Boolean).length;
    return Math.max(1, Math.round(words / 200));
  }

  /* ------------------------------ the panel ----------------------------- */
  function paintPanel() {
    var list = listOf(current);
    var at = store.articles[list].indexOf(current);
    var p = ui.panel;
    p.innerHTML =
      '<h2 class="adm-panel__head">Article</h2>' +
      '<label class="adm-label">Open<select data-f="open">' + lists.map(function (name) {
        return '<optgroup label="' + esc(cap(name)) + '">' + store.articles[name].map(function (a, i) {
          return '<option value="' + esc(name + ":" + i) + '"' + (a === current ? " selected" : "") + ">" +
            esc((i + 1) + ". " + ((a === current ? textOf(ui.title) : a.title) || "Untitled")) + "</option>";
        }).join("") + "</optgroup>";
      }).join("") + "</select></label>" +
      '<div class="adm-row"><button class="adm-btn" type="button" data-p="new">+ New article</button>' +
      '<button class="adm-btn adm-btn--danger" type="button" data-p="delete">Delete</button></div>' +
      '<hr class="adm-hr">' +
      '<label class="adm-label">List<select data-f="list">' + lists.map(function (name) {
        return '<option value="' + esc(name) + '"' + (name === list ? " selected" : "") + ">" + esc(cap(name)) + "</option>";
      }).join("") + "</select></label>" +
      '<div class="adm-label">Position' +
      '<div class="adm-row"><span class="adm-pos">' + (at + 1) + " of " + store.articles[list].length +
      (at === 0 ? " · featured" : "") + "</span>" +
      '<button class="adm-btn" type="button" data-p="earlier"' + (at === 0 ? " disabled" : "") + ">↑ Earlier</button>" +
      '<button class="adm-btn" type="button" data-p="later"' + (at === store.articles[list].length - 1 ? " disabled" : "") + ">↓ Later</button></div>" +
      '<small>The first is featured on the home page.</small></div>' +
      '<label class="adm-label">Subject<input data-f="subject" value="' + esc(current.subject) + '"></label>' +
      '<label class="adm-label">Author<input data-f="author" value="' + esc(current.author) + '"></label>' +
      '<div class="adm-label">Read time (minutes)<div class="adm-row">' +
      '<input data-f="readMinutes" type="number" min="0" max="999" value="' + esc(current.readMinutes == null ? "" : current.readMinutes) + '">' +
      '<button class="adm-btn" type="button" data-p="estimate">Estimate</button></div></div>' +
      '<div class="adm-label">Id (the page’s address)<div class="adm-row">' +
      '<input data-f="id" value="' + esc(current.id) + '" spellcheck="false">' +
      '<button class="adm-btn" type="button" data-p="slug">From title</button></div>' +
      '<small data-f="id-note">Links use it: keep it once published.</small></div>' +
      '<label class="adm-label">Link elsewhere<input data-f="href" value="' + esc(current.href) + '" placeholder="Leave empty">' +
      "<small>Sends the article to another address instead of its own page.</small></label>" +
      '<hr class="adm-hr">' +
      '<div class="adm-help"><b>Formatting</b> Ctrl+B bold, Ctrl+I italic, Ctrl+K link. ' +
      "Enter starts a new paragraph; Backspace at the start of one joins it to the one before. " +
      "Pasted text keeps its paragraphs but not its styling. Ctrl+S saves.</div>";
    checkId();
  }

  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

  function checkId() {
    var note = ui.panel.querySelector('[data-f="id-note"]');
    var id = current.id;
    var clash = allArticles().some(function (a) { return a !== current && a.id === id; });
    var bad = !ID_RE.test(id) ? "Lowercase letters and numbers, joined by hyphens." :
      clash ? "Another article already has this id." : "";
    note.textContent = bad || "Links use it: keep it once published.";
    note.classList.toggle("adm-bad", !!bad);
  }

  function onPanelInput(e) {
    var f = e.target.dataset.f;
    if (!f || f === "open" || f === "list") return;
    if (f === "readMinutes") {
      var n = parseInt(e.target.value, 10);
      current.readMinutes = isNaN(n) ? 0 : Math.max(0, Math.min(999, n));
    } else {
      current[f] = f === "id" ? e.target.value.trim() : e.target.value;
    }
    if (f === "id") checkId();
    paintHero();
    setDirty();
  }

  function onPanelChange(e) {
    var f = e.target.dataset.f;
    if (f === "open") {
      var parts = e.target.value.split(":");
      openArticle(store.articles[parts[0]][+parts[1]]);
    } else if (f === "list") {
      moveTo(e.target.value);
    }
  }

  function onPanelClick(e) {
    var b = e.target.closest("[data-p]");
    if (!b) return;
    var act = b.dataset.p;
    if (act === "new") newArticle(listOf(current));
    else if (act === "delete") deleteArticle();
    else if (act === "earlier") shift(-1);
    else if (act === "later") shift(1);
    else if (act === "estimate") {
      current.readMinutes = estimateMinutes();
      ui.panel.querySelector('[data-f="readMinutes"]').value = current.readMinutes;
      paintHero();
      setDirty();
    } else if (act === "slug") {
      current.id = uniqueId(slugify(textOf(ui.title)) || "article");
      ui.panel.querySelector('[data-f="id"]').value = current.id;
      checkId();
      setDirty();
    }
  }

  /* ------------------------------ formatting ---------------------------- */
  function format(cmd) {
    var f = activeField();
    if (!f || !f.classList.contains("adm-rich")) return;
    document.execCommand(cmd);
    setDirty();
    reflectFormat();
  }

  function link() {
    var f = activeField();
    if (!f || !f.classList.contains("adm-rich")) return;
    var s = getSelection();
    var range = s.getRangeAt(0).cloneRange();
    var node = s.anchorNode.nodeType === 1 ? s.anchorNode : s.anchorNode.parentNode;
    var a = node.closest("a");
    if (a && f.contains(a)) {
      var edited = prompt("Link address (leave empty to remove the link):", a.getAttribute("href"));
      if (edited == null) return;
      edited = edited.trim();
      if (!edited) {
        a.replaceWith.apply(a, Array.prototype.slice.call(a.childNodes));
      } else if (checkHref(edited)) {
        a.setAttribute("href", checkHref(edited));
      }
      setDirty();
      return;
    }
    if (s.isCollapsed) { status("Select the words to link first", true); return; }
    var url = prompt("Link address:", "https://");
    if (url == null) return;
    url = checkHref(url.trim());
    if (!url) return;
    f.focus();
    s.removeAllRanges();
    s.addRange(range);
    document.execCommand("createLink", false, url);
    setDirty();
  }

  // A bare "example.com" gains https://; javascript: and the like are refused.
  function checkHref(u) {
    if (!u || u === "https://") return "";
    if (!/^[a-z][a-z0-9+.-]*:/i.test(u) && /^[\w-]+(\.[\w-]+)+(\/|$)/.test(u)) u = "https://" + u;
    if (!safeHref(u)) { status("Only web, email and phone links are allowed", true); return ""; }
    return u;
  }

  function reflectFormat() {
    var rich = (activeField() || { classList: { contains: function () { return false; } } }).classList.contains("adm-rich");
    ["bold", "italic"].forEach(function (cmd) {
      var b = ui.bar.querySelector('[data-cmd="' + cmd + '"]');
      b.disabled = !rich;
      b.setAttribute("aria-pressed", String(rich && document.queryCommandState(cmd)));
    });
    ui.bar.querySelector('[data-cmd="link"]').disabled = !rich;
  }

  /* ------------------------------- keyboard ----------------------------- */
  function onKey(e) {
    var mod = e.ctrlKey || e.metaKey;
    var key = e.key.toLowerCase();
    if (mod && key === "s") { e.preventDefault(); save(); return; }

    var f = fieldOf(e.target);
    if (!f) return;
    if (mod && /^[biuk]$/.test(key)) {
      e.preventDefault();
      if (key === "b") format("bold");
      else if (key === "i") format("italic");
      else if (key === "k") link();
      return;
    }

    var wrap = f.closest(".adm-block");
    if (e.key === "Enter") {
      e.preventDefault();
      if (f === ui.title) caretTo(ui.lede, true);
      else if (f === ui.lede) caretTo(mainField(blocks()[0] || addBlock("p", null, false)), false);
      else if (wrap && wrap.dataset.type === "p") {
        var tail = cutToEnd(f);
        var next = addBlock("p", wrap);
        mainField(next).appendChild(tail);
        caretTo(mainField(next), false);
      } else if (f.tagName === "P") {
        caretTo(wrap.querySelector("cite"), true);        // the quotation, then its source
      } else if (wrap) {
        addBlock("p", wrap);
      }
      return;
    }

    if (e.key === "Backspace" && wrap && f === mainField(wrap) && caretAtStart(f)) {
      var prev = wrap.previousElementSibling;
      var empty = !Array.prototype.some.call(wrap.querySelectorAll(".adm-field"), function (x) { return textOf(x); });
      if (empty && prev) {
        e.preventDefault();
        wrap.remove();
        caretTo(prev.dataset.type === "quote" ? prev.querySelector("cite") : mainField(prev), true);
        setDirty();
      } else if (prev && prev.dataset.type === "p" && wrap.dataset.type === "p") {
        e.preventDefault();
        var into = mainField(prev);
        var join = document.createRange();
        join.selectNodeContents(into);
        join.collapse(false);
        while (f.firstChild) into.appendChild(f.firstChild);
        wrap.remove();
        into.focus();
        getSelection().removeAllRanges();
        getSelection().addRange(join);
        setDirty();
      }
    }
  }

  // Plain text only. Into a paragraph, each line of what is pasted becomes a
  // paragraph of its own; anywhere else the lines are run together.
  function onPaste(e) {
    var f = fieldOf(e.target);
    if (!f) return;
    e.preventDefault();
    var text = (e.clipboardData || window.clipboardData).getData("text/plain") || "";
    var wrap = f.closest(".adm-block");
    var parts = text.split(/\r?\n/).map(function (s) { return s.replace(/\s+/g, " ").trim(); }).filter(Boolean);
    if (!parts.length) return;
    if (!wrap || wrap.dataset.type !== "p" || parts.length === 1) {
      document.execCommand("insertText", false, parts.join(" "));
      return;
    }
    document.execCommand("insertText", false, parts[0]);
    var tail = cutToEnd(f), after = wrap, last = null;
    parts.slice(1).forEach(function (part) {
      after = addBlock("p", after, false);
      last = mainField(after);
      last.textContent = part;
    });
    caretTo(last, true);
    last.appendChild(tail);
    setDirty();
  }

  function onInput(e) {
    var f = fieldOf(e.target);
    if (!f) return;
    // An emptied field can keep a stray <br>, which hides its placeholder.
    if (!f.textContent && f.querySelector("br")) { f.textContent = ""; caretTo(f, true); }
    if (f === ui.title) {
      paintHero();
      var opt = ui.panel.querySelector('[data-f="open"] option:checked');
      var list = store.articles[listOf(current)];
      if (opt) opt.textContent = (list.indexOf(current) + 1) + ". " + (textOf(f) || "Untitled");
    }
    setDirty();
  }

  function onBodyClick(e) {
    var b = e.target.closest("[data-act]");
    if (!b) return;
    var wrap = b.closest(".adm-block");
    var act = b.dataset.act;
    if (act.indexOf("type-") === 0) return retype(wrap, act.slice(5));
    if (act === "up" && wrap.previousElementSibling) wrap.previousElementSibling.before(wrap);
    else if (act === "down" && wrap.nextElementSibling) wrap.nextElementSibling.after(wrap);
    else if (act === "remove") {
      var near = wrap.previousElementSibling || wrap.nextElementSibling;
      wrap.remove();
      if (!blocks().length) near = addBlock("p", null, false);
      if (near) caretTo(mainField(near), true);
      setDirty();
      return;
    } else return;
    b.focus();
    setDirty();
  }

  /* -------------------------------- saving ------------------------------ */
  function problem() {
    var seen = {};
    var all = allArticles();
    for (var i = 0; i < all.length; i++) {
      var a = all[i], name = "“" + (a.title || "Untitled") + "”";
      if (!String(a.title || "").trim()) return "An article has no title (" + cap(listOf(a)) + " " + (store.articles[listOf(a)].indexOf(a) + 1) + ")";
      if (!ID_RE.test(a.id)) return name + ": the id must be lowercase words joined by hyphens";
      if (seen[a.id]) return name + ": another article has the id “" + a.id + "”";
      seen[a.id] = true;
    }
    return null;
  }

  function save(force) {
    if (ui.saving) return;
    commit();
    var bad = problem();
    if (bad) { status("Not saved: " + bad, true); return; }
    var articles = {};
    lists.forEach(function (name) { articles[name] = store.articles[name]; });
    ui.saving = true;
    status("Saving…");
    fetch(API, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: store.version, force: !!force, articles: articles })
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, ok: r.ok, json: j }; });
    }).then(function (res) {
      ui.saving = false;
      if (res.status === 409) {
        if (confirm("media.json has changed on disk since the editor loaded it (edited by hand, or saved from another tab).\n\n" +
                    "OK overwrites it with what is here. Cancel keeps editing; Discard would load the newer file.")) {
          save(true);
        } else {
          status("Not saved: media.json changed on disk", true);
        }
        return;
      }
      if (!res.ok) { status("Not saved: " + (res.json.error || "HTTP " + res.status), true); return; }
      store.version = res.json.version;
      dirty = false;
      history.replaceState(null, "", "?id=" + encodeURIComponent(current.id));
      status("Saved at " + new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    }).catch(function () {
      ui.saving = false;
      status("Not saved: is tools/admin_server.py still running?", true);
    });
  }

  function discard() {
    if (dirty && !confirm("Throw away every unsaved change, in every article?")) return;
    var id = current && current.id;
    load().then(function () {
      dirty = false;
      current = null;
      var a = findById(id) || allArticles()[0];
      if (a) { current = a; paint(); status("Changes discarded"); }
      else newArticle(lists[0]);
    }).catch(function () { status("Could not reload media.json", true); });
  }

  // Leaving the editor reloads the page, so article.js draws what was saved.
  function done() {
    if (dirty && !confirm("Leave the editor without saving?")) return;
    dirty = false;
    location.reload();
  }

  /* -------------------------------- set-up ------------------------------ */
  function buildBar() {
    var bar = el("div", "adm-bar");
    bar.setAttribute("role", "toolbar");
    bar.setAttribute("aria-label", "Article editor");
    bar.innerHTML =
      '<button class="adm-btn adm-btn--sq" type="button" data-cmd="bold" title="Bold (Ctrl+B)" aria-label="Bold"><b>B</b></button>' +
      '<button class="adm-btn adm-btn--sq" type="button" data-cmd="italic" title="Italic (Ctrl+I)" aria-label="Italic"><i>I</i></button>' +
      '<button class="adm-btn" type="button" data-cmd="link" title="Link (Ctrl+K)">Link</button>' +
      '<span class="adm-sep"></span>' +
      '<button class="adm-btn" type="button" data-add="p" title="Add a paragraph after this block">+ Paragraph</button>' +
      '<button class="adm-btn" type="button" data-add="h" title="Add a heading after this block">+ Heading</button>' +
      '<button class="adm-btn" type="button" data-add="quote" title="Add a quotation after this block">+ Quote</button>' +
      '<span class="adm-sep"></span>' +
      '<span class="adm-status" role="status"></span>' +
      '<button class="adm-btn" type="button" data-bar="panel" aria-pressed="false">Article</button>' +
      '<button class="adm-btn" type="button" data-bar="discard">Discard</button>' +
      '<button class="adm-btn" type="button" data-bar="done">Done</button>' +
      '<button class="adm-btn adm-btn--gold" type="button" data-bar="save" title="Save (Ctrl+S)">Save</button>';
    // Keep the selection in the text when a formatting button is pressed.
    bar.addEventListener("mousedown", function (e) {
      if (e.target.closest("[data-cmd], [data-add]")) e.preventDefault();
    });
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      if (b.dataset.cmd === "link") link();
      else if (b.dataset.cmd) format(b.dataset.cmd);
      else if (b.dataset.add) addBlock(b.dataset.add, ui.lastBlock && ui.lastBlock.isConnected ? ui.lastBlock : null);
      else if (b.dataset.bar === "panel") togglePanel();
      else if (b.dataset.bar === "discard") discard();
      else if (b.dataset.bar === "done") done();
      else if (b.dataset.bar === "save") save();
    });
    document.body.appendChild(bar);
    return bar;
  }

  function togglePanel(open) {
    open = open == null ? ui.panel.hidden : open;
    ui.panel.hidden = !open;
    ui.bar.querySelector('[data-bar="panel"]').setAttribute("aria-pressed", String(open));
  }

  function enter() {
    document.body.classList.add("adm-on");
    ui.launch.hidden = true;
    var more = slot("article-more");
    if (more) more.hidden = true;             // the other articles' cards: not edited here

    ui.title = slot("article-title");
    ui.lede = slot("article-lede");
    ui.body = slot("article-body");
    [[ui.title, "Title"], [ui.lede, "Excerpt: a sentence or two introducing the article"]].forEach(function (p) {
      p[0].classList.add("adm-field", "adm-plain");
      editable(p[0], false);
      p[0].setAttribute("data-ph", p[1]);
    });

    ui.bar = buildBar();
    ui.status = ui.bar.querySelector(".adm-status");
    ui.panel = el("aside", "adm-panel");
    ui.panel.setAttribute("aria-label", "Article settings");
    ui.panel.addEventListener("input", onPanelInput);
    ui.panel.addEventListener("change", onPanelChange);
    ui.panel.addEventListener("click", onPanelClick);
    document.body.appendChild(ui.panel);

    document.execCommand("styleWithCSS", false, false);
    document.addEventListener("keydown", onKey);
    document.addEventListener("paste", onPaste);
    document.addEventListener("input", onInput);
    document.addEventListener("selectionchange", reflectFormat);
    ui.body.addEventListener("click", onBodyClick);
    ui.body.addEventListener("mousedown", function (e) {
      if (e.target.closest(".adm-block__tools")) e.preventDefault();
    });
    ui.body.addEventListener("focusin", function (e) { ui.lastBlock = e.target.closest(".adm-block"); });
    window.addEventListener("beforeunload", function (e) {
      if (dirty) { e.preventDefault(); e.returnValue = ""; }
    });

    togglePanel(window.innerWidth >= 1400);
    status("Nothing changed yet");
  }

  // article.js fills the page from its own fetch; wait for it (it always
  // sets the title, even to "Article not found"), or it could draw over
  // the editor once that has started.
  function drawn() {
    return new Promise(function (resolve) {
      var tries = 0;
      (function check() {
        if (slot("article-title").textContent || ++tries > 100) resolve(); else setTimeout(check, 50);
      })();
    });
  }

  function boot() {
    var id = new URLSearchParams(location.search).get("id");
    Promise.all([load(), drawn()]).then(function () {
      var hit = id && findById(id);
      ui.launch = el("button", "adm-btn adm-btn--gold adm-launch", hit ? "✎ Edit article" : "+ New article");
      ui.launch.type = "button";
      ui.launch.addEventListener("click", function () {
        enter();
        if (hit) { current = hit; paint(); } else newArticle(lists[0]);
      });
      document.body.appendChild(ui.launch);
    }).catch(function (err) {
      console.error("The article editor could not load media.json.", err);
    });
  }

  boot();
})();

/* =====================================================================
   books.js - the bookstore dashboard (/__admin/books), served by
   tools/admin_server.py only. Every book of content/bookstore.json, each
   print on a line of its own with its picture, price and state; a book
   opens in a drawer where its details, its prints and their photographs
   are edited. Saves go to /__admin/bookstore, as the bookstore editor's do
   (the same checks, backups and 409 on a file changed on disk); a new
   photograph goes to /__admin/photo, which stores it under a new name and
   cuts it with tools/covers.py at once.
   ===================================================================== */
(function () {
  "use strict";

  var API = "/__admin/bookstore";
  var PHOTO_API = "/__admin/photo";
  // The bindings assets/js/curriculum.js draws (its BINDINGS); keep in step.
  var BINDINGS = ["lapis", "ink", "lapis-silver", "ink-silver", "petrol", "slate", "oxblood", "aubergine"];
  var YEARS = ["First Year", "Second Year", "Third Year", "Fourth Year", "Fifth Year", "Sixth Year", "Seventh Year"];
  var ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"];
  // A print's own fields; a book of one print keeps them itself.
  var PRINT = ["edition", "price", "cover", "buyHref", "soldOut"];
  var STRIPE = "https://buy.stripe.com/";

  var store = null;            // bookstore.json's editable part, as loaded or saved
  var covers = {};             // assets/img/books/tight/covers.json
  var filter = { q: "", group: "", need: "" };
  var open = -1;               // the book in the drawer
  var openPrint = 0;           // its print last touched
  var dirty = false, saving = false, timer = 0;

  function $(sel, root) { return (root || document).querySelector(sel); }
  function slot(name) { return $('[data-slot="' + name + '"]'); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function slug(s) {
    return String(s || "").toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  }

  /* --------------------------------- the data -------------------------------- */
  function printsOf(b) { return Array.isArray(b.prints) && b.prints.length ? b.prints : [b]; }
  function groups() { return (store.subjectGroups || []).filter(function (g) { return g && g.name; }); }
  // As bookstore.js files it: a subject in no group falls into the last.
  function groupOf(b) {
    var gs = groups(), s = String(b.subject || "").trim();
    if (!gs.length) return "";
    for (var i = 0; i < gs.length - 1; i++) if ((gs[i].subjects || []).indexOf(s) >= 0) return gs[i].name;
    return gs[gs.length - 1].name;
  }
  function yearsLine(b) {
    return (b.years || []).map(function (y) {
      var k = YEARS.indexOf(y);
      return k >= 0 ? ROMAN[k] : y;
    }).join(", ");
  }
  function subjects() {
    var seen = {};
    groups().forEach(function (g) { (g.subjects || []).forEach(function (s) { seen[s] = true; }); });
    store.books.forEach(function (b) { if (b.subject) seen[b.subject] = true; });
    return Object.keys(seen).sort();
  }
  function priceOk(p) { return /^\$\d+(?:,\d{3})*\.\d{2}$/.test(p || ""); }

  // A print's picture: its tight crop, else the photograph, else the binding drawn.
  function picture(b, i, p) {
    var t = p.cover && covers[p.cover];
    if (t) return { src: t.tight, tight: true };
    if (p.cover) return { src: p.cover, tight: false };
    var draw = window.renderCurriculum && window.renderCurriculum.drawnCover;
    return { src: draw ? draw(b, i) : "", tight: false };
  }

  // What a print lacks or is: for the filter, the tags and the counts.
  function needs(p) {
    return { photo: !p.cover, link: !p.buyHref, price: !String(p.price || "").trim(), sold: !!p.soldOut };
  }

  /* ---------------------------------- layouts -------------------------------- */
  // A book's id changed (or went): each tab's layout follows.
  function renameId(from, to) {
    if (!from || !store.layouts) return;
    Object.keys(store.layouts).forEach(function (g) {
      ["order", "large", "medium"].forEach(function (f) {
        var list = store.layouts[g][f] || [], k = list.indexOf(from);
        if (k < 0) return;
        if (to) list[k] = to; else list.splice(k, 1);
      });
    });
  }
  function pruneLayouts() {
    var ids = {};
    store.books.forEach(function (b) { if (b.id) ids[b.id] = true; });
    var L = store.layouts || {};
    Object.keys(L).forEach(function (g) {
      ["order", "large", "medium"].forEach(function (f) {
        var seen = {};
        L[g][f] = (L[g][f] || []).filter(function (id) { return ids[id] && !seen[id] && (seen[id] = true); });
      });
    });
  }

  /* ----------------------------------- status -------------------------------- */
  function status(text, kind) {
    var s = slot("status");
    s.textContent = text;
    s.classList.toggle("is-bad", kind === "bad");
    s.classList.toggle("is-dirty", kind === "dirty");
  }
  function changed() {
    if (!dirty) { dirty = true; status("Unsaved changes", "dirty"); }
    clearTimeout(timer);
    timer = setTimeout(function () { drawStats(); drawRows(); }, 120);
  }

  /* ----------------------------------- stats --------------------------------- */
  function drawStats() {
    var n = { photo: 0, link: 0, price: 0, sold: 0, featured: 0 }, listings = 0;
    store.books.forEach(function (b) {
      if (b.featured) n.featured++;
      printsOf(b).forEach(function (p) {
        listings++;
        var x = needs(p);
        Object.keys(x).forEach(function (k) { if (x[k]) n[k]++; });
      });
    });
    var cards = [
      ["", store.books.length, "books"],
      ["", listings, "listings (prints)"],
      ["photo", n.photo, "without a photograph", true],
      ["price", n.price, "without a price", true],
      ["link", n.link, "without a payment link"],
      ["sold", n.sold, "sold out"],
      ["featured", n.featured, "featured"]
    ];
    slot("stats").innerHTML = cards.map(function (c) {
      return '<button class="stat' + (c[3] && c[1] ? " stat--warn" : "") + '" type="button" data-need="' + c[0] + '" aria-pressed="' +
        (filter.need === c[0] && (c[0] || c[2] === "books")) + '"><b>' + c[1] + "</b><span>" + esc(c[2]) + "</span></button>";
    }).join("");
  }

  function drawGroups() {
    var names = groups().map(function (g) { return g.name; });
    var count = function (g) { return store.books.filter(function (b) { return !g || groupOf(b) === g; }).length; };
    slot("groups").innerHTML = [""].concat(names).map(function (g) {
      return '<button class="chip" type="button" data-group="' + esc(g) + '" aria-pressed="' + (filter.group === g) + '">' +
        esc(g || "All") + "<sup>" + count(g) + "</sup></button>";
    }).join("");
  }

  /* ------------------------------------ rows --------------------------------- */
  function matchesText(b) {
    var q = filter.q.trim().toLowerCase();
    if (!q) return true;
    var hay = [b.title, b.subject, b.id, b.description, groupOf(b)].concat(printsOf(b).map(function (p) { return p.edition; }))
      .join(" ").toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "");
    return q.normalize("NFKD").replace(/[̀-ͯ]/g, "").split(/\s+/).every(function (w) { return hay.indexOf(w) >= 0; });
  }
  function printShown(b, p) {
    if (!filter.need) return true;
    if (filter.need === "featured") return !!b.featured;
    return needs(p)[filter.need];
  }

  function thumb(b, i, p) {
    var pic = picture(b, i, p);
    return '<img class="thumb' + (pic.tight ? " thumb--tight" : "") + '" src="' + esc(pic.src) + '" alt="" loading="lazy" width="52" height="70">';
  }
  function priceCell(p) {
    var price = String(p.price || "").trim();
    if (!price) return '<span class="price price--none">—</span>';
    return '<span class="price' + (priceOk(price) ? "" : " price--odd") + '"' + (priceOk(price) ? "" : ' title="Not written like $12.00"') + ">" + esc(price) + "</span>";
  }
  function tags(b, p, withBook) {
    var t = [], x = needs(p);
    if (withBook && b.featured) t.push('<span class="tag tag--gold">Featured</span>');
    if (withBook && (b.size === "large" || b.size === "medium")) t.push('<span class="tag">' + b.size + "</span>");
    if (x.sold) t.push('<span class="tag tag--warn">Sold out</span>');
    if (p.buyHref) t.push('<span class="tag tag--ok">Payment link</span>');
    else t.push('<span class="tag">No payment link</span>');
    if (x.photo) t.push('<span class="tag tag--warn">No photo</span>');
    return '<div class="tags">' + t.join("") + "</div>";
  }
  function subjCell(b) {
    return '<div class="subj">' + esc(b.subject || "—") + "<small>" + esc(groupOf(b)) + "</small></div>";
  }

  function drawRows() {
    var html = "";
    store.books.forEach(function (b, i) {
      if (filter.group && groupOf(b) !== filter.group) return;
      if (!matchesText(b)) return;
      var isOpen = i === open ? " is-open" : "";
      var title = '<div class="b-title">' + esc(b.title || "Untitled") + "</div>";
      var id = '<div class="b-id">' + (b.id ? esc(b.id) : "no page id") + "</div>";
      if (!b.prints) {
        if (!printShown(b, b)) return;
        html += '<tr class="row' + isOpen + '" data-i="' + i + '" data-k="0" tabindex="0">' +
          '<td class="c-pic">' + thumb(b, i, b) + "</td>" +
          "<td>" + title + (b.edition ? '<div class="b-sub">' + esc(b.edition) + "</div>" : "") + id + "</td>" +
          "<td>" + subjCell(b) + '</td><td class="years">' + esc(yearsLine(b)) + '</td><td class="c-price">' + priceCell(b) + "</td>" +
          "<td>" + tags(b, b, true) + "</td></tr>";
        return;
      }
      var shown = b.prints.map(function (p, k) { return printShown(b, p) ? k : -1; }).filter(function (k) { return k >= 0; });
      if (!shown.length) return;
      var head = [];
      if (b.featured) head.push('<span class="tag tag--gold">Featured</span>');
      if (b.size === "large" || b.size === "medium") head.push('<span class="tag">' + b.size + "</span>");
      html += '<tr class="book-head' + isOpen + '" data-i="' + i + '">' +
        '<td class="c-pic"></td><td><div class="b-title">' + esc(b.title || "Untitled") + "<small>" + b.prints.length + " prints</small></div>" + id + "</td>" +
        "<td>" + subjCell(b) + '</td><td class="years">' + esc(yearsLine(b)) + "</td><td></td>" +
        '<td><div class="tags">' + head.join("") + "</div></td></tr>";
      shown.forEach(function (k) {
        var p = b.prints[k];
        html += '<tr class="row row--print' + isOpen + '" data-i="' + i + '" data-k="' + k + '" tabindex="0">' +
          '<td class="c-pic">' + thumb(b, i, p) + "</td>" +
          '<td><div class="b-print">Print ' + (k + 1) + '</div><div class="b-sub">' + esc(p.edition || "No edition line") + "</div></td>" +
          "<td></td><td></td>" +
          '<td class="c-price">' + priceCell(p) + "</td><td>" + tags(b, p, false) + "</td></tr>";
      });
    });
    slot("rows").innerHTML = html;
    slot("empty").hidden = !!html;
  }

  /* ----------------------------------- drawer -------------------------------- */
  function field(label, attrs, value, note, kind) {
    var input = kind === "textarea"
      ? "<textarea " + attrs + ">" + esc(value) + "</textarea>"
      : "<input " + attrs + ' value="' + esc(value) + '" spellcheck="false">';
    return '<label class="f"><span>' + label + "</span>" + input + (note ? "<small>" + note + "</small>" : "") + "</label>";
  }

  function printCard(b, i, p, k) {
    var many = !!b.prints, pic = picture(b, i, p);
    var crop = b.id && p.cover && covers[p.cover]
      ? '<a class="btn btn--sm" href="/book.html?id=' + encodeURIComponent(b.id) + (many ? "&print=" + (k + 1) : "") +
        '" target="_blank" rel="noopener" title="Rotate and crop on the book’s page (save here first)">Crop ↗</a>' : "";
    return '<div class="print' + (many && k === openPrint ? " is-open" : "") + '" data-k="' + k + '">' +
      '<div class="print__head"><b>' + (many ? "Print " + (k + 1) + " of " + b.prints.length : "Print") + "</b>" +
      (many ? '<span class="row-btns" style="margin:0">' +
        '<button class="btn btn--sm" type="button" data-act="pmove" data-dir="-1"' + (k === 0 ? " disabled" : "") + ' aria-label="Move earlier">↑</button>' +
        '<button class="btn btn--sm" type="button" data-act="pmove" data-dir="1"' + (k === b.prints.length - 1 ? " disabled" : "") + ' aria-label="Move later">↓</button>' +
        '<button class="btn btn--sm btn--danger" type="button" data-act="premove">Remove</button></span>' : "") + "</div>" +
      '<div class="print__body">' +
        '<div class="photo">' +
          '<div class="photo__frame" data-drop>' + (pic.src ? '<img src="' + esc(pic.src) + '" alt="">' : "") + "</div>" +
          '<label class="btn btn--sm">' + (p.cover ? "Replace photo" : "Upload photo") + '<input type="file" accept="image/*" data-upload></label>' +
          (p.cover ? '<button class="btn btn--sm" type="button" data-act="nophoto">Use drawn binding</button>' : "") + crop +
        "</div>" +
        "<div>" +
          field("Edition", 'data-pf="edition" placeholder="e.g. Maktaba al-Bushra, 2 vols"', p.edition, "The line under the title that tells this print from others.") +
          '<div class="grid2">' +
            field("Price", 'data-pf="price" placeholder="$12.00"' + (p.price && !priceOk(p.price) ? ' class="bad"' : ""), p.price,
              "Keep equal to the Stripe link’s price.") +
            '<label class="f"><span>Stock</span><span class="check" style="margin-top:6px"><input type="checkbox" data-pf="soldOut"' +
              (p.soldOut ? " checked" : "") + "> Sold out</span></label>" +
          "</div>" +
          field("Stripe payment link", 'data-pf="buyHref" type="url" placeholder="' + STRIPE + '…"' +
            (p.buyHref && p.buyHref.indexOf(STRIPE) !== 0 ? ' class="bad"' : ""), p.buyHref,
            "Empty: no Buy button. Redirect to <code>book.html?id=" + esc(b.id || "…") + (many ? "&amp;print=" + (k + 1) : "") + "&amp;paid=1</code>.") +
          field("Photograph path", 'data-pf="cover" placeholder="assets/img/books/name.jpg"', p.cover, "Set by uploading; empty draws the binding.") +
        "</div>" +
      "</div></div>";
  }

  function drawDrawer() {
    var d = slot("drawer");
    if (open < 0 || !store.books[open]) {
      d.hidden = true;
      document.body.classList.remove("has-drawer");
      return;
    }
    var b = store.books[open], i = open;
    var size = b.size === "large" || b.size === "medium" ? b.size : "normal";
    var page = b.id ? '<a class="btn btn--sm" href="/book.html?id=' + encodeURIComponent(b.id) + '" target="_blank" rel="noopener">Book page ↗</a>' : "";
    d.innerHTML =
      '<div class="drawer__head"><div><h2>' + esc(b.title || "Untitled") + '</h2><div class="drawer__links">' + page +
        '<button class="btn btn--sm" type="button" data-act="bmove" data-dir="-1"' + (i === 0 ? " disabled" : "") + ">↑ Earlier in the list</button>" +
        '<button class="btn btn--sm" type="button" data-act="bmove" data-dir="1"' + (i === store.books.length - 1 ? " disabled" : "") + ">↓ Later</button>" +
        '</div></div><button class="btn btn--sm" type="button" data-act="close" aria-label="Close">✕</button></div>' +

      "<h3>The book</h3>" +
      field("Title", 'data-f="title"', b.title) +
      '<div class="grid2">' +
        field("Subject (category)", 'data-f="subject" list="dash-subjects"', b.subject,
          "Group: <b data-groupnote>" + esc(groupOf(b)) + "</b>. Groups are set by hand in bookstore.json.") +
        field("Page id", 'data-f="id" placeholder="e.g. sahih-muslim"', b.id || "", "Its page: book.html?id=… Keep once published.") +
      "</div>" +
      '<datalist id="dash-subjects">' + subjects().map(function (s) { return '<option value="' + esc(s) + '">'; }).join("") + "</datalist>" +
      '<div class="f"><span>Taught in</span><div class="yearbox">' + YEARS.map(function (y) {
        return '<label class="check"><input type="checkbox" data-year="' + esc(y) + '"' + ((b.years || []).indexOf(y) >= 0 ? " checked" : "") + "> " + esc(y) + "</label>";
      }).join("") + "</div></div>" +
      field("Description", 'data-f="description" rows="4"', b.description, "On the book’s page, and on a large card.", "textarea") +

      "<h3>On the bookstore</h3>" +
      '<label class="check"><input type="checkbox" data-f="featured"' + (b.featured ? " checked" : "") + "> Featured (on the home page first)</label>" +
      '<div class="f"><span>Card size (the All tab; each subject tab sizes its own on the bookstore page)</span><div class="seg">' +
        ["normal", "medium", "large"].map(function (s) {
          return '<button class="btn btn--sm" type="button" data-act="size" data-size="' + s + '" aria-pressed="' + (size === s) + '">' + s[0].toUpperCase() + s.slice(1) + "</button>";
        }).join("") + "</div></div>" +
      (size !== "normal" ? '<div class="f"><span>Card colour</span><div class="tintrow"><input type="color" data-f="tint" value="' + esc(b.tint || "#5a4947") + '">' +
        "<code>" + esc(b.tint || "the cover’s") + "</code>" +
        (b.tint ? '<button class="btn btn--sm" type="button" data-act="notint">Use the cover’s</button>' : "") + "</div></div>" : "") +
      '<label class="f"><span>Binding (drawn when there is no photograph)</span><select data-f="color">' +
        BINDINGS.map(function (c) { return '<option' + (b.color === c ? " selected" : "") + ">" + c + "</option>"; }).join("") + "</select></label>" +

      "<h3>" + (b.prints ? "Prints" : "Print, price and photograph") + "</h3>" +
      printsOf(b).map(function (p, k) { return printCard(b, i, p, k); }).join("") +
      '<div class="row-btns"><button class="btn" type="button" data-act="padd">+ Add ' + (b.prints ? "a print" : "another print") + "</button></div>" +
      "<small style=\"display:block;margin-top:6px;color:var(--faint)\">For a book sold in more than one edition or cover, perhaps at another price.</small>" +

      '<h3>Remove</h3><button class="btn btn--danger" type="button" data-act="delete">Delete this book</button>';
    d.hidden = false;
    document.body.classList.add("has-drawer");
  }

  function openBook(i, k, focus) {
    open = i;
    openPrint = k || 0;
    drawDrawer();
    drawRows();
    if (focus) {
      var card = $('.print[data-k="' + openPrint + '"]', slot("drawer"));
      if (card && store.books[i].prints) card.scrollIntoView({ block: "center" });
      else slot("drawer").scrollTop = 0;
    }
  }

  /* ---------------------------------- editing -------------------------------- */
  function printAt(b, k) { return b.prints ? b.prints[k] : b; }

  function onInput(e) {
    var t = e.target, b = store.books[open];
    if (!b) return;
    if (t.dataset.year != null) {
      b.years = Array.prototype.filter.call(slot("drawer").querySelectorAll("[data-year]"), function (x) { return x.checked; })
        .map(function (x) { return x.dataset.year; });
      return changed();
    }
    var pf = t.dataset.pf;
    if (pf) {
      var card = t.closest(".print"), k = +card.dataset.k, p = printAt(b, k);
      openPrint = k;
      if (pf === "soldOut") { if (t.checked) p.soldOut = true; else delete p.soldOut; }
      else if (pf === "buyHref") {
        p.buyHref = t.value.trim();
        if (!p.buyHref) delete p.buyHref;
        t.classList.toggle("bad", !!p.buyHref && p.buyHref.indexOf(STRIPE) !== 0);
      } else if (pf === "cover") p.cover = t.value.trim();
      else if (pf === "price") { p.price = t.value.trim(); t.classList.toggle("bad", !!p.price && !priceOk(p.price)); }
      else p[pf] = t.value.replace(/\s+/g, " ");
      return changed();
    }
    var f = t.dataset.f;
    if (!f) return;
    if (f === "title") {
      // An id that followed the title keeps following it.
      if (b.id == null || b.id === "" || b.id === slug(b.title)) {
        var to = slug(t.value);
        renameId(b.id, to);
        b.id = to;
        var idBox = $('[data-f="id"]', slot("drawer"));
        if (idBox) idBox.value = b.id;
      }
      b.title = t.value.replace(/\s+/g, " ");
      $(".drawer__head h2").textContent = b.title || "Untitled";
    } else if (f === "id") {
      var id = t.value.trim();
      renameId(b.id, id);
      if (id) b.id = id; else delete b.id;
    } else if (f === "featured") b.featured = t.checked;
    else if (f === "tint") { b.tint = t.value.toLowerCase(); var code = $(".tintrow code"); if (code) code.textContent = b.tint; }
    else if (f === "subject") {
      b.subject = t.value.replace(/\s+/g, " ").trim();
      var note = $("[data-groupnote]");
      if (note) note.textContent = groupOf(b);
    } else b[f] = t.value.replace(/\s+/g, " ");
    changed();
  }

  // A price typed as 12 or 12.5 is written $12.00 / $12.50.
  function onChange(e) {
    var t = e.target;
    if (t.dataset.pf !== "price") return;
    var m = /^\$?\s*(\d+)(?:\.(\d{1,2}))?$/.exec(t.value.trim());
    if (!m) return;
    var v = "$" + m[1] + "." + ((m[2] || "") + "00").slice(0, 2);
    if (v === t.value) return;
    t.value = v;
    onInput({ target: t });
  }

  function addPrint(b) {
    if (!b.prints) {
      var one = {};
      PRINT.forEach(function (f) { if (f in b) { one[f] = b[f]; delete b[f]; } });
      b.prints = [one];
    }
    var last = b.prints[b.prints.length - 1];
    b.prints.push({ edition: "", price: last.price || "", cover: "" });
    openPrint = b.prints.length - 1;
  }
  function removePrint(b, k) {
    var p = b.prints[k];
    if (!confirm("Remove print " + (k + 1) + (p.edition ? " (“" + p.edition + "”)" : "") + " of " + (b.title || "Untitled") + "?")) return false;
    b.prints.splice(k, 1);
    if (b.prints.length === 1) {
      // One print left: its fields go back to the book.
      var one = b.prints[0];
      delete b.prints;
      PRINT.forEach(function (f) { if (f in one) b[f] = one[f]; });
    }
    openPrint = Math.max(0, k - 1);
    return true;
  }

  function onClick(e) {
    var t = e.target.closest("button");
    if (!t) return;
    var b = store.books[open], act = t.dataset.act, card = t.closest(".print"), k = card ? +card.dataset.k : 0;
    if (act === "close") { open = -1; drawDrawer(); drawRows(); return; }
    if (!b) return;
    if (act === "size") {
      if (t.dataset.size === "normal") { delete b.size; delete b.tint; } else b.size = t.dataset.size;
    } else if (act === "notint") delete b.tint;
    else if (act === "padd") addPrint(b);
    else if (act === "premove") { if (!removePrint(b, k)) return; }
    else if (act === "pmove") {
      var to = k + +t.dataset.dir;
      b.prints.splice(to, 0, b.prints.splice(k, 1)[0]);
      openPrint = to;
    } else if (act === "bmove") {
      var j = open + +t.dataset.dir;
      store.books.splice(j, 0, store.books.splice(open, 1)[0]);
      open = j;
    } else if (act === "nophoto") { printAt(b, k).cover = ""; }
    else if (act === "delete") {
      if (!confirm("Delete “" + (b.title || "Untitled") + "”?\n\nIt goes from bookstore.json when you save.")) return;
      renameId(b.id, "");
      store.books.splice(open, 1);
      open = -1;
    } else return;
    changed();
    drawDrawer();
    drawRows();
    if (act === "padd") openBook(open, openPrint, true);
  }

  /* --------------------------------- photographs ----------------------------- */
  function upload(file, k) {
    var b = store.books[open];
    if (!b || !file) return;
    if (!/^image\//.test(file.type)) { status("Not an image: " + file.name, "bad"); return; }
    var name = (b.id || slug(b.title) || "book") + (b.prints && k > 0 ? "-" + (k + 1) : "");
    var frame = $('.print[data-k="' + k + '"] .photo__frame', slot("drawer"));
    if (frame) frame.classList.add("is-busy");
    status("Uploading " + file.name + "…");
    var reader = new FileReader();
    reader.onload = function () {
      fetch(PHOTO_API, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name, data: reader.result })
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, status: r.status, json: j }; });
      }).then(function (res) {
        if (!res.ok) { if (frame) frame.classList.remove("is-busy"); status("Photo not added: " + (res.json.error || "HTTP " + res.status), "bad"); return; }
        covers[res.json.path] = res.json.entry;
        if (store.books[open] !== b) return;   // the drawer moved on
        printAt(b, k).cover = res.json.path;
        openPrint = k;
        changed();
        status("Photo added as " + res.json.path + ". Save to use it.", "dirty");
        drawDrawer();
        drawRows();
      }).catch(function () {
        if (frame) frame.classList.remove("is-busy");
        status("Photo not added: is tools/admin_server.py still running?", "bad");
      });
    };
    reader.readAsDataURL(file);
  }

  /* ----------------------------------- saving -------------------------------- */
  function problem() {
    var seen = {};
    for (var i = 0; i < store.books.length; i++) {
      var b = store.books[i], where = "“" + (b.title || "book " + (i + 1)) + "”";
      if (!String(b.title || "").trim()) return "book " + (i + 1) + " has no title";
      if (printsOf(b).some(function (p) { return p.buyHref && p.buyHref.indexOf(STRIPE) !== 0; })) return where + ": the payment link must start with " + STRIPE;
      if (b.id === "") delete b.id;
      if (b.id == null) continue;
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(b.id)) return where + ": the page id must be lowercase words joined by hyphens";
      if (seen[b.id]) return where + ": the page id “" + b.id + "” is used twice";
      seen[b.id] = true;
    }
    return null;
  }

  function save(force) {
    if (saving || !store) return;
    var bad = problem();
    if (bad) { status("Not saved: " + bad, "bad"); return; }
    pruneLayouts();
    saving = true;
    status("Saving…");
    var body = { version: store.version, force: !!force, books: store.books, layouts: store.layouts || {} };
    ["heading", "kicker", "lede", "visitLabel", "buyLabel", "pickup", "thanks"].forEach(function (f) { body[f] = store[f]; });
    fetch(API, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, ok: r.ok, json: j }; });
      }).then(function (res) {
        saving = false;
        if (res.status === 409) {
          if (confirm("bookstore.json has changed on disk since this page loaded it (edited by hand, or saved from another tab).\n\n" +
                      "OK overwrites it with what is here. Cancel keeps editing; Discard would load the newer file.")) save(true);
          else status("Not saved: bookstore.json changed on disk", "bad");
          return;
        }
        if (!res.ok) { status("Not saved: " + (res.json.error || "HTTP " + res.status), "bad"); return; }
        store.version = res.json.version;
        dirty = false;
        status("Saved at " + new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
        drawDrawer();   // the crop links need the saved state
      }).catch(function () {
        saving = false;
        status("Not saved: is tools/admin_server.py still running?", "bad");
      });
  }

  function load() {
    return Promise.all([
      fetch(API, { cache: "no-store" }).then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); }),
      fetch("/assets/img/books/tight/covers.json", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; })
    ]).then(function (got) {
      store = got[0];
      covers = got[1] || {};
    });
  }

  function drawAll() { drawStats(); drawGroups(); drawRows(); drawDrawer(); }

  function discard() {
    if (dirty && !confirm("Throw away every unsaved change?")) return;
    load().then(function () {
      dirty = false;
      if (open >= store.books.length) open = -1;
      drawAll();
      status("Changes discarded");
    }).catch(function () { status("Could not reload bookstore.json", "bad"); });
  }

  /* ----------------------------------- set-up -------------------------------- */
  function boot() {
    var drawer = slot("drawer");
    drawer.addEventListener("input", onInput);
    drawer.addEventListener("change", function (e) {
      if (e.target.matches("[data-upload]")) {
        upload(e.target.files[0], +e.target.closest(".print").dataset.k);
        e.target.value = "";
        return;
      }
      onChange(e);
    });
    drawer.addEventListener("click", onClick);
    // A photograph dropped on a print's frame is uploaded for it.
    drawer.addEventListener("dragover", function (e) {
      var f = e.target.closest("[data-drop]");
      if (!f) return;
      e.preventDefault();
      f.classList.add("is-drop");
    });
    drawer.addEventListener("dragleave", function (e) {
      var f = e.target.closest("[data-drop]");
      if (f) f.classList.remove("is-drop");
    });
    drawer.addEventListener("drop", function (e) {
      var f = e.target.closest("[data-drop]");
      if (!f) return;
      e.preventDefault();
      f.classList.remove("is-drop");
      upload(e.dataTransfer.files[0], +f.closest(".print").dataset.k);
    });

    slot("rows").addEventListener("click", function (e) {
      var tr = e.target.closest("tr[data-i]");
      if (tr) openBook(+tr.dataset.i, +(tr.dataset.k || 0), true);
    });
    slot("rows").addEventListener("keydown", function (e) {
      var tr = e.target.closest("tr[data-i]");
      if (tr && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); openBook(+tr.dataset.i, +(tr.dataset.k || 0), true); }
    });
    slot("stats").addEventListener("click", function (e) {
      var s = e.target.closest("[data-need]");
      if (!s) return;
      filter.need = filter.need === s.dataset.need ? "" : s.dataset.need;
      $('[data-filter="need"]').value = filter.need;
      drawStats();
      drawRows();
    });
    slot("groups").addEventListener("click", function (e) {
      var c = e.target.closest("[data-group]");
      if (!c) return;
      filter.group = c.dataset.group;
      drawGroups();
      drawRows();
    });
    $('[data-filter="q"]').addEventListener("input", function (e) { filter.q = e.target.value; drawRows(); });
    $('[data-filter="need"]').addEventListener("change", function (e) { filter.need = e.target.value; drawStats(); drawRows(); });

    document.addEventListener("click", function (e) {
      var t = e.target.closest("[data-act]");
      if (!t || t.closest(".drawer")) return;
      if (t.dataset.act === "save") save();
      else if (t.dataset.act === "discard") discard();
      else if (t.dataset.act === "add") {
        store.books.push({ id: slug("New book"), title: "New book", subject: "", years: [], price: "", description: "", cover: "", color: "lapis" });
        filter.group = ""; filter.q = ""; filter.need = "";
        $('[data-filter="q"]').value = "";
        $('[data-filter="need"]').value = "";
        changed();
        drawGroups();
        openBook(store.books.length - 1, 0, true);
        var title = $('[data-f="title"]');
        title.focus();
        title.select();
        var row = $('tr[data-i="' + (store.books.length - 1) + '"]');
        if (row) row.scrollIntoView({ block: "center" });
      }
    });
    document.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") { e.preventDefault(); save(); }
      else if (e.key === "Escape" && open >= 0 && !e.target.closest("input, textarea, select")) { open = -1; drawDrawer(); drawRows(); }
    });
    window.addEventListener("beforeunload", function (e) { if (dirty) { e.preventDefault(); e.returnValue = ""; } });

    load().then(function () {
      drawAll();
      status("Nothing changed yet");
      // ?id=<book id> opens that book.
      var want = new URLSearchParams(location.search).get("id");
      var at = want ? store.books.findIndex(function (b) { return b.id === want; }) : -1;
      if (at >= 0) openBook(at, 0, true);
    }).catch(function (err) {
      status("Could not load bookstore.json (" + err.message + "). Is this page served by tools/admin_server.py?", "bad");
    });
  }

  boot();
})();

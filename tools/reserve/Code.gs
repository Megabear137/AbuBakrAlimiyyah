/* =====================================================================
   Code.gs - the bookstore's reservations: a Google Apps Script web app,
   bound to a Google Sheet in the masjid's Google account. See README.md
   beside it for setting it up; this file is pasted into the script editor
   (Extensions > Apps Script) as it stands.

   The site's cart (assets/js/cart.js) posts
     {name, email, website, items: [{id, print, qty, title, edition, price}]}
   as JSON. The script checks it, looks every book up in the live site's
   content/bookstore.json (the title, edition and price the page sent are
   used only while Settings' "site" is empty, for testing), gives the
   reservation the next reference (R-1001, R-1002, ...), adds a row per book
   to the Reservations sheet, emails the reader a receipt and the bookstore
   a copy, and answers {ok: true, ref} or {ok: false, message}; the message
   is shown to the reader as it stands.

   The sheet is the ledger. The script writes every column up to Status;
   Status (Reserved, Collected, Cancelled), Collected and Note are the
   bookstore's to keep by hand.

   "website" is a field people never see: a robot that fills it gets a
   pretend reference and nothing is recorded or sent.
   ===================================================================== */

var SHEET = "Reservations";
var SETTINGS = "Settings";
var HEAD = ["Ref", "Reserved", "Name", "Email", "Book", "Print", "Copies", "Price", "Line total", "Status", "Collected", "Note"];
var STATUSES = ["Reserved", "Collected", "Cancelled"];
var FIRST_REF = 1001;
var MAX_LINES = 20;
var SORRY = "The reservation didn’t go through, and nothing was reserved. Please try again in a moment.";

// Settings: the second sheet, a key, a value and what it is, row by row.
var DEFAULTS = [
  ["site", "", "The live site's address, ending in / (e.g. https://example.org/). Books and prices are checked against its content/bookstore.json, and the receipt's collection details and the masjid's contacts come from it. Empty: the books and prices the page sends are trusted - for testing only."],
  ["notify", "", "Where the bookstore's copy of each reservation goes, and where the reader's replies go. Empty: the account that runs this script."],
  ["sender", "Jāmiʿah Islāmiyah Abū Bakr Bookstore", "The name the emails come from."],
  ["perDay", "3", "The most reservations one email address can make in 24 hours."],
  ["maxCopies", "5", "The most copies of one print in one reservation (the site's cart allows 5)."]
];

/* ------------------------------- setup ------------------------------- */
// Run once from the editor (choose "setup", then Run): makes both sheets,
// the Status dropdown and the settings, and asks for the permissions the
// web app needs (the sheet, sending mail, fetching the site's JSON).
function setup() {
  var book = SpreadsheetApp.getActive();
  var sheet = book.getSheetByName(SHEET) || book.insertSheet(SHEET, 0);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEAD);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, HEAD.length).setFontWeight("bold").setBackground("#f3e6cc");
  }
  if (sheet.getMaxRows() > 1) shape(sheet, 2, sheet.getMaxRows() - 1);

  var set = book.getSheetByName(SETTINGS) || book.insertSheet(SETTINGS);
  if (set.getLastRow() === 0) {
    set.appendRow(["Setting", "Value", "What it is"]);
    set.getRange(1, 1, 1, 3).setFontWeight("bold");
    set.setFrozenRows(1);
  }
  var have = set.getRange(1, 1, set.getLastRow(), 1).getValues().map(function (r) { return r[0]; });
  DEFAULTS.forEach(function (d) { if (have.indexOf(d[0]) < 0) set.appendRow(d); });
  set.setColumnWidth(2, 320);
  set.setColumnWidth(3, 560);

  var props = PropertiesService.getScriptProperties();
  if (!props.getProperty("nextRef")) props.setProperty("nextRef", String(FIRST_REF));

  // Touch each service so the editor asks for its permission now.
  MailApp.getRemainingDailyQuota();
  try { UrlFetchApp.fetch("https://www.google.com/", { muteHttpExceptions: true }); } catch (e) {}
  Logger.log("Ready. Emails go from " + Session.getEffectiveUser().getEmail() + ".");
}

/* ------------------------------ web app ------------------------------ */
function doPost(e) {
  var out;
  try {
    out = reserve(JSON.parse(e.postData.contents));
  } catch (err) {
    if (err && err.refuse) out = { ok: false, message: err.refuse };
    else { console.error(err && err.stack || err); out = { ok: false, message: SORRY }; }
  }
  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return ContentService.createTextOutput("The bookstore's reservations. The site's cart sends them here.");
}

function refuse(message) { throw { refuse: message }; }

/* ---------------------------- a reservation --------------------------- */
function reserve(req) {
  if (!req || typeof req !== "object") refuse(SORRY);
  if (req.website) return { ok: true, ref: "R-" + FIRST_REF };   // a robot: pretend

  var cfg = settings();
  var name = text(req.name, 100);
  var email = text(req.email, 200);
  if (!name) refuse("Please give your name.");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) refuse("Please check your email address.");
  if (!Array.isArray(req.items) || !req.items.length) refuse("Your cart is empty.");
  if (req.items.length > MAX_LINES) refuse("Please reserve at most " + MAX_LINES + " books at a time.");

  var site = cfg.site ? cfg.site.replace(/\/?$/, "/") : "";
  var store = site ? fetchJSON(site + "content/bookstore.json") : null;
  var program = site ? fetchJSON(site + "content/program.json", true) : null;

  // Each line, looked up in the catalogue; the same print twice is one line.
  var lines = [];
  req.items.forEach(function (it) {
    var id = text(it && it.id, 100), print = it && it.print, qty = it && it.qty;
    if (!id || print !== Math.floor(print) || print < 0 || qty !== Math.floor(qty) || qty < 1) refuse(SORRY);
    if (qty > cfg.maxCopies) refuse("Please reserve at most " + cfg.maxCopies + " copies of a book.");
    var line;
    if (store) {
      var b = (store.books || []).filter(function (x) { return x.id === id; })[0];
      var p = b && printsOf(b)[print];
      if (!p) refuse("A book in your cart is no longer in the bookstore. Please reload the page and try again.");
      var label = b.title + (p.edition ? " (" + p.edition + ")" : "");
      if (p.soldOut) refuse(label + " has just sold out. Please remove it from your cart and try again.");
      if (cents(p.price) == null) refuse(label + " can't be reserved at the moment. Please remove it from your cart and try again.");
      line = { id: id, print: print, qty: qty, title: b.title, edition: p.edition || "", each: cents(p.price) };
    } else {
      var each = cents(it.price);
      if (!text(it.title, 200) || each == null) refuse(SORRY);
      line = { id: id, print: print, qty: qty, title: text(it.title, 200), edition: text(it.edition, 200), each: each };
    }
    var same = lines.filter(function (l) { return l.id === id && l.print === print; })[0];
    if (same) same.qty = Math.min(cfg.maxCopies, same.qty + qty);
    else lines.push(line);
  });

  var when = new Date();
  var sheet = SpreadsheetApp.getActive().getSheetByName(SHEET);
  if (!sheet) throw new Error("Run setup() first: there is no " + SHEET + " sheet.");

  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  var ref;
  try {
    if (madeToday(sheet, email, when) >= cfg.perDay) {
      refuse("You’ve made several reservations today. To reserve more, please reply to one of your receipts.");
    }
    if (MailApp.getRemainingDailyQuota() < 2) {
      refuse("We can’t take more reservations today. Please try again tomorrow.");
    }
    var props = PropertiesService.getScriptProperties();
    var n = parseInt(props.getProperty("nextRef"), 10) || FIRST_REF;
    ref = "R-" + n;
    props.setProperty("nextRef", String(n + 1));
    var rows = lines.map(function (l) {
      return [ref, when, name, email, l.title, l.edition, l.qty, l.each / 100, l.each * l.qty / 100, "Reserved", "", ""];
    });
    var start = sheet.getLastRow() + 1, end = start + rows.length - 1;
    if (end > sheet.getMaxRows()) sheet.insertRowsAfter(sheet.getMaxRows(), end - sheet.getMaxRows() + 100);
    sheet.getRange(start, 1, rows.length, HEAD.length).setValues(rows);
    shape(sheet, start, rows.length);
    SpreadsheetApp.flush();
  } finally {
    lock.releaseLock();
  }

  var r = { ref: ref, when: when, name: name, email: email, lines: lines,
            total: lines.reduce(function (s, l) { return s + l.each * l.qty; }, 0) };
  var notify = cfg.notify || Session.getEffectiveUser().getEmail();
  try {
    MailApp.sendEmail({
      to: email, replyTo: notify, name: cfg.sender,
      subject: "Reserved: " + summary(lines) + " · " + ref,
      htmlBody: receiptHTML(r, store, program, site),
      body: receiptText(r, store)
    });
  } catch (err) {
    console.error(err);
    note(sheet, ref, "The receipt could not be sent: " + err);
  }
  try {
    MailApp.sendEmail({
      to: notify, replyTo: email, name: "Bookstore reservations",
      subject: ref + " · " + summary(lines) + " · " + name,
      htmlBody: copyHTML(r, SpreadsheetApp.getActive().getUrl())
    });
  } catch (err) { console.error(err); }
  return { ok: true, ref: ref };
}

/* ------------------------------ helpers ------------------------------ */
// The ledger's formats and the Status dropdown, on rows from..from+n-1.
function shape(sheet, from, n) {
  var col = function (name) { return HEAD.indexOf(name) + 1; };
  sheet.getRange(from, col("Reserved"), n, 1).setNumberFormat("d mmm yyyy h:mm");
  sheet.getRange(from, col("Collected"), n, 1).setNumberFormat("d mmm yyyy");
  sheet.getRange(from, col("Price"), n, 2).setNumberFormat("$#,##0.00");
  sheet.getRange(from, col("Status"), n, 1).setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(STATUSES, true).setAllowInvalid(false).build());
}

function settings() {
  var out = {};
  DEFAULTS.forEach(function (d) { out[d[0]] = d[1]; });
  var set = SpreadsheetApp.getActive().getSheetByName(SETTINGS);
  if (set && set.getLastRow() > 1) {
    set.getRange(2, 1, set.getLastRow() - 1, 2).getValues().forEach(function (r) {
      if (r[0]) out[String(r[0]).trim()] = String(r[1]).trim();
    });
  }
  out.perDay = parseInt(out.perDay, 10) || 3;
  out.maxCopies = parseInt(out.maxCopies, 10) || 5;
  return out;
}

function text(v, max) {
  return typeof v === "string" ? v.replace(/\s+/g, " ").trim().slice(0, max) : "";
}

// "$1,250.00" -> 125000; anything else -> null (as the site's cart.js).
function cents(price) {
  var m = /^\$(\d{1,3}(?:,\d{3})*|\d+)\.(\d{2})$/.exec(String(price || "").trim());
  return m ? parseInt(m[1].replace(/,/g, ""), 10) * 100 + parseInt(m[2], 10) : null;
}
function money(c) {
  return "$" + String(Math.floor(c / 100)).replace(/\B(?=(\d{3})+(?!\d))/g, ",") + "." + ("0" + (c % 100)).slice(-2);
}

// A book's prints, as the site reads them.
function printsOf(b) {
  if (Array.isArray(b.prints) && b.prints.length) return b.prints;
  return [{ edition: b.edition, price: b.price, cover: b.cover, soldOut: b.soldOut }];
}

function fetchJSON(url, optional) {
  try {
    var r = UrlFetchApp.fetch(url + "?t=" + Date.now(), { muteHttpExceptions: true });
    if (r.getResponseCode() !== 200) throw new Error(url + " -> HTTP " + r.getResponseCode());
    return JSON.parse(r.getContentText("UTF-8"));
  } catch (err) {
    if (optional) return null;
    throw err;
  }
}

// How many reservations this address made in the last 24 hours.
function madeToday(sheet, email, now) {
  var last = sheet.getLastRow();
  if (last < 2) return 0;
  var from = Math.max(2, last - 1999);
  var since = now.getTime() - 24 * 3600 * 1000, refs = {};
  sheet.getRange(from, 1, last - from + 1, 4).getValues().forEach(function (r) {
    if (r[1] instanceof Date && r[1].getTime() > since && String(r[3]).toLowerCase() === email.toLowerCase()) refs[r[0]] = true;
  });
  return Object.keys(refs).length;
}

function note(sheet, ref, msg) {
  var refs = sheet.getRange(1, 1, sheet.getLastRow(), 1).getValues();
  for (var i = refs.length - 1; i > 0; i--) {
    if (refs[i][0] === ref) { sheet.getRange(i + 1, HEAD.indexOf("Note") + 1).setValue(msg); return; }
  }
}

function summary(lines) {
  if (lines.length > 1) return lines.length + " books";
  var l = lines[0];
  return l.title + (l.edition ? " (" + l.edition + ")" : "") + (l.qty > 1 ? " × " + l.qty : "");
}

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}

// Policy and contacts not yet given read "TODO: ..." on the site; the
// receipt leaves them out.
function given(s) { return !!(s && String(s).trim() && !/^\s*TODO\b/i.test(s)); }

function dated(d) {
  return Utilities.formatDate(d, Session.getScriptTimeZone(), "EEEE d MMMM yyyy, h:mm a");
}

/* ------------------------------ the emails --------------------------- */
// The book page's leaf as an email: cream paper under a red and gold rule,
// the reference in a double frame. Email clients load no web fonts, so it
// is set in Georgia and Arial, with every style inline.
function receiptHTML(r, store, program, site) {
  var INK = "#462c16", MUTED = "#8a6a4a", RULE = "#d9c39a";
  var serif = "Georgia,'Times New Roman',serif", sans = "Arial,Helvetica,sans-serif";
  var facts = store ? [["Collect", store.pickup], ["Held for", store.hold], ["Pay with", store.payWith]].filter(function (f) { return given(f[1]); }) : [];
  var foot = program && program.footer ? [program.footer.address, program.footer.email, program.footer.phone].filter(given) : [];
  var first = r.name.split(" ")[0];

  var rows = r.lines.map(function (l) {
    return '<tr><td style="padding:12px 0;border-bottom:1px solid #ecdcbc;font:17px ' + serif + ';color:' + INK + '">' + esc(l.title) +
      (l.edition ? '<div style="font:13px ' + sans + ';color:' + MUTED + ';margin-top:2px">' + esc(l.edition) + "</div>" : "") + "</td>" +
      '<td align="right" style="padding:12px 0 12px 12px;border-bottom:1px solid #ecdcbc;font:14px ' + sans + ';color:' + INK + ';white-space:nowrap">' + l.qty + " × " + money(l.each) + "</td>" +
      '<td align="right" style="padding:12px 0 12px 12px;border-bottom:1px solid #ecdcbc;font:14px ' + sans + ';color:' + INK + ';white-space:nowrap">' + money(l.each * l.qty) + "</td></tr>";
  }).join("");

  var factRows = [["Reserved", dated(r.when)]].concat(facts).map(function (f) {
    return '<tr><td valign="top" style="padding:9px 16px;width:96px;font:bold 11px ' + sans + ';letter-spacing:1.5px;text-transform:uppercase;color:' + MUTED + '">' + esc(f[0]) + "</td>" +
      '<td style="padding:8px 16px 8px 0;font:14px/1.5 ' + sans + ';color:' + INK + '">' + esc(f[1]) + "</td></tr>";
  }).join("");

  return '<!doctype html><html><body style="margin:0;padding:0;background:#f4ece0">' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4ece0"><tr><td align="center" style="padding:24px 12px">' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#fbf5ea;border:1px solid #e3cfa6">' +
    '<tr><td style="height:4px;background:#a3301c;font-size:0;line-height:0">&nbsp;</td></tr>' +
    '<tr><td style="height:3px;font-size:0;line-height:0;border-bottom:1px solid #b07f22">&nbsp;</td></tr>' +
    '<tr><td align="center" style="padding:30px 32px 0">' +
      (site ? '<img src="' + esc(site) + 'assets/img/logo_black_web.png" width="104" alt="Jāmiʿah Islāmiyah Abū Bakr" style="display:block;width:104px;height:auto;border:0">' : "") +
      '<div style="margin-top:16px;font:bold 11px ' + sans + ';letter-spacing:3px;text-transform:uppercase;color:#a3301c">Bookstore · Reservation</div>' +
      '<div style="margin-top:8px;font:30px/1.15 ' + serif + ';color:' + INK + '">' + (r.lines.length > 1 ? "Your books are set aside" : "Your book is set aside") + "</div></td></tr>" +
    '<tr><td align="center" style="padding:14px 32px 0;font:16px/1.6 ' + serif + ';color:' + INK + '">As-salāmu ʿalaykum ' + esc(first) + ",<br>" +
      "we’ve reserved " + (r.lines.length > 1 ? "the books" : "the book") + " below for you. Nothing has been paid: bring this email, or the reference, to the masjid, pay there and take " + (r.lines.length > 1 ? "them" : "it") + " home.</td></tr>" +
    '<tr><td align="center" style="padding:22px 32px 4px"><table role="presentation" cellpadding="0" cellspacing="0" style="border:1px solid #a3301c"><tr><td style="padding:3px">' +
      '<table role="presentation" cellpadding="0" cellspacing="0" style="border:1px solid #b07f22;background:#ffffff"><tr><td align="center" style="padding:12px 30px">' +
      '<div style="font:bold 10px ' + sans + ';letter-spacing:3px;text-transform:uppercase;color:' + MUTED + '">Reference</div>' +
      '<div style="margin-top:4px;font:32px ' + serif + ';letter-spacing:6px;color:' + INK + '">' + esc(r.ref) + "</div></td></tr></table></td></tr></table></td></tr>" +
    '<tr><td style="padding:24px 32px 0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">' +
      '<tr><td style="padding-bottom:8px;border-bottom:1px solid ' + RULE + ';font:bold 10px ' + sans + ';letter-spacing:2px;text-transform:uppercase;color:' + MUTED + '">Book</td>' +
      '<td align="right" style="padding-bottom:8px;border-bottom:1px solid ' + RULE + ';font:bold 10px ' + sans + ';letter-spacing:2px;text-transform:uppercase;color:' + MUTED + '">Copies</td>' +
      '<td align="right" style="padding-bottom:8px;border-bottom:1px solid ' + RULE + ';font:bold 10px ' + sans + ';letter-spacing:2px;text-transform:uppercase;color:' + MUTED + '">Price</td></tr>' +
      rows +
      '<tr><td colspan="2" style="padding-top:14px;font:bold 15px ' + sans + ';color:' + INK + '">To pay at collection<div style="font:12px ' + sans + ';color:' + MUTED + '">Not paid yet</div></td>' +
      '<td align="right" valign="top" style="padding-top:14px;font:bold 15px ' + sans + ';color:' + INK + '">' + money(r.total) + "</td></tr></table></td></tr>" +
    '<tr><td style="padding:22px 32px 0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f3e6cc">' + factRows + "</table></td></tr>" +
    '<tr><td align="center" style="padding:22px 32px 0;font:13px/1.6 ' + sans + ';color:#6e5137">Changed your mind, or need a different print? Reply to this email and we’ll change or release the reservation.</td></tr>' +
    '<tr><td align="center" style="padding:26px 32px 30px"><div style="padding-top:18px;border-top:1px solid ' + RULE + ';font:12px/1.7 ' + sans + ';color:' + MUTED + '">' +
      '<span style="font:14px ' + serif + ';letter-spacing:2px;text-transform:uppercase;color:' + INK + '">Jāmiʿah Islāmiyah Abū Bakr</span>' +
      foot.map(function (f) { return "<br>" + esc(f); }).join("") +
      "<br>You’re receiving this because books were reserved with this address on the masjid’s website.</div></td></tr>" +
    "</table></td></tr></table></body></html>";
}

function receiptText(r, store) {
  var out = ["As-salāmu ʿalaykum " + r.name.split(" ")[0] + ",", "",
    "We’ve reserved the books below for you. Nothing has been paid: bring this email, or the reference, to the masjid, pay there and take them home.", "",
    "Reference: " + r.ref, ""];
  r.lines.forEach(function (l) {
    out.push(l.title + (l.edition ? " (" + l.edition + ")" : "") + ": " + l.qty + " × " + money(l.each) + " = " + money(l.each * l.qty));
  });
  out.push("To pay at collection: " + money(r.total), "", "Reserved: " + dated(r.when));
  if (store) [["Collect", store.pickup], ["Held for", store.hold], ["Pay with", store.payWith]].forEach(function (f) {
    if (given(f[1])) out.push(f[0] + ": " + f[1]);
  });
  out.push("", "Changed your mind? Reply to this email and we’ll change or release the reservation.", "", "Jāmiʿah Islāmiyah Abū Bakr");
  return out.join("\n");
}

// The bookstore's copy: plain and quick to scan; replying writes to the reader.
function copyHTML(r, sheetUrl) {
  var td = 'style="padding:6px 12px 6px 0;border-bottom:1px solid #eee;vertical-align:top"';
  var books = r.lines.map(function (l) {
    return esc(l.title) + (l.edition ? " · " + esc(l.edition) : "") + " × " + l.qty + " (" + money(l.each * l.qty) + ")";
  }).join("<br>");
  return '<div style="font:14px/1.55 Arial,Helvetica,sans-serif;color:#222">New reservation: set aside and wait for collection.' +
    '<table cellpadding="0" cellspacing="0" style="margin-top:12px;border-collapse:collapse">' +
    "<tr><td " + td + ' width="110"><span style="color:#777">Reference</span></td><td ' + td + "><b>" + esc(r.ref) + "</b></td></tr>" +
    "<tr><td " + td + '><span style="color:#777">Books</span></td><td ' + td + ">" + books + "</td></tr>" +
    "<tr><td " + td + '><span style="color:#777">To pay</span></td><td ' + td + ">" + money(r.total) + "</td></tr>" +
    "<tr><td " + td + '><span style="color:#777">Name</span></td><td ' + td + ">" + esc(r.name) + "</td></tr>" +
    "<tr><td " + td + '><span style="color:#777">Email</span></td><td ' + td + '><a href="mailto:' + esc(r.email) + '">' + esc(r.email) + "</a></td></tr>" +
    "<tr><td " + td + '><span style="color:#777">Reserved</span></td><td ' + td + ">" + esc(dated(r.when)) + "</td></tr>" +
    '</table><p style="margin-top:12px"><a href="' + esc(sheetUrl) + '">Open the reservations sheet</a></p></div>';
}

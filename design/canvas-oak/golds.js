/* The wood is fixed (wood.css); each variant is a dark gold for the text on
   the white ground and the cream cards: headings, titles, kickers and body.
   ink = headings and titles, body = paragraphs (a darker step of the same
   gold, for reading), em = the italic word in each heading. */
window.GOLDS = [
  { n: 1, name: "Antique Gold", ink: "#8a6414", body: "#654a10", em: "#a87a18",
    desc: "A warm, slightly orange antique gold, the closest to gilt lettering on an old binding. Body copy steps down to a deep honey so paragraphs stay easy to read." },
  { n: 2, name: "Old Brass", ink: "#76651f", body: "#554916", em: "#968024",
    desc: "A cooler, greener brass gold. It sits furthest from the wood's red-brown, so text and wood read as two distinct materials." },
  { n: 3, name: "Bronze Gold", ink: "#83591c", body: "#5f4115", em: "#a26f24",
    desc: "A gold leaning towards bronze and the wood itself. The quietest pairing: the page reads as one warm family." },
  { n: 4, name: "Burnished Amber", ink: "#93600e", body: "#6c470b", em: "#b27716",
    desc: "The most saturated: a deep amber gold, bright in the headings. It ties in with the gold buttons and the gold titles on the wood." },
  { n: 5, name: "Dark Ochre", ink: "#6c5714", body: "#4c3e0f", em: "#8a7019",
    desc: "The darkest and most sober, an olive-ochre gold that is nearly bronze-black in body copy. Highest contrast of the six." },
  { n: 6, name: "Gold Heads, Walnut Body", ink: "#8a6414", body: "#462c16", em: "#a87a18",
    desc: "Antique gold (1) for the headings, titles, kickers and names only; paragraphs keep today's walnut brown. For comparison, if all-gold body copy feels too much." }
];

window.goldFrame = function (iframe, n) {
  var t = GOLDS.filter(function (g) { return g.n === n; })[0];
  iframe.addEventListener("load", function () {
    var doc = iframe.contentDocument;
    if (!doc) return;
    var link = doc.createElement("link");
    link.rel = "stylesheet";
    link.href = new URL("wood.css", location.href).href;
    doc.head.appendChild(link);
    if (!t) return;
    var style = doc.createElement("style");
    style.textContent =
      ":root { --brown-ink: " + t.ink + "; --gold-ink: " + t.em + "; }" +
      ".section__heading em { color: " + t.em + "; }" +
      ".section__lede, .program-pill__body, .face__body, .face__urdu, .teacher__bio, .article__excerpt," +
      ".article__meta, .media-empty, .site-footer p, .site-footer__contact, .site-footer__contact a { color: " + t.body + "; }" +
      ".article-feature .article__excerpt { color: var(--on-choc); } .article-feature .article__meta { color: var(--gold); }" +
      ".aud-toggle__side { color: " + t.ink + "8c; }" +
      ".pill, .face__rule, .teacher__bio { border-color: " + t.em + "66; }";
    doc.head.appendChild(style);
  });
  iframe.src = "../../index.html";
};

/* Round 2 of design/canvas-oak: the wood is settled at rgb(161, 101, 65); the
   question is the text laid on it, above all the two Details cards. Each
   option is wood.css plus legible-N.css over the live page; the text on the
   white ground is untouched walnut brown throughout. */
window.LEGIBLE = [
  { n: 1, name: "Deeper boards (adopted)", swatches: ["#6b3f26", "#3c2213", "#f3cb68", "#fff6ea"],
    desc: "<b>This is the live page.</b> The panels that carry text are cut from a darker board of the same timber, while the shelf wall, teachers band and testimonies wall keep the new colour. The smallest change: nothing about the type or the layout moves, the contrast simply comes back." },
  { n: 2, name: "Cream inset", swatches: ["#fdf6ea", "#a16541", "#9a6508", "#462c16"],
    desc: "The wood becomes a frame around a cream panel, and the copy is the same dark brown as the rest of the page, with gold-ink labels and rust figures. The most readable by a distance, and it makes the Details cards siblings of the teacher cards; the cost is that the page loses two of its dark panels." },
  { n: 3, name: "Oiled glaze", swatches: ["#5a3117", "#a16541", "#ffd98b", "#ffe6ad"],
    desc: "The wood stays visible but the panels are glazed: a dark wash, deepest behind the text and lifting towards the edges, the way an oiled board darkens where it is handled. Keeps the wood reading as wood, with brighter gold on top." },
  { n: 4, name: "Engraved bands", swatches: ["#160802", "#a16541", "#ffd98b", "#fff6ea"],
    desc: "Only the lines of type darken: each timing row, each heading and each fee tier sits in a shallow routed channel with a lit lower lip. The panel between the lines stays bright wood, so the section keeps its colour and gains a timetable-board rhythm." },
  { n: 5, name: "Brass plate", swatches: ["#2e1e0d", "#f7d485", "#a16541", "#fff6ea"],
    desc: "The text is engraved on a dark bronze plate screwed to the wood with four brass screws, like a masjid timetable board. Heaviest and most literal, and the strongest contrast after the cream inset." }
];

window.legibleFrame = function (iframe, n) {
  iframe.addEventListener("load", function () {
    var doc = iframe.contentDocument;
    if (!doc) return;
    ["wood.css"].concat(n ? ["legible-" + n + ".css"] : []).forEach(function (href) {
      var link = doc.createElement("link");
      link.rel = "stylesheet";
      link.href = new URL(href, location.href).href;
      doc.head.appendChild(link);
    });
  });
  iframe.src = "../../index.html";
};

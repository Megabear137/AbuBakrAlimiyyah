/* Loads the live site into an iframe and lays a wood finish over it. Shared by
   index.html (the three previews) and view.html (one finish, full size).
   The finishes are wood-N.css, written by generate.py. */
window.WOODS = [
  { n: 1, name: "Walnut", swatches: ["#5a3a20", "#462c16", "#34200f", "#34190a", "#1e1208"],
    desc: "Dark, straight-grained walnut with a soft oiled finish. The bookshelf, the Details cards, the teachers band, the featured article and the switch share one quiet grain, close in tone to today's chocolate, so the page reads the same with texture added. The most restrained." },
  { n: 2, name: "Mahogany & Inlay", swatches: ["#8c4520", "#7a3412", "#5e2c12", "#3e1807", "#e3b34a"],
    desc: "Red-brown figured mahogany under a lacquer sheen, picking up the rust of the headings. Each panel and each shelf bay has a thin gold inlay line set inside its edge, and the teachers band's rails are gold stringing. The richest." },
  { n: 3, name: "Oak Boards & Panels", swatches: ["#a0703c", "#8a5a2c", "#74461e", "#4a2a0e", "#f6d27a"],
    desc: "Warmer, lighter oak with open growth rings. The teachers band is laid as planks, and the Details cards and the featured article are framed, raised panels like cabinet doors. The gold titles are a shade lighter to stay readable. The most handmade." }
];

window.woodFrame = function (iframe, n) {
  iframe.addEventListener("load", function () {
    var doc = iframe.contentDocument;
    if (!doc || !n) return;
    var link = doc.createElement("link");
    link.rel = "stylesheet";
    link.href = new URL("wood-" + n + ".css", location.href).href;
    doc.head.appendChild(link);
  });
  iframe.src = "../../index.html";
};

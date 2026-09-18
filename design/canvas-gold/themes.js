/* Loads the live site into an iframe and lays a theme over it. Shared by
   index.html (a round of previews) and view.html (one theme, full size).
   Round 1 is gold with light brown; round 2 makes gold the lead colour;
   round 3 pairs the brown rgb(189, 93, 15) with a gold. */
window.GOLD_THEMES = [
  { n: 1, round: 1, name: "Camel & Gilt", swatches: ["#faf8f3", "#e3cfb0", "#8c6640", "#5c3f23", "#c9a24f", "#ecd08a"],
    desc: "The closest to today's page: every green becomes a warm saddle brown. The Details cards, the teachers band and the featured article are brown with cream type, the gilt reads brighter against them, and the margin pools turn tan and honey." },
  { n: 2, round: 1, name: "Honey & Sand", swatches: ["#fefdfa", "#f5ead6", "#e6d0ac", "#e9c46a", "#d4a53c", "#5a3d1f"],
    desc: "An all-light page. The bands become pale sand with dark brown ink, honey gold carries the buttons, the switch and the emphasis, and only the header, the wooden shelf and the video scrims stay dark. The lightest and airiest of the three." },
  { n: 3, round: 1, name: "Burnished Gold", swatches: ["#fffdf8", "#dcc3a0", "#dcb35c", "#b98a36", "#7a5226", "#2b1c0c"],
    desc: "Gold is the surface. Details, Teachers and the featured article are laid in burnished gold with dark brown ink, light brown tints the white cards and the pools, and the brown headings tie them to the shelf. The boldest of the three." },
  { n: 4, round: 2, name: "Champagne", swatches: ["#fbf9f4", "#f4ecda", "#e4d5b4", "#c2a26a", "#8a6a30", "#2c241a"],
    desc: "Pale champagne gold on ivory. The Details cards, the teachers band and the featured article are soft champagne with espresso ink, and gold shows as a quiet sheen rather than a block of colour. The lightest and most understated." },
  { n: 5, round: 2, name: "Antique Gold", swatches: ["#f7f3e9", "#ecdca8", "#b8964a", "#806629", "#54421a", "#25200f"],
    desc: "The muted, faintly olive gold of old gilding and manuscript leaf. The bands are deep old gold with ivory type on a parchment ground, so it keeps the weight and calm of today's green. The most heritage-minded." },
  { n: 6, round: 2, name: "Gilded Leaf", swatches: ["#fffdf6", "#f8e39c", "#eac86a", "#d2a53d", "#b8862b", "#6e4a0c"],
    desc: "Bright yellow gold laid on as metal. The bands carry a banded metallic sheen with dark amber ink, and the pools glow honey in the margins. The richest and most ornamental." },
  { n: 7, round: 2, name: "Onyx & Gold", swatches: ["#faf8f2", "#f3e2b0", "#e6c77c", "#d4af5a", "#26221c", "#0f0d0a"],
    desc: "Gold set against black. The bands turn onyx with gold titles and cream type, headings go near-black with gold italics, and every gilt edge, bolt and button reads at full brightness. The most formal and high-contrast." },
  { n: 8, round: 2, name: "Rose Gold", swatches: ["#fcf8f5", "#f4dccd", "#e6b9a0", "#cf9a80", "#8f5647", "#633529"],
    desc: "Gold with copper in it. The bands are a deep rose-bronze with blush type, the buttons, bolts and testimony edges turn pink-gold, and the ground is a warm blush white. The softest and least traditional." },
  { n: 9, round: 3, name: "Rust & Pale Gold", swatches: ["#fbf8f2", "#f6e6bb", "#ecd08f", "#d9b56a", "#bd5d0f", "#8a4009"],
    desc: "The brown takes green's place everywhere: the Details cards, the teachers band, the featured article and the headings. A pale buttery gold on the buttons, titles and switch softens its orange. The direct swap." },
  { n: 10, round: 3, name: "Rust & Brass", swatches: ["#fcf9f3", "#efd9a0", "#d6ae52", "#b38a34", "#bd5d0f", "#8a4009"],
    desc: "The brown and a warm brass gold share the page. The Details cards and the featured article are brown with brass type, and the teachers band between them is laid in brass with brown ink, so the two colours alternate down the page." },
  { n: 11, round: 3, name: "Champagne & Rust", swatches: ["#fdfaf5", "#f6ead4", "#e8d3ae", "#d8b878", "#bd5d0f", "#9a4a0b"],
    desc: "A light page. The bands are champagne gold with dark ink, and the brown does the talking: the headings, the titles on the bands, the buttons and the switch. The lightest of the five." },
  { n: 12, round: 3, name: "Chocolate & Bright Gold", swatches: ["#fbf7f0", "#f7e0a4", "#eec25a", "#bd5d0f", "#5e2e08", "#361a04"],
    desc: "The brown deepened to chocolate for the bands, with bright gold titles and cream type and a rust edge on the cards; the true brown carries the headings and the switch on the light ground. The darkest and most formal." },
  { n: 13, round: 3, name: "Gilded Leaf & Rust", swatches: ["#fdf9f1", "#f8e39c", "#eac86a", "#c4923a", "#bd5d0f", "#7a3a08"],
    desc: "Brown on gold rather than gold on brown. The bands are laid in metallic leaf gold with their titles and rails in the brown, and the brown becomes the buttons, the switch and the play buttons. The most ornamental." }
];

window.themeFrame = function (iframe, n) {
  iframe.addEventListener("load", function () {
    var doc = iframe.contentDocument;
    if (!doc || !n) return;
    ["theme-base.css", "theme-" + n + ".css"].forEach(function (f) {
      var link = doc.createElement("link");
      link.rel = "stylesheet";
      link.href = new URL(f, location.href).href;
      doc.head.appendChild(link);
    });
  });
  iframe.src = "../../index.html";
};

#!/usr/bin/env python3
"""Mockup B (Islamic kitab) on lighter grounds: three blends of soft white and
green, with the year panel removed from the banner.

    python3 generate_light.py [outdir] [--preview]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as g
import generate_combined as gc

OUT = next((a for a in sys.argv[1:] if not a.startswith("--")), os.path.dirname(os.path.abspath(__file__)))

def hero():
    h = gc.hero()
    return h.split('<div class="hero__card')[0] + '</header>'

# Everything on the light ground reads in green ink; the banner and the shelf
# stay dark, so their own colours are left alone.
LIGHT = """
body{background:#f5f6f0;color:#14251b;}
.glass{background:linear-gradient(145deg,rgba(255,255,255,.78),rgba(255,255,255,.5));border:1px solid rgba(19,69,40,.1);
  box-shadow:inset 0 1px 0 #fff,0 24px 50px -32px rgba(19,69,40,.4);}
.nav.glass{background:linear-gradient(145deg,rgba(255,255,255,.085),rgba(255,255,255,.025));border-color:rgba(217,190,120,.28);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 24px 60px -24px rgba(0,0,0,.55);}
.tile:hover{border-color:rgba(154,122,46,.4);}
.tile__k{color:#9a7a2e;}
.lead{color:#134528;}
.muted{color:#3a4a41;}
.sec__head h2{color:#134528;} .sec__head h2 em{color:#9a7a2e;} .sec__head p{color:#4a5a50;}
.fee__amt{color:#134528;} .fee__amt small{color:#4a5a50;} .fee__note{color:#4a5a50;}
.tgroup+.tgroup{border-color:rgba(19,69,40,.12);}
.tgroup__h b{color:#134528;} .tgroup__h span{color:#9a7a2e;}
.trow{color:#3a4a41;} .trow .t{color:#134528;}
.drow{border-color:rgba(19,69,40,.1);} .drow b{color:#134528;}
.tcard h3{color:#134528;} .tcard p{color:#4a5a50;} .tcard small{color:#9a7a2e;}
.mono{box-shadow:0 0 0 5px rgba(201,169,97,.22);}
.cbtn{color:#134528;}
.gb{background:linear-gradient(160deg,rgba(255,255,255,.8),rgba(255,255,255,.5));box-shadow:0 24px 50px -32px rgba(19,69,40,.35);}
.gb::after{background:linear-gradient(135deg,#c9a961,rgba(201,169,97,.12) 35%,rgba(201,169,97,.12) 65%,#b8924a);}
.q6 p{color:#14251b;} .q6 cite{color:#4a5a50;} .q6 cite b{color:#134528;}
.soon h3{color:#134528;} .soon p{color:#4a5a50;}
.pill{color:#9a7a2e;border-color:rgba(154,122,46,.4);}
.foot{color:#4a5a50;border-color:rgba(19,69,40,.15);} .foot .brand{color:#134528;}
.prog-k{color:#9a7a2e !important;}
.fee-l{color:#4a5a50 !important;}
.fee-split{border-color:rgba(19,69,40,.12) !important;}
.shelf-tile{box-shadow:0 40px 70px -40px rgba(19,69,40,.55),inset 0 1px 0 rgba(255,235,200,.08);}
"""

# the same colours as the dark page, for a band that stays green
DARK_BAND = """
.band--green{color:#f4efe2;}
.band--green .glass{background:linear-gradient(145deg,rgba(255,255,255,.09),rgba(255,255,255,.03));border-color:rgba(217,190,120,.28);box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 24px 60px -24px rgba(0,0,0,.5);}
.band--green .sec__head h2{color:#fbf6e9;}
.band--green .tcard h3{color:#fbf6e9;} .band--green .tcard p{color:rgba(244,239,226,.72);} .band--green .tcard small{color:#d9be78;}
.band--green .cbtn{color:#e2c77f;}
"""

def fix_inline(html):
    # inline colours in B's intro and details that were written for the dark page
    return (html.replace('color:#e2c77f;font-style:italic;padding-left:14px"', 'font-style:italic;padding-left:14px" class="prog-k"')
                .replace('<div style="color:rgba(244,239,226,.7);font-size:14px">', '<div class="fee-l" style="font-size:14px">')
                .replace('border-bottom:1px solid rgba(217,190,120,.2);margin-bottom:22px"', 'border-bottom:1px solid rgba(217,190,120,.2);margin-bottom:22px" class="fee-split"'))

def sections():
    return [fix_inline(gc.intro_statement()), gc.curriculum("kitab", "Islamic kitab", 1),
            fix_inline(gc.details_two_panels()), gc.teachers(), gc.testimonies_and_rest()]

def tag(html, cls):
    return html.replace('class="wrap sec"', f'class="wrap sec {cls}"', 1)

def build(theme_css, body_inner):
    return g.doc(gc.PAGE_CSS + gc.BOOK_CSS + LIGHT + theme_css, body_inner, gc.FONTS)

# ---------------------------------------------------------------- 1 · Sage wash
def sage_wash():
    css = """
/* one long wash: the banner's green thins to sage, rests on soft white, and gathers again at the foot */
.page{background:
  radial-gradient(1100px 700px at 85% 1250px,rgba(201,235,221,.85),transparent 70%),
  radial-gradient(900px 700px at 8% 2500px,rgba(190,217,199,.6),transparent 70%),
  radial-gradient(1000px 700px at 92% 3700px,rgba(201,235,221,.75),transparent 70%),
  linear-gradient(180deg,#062707 0,#134528 860px,#8fb39a 930px,#dbe8dd 1010px,#eef3ec 1300px,#f6f6f0 2200px,#f3f6ef 3400px,#e6efe6 4400px,#cfe1d4 100%);}
.hero__tint{background:
  linear-gradient(180deg,rgba(6,39,7,.72) 0%,rgba(6,39,7,.18) 30%,rgba(19,69,40,.6) 64%,#134528 100%),
  linear-gradient(90deg,rgba(6,39,7,.75),rgba(6,39,7,0) 60%);}
"""
    s = sections()
    return build(css, '<div class="page">' + hero() + "".join(s) + '</div>')

# ---------------------------------------------------------------- 2 · Bands
def bands():
    css = """
/* full-width bands behind 1180px sections: the shadow paints the band, the clip keeps it to the section's height */
.page{background:#f6f5ef;}
.band{padding:110px 0 !important;box-shadow:0 0 0 100vmax var(--band);clip-path:inset(0 -100vmax);background:var(--band);}
.band--white{--band:#f7f6f0;}
.band--sage{--band:#dde9df;}
.band--mint{--band:#e9f3ec;}
.band--green{--band:#1b4d31;background:linear-gradient(180deg,#1f5738,#134528);box-shadow:0 0 0 100vmax #17492d;}
.band--first{padding-top:90px !important;}
.band--sage .shelf-tile{box-shadow:0 40px 70px -40px rgba(19,69,40,.6);}
.band--mint .foot{margin-top:90px;}
.hero__tint{background:
  linear-gradient(180deg,rgba(6,39,7,.72) 0%,rgba(6,39,7,.18) 30%,rgba(6,39,7,.55) 70%,rgba(6,39,7,.92) 100%),
  linear-gradient(90deg,rgba(6,39,7,.75),rgba(6,39,7,0) 60%);}
/* a gold hairline where the banner meets the first band */
.hero::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:linear-gradient(90deg,transparent,#c9a961 20%,#e2c77f 50%,#c9a961 80%,transparent);}
""" + DARK_BAND
    i, c, d, t, q = sections()
    body = (hero() + tag(i, "band band--white band--first") + tag(c, "band band--sage") + tag(d, "band band--white")
            + tag(t, "band band--green") + tag(q, "band band--mint"))
    return build(css, '<div class="page">' + body + '</div>')

# ---------------------------------------------------------------- 3 · Mint watercolour
def watercolour():
    css = """
/* soft white with pools of mint and sage for the glass to catch; the banner fades straight into it */
.page{background:#f7f7f2;}
.pools{position:absolute;inset:0;pointer-events:none;overflow:hidden;}
.pools i{position:absolute;border-radius:50%;}
.content{position:relative;}
.glass{background:linear-gradient(145deg,rgba(255,255,255,.55),rgba(255,255,255,.3));border:1px solid rgba(255,255,255,.85);
  -webkit-backdrop-filter:blur(26px) saturate(1.5);backdrop-filter:blur(26px) saturate(1.5);
  box-shadow:inset 0 1px 0 #fff,0 30px 60px -36px rgba(19,69,40,.45);}
.gb{background:linear-gradient(160deg,rgba(255,255,255,.6),rgba(255,255,255,.32));-webkit-backdrop-filter:blur(26px) saturate(1.5);backdrop-filter:blur(26px) saturate(1.5);}
.hero__tint{background:
  linear-gradient(180deg,rgba(6,39,7,.72) 0%,rgba(6,39,7,.2) 28%,rgba(19,69,40,.62) 62%,rgba(19,69,40,.9) 86%,rgba(120,160,132,.9) 94%,#f7f7f2 100%),
  linear-gradient(90deg,rgba(6,39,7,.7),rgba(6,39,7,0) 60%);}
"""
    pools = [  # left, top, size, colour
        ("58%", 640, 1000, "rgba(185,228,208,1)"),
        ("-22%", 1300, 1100, "rgba(158,200,172,.85)"),
        ("62%", 2200, 1100, "rgba(140,188,156,.7)"),
        ("-16%", 3100, 1000, "rgba(185,228,208,1)"),
        ("58%", 3800, 1050, "rgba(214,228,178,.85)"),
        ("-14%", 4500, 1100, "rgba(150,196,165,.75)"),
    ]
    blobs = "".join(f'<i style="left:{l};top:{t}px;width:{s}px;height:{s}px;background:radial-gradient(closest-side,{c},transparent)"></i>' for l, t, s, c in pools)
    return build(css, '<div class="page"><div class="pools">' + blobs + '</div><div class="content">' + hero() + "".join(sections()) + '</div></div>')

# ---------------------------------------------------------------- 3 revised
def watercolour_mounted():
    css = """
.page{background:#f7f7f2;}
.pools{position:absolute;inset:0;pointer-events:none;overflow:hidden;}
.pools i{position:absolute;border-radius:50%;}
.content{position:relative;}
/* the pools now live in the side margins, and the cards are near-opaque, so no tint crosses the information */
.glass{background:linear-gradient(145deg,rgba(255,255,255,.94),rgba(255,255,255,.86));border:1px solid rgba(19,69,40,.08);
  box-shadow:inset 0 1px 0 #fff,0 30px 60px -36px rgba(19,69,40,.4);}
.gb{background:linear-gradient(160deg,rgba(255,255,255,.95),rgba(255,255,255,.86));}
.hero__tint{background:
  linear-gradient(180deg,rgba(6,39,7,.72) 0%,rgba(6,39,7,.2) 28%,rgba(19,69,40,.62) 62%,rgba(19,69,40,.9) 86%,rgba(120,160,132,.9) 94%,#f7f7f2 100%),
  linear-gradient(90deg,rgba(6,39,7,.7),rgba(6,39,7,0) 60%);}

/* ---- the shelf runs edge to edge, bolted to the wall top and bottom ---- */
.shelf-tile{position:relative;margin-inline:calc(590px - 50vw);border-radius:0;padding:64px calc(50vw - 590px) 70px;
  background:
    linear-gradient(180deg,#6b5230 0,#4a3820 22px,#2c2114 34px,#221a0f calc(100% - 34px),#3a2c16 calc(100% - 22px),#5b4627 100%);
  box-shadow:0 -1px 0 rgba(255,235,200,.25) inset,0 40px 70px -40px rgba(19,69,40,.55),0 -18px 40px -30px rgba(19,69,40,.35);}
.shelf-tile::before,.shelf-tile::after{content:"";position:absolute;left:0;right:0;height:1px;background:rgba(0,0,0,.45);}
.shelf-tile::before{top:34px;} .shelf-tile::after{bottom:34px;}
.bolts{position:absolute;left:28px;right:28px;display:flex;justify-content:space-between;pointer-events:none;}
.bolts--top{top:10px;} .bolts--bottom{bottom:10px;}
.bolts i{width:14px;height:14px;border-radius:50%;position:relative;
  background:radial-gradient(circle at 35% 30%,#f5e2ae,#c9a961 45%,#7d6224 100%);
  box-shadow:0 1px 2px rgba(0,0,0,.6),inset 0 -1px 1px rgba(0,0,0,.35);}
.bolts i::after{content:"";position:absolute;left:3px;right:3px;top:50%;height:1.5px;margin-top:-.75px;background:rgba(60,40,10,.7);transform:rotate(var(--r,35deg));}
.bolts i:nth-child(2n)::after{--r:-20deg;} .bolts i:nth-child(3n)::after{--r:80deg;}

/* ---- details on green, as on the dark pages ---- */
.details-green .glass{background:linear-gradient(160deg,#1b5a37,#0f3b21);border:1px solid rgba(217,190,120,.35);color:#f4efe2;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 30px 60px -30px rgba(6,39,7,.55);}
.details-green .tile:hover{border-color:rgba(217,190,120,.6);}
.details-green .tile__k{color:#d9be78;}
.details-green .tgroup+.tgroup{border-color:rgba(217,190,120,.2);}
.details-green .tgroup__h b,.details-green .fee__amt{color:#fbf6e9;}
.details-green .tgroup__h span{color:#d9be78;}
.details-green .fee__amt small{color:rgba(244,239,226,.65);}
.details-green .trow{color:rgba(244,239,226,.85);} .details-green .trow .t{color:#f0dca6;}
.details-green .drow{border-color:rgba(217,190,120,.16);} .details-green .drow b{color:#f0dca6;}
.details-green .fee-l{color:rgba(244,239,226,.7) !important;}
.details-green .fee-split{border-color:rgba(217,190,120,.2) !important;}
"""
    # tall pools anchored to the left and right edges: their soft ends stop at the card column
    pools = [  # side, top, colour
        ("l", 900, "rgba(185,228,208,1)"), ("r", 1100, "rgba(158,200,172,.9)"),
        ("l", 3300, "rgba(158,200,172,.85)"), ("r", 3500, "rgba(185,228,208,1)"),
        ("l", 4300, "rgba(214,228,178,.9)"), ("r", 4600, "rgba(150,196,165,.8)"),
    ]
    blobs = "".join(
        f'<i style="{"left:-250px" if side == "l" else "right:-250px"};top:{t}px;width:440px;height:1000px;background:radial-gradient(closest-side,{c},transparent)"></i>'
        for side, t, c in pools)
    bolts = lambda where: f'<div class="bolts bolts--{where}">' + "<i></i>" * 12 + '</div>'
    i, c, d, t, q = sections()
    c = c.replace('<div class="shelf-tile rv">', '<div class="shelf-tile rv">' + bolts("top"), 1)
    c = c[:c.rindex('</div>')] + bolts("bottom") + '</div>' + c[c.rindex('</div>') + 6:]
    d = tag(d, "details-green")
    return build(css, '<div class="page"><div class="pools">' + blobs + '</div><div class="content">' + hero() + i + c + d + t + q + '</div></div>')

def main():
    preview = "--preview" in sys.argv
    files = {
        "LightSageWash.dc.html": sage_wash(),
        "LightBands.dc.html": bands(),
        "LightWatercolour.dc.html": watercolour(),
        "WatercolourMounted.dc.html": watercolour_mounted(),
    }
    os.makedirs(OUT, exist_ok=True)
    for name, src in files.items():
        open(os.path.join(OUT, name.replace(".dc.html", ".html") if preview else name), "w").write(src)
    print("wrote", len(files), "to", OUT)

if __name__ == "__main__":
    main()

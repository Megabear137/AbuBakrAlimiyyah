#!/usr/bin/env python3
"""Combined directions: 1's banner, background and teachers; 2's bookshelf;
6's testimonies. Three takes, each with a different traditional binding and a
different arrangement of the sections the brief left open (intro, details).

    python3 generate_combined.py [outdir] [--preview]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as g

OUT = next((a for a in sys.argv[1:] if not a.startswith("--")), os.path.dirname(os.path.abspath(__file__)))

GILT = "#c9a457"

# ---------------------------------------------------------- traditional books
# Per book: title lines for a horizontal label, width, height, and a binding
# colour for each of the three traditions.
BOOKS = [
    dict(t="Achi Baatain",     lines=["Achi", "Baatain"],    s="Urdu"),
    dict(t="Tasheel ul-Nahwa", lines=["Tasheel", "ul-Nahwa"], s="Nahwa"),
    dict(t="Tasheel ul-Sarf",  lines=["Tasheel", "ul-Sarf"],  s="Sarf"),
    dict(t="Duroos 1",         lines=["Duroos", "I"],         s="Arabic"),
    dict(t="Qasas 1",          lines=["Qasas", "I"],          s="Arabic"),
]
ANTIQUE = [  # (width, height, leather, label, second label)
    (60, 244, "#4f1a14", "#1b1512", "#6d2419"),
    (66, 252, "#3d2a18", "#6d2419", "#1b1512"),
    (58, 236, "#23301f", "#6d2419", "#1b1512"),
    (64, 248, "#6a4524", "#1d3524", "#6d2419"),
    (56, 230, "#2a1d16", "#6d2419", "#3d2a18"),
]
KITAB = [  # (width, height, leather, cartouche ground)
    (48, 254, "#4a1813", "#1a1210"),
    (54, 268, "#2c1d13", "#5a1916"),
    (48, 262, "#1c2a22", "#4a1813"),
    (52, 256, "#5e3b1f", "#1c2a22"),
    (46, 240, "#16120f", "#5a1916"),
]
PRESS = [  # (width, height, cloth, paper label?)
    (44, 238, "#5b1e1e", False),
    (50, 250, "#1f3a2b", False),
    (42, 232, "#1d2438", False),
    (48, 244, "#4d3520", True),
    (44, 226, "#1b1a18", True),
]

BOOK_CSS = """
/* ======================================= traditional bindings ===== */
.tb{--gilt:""" + GILT + """;--grain:""" + g.GRAIN + """;
  position:relative;flex:none;width:var(--w);height:var(--h);display:flex;flex-direction:column;color:var(--gilt);cursor:pointer;
  border-radius:3px 3px 2px 2px;transform-origin:0% 100%;
  transition:transform .55s cubic-bezier(.2,.8,.2,1),box-shadow .55s;
  box-shadow:inset 0 1px 0 rgba(255,235,200,.14),inset 0 -1px 0 rgba(0,0,0,.45),4px 0 8px -3px rgba(0,0,0,.55);}
.tb:hover{transform:translateY(-10px) rotate(-6deg);z-index:3;box-shadow:inset 0 1px 0 rgba(255,235,200,.14),12px 14px 22px -8px rgba(0,0,0,.65);}
.tb.is-tilt{transform:translateY(-10px) rotate(-6deg);z-index:3;box-shadow:inset 0 1px 0 rgba(255,235,200,.14),12px 14px 22px -8px rgba(0,0,0,.65);}
.gilt-text{background:linear-gradient(180deg,#f0d69a,#c79d4c 55%,#e6c687);-webkit-background-clip:text;background-clip:text;color:transparent;}

/* --- A · antiquarian calf: five raised bands, six tooled compartments, two labels --- */
.tb--antique{background:
    linear-gradient(180deg,rgba(225,195,145,.2),transparent 5%,transparent 95%,rgba(225,195,145,.16)),
    radial-gradient(18px 30px at 20% 62%,rgba(225,195,145,.10),transparent),
    radial-gradient(14px 22px at 75% 30%,rgba(0,0,0,.18),transparent),
    linear-gradient(90deg,rgba(0,0,0,.55),rgba(0,0,0,.06) 12%,rgba(255,235,200,.09) 34%,rgba(0,0,0,.03) 58%,rgba(0,0,0,.5)),
    var(--grain),var(--c);
  background-blend-mode:normal,normal,normal,normal,overlay,normal;}
.tb--antique .tb__cap{flex:0 0 10px;position:relative;background:linear-gradient(180deg,rgba(225,195,145,.22),rgba(0,0,0,.3));border-radius:3px 3px 0 0;}
.tb--antique .tb__cap::before{content:"";position:absolute;left:5px;right:5px;top:-3px;height:3px;border-radius:2px 2px 0 0;
  background:repeating-linear-gradient(90deg,#2d4a6b 0 2px,#e6d4a4 2px 4px);}
.tb--antique .tb__cap--tail{background:linear-gradient(0deg,rgba(225,195,145,.2),rgba(0,0,0,.28));border-radius:0 0 2px 2px;}
.tb--antique .tb__cap--tail::before{display:none;}
.tb__band{flex:0 0 8px;margin:0 -2px;position:relative;border-radius:4px;
  background:linear-gradient(180deg,rgba(0,0,0,.45),rgba(255,235,200,.26) 45%,rgba(0,0,0,.5)),var(--c);box-shadow:0 1px 2px rgba(0,0,0,.5);}
.tb__band::before{content:"";position:absolute;left:4px;right:4px;top:50%;height:1px;margin-top:-.5px;
  background:repeating-linear-gradient(90deg,var(--gilt) 0 1.5px,transparent 1.5px 3.5px);}
.tb__band::after{content:"";position:absolute;left:5px;right:5px;top:-4px;bottom:-4px;border-top:1px solid var(--gilt);border-bottom:1px solid var(--gilt);opacity:.8;}
.tb__comp{flex:1 1 0;position:relative;margin:0 3px;}
.tb__comp--sm{flex:.6 1 0;}
.tb__comp::before{content:"";position:absolute;inset:6px 3px;border:1px solid var(--gilt);opacity:.45;}
.tb__comp::after{content:"";position:absolute;left:50%;top:50%;width:9px;height:9px;margin:-4.5px 0 0 -4.5px;transform:rotate(45deg);
  border:1px solid var(--gilt);
  background:radial-gradient(circle,var(--gilt) 1.2px,transparent 1.6px),
    radial-gradient(circle at 0 0,var(--gilt) 1.2px,transparent 1.6px),radial-gradient(circle at 100% 0,var(--gilt) 1.2px,transparent 1.6px),
    radial-gradient(circle at 0 100%,var(--gilt) 1.2px,transparent 1.6px),radial-gradient(circle at 100% 100%,var(--gilt) 1.2px,transparent 1.6px);}
.tb__comp--label{flex:0 0 48px;} .tb__comp--label2{flex:0 0 30px;}
.tb__comp--label::before,.tb__comp--label::after,.tb__comp--label2::before,.tb__comp--label2::after{display:none;}
.tb__lab{position:absolute;inset:5px 1px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;
  background:linear-gradient(90deg,rgba(0,0,0,.4),rgba(255,235,200,.08) 40%,rgba(0,0,0,.3)),var(--lab);
  box-shadow:inset 0 0 0 1px rgba(0,0,0,.5),0 0 0 .5px rgba(0,0,0,.4);
  font:700 8.8px/1.18 "Cormorant Garamond",Garamond,serif;letter-spacing:.05em;text-transform:uppercase;}
.tb__lab::before,.tb__lab::after{content:"";position:absolute;left:3px;right:3px;height:1px;background:var(--gilt);opacity:.85;}
.tb__lab::before{top:3px;} .tb__lab::after{bottom:3px;}
.tb__lab--2{background:linear-gradient(90deg,rgba(0,0,0,.4),rgba(255,235,200,.06) 40%,rgba(0,0,0,.3)),var(--lab2);font-size:9px;font-style:italic;font-weight:700;text-transform:none;letter-spacing:.03em;}
.tb__lab span{text-shadow:0 .6px 0 rgba(0,0,0,.6);}

/* --- B · Islamic kitab: flat goatskin spine, gilt frame, pointed cartouche, chevron headband --- */
.tb--kitab{align-items:center;padding:14px 0 10px;gap:5px;background:
    linear-gradient(180deg,rgba(225,195,145,.12),transparent 6%,transparent 94%,rgba(225,195,145,.12)),
    linear-gradient(90deg,rgba(0,0,0,.6),rgba(0,0,0,.1) 14%,rgba(255,235,200,.1) 38%,rgba(0,0,0,.05) 62%,rgba(0,0,0,.55)),
    var(--grain),var(--c);
  background-blend-mode:normal,normal,soft-light,normal;border-radius:2px;}
.tb--kitab::before{content:"";position:absolute;left:5px;right:5px;top:-4px;height:4px;border-radius:2px 2px 0 0;
  background:linear-gradient(135deg,#8a2a20 25%,transparent 25%) -2px 0/4px 4px,linear-gradient(225deg,#8a2a20 25%,transparent 25%) -2px 0/4px 4px,
    linear-gradient(315deg,#1f4a3a 25%,transparent 25%) 0 0/4px 4px,linear-gradient(45deg,#1f4a3a 25%,transparent 25%) 0 0/4px 4px,#e3cf98;}
.tb--kitab::after{content:"";position:absolute;inset:6px 5px;border:1px solid var(--gilt);opacity:.75;
  box-shadow:inset 0 0 0 2px transparent,inset 0 0 0 3px rgba(201,164,87,.5);pointer-events:none;}
.tb__fin{flex:none;width:10px;height:12px;position:relative;}
.tb__fin::before{content:"";position:absolute;left:50%;top:0;bottom:4px;width:1px;background:var(--gilt);}
.tb__fin::after{content:"";position:absolute;left:50%;bottom:0;width:6px;height:6px;margin-left:-3px;transform:rotate(45deg);background:var(--gilt);}
.tb__fin--b{transform:scaleY(-1);}
.tb__fin--top{margin-top:4px;}
.tb__cart{flex:1 1 auto;width:calc(var(--w) - 16px);position:relative;background:var(--gilt);
  clip-path:polygon(50% 0,100% 12%,100% 88%,50% 100%,0 88%,0 12%);}
.tb__cart-in{position:absolute;inset:1.5px;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(90deg,rgba(0,0,0,.35),rgba(255,235,200,.06) 45%,rgba(0,0,0,.3)),var(--lab);
  clip-path:polygon(50% 0,100% 12%,100% 88%,50% 100%,0 88%,0 12%);}
.tb__cart-in::before{content:"";position:absolute;inset:3px;border:1px solid var(--gilt);opacity:.5;clip-path:polygon(50% 0,100% 12%,100% 88%,50% 100%,0 88%,0 12%);}
.tb__vt{writing-mode:vertical-rl;font:700 11.5px/1 "Cormorant Garamond",Garamond,serif;letter-spacing:.02em;white-space:nowrap;}
.tb__sub{flex:none;writing-mode:vertical-rl;font:italic 600 9.5px/1 "Cormorant Garamond",serif;letter-spacing:.1em;opacity:.9;height:34px;display:flex;align-items:center;}
.tb__medal{flex:none;width:12px;height:12px;border-radius:50%;border:1px solid var(--gilt);position:relative;margin-bottom:6px;}
.tb__medal::after{content:"";position:absolute;inset:2.5px;border-radius:50%;background:var(--gilt);}

/* --- C · madrasa press: book-cloth, blocked gilt rules and a chain roll, some with a paper label --- */
.tb--press{align-items:stretch;padding:0;background:
    linear-gradient(180deg,rgba(235,215,170,.18),transparent 22%),
    linear-gradient(90deg,rgba(0,0,0,.5),rgba(0,0,0,.05) 12%,rgba(255,240,210,.08) 36%,rgba(0,0,0,.04) 60%,rgba(0,0,0,.48)),
    repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 1px,transparent 1px 3px),
    repeating-linear-gradient(90deg,rgba(0,0,0,.07) 0 1px,transparent 1px 3px),var(--grain),var(--c);
  background-blend-mode:normal,normal,normal,normal,soft-light,normal;
  border-radius:2px 2px 1px 1px;}
.tb--press::before{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;
  background:radial-gradient(10px 8px at 0 0,rgba(235,215,170,.3),transparent),radial-gradient(10px 8px at 100% 0,rgba(235,215,170,.3),transparent),
    radial-gradient(10px 8px at 0 100%,rgba(235,215,170,.22),transparent),radial-gradient(10px 8px at 100% 100%,rgba(235,215,170,.22),transparent);}
.tb__rules{flex:0 0 10px;margin:12px 4px 0;background:
  linear-gradient(var(--gilt),var(--gilt)) 0 0/100% 1.6px no-repeat,
  linear-gradient(var(--gilt),var(--gilt)) 0 4px/100% .8px no-repeat,
  linear-gradient(var(--gilt),var(--gilt)) 0 8px/100% 1.6px no-repeat;}
.tb__rules--b{margin:0 4px 12px;transform:scaleY(-1);}
.tb__chain{flex:0 0 9px;margin:4px 5px;background:
  radial-gradient(circle,var(--gilt) 1.3px,transparent 1.8px) 0 50%/6px 9px repeat-x,
  linear-gradient(var(--gilt),var(--gilt)) 0 1px/100% .8px no-repeat,linear-gradient(var(--gilt),var(--gilt)) 0 7px/100% .8px no-repeat;}
.tb__press-t{flex:1 1 auto;display:flex;align-items:center;justify-content:center;margin:6px 0;}
.tb__press-t span{writing-mode:vertical-rl;font:700 13px/1 "Cormorant Garamond",Garamond,serif;letter-spacing:.07em;white-space:nowrap;}
.tb__paper{margin:6px 0;padding:9px 6px;background:linear-gradient(90deg,#cdbf9f,#e9dfc6 40%,#d6c8a7);color:#3b2a1a;border-radius:1px;
  box-shadow:0 0 0 1px rgba(60,40,20,.35),inset 0 0 0 2px #e9dfc6,inset 0 0 0 2.8px rgba(90,40,30,.55);}
.tb__paper span{color:#3b2a1a;background:none;-webkit-background-clip:border-box;background-clip:border-box;}
.tb__press-s{flex:0 0 34px;display:flex;align-items:center;justify-content:center;writing-mode:vertical-rl;font:italic 600 9.5px/1 "Cormorant Garamond",serif;letter-spacing:.1em;}

.tb-ghost{flex:none;width:var(--w);height:var(--h);border:1.5px dashed rgba(201,169,97,.4);border-radius:3px;display:flex;align-items:center;justify-content:center;background:rgba(201,169,97,.035);}
.tb-ghost span{writing-mode:vertical-rl;font:italic 500 10px/1 "Cormorant Garamond",serif;letter-spacing:.24em;color:rgba(201,169,97,.6);}
"""

def antique(i, tilt=False):
    b = BOOKS[i]; w, h, c, lab, lab2 = ANTIQUE[i]
    lines = "".join(f'<span class="gilt-text">{l}</span>' for l in b["lines"])
    return (f'<div class="tb tb--antique{" is-tilt" if tilt else ""}" style="--w:{w}px;--h:{h}px;--c:{c};--lab:{lab};--lab2:{lab2}" title="{b["t"]}">'
            '<span class="tb__cap"></span><span class="tb__comp"></span><span class="tb__band"></span>'
            f'<span class="tb__comp tb__comp--label"><span class="tb__lab">{lines}</span></span><span class="tb__band"></span>'
            '<span class="tb__comp"></span><span class="tb__band"></span>'
            f'<span class="tb__comp tb__comp--label2"><span class="tb__lab tb__lab--2"><span class="gilt-text">{b["s"]}</span></span></span><span class="tb__band"></span>'
            '<span class="tb__comp"></span><span class="tb__band"></span><span class="tb__comp tb__comp--sm"></span>'
            '<span class="tb__cap tb__cap--tail"></span></div>')

def kitab(i, tilt=False):
    b = BOOKS[i]; w, h, c, lab = KITAB[i]
    return (f'<div class="tb tb--kitab{" is-tilt" if tilt else ""}" style="--w:{w}px;--h:{h}px;--c:{c};--lab:{lab}" title="{b["t"]}">'
            '<span class="tb__fin tb__fin--top"></span>'
            f'<span class="tb__cart"><span class="tb__cart-in"><span class="tb__vt gilt-text">{b["t"]}</span></span></span>'
            '<span class="tb__fin tb__fin--b"></span>'
            f'<span class="tb__sub">{b["s"]}</span><span class="tb__medal"></span></div>')

def press(i, tilt=False):
    b = BOOKS[i]; w, h, c, paper = PRESS[i]
    title = (f'<span class="tb__press-t"><span class="tb__paper"><span style="writing-mode:vertical-rl;font:700 12.5px/1 \'Cormorant Garamond\',serif;letter-spacing:.05em;white-space:nowrap">{b["t"]}</span></span></span>'
             if paper else f'<span class="tb__press-t"><span class="gilt-text">{b["t"]}</span></span>')
    return (f'<div class="tb tb--press{" is-tilt" if tilt else ""}" style="--w:{w}px;--h:{h}px;--c:{c}" title="{b["t"]}">'
            '<span class="tb__rules"></span><span class="tb__chain"></span>'
            f'{title}'
            '<span class="tb__chain"></span>'
            f'<span class="tb__press-s gilt-text">{b["s"]}</span>'
            '<span class="tb__rules tb__rules--b"></span></div>')

def tghost(w, h):
    return f'<div class="tb-ghost" style="--w:{w}px;--h:{h}px"><span>TODO</span></div>'

MAKERS = {"antique": antique, "kitab": kitab, "press": press}
GHOST_W = {"antique": (62, 56), "kitab": (50, 46), "press": (46, 42)}

def year_books(style, i, tilt_idx=None):
    mk = MAKERS[style]; gw = GHOST_W[style]
    if i == 1:
        return "".join(mk(j, j == tilt_idx) for j in range(5)) + tghost(gw[1], 232)
    return tghost(gw[0], 240) + tghost(gw[1], 226)

def shelf(style, tilt_idx=None):
    """Mockup 2's walnut shelf: seven bays, two to a board, the seventh alone."""
    rows = []
    for r in range(4):
        idx = [r * 2, r * 2 + 1] if r < 3 else [6]
        bays = "".join(
            f'<div class="w-bay"><div class="w-well">{year_books(style, i, tilt_idx)}</div><div class="w-plank"></div>'
            f'<div class="w-tag"><span>{g.ROMAN[i]}</span>{g.YEARS[i]}</div></div>' for i in idx)
        rows.append(f'<div class="w-row{" w-row--one" if r == 3 else ""} rv{" rv2" if r % 2 else ""}">{bays}</div>')
    return "".join(rows)

# ------------------------------------------------------------------ page css
PAGE_CSS = """
body{background:#041d08;color:#f4efe2;font-family:"Instrument Sans",system-ui,sans-serif;font-size:16px;line-height:1.6;}
/* 1's ground: deep green with soft gold and green glows for the glass to catch */
.page{position:relative;overflow:hidden;
  background:radial-gradient(900px 700px at 12% 1250px,rgba(201,169,97,.16),transparent 70%),
             radial-gradient(800px 800px at 92% 2100px,rgba(47,122,78,.45),transparent 70%),
             radial-gradient(700px 600px at 20% 3300px,rgba(47,122,78,.4),transparent 70%),
             radial-gradient(900px 700px at 85% 4300px,rgba(201,169,97,.12),transparent 70%),
             radial-gradient(800px 700px at 15% 5200px,rgba(47,122,78,.35),transparent 70%),
             linear-gradient(180deg,#062707,#041d08);}
.glass{background:linear-gradient(145deg,rgba(255,255,255,.085),rgba(255,255,255,.025));
  -webkit-backdrop-filter:blur(22px) saturate(1.3);backdrop-filter:blur(22px) saturate(1.3);
  border:1px solid rgba(217,190,120,.28);border-radius:26px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 24px 60px -24px rgba(0,0,0,.55);}

/* ---- 1's banner ---- */
.hero{position:relative;height:860px;overflow:hidden;}
.hero__img{position:absolute;inset:0;background:url(./masjid.jpg) center 30%/cover;filter:saturate(.75) contrast(1.05);}
.hero__tint{position:absolute;inset:0;background:
  linear-gradient(180deg,rgba(6,39,7,.72) 0%,rgba(6,39,7,.18) 30%,rgba(6,39,7,.55) 62%,#062707 100%),
  linear-gradient(90deg,rgba(6,39,7,.75),rgba(6,39,7,0) 60%);}
.nav{position:absolute;z-index:5;top:26px;left:0;right:0;margin:0 auto;width:1240px;height:66px;padding:0 12px 0 16px;
  display:flex;align-items:center;justify-content:space-between;border-radius:999px;}
.brand{display:flex;align-items:center;gap:12px;font:600 20px/1 "Cormorant Garamond",serif;color:#f4efe2;}
.brand img{width:40px;height:40px;}
.nav__links{display:flex;gap:6px;}
.nav__a{padding:9px 16px;border-radius:999px;color:rgba(244,239,226,.82);font-size:14.5px;}
.nav__a:first-child{background:rgba(217,190,120,.16);color:#f0dca6;}
.btn{display:inline-flex;align-items:center;gap:10px;height:52px;padding:0 26px;border-radius:999px;font-weight:600;font-size:15px;}
.btn--gold{background:linear-gradient(180deg,#e0c57f,#c29e52);color:#062707;box-shadow:0 10px 30px -10px rgba(201,169,97,.7);}
.btn--gold:hover{color:#062707;}
.btn--sm{height:46px;padding:0 20px;font-size:14px;}
.hero__body{position:absolute;left:100px;bottom:120px;width:780px;z-index:2;}
.eyebrow{display:inline-flex;align-items:center;gap:12px;color:#d9be78;font-size:13px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;}
.eyebrow::before{content:"";width:34px;height:1px;background:#c9a961;}
.hero h1{font:600 104px/.94 "Cormorant Garamond",serif;letter-spacing:-.01em;margin:22px 0 26px;color:#fbf6e9;text-wrap:balance;}
.hero h1 em{font-style:italic;color:#e2c77f;font-weight:500;}
.hero__sub{font-size:19px;color:rgba(244,239,226,.85);max-width:560px;margin-bottom:36px;}
.hero__card{position:absolute;right:100px;bottom:120px;width:330px;padding:24px 26px;z-index:2;}
.hero__card h4{font:600 13px/1 "Instrument Sans",sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#d9be78;margin-bottom:16px;}
.split{display:flex;gap:4px;margin-bottom:14px;}
.split i{flex:1;height:8px;border-radius:4px;background:rgba(201,169,97,.85);}
.split i.ft{background:#f4efe2;}
.legend{display:flex;justify-content:space-between;font-size:14px;color:rgba(244,239,226,.8);}
.legend b{display:block;font:600 26px/1.1 "Cormorant Garamond",serif;color:#fbf6e9;}

.sec{padding:120px 0 0;}
.sec__head{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:40px;gap:40px;}
.sec__head h2{font:600 60px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.sec__head h2 em{font-weight:500;color:#e2c77f;}
.sec__head p{max-width:420px;color:rgba(244,239,226,.7);font-size:15.5px;}
.bento{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:20px;}
.tile{padding:34px 36px;transition:transform .4s cubic-bezier(.2,.8,.2,1),border-color .4s;}
.tile:hover{transform:translateY(-4px);border-color:rgba(217,190,120,.55);}
.tile__k{font-size:12.5px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#d9be78;margin-bottom:18px;}
.lead{font:500 34px/1.28 "Cormorant Garamond",serif;color:#fbf6e9;text-wrap:pretty;}
.muted{color:rgba(244,239,226,.8);font-size:17px;}

/* ---- 2's bookshelf ---- */
.shelf-tile{border-radius:30px;padding:40px;background:linear-gradient(180deg,#2c2114,#1c150b);box-shadow:0 40px 80px -40px rgba(0,0,0,.7),inset 0 1px 0 rgba(255,235,200,.08);}
.sh{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:28px;color:#f4efe2;}
.sh h2{font:600 64px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.sh p{max-width:400px;color:rgba(244,239,226,.65);font-size:15px;}
.sh .tile__k{margin-bottom:10px;}
.w-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:16px;}
.w-row--one{grid-template-columns:minmax(0,1fr);}
.w-bay{position:relative;border-radius:18px;padding:10px 10px 0;
  background:linear-gradient(180deg,#5b4627,#45351e 50%,#372a14);box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 12px 24px -12px rgba(0,0,0,.6);}
.w-well{height:300px;border-radius:10px 10px 0 0;display:flex;align-items:flex-end;justify-content:center;gap:3px;padding:0 20px;
  background:radial-gradient(60% 70% at 50% 0%,rgba(255,222,150,.18),transparent 70%),linear-gradient(180deg,#0b2410,#062707);
  box-shadow:inset 0 10px 24px rgba(0,0,0,.6),inset 0 -2px 0 rgba(0,0,0,.4);}
.w-plank{height:14px;margin:0 -10px;background:linear-gradient(180deg,#7a5e36,#5b4627 40%,#3a2c16);box-shadow:0 -1px 0 rgba(255,255,255,.18) inset;}
.w-tag{height:46px;display:flex;align-items:center;justify-content:center;gap:10px;font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#e9d59c;}
.w-tag span{color:#c9a961;font-family:"Cormorant Garamond",serif;font-size:17px;letter-spacing:0;}

/* ---- details ---- */
.fee__amt{font:600 76px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.fee__amt small{font:500 16px/1 "Instrument Sans",sans-serif;color:rgba(244,239,226,.65);margin-left:6px;}
.fee__note{color:rgba(244,239,226,.6);font-size:14px;margin-top:8px;}
.tgroup+.tgroup{margin-top:28px;padding-top:28px;border-top:1px solid rgba(217,190,120,.2);}
.tgroup__h{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:12px;}
.tgroup__h b{font:600 32px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.tgroup__h span{font-size:13px;color:#d9be78;letter-spacing:.08em;}
.trow{display:flex;justify-content:space-between;align-items:center;padding:12px 0;font-size:16px;color:rgba(244,239,226,.85);}
.trow .t{display:inline-flex;align-items:center;gap:8px;color:#f0dca6;font-variant-numeric:tabular-nums;}
.drow{display:flex;justify-content:space-between;align-items:center;padding:13px 0;border-top:1px solid rgba(217,190,120,.16);font-size:16px;}
.drow:first-of-type{border-top:0;}
.drow b{font-weight:600;color:#f0dca6;}

/* ---- 1's teachers ---- */
.teach{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;}
.tcard{padding:32px;display:flex;flex-direction:column;gap:16px;min-height:250px;}
.mono{width:64px;height:64px;border-radius:50%;display:grid;place-items:center;font:600 24px/1 "Cormorant Garamond",serif;color:#062707;
  background:linear-gradient(145deg,#e6cc88,#b8924a);box-shadow:0 0 0 5px rgba(217,190,120,.14);}
.tcard small{color:#d9be78;font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;font-weight:600;}
.tcard h3{font:600 32px/1.05 "Cormorant Garamond",serif;color:#fbf6e9;}
.tcard p{color:rgba(244,239,226,.7);font-size:15px;}
.ctrls{display:flex;gap:10px;}
.cbtn{width:48px;height:48px;border-radius:50%;display:grid;place-items:center;color:#e2c77f;}

/* ---- 6's testimonies ---- */
.gb{position:relative;border-radius:24px;background:linear-gradient(160deg,rgba(255,255,255,.07),rgba(255,255,255,.02));
  -webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px);}
.gb::after{content:"";position:absolute;inset:0;border-radius:inherit;padding:1px;pointer-events:none;
  background:linear-gradient(135deg,rgba(226,199,127,.95),rgba(226,199,127,.1) 35%,rgba(226,199,127,.1) 65%,rgba(226,199,127,.75));
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;}
.q6{padding:32px;margin:0;transition:transform .45s cubic-bezier(.2,.8,.2,1);}
.q6:hover{transform:translateY(-5px);}
.q6 p{font:italic 500 29px/1.32 "Cormorant Garamond",serif;color:#fbf6e9;margin:14px 0 22px;}
.q6 cite{font-style:normal;color:rgba(244,239,226,.72);} .q6 cite b{color:#f0dca6;}

.soon{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;margin-top:20px;}
.soon .tile{display:flex;justify-content:space-between;align-items:center;}
.soon h3{font:600 34px/1 "Cormorant Garamond",serif;color:#fbf6e9;margin-bottom:6px;}
.soon p{color:rgba(244,239,226,.6);font-size:15px;}
.pill{font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#d9be78;border:1px solid rgba(217,190,120,.4);border-radius:999px;padding:7px 14px;}
.foot{margin-top:120px;border-top:1px solid rgba(217,190,120,.2);padding:48px 0 56px;display:flex;justify-content:space-between;align-items:center;color:rgba(244,239,226,.62);font-size:14.5px;}
.foot .brand{font-size:22px;}
"""

# ------------------------------------------------------------------ sections
def hero():
    N = g.NAME
    return f"""
<header class="hero">
  <div class="hero__img drift"></div><div class="hero__tint"></div>
  <nav class="nav glass in">
    <a class="brand" href="#"><img src="./logo.png" alt="">{N}</a>
    <div class="nav__links">{g.nav_links("nav__a")}</div>
    <a class="btn btn--gold btn--sm" href="#">View Curriculum</a>
  </nav>
  <div class="hero__body">
    <div class="eyebrow in" style="--d:.15s">{N}</div>
    <h1 class="in" style="--d:.3s">The Seven-Year <em>Alimiyyah</em> Program</h1>
    <p class="hero__sub in" style="--d:.45s">{g.SUB}</p>
    <a class="btn btn--gold in" style="--d:.6s" href="#">View Curriculum {g.ARROW}</a>
  </div>
  <div class="hero__card glass in" style="--d:.8s">
    <h4>Seven years</h4>
    <div class="split"><i></i><i></i><i></i><i></i><i class="ft"></i><i class="ft"></i><i class="ft"></i></div>
    <div class="legend"><div><b>Years I – IV</b>Part-time</div><div style="text-align:right"><b>Years V – VII</b>Full-time</div></div>
  </div>
</header>"""

def curriculum(style, kicker, tilt_idx=3):
    return f"""
<section class="wrap sec">
  <div class="shelf-tile rv">
    <div class="sh"><div><div class="tile__k">{kicker}</div><h2>Curriculum</h2></div><p>Every book in the course stands on the shelf at once. Select a spine to turn it face-on.</p></div>
    {shelf(style, tilt_idx)}
  </div>
</section>"""

def times_html():
    return "".join(
        f'<div class="tgroup"><div class="tgroup__h"><b>{l}</b><span>{y}</span></div>'
        + g.timings_rows("trow", "d", "t", [(d, g.CLOCK + t) for d, t in rows]) + '</div>'
        for l, y, rows in g.TIMINGS)

def disc_html():
    return "".join(f'<div class="drow"><span>{a}</span><b>{b}</b></div>' for a, b in g.DISC)

def teachers():
    cards = "".join(
        f'<div class="tile glass tcard rv{" rv2" if i==1 else " rv3" if i==2 else ""}"><div class="mono">{m}</div><small>{h}</small><h3>{n}</h3>{f"<p>{b}</p>" if b else ""}</div>'
        for i, (h, n, b, m) in enumerate(g.TEACHERS))
    return f"""
<section class="wrap sec">
  <div class="sec__head rv"><h2>Our Teachers</h2><div class="ctrls"><a class="cbtn glass" href="#">{g.ARROW_L}</a><a class="cbtn glass" href="#">{g.ARROW}</a></div></div>
  <div class="teach">{cards}</div>
</section>"""

def testimonies_and_rest():
    qs = "".join(
        f'<figure class="gb q6 rv{" rv2" if i else ""}" style="grid-column:span 6"><span style="color:#c9a961">{g.QUOTE}</span><p>{q}</p><cite><b>{n}</b> · Class of {y}</cite></figure>'
        for i, (q, n, y) in enumerate(g.TESTI))
    return f"""
<section class="wrap sec">
  <div class="sec__head rv"><h2>Alumni <em>Testimonies</em></h2></div>
  <div class="bento" style="gap:16px">{qs}</div>
  <div class="soon">
    <div class="tile glass rv"><div><h3>Articles</h3><p>Writing from our teachers and students.</p></div><span class="pill">Coming soon</span></div>
    <div class="tile glass rv rv2"><div><h3>Videos</h3><p>Recorded lessons and talks.</p></div><span class="pill">Coming soon</span></div>
  </div>
  <footer class="foot"><a class="brand" href="#"><img src="./logo.png" alt="">{g.NAME}</a><span>[Masjid address] · [Email] · [Phone]</span><span>© 2026</span></footer>
</section>"""

# --- the open sections, three ways ---
def intro_bento():
    return f"""
<section class="wrap sec" style="padding-top:40px">
  <div class="bento">
    <div class="tile glass rv" style="grid-column:span 7"><div class="tile__k">Introduction</div><p class="lead">{g.INTRO}</p></div>
    <div class="tile glass rv rv2" style="grid-column:span 5;display:flex;flex-direction:column;justify-content:space-between"><div class="tile__k">Our Program</div><p class="muted">{g.PROGRAM}</p></div>
  </div>
</section>"""

def intro_statement():
    return f"""
<section class="wrap sec" style="padding-top:60px;text-align:center">
  <div class="rv" style="max-width:980px;margin:0 auto">
    <div class="tile__k">Introduction</div>
    <p class="lead" style="font-size:44px;line-height:1.24">{g.INTRO}</p>
  </div>
  <div class="glass rv rv2" style="margin:60px auto 0;max-width:980px;padding:30px 40px;display:grid;grid-template-columns:auto minmax(0,1fr);gap:40px;align-items:center;text-align:left;border-radius:999px">
    <div style="font:600 30px/1 'Cormorant Garamond',serif;color:#e2c77f;font-style:italic;padding-left:14px">Our Program</div>
    <p class="muted" style="font-size:16px">{g.PROGRAM}</p>
  </div>
</section>"""

def intro_split():
    return f"""
<section class="wrap sec" style="padding-top:60px">
  <div class="glass rv" style="padding:56px 60px;display:grid;grid-template-columns:minmax(0,1.15fr) 1px minmax(0,1fr);gap:56px;align-items:center">
    <div><div class="tile__k">Introduction</div><p class="lead">{g.INTRO}</p></div>
    <div style="align-self:stretch;background:linear-gradient(transparent,rgba(217,190,120,.45),transparent)"></div>
    <div><div class="tile__k">Our Program</div><p class="muted">{g.PROGRAM}</p></div>
  </div>
</section>"""

def details_bento():
    return f"""
<section class="wrap sec">
  <div class="sec__head rv"><h2>Details</h2><p>Class timings, monthly fees and the family discount.</p></div>
  <div class="bento">
    <div class="tile glass rv-l" style="grid-column:span 6;grid-row:span 2"><div class="tile__k">Class timings</div>{times_html()}</div>
    <div class="tile glass rv" style="grid-column:span 3"><div class="tile__k">Part-time</div><div class="fee__amt">$125<small>/month</small></div><div class="fee__note">per student</div></div>
    <div class="tile glass rv rv2" style="grid-column:span 3"><div class="tile__k">Full-time</div><div class="fee__amt">$325<small>/month</small></div><div class="fee__note">per student</div></div>
    <div class="tile glass rv-r" style="grid-column:span 6"><div class="tile__k">Family discounts</div>{disc_html()}</div>
  </div>
</section>"""

def details_two_panels():
    return f"""
<section class="wrap sec">
  <div class="sec__head rv"><h2>Details</h2><p>Class timings, monthly fees and the family discount.</p></div>
  <div class="bento">
    <div class="tile glass rv-l" style="grid-column:span 6"><div class="tile__k">Class timings</div>{times_html()}</div>
    <div class="tile glass rv-r" style="grid-column:span 6">
      <div class="tile__k">Fees</div>
      <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;padding-bottom:26px;border-bottom:1px solid rgba(217,190,120,.2);margin-bottom:22px">
        <div><div style="color:rgba(244,239,226,.7);font-size:14px">Part-time</div><div class="fee__amt" style="font-size:64px">$125<small>/month</small></div></div>
        <div><div style="color:rgba(244,239,226,.7);font-size:14px">Full-time</div><div class="fee__amt" style="font-size:64px">$325<small>/month</small></div></div>
      </div>
      <div class="tile__k" style="margin-bottom:6px">Family discounts</div>{disc_html()}
    </div>
  </div>
</section>"""

def details_strip():
    tiles = []
    for l, y, rows in g.TIMINGS:
        rws = "".join(f'<div class="trow" style="flex-direction:column;align-items:flex-start;gap:2px;padding:8px 0"><span>{d}</span><span class="t">{g.CLOCK}{t}</span></div>' for d, t in rows)
        tiles.append(f'<div class="tile glass rv" style="grid-column:span 3"><div class="tile__k">{y}</div><div class="tgroup__h"><b>{l}</b></div>{rws}</div>')
    fees = "".join(f'<div class="tile glass rv rv2" style="grid-column:span 3"><div class="tile__k">{l} fee</div><div class="fee__amt">{a}<small>/month</small></div><div class="fee__note">per student</div></div>' for l, a in g.FEES)
    discs = "".join(f'<div style="flex:1;text-align:center;padding:6px 0"><div style="font:600 44px/1 \'Cormorant Garamond\',serif;color:#e2c77f">{b.split(" ")[0]}</div><div style="color:rgba(244,239,226,.7);font-size:14.5px;margin-top:6px">{a}</div></div>' for a, b in g.DISC)
    return f"""
<section class="wrap sec">
  <div class="sec__head rv"><h2>Details</h2><p>Class timings, monthly fees and the family discount.</p></div>
  <div class="bento">
    {"".join(tiles)}{fees}
    <div class="tile glass rv" style="grid-column:span 12;display:flex;align-items:center;gap:30px">
      <div style="flex:0 0 220px"><div class="tile__k" style="margin-bottom:6px">Family discounts</div><div style="color:rgba(244,239,226,.65);font-size:14.5px">off the total</div></div>
      <div style="flex:1;display:flex;gap:10px;border-left:1px solid rgba(217,190,120,.2);padding-left:20px">{discs}</div>
    </div>
  </div>
</section>"""

# ------------------------------------------------------------------ pages
FONTS = [g.CORM, "Instrument+Sans:wght@400;500;600", g.URDU]

def page(intro, style, kicker, details, tilt_idx=3):
    body = ('<div class="page">' + hero() + intro() + curriculum(style, kicker, tilt_idx) + details()
            + teachers() + testimonies_and_rest() + '</div>')
    return g.doc(PAGE_CSS + BOOK_CSS, body, FONTS)

def bindings_sheet():
    css = """
body{background:#062707;color:#f4efe2;font-family:"Instrument Sans",system-ui,sans-serif;}
.sheet{padding:64px 72px;}
h2{font:600 56px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.sub{color:rgba(244,239,226,.7);margin-top:12px;font-size:16px;max-width:820px;line-height:1.6;}
.set{margin-top:40px;display:grid;grid-template-columns:320px minmax(0,1fr);gap:40px;align-items:center;}
.set h3{font:600 36px/1.05 "Cormorant Garamond",serif;color:#fbf6e9;margin-bottom:10px;}
.set h3 small{display:block;font:600 12.5px "Instrument Sans",sans-serif;letter-spacing:.18em;text-transform:uppercase;color:#d9be78;margin-bottom:8px;}
.set p{color:rgba(244,239,226,.72);font-size:15px;line-height:1.6;}
.stage{border-radius:24px;padding:26px 30px 0;background:radial-gradient(60% 80% at 50% 0%,rgba(255,222,150,.14),transparent 70%),linear-gradient(180deg,#0b2410,#041d06);box-shadow:inset 0 0 0 1px rgba(217,190,120,.2);}
.books{display:flex;justify-content:center;align-items:flex-end;gap:5px;zoom:1.75;}
.plank{height:16px;margin:0 -30px;background:linear-gradient(180deg,#7a5e36,#5b4627 40%,#3a2c16);}
"""
    sets = [
        ("A", "Antiquarian calf", "antique",
         "Five raised bands make six compartments, each framed in gilt with a small tooled flower. Two leather labels carry the title and subject across the spine, the way an old library set is lettered. Rubbed at the head and tail."),
        ("B", "Islamic kitab", "kitab",
         "A flat goatskin spine with no raised bands, as Islamic bindings are made. A double gilt frame runs the length, the title sits in a pointed cartouche between finials, and the headband is a two-colour chevron."),
        ("C", "Madrasa press", "press",
         "Book-cloth like the printed texts used in the dars today: blocked gilt rules and a chain roll at head and foot, titles stamped in gilt or on a pasted paper label, corners bumped with use."),
    ]
    rows = "".join(
        f'<div class="set"><div><h3><small>Mockup {k}</small>{name}</h3><p>{desc}</p></div>'
        f'<div class="stage"><div class="books">{"".join(MAKERS[st](j) for j in range(5))}</div><div class="plank"></div></div></div>'
        for k, name, st, desc in sets)
    body = f"""<div class="sheet"><h2>Traditional bindings</h2>
<p class="sub">One binding tradition per mockup, shown here at nearly twice shelf size with the Second Year books. Hover any spine to lean it out.</p>{rows}</div>"""
    return g.doc(css + BOOK_CSS, body, FONTS)

def main():
    preview = "--preview" in sys.argv
    files = {
        "CombinedAntiquarian.dc.html": page(intro_bento, "antique", "Antiquarian calf", details_bento),
        "CombinedKitab.dc.html": page(intro_statement, "kitab", "Islamic kitab", details_two_panels, tilt_idx=1),
        "CombinedPress.dc.html": page(intro_split, "press", "Madrasa press", details_strip, tilt_idx=2),
        "TraditionalBindings.dc.html": bindings_sheet(),
    }
    os.makedirs(OUT, exist_ok=True)
    for name, src in files.items():
        fn = name.replace(".dc.html", ".html") if preview else name
        open(os.path.join(OUT, fn), "w").write(src)
    print("wrote", len(files), "to", OUT)

if __name__ == "__main__":
    main()

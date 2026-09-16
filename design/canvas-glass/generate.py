#!/usr/bin/env python3
"""Generate the modern-direction artboards into design/canvas-glass/."""
import json, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "design/canvas-glass"
PREVIEW = "--preview" in sys.argv

# ----------------------------------------------------------------- content
NAME = "Jamiyah Islamiyyah Abu Bakr"
KICKER = "Seven-Year Alimiyyah Program"
SUB = "Qur'an, hadith, fiqh and Arabic — taught the traditional way, text by text, with a teacher."
INTRO = ("A full course of study in Qur'an, hadith, fiqh, Arabic and the sciences that serve them, "
         "taught in the traditional way: text by text, with a teacher, in the company of fellow students.")
PROGRAM = ("Our Alimiyya program is a seven year program, from which the first four years are part time and "
           "the last three years are full time. Throughout this course, students will attain a mastery of the "
           "Arabic language, through which they will gain a deep understanding of the Qur'an and Hadith.")
NAV = ["Home", "About", "Program", "Articles", "Videos", "Alumni", "Contact"]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]
YEARS = ["First Year", "Second Year", "Third Year", "Fourth Year", "Fifth Year", "Sixth Year", "Seventh Year"]
ACHI = ("Achi Baatain is the first of the Urdu books taught to the students. It will give them a beginners "
        "understanding to urdu words and grammar.")

# Second Year is the only year with real books; every other slot is a TODO.
REAL = [
    dict(t="Achi Baatain",     s="Urdu",   w=46, h=224, k="leather", c="#5a1916", lab="#17130f"),
    dict(t="Tasheel ul-Nahwa", s="Nahwa",  w=52, h=238, k="leather", c="#15403b", lab="#6a1e1a"),
    dict(t="Tasheel ul-Sarf",  s="Sarf",   w=44, h=226, k="cloth",   c="#1d2a45"),
    dict(t="Duroos 1",         s="Arabic", w=50, h=230, k="leather", c="#8a5c31", lab="#134528"),
    dict(t="Qasas 1",          s="Arabic", w=44, h=212, k="vellum",  c="#e3d6b6", lab="#7a1f1a"),
]
BINDING_NOTES = [
    "Oxblood morocco · raised bands · black title label",
    "Bottle-green calf · five bands · oxblood label",
    "Navy book-cloth · gilt rules · lettered direct",
    "Tan calf · raised bands · green label",
    "Limp vellum · ink tooling · red label",
]

GRAIN = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.95' numOctaves='3' stitchTiles='stitch'/%3E"
         "%3CfeColorMatrix values='0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 1.6 -.45'/%3E%3C/filter%3E"
         "%3Crect width='140' height='140' filter='url(%23n)'/%3E%3C/svg%3E\")")

PATTERN = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='96' height='96' viewBox='0 0 96 96'%3E"
           "%3Cg fill='none' stroke='%23c9a961' stroke-width='1'%3E%3Crect x='30' y='30' width='36' height='36'/%3E"
           "%3Crect x='30' y='30' width='36' height='36' transform='rotate(45 48 48)'/%3E%3Ccircle cx='48' cy='48' r='6'/%3E"
           "%3Cpath d='M0 48h12M84 48h12M48 0v12M48 84v12'/%3E%3C/g%3E%3C/svg%3E\")")

# ------------------------------------------------------------ shared css
BASE_CSS = """
*,*::before,*::after{box-sizing:border-box;}
body{margin:0;-webkit-font-smoothing:antialiased;}
h1,h2,h3,h4,p{margin:0;}
a{color:#c9a961;text-decoration:none;} a:hover{color:#e2c77f;}
.wrap{width:1180px;margin:0 auto;}
.serif{font-family:"Cormorant Garamond",Garamond,"Times New Roman",serif;}
.urdu{font-family:"Noto Nastaliq Urdu",serif;}
svg.ic{width:18px;height:18px;flex:none;}

/* ---- motion: hero plays on load; everything else rises as it scrolls in.
   Scroll-driven, so on the canvas (where the whole page is in view) every
   section simply sits in its final state. ---- */
@keyframes rise{from{opacity:0;transform:translateY(34px);}to{opacity:1;transform:none;}}
@keyframes rise-l{from{opacity:0;transform:translateX(-44px);}to{opacity:1;transform:none;}}
@keyframes rise-r{from{opacity:0;transform:translateX(44px);}to{opacity:1;transform:none;}}
@keyframes drift{from{transform:scale(1.12);}to{transform:scale(1.02);}}
.in{animation:rise 1s cubic-bezier(.2,.7,.2,1) both;animation-delay:var(--d,0s);}
.drift{animation:drift 14s ease-out both;}
@supports (animation-timeline: view()){
  .rv{animation:rise linear both;animation-timeline:view();animation-range:entry 0% entry 85%;}
  .rv-l{animation:rise-l linear both;animation-timeline:view();animation-range:entry 0% entry 85%;}
  .rv-r{animation:rise-r linear both;animation-timeline:view();animation-range:entry 0% entry 85%;}
  .rv2{animation-range:entry 12% entry 100%;}
  .rv3{animation-range:entry 24% entry 100%;}
}

/* =================================================== the books ==== */
.bk{--gilt:#dcbb6c;--grain:""" + GRAIN + """;
  position:relative;flex:none;width:var(--w);height:var(--h);display:flex;flex-direction:column;
  border-radius:4px 4px 2px 2px;color:var(--gilt);cursor:pointer;
  background:
    linear-gradient(90deg,rgba(0,0,0,.58) 0%,rgba(0,0,0,.14) 9%,rgba(255,255,255,.10) 26%,rgba(255,255,255,.24) 37%,rgba(255,255,255,.05) 52%,rgba(0,0,0,.16) 76%,rgba(0,0,0,.62) 100%),
    var(--grain),var(--c);
  background-blend-mode:normal,soft-light,normal;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.2),inset 0 -1px 0 rgba(0,0,0,.4),5px 0 9px -3px rgba(0,0,0,.5);
  transform-origin:0% 100%;
  transition:transform .5s cubic-bezier(.2,.8,.2,1),box-shadow .5s,filter .5s;}
.bk:hover{transform:translateY(-12px) rotate(-8deg);z-index:3;filter:brightness(1.08);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.2),inset 0 -1px 0 rgba(0,0,0,.4),14px 16px 24px -8px rgba(0,0,0,.6);}
.bk.is-tilt{transform:translateY(-12px) rotate(-8deg);z-index:3;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.2),inset 0 -1px 0 rgba(0,0,0,.4),14px 16px 24px -8px rgba(0,0,0,.6);}
.bk__cap{flex:0 0 10px;position:relative;}
.bk__cap--head{border-radius:4px 4px 0 0;background:linear-gradient(180deg,rgba(255,255,255,.22),rgba(0,0,0,.28));border-bottom:1px solid rgba(0,0,0,.35);}
.bk__cap--head::before{content:"";position:absolute;left:4px;right:4px;top:-3px;height:3px;border-radius:2px 2px 0 0;
  background:repeating-linear-gradient(90deg,#8e2a22 0 2px,#e9d59c 2px 4px);box-shadow:0 -1px 0 rgba(0,0,0,.25);}
.bk__cap--tail{border-radius:0 0 2px 2px;background:linear-gradient(0deg,rgba(0,0,0,.34),rgba(255,255,255,.08));border-top:1px solid rgba(0,0,0,.35);}
.bk__band{flex:0 0 7px;margin:0 -1.5px;position:relative;border-radius:3.5px;
  background:linear-gradient(180deg,rgba(0,0,0,.38),rgba(255,255,255,.3) 46%,rgba(0,0,0,.42)),var(--c);
  box-shadow:0 1px 2px rgba(0,0,0,.45);}
.bk__band::before,.bk__band::after{content:"";position:absolute;left:4px;right:4px;height:1px;background:var(--gilt);opacity:.9;}
.bk__band::before{top:-4px;} .bk__band::after{bottom:-4px;}
.bk__panel{flex:0 0 22px;position:relative;}
.bk__panel--sm{flex-basis:16px;}
.bk__panel::after{content:"";position:absolute;left:50%;top:50%;width:6px;height:6px;border:1px solid var(--gilt);transform:translate(-50%,-50%) rotate(45deg);}
.bk__panel::before{content:"";position:absolute;left:50%;top:50%;width:2px;height:2px;margin:-1px 0 0 -1px;background:var(--gilt);}
.bk__label{flex:1 1 auto;margin:8px 5px;display:flex;align-items:center;justify-content:center;overflow:hidden;
  background:linear-gradient(90deg,rgba(0,0,0,.35),rgba(255,255,255,.08) 40%,rgba(0,0,0,.25)),var(--lab);border-radius:1.5px;
  box-shadow:inset 0 0 0 1px rgba(0,0,0,.4),inset 0 0 0 2.5px rgba(220,187,108,.0),inset 0 0 0 3px rgba(220,187,108,.7);}
.bk__title{writing-mode:vertical-rl;font-family:"Cormorant Garamond",Garamond,serif;font-weight:700;font-size:12.5px;letter-spacing:.03em;
  white-space:nowrap;line-height:1;text-shadow:0 1px 0 rgba(0,0,0,.55);}
.bk__foot{flex:0 0 38px;display:flex;align-items:center;justify-content:center;writing-mode:vertical-rl;
  font-family:"Cormorant Garamond",Garamond,serif;font-style:italic;font-weight:600;font-size:10px;letter-spacing:.08em;opacity:.9;}
/* book-cloth: no raised bands, gilt double rules, lettered straight onto the cloth */
.bk--cloth{--grain:repeating-linear-gradient(0deg,rgba(255,255,255,.06) 0 1px,transparent 1px 3px),repeating-linear-gradient(90deg,rgba(0,0,0,.12) 0 1px,transparent 1px 3px);}
.bk--cloth .bk__band{flex-basis:3px;background:none;box-shadow:none;margin:0;}
.bk--cloth .bk__band::before{top:-1px;} .bk--cloth .bk__band::after{bottom:-1px;}
.bk--cloth .bk__label{background:none;box-shadow:none;}
.bk--cloth .bk__title{font-size:13.5px;letter-spacing:.06em;}
/* vellum: pale, ink-tooled, a red label */
.bk--vellum{--ink:#5a3b1c;background:
    linear-gradient(90deg,rgba(60,40,15,.45) 0%,rgba(60,40,15,.08) 10%,rgba(255,255,255,.35) 34%,rgba(255,255,255,.1) 55%,rgba(60,40,15,.14) 80%,rgba(60,40,15,.5) 100%),
    var(--grain),var(--c);}
.bk--vellum .bk__band{background:linear-gradient(180deg,rgba(60,40,15,.3),rgba(255,255,255,.45) 46%,rgba(60,40,15,.35)),var(--c);}
.bk--vellum .bk__band::before,.bk--vellum .bk__band::after{background:var(--ink);opacity:.7;}
.bk--vellum .bk__panel::after{border-color:var(--ink);} .bk--vellum .bk__panel::before{background:var(--ink);}
.bk--vellum .bk__foot{color:var(--ink);}
.bk--vellum .bk__cap--head{background:linear-gradient(180deg,rgba(255,255,255,.4),rgba(60,40,15,.2));}
/* a slot the masjid has not filled yet */
.bk-ghost{flex:none;width:var(--w);height:var(--h);border:1.5px dashed rgba(201,169,97,.42);border-radius:4px 4px 2px 2px;
  display:flex;align-items:center;justify-content:center;background:rgba(201,169,97,.04);}
.bk-ghost span{writing-mode:vertical-rl;font:italic 500 10px/1 "Cormorant Garamond",serif;letter-spacing:.24em;color:rgba(201,169,97,.62);}

/* the book turned face-on */
.cover{position:relative;flex:none;width:150px;height:212px;border-radius:3px 7px 7px 3px;color:#dcbb6c;
  background:linear-gradient(90deg,rgba(0,0,0,.55) 0,rgba(0,0,0,.15) 9px,rgba(255,255,255,.14) 11px,rgba(255,255,255,.04) 40%,rgba(0,0,0,.2) 100%)," + "",
"""  # placeholder, replaced below
BASE_CSS = BASE_CSS.split('" + "",')[0] + GRAIN + """,#5a1916;
  background-blend-mode:normal,soft-light,normal;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.2),10px 14px 28px -8px rgba(0,0,0,.55),2px 2px 0 #e8dcc0,3px 3px 0 rgba(0,0,0,.25);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:18px 16px;}
.cover::before{content:"";position:absolute;inset:12px 10px 12px 18px;border:1px solid rgba(220,187,108,.8);box-shadow:inset 0 0 0 3px rgba(0,0,0,0),inset 0 0 0 4px rgba(220,187,108,.45);}
.cover__orn{width:26px;height:26px;margin-left:8px;}
.cover__t{font:700 17px/1.05 "Cormorant Garamond",serif;text-align:center;margin-left:8px;text-shadow:0 1px 0 rgba(0,0,0,.5);}
.cover__u{font-family:"Noto Nastaliq Urdu",serif;font-size:13px;line-height:1.9;margin-left:8px;}
"""

def book(b):
    if b is None:
        return None
    style = f"--w:{b['w']}px;--h:{b['h']}px;--c:{b['c']};" + (f"--lab:{b['lab']};" if 'lab' in b else "")
    return (f'<div class="bk bk--{b["k"]}{" " + b["extra"] if b.get("extra") else ""}" style="{style}" title="{b["t"]}">'
            '<span class="bk__cap bk__cap--head"></span><span class="bk__panel"></span><span class="bk__band"></span>'
            f'<span class="bk__label"><span class="bk__title">{b["t"]}</span></span>'
            '<span class="bk__band"></span>'
            f'<span class="bk__foot">{b["s"]}</span>'
            '<span class="bk__band"></span><span class="bk__panel bk__panel--sm"></span><span class="bk__cap bk__cap--tail"></span></div>')

def ghost(w, h):
    return f'<div class="bk-ghost" style="--w:{w}px;--h:{h}px"><span>TODO</span></div>'

def year_books(i, tilt=False):
    if i == 1:
        bs = [dict(b) for b in REAL]
        if tilt:
            bs[3]["extra"] = "is-tilt"
        return "".join(book(b) for b in bs) + ghost(44, 214)
    return ghost(48, 226) + ghost(40, 210)

ORN = ('<svg class="cover__orn" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4">'
       '<rect x="11" y="11" width="26" height="26"></rect><rect x="11" y="11" width="26" height="26" transform="rotate(45 24 24)"></rect>'
       '<circle cx="24" cy="24" r="4.5"></circle></svg>')

def cover():
    return (f'<div class="cover">{ORN}<div class="cover__t">Achi<br>Baatain</div>'
            '<div class="cover__u">اچھی باتیں</div></div>')

def shelf(prefix, tilt=False):
    """Seven bays, paired two to a board; the seventh gets a board to itself."""
    rows = []
    for r in range(4):
        idx = [r * 2, r * 2 + 1] if r < 3 else [6]
        bays = []
        for j, i in enumerate(idx):
            bays.append(
                f'<div class="{prefix}bay">'
                f'<div class="{prefix}well">{year_books(i, tilt)}</div>'
                f'<div class="{prefix}plank"></div>'
                f'<div class="{prefix}tag"><span>{ROMAN[i]}</span>{YEARS[i]}</div>'
                '</div>')
        cls = f'{prefix}row' + (f' {prefix}row--one' if r == 3 else '')
        rows.append(f'<div class="{cls} rv{" rv2" if r % 2 else ""}">' + "".join(bays) + '</div>')
    return "".join(rows)

# ------------------------------------------------------------ small parts
ARROW = '<svg class="ic" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 10h12M11 5l5 5-5 5"></path></svg>'
ARROW_L = '<svg class="ic" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M16 10H4M9 5l-5 5 5 5"></path></svg>'
CLOCK = '<svg class="ic" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="10" cy="10" r="7.2"></circle><path d="M10 6v4.3l2.8 1.7"></path></svg>'
QUOTE = '<svg viewBox="0 0 40 32" width="40" height="32" fill="currentColor"><path d="M0 32V19C0 8 6 1.5 16 0l1.6 4C11.6 5.8 9 9.4 8.8 14H16v18H0zm22 0V19C22 8 28 1.5 38 0l1.6 4C33.6 5.8 31 9.4 30.8 14H38v18H22z"></path></svg>'

TIMINGS = [
    ("Part-time", "Years I – IV", [("Monday to Friday", "4:30 PM – 7:30 PM")]),
    ("Full-time", "Years V – VII", [("Monday to Friday", "8:30 AM – 4:15 PM"), ("Saturday", "8:30 AM – 12:30 PM")]),
]
FEES = [("Part-time", "$125"), ("Full-time", "$325")]
DISC = [("2 students", "5% off the total"), ("3 students", "10% off the total"), ("4 or more", "15% off the total")]
TEACHERS = [("Moulana", "Kasim Ingar", "Imam of our masjid, and teacher for over 30 years", "KI"),
            ("Moulana", "Salim Chauhan", "", "SC"),
            ("Moulana", "Zuber Motala", "", "ZM")]
TESTI = [("I came expecting to memorise rulings and left having learned how the scholars arrived at them. That shift changed the way I read everything.", "Sumayyah Noor", "2020"),
         ("My teacher went through the same page with me four times without once making me feel slow. I try to teach my own students that way now.", "Abdurrahman Sheikh", "2022")]

def nav_links(cls):
    return "".join(f'<a class="{cls}" href="#">{n}</a>' for n in NAV)

def doc(css, body, fonts):
    fam = "&family=".join(fonts)
    head = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=' + fam + '&display=swap">\n'
            '<style>' + BASE_CSS + css + '</style>')
    if PREVIEW:
        return f'<!doctype html><html><head><meta charset="utf-8">{head}</head><body>{body}</body></html>\n'
    return ('<!doctype html>\n<html>\n<head>\n<meta charset="utf-8">\n<script src="./support.js"></script>\n</head>\n<body>\n<x-dc>\n'
            f'<helmet>\n{head}\n</helmet>\n{body}\n</x-dc>\n</body>\n</html>\n')

CORM = "Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600"
URDU = "Noto+Nastaliq+Urdu:wght@400;600"

def timings_rows(row_cls, day_cls, time_cls, rows):
    return "".join(f'<div class="{row_cls}"><span class="{day_cls}">{d}</span><span class="{time_cls}">{t}</span></div>' for d, t in rows)

# ======================================================================
# 1 · GLASS NAVE — full-bleed photo, deep green page, frosted tiles
# ======================================================================
def v1():
    css = """
body{background:#041d08;color:#f4efe2;font-family:"Instrument Sans",system-ui,sans-serif;font-size:16px;line-height:1.6;}
.page{position:relative;overflow:hidden;
  background:radial-gradient(900px 700px at 12% 1250px,rgba(201,169,97,.16),transparent 70%),
             radial-gradient(800px 800px at 92% 2100px,rgba(47,122,78,.45),transparent 70%),
             radial-gradient(700px 600px at 20% 3300px,rgba(47,122,78,.4),transparent 70%),
             radial-gradient(900px 700px at 85% 4300px,rgba(201,169,97,.12),transparent 70%),
             linear-gradient(180deg,#062707,#041d08);}
.glass{background:linear-gradient(145deg,rgba(255,255,255,.085),rgba(255,255,255,.025));
  -webkit-backdrop-filter:blur(22px) saturate(1.3);backdrop-filter:blur(22px) saturate(1.3);
  border:1px solid rgba(217,190,120,.28);border-radius:26px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 24px 60px -24px rgba(0,0,0,.55);}
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
.sec__head{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:40px;}
.sec__head h2{font:600 60px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.sec__head p{max-width:420px;color:rgba(244,239,226,.7);font-size:15.5px;}
.bento{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:20px;}
.tile{padding:34px 36px;transition:transform .4s cubic-bezier(.2,.8,.2,1),border-color .4s;}
.tile:hover{transform:translateY(-4px);border-color:rgba(217,190,120,.55);}
.tile__k{font-size:12.5px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#d9be78;margin-bottom:18px;}
.intro{grid-column:span 7;}
.intro p{font:500 34px/1.28 "Cormorant Garamond",serif;color:#fbf6e9;text-wrap:pretty;}
.stat{grid-column:span 5;display:flex;flex-direction:column;justify-content:space-between;}
.stat__n{font:600 150px/.8 "Cormorant Garamond",serif;color:#e2c77f;}
.stat__n small{font-size:34px;color:#f4efe2;margin-left:10px;font-style:italic;font-weight:500;}
.prog{grid-column:span 12;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:60px;align-items:center;}
.prog p{color:rgba(244,239,226,.82);font-size:17px;}
.prog h3{font:500 30px/1.2 "Cormorant Garamond",serif;font-style:italic;color:#e2c77f;}

.case{padding:22px;border-radius:32px;display:flex;flex-direction:column;gap:18px;}
.s-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;}
.s-row--one{grid-template-columns:minmax(0,1fr);}
.s-bay{position:relative;border-radius:20px;overflow:hidden;background:linear-gradient(180deg,rgba(0,0,0,.28),rgba(0,0,0,.12));
  border:1px solid rgba(217,190,120,.14);padding:0 0 48px;}
.s-bay::before{content:"";position:absolute;left:10%;right:10%;top:0;height:120px;background:radial-gradient(closest-side,rgba(233,207,140,.22),transparent);pointer-events:none;}
.s-well{height:290px;display:flex;align-items:flex-end;justify-content:center;gap:5px;padding:0 24px;position:relative;}
.s-plank{height:10px;margin:0 14px;border-radius:3px;background:linear-gradient(180deg,rgba(233,207,140,.55),rgba(201,169,97,.18) 40%,rgba(255,255,255,.04));
  box-shadow:0 -1px 0 rgba(255,255,255,.35),0 16px 30px rgba(233,207,140,.12);}
.s-tag{position:absolute;left:24px;bottom:13px;display:flex;align-items:center;gap:10px;font-size:13px;font-weight:600;letter-spacing:.06em;color:rgba(244,239,226,.78);}
.s-tag span{display:inline-grid;place-items:center;min-width:30px;height:22px;padding:0 6px;border-radius:999px;border:1px solid rgba(217,190,120,.5);color:#e2c77f;font-size:11px;}

.fee{grid-column:span 3;}
.fee__amt{font:600 76px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.fee__amt small{font:500 16px/1 "Instrument Sans",sans-serif;color:rgba(244,239,226,.65);margin-left:6px;}
.fee__note{color:rgba(244,239,226,.6);font-size:14px;margin-top:8px;}
.times{grid-column:span 6;grid-row:span 2;}
.tgroup+.tgroup{margin-top:28px;padding-top:28px;border-top:1px solid rgba(217,190,120,.2);}
.tgroup__h{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:12px;}
.tgroup__h b{font:600 32px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.tgroup__h span{font-size:13px;color:#d9be78;letter-spacing:.08em;}
.trow{display:flex;justify-content:space-between;align-items:center;padding:12px 0;font-size:16px;color:rgba(244,239,226,.85);}
.trow .t{display:inline-flex;align-items:center;gap:8px;color:#f0dca6;font-variant-numeric:tabular-nums;}
.disc{grid-column:span 6;}
.drow{display:flex;justify-content:space-between;align-items:center;padding:13px 0;border-top:1px solid rgba(217,190,120,.16);font-size:16px;}
.drow:first-of-type{border-top:0;}
.drow b{font-weight:600;color:#f0dca6;}

.teach{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;}
.tcard{padding:32px;display:flex;flex-direction:column;gap:16px;min-height:250px;}
.mono{width:64px;height:64px;border-radius:50%;display:grid;place-items:center;font:600 24px/1 "Cormorant Garamond",serif;color:#062707;
  background:linear-gradient(145deg,#e6cc88,#b8924a);box-shadow:0 0 0 5px rgba(217,190,120,.14);}
.tcard small{color:#d9be78;font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;font-weight:600;}
.tcard h3{font:600 32px/1.05 "Cormorant Garamond",serif;color:#fbf6e9;}
.tcard p{color:rgba(244,239,226,.7);font-size:15px;}
.ctrls{display:flex;gap:10px;}
.cbtn{width:48px;height:48px;border-radius:50%;display:grid;place-items:center;color:#e2c77f;}

.quotes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;}
.q{padding:40px 42px;color:#d9be78;}
.q p{font:italic 500 27px/1.35 "Cormorant Garamond",serif;color:#fbf6e9;margin:22px 0 28px;}
.q cite{font-style:normal;font-size:14.5px;color:rgba(244,239,226,.75);} .q cite b{color:#f0dca6;font-weight:600;}

.soon{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;margin-top:120px;}
.soon .tile{display:flex;justify-content:space-between;align-items:center;}
.soon h3{font:600 34px/1 "Cormorant Garamond",serif;color:#fbf6e9;margin-bottom:6px;}
.soon p{color:rgba(244,239,226,.6);font-size:15px;}
.pill{font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#d9be78;border:1px solid rgba(217,190,120,.4);border-radius:999px;padding:7px 14px;}
.foot{margin-top:120px;border-top:1px solid rgba(217,190,120,.2);padding:48px 0 56px;display:flex;justify-content:space-between;align-items:center;color:rgba(244,239,226,.62);font-size:14.5px;}
.foot .brand{font-size:22px;}
"""
    times = "".join(
        f'<div class="tgroup"><div class="tgroup__h"><b>{l}</b><span>{y}</span></div>'
        + timings_rows("trow", "d", "t", [(d, CLOCK + t) for d, t in rows]) + '</div>'
        for l, y, rows in TIMINGS)
    body = f"""
<div class="page">
<header class="hero">
  <div class="hero__img drift"></div><div class="hero__tint"></div>
  <nav class="nav glass in">
    <a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a>
    <div class="nav__links">{nav_links("nav__a")}</div>
    <a class="btn btn--gold btn--sm" href="#">View Curriculum</a>
  </nav>
  <div class="hero__body">
    <div class="eyebrow in" style="--d:.15s">{NAME}</div>
    <h1 class="in" style="--d:.3s">The Seven-Year <em>Alimiyyah</em> Program</h1>
    <p class="hero__sub in" style="--d:.45s">{SUB}</p>
    <a class="btn btn--gold in" style="--d:.6s" href="#">View Curriculum {ARROW}</a>
  </div>
  <div class="hero__card glass in" style="--d:.8s">
    <h4>Seven years</h4>
    <div class="split"><i></i><i></i><i></i><i></i><i class="ft"></i><i class="ft"></i><i class="ft"></i></div>
    <div class="legend"><div><b>Years I – IV</b>Part-time</div><div style="text-align:right"><b>Years V – VII</b>Full-time</div></div>
  </div>
</header>

<section class="wrap sec" style="padding-top:40px">
  <div class="bento">
    <div class="tile glass intro rv"><div class="tile__k">Introduction</div><p>{INTRO}</p></div>
    <div class="tile glass stat rv rv2"><div class="tile__k">The course</div><div class="stat__n">7<small>years</small></div>
      <div class="legend" style="margin-top:22px"><div><b>4</b>part-time</div><div style="text-align:right"><b>3</b>full-time</div></div></div>
    <div class="tile glass prog rv"><h3>Our Program</h3><p>{PROGRAM}</p></div>
  </div>
</section>

<section class="wrap sec">
  <div class="sec__head rv"><h2>Curriculum</h2><p>Every book in the course stands on the shelf at once. Select a spine to turn it face-on.</p></div>
  <div class="case glass">{shelf("s-", True)}</div>
</section>

<section class="wrap sec">
  <div class="sec__head rv"><h2>Details</h2><p>Class timings, monthly fees and the family discount.</p></div>
  <div class="bento">
    <div class="tile glass times rv-l"><div class="tile__k">Class timings</div>{times}</div>
    <div class="tile glass fee rv"><div class="tile__k">Part-time</div><div class="fee__amt">$125<small>/month</small></div><div class="fee__note">per student</div></div>
    <div class="tile glass fee rv rv2"><div class="tile__k">Full-time</div><div class="fee__amt">$325<small>/month</small></div><div class="fee__note">per student</div></div>
    <div class="tile glass disc rv-r"><div class="tile__k">Family discounts</div>{"".join(f'<div class="drow"><span>{a}</span><b>{b}</b></div>' for a, b in DISC)}</div>
  </div>
</section>

<section class="wrap sec">
  <div class="sec__head rv"><h2>Our Teachers</h2><div class="ctrls"><a class="cbtn glass" href="#">{ARROW_L}</a><a class="cbtn glass" href="#">{ARROW}</a></div></div>
  <div class="teach">{"".join(f'<div class="tile glass tcard rv{" rv2" if i==1 else " rv3" if i==2 else ""}"><div class="mono">{m}</div><small>{h}</small><h3>{n}</h3>{f"<p>{b}</p>" if b else ""}</div>' for i,(h,n,b,m) in enumerate(TEACHERS))}</div>
</section>

<section class="wrap sec">
  <div class="sec__head rv"><h2>Alumni Testimonies</h2></div>
  <div class="quotes">{"".join(f'<figure class="tile glass q rv{" rv2" if i else ""}" style="margin:0">{QUOTE}<p>{q}</p><cite><b>{n}</b> · Class of {y}</cite></figure>' for i,(q,n,y) in enumerate(TESTI))}</div>
  <div class="soon">
    <div class="tile glass rv"><div><h3>Articles</h3><p>Writing from our teachers and students.</p></div><span class="pill">Coming soon</span></div>
    <div class="tile glass rv rv2"><div><h3>Videos</h3><p>Recorded lessons and talks.</p></div><span class="pill">Coming soon</span></div>
  </div>
  <footer class="foot"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><span>[Masjid address] · [Email] · [Phone]</span><span>© 2026</span></footer>
</section>
</div>
"""
    return doc(css, body, [CORM, "Instrument+Sans:wght@400;500;600", URDU])

# ======================================================================
# 2 · DAYLIGHT BENTO — light page, photo in an inset card, glass on photo
# ======================================================================
def v2():
    css = """
body{background:#f3eee3;color:#14251b;font-family:"Hanken Grotesk",system-ui,sans-serif;font-size:16px;line-height:1.6;}
.page{padding:20px 30px 30px;}
.top{height:72px;display:flex;align-items:center;justify-content:space-between;padding:0 20px 0 10px;}
.brand{display:flex;align-items:center;gap:12px;font:600 21px/1 "Cormorant Garamond",serif;color:#134528;}
.brand img{width:42px;height:42px;}
.links{display:flex;gap:30px;} .links a{color:#3a4a41;font-size:15px;font-weight:500;} .links a:first-child{color:#134528;font-weight:700;}
.btn{display:inline-flex;align-items:center;gap:10px;height:50px;padding:0 24px;border-radius:14px;font-weight:600;font-size:15px;}
.btn--green{background:#134528;color:#f4efe2;} .btn--green:hover{color:#fff;}
.btn--glass{color:#fff;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.35);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);}
.btn--gold{background:#c9a961;color:#062707;} .btn--gold:hover{color:#062707;}
.hero{position:relative;height:720px;border-radius:34px;overflow:hidden;margin-top:10px;}
.hero__img{position:absolute;inset:0;background:url(./masjid.jpg) center 35%/cover;}
.hero__tint{position:absolute;inset:0;background:linear-gradient(0deg,rgba(6,39,7,.92) 0%,rgba(19,69,40,.55) 45%,rgba(19,69,40,.25) 100%);}
.hero__body{position:absolute;left:64px;bottom:64px;width:760px;color:#fbf6e9;}
.chip{display:inline-flex;align-items:center;gap:10px;height:36px;padding:0 16px;border-radius:999px;font-size:13.5px;font-weight:600;letter-spacing:.04em;
  background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.28);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);color:#f0dca6;}
.chip i{width:7px;height:7px;border-radius:50%;background:#c9a961;box-shadow:0 0 0 4px rgba(201,169,97,.25);}
.hero h1{font:600 96px/.95 "Cormorant Garamond",serif;margin:22px 0 22px;letter-spacing:-.01em;}
.hero__sub{font-size:19px;opacity:.88;max-width:560px;margin-bottom:34px;}
.hero__glass{position:absolute;right:40px;bottom:40px;width:380px;padding:30px;border-radius:24px;color:#fbf6e9;
  background:rgba(6,39,7,.28);border:1px solid rgba(255,255,255,.22);-webkit-backdrop-filter:blur(26px) saturate(1.4);backdrop-filter:blur(26px) saturate(1.4);}
.hero__glass .k{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#e2c77f;margin-bottom:12px;}
.hero__glass p{font:500 22px/1.35 "Cormorant Garamond",serif;}

.bento{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:18px;margin-top:18px;}
.t{border-radius:28px;padding:36px;background:#fbf8f1;border:1px solid rgba(19,69,40,.1);transition:transform .45s cubic-bezier(.2,.8,.2,1),box-shadow .45s;}
.t:hover{transform:translateY(-5px);box-shadow:0 30px 50px -30px rgba(19,69,40,.35);}
.t--green{background:#134528;color:#f4efe2;border-color:transparent;}
.t--deep{background:linear-gradient(160deg,#134528,#062707);color:#f4efe2;border-color:transparent;}
.k{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#9a7a2e;margin-bottom:16px;}
.t--green .k,.t--deep .k{color:#d9be78;}
h2.big{font:600 64px/1 "Cormorant Garamond",serif;color:#134528;}
.t--green h2.big,.t--deep h2.big{color:#fbf6e9;}
.lead{font:500 30px/1.3 "Cormorant Garamond",serif;color:#14251b;text-wrap:pretty;}
.body{color:#3a4a41;font-size:16.5px;}
.num{font:600 130px/.8 "Cormorant Garamond",serif;color:#c9a961;}
.yrs{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px;margin-top:26px;}
.yrs span{height:64px;border-radius:12px;display:grid;place-items:center;font:600 18px/1 "Cormorant Garamond",serif;background:rgba(201,169,97,.2);color:#e2c77f;}
.yrs span.ft{background:#c9a961;color:#062707;}
.yrs-l{display:flex;justify-content:space-between;margin-top:12px;font-size:13.5px;color:rgba(244,239,226,.75);}

.shelf-tile{grid-column:span 12;padding:40px;background:linear-gradient(180deg,#2c2114,#1c150b);border:0;}
.shelf-tile:hover{transform:none;box-shadow:none;}
.sh{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:28px;color:#f4efe2;}
.sh h2{font:600 64px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.sh p{max-width:400px;color:rgba(244,239,226,.65);font-size:15px;}
.w-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:16px;}
.w-row--one{grid-template-columns:minmax(0,1fr);}
.w-bay{position:relative;border-radius:18px;padding:10px 10px 0;
  background:linear-gradient(180deg,#5b4627,#45351e 50%,#372a14);box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 12px 24px -12px rgba(0,0,0,.6);}
.w-well{height:280px;border-radius:10px 10px 0 0;display:flex;align-items:flex-end;justify-content:center;gap:4px;padding:0 20px;
  background:radial-gradient(60% 70% at 50% 0%,rgba(255,222,150,.18),transparent 70%),linear-gradient(180deg,#0b2410,#062707);
  box-shadow:inset 0 10px 24px rgba(0,0,0,.6),inset 0 -2px 0 rgba(0,0,0,.4);}
.w-plank{height:14px;margin:0 -10px;background:linear-gradient(180deg,#7a5e36,#5b4627 40%,#3a2c16);box-shadow:0 -1px 0 rgba(255,255,255,.18) inset;}
.w-tag{height:46px;display:flex;align-items:center;justify-content:center;gap:10px;font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#e9d59c;}
.w-tag span{color:#c9a961;font-family:"Cormorant Garamond",serif;font-size:17px;letter-spacing:0;}

.price{font:600 84px/1 "Cormorant Garamond",serif;color:#134528;}
.price small{font:600 16px "Hanken Grotesk",sans-serif;color:#4a5a50;margin-left:6px;}
.row{display:flex;justify-content:space-between;align-items:center;padding:14px 0;border-top:1px solid rgba(244,239,226,.16);font-size:16px;}
.row:first-of-type{border-top:0;}
.row .tm{display:inline-flex;align-items:center;gap:8px;color:#f0dca6;font-weight:600;font-variant-numeric:tabular-nums;}
.grp+.grp{margin-top:22px;}
.grp h3{display:flex;justify-content:space-between;align-items:baseline;font:600 30px/1 "Cormorant Garamond",serif;margin-bottom:6px;}
.grp h3 span{font:600 12.5px "Hanken Grotesk",sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#d9be78;}
.drow{display:flex;justify-content:space-between;padding:14px 0;border-top:1px solid rgba(19,69,40,.1);}
.drow:first-of-type{border-top:0;} .drow b{color:#134528;}
.teacher{display:flex;flex-direction:column;gap:14px;}
.av{width:72px;height:72px;border-radius:22px;display:grid;place-items:center;background:#134528;color:#e2c77f;font:600 26px/1 "Cormorant Garamond",serif;}
.teacher small{font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#9a7a2e;}
.teacher h3{font:600 32px/1.05 "Cormorant Garamond",serif;color:#134528;}
.teacher p{color:#4a5a50;font-size:15px;}
.q p{font:italic 500 30px/1.32 "Cormorant Garamond",serif;margin:18px 0 22px;}
.q cite{font-style:normal;font-size:15px;color:rgba(244,239,226,.75);} .q cite b{color:#f0dca6;}
.q svg{color:#c9a961;}
.foot{margin-top:18px;border-radius:28px;background:#134528;color:rgba(244,239,226,.75);padding:40px 44px;display:flex;justify-content:space-between;align-items:center;font-size:15px;}
.foot .brand{color:#fbf6e9;}
.arrows{display:flex;gap:8px;} .arrows a{width:46px;height:46px;border-radius:14px;display:grid;place-items:center;border:1px solid rgba(19,69,40,.18);color:#134528;}
"""
    times = "".join(
        f'<div class="grp"><h3>{l}<span>{y}</span></h3>' + timings_rows("row", "d", "tm", [(d, CLOCK + t) for d, t in rows]) + '</div>'
        for l, y, rows in TIMINGS)
    body = f"""
<div class="page">
  <div class="top in"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><div class="links">{nav_links("")}</div><a class="btn btn--green" href="#">View Curriculum</a></div>
  <header class="hero">
    <div class="hero__img drift"></div><div class="hero__tint"></div>
    <div class="hero__body">
      <span class="chip in" style="--d:.1s"><i></i>{NAME}</span>
      <h1 class="in" style="--d:.25s">The Seven-Year Alimiyyah Program</h1>
      <p class="hero__sub in" style="--d:.4s">{SUB}</p>
      <div class="in" style="--d:.55s;display:flex;gap:12px"><a class="btn btn--gold" href="#">View Curriculum {ARROW}</a><a class="btn btn--glass" href="#">Timings &amp; fees</a></div>
    </div>
    <div class="hero__glass in" style="--d:.75s"><div class="k">Introduction</div><p>{INTRO}</p></div>
  </header>

  <div class="bento">
    <div class="t rv" style="grid-column:span 5"><div class="k">Our Program</div><h2 class="big">Seven years, one path.</h2></div>
    <div class="t rv rv2" style="grid-column:span 7;display:flex;align-items:center"><p class="body" style="font-size:18px">{PROGRAM}</p></div>
    <div class="t t--deep rv" style="grid-column:span 12;display:grid;grid-template-columns:auto minmax(0,1fr);gap:56px;align-items:center">
      <div class="num">7</div>
      <div><div class="yrs">{"".join(f'<span class="{"ft" if i>3 else ""}">{r}</span>' for i,r in enumerate(ROMAN))}</div>
      <div class="yrs-l"><span>Years I – IV · part-time, weekday evenings</span><span>Years V – VII · full-time</span></div></div>
    </div>

    <div class="t shelf-tile rv">
      <div class="sh"><div><div class="k" style="color:#d9be78">The books</div><h2>Curriculum</h2></div><p>Every book in the course stands on the shelf at once. Select a spine to turn it face-on.</p></div>
      {shelf("w-")}
    </div>

    <div class="t t--green rv-l" style="grid-column:span 6;grid-row:span 2"><div class="k">Details · Class timings</div>{times}</div>
    <div class="t rv" style="grid-column:span 3"><div class="k">Part-time</div><div class="price">$125<small>/mo</small></div><p class="body">per student</p></div>
    <div class="t rv rv2" style="grid-column:span 3"><div class="k">Full-time</div><div class="price">$325<small>/mo</small></div><p class="body">per student</p></div>
    <div class="t rv-r" style="grid-column:span 6"><div class="k">Family discounts</div>{"".join(f'<div class="drow"><span>{a}</span><b>{b}</b></div>' for a,b in DISC)}</div>

    <div class="t rv" style="grid-column:span 3;display:flex;flex-direction:column;justify-content:space-between"><div><div class="k">Our Teachers</div><h2 class="big" style="font-size:52px">Taught by scholars.</h2></div><div class="arrows"><a href="#">{ARROW_L}</a><a href="#">{ARROW}</a></div></div>
    {"".join(f'<div class="t teacher rv{" rv2" if i==1 else " rv3" if i==2 else ""}" style="grid-column:span 3"><div class="av">{m}</div><small>{h}</small><h3>{n}</h3>{f"<p>{b}</p>" if b else ""}</div>' for i,(h,n,b,m) in enumerate(TEACHERS))}

    {"".join(f'<figure class="t t--deep q rv{" rv2" if i else ""}" style="grid-column:span 6;margin:0">{QUOTE}<p>{q}</p><cite><b>{n}</b> · Class of {y}</cite></figure>' for i,(q,n,y) in enumerate(TESTI))}
    <div class="t rv" style="grid-column:span 6;display:flex;justify-content:space-between;align-items:center"><div><h2 class="big" style="font-size:40px">Articles</h2><p class="body">Writing from our teachers and students — coming soon.</p></div></div>
    <div class="t rv rv2" style="grid-column:span 6;display:flex;justify-content:space-between;align-items:center"><div><h2 class="big" style="font-size:40px">Videos</h2><p class="body">Recorded lessons and talks — coming soon.</p></div></div>
  </div>
  <footer class="foot"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><span>[Masjid address] · [Email] · [Phone]</span><span>© 2026</span></footer>
</div>
"""
    return doc(css, body, [CORM, "Hanken+Grotesk:wght@400;500;600;700", URDU])

# ======================================================================
# 3 · MIHRAB SPLIT — headline beside a photo cut as an arch
# ======================================================================
def v3():
    css = """
body{background:#efe7d6;color:#14251b;font-family:"Outfit",system-ui,sans-serif;font-size:16px;line-height:1.6;font-weight:350;}
.hero{position:relative;height:960px;background:#062707;overflow:hidden;}
.hero::before{content:"";position:absolute;inset:0;background-image:""" + PATTERN + """;background-size:96px;opacity:.07;}
.hero::after{content:"";position:absolute;right:-200px;top:-100px;width:900px;height:900px;background:radial-gradient(closest-side,rgba(201,169,97,.2),transparent);}
.nav{position:relative;z-index:3;width:1260px;margin:0 auto;height:96px;display:flex;align-items:center;justify-content:space-between;}
.brand{display:flex;align-items:center;gap:12px;font:600 21px/1 "Cormorant Garamond",serif;color:#f4efe2;}
.brand img{width:42px;height:42px;}
.links{display:flex;gap:30px;} .links a{color:rgba(244,239,226,.75);font-size:15px;} .links a:first-child{color:#e2c77f;}
.btn{display:inline-flex;align-items:center;gap:10px;height:54px;padding:0 28px;border-radius:999px;font-weight:500;font-size:15.5px;}
.btn--gold{background:#c9a961;color:#062707;} .btn--gold:hover{color:#062707;}
.btn--line{border:1px solid rgba(217,190,120,.5);color:#f0dca6;}
.hero__grid{position:relative;z-index:2;width:1260px;margin:30px auto 0;display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:40px;align-items:center;}
.eyebrow{color:#d9be78;font-size:14px;letter-spacing:.22em;text-transform:uppercase;font-weight:500;}
.hero h1{font:600 112px/.9 "Cormorant Garamond",serif;color:#fbf6e9;margin:26px 0 30px;letter-spacing:-.015em;}
.hero h1 em{display:block;font-style:italic;font-weight:500;color:#e2c77f;}
.hero__sub{color:rgba(244,239,226,.8);font-size:19px;max-width:520px;margin-bottom:40px;}
.arch{position:relative;justify-self:end;width:480px;height:640px;margin-right:16px;}
.arch__img{position:absolute;inset:0;border-radius:240px 240px 28px 28px;overflow:hidden;box-shadow:0 40px 80px -30px rgba(0,0,0,.7);}
.arch__img div{position:absolute;inset:0;background:url(./masjid.jpg) 50% 40%/auto 100%;}
.arch__img::after{content:"";position:absolute;inset:0;background:linear-gradient(0deg,rgba(6,39,7,.75),rgba(19,69,40,.15) 55%,rgba(19,69,40,.35));}
.arch__line{position:absolute;inset:-16px;border:1px solid rgba(217,190,120,.55);border-radius:256px 256px 40px 40px;}
.float{position:absolute;left:-120px;bottom:64px;width:320px;padding:24px 26px;border-radius:22px;color:#fbf6e9;
  background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.25);-webkit-backdrop-filter:blur(20px) saturate(1.4);backdrop-filter:blur(20px) saturate(1.4);
  box-shadow:0 30px 60px -20px rgba(0,0,0,.5);}
.float .k{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#e2c77f;font-weight:500;margin-bottom:10px;}
.float b{display:block;font:600 30px/1.1 "Cormorant Garamond",serif;}
.float span{font-size:14.5px;color:rgba(244,239,226,.78);}
.float2{left:auto;right:-50px;bottom:auto;top:120px;width:220px;}

.sec{width:1180px;margin:0 auto;padding-top:130px;}
.hd{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:60px;align-items:end;margin-bottom:44px;}
.hd h2{font:600 72px/.95 "Cormorant Garamond",serif;color:#134528;}
.hd h2 em{font-weight:500;color:#9a7a2e;}
.hd p{color:#3a4a41;font-size:17px;}
.bento{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));grid-auto-rows:minmax(120px,auto);gap:20px;}
.t{position:relative;border-radius:30px;padding:38px;overflow:hidden;transition:transform .45s cubic-bezier(.2,.8,.2,1);}
.t:hover{transform:translateY(-5px) rotate(-.3deg);}
.t--cream{background:#f8f3e8;box-shadow:0 1px 0 rgba(255,255,255,.8) inset,0 20px 40px -30px rgba(60,40,15,.4);}
.t--green{background:#134528;color:#f4efe2;}
.t--mesh{color:#fbf6e9;background:radial-gradient(120% 90% at 0% 0%,#2f7a4e,transparent 55%),radial-gradient(90% 90% at 100% 100%,#c9a961,transparent 60%),#134528;}
.glass{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.28);-webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);border-radius:20px;padding:22px 24px;}
.k{font-size:12.5px;letter-spacing:.2em;text-transform:uppercase;color:#9a7a2e;font-weight:500;margin-bottom:16px;}
.t--green .k,.t--mesh .k{color:#e2c77f;}
.lead{font:500 34px/1.25 "Cormorant Garamond",serif;color:#14251b;text-wrap:pretty;}

.case{border-radius:34px;padding:28px;background:linear-gradient(180deg,#4f3c20,#372a14);box-shadow:inset 0 1px 0 rgba(255,255,255,.14),0 40px 70px -40px rgba(55,42,20,.8);}
.a-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;}
.a-row+.a-row{margin-top:22px;}
.a-row--one{grid-template-columns:minmax(0,1fr);}
.a-bay{position:relative;}
.a-well{height:300px;display:flex;align-items:flex-end;justify-content:center;gap:5px;padding:0 24px;border-radius:150px 150px 6px 6px;
  background:radial-gradient(50% 60% at 50% 0%,rgba(255,222,150,.2),transparent 70%),linear-gradient(180deg,#0a2a10,#051f07);
  box-shadow:inset 0 14px 30px rgba(0,0,0,.65),0 0 0 1px rgba(217,190,120,.35);}
.a-row--one .a-well{border-radius:24px 24px 6px 6px;}
.a-plank{height:14px;margin:0 -8px;border-radius:4px;background:linear-gradient(180deg,#8a6b3e,#5b4627 45%,#34270f);box-shadow:0 8px 16px -6px rgba(0,0,0,.6);}
.a-tag{display:flex;justify-content:center;align-items:center;gap:10px;height:48px;color:#f0dca6;font-size:13px;letter-spacing:.14em;text-transform:uppercase;}
.a-tag span{font:600 20px/1 "Cormorant Garamond",serif;color:#c9a961;letter-spacing:0;}

.price{font:600 96px/.9 "Cormorant Garamond",serif;}
.price small{font:400 16px "Outfit",sans-serif;opacity:.7;margin-left:6px;}
.row{display:flex;justify-content:space-between;padding:12px 0;border-top:1px solid rgba(19,69,40,.12);font-size:16px;}
.row:first-of-type{border-top:0;} .row b{font-weight:500;color:#134528;}
.t--green .row{border-color:rgba(244,239,226,.14);} .t--green .row b{color:#f0dca6;}
.grp h3{font:600 34px/1 "Cormorant Garamond",serif;color:#134528;margin-bottom:4px;}
.grp small{font-size:13px;color:#9a7a2e;letter-spacing:.1em;}
.grp+.grp{margin-top:26px;}
.teachers{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;}
.tc{border-radius:200px 200px 28px 28px;padding:56px 32px 36px;text-align:center;background:#f8f3e8;transition:transform .45s cubic-bezier(.2,.8,.2,1);}
.tc:hover{transform:translateY(-6px);}
.tc .m{width:90px;height:90px;margin:0 auto 22px;border-radius:50%;display:grid;place-items:center;background:#134528;color:#e2c77f;font:600 32px/1 "Cormorant Garamond",serif;box-shadow:0 0 0 6px #efe7d6,0 0 0 7px rgba(201,169,97,.6);}
.tc small{font-size:12.5px;letter-spacing:.18em;text-transform:uppercase;color:#9a7a2e;}
.tc h3{font:600 34px/1.05 "Cormorant Garamond",serif;color:#134528;margin:6px 0 10px;}
.tc p{color:#4a5a50;font-size:15px;}
.q p{font:italic 500 32px/1.3 "Cormorant Garamond",serif;margin:18px 0 26px;}
.q cite{font-style:normal;font-size:15px;opacity:.8;}
.foot{margin-top:130px;background:#062707;color:rgba(244,239,226,.7);}
.foot__in{width:1180px;margin:0 auto;padding:60px 0;display:flex;justify-content:space-between;align-items:center;font-size:15px;}
"""
    times = "".join(
        f'<div class="grp"><h3>{l}</h3><small>{y}</small>' + timings_rows("row", "d", "", [(d, f"<b>{t}</b>") for d, t in rows]).replace('<span class="">', '<span>') + '</div>'
        for l, y, rows in TIMINGS)
    body = f"""
<header class="hero">
  <nav class="nav in"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><div class="links">{nav_links("")}</div><a class="btn btn--line" href="#" style="height:46px">Contact</a></nav>
  <div class="hero__grid">
    <div>
      <div class="eyebrow in" style="--d:.1s">{NAME}</div>
      <h1 class="in" style="--d:.25s">The Seven-Year <em>Alimiyyah Program</em></h1>
      <p class="hero__sub in" style="--d:.4s">{SUB}</p>
      <div class="in" style="--d:.55s;display:flex;gap:14px"><a class="btn btn--gold" href="#">View Curriculum {ARROW}</a><a class="btn btn--line" href="#">Timings &amp; fees</a></div>
    </div>
    <div class="arch in" style="--d:.35s">
      <div class="arch__line"></div>
      <div class="arch__img"><div class="drift"></div></div>
      <div class="float in" style="--d:.9s"><div class="k">Part-time · Years I – IV</div><b>Weekday evenings</b><span>Monday to Friday, 4:30 PM – 7:30 PM</span></div>
    </div>
  </div>
</header>

<section class="sec">
  <div class="hd rv"><h2>A course of study, <em>text by text.</em></h2><p>{PROGRAM}</p></div>
  <div class="bento">
    <div class="t t--cream rv-l" style="grid-column:span 7"><div class="k">Introduction</div><p class="lead">{INTRO}</p></div>
    <div class="t t--mesh rv-r" style="grid-column:span 5;display:flex;flex-direction:column;justify-content:space-between">
      <div class="k">Seven years</div>
      <div style="display:flex;gap:12px">
        <div class="glass" style="flex:1"><div style="font:600 64px/1 'Cormorant Garamond',serif">4</div><div style="font-size:14px;opacity:.85">years part-time</div></div>
        <div class="glass" style="flex:1"><div style="font:600 64px/1 'Cormorant Garamond',serif">3</div><div style="font-size:14px;opacity:.85">years full-time</div></div>
      </div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Curriculum</h2><p>Every book in the course stands on the shelf at once. Select a spine to turn it face-on.</p></div>
  <div class="case rv">{shelf("a-")}</div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Details</h2><p>Class timings, monthly fees and the family discount.</p></div>
  <div class="bento">
    <div class="t t--cream rv-l" style="grid-column:span 5;grid-row:span 2"><div class="k">Class timings</div>{times}</div>
    <div class="t t--green rv" style="grid-column:span 7;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:30px">
      <div><div class="k">Part-time</div><div class="price">$125<small>/month</small></div><div style="opacity:.7;margin-top:8px">per student</div></div>
      <div><div class="k">Full-time</div><div class="price">$325<small>/month</small></div><div style="opacity:.7;margin-top:8px">per student</div></div>
    </div>
    <div class="t t--cream rv-r" style="grid-column:span 7"><div class="k">Family discounts</div>{"".join(f'<div class="row"><span>{a}</span><b>{b}</b></div>' for a,b in DISC)}</div>
  </div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Our Teachers</h2><p></p></div>
  <div class="teachers">{"".join(f'<div class="tc rv{" rv2" if i==1 else " rv3" if i==2 else ""}"><div class="m">{m}</div><small>{h}</small><h3>{n}</h3>{f"<p>{b}</p>" if b else ""}</div>' for i,(h,n,b,m) in enumerate(TEACHERS))}</div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Alumni <em>Testimonies</em></h2><p></p></div>
  <div class="bento">{"".join(f'<figure class="t {"t--mesh" if i else "t--green"} q rv{" rv2" if i else ""}" style="grid-column:span 6;margin:0"><span style="color:#c9a961">{QUOTE}</span><p>{q}</p><cite><b>{n}</b> · Class of {y}</cite></figure>' for i,(q,n,y) in enumerate(TESTI))}
    <div class="t t--cream rv" style="grid-column:span 6"><div class="k">Coming soon</div><h3 style="font:600 40px/1 'Cormorant Garamond',serif;color:#134528">Articles</h3></div>
    <div class="t t--cream rv rv2" style="grid-column:span 6"><div class="k">Coming soon</div><h3 style="font:600 40px/1 'Cormorant Garamond',serif;color:#134528">Videos</h3></div>
  </div>
</section>
<footer class="foot"><div class="foot__in"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><span>[Masjid address] · [Email] · [Phone]</span><span>© 2026</span></div></footer>
"""
    return doc(css, body, [CORM, "Outfit:wght@300;400;500;600", URDU])

# ======================================================================
# 4 · THROUGH THE WINDOW — the photo becomes the backdrop to the whole page
# ======================================================================
def v4():
    css = """
body{background:#062707;color:#f4efe2;font-family:"Instrument Sans",system-ui,sans-serif;font-size:16px;line-height:1.6;}
.page{position:relative;overflow:hidden;}
.bg{position:absolute;inset:0;z-index:0;}
.bg__photo{position:absolute;left:-10%;right:-10%;top:600px;bottom:-5%;background:url(./masjid.jpg) center/cover;filter:blur(60px) saturate(1.6) brightness(.8);transform:scale(1.2);}
.bg__tint{position:absolute;inset:0;background:linear-gradient(180deg,transparent 0,rgba(6,39,7,.55) 900px,rgba(6,39,7,.7) 60%,rgba(6,39,7,.85));}
.bg__glow{position:absolute;inset:0;background:radial-gradient(700px 500px at 80% 1500px,rgba(201,169,97,.35),transparent 70%),radial-gradient(800px 600px at 10% 2600px,rgba(47,122,78,.6),transparent 70%),radial-gradient(700px 500px at 90% 3900px,rgba(201,169,97,.25),transparent 70%);}
.content{position:relative;z-index:1;}
.hero{position:relative;height:940px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;overflow:hidden;}
.hero__img{position:absolute;inset:0;background:url(./masjid.jpg) center 35%/cover;}
.hero__tint{position:absolute;inset:0;background:radial-gradient(70% 60% at 50% 55%,rgba(6,39,7,.35),rgba(6,39,7,.75)),linear-gradient(180deg,rgba(6,39,7,.4),transparent 30%,transparent 70%,rgba(6,39,7,.0));}
.nav{position:absolute;top:0;left:0;right:0;height:92px;display:flex;align-items:center;justify-content:space-between;padding:0 60px;
  background:rgba(6,39,7,.25);border-bottom:1px solid rgba(255,255,255,.14);-webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);z-index:3;}
.brand{display:flex;align-items:center;gap:12px;font:600 21px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.brand img{width:42px;height:42px;}
.links{display:flex;gap:32px;} .links a{color:rgba(255,255,255,.8);font-size:15px;} .links a:first-child{color:#f0dca6;}
.hero__body{position:relative;z-index:2;max-width:1100px;}
.hero small{display:inline-block;color:#f0dca6;font-size:14px;letter-spacing:.3em;text-transform:uppercase;padding:10px 20px;border-radius:999px;
  background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.25);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);}
.hero h1{font:600 132px/.9 "Cormorant Garamond",serif;color:#fff;margin:34px 0 30px;letter-spacing:-.02em;text-shadow:0 10px 40px rgba(0,0,0,.35);}
.hero h1 em{font-style:italic;font-weight:500;color:#f0dca6;}
.hero p{font-size:21px;color:rgba(255,255,255,.88);max-width:640px;margin:0 auto 44px;}
.btn{display:inline-flex;align-items:center;gap:10px;height:58px;padding:0 32px;border-radius:999px;font-weight:600;font-size:16px;}
.btn--gold{background:#e2c77f;color:#062707;} .btn--gold:hover{color:#062707;}
.btn--glass{color:#fff;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.35);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);}
.scroll{position:absolute;bottom:40px;left:50%;transform:translateX(-50%);width:28px;height:46px;border-radius:14px;border:1.5px solid rgba(255,255,255,.5);z-index:2;}
.scroll::after{content:"";position:absolute;left:50%;top:9px;width:4px;height:9px;margin-left:-2px;border-radius:2px;background:#f0dca6;animation:dot 1.8s ease-in-out infinite;}
@keyframes dot{0%{transform:translateY(0);opacity:1}70%{transform:translateY(14px);opacity:0}100%{opacity:0}}

.sheet{width:1240px;margin:0 auto 40px;padding:60px;border-radius:40px;
  background:linear-gradient(160deg,rgba(255,255,255,.14),rgba(255,255,255,.04));border:1px solid rgba(255,255,255,.2);
  -webkit-backdrop-filter:blur(30px) saturate(1.5);backdrop-filter:blur(30px) saturate(1.5);box-shadow:inset 0 1px 0 rgba(255,255,255,.25),0 40px 90px -40px rgba(0,0,0,.6);}
.sheet--first{margin-top:-120px;position:relative;z-index:3;}
.hd{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:36px;gap:40px;}
.hd h2{font:600 64px/1 "Cormorant Garamond",serif;color:#fff;}
.hd p{max-width:440px;color:rgba(255,255,255,.72);font-size:15.5px;}
.bento{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:16px;}
.t{padding:30px;border-radius:26px;background:rgba(6,39,7,.32);border:1px solid rgba(217,190,120,.22);transition:transform .45s cubic-bezier(.2,.8,.2,1),background .45s;}
.t:hover{transform:translateY(-4px);background:rgba(6,39,7,.45);}
.t--light{background:rgba(255,255,255,.12);border-color:rgba(255,255,255,.22);}
.k{font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:#f0dca6;margin-bottom:14px;}
.lead{font:500 36px/1.25 "Cormorant Garamond",serif;color:#fff;text-wrap:pretty;}

.g-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;}
.g-row+.g-row{margin-top:16px;}
.g-row--one{grid-template-columns:minmax(0,1fr);}
.g-bay{position:relative;border-radius:24px;background:rgba(3,20,5,.5);border:1px solid rgba(217,190,120,.2);overflow:hidden;}
.g-well{height:292px;display:flex;align-items:flex-end;justify-content:center;gap:5px;padding:0 24px;}
.g-plank{position:relative;height:12px;margin:0 16px;border-radius:6px;background:linear-gradient(180deg,rgba(255,255,255,.55),rgba(255,255,255,.12));
  box-shadow:0 1px 0 rgba(255,255,255,.4) inset,0 0 28px 4px rgba(240,220,166,.25);}
.g-tag{height:54px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;font-size:14px;color:rgba(255,255,255,.82);}
.g-tag span{order:2;font:600 22px/1 "Cormorant Garamond",serif;color:#f0dca6;}

.big{font:600 90px/.9 "Cormorant Garamond",serif;color:#fff;}
.big small{font:500 15px "Instrument Sans",sans-serif;color:rgba(255,255,255,.65);margin-left:6px;}
.row{display:flex;justify-content:space-between;align-items:center;padding:13px 0;border-top:1px solid rgba(255,255,255,.12);}
.row:first-of-type{border-top:0;} .row b{font-weight:600;color:#f0dca6;}
.grp h3{font:600 32px/1 "Cormorant Garamond",serif;color:#fff;display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;}
.grp h3 span{font:500 13px "Instrument Sans",sans-serif;color:#f0dca6;letter-spacing:.08em;}
.grp+.grp{margin-top:24px;}
.tc{display:flex;gap:20px;align-items:center;}
.tc .m{width:76px;height:76px;flex:none;border-radius:50%;display:grid;place-items:center;font:600 28px/1 "Cormorant Garamond",serif;color:#062707;background:linear-gradient(145deg,#f0dca6,#c29e52);}
.tc small{font-size:12px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#f0dca6;}
.tc h3{font:600 30px/1.05 "Cormorant Garamond",serif;color:#fff;}
.tc p{font-size:14px;color:rgba(255,255,255,.7);margin-top:4px;}
.q p{font:italic 500 30px/1.32 "Cormorant Garamond",serif;color:#fff;margin:16px 0 22px;}
.q cite{font-style:normal;color:rgba(255,255,255,.75);} .q cite b{color:#f0dca6;}
.foot{width:1240px;margin:60px auto 0;padding:40px 0 60px;display:flex;justify-content:space-between;color:rgba(255,255,255,.65);border-top:1px solid rgba(255,255,255,.18);}
"""
    times = "".join(
        f'<div class="grp"><h3>{l}<span>{y}</span></h3>' + timings_rows("row", "", "", [(d, f"<b>{t}</b>") for d, t in rows]).replace(' class=""', '') + '</div>'
        for l, y, rows in TIMINGS)
    body = f"""
<div class="page">
<div class="bg"><div class="bg__photo"></div><div class="bg__tint"></div><div class="bg__glow"></div></div>
<div class="content">
  <header class="hero">
    <div class="hero__img drift"></div><div class="hero__tint"></div>
    <nav class="nav"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><div class="links">{nav_links("")}</div><a class="btn btn--glass" href="#" style="height:46px;padding:0 22px;font-size:14.5px">Contact</a></nav>
    <div class="hero__body">
      <small class="in" style="--d:.1s">{NAME}</small>
      <h1 class="in" style="--d:.3s">The Seven-Year<br><em>Alimiyyah</em> Program</h1>
      <p class="in" style="--d:.5s">{SUB}</p>
      <div class="in" style="--d:.7s;display:flex;gap:14px;justify-content:center"><a class="btn btn--gold" href="#">View Curriculum {ARROW}</a><a class="btn btn--glass" href="#">Timings &amp; fees</a></div>
    </div>
    <div class="scroll"></div>
  </header>

  <section class="sheet sheet--first rv">
    <div class="bento">
      <div class="t t--light" style="grid-column:span 8"><div class="k">Introduction</div><p class="lead">{INTRO}</p></div>
      <div class="t" style="grid-column:span 4;display:flex;flex-direction:column;justify-content:space-between"><div class="k">Our Program</div><div class="big">7<small>years</small></div><div style="display:flex;gap:8px;margin-top:18px">{"".join(f'<i style="flex:1;height:6px;border-radius:3px;background:{"#f0dca6" if i<4 else "rgba(255,255,255,.85)"}"></i>' for i in range(7))}</div><div style="display:flex;justify-content:space-between;font-size:13.5px;color:rgba(255,255,255,.7);margin-top:10px"><span>4 part-time</span><span>3 full-time</span></div></div>
      <div class="t" style="grid-column:span 12"><p style="font-size:17.5px;color:rgba(255,255,255,.85);max-width:900px">{PROGRAM}</p></div>
    </div>
  </section>

  <section class="sheet rv">
    <div class="hd"><h2>Curriculum</h2><p>Every book in the course stands on the shelf at once. Select a spine to turn it face-on.</p></div>
    {shelf("g-")}
  </section>

  <section class="sheet rv">
    <div class="hd"><h2>Details</h2><p>Class timings, monthly fees and the family discount.</p></div>
    <div class="bento">
      <div class="t rv-l" style="grid-column:span 6;grid-row:span 2"><div class="k">Class timings</div>{times}</div>
      <div class="t t--light rv" style="grid-column:span 3"><div class="k">Part-time</div><div class="big" style="font-size:72px">$125<small>/mo</small></div></div>
      <div class="t t--light rv rv2" style="grid-column:span 3"><div class="k">Full-time</div><div class="big" style="font-size:72px">$325<small>/mo</small></div></div>
      <div class="t rv-r" style="grid-column:span 6"><div class="k">Family discounts</div>{"".join(f'<div class="row"><span>{a}</span><b>{b}</b></div>' for a,b in DISC)}</div>
    </div>
  </section>

  <section class="sheet rv">
    <div class="hd"><h2>Our Teachers</h2></div>
    <div class="bento">{"".join(f'<div class="t tc rv{" rv2" if i==1 else " rv3" if i==2 else ""}" style="grid-column:span 4"><div class="m">{m}</div><div><small>{h}</small><h3>{n}</h3>{f"<p>{b}</p>" if b else ""}</div></div>' for i,(h,n,b,m) in enumerate(TEACHERS))}</div>
    <div class="hd" style="margin-top:60px"><h2>Alumni Testimonies</h2></div>
    <div class="bento">{"".join(f'<figure class="t t--light q rv{" rv2" if i else ""}" style="grid-column:span 6;margin:0"><span style="color:#f0dca6">{QUOTE}</span><p>{q}</p><cite><b>{n}</b> · Class of {y}</cite></figure>' for i,(q,n,y) in enumerate(TESTI))}
      <div class="t rv" style="grid-column:span 6;display:flex;justify-content:space-between;align-items:center"><h3 style="font:600 36px/1 'Cormorant Garamond',serif">Articles</h3><span class="k" style="margin:0">Coming soon</span></div>
      <div class="t rv rv2" style="grid-column:span 6;display:flex;justify-content:space-between;align-items:center"><h3 style="font:600 36px/1 'Cormorant Garamond',serif">Videos</h3><span class="k" style="margin:0">Coming soon</span></div>
    </div>
  </section>
  <footer class="foot"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><span>[Masjid address] · [Email] · [Phone]</span><span>© 2026</span></footer>
</div>
</div>
"""
    return doc(css, body, [CORM, "Instrument+Sans:wght@400;500;600", URDU])

# ======================================================================
# 5 · SHELF FIRST — photo band, the bookshelf rises into it
# ======================================================================
def v5():
    css = """
body{background:#f1ebdf;color:#14251b;font-family:"Figtree",system-ui,sans-serif;font-size:16px;line-height:1.6;}
.hero{position:relative;height:720px;overflow:hidden;}
.hero__img{position:absolute;inset:0;background:url(./masjid.jpg) center 30%/cover;}
.hero__tint{position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,39,7,.85) 0%,rgba(19,69,40,.55) 40%,rgba(6,39,7,.92) 100%);}
.nav{position:relative;z-index:3;width:1240px;margin:0 auto;height:90px;display:flex;align-items:center;justify-content:space-between;}
.brand{display:flex;align-items:center;gap:12px;font:600 21px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.brand img{width:42px;height:42px;}
.links{display:flex;gap:4px;padding:6px;border-radius:999px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);}
.links a{padding:8px 16px;border-radius:999px;color:rgba(255,255,255,.82);font-size:14.5px;} .links a:first-child{background:#fbf6e9;color:#134528;font-weight:600;}
.btn{display:inline-flex;align-items:center;gap:10px;height:52px;padding:0 26px;border-radius:999px;font-weight:600;font-size:15px;}
.btn--gold{background:#c9a961;color:#062707;} .btn--gold:hover{color:#062707;}
.btn--green{background:#134528;color:#fbf6e9;} .btn--green:hover{color:#fff;}
.hero__body{position:relative;z-index:2;width:1240px;margin:60px auto 0;display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:60px;align-items:end;color:#fbf6e9;}
.hero small{color:#e2c77f;font-size:13.5px;font-weight:600;letter-spacing:.22em;text-transform:uppercase;}
.hero h1{font:600 100px/.92 "Cormorant Garamond",serif;margin:20px 0 0;letter-spacing:-.015em;}
.hero h1 em{font-weight:500;color:#e2c77f;}
.hero__side p{font-size:18px;color:rgba(255,255,255,.85);margin-bottom:28px;}

.stage{position:relative;z-index:4;width:1240px;margin:-230px auto 0;border-radius:36px;padding:26px;
  background:linear-gradient(160deg,rgba(255,255,255,.22),rgba(255,255,255,.06) 40%,rgba(255,255,255,.1));border:1px solid rgba(255,255,255,.35);
  -webkit-backdrop-filter:blur(28px) saturate(1.4);backdrop-filter:blur(28px) saturate(1.4);box-shadow:0 50px 90px -40px rgba(6,39,7,.6);}
.stage__hd{display:flex;justify-content:space-between;align-items:center;padding:4px 10px 22px;color:#fbf6e9;}
.stage__hd h2{font:600 40px/1 "Cormorant Garamond",serif;}
.tabs{display:flex;gap:6px;}
.tabs span{height:36px;min-width:44px;padding:0 12px;display:grid;place-items:center;border-radius:999px;font:600 16px/1 "Cormorant Garamond",serif;color:rgba(255,255,255,.8);border:1px solid rgba(255,255,255,.25);}
.tabs span.on{background:#e2c77f;color:#062707;border-color:#e2c77f;}
.shelfbox{border-radius:26px;padding:22px;background:linear-gradient(180deg,#44331b,#2f230f);box-shadow:inset 0 1px 0 rgba(255,255,255,.12);}
.f-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;}
.f-row+.f-row{margin-top:20px;}
.f-row--one{grid-template-columns:minmax(0,1fr);}
.f-bay{position:relative;border-radius:16px;overflow:hidden;background:#062707;box-shadow:0 0 0 1px rgba(217,190,120,.25);}
.f-well{height:284px;display:flex;align-items:flex-end;justify-content:center;gap:5px;padding:0 24px;
  background:linear-gradient(180deg,rgba(255,236,190,.14),transparent 45%),repeating-linear-gradient(90deg,rgba(255,255,255,.015) 0 2px,transparent 2px 7px),#0a2a10;
  box-shadow:inset 0 18px 30px -10px rgba(0,0,0,.6);}
.f-plank{height:12px;background:linear-gradient(180deg,#c9a961,#8f7038);box-shadow:0 1px 0 rgba(255,255,255,.4) inset;}
.f-tag{position:absolute;top:14px;left:16px;display:flex;align-items:center;gap:8px;height:30px;padding:0 12px 0 4px;border-radius:999px;
  background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);color:rgba(255,255,255,.85);font-size:12.5px;font-weight:600;}
.f-tag span{display:grid;place-items:center;min-width:24px;height:22px;padding:0 5px;border-radius:999px;background:#c9a961;color:#062707;font-size:11px;}

.sec{width:1240px;margin:0 auto;padding-top:110px;}
.hd{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:34px;}
.hd h2{font:600 64px/1 "Cormorant Garamond",serif;color:#134528;}
.hd p{max-width:440px;color:#3a4a41;}
.bento{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:18px;}
.t{border-radius:28px;padding:36px;background:#fffdf8;box-shadow:0 1px 0 rgba(19,69,40,.06),0 24px 40px -30px rgba(19,69,40,.3);transition:transform .45s cubic-bezier(.2,.8,.2,1),box-shadow .45s;}
.t:hover{transform:translateY(-6px);box-shadow:0 1px 0 rgba(19,69,40,.06),0 40px 60px -30px rgba(19,69,40,.35);}
.t--g{background:#134528;color:#f4efe2;}
.t--photo{position:relative;overflow:hidden;color:#fff;background:#134528;}
.t--photo::before{content:"";position:absolute;inset:0;background:url(./masjid.jpg) center/cover;opacity:.55;}
.t--photo::after{content:"";position:absolute;inset:0;background:linear-gradient(0deg,rgba(6,39,7,.95),rgba(6,39,7,.2));}
.t--photo>*{position:relative;z-index:1;}
.k{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#9a7a2e;margin-bottom:14px;}
.t--g .k,.t--photo .k{color:#e2c77f;}
.lead{font:500 32px/1.28 "Cormorant Garamond",serif;text-wrap:pretty;}
.num{font:600 88px/.9 "Cormorant Garamond",serif;}
.num small{font:600 15px "Figtree",sans-serif;opacity:.65;margin-left:6px;}
.row{display:flex;justify-content:space-between;align-items:center;padding:13px 0;border-top:1px solid rgba(19,69,40,.1);}
.row:first-of-type{border-top:0;} .row b{font-weight:600;color:#134528;}
.t--g .row{border-color:rgba(244,239,226,.14);} .t--g .row b{color:#f0dca6;}
.grp h3{font:600 30px/1 "Cormorant Garamond",serif;display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;}
.grp h3 span{font:600 12.5px "Figtree",sans-serif;letter-spacing:.1em;color:#d9be78;}
.grp+.grp{margin-top:24px;}
.av{width:56px;height:56px;border-radius:50%;display:grid;place-items:center;background:#e9dfc8;color:#134528;font:600 22px/1 "Cormorant Garamond",serif;margin-bottom:18px;}
.tc small{font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#9a7a2e;}
.tc h3{font:600 32px/1.05 "Cormorant Garamond",serif;color:#134528;margin-top:4px;}
.tc p{color:#4a5a50;font-size:15px;margin-top:8px;}
.q p{font:italic 500 28px/1.34 "Cormorant Garamond",serif;margin:14px 0 22px;}
.q cite{font-style:normal;font-size:15px;opacity:.8;}
.foot{margin-top:110px;background:#062707;color:rgba(244,239,226,.7);}
.foot__in{width:1240px;margin:0 auto;padding:56px 0;display:flex;justify-content:space-between;align-items:center;}
"""
    times = "".join(
        f'<div class="grp"><h3>{l}<span>{y}</span></h3>' + timings_rows("row", "", "", [(d, f"<b>{t}</b>") for d, t in rows]).replace(' class=""', '') + '</div>'
        for l, y, rows in TIMINGS)
    body = f"""
<header class="hero">
  <div class="hero__img drift"></div><div class="hero__tint"></div>
  <nav class="nav in"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><div class="links">{nav_links("")}</div></nav>
  <div class="hero__body">
    <div><small class="in" style="--d:.1s">{NAME}</small><h1 class="in" style="--d:.25s">The Seven-Year <em>Alimiyyah</em> Program</h1></div>
    <div class="hero__side in" style="--d:.45s"><p>{SUB}</p></div>
  </div>
</header>

<section class="stage in" style="--d:.65s">
  <div class="stage__hd"><h2>Curriculum</h2><div class="tabs">{"".join(f'<span class="{"on" if i==1 else ""}">{r}</span>' for i,r in enumerate(ROMAN))}</div></div>
  <div class="shelfbox">{shelf("f-")}</div>
</section>

<section class="sec">
  <div class="bento">
    <div class="t rv-l" style="grid-column:span 7"><div class="k">Introduction</div><p class="lead">{INTRO}</p></div>
    <div class="t t--photo rv-r" style="grid-column:span 5;display:flex;flex-direction:column;justify-content:flex-end;min-height:320px"><div class="k">Our Program</div><p style="font-size:16.5px;color:rgba(255,255,255,.88)">{PROGRAM}</p></div>
  </div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Details</h2><a class="btn btn--green" href="#">Contact the masjid {ARROW}</a></div>
  <div class="bento">
    <div class="t t--g rv" style="grid-column:span 5;grid-row:span 2"><div class="k">Class timings</div>{times}</div>
    <div class="t rv rv2" style="grid-column:span 7;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px">
      <div><div class="k">Part-time</div><div class="num" style="color:#134528">$125<small>/month</small></div></div>
      <div><div class="k">Full-time</div><div class="num" style="color:#134528">$325<small>/month</small></div></div>
    </div>
    <div class="t rv rv3" style="grid-column:span 7"><div class="k">Family discounts · per student</div>{"".join(f'<div class="row"><span>{a}</span><b>{b}</b></div>' for a,b in DISC)}</div>
  </div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Our Teachers</h2></div>
  <div class="bento">{"".join(f'<div class="t tc rv{" rv2" if i==1 else " rv3" if i==2 else ""}" style="grid-column:span 4"><div class="av">{m}</div><small>{h}</small><h3>{n}</h3>{f"<p>{b}</p>" if b else ""}</div>' for i,(h,n,b,m) in enumerate(TEACHERS))}</div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Alumni Testimonies</h2></div>
  <div class="bento">{"".join(f'<figure class="t {"t--g" if i==0 else ""} q rv{" rv2" if i else ""}" style="grid-column:span 6;margin:0"><span style="color:#c9a961">{QUOTE}</span><p>{q}</p><cite><b>{n}</b> · Class of {y}</cite></figure>' for i,(q,n,y) in enumerate(TESTI))}
    <div class="t rv" style="grid-column:span 6"><div class="k">Coming soon</div><h3 style="font:600 38px/1 'Cormorant Garamond',serif;color:#134528">Articles</h3></div>
    <div class="t rv rv2" style="grid-column:span 6"><div class="k">Coming soon</div><h3 style="font:600 38px/1 'Cormorant Garamond',serif;color:#134528">Videos</h3></div>
  </div>
</section>
<footer class="foot"><div class="foot__in"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><span>[Masjid address] · [Email] · [Phone]</span><span>© 2026</span></div></footer>
"""
    return doc(css, body, [CORM, "Figtree:wght@400;500;600;700", URDU])

# ======================================================================
# 6 · NIGHT MOSAIC — duotone photo, patterned green, shelf + open book
# ======================================================================
def v6():
    css = """
body{background:#051f08;color:#f4efe2;font-family:"Hanken Grotesk",system-ui,sans-serif;font-size:16px;line-height:1.6;}
.page{position:relative;overflow:hidden;background:#051f08;}
.page::before{content:"";position:absolute;inset:0;background-image:""" + PATTERN + """;background-size:120px;opacity:.05;}
.hero{position:relative;height:880px;overflow:hidden;text-align:center;}
.hero__img{position:absolute;inset:0;background:url(./masjid.jpg) center 35%/cover;filter:grayscale(1) contrast(1.15) brightness(.9);mix-blend-mode:luminosity;opacity:.75;}
.hero__duo{position:absolute;inset:0;background:linear-gradient(180deg,#134528,#062707);}
.hero__gold{position:absolute;inset:0;background:radial-gradient(60% 50% at 50% 30%,rgba(201,169,97,.35),transparent 70%);mix-blend-mode:soft-light;}
.hero__fade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,31,8,.5),transparent 30%,transparent 55%,#051f08 100%);}
.nav{position:relative;z-index:3;height:90px;width:1240px;margin:0 auto;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;}
.brand{display:flex;align-items:center;gap:12px;font:600 21px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.brand img{width:42px;height:42px;}
.links{display:flex;gap:30px;} .links a{color:rgba(244,239,226,.75);font-size:14.5px;} .links a:first-child{color:#e2c77f;}
.gb{position:relative;border-radius:24px;background:linear-gradient(160deg,rgba(255,255,255,.07),rgba(255,255,255,.02));
  -webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px);}
/* a gold edge that fades around the corners - masked so only the 1px ring paints */
.gb::after{content:"";position:absolute;inset:0;border-radius:inherit;padding:1px;pointer-events:none;
  background:linear-gradient(135deg,rgba(226,199,127,.95),rgba(226,199,127,.1) 35%,rgba(226,199,127,.1) 65%,rgba(226,199,127,.75));
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;}
.btn{display:inline-flex;align-items:center;gap:10px;height:54px;padding:0 28px;border-radius:999px;font-weight:600;font-size:15px;}
.btn--gold{background:linear-gradient(180deg,#ecd394,#c29e52);color:#062707;} .btn--gold:hover{color:#062707;}
.hero__body{position:relative;z-index:2;margin-top:140px;}
.orn{width:54px;height:54px;color:#c9a961;margin:0 auto 22px;display:block;}
.hero small{color:#e2c77f;font-size:14px;letter-spacing:.34em;text-transform:uppercase;}
.hero h1{font:italic 500 124px/.92 "Cormorant Garamond",serif;color:#fbf6e9;margin:24px auto 28px;max-width:1100px;letter-spacing:-.01em;}
.hero h1 b{font-style:normal;font-weight:600;background:linear-gradient(180deg,#f3dea3,#b8924a);-webkit-background-clip:text;background-clip:text;color:transparent;}
.hero p{font-size:20px;color:rgba(244,239,226,.82);max-width:620px;margin:0 auto 40px;}
.rule{display:flex;align-items:center;gap:18px;justify-content:center;color:#c9a961;margin:0 auto 34px;}
.rule::before,.rule::after{content:"";width:120px;height:1px;background:linear-gradient(90deg,transparent,#c9a961);}
.rule::after{transform:scaleX(-1);}

.sec{position:relative;width:1240px;margin:0 auto;padding-top:110px;}
.hd{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:32px;}
.hd h2{font:600 62px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.hd h2 em{font-weight:500;color:#e2c77f;}
.hd p{max-width:420px;color:rgba(244,239,226,.65);}
.bento{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:16px;}
.t{padding:32px;transition:transform .45s cubic-bezier(.2,.8,.2,1);}
.t:hover{transform:translateY(-5px);}
.k{font-size:12px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#d9be78;margin-bottom:14px;}
.lead{font:500 31px/1.3 "Cormorant Garamond",serif;color:#fbf6e9;text-wrap:pretty;}

.m-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;}
.m-row+.m-row{margin-top:12px;}
.m-row--one{grid-template-columns:minmax(0,1fr);}
.m-bay{position:relative;border-radius:16px;background:rgba(0,0,0,.28);box-shadow:inset 0 0 0 1px rgba(217,190,120,.16);overflow:hidden;}
.m-well{height:276px;display:flex;align-items:flex-end;justify-content:center;gap:4px;padding:0 16px;background:radial-gradient(70% 55% at 50% 100%,rgba(226,199,127,.16),transparent 70%);}
.m-plank{height:6px;margin:0 10px;border-radius:3px;background:linear-gradient(90deg,transparent,#c9a961 15%,#f0dca6 50%,#c9a961 85%,transparent);box-shadow:0 0 20px rgba(226,199,127,.35);}
.m-tag{height:44px;display:flex;align-items:center;justify-content:center;gap:8px;font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:rgba(244,239,226,.7);}
.m-tag span{color:#e2c77f;font:600 17px/1 "Cormorant Garamond",serif;letter-spacing:0;}

.open{display:flex;flex-direction:column;gap:22px;}
.open__stage{height:300px;border-radius:18px;display:grid;place-items:center;background:radial-gradient(60% 60% at 50% 60%,rgba(226,199,127,.2),transparent 70%),rgba(0,0,0,.25);}
.open h3{font:600 38px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.open .u{font-family:"Noto Nastaliq Urdu",serif;font-size:20px;color:#e2c77f;line-height:2;}
.open p{color:rgba(244,239,226,.78);font-size:15.5px;}
.chips{display:flex;gap:8px;}
.chips span{font-size:12.5px;font-weight:600;padding:5px 12px;border-radius:999px;border:1px solid rgba(217,190,120,.35);color:#f0dca6;}

.price{font:600 80px/.9 "Cormorant Garamond",serif;color:#fbf6e9;}
.price small{font:500 15px "Hanken Grotesk",sans-serif;color:rgba(244,239,226,.6);margin-left:6px;}
.row{display:flex;justify-content:space-between;align-items:center;padding:13px 0;border-top:1px solid rgba(217,190,120,.14);}
.row:first-of-type{border-top:0;} .row b{font-weight:600;color:#f0dca6;}
.grp h3{font:600 30px/1 "Cormorant Garamond",serif;display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;}
.grp h3 span{font:600 12.5px "Hanken Grotesk",sans-serif;letter-spacing:.1em;color:#d9be78;}
.grp+.grp{margin-top:22px;}
.tc{text-align:center;padding:40px 30px;}
.tc .m{width:84px;height:84px;margin:0 auto 18px;display:grid;place-items:center;font:600 30px/1 "Cormorant Garamond",serif;color:#e2c77f;
  clip-path:polygon(50% 0,64% 14%,86% 14%,86% 36%,100% 50%,86% 64%,86% 86%,64% 86%,50% 100%,36% 86%,14% 86%,14% 64%,0 50%,14% 36%,14% 14%,36% 14%);background:#134528;}
.tc small{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#d9be78;}
.tc h3{font:600 32px/1.05 "Cormorant Garamond",serif;color:#fbf6e9;margin-top:4px;}
.tc p{color:rgba(244,239,226,.68);font-size:15px;margin-top:8px;}
.q p{font:italic 500 29px/1.32 "Cormorant Garamond",serif;color:#fbf6e9;margin:14px 0 22px;}
.q cite{font-style:normal;color:rgba(244,239,226,.72);} .q cite b{color:#f0dca6;}
.foot{position:relative;width:1240px;margin:110px auto 0;padding:44px 0 60px;display:flex;justify-content:space-between;align-items:center;color:rgba(244,239,226,.6);border-top:1px solid rgba(217,190,120,.2);}
"""
    times = "".join(
        f'<div class="grp"><h3>{l}<span>{y}</span></h3>' + timings_rows("row", "", "", [(d, f"<b>{t}</b>") for d, t in rows]).replace(' class=""', '') + '</div>'
        for l, y, rows in TIMINGS)
    orn = ('<svg class="orn" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2"><rect x="11" y="11" width="26" height="26"></rect>'
           '<rect x="11" y="11" width="26" height="26" transform="rotate(45 24 24)"></rect><circle cx="24" cy="24" r="5"></circle></svg>')
    body = f"""
<div class="page">
<header class="hero">
  <div class="hero__duo"></div><div class="hero__img drift"></div><div class="hero__gold"></div><div class="hero__fade"></div>
  <nav class="nav in"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><div class="links">{nav_links("")}</div>
    <div style="justify-self:end"><a class="btn gb" href="#" style="height:46px;border-radius:999px;color:#f0dca6">Contact</a></div></nav>
  <div class="hero__body">
    <div class="in" style="--d:.1s">{orn}</div>
    <small class="in" style="--d:.2s">{NAME}</small>
    <h1 class="in" style="--d:.35s">The Seven-Year <b>Alimiyyah</b> Program</h1>
    <div class="rule in" style="--d:.5s">◆</div>
    <p class="in" style="--d:.6s">{SUB}</p>
    <a class="btn btn--gold in" style="--d:.75s" href="#">View Curriculum {ARROW}</a>
  </div>
</header>

<section class="sec" style="padding-top:20px">
  <div class="bento">
    <div class="t gb rv-l" style="grid-column:span 7"><div class="k">Introduction</div><p class="lead">{INTRO}</p></div>
    <div class="t gb rv-r" style="grid-column:span 5"><div class="k">Our Program</div><p style="color:rgba(244,239,226,.82)">{PROGRAM}</p></div>
  </div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Curriculum</h2><p>Every book in the course stands on the shelf at once. Select a spine to turn it face-on.</p></div>
  <div class="bento" style="align-items:start">
    <div class="t gb rv" style="grid-column:span 8;padding:14px">{shelf("m-")}</div>
    <div class="t gb open rv rv2" style="grid-column:span 4;position:sticky;top:20px">
      <div class="open__stage">{cover()}</div>
      <div class="chips"><span>Second Year</span><span>Urdu</span></div>
      <div><h3>Achi Baatain</h3><div class="u">اچھی باتیں</div></div>
      <p>{ACHI}</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Details</h2><p>Class timings, monthly fees and the family discount.</p></div>
  <div class="bento">
    <div class="t gb rv-l" style="grid-column:span 5;grid-row:span 2"><div class="k">Class timings</div>{times}</div>
    <div class="t gb rv" style="grid-column:span 7;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px">
      <div><div class="k">Part-time</div><div class="price">$125<small>/month</small></div></div>
      <div><div class="k">Full-time</div><div class="price">$325<small>/month</small></div></div>
    </div>
    <div class="t gb rv-r" style="grid-column:span 7"><div class="k">Family discounts · per student</div>{"".join(f'<div class="row"><span>{a}</span><b>{b}</b></div>' for a,b in DISC)}</div>
  </div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Our <em>Teachers</em></h2></div>
  <div class="bento">{"".join(f'<div class="t gb tc rv{" rv2" if i==1 else " rv3" if i==2 else ""}" style="grid-column:span 4"><div class="m">{m}</div><small>{h}</small><h3>{n}</h3>{f"<p>{b}</p>" if b else ""}</div>' for i,(h,n,b,m) in enumerate(TEACHERS))}</div>
</section>

<section class="sec">
  <div class="hd rv"><h2>Alumni <em>Testimonies</em></h2></div>
  <div class="bento">{"".join(f'<figure class="t gb q rv{" rv2" if i else ""}" style="grid-column:span 6;margin:0"><span style="color:#c9a961">{QUOTE}</span><p>{q}</p><cite><b>{n}</b> · Class of {y}</cite></figure>' for i,(q,n,y) in enumerate(TESTI))}
    <div class="t gb rv" style="grid-column:span 6;display:flex;justify-content:space-between;align-items:center"><h3 style="font:600 36px/1 'Cormorant Garamond',serif">Articles</h3><span class="k" style="margin:0">Coming soon</span></div>
    <div class="t gb rv rv2" style="grid-column:span 6;display:flex;justify-content:space-between;align-items:center"><h3 style="font:600 36px/1 'Cormorant Garamond',serif">Videos</h3><span class="k" style="margin:0">Coming soon</span></div>
  </div>
</section>
<footer class="foot"><a class="brand" href="#"><img src="./logo.png" alt="">{NAME}</a><span>[Masjid address] · [Email] · [Phone]</span><span>© 2026</span></footer>
</div>
"""
    return doc(css, body, [CORM, "Hanken+Grotesk:wght@400;500;600;700", URDU])

# ======================================================================
# Bindings — the books up close
# ======================================================================
def bindings():
    css = """
body{background:#062707;color:#f4efe2;font-family:"Hanken Grotesk",system-ui,sans-serif;}
.sheet{padding:64px 72px;}
h2{font:600 56px/1 "Cormorant Garamond",serif;color:#fbf6e9;}
.sub{color:rgba(244,239,226,.7);margin-top:12px;font-size:16px;max-width:760px;line-height:1.6;}
.stage{margin-top:44px;border-radius:28px;padding:50px 40px 0;background:radial-gradient(60% 70% at 50% 0%,rgba(255,222,150,.14),transparent 70%),#041d06;box-shadow:inset 0 0 0 1px rgba(217,190,120,.2);}
.books{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));justify-items:center;align-items:end;zoom:1.9;height:260px;}
.plank{height:18px;margin:0 -40px;background:linear-gradient(180deg,#8a6b3e,#5b4627 45%,#34270f);}
.caps{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:20px;padding:26px 0 32px;}
.caps div{text-align:center;} .caps b{display:block;font:600 22px/1.1 "Cormorant Garamond",serif;color:#fbf6e9;}
.caps span{font-size:13px;color:rgba(244,239,226,.62);}
.row2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;margin-top:24px;}
.panel{border-radius:24px;padding:34px;background:rgba(255,255,255,.04);box-shadow:inset 0 0 0 1px rgba(217,190,120,.2);}
.panel h3{font:600 30px/1 "Cormorant Garamond",serif;margin-bottom:18px;}
.anat{display:flex;gap:40px;align-items:center;}
.anat .books{zoom:1.6;height:auto;display:flex;}
.anat ol{margin:0;padding-left:20px;color:rgba(244,239,226,.8);line-height:2;font-size:15px;}
.anat ol b{color:#f0dca6;font-weight:600;}
.tiltdemo{display:flex;align-items:flex-end;gap:6px;height:280px;justify-content:center;zoom:1.3;}
"""
    books = "".join(book(b) for b in REAL) + ghost(44, 214)
    caps = "".join(f'<div><b>{b["t"]}</b><span>{n}</span></div>' for b, n in zip(REAL, BINDING_NOTES)) + '<div><b>Empty slot</b><span>Awaiting a title from the masjid</span></div>'
    tb = [dict(b) for b in REAL]
    tb[1]["extra"] = "is-tilt"
    body = f"""
<div class="sheet">
  <h2>The bindings, up close</h2>
  <p class="sub">Second Year at twice the shelf size. Every spine is built from the same parts, so a new book only needs a colour and a binding type. Hover any spine to tilt it off the shelf.</p>
  <div class="stage"><div class="books">{books}</div><div class="plank"></div><div class="caps">{caps}</div></div>
  <div class="row2">
    <div class="panel"><h3>Anatomy of a spine</h3>
      <div class="anat"><div class="books">{book(REAL[0])}</div>
      <ol><li><b>Headband</b> — striped silk peeking above the boards</li><li><b>Head cap</b> — the turned-over leather at the top</li>
      <li><b>Raised bands</b> — the cords the pages are sewn on, each ruled in gilt</li><li><b>Title label</b> — a contrasting leather inlay with a gilt frame</li>
      <li><b>Subject</b> — lettered in italic between the lower bands</li><li><b>Fleurons</b> — small gilt tools in the end panels</li><li><b>Tail cap</b> — finishes the foot</li></ol></div>
    </div>
    <div class="panel"><h3>Hover · the book leans out</h3>
      <div class="tiltdemo">{"".join(book(b) for b in tb)}</div>
    </div>
  </div>
</div>
"""
    return doc(css, body, [CORM, "Hanken+Grotesk:wght@400;500;600", URDU])

def main():
    files = {
        "Main.dc.html": v1(),
        "DaylightBento.dc.html": v2(),
        "MihrabSplit.dc.html": v3(),
        "ThroughTheWindow.dc.html": v4(),
        "ShelfFirst.dc.html": v5(),
        "NightMosaic.dc.html": v6(),
        "Bindings.dc.html": bindings(),
    }
    os.makedirs(OUT, exist_ok=True)
    for name, src in files.items():
        fn = name.replace(".dc.html", ".html") if PREVIEW else name
        open(os.path.join(OUT, fn), "w").write(src)
    print("wrote", len(files), "to", OUT)

if __name__ == "__main__":
    main()

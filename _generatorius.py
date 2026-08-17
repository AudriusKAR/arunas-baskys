# -*- coding: utf-8 -*-
"""
Arūno Baškio puslapio generatorius.

Kodėl: navigacija, poraštė ir <head> kartojasi visuose puslapiuose. Kad
nereiktų taisyti septyniose vietose, jie aprašyti čia vieną kartą.

Paleidimas:  python _generatorius.py
"""
import io, os, re

TEL_RAW = "+37061170101"
TEL = "+370 611 70101"
EMAIL = "arunas@baskys.lt"
PROFILIS = "https://paslaugos.lt/arunas-baskys-av3050"
BASE_URL = "https://arunas-baskys.netlify.app"

NAV = [
    ("paslaugos.html", "Paslaugos"),
    ("sudetingi-gedimai.html", "Sudėtingi gedimai"),
    ("iranga.html", "Įranga"),
    ("patirtis.html", "Patirtis"),
    ("atsiliepimai.html", "Atsiliepimai"),
]
CTA_FILE = "registruoti-gedima.html"
CTA_TEXT = "Registruoti gedimą"


def head(title, desc, page):
    # Netlify „pretty URLs": index.html → /, kiti → /vardas-be-.html
    url = BASE_URL + "/" + ("" if page == "index.html" else page[: -len(".html")])
    return f"""<!doctype html>
<html lang="lt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0F172A">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE_URL}/images/darbas-01.jpg">
<meta property="og:locale" content="lt_LT">
<link rel="canonical" href="{url}">
<link rel="icon" href="assets/logo-mark.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
{nav(page)}
"""


def nav(page):
    links = "".join(
        f'      <a href="{f}"{" class=\"active\"" if f == page else ""}>{t}</a>\n'
        for f, t in NAV
    )
    mobile = "".join(
        f'    <a href="{f}"{" class=\"active\"" if f == page else ""}>{t} <span class="ms ms-sm">chevron_right</span></a>\n'
        for f, t in NAV
    )
    return f"""<header class="nav">
  <div class="nav-in">
    <a class="logo" href="index.html"><img src="assets/logo.png" alt="Arūnas Baškys"></a>
    <nav class="nav-links">
{links}      <a class="btn btn-primary btn-sm" href="{CTA_FILE}">{CTA_TEXT} <span class="ms ms-sm">arrow_forward</span></a>
    </nav>
    <button class="nav-toggle" aria-label="Meniu" aria-expanded="false"><span class="ms">menu</span></button>
  </div>
  <div class="nav-mobile">
{mobile}    <a class="cta" href="{CTA_FILE}">{CTA_TEXT} <span class="ms ms-sm">arrow_forward</span></a>
  </div>
</header>
"""


FOOTER = f"""<footer class="site-footer">
  <div class="foot">
    <div>
      <img src="assets/logo.png" alt="Arūnas Baškys">
      <p class="muted" style="font-size:15px; max-width:34ch">
        Specializuota techninė diagnostika, remontas ir įrangos priežiūra.
        Naujos įrangos montavimu neužsiimu.
      </p>
    </div>
    <div>
      <h4>Kontaktai</h4>
      <ul>
        <li><a href="tel:{TEL_RAW}">Telefonas: {TEL}</a></li>
        <li><a href="mailto:{EMAIL}">El. paštas: {EMAIL}</a></li>
        <li><a href="{PROFILIS}" target="_blank" rel="noopener">Paslaugos.lt profilis</a></li>
        <li class="muted" style="font-size:15px">Vilnius · visa Lietuva</li>
      </ul>
    </div>
    <div>
      <h4>Puslapiai</h4>
      <ul>
        <li><a href="paslaugos.html">Paslaugos</a></li>
        <li><a href="sudetingi-gedimai.html">Sudėtingi gedimai</a></li>
        <li><a href="iranga.html">Įrangos kategorijos</a></li>
        <li><a href="patirtis.html">Patirtis ir darbai</a></li>
        <li><a href="{CTA_FILE}">{CTA_TEXT}</a></li>
      </ul>
    </div>
    <div class="copy">© Arūnas Baškys · ŠVOK sistemų diagnostika, remontas ir priežiūra · Vilnius, visa Lietuva</div>
  </div>
</footer>

<div class="callbar">
  <a href="{CTA_FILE}"><span class="ms ms-sm">assignment</span> {CTA_TEXT}</a>
  <a href="tel:{TEL_RAW}"><span class="ms ms-sm">call</span> Skambinti</a>
</div>

<script src="assets/site.js"></script>
</body>
</html>
"""

LIGHTBOX = """<div class="lb" id="lb">
  <button class="lb-close" aria-label="Uždaryti">&times;</button>
  <button class="lb-prev" aria-label="Ankstesnė">&#8249;</button>
  <img src="" alt="">
  <button class="lb-next" aria-label="Kita">&#8250;</button>
</div>
"""


def page_head(crumb, h1, lead, index=""):
    return f"""<section class="page-head">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Pradžia</a> <span>/</span> <span>{crumb}</span></div>
    <h1 class="h-lg">{h1}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>
"""


CTA_BLOCK = f"""<section class="dark">
  <div class="wrap" style="text-align:center">
    <h2 class="h-md">Turite gedimą ar reikia įrangos priežiūros?</h2>
    <p class="lead" style="margin:16px auto 32px; max-width:60ch">
      Užpildykite trumpą formą arba paskambinkite. Kuo daugiau techninės informacijos –
      tuo greičiau įvertinsiu situaciją.
    </p>
    <div class="btn-row" style="justify-content:center">
      <a class="btn btn-blue" href="{CTA_FILE}"><span class="ms ms-sm">assignment</span> {CTA_TEXT}</a>
      <a class="btn btn-light" href="tel:{TEL_RAW}"><span class="ms ms-sm">call</span> {TEL}</a>
    </div>
  </div>
</section>
"""

STARS = '<div class="stars">' + '<span class="ms ms-sm fill">star</span>' * 5 + "</div>"

ATSILIEPIMAI = [
    ("Kuo daugiau tokių specialistų Lietuvoje! Ačiū jums", "Karolis", "Kondicionieriaus remontas · 2026"),
    ("Rekomenduoju meistrą. Atvyko savaitgalį. Sutvarkė įstrigusį filtrą, atliko profilaktiką. Greitai, atsakingai, kokybiškai.", "Rimantas", "Vėdinimo sistemos remontas · 2026"),
    ("Arūnas Baškys iš tikrųjų gali vadintis specialistu. Sutrikus šilumos siurbliui po elektros atjungimo, jis ieškojo priežasties ir priėmė sprendimą, kaip jį sutvarkyti, kad šilumos siurblys vėl veiktų. Iš tikrųjų jį rekomenduoju visiems.", "Virginija", "Šilumos siurblio gedimo paieška · 2023"),
    ("Puikus žmogus – net ir nevažiuodamas į objektą, kaip sakant, neturint tiesioginės naudos, mielai pakonsultavo dėl rekuperatoriaus užsikimšusių grotelių.", "Gintaras Grigalaitis", "Vėdinimo sistemos remontas · 2025"),
    ("Kompetentingas specialistas, viską ir net daugiau atliko pagal užsakymą. 100 % rekomenduoju.", "Marija", "Kondicionieriaus remontas · 2025"),
    ("Viskas puiku. Meistras profesionalus, viskas atlikta laiku, kokybiškai ir be klausimų.", "Aidas", "Kondicionieriaus remontas · 2025"),
    ("Operatyviai, profesionaliai bendraujantis, tvarkingas, likome patenkinti. Rekomenduoju.", "Giedrius Kavoliūnas", "Rekuperatoriaus variklių guolių keitimas · 2024"),
    ("Kokybė, žinios, atsakingumas.", "Marius Lunys", "Granulinio katilo remontas · 2023"),
    ("Labai profesionalus ir malonus meistras.", "Kristina Karvelytė", "Vėdinimo sistemos remontas · 2025"),
]


def rev_card(t, who, meta):
    return f"""      <div class="rev-card">
        {STARS}
        <p>„{t}“</p>
        <div class="rev-meta"><b>{who}</b><span>{meta}</span></div>
      </div>
"""


GALERIJA = [
    ("01", "Skaitmeninio manometro ir programėlės matavimai objekte"),
    ("03", "Komercinė šaldymo mašina – čilerio aptarnavimas"),
    ("05", "Diagnostikos ir vakuumavimo įranga objekte lauke"),
    ("06", "Šaldymo kontūro slėgių matavimas skaitmeniniu manometru"),
    ("07", "Vėdinimo kameros ir ventiliatoriaus mazgas"),
    ("09", "Šaldymo kontūro vakuumavimas prieš pildymą šaltnešiu"),
    ("10", "Lauko blokas ir prijungta diagnostikos įranga"),
    ("11", "Šaldymo agregatas su prijungtais matavimo prietaisais"),
    ("12", "Šaldymo kontūro vamzdynas ir ventilių mazgas"),
    ("13", "Automatikos spinta ir įrangos mazgas objekte"),
    ("14", "Temperatūros matavimas vamzdyne matavimo prietaisu"),
    ("15", "Vakuumo matavimas šaldymo sistemoje"),
]

KATEGORIJOS = [
    ("air_purifier_gen", "Rekuperatoriai ir vėdinimas", [
        "Rekuperatorių diagnostika ir remontas",
        "Ventiliatorių gedimai, guolių keitimas",
        "Vėdinimo kamerų diagnostika",
        "Oro srautų ir valdymo problemos",
        "Automatika ir davikliai",
        "Ventiliatoriniai konvektoriai („fancoil“)",
    ]),
    ("heat_pump", "Šilumos siurbliai", [
        "Oras–oras, oras–vanduo, geoterminiai",
        "Šaldymo kontūro diagnostika",
        "Kompresoriaus darbo analizė",
        "Elektronikos ir automatikos gedimai",
        "Darbo parametrų diagnostika",
        "Šaltnešio pildymas pagal išmatuotą perkaitimą",
    ]),
    ("ac_unit", "Kondicionieriai ir šaldymas", [
        "Split ir multi-split sistemos",
        "Komercinės kondicionavimo sistemos",
        "Šaldymo mašinos („čileriai“)",
        "Serverinių šaldymo įranga (CRAC, CCU)",
        "Pramoniniai šaldytuvai",
        "Slėgių, temperatūrų ir režimų diagnostika",
    ]),
    ("thermostat", "Šildymo įranga", [
        "Šildymo sistemų diagnostika",
        "Valdymo sistemos ir šildymo automatika",
        "Hidraulinės sistemos",
        "Cirkuliaciniai kontūrai",
        "Sistemos darbo parametrų vertinimas",
    ]),
    ("local_fire_department", "Katilai", [
        "Dujiniai katilai",
        "Granuliniai katilai",
        "Dyzeliniai katilai",
        "Kieto kuro katilai",
        "Šilumokaičių valymas",
        "Degimo mišinio optimizavimas, kasmetinis servisas",
    ]),
    ("humidity_percentage", "Baseinai ir oro paruošimas", [
        "Baseinų vėdinimo kameros su šilumos siurbliais",
        "Baseinų ventiliacinių sistemų remontas ir derinimas",
        "Ortakių sausintuvai ir drėkintuvai",
        "Baseininiai sausintuvai",
        "Ortakiniai ozono generatoriai",
    ]),
]


def kat_html():
    out = ""
    for icon, name, items in KATEGORIJOS:
        lis = "".join(f"          <li>{i}</li>\n" for i in items)
        out += f"""      <div class="cat">
        <div class="cat-top"><span class="ms ms-lg">{icon}</span><h4>{name}</h4></div>
        <ul>
{lis}        </ul>
      </div>
"""
    return out


BANNER = f"""    <div class="banner">
      <div class="banner-l">
        <div class="banner-icon"><span class="ms">contact_support</span></div>
        <div>
          <h5>Neradote savo įrangos sąraše?</h5>
          <p>
            Susisiekite. Jeigu tai susiję su šildymo, vėdinimo, kondicionavimo ar šaldymo sistema,
            pirmiausia įvertinsiu, ar galiu padėti. Nepažįstama sistema nėra priežastis jos atsisakyti –
            pirmiausia reikia suprasti, kaip ji veikia.
          </p>
        </div>
      </div>
      <a class="btn btn-outline btn-sm" href="tel:{TEL_RAW}"><span class="ms ms-sm">call</span> Susisiekti</a>
    </div>
"""

SIMPTOMAI = [
    "Įranga neveikia arba visai neįsijungia",
    "Veikia nestabiliai, su pertrūkiais",
    "Rodo klaidos kodą",
    "Nepasiekia reikiamos temperatūros",
    "Per dažnai įsijungia ir išsijungia",
    "Naudoja per daug energijos",
    "Kelia neįprastą triukšmą ar vibraciją",
    "Dirba, tačiau rezultatas netenkina",
    "Jau buvo remontuota, bet problema liko",
    "Gedimas kartojasi arba sunkiai nustatomas",
]


def simptomai_html():
    return "".join(
        f"      <li><em>{i+1:02d}</em> {t}</li>\n" for i, t in enumerate(SIMPTOMAI)
    )


# ============================================================
# PUSLAPIAI
# ============================================================

def p_index():
    revs = "".join(rev_card(*r) for r in ATSILIEPIMAI[:3])
    return head(
        "Arūnas Baškys — ŠVOK sistemų diagnostika ir remontas | Vilnius, visa Lietuva",
        "Gedimų paieška, diagnostika, remontas ir įrangos priežiūra: šilumos siurbliai, kondicionieriai, rekuperatoriai, šildymo įranga, katilai, šaldymo sistemos. Daugiau nei 25 metų patirtis.",
        "index.html",
    ) + f"""<main class="blueprint">

<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <div class="pill"><span class="pulse"></span> Gedimų paieška · Diagnostika · Remontas</div>
      <h1 class="h-lg">ŠVOK sistemų diagnostika ir remontas</h1>
      <p class="hero-sub">
        Nuo šilumos siurblio ar rekuperatoriaus iki sudėtingos komercinio objekto inžinerinės sistemos.
        <br><br>
        Gedimų paieška, diagnostika, remontas ir <strong>reguliari įrangos priežiūra</strong> –
        šilumos siurblių, kondicionierių, rekuperatorių, šildymo įrangos, katilų, šaldymo, baseinų
        ir kitose ŠVOK sistemose.
      </p>
      <div class="hero-years">Daugiau nei 25 metų praktinė patirtis</div>
      <div class="btn-row" style="margin-top:32px">
        <a class="btn btn-primary" href="{CTA_FILE}"><span class="ms ms-sm">assignment</span> {CTA_TEXT}</a>
        <a class="btn btn-outline" href="tel:{TEL_RAW}"><span class="ms ms-sm">call</span> Skambinti</a>
      </div>
      <p class="hero-note">
        <span class="ms ms-sm">warning</span>
        Sudėtingas ar nestandartinis gedimas? Tokias užduotis verta aptarti.
      </p>
    </div>
    <figure class="hero-fig">
      <img src="images/darbas-01.jpg" alt="Šaldymo kontūro parametrų matavimas skaitmeniniu manometru ir programėle">
      <div class="tag-dark">SYS_ANALYSIS: ACTIVE</div>
      <div class="tag-light"><span class="ms ms-sm">timeline</span> Duomenų registravimas</div>
    </figure>
  </div>
</section>
</main>

<div class="facts">
  <div class="facts-in">
    <div class="fact"><b>5,0</b><span>12 atsiliepimų · Paslaugos.lt</span></div>
    <div class="fact"><b>25+</b><span>metų ŠVOK servise</span></div>
    <div class="fact"><b>17</b><span>metų Londono komerciniuose pastatuose</span></div>
    <div class="fact"><b>Vilnius</b><span>ir visa Lietuva · nuo 70 €/val.</span></div>
  </div>
</div>

<main class="blueprint">
<section>
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">Ką darau</h2>
        <p>Trys kryptys: rasti priežastį, ją pašalinti ir neleisti gedimui pasikartoti</p>
      </div>
      <div class="sec-index">PASLAUGOS</div>
    </div>

    <div class="grid g3">
      <div class="card">
        <div class="card-head">
          <h3 class="h-sm">Diagnostika</h3>
          <span class="ms ms-lg fill">manage_search</span>
        </div>
        <p>
          Kai įranga dirba nestabiliai, rodo klaidų kodus, praranda efektyvumą ar suvartoja
          neįprastai daug energijos. Matavimai ir sistemos veikimo logikos analizė, o ne spėliojimas.
        </p>
        <a class="card-link" href="paslaugos.html#diagnostika">Plačiau <span class="ms ms-sm">arrow_forward</span></a>
      </div>

      <div class="card">
        <div class="card-head">
          <h3 class="h-sm">Remontas</h3>
          <span class="ms ms-lg fill">build_circle</span>
        </div>
        <p>
          Nustačius priežastį – techniškai ir ekonomiškai pagrįstas remontas. Tikslus įsikišimas
          į probleminį mazgą. Jei remontas neapsimoka, apie tai pasakau atvirai.
        </p>
        <a class="card-link" href="paslaugos.html#remontas">Plačiau <span class="ms ms-sm">arrow_forward</span></a>
      </div>

      <div class="card">
        <div class="card-head">
          <h3 class="h-sm">Aptarnavimas ir priežiūra</h3>
          <span class="ms ms-lg fill">event_repeat</span>
        </div>
        <p>
          Kasmetinis servisas ir profilaktika: valymas, filtrai, šilumokaičiai, šaltnešio kiekio
          patikra, degimo mišinio optimizavimas. Tvarkinga sistema sugenda rečiau ir naudoja mažiau.
        </p>
        <a class="card-link" href="paslaugos.html#prieziura">Plačiau <span class="ms ms-sm">arrow_forward</span></a>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">Kada verta kreiptis</h2>
        <p>Dažniausios situacijos, dėl kurių į mane kreipiasi</p>
      </div>
      <div class="sec-index">SIMPTOMAI</div>
    </div>
    <ul class="sympt">
{simptomai_html()}    </ul>
  </div>
</section>
</main>

<section class="dark">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">Sudėtingi gedimai – ne problema, o įdomi užduotis</h2>
        <p>Man įdomios sudėtingos užduotys</p>
      </div>
      <div class="sec-index">SPECIALIZACIJA</div>
    </div>
    <p class="lead body-lg" style="max-width:78ch">
      Ne visi gedimai telpa į serviso instrukcijos lentelę. Kartais reikia perprasti konkrečios
      sistemos veikimą, analizuoti matavimus, techninę dokumentaciją, automatiką ir kelių įrenginių
      tarpusavio sąveiką. Tokie darbai – viena įdomiausių mano veiklos dalių.
    </p>
    <div class="btn-row" style="margin-top:32px">
      <a class="btn btn-light" href="sudetingi-gedimai.html">
        Kada tai aktualu <span class="ms ms-sm">arrow_forward</span>
      </a>
    </div>
  </div>
</section>

<main class="blueprint">
<section>
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">Klientų atsiliepimai</h2>
        <p>Įvertinimas 5,0 iš 12 atsiliepimų Paslaugos.lt portale</p>
      </div>
      <div class="sec-index"><a href="atsiliepimai.html" style="color:inherit">VISI →</a></div>
    </div>
    <div class="rev">
{revs}    </div>
  </div>
</section>
</main>

{CTA_BLOCK}
{FOOTER}"""


def p_paslaugos():
    return head(
        "Paslaugos — diagnostika, remontas ir įrangos priežiūra | Arūnas Baškys",
        "ŠVOK sistemų gedimų diagnostika, remontas ir reguliarus įrangos aptarnavimas. Vilnius ir visa Lietuva.",
        "paslaugos.html",
    ) + f"""<main class="blueprint">
{page_head("Paslaugos", "Diagnostika, remontas ir priežiūra",
           "Trys kryptys, kurios viena kitą papildo: rasti gedimo priežastį, ją pašalinti ir prižiūrėti sistemą taip, kad gedimas nesikartotų.")}

<section id="diagnostika">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">01 — Diagnostika</h2>
        <p>Priežasties nustatymas, o ne klaidos kodo perskaitymas</p>
      </div>
      <div class="sec-index">nuo 70 €/val.</div>
    </div>
    <div class="grid g2">
      <div>
        <p class="body-lg muted">
          Diagnostika prasideda nuo klausimo „kodėl“. Matuojami realūs sistemos darbo parametrai,
          tikrinama automatika, davikliai ir įrenginių tarpusavio sąveika. Tik tada priimamas
          sprendimas, ką keisti ar derinti.
        </p>
        <p class="muted">
          Dirbu pažangia diagnostikos įranga: skaitmeniniais manometrais, termovizoriumi,
          bevieliais matavimo davikliais, vakuumo matuokliais. Matavimai leidžia pamatyti,
          kas iš tikrųjų vyksta sistemoje.
        </p>
      </div>
      <div class="card">
        <div class="card-head">
          <h3 class="h-sm">Ką apima</h3>
          <span class="ms ms-lg fill">manage_search</span>
        </div>
        <ul>
          <li><span class="ms ms-sm">check</span> Veikimo parametrų matavimas ir registravimas</li>
          <li><span class="ms ms-sm">check</span> Klaidų kodų interpretavimas</li>
          <li><span class="ms ms-sm">check</span> Termovizinė ir elektrinė analizė</li>
          <li><span class="ms ms-sm">check</span> Automatikos ir daviklių patikra</li>
          <li><span class="ms ms-sm">check</span> Šaldymo kontūro slėgių ir perkaitimo matavimas</li>
          <li><span class="ms ms-sm">check</span> Išvada: ką verta remontuoti, o ko – ne</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section id="remontas">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">02 — Remontas</h2>
        <p>Tikslus įsikišimas į probleminį mazgą</p>
      </div>
      <div class="sec-index">nuo 70 €/val.</div>
    </div>
    <div class="grid g2">
      <div>
        <p class="body-lg muted">
          Nustačius priežastį atliekamas remontas – tada, kai jis techniškai ir ekonomiškai
          pagrįstas. Be spėliojimų ir be detalių keitimo „dėl visa ko“.
        </p>
        <p class="muted">
          Jei remontas neapsimoka arba įranga jau pasiekė savo ribą, apie tai pasakau atvirai
          ir paaiškinu, kodėl.
        </p>
      </div>
      <div class="card">
        <div class="card-head">
          <h3 class="h-sm">Ką apima</h3>
          <span class="ms ms-lg fill">build_circle</span>
        </div>
        <ul>
          <li><span class="ms ms-sm">check</span> Šaldymo kontūro remontas, vakuumavimas, pildymas</li>
          <li><span class="ms ms-sm">check</span> Elektronikos plokščių defektavimas</li>
          <li><span class="ms ms-sm">check</span> Automatika ir valdikliai</li>
          <li><span class="ms ms-sm">check</span> Ventiliatorių ir variklių guolių keitimas</li>
          <li><span class="ms ms-sm">check</span> Hidraulinių mazgų ir cirkuliacinių kontūrų atstatymas</li>
          <li><span class="ms ms-sm">check</span> Sistemos darbo parametrų atstatymas ir derinimas</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section id="prieziura">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">03 — Įrangos aptarnavimas ir priežiūra</h2>
        <p>Kad gedimo išvis netektų ieškoti</p>
      </div>
      <div class="sec-index">SEZONINIS / KASMETINIS</div>
    </div>
    <div class="grid g2">
      <div>
        <p class="body-lg muted">
          Didelė dalis gedimų, į kuriuos mane kviečia, prasideda nuo paprastų dalykų: užterštų
          šilumokaičių, nekeistų filtrų, sumažėjusio šaltnešio kiekio ar niekada nederinto
          degimo mišinio.
        </p>
        <p class="muted">
          Reguliarus aptarnavimas kainuoja kelis kartus mažiau nei avarinis remontas sezono
          viduryje – ir sistema dirba efektyviau, su mažesnėmis energijos sąnaudomis.
        </p>
        <p class="muted">
          Aptarnavimą galima suderinti kaip vienkartinį darbą arba kaip kasmetinį –
          priminsiu, kada laikas.
        </p>
      </div>
      <div class="card">
        <div class="card-head">
          <h3 class="h-sm">Ką apima</h3>
          <span class="ms ms-lg fill">event_repeat</span>
        </div>
        <ul>
          <li><span class="ms ms-sm">check</span> Kasmetinis katilų servisas, degimo mišinio optimizavimas</li>
          <li><span class="ms ms-sm">check</span> Šilumokaičių valymas</li>
          <li><span class="ms ms-sm">check</span> Rekuperatorių filtrų keitimas ir vidaus valymas</li>
          <li><span class="ms ms-sm">check</span> Kondicionierių ir šilumos siurblių profilaktika</li>
          <li><span class="ms ms-sm">check</span> Šaltnešio kiekio ir sistemos sandarumo patikra</li>
          <li><span class="ms ms-sm">check</span> Oro srautų ir darbo parametrų patikra bei derinimas</li>
          <li><span class="ms ms-sm">check</span> Ataskaita: kokios būklės sistema ir ko tikėtis</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">Kada verta kreiptis</h2>
        <p>Dažniausios situacijos, dėl kurių į mane kreipiasi</p>
      </div>
      <div class="sec-index">SIMPTOMAI</div>
    </div>
    <ul class="sympt">
{simptomai_html()}    </ul>
  </div>
</section>
</main>

{CTA_BLOCK}
{FOOTER}"""


def p_sudetingi():
    return head(
        "Sudėtingi gedimai — kai priežastis nėra akivaizdi | Arūnas Baškys",
        "Nestandartiniai ir pasikartojantys ŠVOK sistemų gedimai: kai keli meistrai jau bandė, detalės pakeistos, o problema liko.",
        "sudetingi-gedimai.html",
    ) + f"""<main class="blueprint">
{page_head("Sudėtingi gedimai", "Sudėtingi gedimai – ne problema, o įdomi užduotis",
           "Ne visi gedimai telpa į serviso instrukcijos lentelę. Kartais reikia perprasti konkrečios sistemos veikimą, analizuoti matavimus, techninę dokumentaciją, automatiką ir kelių įrenginių tarpusavio sąveiką. Tokie darbai – viena įdomiausių mano veiklos dalių.")}
</main>

<section class="dark">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">Ypač aktualu, kai:</h2>
        <p>Situacijos, kuriose įprasto serviso nebeužtenka</p>
      </div>
      <div class="sec-index">01 / 07</div>
    </div>
    <ul class="checklist">
      <li><span class="ms ms-sm">arrow_forward</span> keli meistrai jau bandė spręsti problemą;</li>
      <li><span class="ms ms-sm">arrow_forward</span> pakeistos detalės, bet gedimas išliko;</li>
      <li><span class="ms ms-sm">arrow_forward</span> įranga reta arba nestandartinė;</li>
      <li><span class="ms ms-sm">arrow_forward</span> problema pasireiškia tik tam tikromis sąlygomis;</li>
      <li><span class="ms ms-sm">arrow_forward</span> neaišku, ar gedimas mechaninis, elektrinis, automatikos, ar hidraulinės sistemos;</li>
      <li><span class="ms ms-sm">arrow_forward</span> vienas įrenginys veikia, tačiau visa sistema neveikia tinkamai;</li>
      <li><span class="ms ms-sm">arrow_forward</span> reikia suprasti ne tik įrangą, bet ir jos integraciją į visą objektą.</li>
    </ul>
    <div class="btn-row" style="margin-top:40px">
      <a class="btn btn-blue" href="{CTA_FILE}">
        Turite sudėtingą gedimą? Aprašykite problemą <span class="ms ms-sm">arrow_forward</span>
      </a>
    </div>
  </div>
</section>

<main class="blueprint">
<section>
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">„Ko negali išmatuoti, to negali kontroliuoti“</h2>
        <p>Inžinieriaus mąstysena ir darbo įrankiai</p>
      </div>
      <div class="sec-index">METODIKA</div>
    </div>

    <div class="measure">
      <figure>
        <img src="images/darbas-08.jpg" alt="Termovizinis matavimas prieš ir po remonto, Testo matavimo duomenys">
        <figcaption>PRIEŠ / PO — termovizija ir Testo 549i matavimų registravimas</figcaption>
      </figure>
      <div>
        <p class="body-lg muted">
          Geram darbui atlikti būtini geri įrankiai. Dirbu pažangia diagnostikos įranga –
          skaitmeniniais manometrais, termovizoriumi, bevieliais matavimo davikliais,
          vakuumo matuokliais.
        </p>
        <p class="muted">
          Matavimai leidžia pamatyti, kas iš tikrųjų vyksta sistemoje, o ne spėlioti. Rezultatas
          užfiksuojamas skaičiais – prieš ir po remonto.
        </p>
        <div class="quotes">
          <blockquote class="quote">„Kiekvienas sudėtingas gedimas pirmiausia yra techninis klausimas, į kurį reikia rasti atsakymą.“</blockquote>
          <blockquote class="quote">„Man įdomiausi darbai prasideda ten, kur atsakymas nėra akivaizdus.“</blockquote>
          <blockquote class="quote">„Nauja ar nepažįstama sistema nėra priežastis jos atsisakyti – pirmiausia reikia suprasti, kaip ji veikia.“</blockquote>
          <blockquote class="quote">„Didžiausia vertė atsiranda tada, kai reikia ne pakeisti detalę, o suprasti, kodėl sistema neveikia.“</blockquote>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid g3">
      <div class="card card-dark" style="grid-column:span 3">
        <span class="ms watermark">troubleshoot</span>
        <div class="card-head" style="border-color:rgba(255,255,255,.2)">
          <h3 class="h-sm">Ko nedarau</h3>
        </div>
        <p style="max-width:80ch">
          Naujos įrangos nemontuoju. Mano sritis – diagnozuoti, suremontuoti ir prižiūrėti tai, kas
          jau sumontuota: gilus sistemos veikimo išmanymas, nestandartiniai gedimai ir atvejai,
          kai kiti meistrai jau nuleido rankas.
        </p>
        <blockquote>
          <p>„Diagnostika – tai ne klaidos kodo perskaitymas. Tai priežasties nustatymas.“</p>
          <footer>— Arūnas Baškys</footer>
        </blockquote>
      </div>
    </div>
  </div>
</section>
</main>

{CTA_BLOCK}
{FOOTER}"""


def p_iranga():
    return head(
        "Įrangos kategorijos — su kokia įranga dirbu | Arūnas Baškys",
        "Rekuperatoriai, šilumos siurbliai, kondicionieriai, šaldymo mašinos, katilai, baseinų vėdinimo sistemos, sausintuvai — diagnostika, remontas ir priežiūra.",
        "iranga.html",
    ) + f"""<main class="blueprint">
{page_head("Įranga", "Įrangos kategorijos",
           "Sistemos, kurioms teikiama diagnostika, remontas ir priežiūra – nuo buto rekuperatoriaus iki komercinio objekto šaldymo mašinos. Sąrašas nėra ribojantis.")}

<section>
  <div class="wrap">
    <div class="grid g3">
{kat_html()}    </div>
{BANNER}  </div>
</section>
</main>

{CTA_BLOCK}
{FOOTER}"""


def p_patirtis():
    gal = "".join(
        f'      <button type="button"><img src="images/darbas-{n}.jpg" alt="{alt}" loading="lazy"></button>\n'
        for n, alt in GALERIJA
    )
    return head(
        "Patirtis ir darbai — 25+ metai ŠVOK servise | Arūnas Baškys",
        "ŠVOK serviso inžinierius: Senukai, BMS Megapolis, 17 metų Londono komerciniuose pastatuose (CNN, HBO, Time Warner), TaskRabbit, NIT UAB.",
        "patirtis.html",
    ) + f"""<main class="blueprint">
{page_head("Patirtis", "Daugiau nei 25 metai ŠVOK servise",
           "ŠVOK serviso inžinierius. Didelė dalis patirties sukaupta Londono komerciniuose pastatuose, kur sistemos negali sustoti, o gedimo priežastį reikia rasti greitai.")}

<section>
  <div class="wrap">
    <div class="exp">
      <ul class="tl">
        <li>
          <div class="yr">PRADŽIA</div>
          <div>
            <h3>Buitinės technikos servisas</h3>
            <p>Darbas „Senukuose“, buitinių prietaisų parduotuvėse, vėliau – „BMS Megapolis“ garantinio aptarnavimo servise.</p>
          </div>
        </li>
        <li>
          <div class="yr">17 METŲ<br>LONDONAS</div>
          <div>
            <h3>Komercinių pastatų serviso inžinierius</h3>
            <p>4 metai – St. Magnus House (3 Lower Thames St.). 11 metų – kritinio serviso inžinierius Turner House (16 Great Marlborough St.), kur veikė CNN, Time Warner, HBO, Cartoon Network ir kitos kompanijos.</p>
          </div>
        </li>
        <li>
          <div class="yr">PROJEKTAI</div>
          <div>
            <h3>Dešimtys Londono objektų</h3>
            <p>Iki ilgalaikių sutarčių – trumpalaikiai darbai per įdarbinimo agentūras. Taip susipažinta su daugelio Londono komercinių pastatų inžinerija.</p>
          </div>
        </li>
        <li>
          <div class="yr">2020<br>KARANTINAS</div>
          <div>
            <h3>350+ klientų per metus</h3>
            <p>Per darbų platformą „TaskRabbit“ kaip inžinierius aplankyta virš 350 klientų. Surinkta 100 penkių žvaigždučių atsiliepimų iš 103.</p>
          </div>
        </li>
        <li>
          <div class="yr">NUO 2021<br>LIETUVA</div>
          <div>
            <h3>Serviso inžinierius „NIT UAB“</h3>
            <p>Grįžus į Lietuvą – serviso inžinieriaus darbas su Lietuvos objektais.</p>
          </div>
        </li>
        <li>
          <div class="yr">ŠIANDIEN</div>
          <div>
            <h3>Savarankiška diagnostikos, remonto ir priežiūros praktika</h3>
            <p>Vilnius ir visa Lietuva. Buitinė ir komercinė įranga. Įvertinimas 5,0 iš 12 atsiliepimų Paslaugos.lt portale.</p>
          </div>
        </li>
      </ul>

      <div class="proof">
        <figure>
          <img src="images/darbas-02.jpg" alt="TaskRabbit atsiliepimų suvestinė: 103 atsiliepimai, 4,9 įvertinimas">
          <figcaption>„TASKRABBIT“ LONDONAS — 103 atsiliepimai, 4,9</figcaption>
        </figure>
        <figure>
          <img src="images/darbas-04.jpg" alt="Londono klientų atsiliepimai apie Arūno darbą">
          <figcaption>LONDONO KLIENTŲ ATSILIEPIMAI</figcaption>
        </figure>
        <div class="card" style="padding:24px">
          <h3 class="h-sm" style="font-size:18px; margin-bottom:12px">Ką tai reiškia praktiškai</h3>
          <p style="font-size:15px; margin-bottom:12px">
            Komerciniame pastate sistema negali „palaukti iki rytojaus“. Tokia aplinka išmoko dirbti
            metodiškai: matuoti, tikrinti versijas, skaityti dokumentaciją ir suprasti visos sistemos
            logiką, o ne tik atskirą įrenginį.
          </p>
          <p style="font-size:15px; margin:0">Ta pati metodika taikoma ir privačiame name – tik mastelis kitas.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="galerija">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">Iš darbo objektuose</h2>
        <p>Matavimai, šaldymo kontūrai, automatika, vėdinimo kameros, komercinė šaldymo įranga</p>
      </div>
      <div class="sec-index">FOTO</div>
    </div>
    <div class="gal" id="gal">
{gal}    </div>
  </div>
</section>
</main>

{CTA_BLOCK}
{LIGHTBOX}
{FOOTER}"""


def p_atsiliepimai():
    revs = "".join(rev_card(*r) for r in ATSILIEPIMAI)
    return head(
        "Klientų atsiliepimai — 5,0 įvertinimas | Arūnas Baškys",
        "Tikri klientų atsiliepimai apie ŠVOK sistemų diagnostiką ir remontą. Įvertinimas 5,0 iš 12 atsiliepimų Paslaugos.lt portale.",
        "atsiliepimai.html",
    ) + f"""<main class="blueprint">
{page_head("Atsiliepimai", "Ką sako klientai",
           "Atsiliepimai iš Paslaugos.lt portalo, kur vertinama kokybė, kaina, bendravimas ir terminai.")}

<section>
  <div class="wrap">
    <div class="score">
      <div class="num">5,0</div>
      <div>
        {STARS}
        <div class="meta" style="margin-top:8px">12 ATSILIEPIMŲ · VERTINTA KOKYBĖ, KAINA, BENDRAVIMAS, TERMINAI</div>
      </div>
    </div>
    <div class="rev">
{revs}    </div>
    <p style="margin-top:24px; font-family:var(--f-mono); font-size:13px; color:var(--slate)">
      Visi atsiliepimai – <a href="{PROFILIS}" target="_blank" rel="noopener" style="color:var(--eng-blue)">Paslaugos.lt profilyje</a>.
    </p>
  </div>
</section>
</main>

<section class="dark" id="kontaktai">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <h2 class="h-md">Kontaktai</h2>
        <p>Vilnius ir visa Lietuva · buitinė ir komercinė įranga</p>
      </div>
      <div class="sec-index">KONTAKTAI</div>
    </div>
    <div class="contact-grid">
      <div>
        <div class="sheet">
          <div class="sheet-row"><span class="k">Telefonas</span><a class="v" href="tel:{TEL_RAW}">{TEL}</a></div>
          <div class="sheet-row"><span class="k">El. paštas</span><a class="v" href="mailto:{EMAIL}">{EMAIL}</a></div>
          <div class="sheet-row"><span class="k">Regionas</span><span class="v">Vilnius · visa Lietuva</span></div>
          <div class="sheet-row"><span class="k">Įkainis</span><span class="v">nuo 70 € / val.</span></div>
          <div class="sheet-row"><span class="k">Profilis</span><a class="v" href="{PROFILIS}" target="_blank" rel="noopener">Paslaugos.lt →</a></div>
        </div>
        <div class="btn-row" style="margin-top:28px">
          <a class="btn btn-blue" href="{CTA_FILE}"><span class="ms ms-sm">assignment</span> {CTA_TEXT}</a>
          <a class="btn btn-light" href="tel:{TEL_RAW}"><span class="ms ms-sm">call</span> Skambinti</a>
        </div>
      </div>
      <div>
        <h3 class="h-sm" style="font-size:18px; margin-bottom:8px">Kad pokalbis būtų greitesnis</h3>
        <p class="lead" style="font-size:15px">Jei turite – pravartu iš karto pasakyti:</p>
        <ul class="tips">
          <li><span class="ms ms-sm">check</span> įrangos gamintoją ir modelį (užrašas ant lentelės);</li>
          <li><span class="ms ms-sm">check</span> kaip problema pasireiškia ir kada prasidėjo;</li>
          <li><span class="ms ms-sm">check</span> ar rodomas klaidos kodas;</li>
          <li><span class="ms ms-sm">check</span> ar problema nuolatinė, ar tik tam tikromis sąlygomis;</li>
          <li><span class="ms ms-sm">check</span> ką jau bandė kiti meistrai ir kokios detalės keistos;</li>
          <li><span class="ms ms-sm">check</span> objekto tipą – butas, namas ar komercinis objektas.</li>
        </ul>
      </div>
    </div>
  </div>
</section>

{FOOTER}"""


IRANGOS_TIPAI = [
    "Šilumos siurblys (oras–oras)",
    "Šilumos siurblys (oras–vanduo)",
    "Geoterminis šilumos siurblys",
    "Kondicionierius (split / multi-split)",
    "Komercinė kondicionavimo sistema",
    "Rekuperatorius / vėdinimo įranga",
    "Ventiliatorinis konvektorius („fancoil“)",
    "Dujinis katilas",
    "Granulinis katilas",
    "Dyzelinis katilas",
    "Kieto kuro katilas",
    "Šaldymo mašina („čileris“)",
    "Pramoninis šaldytuvas / šaldymo įranga",
    "Serverinės šaldymo įranga (CRAC, CCU)",
    "Baseino vėdinimo kamera / sausintuvas",
    "Šildymo sistema / automatika",
    "Kita įranga (nurodysiu aprašyme)",
]


def p_forma():
    tipai = "".join(f'            <option>{t}</option>\n' for t in IRANGOS_TIPAI)
    return head(
        "Registruoti gedimą arba užsakyti aptarnavimą | Arūnas Baškys",
        "Užpildykite formą: įrangos tipas, klaidos kodas, simptomai ir kontaktai. Kuo daugiau techninės informacijos, tuo greičiau įvertinsiu situaciją.",
        CTA_FILE,
    ) + f"""<main class="blueprint">
<section>
  <div class="wrap form-wrap">
    <div class="crumbs" style="margin-bottom:24px">
      <a href="index.html"><span class="ms ms-sm" style="vertical-align:-3px">arrow_back</span> Grįžti į pradžią</a>
    </div>

    <div class="form-box" id="form-box">
      <h1 class="h-lg" style="margin-bottom:16px">Gedimo registracija</h1>
      <p class="lead" style="font-size:18px; margin-bottom:32px">
        Pateikite kuo daugiau techninės informacijos apie sistemą ir pastebėtus simptomus.
        Tą pačią formą naudokite ir tada, kai reikia planinio įrangos aptarnavimo.
      </p>

      <form id="uzklausa" name="Gedimo registracija" method="POST" data-netlify="true"
            netlify-honeypot="bot-field" action="/aciu.html" novalidate>
        <input type="hidden" name="form-name" value="Gedimo registracija">
        <p style="display:none"><label>Nepildykite: <input name="bot-field"></label></p>

        <div class="form-section">
          <h2><span class="ms">assignment</span> Užklausos tipas</h2>
          <div class="field">
            <label for="tipas">Ko reikia <span class="req">*</span></label>
            <select id="tipas" name="tipas" required>
              <option value="">Pasirinkite užklausos tipą</option>
              <option>Gedimas – įranga neveikia arba veikia netinkamai</option>
              <option>Sudėtingas gedimas – jau buvo bandyta taisyti</option>
              <option>Įrangos aptarnavimas ir priežiūra (profilaktika)</option>
              <option>Kasmetinis katilo ar sistemos servisas</option>
              <option>Konsultacija / nuomonė dėl sistemos</option>
            </select>
            <div class="err-msg">Pasirinkite užklausos tipą</div>
          </div>
        </div>

        <div class="form-section">
          <h2><span class="ms">build</span> Įrangos informacija</h2>
          <div class="field">
            <label for="iranga">Įrangos tipas <span class="req">*</span></label>
            <select id="iranga" name="iranga" required>
              <option value="">Pasirinkite įrangos tipą</option>
{tipai}            </select>
            <div class="err-msg">Pasirinkite įrangos tipą</div>
          </div>
          <div class="field">
            <label for="modelis">Gamintojas / Modelis</label>
            <input type="text" id="modelis" name="modelis" placeholder="Pvz., Daikin Altherma 3">
            <div class="hint">
              <span class="ms ms-sm">info</span>
              Užrašas paprastai būna ant įrenginio techninių duomenų lentelės.
            </div>
          </div>
        </div>

        <div class="form-section">
          <h2><span class="ms">warning</span> Problemos aprašymas</h2>
          <div class="field">
            <label for="klaida">Klaidos kodas (jei rodo)</label>
            <input type="text" id="klaida" name="klaida" placeholder="Pvz., E-04, U4, 7H">
          </div>
          <div class="field">
            <label for="simptomai">Simptomai ir situacija <span class="req">*</span></label>
            <textarea id="simptomai" name="simptomai" required placeholder="Išsamiai aprašykite, kas vyksta. Kada prasidėjo problema? Ar atsiranda specifinėmis sąlygomis? Ar jau buvo taisyta, kokios detalės keistos?"></textarea>
            <div class="hint">
              <span class="ms ms-sm">info</span>
              Kuo detalesnis aprašymas padės greičiau įvertinti situaciją.
            </div>
            <div class="err-msg">Trumpai aprašykite, kas vyksta</div>
          </div>
        </div>

        <div class="form-section">
          <h2><span class="ms">contact_page</span> Kontaktinė informacija</h2>
          <div class="field">
            <label for="vardas">Vardas <span class="req">*</span></label>
            <input type="text" id="vardas" name="vardas" required autocomplete="name">
            <div class="err-msg">Įrašykite vardą</div>
          </div>
          <div class="field">
            <label for="telefonas">Telefonas <span class="req">*</span></label>
            <input type="tel" id="telefonas" name="telefonas" required placeholder="+370..." autocomplete="tel">
            <div class="err-msg">Įrašykite telefono numerį</div>
          </div>
          <div class="field">
            <label for="elpastas">El. paštas</label>
            <input type="email" id="elpastas" name="elpastas" placeholder="vardas@pastas.lt" autocomplete="email">
          </div>
          <div class="field">
            <label for="adresas">Objekto adresas (miestas / rajonas) <span class="req">*</span></label>
            <input type="text" id="adresas" name="adresas" required placeholder="Pvz., Vilnius, Antakalnis">
            <div class="err-msg">Nurodykite miestą ar rajoną</div>
          </div>
          <div class="field">
            <label for="objektas">Objekto tipas</label>
            <select id="objektas" name="objektas">
              <option value="">Nenurodyta</option>
              <option>Butas</option>
              <option>Privatus namas</option>
              <option>Komercinis objektas</option>
              <option>Pramoninis objektas</option>
            </select>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-blue">
            {CTA_TEXT} <span class="ms ms-sm">send</span>
          </button>
          <a class="btn btn-ghost btn-sm" href="index.html">Atšaukti</a>
          <p class="form-note">
            Paspaudus mygtuką duomenys surenkami į vieną žinutę – ją išsiųsite el. paštu arba SMS žinute.
            Skubiu atveju skambinkite <a href="tel:{TEL_RAW}" style="color:var(--eng-blue)">{TEL}</a>.
          </p>
        </div>
      </form>
    </div>

    <div class="form-done" id="form-done">
      <div class="ms ok-icon fill">check_circle</div>

      <div id="done-auto" style="display:none">
        <h2 class="h-md">Užklausa išsiųsta</h2>
        <p class="lead">
          Ačiū. Užklausa jau iškeliavo Arūnui. Su jumis susisieks nurodytu telefonu.
          Skubiu atveju skambinkite <a href="tel:{TEL_RAW}" style="color:var(--eng-blue)">{TEL}</a>.
        </p>
      </div>

      <div id="done-manual" style="display:none">
        <h2 class="h-md">Užklausa paruošta</h2>
        <p class="lead">
          Pasirinkite, kaip ją išsiųsti. Tekstą taip pat galite nukopijuoti ir atsiųsti bet kuriuo kitu būdu.
        </p>
      </div>

      <div class="summary" id="summary"></div>

      <div class="btn-row" id="send-buttons">
        <a class="btn btn-blue" id="send-mail" href="#"><span class="ms ms-sm">mail</span> Siųsti el. paštu</a>
        <a class="btn btn-outline" id="send-sms" href="#"><span class="ms ms-sm">sms</span> Siųsti SMS</a>
        <button class="btn btn-outline" id="copy-btn" type="button"><span class="ms ms-sm">content_copy</span> Kopijuoti</button>
        <a class="btn btn-outline" href="tel:{TEL_RAW}"><span class="ms ms-sm">call</span> Skambinti</a>
      </div>

      <p class="form-note" style="text-align:left; margin-top:24px">
        <a href="index.html" style="color:var(--eng-blue)">← Grįžti į pradžią</a>
        &nbsp;·&nbsp;
        <a href="#" id="back-to-form" style="color:var(--eng-blue)">Pataisyti duomenis</a>
      </p>
    </div>
  </div>
</section>
</main>

<script>
(function () {{
  var EMAIL = '{EMAIL}';
  var TEL = '{TEL_RAW}';

  var form = document.getElementById('uzklausa');
  var box = document.getElementById('form-box');
  var done = document.getElementById('form-done');
  var summary = document.getElementById('summary');

  function val(id) {{ return document.getElementById(id).value.trim(); }}
  function fieldOf(id) {{ return document.getElementById(id).closest('.field'); }}

  var required = ['tipas', 'iranga', 'simptomai', 'vardas', 'telefonas', 'adresas'];

  form.addEventListener('submit', function (e) {{
    e.preventDefault();

    var bad = null;
    required.forEach(function (id) {{
      var ok = val(id) !== '';
      fieldOf(id).classList.toggle('invalid', !ok);
      if (!ok && !bad) bad = id;
    }});
    if (bad) {{
      document.getElementById(bad).focus();
      document.getElementById(bad).scrollIntoView({{ block: 'center', behavior: 'smooth' }});
      return;
    }}

    var rows = [
      ['Užklausos tipas', val('tipas')],
      ['Įrangos tipas', val('iranga')],
      ['Gamintojas / modelis', val('modelis')],
      ['Klaidos kodas', val('klaida')],
      ['Simptomai ir situacija', val('simptomai')],
      ['Vardas', val('vardas')],
      ['Telefonas', val('telefonas')],
      ['El. paštas', val('elpastas')],
      ['Objekto adresas', val('adresas')],
      ['Objekto tipas', val('objektas')]
    ];

    var text = rows
      .filter(function (r) {{ return r[1]; }})
      .map(function (r) {{ return r[0] + ': ' + r[1]; }})
      .join('\\n');

    summary.textContent = text;

    var subject = 'Užklausa: ' + val('iranga') + ' — ' + val('vardas');
    document.getElementById('send-mail').href =
      'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text);
    document.getElementById('send-sms').href =
      'sms:' + TEL + '?body=' + encodeURIComponent(text);

    /* Pirmiausia bandom išsiųsti automatiškai (veikia ten, kur yra formų
       tarnyba, pvz. Netlify). Jei serveris to nepalaiko – parodom rankinį
       siuntimo variantą, kad užklausa nedingtų. */
    var btn = form.querySelector('button[type=submit]');
    btn.disabled = true;
    btn.innerHTML = 'Siunčiama…';

    var data = new FormData(form);
    var body = new URLSearchParams(data).toString();

    /* GitHub Pages ir vietinis failas formų nepriima – ten iš karto rankinis būdas */
    var canPost = location.protocol.indexOf('http') === 0 &&
                  location.hostname.indexOf('github.io') === -1;
    if (!canPost) {{ finish(false); return; }}

    fetch(form.getAttribute('action') || '/', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
      body: body
    }})
      .then(function (r) {{ finish(r.ok); }})
      .catch(function () {{ finish(false); }});

    function finish(auto) {{
      document.getElementById('done-auto').style.display = auto ? '' : 'none';
      document.getElementById('done-manual').style.display = auto ? 'none' : '';
      document.getElementById('send-buttons').style.display = auto ? 'none' : '';
      box.style.display = 'none';
      done.classList.add('on');
      btn.disabled = false;
      btn.innerHTML = '{CTA_TEXT} <span class="ms ms-sm">send</span>';
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}
  }});

  form.addEventListener('input', function (e) {{
    var f = e.target.closest('.field');
    if (f && e.target.value.trim()) f.classList.remove('invalid');
  }});

  document.getElementById('copy-btn').addEventListener('click', function () {{
    var btn = this;
    navigator.clipboard.writeText(summary.textContent).then(function () {{
      btn.innerHTML = '<span class="ms ms-sm">check</span> Nukopijuota';
      setTimeout(function () {{
        btn.innerHTML = '<span class="ms ms-sm">content_copy</span> Kopijuoti';
      }}, 2000);
    }});
  }});

  document.getElementById('back-to-form').addEventListener('click', function (e) {{
    e.preventDefault();
    done.classList.remove('on');
    box.style.display = '';
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }});
}})();
</script>
{FOOTER}"""


def p_aciu():
    """Padėkos puslapis – į jį nukreipiama, jei naršyklėje išjungtas JS."""
    return head(
        "Ačiū — užklausa gauta | Arūnas Baškys",
        "Užklausa gauta. Su jumis susisieks nurodytu telefonu.",
        "aciu.html",
    ) + f"""<main class="blueprint">
<section>
  <div class="wrap form-wrap">
    <div class="form-box" style="text-align:center">
      <div class="ms ok-icon fill" style="color:var(--ok); font-size:48px; margin-bottom:16px">check_circle</div>
      <h1 class="h-md">Užklausa gauta</h1>
      <p class="lead" style="margin:16px auto 32px; max-width:52ch">
        Ačiū. Su jumis susisieksiu nurodytu telefonu. Skubiu atveju skambinkite
        <a href="tel:{TEL_RAW}" style="color:var(--eng-blue)">{TEL}</a>.
      </p>
      <div class="btn-row" style="justify-content:center">
        <a class="btn btn-primary" href="index.html">Grįžti į pradžią</a>
        <a class="btn btn-outline" href="tel:{TEL_RAW}"><span class="ms ms-sm">call</span> Skambinti</a>
      </div>
    </div>
  </div>
</section>
</main>

{FOOTER}"""


PUSLAPIAI = {
    "index.html": p_index,
    "aciu.html": p_aciu,
    "paslaugos.html": p_paslaugos,
    "sudetingi-gedimai.html": p_sudetingi,
    "iranga.html": p_iranga,
    "patirtis.html": p_patirtis,
    "atsiliepimai.html": p_atsiliepimai,
    CTA_FILE: p_forma,
}

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for name, fn in PUSLAPIAI.items():
        path = os.path.join(here, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(fn())
        print("OK  %-26s %6d B" % (name, os.path.getsize(path)))

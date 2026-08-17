# TU: Gedimų registracijos formos laiško pertvarkymas (Kraulis MB)

**Užsakovas:** Audrius, Kraulis MB
**Objektas:** svetainės forma „Gedimo registracija“ ir jos siunčiamas el. laiškas
**Tikslas:** laiškas, kurį gaunu į paštą, turi būti iš karto veiksmingas — matau, kas nutiko, ir vienu paspaudimu skambinu, rašau arba atsidarau adresą žemėlapyje. Šiandien ateina nesuformatuotas tekstas be lietuviškų raidžių ir be jokių aktyvių nuorodų.

---

## 0. Pirmiausia — išsiaiškink aplinką

Prieš keisdamas ką nors, nustatyk ir parašyk man santrauką:

1. **Kur gyvena forma?** (WordPress + Contact Form 7 / WPForms / Elementor Forms / Fluent Forms; ar custom PHP; ar EviShop „verskis“ modulis.)
2. **Kur formuojamas laiško turinys?** — šablonas plugino nustatymuose, `functions.php` hook’as (`wpcf7_mail_components`, `wpforms_email_message`), ar atskiras PHP failas.
3. **Kuo siunčiama?** — `wp_mail()`, PHP `mail()`, ar SMTP pluginas (FluentSMTP, WP Mail SMTP). Ar domenui sutvarkyti SPF/DKIM/DMARC.
4. **Kur guli priedai?** — failai keliami į serverį, ar į CDN (matau `d33wubrfki0l68.cloudfront.net` nuorodas)?

Jei ko nors pasiekti negali (FTP, wp-admin, repo) — surašyk, ko trūksta, ir kol kas dirbk su šablonu iš `gedimo-laisko-sablonas.html`.

---

## 1. Esamos klaidos — ką būtina ištaisyti

| # | Problema (realus pavyzdys iš gauto laiško) | Priežastis | Sprendimas |
|---|---|---|---|
| 1 | Nėra lietuviškų raidžių: „**�ilumos siurblys**“, „Pilaite“, „persileid�ia“ | Sulaužyta UTF-8 grandinė | Žr. 2 skyrių — pilnas patikros sąrašas |
| 2 | Telefonas neaktyvus: `+37061234567` tik tekstas | Nėra `tel:` nuorodos | `<a href="tel:+37061234567">` + normalizacija (žr. 3.1) |
| 3 | El. paštas rodomas kaip Markdown: `[audrius@kraulis.lt](mailto:...)` | Turinys generuojamas Markdown, o siunčiamas kaip `text/plain` | HTML laiškas + `multipart/alternative` plain-text versija |
| 4 | Adresas „Vilnius, Pilaite“ — negalima atidaryti žemėlapyje | Nėra nuorodos | Google Maps universali nuoroda (žr. 3.3) |
| 5 | Priedai — nuogos ilgos CDN nuorodos | Nėra failo konteksto | Mygtukai su failo pavadinimu, tipu ir dydžiu |
| 6 | Rodomi tušti laukai („Priedas 3:“, „Klaidos kodas:“ kai tuščias) | Šablonas neturi sąlygų | Tuščias laukas — eilutė nerodoma visai |
| 7 | Neinformatyvi laiško tema | Fiksuotas tekstas | `Gedimas · Šilumos siurblys · Vilnius, Pilaitė · E7-01 · #2026-0817-014` |
| 8 | Spaudžiu „Atsakyti“ — eina ne klientui | Nėra `Reply-To` | `Reply-To: <kliento el. paštas>`, `From:` — visada įmonės domenas |
| 9 | Nėra užklausos numerio ir laiko | Netrūksta duomenų šaltinio | Pridėti ID, datą/laiką (Europe/Vilnius), formos URL |
| 10 | Klientas negauna patvirtinimo | Nėra autoatsako | Antras laiškas klientui (žr. 6 skyrių) |
| 11 | Neaišku, ar užklausa skubi | Nėra logikos | Žymė „SKUBU“, kai `Ko reikia = Gedimas` arba užpildytas klaidos kodas |

---

## 2. Lietuviškos raidės — patikrink VISĄ grandinę

Raidės dingsta viename konkrečiame taške; patikrink iš eilės ir pataisyk kiekvieną:

**Forma (frontend)**
- `<meta charset="UTF-8">` puslapyje
- `<form accept-charset="UTF-8">`

**Apdorojimas (PHP)**
- `mb_internal_encoding('UTF-8');`
- Escape’inimas tik su charset: `htmlspecialchars($v, ENT_QUOTES, 'UTF-8')`
- **Uždrausta** (šitie ir „valo“ diakritiką): `utf8_decode()`, `iconv('UTF-8','ASCII//TRANSLIT',...)`, `htmlentities()` be charset, WordPress `remove_accents()`, `sanitize_title()`, `sanitize_text_field()` ant viso laiško teksto

**Duomenų bazė (jei įrašoma)**
- Lentelė ir stulpeliai: `utf8mb4_unicode_ci`
- Ryšys: `SET NAMES utf8mb4` / `$wpdb->set_charset`

**Laiško antraštės**
```
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: quoted-printable
```
- Tema **privalo** būti koduota: `mb_encode_mimeheader($subject, 'UTF-8', 'B')` — kitaip lūžta būtent temoje
- Vardas `From`/`Reply-To` lauke taip pat per `mb_encode_mimeheader()`

**Testinė eilutė** (privalo pereiti visą kelią nepakitusi):
```
ąčęėįšųūž ĄČĘĖĮŠŲŪŽ — Pilaitė, šilumos siurblys, „persileidžia“
```

---

## 3. Aktyvūs elementai

### 3.1 Telefonas
Normalizuok prieš dedant į `tel:` — nuimk tarpus, brūkšnelius, skliaustus; `8…` → `+370…`.

```php
function kr_tel($raw) {
    $d = preg_replace('/[^0-9+]/', '', $raw);
    if (str_starts_with($d, '8'))    $d = '+370' . substr($d, 1);
    if (str_starts_with($d, '370'))  $d = '+' . $d;
    return $d; // +37061234567
}
```
- Nuoroda: `<a href="tel:+37061234567">+370 612 34567</a>`
- Rodomas tekstas — su tarpais, `href` — be jų
- Telefone tai turi būti **mygtukas**, ne tekstas: min. 44 px aukščio liečiamoji zona

### 3.2 El. paštas
```html
<a href="mailto:audrius@kraulis.lt?subject=Kraulis%20MB%20—%20gedimo%20u%C5%BEklausa%20%232026-0817-014">
```
- Papildomai laiške nustatyk `Reply-To`, kad tiktų ir paprastas „Atsakyti“

### 3.3 Adresas → Google Maps
Naudok **universalią** nuorodą — veikia ir telefone (atidaro programėlę), ir kompiuteryje (naršyklę):
```
https://www.google.com/maps/search/?api=1&query={urlencode(adresas)}
```
Pavyzdys: `...&query=Vilnius%2C%20Pilait%C4%97%2C%20Lietuva`

- Prie adreso visada pridėk `, Lietuva`
- **Nenaudok** `geo:`, `maps://`, `comgooglemaps://` — lūžta desktop’e ir dalyje pašto klientų
- Jei formoje bus tikslus adresas (gatvė + nr.) — naudok jį; kitu atveju miestas + rajonas

### 3.4 Priedai
- Kiekvienas priedas — atskira kortelė: piktograma pagal tipą, failo pavadinimas, dydis, mygtukas „Atidaryti“
- Jei bendras dydis < 10 MB — **prisek failus ir prie paties laiško** (kad matyčiau ir be interneto/CDN)
- Tušti priedų laukai nerodomi

---

## 4. Laiško dizainas

Pilnai laikykis `kraulis-brand` gairių. Paruoštas šablonas: **`gedimo-laisko-sablonas.html`** (peržiūra su realiais duomenimis: `perziura-pavyzdys.html`).

**Spalvos:** `#0E3A57` (gilioji mėlyna), `#2E9BD6` (oro mėlyna, saikingai), `#FBFCFD`, `#16242C` (tekstas), `#6E7E88` (antrinis), `#EAF0F4` (šviesus fonas). Kitų spalvų nenaudoti.

**Šriftai laiške:** webfontai el. pašte neveikia patikimai — naudok stack’ą
`'IBM Plex Sans', -apple-system, 'Segoe UI', Roboto, Arial, sans-serif`, o etiketėms/kodams
`'IBM Plex Mono', 'Courier New', monospace`.

**Struktūra (iš viršaus į apačią):**
1. **Antraštė** — logotipas (baltas ant `#0E3A57`), „Gedimo registracija“, užklausos Nr. ir laikas
2. **Veiksmų juosta** — 3 mygtukai: `Skambinti` · `Rašyti` · `Žemėlapis`. Iš karto po antrašte, kad matytųsi be scrollinimo
3. **Klaidos kodo blokas** — monospace, didelis, `#EAF0F4` fone (jei yra)
4. **Simptomai** — kliento tekstas, gerai skaitomas (16 px, 1.6 tarpai)
5. **Įranga** — tipas, gamintojas/modelis
6. **Objektas** — adresas (nuoroda), objekto tipas
7. **Kontaktai** — vardas, telefonas (nuoroda), paštas (nuoroda)
8. **Priedai** — kortelės
9. **Poraštė** — iš kurios formos, IP/šaltinis, laikas

**Duomenų eilutė:** etiketė — mono, DIDŽIOSIOMIS, 11 px, `#6E7E88`; reikšmė — 15–16 px, `#16242C`; skirtukas — 1 px `#EAF0F4`.

**Techniniai reikalavimai (el. pašto specifika, ne svetainė):**
- Table layout, 600 px, `role="presentation"`, `cellpadding="0" cellspacing="0" border="0"`
- **Visas CSS — inline.** Jokio flexbox, grid, `position`, išorinių CSS/JS
- Preheader (paslėptas peržiūros tekstas): `E7-01 · Vilnius, Pilaitė · +370 612 34567`
- Outlook: „bulletproof“ mygtukai su VML (`<!--[if mso]>`), `mso-line-height-rule:exactly`
- Mobile: `<style>` head’e su media query — viena kolona, mygtukai per visą plotį
- Dark mode: `<meta name="color-scheme" content="light dark">` + `@media (prefers-color-scheme: dark)`; patikrink, kad logotipas ir mygtukai išliktų matomi
- Visiems paveikslėliams — prasmingas `alt` (jei paveikslėlis neužsikrauna, `alt` turi atstoti turinį)

---

## 5. Saugumas

- Visi kliento įvesti duomenys prieš dedant į HTML — `htmlspecialchars($v, ENT_QUOTES, 'UTF-8')`
- Iš `From`, `Reply-To`, `Subject` išvalyti `\r` ir `\n` (header injection)
- El. pašto validacija `filter_var($e, FILTER_VALIDATE_EMAIL)`
- `From:` — **visada** įmonės domenas (pvz. `forma@kraulis.lt`); kliento adresas tik `Reply-To` (kitaip laiškai kris į spam’ą)

---

## 6. Formos patobulinimai (antras etapas)

- **Įrangos tipas** — `select` (šilumos siurblys oras–vanduo / oras–oras, kondicionierius, rekuperatorius, katilas, boileris, kita)
- **Ko reikia** — radio mygtukai
- **Telefonas** — laukas su `+370` prefiksu ir validacija (9 skaitmenys)
- **Adresas** — atskiri laukai: miestas, rajonas/gatvė, namo nr. → tikslesnė Maps nuoroda
- **Priedai** — failų įkėlimas (drag & drop), iki 5 failų po 10 MB, `jpg/png/heic/pdf`; ne nuorodų vedimas ranka
- **Antispam** — honeypot laukas + laiko spąstai (jei forma užpildyta < 3 s — atmesti). CAPTCHA nereikia
- **GDPR** — sutikimo varnelė su nuoroda į privatumo politiką
- **Po išsiuntimo** — padėkos ekranas su užklausos numeriu ir žinute, per kiek susisieksime
- **Autoatsakas klientui** — tas pats brand’o dizainas, trumpai: „Gavome jūsų užklausą Nr. …“, ką pridėjo, kontaktai, kada susisieksime

---

## 7. Priėmimo kriterijai

Prieš atiduodamas darbą, patikrink ir atsakyme surašyk rezultatus:

- [ ] Testinė eilutė su `ąčęėįšųūž ĄČĘĖĮŠŲŪŽ` pereina nepakitusi — ir **laiško temoje**, ir tekste
- [ ] iPhone ir Android: telefono numerio paspaudimas atidaro skambinimą
- [ ] Adreso paspaudimas iš telefono atidaro Google Maps programėlę; iš kompiuterio — naršyklę, tikslus taškas
- [ ] „Atsakyti“ formuoja laišką klientui, ne no-reply
- [ ] Tušti laukai laiške nerodomi (patikrinti su tuščiu klaidos kodu ir be priedų)
- [ ] Peržiūrėta: Gmail (web + Android + iOS), Outlook 365 (web + desktop), Apple Mail
- [ ] Dark mode — tekstas ir logotipas matomi
- [ ] Plain-text versija skaitoma, be Markdown simbolių
- [ ] Priedai atsidaro; failai < 10 MB prisegti prie laiško
- [ ] Laiško tema informatyvi ir telpa į ~60 simbolių mobiliajame

---

## 8. Rezultatas (ką pateikti)

1. Pataisytas laiško šablonas, prijungtas prie realios formos
2. `preview.html` — peržiūrai naršyklėje su testiniais duomenimis
3. Trumpas README: kur šablonas, kaip keisti tekstus, kokie kintamieji
4. Autoatsako klientui šablonas
5. Testų rezultatų sąrašas pagal 7 skyrių

**Testiniai duomenys naudok šiuos** (tikra užklausa iš pašto):
```
Ko reikia:        Gedimas — įranga neveikia arba veikia netinkamai
Įrangos tipas:    Šilumos siurblys (oras–vanduo)
Gamintojas:       Daikin Altherma 3 ERGA08DV
Klaidos kodas:    E7-01
Simptomai:        Šilumos siurblys po elektros dingimo nebepasiekia nustatytos
                  temperatūros, kas ~2 val. rodo klaidą E7-01 ir persileidžia.
Priedas 1:        https://d33wubrfki0l68.cloudfront.net/…/irangos-lentele.jpg
Priedas 2:        https://d33wubrfki0l68.cloudfront.net/…/irangos-pasas.pdf
Vardas:           Audrius Kraulis
Telefonas:        +37061234567
El. paštas:       audrius@kraulis.lt
Adresas:          Vilnius, Pilaitė
Objekto tipas:    Privatus namas
```

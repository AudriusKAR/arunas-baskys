# Gedimų formos laiškai — kaip tai veikia

## Architektūra

Svetainė — statinė, Netlify. Forma — Netlify Forms. Gavus užklausą, Netlify
automatiškai iškviečia funkciją `netlify/functions/submission-created.mjs`,
kuri:

1. suformuoja HTML laišką pagal Kraulis brand šabloną (`gedimo-laisko-sablonas.html`
   struktūra perkelta į funkciją — laiškas generuojamas kode);
2. prisega kliento įkeltus failus prie laiško (kol bendras dydis ≤ 10 MB;
   didesnius palieka tik kaip nuorodas-korteles);
3. išsiunčia per Gmail SMTP į `NOTIFY_TO`;
4. klientui, palikusiam el. paštą, išsiunčia autoatsaką „Užklausa gauta“.

## Aplinkos kintamieji (Netlify → Site settings → Environment variables)

| Kintamasis | Reikšmė |
|---|---|
| `SMTP_USER` | Gmail adresas, iš kurio siunčiama (audrius@kraulis.lt) |
| `SMTP_PASS` | Google App Password (tas pats kaip email-tool) |
| `NOTIFY_TO` | Kam siųsti užklausas. **Perdavimui Arūnui:** pakeisti į arunas@baskys.lt ir perdeploy'inti |

Pakeitus kintamąjį būtina perdeploy'inti (`netlify deploy --prod ...`).

## Kur kas keičiama

- **Laiško tekstai / išdėstymas** — `netlify/functions/submission-created.mjs`
  (funkcijos `laiskoHtml`, `turinys` blokai, autoatsako tekstas).
- **Spalvos** — tame pačiame faile: `#0E3A57` (gilioji mėlyna), `#2E9BD6` (oro
  mėlyna), `#FBFCFD`, `#16242C`, `#6E7E88`, `#EAF0F4`. Kraulis brand.
- **Tema (subject)** — kintamasis `subject` funkcijos gale:
  `[SKUBU ·] Tipas · Įranga · Adresas · Klaida · #Nr`.
- **Skubumo logika** — `skubu`: tipas prasideda „Gedimas“/„Sudėtingas“ ARBA
  užpildytas klaidos kodas.
- **Užklausos Nr.** — `#MMMM-MMDD-NNN`, NNN = Netlify submission numeris.

## Failai šiame kataloge

- `gedimo-laisko-sablonas.html` — originalus šablonas su `{{KINTAMAISIAIS}}` (referencija)
- `perziura-pavyzdys.html` — peržiūra naršyklėje su testiniais duomenimis
- `TZ-gedimu-formos-laiskas.md` — techninė užduotis

## Deploy

```powershell
$env:NETLIFY_AUTH_TOKEN = (Get-Content "$env:USERPROFILE\.netlify-token" -Raw).Trim()
netlify deploy --prod --dir . --functions netlify/functions --skip-functions-cache --site c306bdbc-5dc5-4f74-bb21-48c605d88c10
```

## Pastabos

- Senasis Netlify standartinis el. pranešimas (plain-text „Form submission from…“)
  paliekamas įjungtas, kol patvirtinamas naujo laiško veikimas; tada išjungiamas
  (Netlify API: DELETE /api/v1/hooks/{id}), kad nesidubliuotų.
- „Lietuviškų raidžių dingimo“ problema buvo tik testavimo įrankio (Windows curl)
  artefaktas — naršyklės siunčia UTF-8 teisingai. Formoje papildomai nustatyta
  `accept-charset="UTF-8"`.

/* Netlify event funkcija: suveikia gavus formos užklausą (submission-created).
   Suformuoja HTML laišką pagal Kraulis šabloną (email/gedimo-laisko-sablonas.html
   struktūra perkelta čia, nes funkcija turi būti savarankiška) ir išsiunčia per
   Gmail SMTP. Klientui, palikusiam el. paštą, išsiunčiamas autoatsakas.

   Aplinkos kintamieji (Netlify → Environment variables):
     SMTP_USER  – Gmail adresas, iš kurio siunčiama
     SMTP_PASS  – Google App Password
     NOTIFY_TO  – kam siųsti užklausas (dabar audrius@kraulis.lt,
                  vėliau perjungiama į arunas@baskys.lt)
*/
import nodemailer from "nodemailer";

const FORMOS_URL = "https://arunas-baskys.netlify.app/registruoti-gedima";
const MAX_ATTACH_BYTES = 10 * 1024 * 1024; // priedai segami, kol telpa į 10 MB

/* ---------- pagalbinės ---------- */

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const nl2br = (s) => esc(s).replace(/\r?\n/g, "<br>");

function telNorm(raw) {
  let d = String(raw || "").replace(/[^0-9+]/g, "");
  if (d.startsWith("8")) d = "+370" + d.slice(1);
  else if (d.startsWith("370")) d = "+" + d;
  return d;
}

function telShow(raw) {
  const d = telNorm(raw);
  const m = d.match(/^\+370(\d{3})(\d{2})(\d{3})$/);
  return m ? `+370 ${m[1]} ${m[2]} ${m[3]}` : d || String(raw || "");
}

const mapsUrl = (adresas) =>
  "https://www.google.com/maps/search/?api=1&query=" +
  encodeURIComponent(`${adresas}, Lietuva`);

function fmtBytes(b) {
  if (!b && b !== 0) return "";
  return b >= 1024 * 1024 ? (b / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(b / 1024)) + " KB";
}

function vilniusTime(iso) {
  return new Intl.DateTimeFormat("lt-LT", {
    timeZone: "Europe/Vilnius",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  }).format(new Date(iso));
}

/* ---------- laiško HTML ---------- */

const MONO = "'IBM Plex Mono','Courier New',monospace";
const SANS = "'IBM Plex Sans',-apple-system,'Segoe UI',Roboto,Arial,sans-serif";

const label = (t, pad = "30px 0 4px 0") =>
  `<div class="t-sub" style="font-family:${MONO};font-size:11px;letter-spacing:1.5px;color:#6E7E88;text-transform:uppercase;padding:${pad};">${t}</div>`;

const row = (k, vHtml) => `<tr><td class="rule" style="border-bottom:1px solid #EAF0F4;padding:12px 0;">
  ${k ? `<span class="t-sub" style="font-family:${SANS};font-size:13px;color:#6E7E88;">${k}</span><br>` : ""}
  ${vHtml}</td></tr>`;

const val = (v, extra = "") =>
  `<span class="t-main" style="font-family:${SANS};font-size:16px;color:#16242C;${extra}">${v}</span>`;

const link = (href, text) =>
  `<a href="${href}" style="font-family:${SANS};font-size:16px;color:#2E9BD6;text-decoration:none;font-weight:600;">${text}</a>`;

function btn(href, text, primary) {
  const bg = primary ? "#2E9BD6" : "#FBFCFD";
  const fg = primary ? "#FFFFFF" : "#0E3A57";
  return `<td class="btn-cell" width="33%" style="padding-right:8px;">
    <a class="btn-a" href="${href}" style="display:block;background:${bg};color:${fg};font-family:${SANS};font-size:14px;font-weight:600;text-decoration:none;text-align:center;padding:14px 10px;border-radius:6px;mso-line-height-rule:exactly;line-height:16px;">${text}</a>
  </td>`;
}

function priedoKortele(f) {
  const tipas = (f.filename || "").split(".").pop().toUpperCase();
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:8px;">
  <tr><td class="soft" style="background:#EAF0F4;border-radius:6px;padding:14px 16px;">
    <table role="presentation" width="100%"><tr>
      <td><span class="t-main" style="font-family:${SANS};font-size:15px;color:#16242C;font-weight:600;">${esc(f.filename)}</span><br>
          <span class="t-sub" style="font-family:${MONO};font-size:11px;color:#6E7E88;">${tipas} · ${fmtBytes(f.size)}</span></td>
      <td align="right"><a href="${f.url}" style="font-family:${SANS};font-size:14px;color:#2E9BD6;text-decoration:none;font-weight:600;">Atidaryti &rsaquo;</a></td>
    </tr></table>
  </td></tr></table>`;
}

function laiskoHtml(v) {
  return `<!DOCTYPE html>
<html lang="lt"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark">
<title>Gedimo registracija ${v.nr}</title>
<style>
  body{margin:0;padding:0;width:100%!important;background:#EAF0F4;}
  table{border-collapse:collapse;} img{border:0;} a{color:#0E3A57;}
  @media only screen and (max-width:600px){
    .wrap{width:100%!important;} .px{padding-left:20px!important;padding-right:20px!important;}
    .btn-cell{display:block!important;width:100%!important;padding:0 0 10px 0!important;}
    .btn-a{display:block!important;width:auto!important;} .h1{font-size:22px!important;}
  }
  @media (prefers-color-scheme: dark){
    .card{background:#16242C!important;} .t-main{color:#FBFCFD!important;}
    .t-sub{color:#A9B7C0!important;} .rule{border-color:#2A3B45!important;} .soft{background:#1E2F38!important;}
  }
</style></head>
<body style="margin:0;padding:0;background:#EAF0F4;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">${esc(v.preheader)}&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#EAF0F4;">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" class="wrap" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;">
  <tr><td class="px" style="background:#0E3A57;padding:24px 32px;border-radius:6px 6px 0 0;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td align="left" style="font-family:Arial,sans-serif;font-size:20px;font-weight:800;letter-spacing:2px;color:#FBFCFD;">KRAULIS</td>
      <td align="right" style="font-family:${MONO};font-size:11px;color:${v.skubu ? "#FFD666" : "#8FB6CE"};letter-spacing:1px;font-weight:${v.skubu ? "700" : "400"};">${v.skubu ? "&#9888; SKUBU" : ""}</td>
    </tr></table>
    <div class="h1" style="font-family:${SANS};font-size:26px;line-height:1.2;font-weight:800;color:#FBFCFD;padding-top:20px;">${v.antraste}</div>
    <div style="font-family:${MONO};font-size:12px;color:#8FB6CE;padding-top:8px;letter-spacing:0.5px;">${v.nr} &nbsp;·&nbsp; ${v.laikas}</div>
  </td></tr>
  ${v.veiksmai ? `<tr><td class="px" style="background:#0B2F47;padding:16px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      ${btn(v.telHref, "Skambinti", true)}
      ${v.email ? btn(`mailto:${v.email}?subject=${encodeURIComponent("Kraulis MB — gedimo užklausa " + v.nr)}`, "Rašyti", false) : ""}
      ${v.adresas ? btn(v.mapsUrl, "Žemėlapis", false) : ""}
    </tr></table>
  </td></tr>` : ""}
  <tr><td class="card px" style="background:#FBFCFD;padding:28px 32px 8px 32px;">
    ${v.turinys}
    <div style="height:20px;line-height:20px;">&nbsp;</div>
  </td></tr>
  <tr><td class="px" style="background:#0E3A57;padding:20px 32px;border-radius:0 0 6px 6px;">
    <div style="font-family:${SANS};font-size:12px;line-height:1.6;color:#8FB6CE;">
      ${v.porasteTekstas} <a href="${FORMOS_URL}" style="color:#FBFCFD;text-decoration:underline;">gedimų registracijos formos</a> · ${v.laikas}<br>
      Kraulis MB · šildymas, vėdinimas, vėsinimas
    </div>
  </td></tr>
</table></td></tr></table></body></html>`;
}

/* ---------- pagrindinė logika ---------- */

export async function handler(event) {
  const payload = JSON.parse(event.body).payload;
  const d = payload.data || {};

  const created = payload.created_at || new Date().toISOString();
  const laikas = vilniusTime(created);
  const dienosDalis = new Intl.DateTimeFormat("lt-LT", {
    timeZone: "Europe/Vilnius", year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date(created)).replace(/-/g, "").slice(0, 8);
  const nr = `#${dienosDalis.slice(0, 4)}-${dienosDalis.slice(4)}-${String(payload.number || 0).padStart(3, "0")}`;

  const tipas = d.tipas || "";
  const klaida = (d.klaida || "").trim();
  const skubu = /^(Gedimas|Sudėtingas)/.test(tipas) || !!klaida;

  const telHref = "tel:" + telNorm(d.telefonas);
  const telRod = telShow(d.telefonas);
  const klientoEmail = (d.elpastas || "").trim();
  const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(klientoEmail) ? klientoEmail : "";
  const adresas = (d.adresas || "").trim();
  const maps = mapsUrl(adresas);

  const priedai = ["priedas-1", "priedas-2", "priedas-3"]
    .map((k) => d[k])
    .filter((f) => f && f.url && f.filename);

  /* turinio blokai — tušti laukai praleidžiami */
  let turinys = `<div class="t-main" style="font-family:${SANS};font-size:17px;line-height:1.45;color:#16242C;font-weight:600;">${esc(tipas)}</div>`;

  if (klaida) {
    turinys += `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:20px;">
      <tr><td class="soft" style="background:#EAF0F4;border-left:4px solid #2E9BD6;padding:16px 18px;border-radius:0 6px 6px 0;">
        <div class="t-sub" style="font-family:${MONO};font-size:11px;letter-spacing:1.5px;color:#6E7E88;text-transform:uppercase;">Klaidos kodas</div>
        <div class="t-main" style="font-family:${MONO};font-size:24px;font-weight:600;color:#0E3A57;padding-top:4px;">${esc(klaida)}</div>
      </td></tr></table>`;
  }

  turinys += label("Simptomai ir situacija", "26px 0 8px 0");
  turinys += `<div class="t-main" style="font-family:${SANS};font-size:16px;line-height:1.65;color:#16242C;">${nl2br(d.simptomai)}</div>`;

  turinys += label("Įranga");
  turinys += `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">`;
  turinys += row("Tipas", val(esc(d.iranga)));
  if ((d.modelis || "").trim()) turinys += row("Gamintojas / modelis", val(esc(d.modelis)));
  turinys += `</table>`;

  turinys += label("Objektas");
  turinys += `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">`;
  if (adresas) turinys += row("Adresas", link(maps, esc(adresas) + " &rsaquo;"));
  if ((d.objektas || "").trim()) turinys += row("Objekto tipas", val(esc(d.objektas)));
  turinys += `</table>`;

  turinys += label("Kontaktai");
  turinys += `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">`;
  turinys += row("", val(esc(d.vardas), "font-weight:600;"));
  turinys += row("", link(telHref, esc(telRod)));
  if (validEmail) turinys += row("", link("mailto:" + validEmail, esc(validEmail)));
  turinys += `</table>`;

  if (priedai.length) {
    turinys += label("Priedai", "30px 0 10px 0");
    turinys += priedai.map(priedoKortele).join("");
  }

  const html = laiskoHtml({
    nr, laikas, skubu,
    antraste: "Gedimo registracija",
    preheader: [klaida, adresas, telRod, d.iranga].filter(Boolean).join(" · "),
    veiksmai: true,
    telHref, email: validEmail, adresas, mapsUrl: maps,
    turinys,
    porasteTekstas: "Užklausa gauta iš",
  });

  /* plain-text alternatyva */
  const text = [
    `GEDIMO REGISTRACIJA ${nr} · ${laikas}${skubu ? " · SKUBU" : ""}`,
    ``, tipas,
    klaida ? `Klaidos kodas: ${klaida}` : null,
    ``, `Simptomai:`, d.simptomai, ``,
    `Įranga: ${d.iranga}`,
    (d.modelis || "").trim() ? `Gamintojas / modelis: ${d.modelis}` : null,
    adresas ? `Adresas: ${adresas} (${maps})` : null,
    (d.objektas || "").trim() ? `Objekto tipas: ${d.objektas}` : null,
    ``, `Klientas: ${d.vardas}`, `Telefonas: ${telRod}`,
    validEmail ? `El. paštas: ${validEmail}` : null,
    ...priedai.map((f, i) => `Priedas ${i + 1}: ${f.filename} — ${f.url}`),
  ].filter((x) => x !== null).join("\n");

  /* priedų prisegimas prie laiško (kol telpa į 10 MB) */
  const attachments = [];
  let used = 0;
  for (const f of priedai) {
    try {
      if (used + (f.size || 0) > MAX_ATTACH_BYTES) continue;
      const r = await fetch(f.url);
      if (!r.ok) continue;
      const buf = Buffer.from(await r.arrayBuffer());
      if (used + buf.length > MAX_ATTACH_BYTES) continue;
      used += buf.length;
      attachments.push({ filename: f.filename, content: buf });
    } catch { /* priedo nepavyko parsisiųsti – laiške lieka nuoroda */ }
  }

  const transporter = nodemailer.createTransport({
    host: "smtp.gmail.com", port: 465, secure: true,
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  });

  /* tema: informatyvi, telpanti į ~60 simbolių */
  const tipasTrumpas = tipas.split("–")[0].split("(")[0].trim() || "Užklausa";
  const subject = [skubu ? "SKUBU" : null, tipasTrumpas, d.iranga, adresas, klaida || null, nr]
    .filter(Boolean).join(" · ");

  await transporter.sendMail({
    from: { name: "Gedimų registracija · Kraulis MB", address: process.env.SMTP_USER },
    to: process.env.NOTIFY_TO,
    replyTo: validEmail ? { name: d.vardas || "", address: validEmail } : undefined,
    subject, html, text, attachments,
  });

  /* autoatsakas klientui (klaida čia nesužlugdo pagrindinio laiško) */
  if (validEmail) {
    try {
      const acHtml = laiskoHtml({
        nr, laikas, skubu: false,
        antraste: "Užklausa gauta",
        preheader: `Jūsų užklausa ${nr} gauta — susisieksime artimiausiu metu.`,
        veiksmai: false,
        telHref: "", email: "", adresas: "", mapsUrl: "",
        turinys:
          `<div class="t-main" style="font-family:${SANS};font-size:16px;line-height:1.65;color:#16242C;">
            Sveiki${d.vardas ? ", " + esc(d.vardas) : ""},<br><br>
            gavome jūsų užklausą <b>${nr}</b> (${esc(d.iranga)}${klaida ? ", klaidos kodas " + esc(klaida) : ""}).
            Susisieksime nurodytu telefonu <b>${esc(telRod)}</b> artimiausiu darbo metu.<br><br>
            Jei situacija skubi, skambinkite <a href="tel:+37061170101" style="color:#2E9BD6;font-weight:600;text-decoration:none;">+370 611 70101</a>.
          </div>` +
          (priedai.length ? label("Jūsų pridėti failai", "26px 0 10px 0") + priedai.map(priedoKortele).join("") : ""),
        porasteTekstas: "Šis patvirtinimas išsiųstas automatiškai iš",
      });
      await transporter.sendMail({
        from: { name: "Gedimų registracija · Kraulis MB", address: process.env.SMTP_USER },
        to: validEmail,
        subject: `Jūsų užklausa ${nr} gauta · Gedimo registracija`,
        html: acHtml,
        text: `Sveiki,\n\ngavome jūsų užklausą ${nr} (${d.iranga}). Susisieksime telefonu ${telRod} artimiausiu darbo metu.\n\nSkubiu atveju skambinkite +370 611 70101.`,
      });
    } catch (e) { console.error("Autoatsakas nepavyko:", e.message); }
  }

  return { statusCode: 200, body: "OK" };
}

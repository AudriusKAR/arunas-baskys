/* Netlify BACKGROUND funkcija (vardas baigiasi -background => iki 15 min).
   Paleidžia Claude diagnostikos analizę gedimo bylai ir įrašo rezultatą.
   Kviečiama iš bylos puslapio: POST {id, t}. Sauga: HMAC parašas t. */
import fs from "node:fs";
import path from "node:path";
import { dbInsert, dbUpdate, dbSelect, storageDownload, verify } from "./_supabase.mjs";

const PROMPT_VERSION = "1.1";

function promptText() {
  const kandidatai = [
    process.env.LAMBDA_TASK_ROOT ? path.join(process.env.LAMBDA_TASK_ROOT, "ai/prompts/equipment-diagnostics.md") : null,
    path.join(process.cwd(), "ai/prompts/equipment-diagnostics.md"),
    "ai/prompts/equipment-diagnostics.md",
  ].filter(Boolean);
  for (const p of kandidatai) { try { return fs.readFileSync(p, "utf8"); } catch {} }
  throw new Error("prompt failas nerastas: " + kandidatai.join(" | "));
}

/* atnaujinimai tik kol busena=vyksta — jei vartotojas nutraukė, nebeperrašom */
async function etapas(aid, tekstas) {
  await dbUpdate("gedimu_analizes", `id=eq.${aid}&busena=eq.vyksta`, { etapas: tekstas }).catch(() => {});
}

export async function handler(event) {
  const { id, t } = JSON.parse(event.body || "{}");
  if (!id || !verify(id, t)) return { statusCode: 403, body: "forbidden" };

  const bylos = await dbSelect("gedimai", `id=eq.${id}`);
  if (!bylos.length) return { statusCode: 404, body: "nera" };
  const b = bylos[0];

  /* jei analizė jau vyksta – nekartojam */
  const vykstancios = await dbSelect("gedimu_analizes", `gedimo_id=eq.${id}&busena=eq.vyksta&select=id`);
  if (vykstancios.length) return { statusCode: 200, body: "vyksta" };

  const senos = await dbSelect("gedimu_analizes", `gedimo_id=eq.${id}&select=versija,rezultatas&order=versija.desc`);
  const versija = (senos[0]?.versija || 0) + 1;

  const a = await dbInsert("gedimu_analizes", {
    gedimo_id: id, versija, prompt_version: PROMPT_VERSION,
    modelis: process.env.CLAUDE_MODEL, busena: "vyksta",
    etapas: "Analizuojami kliento duomenys…",
  });
  await dbUpdate("gedimai", `id=eq.${id}`, { statusas: "analizuojamas" }).catch(() => {});

  try {
    /* nuotraukos iš saugyklos originalia kokybe */
    await etapas(a.id, "Analizuojamos nuotraukos…");
    const images = [];
    for (const f of (b.failai || []).slice(0, 8)) {
      if (!/\.(jpe?g|png|webp|gif)$/i.test(f.pavadinimas)) continue;
      try {
        const buf = await storageDownload(f.storage_path);
        const mt = /\.png$/i.test(f.pavadinimas) ? "image/png" : /\.webp$/i.test(f.pavadinimas) ? "image/webp" : /\.gif$/i.test(f.pavadinimas) ? "image/gif" : "image/jpeg";
        images.push({ type: "image", source: { type: "base64", media_type: mt, data: buf.toString("base64") } });
      } catch (e) { console.error("foto:", f.pavadinimas, e.message); }
    }

    await etapas(a.id, "Identifikuojama įranga, ieškoma gamintojo dokumentacija…");
    const bylosDuomenys = {
      gedimo_id: id, data: b.sukurta,
      klientas: b.vardas, telefonas: b.telefonas, adresas: b.adresas,
      objekto_tipas: b.objekto_tipas, uzkausos_tipas: b.tipas,
      irangos_kategorija: b.iranga, gamintojas_modelis: b.gamintojas_modelis,
      klaidos_kodas: b.klaidos_kodas, kliento_aprasymas: b.aprasymas,
      visi_formos_laukai: b.forma, meistro_pastabos: b.pastabos,
    };
    const ankstesne = senos[0]?.rezultatas
      ? `\n\nANKSTESNĖS ANALIZĖS (v${senos[0].versija}) SANTRAUKA – atsižvelk, bet vertink naują informaciją:\n${JSON.stringify(senos[0].rezultatas.greita_isvada || "")}`
      : "";

    const req = {
      model: process.env.CLAUDE_MODEL,
      max_tokens: 40000,
      system: promptText(),
      tools: [
        { type: "web_search_20250305", name: "web_search", max_uses: 8 },
        { type: "web_fetch_20250910", name: "web_fetch", max_uses: 8 },
      ],
      messages: [{
        role: "user",
        content: [
          { type: "text", text: `GEDIMO BYLA (JSON):\n${JSON.stringify(bylosDuomenys, null, 1)}${ankstesne}\n\nPridedamos kliento nuotraukos (${images.length} vnt.). Atlik pilną diagnostikos analizę ir grąžink TIK JSON pagal nurodytą struktūrą.` },
          ...images,
        ],
      }],
    };

    await etapas(a.id, "Claude analizuoja gedimą (klaidų kodai, priežastys, planas)…");
    /* ilgoms užklausoms privalomas streaming – kitaip ryšys nutrūksta */
    req.stream = true;
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": process.env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "web-fetch-2025-09-10",
        "content-type": "application/json",
      },
      body: JSON.stringify(req),
    });
    if (!r.ok) {
      const err = await r.text();
      throw new Error(`API ${r.status}: ${err.slice(0, 300)} (req: ${r.headers.get("request-id") || ""})`);
    }

    let tekstas = "";
    const j = { usage: {} };
    let searches = 0;
    const reader = r.body.getReader();
    const dec = new TextDecoder();
    let liekana = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      liekana += dec.decode(value, { stream: true });
      const eilutes = liekana.split("\n");
      liekana = eilutes.pop();
      for (const e of eilutes) {
        if (!e.startsWith("data: ")) continue;
        let ev; try { ev = JSON.parse(e.slice(6)); } catch { continue; }
        if (ev.type === "message_start") j.usage.input_tokens = ev.message?.usage?.input_tokens || 0;
        else if (ev.type === "content_block_start" && ev.content_block?.type === "server_tool_use") {
          searches++; await etapas(a.id, `Ieškoma gamintojo dokumentacija (paieška ${searches})…`);
        }
        else if (ev.type === "content_block_delta" && ev.delta?.type === "text_delta") tekstas += ev.delta.text;
        else if (ev.type === "message_delta") {
          j.usage.output_tokens = ev.usage?.output_tokens || j.usage.output_tokens;
          if (ev.usage?.server_tool_use?.web_search_requests) j.usage.server_tool_use = ev.usage.server_tool_use;
        }
        else if (ev.type === "error") throw new Error(`${ev.error?.type}: ${ev.error?.message}`);
      }
    }

    await etapas(a.id, "Formuojamas diagnostikos planas…");
    let rezultatas;
    try {
      const m = tekstas.match(/\{[\s\S]*\}/);
      rezultatas = JSON.parse(m ? m[0] : tekstas);
    } catch { rezultatas = { greita_isvada: tekstas.slice(0, 4000), neformatuota: true }; }

    const u = j.usage || {};
    const webs = Math.max(u.server_tool_use?.web_search_requests || 0, searches);
    await dbUpdate("gedimu_analizes", `id=eq.${a.id}&busena=eq.vyksta`, {
      busena: "baigta", etapas: null, rezultatas,
      input_tokens: u.input_tokens || 0, output_tokens: u.output_tokens || 0,
      web_searches: webs, baigta: new Date().toISOString(),
    });
    return { statusCode: 200, body: "ok" };
  } catch (e) {
    console.error("analize", id, "v" + versija, process.env.CLAUDE_MODEL, e.message);
    await dbUpdate("gedimu_analizes", `id=eq.${a.id}`, {
      busena: "klaida", etapas: null, klaida: e.message, baigta: new Date().toISOString(),
    }).catch(() => {});
    return { statusCode: 500, body: "klaida" };
  }
}

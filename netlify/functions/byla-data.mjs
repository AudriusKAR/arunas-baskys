/* Gedimo bylos duomenys puslapiui: GET ?id=...&t=<parašas>
   Grąžina bylą, visų analizių sąrašą ir laikinas nuotraukų nuorodas. */
import { dbSelect, storageSignedUrl, verify } from "./_supabase.mjs";

export async function handler(event) {
  const { id, t } = event.queryStringParameters || {};
  if (!id || !verify(id, t)) return { statusCode: 403, body: "{}" };

  const bylos = await dbSelect("gedimai", `id=eq.${id}`);
  if (!bylos.length) return { statusCode: 404, body: "{}" };
  const b = bylos[0];

  const failai = [];
  for (const f of b.failai || []) {
    failai.push({ ...f, perziura: await storageSignedUrl(f.storage_path) });
  }
  const analizes = await dbSelect(
    "gedimu_analizes",
    `gedimo_id=eq.${id}&select=id,versija,busena,etapas,rezultatas,klaida,modelis,prompt_version,input_tokens,output_tokens,web_searches,kaina_usd,sukurta,baigta&order=versija.desc`
  );
  return {
    statusCode: 200,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
    body: JSON.stringify({ byla: { ...b, failai }, analizes }),
  };
}

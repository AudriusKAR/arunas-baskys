/* Gedimų sąrašas administravimui: GET ?t=<admin parašas>.
   Kiekvienai bylai grąžinamas ir jos atidarymo parašas. */
import { dbSelect, verify, sign } from "./_supabase.mjs";

export async function handler(event) {
  const { t } = event.queryStringParameters || {};
  if (!verify("admin", t)) return { statusCode: 403, body: "[]" };
  const eilutes = await dbSelect(
    "gedimai",
    "select=id,sukurta,statusas,vardas,telefonas,adresas,iranga,gamintojas_modelis,klaidos_kodas&order=sukurta.desc&limit=500"
  );
  return {
    statusCode: 200,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
    body: JSON.stringify(eilutes.map((e) => ({ ...e, t: sign(e.id) }))),
  };
}

/* Bylos papildymas iš puslapio: POST {id, t, veiksmas, ...}
   veiksmas: 'pastaba' {tekstas, rusys} | 'statusas' {statusas} | 'galutine' {laukai} */
import { dbSelect, dbUpdate, verify } from "./_supabase.mjs";

const STATUSAI = ["naujas", "analizuojamas", "reikia_info", "suplanuotas", "sutvarkyta", "uzdaryta"];

export async function handler(event) {
  if (event.httpMethod !== "POST") return { statusCode: 405, body: "" };
  const d = JSON.parse(event.body || "{}");
  if (!d.id || !verify(d.id, d.t)) return { statusCode: 403, body: "" };

  if (d.veiksmas === "pastaba" && (d.tekstas || "").trim()) {
    const b = (await dbSelect("gedimai", `id=eq.${d.id}&select=pastabos`))[0];
    const pastabos = [...(b?.pastabos || []), {
      laikas: new Date().toISOString(),
      rusys: d.rusys || "pastaba", // pastaba|matavimas|klaidos_kodas
      tekstas: String(d.tekstas).slice(0, 4000),
    }];
    await dbUpdate("gedimai", `id=eq.${d.id}`, { pastabos });
    return { statusCode: 200, body: "ok" };
  }
  if (d.veiksmas === "statusas" && STATUSAI.includes(d.statusas)) {
    await dbUpdate("gedimai", `id=eq.${d.id}`, { statusas: d.statusas });
    return { statusCode: 200, body: "ok" };
  }
  if (d.veiksmas === "nutraukti") {
    await dbUpdate("gedimu_analizes",
      `gedimo_id=eq.${d.id}&busena=eq.vyksta`,
      { busena: "klaida", etapas: null, klaida: "Nutraukta vartotojo", baigta: new Date().toISOString() });
    return { statusCode: 200, body: "ok" };
  }
  if (d.veiksmas === "galutine") {
    await dbUpdate("gedimai", `id=eq.${d.id}`, {
      statusas: "sutvarkyta",
      galutine: {
        gedimas: d.gedimas || "", darbai: d.darbai || "", dalys: d.dalys || "",
        matavimai: d.matavimai || "", rezultatas: d.rezultatas || "",
        pastabos: d.pastabos || "", laikas: new Date().toISOString(),
      },
    });
    return { statusCode: 200, body: "ok" };
  }
  return { statusCode: 400, body: "" };
}

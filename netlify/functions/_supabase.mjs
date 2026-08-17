/* Bendras Supabase REST/Storage sluoksnis Netlify funkcijoms.
   Naudojamas tik serveryje su SUPABASE_SERVICE_KEY (pilnos teisės). */
import crypto from "node:crypto";

const URL_ = process.env.SUPABASE_URL;
const KEY = process.env.SUPABASE_SERVICE_KEY;
const H = () => ({
  apikey: KEY,
  Authorization: `Bearer ${KEY}`,
  "Content-Type": "application/json",
});

export async function dbInsert(table, row) {
  const r = await fetch(`${URL_}/rest/v1/${table}`, {
    method: "POST",
    headers: { ...H(), Prefer: "return=representation" },
    body: JSON.stringify(row),
  });
  if (!r.ok) throw new Error(`${table} insert: ${r.status} ${await r.text()}`);
  return (await r.json())[0];
}

export async function dbUpdate(table, filter, patch) {
  const r = await fetch(`${URL_}/rest/v1/${table}?${filter}`, {
    method: "PATCH",
    headers: { ...H(), Prefer: "return=representation" },
    body: JSON.stringify(patch),
  });
  if (!r.ok) throw new Error(`${table} update: ${r.status} ${await r.text()}`);
  return await r.json();
}

export async function dbSelect(table, query) {
  const r = await fetch(`${URL_}/rest/v1/${table}?${query}`, { headers: H() });
  if (!r.ok) throw new Error(`${table} select: ${r.status} ${await r.text()}`);
  return await r.json();
}

/* Failas į privatų bucket'ą; grąžina storage kelią. */
export async function storageUpload(path, buf, contentType) {
  const r = await fetch(`${URL_}/storage/v1/object/gedimu-failai/${path}`, {
    method: "POST",
    headers: { apikey: KEY, Authorization: `Bearer ${KEY}`, "Content-Type": contentType, "x-upsert": "true" },
    body: buf,
  });
  if (!r.ok) throw new Error(`storage upload: ${r.status} ${await r.text()}`);
  return path;
}

export async function storageDownload(path) {
  const r = await fetch(`${URL_}/storage/v1/object/gedimu-failai/${path}`, {
    headers: { apikey: KEY, Authorization: `Bearer ${KEY}` },
  });
  if (!r.ok) throw new Error(`storage download: ${r.status}`);
  return Buffer.from(await r.arrayBuffer());
}

/* Laikina pasirašyta nuoroda failui parodyti naršyklėje (galioja 7 d.). */
export async function storageSignedUrl(path, expiresSec = 604800) {
  const r = await fetch(`${URL_}/storage/v1/object/sign/gedimu-failai/${path}`, {
    method: "POST", headers: H(), body: JSON.stringify({ expiresIn: expiresSec }),
  });
  if (!r.ok) return null;
  const j = await r.json();
  return `${URL_}/storage/v1${j.signedURL}`;
}

/* Bylos nuorodos parašas laiško mygtukui: HMAC(gedimo_id, LINK_SECRET). */
export function sign(id) {
  return crypto.createHmac("sha256", process.env.LINK_SECRET).update(String(id)).digest("hex").slice(0, 32);
}
export function verify(id, token) {
  try { return crypto.timingSafeEqual(Buffer.from(sign(id)), Buffer.from(String(token))); }
  catch { return false; }
}

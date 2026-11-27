// Serve the latest live-data snapshot at /live/board.json so this URL
// does not lag behind the baked copy shipped with the site.
const RAW = "https://raw.githubusercontent.com/Pdee1077/plja-corp/live-data/board.json";
const HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
  "Cache-Control": "public, max-age=60",
  "Content-Type": "application/json; charset=utf-8",
};

export async function onRequest({ request, env }) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: HEADERS });
  }
  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response("Method not allowed", { status: 405, headers: HEADERS });
  }
  try {
    if (env && env.CHATTER) {
      const fromKv = await env.CHATTER.get("board.json");
      if (fromKv) {
        JSON.parse(fromKv);
        return new Response(fromKv, { headers: HEADERS });
      }
    }
  } catch (e) {
    // Fall through to the public data branch.
  }
  const r = await fetch(RAW + "?t=" + Date.now(), {
    headers: { "User-Agent": "PLJALiveScanner/1.1 (+https://plja-corp.pages.dev/live/)", Accept: "application/json" },
    cf: { cacheTtl: 0 },
  });
  if (!r.ok) {
    return new Response(JSON.stringify({ error: "feed unavailable" }), { status: 502, headers: HEADERS });
  }
  const body = await r.text();
  try {
    JSON.parse(body);
  } catch (e) {
    return new Response(JSON.stringify({ error: "feed unavailable" }), { status: 502, headers: HEADERS });
  }
  return new Response(body, { headers: HEADERS });
}

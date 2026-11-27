// Serve the latest Market Chatter snapshot at /live/board.json.
// Prefer the cron worker / KV, then the live-data branch. CORS is open for Tipoff.
const RAW = "https://raw.githubusercontent.com/Pdee1077/plja-corp/live-data/board.json";
const WORKER = "https://plja-chatter-feed.analogquant.workers.dev/live/board.json";
const HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
  "Cache-Control": "public, max-age=60",
  "Content-Type": "application/json; charset=utf-8",
};

function parse(text) {
  try {
    const data = JSON.parse(text);
    if (data && data.updated && Array.isArray(data.rows)) return { data, text };
  } catch (e) {}
  return null;
}

function newer(a, b) {
  if (a && b) return new Date(a.data.updated) > new Date(b.data.updated) ? a : b;
  return a || b;
}

async function load(url) {
  const r = await fetch(url + (url.includes("?") ? "&" : "?") + "t=" + Date.now(), {
    headers: {
      "User-Agent": "PLJALiveScanner/1.1 (+https://plja-corp.pages.dev/live/)",
      Accept: "application/json",
      "Cache-Control": "no-cache",
    },
    cf: { cacheTtl: 0, cacheEverything: false },
  });
  if (!r.ok) return null;
  return parse(await r.text());
}

export async function onRequest({ request, env }) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: HEADERS });
  }
  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response("Method not allowed", { status: 405, headers: HEADERS });
  }
  let best = null;
  try {
    if (env && env.CHATTER) {
      const fromKv = await env.CHATTER.get("board.json");
      if (fromKv) best = newer(best, parse(fromKv));
    }
  } catch (e) {}
  try { best = newer(best, await load(WORKER)); } catch (e) {}
  try { best = newer(best, await load(RAW)); } catch (e) {}
  if (!best) {
    return new Response(JSON.stringify({ error: "feed unavailable" }), { status: 502, headers: HEADERS });
  }
  return new Response(best.text, { headers: HEADERS });
}

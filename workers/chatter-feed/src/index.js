/**
 * PLJA Market Chatter feed worker.
 * Cron: collect a public snapshot every 15 minutes and store it in KV.
 * GET /live/board.json (and GET /): serve that snapshot with CORS open.
 * Public APIs only (ApeWisdom, StockTwits, Yahoo). No posts, no secrets.
 */
const UA = "PLJALiveScanner/1.1 (+https://plja-corp.pages.dev/live/)";
const VERSION = "2026.11.27.1";
const ST_VOL_CALLS = 30;
const ST_FRESH_MIN = 55;
const VOLUME_MAX_AGE_MIN = 360;
const UNIVERSE = (
  "AAPL MSFT NVDA GOOGL AMZN META TSLA AVGO AMD MU TSM ASML INTC QCOM " +
  "DELL HPE ORCL CRM ADBE NOW PLTR NET CRWD ORCL CRWV NBIS IREN " +
  "NFLX DIS WMT COST TGT HD LOW NKE JPM BAC GS MS SCHW V MA COIN MSTR " +
  "XOM CVX CAT DE BA UNH LLY JNJ GME"
).split(" ");
const RAW = "https://raw.githubusercontent.com/Pdee1077/plja-corp/live-data";
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
  "Cache-Control": "public, max-age=60",
  "Content-Type": "application/json; charset=utf-8",
};

const ET = "America/New_York";

function nowET() {
  return new Date(new Date().toLocaleString("en-US", { timeZone: ET }));
}

function isoMinutesET(d) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: ET, year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", hourCycle: "h23",
  }).formatToParts(d || new Date());
  const g = (t) => parts.find((p) => p.type === t).value;
  // Eastern offset from a sample: use America/New_York ISO with offset
  const utc = (d || new Date());
  const etMs = new Date(utc.toLocaleString("en-US", { timeZone: ET })).getTime();
  const offMin = Math.round((etMs - utc.getTime()) / 60000);
  // offMin is wrong because toLocaleString + Date parses as local. Better: format offset via formatToParts timeZoneName? 
  // We'll compute offset with two formatters.
  return formatIsoET(d || new Date());
}

function formatIsoET(date) {
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: ET, year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", hourCycle: "h23",
  });
  const parts = Object.fromEntries(fmt.formatToParts(date).map((p) => [p.type, p.value]));
  const offset = tzOffset(date);
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}${offset}`;
}

function tzOffset(date) {
  // Get ET offset as ±HH:MM
  const s = date.toLocaleString("en-US", { timeZone: ET, timeZoneName: "shortOffset" });
  const m = s.match(/GMT([+-]\d+)(?::?(\d{2}))?/);
  if (!m) {
    // Fallback: Nov-Mar EST is -05:00, Mar-Nov EDT is -04:00. Use a known trick.
    const utc = date.getTime() + date.getTimezoneOffset() * 60000;
    const et = new Date(date.toLocaleString("en-US", { timeZone: "UTC" }));
    // simpler hardcoded: format with resolvedOptions is messy. Use
    const probe = new Date(date.toLocaleString("en-US", { timeZone: ET }));
    // This is unreliable in Workers. Use Intl longOffset.
    return "-05:00";
  }
  const h = Number(m[1]);
  const mm = m[2] || "00";
  const sign = h < 0 || Object.is(h, -0) || String(m[1]).startsWith("-") ? "-" : "+";
  const ah = Math.abs(h).toString().padStart(2, "0");
  return `${sign}${ah}:${mm}`;
}

function updatedEt(date) {
  const fmt = new Intl.DateTimeFormat("en-US", {
    timeZone: ET, weekday: "long", month: "short", day: "numeric", year: "numeric",
    hour: "numeric", minute: "2-digit", hour12: true,
  });
  // "Friday, Nov 27, 2026, 1:20 PM" + " ET"
  let s = fmt.format(date);
  s = s.replace(" at ", ", ").replace(/, ([0-9]{1,2},)/, ", $1"); // keep close to Python
  // Python: "%A, %b %d, %Y, %I:%M %p ET" with leading zero stripped from day/hour
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: ET, weekday: "long", month: "short", day: "numeric", year: "numeric",
    hour: "numeric", minute: "2-digit", hour12: true,
  }).formatToParts(date);
  const g = (t) => (parts.find((p) => p.type === t) || {}).value;
  return `${g("weekday")}, ${g("month")} ${g("day")}, ${g("year")}, ${g("hour")}:${g("minute")} ${g("dayPeriod")} ET`;
}

function tsEt(date) {
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat("en-CA", {
      timeZone: ET, year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hourCycle: "h23",
    }).formatToParts(date).map((p) => [p.type, p.value])
  );
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}`;
}

function num(x) {
  const n = Number(x);
  return Number.isFinite(n) ? n : null;
}

async function getJson(url, t = 20000) {
  try {
    const r = await fetch(url, { headers: { "User-Agent": UA, Accept: "application/json, text/plain, */*" }, signal: AbortSignal.timeout(t) });
    if (!r.ok) return null;
    return await r.json();
  } catch (e) {
    return null;
  }
}

async function fetchReddit() {
  const out = {};
  for (const filt of ["all-stocks", "crypto"]) {
    for (const page of [1, 2, 3]) {
      const data = await getJson(`https://apewisdom.io/api/v1.0/filter/${filt}/page/${page}`);
      for (const a of (data && data.results) || []) {
        let sym = (a.ticker || "").toUpperCase();
        if (filt === "crypto" && !sym.endsWith("-USD") && ["BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "SHIB"].includes(sym)) {
          sym = `${sym}-USD`;
        }
        if (!sym) continue;
        out[sym] = {
          sym,
          name: a.name || "",
          reddit: Number(a.mentions || 0),
          reddit_prev24: Number(a.mentions_24h_ago || 0),
          reddit_rank: a.rank,
        };
      }
    }
  }
  return out;
}

async function fetchTrending() {
  const ranks = {};
  const data = await getJson("https://api.stocktwits.com/api/2/trending/symbols.json");
  const symbols = (data && data.symbols) || [];
  symbols.forEach((s, i) => {
    let sym = (s.symbol || "").toUpperCase();
    if (!sym) return;
    if (s.type === "cryptocurrency" && !sym.endsWith("-USD") && !sym.includes(".")) {
      if (sym.endsWith(".X")) sym = sym.slice(0, -2) + "-USD";
    }
    if (sym.endsWith(".X")) sym = sym.slice(0, -2) + "-USD";
    ranks[sym] = i + 1;
  });
  return ranks;
}

function stSym(s) {
  return s.replace("-USD", ".X");
}

async function fetchVolume(sym) {
  const data = await getJson(`https://api.stocktwits.com/api/2/symbols/${encodeURIComponent(stSym(sym))}/volume.json`);
  try {
    const rows = (data.data || [])
      .filter((x) => x.volume_score != null)
      .map((x) => [String(x.timestamp).slice(0, 10), x.volume_score]);
    return [sym, rows.length ? rows : null];
  } catch (e) {
    return [sym, null];
  }
}

function median(arr) {
  if (!arr.length) return null;
  const a = [...arr].sort((x, y) => x - y);
  const mid = Math.floor(a.length / 2);
  return a.length % 2 ? a[mid] : (a[mid - 1] + a[mid]) / 2;
}

function stStats(cache, sym) {
  const raw = (cache[sym] || {}).d;
  if (!raw || raw.length < 8) return null;
  const d = [...raw].sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
  const s0 = d[d.length - 1][1];
  const prior = d.slice(0, -1).map((x) => x[1]);
  const med = median(prior.slice(-20));
  const wk = prior.length >= 7 ? prior[prior.length - 7] : null;
  let streak = 0;
  for (let i = d.length - 1; i > 0; i--) {
    if (d[i][1] > d[i - 1][1]) streak++;
    else break;
  }
  return {
    s0,
    med,
    jump: s0 / Math.max(prior[prior.length - 1], 3),
    ratio: s0 / Math.max(med, 3),
    wk: wk != null ? s0 / Math.max(wk, 3) : null,
    streak,
  };
}

async function price(r) {
  r.px = r.d1 = r.vol = null;
  r.kind = "";
  const data = await getJson(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(r.sym)}?range=3mo&interval=1d`);
  try {
    const res = data.chart.result[0];
    const q = res.indicators.quote[0];
    const offSec = res.meta.gmtoffset || 0;
    const bars = [];
    for (let i = 0; i < res.timestamp.length; i++) {
      const c = q.close[i];
      if (c == null) continue;
      const day = new Date((res.timestamp[i] + offSec) * 1000).toISOString().slice(0, 10);
      bars.push([day, c, q.volume[i] || 0]);
    }
    const todayX = new Date((Date.now() / 1000 + offSec) * 1000).toISOString().slice(0, 10);
    const prior = bars.filter((b) => b[0] < todayX);
    const last = res.meta.regularMarketPrice || bars[bars.length - 1][1];
    r.name = r.name || res.meta.shortName || "";
    r.px = last;
    const usePrior = prior.length ? prior : bars.slice(0, -1);
    r.d1 = (last / usePrior[usePrior.length - 1][1] - 1) * 100;
    const last60 = usePrior.slice(-60);
    const avg = last60.reduce((s, b) => s + b[2], 0) / Math.max(1, last60.length);
    const tv = bars[bars.length - 1][0] === todayX && !r.sym.endsWith("-USD") ? bars[bars.length - 1][2] : 0;
    const n = nowET();
    const mins = n.getHours() * 60 + n.getMinutes() - 570;
    const frac = mins > 0 ? Math.min(1.0, Math.max(0.05, mins / 390)) : null;
    r.vol = avg && frac && tv ? tv / avg / frac : null;
    const d1 = r.d1, vol = r.vol;
    if (d1 == null) r.kind = "";
    else if (Math.abs(d1) >= 5 || (vol && vol >= 2.5)) r.kind = "talk and price";
    else if (Math.abs(d1) < 2 && (!vol || vol < 1.5)) r.kind = "talk only";
    else r.kind = "some of both";
  } catch (e) {}
  return r;
}

async function newsCount(r) {
  r.n24 = null;
  if (r.sym.endsWith("-USD")) return r;
  const data = await getJson(`https://query1.finance.yahoo.com/v1/finance/search?q=${encodeURIComponent(r.sym)}&newsCount=100&quotesCount=0`);
  try {
    const items = (data && data.news) || [];
    const ages = items.filter((x) => x.providerPublishTime).map((x) => (Date.now() / 1000 - x.providerPublishTime) / 3600);
    r.n24 = ages.length ? ages.filter((a) => a <= 24).length : 0;
  } catch (e) {}
  return r;
}

function parseHistory(text) {
  const lines = String(text || "").trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const cols = line.split(",");
    const row = {};
    headers.forEach((h, i) => { row[h] = cols[i] || ""; });
    return row;
  });
}

function dumpHistory(rows) {
  const fields = ["ts_et", "sym", "reddit", "reddit_prev24", "st_rank", "yahoo", "name"];
  const esc = (v) => {
    const s = String(v == null ? "" : v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [fields.join(","), ...rows.map((r) => fields.map((k) => esc(r[k] || "")).join(","))].join("\n") + "\n";
}

function ageMin(cache, sym, n) {
  try {
    const t = cache[sym].t;
    // t is like 2026-11-27T13:20-05:00
    return (n.getTime() - new Date(t).getTime()) / 60000;
  } catch (e) {
    return 1e9;
  }
}

async function mapPool(items, limit, fn) {
  const out = new Array(items.length);
  let i = 0;
  async function worker() {
    while (i < items.length) {
      const idx = i++;
      out[idx] = await fn(items[idx], idx);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return out;
}

async function build(historyText, cache) {
  const n = new Date();
  const reddit = await fetchReddit();
  const ranks = await fetchTrending();
  const ts = tsEt(n);
  const names = [...new Set([...Object.keys(reddit), ...Object.keys(ranks), ...UNIVERSE])];
  const snap = names.map((sym) => {
    const h = reddit[sym] || {};
    return {
      ts_et: ts,
      sym,
      reddit: h.reddit || 0,
      reddit_prev24: h.reddit_prev24 != null ? h.reddit_prev24 : "",
      st_rank: ranks[sym] || "",
      yahoo: "",
      name: h.name || "",
    };
  });
  let hist = parseHistory(historyText).filter((r) => r.sym && r.ts_et);
  hist = hist.concat(snap);
  const cutoffDate = new Date(n.getTime() - 14 * 24 * 3600 * 1000);
  const cutoff = tsEt(cutoffDate);
  hist = hist.filter((r) => r.ts_et >= cutoff);

  const snaps = {};
  for (const r of hist) {
    (snaps[r.ts_et] ||= {})[r.sym] = r;
  }
  const times = Object.keys(snaps).sort();
  const curT = times[times.length - 1];
  const cur = snaps[curT];

  const cands = Object.keys(cur)
    .filter((s) => (num(cur[s].reddit) || 0) >= 10 || cur[s].st_rank)
    .sort((a, b) => (num(cur[b].reddit) || 0) - (num(cur[a].reddit) || 0));
  let want = cands.filter((s) => ageMin(cache, s, n) > ST_FRESH_MIN);
  want = want.concat(
    UNIVERSE.filter((s) => !want.includes(s) && ageMin(cache, s, n) > ST_FRESH_MIN)
      .sort((a, b) => ageMin(cache, b, n) - ageMin(cache, a, n))
  );
  const isLoud = (sym) => {
    const sv = stStats(cache, sym);
    return !!(sv && sv.s0 >= 15 && (sv.ratio >= 2 || (sv.streak >= 4 && sv.wk != null && sv.wk >= 2)));
  };
  const trendingNow = Object.keys(cur)
    .filter((s) => cur[s].st_rank && ageMin(cache, s, n) > ST_FRESH_MIN)
    .sort((a, b) => (num(cur[a].st_rank) || 99) - (num(cur[b].st_rank) || 99));
  const staleLoud = Object.keys(cache)
    .filter((s) => ageMin(cache, s, n) > ST_FRESH_MIN && isLoud(s))
    .sort((a, b) => ageMin(cache, b, n) - ageMin(cache, a, n));
  const ordered = [];
  const seen = new Set();
  for (const s of [...trendingNow, ...staleLoud, ...want]) {
    if (!seen.has(s)) { seen.add(s); ordered.push(s); }
  }
  const fetched = await mapPool(ordered.slice(0, ST_VOL_CALLS), 4, (s) => fetchVolume(s));
  const stamp = formatIsoET(n);
  for (const [s, d] of fetched) {
    if (d) cache[s] = { t: stamp, d };
  }

  const rows = [];
  const allSyms = [...new Set([...Object.keys(cur), ...Object.keys(cache)])];
  for (const sym of allSyms) {
    const h = cur[sym] || {};
    const red = num(h.reddit) || 0;
    const onst = !!h.st_rank;
    const svAll = stStats(cache, sym);
    const sv = svAll && ageMin(cache, sym, n) <= VOLUME_MAX_AGE_MIN ? svAll : null;
    const st_as_of = sv ? (cache[sym] || {}).t : null;
    const st_high = !!(sv && sv.s0 >= 15 && sv.ratio >= 2);
    const st_abn = !!(st_high && sv.jump >= 1.25);
    const st_linger = !!(st_high && !st_abn);
    const st_build = !!(sv && sv.s0 >= 15 && sv.streak >= 4 && sv.wk != null && sv.wk >= 2 && sv.jump >= 1.1);
    if (red < 10 && !onst && !st_high && !st_build) continue;
    const prev24 = num(h.reddit_prev24);
    const old = [];
    const days = new Set();
    const curDt = new Date(curT.replace(" ", "T"));
    for (const t of times) {
      const dt = new Date(t.replace(" ", "T"));
      if (cur[sym] != null && snaps[t][sym] && curDt - dt >= 20 * 3600 * 1000) {
        const v = num(snaps[t][sym].reddit);
        if (v != null) old.push(v);
        days.add(t.slice(0, 10));
      }
    }
    const base = days.size >= 3 ? median(old) : null;
    const x24 = red && prev24 != null ? red / Math.max(prev24, 5) : null;
    const xbase = red && base != null ? red / Math.max(base, 5) : null;
    const priorSeen = times.filter((t) => t < curT && snaps[t][sym]).map((t) => snaps[t][sym]);
    const wasTrending = priorSeen.some((row) => row && row.st_rank);
    const new_st = !!(onst && priorSeen.length && !wasTrending);
    const on_st_only = !!(onst && !priorSeen.length);
    const strong = [], weak = [];
    if (st_abn) strong.push(`StockTwits talk ${sv.ratio.toFixed(1)}x its 20-day normal`);
    if (st_linger) weak.push(`talk still ${sv.ratio.toFixed(1)}x normal from earlier, not rising today`);
    if (st_build) strong.push(`StockTwits building ${sv.streak} days in a row`);
    if (new_st) strong.push("new on StockTwits trending");
    else if (on_st_only) weak.push("on StockTwits trending");
    const rFlags = [];
    if (red >= 15 && x24 != null && x24 >= 3) rFlags.push(`Reddit ${x24.toFixed(1)}x the day before`);
    if (red >= 10 && prev24 != null && prev24 <= 2) rFlags.push("Reddit: new name");
    if (red >= 15 && xbase != null && xbase >= 3) rFlags.push(`Reddit ${xbase.toFixed(1)}x its own normal`);
    const confirmed = !!(sv && sv.ratio >= 1.5);
    (rFlags.length && (red >= 50 || confirmed) ? strong : weak).push(...rFlags);
    let heat = (sv ? sv.ratio : 0) + (x24 || 0) * 0.3 + (onst ? 0.6 : 0);
    if (strong.length) heat += 100;
    else if (weak.length) heat += 20;
    rows.push({
      sym, name: h.name || "", strong, weak, reddit: red, reddit_prev: prev24,
      x24: x24 != null ? Math.round(x24 * 10) / 10 : null,
      st_rank: num(h.st_rank),
      st_x_normal: sv ? Math.round(sv.ratio * 10) / 10 : null,
      st_as_of, heat,
    });
  }
  rows.sort((a, b) => b.heat - a.heat);
  let kept = rows.filter((r) => r.strong.length).slice(0, 30);
  kept = kept.concat(rows.filter((r) => !r.strong.length && r.weak.length).slice(0, 12));
  kept = await mapPool(kept, 8, (r) => price(r));
  const head = kept.filter((r) => r.strong.length);
  await mapPool(head, 6, (r) => newsCount(r));

  const publicRows = kept.map((r) => {
    const nonews = !!(r.strong.length && r.n24 != null && r.n24 <= 2);
    return {
      sym: r.sym,
      name: (r.name || "").slice(0, 40),
      group: r.strong.length ? "abnormal" : "faint",
      flags: [...(r.strong.length ? r.strong : r.weak)],
      reddit: r.reddit,
      reddit_prev: r.reddit_prev,
      x24: r.x24,
      st_rank: r.st_rank,
      st_x_normal: r.st_x_normal,
      st_as_of: r.st_as_of,
      d1: r.d1 == null ? null : Math.round(r.d1 * 10) / 10,
      vol: r.vol == null ? null : Math.round(r.vol * 10) / 10,
      n24: r.n24,
      nonews,
      kind: r.kind || "",
    };
  });

  const data = {
    version: VERSION,
    updated: formatIsoET(n),
    updated_et: updatedEt(n),
    disclaimer: "Research and education only. Not investment advice.",
    sources: "Reddit mention counts: ApeWisdom. Trending ranks and talk volume: StockTwits (ranks and scores only; no post text). Prices: Yahoo Finance. News flags use a headline count, not copied articles.",
    refresh: "A job tries to update this file every 15 minutes. GitHub can delay scheduled runs, so a Cloudflare Worker cron is also used when it is deployed. A snapshot older than 90 minutes on a weekday is stale.",
    stale_after_minutes: 90,
    refresh_minutes: 15,
    rows: publicRows,
  };
  return { data, history: dumpHistory(hist), cache };
}

async function loadSeed(env) {
  let history = (env.CHATTER && (await env.CHATTER.get("history.csv"))) || "";
  let cacheRaw = (env.CHATTER && (await env.CHATTER.get("st_volume.json"))) || "";
  if (!history) {
    try {
      const r = await fetch(RAW + "/history.csv?t=" + Date.now(), { headers: { "User-Agent": UA } });
      if (r.ok) history = await r.text();
    } catch (e) {}
  }
  if (!cacheRaw) {
    try {
      const r = await fetch(RAW + "/st_volume.json?t=" + Date.now(), { headers: { "User-Agent": UA } });
      if (r.ok) cacheRaw = await r.text();
    } catch (e) {}
  }
  let cache = {};
  try { cache = cacheRaw ? JSON.parse(cacheRaw) : {}; } catch (e) { cache = {}; }
  return { history, cache };
}

async function collect(env) {
  const seed = await loadSeed(env);
  const { data, history, cache } = await build(seed.history, seed.cache);
  if (env.CHATTER) {
    await env.CHATTER.put("board.json", JSON.stringify(data, null, 1));
    await env.CHATTER.put("history.csv", history);
    await env.CHATTER.put("st_volume.json", JSON.stringify(cache));
  }
  return data;
}

function jsonResponse(obj, status = 200) {
  return new Response(typeof obj === "string" ? obj : JSON.stringify(obj), { status, headers: CORS });
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    const url = new URL(request.url);
    if (url.pathname === "/live/board.json" || url.pathname === "/" || url.pathname === "/board.json") {
      try {
        const fromKv = env.CHATTER && (await env.CHATTER.get("board.json"));
        if (fromKv) return jsonResponse(fromKv);
      } catch (e) {}
      try {
        const r = await fetch(RAW + "/board.json?t=" + Date.now(), { headers: { "User-Agent": UA } });
        if (r.ok) return jsonResponse(await r.text());
      } catch (e) {}
      return jsonResponse({ error: "feed unavailable" }, 502);
    }
    if (url.pathname === "/refresh" && request.method === "POST") {
      // Optional manual kick; only from cron we auto-run. Reject public POST.
      return new Response("Not found", { status: 404 });
    }
    return new Response("Not found", { status: 404 });
  },
  async scheduled(event, env, ctx) {
    ctx.waitUntil(collect(env));
  },
};

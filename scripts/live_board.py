#!/usr/bin/env python3
"""Build a public, scrubbed chatter-vs-normal snapshot.

Uses only public APIs (ApeWisdom, StockTwits, market prices). Writes a JSON
file with tickers, talk counts, x-normal, price moves and NO NEWS flags.
No personal names, no emails, no analyst notes, no copied social posts.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import statistics as st
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zoneinfo import ZoneInfo

E = ZoneInfo("America/New_York")
UA = "PLJALiveScanner/1.0 (+https://plja-corp.pages.dev/live/)"
VERSION = "2026.11.25.2"
ST_VOL_CALLS = 18
ST_FRESH_MIN = 55

# Large names we rotate through for StockTwits volume, same idea as the
# internal scanner, with no private commentary attached.
UNIVERSE = (
    "AAPL MSFT NVDA GOOGL AMZN META TSLA AVGO AMD MU TSM ASML INTC QCOM "
    "DELL HPE ORCL CRM ADBE NOW PLTR NET CRWD ORCL CRWV NBIS IREN "
    "NFLX DIS WMT COST TGT HD LOW NKE JPM BAC GS MS SCHW V MA COIN MSTR "
    "XOM CVX CAT DE BA UNH LLY JNJ GME"
).split()


def now() -> dt.datetime:
    return dt.datetime.now(E)


def get(url: str, t: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/plain, */*"})
    try:
        with urllib.request.urlopen(req, timeout=t) as r:
            return r.read()
    except Exception:
        return b""


def num(x):
    try:
        return int(float(x))
    except Exception:
        return None


def load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_history(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["ts_et", "sym", "reddit", "reddit_prev24", "st_rank", "yahoo", "name"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def fetch_reddit() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for filt in ("all-stocks", "crypto"):
        for page in (1, 2, 3):
            raw = get(f"https://apewisdom.io/api/v1.0/filter/{filt}/page/{page}")
            try:
                data = json.loads(raw)
            except Exception:
                continue
            for a in data.get("results") or []:
                sym = (a.get("ticker") or "").upper()
                if filt == "crypto" and not sym.endswith("-USD") and sym in {"BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "SHIB"}:
                    sym = f"{sym}-USD"
                if not sym:
                    continue
                out[sym] = {
                    "sym": sym,
                    "name": a.get("name") or "",
                    "reddit": int(a.get("mentions") or 0),
                    "reddit_prev24": int(a.get("mentions_24h_ago") or 0),
                    "reddit_rank": a.get("rank"),
                }
            time.sleep(0.15)
    return out


def fetch_trending() -> dict[str, int]:
    raw = get("https://api.stocktwits.com/api/2/trending/symbols.json")
    ranks: dict[str, int] = {}
    try:
        symbols = json.loads(raw).get("symbols") or []
    except Exception:
        return ranks
    for i, s in enumerate(symbols, 1):
        sym = (s.get("symbol") or "").upper()
        if not sym:
            continue
        if s.get("type") == "cryptocurrency" and not sym.endswith("-USD") and "." not in sym:
            # StockTwits uses BTC.X for bitcoin; keep our BTC-USD form when we can.
            if sym.endswith(".X"):
                sym = sym[:-2] + "-USD"
        if sym.endswith(".X"):
            sym = sym[:-2] + "-USD"
        ranks[sym] = i
    return ranks


def st_sym(s: str) -> str:
    return s.replace("-USD", ".X")


def fetch_volume(sym: str):
    raw = get(f"https://api.stocktwits.com/api/2/symbols/{urllib.parse.quote(st_sym(sym))}/volume.json")
    try:
        data = json.loads(raw)["data"]
        return sym, [[x["timestamp"][:10], x["volume_score"]] for x in data if x.get("volume_score") is not None]
    except Exception:
        return sym, None


def st_stats(cache: dict, sym: str):
    d = (cache.get(sym) or {}).get("d")
    if not d or len(d) < 8:
        return None
    d = sorted(d)
    s0 = d[-1][1]
    prior = [x[1] for x in d[:-1]]
    med = st.median(prior[-20:])
    wk = prior[-7] if len(prior) >= 7 else None
    streak = 0
    for i in range(len(d) - 1, 0, -1):
        if d[i][1] > d[i - 1][1]:
            streak += 1
        else:
            break
    return dict(
        s0=s0,
        med=med,
        jump=s0 / max(prior[-1], 3),
        ratio=s0 / max(med, 3),
        wk=(s0 / max(wk, 3)) if wk is not None else None,
        streak=streak,
    )


def price(r: dict) -> dict:
    r["px"] = r["d1"] = r["vol"] = None
    raw = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(r['sym'])}?range=3mo&interval=1d")
    try:
        res = json.loads(raw)["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        off = dt.timedelta(seconds=res["meta"].get("gmtoffset", 0) or 0)
        bars = [
            ((dt.datetime(1970, 1, 1) + dt.timedelta(seconds=t) + off).date(), c, v or 0)
            for t, c, v in zip(res["timestamp"], q["close"], q["volume"])
            if c is not None
        ]
        today_x = (dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) + off).date()
        prior = [b for b in bars if b[0] < today_x] or bars[:-1]
        last = res["meta"].get("regularMarketPrice") or bars[-1][1]
        r["name"] = r["name"] or res["meta"].get("shortName") or ""
        r["px"] = last
        r["d1"] = (last / prior[-1][1] - 1) * 100
        avg = sum(b[2] for b in prior[-60:]) / max(1, len(prior[-60:]))
        tv = bars[-1][2] if (bars[-1][0] == today_x and not r["sym"].endswith("-USD")) else 0
        n = now()
        mins = (n.hour * 60 + n.minute) - 570
        frac = min(1.0, max(0.05, mins / 390)) if 0 < mins else None
        r["vol"] = (tv / avg / frac) if (avg and frac and tv) else None
    except Exception:
        pass
    d1, vol = r["d1"], r["vol"]
    if d1 is None:
        r["kind"] = ""
    elif abs(d1) >= 5 or (vol and vol >= 2.5):
        r["kind"] = "talk and price"
    elif abs(d1) < 2 and (not vol or vol < 1.5):
        r["kind"] = "talk only"
    else:
        r["kind"] = "some of both"
    return r


def news_count(r: dict) -> dict:
    r["n24"] = None
    if r["sym"].endswith("-USD"):
        return r
    raw = get(
        f"https://query1.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(r['sym'])}&newsCount=100&quotesCount=0"
    )
    try:
        items = json.loads(raw).get("news") or []
        ages = [
            (time.time() - x["providerPublishTime"]) / 3600
            for x in items
            if x.get("providerPublishTime")
        ]
        r["n24"] = sum(1 for a in ages if a <= 24) if ages else 0
    except Exception:
        pass
    return r


def build(history_path: Path, cache_path: Path) -> dict:
    n = now()
    reddit = fetch_reddit()
    ranks = fetch_trending()
    ts = n.strftime("%Y-%m-%d %H:%M")

    # Merge names
    names = dict.fromkeys(list(reddit) + list(ranks) + UNIVERSE)
    snap = []
    for sym in names:
        h = reddit.get(sym, {})
        snap.append(
            {
                "ts_et": ts,
                "sym": sym,
                "reddit": h.get("reddit") or 0,
                "reddit_prev24": h.get("reddit_prev24") if h else "",
                "st_rank": ranks.get(sym, ""),
                "yahoo": "",
                "name": h.get("name") or "",
            }
        )

    hist = [r for r in load_history(history_path) if r.get("sym") and r.get("ts_et")]
    # Drop copied social text if a seed file ever had it
    for r in hist:
        r.pop("st_summary", None)
    hist.extend(snap)
    # Keep two weeks
    cutoff = (n - dt.timedelta(days=14)).strftime("%Y-%m-%d %H:%M")
    hist = [r for r in hist if r["ts_et"] >= cutoff]
    save_history(history_path, hist)

    # Snapshots by time
    snaps: dict[str, dict[str, dict]] = {}
    for r in hist:
        snaps.setdefault(r["ts_et"], {})[r["sym"]] = r
    times = sorted(snaps)
    cur_t = times[-1]
    cur = snaps[cur_t]

    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    except Exception:
        cache = {}

    def age_min(sym: str) -> float:
        try:
            return (n - dt.datetime.fromisoformat(cache[sym]["t"])).total_seconds() / 60
        except Exception:
            return 1e9

    cands = sorted(
        [s for s, h in cur.items() if (num(h.get("reddit")) or 0) >= 10 or h.get("st_rank")],
        key=lambda s: -(num(cur[s].get("reddit")) or 0),
    )
    want = [s for s in cands if age_min(s) > ST_FRESH_MIN]
    want += sorted([s for s in UNIVERSE if s not in want and age_min(s) > ST_FRESH_MIN], key=lambda s: -age_min(s))
    with ThreadPoolExecutor(4) as ex:
        for s, d in ex.map(fetch_volume, want[:ST_VOL_CALLS]):
            if d:
                cache[s] = dict(t=n.isoformat(timespec="minutes"), d=d)
            else:
                cache.setdefault(s, {})["t"] = n.isoformat(timespec="minutes")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache), encoding="utf-8")

    rows = []
    for sym in dict.fromkeys(list(cur) + [s for s in cache if s not in cur]):
        h = cur.get(sym, {})
        red = num(h.get("reddit")) or 0
        onst = bool(h.get("st_rank"))
        sv = st_stats(cache, sym)
        st_high = bool(sv and sv["s0"] >= 15 and sv["ratio"] >= 2)
        st_abn = bool(st_high and sv["jump"] >= 1.25)
        st_linger = bool(st_high and not st_abn)
        st_build = bool(sv and sv["s0"] >= 15 and sv["streak"] >= 4 and sv["wk"] is not None and sv["wk"] >= 2 and sv["jump"] >= 1.10)
        if red < 10 and not onst and not st_high and not st_build:
            continue
        prev24 = num(h.get("reddit_prev24"))
        old = []
        days = set()
        for t in times:
            if sym in snaps[t] and (dt.datetime.strptime(cur_t, "%Y-%m-%d %H:%M") - dt.datetime.strptime(t, "%Y-%m-%d %H:%M")) >= dt.timedelta(hours=20):
                v = num(snaps[t][sym].get("reddit"))
                if v is not None:
                    old.append(v)
                days.add(t[:10])
        base = st.median(old) if len(days) >= 3 else None
        x24 = red / max(prev24, 5) if (red and prev24 is not None) else None
        xbase = red / max(base, 5) if (red and base is not None) else None
        prior_seen = [snaps[t].get(sym) for t in times if t < cur_t and snaps[t].get(sym)]
        was_trending = any((h or {}).get("st_rank") for h in prior_seen)
        # Only call it "new" if we already had this name in an earlier snapshot
        # with no rank. Names we have never seen get a weaker "on the list" flag.
        new_st = bool(onst and prior_seen and not was_trending)
        on_st_only = bool(onst and not prior_seen)

        strong, weak = [], []
        if st_abn:
            strong.append(f"StockTwits talk {sv['ratio']:.1f}x its 20-day normal")
        if st_linger:
            weak.append(f"talk still {sv['ratio']:.1f}x normal from earlier, not rising today")
        if st_build:
            strong.append(f"StockTwits building {sv['streak']} days in a row")
        if new_st:
            strong.append("new on StockTwits trending")
        elif on_st_only:
            weak.append("on StockTwits trending")
        r_flags = []
        if red >= 15 and x24 is not None and x24 >= 3:
            r_flags.append(f"Reddit {x24:.1f}x the day before")
        if red >= 10 and prev24 is not None and prev24 <= 2:
            r_flags.append("Reddit: new name")
        if red >= 15 and xbase is not None and xbase >= 3:
            r_flags.append(f"Reddit {xbase:.1f}x its own normal")
        confirmed = bool(sv and sv["ratio"] >= 1.5)
        (strong if (r_flags and (red >= 50 or confirmed)) else weak).extend(r_flags)
        heat = (sv["ratio"] if sv else 0) + (x24 or 0) * 0.3 + (0.6 if onst else 0)
        if strong:
            heat += 100
        elif weak:
            heat += 20
        rows.append(
            dict(
                sym=sym,
                name=h.get("name") or "",
                strong=strong,
                weak=weak,
                reddit=red,
                reddit_prev=prev24,
                x24=round(x24, 1) if x24 is not None else None,
                st_rank=num(h.get("st_rank")),
                st_x_normal=round(sv["ratio"], 1) if sv else None,
                heat=heat,
            )
        )
    rows.sort(key=lambda r: -r["heat"])
    rows = [r for r in rows if r["strong"]][:30] + [r for r in rows if not r["strong"] and r["weak"]][:12]

    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(price, rows))
    head = [r for r in rows if r["strong"]]
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(news_count, head))

    public_rows = []
    for r in rows:
        nonews = bool(r.get("strong") and r.get("n24") is not None and r["n24"] <= 2)
        flags = list(r["strong"] or r["weak"] or [])
        public_rows.append(
            {
                "sym": r["sym"],
                "name": (r.get("name") or "")[:40],
                "group": "abnormal" if r["strong"] else "faint",
                "flags": flags,
                "reddit": r.get("reddit"),
                "reddit_prev": r.get("reddit_prev"),
                "x24": r.get("x24"),
                "st_rank": r.get("st_rank"),
                "st_x_normal": r.get("st_x_normal"),
                "d1": None if r.get("d1") is None else round(r["d1"], 1),
                "vol": None if r.get("vol") is None else round(r["vol"], 1),
                "n24": r.get("n24"),
                "nonews": nonews,
                "kind": r.get("kind") or "",
            }
        )

    updated_et = n.strftime("%A, %b %d, %Y, %I:%M %p ET").replace(" 0", " ")
    return {
        "version": VERSION,
        "updated": n.isoformat(timespec="minutes"),
        "updated_et": updated_et,
        "disclaimer": "Research and education only. Not investment advice.",
        "sources": "Reddit mention counts: ApeWisdom. Trending ranks and talk volume: StockTwits (ranks and scores only; no post text). Prices: Yahoo Finance. News flags use a headline count, not copied articles.",
        "refresh": "A free GitHub Action tries to update this file every 15 minutes on weekdays. Scheduled runs can be delayed by GitHub.",
        "rows": public_rows,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--history", required=True)
    p.add_argument("--cache", required=True)
    args = p.parse_args()
    data = build(Path(args.history), Path(args.cache))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print("wrote", out, "rows", len(data["rows"]), "updated", data["updated_et"])


if __name__ == "__main__":
    main()

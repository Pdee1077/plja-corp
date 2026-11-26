#!/usr/bin/env python3
"""Market Chatter 15-second spoken briefing.

Reusable script generator for the live heat panel (browser speechSynthesis)
and later captioned videos for X posts. No network, no cost: pass in a
board.json dict (or a path / URL via the CLI).

    from chatter_briefing import briefing, tile_line, clean_rows
    print(briefing(board))            # full panel script, ~15 seconds
    print(tile_line(row))             # one name, plus the not-advice line

    python3 chatter_briefing.py [board.json]

Keep this file and chatter-briefing.js in sync: both implement the same
wording. tests at the bottom of a run compare a few fixtures.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
STALE_MIN = 90
DISCLAIMER = "Research and education only, not investment advice."
MIN_X = 2
MAX_NAMES = 3

ONES = (
    "zero one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen"
).split()
TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()


def words(n: int) -> str:
    n = int(n)
    if n < 0:
        return "minus " + words(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return TENS[t - 2] + (f"-{ONES[o]}" if o else "")
    if n < 1000:
        h, r = divmod(n, 100)
        return ONES[h] + " hundred" + (f" {words(r)}" if r else "")
    return str(n)


def say_times(x: float) -> str:
    """'eight times', 'about thirty-five times', or 'seven point six times'."""
    if x is None:
        return "more than its usual"
    nearest = int(round(x))
    gap = abs(x - nearest)
    if gap < 0.2:
        return f"{words(nearest)} times"
    if gap <= 0.35 and nearest >= 10:
        return f"about {words(nearest)} times"
    whole = int(x)
    frac = int(round((x - whole) * 10))
    if frac == 10:
        whole += 1
        frac = 0
    if frac == 0:
        return f"{words(whole)} times"
    return f"{words(whole)} point {words(frac)} times"


def spoken_name(row: dict[str, Any], *, short: bool = False) -> str:
    name = re.sub(r"&amp;", "&", str(row.get("name") or "")).strip()
    sym = str(row.get("sym") or "").strip()
    if short and name and len(name.split()) >= 3:
        return " ".join(name.split()[:2])
    if name and len(name) <= 28 and "-" not in name:
        return name
    if name:
        parts = [p for p in re.split(r"[,\-/]", name)[0].split() if p]
        cut = " ".join(parts[:2])
        if cut and len(cut) <= 28:
            return cut
    if re.fullmatch(r"[A-Z]{1,5}", sym):
        return " ".join(sym)
    return sym or "This name"


def say_why(row: dict[str, Any], *, headlines: bool = True) -> str:
    flags = " | ".join(row.get("flags") or [])
    m = re.search(r"building (\d+) days in a row", flags)
    if m:
        n = int(m.group(1))
        return f"building {words(n)} days in a row"
    m = re.search(r"Reddit ([\d.]+)x the day before", flags)
    if m:
        return f"Reddit talk is {say_times(float(m.group(1)))} the day before"
    n = row.get("n24") or 0
    if headlines and n:
        return f"with {words(n)} headline{'s' if n != 1 else ''} in the last day"
    return ""


def tile_sentence(row: dict[str, Any], *, headlines: bool = True, short: bool = False, compact: bool = False) -> str:
    name = spoken_name(row, short=short)
    times = say_times(row.get("st_x_normal"))
    why = say_why(row, headlines=headlines)
    if compact:
        line = f"{name} is at {times} usual"
        if why:
            # trim "building N days in a row" stays; drop "in a row" already in why
            line += f", {why}"
    else:
        line = f"{name} chatter is running {times} its usual level"
        if why:
            line += f", {why}"
    return line + "."


def tile_line(row: dict[str, Any]) -> str:
    """One-name script, including the not-advice line."""
    return f"{tile_sentence(row)} {DISCLAIMER}"


def is_clean(row: dict[str, Any], min_x: float = MIN_X) -> bool:
    x = row.get("st_x_normal")
    if row.get("group") != "abnormal" or x is None or x < min_x:
        return False
    if "-" in str(row.get("sym") or ""):
        return False
    blob = f"{row.get('name') or ''} {row.get('sym') or ''}"
    if re.search(r"airpods|find my", blob, re.I):
        return False
    if re.search(r"\bIPO\b", " ".join(row.get("flags") or []) + " " + str(row.get("name") or "")):
        return False
    return True


def clean_rows(board: dict[str, Any], n: int = MAX_NAMES, min_x: float = MIN_X) -> list[dict[str, Any]]:
    rows = [r for r in (board.get("rows") or []) if is_clean(r, min_x)]
    rows.sort(key=lambda r: -(r.get("st_x_normal") or 0))
    return rows[:n]


def snapshot_age_ms(board: dict[str, Any], now: datetime | None = None) -> int | None:
    raw = board.get("updated")
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(str(raw))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ET)
    now = now or datetime.now(timezone.utc)
    return int((now - dt.astimezone(timezone.utc)).total_seconds() * 1000)


def say_age(ms: int) -> str:
    m = max(0, round(ms / 60000))
    if m < 60:
        return f"{words(m)} minute" + ("s" if m != 1 else "")
    h = max(1, round(m / 60))
    if h < 48:
        return f"{words(h)} hour" + ("s" if h != 1 else "")
    d = max(1, round(h / 24))
    return f"{words(d)} day" + ("s" if d != 1 else "")


def briefing(
    board: dict[str, Any],
    *,
    now: datetime | None = None,
    stale_min: int = STALE_MIN,
    max_names: int = MAX_NAMES,
) -> str:
    """~15-second panel briefing, ending with the not-advice line.

    If the snapshot is older than stale_min minutes, the script says how old it is.
    """
    rows = clean_rows(board, n=max_names)
    if not rows:
        return f"Market Chatter has no unusually loud names in this snapshot. {DISCLAIMER}"
    parts = ["Market Chatter."]
    for i, row in enumerate(rows):
        # Keep the briefing near 15 seconds: full sentence on the top name, compact after.
        parts.append(tile_sentence(row, headlines=(i == 0), short=(i > 0), compact=(i > 0)))
    age_ms = snapshot_age_ms(board, now=now)
    if age_ms is not None and age_ms > stale_min * 60 * 1000:
        parts.append(f"This snapshot is about {say_age(age_ms)} old.")
    parts.append(DISCLAIMER)
    return " ".join(parts)


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", text))


def eta_seconds(text: str, wpm: int = 150) -> float:
    return round(word_count(text) * 60 / wpm, 1)


# --- JS twin, kept here so a video pipeline and the panel stay in sync. ---

JS_SOURCE = r"""
/* chatter-briefing.js — 15-second Market Chatter spoken script.
   Browser and Node. No network, no cost. Keep in sync with chatter_briefing.py.

     const { briefing, tileLine, cleanRows } = require('./chatter-briefing.js');
     // or window.ChatterBriefing in a browser script tag
*/
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.ChatterBriefing = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  var STALE_MIN = 90, DISCLAIMER = 'Research and education only, not investment advice.';
  var MIN_X = 2, MAX_NAMES = 3;
  var ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split(' ');
  var TENS = 'twenty thirty forty fifty sixty seventy eighty ninety'.split(' ');

  function words(n) {
    n = Math.round(Number(n));
    if (n < 0) return 'minus ' + words(-n);
    if (n < 20) return ONES[n];
    if (n < 100) { var t = Math.floor(n / 10), o = n % 10; return TENS[t - 2] + (o ? '-' + ONES[o] : ''); }
    if (n < 1000) { var h = Math.floor(n / 100), r = n % 100; return ONES[h] + ' hundred' + (r ? ' ' + words(r) : ''); }
    return String(n);
  }
  function sayTimes(x) {
    if (x == null || isNaN(x)) return 'more than its usual';
    var nearest = Math.round(x), gap = Math.abs(x - nearest);
    if (gap < 0.2) return words(nearest) + ' times';
    if (gap <= 0.35 && nearest >= 10) return 'about ' + words(nearest) + ' times';
    var whole = Math.floor(x), frac = Math.round((x - whole) * 10);
    if (frac === 10) { whole += 1; frac = 0; }
    if (frac === 0) return words(whole) + ' times';
    return words(whole) + ' point ' + words(frac) + ' times';
  }
  function spokenName(row, short) {
    var name = String((row && row.name) || '').replace(/&amp;/g, '&').trim();
    var sym = String((row && row.sym) || '').trim();
    if (short && name && name.split(/\s+/).length >= 3) return name.split(/\s+/).slice(0, 2).join(' ');
    if (name && name.length <= 28 && name.indexOf('-') < 0) return name;
    if (name) {
      var cut = name.split(/[,\-\/]/)[0].split(/\s+/).filter(Boolean).slice(0, 2).join(' ');
      if (cut && cut.length <= 28) return cut;
    }
    if (/^[A-Z]{1,5}$/.test(sym)) return sym.split('').join(' ');
    return sym || 'This name';
  }
  function sayWhy(row, headlines) {
    var flags = (row.flags || []).join(' | '), m;
    if (m = flags.match(/building (\d+) days in a row/)) return 'building ' + words(+m[1]) + ' days in a row';
    if (m = flags.match(/Reddit ([\d.]+)x the day before/)) return 'Reddit talk is ' + sayTimes(parseFloat(m[1])) + ' the day before';
    var n = row.n24 || 0;
    if (headlines && n) return 'with ' + words(n) + ' headline' + (n === 1 ? '' : 's') + ' in the last day';
    return '';
  }
  function tileSentence(row, headlines, short, compact) {
    if (headlines == null) headlines = true;
    var times = sayTimes(row.st_x_normal), why = sayWhy(row, headlines), line;
    if (compact) {
      line = spokenName(row, true) + ' is at ' + times + ' usual';
      if (why) line += ', ' + why;
    } else {
      line = spokenName(row, short) + ' chatter is running ' + times + ' its usual level';
      if (why) line += ', ' + why;
    }
    return line + '.';
  }
  function tileLine(row) { return tileSentence(row, true) + ' ' + DISCLAIMER; }
  function isClean(row, minX) {
    minX = minX == null ? MIN_X : minX;
    var x = row && row.st_x_normal;
    if (!row || row.group !== 'abnormal' || x == null || x < minX) return false;
    if (/-/.test(row.sym || '')) return false;
    if (/airpods|find my/i.test((row.name || '') + ' ' + (row.sym || ''))) return false;
    if (/\bIPO\b/i.test((row.flags || []).join(' ') + ' ' + (row.name || ''))) return false;
    return true;
  }
  function cleanRows(board, n, minX) {
    n = n == null ? MAX_NAMES : n;
    var rows = ((board && board.rows) || []).filter(function (r) { return isClean(r, minX); });
    rows.sort(function (a, b) { return (b.st_x_normal || 0) - (a.st_x_normal || 0); });
    return rows.slice(0, n);
  }
  function snapshotAgeMs(board, now) {
    if (!board || !board.updated) return null;
    var t = Date.parse(board.updated);
    if (isNaN(t)) return null;
    return (now != null ? +now : Date.now()) - t;
  }
  function sayAge(ms) {
    var m = Math.max(0, Math.round(ms / 60000));
    if (m < 60) return words(m) + ' minute' + (m === 1 ? '' : 's');
    var h = Math.max(1, Math.round(m / 60));
    if (h < 48) return words(h) + ' hour' + (h === 1 ? '' : 's');
    var d = Math.max(1, Math.round(h / 24));
    return words(d) + ' day' + (d === 1 ? '' : 's');
  }
  function briefing(board, opts) {
    opts = opts || {};
    var staleMin = opts.staleMin == null ? STALE_MIN : opts.staleMin;
    var rows = cleanRows(board, opts.maxNames);
    if (!rows.length) return 'Market Chatter has no unusually loud names in this snapshot. ' + DISCLAIMER;
    var parts = ['Market Chatter.'];
    rows.forEach(function (row, i) { parts.push(tileSentence(row, i === 0, i > 0, i > 0)); });
    var age = snapshotAgeMs(board, opts.now);
    if (age != null && age > staleMin * 60 * 1000) parts.push('This snapshot is about ' + sayAge(age) + ' old.');
    parts.push(DISCLAIMER);
    return parts.join(' ');
  }
  function wordCount(text) { return (String(text).match(/[A-Za-z0-9]+(?:'[A-Za-z]+)?/g) || []).length; }
  function etaSeconds(text, wpm) { return Math.round(wordCount(text) * 60 / (wpm || 150) * 10) / 10; }

  return {
    STALE_MIN: STALE_MIN, DISCLAIMER: DISCLAIMER,
    words: words, sayTimes: sayTimes, spokenName: spokenName, sayWhy: sayWhy,
    tileSentence: tileSentence, tileLine: tileLine,
    isClean: isClean, cleanRows: cleanRows,
    snapshotAgeMs: snapshotAgeMs, sayAge: sayAge,
    briefing: briefing, wordCount: wordCount, etaSeconds: etaSeconds
  };
}));
"""


def write_js(path: Path | None = None) -> Path:
    dest = Path(path) if path else Path(__file__).with_name("chatter-briefing.js")
    dest.write_text(JS_SOURCE.lstrip() + "\n", encoding="utf-8")
    return dest


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--write-js" in argv:
        argv.remove("--write-js")
        dest = Path(argv[0]) if argv else None
        out = write_js(dest)
        print("wrote", out)
        return 0
    src = Path(argv[0]) if argv else Path(__file__).with_name("board.json")
    if not src.exists():
        sys.stderr.write(f"no board file at {src}\n")
        return 1
    board = json.loads(src.read_text(encoding="utf-8"))
    text = briefing(board)
    print(text)
    print(f"({word_count(text)} words, ~{eta_seconds(text)}s at 150 wpm)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

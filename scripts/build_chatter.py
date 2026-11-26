#!/usr/bin/env python3
"""Build Market Chatter, the one room that holds the Daily Scan and the Live board.

/chatter/ shows the newest scan summary on top and the live board right under it.
/daily/ and /live/ keep working as before (archive and full-page board).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme  # noqa: E402
import mcp_panel  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
UTM = "utm_source=plja_chatter"
OG_PATH = "/assets/img/chatter-og.png"
TITLE = "Market Chatter — PLJA Corp"
DESC = (
    "Today's market scan and a live, sortable board of names being talked about far more than usual. "
    "Free research and education, not investment advice."
)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def write_og() -> None:
    w, h = 1200, 630
    bg, ink, mute, accent = (245, 240, 231), (27, 24, 20), (106, 99, 90), (169, 82, 44)
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    base = Path("/usr/share/fonts/truetype/sand-box/google")
    fra = base / "Fraunces/Fraunces-VariableFont_SOFT,WONK,opsz,wght.ttf"
    plex = base / "IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf"
    mono = base / "IBM Plex Mono/IBMPlexMono-Medium.ttf"
    fb = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    f = lambda p, s: ImageFont.truetype(str(p if p.exists() else fb), s)  # noqa: E731
    d.rectangle([0, 0, w, 10], fill=accent)
    d.text((80, 70), "PLJA CORP · MARKET CHATTER", font=f(plex, 24), fill=accent)
    d.text((80, 130), "Who is suddenly being", font=f(fra, 84), fill=ink)
    d.text((80, 225), "talked about.", font=f(fra, 84), fill=ink)
    d.text((80, 350), "Today's scan and a live board, in one place.", font=f(plex, 34), fill=mute)
    for i, (frac, label) in enumerate([(0.9, "35×"), (0.55, "7.6×"), (0.4, "5.8×")]):
        y = 430 + i * 38
        d.rounded_rectangle([80, y, 80 + 700, y + 20], radius=10, fill=(232, 224, 211))
        d.rounded_rectangle([80, y, 80 + int(700 * frac), y + 20], radius=10, fill=accent)
        d.text((810, y - 8), label, font=f(mono, 30), fill=ink)
    d.text((80, 570), "Research and education only. Not investment advice.", font=f(plex, 24), fill=mute)
    out = PUBLIC / OG_PATH.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)


def main() -> None:
    daily = _load("build_daily")
    live = _load("build_live")
    day = daily.DAYS[0]
    I = theme.ICONS
    import json, subprocess
    try:
        board_json = json.loads(subprocess.check_output(["git", "show", "origin/live-data:board.json"], cwd=ROOT, stderr=subprocess.DEVNULL))
    except Exception:
        board_json = json.loads((PUBLIC / "live" / "board.json").read_text(encoding="utf-8"))
    names_panel = mcp_panel.panel_html(board_json, "#live")
    summary = f"""
    <section class="day-hero chatter-top">
      <div class="wrap">
        <p class="crumb"><a href="/">PLJA Corp</a> › Market Chatter</p>
        {names_panel}
        <p class="kicker">Market Chatter · @PLJA_AI</p>
        <h1>Today's scan, and who is being talked about.</h1>
        <p class="lede">One free page for market chatter. The morning scan is first, and the live board is right underneath. Research and education, never advice.</p>
        <nav class="jumps no-print" aria-label="On this page">
          <a class="chip" href="#scan">{I["sunrise"]} Today's scan</a>
          <a class="chip" href="#live">{I["pulse"]} Live board</a>
          <a class="chip" href="/daily/">Scan archive</a>
        </nav>
        <div class="surface summary" id="scan">
          <h2>Today's scan · {day["label"]}</h2>
          <p class="days"><a href="/daily/{day["date"]}/"><span class="h">{day["headline"]}</span></a></p>
          <div class="dtiles">{daily.tiles_html(day)}</div>
          {daily.frag(day["date"], "short")}
          <div class="actions">
            <a class="btn btn-primary" href="/daily/{day["date"]}/">Read the full scan <span class="arr" aria-hidden="true">→</span></a>
            <a class="btn btn-ghost" href="/daily/">Scan archive</a>
          </div>
          {daily.DISCLAIMER}
        </div>
      </div>
    </section>
"""
    board = live.body(embedded=True)
    css_extra = ".chatter-top { padding-bottom: 0; }\n.jumps { display: flex; flex-wrap: wrap; gap: .45rem; margin: 1rem 0 0; }\n.chatter-top + .live-hero { padding-top: clamp(2rem, 5vw, 3.5rem); }\n#scan, #live { scroll-margin-top: 5rem; }\n"
    css_href = theme.write_page_css(PUBLIC, "chatter", css_extra)
    head = (
        f'\n  <link rel="stylesheet" href="{theme.write_page_css(PUBLIC, "daily", daily.CSS)}">'
        f'\n  <link rel="stylesheet" href="{theme.write_page_css(PUBLIC, "live", live.CSS)}">'
        f'\n  <link rel="stylesheet" href="{css_href}">'
        '\n  <link rel="preconnect" href="https://raw.githubusercontent.com" crossorigin>'
    )
    write_og()
    dest = PUBLIC / "chatter" / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        theme.page(
            title=TITLE,
            description=DESC,
            path="/chatter/",
            body=summary + board,
            og_image=OG_PATH,
            robots="index,follow",
            draft_banner=False,
            footer_blurb="Market Chatter is one room in PLJA Corp: a free scan and live board of public chatter, and a link back to the Analog Arcade shop.",
            footer_note="Research and education only. Not investment advice.",
            after_main=theme.arcade_section(UTM, "Market Chatter"),
            scripts=live.JS,
            utm=UTM,
            extra_head=head,
            preload_mono=True,
        ),
        encoding="utf-8",
    )
    print("wrote", dest, dest.stat().st_size)


if __name__ == "__main__":
    main()

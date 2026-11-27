#!/usr/bin/env python3
"""Shared PLJA Corp design system: tokens, components, page shell.

Every page builder (build_site, build_daily, build_live) renders through
`page()` so the header, footer, version stamp and theme stay identical.
No frameworks, no third-party scripts, no paid fonts.
"""
from __future__ import annotations
from pathlib import Path

from datetime import datetime
from zoneinfo import ZoneInfo

SITE = "https://plja-corp.pages.dev"
ET = ZoneInfo("America/New_York")
# One site-wide version. Bump on every design or content release.
VERSION = "2026.11.26.3"
# CSS and JS file names carry the version because /assets/* is cached for a year.
CSS_HREF = f"/assets/css/plja-{VERSION}.css"
YEAR = "2026"


def published_et(now: datetime | None = None) -> str:
    now = (now or datetime.now(ET)).astimezone(ET)
    hour = now.strftime("%I").lstrip("0") or "12"
    return f"{now.strftime('%a')}, {now.strftime('%b')} {now.day}, {now.year}, {hour}:{now.strftime('%M %p')} ET"


PUBLISHED = published_et()

NAV = [
    ("/chatter/", 'Market Chatter <span class="live-word">— live</span>'),
    ("/products/", "Apps"),
    ("/about/", "About"),
    ("/support/", "Support"),
]
# Pages that live inside a nav section but have their own URL.
SECTION_OF = {"/daily/": "/chatter/", "/live/": "/chatter/"}

TIPOFF_CHATTER = "https://tipoff.analogarcade.net/chatter"

def tipoff_home_banner() -> str:
    """A clear, no-redirect pointer to Tipoff, where Market Chatter now lives."""
    return (
        '<div class="callout tipoff-home" role="note">'
        "<p><strong>Market Chatter now lives at "
        f'<a href="{TIPOFF_CHATTER}">tipoff.analogarcade.net/chatter</a>.</strong> '
        "That’s the full board, with filters, on Tipoff. This page stays here as the source board. "
        "We’re not redirecting yet.</p>"
        "</div>\n"
    )


JUMP = [
    ("Home", "/", "Start here"),
    ("Market Chatter", "/chatter/", "What the internet is talking about vs. normal"),
    ("Apps", "/products/", "House Binder, House Radar, Local Mass Finder, Keysong, Card Check"),
    ("Daily Scan (archive)", "/daily/", "Morning research log"),
    ("Latest scan: Nov 25, 2026", "/daily/2026-11-25/", "Daily Scan"),
    ("Live board", "/live/", "Chatter vs. normal, refreshed on weekdays"),
    ("About", "/about/", "Who makes these"),
    ("Contact", "/contact/", "How to reach us"),
    ("Support", "/support/", "Help for each app"),
    ("Privacy", "/privacy/", "What this site collects (nothing extra)"),
    ("House Binder", "https://binder.analogarcade.net/", "Web app"),
    ("House Radar", "https://apps.apple.com/us/app/house-radar/id6816271323", "App Store"),
    ("Local Mass Finder", "https://church.analogarcade.net/", "Web app"),
    ("Keysong", "https://apps.apple.com/us/app/keysong/id6804326066", "App Store"),
    ("Card Check", "https://cards.analogarcade.net/", "Web app"),
    ("Analog Arcade", "https://analogarcade.net/", "The PLJA Corp studio's public shop"),
]

CSS = r"""/* PLJA Corp design system. Ink, paper, copper. Light + dark. */
@font-face { font-family: "Fraunces"; src: url("/assets/fonts/fraunces-semibold.woff2") format("woff2"); font-weight: 600; font-display: swap; }
@font-face { font-family: "IBM Plex Sans"; src: url("/assets/fonts/ibm-plex-sans-regular.woff2") format("woff2"); font-weight: 400; font-display: swap; }
@font-face { font-family: "IBM Plex Sans"; src: url("/assets/fonts/ibm-plex-sans-medium.woff2") format("woff2"); font-weight: 500 700; font-display: swap; }
@font-face { font-family: "IBM Plex Mono"; src: url("/assets/fonts/ibm-plex-mono-medium.woff2") format("woff2"); font-weight: 500; font-display: swap; }

@view-transition { navigation: auto; }

:root {
  color-scheme: light;
  --bg: #f5f0e7; --bg-2: #ede6d9; --surface: #fffdf9; --surface-2: #faf6ef;
  --ink: #1b1814; --ink-2: #4f4942; --mute: #6a635a; --line: #ddd4c6; --line-2: #e9e2d6;
  --accent: #a9522c; --accent-ink: #8a3b20; --accent-soft: #f6e4d9;
  --good: #2c6a45; --good-soft: #e3f0e7; --bad: #a33a2a; --bad-soft: #f8e3df; --warn: #8a6100; --warn-soft: #fbf0d4;
  --focus: #c46a3d;
  --shadow-1: 0 1px 2px rgb(27 24 20 / .06);
  --shadow-2: 0 1px 2px rgb(27 24 20 / .05), 0 12px 32px -12px rgb(27 24 20 / .14);
  --glow: radial-gradient(60rem 30rem at 85% -10%, rgb(169 82 44 / .14), transparent 60%), radial-gradient(40rem 26rem at -10% 10%, rgb(44 106 69 / .08), transparent 60%);
  --sans: "IBM Plex Sans", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  --serif: "Fraunces", "Iowan Old Style", Palatino, Georgia, serif;
  --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  /* Type scale: 1.2 minor third, fluid between 360px and 1280px. */
  --s--1: clamp(.83rem, .8rem + .1vw, .9rem);
  --s-0: clamp(1rem, .96rem + .2vw, 1.0625rem);
  --s-1: clamp(1.15rem, 1.08rem + .35vw, 1.3rem);
  --s-2: clamp(1.35rem, 1.2rem + .7vw, 1.7rem);
  --s-3: clamp(1.6rem, 1.35rem + 1.2vw, 2.3rem);
  --s-4: clamp(2rem, 1.5rem + 2.3vw, 3.3rem);
  --s-5: clamp(2.4rem, 1.6rem + 3.8vw, 4.6rem);
  --space: clamp(1rem, .8rem + 1vw, 1.5rem);
  --pad: clamp(1.1rem, 4vw, 2rem);
  --max: 72rem; --text: 40rem;
  --r-1: .55rem; --r-2: .9rem; --r-3: 1.35rem;
  --ease: cubic-bezier(.2,.7,.2,1);
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #12110f; --bg-2: #1a1815; --surface: #1d1b18; --surface-2: #232019;
  --ink: #f1ebe1; --ink-2: #cbc3b6; --mute: #a49b8e; --line: #34302a; --line-2: #2a2722;
  --accent: #e3895a; --accent-ink: #f0a47a; --accent-soft: #3a261b;
  --good: #7fcf9b; --good-soft: #17301f; --bad: #ff8f7d; --bad-soft: #3a1c17; --warn: #f2c86a; --warn-soft: #33290f;
  --focus: #f0a47a;
  --shadow-1: 0 1px 2px rgb(0 0 0 / .4);
  --shadow-2: 0 1px 2px rgb(0 0 0 / .4), 0 18px 40px -18px rgb(0 0 0 / .7);
  --glow: radial-gradient(60rem 30rem at 85% -10%, rgb(227 137 90 / .16), transparent 60%), radial-gradient(40rem 26rem at -10% 10%, rgb(127 207 155 / .07), transparent 60%);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #12110f; --bg-2: #1a1815; --surface: #1d1b18; --surface-2: #232019;
    --ink: #f1ebe1; --ink-2: #cbc3b6; --mute: #a49b8e; --line: #34302a; --line-2: #2a2722;
    --accent: #e3895a; --accent-ink: #f0a47a; --accent-soft: #3a261b;
    --good: #7fcf9b; --good-soft: #17301f; --bad: #ff8f7d; --bad-soft: #3a1c17; --warn: #f2c86a; --warn-soft: #33290f;
    --focus: #f0a47a;
    --shadow-1: 0 1px 2px rgb(0 0 0 / .4);
    --shadow-2: 0 1px 2px rgb(0 0 0 / .4), 0 18px 40px -18px rgb(0 0 0 / .7);
    --glow: radial-gradient(60rem 30rem at 85% -10%, rgb(227 137 90 / .16), transparent 60%), radial-gradient(40rem 26rem at -10% 10%, rgb(127 207 155 / .07), transparent 60%);
  }
}

*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-padding-top: 5rem; }
html, body { margin: 0; }
body {
  background: var(--bg); color: var(--ink); font: 400 var(--s-0)/1.62 var(--sans);
  font-feature-settings: "kern", "liga"; -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
  min-height: 100vh; display: flex; flex-direction: column;
}
main { flex: 1; }
img, svg { max-width: 100%; height: auto; display: block; }
a { color: var(--accent-ink); text-decoration-thickness: .08em; text-underline-offset: .18em; }
a:hover { color: var(--ink); }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 3px; border-radius: 4px; }
::selection { background: var(--accent-soft); color: var(--ink); }
h1, h2, h3 { line-height: 1.15; letter-spacing: -.01em; margin: 0 0 .6em; text-wrap: balance; }
h1 { font: 600 var(--s-4)/1.08 var(--serif); letter-spacing: -.02em; }
h2 { font: 600 var(--s-3)/1.15 var(--serif); }
h3 { font-size: var(--s-1); font-weight: 500; }
p { margin: 0 0 1em; text-wrap: pretty; }
.num, td.r, .tile .v, .mono { font-variant-numeric: tabular-nums; }
.mono { font-family: var(--mono); font-weight: 500; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

.wrap { width: min(var(--max), 100% - 2 * var(--pad)); margin-inline: auto; }
.narrow { width: min(var(--text), 100% - 2 * var(--pad)); margin-inline: auto; }

.skip { position: absolute; left: 1rem; top: -4rem; background: var(--ink); color: var(--bg); padding: .6rem .9rem; z-index: 50; border-radius: var(--r-1); }
.skip:focus { top: .75rem; color: var(--bg); }

.draft { background: var(--ink); color: var(--bg); font-size: var(--s--1); text-align: center; padding: .45rem var(--pad); }
.draft strong { font-weight: 500; }

/* Header */
.site-header { position: sticky; top: 0; z-index: 30; background: color-mix(in srgb, var(--bg) 82%, transparent); backdrop-filter: saturate(1.4) blur(14px); -webkit-backdrop-filter: saturate(1.4) blur(14px); border-bottom: 1px solid color-mix(in srgb, var(--line) 70%, transparent); }
.bar { display: flex; align-items: center; gap: .75rem; min-height: 3.75rem; }
.brand { display: inline-flex; align-items: center; gap: .6rem; color: var(--ink); text-decoration: none; font-weight: 500; letter-spacing: .08em; font-size: .95rem; margin-right: auto; }
.brand img { width: 2rem; height: 2rem; border-radius: .45rem; }
.brand .name { display: flex; flex-direction: column; line-height: 1.02; }
.brand .corp { font-size: .62rem; letter-spacing: .26em; color: var(--mute); }
.nav { display: none; gap: .15rem; }
.nav a { color: var(--ink-2); text-decoration: none; padding: .5rem .8rem; border-radius: 999px; font-size: .94rem; min-height: 40px; display: inline-flex; align-items: center; transition: background .2s var(--ease), color .2s; }
.nav a:hover { background: var(--bg-2); color: var(--ink); }
.nav a[aria-current="page"] { background: var(--surface); color: var(--ink); box-shadow: var(--shadow-1), inset 0 0 0 1px var(--line); font-weight: 500; }
.nav a.live-dot::before { content: ""; width: .45rem; height: .45rem; border-radius: 50%; background: var(--good); margin-right: .45rem; box-shadow: 0 0 0 0 var(--good); animation: pulse 2.4s infinite; flex: none; }
.nav a.live-word { font-weight: 500; color: var(--good); letter-spacing: .02em; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--good) 60%, transparent); } 70% { box-shadow: 0 0 0 .45rem transparent; } 100% { box-shadow: 0 0 0 0 transparent; } }
.chatter-rail { background: var(--accent-soft); border-bottom: 1px solid color-mix(in srgb, var(--accent) 22%, var(--line)); }
.chatter-rail a { display: flex; flex-wrap: wrap; align-items: center; gap: .35rem 1rem; text-decoration: none; color: var(--ink); padding: .65rem 0; min-height: 44px; }
.chatter-rail .ttl { font-weight: 500; display: inline-flex; align-items: center; gap: .45rem; white-space: nowrap; }
.chatter-rail .ttl::before { content: ""; width: .45rem; height: .45rem; border-radius: 50%; background: var(--good); box-shadow: 0 0 0 0 var(--good); animation: pulse 2.4s infinite; flex: none; }
.chatter-rail .top { font: 500 .95rem var(--mono); color: var(--accent-ink); }
.chatter-rail .why { color: var(--ink-2); font-size: .93rem; flex: 1 1 14rem; }
.chatter-rail .go { margin-left: auto; font-weight: 500; color: var(--accent-ink); white-space: nowrap; }
.chatter-rail a:hover { color: var(--ink); }
.chatter-rail a:hover .go { color: var(--ink); }
@media (max-width: 640px) {
  .chatter-rail .why { display: none; }
}
.tool { appearance: none; border: 1px solid var(--line); background: var(--surface); color: var(--ink); border-radius: 999px; min-height: 40px; min-width: 40px; padding: 0 .7rem; display: inline-flex; align-items: center; justify-content: center; gap: .4rem; font: inherit; font-size: .88rem; cursor: pointer; transition: border-color .2s, transform .2s var(--ease); }
.tool:hover { border-color: var(--ink-2); }
.tool:active { transform: scale(.96); }
.tool svg { width: 1.05rem; height: 1.05rem; }
.tool kbd { font: 500 .72rem var(--mono); color: var(--mute); border: 1px solid var(--line); border-radius: .3rem; padding: 0 .3rem; }
.jump-btn .lbl, .jump-btn kbd { display: none; }
.menu { position: relative; }
.menu summary { list-style: none; }
.menu summary::-webkit-details-marker { display: none; }
.menu .panel { position: absolute; right: 0; top: calc(100% + .5rem); background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-2); box-shadow: var(--shadow-2); padding: .4rem; min-width: 14rem; display: grid; animation: pop .18s var(--ease); }
.menu .panel a { color: var(--ink); text-decoration: none; padding: .7rem .8rem; border-radius: var(--r-1); min-height: 44px; }
.menu .panel a:hover, .menu .panel a[aria-current="page"] { background: var(--bg-2); }
@keyframes pop { from { opacity: 0; transform: translateY(-4px) scale(.98); } to { opacity: 1; transform: none; } }
@media (min-width: 900px) {
  .nav { display: flex; }
  .menu { display: none; }
  .jump-btn .lbl, .jump-btn kbd { display: inline; }
}

/* Buttons, chips, kickers */
.crumb { font-size: .86rem; color: var(--mute); margin: 0 0 .8rem; }
.crumb a { color: var(--ink-2); }
.kicker { display: inline-flex; align-items: center; gap: .5rem; font-size: .74rem; font-weight: 500; letter-spacing: .16em; text-transform: uppercase; color: var(--accent-ink); margin: 0 0 .9rem; }
.kicker::before { content: ""; width: 1.4rem; height: 2px; background: currentColor; border-radius: 2px; }
.lede { font-size: var(--s-1); color: var(--ink-2); max-width: 40rem; }
.lede strong { color: var(--ink); font-weight: 500; }
.actions { display: flex; flex-wrap: wrap; gap: .6rem; margin: 1.4rem 0 0; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: .5rem; min-height: 46px; padding: .7rem 1.15rem; border-radius: 999px; font: 500 .97rem var(--sans); text-decoration: none; border: 1px solid transparent; cursor: pointer; transition: transform .18s var(--ease), background .2s, border-color .2s, color .2s, box-shadow .2s; }
.btn:active { transform: translateY(1px) scale(.985); }
.btn-primary { background: var(--ink); color: var(--bg); box-shadow: var(--shadow-1); }
.btn-primary:hover { background: var(--accent-ink); color: #fff; }
.btn-ghost { background: var(--surface); color: var(--ink); border-color: var(--line); }
.btn-ghost:hover { border-color: var(--ink-2); color: var(--ink); }
.btn .arr { transition: transform .2s var(--ease); }
.btn:hover .arr { transform: translateX(3px); }
.chip { appearance: none; font: 500 .86rem var(--sans); border: 1px solid var(--line); background: var(--surface); color: var(--ink-2); border-radius: 999px; padding: .4rem .8rem; min-height: 38px; cursor: pointer; display: inline-flex; align-items: center; gap: .4rem; transition: all .18s var(--ease); }
.chip:hover { border-color: var(--ink-2); color: var(--ink); }
.chip[aria-pressed="true"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.chip .ct { font-family: var(--mono); font-size: .75rem; opacity: .75; }
.chip svg { width: 1rem; height: 1rem; flex: none; }
a.chip { text-decoration: none; }
.chip[hidden] { display: none; }
.pill { display: inline-flex; align-items: center; font-size: .75rem; font-weight: 500; padding: .18rem .55rem; border-radius: 999px; background: var(--bg-2); color: var(--ink-2); border: 1px solid var(--line-2); white-space: nowrap; }
.pill-free { background: var(--good-soft); color: var(--good); border-color: transparent; }
.pill-paid { background: var(--accent-soft); color: var(--accent-ink); border-color: transparent; }
.badge { display: inline-flex; font: 500 .7rem/1 var(--sans); letter-spacing: .06em; text-transform: uppercase; padding: .3rem .45rem; border-radius: .35rem; background: var(--warn-soft); color: var(--warn); white-space: nowrap; }
.badge.new { background: var(--accent-soft); color: var(--accent-ink); }

/* Sections, cards */
.section { padding: clamp(2rem, 5vw, 4rem) 0; }
.section.tight-top { padding-top: 0; }
.section-head { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: .6rem 1.5rem; margin-bottom: 1.4rem; }
.section-head h2 { margin: 0; }
.section-head p { margin: 0; color: var(--mute); }
.surface { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-3); box-shadow: var(--shadow-2); }
.grid { display: grid; gap: var(--space); }
@media (min-width: 680px) { .grid.products { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1040px) { .grid.products { grid-template-columns: repeat(3, 1fr); } }
.card { position: relative; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-3); padding: 1.3rem; display: flex; flex-direction: column; gap: .8rem; box-shadow: var(--shadow-1); transition: transform .25s var(--ease), box-shadow .25s var(--ease), border-color .25s; }
.card:hover { transform: translateY(-3px); box-shadow: var(--shadow-2); border-color: color-mix(in srgb, var(--accent) 35%, var(--line)); }
.card[hidden] { display: none; }
.card-top { display: flex; gap: .9rem; align-items: center; }
.card-top img { width: 3.5rem; height: 3.5rem; border-radius: .85rem; box-shadow: var(--shadow-1); flex: none; }
.card h3 { margin: 0 0 .3rem; font: 600 var(--s-1)/1.2 var(--serif); }
.pills { display: flex; flex-wrap: wrap; gap: .3rem; }
.card p { margin: 0; color: var(--ink-2); font-size: .97rem; }
.card p strong { color: var(--ink); font-weight: 500; }
.card details { font-size: .93rem; color: var(--ink-2); }
.card details summary { cursor: pointer; color: var(--mute); font-size: .88rem; min-height: 32px; display: flex; align-items: center; }
.card details p { margin-top: .5rem; }
.card details summary::before { content: "+"; display: inline-grid; place-items: center; width: 1.1rem; height: 1.1rem; margin-right: .45rem; border-radius: 50%; border: 1px solid var(--line); font: 500 .8rem/1 var(--mono); color: var(--accent-ink); }
.card details[open] summary::before { content: "−"; }
.card details summary:hover { color: var(--ink); }
.note { font-size: .88rem !important; color: var(--mute) !important; border-left: 2px solid var(--line); padding-left: .7rem; }
.card-links { display: flex; flex-wrap: wrap; gap: .45rem; margin-top: auto; padding-top: .3rem; }
.card-links a { font-size: .9rem; font-weight: 500; text-decoration: none; color: var(--ink); background: var(--bg-2); border: 1px solid var(--line-2); padding: .45rem .8rem; border-radius: 999px; min-height: 40px; display: inline-flex; align-items: center; }
.card-links a:first-child { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.card-links a:hover { border-color: var(--ink-2); }
.card-links a:first-child:hover { background: var(--accent-ink); border-color: var(--accent-ink); color: #fff; }
.filters { display: flex; flex-wrap: wrap; gap: .45rem; margin: 0 0 1.2rem; }

/* Hero */
.hero { position: relative; padding: clamp(1.4rem, 4.5vw, 3.2rem) 0 clamp(1.6rem, 4vw, 2.8rem); isolation: isolate; overflow: hidden; }
.hero::before { content: ""; position: absolute; inset: 0; background: var(--glow); z-index: -1; }
.hero h1 { font-size: var(--s-5); max-width: 18ch; }
.hero h1 em { font-style: normal; color: var(--accent); }
.hero-grid { display: grid; gap: 2rem; align-items: center; }
@media (min-width: 1000px) {
  .hero-grid {
    grid-template-columns: minmax(0, 1.25fr) minmax(0, .75fr);
    grid-template-areas: "kicker pulse" "title pulse" "more pulse";
    align-items: start;
  }
  .hero-grid > .kicker { grid-area: kicker; }
  .hero-grid > h1 { grid-area: title; }
  .hero-grid > .hero-pulse { grid-area: pulse; }
  .hero-grid > .hero-more { grid-area: more; }
}
.mosaic { display: none; position: relative; aspect-ratio: 1; max-width: 24rem; margin-inline: auto; width: 100%; }
@media (min-width: 1000px) { .mosaic { display: block; } }
.mosaic img { position: absolute; width: 34%; border-radius: 22%; box-shadow: 0 2px 4px rgb(0 0 0 / .08), 0 24px 48px -16px rgb(27 24 20 / .35); }
.mosaic img:nth-child(1) { left: 33%; top: 33%; width: 38%; z-index: 2; }
.mosaic img:nth-child(2) { left: 2%; top: 10%; transform: rotate(-8deg); }
.mosaic img:nth-child(3) { right: 0; top: 4%; transform: rotate(7deg); }
.mosaic img:nth-child(4) { left: 6%; bottom: 4%; transform: rotate(6deg); }
.mosaic img:nth-child(5) { right: 4%; bottom: 8%; transform: rotate(-6deg); }
@media (prefers-reduced-motion: no-preference) {
  .mosaic img { animation: float 7s ease-in-out infinite; }
  .mosaic img:nth-child(2) { animation-delay: -1.5s; } .mosaic img:nth-child(3) { animation-delay: -3s; }
  .mosaic img:nth-child(4) { animation-delay: -4.5s; } .mosaic img:nth-child(5) { animation-delay: -6s; }
  @keyframes float { 50% { translate: 0 -8px; } }
}
.doors { display: grid; gap: var(--space); margin-top: clamp(2rem, 5vw, 3rem); }
@media (min-width: 760px) { .doors { grid-template-columns: repeat(3, 1fr); } }
.door { display: flex; flex-direction: column; gap: .35rem; padding: 1.2rem 1.25rem 1.1rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-3); text-decoration: none; color: var(--ink); box-shadow: var(--shadow-1); transition: transform .25s var(--ease), box-shadow .25s, border-color .25s; }
.door:hover { transform: translateY(-3px); box-shadow: var(--shadow-2); border-color: color-mix(in srgb, var(--accent) 40%, var(--line)); color: var(--ink); }
.door .ico { width: 2.4rem; height: 2.4rem; border-radius: .7rem; display: grid; place-items: center; background: var(--accent-soft); color: var(--accent-ink); margin-bottom: .4rem; }
.door .ico svg { width: 1.25rem; height: 1.25rem; }
.door strong { font: 600 var(--s-1)/1.2 var(--serif); }
.door span { color: var(--ink-2); font-size: .95rem; }
.door .go { margin-top: auto; padding-top: .5rem; font-size: .88rem; font-weight: 500; color: var(--accent-ink); }
.pulse { margin-top: var(--space); padding: 1rem 1.2rem; display: grid; gap: .7rem; }
.pulse-head { display: flex; flex-wrap: wrap; gap: .4rem 1rem; justify-content: space-between; align-items: baseline; font-size: .9rem; color: var(--mute); }
.pulse-head strong { color: var(--ink); font-weight: 500; }
.pulse-list { display: grid; gap: .5rem; list-style: none; margin: 0; padding: 0; }
@media (min-width: 760px) { .pulse-list { grid-template-columns: repeat(3, 1fr); } }
.pulse-list li { display: flex; align-items: center; gap: .7rem; background: var(--surface-2); border: 1px solid var(--line-2); border-radius: var(--r-2); padding: .55rem .75rem; }
.pulse-list .sym { font: 500 1rem var(--mono); }
.pulse-list .x { margin-left: auto; font: 500 .95rem var(--mono); color: var(--accent-ink); }
.pulse-list .lbl { font-size: .78rem; color: var(--mute); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.hero-pulse { margin-top: 0; align-self: stretch; }
.hero-pulse .pulse-list { grid-template-columns: 1fr; }
.hero-pulse .go { font-weight: 500; font-size: .93rem; }
.door.featured { border-color: color-mix(in srgb, var(--accent) 40%, var(--line)); box-shadow: var(--shadow-2); }
.trust { display: flex; flex-wrap: wrap; gap: .5rem 1.4rem; margin: 1.6rem 0 0; padding: 0; list-style: none; color: var(--ink-2); font-size: .93rem; }
.trust li { display: inline-flex; align-items: center; gap: .45rem; }
.trust svg { width: 1rem; height: 1rem; color: var(--good); }

/* Prose */
.prose { padding: clamp(2rem, 5vw, 3.5rem) 0 clamp(2.5rem, 6vw, 4rem); }
.prose.tight-bottom { padding-bottom: .5rem; }
.prose p, .prose li { color: var(--ink-2); }
.prose strong { color: var(--ink); font-weight: 500; }
.prose ul, .prose ol { margin: 0 0 1.1rem; padding-left: 1.25rem; }
.prose li { margin: 0 0 .45rem; }
.prose li::marker { color: var(--accent); }
.prose h2 { margin-top: 2.4rem; font-size: var(--s-2); }
.flag, .callout { background: var(--warn-soft); border: 1px solid color-mix(in srgb, var(--warn) 25%, transparent); border-radius: var(--r-2); padding: .9rem 1.1rem; margin: 1.2rem 0; font-size: .95rem; }
.flag p, .callout p { margin: 0; color: var(--ink-2); }
.flag strong, .callout strong { color: var(--ink); }
.callout { background: var(--surface-2); border-color: var(--line); }
.callout.compact { font-size: .86rem; padding: .7rem .95rem; }
.contacts { list-style: none; padding: 0 !important; margin: 0 0 1.2rem; display: grid; gap: .6rem; }
.contacts li { display: grid; gap: .2rem; padding: 1rem 1.1rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-2); margin: 0; }
.contacts span { color: var(--mute); font-size: .93rem; }

/* Tables */
.table-wrap { overflow-x: auto; margin: 0 0 1.2rem; border: 1px solid var(--line); border-radius: var(--r-2); background: var(--surface); -webkit-overflow-scrolling: touch; }
table { width: 100%; border-collapse: collapse; font-size: .94rem; }
th, td { text-align: left; padding: .6rem .8rem; border-bottom: 1px solid var(--line-2); vertical-align: top; }
tbody tr:last-child td { border-bottom: 0; }
th { font-weight: 500; color: var(--mute); font-size: .76rem; letter-spacing: .06em; text-transform: uppercase; background: var(--surface-2); white-space: nowrap; }
td.r, th.r { text-align: right; }
td.up { color: var(--good); } td.down { color: var(--bad); }
tbody tr:hover td { background: color-mix(in srgb, var(--accent-soft) 35%, transparent); }

/* Footer */
.site-footer { border-top: 1px solid var(--line); padding: 2.5rem 0 2rem; color: var(--mute); font-size: .93rem; background: var(--bg-2); margin-top: auto; }
.foot-grid { display: grid; gap: 1.6rem; }
@media (min-width: 760px) { .foot-grid { grid-template-columns: 1.4fr 1fr 1fr; } }
.site-footer a { color: var(--ink-2); text-decoration: none; }
.site-footer a:hover { color: var(--ink); text-decoration: underline; }
.site-footer nav { display: flex; flex-direction: column; gap: .5rem; }
.site-footer h2 { font: 500 .72rem var(--sans); letter-spacing: .16em; text-transform: uppercase; color: var(--mute); margin: 0 0 .7rem; }
.stampline { margin-top: 2rem; padding-top: 1.2rem; border-top: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: .4rem 1.2rem; justify-content: space-between; font-size: .82rem; }
.stampline .ver { font-family: var(--mono); color: var(--ink-2); }

/* Shop strip */
.arcade { border-top: 1px solid var(--line); padding: clamp(2rem, 5vw, 3rem) 0; }
.arcade h2 { font-size: var(--s-2); }
.arcade-list { list-style: none; padding: 0; margin: 1.2rem 0 0; display: grid; gap: .6rem; }
@media (min-width: 720px) { .arcade-list { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1040px) { .arcade-list { grid-template-columns: repeat(3, 1fr); } }
.arcade-list li { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-2); padding: .8rem 1rem; color: var(--ink-2); font-size: .93rem; }
.arcade-list a { font-weight: 500; color: var(--ink); text-decoration: none; }
.arcade-list a:hover { color: var(--accent-ink); text-decoration: underline; }

/* Jump dialog */
dialog.jump { border: 1px solid var(--line); border-radius: var(--r-3); padding: 0; width: min(34rem, 100% - 2rem); background: var(--surface); color: var(--ink); box-shadow: var(--shadow-2); margin-top: 12vh; }
dialog.jump::backdrop { background: rgb(10 9 8 / .45); backdrop-filter: blur(3px); }
dialog.jump[open] { animation: pop .18s var(--ease); }
.jump input { width: 100%; border: 0; border-bottom: 1px solid var(--line); background: transparent; color: var(--ink); font: 400 1.05rem var(--sans); padding: 1rem 1.1rem; outline: none; }
.jump ul { list-style: none; margin: 0; padding: .4rem; max-height: 55vh; overflow: auto; }
.jump li a { display: flex; justify-content: space-between; gap: 1rem; padding: .65rem .8rem; border-radius: var(--r-1); color: var(--ink); text-decoration: none; }
.jump li a span { color: var(--mute); font-size: .85rem; text-align: right; }
.jump li a[aria-selected="true"], .jump li a:hover { background: var(--bg-2); }
.jump .hint { font-size: .78rem; color: var(--mute); padding: .5rem 1.1rem .8rem; margin: 0; }

.toast { position: fixed; left: 50%; bottom: 1.4rem; transform: translate(-50%, 1rem); background: var(--ink); color: var(--bg); padding: .6rem 1rem; border-radius: 999px; font-size: .9rem; opacity: 0; pointer-events: none; transition: all .25s var(--ease); z-index: 60; }
.toast.on { opacity: 1; transform: translate(-50%, 0); }

/* Entrance motion: content only, once, and never for reduced motion. */
@media (prefers-reduced-motion: no-preference) {
  .rise { animation: rise .6s var(--ease) both; }
  .rise.d1 { animation-delay: .06s; } .rise.d2 { animation-delay: .12s; } .rise.d3 { animation-delay: .18s; }
  @keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
  @view-transition { navigation: none; }
}

.hero-pulse .mcp { margin: 0; }
.hero-pulse .mcp-tiles { grid-template-columns: 1fr; }
.hero-pulse .mcp-tile { grid-template-columns: auto 1fr auto; grid-template-areas: "x sym play" "x why play"; gap: 1px 14px; padding: 10px 14px; }
.hero-pulse .mcp-x { font-size: clamp(2rem, 9vw, 2.5rem); }
.chatter-top .mcp { margin: 0 0 1.6rem; }
@media print {
  .site-header, .site-footer, .draft, .arcade, .chatter-rail, .no-print { display: none !important; }
  body { background: #fff; color: #000; }
}
"""

ICONS = {
    "sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "moon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "apps": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/></svg>',
    "sunrise": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 18h18M7 18a5 5 0 0 1 10 0M12 4v5M5.6 9.6l1.4 1.4M18.4 9.6 17 11M8 22h8"/></svg>',
    "pulse": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 12h4l3-8 4 16 3-8h4"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5 9-10"/></svg>',
    "share": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7M16 6l-4-4-4 4M12 2v13"/></svg>',
    "link": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>',
}

# Runs before first paint so there is no light flash for dark-mode users.
import mcp_panel  # noqa: E402
MCP_JS = mcp_panel.JS

THEME_BOOT = """<script>(function(){try{var t=localStorage.getItem('plja-theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>"""

SHELL_JS = r"""<script>
(function(){
  var root = document.documentElement;
  function current(){ var t = root.getAttribute('data-theme'); if (t) return t; return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; }
  var tb = document.getElementById('theme-btn');
  function paint(){ if (!tb) return; var d = current() === 'dark'; tb.setAttribute('aria-pressed', d ? 'true' : 'false'); tb.setAttribute('aria-label', d ? 'Switch to light mode' : 'Switch to dark mode'); tb.innerHTML = d ? tb.dataset.sun : tb.dataset.moon; var m = document.querySelector('meta[name="theme-color"]'); if (m) m.content = d ? '#12110f' : '#f5f0e7'; }
  if (tb) tb.addEventListener('click', function(){ var n = current() === 'dark' ? 'light' : 'dark'; root.setAttribute('data-theme', n); try { localStorage.setItem('plja-theme', n); } catch(e){} paint(); });
  paint();
  // Jump anywhere: press / or Ctrl/Cmd+K.
  var dlg = document.getElementById('jump'), inp = document.getElementById('jump-q'), list = document.getElementById('jump-list');
  var jb = document.getElementById('jump-btn');
  if (dlg && inp && list) {
    var items = [].slice.call(list.querySelectorAll('li'));
    var sel = 0;
    function vis(){ return items.filter(function(li){ return !li.hidden; }); }
    function mark(){ var v = vis(); v.forEach(function(li, i){ li.firstChild.setAttribute('aria-selected', i === sel ? 'true' : 'false'); }); if (v[sel]) v[sel].scrollIntoView({block:'nearest'}); }
    function filter(){ var q = inp.value.toLowerCase().trim(); items.forEach(function(li){ li.hidden = q && li.textContent.toLowerCase().indexOf(q) < 0; }); sel = 0; mark(); }
    function open(){ if (dlg.open) return; inp.value = ''; filter(); dlg.showModal(); inp.focus(); }
    inp.addEventListener('input', filter);
    inp.addEventListener('keydown', function(e){ var v = vis(); if (e.key === 'ArrowDown'){ sel = Math.min(sel+1, v.length-1); mark(); e.preventDefault(); } else if (e.key === 'ArrowUp'){ sel = Math.max(sel-1, 0); mark(); e.preventDefault(); } else if (e.key === 'Enter' && v[sel]){ location.href = v[sel].firstChild.href; } });
    dlg.addEventListener('click', function(e){ if (e.target === dlg) dlg.close(); });
    if (jb) jb.addEventListener('click', open);
    document.addEventListener('keydown', function(e){
      var tag = (e.target.tagName || '').toLowerCase();
      if ((e.key === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && tag !== 'input' && tag !== 'textarea')) { e.preventDefault(); open(); }
    });
  }
  window.plja = window.plja || {};
  window.plja.toast = function(msg){ var t = document.getElementById('toast'); if (!t) return; t.textContent = msg; t.classList.add('on'); clearTimeout(t._h); t._h = setTimeout(function(){ t.classList.remove('on'); }, 2200); };

  // Fill the site-wide Market Chatter card and the home pulse from the live board.
  // Site-wide Market Chatter card: show the loudest clean name.
  var railTop = document.getElementById('rail-top');
  if (railTop && window.fetch) {
    function get(u){ return fetch(u, {cache:'no-store'}).then(function(r){ return r.ok ? r.json() : null; }).catch(function(){ return null; }); }
    Promise.all([get('/live/board.json'), get('https://raw.githubusercontent.com/Pdee1077/plja-corp/live-data/board.json?t=' + Date.now())]).then(function(p){
      var d = p[1] || p[0];
      if (p[0] && p[1] && new Date(p[0].updated) > new Date(p[1].updated)) d = p[0];
      if (!d || !d.rows) return;
      var rows = d.rows.filter(function(r){ return r.group === 'abnormal' && r.st_x_normal != null && r.st_x_normal >= 2 && !/-/.test(r.sym || ''); });
      rows.sort(function(a, b){ return b.st_x_normal - a.st_x_normal; });
      if (rows[0]) { railTop.textContent = rows[0].sym + ' \u00b7 ' + rows[0].st_x_normal.toFixed(1) + '\u00d7 its usual chatter'; railTop.hidden = false; }
    });
  }
})();
</script>"""


def nav_links(current: str, cls: str = "") -> str:
    out = []
    section = next((v for k, v in SECTION_OF.items() if current.startswith(k)), current)
    for href, label in NAV:
        on = section == href or (href != "/" and section.startswith(href))
        cur = ' aria-current="page"' if on else ""
        extra = ' class="live-dot"' if href == "/chatter/" else ""
        out.append(f'<a href="{href}"{cur}{extra}>{label}</a>')
    return "".join(out)



def chatter_rail(current: str) -> str:
    """A modest Market Chatter card on every page except the room itself."""
    if current.startswith("/chatter/") or current in ("/", ""):
        return ""
    return """
  <aside class="chatter-rail" aria-label="Market Chatter">
    <div class="wrap">
      <a href="/chatter/">
        <span class="ttl">Market Chatter — live</span>
        <span class="top" id="rail-top" hidden></span>
        <span class="why">What the internet is talking about vs. its usual chatter. Research, not advice.</span>
        <span class="go">Open the board &rarr;</span>
      </a>
    </div>
  </aside>"""


def header(current: str) -> str:
    sun = ICONS["sun"].replace('"', "&quot;")
    moon = ICONS["moon"].replace('"', "&quot;")
    return f"""
  <header class="site-header">
    <div class="wrap bar">
      <a class="brand" href="/" aria-label="PLJA Corp home">
        <img src="/assets/img/mark.svg" width="32" height="32" alt="">
        <span class="name">PLJA<span class="corp">CORP</span></span>
      </a>
      <nav class="nav" aria-label="Primary">{nav_links(current, "wide")}</nav>
      <button class="tool jump-btn" id="jump-btn" type="button" aria-label="Jump to a page" aria-keyshortcuts="/ Control+K">{ICONS["search"]}<span class="lbl">Jump</span><kbd>/</kbd></button>
      <button class="tool" id="theme-btn" type="button" aria-label="Switch theme" aria-pressed="false" data-sun="{sun}" data-moon="{moon}">{ICONS["moon"]}</button>
      <details class="menu">
        <summary class="tool" aria-label="Menu">{ICONS["menu"]}</summary>
        <nav class="panel" aria-label="Primary">{nav_links(current)}<a href="/contact/">Contact</a><a href="/privacy/">Privacy</a></nav>
      </details>
    </div>
  </header>"""


def jump_dialog() -> str:
    items = "".join(
        f'<li><a href="{href}"{" rel=\"noopener noreferrer\"" if href.startswith("http") else ""}>{label}<span>{hint}</span></a></li>'
        for label, href, hint in JUMP
    )
    return f"""
  <dialog class="jump" id="jump" aria-label="Jump to a page">
    <label class="sr-only" for="jump-q">Search pages</label>
    <input id="jump-q" type="search" placeholder="Jump to… (apps, Daily Scan, Live board)" autocomplete="off">
    <ul id="jump-list">{items}</ul>
    <p class="hint">↑ ↓ to move · Enter to open · Esc to close</p>
  </dialog>
  <div class="toast" id="toast" role="status" aria-live="polite"></div>"""


def footer(blurb: str, extra_note: str = "", utm: str = "") -> str:
    q = f"?{utm}" if utm else ""
    return f"""
  <footer class="site-footer">
    <div class="wrap">
      <div class="foot-grid">
        <div>
          <a class="brand" href="/">
            <img src="/assets/img/mark.svg" width="32" height="32" alt="" loading="lazy">
            <span class="name">PLJA<span class="corp">CORP</span></span>
          </a>
          <p>{blurb}</p>
        </div>
        <div>
          <h2>Site</h2>
          <nav aria-label="Footer">
            <a href="/chatter/">Market Chatter</a>
            <a href="/products/">Apps</a>
            <a href="/about/">About</a>
            <a href="/contact/">Contact</a>
            <a href="/support/">Support</a>
            <a href="/privacy/">Privacy</a>
          </nav>
        </div>
        <div>
          <h2>Elsewhere</h2>
          <nav aria-label="Elsewhere">
            <a href="https://analogarcade.net/{q}">Analog Arcade (our studio&rsquo;s shop)</a>
            <a href="https://apps.apple.com/us/developer/peter-de-paola/id6804326068">App Store developer page</a>
            <a href="https://x.com/PLJA_AI">@PLJA_AI on X</a>
          </nav>
        </div>
      </div>
      <div class="stampline">
        <span>© {YEAR} PLJA Corp.{(" " + extra_note) if extra_note else ""}</span>
        <span class="ver">v{VERSION} · {PUBLISHED}</span>
      </div>
    </div>
  </footer>"""


def page(
    *,
    title: str,
    description: str,
    path: str,
    body: str,
    og_image: str = "/assets/img/og.png",
    og_type: str = "website",
    robots: str | None = None,
    draft_banner: bool = True,
    footer_blurb: str = "The company name Pete De Paola uses for the apps he makes. Analog Arcade is the public shop.",
    footer_note: str = "",
    after_main: str = "",
    scripts: str = "",
    utm: str = "",
    extra_head: str = "",
    preload_mono: bool = False,
) -> str:
    canonical = SITE + path
    og = SITE + og_image
    robots_tag = f'\n  <meta name="robots" content="{robots}">' if robots else ""
    banner = (
        '\n  <div class="draft">Preview site on <strong>plja-corp.pages.dev</strong>. No custom domain is attached yet.</div>'
        if draft_banner
        else ""
    )
    mono = '\n  <link rel="preload" href="/assets/fonts/ibm-plex-mono-medium.woff2" as="font" type="font/woff2" crossorigin>' if preload_mono else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{description}">{robots_tag}
  <link rel="canonical" href="{canonical}">
  <meta name="theme-color" content="#f5f0e7">
  <meta name="color-scheme" content="light dark">
  <meta name="generator" content="PLJA site v{VERSION}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="PLJA Corp">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{og}">
  <link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/assets/img/favicon-32.png" type="image/png" sizes="32x32">
  <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
  <link rel="preload" href="/assets/fonts/ibm-plex-sans-regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/fraunces-semibold.woff2" as="font" type="font/woff2" crossorigin>{mono}
  <link rel="stylesheet" href="{CSS_HREF}">
  {THEME_BOOT}{extra_head}
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>{banner}
  {header(path)}
  {chatter_rail(path)}
  <main id="main">
    {body}
  </main>
  {after_main}
  {footer(footer_blurb, footer_note, utm)}
  {jump_dialog()}
  {SHELL_JS}
  {MCP_JS}
  {scripts}
</body>
</html>
"""


APPS_STRIP = [
    ("Analog Arcade", "The shop for the apps, tools and games.", "https://analogarcade.net/"),
    ("Local Mass Finder", "Nearby Mass times in the browser.", "https://church.analogarcade.net/"),
    ("Overhead", "Point your phone at the night sky.", "https://sky.analogarcade.net/"),
    ("Kept", "A private page for family stories.", "https://kept.analogarcade.net/"),
    ("Atlas Kitchen", "Meal plans with local grocery prices.", "https://kitchen.analogarcade.net/"),
    ("House Binder", "Photograph an appliance, get the manual.", "https://binder.analogarcade.net/"),
    ("Keysong", "Watch a song play itself in the browser.", "https://analogarcade.net/write-notes/"),
]


def arcade_section(utm: str, what: str) -> str:
    items = "\n".join(
        f'          <li><a href="{url}?{utm}">{name}</a> — {blurb}</li>' for name, blurb, url in APPS_STRIP
    )
    return f"""
  <section class="arcade" aria-labelledby="arcade-heading">
    <div class="wrap">
      <p class="kicker">Also from Analog Arcade</p>
      <h2 id="arcade-heading">See the rest of the shop</h2>
      <p>{what} is one free page from <a href="https://analogarcade.net/?{utm}">Analog Arcade</a>. The same shop also makes apps, tools and games — some free, some a one-time price, no feed and no ads required to try them.</p>
      <ul class="arcade-list">
{items}
      </ul>
    </div>
  </section>"""


def write_css(public) -> None:
    out = public / "assets" / "css" / f"plja-{VERSION}.css"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(CSS + "\n" + mcp_panel.CSS + "\n", encoding="utf-8")
    js_dir = public / "assets" / "js"
    js_dir.mkdir(parents=True, exist_ok=True)
    js_src = Path(__file__).with_name("chatter-briefing.js")
    if js_src.exists():
        (js_dir / "chatter-briefing.js").write_text(js_src.read_text(encoding="utf-8"), encoding="utf-8")


def write_page_css(public, name: str, css: str) -> str:
    """Write a page-specific stylesheet with a versioned name and return its href."""
    href = f"/assets/css/{name}-{VERSION}.css"
    out = public / href.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(css, encoding="utf-8")
    return href

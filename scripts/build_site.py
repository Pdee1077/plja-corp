#!/usr/bin/env python3
"""Build the first-draft PLJA Corp static site into public/."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import cairosvg
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ASSETS = PUBLIC / "assets"
FONTS_OUT = ASSETS / "fonts"
IMG = ASSETS / "img"
APPS = IMG / "apps"
SITE_ORIGIN = "https://plja-corp.pages.dev"
YEAR = "2026"

FRAUNCES_VAR = Path(
    "/usr/share/fonts/truetype/sand-box/google/Fraunces/Fraunces-VariableFont_SOFT,WONK,opsz,wght.ttf"
)
PLEX_VAR = Path(
    "/usr/share/fonts/truetype/sand-box/google/IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf"
)
# Temporary instantiated fonts for raster work
TMP = ROOT / ".tmp-fonts"

UNICODES = "U+0020-007E,U+00A0-00FF,U+2010-2027,U+20AC,U+2190-2193"

NAV = [
    ("Products", "/products/"),
    ("About", "/about/"),
    ("Contact", "/contact/"),
    ("Support", "/support/"),
]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def subset_fonts() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    FONTS_OUT.mkdir(parents=True, exist_ok=True)
    fra_inst = TMP / "Fraunces-600.ttf"
    plex_reg = TMP / "Plex-400.ttf"
    plex_med = TMP / "Plex-500.ttf"
    if not fra_inst.exists():
        run(
            [
                "fonttools",
                "varLib.instancer",
                str(FRAUNCES_VAR),
                "wght=600",
                "opsz=48",
                "SOFT=0",
                "WONK=0",
                "-o",
                str(fra_inst),
            ]
        )
    if not plex_reg.exists():
        run(
            [
                "fonttools",
                "varLib.instancer",
                str(PLEX_VAR),
                "wght=400",
                "wdth=100",
                "-o",
                str(plex_reg),
            ]
        )
    if not plex_med.exists():
        run(
            [
                "fonttools",
                "varLib.instancer",
                str(PLEX_VAR),
                "wght=500",
                "wdth=100",
                "-o",
                str(plex_med),
            ]
        )
    for src, dest in [
        (fra_inst, FONTS_OUT / "fraunces-semibold.woff2"),
        (plex_reg, FONTS_OUT / "ibm-plex-sans-regular.woff2"),
        (plex_med, FONTS_OUT / "ibm-plex-sans-medium.woff2"),
    ]:
        run(
            [
                "pyftsubset",
                str(src),
                f"--output-file={dest}",
                "--flavor=woff2",
                f"--unicodes={UNICODES}",
                "--layout-features=kern,liga,calt,tnum,lnum",
                "--no-hinting",
                "--desubroutinize",
            ]
        )
        print("font", dest.name, dest.stat().st_size)
    mono_src = Path("/usr/share/fonts/truetype/sand-box/google/IBM Plex Mono/IBMPlexMono-Medium.ttf")
    mono_dest = FONTS_OUT / "ibm-plex-mono-medium.woff2"
    if mono_src.exists():
        run(["pyftsubset", str(mono_src), f"--output-file={mono_dest}", "--flavor=woff2",
             "--unicodes=U+0020-007E,U+00D7,U+2013,U+2014,U+2212,U+2191,U+2193", "--layout-features=kern",
             "--no-hinting", "--desubroutinize"])
        print("font", mono_dest.name, mono_dest.stat().st_size)


MARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="PLJA Corp">
  <rect width="64" height="64" rx="14" fill="#1C1915"/>
  <!-- P -->
  <path fill="#F4EFE6" d="M11 12.5h8.4c5.1 0 8.3 2.55 8.3 6.85 0 4.2-3.2 6.85-8.3 6.85H16.4V31.5H11V12.5zm5.4 4.15v5.4h2.85c2.35 0 3.55-1.05 3.55-2.7 0-1.65-1.2-2.7-3.55-2.7H16.4z"/>
  <!-- L -->
  <path fill="#F4EFE6" d="M35 12.5h5.4V27.2H47.2V31.5H35V12.5z"/>
  <!-- J -->
  <path fill="#F4EFE6" d="M24.2 36.2V40.1H16.5v-3.9h7.7zm-2.7 0v12.15c0 4.7-2.95 7.15-7.7 7.15-2.55 0-4.85-.85-6.5-2.35l3.05-3.55c.95.9 2.1 1.4 3.4 1.4 1.85 0 2.75-1.05 2.75-2.85V36.2h5z"/>
  <!-- A -->
  <path fill="#F4EFE6" d="M47.15 55.5h-5.55l-.9-2.35h-6.4l-.9 2.35h-5.45L35.7 36.2h6.15l5.3 19.3zM41.55 48.4L38.75 41.2l-2.8 7.2h5.6z"/>
  <rect x="10" y="58.2" width="44" height="2.4" rx="1.2" fill="#B35A32"/>
</svg>
"""

WORDMARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 64" role="img" aria-label="PLJA Corp">
  <rect width="64" height="64" rx="14" fill="#1C1915"/>
  <path fill="#F4EFE6" d="M11 12.5h8.4c5.1 0 8.3 2.55 8.3 6.85 0 4.2-3.2 6.85-8.3 6.85H16.4V31.5H11V12.5zm5.4 4.15v5.4h2.85c2.35 0 3.55-1.05 3.55-2.7 0-1.65-1.2-2.7-3.55-2.7H16.4z"/>
  <path fill="#F4EFE6" d="M35 12.5h5.4V27.2H47.2V31.5H35V12.5z"/>
  <path fill="#F4EFE6" d="M24.2 36.2V40.1H16.5v-3.9h7.7zm-2.7 0v12.15c0 4.7-2.95 7.15-7.7 7.15-2.55 0-4.85-.85-6.5-2.35l3.05-3.55c.95.9 2.1 1.4 3.4 1.4 1.85 0 2.75-1.05 2.75-2.85V36.2h5z"/>
  <path fill="#F4EFE6" d="M47.15 55.5h-5.55l-.9-2.35h-6.4l-.9 2.35h-5.45L35.7 36.2h6.15l5.3 19.3zM41.55 48.4L38.75 41.2l-2.8 7.2h5.6z"/>
  <rect x="10" y="58.2" width="44" height="2.4" rx="1.2" fill="#B35A32"/>
  <text x="80" y="30" fill="#1C1915" font-family="IBM Plex Sans, Helvetica Neue, sans-serif" font-size="22" font-weight="500" letter-spacing="0.08em">PLJA</text>
  <text x="80" y="50" fill="#6B645A" font-family="IBM Plex Sans, Helvetica Neue, sans-serif" font-size="13" font-weight="500" letter-spacing="0.22em">CORP</text>
</svg>
"""


def write_mark() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    (IMG / "mark.svg").write_text(MARK_SVG, encoding="utf-8")
    (IMG / "favicon.svg").write_text(MARK_SVG, encoding="utf-8")
    (IMG / "wordmark.svg").write_text(WORDMARK_SVG, encoding="utf-8")
    # Raster favicons and apple touch
    for size, name in [(32, "favicon-32.png"), (16, "favicon-16.png"), (180, "apple-touch-icon.png"), (512, "icon-512.png")]:
        cairosvg.svg2png(bytestring=MARK_SVG.encode(), write_to=str(IMG / name), output_width=size, output_height=size)
    # ICO from 32 and 16
    imgs = [Image.open(IMG / "favicon-16.png").convert("RGBA"), Image.open(IMG / "favicon-32.png").convert("RGBA")]
    imgs[1].save(IMG / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32)])


def make_og() -> None:
    W, H = 1200, 630
    paper = (244, 239, 230)
    ink = (28, 25, 21)
    mute = (107, 100, 90)
    copper = (179, 90, 50)
    img = Image.new("RGB", (W, H), paper)
    draw = ImageDraw.Draw(img)
    # subtle top copper rule
    draw.rectangle([0, 0, W, 8], fill=copper)
    mark_png = cairosvg.svg2png(bytestring=MARK_SVG.encode(), output_width=220, output_height=220)
    import io
    mark = Image.open(io.BytesIO(mark_png)).convert("RGBA")
    # drop a soft shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([88, 196, 88 + 228, 196 + 228], radius=48, fill=(28, 25, 21, 30))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    img.paste(mark, (94, 202), mark)
    fra = ImageFont.truetype(str(TMP / "Fraunces-600.ttf"), 92)
    plex = ImageFont.truetype(str(TMP / "Plex-400.ttf"), 32)
    plex_sm = ImageFont.truetype(str(TMP / "Plex-500.ttf"), 22)
    draw = ImageDraw.Draw(img)
    draw.text((360, 220), "PLJA Corp", font=fra, fill=ink)
    draw.text((360, 330), "Local-first apps, priced once.", font=plex, fill=ink)
    draw.text((360, 382), "A solo maker · Pete De Paola", font=plex_sm, fill=mute)
    img.save(IMG / "og.png", "PNG", optimize=True)
    print("og", (IMG / "og.png").stat().st_size)


def prepare_app_icons() -> None:
    APPS.mkdir(parents=True, exist_ok=True)
    srcs = {
        "houseradar.jpg": Path("/tmp/plja-facts/icons/houseradar-512.jpg"),
        "massfinder.jpg": Path("/tmp/plja-facts/icons/massfinder-512.jpg"),
        "keysong.jpg": Path("/tmp/plja-facts/icons/keysong-512.jpg"),
        "binder.png": Path("/tmp/plja-facts/icons/binder-apple.png"),
        "cardcheck.png": Path("/tmp/plja-facts/icons/cards-192.png"),
    }
    for dest_name, src in srcs.items():
        out = APPS / dest_name
        if not src.exists():
            print("icon kept", dest_name, "(source not on this machine)")
            continue
        im = Image.open(src)
        im = im.resize((256, 256), Image.Resampling.LANCZOS)
        if dest_name.endswith(".jpg"):
            im.convert("RGB").save(out, "JPEG", quality=85, optimize=True, progressive=True)
        else:
            im.convert("RGBA").save(out, "PNG", optimize=True)
        print("icon", dest_name, out.stat().st_size, im.size)


CSS = r"""/* PLJA Corp — first-draft company site. System of ink, paper, copper. */
@font-face {
  font-family: "Fraunces";
  src: url("/assets/fonts/fraunces-semibold.woff2") format("woff2");
  font-weight: 600;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "IBM Plex Sans";
  src: url("/assets/fonts/ibm-plex-sans-regular.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "IBM Plex Sans";
  src: url("/assets/fonts/ibm-plex-sans-medium.woff2") format("woff2");
  font-weight: 500;
  font-style: normal;
  font-display: swap;
}

:root {
  --paper: #f4efe6;
  --paper-deep: #ebe4d6;
  --card: #fffdf8;
  --ink: #1c1915;
  --mute: #5c564e;
  --line: #d8d0c3;
  --copper: #b35a32;
  --copper-deep: #8c3b24;
  --forest: #2d5a3d;
  --forest-soft: #e6f0e8;
  --max: 68rem;
  --text: 38rem;
  --pad: clamp(1.15rem, 4vw, 2rem);
  --sans: "IBM Plex Sans", "Helvetica Neue", Helvetica, ui-sans-serif, system-ui, sans-serif;
  --serif: "Fraunces", "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --shadow: 0 1px 2px rgba(28, 25, 21, 0.06), 0 10px 30px rgba(28, 25, 21, 0.05);
  --radius: 1.15rem;
}

*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  * { animation: none !important; transition: none !important; }
}
html, body { margin: 0; padding: 0; }
body {
  background: var(--paper);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 1.0625rem;
  line-height: 1.6;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}
img { max-width: 100%; height: auto; display: block; }
a { color: var(--copper-deep); text-underline-offset: 0.15em; }
a:hover { color: var(--ink); }
a:focus-visible, button:focus-visible, summary:focus-visible {
  outline: 3px solid var(--copper);
  outline-offset: 3px;
}

.skip {
  position: absolute;
  left: 1rem;
  top: -4rem;
  background: var(--ink);
  color: var(--paper);
  padding: 0.6rem 0.9rem;
  z-index: 20;
  border-radius: 0.4rem;
}
.skip:focus { top: 1rem; color: var(--paper); }

.draft {
  background: var(--ink);
  color: var(--paper);
  font-size: 0.86rem;
  letter-spacing: 0.01em;
  text-align: center;
  padding: 0.55rem var(--pad);
}
.draft strong { font-weight: 500; }

.wrap { width: min(var(--max), 100% - 2 * var(--pad)); margin-inline: auto; }
.narrow { width: min(var(--text), 100% - 2 * var(--pad)); margin-inline: auto; }

.site-header {
  border-bottom: 1px solid var(--line);
  background: color-mix(in srgb, var(--paper) 88%, white);
  backdrop-filter: saturate(1.2) blur(10px);
  position: sticky;
  top: 0;
  z-index: 10;
}
.bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-height: 4rem;
  width: min(var(--max), 100% - 2 * var(--pad));
  margin-inline: auto;
}
.brand {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  text-decoration: none;
  color: var(--ink);
  font-weight: 500;
  letter-spacing: 0.08em;
  font-size: 0.95rem;
}
.brand img, .brand svg { width: 2.15rem; height: 2.15rem; border-radius: 0.48rem; }
.brand .name { display: flex; flex-direction: column; line-height: 1.05; }
.brand .corp { font-size: 0.68rem; letter-spacing: 0.22em; color: var(--mute); font-weight: 500; }

.nav-wide { display: none; gap: 0.25rem; }
.nav-wide a {
  color: var(--ink);
  text-decoration: none;
  padding: 0.55rem 0.8rem;
  border-radius: 999px;
  font-size: 0.95rem;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}
.nav-wide a:hover, .nav-wide a[aria-current="page"] { background: var(--paper-deep); }
.nav-wide a[aria-current="page"] { font-weight: 500; }

nav.mobile { display: block; }
nav.mobile summary {
  list-style: none;
  cursor: pointer;
  padding: 0.55rem 0.85rem;
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--card);
  font-weight: 500;
  font-size: 0.92rem;
}
nav.mobile summary::-webkit-details-marker { display: none; }
nav.mobile[open] summary { background: var(--ink); color: var(--paper); border-color: var(--ink); }
nav.mobile .panel {
  position: absolute;
  right: var(--pad);
  top: calc(4rem + 0.4rem);
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 1rem;
  box-shadow: var(--shadow);
  padding: 0.5rem;
  min-width: 14rem;
  display: flex;
  flex-direction: column;
}
nav.mobile .panel a {
  color: var(--ink);
  text-decoration: none;
  padding: 0.75rem 0.9rem;
  border-radius: 0.7rem;
  min-height: 44px;
  display: flex;
  align-items: center;
}
nav.mobile .panel a:hover, nav.mobile .panel a[aria-current="page"] { background: var(--paper-deep); }

@media (min-width: 720px) {
  nav.mobile { display: none; }
  .nav-wide { display: flex; }
}

.hero { padding: clamp(2.2rem, 6vw, 5rem) 0 2.4rem; }
.kicker {
  font-size: 0.8rem;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--copper-deep);
  margin: 0 0 0.85rem;
}
h1, h2, h3 { font-family: var(--serif); font-weight: 600; line-height: 1.15; letter-spacing: -0.02em; }
h1 { font-size: clamp(2.25rem, 6vw, 4.1rem); margin: 0 0 1rem; }
h2 { font-size: clamp(1.6rem, 3vw, 2.15rem); margin: 0 0 0.8rem; }
h3 { font-size: 1.25rem; margin: 0 0 0.35rem; }
.lede { font-size: clamp(1.1rem, 2.2vw, 1.3rem); color: var(--mute); max-width: 38rem; margin: 0 0 1.5rem; }
.lede strong { color: var(--ink); font-weight: 500; }

.actions { display: flex; flex-wrap: wrap; gap: 0.7rem; margin: 1.4rem 0 0; }
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.65rem 1.15rem;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 500;
  border: 1px solid transparent;
}
.btn-primary { background: var(--ink); color: var(--paper); }
.btn-primary:hover { background: var(--copper-deep); color: var(--paper); }
.btn-ghost { background: transparent; color: var(--ink); border-color: var(--line); }
.btn-ghost:hover { border-color: var(--ink); color: var(--ink); background: var(--card); }

.section { padding: 1.5rem 0 3.2rem; }
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.2rem;
  flex-wrap: wrap;
}
.section-head a { font-weight: 500; }

.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
@media (min-width: 640px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 960px) {
  .grid.products { grid-template-columns: repeat(2, 1fr); }
}

.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1.2rem 1.2rem 1.25rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  height: 100%;
}
.card-top { display: flex; gap: 0.9rem; align-items: flex-start; }
.card-top img {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 0.85rem;
  flex: none;
  background: var(--paper-deep);
}
.pills { display: flex; flex-wrap: wrap; gap: 0.35rem; margin: 0.15rem 0 0; }
.pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.02em;
  padding: 0.18rem 0.5rem;
  border-radius: 999px;
  background: var(--paper-deep);
  color: var(--ink);
}
.pill-free { background: var(--forest-soft); color: var(--forest); }
.pill-paid { background: #f3e3da; color: var(--copper-deep); }
.card p { margin: 0; color: var(--mute); }
.card p strong { color: var(--ink); font-weight: 500; }
.note {
  font-size: 0.9rem;
  color: var(--mute);
  border-left: 3px solid var(--line);
  padding-left: 0.75rem;
  margin: 0.2rem 0 0;
}
.card-links { display: flex; flex-wrap: wrap; gap: 0.55rem; margin-top: auto; padding-top: 0.4rem; }
.card-links a {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  font-weight: 500;
  text-decoration: none;
  padding: 0.35rem 0.15rem;
}
.prose { padding: 2rem 0 3.5rem; }
.prose p { margin: 0 0 1rem; }
.prose ul, .prose ol { margin: 0 0 1.1rem; padding-left: 1.2rem; }
.prose li { margin: 0 0 0.4rem; }
.prose h2 { margin-top: 2.2rem; }
.flag {
  background: #f3e3da;
  border: 1px solid #e2c4b3;
  border-radius: 0.9rem;
  padding: 1rem 1.1rem;
  margin: 1.2rem 0;
}
.flag strong { color: var(--copper-deep); }
.contacts { list-style: none; padding: 0; margin: 0 0 1.2rem; }
.contacts li {
  display: grid;
  gap: 0.15rem;
  padding: 0.9rem 0;
  border-bottom: 1px solid var(--line);
}
.contacts span { color: var(--mute); font-size: 0.92rem; }

.site-footer {
  border-top: 1px solid var(--line);
  padding: 2rem 0 2.6rem;
  color: var(--mute);
  font-size: 0.95rem;
}
.foot-grid {
  display: grid;
  gap: 1.5rem;
}
@media (min-width: 720px) {
  .foot-grid { grid-template-columns: 1.3fr 1fr 1fr; }
}
.site-footer a { color: var(--ink); text-decoration: none; }
.site-footer a:hover { text-decoration: underline; }
.site-footer nav { display: flex; flex-direction: column; gap: 0.45rem; }
.site-footer h2 { font-family: var(--sans); font-size: 0.75rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--mute); margin: 0 0 0.6rem; font-weight: 500; }
.tiny { margin-top: 1.8rem; font-size: 0.85rem; }
"""


def nav_html(current: str) -> str:
    def link(href: str, label: str) -> str:
        cur = ' aria-current="page"' if href == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'

    items = "".join(link(h, l) for l, h in NAV)
    return f"""
    <nav class="nav-wide" aria-label="Primary">{items}</nav>
    <nav class="mobile" aria-label="Primary">
      <details>
        <summary>Menu</summary>
        <div class="panel">{items}</div>
      </details>
    </nav>"""


def layout(title: str, description: str, path: str, body: str, og_title: str | None = None, scripts: str = "", preload_mono: bool = False) -> str:
    return theme.page(title=title, description=description, path=path, body=body, scripts=scripts, preload_mono=preload_mono)


def product_card(
    name: str,
    icon: str,
    icon_alt: str,
    pills: list[tuple[str, str]],
    pitch: str,
    body: str,
    note: str | None,
    links: list[tuple[str, str, bool]],
) -> str:
    pill_html = "".join(f'<span class="pill {cls}">{label}</span>' for label, cls in pills)
    tags = set()
    for label, cls in pills:
        low = label.lower()
        if "free" in low or cls == "pill-free":
            tags.add("free")
        if "iphone" in low or "ipad" in low:
            tags.add("iphone")
        if "web" in low:
            tags.add("web")
        if "mac" in low:
            tags.add("mac")
    note_html = f'<p class="note">{note}</p>' if note else ""
    bits = []
    for label, href, ext in links:
        rel = ' rel="noopener noreferrer"' if ext else ""
        bits.append(f'<a href="{href}"{rel}>{label}</a>')
    link_html = "".join(bits)
    return f"""
    <article class="card" data-tags="{' '.join(sorted(tags))}">
      <div class="card-top">
        <img src="{icon}" width="56" height="56" alt="{icon_alt}" loading="lazy" decoding="async">
        <div>
          <h3>{name}</h3>
          <div class="pills">{pill_html}</div>
        </div>
      </div>
      <p><strong>{pitch}</strong></p>
      <details>
        <summary>Details, price and fine print</summary>
        <p>{body}</p>
        {note_html}
      </details>
      <div class="card-links">{link_html}</div>
    </article>
    """


CARDS = "".join(
    [
        product_card(
            "House Binder",
            "/assets/img/apps/binder.png",
            "House Binder icon: a green binder with a small house on the cover",
            [("Web", ""), ("Free on the live site", "pill-free")],
            "Photograph the label on a boiler, air conditioner or other appliance. House Binder names it, works out its age, finds the manual, and checks for a recall.",
            "Your binder is private to your sign-in. Sign in with Apple, Google, or email. “We never invent a part number or a build date. Every fact says where it came from.” The live sign-in page, checked 22 November 2026, America/New_York, describes it as free. It is not on the App Store.",
            None,
            [("Open House Binder", "https://binder.analogarcade.net/", True)],
        ),
        product_card(
            "House Radar",
            "/assets/img/apps/houseradar.jpg",
            "House Radar app icon",
            [
                ("iPhone & iPad", ""),
                ("$2.99 once", "pill-paid"),
                ("App Store 1.10", ""),
            ],
            "Finds the things in your home that send a signal — phones, earbuds, watches, TVs and speakers — and walks you to them.",
            "The screen goes from cold blue to hot red, with Warmer, Colder or Right here. Quick scan lists devices on the Wi-Fi you are on. Optional free Mac home base for whole-house finding. Version 1.10 on the US App Store (released 21 November 2026, 5:19 PM ET) costs $2.99 once, with no subscription and no in-app purchases. It needs iOS 16 or later.",
            "Signal strength is a guide, not a tape measure. AirPods connected to the iPhone may not broadcast; the app tells you to use Find My to play a sound.",
            [
                ("App Store", "https://apps.apple.com/us/app/house-radar/id6816271323", True),
                ("Guide", "https://analogarcade.net/houseradar/", True),
            ],
        ),
        product_card(
            "Local Mass Finder",
            "/assets/img/apps/massfinder.jpg",
            "Local Mass Finder app icon",
            [
                ("Web + iPhone & Mac", ""),
                ("Free", "pill-free"),
                ("App Store 1.1.1", ""),
            ],
            "Next Mass or worship near you — all faiths welcome.",
            "The web app is free at church.analogarcade.net (live site showed v2.33.44, updated Saturday 21 November 2026, 9:34 AM Eastern). It can browse all 50 U.S. states, plus Italy and Rome where listed, and is also offered in Español and other languages on the site. The App Store app is also free, version 1.1.1 (released 19 November 2026, 12:15 PM ET), for iPhone and Mac, with no account and no ads. The app’s own listing says it has more than 6,000 places of worship across 48 states; that figure is for the app, not a claim about the website.",
            "Independent — not affiliated with any church, diocese, synagogue, mosque or temple. Always verify with the parish before you go.",
            [
                ("Open the web app", "https://church.analogarcade.net/", True),
                ("App Store", "https://apps.apple.com/us/app/local-mass-finder/id6825162225", True),
            ],
        ),
        product_card(
            "Keysong",
            "/assets/img/apps/keysong.jpg",
            "Keysong app icon",
            [
                ("iPhone, iPad & Mac", ""),
                ("Free", "pill-free"),
                ("App Store 1.0.6", ""),
            ],
            "Tap a piano key. Press Write. That’s a song — chords underneath, a tune on top.",
            "Free on the App Store, version 1.0.6 (released 16 November 2026, 6:05 PM ET). It teaches 34 well-known songs one lit key at a time. No account. It works without internet; nothing leaves the device. There is also a free browser preview, and an optional free zip on Gumroad.",
            None,
            [
                ("App Store", "https://apps.apple.com/us/app/keysong/id6804326066", True),
                ("Play in the browser", "https://analogarcade.net/write-notes/", True),
                ("Gumroad zip", "https://analogquantum.gumroad.com/l/writenotes", True),
            ],
        ),
        product_card(
            "Card Check",
            "/assets/img/apps/cardcheck.png",
            "Card Check icon",
            [("Web", "")],
            "Snap 11 guided photos of a trading card and get an AI condition estimate — before you pay to have it graded.",
            "Photos are cropped to the card. You can save cards to My Cards if you sign in first; a check without an account is not added later. No price is shown on the live page. On an iPhone, open it in Safari and add it to the Home Screen.",
            "This is a pre-grade estimate from photos. It is not a professional grade.",
            [("Open Card Check", "https://cards.analogarcade.net/", True)],
        ),
    ]
)


HOME_JSONLD = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "PLJA Corp",
  "url": "{SITE_ORIGIN}/",
  "founder": {{"@type": "Person", "name": "Peter De Paola"}},
  "description": "The company name Pete De Paola uses for the apps he makes. A solo maker of local-first, one-time-price apps.",
  "sameAs": [
    "https://x.com/PLJA_AI",
    "https://analogarcade.net/",
    "https://apps.apple.com/us/developer/peter-de-paola/id6804326068"
  ]
}}
</script>
"""
# JSON-LD is a script; CSP script-src 'none' would block it from executing, but JSON-LD
# does not need to execute. To keep a strict CSP, put JSON-LD as a file or allow
# 'unsafe-inline' for this page only. We'll allow nothing and skip executed JS;
# crawlers still parse JSON-LD in the HTML even when CSP forbids script execution
# in browsers. Keep it in the body.


PAGES: dict[str, tuple[str, str, str, str]] = {}

FILTER_JS = """<script>
(function(){
  var chips = [].slice.call(document.querySelectorAll('.filters .chip'));
  var cards = [].slice.call(document.querySelectorAll('.grid.products .card'));
  var st = document.getElementById('filter-status');
  chips.forEach(function(c){ c.addEventListener('click', function(){
    var f = c.dataset.f, n = 0;
    chips.forEach(function(o){ o.setAttribute('aria-pressed', o === c ? 'true' : 'false'); });
    cards.forEach(function(card){ var on = f === 'all' || (' ' + card.dataset.tags + ' ').indexOf(' ' + f + ' ') >= 0; card.hidden = !on; if (on) n++; });
    if (st) st.textContent = n + (n === 1 ? ' app' : ' apps') + ' shown';
  }); });
})();
</script>"""

PULSE_JS = """<script>
(function(){
  var box = document.getElementById('pulse'), list = document.getElementById('pulse-list'), when = document.getElementById('pulse-when');
  if (!box || !window.fetch) return;
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function get(u){ return fetch(u, {cache:'no-store'}).then(function(r){ return r.ok ? r.json() : null; }).catch(function(){ return null; }); }
  Promise.all([get('/live/board.json'), get('https://raw.githubusercontent.com/Pdee1077/plja-corp/live-data/board.json?t=' + Date.now())]).then(function(p){
    var d = p[1] || p[0];
    if (p[0] && p[1] && new Date(p[0].updated) > new Date(p[1].updated)) d = p[0];
    if (!d || !d.rows || !d.rows.length) return;
    var rows = d.rows.filter(function(r){ return r.group === 'abnormal'; });
    rows.sort(function(a, b){ return (b.st_x_normal || b.x24 || 0) - (a.st_x_normal || a.x24 || 0); });
    list.innerHTML = rows.slice(0, 3).map(function(r){
      var x = r.st_x_normal != null ? r.st_x_normal : r.x24;
      return '<li><span class="sym">' + esc(r.sym) + '</span><span class="lbl">' + esc(r.name || '') + '</span><span class="x">' + (x != null ? esc(Number(x).toFixed(1)) + '×' : '–') + '</span></li>';
    }).join('');
    when.textContent = 'Snapshot ' + (d.updated_et || '');
    box.hidden = false;
  });
})();
</script>"""



def _board_top(n: int = 3) -> tuple[list[dict], str]:
    """Top abnormal names from the bundled or live-data board, for a no-JS fallback."""
    import json, subprocess
    board = None
    try:
        raw = subprocess.check_output(["git", "show", "origin/live-data:board.json"], cwd=ROOT, stderr=subprocess.DEVNULL)
        board = json.loads(raw)
    except Exception:
        path = PUBLIC / "live" / "board.json"
        if path.exists():
            board = json.loads(path.read_text(encoding="utf-8"))
    if not board or not board.get("rows"):
        return [], ""
    rows = [r for r in board["rows"] if r.get("group") == "abnormal"]
    rows.sort(key=lambda r: (r.get("st_x_normal") or r.get("x24") or 0), reverse=True)
    return rows[:n], str(board.get("updated_et") or "")


def pulse_fallback_html() -> tuple[str, str]:
    rows, when = _board_top(3)
    if not rows:
        return ""
    lis = []
    for r in rows:
        x = r.get("st_x_normal")
        if x is None:
            x = r.get("x24")
        xv = f"{float(x):.1f}×" if x is not None else "–"
        name = (r.get("name") or "").replace("&", "&amp;").replace("<", "&lt;")
        sym = (r.get("sym") or "").replace("&", "&amp;").replace("<", "&lt;")
        lis.append(f'<li><span class="sym">{sym}</span><span class="lbl">{name}</span><span class="x">{xv}</span></li>')
    return "".join(lis), when


def pages() -> dict[str, str]:
    I = theme.ICONS
    pulse_lis, pulse_when = pulse_fallback_html()
    home_body = f"""
    {HOME_JSONLD}
    <section class="hero">
      <div class="wrap">
        <div class="hero-grid">
        <p class="kicker rise">Market Chatter · a free research room</p>
        <h1 class="rise d1">What the internet is <em>talking about</em>, versus its usual chatter.</h1>
        <aside class="surface pulse hero-pulse rise d2" id="pulse">
          <div class="pulse-head"><strong>Loudest names right now</strong><span id="pulse-when">{"Snapshot " + pulse_when if pulse_when else ""}</span></div>
          <ul class="pulse-list" id="pulse-list">{pulse_lis}</ul>
          <p class="pulse-head">Talk vs. its own normal. A lead to check, not a fact, and not investment advice.</p>
          <a class="go" href="/chatter/">Open the full board →</a>
        </aside>
        <div class="hero-more rise d3">
        <p class="lede">Today&rsquo;s scan and a live board, in one place. A number like 8× means talk is louder than that name&rsquo;s own recent normal &mdash; a lead to check, not a fact. <strong>Research and education only. Not investment advice.</strong></p>
        <div class="actions">
          <a class="btn btn-primary" href="/chatter/">Open Market Chatter <span class="arr" aria-hidden="true">→</span></a>
          <a class="btn btn-ghost" href="/products/">See the five apps</a>
        </div>
        </div>
        </div>
        <div class="doors">
          <a class="door featured" href="/chatter/">
            <span class="ico">{I["pulse"]}</span>
            <strong>Market Chatter</strong>
            <span>Today&rsquo;s scan and a live board of what people are talking about, versus each name&rsquo;s usual chatter. Research, not advice.</span>
            <span class="go">Enter the room →</span>
          </a>
          <a class="door" href="/products/">
            <span class="ico">{I["apps"]}</span>
            <strong>Apps</strong>
            <span>House Binder, House Radar, Local Mass Finder, Keysong and Card Check. Web, iPhone, iPad and Mac.</span>
            <span class="go">Browse the apps →</span>
          </a>
          <a class="door" href="https://analogarcade.net/?utm_source=plja_hub" rel="noopener noreferrer">
            <span class="ico">{I["sunrise"]}</span>
            <strong>Analog Arcade</strong>
            <span>Our studio&rsquo;s public shop: free games, family tools, and the newest launches like Kept and Overhead.</span>
            <span class="go">Visit the shop →</span>
          </a>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <h2>The apps</h2>
          <a href="/products/">Compare all five →</a>
        </div>
        <ul class="trust" aria-label="How these are made">
          <li>{I["check"]} No subscriptions</li>
          <li>{I["check"]} No ads or tracking on this site</li>
          <li>{I["check"]} Local-first where it can be</li>
          <li>{I["check"]} Made and shipped by one person</li>
        </ul>
        <div class="grid products">
          {CARDS}
        </div>
      </div>
    </section>
    """

    products_body = f"""
    <article class="prose">
      <div class="wrap">
        <p class="kicker">Products</p>
        <h1>Five live products</h1>
        <p class="lede">This list is only the finished set for this draft: House Binder, House Radar, Local Mass Finder, Keysong and Card Check. Overhead and Vanish Cam are not included. Prices, versions and wording were checked on the live pages and the US App Store on 22 November 2026, America/New_York.</p>
      </div>
    </article>
    <section class="section" style="padding-top:0">
      <div class="wrap">
        <div class="grid products">{CARDS}</div>
      </div>
    </section>
    """
    # Wait, I used an inline style on section - avoid for CSP of style-src 'self' only.
    # I'll use a class instead. Let me fix after - I'll add .section.tight { padding-top: 0 }

    about_body = """
    <article class="prose">
      <div class="narrow">
        <p class="kicker">About</p>
        <h1>A solo maker, under one company name.</h1>
        <p>Pete De Paola builds small apps and ships them himself. <strong>PLJA Corp</strong> is the company name he uses for that work. It matches his main X account, <a href="https://x.com/PLJA_AI">@PLJA_AI</a>. The public shop people already know is <a href="https://analogarcade.net/">Analog Arcade</a>.</p>
        <p>The idea is simple: local-first where the product can work that way, and a one-time price when a product is sold. House Radar is $2.99 once on the App Store, with no subscription and no in-app purchases. Local Mass Finder and Keysong are free. House Binder is described as free on its live sign-in page. Card Check shows no price on its live page.</p>
        <p>Where a product can run without an account, it says so. Keysong and the Local Mass Finder app need no account. House Binder is private to your sign-in. Card Check can be used without an account, but a check is only saved to My Cards if you sign in first.</p>
        <h2>What this draft does not claim</h2>
        <p>This site does not claim that PLJA Corp has been filed as a legal entity. That still needs to be confirmed. On the App Store, the seller name today is Peter De Paola, enrolled as an individual. Showing PLJA Corp as the seller would take a later change, and only after a legal entity and the other steps Apple requires are in place.</p>
        <p>Pete is the only maker behind these five products.</p>
        <div class="actions">
          <a class="btn btn-primary" href="/contact/">Contact</a>
          <a class="btn btn-ghost" href="/products/">See the products</a>
        </div>
      </div>
    </article>
    """

    contact_body = """
    <article class="prose">
      <div class="narrow">
        <p class="kicker">Contact</p>
        <h1>How to reach us.</h1>
        <div class="flag">
          <p><strong>Company email is not published on this draft.</strong> A public PLJA Corp address still needs Pete’s yes before it goes on this page. This is a placeholder, not a working company mailbox. Do not assume a guess such as info@ or hello@ is monitored.</p>
        </div>
        <p>Until a company address is approved, the surest way to get help with a specific product is the support address already shown on that product’s own site. Those addresses are listed on the <a href="/support/">support page</a>.</p>
        <p>For press or a general question, wait for a confirmed company address, or use the support address for the product you are writing about.</p>
        <h2>Other public places</h2>
        <ul>
          <li>X: <a href="https://x.com/PLJA_AI">@PLJA_AI</a></li>
          <li>Shop: <a href="https://analogarcade.net/">analogarcade.net</a></li>
          <li>App Store: <a href="https://apps.apple.com/us/developer/peter-de-paola/id6804326068">Peter De Paola</a></li>
        </ul>
      </div>
    </article>
    """

    privacy_body = """
    <article class="prose">
      <div class="narrow">
        <p class="kicker">Privacy</p>
        <h1>Privacy on this website.</h1>
        <p>This page covers the PLJA Corp company website only — the pages you are reading now. It does not replace the privacy page of each product.</p>
        <h2>What this site collects</h2>
        <p>This website is a static site. It does not use accounts, cookies, or analytics. It does not run advertising. It does not have a contact form that sends information to our servers. If you open a mailto link on your own device, that uses your own email app.</p>
        <p>We do not collect personal information through this website itself. Ordinary web logs may be kept by the host (Cloudflare) when a page is requested, as they are for most sites. This draft does not add any extra tracking on top of that.</p>
        <h2>Product apps and sites</h2>
        <p>Each product has its own privacy page, and that is the one that applies when you use that product:</p>
        <ul>
          <li>House Binder — <a href="https://binder.analogarcade.net/privacy">Privacy</a></li>
          <li>House Radar — <a href="https://analogarcade.net/houseradar/privacy/">Privacy</a></li>
          <li>Local Mass Finder — <a href="https://church.analogarcade.net/privacy">Privacy</a></li>
          <li>Keysong — <a href="https://analogarcade.net/write-notes/privacy/">Privacy</a></li>
          <li>Card Check — <a href="https://cards.analogarcade.net/privacy">Privacy</a></li>
        </ul>
        <h2>If you email us</h2>
        <p>If you write to a product support address, that message is handled for that product. A company address for PLJA Corp has not been published on this draft yet.</p>
        <p>Last updated 22 November 2026, America/New_York.</p>
      </div>
    </article>
    """

    support_body = """
    <article class="prose">
      <div class="narrow">
        <p class="kicker">Support</p>
        <h1>Get help with a product.</h1>
        <p>This page is the company support entry for App Store listings and for anyone who lands here first. For the fastest help, use the address or page that already belongs to the product.</p>
        <div class="flag">
          <p><strong>There is no general company inbox on this draft.</strong> A shared PLJA Corp email still needs Pete’s yes. The addresses below are the ones already published on the live product sites, checked 22 November 2026, America/New_York.</p>
        </div>
        <ul class="contacts">
          <li>
            <strong>House Binder</strong>
            <span>Web app. Email <a href="mailto:binder@analogarcade.net">binder@analogarcade.net</a>. Support page: <a href="https://binder.analogarcade.net/support">binder.analogarcade.net/support</a>.</span>
          </li>
          <li>
            <strong>House Radar</strong>
            <span>iPhone and iPad app. Email <a href="mailto:radar@analogarcade.net">radar@analogarcade.net</a>. Guide: <a href="https://analogarcade.net/houseradar/">analogarcade.net/houseradar</a>.</span>
          </li>
          <li>
            <strong>Local Mass Finder</strong>
            <span>Web app and free iPhone and Mac app. Email <a href="mailto:church@analogarcade.net">church@analogarcade.net</a>. Support page: <a href="https://church.analogarcade.net/support">church.analogarcade.net/support</a>.</span>
          </li>
          <li>
            <strong>Keysong</strong>
            <span>iPhone, iPad and Mac app, plus a browser preview. Email <a href="mailto:keysong@analogarcade.net">keysong@analogarcade.net</a>.</span>
          </li>
          <li>
            <strong>Card Check</strong>
            <span>Web app. The live site has a privacy page at <a href="https://cards.analogarcade.net/privacy">cards.analogarcade.net/privacy</a>. A dedicated /support URL was not on the site when this draft was checked (it returned 404). Use the product site if you need help, until a company address is approved.</span>
          </li>
        </ul>
        <p>If something is broken on this company website, say so through the support address of the product you were trying to reach, and mention the PLJA Corp preview, until a company inbox is published.</p>
      </div>
    </article>
    """

    # Fix products_body inline style
    products_body = f"""
    <article class="prose tight-bottom">
      <div class="wrap">
        <p class="kicker">Apps</p>
        <h1>Five live apps</h1>
        <p class="lede">The finished set: House Binder, House Radar, Local Mass Finder, Keysong and Card Check. Prices, versions and wording were checked on the live pages and the US App Store on 22 November 2026, America/New_York.</p>
      </div>
    </article>
    <section class="section tight-top">
      <div class="wrap">
        <div class="filters" role="group" aria-label="Filter apps">
          <button class="chip" type="button" data-f="all" aria-pressed="true">All <span class="ct">5</span></button>
          <button class="chip" type="button" data-f="free" aria-pressed="false">Free</button>
          <button class="chip" type="button" data-f="iphone" aria-pressed="false">iPhone &amp; iPad</button>
          <button class="chip" type="button" data-f="mac" aria-pressed="false">Mac</button>
          <button class="chip" type="button" data-f="web" aria-pressed="false">Web</button>
        </div>
        <p class="sr-only" id="filter-status" role="status" aria-live="polite"></p>
        <div class="grid products">{CARDS}</div>
      </div>
    </section>
    """

    out = {
        "index.html": layout(
            "PLJA Corp — Market Chatter and local-first apps",
            "Market Chatter: what the internet is talking about versus its usual chatter, plus the apps PLJA Corp ships. Research and education only. Not investment advice.",
            "/",
            home_body,
            preload_mono=True,
        ),
        "products/index.html": layout(
            "Products — PLJA Corp",
            "House Binder, House Radar, Local Mass Finder, Keysong and Card Check — the finished, live products from PLJA Corp.",
            "/products/",
            products_body,
            scripts=FILTER_JS,
        ),
        "about/index.html": layout(
            "About — PLJA Corp",
            "PLJA Corp is the company name Pete De Paola uses for his work. He is a solo maker. Analog Arcade is the public shop.",
            "/about/",
            about_body,
        ),
        "contact/index.html": layout(
            "Contact — PLJA Corp",
            "How to reach PLJA Corp. A company email is not published on this draft until Pete approves one.",
            "/contact/",
            contact_body,
        ),
        "privacy/index.html": layout(
            "Privacy — PLJA Corp",
            "The PLJA Corp company website is a static site. It does not use accounts, cookies or analytics. Product privacy pages are linked here.",
            "/privacy/",
            privacy_body,
        ),
        "support/index.html": layout(
            "Support — PLJA Corp",
            "Get help with House Binder, House Radar, Local Mass Finder, Keysong or Card Check. Product support addresses already on the live sites are listed here.",
            "/support/",
            support_body,
        ),
    }

    not_found = layout(
        "Page not found — PLJA Corp",
        "That page is not on the PLJA Corp site.",
        "/404",
        """
        <article class="prose">
          <div class="narrow">
            <p class="kicker">404</p>
            <h1>That page is not here.</h1>
            <p>The link may be old, or this first-draft site may not have that path yet.</p>
            <div class="actions">
              <a class="btn btn-primary" href="/">Go to the home page</a>
              <a class="btn btn-ghost" href="/chatter/">Open Market Chatter</a>
              <a class="btn btn-ghost" href="/products/">See the products</a>
            </div>
          </div>
        </article>
        """,
    )
    out["404.html"] = not_found
    return out


HEADERS = """# Security and cache headers for the preview site.
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; img-src 'self'; style-src 'self'; font-src 'self'; script-src 'unsafe-inline'; connect-src 'self' https://raw.githubusercontent.com; base-uri 'self'; form-action 'none'; frame-ancestors 'none'
  Cache-Control: public, max-age=300

/assets/*
  ! Cache-Control
  Cache-Control: public, max-age=31536000, immutable

# The live board and its bundled snapshot go stale fast.
/live/*
  ! Cache-Control
  Cache-Control: public, max-age=60
"""

ROBOTS = f"""User-agent: *
Allow: /daily/
Allow: /assets/
Disallow: /

Sitemap: {SITE_ORIGIN}/sitemap.xml
"""

SITEMAP = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{SITE_ORIGIN}/daily/</loc></url>
  <url><loc>{SITE_ORIGIN}/daily/2026-11-25/</loc></url>
</urlset>
"""


def write_static() -> None:
    css_dir = ASSETS / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    # add tight helpers
    css = CSS + """
.prose.tight-bottom { padding-bottom: 0.5rem; }
.section.tight-top { padding-top: 0; }
.section .trust { margin: 0 0 1.4rem; }
"""
    (css_dir / "site.css").write_text(css, encoding="utf-8")  # legacy, kept for old cached pages
    theme.write_css(PUBLIC)
    (PUBLIC / "_headers").write_text(HEADERS, encoding="utf-8")
    (PUBLIC / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    (PUBLIC / "sitemap.xml").write_text(SITEMAP, encoding="utf-8")
    for rel, html in pages().items():
        path = PUBLIC / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        print("wrote", rel, path.stat().st_size)

    # Public Daily Scan pages. Run last so /daily/, robots.txt and sitemap.xml
    # are not overwritten by the company-site defaults above.
    import importlib.util
    daily_path = ROOT / "scripts" / "build_daily.py"
    spec = importlib.util.spec_from_file_location("build_daily", daily_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(mod)
    mod.main()

    live_path = ROOT / "scripts" / "build_live.py"
    live_spec = importlib.util.spec_from_file_location("build_live", live_path)
    live_mod = importlib.util.module_from_spec(live_spec)
    assert live_spec is not None and live_spec.loader is not None
    live_spec.loader.exec_module(live_mod)
    live_mod.main()

    chatter_spec = importlib.util.spec_from_file_location("build_chatter", ROOT / "scripts" / "build_chatter.py")
    chatter_mod = importlib.util.module_from_spec(chatter_spec)
    assert chatter_spec is not None and chatter_spec.loader is not None
    chatter_spec.loader.exec_module(chatter_mod)
    chatter_mod.main()


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    subset_fonts()
    write_mark()
    make_og()
    prepare_app_icons()
    write_static()
    print("done")


if __name__ == "__main__":
    main()

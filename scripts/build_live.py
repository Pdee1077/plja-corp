#!/usr/bin/env python3
"""Build the public PLJA Live Scanner page into public/live/. No personal names."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SITE = "https://plja-corp.pages.dev"
VERSION = "2026.11.25.2"
PUBLISHED = "Wednesday, Nov 25, 2026, 10:20 AM ET"
YEAR = "2026"
TITLE = "PLJA Live Scanner — chatter vs. normal"
DESC = (
    "A live board of names being talked about far more than usual, with price moves "
    "and a NO NEWS flag. Research and education, not investment advice."
)
UTM = "utm_source=plja_live"
REMOTE_JSON = "https://raw.githubusercontent.com/Pdee1077/plja-corp/live-data/board.json"

APPS = [
    ("Analog Arcade", "The shop for the apps, tools and games.", f"https://analogarcade.net/?{UTM}"),
    ("Local Mass Finder", "Nearby Mass times in the browser.", f"https://church.analogarcade.net/?{UTM}"),
    ("Overhead", "Point your phone at the night sky.", f"https://sky.analogarcade.net/?{UTM}"),
    ("Kept", "A private page for family stories.", f"https://kept.analogarcade.net/?{UTM}"),
    ("Atlas Kitchen", "Meal plans with local grocery prices.", f"https://kitchen.analogarcade.net/?{UTM}"),
    ("House Binder", "Photograph an appliance, get the manual.", f"https://binder.analogarcade.net/?{UTM}"),
    ("Keysong", "Watch a song play itself in the browser.", f"https://analogarcade.net/write-notes/?{UTM}"),
]


def arcade_section() -> str:
    items = "\n".join(
        f'          <li><a href="{url}">{name}</a> — {blurb}</li>'
        for name, blurb, url in APPS
    )
    return f"""
    <section class="arcade" aria-labelledby="arcade-heading">
      <div class="wrap">
        <p class="kicker">Also from Analog Arcade</p>
        <h2 id="arcade-heading">See the rest of the shop</h2>
        <p>This live board is one free page from <a href="https://analogarcade.net/?{UTM}">Analog Arcade</a>. The same shop also makes apps, tools and games — some free, some a one-time price, no feed and no ads required to try them.</p>
        <ul class="arcade-list">
{items}
        </ul>
      </div>
    </section>"""


def nav(current: str) -> str:
    links = [
        ("/products/", "Products"),
        ("/daily/", "Daily"),
        ("/live/", "Live"),
        ("/about/", "About"),
        ("/contact/", "Contact"),
        ("/support/", "Support"),
    ]

    def item(href: str, label: str) -> str:
        on = href == current or (href == "/daily/" and current.startswith("/daily/")) or (
            href == "/live/" and current.startswith("/live/")
        )
        cur = ' aria-current="page"' if on else ""
        return f'<a href="{href}"{cur}>{label}</a>'

    items = "".join(item(h, l) for h, l in links)
    return f"""
    <nav class="nav-wide" aria-label="Primary">{items}</nav>
    <nav class="mobile" aria-label="Primary">
      <details>
        <summary>Menu</summary>
        <div class="panel">{items}</div>
      </details>
    </nav>"""


CSS = """/* Live Scanner */
.scan { padding-bottom: 1.5rem; }
.scan .wrap { max-width: 56rem; }
.scan h1 { font-family: var(--serif); font-weight: 600; font-size: clamp(2rem, 5vw, 2.8rem); line-height: 1.15; margin: 0 0 0.7rem; }
.stamp { font-size: 0.9rem; color: var(--mute); margin: 0 0 0.4rem; }
.fresh { font-size: 0.95rem; margin: 0 0 1.2rem; }
.fresh.stale { color: var(--copper-deep); }
.callout {
  background: var(--paper-deep);
  border-left: 4px solid var(--copper);
  padding: 0.9rem 1.1rem;
  margin: 0 0 1.8rem;
  border-radius: 0 0.6rem 0.6rem 0;
}
.callout p { margin: 0; }
.table-wrap { overflow-x: auto; margin: 0 0 1.2rem; -webkit-overflow-scrolling: touch; }
.scan table { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
.scan th, .scan td { text-align: left; padding: 0.55rem 0.65rem; border-bottom: 1px solid var(--line); vertical-align: top; }
.scan th { font-weight: 500; color: var(--mute); font-size: 0.8rem; letter-spacing: 0.02em; white-space: nowrap; }
.scan td.r, .scan th.r { text-align: right; font-variant-numeric: tabular-nums; }
.scan .nm { display: block; color: var(--mute); font-size: 0.82rem; }
.scan tr.only td { background: #f6ebd3; }
.scan tr.nonews td { background: #f3e4dc; }
.scan .up { color: var(--forest); }
.scan .dn { color: var(--copper-deep); }
.badge { display: inline-block; font-size: 0.72rem; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; padding: 0.12rem 0.4rem; border-radius: 999px; background: var(--copper); color: #fffdf8; }
.group-row td { font-weight: 500; padding-top: 1.1rem; border-bottom: 2px solid var(--ink); background: var(--paper); }
.empty { color: var(--mute); }
.legend { color: var(--mute); font-size: 0.95rem; }
.legend strong { color: var(--ink); font-weight: 500; }
.arcade {
  background: var(--paper-deep);
  border-top: 1px solid var(--line);
  padding: 2.2rem 0 2.6rem;
}
.arcade h2 { font-family: var(--serif); font-weight: 600; margin: 0 0 0.7rem; }
.arcade-list { list-style: none; padding: 0; margin: 1.1rem 0 0; display: grid; gap: 0.7rem; }
@media (min-width: 720px) {
  .arcade-list { grid-template-columns: 1fr 1fr; }
}
.arcade-list li { background: var(--card); border: 1px solid var(--line); border-radius: 0.85rem; padding: 0.85rem 1rem; box-shadow: var(--shadow); }
.arcade-list a { font-weight: 500; color: var(--ink); text-decoration: none; }
.arcade-list a:hover { color: var(--copper-deep); text-decoration: underline; }
"""

JS = r"""
(function(){
  var REMOTE = "REMOTE_JSON";
  var statusEl = document.getElementById('fresh');
  var stampEl = document.getElementById('data-stamp');
  var bodyEl = document.getElementById('board-body');

  function esc(s){
    return String(s == null ? '' : s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function fmtX(v){ return (v == null || v === '') ? '–' : Number(v).toFixed(1) + '×'; }
  function fmtN(v){ return (v == null || v === '') ? '–' : String(v); }
  function fmtPct(v){
    if (v == null || v === '') return '–';
    var n = Number(v);
    var cls = n > 0 ? 'up' : (n < 0 ? 'dn' : '');
    var sign = n > 0 ? '+' : '';
    return '<span class="'+cls+'">'+sign+n.toFixed(1)+'%</span>';
  }
  function ageText(iso){
    if (!iso) return '';
    var mins = Math.max(0, Math.round((Date.now() - new Date(iso).getTime())/60000));
    if (mins < 1) return 'Updated just now.';
    if (mins === 1) return 'Updated 1 minute ago.';
    if (mins < 60) return 'Updated '+mins+' minutes ago.';
    var hrs = Math.round(mins/60);
    return 'Updated '+hrs+' hour'+(hrs===1?'':'s')+' ago.';
  }
  function render(data){
    if (!data || !Array.isArray(data.rows)) {
      bodyEl.innerHTML = '<tr><td colspan="8" class="empty">The live snapshot could not be loaded. The morning scan is still on the Daily page.</td></tr>';
      return;
    }
    if (stampEl) stampEl.textContent = 'Data: ' + (data.updated_et || data.updated || '') + (data.version ? ' · Snapshot ' + data.version : '');
    if (statusEl){
      statusEl.textContent = ageText(data.updated);
      var mins = data.updated ? Math.max(0, Math.round((Date.now() - new Date(data.updated).getTime())/60000)) : 999;
      statusEl.className = 'fresh' + (mins > 25 ? ' stale' : '');
      if (mins > 25) statusEl.textContent += ' A weekday refresh is set for every 15 minutes; GitHub can delay those runs.';
    }
    var groups = {abnormal: 'Abnormal talk right now, whether or not the price has moved', faint: 'Faint or fading: one source only, or a smaller jump'};
    var html = '';
    var last = '';
    data.rows.forEach(function(r){
      if (r.group !== last){
        last = r.group;
        html += '<tr class="group-row"><td colspan="8">'+esc(groups[r.group] || r.group)+'</td></tr>';
      }
      var cls = [];
      if (r.kind === 'talk only') cls.push('only');
      if (r.nonews) cls.push('nonews');
      var flags = (r.flags || []).map(esc).join('; ');
      var news = r.nonews ? '<span class="badge">No news</span>' : fmtN(r.n24);
      html += '<tr class="'+cls.join(' ')+'">'
        + '<td><strong>'+esc(r.sym)+'</strong>'+(r.name?'<span class="nm">'+esc(r.name)+'</span>':'')+'</td>'
        + '<td>'+flags+'</td>'
        + '<td class="r">'+fmtN(r.reddit)+'</td>'
        + '<td class="r">'+fmtX(r.x24)+'</td>'
        + '<td class="r">'+(r.st_x_normal != null ? fmtX(r.st_x_normal) : (r.st_rank != null ? '#'+esc(r.st_rank) : '–'))+'</td>'
        + '<td class="r">'+fmtPct(r.d1)+'</td>'
        + '<td class="r">'+news+'</td>'
        + '<td>'+esc(r.kind || '')+'</td>'
        + '</tr>';
    });
    bodyEl.innerHTML = html || '<tr><td colspan="8" class="empty">Nothing looks abnormal in this snapshot.</td></tr>';
  }
  function boot(){
    var local = fetch('/live/board.json', {cache:'no-store'}).then(function(r){ return r.ok ? r.json() : null; }).catch(function(){ return null; });
    var remote = fetch(REMOTE + '?t=' + Date.now(), {cache:'no-store'}).then(function(r){ return r.ok ? r.json() : null; }).catch(function(){ return null; });
    Promise.all([local, remote]).then(function(pair){
      var a = pair[0], b = pair[1], pick = b || a;
      if (a && b && a.updated && b.updated && new Date(a.updated) > new Date(b.updated)) pick = a;
      render(pick);
    });
  }
  boot();
  setInterval(boot, 15 * 60 * 1000);
})();
""".replace("REMOTE_JSON", REMOTE_JSON)


def write_og() -> None:
    w, h = 1200, 630
    paper = (244, 239, 230)
    ink = (28, 25, 21)
    mute = (92, 86, 78)
    copper = (179, 90, 50)
    img = Image.new("RGB", (w, h), paper)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, 10], fill=copper)
    fra_path = Path("/usr/share/fonts/truetype/sand-box/google/Fraunces/Fraunces-VariableFont_SOFT,WONK,opsz,wght.ttf")
    plex_path = Path("/usr/share/fonts/truetype/sand-box/google/IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf")
    if not plex_path.exists():
        plex_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not fra_path.exists():
        fra_path = plex_path
    title = ImageFont.truetype(str(fra_path), 76)
    sub = ImageFont.truetype(str(plex_path), 36)
    small = ImageFont.truetype(str(plex_path), 26)
    draw.text((80, 150), "PLJA Live Scanner", font=title, fill=ink)
    draw.text((80, 260), "Chatter vs. normal", font=sub, fill=ink)
    draw.text((80, 330), "Talk jumps, price moves, and a NO NEWS flag", font=sub, fill=mute)
    draw.text((80, 500), "Research and education only. Not investment advice.", font=small, fill=mute)
    out = PUBLIC / "assets" / "img" / "live-og.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)


def layout(body: str) -> str:
    canonical = f"{SITE}/live/"
    og = f"{SITE}/assets/img/live-og.png"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{TITLE}</title>
  <meta name="description" content="{DESC}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{canonical}">
  <meta name="theme-color" content="#f4efe6">
  <meta name="color-scheme" content="light">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="PLJA Corp">
  <meta property="og:title" content="{TITLE}">
  <meta property="og:description" content="{DESC}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{TITLE}">
  <meta name="twitter:description" content="{DESC}">
  <meta name="twitter:image" content="{og}">
  <link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/assets/img/favicon-32.png" type="image/png" sizes="32x32">
  <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
  <link rel="preload" href="/assets/fonts/ibm-plex-sans-regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/fraunces-semibold.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/css/site.css">
  <link rel="stylesheet" href="/assets/css/daily.css">
  <link rel="stylesheet" href="/assets/css/live.css">
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="bar">
      <a class="brand" href="/">
        <img src="/assets/img/mark.svg" width="34" height="34" alt="">
        <span class="name">PLJA<span class="corp">CORP</span></span>
      </a>
      {nav("/live/")}
    </div>
  </header>
  <main id="main">
    {body}
  </main>
  {arcade_section()}
  <footer class="site-footer">
    <div class="wrap foot-grid">
      <div>
        <a class="brand" href="/">
          <img src="/assets/img/mark.svg" width="34" height="34" alt="">
          <span class="name">PLJA<span class="corp">CORP</span></span>
        </a>
        <p>A public live board of chatter vs. normal, and a link back to the Analog Arcade shop.</p>
      </div>
      <div>
        <h2>Site</h2>
        <nav aria-label="Footer">
          <a href="/live/">Live Scanner</a>
          <a href="/daily/">Daily Scan</a>
          <a href="/products/">Products</a>
          <a href="/privacy/">Privacy</a>
        </nav>
      </div>
      <div>
        <h2>Elsewhere</h2>
        <nav aria-label="Elsewhere">
          <a href="https://analogarcade.net/?{UTM}">Analog Arcade</a>
          <a href="https://x.com/PLJA_AI">@PLJA_AI on X</a>
        </nav>
      </div>
    </div>
    <div class="wrap tiny">© {YEAR} PLJA Corp. Page version {VERSION}. Published {PUBLISHED}. Research and education only. Not investment advice.</div>
  </footer>
  <script>
{JS}
  </script>
</body>
</html>
"""


BODY = f"""
    <article class="prose scan">
      <div class="wrap">
        <p class="kicker">PLJA Live Scanner · @PLJA_AI</p>
        <h1>Chatter vs. normal</h1>
        <p class="lede">Names being talked about far more than their own usual level, with the price move beside them and a NO NEWS flag when talk jumps and the headline count does not.</p>
        <p class="stamp">Page version {VERSION} · Published {PUBLISHED}</p>
        <p class="stamp" id="data-stamp">Loading the latest snapshot…</p>
        <p class="fresh" id="fresh"></p>
        <div class="callout" role="note">
          <p><strong>Research and education only. Not investment advice.</strong> This is a snapshot of public talk counts and market prices. It is not a recommendation to buy, sell or hold anything, and it does not consider anyone's finances. PLJA Corp is not a broker-dealer or an investment adviser. Counts can be wrong or late. A place on this board is a lead to check, not a fact. Do your own research.</p>
        </div>
        <p>The morning write-up stays on the <a href="/daily/">Daily Scan</a>. This page is the live board. It tries to refresh every 15 minutes on weekdays through a free GitHub Action. GitHub can delay those runs. The private office copy of the scanner was not changed.</p>
        <div class="table-wrap" tabindex="0">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Why it is flagged</th>
                <th class="r">Reddit 24h</th>
                <th class="r">vs day before</th>
                <th class="r">StockTwits</th>
                <th class="r">Price</th>
                <th class="r">News 24h</th>
                <th>Talk vs price</th>
              </tr>
            </thead>
            <tbody id="board-body">
              <tr><td colspan="8" class="empty">Loading…</td></tr>
            </tbody>
          </table>
        </div>
        <p class="legend"><strong>Talk only</strong> (cream row) means the talk jumped and the price is quiet. <strong>NO NEWS</strong> means abnormal talk with two or fewer headlines counted for that ticker in the last 24 hours. StockTwits is shown as “vs its own 20-day normal” when we have it, otherwise as a trending rank. Reddit counts come from ApeWisdom and mostly reflect one forum. X is not counted. Nothing here is a prediction or a trade idea.</p>
      </div>
    </article>
"""


def write_robots() -> None:
    robots = f"""User-agent: *
Allow: /daily/
Allow: /live/
Allow: /assets/
Disallow: /

Sitemap: {SITE}/sitemap.xml
"""
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{SITE}/daily/</loc></url>
  <url><loc>{SITE}/daily/2026-11-25/</loc></url>
  <url><loc>{SITE}/live/</loc></url>
</urlset>
"""
    (PUBLIC / "robots.txt").write_text(robots, encoding="utf-8")
    (PUBLIC / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def write_headers() -> None:
    path = PUBLIC / "_headers"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    block = """
# Live scanner may fetch the latest snapshot from the public data branch.
/live/*
  Content-Security-Policy: default-src 'self'; img-src 'self'; style-src 'self'; font-src 'self'; script-src 'unsafe-inline'; connect-src 'self' https://raw.githubusercontent.com; base-uri 'self'; form-action 'none'; frame-ancestors 'none'
  Cache-Control: public, max-age=60
"""
    if "connect-src 'self' https://raw.githubusercontent.com" not in text:
        path.write_text(text.rstrip() + "\n" + block, encoding="utf-8")


def main() -> None:
    css = PUBLIC / "assets" / "css" / "live.css"
    css.parent.mkdir(parents=True, exist_ok=True)
    css.write_text(CSS, encoding="utf-8")
    write_og()
    dest = PUBLIC / "live" / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(layout(BODY), encoding="utf-8")
    write_robots()
    write_headers()
    print("wrote", dest, dest.stat().st_size)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the public PLJA Daily Scan pages into public/. No personal names."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SITE = "https://plja-corp.pages.dev"
VERSION = "2026.11.25.1"
PUBLISHED = "Wednesday, Nov 25, 2026, 10:05 AM ET"
YEAR = "2026"
OG_TITLE = "PLJA Daily Scan: Wednesday, Nov 25, 2026"
OG_DESC = (
    "Chatter vs. normal, odd moves and news flags from public market data. "
    "Research and education, not investment advice."
)
UTM = "utm_source=plja_daily"

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
        <p>This scan is one free page from <a href="https://analogarcade.net/?{UTM}">Analog Arcade</a>. The same shop also makes apps, tools and games — some free, some a one-time price, no feed and no ads required to try them.</p>
        <ul class="arcade-list">
{items}
        </ul>
      </div>
    </section>"""


def daily_nav(current: str) -> str:
    links = [
        ("/products/", "Products"),
        ("/daily/", "Daily"),
        ("/live/", "Live"),
        ("/about/", "About"),
        ("/contact/", "Contact"),
        ("/support/", "Support"),
    ]

    def item(href: str, label: str) -> str:
        on = href == current or (href == "/daily/" and current.startswith("/daily/")) or (href == "/live/" and current.startswith("/live/"))
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


def layout(title: str, description: str, path: str, body: str, og_image: str) -> str:
    canonical = SITE + path
    og = f"{SITE}{og_image}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{canonical}">
  <meta name="theme-color" content="#f4efe6">
  <meta name="color-scheme" content="light">
  <meta property="og:type" content="article">
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
  <link rel="preload" href="/assets/fonts/fraunces-semibold.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/css/site.css">
  <link rel="stylesheet" href="/assets/css/daily.css">
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="bar">
      <a class="brand" href="/">
        <img src="/assets/img/mark.svg" width="34" height="34" alt="">
        <span class="name">PLJA<span class="corp">CORP</span></span>
      </a>
      {daily_nav(path if path.endswith('/') else path + '/')}
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
        <p>A daily research log of public market data, and a link back to the Analog Arcade shop.</p>
      </div>
      <div>
        <h2>Site</h2>
        <nav aria-label="Footer">
          <a href="/daily/">Daily Scan</a>
          <a href="/live/">Live Scanner</a>
          <a href="/products/">Products</a>
          <a href="/about/">About</a>
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
    <div class="wrap tiny">© {YEAR} PLJA Corp. Version {VERSION}. Published {PUBLISHED}. Research and education only. Not investment advice.</div>
  </footer>
</body>
</html>
"""


DISCLAIMER = """    <div class="callout" role="note">
      <p><strong>Research and education only. Not investment advice.</strong> This is a summary of public market data and online chatter. It is not a recommendation to buy, sell or hold anything, and it does not consider anyone's finances. PLJA Corp is not a broker-dealer or an investment adviser. Prices and counts can be wrong or late. Do your own research.</p>
    </div>"""

STAMP = f'<p class="stamp">Version {VERSION} · Published {PUBLISHED}</p>'


ARTICLE = f"""
    <article class="prose scan">
      <div class="wrap">
        <p class="kicker">PLJA Daily Scan · @PLJA_AI</p>
        <h1>Wednesday, Nov 25, 2026</h1>
        <p class="lede">Chatter vs. normal, odd moves, and news flags. Data through Tuesday's close (Nov 24, 2026). Overnight section as of 7:00 AM ET Wednesday, before the open. Quotes before the open are thin and can change.</p>
        {STAMP}
        {DISCLAIMER}
        <p class="actions"><a class="btn btn-ghost" href="/live/">Open the live scanner</a></p>

        <h2>The short version</h2>
        <ol>
          <li><strong>Tuesday split in two.</strong> Chips fell hard (the SMH chip fund −7.3%) while the S&amp;P 500 fell only 0.5%, the Russell 2000 rose 0.6%, and staples (XLP) rose 1.7%.</li>
          <li><strong>Chatter spiked on a few names, and most of those had news.</strong> Dell's Reddit mentions rose 6.8× in a day (163 vs 24) with the stock down. Ambarella and Walmart also jumped. Nvidia's talk went the other way: 681 mentions vs 1,883 the day before (0.4×).</li>
          <li><strong>One name had loud talk and a quiet price: Apple.</strong> Mentions were 4.3× the day before (94 vs 22) and the stock moved +1.4%.</li>
          <li><strong>Overnight, the selling spread.</strong> Index futures were down (S&amp;P −1.6%, Nasdaq 100 −2.5%), the VIX was near 30, and Asian chip markets fell sharply.</li>
        </ol>

        <h2>1. Tuesday's close (Nov 24)</h2>
        <div class="table-wrap" tabindex="0">
        <table>
          <thead><tr><th>Market</th><th>Level</th><th>1 day</th></tr></thead>
          <tbody>
            <tr><td>S&amp;P 500</td><td>7,201</td><td>−0.5%</td></tr>
            <tr><td>Nasdaq</td><td>23,734</td><td>−1.5%</td></tr>
            <tr><td>Russell 2000</td><td>2,685</td><td>+0.6%</td></tr>
            <tr><td>SMH (chip fund)</td><td>426.75</td><td>−7.3%</td></tr>
            <tr><td>RSP (equal-weight S&amp;P fund)</td><td>213.96</td><td>+0.5%</td></tr>
            <tr><td>XLP (staples fund)</td><td>91.88</td><td>+1.7%</td></tr>
            <tr><td>VIX</td><td>26.36</td><td>−0.26 pt</td></tr>
            <tr><td>10-year Treasury yield</td><td>4.90%</td><td>−0.01 pt</td></tr>
            <tr><td>Junk bond spread (ICE BofA HY OAS, Nov 23)</td><td>3.63 pts</td><td>−0.13 pt</td></tr>
            <tr><td>Investment-grade spread (OAS, Nov 23)</td><td>0.97 pts</td><td>−0.01 pt</td></tr>
            <tr><td>US crude (WTI)</td><td>$82.05</td><td>+2.4%</td></tr>
            <tr><td>Bitcoin</td><td>$59,748</td><td>−2.4%</td></tr>
          </tbody>
        </table>
        </div>
        <p><strong>What stands out.</strong> Chip stocks fell 7.3% as a group while the equal-weight S&amp;P rose. That is a narrow, sector-specific move, not a broad one. Credit spreads narrowed on Monday's data, so the stress was not (yet) showing up in bonds.</p>
        <p><strong>Biggest Tuesday moves among the AI-linked names we track:</strong> CoreWeave −11.9%, Nebius −10.7%, AMD −8.9%, Nvidia −5.9%, Oracle −3.7%, Broadcom −4.0%.</p>
        <p class="note">No chart is included on this page. The figures above are written out so they can be checked against the sources listed at the end.</p>

        <h2>2. Chatter vs. normal</h2>
        <p>We count how often a name is mentioned on Reddit (24 hours vs the 24 hours before) and whether it newly appears on StockTwits' trending list. A jump is a lead to check, <strong>not</strong> a fact or a signal.</p>
        <p><strong>Talk and price both moved (usually there is news):</strong></p>
        <div class="table-wrap" tabindex="0">
        <table>
          <thead><tr><th>Name</th><th>Reddit mentions, 24h</th><th>Day before</th><th>Multiple</th><th>Tuesday move</th><th>Likely driver (from public headlines)</th></tr></thead>
          <tbody>
            <tr><td>Dell (DELL)</td><td>163</td><td>24</td><td>6.8×</td><td>−11.8%</td><td>Quarterly report after the close; indicated −8.2% before the open</td></tr>
            <tr><td>Ambarella (AMBA)</td><td>28</td><td>1</td><td>5.6×</td><td>−20.0%</td><td>Weak guidance; −35.9% before the open</td></tr>
            <tr><td>Micron (MU)</td><td>143</td><td>95</td><td>1.5×</td><td>−11.0%</td><td>Analyst downgrade headlines</td></tr>
            <tr><td>AMD</td><td>163</td><td>127</td><td>1.3×</td><td>−8.9%</td><td>Share-registration filing headlines</td></tr>
          </tbody>
        </table>
        </div>
        <p><strong>Talk jumped, price moved a little:</strong> Walmart (WMT): 31 vs 3 mentions (6.2×), +2.1%.</p>
        <p><strong>Talk only, price quiet (the interesting kind):</strong> Apple (AAPL): 94 vs 22 mentions (4.3×; its own recent median is 39), price +1.4%, near its 52-week high. Apple was the one large name with a talk jump and no clear news. Reading it as a signal would be a mistake. Crowds are often early, late, or wrong.</p>
        <p><strong>Talk faded:</strong> Nvidia (NVDA) still led Reddit with 681 mentions, but that is down from 1,883 the day before.</p>
        <p><strong>New on StockTwits' trending list (rank only):</strong> Dell (#1), Ambarella (#7), Micron (#5), AMD (#11), Nebius (#16), Bitcoin (#9), Broadcom (#23), TSMC (#18), Abercrombie &amp; Fitch (#14), Arm (#17), Schwab (#28), Deere (#8), Coinbase (#10).</p>
        <p><strong>Caveat on our own method.</strong> The chatter tracker only has 2 earlier days of its own history, so “vs. its own normal” is mostly “vs. yesterday” for now. It gets more reliable as the history grows. Some ticker symbols are ordinary words (IT, AM, NYT, CIA), and those are ignored.</p>

        <h2>3. Abnormal movers before the open</h2>
        <p>Rule: price $5+, about $20 million+ traded a day, a move of 5%+ and at least 3× the stock's own normal daily move. 5 of 269 stocks checked qualified at 7:00 AM ET.</p>
        <div class="table-wrap" tabindex="0">
        <table>
          <thead><tr><th>Stock</th><th>Premarket move</th><th>Times its normal day</th><th>What the headlines say</th></tr></thead>
          <tbody>
            <tr><td>Ambarella (AMBA)</td><td>−35.5%</td><td>7.5×</td><td>Guidance well below estimates</td></tr>
            <tr><td>Urban Outfitters (URBN)</td><td>−14.7%</td><td>6.7×</td><td>Sales miss; analyst downgrade</td></tr>
            <tr><td>Nutanix (NTNX)</td><td>−13.8%</td><td>5.8×</td><td>Analyst downgrade; CEO change</td></tr>
            <tr><td>Workday (WDAY)</td><td>−9.5%</td><td>4.0×</td><td>Earnings reaction</td></tr>
            <tr><td>Sandisk (SNDK)</td><td>−23.2%</td><td>4.0×</td><td>Sector selling; headlines do not name one cause</td></tr>
          </tbody>
        </table>
        </div>
        <p>All five have ordinary, explained news. We found no unexplained jump.</p>

        <h2>4. Overnight (as of 7:00 AM ET)</h2>
        <div class="table-wrap" tabindex="0">
        <table>
          <thead><tr><th></th><th>Move since Tuesday's 4 PM close</th></tr></thead>
          <tbody>
            <tr><td>S&amp;P 500 futures</td><td>−1.6%</td></tr>
            <tr><td>Nasdaq 100 futures</td><td>−2.5%</td></tr>
            <tr><td>VIX</td><td>26.4 to 30.3</td></tr>
            <tr><td>Bitcoin</td><td>−1.9%</td></tr>
            <tr><td>Gold / Silver / Copper</td><td>−0.2% / −1.0% / −1.5%</td></tr>
            <tr><td>Korea (Kospi)</td><td>−6.2%</td></tr>
            <tr><td>Taiwan</td><td>−4.8%</td></tr>
            <tr><td>Japan (Nikkei)</td><td>−2.8%</td></tr>
            <tr><td>Europe (Stoxx 50)</td><td>−0.3%</td></tr>
            <tr><td>India (Nifty)</td><td>+1.9%</td></tr>
          </tbody>
        </table>
        </div>
        <p><strong>Observation.</strong> Asia's chip-heavy markets fell the most while Europe was close to flat. The weakness is concentrated in semiconductor and AI-linked names, not everywhere.</p>

        <h2>5. What is on the calendar</h2>
        <ul>
          <li>8:30 AM ET: October PCE inflation, GDP, durable goods, jobless claims.</li>
          <li>Late morning: US 7-year Treasury auction.</li>
          <li>Thursday: US markets closed (Thanksgiving). Friday: stocks close at 1:00 PM ET.</li>
        </ul>

        <h2>Data sources</h2>
        <p>Market prices and changes: Yahoo Finance. Treasury yields, credit spreads and breakevens: Federal Reserve Bank of St. Louis (FRED). Reddit mention counts: ApeWisdom. Trending ranks: StockTwits (rank only). Headlines: public news search results (Yahoo Finance, Investing.com, Seeking Alpha, Benzinga and others); we link to headlines but do not copy articles. Moves and multiples are our own calculations.</p>

        <h2>About this scan</h2>
        <p>PLJA Corp (<a href="https://x.com/PLJA_AI">@PLJA_AI</a>) publishes this as a daily research log. It is built with AI tools (the analysis assistant runs on Claude, made by Anthropic) and the numbers are pulled automatically from the sources above. Errors happen. Tell us what we got wrong. Nothing here is a prediction, a trade idea, or personalized advice.</p>
        <p><em>Research and education only. Not investment advice.</em></p>
        {STAMP}
      </div>
    </article>
"""

INDEX = f"""
    <article class="prose scan">
      <div class="wrap">
        <p class="kicker">PLJA Daily Scan · @PLJA_AI</p>
        <h1>Chatter vs. normal</h1>
        <p class="lede">A free, public research log of odd moves, news flags, and names being talked about far more than usual. Built from public market data. Not a newsletter of trade ideas.</p>
        {STAMP}
        {DISCLAIMER}
        <p class="actions"><a class="btn btn-primary" href="/live/">Open the live scanner</a></p>

        <h2>Latest: Wednesday, Nov 25, 2026</h2>
        <p>Data through Tuesday's close (Nov 24). Overnight figures as of 7:00 AM ET Wednesday, before the open.</p>
        <ol>
          <li><strong>Tuesday split in two.</strong> The chip fund fell 7.3% while the S&amp;P 500 fell 0.5% and the equal-weight S&amp;P rose 0.5%.</li>
          <li><strong>Dell chatter jumped 6.8×</strong> in a day (163 Reddit mentions vs 24), with the stock down 11.8% after its quarterly report.</li>
          <li><strong>Apple was talk-only:</strong> mentions 4.3× the day before, price +1.4%.</li>
          <li><strong>Nvidia's talk faded</strong> to about 0.4× the day before, even though it still led the mention counts.</li>
          <li><strong>Overnight the selling spread</strong> to Asia: Korea −6.2%, Taiwan −4.8%, S&amp;P futures −1.6%.</li>
        </ol>
        <p class="actions">
          <a class="btn btn-primary" href="/daily/2026-11-25/">Read the full Nov 25 scan</a>
        </p>
        <p>New scans will be listed here as they are published. This page is version {VERSION}.</p>
      </div>
    </article>
"""

CSS = """/* Daily Scan — tables, disclaimer, Analog Arcade section. */
.scan { padding-bottom: 1.5rem; }
.scan .wrap { max-width: 46rem; }
.scan h1 { font-family: var(--serif); font-weight: 600; font-size: clamp(2rem, 5vw, 2.8rem); line-height: 1.15; margin: 0 0 0.7rem; }
.stamp { font-size: 0.9rem; color: var(--mute); margin: 0 0 1.2rem; }
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
.scan th, .scan td { text-align: left; padding: 0.5rem 0.65rem; border-bottom: 1px solid var(--line); vertical-align: top; }
.scan th { font-weight: 500; color: var(--mute); font-size: 0.82rem; letter-spacing: 0.02em; }
.scan .note { color: var(--mute); font-size: 0.95rem; }
.scan .actions { margin: 1.4rem 0 1.6rem; }
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


def write_og() -> Path:
    w, h = 1200, 630
    paper = (244, 239, 230)
    ink = (28, 25, 21)
    mute = (92, 86, 78)
    copper = (179, 90, 50)
    img = Image.new("RGB", (w, h), paper)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, 10], fill=copper)
    fra_path = Path(
        "/usr/share/fonts/truetype/sand-box/google/Fraunces/Fraunces-VariableFont_SOFT,WONK,opsz,wght.ttf"
    )
    plex_path = Path(
        "/usr/share/fonts/truetype/sand-box/google/IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf"
    )
    if not plex_path.exists():
        plex_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not fra_path.exists():
        fra_path = plex_path
    title = ImageFont.truetype(str(fra_path), 76)
    sub = ImageFont.truetype(str(plex_path), 36)
    small = ImageFont.truetype(str(plex_path), 26)
    draw.text((80, 150), "PLJA Daily Scan", font=title, fill=ink)
    draw.text((80, 260), "Wednesday, Nov 25, 2026", font=sub, fill=ink)
    draw.text((80, 330), "Chatter vs. normal · odd moves · news flags", font=sub, fill=mute)
    draw.text((80, 500), "Research and education only. Not investment advice.", font=small, fill=mute)
    out = PUBLIC / "assets" / "img" / "daily-og.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def write_robots_and_sitemap() -> None:
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


def main() -> None:
    css_path = PUBLIC / "assets" / "css" / "daily.css"
    css_path.parent.mkdir(parents=True, exist_ok=True)
    css_path.write_text(CSS, encoding="utf-8")
    og = write_og()
    og_path = "/assets/img/daily-og.png"
    dated = PUBLIC / "daily" / "2026-11-25" / "index.html"
    index = PUBLIC / "daily" / "index.html"
    dated.parent.mkdir(parents=True, exist_ok=True)
    dated.write_text(
        layout(OG_TITLE, OG_DESC, "/daily/2026-11-25/", ARTICLE, og_path),
        encoding="utf-8",
    )
    index.write_text(
        layout(
            "PLJA Daily Scan — chatter vs. normal",
            OG_DESC,
            "/daily/",
            INDEX,
            og_path,
        ),
        encoding="utf-8",
    )
    write_robots_and_sitemap()
    print("wrote", dated, dated.stat().st_size)
    print("wrote", index, index.stat().st_size)
    print("wrote", og, og.stat().st_size)
    print("version", VERSION, "published", PUBLISHED)


if __name__ == "__main__":
    main()

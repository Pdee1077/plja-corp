#!/usr/bin/env python3
"""Build the public PLJA Daily Scan pages into public/daily/. No personal names.

Each day is one entry in DAYS plus three HTML fragments in content/daily/:
  YYYY-MM-DD.short.html  the "short version" list shown in the summary card
  YYYY-MM-DD.index.html  the shorter list used on /daily/ for the latest day
  YYYY-MM-DD.body.html   the full write-up, one <h2> per section
To add a day: drop in the three files, add a DAYS entry at the top, rebuild.
"""
from __future__ import annotations

import calendar
import re
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CONTENT = ROOT / "content" / "daily"
SITE = theme.SITE
VERSION = theme.VERSION
UTM = "utm_source=plja_daily"
DESC = (
    "Chatter vs. normal, odd moves and news flags from public market data. "
    "Research and education, not investment advice."
)

# Newest first.
DAYS = [
    {
        "date": "2026-11-25",
        "label": "Wednesday, Nov 25, 2026",
        "headline": "Chips fell 7.3% while the broad market barely moved.",
        "data_note": "Data through Tuesday’s close (Nov 24, 2026). Overnight section as of 7:00 AM ET Wednesday, before the open. Quotes before the open are thin and can change.",
        "first_published": "Wed, Nov 25, 2026, 10:05 AM ET",
        "tiles": [
            ("S&amp;P 500", "7,201", "−0.5%", "down"),
            ("Nasdaq", "23,734", "−1.5%", "down"),
            ("SMH chip fund", "426.75", "−7.3%", "down"),
            ("Russell 2000", "2,685", "+0.6%", "up"),
            ("VIX", "26.36", "−0.26 pt", ""),
            ("10-year yield", "4.90%", "−0.01 pt", ""),
        ],
        "og_tiles": [("S&P 500", "−0.5%"), ("Chip fund (SMH)", "−7.3%"), ("Russell 2000", "+0.6%")],
    },
]

DISCLAIMER = """<div class="callout compact" role="note">
          <p><strong>Research and education only. Not investment advice.</strong> This is a summary of public market data and online chatter. It is not a recommendation to buy, sell or hold anything, and it does not consider anyone's finances. PLJA Corp is not a broker-dealer or an investment adviser. Prices and counts can be wrong or late. Do your own research.</p>
        </div>"""

CSS = r"""/* Daily Scan */
.day-hero { padding: clamp(1.8rem, 5vw, 3rem) 0 1rem; position: relative; isolation: isolate; }
.day-hero::before { content: ""; position: absolute; inset: 0; background: var(--glow); z-index: -1; }
.day-hero h1 { max-width: 22ch; }
.meta { display: flex; flex-wrap: wrap; gap: .4rem 1rem; color: var(--mute); font-size: .9rem; margin: 0 0 1rem; }
.share { display: flex; flex-wrap: wrap; gap: .45rem; margin: 1rem 0 0; }
.summary { padding: clamp(1rem, 3vw, 1.6rem); margin: 1.4rem 0 0; display: grid; gap: 1.2rem; }
.summary h2 { font-size: var(--s-1); font-family: var(--sans); font-weight: 500; letter-spacing: .12em; text-transform: uppercase; color: var(--mute); margin: 0; }
.summary ol { margin: 0; padding-left: 1.3rem; display: grid; gap: .55rem; }
.summary li { color: var(--ink-2); }
.summary li::marker { color: var(--accent); font-weight: 500; }
.summary strong { color: var(--ink); font-weight: 500; }
.dtiles { display: grid; grid-template-columns: repeat(2, 1fr); gap: .5rem; }
@media (min-width: 640px) { .dtiles { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1000px) { .dtiles { grid-template-columns: repeat(6, 1fr); } }
.dtile { background: var(--surface-2); border: 1px solid var(--line-2); border-radius: var(--r-2); padding: .65rem .8rem; display: grid; gap: .05rem; }
.dtile .k { font-size: .74rem; color: var(--mute); }
.dtile .v { font: 500 1.12rem/1.2 var(--mono); }
.dtile .c { font: 500 .86rem var(--mono); color: var(--ink-2); }
.dtile .c.up { color: var(--good); } .dtile .c.down { color: var(--bad); }
.read { display: grid; gap: 2rem; padding: 2rem 0 3rem; }
@media (min-width: 1000px) { .read { grid-template-columns: 14rem minmax(0, 1fr); gap: 3rem; } }
.toc { font-size: .9rem; }
.toc nav { position: sticky; top: 5rem; display: grid; gap: .1rem; border-left: 2px solid var(--line); }
.toc .k { font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--mute); margin: 0 0 .5rem; }
.toc a { color: var(--ink-2); text-decoration: none; padding: .35rem .8rem; margin-left: -2px; border-left: 2px solid transparent; }
.toc a:hover { color: var(--ink); }
.toc a.on { color: var(--accent-ink); border-left-color: var(--accent); font-weight: 500; }
@media (max-width: 999px) { .toc nav { position: static; display: flex; flex-wrap: wrap; gap: .35rem; border: 0; } .toc a { border: 1px solid var(--line); border-radius: 999px; margin: 0; padding: .35rem .75rem; background: var(--surface); } }
.article { max-width: 46rem; }
.article h2 { font-size: var(--s-2); margin-top: 2.6rem; scroll-margin-top: 5rem; }
.article h2:first-child { margin-top: 0; }
.article p, .article li { color: var(--ink-2); }
.article strong { color: var(--ink); font-weight: 500; }
.article .note { border: 0; padding: 0; }
.pager { display: flex; justify-content: space-between; gap: 1rem; border-top: 1px solid var(--line); padding-top: 1.2rem; margin-top: 2rem; font-size: .95rem; }
.pager .off { color: var(--mute); }
.archive { display: grid; gap: var(--space); }
@media (min-width: 900px) { .archive { grid-template-columns: minmax(0, 1fr) 20rem; align-items: start; } }
.cal { padding: 1rem 1.1rem 1.2rem; }
.cal h3 { margin: 0 0 .7rem; font: 600 var(--s-1) var(--serif); }
.cal table { font-size: .85rem; table-layout: fixed; }
.cal th { background: none; text-align: center; padding: .25rem 0; font-size: .7rem; }
.cal td { text-align: center; padding: .15rem; border: 0; }
.cal td span, .cal td a { display: grid; place-items: center; height: 2.1rem; border-radius: .5rem; color: var(--mute); }
.cal td a { background: var(--accent); color: #fff; font-weight: 500; text-decoration: none; }
.cal td a:hover { background: var(--accent-ink); }
.cal td.today span { box-shadow: inset 0 0 0 1px var(--ink-2); color: var(--ink); }
.cal tbody tr:hover td { background: none; }
.cal .k { font-size: .8rem; color: var(--mute); margin: .7rem 0 0; }
.days { list-style: none; margin: 0; padding: 0; display: grid; gap: .6rem; }
.days a { display: grid; gap: .2rem; padding: 1rem 1.1rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-2); text-decoration: none; color: var(--ink); transition: border-color .2s, transform .2s var(--ease); }
.days a:hover { border-color: var(--accent); transform: translateY(-2px); }
.days .d { font-size: .8rem; color: var(--mute); letter-spacing: .06em; text-transform: uppercase; }
.days .h { font: 600 var(--s-1)/1.25 var(--serif); }
"""

JS = r"""<script>
(function(){
  var url = location.href.split('#')[0];
  var c = document.getElementById('copy'), s = document.getElementById('share'), p = document.getElementById('print');
  if (c) c.addEventListener('click', function(){
    (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function(){ plja.toast('Link copied'); }, function(){ prompt('Copy this link', url); });
  });
  if (s) { if (navigator.share) s.addEventListener('click', function(){ navigator.share({title: document.title, url: url}).catch(function(){}); }); else s.hidden = true; }
  if (p) p.addEventListener('click', function(){ window.print(); });
  var links = [].slice.call(document.querySelectorAll('.toc a'));
  if (links.length && 'IntersectionObserver' in window) {
    var map = {}; links.forEach(function(a){ map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function(es){ es.forEach(function(e){ if (e.isIntersecting) { links.forEach(function(a){ a.classList.remove('on'); }); var a = map[e.target.id]; if (a) a.classList.add('on'); } }); }, {rootMargin: '-20% 0px -70% 0px'});
    Object.keys(map).forEach(function(id){ var el = document.getElementById(id); if (el) io.observe(el); });
  }
})();
</script>"""


def slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&\w+;", "", text).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:48]


def frag(day: str, kind: str) -> str:
    return (CONTENT / f"{day}.{kind}.html").read_text(encoding="utf-8").strip()


def prepare_body(html: str) -> tuple[str, list[tuple[str, str]]]:
    toc: list[tuple[str, str]] = []

    def h2(m: re.Match) -> str:
        label = m.group(1)
        sid = slug(label)
        toc.append((sid, re.sub(r"^\d+\.\s*", "", re.sub(r"<[^>]+>", "", label))))
        return f'<h2 id="{sid}">{label}</h2>'

    html = re.sub(r"<h2>(.*?)</h2>", h2, html)

    # Right-align and tint signed numbers in tables so the eye can scan them.
    def td(m: re.Match) -> str:
        val = m.group(1)
        plain = re.sub(r"<[^>]+>", "", val).strip()
        if re.match(r"^[−+\-]?[$]?[\d.,]+(%| pt| pts|×|x)?$", plain):
            cls = "r num"
            if plain.startswith("−") and plain.endswith("%"):
                cls += " down"
            elif plain.startswith("+") and plain.endswith("%"):
                cls += " up"
            return f'<td class="{cls}">{val}</td>'
        return m.group(0)

    html = re.sub(r"<td>(.*?)</td>", td, html)

    # Right-align a header when every cell in its column is numeric.
    def table(m: re.Match) -> str:
        t = m.group(0)
        rows = re.findall(r"<tr>(.*?)</tr>", t, flags=re.S)
        if not rows:
            return t
        heads = re.findall(r"<th>(.*?)</th>", rows[0])
        body = [re.findall(r"<td(?: class=\"([^\"]*)\")?>", r) for r in rows[1:]]
        for ci in range(len(heads)):
            col = [r[ci] for r in body if ci < len(r)]
            if col and all("r" in c.split() for c in col):
                heads[ci] = None
        out_heads = iter(re.findall(r"<th>(.*?)</th>", rows[0]))
        idx = iter(range(len(heads)))
        return re.sub(r"<th>(.*?)</th>", lambda h: (f'<th class="r">{h.group(1)}</th>' if heads[next(idx)] is None else h.group(0)), t, count=len(heads))

    html = re.sub(r"<table>.*?</table>", table, html, flags=re.S)
    return html, toc


def tiles_html(day: dict) -> str:
    return "".join(
        f'<div class="dtile"><span class="k">{k}</span><span class="v">{v}</span><span class="c {cls}">{c}</span></div>'
        for k, v, c, cls in day["tiles"]
    )


def share_row() -> str:
    I = theme.ICONS
    return f"""<div class="share no-print">
          <button class="chip" type="button" id="copy">{I["link"]} Copy link</button>
          <button class="chip" type="button" id="share">{I["share"]} Share</button>
          <button class="chip" type="button" id="print">Print</button>
          <a class="chip" href="/live/">Open the live board →</a>
        </div>"""


def day_page(i: int, day: dict) -> str:
    body, toc = prepare_body(frag(day["date"], "body"))
    newer = DAYS[i - 1] if i > 0 else None
    older = DAYS[i + 1] if i + 1 < len(DAYS) else None
    toc_html = "".join(f'<a href="#{sid}">{label}</a>' for sid, label in toc)
    pager = (
        (f'<a href="/daily/{older["date"]}/">← {older["label"]}</a>' if older else '<span class="off">This is the first scan</span>')
        + (f'<a href="/daily/{newer["date"]}/">{newer["label"]} →</a>' if newer else '<a href="/daily/">All scans →</a>')
    )
    return f"""
    <section class="day-hero">
      <div class="wrap">
        <p class="kicker">Daily Scan · {day["label"]}</p>
        <h1>{day["headline"]}</h1>
        <p class="meta"><span>{day["data_note"]}</span></p>
        <p class="meta"><span>First published {day["first_published"]}</span><span>Page v{VERSION}</span></p>
        {share_row()}
        <div class="surface summary">
          <h2>At a glance</h2>
          <div class="dtiles">{tiles_html(day)}</div>
          <h2>The short version</h2>
          {frag(day["date"], "short")}
          {DISCLAIMER}
        </div>
      </div>
    </section>
    <div class="wrap read">
      <aside class="toc no-print" aria-label="On this page"><p class="k">On this page</p><nav>{toc_html}</nav></aside>
      <article class="article">
        {body}
        <nav class="pager no-print" aria-label="More scans">{pager}</nav>
      </article>
    </div>
"""


def month_calendar(year: int, month: int, have: set[str], today: date) -> str:
    cal = calendar.Calendar(firstweekday=6)
    rows = []
    for week in cal.monthdatescalendar(year, month):
        cells = []
        for d in week:
            if d.month != month:
                cells.append("<td></td>")
                continue
            iso = d.isoformat()
            cls = ' class="today"' if d == today else ""
            if iso in have:
                cells.append(f'<td{cls}><a href="/daily/{iso}/" aria-label="Scan for {d.strftime("%B")} {d.day}">{d.day}</a></td>')
            else:
                cells.append(f"<td{cls}><span>{d.day}</span></td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    head = "".join(f'<th scope="col" abbr="{n}">{n[0]}</th>' for n in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
    return f"""<div class="surface cal">
          <h3>{calendar.month_name[month]} {year}</h3>
          <table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>
          <p class="k">Highlighted days have a scan.{" US markets are closed Thursday, Nov 26 (Thanksgiving)." if (year, month) == (2026, 11) else ""}</p>
        </div>"""


def index_page() -> str:
    latest = DAYS[0]
    have = {d["date"] for d in DAYS}
    today = theme.datetime.now(theme.ET).date()
    months = sorted({(int(d["date"][:4]), int(d["date"][5:7])) for d in DAYS}, reverse=True)
    cals = "".join(month_calendar(y, m, have, today) for y, m in months)
    days = "".join(
        f'<li><a href="/daily/{d["date"]}/"><span class="d">{d["label"]}</span><span class="h">{d["headline"]}</span></a></li>'
        for d in DAYS
    )
    return f"""
    <section class="day-hero">
      <div class="wrap">
        <p class="kicker">Daily Scan · @PLJA_AI</p>
        <h1>The morning read on market chatter.</h1>
        <p class="lede">A free, public research log of odd moves, news flags, and names being talked about far more than usual. Built from public market data. Not a newsletter of trade ideas.</p>
        <div class="surface summary">
          <h2>Latest · {latest["label"]}</h2>
          <p class="days"><a href="/daily/{latest["date"]}/"><span class="h">{latest["headline"]}</span></a></p>
          <div class="dtiles">{tiles_html(latest)}</div>
          {frag(latest["date"], "index")}
          <div class="actions">
            <a class="btn btn-primary" href="/daily/{latest["date"]}/">Read the full scan <span class="arr" aria-hidden="true">→</span></a>
            <a class="btn btn-ghost" href="/live/">Open the live board</a>
          </div>
          {DISCLAIMER}
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="section-head"><h2>Archive</h2><p>{len(DAYS)} scan{"s" if len(DAYS) != 1 else ""} so far. New scans are added here as they are published.</p></div>
        <div class="archive">
          <ul class="days">{days}</ul>
          <div>{cals}</div>
        </div>
      </div>
    </section>
"""


def write_og(day: dict) -> str:
    w, h = 1200, 630
    paper, ink, mute = (245, 240, 231), (27, 24, 20), (106, 99, 90)
    accent, bad, good = (169, 82, 44), (163, 58, 42), (44, 106, 69)
    img = Image.new("RGB", (w, h), paper)
    d = ImageDraw.Draw(img)
    fra = Path("/usr/share/fonts/truetype/sand-box/google/Fraunces/Fraunces-VariableFont_SOFT,WONK,opsz,wght.ttf")
    plex = Path("/usr/share/fonts/truetype/sand-box/google/IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf")
    mono = Path("/usr/share/fonts/truetype/sand-box/google/IBM Plex Mono/IBMPlexMono-Medium.ttf")
    fb = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    f = lambda p, s: ImageFont.truetype(str(p if p.exists() else fb), s)  # noqa: E731
    d.rectangle([0, 0, w, 10], fill=accent)
    d.text((80, 70), f"PLJA DAILY SCAN · {day['label'].upper()}", font=f(plex, 24), fill=accent)
    # wrap headline
    words, lines, cur = day["headline"].split(), [], ""
    font = f(fra, 66)
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=font) > 1040:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    lines.append(cur)
    y = 120
    for ln in lines[:3]:
        d.text((80, y), ln, font=font, fill=ink)
        y += 80
    x = 80
    for k, v in day["og_tiles"]:
        d.rounded_rectangle([x, 380, x + 330, 520], radius=22, fill=(255, 253, 249), outline=(221, 212, 198), width=2)
        d.text((x + 24, 400), k, font=f(plex, 24), fill=mute)
        d.text((x + 24, 440), v, font=f(mono, 52), fill=bad if v.startswith("−") else good if v.startswith("+") else ink)
        x += 355
    d.text((80, 560), "Research and education only. Not investment advice.", font=f(plex, 24), fill=mute)
    rel = f"/assets/img/daily-{day['date']}-og.png"
    out = PUBLIC / rel.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return rel


def main() -> None:
    css_href = theme.write_page_css(PUBLIC, "daily", CSS)
    head = f'\n  <link rel="stylesheet" href="{css_href}">'
    common = dict(
        robots="index,follow",
        draft_banner=False,
        footer_blurb="A daily research log of public market data, and a link back to the Analog Arcade shop.",
        footer_note="Research and education only. Not investment advice.",
        after_main=theme.arcade_section(UTM, "This scan"),
        scripts=JS,
        utm=UTM,
        extra_head=head,
        preload_mono=True,
    )
    for i, day in enumerate(DAYS):
        og = write_og(day)
        dest = PUBLIC / "daily" / day["date"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            theme.page(
                title=f"PLJA Daily Scan: {day['label']}",
                description=day["headline"] + " " + DESC,
                path=f"/daily/{day['date']}/",
                body=day_page(i, day),
                og_image=og,
                og_type="article",
                **common,
            ),
            encoding="utf-8",
        )
        print("wrote", dest, dest.stat().st_size)
    index = PUBLIC / "daily" / "index.html"
    index.write_text(
        theme.page(
            title="PLJA Daily Scan — chatter vs. normal",
            description=DESC,
            path="/daily/",
            body=index_page(),
            og_image=f"/assets/img/daily-{DAYS[0]['date']}-og.png",
            **common,
        ),
        encoding="utf-8",
    )
    print("wrote", index, index.stat().st_size)


if __name__ == "__main__":
    main()

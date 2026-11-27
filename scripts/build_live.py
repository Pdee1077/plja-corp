#!/usr/bin/env python3
"""Build the public PLJA Live board into public/live/. No personal names.

Reads nothing private. The page loads board.json (and history.csv for the
sparklines) from the public live-data branch that the GitHub Action writes.
The data format is owned by scripts/live_board.py and is not changed here.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SITE = theme.SITE
VERSION = theme.VERSION
TITLE = "PLJA Live board — chatter vs. normal"
DESC = (
    "A live, sortable board of names being talked about far more than usual, with price moves "
    "and a NO NEWS flag. Research and education, not investment advice."
)
UTM = "utm_source=plja_live"
RAW = "https://raw.githubusercontent.com/Pdee1077/plja-corp/live-data"
OG_PATH = "/assets/img/live-og-v3.png"

CSS = r"""/* Live board */
.live-hero { padding: clamp(1.8rem, 5vw, 3rem) 0 1rem; position: relative; isolation: isolate; }
.live-hero::before { content: ""; position: absolute; inset: 0; background: var(--glow); z-index: -1; }
.live-hero h1 { max-width: 20ch; }
.status { display: flex; flex-wrap: wrap; align-items: center; gap: .6rem 1rem; padding: .75rem 1rem; margin: 1.2rem 0 0; font-size: .92rem; }
.status .dot { width: .6rem; height: .6rem; border-radius: 50%; background: var(--mute); flex: none; }
.status.fresh .dot { background: var(--good); animation: pulse 2.4s infinite; }
.status.stale .dot { background: var(--warn); }
.status .when { font-weight: 500; }
.status .age { color: var(--mute); }
.status .st-main { flex: 1 1 16rem; }
.status .st-tools { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem; margin-left: auto; }
.status #auto[aria-pressed="true"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.market .warn { color: var(--warn); font-weight: 500; }
.status .count { font: 500 .8rem var(--mono); color: var(--mute); }
.market { font-size: .86rem; color: var(--ink-2); margin: .55rem 0 0; }
.tiles { display: grid; grid-template-columns: repeat(2, 1fr); gap: .6rem; margin: 1.2rem 0 0; }
@media (min-width: 760px) { .tiles { grid-template-columns: repeat(4, 1fr); } }
.tile { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-2); padding: .8rem 1rem; display: grid; gap: .1rem; }
.tile .k { font-size: .74rem; letter-spacing: .1em; text-transform: uppercase; color: var(--mute); }
.tile .v { font: 600 var(--s-2)/1.1 var(--serif); }
.tile .s { font-size: .84rem; color: var(--ink-2); }
.tile .v .mono { font-size: .8em; }
.changes { margin: 1rem 0 0; padding: .75rem 1rem; border-radius: var(--r-2); background: var(--accent-soft); color: var(--ink); font-size: .93rem; }
.changes[hidden] { display: none; }
.controls { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; margin: 1.6rem 0 .8rem; }
.controls .search { flex: 1 1 14rem; position: relative; }
.controls input { width: 100%; min-height: 42px; border-radius: 999px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); font: inherit; font-size: .95rem; padding: .5rem 1rem .5rem 2.3rem; }
.controls input:focus { outline: 3px solid var(--focus); outline-offset: 1px; }
.controls .search svg { position: absolute; left: .8rem; top: 50%; transform: translateY(-50%); width: 1rem; height: 1rem; color: var(--mute); pointer-events: none; }
.board th button { all: unset; cursor: pointer; display: inline-flex; gap: .3rem; align-items: center; }
.board th button:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; border-radius: 3px; }
.board th[aria-sort] button::after { content: "↕"; opacity: .35; font-size: .9em; }
.board th[aria-sort="ascending"] button::after { content: "↑"; opacity: 1; color: var(--accent-ink); }
.board th[aria-sort="descending"] button::after { content: "↓"; opacity: 1; color: var(--accent-ink); }
.board td { vertical-align: middle; }
.board .sym { font: 500 1rem var(--mono); display: flex; align-items: center; gap: .4rem; flex-wrap: wrap; }
.board .nm { display: block; color: var(--mute); font-size: .8rem; max-width: 16rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.board .why { font-size: .86rem; color: var(--ink-2); min-width: 12rem; }
.board .why li { margin: 0; }
.board .why ul { margin: 0; padding-left: 1rem; }
.board .heatcell { min-width: 9rem; }
.heat { display: flex; align-items: center; gap: .5rem; justify-content: flex-end; }
.heat svg { width: 5.5rem; height: .5rem; flex: none; }
.heat .bg { fill: var(--line-2); }
.heat .f { fill: var(--accent); }
.heat .f.hot { fill: var(--bad); }
.heat b { font: 500 .92rem var(--mono); min-width: 3.6rem; text-align: right; }
.spark { width: 5rem; height: 1.4rem; display: inline-block; vertical-align: middle; margin-right: .4rem; overflow: visible; }
.spark polyline { fill: none; stroke: var(--accent); stroke-width: 1.6; stroke-linejoin: round; stroke-linecap: round; vector-effect: non-scaling-stroke; }
.spark circle { fill: var(--accent); }
.board td.up { color: var(--good); } .board td.down { color: var(--bad); }
.board tr.only td:first-child { box-shadow: inset 3px 0 0 var(--warn); }
.board tr.nonews td:first-child { box-shadow: inset 3px 0 0 var(--bad); }
.board tr.changed td { animation: flash 2.4s var(--ease) 1; }
@keyframes flash { 0% { background: var(--accent-soft); } 100% { background: transparent; } }
.delta { font: 500 .72rem var(--mono); padding: .1rem .35rem; border-radius: .3rem; }
.delta.up { color: var(--good); background: var(--good-soft); }
.delta.down { color: var(--bad); background: var(--bad-soft); }
.empty { color: var(--mute); text-align: center; padding: 2rem 1rem !important; }
.legend { color: var(--ink-2); font-size: .92rem; }
.legend strong { color: var(--ink); font-weight: 500; }
.keys { display: flex; flex-wrap: wrap; gap: .4rem 1rem; font-size: .84rem; color: var(--mute); margin: 0 0 1rem; }
.keys span::before { content: ""; display: inline-block; width: .7rem; height: .7rem; border-radius: 2px; margin-right: .35rem; vertical-align: -1px; }
.keys .k-only::before { background: var(--warn); }
.keys .k-nonews::before { background: var(--bad); }
.keys .k-new::before { background: var(--accent); }
@media (max-width: 760px) {
  .board, .board tbody, .board tr, .board td { display: block; width: 100%; }
  .board thead { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
  .table-wrap.board-wrap { border: 0; background: transparent; overflow: visible; }
  .board tr { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-2); margin: 0 0 .6rem; padding: .5rem .2rem; }
  .board td { border: 0; padding: .3rem .8rem; display: flex; justify-content: space-between; gap: 1rem; text-align: right; }
  .board td::before { content: attr(data-label); color: var(--mute); font-size: .78rem; text-align: left; flex: none; }
  .board td.first { display: block; text-align: left; }
  .board td.first::before { content: none; }
  .board td.why { display: block; text-align: left; }
  .board td.why::before { content: none; }
  .board tr.only td:first-child, .board tr.nonews td:first-child { box-shadow: none; }
  .board tr.only { border-left: 4px solid var(--warn); }
  .board tr.nonews { border-left: 4px solid var(--bad); }
  .heat { justify-content: flex-end; }
}
"""

JS = r"""<script>
(function(){
  var RAW = "__RAW__";
  var $ = function(id){ return document.getElementById(id); };
  var bodyEl = $('board-body'), statusEl = $('status'), whenEl = $('st-when'), ageEl = $('st-age'),
      nextEl = $('st-next'), autoBtn = $('auto'), nowBtn = $('refresh'), q = $('q'), chg = $('changes'),
      countEl = $('st-count'), marketEl = $('market');
  var data = null, hist = null, sortKey = 'heat', sortDir = -1, filter = 'all', diff = {};
  var ET = 'America/New_York';
  var fmt = new Intl.DateTimeFormat('en-US', {timeZone: ET, weekday:'short', month:'short', day:'numeric', hour:'numeric', minute:'2-digit'});
  function etText(d){ return fmt.format(d) + ' ET'; }
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function num(v){ return v == null || v === '' || isNaN(Number(v)) ? null : Number(v); }
  function heatOf(r){ var a = num(r.st_x_normal), b = num(r.x24); return a != null ? a : b; }
  function x(v){ v = num(v); return v == null ? '–' : (v >= 10 ? v.toFixed(0) : v.toFixed(1)) + '×'; }
  function pct(v){ v = num(v); return v == null ? '–' : (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(1) + '%'; }
  function n(v){ v = num(v); return v == null ? '–' : v.toLocaleString('en-US'); }

  // Market hours in Eastern time, including the 2026 Thanksgiving week.
  function marketNote(){
    var parts = {}; new Intl.DateTimeFormat('en-US', {timeZone: ET, year:'numeric', month:'2-digit', day:'2-digit', weekday:'short', hour:'2-digit', minute:'2-digit', hourCycle:'h23'}).formatToParts(new Date()).forEach(function(p){ parts[p.type] = p.value; });
    var ymd = parts.year + '-' + parts.month + '-' + parts.day, mins = Number(parts.hour) * 60 + Number(parts.minute), wd = parts.weekday;
    var closed = {'2026-11-26':'Thanksgiving','2026-12-25':'Christmas','2027-01-01':"New Year's Day"};
    var early = {'2026-11-27': 13 * 60, '2026-12-24': 13 * 60};
    if (closed[ymd]) return 'US stock markets are closed today (' + closed[ymd] + '). Talk counts can still move.';
    if (wd === 'Sat' || wd === 'Sun') return 'US stock markets are closed for the weekend. The board refreshes on weekdays only.';
    var close = early[ymd] || 16 * 60;
    if (mins < 570) return 'Before the US open (9:30 AM ET).';
    if (mins >= close) return 'US stock markets have closed for the day' + (early[ymd] ? ' (early close, 1:00 PM ET)' : '') + '.';
    return 'US markets are open' + (early[ymd] ? ' until 1:00 PM ET today' : '') + '.';
  }

  function load(u){ return fetch(u, {cache:'no-store'}).then(function(r){ return r.ok ? r.json() : null; }).catch(function(){ return null; }); }
  function pickNewest(a, b){ if (a && b && a.updated && b.updated) return new Date(a.updated) > new Date(b.updated) ? a : b; return b || a; }

  function remember(d){
    // What changed since the snapshot you saw before this one. Stored only in this browser.
    var key = 'plja-live-seen', seen = null, prev = null;
    try { seen = JSON.parse(localStorage.getItem(key) || 'null'); prev = JSON.parse(localStorage.getItem('plja-live-prev') || 'null'); } catch(e){}
    var snap = {updated: d.updated, updated_et: d.updated_et, rows: {}};
    d.rows.forEach(function(r){ snap.rows[r.sym] = {h: heatOf(r), reddit: num(r.reddit)}; });
    if (!seen || seen.updated !== d.updated) { prev = seen; try { localStorage.setItem('plja-live-prev', JSON.stringify(prev)); localStorage.setItem(key, JSON.stringify(snap)); } catch(e){} }
    diff = {};
    if (!prev || !prev.rows) { chg.hidden = true; return; }
    var added = [], gone = [], up = 0;
    Object.keys(snap.rows).forEach(function(s){
      var a = prev.rows[s], b = snap.rows[s];
      if (!a) { added.push(s); diff[s] = 'new'; }
      else if (a.h != null && b.h != null && Math.abs(b.h - a.h) >= 0.5) { diff[s] = b.h > a.h ? 'up' : 'down'; if (b.h > a.h) up++; }
    });
    Object.keys(prev.rows).forEach(function(s){ if (!snap.rows[s]) gone.push(s); });
    var bits = [];
    if (added.length) bits.push('<strong>New:</strong> ' + added.map(esc).join(', '));
    if (gone.length) bits.push('<strong>Dropped off:</strong> ' + gone.map(esc).join(', '));
    if (up) bits.push(up + ' name' + (up === 1 ? '' : 's') + ' heating up');
    chg.innerHTML = 'Since the snapshot you saw at ' + esc(prev.updated_et || '') + ': ' + (bits.length ? bits.join(' · ') : 'no names added or dropped.');
    chg.hidden = false;
  }

  function status(){
    if (!data) return;
    var t = new Date(data.updated), mins = Math.max(0, Math.round((Date.now() - t.getTime()) / 60000));
    whenEl.textContent = 'Snapshot ' + etText(t);
    var age = mins < 1 ? 'just now' : mins < 60 ? mins + ' min old' : mins < 1440 ? Math.round(mins / 60) + ' h old' : Math.round(mins / 1440) + ' d old';
    ageEl.textContent = '· ' + age;
    statusEl.className = 'surface status ' + (mins > 25 ? 'stale' : 'fresh');
    marketEl.innerHTML = esc(marketNote()) + (mins > 25 ? ' <span class="warn">This snapshot is older than the 15-minute refresh, so the scheduled update may be paused or delayed. Prices and counts are as of the snapshot time.</span>' : '');
  }

  function heatSvg(v){
    if (v == null) return '<span class="heat"><b>–</b></span>';
    var w = Math.max(3, Math.min(100, Math.log(Math.max(v, 1)) / Math.log(40) * 100));
    return '<span class="heat"><svg viewBox="0 0 100 8" preserveAspectRatio="none" aria-hidden="true"><rect class="bg" width="100" height="8" rx="4"/><rect class="f' + (v >= 5 ? ' hot' : '') + '" width="' + w.toFixed(1) + '" height="8" rx="4"/></svg><b>' + x(v) + '</b></span>';
  }
  function spark(sym){
    var s = hist && hist[sym];
    if (!s || s.length < 3) return '';
    var max = Math.max.apply(null, s), min = Math.min.apply(null, s), span = max - min || 1;
    var pts = s.map(function(v, i){ return (i / (s.length - 1) * 100).toFixed(1) + ',' + (22 - (v - min) / span * 20).toFixed(1); }).join(' ');
    var last = pts.split(' ').pop().split(',');
    return '<svg class="spark" viewBox="0 0 100 24" preserveAspectRatio="none" role="img" aria-label="Reddit mentions trend, ' + s.length + ' readings"><polyline points="' + pts + '"/><circle cx="' + last[0] + '" cy="' + last[1] + '" r="2.4"/></svg>';
  }

  function rowsView(){
    var term = (q.value || '').toLowerCase().trim();
    var rows = data.rows.filter(function(r){
      if (filter === 'abnormal' && r.group !== 'abnormal') return false;
      if (filter === 'faint' && r.group === 'abnormal') return false;
      if (filter === 'nonews' && !r.nonews) return false;
      if (filter === 'only' && r.kind !== 'talk only') return false;
      if (filter === 'changed' && !diff[r.sym]) return false;
      if (term && (r.sym + ' ' + (r.name || '')).toLowerCase().indexOf(term) < 0) return false;
      return true;
    });
    var get = {
      sym: function(r){ return r.sym; }, heat: heatOf, reddit: function(r){ return num(r.reddit); },
      x24: function(r){ return num(r.x24); }, d1: function(r){ return num(r.d1); }, n24: function(r){ return num(r.n24); }
    }[sortKey] || heatOf;
    rows.sort(function(a, b){ var A = get(a), B = get(b); if (A == null) return 1; if (B == null) return -1; return (A > B ? 1 : A < B ? -1 : 0) * sortDir; });
    return rows;
  }

  function render(){
    if (!data || !Array.isArray(data.rows)) {
      bodyEl.innerHTML = '<tr><td colspan="7" class="empty">The live snapshot could not be loaded. The morning scan is still on the <a href="/daily/">Daily Scan</a>.</td></tr>';
      return;
    }
    var rows = rowsView();
    bodyEl.innerHTML = rows.map(function(r){
      var cls = []; if (r.kind === 'talk only') cls.push('only'); if (r.nonews) cls.push('nonews'); if (diff[r.sym]) cls.push('changed');
      var tag = diff[r.sym] === 'new' ? '<span class="badge new">New</span>' : diff[r.sym] === 'up' ? '<span class="delta up" title="Hotter than the last snapshot you saw">▲</span>' : diff[r.sym] === 'down' ? '<span class="delta down" title="Cooler than the last snapshot you saw">▼</span>' : '';
      var d1 = num(r.d1);
      var flags = (r.flags || []).map(function(f){ return '<li>' + esc(f) + '</li>'; }).join('');
      return '<tr class="' + cls.join(' ') + '">'
        + '<td class="first"><span class="sym">' + esc(r.sym) + (r.nonews ? ' <span class="badge">No news</span>' : '') + ' ' + tag + '</span>' + (r.name ? '<span class="nm">' + esc(r.name) + '</span>' : '') + '</td>'
        + '<td class="r heatcell" data-label="Talk vs normal">' + heatSvg(heatOf(r)) + '</td>'
        + '<td class="r" data-label="Reddit 24h">' + spark(r.sym) + n(r.reddit) + '</td>'
        + '<td class="r" data-label="vs day before">' + x(r.x24) + '</td>'
        + '<td class="r ' + (d1 > 0 ? 'up' : d1 < 0 ? 'down' : '') + '" data-label="Price, 1 day">' + pct(r.d1) + '</td>'
        + '<td class="r" data-label="News 24h">' + n(r.n24) + '</td>'
        + '<td class="why" data-label="Why"><ul>' + flags + '</ul></td>'
        + '</tr>';
    }).join('') || '<tr><td colspan="7" class="empty">No names match. Try “All”.</td></tr>';
    countEl.textContent = rows.length + ' of ' + data.rows.length + ' names';
  }

  function tiles(){
    var rows = data.rows, ab = rows.filter(function(r){ return r.group === 'abnormal'; });
    var top = rows.slice().sort(function(a, b){ return (heatOf(b) || 0) - (heatOf(a) || 0); })[0];
    $('t-ab').textContent = ab.length;
    $('t-nn').textContent = rows.filter(function(r){ return r.nonews; }).length;
    $('t-only').textContent = rows.filter(function(r){ return r.kind === 'talk only'; }).length;
    $('t-top').innerHTML = top ? '<span class="mono">' + esc(top.sym) + '</span> ' + x(heatOf(top)) : '–';
    $('t-top-s').textContent = top && top.name ? top.name : '';
    [].forEach.call(document.querySelectorAll('[data-f] .ct'), function(el){
      var f = el.parentNode.dataset.f;
      var c = f === 'all' ? rows.length : f === 'abnormal' ? ab.length : f === 'faint' ? rows.length - ab.length : f === 'nonews' ? rows.filter(function(r){ return r.nonews; }).length : f === 'only' ? rows.filter(function(r){ return r.kind === 'talk only'; }).length : Object.keys(diff).length;
      el.textContent = c;
    });
  }

  function parseHist(text){
    var out = {}, seen = {};
    text.split('\n').slice(1).forEach(function(line){
      var p = line.split(','); if (p.length < 3 || !p[1]) return;
      var k = p[0] + '|' + p[1]; if (seen[k]) return; seen[k] = 1;
      var v = Number(p[2]); if (p[2] === '' || isNaN(v)) return;
      (out[p[1]] = out[p[1]] || []).push(v);
    });
    Object.keys(out).forEach(function(s){ out[s] = out[s].slice(-40); });
    return out;
  }
  function loadHist(){
    fetch(RAW + '/history.csv?t=' + Math.floor(Date.now() / 300000), {cache:'no-store'}).then(function(r){ return r.ok ? r.text() : ''; }).then(function(t){ if (t) { hist = parseHist(t); render(); } }).catch(function(){});
  }

  var timer = null, nextAt = 0, AUTO_MS = 5 * 60 * 1000;
  function boot(manual){
    if (manual) nowBtn.disabled = true;
    Promise.all([load('/live/board.json'), load(RAW + '/board.json?t=' + Date.now())]).then(function(p){
      var d = pickNewest(p[0], p[1]);
      var changed = !data || (d && d.updated !== data.updated);
      if (d) data = d;
      if (data && changed) { remember(data); tiles(); }
      render(); status();
      if (manual) { nowBtn.disabled = false; window.plja && plja.toast(changed && d ? 'New snapshot loaded' : 'Already showing the newest snapshot'); }
      if (!hist && data) (window.requestIdleCallback || setTimeout)(loadHist);
      nextAt = Date.now() + AUTO_MS;
    });
  }
  function tick(){
    status();
    if (autoBtn.getAttribute('aria-pressed') !== 'true') { nextEl.textContent = 'Auto-refresh off'; return; }
    var s = Math.max(0, Math.round((nextAt - Date.now()) / 1000));
    nextEl.textContent = 'Next check in ' + Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
    if (s === 0 && !document.hidden) boot(false);
  }
  autoBtn.addEventListener('click', function(){ var on = autoBtn.getAttribute('aria-pressed') !== 'true'; autoBtn.setAttribute('aria-pressed', on ? 'true' : 'false'); try { localStorage.setItem('plja-live-auto', on ? '1' : '0'); } catch(e){} nextAt = Date.now() + AUTO_MS; tick(); });
  try { if (localStorage.getItem('plja-live-auto') === '0') autoBtn.setAttribute('aria-pressed', 'false'); } catch(e){}
  nowBtn.addEventListener('click', function(){ boot(true); });
  document.addEventListener('visibilitychange', function(){ if (!document.hidden && Date.now() > nextAt) boot(false); });
  q.addEventListener('input', render);
  [].forEach.call(document.querySelectorAll('[data-f]'), function(c){ c.addEventListener('click', function(){ filter = c.dataset.f; [].forEach.call(document.querySelectorAll('[data-f]'), function(o){ o.setAttribute('aria-pressed', o === c ? 'true' : 'false'); }); render(); }); });
  [].forEach.call(document.querySelectorAll('th[data-k] button'), function(b){ b.addEventListener('click', function(){
    var th = b.parentNode, k = th.dataset.k;
    if (sortKey === k) sortDir = -sortDir; else { sortKey = k; sortDir = k === 'sym' ? 1 : -1; }
    [].forEach.call(document.querySelectorAll('th[data-k]'), function(o){ o.setAttribute('aria-sort', o === th ? (sortDir > 0 ? 'ascending' : 'descending') : 'none'); });
    render();
  }); });
  boot(false);
  setInterval(tick, 1000);
})();
</script>""".replace("__RAW__", RAW)


def write_og() -> None:
    w, h = 1200, 630
    bg = (18, 17, 15)
    ink = (241, 235, 225)
    mute = (164, 155, 142)
    accent = (227, 137, 90)
    hot = (255, 143, 125)
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    fra = Path("/usr/share/fonts/truetype/sand-box/google/Fraunces/Fraunces-VariableFont_SOFT,WONK,opsz,wght.ttf")
    plex = Path("/usr/share/fonts/truetype/sand-box/google/IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf")
    mono = Path("/usr/share/fonts/truetype/sand-box/google/IBM Plex Mono/IBMPlexMono-Medium.ttf")
    fallback = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    f = lambda p, s: ImageFont.truetype(str(p if p.exists() else fallback), s)  # noqa: E731
    title, sub, small, m = f(fra, 78), f(plex, 34), f(plex, 24), f(mono, 30)
    d.ellipse([84, 92, 104, 112], fill=(127, 207, 155))
    d.text((120, 84), "LIVE BOARD · PLJA CORP", font=small, fill=mute)
    d.text((80, 140), "Chatter vs. normal", font=title, fill=ink)
    d.text((80, 248), "Who is suddenly being talked about, with price", font=sub, fill=mute)
    d.text((80, 292), "moves and a NO NEWS flag. Sortable. Refreshed on weekdays.", font=sub, fill=mute)
    bars = [("AAA", 0.92), ("BBB", 0.66), ("CCC", 0.48), ("DDD", 0.3)]
    y = 372
    for i, (_, frac) in enumerate(bars):
        d.rounded_rectangle([80, y, 80 + 760, y + 22], radius=11, fill=(42, 39, 34))
        d.rounded_rectangle([80, y, 80 + int(760 * frac), y + 22], radius=11, fill=hot if i == 0 else accent)
        d.text((870, y - 6), f"{[34.7, 9.2, 5.8, 3.2][i]}×", font=m, fill=ink)
        y += 44
    d.text((80, 562), "Research and education only. Not investment advice.", font=small, fill=mute)
    out = PUBLIC / OG_PATH.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)


def body(embedded: bool = False) -> str:
    s = theme.ICONS["search"]
    banner = "" if embedded else theme.tipoff_home_banner()
    if embedded:
        head = """<p class="kicker">Live board · @PLJA_AI</p>
        <h2 id="live">Who is suddenly being talked about</h2>
        <p class="lede">Names getting far more chatter than their own usual level, with the price move beside them and a <strong>NO NEWS</strong> flag when talk jumps but headlines do not.</p>"""
    else:
        head = """<p class="crumb"><a href="/">PLJA Corp</a> › <a href="/chatter/">Market Chatter</a> › Live board</p>
        <p class="kicker">Live board · @PLJA_AI</p>
        <h1>Who is suddenly being talked about.</h1>
        <p class="lede">Names getting far more chatter than their own usual level, with the price move beside them and a <strong>NO NEWS</strong> flag when talk jumps but headlines do not.</p>"""
    return f"""
    <section class="live-hero">
      <div class="wrap">
        {head}
        {banner}
        <div class="surface status" id="status" role="status" aria-live="polite">
          <span class="dot" aria-hidden="true"></span>
          <span class="st-main"><span class="when" id="st-when">Loading the latest snapshot…</span> <span class="age" id="st-age"></span></span>
          <span class="st-tools">
            <span class="count" id="st-next"></span>
            <button class="tool" type="button" id="auto" aria-pressed="true">Auto-refresh</button>
            <button class="tool" type="button" id="refresh">Refresh now</button>
          </span>
        </div>
        <p class="market" id="market"></p>
        <div class="tiles" aria-label="This snapshot at a glance">
          <div class="tile"><span class="k">Flagged</span><span class="v num" id="t-ab">–</span><span class="s">abnormal talk now</span></div>
          <div class="tile"><span class="k">No news</span><span class="v num" id="t-nn">–</span><span class="s">talk without headlines</span></div>
          <div class="tile"><span class="k">Talk only</span><span class="v num" id="t-only">–</span><span class="s">talk up, price quiet</span></div>
          <div class="tile"><span class="k">Loudest</span><span class="v" id="t-top">–</span><span class="s" id="t-top-s"></span></div>
        </div>
        <p class="changes" id="changes" hidden></p>
      </div>
    </section>
    <section class="section tight-top">
      <div class="wrap">
        <div class="controls">
          <div class="search">{s}<label class="sr-only" for="q">Filter by ticker or name</label><input id="q" type="search" placeholder="Filter by ticker or name" autocomplete="off"></div>
          <div class="filters" role="group" aria-label="Show">
            <button class="chip" type="button" data-f="all" aria-pressed="true">All <span class="ct"></span></button>
            <button class="chip" type="button" data-f="abnormal" aria-pressed="false">Abnormal <span class="ct"></span></button>
            <button class="chip" type="button" data-f="nonews" aria-pressed="false">No news <span class="ct"></span></button>
            <button class="chip" type="button" data-f="only" aria-pressed="false">Talk only <span class="ct"></span></button>
            <button class="chip" type="button" data-f="faint" aria-pressed="false">Faint <span class="ct"></span></button>
            <button class="chip" type="button" data-f="changed" aria-pressed="false">Changed <span class="ct"></span></button>
          </div>
        </div>
        <div class="keys" aria-hidden="true"><span class="k-nonews">No news</span><span class="k-only">Talk only, price quiet</span><span class="k-new">New since your last look</span><span id="st-count"></span></div>
        <div class="table-wrap board-wrap" tabindex="0" aria-label="Live board, scrolls sideways on small screens">
          <table class="board">
            <caption class="sr-only">Names with abnormal talk. Use the column buttons to sort.</caption>
            <thead>
              <tr>
                <th scope="col" data-k="sym" aria-sort="none"><button type="button">Name</button></th>
                <th scope="col" class="r" data-k="heat" aria-sort="descending"><button type="button">Talk vs normal</button></th>
                <th scope="col" class="r" data-k="reddit" aria-sort="none"><button type="button">Reddit 24h</button></th>
                <th scope="col" class="r" data-k="x24" aria-sort="none"><button type="button">vs day before</button></th>
                <th scope="col" class="r" data-k="d1" aria-sort="none"><button type="button">Price 1d</button></th>
                <th scope="col" class="r" data-k="n24" aria-sort="none"><button type="button">News 24h</button></th>
                <th scope="col">Why it is flagged</th>
              </tr>
            </thead>
            <tbody id="board-body">
              <tr><td colspan="7" class="empty">Loading…</td></tr>
            </tbody>
          </table>
        </div>
        <noscript><p class="callout">This board needs JavaScript to load the latest snapshot. The raw file is at <a href="/live/board.json">/live/board.json</a>, and the morning write-up is on the <a href="/daily/">Daily Scan</a>.</p></noscript>
        <p class="legend"><strong>Talk vs normal</strong> is StockTwits talk against its own 20-day normal when we have it, otherwise Reddit mentions against the day before. <strong>NO NEWS</strong> means abnormal talk with two or fewer headlines counted for that ticker in the last 24 hours. <strong>Talk only</strong> means the talk jumped and the price is quiet. The small line next to Reddit counts is that name’s recent readings. Reddit counts come from ApeWisdom and mostly reflect one forum. X is not counted. “Changed” compares with the snapshot you last saw in this browser; nothing is sent anywhere.</p>
        <div class="callout" role="note">
          <p><strong>Research and education only. Not investment advice.</strong> This is a snapshot of public talk counts and market prices. It is not a recommendation to buy, sell or hold anything, and it does not consider anyone's finances. PLJA Corp is not a broker-dealer or an investment adviser. Counts can be wrong or late. A place on this board is a lead to check, not a fact. Do your own research.</p>
        </div>
        <p class="legend">The morning write-up is on the <a href="/daily/">Daily Scan</a>. A free GitHub Action tries to refresh this board every 15 minutes on weekdays; GitHub can delay or pause those runs. This page checks for a new snapshot every 5 minutes while it is open.</p>
      </div>
    </section>
"""


def write_robots() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("build_daily_days", ROOT / "scripts" / "build_daily.py")
    days = ["2026-11-25"]
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        days = [d["date"] for d in mod.DAYS]
    robots = f"""User-agent: *
Allow: /daily/
Allow: /chatter/
Allow: /live/
Allow: /assets/
Disallow: /

Sitemap: {SITE}/sitemap.xml
"""
    urls = [f"{SITE}/chatter/", f"{SITE}/daily/"] + [f"{SITE}/daily/{d}/" for d in days] + [f"{SITE}/live/"]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (PUBLIC / "robots.txt").write_text(robots, encoding="utf-8")
    (PUBLIC / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def refresh_bundled_snapshot() -> None:
    """Ship the newest live-data snapshot with the page as a fallback (same file, same format)."""
    import json
    import subprocess

    try:
        raw = subprocess.run(["git", "-C", str(ROOT), "show", "origin/live-data:board.json"], check=True, capture_output=True).stdout
        data = json.loads(raw)
        assert isinstance(data.get("rows"), list) and data.get("updated")
    except Exception as exc:  # keep whatever is already bundled
        print("bundled snapshot kept:", exc)
        return
    (PUBLIC / "live" / "board.json").write_bytes(raw)
    print("bundled snapshot", data["updated"])


def main() -> None:
    refresh_bundled_snapshot()
    css_href = theme.write_page_css(PUBLIC, "live", CSS)
    write_og()
    dest = PUBLIC / "live" / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    html = theme.page(
        title=TITLE,
        description=DESC,
        path="/live/",
        body=body(),
        og_image=OG_PATH,
        robots="index,follow",
        draft_banner=False,
        footer_blurb="A public live board of chatter vs. normal, and a link back to the Analog Arcade shop.",
        footer_note="Research and education only. Not investment advice.",
        after_main=theme.arcade_section(UTM, "This live board"),
        scripts=JS,
        utm=UTM,
        extra_head=f'\n  <link rel="stylesheet" href="{css_href}">\n  <link rel="preconnect" href="https://raw.githubusercontent.com" crossorigin>',
        preload_mono=True,
    )
    dest.write_text(html, encoding="utf-8")
    write_robots()
    print("wrote", dest, dest.stat().st_size)


if __name__ == "__main__":
    main()

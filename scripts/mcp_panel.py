"""Shared 'Market Chatter — loudest names right now' panel (CSS, JS, static fallback).
Used by Analog Arcade /studio and the PLJA home hero + /chatter so the heat style matches."""
import html, json, re

CSS = r"""
/* MCP_PANEL_V1: Market Chatter heat panel. Self-contained colors so it looks the same on every site. */
.mcp{--mcp-ink:#1a1030;margin:18px 0 6px;border-radius:20px;padding:16px;color:#fff;background:linear-gradient(135deg,#1b1038 0%,#3a1457 55%,#5c1a3f 100%);border:1px solid rgba(255,255,255,.16);box-shadow:0 12px 34px rgba(20,8,40,.45)}
.mcp *{box-sizing:border-box}
.mcp-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 14px}
.mcp-title{margin:0;font:800 clamp(1.05rem,3.8vw,1.4rem)/1.15 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#fff;letter-spacing:.1px;max-width:none}
.mcp-title .dot{display:inline-block;width:.6em;height:.6em;border-radius:50%;background:#3ddc97;margin-right:.45em;vertical-align:.05em;box-shadow:0 0 0 0 rgba(61,220,151,.7);animation:mcpPulse 2.2s infinite}
.mcp[data-state="stale"] .mcp-title .dot{background:#ffd23f;animation:none}
@keyframes mcpPulse{0%{box-shadow:0 0 0 0 rgba(61,220,151,.6)}70%{box-shadow:0 0 0 .5em rgba(61,220,151,0)}100%{box-shadow:0 0 0 0 rgba(61,220,151,0)}}
.mcp-meta{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;font-size:.9rem;color:#e7dcff}
.mcp-badge{display:inline-flex;align-items:center;font-weight:800;font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;padding:.28rem .6rem;border-radius:999px;background:#3ddc97;color:#06301f}
.mcp[data-state="stale"] .mcp-badge{background:#fff;color:#8a1020;box-shadow:0 0 0 2px #ff5c5c inset}
.mcp-tiles{list-style:none;margin:12px 0 0;padding:0;display:grid;gap:10px;grid-template-columns:1fr}
.mcp-tile{--heat:#ffe14d;display:grid;grid-template-columns:auto 1fr;grid-template-areas:"x sym" "x why";gap:1px 14px;align-items:center;border-radius:14px;padding:10px 14px;background:var(--heat);color:var(--mcp-ink)}
.mcp-tile.h4{--heat:#ff5c5c}.mcp-tile.h3{--heat:#ff9a3d}.mcp-tile.h2{--heat:#ffc233}.mcp-tile.h1{--heat:#ffe14d}
.mcp-x{grid-area:x;font:800 clamp(2rem,9.5vw,2.7rem)/1 ui-monospace,"SF Mono",Menlo,Consolas,monospace;letter-spacing:-.02em;min-width:3.9ch;font-variant-numeric:tabular-nums}
.mcp-sym{grid-area:sym;font-weight:800;font-size:1.05rem;line-height:1.2}
.mcp-sym small{font-weight:600;font-size:.8rem;opacity:.85;margin-left:.4em}
.mcp-why{grid-area:why;font-size:.88rem;line-height:1.3;font-weight:500}
.mcp-foot{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;margin-top:12px}
.mcp-note{margin:0;font-size:.88rem;line-height:1.4;color:#e7dcff;max-width:44rem}
.mcp-note b{color:#fff}
.mcp-legend{display:inline-flex;gap:4px;align-items:center;margin-left:.5em;vertical-align:middle}
.mcp-legend i{display:inline-block;width:.8em;height:.8em;border-radius:3px}
.mcp-btn{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:10px 20px;border-radius:999px;background:#fff;color:#2a0f4a !important;font-weight:800;font-size:1rem;text-decoration:none !important;box-shadow:0 6px 16px rgba(0,0,0,.3);border:0}
.mcp-btn:hover{background:#ffe14d}
.mcp a:focus-visible{outline:3px solid #ffe14d;outline-offset:3px}
@media(min-width:760px){
  .mcp{padding:20px 22px}
  .mcp-tiles{grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
  .mcp-tile{grid-template-columns:1fr;grid-template-areas:"x" "sym" "why";gap:2px;padding:14px 16px}
  .mcp-x{font-size:clamp(2.6rem,4.4vw,3.4rem)}
}
@media(prefers-reduced-motion:reduce){.mcp-title .dot{animation:none}}
@media print{.mcp{display:none}}
"""

JS = r"""<script>
/* MCP_PANEL_V1: fills #mcp from the live board. Fresher of the site copy and raw live-data wins. */
(function(){
  var box=document.getElementById('mcp'); if(!box||!window.fetch) return;
  var list=box.querySelector('.mcp-tiles'), when=box.querySelector('.mcp-when'), badge=box.querySelector('.mcp-badge');
  var MIN_X=2, MAX=5, STALE_MIN=90;
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function get(u){return fetch(u,{cache:'no-store'}).then(function(r){return r.ok?r.json():null;}).catch(function(){return null;});}
  function heat(x){return x>=20?'h4':x>=8?'h3':x>=4?'h2':'h1';}
  function why(r){
    var p=[],f=(r.flags||[]).join(' | '),m;
    if(m=f.match(/building (\d+) days in a row/)) p.push('building '+m[1]+' days in a row');
    else if(m=f.match(/Reddit ([\d.]+)x the day before/)) p.push('Reddit '+m[1]+'\u00d7 the day before');
    if(r.n24>0) p.push(r.n24+' headline'+(r.n24===1?'':'s')+' in 24h');
    return p.length?p.join(' \u00b7 '):'StockTwits chatter vs its usual';
  }
  function clean(r){
    if(r.group!=='abnormal'||r.st_x_normal==null||r.st_x_normal<MIN_X) return false;
    if(/-/.test(r.sym||'')) return false;
    if(/airpods|find my/i.test((r.name||'')+' '+(r.sym||''))) return false;
    if(/\bIPO\b/i.test((r.flags||[]).join(' ')+' '+(r.name||''))) return false;
    return true;
  }
  function nice(s){return String(s||'').replace(/^(\w{3})\w*day,/,'$1,').replace(/, 20\d\d,/,',');}
  function age(ms){var m=Math.round(ms/60000); if(m<60) return m+' min'; var h=Math.round(m/60); if(h<48) return h+' h'; return Math.round(h/24)+' days';}
  Promise.all([get('https://plja-corp.pages.dev/live/board.json?t='+Date.now()),get('https://raw.githubusercontent.com/Pdee1077/plja-corp/live-data/board.json?t='+Date.now())]).then(function(p){
    var d=p[1]||p[0];
    if(p[0]&&p[1]&&new Date(p[0].updated)>new Date(p[1].updated)) d=p[0];
    if(!d||!d.rows||!d.rows.length) return;
    var rows=d.rows.filter(clean).sort(function(a,b){return b.st_x_normal-a.st_x_normal;}).slice(0,MAX);
    if(!rows.length) return;
    list.innerHTML=rows.map(function(r){
      return '<li class="mcp-tile '+heat(r.st_x_normal)+'"><span class="mcp-x">'+esc(r.st_x_normal.toFixed(1))+'\u00d7</span><span class="mcp-sym">'+esc(r.sym)+'<small>'+esc(r.name||'')+'</small></span><span class="mcp-why">'+esc(why(r))+'</span></li>';
    }).join('');
    var ms=Date.now()-new Date(d.updated).getTime(), stale=!(ms>=0&&ms<=STALE_MIN*60000);
    box.setAttribute('data-state',stale?'stale':'live');
    if(when) when.textContent='Snapshot '+nice(d.updated_et);
    if(badge) badge.textContent=stale?('Stale \u00b7 '+age(ms)+' old'):('Live \u00b7 '+age(ms)+' old');
  });
})();
</script>"""

def _heat(x): return "h4" if x >= 20 else "h3" if x >= 8 else "h2" if x >= 4 else "h1"

def _why(r):
    p, f = [], " | ".join(r.get("flags") or [])
    m = re.search(r"building (\d+) days in a row", f)
    m2 = re.search(r"Reddit ([\d.]+)x the day before", f)
    if m: p.append(f"building {m.group(1)} days in a row")
    elif m2: p.append(f"Reddit {m2.group(1)}\u00d7 the day before")
    n = r.get("n24") or 0
    if n > 0: p.append(f"{n} headline{'' if n == 1 else 's'} in 24h")
    return " \u00b7 ".join(p) if p else "StockTwits chatter vs its usual"

def clean_rows(board, n=5, min_x=2):
    out = []
    for r in board["rows"]:
        x = r.get("st_x_normal")
        if r.get("group") != "abnormal" or x is None or x < min_x: continue
        if "-" in (r.get("sym") or ""): continue
        if re.search(r"airpods|find my", (r.get("name") or "") + " " + (r.get("sym") or ""), re.I): continue
        if re.search(r"\bIPO\b", " ".join(r.get("flags") or []) + " " + (r.get("name") or "")): continue
        out.append(r)
    out.sort(key=lambda r: -r["st_x_normal"])
    return out[:n]

def nice_when(s):
    s = re.sub(r"^(\w{3})\w*day,", r"\1,", s or "")
    return re.sub(r", 20\d\d,", ",", s)

def panel_html(board, full_href, heading="Market Chatter \u2014 loudest names right now", note_extra=""):
    rows = clean_rows(board)
    e = html.escape
    tiles = "".join(
        f'<li class="mcp-tile {_heat(r["st_x_normal"])}"><span class="mcp-x">{r["st_x_normal"]:.1f}\u00d7</span>'
        f'<span class="mcp-sym">{e(r["sym"])}<small>{e(r.get("name") or "")}</small></span>'
        f'<span class="mcp-why">{e(_why(r))}</span></li>' for r in rows)
    return f'''<section class="mcp" id="mcp" data-state="stale" aria-labelledby="mcp-h">
  <div class="mcp-head">
    <h2 class="mcp-title" id="mcp-h"><span class="dot" aria-hidden="true"></span>{e(heading)}</h2>
    <div class="mcp-meta"><span class="mcp-when">Snapshot {e(nice_when(board.get("updated_et")))}</span><span class="mcp-badge" role="status">Checking&hellip;</span></div>
  </div>
  <ul class="mcp-tiles" aria-label="Names being talked about far more than usual">{tiles}</ul>
  <div class="mcp-foot">
    <p class="mcp-note"><b>StockTwits chatter vs. each name&rsquo;s own usual.</b> Heat: <span class="mcp-legend" aria-hidden="true"><i style="background:#ffe14d"></i><i style="background:#ffc233"></i><i style="background:#ff9a3d"></i><i style="background:#ff5c5c"></i></span> hotter = louder. A lead to check, not a fact. Research and education only. Not investment advice.{note_extra}</p>
    <a class="mcp-btn" href="{full_href}">Open the full board &rarr;</a>
  </div>
</section>'''

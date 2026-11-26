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

.mcp-tile{grid-template-columns:auto 1fr auto;grid-template-areas:"x sym play" "x why play"}
.mcp-play,.mcp-brief{display:none}
.mcp-has-speech .mcp-play,.mcp-has-speech .mcp-brief{display:inline-flex}
.mcp-play{grid-area:play;appearance:none;border:0;background:rgba(26,16,48,.14);color:var(--mcp-ink);width:44px;height:44px;min-width:44px;min-height:44px;padding:0;border-radius:50%;align-items:center;justify-content:center;cursor:pointer;align-self:center;flex:none}
.mcp-play:hover{background:rgba(26,16,48,.22)}
.mcp-play[aria-pressed="true"]{background:#1a1030;color:#ffe14d}
.mcp-play:focus-visible,.mcp-brief:focus-visible{outline:3px solid #ffe14d;outline-offset:3px}
.mcp-play svg,.mcp-brief svg{width:18px;height:18px;max-width:18px;max-height:18px;fill:currentColor;display:block;flex:none}
.mcp-actions{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.mcp-brief{appearance:none;align-items:center;gap:8px;min-height:46px;padding:10px 18px;border-radius:999px;border:2px solid #fff;background:transparent;color:#fff;font:800 1rem/1 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;cursor:pointer}
.mcp-brief:hover{background:#fff;color:#2a0f4a}
.mcp-brief[aria-pressed="true"]{background:#ffe14d;color:#1a1030;border-color:#ffe14d}
.mcp-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
@media(min-width:760px){
  .mcp-tile{grid-template-columns:1fr auto;grid-template-areas:"x play" "sym sym" "why why"}
  .mcp-play{align-self:start}
}
@media(prefers-reduced-motion:reduce){.mcp-title .dot{animation:none}}
@media print{.mcp{display:none}}
"""

JS = r"""<script>
/* MCP_PANEL_V1: fills #mcp from the live board, then optional read-aloud. */
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


(function(){
  var box=document.getElementById('mcp'); if(!box||!window.fetch) return;
  var list=box.querySelector('.mcp-tiles'), when=box.querySelector('.mcp-when'), badge=box.querySelector('.mcp-badge');
  var live=document.getElementById('mcp-live');
  var MIN_X=2, MAX=5, STALE_MIN=90;
  var ICON={
    play:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
    pause:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 5h4v14H6zm8 0h4v14h-4z"/></svg>',
    stop:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6h12v12H6z"/></svg>'
  };
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
  function tileHtml(r){
    var label=esc(r.name||r.sym);
    return '<li class="mcp-tile '+heat(r.st_x_normal)+'" data-sym="'+esc(r.sym)+'">'
      +'<span class="mcp-x">'+esc(r.st_x_normal.toFixed(1))+'\u00d7</span>'
      +'<span class="mcp-sym">'+esc(r.sym)+'<small>'+esc(r.name||'')+'</small></span>'
      +'<span class="mcp-why">'+esc(why(r))+'</span>'
      +'<button type="button" class="mcp-play" aria-pressed="false" aria-label="Play briefing for '+label+'">'+ICON.play+'</button></li>';
  }

  var canSpeak=typeof window.speechSynthesis==='object' && typeof window.SpeechSynthesisUtterance==='function';
  var pauseOk=canSpeak && typeof speechSynthesis.pause==='function' && !/iPhone|iPad|iPod/i.test(navigator.userAgent||'');
  var utter=null, active=null, holding=false;
  function announce(msg){ if(live) live.textContent=msg||''; }
  function pickVoice(){
    var vs=[], all=(speechSynthesis.getVoices&&speechSynthesis.getVoices())||[];
    for(var i=0;i<all.length;i++) if(/^en([-_]|$)/i.test(all[i].lang||'')) vs.push(all[i]);
    var like=/samantha|karen|moira|daniel|alex|allison|ava|susan|tom|google (us|uk)|microsoft (aria|guy|jenny|davis|andrew|emma|sonia)|natural|premium|enhanced/i;
    function ok(v){ return !/compact|eloq|trinoid|organ|zarvox|bad news|bells|boing|bubbles|cellos|good news|hysterical|pipe|whisper/i.test(v.name||''); }
    return vs.filter(function(v){return like.test(v.name||'')&&ok(v);})[0]
      || vs.filter(function(v){return /en-US/i.test(v.lang||'')&&v.localService&&ok(v);})[0]
      || vs.filter(ok)[0] || vs[0] || all[0] || null;
  }
  function resetBtn(btn){
    if(!btn) return;
    btn.setAttribute('aria-pressed','false');
    var isBrief=btn.classList.contains('mcp-brief');
    var label=isBrief?'Play Market Chatter briefing':(btn.getAttribute('aria-label')||'').replace(/^(Pause|Resume|Stop) /,'Play ');
    if(!/^Play /.test(label) && !isBrief){
      var tile=btn.closest('.mcp-tile'); var name=tile&&box._mcp?((box._mcp.bySym[tile.getAttribute('data-sym')]||{}).name||tile.getAttribute('data-sym')): '';
      label='Play briefing for '+(name||'this name');
    }
    btn.setAttribute('aria-label', isBrief?'Play Market Chatter briefing':label);
    var icon=btn.querySelector('svg'); var html=ICON.play;
    if(isBrief){
      var lbl=btn.querySelector('.mcp-brief-lbl'); if(lbl) lbl.textContent='Play briefing';
      btn.innerHTML=html+'<span class="mcp-brief-lbl">Play briefing</span>';
    } else {
      btn.innerHTML=html;
    }
  }
  function mark(btn, state){ // playing | paused
    var isBrief=btn.classList.contains('mcp-brief');
    btn.setAttribute('aria-pressed','true');
    var verb=state==='paused'?'Resume':(pauseOk?'Pause':'Stop');
    var what=isBrief?'Market Chatter briefing': (btn.getAttribute('aria-label')||'').replace(/^(Play|Pause|Resume|Stop) briefing for /,'');
    if(!isBrief && /^Play /.test(btn.getAttribute('aria-label')||'')) what=(btn.getAttribute('aria-label')||'').replace(/^Play briefing for /,'');
    btn.setAttribute('aria-label', verb+(isBrief?' Market Chatter briefing':' briefing for '+what));
    var icon=state==='paused'?ICON.play:(pauseOk?ICON.pause:ICON.stop);
    if(isBrief){
      var text=state==='paused'?'Resume briefing':(pauseOk?'Pause briefing':'Stop briefing');
      btn.innerHTML=icon+'<span class="mcp-brief-lbl">'+text+'</span>';
    } else btn.innerHTML=icon;
  }
  function stopTalk(){
    holding=false;
    try{ speechSynthesis.cancel(); }catch(e){}
    if(active) resetBtn(active);
    active=null; utter=null;
    announce('');
  }
  function speak(text, btn){
    if(!canSpeak) return;
    if(active===btn && speechSynthesis.speaking && !speechSynthesis.paused && pauseOk){
      try{ speechSynthesis.pause(); }catch(e){}
      mark(btn,'paused'); announce('Paused');
      return;
    }
    if(active===btn && speechSynthesis.paused && pauseOk){
      try{ speechSynthesis.resume(); }catch(e){}
      mark(btn,'playing'); announce('Playing briefing');
      return;
    }
    if(active===btn && speechSynthesis.speaking && !pauseOk){ stopTalk(); return; }
    stopTalk();
    holding=true;
    var u=new SpeechSynthesisUtterance(text);
    var v=pickVoice();
    if(v){ u.voice=v; u.lang=v.lang; } else u.lang='en-US';
    u.rate=1.12; u.pitch=1; u.volume=1;
    u.onend=function(){ if(utter===u){ if(active) resetBtn(active); active=null; utter=null; announce(''); } };
    u.onerror=function(ev){ if(utter!==u) return; if(ev&&ev.error==='interrupted') return; stopTalk(); announce("Couldn't play the briefing in this browser."); };
    utter=u; active=btn;
    mark(btn,'playing'); announce('Playing briefing');
    // Chrome can drop speak() if it follows cancel() in the same turn.
    setTimeout(function(){ if(holding && utter===u) speechSynthesis.speak(u); }, 40);
  }
  function scriptFor(btn){
    var B=window.ChatterBriefing, data=box._mcp;
    if(!B||!data) return '';
    if(btn.classList.contains('mcp-brief')) return B.briefing(data.board);
    var tile=btn.closest('.mcp-tile'); if(!tile) return '';
    var row=data.bySym[tile.getAttribute('data-sym')];
    return row?B.tileLine(row):'';
  }
  if(canSpeak){
    box.classList.add('mcp-has-speech');
    if(speechSynthesis.getVoices) { speechSynthesis.getVoices(); speechSynthesis.addEventListener('voiceschanged', function(){ pickVoice(); }); }
    box.addEventListener('click', function(e){
      var btn=e.target.closest('.mcp-play, .mcp-brief');
      if(!btn||!box.contains(btn)) return;
      e.preventDefault();
      var text=scriptFor(btn); if(!text) return;
      speak(text, btn);
    });
    document.addEventListener('keydown', function(e){ if(e.key==='Escape' && (utter|| (speechSynthesis.speaking||speechSynthesis.paused))) { stopTalk(); } });
  }

  Promise.all([get('https://plja-corp.pages.dev/live/board.json?t='+Date.now()),get('https://raw.githubusercontent.com/Pdee1077/plja-corp/live-data/board.json?t='+Date.now())]).then(function(p){
    var d=p[1]||p[0];
    if(p[0]&&p[1]&&new Date(p[0].updated)>new Date(p[1].updated)) d=p[0];
    if(!d||!d.rows||!d.rows.length) return;
    var rows=d.rows.filter(clean).sort(function(a,b){return b.st_x_normal-a.st_x_normal;}).slice(0,MAX);
    if(!rows.length) return;
    list.innerHTML=rows.map(tileHtml).join('');
    var ms=Date.now()-new Date(d.updated).getTime(), stale=!(ms>=0&&ms<=STALE_MIN*60000);
    box.setAttribute('data-state',stale?'stale':'live');
    if(when) when.textContent='Snapshot '+nice(d.updated_et);
    if(badge) badge.textContent=stale?('Stale \u00b7 '+age(ms)+' old'):('Live \u00b7 '+age(ms)+' old');
    var bySym={}; rows.forEach(function(r){ bySym[r.sym]=r; });
    box._mcp={board:d, rows:rows, bySym:bySym, stale:stale, ageMs:ms};
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
    play = '<button type="button" class="mcp-play" aria-pressed="false" aria-label="Play briefing for {name}">{icon}</button>'
    icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>'
    tiles = "".join(
        f'<li class="mcp-tile {_heat(r["st_x_normal"])}" data-sym="{e(r["sym"])}">'
        f'<span class="mcp-x">{r["st_x_normal"]:.1f}\u00d7</span>'
        f'<span class="mcp-sym">{e(r["sym"])}<small>{e(r.get("name") or "")}</small></span>'
        f'<span class="mcp-why">{e(_why(r))}</span>'
        f'{play.format(name=e(r.get("name") or r["sym"]), icon=icon)}</li>' for r in rows)
    return f'''<section class="mcp" id="mcp" data-state="stale" aria-labelledby="mcp-h">
  <div class="mcp-head">
    <h2 class="mcp-title" id="mcp-h"><span class="dot" aria-hidden="true"></span>{e(heading)}</h2>
    <div class="mcp-meta"><span class="mcp-when">Snapshot {e(nice_when(board.get("updated_et")))}</span><span class="mcp-badge" role="status">Checking&hellip;</span></div>
  </div>
  <ul class="mcp-tiles" aria-label="Names being talked about far more than usual">{tiles}</ul>
  <div class="mcp-foot">
    <p class="mcp-note"><b>StockTwits chatter vs. each name&rsquo;s own usual.</b> Heat: <span class="mcp-legend" aria-hidden="true"><i style="background:#ffe14d"></i><i style="background:#ffc233"></i><i style="background:#ff9a3d"></i><i style="background:#ff5c5c"></i></span> hotter = louder. A lead to check, not a fact. Research and education only. Not investment advice.{note_extra}</p>
    <div class="mcp-actions">
      <button type="button" class="mcp-brief" aria-pressed="false" aria-label="Play Market Chatter briefing">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>
        <span class="mcp-brief-lbl">Play briefing</span>
      </button>
      <a class="mcp-btn" href="{full_href}">Open the full board &rarr;</a>
    </div>
  </div>
  <p class="mcp-sr" id="mcp-live" role="status" aria-live="polite"></p>
</section>'''

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


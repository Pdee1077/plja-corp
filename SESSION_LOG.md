# Session log — PLJA Corp first-draft site

## 22 November 2026, America/New_York

- Noted PLJA Corp as Pete De Paola’s company name (matches X @PLJA_AI). Did not register a legal entity and did not claim one on the site.
- Checked `pljacorp.com` with a Verisign RDAP lookup: HTTP 404, no registration record at that moment. Did not buy it. Public November 2026 recordings of Cloudflare Registrar’s at-cost `.com` price are $11.17/year; no checkout was run.
- Confirmed `plja.analogarcade.net` has no DNS record (NXDOMAIN). Did not add one.
- Hosting of `analogarcade.net`: Cloudflare zone; hub is Pages project `analogarcade` (GitHub `Pdee1077/AnalogArcade`); product apps on Workers custom domains (`house-binder`, `church-mass-finder`, `card-grader`) or hub paths (`/houseradar/`, `/write-notes/`).
- Verified live product facts (US App Store iTunes lookup for artist 6804326068, plus live pages, all HTTP 200 unless noted):
  - House Binder — https://binder.analogarcade.net/ (redirects to `/start`), described as free on the live page; privacy and support pages 200.
  - House Radar — App Store 1.10, $2.99 once, released 21 Nov 2026, 5:19 PM ET; iOS 16+; guide at https://analogarcade.net/houseradar/ (the guide still mentions iOS 17 / iPhone XR; the live store listing and 1.10 notes were used instead).
  - Local Mass Finder — App Store 1.1.1, Free, released 19 Nov 2026, 12:15 PM ET; web app https://church.analogarcade.net/ showed v2.33.44, updated Sat 21 Nov 2026, 9:34 AM Eastern.
  - Keysong — App Store 1.0.6, Free, released 16 Nov 2026, 6:05 PM ET; 34 songs in the live listing; browser preview https://analogarcade.net/write-notes/; Gumroad zip 200.
  - Card Check — https://cards.analogarcade.net/ 200; privacy 200; `/support` 404; no price shown.
- Built a static first-draft site in a new repo, with a made-in-house PLJA wordmark, product cards, about, contact (placeholder email flagged), privacy, and support pages.
- Deployed only to a Cloudflare Pages `*.pages.dev` preview. No custom domain, no DNS change, no App Store / X / Gumroad edits, no purchases.

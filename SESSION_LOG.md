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

## 25 November 2026, America/New_York

- Added a public Daily Scan section at `/daily/` and `/daily/2026-11-25/` (version 2026.11.25.1, published 10:05 AM ET). The pages use only public market data, carry a research/education disclaimer, and do not include a Yahoo-sourced chart.
- `robots.txt` now allows indexing on `/daily/` and `/assets/` only. Daily pages have Open Graph title, description and image.
- Each Daily page has a footer section linking to Analog Arcade and its apps, with `utm_source=plja_daily`.
- Deployed to the existing Cloudflare Pages preview (`plja-corp.pages.dev`) only. No custom domain and no DNS change.

## 25 November 2026, later the same morning, America/New_York

- Added a public Live Scanner at `/live/` (page version 2026.11.25.2, published 10:20 AM ET). It shows tickers, talk counts, x-normal, price moves and NO NEWS flags only, with the research/education disclaimer. No analyst notes, no prepared answers, and no copied social posts.
- The private board and daily.analogarcade.net were not opened up. The scheduled scanner job on the office computer was not changed.
- Refresh path ($0): a GitHub Action on this public repo tries to run every 15 minutes on weekdays, writes a scrubbed `board.json` to the `live-data` branch, and the public page fetches that file. GitHub can delay scheduled runs. The first snapshot is also shipped with the page so it has data if the fetch is late.

## 25 November 2026, evening, America/New_York

- Site-wide redesign, version 2026.11.25.4: shared design system (`scripts/theme.py`), light/dark, Jump page finder, version + Eastern timestamp in every footer, versioned CSS file names.
- Home: five-second hero (what PLJA Corp is, three doors: Apps, Daily Scan, Live board), app-icon mosaic, live-board snapshot strip. Apps page: filter by Free / iPhone & iPad / Mac / Web, fine print folded into Details.
- Daily: summary card with key numbers, table of contents, archive list and calendar, copy/share/print, per-day share image. Content moved to `content/daily/` unchanged.
- Live: sortable, filterable board, heat bars for talk vs normal, Reddit sparklines from `history.csv`, "what changed since your last look" (stored in the browser only), status bar with Eastern snapshot time, age, market-hours note, auto-refresh every 5 minutes with a countdown, mobile card layout.
- Fixed `_headers`: the site-wide CSP was also sent on /live/ and blocked the fetch from raw.githubusercontent.com, so the board only ever showed the bundled snapshot. Cache-Control on /assets/ and /live/ was being joined with the site default; both now detach and set one value.
- Found the "Refresh live scanner" workflow is disabled (state `disabled_manually`, changed 4:38 PM ET today). Did not re-enable it; that needs Pete's yes. The board shows its snapshot age and says when the refresh looks paused.
- Did not change `live_board.py`, the workflow file, the data format, any account, DNS, or domain.

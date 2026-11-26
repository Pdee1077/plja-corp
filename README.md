# PLJA Corp

First-draft company website for **PLJA Corp**, the company name Pete De Paola uses for the apps he makes.

This is a static site. The public shop remains [Analog Arcade](https://analogarcade.net/).

## Preview only

The live preview is intended at `https://plja-corp.pages.dev`. That URL is a Cloudflare Pages project with **no custom domain**.

Do **not** attach `plja.analogarcade.net` or change DNS until Pete says yes.

`pljacorp.com` looks unregistered. Do **not** buy it until Pete says yes.

## Pages

- `/` — home
- `/products/` — House Binder, House Radar, Local Mass Finder, Keysong, Card Check
- `/about/`
- `/contact/` — company email is a flagged placeholder
- `/privacy/` — this website, plus links to each product’s own privacy page
- `/support/` — App Store support URL; lists the product addresses already on the live sites
- `/daily/` and `/daily/YYYY-MM-DD/` — the public PLJA Daily Scan (chatter vs. normal, odd moves, news flags). These pages are written to be indexed. The rest of this preview site is disallowed in `robots.txt`.
- `/live/` — the public live scanner (chatter vs. normal, price moves, NO NEWS flags). It loads a snapshot from the `live-data` branch, which a free weekday GitHub Action tries to refresh every 15 minutes. The private office board is not on this site.

Overhead and Vanish Cam are excluded on purpose from the products list. The Daily Scan page links to Analog Arcade, including Overhead and Kept.

## Design system (v2026.11.25.4)

All pages render through `scripts/theme.py`: one header, footer, type scale, light/dark theme (follows the device, with a toggle saved only in the browser), a "Jump" page finder (press `/` or Ctrl/Cmd+K), and a footer stamp with the site version and the Eastern build time. CSS file names carry the version (`/assets/css/plja-<version>.css`) because `/assets/*` is cached for a year, so bump `theme.VERSION` on every release. No frameworks, no third-party scripts, no paid fonts.

- Daily Scan: each day is a `DAYS` entry in `scripts/build_daily.py` plus three fragments in `content/daily/` (`.short`, `.index`, `.body`). The builder adds the summary card, table of contents, archive calendar, share buttons, older/newer links and a per-day share image (`/assets/img/daily-<date>-og.png`).
- Live board: `scripts/build_live.py` builds the page only. Data still comes from `board.json` and `history.csv` on the `live-data` branch, written by `scripts/live_board.py` through the GitHub Action; the format is unchanged. The build also copies the newest `live-data` snapshot into `public/live/board.json` as the bundled fallback.

## Local build

```bash
python3 scripts/build_site.py
```

Output is in `public/`. Fonts need the `brotli` Python package for WOFF2 subsetting.

## Deploy (preview project only)

```bash
npx wrangler pages deploy public --project-name=plja-corp
```

Do not add a custom domain in that command or in the Cloudflare dashboard.

## Facts

Copy on the site was checked against live product pages and the US App Store (iTunes Search API) on 22 November 2026, America/New_York. See `APP-PRESENCE-PLAN.md` for the App Store seller-name plan and domain options.

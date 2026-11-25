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

Overhead and Vanish Cam are excluded on purpose from the products list. The Daily Scan page links to Analog Arcade, including Overhead and Kept.

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

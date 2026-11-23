# PLJA Corp app-presence plan

Drafted 22 November 2026, America/New_York. Nothing in this plan has been changed in App Store Connect, on X, on Gumroad, or in DNS.

The company website first draft lives in this repo and is preview-only at `https://plja-corp.pages.dev` (or the `*.pages.dev` URL returned by the deploy). It is not on `plja.analogarcade.net`.

## What is already true today

- App Store seller name: **Peter De Paola**, artist ID `6804326068`, enrolled as an **Individual**. Developer page: https://apps.apple.com/us/developer/peter-de-paola/id6804326068
- Three live App Store apps, all checked on the US store on 22 November 2026, America/New_York:
  - **House Radar** 1.10, $2.99 once, https://apps.apple.com/us/app/house-radar/id6816271323 — marketing URL already `https://analogarcade.net/houseradar/`
  - **Local Mass Finder** 1.1.1, Free, https://apps.apple.com/us/app/local-mass-finder/id6825162225 — marketing URL already `https://church.analogarcade.net/`
  - **Keysong** 1.0.6, Free, https://apps.apple.com/us/app/keysong/id6804326066 — marketing URL already `https://analogarcade.net/write-notes/`
- House Binder and Card Check are live on the web only. They are not among those three App Store apps.
- We do **not** know whether PLJA Corp is legally registered. This site does not claim that it is.

---

## (a) Showing “PLJA Corp” as the App Store seller

Apple lists an Individual member’s personal legal name as the seller. To show an organization name instead, the membership has to be updated from Individual to Organization. A sole proprietor or single-person business that is not a separate legal entity stays an Individual, and the personal legal name stays on the store. Apple does not accept a DBA, trade name, fictitious business, or branch as an Organization seller.

Official references:

- [Program enrollment](https://developer.apple.com/help/account/membership/program-enrollment/)
- [Updating your account information](https://developer.apple.com/help/account/membership/updating-your-account-information/)
- [D-U-N-S Number](https://developer.apple.com/help/account/membership/D-U-N-S/)

### Exact steps (none of these should be started without Pete’s yes)

1. **Confirm the legal entity.** If PLJA Corp is only a name in use, Apple will not list it as the seller. Pete would need a recognized legal entity (for example a corporation or LLC) whose *legal* name is the name that should appear as seller — for example `PLJA Corp` only if that is the filed name. We have not checked any state filing. This is the blocker.
2. **Get a free D-U-N-S number** from Dun & Bradstreet, registered to that legal entity (not a DBA). [Look it up first](https://developer.apple.com/enroll/duns-lookup/); if there is none, request one. Apple says to allow up to **5 business days** for D&B to issue it, then up to **2 business days** for Apple to receive it. Expediting through D&B does not shorten Apple’s wait. D&B may call to verify.
3. **Put a real company website on a domain associated with the organization.** Apple requires the site to be publicly available and functional. Social pages, parked registrar pages, or thin placeholder pages are not accepted. A work email must use the organization’s domain. `plja.analogarcade.net` can host the site quickly, but a company domain such as `pljacorp.com` plus an address like `…@pljacorp.com` is the stronger match for this requirement (see domain options below). The preview URL is not the one to submit to Apple.
4. **Submit the membership update (Account Holder only).** Apple’s instructions: sign in at [developer.apple.com/account](https://developer.apple.com/account), go to membership details, submit a request to update the information, and choose to switch to organization membership. Pete must be the founder or co-founder and provide the organization’s D-U-N-S number. Apple may ask for business documents to verify the organization’s identity.
5. **Wait for Apple’s review.** Timing varies. Apple does not publish a fixed number of days on the official update page. Do not change other account settings while this is open.
6. **After approval**, the legal entity name becomes the seller on the App Store. Existing apps stay on the same membership; this is a conversion of the current account, not a plan to create a second paid membership. If Apple later asks for another fee, stop and confirm with Pete before paying. A later change of organization name would update the vendor name across all apps and reset `identifierForVendor` (IDFV) for existing users — only relevant once the account is already an Organization.

### What Pete must supply

- Whether PLJA Corp is already a filed legal entity, and if so the exact legal name, formation state, and business address.
- If it is not filed: whether he wants to form one, and under which name. That is a legal step we should not take for him.
- The D-U-N-S number once it exists (or a yes to start the free D&B lookup / request in his name).
- The public website URL and a work email on that same organization domain.
- Formation or identity documents if Apple asks for them.
- An explicit yes before anyone submits the Apple request.

No App Store account settings should be changed until that yes is in hand.

---

## (b) What can point at the PLJA site today — propose only, do not change

These can be pointed at the company site **after** the site is on a stable public host (the subdomain or `pljacorp.com`), not while it only lives on a `*.pages.dev` preview, unless Pete wants the preview used temporarily.

### App Store Connect, per app (propose, do not edit)

Keep the product marketing pages as the marketing URLs where they already help a shopper. Use the company site for support, and as a second door into the set of apps.

| App | Marketing URL today (from the live iTunes record) | Proposed support URL | Proposed privacy URL | Notes |
|---|---|---|---|---|
| House Radar | https://analogarcade.net/houseradar/ (keep) | https://[host]/support/ | Keep https://analogarcade.net/houseradar/privacy/ (product-specific) | Company privacy page links here. |
| Local Mass Finder | https://church.analogarcade.net/ (keep) | https://[host]/support/ or keep https://church.analogarcade.net/support | Keep https://church.analogarcade.net/privacy | Both product pages already exist and load. |
| Keysong | https://analogarcade.net/write-notes/ (keep) | https://[host]/support/ | Keep https://analogarcade.net/write-notes/privacy/ | Product privacy page already exists and loads. |

`[host]` should be the approved public host (`plja.analogarcade.net` or `pljacorp.com`), not the preview, when these are actually changed.

Optional later: add the company products page as a “marketing” alternative only if Pete wants the seller presence to lead with PLJA Corp rather than the product guide. The product guides are better for conversion today.

House Binder already has https://binder.analogarcade.net/support and /privacy. Card Check has /privacy; /support returned 404 on 22 November 2026. If Card Check later needs a support URL, the company `/support/` page can fill that gap, or a product support page can be added in the Card Check repo — not in this task.

### X @PLJA_AI bio link (propose only)

Do not edit the bio. Once the site is on the approved host, a short bio plus that URL would make the company name and the site match. Suggested shape, for Pete to edit himself or to approve as exact text later:

> Solo maker of local-first apps. House Binder, House Radar, Local Mass Finder, Keysong, Card Check. [host]

No post and no bio change in this task.

### Gumroad (propose only)

The store at https://analogquantum.gumroad.com/ is branded AnalogQuant. Keysong’s optional zip is already at https://analogquantum.gumroad.com/l/writenotes (HTTP 200). After the company site is on a stable host, a profile or store description *could* add a line such as “Company site: [host]” without renaming the Gumroad brand. Do not change Gumroad until Pete says yes. This plan does not recommend moving listings.

---

## (c) Domain options and recommendation

### How analogarcade.net is hosted today

Checked 22 November 2026, America/New_York, against the existing Cloudflare inventory and live DNS:

- The zone `analogarcade.net` is on Cloudflare (nameservers `nick.ns.cloudflare.com` and `rosalie.ns.cloudflare.com`), Free plan, account used for Analog Arcade / AnalogQuant.
- The hub `analogarcade.net`, `www`, `next`, and `chino` are a **Cloudflare Pages** project named `analogarcade`, connected to GitHub `Pdee1077/AnalogArcade`, branch `main`.
- Product subdomains are mostly **Workers custom domains** on the same account: `binder.analogarcade.net` → Worker `house-binder`; `church.analogarcade.net` → Worker `church-mass-finder`; `cards.analogarcade.net` → Worker `card-grader`.
- House Radar’s guide and Keysong’s browser preview are **paths on the hub Pages site**: `/houseradar/` and `/write-notes/`.
- `plja.analogarcade.net` has **no DNS record** today (NXDOMAIN). It is free to add later as a Pages custom domain on this new project, but that step is waiting on Pete’s yes. This draft does not add it.

### `plja.analogarcade.net`

- Cost: none. Pete already owns `analogarcade.net`.
- Can be a custom domain on the new Pages project after approval.
- Matches the way other products are named.
- Weaker as the *only* company presence for an Apple Organization enrollment, because Apple wants a website and a work email whose domain is associated with the organization. A subdomain of the Analog Arcade shop may be questioned, or it may be accepted — that is Apple’s call, not something to assume.

### `pljacorp.com`

- Availability: a Verisign RDAP lookup for `pljacorp.com` returned HTTP 404 on 22 November 2026, which means there is no registered domain record in that registry lookup. That is not a purchase, and availability can change.
- Price: Cloudflare Registrar sells domains at cost. Third-party recordings of Cloudflare’s official price list in November 2026 show **$11.17 a year** for a `.com` (register, renew, or transfer; ICANN fee included). We did not run a checkout, so tax or a later registry change could make the amount at payment slightly different. Do not buy it yet.
- Stronger for Apple Organization enrollment: a company website and a work email on `pljacorp.com` match Apple’s “domain associated with the organization” language more cleanly.

### Recommendation

1. Keep this first draft on the `*.pages.dev` preview until Pete says the design is good enough.
2. When he says yes to going live, attach **`plja.analogarcade.net`** first. It costs nothing, can be live the same day, and is enough for people and for App Store support / marketing URLs.
3. **Register `pljacorp.com` only when Pete is ready to form or confirm the legal entity** and, later, to migrate the Apple seller name. At that point the company site can move to or redirect from the `.com`, and a work email can be created on that domain. Do not buy the name just to park it unless Pete wants that protection; if he does, confirm the exact checkout total first.

No domain will be purchased, and no DNS will be changed, until Pete says yes.

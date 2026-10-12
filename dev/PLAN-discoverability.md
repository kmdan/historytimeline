# Plan: findable by search engines and AI agents (2026-10-12)

**Status 2026-10-12: phases 1–6 done** (tests: `dev/test/links.py`; preview image: `dev/test/og.py`). Phase 7 is the owner's part; WebMCP and era pages are open.
Phase 2 needed less than planned: the footer already listed all sources in plain HTML; it got an "About the data" heading (`#about-data`).

Goal: people who search for "world map 4500 BCE", "history timeline interactive", "ice age coastlines map" etc.
find the site, and AI answer engines / browser agents can read, cite and link to it.
Canonical home: https://kmdan.github.io/historytimeline/karahan-era.html (GitHub Pages, indexable).
The claude.ai artifact stays the same page but points its canonical at GitHub Pages.

Order = value per effort. Each phase is one commit, tested with `dev/test/check.py` + `touch.py`, then pushed and republished.

## Phase 1 — Page head (≈30 min)
Today: `<title>Karahan Era</title>` sits in `<body>`; no `lang`, description, canonical, social tags.
- `<html lang="en">`; move `<title>` into `<head>`.
- Title: "Karahan Era: interactive world history timeline & atlas, 40,000 BCE to today".
- `<meta name="description">` (~155 chars: what it is + coastlines, ice, states, 200k dated sites).
- `<link rel="canonical">` → GitHub Pages URL (static, in raw HTML, not set by JS).
- Open Graph + Twitter card: `og:title/description/url/image/type=website`, `twitter:card=summary_large_image`.
- `atlas/og.png` 1200×630 preview: screenshot of the map at ~4500 BCE (made by a headless Playwright script, like the tests).
- Check: the artifact publish keeps these tags (read the published page back).

## Phase 2 — Text that crawlers and AI bots can read without JavaScript (≈45 min)
Most AI crawlers do not run JS, and canvas content is just pixels to them.
- Short lead paragraph right under the `<h1>`: one sentence on what the page is, one on what you can do.
  (Answer first: this is the passage AI answers will quote.)
- "About the data" section at the foot, plain HTML: the sources table from README (dataset, author/year, licence)
  and the caveat "figures before 1800 are scholarly estimates". Merge with the existing credits rather than duplicate them.
- `<noscript>` line: "This interactive map needs JavaScript; the data sources are listed below."
- Check: `curl` the page, strip tags, confirm the lead + sources are in the raw HTML.

## Phase 3 — Structured data (≈20 min)
One `<script type="application/ld+json">` block in the head (schema.org):
- `WebApplication` (+ `isAccessibleForFree`, `applicationCategory: EducationalApplication`, `inLanguage`, `license` MIT, `author`).
- `about`: world history, prehistory, palaeoclimate. `isBasedOn`: the main datasets as `Dataset` entries with their DOIs.
- Check: Google Rich Results Test / schema.org validator (manual paste, no login needed).

## Phase 4 — Deep links `?y=…&at=…` (≈1.5 h, the biggest single gain)
Today only `?cpu` is read from the URL, so every link opens at the same view.
- On load: read `y` (signed civil year, e.g. `-4500`, `1750`) → same path as the `#go` form (`ke()` → `animateTo`).
  Optional `at=lat,lon,zoom` for the map view.
- While scrubbing: update the address bar with `history.replaceState` (throttled, no history spam),
  so copying the URL always shares the current view. Keep `?cpu` and the hash untouched.
- Invalid or out-of-range values are ignored (open at the default view).
- Canonical stays the bare URL (Phase 1); deep links are for sharing and agents, not separate indexed pages.
- Tests: add to `check.py`: open `?y=-4500` and `?y=1750&at=48,10,4`, assert `#ph`/`#atlasYear`; the URL updates after a scrub.

## Phase 5 — Crawler files (≈20 min)
- `robots.txt`: allow everything (incl. AI search + user-fetch bots), `Sitemap:` line.
  The training-bot choice (allow/block GPTBot, ClaudeBot, Google-Extended, CCBot) is an open decision; the default is allow.
- `sitemap.xml`: the one canonical URL with `lastmod`.
- `llms.txt`: ~20 lines: what the site is, the deep-link format, where the open data lives
  (`atlas/c14.json`, `atlas/cp/index.json`, …) with licences, link to the README. Cheap; adoption unproven.
- Note: GitHub Pages serves these only at `/historytimeline/…`, not the domain root, so Google and Bing ignore
  the robots.txt (they only read it at the root); the sitemap still works when submitted in Search Console.

## Phase 6 — Agent- and screen-reader-friendly controls (≈30 min)
Browser agents read the accessibility tree (like screen readers).
- `role="img"` + `aria-label` on the map and timeline canvases, updated in `update()` with the year
  (e.g. "World map, 4500 BCE: coastlines, ice, states"). Throttled, no `aria-live` spam.
- Give unlabelled buttons/inputs a name; make the era buttons and layer toggles say what they do.
- Check: `read_page` accessibility tree in the built-in browser lists the map with its year.

## Phase 7 — Your part (accounts I can't use)
- Google Search Console: add property `https://kmdan.github.io/historytimeline/` (HTML-tag verification;
  I add the meta tag you get), submit `sitemap.xml`, "Request indexing".
- Bing Webmaster Tools: import from Search Console (Bing also feeds ChatGPT search and DuckDuckGo).
- Links (biggest ranking factor for a new site): README badge/link, a post on r/MapPorn, "Show HN",
  a note to the dataset teams (Seshat/Cliopatria, De Groeve, PaleoMIST) who sometimes list users of their data.

## Later / optional
- WebMCP tools (`document.modelContext`, feature-detected): `go_to_year`, `events_near(year, region)`,
  `what_is_at(lat, lon, year)`. Experimental standard (Chrome origin trial, API renamed in 2026); revisit when stable.
- Pre-rendered era pages (e.g. `/era/neolithic.html` with text + a static map image + link into the app):
  would rank for era-specific searches; bigger job.

## Not doing
- `<meta keywords>` (ignored by Google). Changing the projection or the app UI for SEO.

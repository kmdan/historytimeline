# Karahan Era — project guide for Claude

Interactive deep-time world timeline + atlas, published as a claude.ai artifact.
Owner: Daniel (VFX/pipeline TD; fluent in Python, not a web developer).

## Communication rules
- **End every message to the user with a clearly separated "Open questions / decisions" section** listing what needs their input (numbered, each with a recommended option). If nothing is open, say "No open decisions."
- The page already works; work here is about **improvements**, not repair. Don't frame findings as bugs unless they are.
- Explain web/graphics concepts briefly in plain terms; Python analogies are welcome.

## Where things are
- `karahan-era.html` — the whole page (inline CSS/JS, embedded JSON data blocks). Very long lines (embedded JSON): read with offset/limit, search with Grep.
- `atlas/` — map rasters and data files loaded by the page (`terrain.png`, `ice.png`, `biome0-2.png`, `coast.json`, `rivers.json`, `c14.json`, `hb/*.json`).
- `dev/HANDOFF.md` — architecture, data encodings, conventions (read it before structural changes).
- `dev/NOTES.md` — short summary. `dev/RESEARCH-atlas-rendering.md` — rendering options research (WebGL recommendation).
- `dev/scripts/*.py.txt` — Python build scripts for atlas data (rename to `.py` to run). `dev/data/` — raw research JSON.

## Publishing
- Live artifact: https://claude.ai/artifact/EVCozfzuxXvmWzggiSg216 — **always republish to this same url** (link must stay stable; it is shared "anyone with the link").
- Publish = Artifact publish with `url` + `file_path: karahan-era.html`; pass `files` only for changed supporting files (unlisted ones are kept); omit `icon`.
- Before publishing, read the live artifact if it may have changed since last read (the tool refuses otherwise).
- Parallel sessions publish too, sometimes with commits not yet on GitHub: after reading the live artifact, compare it with the local file (e.g. `#ly*` ids, `<script id=…>` blocks) and don't publish over features missing locally — pull or coordinate first (2026-10-13: a publish once dropped the plague layer this way).
- User approved (2026-10-11): republish after each **tested** improvement without asking. Commit to git first; mention each publish in the reply.
- GitHub Pages (2026-10-12, repo public): https://kmdan.github.io/historytimeline/ serves `master` root; `index.html` redirects to `karahan-era.html`, `.nojekyll` disables Jekyll. Updates go live on push.
- Artifact runtime limits: no external fetch/images at runtime (CSP); scripts only from cdnjs / jsdelivr / unpkg with exact versions; everything else ships as files beside the page. **One artifact version holds at most 511 files** (one publish sends at most 255): pack many small files (e.g. sprite sheets, as `atlas/pimg/`) instead of adding hundreds.

## Testing
- Local server: `.claude/launch.json` config `karahan` (python http.server on 8765) → open `http://localhost:8765/karahan-era.html` in the built-in browser.
- **Preferred: headless Playwright with the installed Edge** (works even when the browser pane is hidden — the pane stops rendering/rAF when hidden):
  - `python dev/test/check.py <outdir>` — errors, GPU vs `?cpu` pixel diff at 5 years (must be ~0), scrub long tasks, screenshots (dark/light/phone). Uses SwiftShader, so its timings are NOT representative.
  - `python dev/test/touch.py <outdir>` — emulated phone + tablet: swipe over map/timeline scrolls the page, sideways swipe travels, pinch zooms the map, tapped popups stay open, fit and have reachable links (raw CDP touch events; synthesizeScrollGesture does not scroll headless).
  - `python dev/test/flicker.py [page] [latency_ms]` — border-layer dropouts while scrubbing with simulated network latency (must be 0).
  - `python dev/test/links.py` — deep links `?y=&at=`, address bar following the view, head tags / JSON-LD / text readable without JS.
  - `python dev/test/og.py [year]` — regenerates the social preview `atlas/og.png` (1200×630).
  - `python dev/test/tours.py` — guided tours (menu, steps, back, auto, deep link, search). `python dev/test/play_search.py` and `python dev/test/place.py` — play button, search box, "What happened here?" + play-from-here (desktop + phone). All test scripts take `KE_BASE=http://localhost:PORT/` to test another server/worktree.
  - `python dev/test/profile.py [?cpu]` — CPU profile of a scrub on the real GPU (RTX 3070); use this for performance numbers.
- All JS lives in one IIFE (no globals): drive via UI (`#goY`/`#goU`/`#go` form, buttons, pointer events on `#tl`), read `#ph`, `#mapinfo`, `#eName`, `#pop`, `#map[data-renderer]` (`webgl2` or `cpu`).
- Touch model: one finger scrolls the page over the map (two fingers pan/zoom it); timeline/chart take sideways drags; popups are a bottom sheet on touch/narrow screens; `leave`/hover handlers are mouse-only.
- Check each change at several years (e.g. 21000 BCE, 4500 BCE, 900 CE, 1750, 2020), light + dark, mobile 375 px (no horizontal page scroll), console errors.
- Base map (2026-10-13, screen resolution): the WebGL2 shader (`GLB`) evaluates the old per-cell rules in `cellAt()` — these must still match the CPU `buildBase` loop (change both). Zoomed out (world ≤ 4320 device px wide) it renders the whole world at 2160/4320 px and the canvas scales it (GPU ≈ CPU: check.py mean diff ≈ 0.5–2, the rest is ETOPO vs old relief shading once elev.webp has loaded); zoomed in (cells > 2 px) it renders only the view (`view` uniforms `uV`,`uH`) at device resolution: each pixel blends its 4 cells with noise jitter (`J1/J2`, organic edges, `bo` offsets the 0.5° vegetation lookup), refines the coast inside mixed land/sea cells with ETOPO elevation (`eAt − eLo`, ±40 m) and shades relief from ETOPO (`hill()`, `RELZ/RELK`). The CPU fallback (`?cpu`, context loss) stays the coarse 1/6° image — an approximation when zoomed in, by design (user-approved).
- Painted map (2026-10-13, default; checkbox `#lyPaint`, `LY.paint`): GPU-only Hal Shelton-like style in the same shader (`uPaint`): palette `PAINT` (classes 0–10 + farm/cleared/sea/shadow/light/rock/snow), farmland and forest as continuous tints (no dither), sea colour by ETOPO depth below the sea level of the time, snow line `3100 − 95·(|lat|−42) + 154·ΔT` m, warm light / green-grey shadows, ×0.8 in dark theme. `legendPaint()` swaps the legend swatches. Unchecked (or CPU fallback) = Classic colours.
- Close-zoom detail (2026-10-13): `build_dem_tiles.py` → `atlas/dem/t<col>_<row>.webp` (71 tiles, 30°×30° at 1′, 1800 px, value 128 + (ETOPO − bilinear elev.webp)/8 m, WebP q90, ~19 MB) + `index.json`. `demFor(view)` (views < 45° wide) loads the tiles in view and stitches one R8UI patch around it (40% margin, reused while the view stays inside); shader `eAt()` adds it, `hill()` uses a 1′ step inside it.
- Plant symbols (2026-10-13, `#lyVeg`, `LY.veg`, `k ≥ 7`): gouache sprites painted once per theme (`vegSprites()`, kinds `VK`, per biome `VEGT` = [tree, ground]) on a world-fixed jittered grid (spacing ≈ 70 px, power-of-2 degrees); clusters of 1–5 trees (cover >5/15/35/55/75%) from `vegAt(p,y).tree` (same forest/farm model as the base map: FPOT, FORESTG, FREG, farming share). `groundInfo()` shows tree cover %.
- `atlas/elev.webp` (ETOPO 2022 60″ → 1/12°, 4320×2160, R/G = high/low byte of m+11000, ~9 MB) loads after terrain; until then (or if the GPU max texture size < 4320 → halved) the shader uses the old G-channel shading.
- Perf (2026-10-11, GPU): no long tasks while scrubbing; ~10 ms script per update. CPU fallback: ~200 ms per rebuild, throttled.
- Perf (2026-10-13): the CPU land mask (`buildLand`, ~260k `flagAt`) is throttled to ~6/s while time moves (`buildLandSoon`, trailing rebuild); river under-ice/sea visibility is cached with it (`riverOn`); overview curves are cached (`ovSamples`); `fmt` avoids `toLocaleString`. Long tour jumps (> 3 timeline-widths or 400 yrs) sweep with the map held a few times a second (`mapHold`), then run in over the last timeline-width at full detail. Scrub profile 2.24 s → 1.55 s script.

## Data pipeline (dev/scripts, run with `.venv/Scripts/python -I`; raw downloads in dev/raw/, git-ignored)
- `build_elev.py` → `atlas/elev.webp` (ETOPO 2022 60″ surface elevation, NOAA NCEI, 5×5 block mean; raw GeoTIFF + int16 copy `etopo60_i16.npy` in `dev/raw/etopo/`). Offline style prototype: `dev/proto/painted/` (Shelton-style renders, see its README).
- `build_rivers_valleys.py` → `atlas/rivers.json` (lon,lat ×100; page divides by 100): today's courses from `dev/data/rivers_basemap.json` (basemap-data, ×20), densified to 1′ and snapped to the lowest ETOPO cell within ±2′ (12 m/cell penalty), smoothed + simplified.
- `build_coast_slw.py` → `atlas/slw.png` (De Groeve 2022 shelf-sea history, 26 ka→now; R/G switch times, B state at 26 ka).
- `build_climate.py` → `atlas/biome_beyer.png` (Beyer 2020, 33 snapshots, 0.5°, 3 per RGB block) + `<script id="climdata">` in the page (snapshot years, BIO1 at CLIM points, Osman 2021 + Kaufman 2020 GMST). Includes documented corrections (glacial mammoth steppe, African Humid Period).
- `build_cliopatria.py` → `atlas/cp/<century>.json` + `index.json` (Cliopatria v0.2.1 states with from/to years) and `atlas/hb/peoples.json` (historical-basemaps features kept outside states).
- `build_ice_paleomist.py` → R/G channels of `atlas/ice.png` (PaleoMIST 1.0, 2.5 kyr; distance-interpolated margins). Reads and rewrites ice.png (idempotent).
- `build_c14.py` → `atlas/c14.json` (p3k14c + XRONOS, de-duplicated by lab number, IntCal20).
- `build_eruptions.py` → `<script id="eruptions">` (eVolv2k v4, eruptions ≥ 10 Tg S).
- `build_hyde.py` → `atlas/popd.png` + `<script id="popdata">` (HYDE 3.2.1 population density, log-coded 0.5°; layer `#lyPop`, off by default; drawn as population circles per zoom-sized world grid, people = density × land area from terrain, top 5–8 labelled). Raw grids: `dev/raw/hyde/fetch.py` (range requests + inflate64; HYDE 3.3 on YODA is behind a bot check — don't bypass).
- `build_images.py` → `atlas/img/*.webp` + `index.json` (Commons thumbnails for the era "See it" images, licence/author from Commons metadata; free licences only).
- `build_popup_images.py` → `atlas/pimg/s<n>.webp` sprite sheets (8×6 cells of 360×225) + `index.json` (`{_grid, title: {s, c, file, lic, artist}}`): lead picture of each map item's Wikipedia article, keyed by title / site name; maps, flags, charts and SVGs skipped; `dev/data/popup_images_pick.json` = hand-picked art (user prefers colour paintings of animals in their setting, e.g. Knight, Antón), `popup_images_skip.json` = rejected by eye; thumbnail cache in `dev/raw/pimg/`; `--cultures` adds culture articles. Shown in map popups and the selected-event card.
- Deep time (500 ka → 40 ka): `build_deeptime.py` → `<script id="deepdata">` (Spratt & Lisiecki 2016 sea level, Bereiter 2015 CO₂, EPICA temperature scaled ×0.63 cold / ×0.3 warm, estimate); `build_climate_deep.py` → `atlas/biome_deep1-3.png` + `<script id="climdeep">` (Krapp 2021 biomes/BIO1/ice every 5 kyr, 505–45 ka; lazy-loaded below 40,000 BCE). Raw files in `dev/raw/deep`, `dev/raw/krapp`; set `KE_RAW` when running from a worktree. Era texts for the 5 deep eras: `dev/data/deep_eras.json` → `<script id="deeperas">` (no research panel: `era.ri` undefined).
- Before 45,000 BCE (`DEEPICE`) ice = biome class 9 of the snapshot (not ice.png); seas above today flood land codes `R ≤ 140+1.4846·√sea` (CPU `floodR`, shader). Overview strip/charts use the compressed scale `ovF/ovK` (C=1800 yr).
- Human species before 40,000 BCE: `build_hominins.py` (stdlib `xlsx_min.py`) → `atlas/hominins.json` (Timmermann et al. 2022 finds, CC BY, + hand-added Denisovans/Flores/Luzon/naledi); layer `#lyHomo`, colours `--h0..--h8`, lazy-loaded below 38,000 BCE. Deep-era panels: `dev/data/deep_research.json` → `<script id="deepresearch">`. Hypothetical archaic routes: `dev/data/archaic_migrations.json` merged into `migr` with `hyp:true` (dotted). Natural landmarks / fossil sites / old plants / extinct animals: `dev/data/nature_sites.json` → `<script id="nature">` (joined to MARKS/ANIMALS).
- Ice Age animals: `build_megafauna.py` → `atlas/megafauna.json` (Neotoma + PBDB, CC BY; FosSahul 2.0 CC0 for Diprotodon / marsupial lion / Genyornis (quality A*/A/B); audited radiocarbon lists Stuart & Lister 2012 (woolly rhino) and Lister & Stuart 2019 (giant deer), raw files in `dev/raw/megafauna`; NOW database localities (CC BY, Middle Pleistocene) from a browser export filtered into `dev/data/now_megafauna.json`; species marks in ANIMALS with the same Wikipedia title are hidden while the layer shows that species (`fauActive`); cited localities in `dev/data/megafauna_dated.json`; `LAST`/`last_at` clip to extinction, islands kept); layer `#lyFauna`, hue per species × `--fl` lightness. Big eruptions: `build_bigeruptions.py` → `<script id="bigeruptions">` (GVP VEI ≥ 6 Holocene, non-commercial; `dev/data/super_eruptions.json` for 500–12 ka); skips eruptions already on the page.
- Black Death 1346–53: `dev/data/plague_arrivals.json` (113 dated first arrivals: Wikipedia + Enciclopèdia Catalana + Biraben via Büntgen 2012; `approx` for seasons/years; `spared` list incl. Milan, debated) → `embed_spreads.py` → `<script id="plague">`; layer `#lyPlague` (`drawPlague`): arrival-time grid 0.5° = min(IDW of 6 nearest towns ≤500 km, town date + distance/600 km·yr⁻¹), masked to land, red front (`--plague`), town rings/dots; fades out 1353–1361. Off by default (tour-only colouring). Towns with `pop`/`died` (31, Jedwab et al. 2022 + Wikipedia, ranges in `mort_note`) are circles sized by people that shrink over ~9 months to the survivors, labelled −N%.
- Tour steps in CE may have fractional years (months, `tourK`/`tourWhen`); Black Death steps sit just after the arrivals their caption names. `look` rings start when the camera settles (`tourLook`).
- Earliest farming 9250–3000 BCE: `dev/data/farming_arrivals.json` (101 sites: Wikipedia + Pinhasi et al. 2005 Table S1, `spread`; `centres` = independent centres, not drawn) → `embed_spreads.py` → `<script id="farmspread">`; shown only as a tour overlay (`fx.spread`).
- Tour step extras: `img` = a picture title from `atlas/pimg/index.json` shown on the card; `tips` = [{h, t, lat, lon, img?}] "did you know" notes: Next ▶ visits them before the next step (`tourGo`/`tourTip`, map glides there with `mapGlide`, the note stays pinned, `drawTips`, `#tnote`); auto mode reads each (`tipRead`). Notes for all tours were researched per tour group (Wikipedia-checked). Choosing an event (timeline, search, lists) glides the map there and opens its popup (`focusMap`, `evInfo`). Migration branches start when the route reaches their fork (`migPts`, `off`/`cum`/`total` per migration).
- Tour story overlays (`storyFx`, from tour/step `fx`): `walk` = figures walking the drawn part of active migration routes (`hyp` adds hypothetical routes); `spread` = a SPREADS front; every step's `look` = [[lat,lon,label]] rings that fade in, pulse and fade out on arrival (`drawFocus`). One rAF loop (`walkTick`, ~25 fps) runs only while overlays animate.
- Climate events and open scientific questions: `dev/data/climate_events.json` (Wikipedia-checked, `check` = quoted basis) → `dev/scripts/add_climate_events.py` → research/deepresearch `more` lists by era; `q:true` shows "Open question" in the popup and event card.
- Fact sources for deep time are Wikipedia-checked via subagents; Reddit blocks automated access (no thread data). Candidate datasets (not yet built): Emery-Wetherell 2017 (Dryad CC0, browser download), Lorenzen 2011 dates (PDF tables), LegacyPollen 2.0.
- Python env: project `.venv` (numpy, scipy, pillow, shapely, tifffile, imagecodecs, h5py, netCDF4). No R.
- Land/sea rule lives in `landCell()` (JS) and the shader; biome lookup in `bioCls()` and the shader — change both together.

## Interactive features (2026-10-12)
- Play: `playStart/playStop`, years per second ∝ age (`RATE`, `RATE_MIN`), timeline zoom follows speed; Space toggles.
- Search: header combobox over EVENTS, ERAS, MIGR (choose on click, not pointerdown, so a tap cannot hit what lies under the list).
- Place: tap-opened popups are sticky and carry "What happened here? / Play from here"; `setPlace()` samples land/sea/ice, biome, HYDE, C14 at log-spaced ages; `placePlay()` pauses at nearby events and at changes of the place (`placeStops`, `placeTick`).
- Guided tours: `TOURS` from `<script id="tours">` (built by `dev/scripts/embed_tours.py` from `dev/data/tours.json`; steps {y, lat, lon, z, t, c, w, span?, ly?}); `tourStart/tourStep/tourEnd`, `tourFly` moves time (log-age) and map together; deep link `?tour=<id>&step=<n>`; test `dev/test/tours.py`. Plan, feedback log and candidate stories: `dev/PLAN-play-search-place-tours.md`.

## Conventions
- Year 1 KE = 9500 BCE; signed years in data (BCE negative, no year 0); `ke()`, `toSigned()`, `civil()`.
- Lanes 0 Near East, 1 Africa, 2 Europe, 3 Asia, 4 Americas, 5 Earth & Oceans. Importance `i`: 1 famous, 2 important, 3 specialist.
- Keep design tokens on `:root` with dark-mode overrides; match the existing compact code style.
- Facts must be checked against Wikipedia or cited papers; mark estimates and contested points as such.
- Content scope (user, 2026-10-13): only topics the scientific community takes seriously (peer-reviewed, debated among specialists is fine if marked "debated"); no pseudo-archaeology or popular fringe claims (e.g. Gunung Padang "pyramid", Younger Dryas impact as civilisation-ender, lost Ice Age civilisations).
- Git repo with GitHub remote `origin` (github.com/kmdan/historytimeline, public): commit each working step and `git push` (Git Credential Manager holds the GitHub login since 2026-10-12; if a push asks for credentials, stop and ask the user — never enter them); `.gitattributes` keeps files byte-exact.
- Migrations focus (user, 2026-10-12): historical movements **before 1900**; no modern refugee/flow datasets. Size is shown as 1–5 figures (×10 each) from `people`; streams (`mode:"flow"`) vs advancing fronts.
- Deep links: `?y=<signed civil year>&at=lat,lon,zoom` (zoom 1 = whole world) are read on load; the address bar follows the view via `replaceState` (`linkSoon()` in `draw()`/`drawMap()`); other params (`?cpu`) are kept.
- Discoverability (2026-10-12, `dev/PLAN-discoverability.md`): title, description, canonical (= GitHub Pages URL), Open Graph and JSON-LD live in `<head>`; `robots.txt`, `sitemap.xml`, `llms.txt` at the repo root. Update `sitemap.xml` lastmod and the JSON-LD `isBasedOn` list when datasets change.
- Map projection stays equirectangular (user: Equal Earth / globe not needed for now).

## Known improvement candidates
- Done 2026-10-11: WebGL2 base map, timeline label collision, compact phone info box.
- Done 2026-10-11: De Groeve coastlines, Beyer biomes + BIO1 labels, Osman/Kaufman temperature, Cliopatria states, PaleoMIST ice.
- Next data ideas: `dev/RESEARCH-sources.md` (XRONOS/EUROEVOL dates, HYDE land use, AADR/Glottolog, eVolv2k eruptions).
- Borders: convert 53 snapshots to features with start/end years. Deep time: PALEOMAP paleo-DEMs + GPlates coastlines.
- Backlog in `dev/HANDOFF.md` §7.

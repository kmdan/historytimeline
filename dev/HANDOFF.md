# Karahan Era — handoff for a coding session

**Live artifact (keep updating this one):** https://claude.ai/artifact/EVCozfzuxXvmWzggiSg216
Shared as "Anyone with the link". Owner: Daniel (VFX/pipeline TD; Python-fluent, not a web dev).

## 1. Getting the source back
Everything ships inside the artifact. In a new session:
1. `Artifact` → `action: "read"`, `url` above → saves the page (`index.html`) locally; build on that file.
2. `Artifact` → `action: "list"`, `scope: "files"`, `url` above → lists supporting files.
3. `Artifact` → `action: "read"`, `url`, `paths: [...]` → fetch `atlas/*`, `atlas/hb/*`, `dev/*`.
4. Recreate layout: page as `karahan-era.html`, keep `atlas/…` and `dev/…` beside it.
5. Republish with `Artifact` (publish) + `url` above + `file_path` = the page. Pass `files` only for changed supporting files (unlisted ones are kept). Omit `icon`.

## 2. Calendar & conventions
- Year 1 KE = 9500 BCE. `ke(signed)` (no year 0) → KE; `toSigned(k)`; `civil(k)` → "x BCE/CE".
- Range: `DMIN = ke(-40000)`, `NOW = ke(2026)`, `DMAX = NOW+30`.
- Signed years everywhere in data (BCE negative). "BP" → subtract 1950.
- Lanes: 0 Near East, 1 Africa, 2 Europe, 3 Asia, 4 Americas, 5 Earth & Oceans (global/Oceania).
- Event importance `i`: 1 world-famous, 2 important, 3 specialist (level-of-detail: `lodTime()`, `lodMap()`).

## 3. Page architecture (single HTML, inline CSS/JS, no libraries)
Design tokens on `:root` (light) + dark blocks (`prefers-color-scheme` and `[data-theme]`). Fonts: Gloock / IBM Plex Sans / IBM Plex Mono.
Layout: header + controls → **Atlas & timeline** (layer toggles `#ly*`, era chips, `.stack` = `#map` canvas + `#tl` timeline canvas with overview strip), legend, sea-level chart `#sl` → report cards.

Embedded JSON `<script type="application/json">` blocks (edit data here):
| id | content |
|---|---|
| `research` | per era (15): `events[{t,w}]` (Wikipedia titles), `more[]` extra events, `know[]`, `papers[]` (OpenAlex counts), `images[]` (Commons files) |
| `cultwiki` | 815 culture/state names → `{w,d}` verified Wikipedia |
| `iceage` | 47 Ice Age + 88 European (eu:1) cultures: `{n,w,from,to,region,pts,sites,d,kind}` |
| `reddit` | themes + 31 events (r/AskHistory etc.) |
| `envdata` | `forest.global`, `forest.regions[19]` (series), `impact.events[42]`, `impact.venice` |
| `figdata` | `figs[44]` open-licence scientific figures, `reddit2` (35 events + top posts) |
| `migr` | 60 population movements `{n,w,from,to,kind,path,branches,scale,d}` |

Core JS (search by name):
- `EVENTS` array of `E(y,lane,i,title,desc,[lat,lon])`; later merged: research `more`, reddit, impact (`imp`), reddit2 (`src`). Fields `w` (Wikipedia), `src` (Reddit), `imp`.
- `ERAS` (15 eras: land/nature/life/living/disease + `SOC` society text), metric series `POP, SEA, CO2, TMP, LIFE, FORESTG, CITY, MAT`, `FLAGS`.
- Timeline: `draw()` (overview strip `OVH`, era band, lanes, events, playhead), `gestures()` helper (drag/pinch/wheel/tap).
- Atlas: `buildBase(y,sea)` per-pixel raster (biome, farmland dither, forest model `FPOT/FREG/regIdx`, ice; throttled), `buildFade(y)` evidence fade, `renderMap()` layers → labels via `place()` collision + `hits[]` → popups `showPop/popHTML`. Migrations: `MIGR`, `drawMigrations()`.
- Report: `update()` (metrics, era text, near list), `renderEra(era)` (know, gallery, figures, papers, impact list).
- Layers object `LY` ↔ checkboxes `#lyForest #lyBiome #lyIce #lyFarm #lyCoast #lyRivers #lyClimate #lyFade #lyMarks #lyBorders #lyC14 #lyEvents #lyMigr #lyFigs`.

## 4. Atlas data files (`atlas/`, 2160×1080 = 1/6° unless noted)
- `dem/t<col>_<row>.webp` + `dem/index.json`: 30° tiles of 1′ ETOPO detail (difference to elev.webp, 8 m steps around 128), loaded when zoomed in.
- `elev.webp` (4320×2160, 1/12°): ETOPO 2022 elevation, R/G = high/low byte of metres + 11000; GPU only (fine coasts, relief at screen resolution).
- `terrain.png` R: 1–130 depth m, 131–139 deep, 135 lake, 140–255 land (√elev); G: relief detail (Natural Earth shaded relief); B: smooth noise (biome/forest dithering).
- `ice.png` R onset code, G retreat code (255 permanent) → `iceCode(y)`; B farming start code → `farmYear(c)`.
- `biome0-2.png` 9 snapshots (`BSNAP` years) in RGB; classes 1 rainforest, 2 savanna, 3 desert, 4 steppe, 5 Mediterranean, 6 temperate forest, 7 taiga, 8 tundra, 9 ice, 10 mammoth steppe.
- `coast.json` (Natural Earth 50m, ×10 ints), `rivers.json` (×20 ints), `c14.json` (p3k14c, IntCal20, 0.5° × 100-yr bins), `hb/<year>.json` + `years.json` (historical-basemaps, simplified).
Scripts in `dev/scripts/` (Python: numpy, scipy, PIL, shapely, rdata). Sources: ETOPO20 (matplotlib basemap repo), basemap-data wheel (shadedrelief.jpg, lsmask, rivers), kgcpy (Köppen 100″), p3k14c, historical-basemaps, world-atlas.

## 5. Research workflow & limits
- Shell network blocked Wikipedia, Commons, OpenAlex, Reddit (since 2026-10-12 Commons API + thumbnails work from the shell with a User-Agent). Use WebFetch/WebSearch (often via subagents). Wikipedia rate-limits (429): `sleep 4` between fetches, `sleep 90` on 429. OpenAlex works by DOI lookup.
- The published page's CSP blocks external images/fetch, but files published beside the page load fine. Era images: `dev/scripts/build_images.py` downloads 640 px WebP thumbnails to `atlas/img/` (+ `index.json` with Commons licence/author); the "See it" gallery shows them. Scientific figures are still link cards. Map popups and the selected-event card show the free lead picture of the item's Wikipedia article: `dev/scripts/build_popup_images.py` → `atlas/pimg/s<n>.webp` sprite sheets + `index.json` (`PIMG[title]` = sheet/cell, looked up by the popup's `img`/`w`; drawn as a CSS background sized to the grid, because the artifact allows at most 511 files); items without one keep the Commons search link.
- Raw research JSON in `dev/data/` (same content as embedded blocks, plus source notes).

## 6. Testing
Serve locally (`python3 -m http.server 8765`), Playwright (Chromium preinstalled) screenshots at a few years (e.g. 21000 BCE, 4500 BCE, 900 CE, 1750, 2020), light/dark, 390px width (check `scrollWidth` = 390), and `node --check` on the extracted main script. Note: local server lacks UTF-8 charset (mojibake in screenshots only; the artifact skeleton is fine).

## 7. Backlog / ideas
- Verify the ~2,000 remaining culture names (rate-limited), refine imperfect matches noted in research reports.
- HYDE population density layer (needs data files from the user).
- Pictures (parked 2026-10-13, user happy with current state): era "See it" galleries still mix in maps/charts — could re-curate toward paintings (Vasnetsov *Stone Age* frieze, Paul Jamin, Knight; all PD on Commons); show the picture title in popup credit lines; swap the few dull popup photos (e.g. Cattle, Star Carr field) only for paintings or notable finds.
- Performance: `buildBase` is CPU per-pixel at 2.3 MP — consider WebGL or tiling for smoother scrubbing.
- More regions in the forest model; Holocene sea-level regional rebound (GIA) for northern coasts.
- Tartessos, Sanxingdui, Great Zimbabwe, Cucuteni–Trypillia, Lapita (in Reddit threads but not yet citable).
- Split the 300 KB single HTML into modules only if it helps; the artifact must stay a self-contained page + files.

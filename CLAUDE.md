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
- User approved (2026-10-11): republish after each **tested** improvement without asking. Commit to git first; mention each publish in the reply.
- GitHub Pages (2026-10-12, repo public): https://kmdan.github.io/historytimeline/ serves `master` root; `index.html` redirects to `karahan-era.html`, `.nojekyll` disables Jekyll. Updates go live on push.
- Artifact runtime limits: no external fetch/images at runtime (CSP); scripts only from cdnjs / jsdelivr / unpkg with exact versions; everything else ships as files beside the page.

## Testing
- Local server: `.claude/launch.json` config `karahan` (python http.server on 8765) → open `http://localhost:8765/karahan-era.html` in the built-in browser.
- **Preferred: headless Playwright with the installed Edge** (works even when the browser pane is hidden — the pane stops rendering/rAF when hidden):
  - `python dev/test/check.py <outdir>` — errors, GPU vs `?cpu` pixel diff at 5 years (must be ~0), scrub long tasks, screenshots (dark/light/phone). Uses SwiftShader, so its timings are NOT representative.
  - `python dev/test/touch.py <outdir>` — emulated phone + tablet: swipe over map/timeline scrolls the page, sideways swipe travels, pinch zooms the map, tapped popups stay open, fit and have reachable links (raw CDP touch events; synthesizeScrollGesture does not scroll headless).
  - `python dev/test/profile.py [?cpu]` — CPU profile of a scrub on the real GPU (RTX 3070); use this for performance numbers.
- All JS lives in one IIFE (no globals): drive via UI (`#goY`/`#goU`/`#go` form, buttons, pointer events on `#tl`), read `#ph`, `#mapinfo`, `#eName`, `#pop`, `#map[data-renderer]` (`webgl2` or `cpu`).
- Touch model: one finger scrolls the page over the map (two fingers pan/zoom it); timeline/chart take sideways drags; popups are a bottom sheet on touch/narrow screens; `leave`/hover handlers are mouse-only.
- Check each change at several years (e.g. 21000 BCE, 4500 BCE, 900 CE, 1750, 2020), light + dark, mobile 375 px (no horizontal page scroll), console errors.
- Base map: WebGL2 shader (`GLB`) mirrors the CPU `buildBase` loop exactly; any change to the base-map rules must be made in **both** (CPU is the fallback; `?cpu` forces it). Context loss falls back to CPU automatically.
- Perf (2026-10-11, GPU): no long tasks while scrubbing; ~10 ms script per update. CPU fallback: ~200 ms per rebuild, throttled.

## Data pipeline (dev/scripts, run with `.venv/Scripts/python -I`; raw downloads in dev/raw/, git-ignored)
- `build_coast_slw.py` → `atlas/slw.png` (De Groeve 2022 shelf-sea history, 26 ka→now; R/G switch times, B state at 26 ka).
- `build_climate.py` → `atlas/biome_beyer.png` (Beyer 2020, 33 snapshots, 0.5°, 3 per RGB block) + `<script id="climdata">` in the page (snapshot years, BIO1 at CLIM points, Osman 2021 + Kaufman 2020 GMST). Includes documented corrections (glacial mammoth steppe, African Humid Period).
- `build_cliopatria.py` → `atlas/cp/<century>.json` + `index.json` (Cliopatria v0.2.1 states with from/to years) and `atlas/hb/peoples.json` (historical-basemaps features kept outside states).
- `build_ice_paleomist.py` → R/G channels of `atlas/ice.png` (PaleoMIST 1.0, 2.5 kyr; distance-interpolated margins). Reads and rewrites ice.png (idempotent).
- `build_c14.py` → `atlas/c14.json` (p3k14c + XRONOS, de-duplicated by lab number, IntCal20).
- `build_eruptions.py` → `<script id="eruptions">` (eVolv2k v4, eruptions ≥ 10 Tg S).
- `build_hyde.py` → `atlas/popd.png` + `<script id="popdata">` (HYDE 3.2.1 population density, log-coded 0.5°; layer `#lyPop`, off by default). Raw grids: `dev/raw/hyde/fetch.py` (range requests + inflate64; HYDE 3.3 on YODA is behind a bot check — don't bypass).
- Python env: project `.venv` (numpy, scipy, pillow, shapely, tifffile, imagecodecs, h5py, netCDF4). No R.
- Land/sea rule lives in `landCell()` (JS) and the shader; biome lookup in `bioCls()` and the shader — change both together.

## Conventions
- Year 1 KE = 9500 BCE; signed years in data (BCE negative, no year 0); `ke()`, `toSigned()`, `civil()`.
- Lanes 0 Near East, 1 Africa, 2 Europe, 3 Asia, 4 Americas, 5 Earth & Oceans. Importance `i`: 1 famous, 2 important, 3 specialist.
- Keep design tokens on `:root` with dark-mode overrides; match the existing compact code style.
- Facts must be checked against Wikipedia or cited papers; mark estimates and contested points as such.
- Git repo with GitHub remote `origin` (github.com/kmdan/historytimeline, private): commit each working step; pushing happens from GitHub Desktop (command-line git has no GitHub sign-in here — do not enter credentials); `.gitattributes` keeps files byte-exact.
- Map projection stays equirectangular (user: Equal Earth / globe not needed for now).

## Known improvement candidates
- Done 2026-10-11: WebGL2 base map, timeline label collision, compact phone info box.
- Done 2026-10-11: De Groeve coastlines, Beyer biomes + BIO1 labels, Osman/Kaufman temperature, Cliopatria states, PaleoMIST ice.
- Next data ideas: `dev/RESEARCH-sources.md` (XRONOS/EUROEVOL dates, HYDE land use, AADR/Glottolog, eVolv2k eruptions).
- Borders: convert 53 snapshots to features with start/end years. Deep time: PALEOMAP paleo-DEMs + GPlates coastlines.
- Backlog in `dev/HANDOFF.md` §7.

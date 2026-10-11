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
- Publishing is outward-facing: confirm with the user before republishing unless they asked for it in that request.
- Artifact runtime limits: no external fetch/images at runtime (CSP); scripts only from cdnjs / jsdelivr / unpkg with exact versions; everything else ships as files beside the page.

## Testing
- Local server: `.claude/launch.json` config `karahan` (python http.server on 8765) → open `http://localhost:8765/karahan-era.html` in the built-in browser.
- No Node/Playwright locally. All JS lives in one IIFE (no globals): drive via UI (`#goY`/`#goU`/`#go` form, buttons, pointer events on `#tl`), read `#ph`, `#mapinfo`, `#eName`, `#pop`.
- Check each change at several years (e.g. 21000 BCE, 4500 BCE, 900 CE, 1750, 2020), light + dark, mobile 375 px (no horizontal page scroll), console errors, and long tasks (PerformanceObserver 'longtask') for scrubbing performance.
- Baseline (2026-10-11): map rebuild ~130–290 ms per long task; throttled redraws make scrubbing jumpy.

## Conventions
- Year 1 KE = 9500 BCE; signed years in data (BCE negative, no year 0); `ke()`, `toSigned()`, `civil()`.
- Lanes 0 Near East, 1 Africa, 2 Europe, 3 Asia, 4 Americas, 5 Earth & Oceans. Importance `i`: 1 famous, 2 important, 3 specialist.
- Keep design tokens on `:root` with dark-mode overrides; match the existing compact code style.
- Facts must be checked against Wikipedia or cited papers; mark estimates and contested points as such.
- Not a git repo yet — before large refactors, keep a backup copy of `karahan-era.html` (or suggest `git init`).

## Known improvement candidates
- WebGL2 base-map shader (smooth scrubbing, biome blending, Equal Earth / globe projections) — recommended next step.
- Timeline event labels overlap in dense periods; map info box covers much of the map on phones.
- Borders: convert 53 snapshots to features with start/end years. Deep time: PALEOMAP paleo-DEMs + GPlates coastlines.
- Backlog in `dev/HANDOFF.md` §7.

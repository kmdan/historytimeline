# Karahan Era — project notes

Artifact: https://claude.ai/artifact/EVCozfzuxXvmWzggiSg216 (publish /home/claude/karahan-era.html; supporting files under /home/claude/atlas/).
Calendar: Year 1 KE = 9500 BCE. `ke(signedYear)` → KE; `civil(k)` → "x BCE/CE". Range DMIN=ke(-40000) … NOW=ke(2026).

## Page structure (single HTML, inline JS/CSS)
- Header + controls → "Atlas & timeline" section: layer toggles, era chips, `.stack` = atlas canvas (#map) + timeline canvas (#tl, overview strip on top), legend, sea-level chart (#sl).
- Report cards: stand/metrics, Earth, Nature, Daily life, Living, Sickness, Society, Look around, Selected event, Should know, Humans & environment (+Venice note), Scientific illustrations, See it (Commons links), Reddit themes + top posts, Key papers.
- Embedded JSON <script> tags: research (per-era know/papers/images/more events), cultwiki (815 verified culture→Wikipedia), iceage (47 Ice Age + 88 European cultures; eu:1), reddit, envdata (forest regions/global + impact events + venice), figdata (44 open-licence figures + reddit2 events/top posts).

## Atlas rasters (2160×1080, 1/6°)
- atlas/terrain.png: R = depth(0–130 m)/deep(131–139)/lake 135/land 140–255 (sqrt elev); G = relief detail; B = smooth noise.
- atlas/ice.png: R onset code, G retreat code (255 permanent), B farming start code. iceCode(y), farmYear(c).
- atlas/biome0-2.png: 9 biome snapshots (BSNAP years) in RGB channels; classes 1 rainforest…10 mammoth steppe.
- atlas/coast.json (Natural Earth), rivers.json (basemap rivers_l), c14.json (p3k14c, IntCal20), hb/*.json (historical-basemaps).

## Key JS pieces
- buildBase(y,sea): per-pixel colour (biome, farmland dither, forest model FPOT/FREG/regIdx, ice), throttled.
- buildFade(y): evidence fade layer. renderMap(): layers, labels via place()/hits[] → popups (showPop/popHTML).
- Layers object LY + checkboxes #ly*. Event lists: EVENTS (E(y,lane,importance,title,desc,[lat,lon])), fields w (Wikipedia), src (Reddit), imp (human impact).
- Level of detail: lodTime()/lodMap().

## Limits
Shell network blocks Wikipedia/Commons/OpenAlex; research done through WebFetch subagents (rate-limited; pace with sleep). Page CSP blocks external images → figures/Commons as link cards.

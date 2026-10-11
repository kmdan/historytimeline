# Atlas rendering options (research, 2026-10-11)

## Bottom line
The slow scrubbing is the per-pixel JS loop in `buildBase` (CPU, 2.3 MP, ~130–290 ms per rebuild), not Canvas 2D itself.
Move base-raster composition into one WebGL2 fragment shader with `year` / `seaLevel` as uniforms. The existing encodings
(terrain depth/elevation channels, ice onset/retreat codes, farmland start codes) are already "per-pixel event times" — ideal for a shader.

## Ranked architectures
1. **WebGL2 base layer (raw / twgl.js ~30 KB / regl ~80 KB) + existing Canvas 2D vector overlay on top** — recommended.
   - Shader: `land = elev > sea(year)`, `ice = onset <= year < retreat`, biome via `TEXTURE_2D_ARRAY` of snapshots blended between the two bracketing layers, farmland `year >= start`, hillshade in-shader. Sea-level curve as 1D texture.
   - Any projection for free: full-screen quad, inverse-project each pixel to lon/lat (equirectangular, Equal Earth, orthographic globe). Vectors via d3-geo with the same forward projection.
   - ~2–4 days; payload unchanged; no tiling (detail capped at 1/6°).
   - Deep time: paleo-DEM slices as a texture array blended per Myr; true plate motion = plate-ID texture + per-plate Euler rotations (research-grade).
2. **MapLibre GL JS v5** (~268 KB gz): native globe, symbol collision, time filters on GeoJSON (`start`/`end` attrs, OpenHistoricalMap pattern), raster-dem hillshade.
   Time raster still needs a custom-layer shader (same work as #1, plus fitting MapLibre matrices). PMTiles needs HTTP Range — unverified on artifact hosting. ~1–2 weeks.
3. **deck.gl 9** (~1.5–2 MB): TripsLayer (animated migrations), DataFilterExtension (GPU time filtering of millions of C14 points), GlobeView experimental. Good if points/flows become central; otherwise borrow ideas.

Not recommended: CesiumJS (3–4 MB, CZML model doesn't fit), Leaflet/OpenLayers (CPU raster again; OL WebGLTile band-math is the exception), Three.js globe (= #1 with more weight).

## Smooth-scrubbing techniques
1. Per-pixel event-time encodings compared to a uniform on GPU (what we have). Extend: biome as transition year + from/to class.
2. Texture arrays of snapshots + in-shader blending (continuous fields, paleo-DEMs).
3. Vector features with start/end years + time-bucket index (dedupe the 53 historical-basemaps snapshots into features with lifetimes).
4. Polygon morphing (flubber) — cosmetic only, breaks on topology changes.

## Projection
Keep data equirectangular; render Equal Earth by default, orthographic globe toggle for deep time (polar continents). Avoid Web Mercator.

## How others do it
- GPlates / pyGPlates: `.rot` rotation files + static polygons with plate IDs; rasters reconstructed by plate-ID mask + rotation. Precompute offline. https://gwsdoc.gplates.org/
- PALEOMAP (Scotese & Wright 2018): one paleo-DEM per 5 Myr, 540–0 Ma, 1° (9 MB) or 0.1°. CC BY 4.0. https://zenodo.org/records/5460860
- Ancient Earth (Ian Webster): WebGL globe, one pre-rendered texture per step, no interpolation.
- OpenHistoricalMap: vector tiles with `start_date`/`end_date`, client-side date filter (maplibre-gl-dates).
- historical-basemaps: GeoJSON snapshot per year + index.json (licence reportedly GPL-3.0 — verify LICENSE).

## Data sources for changing geography
| Need | Source | Licence |
|---|---|---|
| Paleo-DEMs 540–0 Ma | PALEOMAP PaleoDEMs, https://zenodo.org/records/5460860 | CC BY 4.0 |
| Phanerozoic coastlines | PaleoMAP PaleoCoastlines (Kocsis & Scotese), https://zenodo.org/record/7994000 | CC BY 4.0 |
| Plate motions 1 Ga–now | Merdith et al. 2021 GPlates model | check Zenodo record |
| Paleo-coordinates, 5 models, 1 Myr | Jones & Domeier 2024 Sci Data, https://zenodo.org/doi/10.5281/zenodo.10069221 | check |
| Last 40 ka ice / sea level | ICE-6G_C, GLAC-1D; Spratt & Lisiecki 2016 | check |

## Suggested path
1. WebGL2 shader base layer, texture-array biome blending, Equal Earth + globe toggle (d3-geo for vectors).
2. Vector snapshots → features with start/end years + time-bucket index.
3. Deep time: PALEOMAP 1° DEM texture array + GPlates-precomputed coastlines with ages (pyGPlates offline).
4. MapLibre only if deep zoom/tiling is needed, after confirming Range requests work on artifact hosting.

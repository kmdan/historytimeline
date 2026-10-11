# Data sources, similar projects and explainers (research, 2026-10-11)

Verification marks: ✔ fetched / confirmed · (✔) confirmed via search or catalogue only · ✘ not verified. Licences must be re-checked before shipping derived data.

## Top-10 "use first" (value for effort)
1. **De Groeve et al. 2022 coastline-age raster** — GIA-corrected coastlines 26 ka→now, 500-yr steps, 120″ GeoTIFF; one "year this cell flooded" band = a single shader threshold (replaces ETOPO-minus-sea-level, adds isostatic rebound). https://doi.org/10.1111/geb.13573 · data https://hdl.handle.net/11245.1/ae1df27f-b7dc-410f-b0f5-43120f5eb48d — *licence to verify*.
2. **Beyer, Krapp & Manica 2020** — 0.5°, 0–120 ka, 1–2 kyr steps: monthly T/P, bioclim, NPP, **BIOME4 biomes** → replace Köppen-shifted biome snapshots. https://doi.org/10.1038/s41597-020-0552-1 · CC BY 4.0 · fetch via R `pastclim`.
3. **Osman et al. 2021 LGMR** (`LGMR_SAT_climo.nc` 13 MB, `LGMR_GMST_ens.nc` 257 kB) + **Kaufman 2020 Temp12k GMST** — temperature map + curve with uncertainty. https://www.ncei.noaa.gov/pub/data/paleo/reconstructions/osman2021/ · https://www.ncei.noaa.gov/access/paleo-search/study/29712 · NOAA public.
4. **Cliopatria (Seshat)** — polity borders 3400 BCE–2024, ~14k records, Wikidata IDs, **CC BY 4.0** (vs historical-basemaps GPL-3). https://github.com/Seshat-Global-History-Databank/cliopatria
5. **Batchelor et al. 2019** NH ice extents (17 Quaternary slices, min/best/max) https://doi.org/10.1038/s41467-019-11601-2 + **Dalton et al. 2020** N. American isochrones (36 slices, 18–1 ka) https://doi.org/10.1016/j.quascirev.2020.106223 — replace schematic ice sheets.
6. **XRONOS** (314k ¹⁴C dates, CC BY, API) https://xronos.ch/ + **EUROEVOL** https://doi.org/10.5334/joad.40 + **NeoNet** https://doi.org/10.5334/joad.87 — densify dates; build an empirical Neolithic farming front.
7. **HYDE 3.4/3.5** (5′ population/cropland/grazing, 10,000 BCE–2025) https://landuse.sites.uu.nl/hyde-project/ + **KK10** (alternative scenario) https://doi.pangaea.de/10.1594/PANGAEA.871369 — calibrate farmland/forest models.
8. **Bereiter 2015 CO₂** https://www.ncei.noaa.gov/pub/data/paleo/icecore/antarctica/antarctica2015co2composite.txt + **eVolv2k v4** volcanic forcing (PANGAEA 10.1594/PANGAEA.971968) — header curves, eruption markers.
9. **Glottolog geo CSV** (CC BY) https://glottolog.org/meta/downloads + **AADR `.anno`** https://doi.org/10.7910/DVN/FFIDCW / **Poseidon `.janno`** https://github.com/poseidon-framework/community-archive — language points, ancient-genome dots.
10. **CHELSA-TraCE21k** — 30″, 100-yr steps 21 ka→1990, T/P + paleo-orography + glacier masks (huge; download selected variables). https://www.envidat.ch/dataset/chelsa_trace · licence field says CC BY-SA 4.0 (inconsistent with description).

Next tier: PaleoMIST 1.0 (ice + topography, 80 ka, 2.5 kyr) https://doi.org/10.1038/s41467-021-21469-w · DIY proglacial lakes (LakeCC method) https://epic.awi.de/id/eprint/50841/ · DIY paleo-rivers via flow accumulation (pysheds/richdem) on paleo-DEMs · BIOME 6000 pollen sites https://researchdata.reading.ac.uk/99 · Pleiades/DARE classical layer · LegacyPollen 2.0 (PANGAEA, CC BY) forest curves · Krapp 2021 (0–800 ka) https://doi.org/10.1038/s41597-021-01009-3.

## Similar projects
| Project | Licence / stack | Borrow |
|---|---|---|
| Ancient Earth https://github.com/typpo/ancient-earth | MIT; texture per epoch on a globe | deep-time UX, "your town back then" |
| climatearchive.org https://github.com/sebsteinig/climate-archive (+ `nimbus` converter) | MIT; NetCDF → image textures → WebGL globe, 540 Myr | closest match to our pipeline |
| GPlates Web Service https://github.com/GPlates/gplates-web-service | GPL-2, pyGPlates | run reconstructions offline |
| Chronas https://github.com/Chronasorg/chronas | licence unclear | UX ideas only |
| OWID Grapher https://github.com/owid/owid-grapher | view-only now | design ideas only; OWID data is CC BY |
| PBDB Navigator https://paleobiodb.org/navigator | data CC BY | geologic-time ribbon selector |
| NeoNet app http://shinyserver.cfs.unipi.it:3838/C14/ | R Shiny | ¹⁴C explorer pattern |

## Other datasets by theme
- **Sea level / coasts / lakes / rivers:** De Groeve shelf-sea rasters https://doi.org/10.21942/uva.20029220.v1 · CRC806 LGM inland waters of Europe https://doi.org/10.5880/SFB806.14 (CC BY).
- **Climate:** PaleoClim snapshots http://www.paleoclim.org/ (CC BY, ✘) · TraCE-21ka https://www.cgd.ucar.edu/ccr/TraCE/ (raw, large).
- **Biosphere:** Allen et al. 2020 LPJ-GUESS 140 ka biomes (Bristol, licence ✘) · Neotoma https://www.neotomadb.org/data (pollen + FAUNMAP megafauna) · ArchaeoGLOBE (Harvard Dataverse, ✘) · Sandom 2014 megafauna extinctions https://doi.org/10.1098/rspb.2013.3254 · PHYLACINE 1.2 present-natural ranges (✘).
- **Migrations / population:** Glottography language polygons https://doi.org/10.5334/johd.459 · D-PLACE https://d-place.org/ (**CC BY-NC**) · Pinhasi 2005 Neolithic dates https://doi.org/10.1371/journal.pbio.0030410 · Seidensticker 2021 Bantu dates https://zenodo.org/records/4394894 (✘).
- **Archaeology / history:** IntChron https://intchron.org/ · RADON (Kiel, ✘) · ROAD (restrictive) · Seshat https://seshat-db.com/ (CC BY-SA) · DARE https://imperium.ahlfeldt.se/ (CC BY-SA) · Pleiades https://pleiades.stoa.org/downloads (CC BY, ✘).
- **Climate events:** 4.2 ka "not remarkable" — McKay et al. 2024 https://doi.org/10.1038/s41467-024-50886-w · Holocene temperature conundrum — Bova et al. 2021 https://doi.org/10.1038/s41586-020-03155-x, Liu et al. 2014 PNAS, Bader et al. 2020.

## Explainers to link
1. Carbon Brief — How proxy data reveals the climate of the distant past: https://interactive.carbonbrief.org/how-proxy-data-reveals-climate-of-earths-distant-past/index.html
2. Carbon Brief — What Greenland ice cores say: https://www.carbonbrief.org/factcheck-what-greenland-ice-cores-say-about-past-and-present-climate-change
3. xkcd 1732 Earth Temperature Timeline: https://xkcd.com/1732/ (CC BY-NC — link only)
4. Our World in Data — Land use: https://ourworldindata.org/land-use · Population sources: https://ourworldindata.org/population-sources
5. Nature News & Views on Bova 2021: https://media.nature.com/original/magazine-assets/d41586-021-00115-x/d41586-021-00115-x.pdf
6. NAU on the 4.2 ka result: https://news.nau.edu/?p=72717
7. Ancient Earth globe: https://dinosaurpictures.org/ancient-earth

## Licence caveats
- Share-alike: Seshat, DARE, possibly CHELSA-TraCE21k (CC BY-SA) → derived files must be BY-SA. GPL-3: historical-basemaps (in use), pastclim code. Cliopatria (CC BY) avoids this for borders.
- Non-commercial: D-PLACE, xkcd → link, don't bundle.
- No reuse: OWID Grapher code, Chronas (no licence), GeaCron, Blakey maps.
- Unclear: De Groeve rasters, BIOME 6000, ArchaeoGLOBE, AADR/Poseidon (cite releases), IntChron, ROAD.
- NOAA/NCEI products are public domain (cite). PANGAEA products are typically CC BY 4.0.

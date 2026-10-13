# Karahan Era

An interactive world timeline and atlas from 500,000 BCE to today. Scrub through time and watch coastlines, ice sheets, vegetation, cultures, states, migrations and population change on the map, with dated events for every region.

**Live site: https://kmdan.github.io/historytimeline/**

The calendar counts from Year 1 KE = 9500 BCE, around the end of the last Ice Age and the start of farming.

## What's on the map

- **Land, sea and ice**: five glacial cycles of sea level, ice and vegetation, shelf-sea coastlines for the last 26,000 years, ice sheets every 2,500 years, sea level and global temperature charts
- **Climate and vegetation**: biomes and local temperatures from climate-model snapshots, with an estimated forest layer
- **People**: Ice Age and European prehistoric cultures, states from 3400 BCE, 60 migrations, about 200,000 radiocarbon-dated sites and an optional population-density layer
- **Events**: hundreds of dated events in six regional lanes, each linked to Wikipedia, plus the largest volcanic eruptions of the last 2,400 years

Works in any modern browser, on desktop and phone. It draws the map on the GPU (WebGL2) and falls back to the CPU on devices without WebGL2.

## Data sources

The main datasets are listed below. Full credits, licences and caveats are at the foot of the page.

| Layer | Source | Licence |
|---|---|---|
| Coastlines, last 26,000 years | De Groeve et al. 2022 | CC BY 4.0 |
| Ice sheets | PaleoMIST 1.0, Gowan et al. 2021 | CC BY 4.0 |
| Biomes, local temperature | Beyer, Krapp & Manica 2020 | CC BY 4.0 |
| Global temperature | Osman et al. 2021; Kaufman et al. 2020 | — |
| States from 3400 BCE | Cliopatria v0.2.1 (Seshat), Bennett et al. 2025 | CC BY 4.0 |
| Peoples, earlier borders | historical-basemaps (A. Ourednik) | see project |
| Radiocarbon dates | p3k14c; XRONOS (Roe et al. 2025) | see projects; CC BY 4.0 |
| Population density | HYDE 3.2.1, Klein Goldewijk et al. 2017 | CC BY 3.0 |
| Deep time: sea level, CO₂, temperature (500,000–40,000 BCE) | Spratt & Lisiecki 2016; Bereiter et al. 2015; EPICA Dome C, Jouzel et al. 2007 (scaled estimate) | free with citation (NOAA) |
| Deep time: biomes, local temperature, ice | Krapp et al. 2021 | CC BY 4.0 |
| Volcanic eruptions | eVolv2k v4, Sigl & Toohey 2024 | CC BY 4.0 |
| Human species finds | Timmermann et al. 2022 | CC BY 4.0 |
| Ice Age animal finds | Neotoma; Paleobiology Database; FosSahul 2.0 (Peters et al. 2019); Stuart & Lister 2012; Lister & Stuart 2019 | CC BY 4.0; CC BY 4.0; CC0; dates cited |
| Large eruptions (VEI 6+) | Smithsonian Global Volcanism Program | non-commercial, with citation |
| Elevation, today's coast | ETOPO (NOAA); Natural Earth | public domain |

Figures before 1800 are scholarly estimates with wide error bars. Contested points are flagged in the page. Linked journal figures are under their own licences (mostly CC BY, a few CC BY-NC/ND), so this project is non-commercial.

## Licence

The code (HTML, CSS, JavaScript, Python scripts) is under the [MIT licence](LICENSE). The data keeps the licences of its sources listed above.

## Repository layout

- `karahan-era.html`: the whole page (HTML, CSS, JavaScript and embedded data)
- `index.html`: forwards the site root to the page
- `atlas/`: map images and data files the page loads
- `dev/`: notes, research, Python build scripts for the atlas data and browser tests

To run it locally, serve the folder with any static web server, for example `python -m http.server` in the repository root, then open `http://localhost:8000/`.

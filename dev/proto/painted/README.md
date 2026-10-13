# Painted map prototype (offline)

Renders one region at one year from the real atlas data, to try map styles before they go into the page shader.

    .venv/Scripts/python -I dev/proto/painted/prep.py <outdir> <signed year>     # base.png, meta.png, clim.png, page.html
    python dev/proto/painted/shot.py <outdir> [name]                              # headless Edge screenshot -> <name>.png

Env: `BBOX=lon0,lon1,lat0,lat1,px_per_cell` (default Europe `-11,41,34,61,5`), `NAME`, `STYLE=shelton|dark`,
`SEALEVEL` (m, used only inside coastal cells), `VEXAG` (relief exaggeration).
Needs `dev/raw/etopo/etopo60_i16.npy` (ETOPO 2022 60″, NOAA, converted to int16) for fine relief/depth/coast; runs without it at 1/6°.
Renders: Shelton-style Europe 6000 BCE, Alps close-up, Doggerland 8100 BCE, resolution comparison (18 km / 9 km / screen resolution).

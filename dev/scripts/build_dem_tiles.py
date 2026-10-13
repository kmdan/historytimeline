"""Detail elevation tiles for close zoom (ETOPO 2022 60 arc-second, NOAA NCEI, public domain).

Each tile covers 30 x 30 degrees at 1 arc-minute (1800 x 1800 px) and stores the *difference* between the full
ETOPO elevation and the 1/12-degree base layer (atlas/elev.webp) as the page interpolates it (bilinear between
pixel centres): value = 128 + round(diff / 8 m), clipped to 0..255 (covers +-1016 m; ~0.003 % of pixels clip).
Lossy WebP q90 (mean error ~1 step = 8 m): the page only uses it for relief shading and coast detail.
Tiles that are entirely deeper than 200 m below today's sea level are skipped.

Input:  dev/raw/etopo/etopo60_i16.npy (see build_elev.py)
Output: atlas/dem/t<col>_<row>.webp (col 0 = 180W..150W, row 0 = 90N..60N) + atlas/dem/index.json
Run:    .venv/Scripts/python -I dev/scripts/build_dem_tiles.py   (KE_RAW for dev/raw elsewhere)
"""
import os, json
import numpy as np
from PIL import Image
from scipy import ndimage as nd

RAW = os.environ.get('KE_RAW', 'dev/raw')
E = np.load(f'{RAW}/etopo/etopo60_i16.npy', mmap_mode='r')
# the base layer exactly as built by build_elev.py (5 x 5 block mean, rounded metres), padded by one column for wrap
base = np.round(np.asarray(E, np.float32).reshape(2160, 5, 4320, 5).mean(axis=(1, 3)))
base = np.hstack([base[:, -1:], base, base[:, :1]])
T, STEP = 1800, 8.0
os.makedirs('atlas/dem', exist_ok=True)
tiles, total = [], 0
for row in range(6):
    for col in range(12):
        y0, x0 = row * T, col * T
        e = np.asarray(E[y0:y0 + T, x0:x0 + T], np.float32)
        if e.max() < -200: continue
        jj, ii = np.mgrid[y0:y0 + T, x0:x0 + T]
        up = nd.map_coordinates(base, [(jj + .5) / 5 - .5, (ii + .5) / 5 - .5 + 1], order=1, mode='nearest')
        q = np.clip(np.round(128 + (e - up) / STEP), 0, 255).astype(np.uint8)
        f = f'atlas/dem/t{col}_{row}.webp'
        Image.fromarray(q, 'L').save(f, quality=90, method=6)
        tiles.append([col, row]); total += os.path.getsize(f)
json.dump({'deg': 30, 'px': T, 'step': STEP, 'tiles': tiles}, open('atlas/dem/index.json', 'w'), separators=(',', ':'))
print(len(tiles), 'tiles', total // 1024, 'KB')

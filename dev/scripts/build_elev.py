"""Global elevation layer for the screen-resolution base map (ETOPO 2022, NOAA NCEI, public domain).

Input:  dev/raw/etopo/etopo60_i16.npy  (ETOPO 2022 v1 60 arc-second surface elevation, int16 m, 10800 x 21600,
        north-up, pixel-centred from 90N / 180W; converted once from ETOPO_2022_v1_60s_N90W180_surface.tif)
Output: atlas/elev.webp  4320 x 2160 (lossless WebP) (1/12 degree, 5x5 block mean), RGB: R = high byte, G = low byte of (metres + 11000), B = 0.
        Exactly 2 x 2 pixels per 1/6-degree atlas cell, so the page derives the cell mean by box-averaging.
Run:    .venv/Scripts/python -I dev/scripts/build_elev.py   (set KE_RAW to read dev/raw from elsewhere)
"""
import os
import numpy as np
from PIL import Image

RAW = os.environ.get('KE_RAW', 'dev/raw')
src = f'{RAW}/etopo/etopo60_i16.npy'
if not os.path.exists(src):                     # first run: convert the GeoTIFF once
    import tifffile
    a = tifffile.imread(f'{RAW}/etopo/ETOPO_2022_v1_60s_N90W180_surface.tif')
    np.save(src, np.clip(np.round(a), -32000, 32000).astype(np.int16)); del a
e = np.load(src).astype(np.float32)
e = e.reshape(2160, 5, 4320, 5).mean(axis=(1, 3))
v = np.clip(np.round(e) + 11000, 0, 65535).astype(np.uint16)
img = np.stack([(v >> 8).astype(np.uint8), (v & 255).astype(np.uint8), np.zeros_like(v, np.uint8)], -1)
Image.fromarray(img, 'RGB').save('atlas/elev.webp', lossless=True, method=6)
print('atlas/elev.webp', img.shape, 'min', e.min().round(), 'max', e.max().round(), os.path.getsize('atlas/elev.webp') // 1024, 'KB')

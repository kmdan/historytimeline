"""Height of the Ice Age ice sheets above today's ground, for the relief shading of the map.

Source: PaleoMIST 1.0 (Gowan et al. 2021, Nat. Commun. 12:1199, https://doi.org/10.1594/PANGAEA.905800, CC BY 4.0),
  paleo_topography (ice surface incl. isostatic depression, present datum) and ice_thickness, 2.5 kyr steps, 80 ka -> 0.
For each slice and 0.5-degree cell: rise = w * max(0, paleo surface - today's mean ETOPO 2022 elevation of the cell),
  w = smoothstep(0, 150 m, ice thickness), smoothed (Gaussian, 0.75 deg), minus the same for today
  (so today is 0: Greenland/Antarctica already are in ETOPO).
The page adds the rise to the fine ETOPO elevation (so bed relief still shows faintly through the ice) and interpolates
  linearly between slices; only the shading uses it.
Output: atlas/iceh.png, 720 x (360 * 33) RGB, one 720x360 block per slice (oldest first, years as in the page's ICEH),
  R/G = high/low byte of the rise in metres, B = 0.
Run:    .venv/Scripts/python -I dev/scripts/build_ice_height.py   (KE_RAW for dev/raw elsewhere)
"""
import os, numpy as np, netCDF4 as nc
from scipy import ndimage
from PIL import Image

RAW = os.environ.get('KE_RAW', 'dev/raw')
d = nc.Dataset(f'{RAW}/paleomist/ice_reconstruction/global_grid/reconstruction_0.25_degree.nc'); d.set_auto_mask(False)
T = d['time'][:]
E = np.load(f'{RAW}/etopo/etopo60_i16.npy', mmap_mode='r')                  # 10800 x 21600, 1 arc-minute, north first
Em = np.asarray(E, np.float32).reshape(360, 30, 720, 30).mean((1, 3))         # 0.5-degree cell means, north first
# PaleoMIST nodes at 0.25 deg (lat -90..90, lon -180..180): the 0.5-degree cell centres are the odd nodes
ri = np.arange(1, 720, 2)[::-1]; ci = np.arange(1, 1440, 2)
def rise(k):
    P = d['paleo_topography'][k][np.ix_(ri, ci)]; H = d['ice_thickness'][k][np.ix_(ri, ci)]
    w = np.clip(H / 150, 0, 1); w = w * w * (3 - 2 * w)
    return ndimage.gaussian_filter(w * np.maximum(0, P - Em), 1.5, mode=('nearest', 'wrap'))   # broad domes, not bed bumps
r0 = rise(len(T) - 1)                                                        # today's mismatch (ice shelves, small glaciers): removed
out = np.zeros((360 * len(T), 720, 3), np.uint8)
for k in range(len(T)):
    r = np.clip(np.round(rise(k) - r0), 0, 65535).astype(np.uint16)
    out[k * 360:(k + 1) * 360, :, 0] = r >> 8; out[k * 360:(k + 1) * 360, :, 1] = r & 255
    print(int(1950 - (-T[k])), 'max', r.max(), 'cells', (r > 50).sum())
Image.fromarray(out).save('atlas/iceh.png', optimize=True)
print('years', [int(1950 + t) for t in T])
print(os.path.getsize('atlas/iceh.png') // 1024, 'KB')

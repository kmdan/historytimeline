"""Rebuild the ice onset/retreat channels of atlas/ice.png from PaleoMIST 1.0.

Source: Gowan et al. 2021, "A new global ice sheet reconstruction for the past 80 000 years", Nat. Commun. 12:1199,
  data PaleoMIST 1.0, https://doi.org/10.1594/PANGAEA.905800 (CC BY 4.0)
  -> dev/raw/paleomist/ice_reconstruction/global_grid/reconstruction_0.25_degree.nc  (ice_thickness, 2.5 kyr steps)

ice.png channels (2160x1080, 1/6 degree):  R = ice onset code, G = retreat code (255 = still ice today),
  B = farming start code (left unchanged). Codes follow iceCode(y) in the page.
Between two slices the margin is interpolated by distance: a cell that is ice at t0 and free at t1 melts at
  t0 + d0/(d0+d1)*(t1-t0), with d0 its distance inside the t0 margin and d1 its distance to the t1 ice (and the
  same for growth). Only the last glaciation of each cell is kept (the encoding has one interval).
Cells PaleoMIST never glaciates keep their previous codes (mountain glaciers from the schematic snowline model).
Run:  .venv/Scripts/python -I dev/scripts/build_ice_paleomist.py
"""
import numpy as np, netCDF4 as nc
from scipy import ndimage
from PIL import Image

def ice_code(y):                        # same as iceCode() in the page
    y = np.asarray(y, float)
    c = np.where(y <= -45000, 1, np.where(y <= -15000, np.round(1 + (y + 45000) / 30000 * 99), np.minimum(255, np.round(100 + (y + 15000) / 12000 * 154))))
    return c.astype(np.uint8)

d = nc.Dataset('dev/raw/paleomist/ice_reconstruction/global_grid/reconstruction_0.25_degree.nc'); d.set_auto_mask(False)
T = d['time'][:]; sel = [i for i, t in enumerate(T) if t >= -45000]          # 45 ka BP .. 0, oldest first
BP = [-T[i] for i in sel]; YR = [1950 - b for b in BP]
# 0.25 deg grid (lat -90..90, lon -180..180 inclusive) -> 1/6 deg cell centres, nearest
la = 90 - (np.arange(1080) + .5) / 6; lo = -180 + (np.arange(2160) + .5) / 6
ri = np.clip(np.round((la + 90) / .25).astype(int), 0, 720); ci = np.clip(np.round((lo + 180) / .25).astype(int), 0, 1440)
M = np.stack([(d['ice_thickness'][i][np.ix_(ri, ci)] > 1) for i in sel])     # (n, 1080, 2160) ice masks
n = len(sel)
dist_in = [ndimage.distance_transform_edt(m) for m in M]                      # distance inside ice
dist_out = [ndimage.distance_transform_edt(~m) for m in M]                    # distance to ice

on = np.full((1080, 2160), np.nan); off = np.full((1080, 2160), np.nan)
ever = M.any(0)
for k in range(n - 1):
    a, b = M[k], M[k + 1]
    t0, t1 = YR[k], YR[k + 1]
    grow = ~a & b; melt = a & ~b
    fg = dist_out[k] / np.maximum(dist_out[k] + dist_in[k + 1], 1e-6)          # growth: reached when margin passes
    fm = dist_in[k] / np.maximum(dist_in[k] + dist_out[k + 1], 1e-6)
    tg = t0 + fg * (t1 - t0); tm = t0 + fm * (t1 - t0)
    on = np.where(grow, tg, on); off = np.where(grow, np.nan, off)             # a new glaciation resets the interval
    off = np.where(melt, tm, off)
on = np.where(M[0] & np.isnan(on), YR[0] - 1, on)                              # already ice at 45 ka BP
still = M[-1]
old = np.array(Image.open('atlas/ice.png').convert('RGB'))
R = old[..., 0].copy(); G = old[..., 1].copy()
use = ever
R[use] = np.maximum(ice_code(on[use]), 1)
G[use] = np.where(still[use], 255, np.minimum(ice_code(np.nan_to_num(off[use], nan=1e9)), 254))
G[use & still] = 255
# cells whose last glaciation ended before 45 ka would have no interval: leave them ice-free
bad = use & ~still & np.isnan(off) & ~np.isnan(on)
R[bad] = 0
Image.fromarray(np.dstack([R, G, old[..., 2]]), 'RGB').save('atlas/ice.png', optimize=True)
print('slices', YR, '| cells from PaleoMIST', int(use.sum()), '| permanent', int(still.sum()))

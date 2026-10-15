"""Estimated height of the ice sheets of the older ice ages (505 ka -> 45 ka), for the relief shading of the map.

The deep-time snapshots (Krapp et al. 2021, atlas/biome_deep1..3.png, ice = class 9) give only the outline of the ice.
The height comes from the Nye (1952) perfectly plastic ice-sheet profile, thickness = sqrt(2 tau d / (rho g)), d = distance
inside the margin, with its scale fitted to PaleoMIST 1.0 at the Last Glacial Maximum (20,550 BCE): the same steps as
build_ice_height.py (rise above today's mean ETOPO, Gaussian smoothing, minus the same for today's ice), with the
PaleoMIST surface replaced by the profile; the baseline removed is the least ice of all snapshots
(cell by cell), since Krapp's Greenland/Antarctica outlines differ from today's. An estimate (marked so in CLAUDE.md); isostatic depression is in the fit.
Output: atlas/iceh_deep1.png, iceh_deep2.png: 360 x (180 * blocks) RGB, 1-degree cells, snapshot s in block s//3,
  channel s%3 (split 16/15 blocks like the biome files), value = rise / 16 m (0..255).
Run:    .venv/Scripts/python -I dev/scripts/build_ice_height_deep.py   (KE_RAW for dev/raw elsewhere)
"""
import os, numpy as np, netCDF4 as nc
from scipy import ndimage
from PIL import Image

RAW = os.environ.get('KE_RAW', 'dev/raw')
E = np.load(f'{RAW}/etopo/etopo60_i16.npy', mmap_mode='r')
Em = np.asarray(E, np.float32).reshape(360, 30, 720, 30).mean((1, 3))         # 0.5-degree cell means, north first
lat = 90 - (np.arange(360) + .5) / 2; KX = 55.6 * np.cos(np.radians(lat))[:, None]   # km per 0.5-degree cell, east-west

def dist_km(m):                       # distance (km) from each ice cell to the nearest cell without ice, lon wrapped
    m3 = np.concatenate([m, m, m], 1)
    _, (iy, ix) = ndimage.distance_transform_edt(m3, return_indices=True)
    yy, xx = np.mgrid[0:360, 0:2160]
    d = np.hypot((iy - yy) * 55.6, (ix - xx) * np.repeat(KX, 2160, 1))
    return np.where(m3, d, 0)[:, 720:1440]

def rise(m, a):                       # same steps as build_ice_height.py, profile a*sqrt(d km) for the surface
    return ndimage.gaussian_filter(m * np.maximum(0, a * np.sqrt(dist_km(m)) - Em), 1.5, mode=('nearest', 'wrap'))

# fit a on PaleoMIST at the LGM
d = nc.Dataset(f'{RAW}/paleomist/ice_reconstruction/global_grid/reconstruction_0.25_degree.nc'); d.set_auto_mask(False)
ri = np.arange(1, 720, 2)[::-1]; ci = np.arange(1, 1440, 2)
def pm(k):
    P = d['paleo_topography'][k][np.ix_(ri, ci)]; H = d['ice_thickness'][k][np.ix_(ri, ci)]
    w = np.clip(H / 150, 0, 1); w = w * w * (3 - 2 * w)
    return ndimage.gaussian_filter(w * np.maximum(0, P - Em), 1.5, mode=('nearest', 'wrap')), H > 1
k_lgm = list(d['time'][:]).index(-22500); (r_lgm, m_lgm), (r_now, m_now) = pm(k_lgm), pm(len(d['time'][:]) - 1)
ref = np.maximum(0, r_lgm - r_now); sel = m_lgm & ~m_now
best = min((np.abs(np.maximum(0, rise(m_lgm, a) - rise(m_now, a))[sel] - ref[sel]).mean(), a) for a in range(40, 161, 5))
A = best[1]; print('fit a =', A, 'm per sqrt(km); mean abs error', round(best[0]), 'm; PaleoMIST mean rise', round(ref[sel].mean()))

# deep snapshots
blocks = []
for f in ('atlas/biome_deep1.png', 'atlas/biome_deep2.png', 'atlas/biome_deep3.png'):
    a = np.asarray(Image.open(f).convert('RGB')); blocks += [a[i * 360:(i + 1) * 360] for i in range(a.shape[0] // 360)]
S = len(blocks) * 3; out = np.zeros((S // 3, 180, 360, 3), np.uint8)
R = [rise((blocks[s // 3][:, :, s % 3] == 9) & (Em > -150), A) for s in range(S)]   # the page draws ice on land only (glacial coasts ~ -120 m)
r0 = np.min(R, 0)                     # ice present in every snapshot (Greenland, Antarctica): already in ETOPO
for s in range(S):
    r = np.maximum(0, R[s] - r0).reshape(180, 2, 360, 2).mean((1, 3))
    out[s // 3, :, :, s % 3] = np.clip(np.round(r / 16), 0, 255)
    if s % 10 == 0: print(s, 'max', int(r.max()), 'm')
n1 = 16
for f, part in (('atlas/iceh_deep1.png', out[:n1]), ('atlas/iceh_deep2.png', out[n1:])):
    Image.fromarray(part.reshape(-1, 360, 3)).save(f, optimize=True); print(f, len(part), 'blocks', os.path.getsize(f) // 1024, 'KB')

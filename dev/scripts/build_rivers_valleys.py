"""Rivers that follow the valleys of the ETOPO relief.

Source courses: dev/data/rivers_basemap.json (today's rivers from matplotlib basemap-data, simplified at 0.04 deg,
stored as lon,lat x20 ints; the previous atlas/rivers.json, see build_rivers_coast.py.txt).
Each course is densified to 1 arc-minute steps; every point moves to the lowest ETOPO 2022 cell within +-2 arc-minutes
(~3.7 km), with a cost of 12 m per cell moved so lines don't jump between neighbouring valleys; the end points stay put.
The result is smoothed (5-point running mean), simplified (0.4 arc-minute) and stored as lon,lat x100 ints.

Input:  dev/data/rivers_basemap.json, dev/raw/etopo/etopo60_i16.npy (see build_elev.py)
Output: atlas/rivers.json  (list of flat [lon*100, lat*100, ...] polylines; the page divides by RIVS = 100)
Run:    .venv/Scripts/python -I dev/scripts/build_rivers_valleys.py   (KE_RAW for dev/raw elsewhere)
"""
import os, json
import numpy as np
from shapely.geometry import LineString

RAW = os.environ.get('KE_RAW', 'dev/raw')
E = np.load(f'{RAW}/etopo/etopo60_i16.npy', mmap_mode='r')
H, W = E.shape
src = json.load(open('dev/data/rivers_basemap.json'))
R, COST = 2, 12.0
dy, dx = np.mgrid[-R:R + 1, -R:R + 1]; pen = COST * np.hypot(dx, dy)
out, npts = [], 0
for pl in src:
    xy = np.array(pl, float).reshape(-1, 2) / 20
    seg = np.hypot(*np.diff(xy, axis=0).T); L = np.r_[0, np.cumsum(seg)]
    if L[-1] <= 0: continue
    t = np.linspace(0, L[-1], max(2, int(L[-1] * 60) + 1))
    p = np.c_[np.interp(t, L, xy[:, 0]), np.interp(t, L, xy[:, 1])]
    col = np.clip(((p[:, 0] + 180) * 60).astype(int), 0, W - 1); row = np.clip(((90 - p[:, 1]) * 60).astype(int), 0, H - 1)
    rr = np.clip(row[:, None, None] + dy, 0, H - 1); cc = (col[:, None, None] + dx) % W
    cost = np.asarray(E[rr, cc], np.float32) + pen
    k = cost.reshape(len(p), -1).argmin(1)
    q = np.c_[(cc.reshape(len(p), -1)[np.arange(len(p)), k] + .5) / 60 - 180, 90 - (rr.reshape(len(p), -1)[np.arange(len(p)), k] + .5) / 60]
    q[0], q[-1] = p[0], p[-1]
    if len(q) >= 5:
        sm = q.copy(); ker = np.ones(5) / 5
        for d in (0, 1): sm[2:-2, d] = np.convolve(q[:, d], ker, 'valid')
        q = sm
    ls = LineString(q).simplify(0.4 / 60)
    c = np.round(np.array(ls.coords) * 100).astype(int).ravel().tolist(); npts += len(c) // 2
    out.append(c)
json.dump(out, open('atlas/rivers.json', 'w'), separators=(',', ':'))
print(len(out), 'rivers', npts, 'points', os.path.getsize('atlas/rivers.json') // 1024, 'KB')

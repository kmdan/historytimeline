"""Build atlas/slw.png: GIA-corrected land/sea history 26 ka BP -> today at 1/6 degree.

Source: De Groeve et al. 2022, "Shelf sea extent rasters (SLW140 2021)", CC BY 4.0,
https://doi.org/10.21942/uva.20029220.v1  (SLW_mosaic.zip -> dev/raw/slw/SLW000.tif ... SLW260.tif,
2 arc-min, one raster per 500 yr; 0 = above past sea level, 1 = 0..-140 m below past sea level, nodata = deeper).

Water that is not connected to a deep basin (nodata) is treated as land, so inland depressions below sea level
(Qattara, Turfan, Death Valley...) are not flooded. Each 1/6-degree cell gets its land fraction per slice; the times
where that fraction crosses 0.5 are interpolated between slices.

Output PNG (2160x1080 RGB):
  R = first land/sea switch, G = second switch (code 1..255 = years BP 0..26000; 0 = none)
  B = state at 26 ka BP (255 land, 0 sea)
Cells with more than two switches keep the switches that preserve the final (present) state.
Run:  .venv/Scripts/python -I dev/scripts/build_coast_slw.py
"""
import glob, logging
import numpy as np, tifffile
from scipy import ndimage
from PIL import Image

logging.disable(logging.WARNING)
fs = sorted(glob.glob('dev/raw/slw/SLW*.tif'))      # SLW000 (0 BP) ... SLW260 (26,000 BP)
assert len(fs) == 53, len(fs)
L = np.zeros((53, 1080, 2160), np.float32)
for i, f in enumerate(fs):
    a = tifffile.imread(f)
    a = np.pad(a, ((0, 0), (0, 10800 - a.shape[1])), mode='edge')
    deep = a < -1e30
    water = a != 0
    lab, n = ndimage.label(water)
    keep = np.zeros(n + 1, bool); keep[np.unique(lab[deep])] = True; keep[0] = False
    land = ~keep[lab]
    L[i] = land.reshape(1080, 5, 2160, 5).mean((1, 3))
    print(f, n, 'water bodies')

BP = np.arange(53) * 500.0
B = L >= 0.5
code = lambda bp: np.clip(np.round(1 + bp / 26000 * 254), 1, 255).astype(np.uint8)
R = np.zeros((1080, 2160), np.uint8); G = np.zeros_like(R)
init = B[52]
# crossings, from old to young: between slice i+1 (older) and i (younger)
cross = []
for i in range(51, -1, -1):
    c = B[i] != B[i + 1]
    f0, f1 = L[i + 1], L[i]
    t = np.where(c, (0.5 - f0) / np.where(f1 - f0 == 0, 1, f1 - f0), 0)        # 0..1 from older to younger
    cross.append((c, BP[i + 1] - np.clip(t, 0, 1) * 500))
cnt = sum(c.astype(np.int32) for c, _ in cross)
first = np.full(R.shape, np.nan); second = np.full(R.shape, np.nan); last = np.full(R.shape, np.nan)
for c, bp in cross:
    first = np.where(c & np.isnan(first), bp, first)
    second = np.where(c & ~np.isnan(first) & np.isnan(second) & (bp != first), bp, second)
    last = np.where(c, bp, last)
one = cnt == 1; two = cnt == 2; odd = (cnt > 2) & (cnt % 2 == 1); even = (cnt > 2) & (cnt % 2 == 0)
R[one] = code(first[one]); R[two] = code(first[two]); G[two] = code(second[two])
R[odd] = code(last[odd])
R[even] = code(first[even]); G[even] = code(last[even])
# sanity: decoded present state must equal slice 0
flips = (R > 0).astype(int) + (G > 0).astype(int)
assert np.array_equal(init ^ (flips % 2 == 1), B[0])
Image.fromarray(np.dstack([R, G, np.where(init, 255, 0).astype(np.uint8)])).save('atlas/slw.png', optimize=True)
print('switch counts', np.unique(cnt, return_counts=True))

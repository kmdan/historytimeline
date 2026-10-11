"""Build biome snapshots and climate tables from published reconstructions.

Sources (download into dev/raw/):
  beyer/LateQuaternary_Environment.nc  Beyer, Krapp & Manica 2020, Sci. Data 7:236, CC BY 4.0
      https://doi.org/10.6084/m9.figshare.12293345   (0.5 deg, BIOME4 biomes + BIO1 annual mean temperature)
  osman/LGMR_GMST_ens.nc              Osman et al. 2021, Nature 599:239 (LGMR), NOAA NCEI
      https://www.ncei.noaa.gov/pub/data/paleo/reconstructions/osman2021/
  kaufman/temp12k_allmethods_percentiles.csv   Kaufman et al. 2020, Sci. Data 7:201 (Temp12k GMST), NOAA NCEI
      https://www.ncei.noaa.gov/pub/data/paleo/reconstructions/kaufman2020/

Outputs:
  atlas/biome_beyer.png  720 x (360*11) RGB: snapshot s is block s//3, channel s%3; rows north->south (90..-90 deg),
                         classes 1 rainforest 2 savanna 3 desert 4 steppe 5 mediterranean 6 temperate forest
                         7 boreal 8 tundra 9 ice 10 mammoth steppe (0 = none)
  <script id="climdata"> in karahan-era.html: snapshot years, BIO1 at the CLIM label points, GMST curves.
Adjustment: HadCM3 keeps the Sahara/Arabia dry in the early-mid Holocene; the African Humid Period is applied with
the same rule as the previous Koppen-based build (greenFactor in the page).
Run:  .venv/Scripts/python -I dev/scripts/build_climate.py
"""
import json, re, io
import numpy as np, netCDF4 as nc
from scipy import ndimage
from PIL import Image

PAGE = 'karahan-era.html'
d = nc.Dataset('dev/raw/beyer/LateQuaternary_Environment.nc'); d.set_auto_mask(False)
T = d['time'][:]; lat = d['latitude'][:]; lon = d['longitude'][:]
sel = [i for i, t in enumerate(T) if t >= -42000]
years = [int(1950 + T[i]) for i in sel]
# BIOME4 (28 classes) -> page classes
MAP = np.zeros(29, np.uint8)
for c, b in {1: 1, 2: 1, 3: 2, 4: 6, 5: 6, 6: 6, 7: 6, 8: 7, 9: 7, 10: 7, 11: 7, 12: 2, 13: 2, 14: 5, 15: 5, 16: 4, 17: 7, 18: 7,
             19: 2, 20: 4, 21: 3, 22: 10, 23: 8, 24: 8, 25: 8, 26: 8, 27: 8, 28: 9}.items():
    MAP[c] = b
LA = np.repeat((90 - (np.arange(360) + .5) / 2)[:, None], 720, 1); LO = np.repeat((-180 + (np.arange(720) + .5) / 2)[None, :], 360, 0)
rng = np.random.default_rng(7)
NZ = ndimage.gaussian_filter(rng.random((360, 720)), 2.5, mode='wrap'); NZ = (NZ.argsort(None).argsort().reshape(NZ.shape) / NZ.size)

def north_up(a):            # Beyer rows: -59.75 .. 89.75 -> 360 rows 89.75 .. -89.75 (pad Antarctica)
    a = a[::-1]
    return np.vstack([a, np.full((60, 720), np.nan, a.dtype)])

def fill(a):                # nearest valid value for every cell (coasts differ between models)
    m = np.isnan(a)
    _, (iy, ix) = ndimage.distance_transform_edt(m, return_indices=True)
    return a[iy, ix]

def green_factor(y):
    if y < -9500 or y > -3000: return 0
    if y < -9000: return (y + 9500) / 500
    if y < -4000: return 1
    return 1 - (y + 4000) / 1000

w = np.clip((LA - 12) / 4, 0, 1) * np.clip((33 - LA) / 4, 0, 1) * np.clip((LO + 18) / 4, 0, 1) * np.clip((36 - LO) / 4, 0, 1)
w = np.maximum(w, 0.8 * np.clip((LA - 13) / 4, 0, 1) * np.clip((31 - LA) / 4, 0, 1) * np.clip((LO - 36) / 3, 0, 1) * np.clip((59 - LO) / 4, 0, 1))
# Glacial Eurasia: HadCM3/BIOME4 puts taiga over Europe at the LGM, while pollen syntheses (BIOME 6000; Prentice et al.
# 2000) show open steppe-tundra. Same rule as the previous build: with glacial coldness c, boreal/tundra cells in
# Europe/N Asia/Beringia become mammoth steppe, and southern European forest opens to grassland.
EUR = (LO > -25) & (LAT_ := LA > 0) & (LO < 180); BER = ((LO < -140) | (LO > 150)) & (LA > 55)
COLD = [(-40000, .55), (-24000, 1), (-17000, .9), (-12700, .45), (-10900, .6), (-9000, .1), (-8000, 0)]
def coldness(y):
    if y <= COLD[0][0]: return COLD[0][1]
    for (y0, c0), (y1, c1) in zip(COLD, COLD[1:]):
        if y <= y1: return c0 + (c1 - c0) * (y - y0) / (y1 - y0)
    return 0
ALA = np.abs(LA)
snaps, bio1 = [], []
for i, y in zip(sel, years):
    b = north_up(d['biome'][i].astype(np.float32)); b[b == 0] = np.nan          # water bodies -> nearest land class
    B = MAP[fill(b).astype(int)]
    c = coldness(y)
    if c > 0.25:
        B[(EUR | BER) & (ALA > 40) & (ALA < 72) & np.isin(B, [6, 7, 8]) & (NZ < 0.35 + 0.6 * c)] = 10
    if c > 0.5:
        B[EUR & (ALA > 36) & (ALA < 48) & (B == 6) & (NZ < 0.45 * c)] = 4
    g = green_factor(y)
    if g > 0:
        wet = np.isin(B, [3, 4]) & (w * g > NZ * 0.9 + 0.05)
        B[wet & (LA < 22)] = 2; B[wet & (LA >= 22)] = 4
    snaps.append(B)
    bio1.append(fill(north_up(d['BIO1'][i].astype(np.float32))))
while len(snaps) % 3: snaps.append(snaps[-1])
img = np.vstack([np.dstack(snaps[k:k + 3]) for k in range(0, len(snaps), 3)]).astype(np.uint8)
Image.fromarray(img, 'RGB').save('atlas/biome_beyer.png', optimize=True)

# BIO1 at the climate label points listed in the page (CLIM)
html = io.open(PAGE, encoding='utf-8', newline='').read()
clim = re.findall(r"\['([^']+)',(-?[\d.]+),(-?[\d.]+),(-?[\d.]+),[01]\]", html[html.index('const CLIM='):html.index(']];', html.index('const CLIM='))+3])
pts = {}
for n, la_, lo_, _ in clim:
    r = int(np.clip((90 - float(la_)) * 2, 0, 359)); c = int(np.clip((float(lo_) + 180) * 2, 0, 719))
    pts[n] = [round(float(a[r, c]), 1) for a in bio1]

# global mean temperature, anomalies vs 1800-1900 CE
o = nc.Dataset('dev/raw/osman/LGMR_GMST_ens.nc'); o.set_auto_mask(False)
age = o['age'][:]; ens = o['gmst'][:]                       # (500, 120)
ref = ens[:, age == 100].mean()
p5, p50, p95 = (np.percentile(ens, q, axis=0) - ref for q in (5, 50, 95))
osman = [[int(1950 - a), round(float(m), 2), round(float(l), 2), round(float(h), 2)] for a, m, l, h in zip(age, p50, p5, p95)][::-1]
k = np.genfromtxt('dev/raw/kaufman/temp12k_allmethods_percentiles.csv', delimiter=',', skip_header=1)
kaufman = [[int(1950 - r[0]), round(float(r[2]), 2), round(float(r[1]), 2), round(float(r[3]), 2)] for r in k][::-1]

data = {'years': years, 'bio1': pts, 'osman': osman, 'kaufman': kaufman,
        'src': {'biomes': 'Beyer, Krapp & Manica 2020', 'osman': 'Osman et al. 2021', 'kaufman': 'Kaufman et al. 2020'}}
tag = '<script id="climdata" type="application/json">'
blob = tag + json.dumps(data, separators=(',', ':'), ensure_ascii=False) + '</script>'
if tag in html:
    a = html.index(tag); b = html.index('</script>', a) + len('</script>')
    html = html[:a] + blob + html[b:]
else:
    a = html.index('<script id="research"')
    html = html[:a] + blob + '\n' + html[a:]
io.open(PAGE, 'w', encoding='utf-8', newline='').write(html)
print(len(years), 'snapshots', years[:3], '...', years[-3:], '| points', len(pts), '| png', img.shape)

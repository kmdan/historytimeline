"""Deep-time biome snapshots (505 ka -> 45 ka, every 5 kyr) from Krapp et al. 2021.

Source (download into dev/raw/krapp/; CC BY 4.0, pastclim copy on Zenodo record 8415273):
  Krapp2021_biome_v1.2.2.nc   BIOME4 biomes, 0.5 deg, 1 kyr, 800 ka -> 0 (ice sheets = class 28)
  Krapp2021_bio01_v1.4.0.nc   BIO1 annual mean temperature, same grid
  Krapp, Beyer, Edmundson, Valdes & Manica 2021, Sci. Data 8:228, https://doi.org/10.1038/s41597-021-01009-3
Sea level for the glacial-steppe correction: dev/raw/deep/spratt2016-noaa.txt (Spratt & Lisiecki 2016).

Outputs:
  atlas/biome_deep1..3.png   720 x (360*blocks) RGB, same encoding and classes as atlas/biome_beyer.png
                             (snapshot s is block s//3, channel s%3); 93 snapshots = 31 blocks, split 11/11/9 so each
                             image stays under 4,000 px tall for phones
  <script id="climdeep">    {years (signed, oldest first), bio1 at the CLIM label points, files [[path, blocks]], src}
The page joins these in front of the Beyer et al. 2020 snapshots (42 ka -> now).
Correction (as in build_climate.py): in cold phases HadCM3/BIOME4 puts taiga where pollen shows open steppe-tundra;
glacial coldness is taken from sea level here (0 at -35 m, 1 at -125 m).
Run:  .venv/Scripts/python -I dev/scripts/build_climate_deep.py
"""
import json, re, io, os
import numpy as np, netCDF4 as nc
from scipy import ndimage
from PIL import Image

PAGE = 'karahan-era.html'
RAW = os.environ.get('KE_RAW', 'dev/raw')        # raw downloads (git-ignored)
KAS = list(range(505, 44, -5))                      # 93 snapshots, oldest first (a multiple of 3)
d = nc.Dataset(f'{RAW}/krapp/Krapp2021_biome_v1.2.2.nc'); d.set_auto_mask(False)
T = list(d['time'][:]); idx = {int(round(-t / 1000)): i for i, t in enumerate(T)}
t1 = nc.Dataset(f'{RAW}/krapp/Krapp2021_bio01_v1.4.0.nc'); t1.set_auto_mask(False)
T1 = list(t1['time'][:]); idx1 = {int(round(-t / 1000)): i for i, t in enumerate(T1)}
v1 = [v for v in t1.variables if v not in ('time', 'latitude', 'longitude', 'lat', 'lon')][0]

MAP = np.zeros(29, np.uint8)                        # BIOME4 -> page classes (same table as build_climate.py)
for c, b in {1: 1, 2: 1, 3: 2, 4: 6, 5: 6, 6: 6, 7: 6, 8: 7, 9: 7, 10: 7, 11: 7, 12: 2, 13: 2, 14: 5, 15: 5, 16: 4, 17: 7, 18: 7,
             19: 2, 20: 4, 21: 3, 22: 10, 23: 8, 24: 8, 25: 8, 26: 8, 27: 8, 28: 9}.items():
    MAP[c] = b
LA = np.repeat((90 - (np.arange(360) + .5) / 2)[:, None], 720, 1); LO = np.repeat((-180 + (np.arange(720) + .5) / 2)[None, :], 360, 0)
rng = np.random.default_rng(7)
NZ = ndimage.gaussian_filter(rng.random((360, 720)), 2.5, mode='wrap'); NZ = (NZ.argsort(None).argsort().reshape(NZ.shape) / NZ.size)
EUR = (LO > -25) & (LA > 0) & (LO < 180); BER = ((LO < -140) | (LO > 150)) & (LA > 55); ALA = np.abs(LA)

def north_up(a): return a[::-1].astype(np.float32)  # Krapp rows -89.75 .. 89.75 -> north first

def fill(a):                                        # nearest valid value for every cell
    m = np.isnan(a)
    _, (iy, ix) = ndimage.distance_transform_edt(m, return_indices=True)
    return a[iy, ix]

sea = {}
for line in open(f'{RAW}/deep/spratt2016-noaa.txt', encoding='utf-8'):
    p = line.split('\t')
    try: ka = int(p[0]); s, l = float(p[1]), float(p[5])
    except (ValueError, IndexError): continue
    sea[ka] = s if ka <= 430 and not np.isnan(s) else l

snaps, bio1 = [], []
for ka in KAS:
    b = north_up(d['biome'][idx[ka]]); b[(b < 1) | (b > 28)] = np.nan
    B = MAP[fill(b).astype(int)]
    c = float(np.clip((-sea[ka] - 35) / 90, 0, 1))
    if c > 0.25:
        B[(EUR | BER) & (ALA > 40) & (ALA < 72) & np.isin(B, [6, 7, 8]) & (NZ < 0.35 + 0.6 * c)] = 10
    if c > 0.5:
        B[EUR & (ALA > 36) & (ALA < 48) & (B == 6) & (NZ < 0.45 * c)] = 4
    snaps.append(B)
    t = north_up(t1[v1][idx1[ka]]); t[(t < -90) | (t > 60)] = np.nan
    bio1.append(fill(t))

files, blocks = [], [np.dstack(snaps[k:k + 3]) for k in range(0, len(snaps), 3)]
for n, (a, z) in enumerate([(0, 11), (11, 22), (22, len(blocks))], 1):
    path = f'atlas/biome_deep{n}.png'
    Image.fromarray(np.vstack(blocks[a:z]).astype(np.uint8), 'RGB').save(path, optimize=True)
    files.append([path, z - a])

html = io.open(PAGE, encoding='utf-8', newline='').read()
clim = re.findall(r"\['([^']+)',(-?[\d.]+),(-?[\d.]+),(-?[\d.]+),[01]\]", html[html.index('const CLIM='):html.index(']];', html.index('const CLIM='))+3])
pts = {}
for n_, la_, lo_, _ in clim:
    r = int(np.clip((90 - float(la_)) * 2, 0, 359)); c_ = int(np.clip((float(lo_) + 180) * 2, 0, 719))
    pts[n_] = [round(float(a[r, c_]), 1) for a in bio1]
data = {'years': [int(1950 - ka * 1000) for ka in KAS], 'bio1': pts, 'files': files, 'src': 'Krapp et al. 2021 (CC BY 4.0)'}
tag = '<script id="climdeep" type="application/json">'
blob = tag + json.dumps(data, separators=(',', ':'), ensure_ascii=False) + '</script>'
if tag in html:
    a = html.index(tag); z = html.index('</script>', a) + len('</script>'); html = html[:a] + blob + html[z:]
else:
    a = html.index('<script id="climdata"'); html = html[:a] + blob + '\n' + html[a:]
io.open(PAGE, 'w', encoding='utf-8', newline='').write(html)
print(len(KAS), 'snapshots', data['years'][:2], '...', data['years'][-2:], '| files', files, '| points', len(pts))

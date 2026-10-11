"""Build atlas/popd.png: HYDE population density, 10,000 BCE - 2015 CE, 0.5 degree, log-coded.

Source: HYDE 3.2.1 baseline (Klein Goldewijk et al. 2017, ESSD 9:927, https://doi.org/10.5194/essd-9-927-2017),
  DANS https://doi.org/10.17026/DANS-25G-GEZ3 (readme: CC BY 3.0). popd_<year>.asc (5 arc-min, people/km2)
  -> dev/raw/hyde/ (dev/raw/hyde/fetch.py pulls only those files out of the 5 GB zip).
(HYDE 3.3 is on Utrecht's YODA, which is behind a bot check; 3.2.1 is the same method, data to 2015.)

Output: atlas/popd.png 720 x (360*blocks) RGB, snapshot s in block s//3 channel s%3, rows north->south;
  code 0 = nobody/no data, else round((log10(density)+3)*32) clamped 1..255  (0.001 .. ~10^5 per km2).
  Snapshot years are embedded in the page as <script id="popdata">.
Run:  .venv/Scripts/python -I dev/scripts/build_hyde.py
"""
import glob, io, json, os, re
import numpy as np
from PIL import Image

def year_of(f):
    m = re.search(r'popd_(\d+)(AD|BC)\.asc', os.path.basename(f)); v = int(m.group(1))
    return -v if m.group(2) == 'BC' else v
files = sorted(glob.glob('dev/raw/hyde/popd_*.asc'), key=year_of)
keep = [f for f in files if (y := year_of(f)) <= 1700 or y % 10 == 0 or y == 2015]
snaps, years = [], []
for f in keep:
    a = np.loadtxt(f, skiprows=6, dtype=np.float32)            # 2160 x 4320, north row first
    a[a < 0] = np.nan
    land = np.isfinite(a)
    s = np.where(land, a, 0).reshape(360, 6, 720, 6).sum((1, 3)); n = land.reshape(360, 6, 720, 6).sum((1, 3))
    d = np.where(n > 0, s / np.maximum(n, 1), 0)                 # mean density over the land part of each 0.5 deg cell
    code = np.where(d > 0, np.clip(np.round((np.log10(np.maximum(d, 1e-9)) + 3) * 32), 1, 255), 0).astype(np.uint8)
    snaps.append(code); years.append(year_of(f)); print(os.path.basename(f), flush=True)
while len(snaps) % 3: snaps.append(snaps[-1]); years.append(years[-1])
img = np.vstack([np.dstack(snaps[k:k + 3]) for k in range(0, len(snaps), 3)])
Image.fromarray(img, 'RGB').save('atlas/popd.png', optimize=True)
p = 'karahan-era.html'; html = io.open(p, encoding='utf-8', newline='').read()
tag = '<script id="popdata" type="application/json">'
blob = tag + json.dumps({'years': years}, separators=(',', ':')) + '</script>'
if tag in html:
    a_ = html.index(tag); b_ = html.index('</script>', a_) + 9; html = html[:a_] + blob + html[b_:]
else:
    a_ = html.index('<script id="research"'); html = html[:a_] + blob + '\n' + html[a_:]
io.open(p, 'w', encoding='utf-8', newline='').write(html)
print(len(years), 'snapshots', img.shape)

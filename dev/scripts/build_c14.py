"""Calibrate and bin radiocarbon dates from p3k14c + XRONOS into atlas/c14.json (0.5 degree cell x 100-year bins).

Sources:
  p3k14c (Bird et al. 2022, Sci. Data 9:27; https://github.com/people3k/p3k14c, CC0)  -> dev/raw/p3k14c/p3k14c_data.rda
  XRONOS (Roe et al. 2025, https://doi.org/10.5334/jcaa.191; https://xronos.ch, CC BY 4.0) -> dev/raw/xronos/data.json
      (download: https://xronos.ch/api/v1/data)
  IntCal20 (Reimer et al. 2020; https://intcal.org/curves/intcal20.14c) -> dev/raw/p3k14c/intcal20.14c
Dates are de-duplicated by lab number (p3k14c first), calibrated with a weighted-mean approximation on IntCal20
(as before), filtered for plausible errors, and counted per 0.5-degree cell and century.
Output format (unchanged): {bin, start, cells:[lon,lat,...], bins:{binIndex:[cellIndex,count,...]}}
Run:  .venv/Scripts/python -I dev/scripts/build_c14.py
"""
import json, re, warnings
import numpy as np, rdata
from collections import Counter
warnings.filterwarnings('ignore')

cur = np.loadtxt('dev/raw/p3k14c/intcal20.14c', delimiter=',', comments='#'); cal, c14, sig = cur[:, 0], cur[:, 1], cur[:, 2]
norm = lambda s: re.sub(r'[^A-Z0-9]', '', str(s).upper()) if s else ''
p3 = rdata.conversion.convert(rdata.parser.parse_file('dev/raw/p3k14c/p3k14c_data.rda'))['p3k14c_data']
rows, seen = [], set()
for lab, a, e, lo, la in zip(p3['LabID'], p3['Age'], p3['Error'], p3['Long'], p3['Lat']):
    k = norm(lab)
    if k: seen.add(k)
    rows.append((a, e, lo, la))
n_p3 = len(rows); dup = 0
for r in json.load(open('dev/raw/xronos/data.json', encoding='utf-8')):
    m = r['measurement']; k = norm(m['labnr'])
    if k and k in seen: dup += 1; continue
    if k: seen.add(k)
    rows.append((m['bp'], m['std'], m['lng'], m['lat']))
A = np.array(rows, dtype=object)
def f(c): return np.array([np.nan if v is None else float(v) for v in A[:, c]])
age, err, lon, lat = f(0), f(1), f(2), f(3)
ok = np.isfinite(age) & np.isfinite(err) & np.isfinite(lon) & np.isfinite(lat) & (age > 0) & (age < 45000) & (err > 0) & (err <= np.maximum(300, age * 0.03)) & (np.abs(lat) <= 90) & (np.abs(lon) <= 180) & ~((lat == 0) & (lon == 0))
age, err, lon, lat = age[ok], err[ok], lon[ok], lat[ok]
out = np.empty(len(age))
for i in range(0, len(age), 2000):
    a = age[i:i + 2000, None]; e = err[i:i + 2000, None]
    w = np.exp(-(c14[None, :] - a) ** 2 / (2 * (e ** 2 + sig[None, :] ** 2)))
    out[i:i + 2000] = (w * cal[None, :]).sum(1) / np.maximum(w.sum(1), 1e-12)
yr = 1950 - out; lon = np.round(lon * 2) / 2; lat = np.round(lat * 2) / 2
BIN = 100; S = -45000; b = np.floor((yr - S) / BIN).astype(int)
ok = (b >= 0) & (yr <= 1950)
cells = {}; cnt = Counter()
for bb, lo, la in zip(b[ok], lon[ok], lat[ok]):
    k = (float(lo), float(la)); cells.setdefault(k, len(cells)); cnt[(int(bb), cells[k])] += 1
cl = sorted(cells, key=cells.get); bins = {}
for (bb, ci), nn in cnt.items(): bins.setdefault(bb, []).extend([ci, nn])
json.dump({'bin': BIN, 'start': S, 'cells': [c for xy in cl for c in xy], 'bins': bins}, open('atlas/c14.json', 'w'), separators=(',', ':'))
print(f'p3k14c {n_p3}, XRONOS added {len(rows) - n_p3} (duplicates skipped {dup}), usable {int(ok.sum())}, cells {len(cells)}')

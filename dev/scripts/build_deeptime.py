"""Deep-time curves (500 ka -> 42 ka) for the page's <script id="deepdata"> block.

Inputs (dev/raw/deep/, from NOAA NCEI paleo, free with citation):
  spratt2016-noaa.txt               Spratt & Lisiecki 2016 sea-level stack (1 kyr; shortPC1 to 430 ka, longPC1 beyond)
  antarctica2015co2composite.txt    Bereiter et al. 2015 CO2 composite (AICC2012)
  edc3deuttemp2007.txt              Jouzel et al. 2007 EPICA Dome C temperature anomaly (vs last 1000 yr, EDC3)
Output: JSON {sea, co2, tmp} as [[signed year, value], ...], 1 kyr steps, oldest first,
for ages >= 42 ka (the page's own curves take over from 40,000 BCE).

Global temperature is a rough estimate: Antarctic anomaly x 0.63 when colder than today
(matches about -6 C global at the Last Glacial Maximum) and x 0.3 when warmer (polar
amplification is stronger in warm periods; gives about +1.2 C for the Last Interglacial).
Run:  .venv/Scripts/python -I dev/scripts/build_deeptime.py  [page]   (rewrites the deepdata block in the page)
"""
import json, re, sys, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'dev' / 'raw' / 'deep'
PAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'karahan-era.html'
KA0, KA1 = 42, 500                      # range in ka BP

def rows(name, skip_hash=True):
    for line in (RAW / name).read_text(encoding='utf-8-sig', errors='replace').splitlines():
        if skip_hash and line.startswith('#'): continue
        parts = line.split()
        try: yield [float(p) for p in parts]
        except ValueError: continue

def year(ka): return round(1950 - ka * 1000)   # BP (1950) -> signed calendar year

# sea level: 1 kyr stack
sea = {}
for r in rows('spratt2016-noaa.txt'):
    if len(r) < 6: continue
    ka, short, long_ = int(r[0]), r[1], r[5]
    v = short if ka <= 430 and not math.isnan(short) else long_
    if KA0 <= ka <= KA1 and not math.isnan(v): sea[ka] = round(v, 1)

def binned(pairs):   # mean per 1 kyr bin centred on whole ka
    acc = {}
    for ka, v in pairs:
        k = round(ka)
        if KA0 <= k <= KA1: acc.setdefault(k, []).append(v)
    return {k: sum(v) / len(v) for k, v in acc.items()}

co2 = binned((r[0] / 1000, r[1]) for r in rows('antarctica2015co2composite.txt') if len(r) >= 2)
edc = binned((r[2] / 1000, r[4]) for r in rows('edc3deuttemp2007.txt', False) if len(r) == 5)

def fill(d):         # linear fill of empty bins
    ks = sorted(d); out = {}
    for k in range(KA0, KA1 + 1):
        if k in d: out[k] = d[k]; continue
        lo = max((x for x in ks if x < k), default=None); hi = min((x for x in ks if x > k), default=None)
        if lo is None or hi is None: out[k] = d[lo if hi is None else hi]
        else: out[k] = d[lo] + (d[hi] - d[lo]) * (k - lo) / (hi - lo)
    return out

co2, edc = fill(co2), fill(edc)
tmp = {k: round(v * (0.63 if v < 0 else 0.3), 2) for k, v in edc.items()}
series = lambda d, nd=1: [[year(k), round(d[k], nd)] for k in sorted(d, reverse=True)]
out = {'sea': series(sea), 'co2': series(co2, 0), 'tmp': series(tmp, 2),
       'src': 'Spratt & Lisiecki 2016; Bereiter et al. 2015; Jouzel et al. 2007 (scaled, estimate)'}
js = json.dumps(out, separators=(',', ':'))

s = PAGE.read_text(encoding='utf-8')
tag = '<script id="deepdata" type="application/json">'
if tag in s: s = re.sub(re.escape(tag) + r'.*?</script>', lambda m: tag + js + '</script>', s, count=1, flags=re.S)
else: s = s.replace('<script id="climdata"', tag + js + '</script>\n<script id="climdata"', 1)
PAGE.write_text(s, encoding='utf-8', newline='')
print(len(out['sea']), 'kyr steps;', 'sea', min(v for _, v in out['sea']), max(v for _, v in out['sea']),
      '| co2', min(v for _, v in out['co2']), max(v for _, v in out['co2']),
      '| tmp', min(v for _, v in out['tmp']), max(v for _, v in out['tmp']), '|', len(js), 'bytes')

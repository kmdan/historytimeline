"""Dated finds of human species, 505 ka -> 30 ka, for the 'Human species' map layer.

Source: Timmermann et al. 2022, Nature 604:495, Supplementary Table 1 ('raw data' sheet: species, lon, lat, site,
level, max/mean/min age, cultural attribution; CC BY 4.0), saved as dev/raw/timmermann/41586_2022_4600_MOESM3_ESM.xlsx
  https://doi.org/10.1038/s41586-022-04600-9
Species missing from that table are added by hand (dates as in dev/data/deep_eras.json, from Wikipedia).
Output atlas/hominins.json:
  sp:   [[key, common name, scientific name, Wikipedia title], ...]   (index = species id; key 'unc' = uncertain)
  site: [[name, cultures], ...]
  f:    [[species id, site id, lat, lon, from, to], ...]   signed years (BCE negative), one row per site and species,
        overlapping levels merged
Run:  .venv/Scripts/python -I dev/scripts/build_hominins.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xlsx_min

RAW = os.environ.get('KE_RAW', 'dev/raw')
SP = [['sap', 'Modern humans', 'Homo sapiens', 'Homo sapiens'],
      ['nea', 'Neanderthals', 'Homo neanderthalensis', 'Neanderthal'],
      ['hei', 'Archaic humans', 'Homo heidelbergensis', 'Homo heidelbergensis'],
      ['ere', 'Homo erectus', 'Homo erectus', 'Homo erectus'],
      ['den', 'Denisovans', 'no formal species name yet', 'Denisovan'],
      ['flo', '“Hobbits” of Flores', 'Homo floresiensis', 'Homo floresiensis'],
      ['luz', 'Homo luzonensis', 'Homo luzonensis', 'Homo luzonensis'],
      ['nal', 'Homo naledi', 'Homo naledi', 'Homo naledi'],
      ['unc', 'Uncertain species', 'two species proposed', 'Archaic humans']]
IDX = {'Homo sapiens': 0, 'Homo neanderthalensis': 1, 'Homo heidelbergensis': 2, 'Homo erectus': 3}
# hand-added finds: species, site, lat, lon, years ago (oldest, youngest), culture
EXTRA = [(4, 'Denisova Cave', 51.397, 84.676, 217000, 52000, 'Denisovan fossils and sediment DNA'),
         (4, 'Baishiya Karst Cave (Xiahe mandible)', 35.448, 102.571, 190000, 160000, 'Denisovan jaw, at least 160,000 years old'),
         (5, 'Liang Bua', -8.534, 120.461, 100000, 60000, 'Skeletons; stone tools to about 50,000 years ago'),
         (6, 'Callao Cave', 17.703, 121.824, 67000, 50000, 'Teeth and bones'),
         (7, 'Rising Star Cave', -26.016, 27.712, 335000, 236000, 'Remains deep in the cave system')]

def signed(ya): return int(1950 - ya)

rows = list(xlsx_min.rows(f'{RAW}/timmermann/41586_2022_4600_MOESM3_ESM.xlsx', 'raw data'))[1:]
groups = {}
for r in rows:
    if len(r) < 9 or not isinstance(r[6], float) or not isinstance(r[8], float): continue
    spn, lon, lat, site, mx, mn = r[1].strip(), r[2], r[3], str(r[4]).strip(), r[6], r[8]
    if mn > 505000 or not isinstance(lat, float) or not isinstance(lon, float): continue
    sid = IDX.get(spn, 8 if '/' in spn and any(s in spn for s in IDX) else None)
    if sid is None: continue
    cult = str(r[9]).strip() if len(r) > 9 and r[9] else ''
    g = groups.setdefault((site, sid), {'lat': lat, 'lon': lon, 'iv': [], 'cult': set()})
    g['iv'].append((min(mx, 505000), mn))
    if cult and cult.lower() not in ('na', 'n/a', 'unknown'): g['cult'].add(cult)
for sid, site, lat, lon, a, b, note in EXTRA:
    groups[(site, sid)] = {'lat': lat, 'lon': lon, 'iv': [(a, b)], 'cult': {note}}

sites, sidx, out = [], {}, []
for (site, sid), g in sorted(groups.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    if (site, sid) not in sidx:              # cultures differ by species at shared sites (e.g. Denisova Cave)
        sidx[(site, sid)] = len(sites); sites.append([site, '; '.join(sorted(g['cult']))[:120]])
    iv = sorted(g['iv'], key=lambda t: -t[0]); merged = [list(iv[0])]
    for a, b in iv[1:]:                       # ages: a older (bigger) than b
        if a >= merged[-1][1] - 2000: merged[-1][1] = min(merged[-1][1], b)
        else: merged.append([a, b])
    for a, b in merged:
        out.append([sid, sidx[(site, sid)], round(g['lat'], 3), round(g['lon'], 3), signed(a), signed(b)])

json.dump({'sp': SP, 'site': sites, 'f': out,
           'src': 'Timmermann et al. 2022 (CC BY 4.0); Denisovans, H. floresiensis, H. luzonensis, H. naledi added from Wikipedia'},
          open('atlas/hominins.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
from collections import Counter
print(len(out), 'rows,', len(sites), 'sites |', Counter(SP[r[0]][0] for r in out).most_common(), '|', os.path.getsize('atlas/hominins.json'), 'bytes')

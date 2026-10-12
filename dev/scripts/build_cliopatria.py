"""Build atlas/cp/<bucket>.json (states 3400 BCE - 2024 CE) and atlas/hb/peoples.json from Cliopatria.

Source: Cliopatria v0.2.1 (Seshat Global History Databank), CC BY 4.0
  https://github.com/Seshat-Global-History-Databank/cliopatria  (cliopatria.geojson.zip -> dev/raw/clio/)
  Paper: Bennett et al. 2025, Sci. Data, https://doi.org/10.1038/s41597-025-04516-9

atlas/cp/<k>.json: rows active in years [k*100, k*100+99] (k may be negative), each
  {n: name, w: Wikipedia title, f: from year, t: to year, r: rings (flat int lon*10,lat*10), c: label point, a: area deg2}
atlas/cp/index.json: list of bucket numbers that exist.
atlas/hb/peoples.json: {hb snapshot year: [indices of historical-basemaps features to keep]} for snapshots >= -3400 BCE;
  a historical-basemaps feature is kept only where Cliopatria has no state over most of it (stateless peoples).
Gaps of up to 25 years between consecutive rows of one polity are bridged (the earlier border is kept).
Run:  .venv/Scripts/python -I dev/scripts/build_cliopatria.py
"""
import json, os, collections, re
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid
from shapely import STRtree

SRC = 'dev/raw/clio/cliopatria_polities_only_v021.geojson'
os.makedirs('atlas/cp', exist_ok=True)
g = json.load(open(SRC, encoding='utf-8'))
rows = []
for f in g['features']:
    p = f['properties']
    if not f.get('geometry'): continue
    s = make_valid(shape(f['geometry'])).simplify(0.1, preserve_topology=True)
    polys = [s] if isinstance(s, Polygon) else [q for q in getattr(s, 'geoms', []) if isinstance(q, Polygon)]
    polys = [q for q in polys if q.area >= 0.02]
    rings = [[v for xy in q.exterior.coords for v in (round(xy[0] * 10), round(xy[1] * 10))] for q in polys]
    rings = [r for r in rings if len(r) >= 6]
    if not rings: continue
    lp = max(polys, key=lambda q: q.area).representative_point()
    rows.append({'n': p['Name'].strip(), 'w': p.get('Wikipedia') or '', 'f': p['FromYear'], 't': p['ToYear'], 'r': rings,
                 'c': [round(lp.x, 1), round(lp.y, 1)], 'a': round(sum(q.area for q in polys), 1), '_g': unary_union(polys)})
print(len(rows), 'rows')
# bridge short gaps (<= 25 years) between consecutive rows of the same polity, so borders do not blink while scrubbing
GAP = 25; byname = collections.defaultdict(list); bridged = 0
for r in rows: byname[r['n']].append(r)
for lst in byname.values():
    lst.sort(key=lambda r: r['f'])
    for a_, b_ in zip(lst, lst[1:]):
        if 0 < b_['f'] - a_['t'] - 1 <= GAP: a_['t'] = b_['f'] - 1; bridged += 1
print(bridged, 'short gaps bridged')
buckets = collections.defaultdict(list)
for r in rows:
    for k in range(r['f'] // 100, r['t'] // 100 + 1): buckets[k].append(r)
total = 0
for k, lst in buckets.items():
    s = json.dumps([{x: v for x, v in r.items() if x != '_g'} for r in lst], separators=(',', ':'), ensure_ascii=False)
    open(f'atlas/cp/{k}.json', 'w', encoding='utf-8').write(s); total += len(s)
json.dump(sorted(buckets), open('atlas/cp/index.json', 'w'))
print(len(buckets), 'buckets', round(total / 1e6, 1), 'MB')

FORAGER = re.compile(r'hunt|forag|gather|tribes|aboriginal|khoisan|mesolithic|paleo|arctic|nomad|pastoral|herder|fishers', re.I)   # as in the page
STOP = {'kingdom','empire','state','states','dynasty','culture','civilization','period','early','late','city','republic','great'}
# historical-basemaps features to keep alongside Cliopatria (peoples outside states)
years = json.load(open('atlas/hb/years.json'))
keep = {}
for Y in years:
    if Y < -3400: continue
    A = [r for r in rows if r['f'] <= Y <= r['t']]; act = [r['_g'] for r in A]; actn = [r['n'] for r in A]
    tree = STRtree(act)
    hb = json.load(open(f'atlas/hb/{Y}.json', encoding='utf-8'))
    ks = []
    for i, f in enumerate(hb):
        polys = [Polygon([(r[j] / 10, r[j + 1] / 10) for j in range(0, len(r), 2)]).buffer(0) for r in f['r']]
        geo = unary_union(polys)
        if geo.is_empty or geo.area == 0: continue
        near = [j for j in tree.query(geo)] if act else []
        cov = unary_union([act[j] for j in near]) if near else None
        frac = geo.intersection(cov).area / geo.area if cov is not None and not cov.is_empty else 0
        forager = bool(FORAGER.search(f['n']))
        words = {w for w in re.findall(r'[a-z]{4,}', f['n'].lower()) if w not in STOP}
        dup = False
        for j in near:
            inter = geo.intersection(act[j]).area
            if inter <= 0: continue
            if words & set(re.findall(r'[a-z]{4,}', actn[j].lower())): dup = True          # same name
            if not forager and inter >= 0.6 * act[j].area and act[j].area >= 0.1 * geo.area: dup = True   # a state inside it
        if frac < 0.4 and not dup: ks.append(i)
    keep[Y] = ks
    print(Y, f'{len(ks)}/{len(hb)} kept')
json.dump(keep, open('atlas/hb/peoples.json', 'w'), separators=(',', ':'))

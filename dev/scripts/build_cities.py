"""Historical city populations -> atlas/cities.json (world, 3700 BCE - 2000 CE) and atlas/cities_eu.json (Europe 700-2000).

Sources (raw files in dev/raw/cities/, git-ignored):
  Reba, Reitsma & Seto 2016, "Spatializing 6,000 years of global urbanization from 3700 BC to AD 2000",
  Scientific Data 3:160034, doi:10.1038/sdata.2016.34 (article CC BY 4.0). Data on figshare, each CC BY 4.0:
    chandlerV2.csv        doi:10.6084/m9.figshare.2059494  (Chandler 1987, 2250 BC - AD 1975, 1,587 cities)
    modelskiAncientV2.csv doi:10.6084/m9.figshare.2059497  (Modelski 2003, 3700 BC - AD 1000, 154 cities)
    modelskiModernV2.csv  doi:10.6084/m9.figshare.2059500  (Modelski 2003, AD 2000, 293 cities)
  Columns: City, OtherName, Country, Latitude, Longitude, Certainty (geocoding reliability 1 best .. 3 worst),
  then one column per year (BC_2250 .. AD_1975). Files are Windows-1252.
  Buringh 2021, "European urban population, 700 - 2000", DANS, doi:10.17026/DANS-XZY-U62Q (CC0 1.0):
    buringh/buringh.tab (long format; inhabitants in thousands; 'natureofestimate' '' = sound source,
    'proxied', 'imputed'; decimal commas in lat/lon).

Output cities.json: {"src","lic","note","cities":[{"n","o"?,"c","lat","lon","q","r","s":[[year,pop],...]}]}
  q = geocoding certainty 1..3 (Reba et al.; best of the merged rows), r = sources "C" Chandler / "M" Modelski.
  Years signed (BCE negative, no year 0). Where Chandler and Modelski give the same city+year, Modelski is kept for
  years <= 1000 CE (newer compilation for the ancient period), Chandler after.
Output cities_eu.json: same, s = [[year, pop, e]] with e 0 = sourced, 1 = proxied, 2 = imputed; zeros (< 500 people)
  are kept only next to a non-zero value (city appears / disappears).
Run:  .venv/Scripts/python -I dev/scripts/build_cities.py   (from the repo root; set KE_RAW for another raw folder)
"""
import csv, json, math, os, re, sys, unicodedata
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
RAW = os.path.join(os.environ.get('KE_RAW', 'dev/raw'), 'cities')
ATLAS = 'atlas'
issues = []

def read_csv(path):
    raw = open(path, 'rb').read()
    try: txt = raw.decode('utf-8')
    except UnicodeDecodeError: txt = raw.decode('cp1252')
    return list(csv.reader(txt.splitlines()))

def clean(s): return re.sub(r'\s+', ' ', s).strip(' ,')  # \s also matches no-break spaces

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z]', '', s)

def names(*fields):
    out = set()
    for f in fields:
        for p in re.split(r'[,;/()]', f):
            k = norm(p)
            if len(k) > 2: out.add(k)
    return out

def year_of(col):
    m = re.fullmatch(r'(BC|AD)_(\d+)', col.strip())
    y = int(m.group(2))
    assert y > 0, col
    return -y if m.group(1) == 'BC' else y

def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a['lat'], a['lon'], b['lat'], b['lon']))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(min(1, h)))

# ---------------- Reba et al. (Chandler + Modelski) ----------------
SUSPECT = {('C', 'Gelibolu', 1000): 'same figure as Constantinople, likely a digitisation slip',
           ('C', 'Gelibolu', 1200): 'same figure as Constantinople, likely a digitisation slip'}
recs = []
for fn, src in (('chandlerV2.csv', 'C'), ('modelskiAncientV2.csv', 'M'), ('modelskiModernV2.csv', 'M')):
    rows = read_csv(os.path.join(RAW, fn)); h = rows[0]; years = [year_of(c) for c in h[6:]]
    for r in rows[1:]:
        if not r or not r[0].strip(): continue
        try: lat, lon = float(r[3]), float(r[4])
        except ValueError: issues.append(f'{fn}: {r[0]!r} without coordinates dropped'); continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            issues.append(f'{fn}: {r[0]!r} bad coordinates {r[3]},{r[4]} dropped'); continue
        pts = {}
        for y, v in zip(years, r[6:]):
            if (src, r[0].strip(), y) in SUSPECT: issues.append(f'{fn}: {r[0].strip()} {y}: {v} dropped ({SUSPECT[(src, r[0].strip(), y)]})'); continue
            v = v.replace(',', '').strip()
            if not v: continue
            p = int(float(v))
            if p <= 0: issues.append(f'{fn}: {r[0].strip()} {y}: population {v} dropped'); continue
            pts[y] = p
        if not pts: continue
        recs.append(dict(n=clean(r[0]), o=clean(r[1]), c=clean(r[2]), lat=lat, lon=lon,
                         q=int(r[5]) if r[5].strip().isdigit() else 3, r=src, pts=pts, f=fn,
                         keys=names(r[0], r[1])))
n_rows = len(recs)

# union-find: same coordinates at 0.01 deg, or one row's name among the other's name/aliases within 15 km
NOMERGE = {'Shangqi',   # Modelski's ancient 'Shangqi' (certainty 3) is geocoded onto Shanghai, which did not exist then
           'Bobastro'}  # Chandler's Bobastro (fortress ~50 km NW of Malaga) is geocoded onto Malaga
par = list(range(len(recs)))
def find(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i
by_ll = defaultdict(list); by_name = defaultdict(list)
for i, r in enumerate(recs):
    by_ll[(round(r['lat'], 2), round(r['lon'], 2))].append(i)
    for k in r['keys']: by_name[k].append(i)
for g in by_ll.values():
    for i in g[1:]:
        if NOMERGE & {recs[i]['n'], recs[g[0]]['n']}: continue
        par[find(i)] = find(g[0])
for g in by_name.values():  # OtherName often holds a state/province ("Ohio"), so alias-alias matches don't count
    for a in range(len(g)):
        for b in range(a + 1, len(g)):
            ra, rb = recs[g[a]], recs[g[b]]
            if (norm(ra['n']) in rb['keys'] or norm(rb['n']) in ra['keys']) and km(ra, rb) < 15: par[find(g[b])] = find(g[a])
groups = defaultdict(list)
for i in range(len(recs)): groups[find(i)].append(i)

cities, merged = [], []
for g in groups.values():
    rs = [recs[i] for i in g]
    best = min(rs, key=lambda r: (r['q'], -len(r['pts']), r['r'] != 'C'))
    pts = {}
    for y in sorted({y for r in rs for y in r['pts']}):
        cand = [(r['r'], r['pts'][y], r['n']) for r in rs if y in r['pts']]
        pref = 'M' if y <= 1000 else 'C'
        use = [c for c in cand if c[0] == pref] or cand
        vals = sorted({c[1] for c in use})
        other = [c[1] for c in cand if c[0] != pref]
        if other and use[0][0] == pref and max(max(other), max(vals)) > 1.5 * min(min(other), min(vals)):
            issues.append(f'sources differ {best["n"]} {y}: Chandler {[c[1] for c in cand if c[0] == "C"]} vs Modelski {[c[1] for c in cand if c[0] == "M"]} -> kept {pref}')
        if len(vals) > 1: issues.append(f'conflict {best["n"]} {y}: {cand} -> kept max')
        pts[y] = max(vals)
    if len(rs) > 1:
        merged.append(f'{best["n"]} <- ' + ', '.join(f'{r["n"]} ({r["f"][:9]}, {r["lat"]:.2f},{r["lon"]:.2f})' for r in rs))
        spread = max(km(a, b) for a in rs for b in rs)
        if spread > 10: issues.append(f'merged {best["n"]}: coordinates up to {spread:.0f} km apart, kept q{best["q"]} position')
    alias = []
    for r in [best] + rs:
        for p in [r['n']] + [x.strip() for x in re.split(r'[,;]', r['o'])]:
            if p and p != best['n'] and p not in alias: alias.append(p)
    c = dict(n=best['n'])
    if alias: c['o'] = ', '.join(alias)
    c.update(c=best['c'], lat=round(best['lat'], 2), lon=round(best['lon'], 2), q=min(r['q'] for r in rs),
             r=''.join(sorted({r['r'] for r in rs})), s=[[y, p] for y, p in pts.items()])
    cities.append(c)
cities.sort(key=lambda c: (-max(p for _, p in c['s']), c['n']))
out = dict(src='Reba, Reitsma & Seto 2016, Sci. Data 3:160034 (doi:10.1038/sdata.2016.34), digitised from '
               'Chandler 1987 "Four Thousand Years of Urban Growth" and Modelski 2003 "World Cities: -3000 to 2000"; '
               'figshare doi:10.6084/m9.figshare.2059494, .2059497, .2059500 (V2 files)',
           lic='CC BY 4.0', note='Rough historical estimates (Chandler: largest cities only, sparse years); q = geocoding '
               'certainty 1 best..3 worst; r = C Chandler / M Modelski', cities=cities)
os.makedirs(ATLAS, exist_ok=True)
with open(os.path.join(ATLAS, 'cities.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

# ---------------- report ----------------
def report(cities, label, years_top):
    pts = [(y, p) for c in cities for y, p, *_ in c['s']]
    yc = Counter(y for y, _ in pts)
    print(f'== {label}: {len(cities)} cities, {len(pts)} data points, years {min(yc)}..{max(yc)}, '
          f'{len(yc)} distinct years')
    print('   years with most data:', ', '.join(f'{y}:{n}' for y, n in yc.most_common(12)))
    for Y in years_top:
        top = sorted(((p, c['n'], c['c']) for c in cities for y, p, *_ in c['s'] if y == Y), reverse=True)[:10]
        print(f'   top {Y} ({sum(1 for c in cities for y, *_ in c["s"] if y == Y)} cities):',
              '; '.join(f'{n} ({cc}) {p:,}' for p, n, cc in top))

print(f'Reba et al.: {n_rows} rows with data -> {len(cities)} cities ({len(merged)} merged groups)')
report(cities, 'cities.json', (-2000, 1, 1000, 1500, 1800))
print('   certainty:', Counter(c['q'] for c in cities), ' sources:', Counter(c['r'] for c in cities))

# ---------------- Buringh (Europe 700-2000) ----------------
bpath = os.path.join(RAW, 'buringh', 'buringh.tab')
if os.path.exists(bpath):
    rows = list(csv.reader(open(bpath, encoding='utf-8'), delimiter='\t'))[1:]
    E = {'': 0, 'proxied': 1, 'imputed': 2}
    bc = {}
    # ~25 rows lost their decimal point in Excel ('524029998779297' = 52.4029998779297, '-1467' = -1.467):
    # put the point after 1 or 2 digits, whichever lands nearest the median of the country's valid cities
    ok = lambda la, lo: 25 <= la <= 75 and -30 <= lo <= 70
    num = lambda v: float(v.replace(',', '.'))
    good = defaultdict(list)
    for r in rows:
        try:
            if ok(num(r[5]), num(r[6])): good[r[3]].append((num(r[5]), num(r[6])))
        except ValueError: pass
    med = {k: (sorted(a for a, _ in v)[len(v) // 2], sorted(b for _, b in v)[len(v) // 2]) for k, v in good.items()}
    def opts(v, lo, hi):
        if ',' in v or '.' in v: return [num(v)]
        sg, d = (-1, v[1:]) if v.startswith('-') else (1, v)
        return [x for x in (sg * float(d[:k] + '.' + d[k:]) for k in (1, 2)) if lo <= x <= hi] or [num(v)]
    fixed = {}
    for r in rows:
        name, la, lo, cty = r[0], r[5], r[6], r[3]
        try:
            if ok(num(la), num(lo)): continue
        except ValueError: pass
        if (name, la, lo) in fixed: continue
        m = med.get(cty, (50, 10))
        cand = [(km(dict(lat=a, lon=b), dict(lat=m[0], lon=m[1])), a, b) for a in opts(la, 25, 75) for b in opts(lo, -30, 70)]
        d, a, b = min(cand)
        fixed[(name, la, lo)] = (a, b) if d < 3000 and ok(a, b) else None
        issues.append(f'buringh: {name} ({cty}) coordinates {la} / {lo} -> ' + (f'{a:.4f}, {b:.4f} ({d:.0f} km from country median)' if fixed[(name, la, lo)] else 'not repairable, dropped'))
    for r in rows:
        name, syn, _, country, _, la, lo, _, yr, pop, _, nat = r
        if (name, la, lo) in fixed:
            if not fixed[(name, la, lo)]: continue
            lat, lon = fixed[(name, la, lo)]
        else:
            try: lat, lon = num(la), num(lo)
            except ValueError: issues.append(f'buringh: {name} bad coordinates dropped'); continue
        if pop == '': continue
        k = (name, round(lat, 2), round(lon, 2))
        c = bc.setdefault(k, dict(n=clean(name), o=clean(syn), c=clean(country), lat=round(lat, 2), lon=round(lon, 2), s=[]))
        c['s'].append([int(float(yr)), int(round(float(pop) * 1000)), E.get(nat, 2)])
    eu = []
    for c in bc.values():
        s = sorted(c['s'])
        keep = [p for i, p in enumerate(s) if p[1] > 0 or (i > 0 and s[i - 1][1] > 0) or (i + 1 < len(s) and s[i + 1][1] > 0)]
        if not any(p[1] > 0 for p in keep): continue
        c['s'] = keep
        if not c['o']: del c['o']
        eu.append(c)
    eu.sort(key=lambda c: (-max(p[1] for p in c['s']), c['n']))
    with open(os.path.join(ATLAS, 'cities_eu.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(src='Buringh 2021, "European urban population, 700 - 2000", DANS, doi:10.17026/DANS-XZY-U62Q',
                       lic='CC0 1.0', note='Inhabitants rounded to thousands; e: 0 sourced, 1 proxied, 2 imputed; '
                       '0 = under 500 people', cities=eu), f, ensure_ascii=False, separators=(',', ':'))
    report(eu, 'cities_eu.json', (800, 1000, 1500, 1800))
    print('   estimate kinds:', Counter(p[2] for c in eu for p in c['s']))

print('\n-- merged groups --'); print('\n'.join(merged))
print('\n-- issues --'); print('\n'.join(issues))
for fn in ('cities.json', 'cities_eu.json'):
    p = os.path.join(ATLAS, fn)
    if os.path.exists(p): print(fn, os.path.getsize(p), 'bytes')

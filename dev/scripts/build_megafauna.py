"""Dated finds of Ice Age megafauna, 505 ka -> extinction, for the 'Ice Age animals' map layer.

Sources (bulk JSON, no key):
  Neotoma Paleoecology Database (incl. FAUNMAP), CC BY 4.0  https://api.neotomadb.org/v2.0/data/occurrences
  Paleobiology Database (PBDB), CC BY 4.0                    https://paleobiodb.org/data1.2/occs/list.json
  FosSahul 2.0 (Peters et al. 2019, Sci Data; CC0): Sahul megafauna dates, quality A*/A/B only
    https://github.com/GlobalEcologyFlinders/FosSahul -> dev/raw/megafauna/fossahul2.csv
  Stuart & Lister 2012 (Quat Sci Rev 51:1-17) woolly rhino radiocarbon dates, supplement mmc1.xlsx
    -> dev/raw/megafauna/stuart2012_rhino_mmc1.xlsx
  Lister & Stuart 2019 (Quat Int 500:185-203) giant deer radiocarbon dates passing audit (Table S1)
    -> dev/raw/megafauna/lister2019_deer_mmc1.xlsx
  dev/data/megafauna_dated.json: hand-compiled dated localities for thinly covered species (each row cited)
Raw API responses are cached in dev/raw/megafauna/ (set KE_RAW to reuse them from another checkout).
Output atlas/megafauna.json:
  sp:   [[key, common name, scientific name, Wikipedia title, last signed year], ...]
  site: [[name, source], ...]
  f:    [[species id, site id, lat, lon, from, to, coarse], ...]  signed years; coarse=1 when dated only to a
        long interval (> 60,000 years, e.g. 'Late Pleistocene'), drawn fainter
Run:  .venv/Scripts/python -I dev/scripts/build_megafauna.py
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import xlsx_min

RAW = Path(os.environ.get('KE_RAW', 'dev/raw')) / 'megafauna'; RAW.mkdir(parents=True, exist_ok=True)
UA = 'KarahanEra/0.1 (https://github.com/kmdan/historytimeline)'
SP = [  # key, name, scientific, Wikipedia, Neotoma taxon names, PBDB base names
    ['mam', 'Woolly mammoth', 'Mammuthus primigenius', 'Woolly mammoth', ['Mammuthus primigenius'], ['Mammuthus primigenius']],
    ['col', 'Columbian mammoth', 'Mammuthus columbi', 'Columbian mammoth', ['Mammuthus columbi'], ['Mammuthus columbi']],
    ['mas', 'American mastodon', 'Mammut americanum', 'American mastodon', ['Mammut americanum'], ['Mammut americanum']],
    ['rhi', 'Woolly rhinoceros', 'Coelodonta antiquitatis', 'Woolly rhinoceros', [], ['Coelodonta antiquitatis']],
    ['bea', 'Cave bear', 'Ursus spelaeus', 'Cave bear', ['Ursus spelaeus'], ['Ursus spelaeus']],
    ['lio', 'Cave lion', 'Panthera spelaea', 'Cave lion', ['Panthera spelaea', 'Panthera leo spelaea'], ['Panthera spelaea']],
    ['ele', 'Straight-tusked elephant', 'Palaeoloxodon antiquus', 'Straight-tusked elephant', [], ['Palaeoloxodon antiquus']],
    ['dee', 'Giant deer', 'Megaloceros giganteus', 'Irish elk', ['Megaloceros giganteus'], ['Megaloceros giganteus']],
    ['smi', 'Sabre-toothed cat', 'Smilodon', 'Smilodon', ['Smilodon fatalis', 'Smilodon populator', 'Smilodon'], ['Smilodon']],
    ['slo', 'Giant ground sloths', 'Megatherium, Megalonyx, Eremotherium …', 'Ground sloth',
     ['Megalonyx jeffersonii', 'Megalonyx', 'Eremotherium', 'Megatherium', 'Paramylodon harlani', 'Nothrotheriops shastensis'],
     ['Megatherium', 'Megalonyx', 'Eremotherium', 'Paramylodon', 'Nothrotheriops', 'Glossotherium', 'Lestodon']],
    ['dip', 'Diprotodon', 'Diprotodon optatum', 'Diprotodon', [], ['Diprotodon']],
    ['arc', 'Short-faced bear', 'Arctodus simus', 'Arctodus', ['Arctodus simus', 'Arctodus'], ['Arctodus']],
    ['thy', 'Marsupial lion', 'Thylacoleo carnifex', 'Thylacoleo', [], ['Thylacoleo carnifex']],
    ['gen', 'Genyornis', 'Genyornis newtoni', 'Genyornis', [], ['Genyornis']]]
KEY = {s[0]: i for i, s in enumerate(SP)}
MAXAGE = 505000
# youngest accepted age per species (years BP): last records per Wikipedia; database records younger than this are
# loose upper bounds ('Late Pleistocene–Holocene'), so ranges are clipped to it
LAST = {'mam': 4000, 'col': 11000, 'mas': 10500, 'rhi': 14000, 'bea': 24000, 'lio': 14000, 'ele': 42000, 'dee': 7700,
        'smi': 10000, 'slo': 4400, 'dip': 40000, 'arc': 11500, 'thy': 40000, 'gen': 40000}

def get(url, cache):
    p = RAW / cache
    if p.exists(): return json.loads(p.read_text(encoding='utf-8'))
    for wait in (0, 5, 20, 60):
        time.sleep(wait)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=120) as r:
                d = json.loads(r.read().decode('utf-8'))
            p.write_text(json.dumps(d), encoding='utf-8'); return d
        except Exception as e:
            print('retry', cache, e)
    raise RuntimeError(url)

# island survivors outlived the mainland: mammoths on Wrangel and St Paul, ground sloths on Cuba and Hispaniola
def last_at(key, lat, lon):
    try: lat, lon = float(lat), float(lon)
    except (TypeError, ValueError): return LAST[key]
    if key == 'mam' and not ((70 < lat < 72.5 and (lon > 175 or lon < -175)) or (56.5 < lat < 57.5 and -171 < lon < -169)): return 10500
    if key == 'slo' and not (17 < lat < 24 and -86 < lon < -68): return 10500
    return LAST[key]
signed = lambda bp: int(1950 - bp)
groups = {}
def add(sid, site, src, lat, lon, old, young, coarse):
    if old is None or young is None or lat is None or lon is None: return
    old, young = min(float(old), MAXAGE), max(float(young), last_at(SP[sid][0], lat, lon))
    if young > MAXAGE or old < young: return
    g = groups.setdefault((site, sid, round(float(lat), 1), round(float(lon), 1)), {'lat': float(lat), 'lon': float(lon), 'iv': [], 'src': src, 'coarse': coarse})
    g['iv'].append((old, young)); g['coarse'] = g['coarse'] and coarse

# Neotoma: resolve taxon ids, then occurrences with ages (years BP)
for sid, s in enumerate(SP):
    for name in s[4]:
        tx = get('https://api.neotomadb.org/v2.0/data/taxa?' + urllib.parse.urlencode({'taxonname': name}), f'neo_taxa_{name}.json')
        for t in tx.get('data', []):
            if t.get('taxonname') != name: continue
            occ = get(f"https://api.neotomadb.org/v2.0/data/occurrences?taxonid={t['taxonid']}&ageold={MAXAGE}&ageyoung=0&limit=10000", f"neo_occ_{t['taxonid']}.json")
            for o in occ.get('data', []):
                a, si = o.get('age') or {}, o.get('site') or {}
                old = a.get('ageolder') if a.get('ageolder') is not None else (a.get('age') + 1000 if a.get('age') is not None else None)
                young = a.get('ageyounger') if a.get('ageyounger') is not None else (a.get('age') - 1000 if a.get('age') is not None else None)
                try: lon, lat = json.loads(si.get('location') or '{}').get('coordinates', [None, None])[:2]
                except (ValueError, TypeError): continue
                if isinstance(lon, list): continue          # polygons: skip
                add(sid, si.get('sitename') or '?', 'Neotoma' + (' / ' + si['database'] if si.get('database') else ''),
                    lat, lon, old, young, (old or 0) - (young or 0) > 60000 if old is not None and young is not None else True)

# PBDB: occurrences overlapping 0.505 Ma - present, ages in Ma
for sid, s in enumerate(SP):
    for name in s[5]:
        d = get('https://paleobiodb.org/data1.2/occs/list.json?' + urllib.parse.urlencode(
            {'base_name': name, 'max_ma': MAXAGE / 1e6, 'min_ma': 0, 'timerule': 'overlap', 'show': 'coords,loc'}), f'pbdb_{name}.json')
        for r in d.get('records', []):
            try: lat, lon = float(r['lat']), float(r['lng'])
            except (KeyError, ValueError): continue
            old, young = float(r['eag']) * 1e6, float(r['lag']) * 1e6
            site = r.get('nam') or f"PBDB collection {str(r.get('cid', '')).replace('col:', '')}"
            add(sid, site, 'Paleobiology Database', lat, lon, old, young, old - young > 60000)

# FosSahul 2.0: ages in ka with 1-sigma precision; keep reliable ('A*', 'A', 'B') finite ages, +-2 sigma. Uncalibrated
# radiocarbon ages are widened on the old side (calibrated ages run up to ~5 kyr older), an approximation
FOSG = {'Diprotodon': 'dip', 'Thylacoleo': 'thy', 'Genyornis': 'gen'}
fs = RAW / 'fossahul2.csv'
if fs.exists():
    for r in csv.DictReader(open(fs, encoding='utf-8', errors='replace')):
        if r['Genus'] not in FOSG or r['Quality'] not in ('A*', 'A', 'B') or r['AgeType'] != '=': continue
        try: age, sd = float(r['Age']) * 1000, float(r['Precision']) * 1000
        except ValueError: continue
        old, young = age + 2 * sd, age - 2 * sd
        if 'radiocarbon' in r['DatingTechnique'].lower() and r['Calibration'] != 'Calibrated': old += min(5000, 0.12 * age)
        site = ' '.join((r['Cave.Site.Deposit'] or r['SpecificRegion'] or '?').split())
        add(KEY[FOSG[r['Genus']]], site, 'FosSahul 2.0', r['Latitude'], r['Longitude'], old, young, old - young > 60000)

# radiocarbon date lists from published audits: calibrated range (cal BP) when given, else 14C +- 2 sigma; '>' dates skipped
def c14list(path, sheet, sp, src, col):
    if not path.exists(): return
    hdr = None
    for row in xlsx_min.rows(path, sheet):
        if not hdr:
            if col['lat'] in row: hdr = {k: row.index(v) for k, v in col.items()}
            continue
        g = lambda k: row[hdr[k]] if hdr[k] < len(row) else ''
        c14, sd, a, b = g('c14'), g('sd'), g('from'), g('to')
        if not isinstance(c14, float): continue
        if isinstance(a, float) and isinstance(b, float): old, young = max(a, b), min(a, b)
        elif isinstance(sd, float): old, young = c14 + 2 * sd, c14 - 2 * sd
        else: continue
        if isinstance(g('lat'), float) and isinstance(g('lon'), float):
            add(KEY[sp], ' '.join(str(g('site')).split()), src, g('lat'), g('lon'), old, young, False)
c14list(RAW / 'stuart2012_rhino_mmc1.xlsx', 'datelist', 'rhi', 'Stuart & Lister 2012',
        {'site': 'site', 'lat': 'LatDD', 'lon': 'LongDD', 'c14': '14C', 'sd': 'sd', 'from': 'calibrated from', 'to': 'calibrated to'})
c14list(RAW / 'lister2019_deer_mmc1.xlsx', 'Table S1', 'dee', 'Lister & Stuart 2019',
        {'site': 'locality', 'lat': 'LatDD', 'lon': 'LongDD', 'c14': '14C date', 'sd': 'sigma', 'from': 'calfrom', 'to': 'calto'})

# hand-compiled dated localities (cited per row)
hand = Path('dev/data/megafauna_dated.json')
if hand.exists():
    for r in json.loads(hand.read_text(encoding='utf-8')):
        if r['sp'] in KEY: add(KEY[r['sp']], r['site'], r['src'], r['lat'], r['lon'], r['old'], r['young'], False)

sites, sidx, out = [], {}, []
for (site, sid, _, _), g in sorted(groups.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    if (site, sid) not in sidx: sidx[(site, sid)] = len(sites); sites.append([site, g['src']])
    iv = sorted(g['iv'], key=lambda t: -t[0]); merged = [list(iv[0])]
    for a, b in iv[1:]:
        if a >= merged[-1][1] - 2000: merged[-1][1] = min(merged[-1][1], b)
        else: merged.append([a, b])
    for a, b in merged:
        out.append([sid, sidx[(site, sid)], round(g['lat'], 2), round(g['lon'], 2), signed(a), signed(b), 1 if g['coarse'] else 0])

# sp rows: [key, name, scientific, Wikipedia, last signed year]
json.dump({'sp': [s[:4] + [signed(LAST[s[0]])] for s in SP], 'site': sites, 'f': out,
           'src': 'Neotoma Paleoecology Database (CC BY 4.0); Paleobiology Database (CC BY 4.0); FosSahul 2.0 (CC0); Stuart & Lister 2012; Lister & Stuart 2019; dev/data/megafauna_dated.json (cited per record)'},
          open('atlas/megafauna.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
from collections import Counter
c = Counter((SP[r[0]][0], r[6]) for r in out)
print(len(out), 'rows', len(sites), 'sites |', {k: (c[(k, 0)], c[(k, 1)]) for k in KEY}, '| (precise, coarse) |', os.path.getsize('atlas/megafauna.json'), 'bytes')

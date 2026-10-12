"""Very large eruptions as timeline events: <script id="bigeruptions"> in karahan-era.html.

Sources:
  Smithsonian Global Volcanism Program, Volcanoes of the World (VOTW) v5, Holocene eruptions with VEI >= 6
    WFS https://webservices.volcano.si.edu/geoserver/GVP-VOTW/ows (non-commercial use with citation:
    Global Volcanism Program, 2024. Volcanoes of the World, v. 5.2. Smithsonian Institution)
    cached in dev/raw/gvp/vei6.json and dev/raw/gvp/volcanoes.json
  dev/data/super_eruptions.json: Pleistocene eruptions of VEI 7-8 (500-12 ka), each row cited
Eruptions the page already shows (same volcano within 60 years) are skipped.
Run:  .venv/Scripts/python -I dev/scripts/build_bigeruptions.py
"""
import json, os, re, urllib.parse, urllib.request
from pathlib import Path

RAW = Path(os.environ.get('KE_RAW', 'dev/raw')) / 'gvp'; RAW.mkdir(parents=True, exist_ok=True)
PAGE = Path('karahan-era.html')
WFS = 'https://webservices.volcano.si.edu/geoserver/GVP-VOTW/ows?service=WFS&version=2.0.0&request=GetFeature&outputFormat=json&typeName='
UA = {'User-Agent': 'KarahanEra/0.1 (https://github.com/kmdan/historytimeline)'}

def cached(name, url):
    p = RAW / name
    if not p.exists():
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r: p.write_bytes(r.read())
    return json.loads(p.read_text(encoding='utf-8'))

er = cached('vei6.json', WFS + 'GVP-VOTW:Smithsonian_VOTW_Holocene_Eruptions&CQL_FILTER=ExplosivityIndexMax%3E%3D6')['features']
vo = {f['properties']['Volcano_Number']: f['properties'] for f in cached('volcanoes.json', WFS + 'GVP-VOTW:Smithsonian_VOTW_Holocene_Volcanoes')['features']}

# Wikipedia titles for volcano names that differ from GVP spelling, and names the page already uses for them
WIKI = {'Rinjani': '1257 Samalas eruption', 'Santorini': 'Minoan eruption', 'Krakatau': '1883 eruption of Krakatoa',
        'Crater Lake': 'Mount Mazama', 'Taupo': 'Taupō Volcano', 'Changbaishan': 'Paektu Mountain', 'Tambora': '1815 eruption of Mount Tambora',
        'Kikai': 'Kikai Caldera', 'Kurile Lake': 'Kurile Lake', 'Aira': 'Aira Caldera', 'Pinatubo': 'Mount Pinatubo',
        'St. Helens': 'Mount St. Helens', 'Hudson, Cerro': 'Cerro Hudson', 'Blanco, Cerro': 'Cerro Blanco (volcano)',
        'Novarupta': 'Novarupta', 'Huaynaputina': 'Huaynaputina', 'Ilopango': 'Ilopango', 'Okmok': 'Mount Okmok',
        'Santa Maria': 'Santa María (volcano)', 'Grimsvotn': 'Grímsvötn', 'Bardarbunga': 'Bárðarbunga', 'Taal': 'Taal Volcano',
        'Masaya': 'Masaya Volcano', 'Rabaul': 'Rabaul caldera', 'Ulleungdo': 'Ulleungdo', 'Aniakchak': 'Aniakchak National Monument and Preserve',
        'Churchill': 'Mount Churchill', 'Ceboruco': 'Ceboruco', 'Quilotoa': 'Quilotoa', 'Ksudach': 'Ksudach', 'Karymsky': 'Karymsky',
        'Mashu': 'Lake Mashū', 'Menengai': 'Menengai', 'Veniaminof': 'Mount Veniaminof', 'Black Peak': 'Black Peak (Alaska)',
        'Macauley': 'Macauley Island', 'Raoul Island': 'Raoul Island', 'Apoyeque': 'Apoyeque', 'Ambrym': 'Ambrym',
        'Dakataua': 'Dakataua', 'Witori': 'Pago (Papua New Guinea)', 'Long Island': 'Long Island (Papua New Guinea)', 'Billy Mitchell': 'Billy Mitchell (volcano)',
        'Michinmahuida': 'Michinmahuida', 'Fisher': 'Fisher Caldera', 'Khangar': 'Khangar', 'Tao-Rusyr Caldera': 'Tao-Rusyr Caldera',
        'Moekeshiwan': 'Lvinaya Past'}
SAME = {'Rinjani': 'samalas', 'Santorini': 'thera', 'Krakatau': 'krakatoa', 'Crater Lake': 'mazama', 'Changbaishan': 'paektu',
        'Taupo': 'taup', 'Tambora': 'tambora', 'Huaynaputina': 'huaynaputina', 'Ilopango': 'ilopango', 'Okmok': 'okmok',
        'Pinatubo': 'pinatubo', 'Novarupta': 'novarupta', 'St. Helens': 'st. helens'}
LANE = lambda lat, lon: 5                 # all eruptions in the Earth & Oceans lane, like the eVolv2k ones

html = PAGE.read_text(encoding='utf-8')
have = []   # (lowercase title, year) of events already on the page
for m in re.finditer(r"\bE\((-?\d+),\d,\d,'((?:[^'\\]|\\.)*)'", html): have.append((m.group(2).lower(), int(m.group(1))))
for tag in ('research', 'deepresearch', 'eruptions'):
    mm = re.search(r'<script id="%s" type="application/json">(.*?)</script>' % tag, html, re.S)
    if not mm: continue
    d = json.loads(mm.group(1))
    for x in (d if tag == 'eruptions' else [e for r in d for e in r.get('more', [])]): have.append((x['t'].lower(), x['y']))
def known(name, y, tol=60):
    key = SAME.get(name, name.lower())
    return any(key in t and abs(ty - y) <= tol for t, ty in have)

out, skipped = [], []
for f in er:
    p = f['properties']; y = p['StartDateYear']; name = p['Volcano_Name']; vei = p['ExplosivityIndexMax']
    if y is None: continue
    y = int(y) if y != 0 else 1
    if known(name, y): skipped.append(f'{name} {y}'); continue
    lon, lat = f['geometry']['coordinates']; v = vo.get(p['Volcano_Number'], {})
    country = v.get('Country') or ''
    unit = f" ({p['ActivityUnit']})" if p.get('ActivityUnit') else ''
    nice = name.replace('Hudson, Cerro', 'Cerro Hudson').replace('Blanco, Cerro', 'Cerro Blanco')
    out.append({'y': y, 'l': LANE(lat, lon), 'i': 1 if vei >= 7 else 2, 't': f'{nice} erupts (VEI {vei})',
                'd': f"A very large explosive eruption of {nice}{', ' + country if country else ''}{unit}, size {vei} on the 0–8 Volcanic Explosivity Index"
                     f"{' (dated ±' + str(p['StartDateYearUncertainty']) + ' years)' if p.get('StartDateYearUncertainty') else ''}. Source: Smithsonian Global Volcanism Program.",
                'w': WIKI.get(name, name), 'lat': round(lat, 2), 'lon': round(lon, 2)})
sup = Path('dev/data/super_eruptions.json')
if sup.exists():
    for r in json.loads(sup.read_text(encoding='utf-8')):
        y = int(1950 - r['age_bp'])
        words = {w.strip('(),').lower() for w in (r['name'].split()[:2] + r['volcano'].split()[:1])} - {'youngest', 'eruption', 'the', 'mount'}
        if any(known(w, y, 3000) for w in words if len(w) > 3): skipped.append(r['name']); continue   # Ice Age dates: looser match
        out.append({'y': y, 'l': LANE(r['lat'], r['lon']), 'i': 1 if (r.get('vei') or 0) >= 8 else 2, 't': r['name'],
                    'd': r['d'], 'w': r['w'], 'lat': r['lat'], 'lon': r['lon']})
out.sort(key=lambda e: e['y'])
tag = '<script id="bigeruptions" type="application/json">'
blob = tag + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '</script>'
html = re.sub(re.escape(tag) + r'.*?</script>', lambda m: blob, html, count=1, flags=re.S) if tag in html else html.replace('<script id="eruptions"', blob + '\n<script id="eruptions"', 1)
PAGE.write_text(html, encoding='utf-8', newline='')
print(len(out), 'eruptions;', 'skipped (already on the page):', skipped)

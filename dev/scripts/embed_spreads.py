"""Embed dated-spread data into karahan-era.html: the page interpolates an arrival-time surface from dated places and
draws an advancing front (SPREADS in the page).

Run:  .venv/Scripts/python -I dev/scripts/embed_spreads.py
- dev/data/plague_arrivals.json  -> <script id="plague">      Black Death first arrivals 1346-53 (layer #lyPlague)
- dev/data/farming_arrivals.json -> <script id="farmspread">  earliest farming, Fertile Crescent -> Europe/N. Africa/S. Asia
                                                              (tour overlay, "fx": {"spread": "farming"})
Place = {"n", "lat", "lon", "t": decimal/signed year, "when": text, "approx": bool, "w": Wikipedia title, "src"}
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JOBS = [('plague_arrivals.json', 'places', 'plague', (1330, 1360)), ('farming_arrivals.json', 'spread', 'farmspread', (-11000, -1000))]
page = ROOT / 'karahan-era.html'
html = page.read_bytes().decode('utf-8')
for fn, key, sid, (t0, t1) in JOBS:
    f = ROOT / 'dev/data' / fn
    if not f.exists(): print('skip', fn); continue
    places = []
    for q in sorted(json.loads(f.read_text(encoding='utf-8'))[key], key=lambda q: q['t']):
        assert t0 <= q['t'] <= t1 and -90 <= q['lat'] <= 90 and -180 <= q['lon'] <= 180, q
        places.append({k: q[k] for k in ('n', 'lat', 'lon', 't', 'when', 'approx', 'w') if k in q})
    blob = json.dumps({'places': places}, ensure_ascii=False, separators=(',', ':')).replace('</', r'<\/')
    html, n = re.subn(rf'(<script id="{sid}" type="application/json">).*?(</script>)', lambda m: m.group(1) + blob + m.group(2), html, flags=re.S)
    assert n == 1, sid
    print(f'{len(places)} places -> #{sid}')
page.write_bytes(html.encode('utf-8'))

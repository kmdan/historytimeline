"""Embed Black Death first-arrival dates (dev/data/plague_arrivals.json) into <script id="plague"> of karahan-era.html.

Run:  .venv/Scripts/python -I dev/scripts/embed_plague.py
Place = {"n", "lat", "lon", "t": decimal year (month m -> year + (m-0.5)/12), "when": text, "approx": bool, "w": Wikipedia title, "src"}
The page interpolates an arrival-time surface from these towns and draws the advancing front (layer #lyPlague).
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
src = json.loads((ROOT / 'dev/data/plague_arrivals.json').read_text(encoding='utf-8'))
places = []
for q in sorted(src['places'], key=lambda q: q['t']):
    assert 1330 <= q['t'] <= 1360 and -90 <= q['lat'] <= 90 and -180 <= q['lon'] <= 180, q
    places.append({k: q[k] for k in ('n', 'lat', 'lon', 't', 'when', 'approx', 'w') if k in q})
blob = json.dumps({'places': places}, ensure_ascii=False, separators=(',', ':')).replace('</', r'<\/')
page = ROOT / 'karahan-era.html'
html = page.read_bytes().decode('utf-8')
new, n = re.subn(r'(<script id="plague" type="application/json">).*?(</script>)', lambda m: m.group(1) + blob + m.group(2), html, flags=re.S)
assert n == 1
page.write_bytes(new.encode('utf-8'))
print(f'{len(places)} places -> {page.name}')

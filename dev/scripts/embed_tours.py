"""Embed the guided tours (dev/data/tours.json) into <script id="tours"> of karahan-era.html.

Run:  .venv/Scripts/python -I dev/scripts/embed_tours.py [tours.json] [page.html]
Tour  = {"id", "title", "blurb", "ly": {"lyPop": true, ...} layers for the whole tour (restored afterwards), "fx": {"walk": true, "hyp": true, "spread": "farming"} story overlays (walkers on active migrations, incl. hypothetical routes; a dated-spread front), "steps": [step, ...]}
Step  = {"y": signed civil year (BCE negative, no year 0), "lat", "lon", "z": map zoom (1 = whole world),
         "t": title, "c": caption, "w": Wikipedia title (optional), "src": source URL (kept here, not embedded),
         "span": timeline width in years (optional), "dur": seconds of travel to this step at 1x (optional, default 4.5), "ly": {"lyIce": true, ...} layer switches (optional)}
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'dev/data/tours.json'
page = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'karahan-era.html'
KEEP = ('y', 'lat', 'lon', 'z', 't', 'c', 'w', 'span', 'dur', 'ly', 'fx', 'look', 'img')

tours = json.loads(src.read_text(encoding='utf-8'))
out = []
for t in tours:
    assert re.fullmatch(r'[a-z0-9-]+', t['id']), t['id']
    steps = []
    for s in t['steps']:
        assert (isinstance(s['y'], int) or s['y'] > 0) and s['y'] != 0 and -500000 <= s['y'] <= 2030, (t['id'], s)   # CE steps may be fractional (months)
        assert -90 <= s['lat'] <= 90 and -180 <= s['lon'] <= 180, (t['id'], s)
        assert s['t'] and s['c'], (t['id'], s)
        steps.append({k: s[k] for k in KEEP if k in s})
    out.append({'id': t['id'], 'title': t['title'], 'blurb': t.get('blurb', ''), 'ly': t.get('ly', {}), **({'fx': t['fx']} if t.get('fx') else {}), 'steps': steps})

blob = json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = page.read_bytes().decode('utf-8')   # keep line endings byte-exact
new, n = re.subn(r'(<script id="tours" type="application/json">).*?(</script>)', lambda m: m.group(1) + blob + m.group(2), html, flags=re.S)
assert n == 1
page.write_bytes(new.encode('utf-8'))
print(f'{len(out)} tours, {sum(len(t["steps"]) for t in out)} steps -> {page.name}')

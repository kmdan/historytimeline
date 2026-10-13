"""Climate events and open scientific questions (dev/data/climate_events.json, Wikipedia-checked 2026-10-13; the 'check'
field quotes the sentence each date rests on) -> the 'more' lists of the era research panels in karahan-era.html
(<script id="research"> for 40,000 BCE onwards, <script id="deepresearch"> before) and dev/data/deep_research.json.
Each event goes to the era whose span holds its year; q: true marks an open scientific question. Idempotent (by title).
Run:  .venv/Scripts/python -I dev/scripts/add_climate_events.py
"""
import json, re
from pathlib import Path

PAGE, DEEP, SRC = Path('karahan-era.html'), Path('dev/data/deep_research.json'), Path('dev/data/climate_events.json')
html = PAGE.read_text(encoding='utf-8')
block = lambda tag: re.search(r'(<script id="%s" type="application/json">)(.*?)(</script>)' % tag, html, re.S)
deep_eras = json.loads(block('deeperas').group(2))                                 # [{a, b, ...}] five deep eras, in order
i = html.index('const ERAS = ['); j = html.index('].map((e,i)=>', i)
eras = [(int(a), int(b)) for a, b in re.findall(r'\{a:(-?\d+),b:(-?\d+)', html[i:j])]   # research era k = eras[k-1]

def era_of(y):
    for k, e in enumerate(deep_eras):
        if e['a'] <= y < e['b']: return 'deepresearch', 'deep%d' % (k + 1)
    for k, (a, b) in enumerate(eras):
        if a <= y < b or (y == b == 2026): return 'research', k + 1
    raise ValueError(y)

events = json.loads(SRC.read_text(encoding='utf-8'))
data = {tag: json.loads(block(tag).group(2)) for tag in ('research', 'deepresearch')}
for e in events:
    tag, era = era_of(e['y'])
    r = next(r for r in data[tag] if r['era'] == era)
    item = {k: e[k] for k in ('y', 'l', 'i', 't', 'd', 'w', 'lat', 'lon')}
    if e.get('q'): item['q'] = True
    r['more'] = sorted([x for x in r['more'] if x['t'] != e['t']] + [item], key=lambda x: x['y'])
for tag in ('research', 'deepresearch'):
    m = block(tag)
    html = html[:m.start()] + m.group(1) + json.dumps(data[tag], ensure_ascii=False, separators=(',', ':')) + m.group(3) + html[m.end():]
PAGE.write_text(html, encoding='utf-8', newline='')
DEEP.write_text(json.dumps(data['deepresearch'], ensure_ascii=False, indent=0), encoding='utf-8', newline='\n')
print(len(events), 'events placed')

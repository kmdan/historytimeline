"""One-off (2026-10-13): three finds asked about on popular archaeology forums, checked against Wikipedia.
Adds them to the 'more' lists of the research panels (deep_research.json + page blocks). Idempotent.
Run:  .venv/Scripts/python -I dev/scripts/add_sci_sites.py
"""
import json, re
from pathlib import Path

PAGE = Path('karahan-era.html'); DEEP = Path('dev/data/deep_research.json')
ADD = {
    ('deepresearch', 'deep3'): {'y': -128050, 'l': 0, 'i': 2, 't': 'Nesher Ramla people',
        'd': 'Pieces of a skull and a jaw from a sinkhole near Ramla, Israel, 140,000–120,000 years ago, with over 6,000 stone tools. '
             'The finders (Hershkovitz 2021) see a late archaic group that mixed with Neanderthals; others classify the bones as early Neanderthals (debated).',
        'w': 'Nesher Ramla Homo', 'lat': 31.9, 'lon': 34.9},
    ('deepresearch', 'deep4'): {'y': -88050, 'l': 3, 'i': 2, 't': 'Denny: Neanderthal–Denisovan child',
        'd': 'A 2 cm bone fragment from Denisova Cave, Siberia, about 90,000 years old, belonged to a girl of at least 13 whose mother was a '
             'Neanderthal and whose father a Denisovan: the first known first-generation child of two human species (Slon 2018).',
        'w': 'Denny (hybrid hominin)', 'lat': 51.397, 'lon': 84.676},
    ('research', 1): {'y': -37050, 'l': 2, 'i': 2, 't': "Gorham's Cave engraving",
        'd': "A cross-hatched pattern scratched into the rock floor of Gorham's Cave, Gibraltar, lay under layers at least 39,000 years old, "
             'so Neanderthals probably made it (Rodríguez-Vidal 2014; the dating is indirect and debated). Finds here have been read as Neanderthals '
             'surviving until 28,000 years ago or later (Finlayson 2006), but those dates come from tools, not bones, and are questioned.',
        'w': "Gorham's Cave", 'lat': 36.12, 'lon': -5.342},
    ('research', 1, 'b'): {'y': -26250, 'l': 2, 'i': 2, 't': 'Lapedo child burial',
        'd': 'A child about four years old buried with red ochre at Lagar Velho, Portugal. A 2025 direct radiocarbon date puts the bones '
             '28,600–27,800 years ago (earlier estimate: 24,500). Its finders see a mix of Neanderthal and modern-human features, a sign of '
             'interbreeding; others see no Neanderthal traits (debated).',
        'w': 'Abrigo do Lagar Velho', 'lat': 39.755, 'lon': -8.735},
}

def put(eras, era, e):
    r = next(r for r in eras if r['era'] == era)
    r['more'] = [x for x in r['more'] if x['t'] != e['t']] + [e]
    r['more'].sort(key=lambda x: x['y'])

html = PAGE.read_text(encoding='utf-8')
for tag in ('research', 'deepresearch'):
    head = f'<script id="{tag}" type="application/json">'
    m = re.search(re.escape(head) + r'(.*?)</script>', html, re.S)
    eras = json.loads(m.group(1))
    for key, e in ADD.items():
        if key[0] == tag: put(eras, key[1], e)
    blob = head + json.dumps(eras, ensure_ascii=False, separators=(',', ':')) + '</script>'
    html = html[:m.start()] + blob + html[m.end():]
    if tag == 'deepresearch': DEEP.write_text(json.dumps(eras, ensure_ascii=False, indent=0), encoding='utf-8', newline='\n')
PAGE.write_text(html, encoding='utf-8', newline='')
print('ok')

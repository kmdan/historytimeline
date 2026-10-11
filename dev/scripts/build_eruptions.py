"""Embed the largest volcanic eruptions of 500 BCE - 1900 CE as timeline events (<script id="eruptions"> in the page).

Source: eVolv2k version 4, Sigl & Toohey 2024, https://doi.org/10.1594/PANGAEA.971968 (CC BY 4.0)
  -> dev/raw/evolv2k/evolv2k_v4.tab  (PANGAEA "textfile" download; stream it, curl tends to fail)
Kept: eruptions with >= 10 Tg stratospheric sulfur (VSSI), except years the page already covers (536, 1815).
Identified volcanoes get coordinates and Wikipedia titles; unidentified ones stay on the timeline only.
Run:  .venv/Scripts/python -I dev/scripts/build_eruptions.py
"""
import io, json

KNOWN = {  # eVolv2k location -> (title, Wikipedia, lat, lon, description)
    'Samalas': ('Samalas erupts', '1257 Samalas eruption', -8.41, 116.41, 'Samalas on Lombok, Indonesia, produced the largest eruption of the last 2,000 years. Its caldera now holds Lake Segara Anak.'),
    'Okmok': ('Okmok erupts', 'Mount Okmok', 53.43, -168.13, "Okmok in Alaska's Aleutian Islands; its sulfur cooled the Northern Hemisphere in the years after Caesar's assassination."),
    'Kuwae': ('Kuwae eruption', 'Kuwae', -16.83, 168.54, 'A great eruption attributed to the Kuwae caldera in Vanuatu; one of the largest sulfate signals of the last millennium.'),
    'Laki': ('Laki fissure eruption', 'Laki', 64.07, -18.23, "An eight-month fissure eruption in Iceland; poisoned pastures and famine killed about a fifth of Iceland's people, and haze spread over Europe."),
    'Huaynaputina': ('Huaynaputina erupts', 'Huaynaputina', -16.61, -70.85, 'The largest eruption in recorded South American history; the cold summers that followed are linked to the Russian famine of 1601–1603.'),
    'Mount Parker': ('Mount Parker erupts', 'Mount Parker', 6.11, 124.89, 'A large eruption of Mount Parker on Mindanao, the Philippines.'),
    'Katla': ('Eldgjá eruption', 'Eldgjá', 63.97, -18.62, "The Eldgjá fissure of Iceland's Katla system: the largest lava flood of historical times."),
    'Ilopango': ('Ilopango erupts', 'Ilopango', 13.67, -89.05, 'The Tierra Blanca Joven eruption of Ilopango, El Salvador, buried nearby Maya settlements in ash.'),
    'Zavaritskii': ('Zavaritski eruption', 'Zavaritski Caldera', 46.93, 151.95, 'Zavaritski caldera on Simushir, Kuril Islands, recently identified as the source of a large 1831 eruption.'),
}
SKIP = {536, 1815}
s = io.open('dev/raw/evolv2k/evolv2k_v4.tab', encoding='utf-8', errors='replace').read()
rows = [l.split('\t') for l in s[s.index('*/') + 3:].splitlines()[1:]]
ev = []
for r in rows:
    y, lat, vssi, loc = int(r[0]), float(r[4]), float(r[7]), r[10].strip()
    if vssi < 10 or y in SKIP: continue
    key = next((k for k in KNOWN if loc.startswith(k)), None)
    if key:
        t, w, la, lo, d = KNOWN[key]
    else:
        where = 'probably tropical (its sulfate reached both Greenland and Antarctica)' if lat == 0 else \
                'in the Northern Hemisphere (sulfate in Greenland ice only)' if lat > 0 else 'in the Southern Hemisphere (sulfate in Antarctic ice only)'
        t, w, la, lo, d = 'Unidentified great eruption', None, None, None, f'A volcano not yet identified, {where}.'
    d += f' Ice cores record about {vssi:.0f} Tg of sulfur injected into the stratosphere (eVolv2k).'
    ev.append({'y': y, 'l': 5, 'i': 2 if vssi >= 25 else 3, 't': t if key else f'{t} ({y if y > 0 else str(-y) + " BCE"})', 'd': d, 'w': w, 'lat': la, 'lon': lo})
ev.sort(key=lambda e: e['y'])
p = 'karahan-era.html'; html = io.open(p, encoding='utf-8', newline='').read()
tag = '<script id="eruptions" type="application/json">'
blob = tag + json.dumps(ev, separators=(',', ':'), ensure_ascii=False) + '</script>'
if tag in html:
    a = html.index(tag); b = html.index('</script>', a) + len('</script>'); html = html[:a] + blob + html[b:]
else:
    a = html.index('<script id="research"'); html = html[:a] + blob + '\n' + html[a:]
io.open(p, 'w', encoding='utf-8', newline='').write(html)
print(len(ev), 'eruptions;', sum(1 for e in ev if e['lat'] is not None), 'located')

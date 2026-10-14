"""Crops and domestic animals -> atlas/crops.json (slim, loaded by the Crops & animals layer) + picture picks.

dev/data/crops.json and dev/data/animals.json (Wikipedia + papers) hold one record per crop / animal: wild ancestor,
centre, first cultivation or herding ('cult'), domestic form ('dom'), dated journeys ('spread'), pictures ('img', the
wild ancestor's 'shows' says 'wild'). Picture picks go to dev/data/popup_images_pick.json as 'Crop: <n>' /
'Animal: <n>' / 'Wild ancestor: <n>'; rebuild the sprites afterwards with build_popup_images.py --cultures.
"""
import json, re
from pathlib import Path

D = Path('dev/data')
WILD = re.compile(r'(?i)\bwild\b|teosinte|ancestor|rufipogon|goatgrass|chiltepin|currant tomato|aurochs|mouflon|junglefowl|tarpan|guanaco|vicu.a|polecat|swan goose|greylag|mallard')

def main():
    crops = json.loads((D / 'crops.json').read_bytes())
    animals = json.loads((D / 'animals.json').read_bytes())
    pick = json.loads((D / 'popup_images_pick.json').read_bytes())
    slim = []
    for kind, recs in (('c', crops['crops']), ('a', animals['animals'])):
        for c in recs:
            imgs = c.get('img') or []
            dom = next((i for i in imgs if not WILD.search(i.get('shows', ''))), None)
            wild = next((i for i in imgs if WILD.search(i.get('shows', '')) and 'side by side' not in i.get('shows', '')), None)
            kc, kw = ('Animal: ' if kind == 'a' else 'Crop: ') + c['n'], 'Wild ancestor: ' + c['n']
            if dom: pick[kc] = dom['file']
            if wild: pick[kw] = wild['file']
            y0 = c['cult'] if c.get('cult') is not None else c.get('dom')
            if y0 is None: print('NO DATE', c['n']); continue
            slim.append({k: v for k, v in dict(n=c['n'], k='a' if kind == 'a' else None, sci=c.get('sci'), wild=c.get('wild'), wl=c.get('wild_look'),
                ch=c.get('changes'), ce=c.get('centre'), lat=c['lat'], lon=c['lon'], cult=y0, dom=c.get('dom'), cn=c.get('cult_note'), dn=c.get('dom_note'),
                sp=[[s['place'], s['lat'], s['lon'], s['y'], s.get('note', '')] for s in c.get('spread', []) if s.get('y') is not None],
                today=c.get('today'), fact=c.get('fact'), ic=kc if dom else None, iw=kw if wild else None).items() if v not in (None, '', [])})
    Path('atlas/crops.json').write_text(json.dumps({'crops': slim, 'before': crops.get('before_farming', [])}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8', newline='\n')
    (D / 'popup_images_pick.json').write_bytes((json.dumps(dict(sorted(pick.items())), ensure_ascii=False, indent=0) + '\n').encode())
    print(len(slim), 'records:', sum(1 for s in slim if s.get('k') != 'a'), 'crops,', sum(1 for s in slim if s.get('k') == 'a'), 'animals;',
          sum(1 for s in slim if 'ic' in s), 'main pictures,', sum(1 for s in slim if 'iw' in s), 'wild pictures')

if __name__ == '__main__':
    main()

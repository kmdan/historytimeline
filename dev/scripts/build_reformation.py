"""Reformation 1415-1685 -> atlas/reformation.json (slim, loaded by the Reformation layer) and the tour.

dev/data/reformation.json (Wikipedia-checked, de/nl/sv Wikipedia where they give adoption years):
  places: {n, lat, lon, y (formal adoption: church order, council vote, diet), approx, conf (hussite / lutheran /
  reformed / anglican / anabaptist / unitarian / back = Catholic measure), kind (city / territory), what,
  back (year reversed by force or law), back_what, src}
  events: {n, y, date, lat, lon, what, src}
dev/data/tour_reformation.json: the tour draft; merged into dev/data/tours.json (img -> 'Tour: <step title>' picked
to the step's img_alt painting in popup_images_pick.json). Run embed_tours.py and build_popup_images.py --cultures after.
"""
import json
from pathlib import Path

D = Path('dev/data')

def main():
    d = json.loads((D / 'reformation.json').read_bytes())
    P = [[p['n'], p['lat'], p['lon'], p['y'], 1 if p.get('approx') else 0, p['conf'], p.get('kind', 'city'), p.get('what', ''),
          p.get('back'), p.get('back_what') or ''] for p in d['places']]
    E = [[e['n'], e['y'], e.get('date', ''), e['lat'], e['lon'], e['what']] for e in d['events']]
    Path('atlas/reformation.json').write_text(json.dumps({'p': P, 'e': E}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8', newline='\n')
    print(len(P), 'places,', len(E), 'events')

    t = json.loads((D / 'tour_reformation.json').read_bytes())
    pick = json.loads((D / 'popup_images_pick.json').read_bytes())
    for s in t['steps']:
        alt = s.pop('img_alt', None)
        if alt: s['img'] = 'Tour: ' + s['t']; pick[s['img']] = alt['file']
    t['ly'] = {'lyReform': True, 'lyCities': False, 'lyRoutes': False, 'lyCrops': False, 'lyBorders': True, 'lyMigr': False,
               'lyFigs': False, 'lyC14': False, 'lyPop': False, 'lyEvents': True, 'lyFauna': False, 'lyHomo': False, 'lyPlague': False}
    raw = (D / 'tours.json').read_bytes().decode('utf-8')
    tours = json.loads(raw)
    tours = [x for x in tours if x['id'] != t['id']]
    i = next((k for k, x in enumerate(tours) if x['id'] == 'black-death'), len(tours) - 1) + 1
    tours.insert(i, t)
    (D / 'tours.json').write_bytes(json.dumps(tours, ensure_ascii=False, indent=1).replace('\n', '\r\n').encode('utf-8') + b'\r\n')
    (D / 'popup_images_pick.json').write_bytes((json.dumps(dict(sorted(pick.items())), ensure_ascii=False, indent=0) + '\n').encode())
    print(len(t['steps']), 'tour steps;', len(tours), 'tours')

if __name__ == '__main__':
    main()

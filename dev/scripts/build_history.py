"""History layers + their tours -> atlas/history.json and dev/data/tours.json.

Topic files dev/data/<topic>.json (format: dev/data/FORMAT-history-layers.md) are merged into atlas/history.json, which the
page loads for the 'Revolutions & empires' (places, routes) and 'Battles & campaigns' (battles, campaigns) layers.
Tour drafts dev/data/tour_<topic>.json are merged into dev/data/tours.json (replacing a tour with the same id); each step's
img_alt painting is picked as 'Tour: <id>: <title>' in popup_images_pick.json. Afterwards run embed_tours.py and
build_popup_images.py --cultures.
"""
import json, sys
from pathlib import Path

D = Path('dev/data')
TOPICS = ['buddhism', 'islam', 'columbian_exchange', 'french_revolution', 'napoleon', 'british_empire']
# layers each new tour shows; every other tour turns these layers off
LY_ALL = ['lyFaith', 'lyHist', 'lyWars', 'lyReform', 'lyCities', 'lyRoutes', 'lyCrops', 'lyMigr', 'lyFigs', 'lyC14', 'lyPop', 'lyFauna', 'lyHomo', 'lyPlague']
TOUR_LY = {
    'buddhism': {'lyFaith', 'lyWars', 'lyRoutes'},
    'islam': {'lyFaith', 'lyWars', 'lyRoutes'},
    'columbian_exchange': {'lyHist', 'lyRoutes', 'lyCrops', 'lyMigr'},
    'french_revolution': {'lyHist', 'lyWars'},
    'napoleon': {'lyHist', 'lyWars'},
    'british_empire': {'lyHist', 'lyWars', 'lyRoutes'},
}
AFTER = {'buddhism': 'black-death', 'islam': 'buddhism', 'columbian_exchange': 'silk-roads', 'french_revolution': 'reformation', 'napoleon': 'french-revolution', 'british_empire': 'napoleon'}

def load(p):
    return json.loads(p.read_bytes()) if p.exists() else None

def main():
    out = {'places': [], 'battles': [], 'campaigns': [], 'routes': []}
    for t in TOPICS:
        d = load(D / f'{t}.json')
        if not d: print('missing', t); continue
        REL = {'buddhism': 'Buddhism', 'islam': 'Islam'}
        for p in d.get('places', []):
            if t in REL and not str(p.get('who', '')).startswith(REL[t]): p['who'] = REL[t]   # all places of a religion topic go to the religions layer
            out['places'].append([p['n'], p['lat'], p['lon'], p['y'], p.get('end'), 1 if p.get('approx') else 0, p.get('kind', 'other'),
                                  p.get('who', '') + (' · ' + p['sub'] if p.get('sub') else ''), p.get('what', ''), p.get('w', '')])
        for b in d.get('battles', []):
            out['battles'].append([b['n'], b['y'], b.get('date', ''), b['lat'], b['lon'], b.get('war', ''), b.get('a', ''), b.get('b', ''),
                                   b.get('won', ''), b.get('men'), b.get('loss'), b.get('what', ''), b.get('w', '')])
        for c in d.get('campaigns', []):
            pts = [q for q in c['pts'] if q[2] is not None]
            out['campaigns'].append({'n': c['n'], 'who': c.get('who', ''), 'side': c.get('side', ''), 'pts': pts, 'what': c.get('what', ''), 'w': c.get('w', '')})
        for r in d.get('routes', []):
            out['routes'].append({k: r.get(k) for k in ('n', 'from', 'to', 'kind', 'path', 'goods', 'd', 'w', 'who') if r.get(k) is not None})
        print(t, {k: len(d.get(k, [])) for k in out})
    for b in out['battles']:   # men/loss may be single numbers or partly missing
        for i in (9, 10):
            v = b[i]
            if v is not None and not (isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) or x is None for x in v)): b[i] = None
            elif v is not None: b[i] = [x if x is not None else 0 for x in v]
    Path('atlas/history.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8', newline='\n')

    tours = json.loads((D / 'tours.json').read_bytes())
    pick = json.loads((D / 'popup_images_pick.json').read_bytes())
    for t in TOPICS:
        tr = load(D / f'tour_{t}.json')
        if not tr: continue
        tr['id'] = tr['id'].replace('_', '-')
        for s in tr['steps']:
            alt = s.pop('img_alt', None)
            if alt and alt.get('file'): s['img'] = f"Tour: {tr['id']}: {s['t']}"; pick[s['img']] = alt['file']
        tr['ly'] = {**{k: k in TOUR_LY[t] for k in LY_ALL}, 'lyBorders': True, 'lyEvents': True}
        tours = [x for x in tours if x['id'] != tr['id']]
        a = AFTER[t]; i = next((k + 1 for k, x in enumerate(tours) if x['id'] == a), len(tours))
        tours.insert(i, tr)
    new = {json.loads((D / f'tour_{t}.json').read_bytes())['id'].replace('_', '-') for t in TOPICS if (D / f'tour_{t}.json').exists()}
    for x in tours:
        if x['id'] not in new: x.setdefault('ly', {}); x['ly'].setdefault('lyHist', False); x['ly'].setdefault('lyWars', False); x['ly'].setdefault('lyFaith', False)
    (D / 'tours.json').write_bytes(json.dumps(tours, ensure_ascii=False, indent=1).replace('\n', '\r\n').encode('utf-8') + b'\r\n')
    (D / 'popup_images_pick.json').write_bytes((json.dumps(dict(sorted(pick.items())), ensure_ascii=False, indent=0) + '\n').encode())
    print(len(tours), 'tours:', [x['id'] for x in tours])

if __name__ == '__main__':
    main()

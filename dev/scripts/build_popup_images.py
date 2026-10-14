"""Pictures for map popups and the selected-event card: the lead image of each item's Wikipedia article.

Collects the Wikipedia titles used by events, landscapes, animals, migrations and Ice Age cultures
(plus Ice Age site names whose article is an archaeological site), asks Wikipedia for the free lead
image (prop=pageimages, pilicense=free), skips maps / flags / charts / SVG drawings, reads licence and
author from Commons, and keeps 360 px thumbnails in dev/raw/pimg/ (download cache, not committed).
The artifact holds at most 511 files, so the published pictures are packed into sprite sheets:
atlas/pimg/s<n>.webp, a grid of COLS x ROWS cells of 360x225 (16:10, cropped 30 % from the top), and
atlas/pimg/index.json: {"_grid": [COLS, ROWS], "<title>": {"s": sheet, "c": cell, "file": "File:..", "lic":.., "artist":..}}
Popup items look pictures up by their Wikipedia title (`w`), sites by name.
dev/data/popup_images_pick.json overrides the lead image per title/site (hand-picked art);
dev/data/popup_images_skip.json lists lead images rejected by eye (maps, charts, text pages).
Run: .venv/Scripts/python -I dev/scripts/build_popup_images.py [--cultures]   (--cultures adds the 800 culture articles)
"""
import hashlib, html, io, json, re, sys, time, urllib.parse, urllib.request
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'atlas' / 'pimg'
CACHE = ROOT / 'dev' / 'raw' / 'pimg'
COLS, ROWS, CW, CH = 8, 6, 360, 225
UA = 'KarahanEra/0.1 (https://github.com/kmdan/historytimeline)'
WIDTH = 360
FREE = re.compile(r'^(public domain|pd|cc0|cc by(-sa)? [\d.]+|cc-by(-sa)?-[\d.]+|no restrictions|attribution$|fal$|free art)', re.I)
# lead images that are maps, flags, charts or diagrams rather than pictures of the thing
SKIP = re.compile(r'(\.svg$|\.gif$|map|karte|carte|mapa|locator|location|distribution|range|extent|expansion|migration|'
                  r'route|flag|coat.of.arms|emblem|seal.of|chart|graph|diagram|timeline|plot|logo|\bpd\b.*text)', re.I)
# hand-picked pictures (paintings / life restorations in their setting) that replace or add to the lead image
PICK = json.loads((ROOT / 'dev' / 'data' / 'popup_images_pick.json').read_text(encoding='utf-8'))
# lead images checked by eye on contact sheets and found to be maps, charts or text pages
SKIP_FILES = set(json.loads((ROOT / 'dev' / 'data' / 'popup_images_skip.json').read_text(encoding='utf-8')))
SITE = re.compile(r'(archaeolog|cave|rock shelter|rockshelter|paleolithic|palaeolithic|mesolithic|neolithic|prehistoric|site|burial|settlement)', re.I)


def get(url):
    for wait in (0, 5, 30, 90):
        time.sleep(wait)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503):
                raise
        except (urllib.error.URLError, TimeoutError):  # dropped connection: wait and retry
            pass
    raise RuntimeError('rate limited: ' + url)


def api(host, **q):
    q.update(action='query', format='json', formatversion=2)
    return json.loads(get(f'https://{host}/w/api.php?' + urllib.parse.urlencode(q)))['query']


def text(v):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', v or ''))).strip()


def block(page, i):
    return json.loads(re.search(rf'<script id="{i}"[^>]*>(.*?)</script>', page, re.S).group(1))


def titles(page, cultures):
    t = []
    for r in block(page, 'research'):
        t += [x.get('w') for x in r['events'] + r['more']]
    t += [x.get('w') for x in block(page, 'envdata')['impact']['events']]
    t += [m.get('w') for m in block(page, 'migr')]
    ice = block(page, 'iceage'); t += [c.get('w') for c in ice]
    for name in ('MARKS', 'ANIMALS'):  # M(la,lo,f,t,'name','desc','Wikipedia title'),
        body = page[page.index(f'const {name}='):]; body = body[:body.index('];')]
        t += [m.group(1).replace("\\'", "'") for m in re.finditer(r"'((?:[^'\\]|\\.)*)'\),?\s*$", body, re.M)]
    if cultures:
        t += [v.get('w') for v in block(page, 'cultwiki').values()]
    sites = [s['n'] for c in ice for s in c.get('sites', [])]
    return list(dict.fromkeys(x for x in t if x)), list(dict.fromkeys(sites))


def lead_images(names, check_site=False):
    """Wikipedia title -> Commons file name of the article's free lead image."""
    out = {}
    for i in range(0, len(names), 50):
        q = api('en.wikipedia.org', titles='|'.join(names[i:i + 50]), prop='pageimages|description',
                piprop='name', pilicense='free', redirects=1)
        back = {}
        for k in ('normalized', 'redirects'):
            for r in q.get(k, []):
                back[r['to']] = back.get(r['from'], r['from'])
        for p in q['pages']:
            name = back.get(p['title'], p['title'])
            if check_site and not SITE.search(p.get('description', '')):
                continue
            if p.get('pageimage') and not SKIP.search(p['pageimage']) and 'File:' + p['pageimage'].replace('_', ' ') not in SKIP_FILES:
                out[name] = 'File:' + p['pageimage']
        time.sleep(1)
    return out


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    page = (ROOT / 'karahan-era.html').read_text(encoding='utf-8')
    wt, sites = titles(page, '--cultures' in sys.argv)
    want = lead_images(wt); want.update({k: v for k, v in lead_images(sites, True).items() if k not in want})
    want.update(PICK)
    print(len(wt), 'titles +', len(sites), 'sites ->', len(want), 'with a usable lead picture')
    CACHE.mkdir(parents=True, exist_ok=True)
    idx_path = CACHE / 'index.json'
    idx = json.loads(idx_path.read_text(encoding='utf-8')) if idx_path.exists() else {}
    todo = [t for t, f in want.items() if not (t in idx and idx[t]['file'] == f and (CACHE / Path(idx[t]['src']).name).exists())]
    files = sorted(set(want[t] for t in todo))
    meta = {}
    for i in range(0, len(files), 50):
        q = api('commons.wikimedia.org', titles='|'.join(files[i:i + 50]), prop='imageinfo',
                iiprop='url|extmetadata', iiurlwidth=WIDTH)
        for p in q['pages']:
            if p.get('imageinfo'):
                meta[p['title']] = p['imageinfo'][0]
        time.sleep(1)
    norm = lambda f: f.replace('_', ' ')
    done = {}
    for t in todo:
        f = norm(want[t]); ii = meta.get(f)
        if not ii:
            print('MISSING', t, f); continue
        m = ii.get('extmetadata', {}); lic = text(m.get('LicenseShortName', {}).get('value'))
        if not FREE.match(lic) or m.get('NonFree', {}).get('value') == 'true':
            print('NONFREE', lic, '|', t); continue
        name = hashlib.sha1(f.encode()).hexdigest()[:10] + '.webp'
        if f not in done and (CACHE / name).exists():  # already downloaded by an interrupted run
            done[f] = Image.open(CACHE / name).size
        if f not in done:
            try:
                im = Image.open(io.BytesIO(get(ii['thumburl']))); im.load()
            except RuntimeError as e:  # still rate limited after the retries: leave it for the next run
                print('LATER', t, e); continue
            if im.mode != 'RGB':  # flatten transparency onto white
                im = im.convert('RGBA'); bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); im = bg
            im.thumbnail((WIDTH, WIDTH * 2))
            im.save(CACHE / name, 'WEBP', quality=72, method=6)
            done[f] = (im.width, im.height); time.sleep(2)
        w, h = done[f]
        idx[t] = {'src': 'pimg/' + name, 'w': w, 'h': h, 'file': f, 'lic': lic,
                  'artist': text(m.get('Artist', {}).get('value'))[:120]}
        print('ok', t, '<-', f, flush=True)
        idx_path.write_bytes(json.dumps(idx, ensure_ascii=False, indent=0, sort_keys=True).encode('utf-8'))
    for t in [t for t in idx if t not in want]:  # titles no longer used or no longer suitable
        del idx[t]
    idx_path.write_bytes(json.dumps(idx, ensure_ascii=False, indent=0, sort_keys=True).encode('utf-8'))
    used = {Path(v['src']).name for v in idx.values()} | {hashlib.sha1(norm(f).encode()).hexdigest()[:10] + '.webp' for f in want.values()}
    for p in CACHE.glob('*.webp'):
        if p.name not in used:
            p.unlink()
    pack(idx)


def pack(idx):
    """Sprite sheets: one 16:10 cell per distinct Commons file, cropped like the page's old object-position 50% 30%."""
    files = sorted({v['file'] for v in idx.values()})
    cell = {f: i for i, f in enumerate(files)}
    per = COLS * ROWS
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob('*'):
        p.unlink()
    src = {v['file']: CACHE / Path(v['src']).name for v in idx.values()}
    for n in range(0, len(files), per):
        sheet = Image.new('RGB', (COLS * CW, ROWS * CH), (128, 128, 128))
        for i, f in enumerate(files[n:n + per]):
            im = Image.open(src[f]).convert('RGB')
            k = max(CW / im.width, CH / im.height)
            im = im.resize((max(CW, round(im.width * k)), max(CH, round(im.height * k))), Image.LANCZOS)
            x0, y0 = (im.width - CW) // 2, round((im.height - CH) * 0.3)
            sheet.paste(im.crop((x0, y0, x0 + CW, y0 + CH)), ((i % COLS) * CW, (i // COLS) * CH))
        sheet.save(OUT / f's{n // per}.webp', 'WEBP', quality=74, method=6)
    # _v: content hash per sheet; the page asks for s<n>.webp?v=<hash> so a browser never pairs a new index with an old cached sheet
    out = {'_grid': [COLS, ROWS], '_v': [hashlib.sha1((OUT / f's{k}.webp').read_bytes()).hexdigest()[:8] for k in range(-(-len(files) // per))]}
    for t, v in sorted(idx.items()):
        c = cell[v['file']]
        out[t] = {'s': c // per, 'c': c % per, 'file': v['file'], 'lic': v['lic'], 'artist': v['artist']}
    (OUT / 'index.json').write_bytes(json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
    print(len(idx), 'pictures in', -(-len(files) // per), 'sheets,', round(sum(p.stat().st_size for p in OUT.glob('*.webp')) / 1e6, 1), 'MB')


if __name__ == '__main__':
    sys.exit(main())

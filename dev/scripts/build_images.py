"""Download era illustrations from Wikimedia Commons as small local files.

Reads the Commons file names from <script id="research"> and <script id="deepresearch"> in karahan-era.html,
asks the Commons API for a 640 px thumbnail plus licence/author metadata, and
writes atlas/img/<id>.webp (quality 76, ~50 kB) and atlas/img/index.json:
  {"File:...": {"src": "img/<id>.webp", "w": .., "h": .., "lic": .., "lic_url": .., "artist": .., "ok": bool}}
"ok" is False when the licence is not free (the page then keeps a link card).
Run: .venv/Scripts/python -I dev/scripts/build_images.py
"""
import hashlib, html, io, json, re, sys, time, urllib.parse, urllib.request
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'atlas' / 'img'
UA = 'KarahanEra/0.1 (https://github.com/kmdan/historytimeline)'
WIDTH = 640
FREE = re.compile(r'^(public domain|pd|cc0|cc by(-sa)? [\d.]+|cc-by(-sa)?-[\d.]+)', re.I)


def get(url):
    for wait in (0, 5, 30, 90):
        time.sleep(wait)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503):
                raise
        except (urllib.error.URLError, TimeoutError, OSError):   # stalled connection: wait and retry
            pass
    raise RuntimeError('rate limited: ' + url)


def text(v):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', v or ''))).strip()


def main():
    page = (ROOT / 'karahan-era.html').read_text(encoding='utf-8')
    research = [era for tag in ('research', 'deepresearch')      # deepresearch: the five eras before 40,000 BCE
                for m in [re.search(r'<script id="%s" type="application/json">(.*?)</script>' % tag, page, re.S)] if m
                for era in json.loads(m.group(1))]
    files = list(dict.fromkeys(im['file'] for era in research for im in era.get('images', [])))
    OUT.mkdir(parents=True, exist_ok=True)
    idx_path = OUT / 'index.json'
    idx = json.loads(idx_path.read_text(encoding='utf-8')) if idx_path.exists() else {}
    for f in files:
        if f in idx and (OUT / Path(idx[f]['src']).name).exists():
            continue
        q = urllib.parse.urlencode({'action': 'query', 'format': 'json', 'titles': f, 'prop': 'imageinfo',
                                    'iiprop': 'url|extmetadata|mime', 'iiurlwidth': WIDTH})
        pages = json.loads(get('https://commons.wikimedia.org/w/api.php?' + q))['query']['pages']
        p = next(iter(pages.values()))
        if 'imageinfo' not in p:
            print('MISSING', f); continue
        ii = p['imageinfo'][0]; m = ii.get('extmetadata', {})
        lic = text(m.get('LicenseShortName', {}).get('value'))
        ok = bool(FREE.match(lic)) and m.get('NonFree', {}).get('value') != 'true'
        rec = {'lic': lic, 'lic_url': m.get('LicenseUrl', {}).get('value', ''),
               'artist': text(m.get('Artist', {}).get('value'))[:120], 'ok': ok}
        if ok:
            name = hashlib.sha1(f.encode()).hexdigest()[:10] + '.webp'
            im = Image.open(io.BytesIO(get(ii['thumburl']))); im.load()
            if im.mode != 'RGB':  # flatten transparency (SVG/PNG thumbs) onto white
                im = im.convert('RGBA'); bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); im = bg
            im.thumbnail((WIDTH, WIDTH * 2))
            im.save(OUT / name, 'WEBP', quality=76, method=6)
            rec.update(src='img/' + name, w=im.width, h=im.height)
        idx[f] = rec
        print('ok ' if ok else 'NONFREE', lic, '|', f)
        idx_path.write_text(json.dumps(idx, ensure_ascii=False, indent=0, sort_keys=True), encoding='utf-8')
        time.sleep(1)
    print(len(idx), 'entries;', sum(1 for v in idx.values() if v['ok']), 'free')


if __name__ == '__main__':
    sys.exit(main())

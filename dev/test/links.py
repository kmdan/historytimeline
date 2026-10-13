"""Deep links, crawler-visible text and head tags (installed Edge via Playwright; local server on 8765).

Run:  python dev/test/links.py
1. ?y=-4500 and ?y=1750&at=48,10,4 open at that year / map view
2. scrubbing the timeline and zooming the map update the address bar (replaceState)
3. bad values are ignored; ?cpu survives
4. raw HTML (no JS) has title, description, canonical, JSON-LD, lead text and the sources section
"""
import os
import json, re, sys, urllib.request
from playwright.sync_api import sync_playwright

URL = os.environ.get('KE_BASE','http://localhost:8765/')+'karahan-era.html'
fails = []
def ok(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

raw = urllib.request.urlopen(URL).read().decode('utf-8')
head = raw[:raw.index('</head>')]
ok('<html lang="en">' in raw[:60], 'lang="en"')
ok(re.search(r'<title>Karahan Era: interactive world history', head) is not None, 'title in <head>')
ok('name="description"' in head and 'rel="canonical"' in head and 'og:image' in head, 'description, canonical, og tags in <head>')
ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', head).group(1))
ok(ld['@type'] == 'WebApplication' and len(ld['isBasedOn']) >= 5, 'JSON-LD parses, lists datasets')
text = re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>', ' ', raw, flags=re.S)
ok('Drag the timeline to travel from' in text and 'About the data' in text and 'De Groeve et al. 2022' in text, 'lead + sources readable without JS')

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True, args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    def page(q, **kw):
        pg = b.new_page(viewport=kw.get('vp', {'width': 1100, 'height': 900}))
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))   # script errors only; outside resources (fonts, thumbnails) may time out headless
        pg.goto(URL + q); pg.wait_for_timeout(4000)
        return pg, errs
    st = lambda pg: pg.evaluate("() => ({ph: document.getElementById('ph').textContent, at: document.getElementById('atlasYear').textContent, url: location.search, label: document.getElementById('map').getAttribute('aria-label')})")

    pg, e = page('')
    s = st(pg); ok(s['url'] == '', f'no params on a plain load: {s["url"]!r}'); ok(not e, f'no errors: {e}')
    pg, e = page('?y=-4500')
    s = st(pg); ok('4,500 BCE' in s['at'] and '4,500 BCE' in s['label'], f'?y=-4500 -> {s["at"]} / label {s["label"][:40]}'); ok(not e, f'no errors: {e}')
    pg, e = page('?y=1750&at=48,10,4')
    s = st(pg); ok('1750' in s['at'], f'?y=1750 -> {s["at"]}')
    ok(s['url'] == '?y=1750&at=48,10,4', f'URL left as given until the view changes: {s["url"]}')
    # scrub the timeline (pointer events, like check.py): URL follows, no history entries
    h0 = pg.evaluate('history.length')
    pg.evaluate("""() => { const c=document.getElementById('tl'); c.scrollIntoView(); const b=c.getBoundingClientRect(), y=b.top+b.height*0.6, x0=b.left+b.width*0.5;
      const ev=(t,x)=>c.dispatchEvent(new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,pointerId:1,pointerType:'mouse',isPrimary:true,buttons:1}));
      ev('pointerdown',x0); for(let i=1;i<=10;i++) ev('pointermove',x0+30*i); ev('pointerup',x0+300); }""")
    pg.wait_for_timeout(1200)
    s2 = st(pg); ok(s2['url'] != s['url'] and 'y=' in s2['url'] and 'at=48.0,10.0,4.0' in s2['url'], f'scrub updates URL: {s["url"]} -> {s2["url"]}')
    ok(pg.evaluate('history.length') == h0, 'no history entries added')
    # map zoom out to whole world drops `at`
    pg.click('#mHome'); pg.wait_for_timeout(2000); s3 = st(pg); ok('at=' not in s3['url'], f'home view drops at: {s3["url"]}')
    pg, e = page('?y=abc&at=x,y'); s = st(pg); ok(not e and s['url'] == '?y=abc&at=x,y', f'bad values ignored, no errors: {e} {s["at"]}')
    pg, e = page('?y=99999'); s = st(pg); ok('99999' not in s['at'], f'out of range ignored: {s["at"]}')
    pg, e = page('?cpu&y=900'); s = st(pg)
    ok(pg.evaluate("document.getElementById('map').dataset.renderer") == 'cpu' and '900' in s['at'], f'?cpu&y=900 -> cpu, {s["at"]}')
    pg.click('#bNow'); pg.wait_for_function("/[?&]y=2/.test(location.search)", timeout=6000); s = st(pg);   # the ?cpu renderer can take a while ok(s['url'].startswith('?cpu&') and 'y=2' in s['url'], f'cpu kept after move: {s["url"]}')
    pg, e = page('?y=-21000', vp={'width': 375, 'height': 812})
    ok(pg.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'phone: no horizontal scroll'); ok(not e, f'phone no errors: {e}')
    b.close()
print('\nFAILED: ' + '; '.join(fails) if fails else '\nall passed')
sys.exit(1 if fails else 0)

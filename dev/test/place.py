"""'What happened here?' checks. Run:  KE_BASE=http://localhost:8767/ python dev/test/place.py [outdir]
Pins a spot (Denmark, near Doggerland) through the ground popup, checks the place card, then plays from there and
waits for the first pause note."""
import os, sys, json
from playwright.sync_api import sync_playwright
BASE = os.environ.get('KE_BASE', 'http://localhost:8765/'); OUT = sys.argv[1] if len(sys.argv) > 1 else 'dev/test/out'
LAT, LON = 55.5, 9.5
for mobile in (False, True):
    with sync_playwright() as p:
        br = p.chromium.launch(channel='msedge', headless=True, args=['--enable-gpu', '--use-angle=d3d11'])
        kw = dict(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True) if mobile else dict(viewport={'width': 1100, 'height': 900})
        pg = br.new_context(**kw).new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE + f'karahan-era.html?y=-16000&at={LAT},{LON},4'); pg.wait_for_timeout(6000)
        pg.evaluate("document.getElementById('atlas').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300)
        m = pg.locator('#map').bounding_box(); x, y = m['x'] + m['width'] / 2, m['y'] + m['height'] / 2   # the view is centred on the spot
        (pg.touchscreen.tap if mobile else pg.mouse.click)(x, y); pg.wait_for_timeout(500)
        r = {'popup': pg.inner_text('#pop').split('\n')[:2] if pg.is_visible('#pop') else None, 'buttons': pg.locator('#pop .phere, #pop .pplay').count()}
        pg.locator('#pop .phere').click(); pg.wait_for_timeout(800)
        r['card'] = pg.is_visible('#placeCard'); r['where'] = pg.inner_text('#plWhere'); r['events'] = pg.locator('#plEvents li:not([hidden]) button[data-i]').count()
        pg.locator('#placeCard').screenshot(path=f'{OUT}/place_card_{"phone" if mobile else "desk"}.png')
        pg.click('#plPlay'); r['stops'] = pg.inner_text('#plNote')
        notes = []
        for _ in range(40):
            pg.wait_for_timeout(500)
            if pg.is_visible('#note'):
                t = pg.inner_text('#note').split('\n')[:2]
                if not notes or notes[-1] != t: notes.append(t)
                if len(notes) == 1: pg.locator('.stack').screenshot(path=f'{OUT}/place_note_{"phone" if mobile else "desk"}.png')
                if len(notes) >= 3: break
        r['notes'] = notes; r['play_button'] = pg.inner_text('#bPlay'); r['errors'] = errs
        if mobile: r['scrollWidth'] = pg.evaluate('document.documentElement.scrollWidth')
        print('phone' if mobile else 'desktop', json.dumps(r, ensure_ascii=False))
        br.close()

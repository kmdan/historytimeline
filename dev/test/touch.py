"""Touch checks on emulated phone/tablet (Edge, Playwright + CDP synthesized gestures).
Run (server on :8765):  python dev/test/touch.py [outdir]
For each device: page scrolls when swiping over the map; sideways swipe on the timeline travels; two-finger pinch zooms
the map; tapping a map label opens a popup that stays open, fits the screen and has a reachable Wikipedia link.
"""
import sys, json
from playwright.sync_api import sync_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'dev/test/out'
def swipe(cdp, pg, x, y, dx, dy, steps=12):     # raw touch events (synthesizeScrollGesture does not scroll in headless)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
    for i in range(1, steps + 1):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x + dx * i / steps, 'y': y + dy * i / steps}]}); pg.wait_for_timeout(16)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
DEV = {'phone': dict(viewport={'width': 390, 'height': 844}, device_scale_factor=3, is_mobile=True, has_touch=True),
       'tablet': dict(viewport={'width': 820, 'height': 1180}, device_scale_factor=2, is_mobile=True, has_touch=True)}
with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge', headless=True, args=['--enable-gpu', '--use-angle=d3d11'])
    for name, kw in DEV.items():
        ctx = br.new_context(**kw); pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('http://localhost:8765/karahan-era.html'); pg.wait_for_timeout(5000)
        cdp = ctx.new_cdp_session(pg); res = {}
        pg.evaluate("document.getElementById('atlas').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300)
        m = pg.locator('#map').bounding_box(); t = pg.locator('#tl').bounding_box()
        # 1. vertical swipe over the map scrolls the page
        y0 = pg.evaluate('scrollY')
        swipe(cdp, pg, m['x'] + m['width'] / 2, m['y'] + m['height'] * .7, 0, -250)
        pg.wait_for_timeout(500); res['page_scroll_over_map'] = pg.evaluate('scrollY') - y0
        pg.evaluate("document.getElementById('atlas').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300)
        m = pg.locator('#map').bounding_box(); t = pg.locator('#tl').bounding_box()
        # 2. sideways swipe on the timeline travels in time, page does not scroll
        ph0 = pg.inner_text('#ph'); y0 = pg.evaluate('scrollY')
        swipe(cdp, pg, t['x'] + t['width'] * .7, t['y'] + t['height'] * .6, -200, 0)
        pg.wait_for_timeout(500); res['timeline_swipe'] = [ph0, pg.inner_text('#ph'), 'page moved %d' % (pg.evaluate('scrollY') - y0)]
        # 3. pinch on the map zooms it (map pixels change), page zoom stays 1
        before = pg.evaluate("document.getElementById('map').toDataURL().length")
        cdp.send('Input.synthesizePinchGesture', {'x': m['x'] + m['width'] / 2, 'y': m['y'] + m['height'] / 2, 'scaleFactor': 2.0, 'gestureSourceType': 'touch'})
        pg.wait_for_timeout(700); res['pinch_changed_map'] = pg.evaluate("document.getElementById('map').toDataURL().length") != before
        res['visual_zoom'] = pg.evaluate('visualViewport.scale')
        # 4. tap a map label: popup opens, stays, fits, link reachable
        pg.click('#mHome'); pg.wait_for_timeout(600)
        m = pg.locator('#map').bounding_box()
        hit = None
        for fx in [i / 12 for i in range(1, 12)]:
            for fy in [j / 8 for j in range(1, 8)]:
                pg.touchscreen.tap(m['x'] + m['width'] * fx, m['y'] + m['height'] * fy); pg.wait_for_timeout(150)
                if pg.is_visible('#pop'): hit = (fx, fy); break
            if hit: break
        pg.wait_for_timeout(1200)
        res['popup_open_after_1s'] = pg.is_visible('#pop')
        if res['popup_open_after_1s']:
            box = pg.locator('#pop').bounding_box(); vw = kw['viewport']
            res['popup_fits'] = box['x'] >= 0 and box['y'] >= 0 and box['x'] + box['width'] <= vw['width'] + 1 and box['y'] + box['height'] <= vw['height'] + 1
            res['popup_title'] = pg.inner_text('#pop h4')
            link = pg.locator('#pop .pl a').first
            if link.count():
                lb = link.bounding_box()
                res['link_reachable'] = pg.evaluate("([x,y])=>{ const e=document.elementFromPoint(x,y); return !!(e&&e.closest('.pl a')); }", [lb['x'] + lb['width'] / 2, lb['y'] + lb['height'] / 2])
            pg.screenshot(path=f'{OUT}/touch_{name}.png')
            pg.tap('#pop .pclose'); pg.wait_for_timeout(200); res['close_button_works'] = not pg.is_visible('#pop')
        res['errors'] = errs; res['scrollWidth'] = pg.evaluate('document.documentElement.scrollWidth')
        print(name, json.dumps(res, ensure_ascii=False))
        ctx.close()
    br.close()

"""Guided-tour checks. Run:  KE_BASE=http://localhost:8768/ python dev/test/tours.py [outdir]
Opens the tours menu, starts the first tour, checks that each Next moves the timeline year and the map view to the
step, tries Back, auto mode and the deep link ?tour=&step=, on desktop and phone."""
import os, sys, json
from playwright.sync_api import sync_playwright
BASE = os.environ.get('KE_BASE', 'http://localhost:8765/'); OUT = sys.argv[1] if len(sys.argv) > 1 else 'dev/test/out'
os.makedirs(OUT, exist_ok=True)
STATE = "(()=>{ const q=new URLSearchParams(location.search); return {y:+q.get('y'), at:q.get('at'), tour:q.get('tour'), step:+q.get('step')}; })()"
for mobile in (False, True):
    tag = 'phone' if mobile else 'desk'
    with sync_playwright() as p:
        br = p.chromium.launch(channel='msedge', headless=True, args=['--enable-gpu', '--use-angle=d3d11'])
        kw = dict(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True) if mobile else dict(viewport={'width': 1100, 'height': 900})
        pg = br.new_context(**kw).new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE + 'karahan-era.html'); pg.wait_for_timeout(6000)
        tours = pg.evaluate("JSON.parse(document.getElementById('tours').textContent)")
        r = {'tours': [t['id'] for t in tours]}
        pg.click('#bTours'); pg.wait_for_timeout(200); r['menu'] = pg.locator('#tourMenu button').count()
        pg.locator('#tourMenu').screenshot(path=f'{OUT}/tour_menu_{tag}.png')
        LY0 = pg.evaluate("Object.fromEntries([...document.querySelectorAll('input[id^=ly]')].map(c=>[c.id,c.checked]))")
        pg.locator('#tourMenu button[data-id]').first.click(); pg.wait_for_timeout(5200)
        T = tours[0]; steps = []
        for i, st in enumerate(T['steps']):
            s = pg.evaluate(STATE); txt = pg.inner_text('#tour').split('\n')
            ok_y = abs(s['y'] - st['y']) <= max(2, abs(st['y']) * 0.002)
            at = [float(v) for v in (s['at'] or '0,0,1').split(',')]
            steps.append({'i': i + 1, 'y': s['y'], 'want': st['y'], 'ok_y': ok_y, 'at': s['at'], 'step': s['step'], 'head': txt[0][:60]})
            if i == 1: pg.locator('.stack').screenshot(path=f'{OUT}/tour_step_{tag}.png')
            if i < len(T['steps']) - 1:   # Next visits the step's "did you know" notes first
                for _ in st.get('tips', []): pg.click('#tour .tn'); pg.wait_for_timeout(400)
                r.setdefault('notes_seen', 0); r['notes_seen'] += len(st.get('tips', [])) and pg.is_visible('#tnote')
                pg.click('#tour .tn'); pg.wait_for_timeout(5200)
        r['steps'] = steps
        pg.click('#tour .tb'); pg.wait_for_timeout(1500); r['back_step'] = pg.evaluate(STATE)['step']
        # auto mode from step 1: should advance by itself
        for _ in range(len(T['steps'])): pg.click('#tour .tb') if pg.is_enabled('#tour .tb') else None; pg.wait_for_timeout(150)   # dots are hidden on phones
        pg.wait_for_timeout(1500); r['first_step'] = pg.evaluate(STATE)['step']; pg.click('#tour .ta')
        card0 = pg.inner_text('#tour'); pg.wait_for_timeout(16000); r['auto_step'] = pg.evaluate(STATE)['step']
        r['auto_moved'] = pg.inner_text('#tour') != card0   # to a note or the next step
        pg.click('#tour .tx'); pg.wait_for_timeout(700); r['closed'] = not pg.is_visible('#tour') and pg.evaluate(STATE)['tour'] is None
        r['layers_restored'] = LY0 == pg.evaluate("Object.fromEntries([...document.querySelectorAll('input[id^=ly]')].map(c=>[c.id,c.checked]))")
        # deep link
        pg.goto(BASE + f"karahan-era.html?tour={T['id']}&step=2"); pg.wait_for_timeout(6000)
        r['deeplink'] = {'visible': pg.is_visible('#tour'), **pg.evaluate(STATE)}
        # search finds the tour
        pg.fill('#q', T['title'][:6]); pg.wait_for_timeout(300); r['search'] = pg.inner_text('#qList').split('\n')[0]
        if mobile: r['scrollWidth'] = pg.evaluate('document.documentElement.scrollWidth')
        r['errors'] = errs
        print(tag, json.dumps(r, ensure_ascii=False))
        br.close()

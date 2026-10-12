"""Play button and search box checks (desktop + phone).  Run:  KE_BASE=http://localhost:8767/ python dev/test/play_search.py [outdir]"""
import os, sys, json
from playwright.sync_api import sync_playwright
BASE = os.environ.get('KE_BASE', 'http://localhost:8765/'); OUT = sys.argv[1] if len(sys.argv) > 1 else 'dev/test/out'
GO = "async ([v,u])=>{const d=document; d.getElementById('goY').value=v; d.getElementById('goU').value=u; d.getElementById('go').requestSubmit(); await new Promise(r=>setTimeout(r,1500));}"
YEAR = "()=>parseInt(document.getElementById('ph').textContent.replace(/[^\\d-]/g,''),10)"
with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge', headless=True, args=['--enable-gpu', '--use-angle=d3d11'])
    pg = br.new_page(viewport={'width': 1100, 'height': 900}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + 'karahan-era.html'); pg.wait_for_timeout(5000); r = {}
    # play from 20,000 BCE for 3 s
    pg.evaluate(GO, [20000, 'bce']); k0 = pg.evaluate(YEAR)
    pg.evaluate("window.__lt=[]; new PerformanceObserver(l=>l.getEntries().forEach(e=>__lt.push(Math.round(e.duration)))).observe({type:'longtask'})")
    pg.click('#bPlay'); pg.wait_for_timeout(3000); k1 = pg.evaluate(YEAR); rate = pg.inner_text('#pRate')
    pg.click('#bPlay'); pg.wait_for_timeout(500); k2 = pg.evaluate(YEAR); pg.wait_for_timeout(800); k3 = pg.evaluate(YEAR)
    r['play'] = {'from': k0, 'after3s': k1, 'rate_label': rate, 'paused_stays': k2 == k3, 'longtasks': pg.evaluate('__lt'), 'button': pg.inner_text('#bPlay')}
    # play near today stops at today
    pg.evaluate(GO, [2000, 'ce']); pg.click('#bPlay'); pg.wait_for_timeout(16000)
    r['stops_at_today'] = {'year': pg.inner_text('#ph'), 'button': pg.inner_text('#bPlay')}
    # search narrows and jumps
    pg.fill('#q', 'd'); n1 = pg.locator('#qList li[data-i]').count()
    pg.fill('#q', 'dogg'); n2 = pg.locator('#qList li[data-i]').count(); first = pg.locator('#qList li[data-i]').first.inner_text().split('\n')[0]
    pg.keyboard.press('Enter'); pg.wait_for_timeout(1500)
    r['search_event'] = {'d': n1, 'dogg': n2, 'first': first, 'selected': pg.inner_text('#evTitle'), 'year_now': pg.inner_text('#ph'), 'list_hidden': not pg.is_visible('#qList')}
    pg.fill('#q', 'bantu'); items = [li.split('\n')[0] for li in pg.locator('#qList li[data-i]').all_inner_texts()]
    pg.locator('#qList li[data-i]', has_text='expansion').first.click(); pg.wait_for_timeout(1500)
    r['search_bantu'] = {'items': items, 'year_now': pg.inner_text('#ph')}
    pg.fill('#q', 'zzzqx'); r['no_match'] = pg.inner_text('#qList')
    pg.keyboard.press('Escape'); r['esc_closes'] = not pg.is_visible('#qList')
    pg.locator('.stack').screenshot(path=f'{OUT}/play_desktop.png'); r['errors'] = errs
    print('desktop', json.dumps(r, ensure_ascii=False))
    ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True); ph = ctx.new_page()
    ph.goto(BASE + 'karahan-era.html'); ph.wait_for_timeout(5000)
    ph.tap('#q'); ph.keyboard.type('pyramid'); ph.wait_for_timeout(300)
    box = ph.locator('#qList').bounding_box(); ph.screenshot(path=f'{OUT}/search_phone.png')
    ph.locator('#qList li[data-i]').first.tap(); ph.wait_for_timeout(1500)
    print('phone', json.dumps({'list_box': box, 'selected': ph.inner_text('#evTitle'), 'year': ph.inner_text('#ph'), 'scrollWidth': ph.evaluate('document.documentElement.scrollWidth')}, ensure_ascii=False))
    br.close()

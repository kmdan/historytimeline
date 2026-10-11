"""Headless checks for karahan-era.html (uses the installed Microsoft Edge via Playwright).

Needs the local server running:  python -m http.server 8765   (from the project root)
Run:  python dev/test/check.py [outdir]

1. errors: loads the page, collects console errors / failed requests
2. compare: GPU (WebGL2) vs ?cpu renderer, mean pixel difference of the map canvas at several years
3. scrub: drags the timeline through the Ice Age and reports main-thread long tasks + map redraws
4. screenshots: atlas at a few years, light and dark, plus a 375 px phone view
"""
import sys, os, json
from playwright.sync_api import sync_playwright

URL = 'http://localhost:8765/karahan-era.html'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'dev/test/out'
YEARS = [(21000, 'bce'), (4500, 'bce'), (900, 'ce'), (1750, 'ce'), (2020, 'ce')]
os.makedirs(OUT, exist_ok=True)

GOTO = """async ([v,u]) => { const d=document; d.getElementById('goY').value=v; d.getElementById('goU').value=u;
  d.getElementById('go').requestSubmit(); await new Promise(r=>setTimeout(r,2500));
  return d.getElementById('ph').textContent; }"""
MAPPX = """() => { const c=document.getElementById('map'); return Array.from(c.getContext('2d').getImageData(0,0,c.width,c.height).data); }"""

def open_page(browser, query='', **kw):
    ctx = browser.new_context(viewport=kw.get('viewport', {'width': 1100, 'height': 900}), color_scheme=kw.get('scheme', 'dark'))
    page = ctx.new_page()
    errs = []
    page.on('console', lambda m: errs.append(m.text + ' ' + str(m.location.get('url', ''))) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errs.append(str(e)))
    page.on('requestfailed', lambda r: errs.append('failed: ' + r.url))
    page.on('response', lambda r: errs.append(f'{r.status}: {r.url}') if r.status >= 400 else None)
    page.goto(URL + query)
    page.wait_for_timeout(5000)
    return page, errs

def main():
    report = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True, args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        gpu, e1 = open_page(browser)
        report['renderer'] = gpu.evaluate("() => document.getElementById('map').dataset.renderer")
        cpu, e2 = open_page(browser, '?cpu')
        report['renderer_cpu_page'] = cpu.evaluate("() => document.getElementById('map').dataset.renderer")
        diffs = []
        for v, u in YEARS:
            gpu.evaluate(GOTO, [v, u]); cpu.evaluate(GOTO, [v, u])
            a, b = gpu.evaluate(MAPPX), cpu.evaluate(MAPPX)
            n = len(a) // 4
            tot = sum(abs(a[i] - b[i]) for i in range(0, len(a)) if i % 4 != 3)
            off = sum(1 for i in range(0, len(a), 4) if abs(a[i]-b[i]) + abs(a[i+1]-b[i+1]) + abs(a[i+2]-b[i+2]) > 30)
            distinct = len({tuple(a[i:i+3]) for i in range(0, len(a), 997 * 4)})
            diffs.append({'year': f'{v} {u}', 'mean_abs_diff': round(tot / n / 3, 3), 'pct_px_off': round(off / n * 100, 3), 'distinct_colours_sampled': distinct})
        report['compare'] = diffs
        for name, page in (('gpu', gpu), ('cpu', cpu)):
            page.evaluate(GOTO, [30000, 'bce'])
            report['scrub_' + name] = page.evaluate("""async () => {
              window.__lt=[]; new PerformanceObserver(l=>l.getEntries().forEach(e=>__lt.push(Math.round(e.duration)))).observe({type:'longtask'});
              const c=document.getElementById('tl'), b=c.getBoundingClientRect(), y=b.top+b.height*0.6, x0=b.left+b.width*0.5;
              const ev=(t,x)=>c.dispatchEvent(new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,pointerId:1,pointerType:'mouse',isPrimary:true,buttons:1}));
              const ph0=document.getElementById('ph').textContent; let frames=0, run=true; (function f(){ frames++; if(run) requestAnimationFrame(f); })();
              const t0=performance.now(); ev('pointerdown',x0);
              for(let i=1;i<=60;i++){ ev('pointermove',x0-i*4); await new Promise(r=>setTimeout(r,16)); }
              ev('pointerup',x0-240); const dt=performance.now()-t0; run=false; await new Promise(r=>setTimeout(r,500));
              return {from:ph0, to:document.getElementById('ph').textContent, ms_for_60_moves:Math.round(dt), fps:Math.round(frames/dt*1000), longtasks:__lt}; }""")
        for v, u in YEARS:
            gpu.evaluate(GOTO, [v, u])
            gpu.locator('#atlas').screenshot(path=f'{OUT}/dark_{v}{u}.png')
        light, e3 = open_page(browser, scheme='light')
        light.evaluate(GOTO, [18000, 'bce']); light.locator('#atlas').screenshot(path=f'{OUT}/light_18000bce.png')
        phone, e4 = open_page(browser, viewport={'width': 375, 'height': 812})
        report['phone_scrollWidth'] = phone.evaluate('document.documentElement.scrollWidth')
        phone.screenshot(path=f'{OUT}/phone.png', full_page=False)
        report['errors'] = sorted(set(e1 + e2 + e3 + e4))
        browser.close()
    print(json.dumps(report, indent=1))

if __name__ == '__main__':
    main()

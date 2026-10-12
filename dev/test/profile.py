"""CPU profile of a timeline scrub (headless Edge on the real GPU). Prints self time by function.
Run (server on :8765):  python dev/test/profile.py [query]   e.g. query '?cpu'
"""
import os
import sys, json, collections
from playwright.sync_api import sync_playwright

Q = sys.argv[1] if len(sys.argv) > 1 else ''
SCRUB = """async () => { const c=document.getElementById('tl'), b=c.getBoundingClientRect(), y=b.top+b.height*0.6, x0=b.left+b.width*0.5;
  const ev=(t,x)=>c.dispatchEvent(new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,pointerId:1,pointerType:'mouse',isPrimary:true,buttons:1}));
  window.__lt=[]; new PerformanceObserver(l=>l.getEntries().forEach(e=>__lt.push(Math.round(e.duration)))).observe({type:'longtask'});
  const t0=performance.now(); ev('pointerdown',x0);
  for(let i=1;i<=60;i++){ ev('pointermove',x0-i*4); await new Promise(r=>setTimeout(r,16)); }
  ev('pointerup',x0-240); await new Promise(r=>setTimeout(r,300));
  return {ms:Math.round(performance.now()-t0), longtasks:__lt, renderer:document.getElementById('map').dataset.renderer, gl:(()=>{ const g=document.createElement('canvas').getContext('webgl2'); const e=g&&g.getExtension('WEBGL_debug_renderer_info'); return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):'?'; })()}; }"""

with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge', headless=True, args=['--enable-gpu', '--use-angle=d3d11', '--ignore-gpu-blocklist'])
    pg = br.new_page(viewport={'width': 1100, 'height': 900})
    pg.goto(os.environ.get('KE_BASE','http://localhost:8765/')+'karahan-era.html' + Q); pg.wait_for_timeout(6000)
    pg.evaluate("""async () => { const d=document; d.getElementById('goY').value=30000; d.getElementById('goU').value='bce'; d.getElementById('go').requestSubmit(); await new Promise(r=>setTimeout(r,2500)); }""")
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Profiler.enable'); cdp.send('Profiler.setSamplingInterval', {'interval': 200}); cdp.send('Profiler.start')
    res = pg.evaluate(SCRUB)
    prof = cdp.send('Profiler.stop')['profile']
    br.close()

nodes = {n['id']: n for n in prof['nodes']}
dt = collections.Counter()
for sid, d in zip(prof['samples'], prof['timeDeltas']):
    f = nodes[sid]['callFrame']; dt[(f['functionName'] or '(anon)') + ':' + str(f['lineNumber'] + 1)] += d / 1000
print(json.dumps(res))
for k, v in dt.most_common(18): print(f'{v:8.0f} ms  {k}')

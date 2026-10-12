"""Count border-layer dropouts while scrubbing, with simulated network latency on atlas/ files.
Run (server on :8765):  python dev/test/flicker.py [page] [latency_ms]
Prints how many animation frames showed 'Loading cultures…' and how many showed fewer than half the usual borders.
"""
import sys, json
from playwright.sync_api import sync_playwright
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'karahan-era.html'
LAT = int(sys.argv[2]) if len(sys.argv) > 2 else 300
with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge', headless=True, args=['--enable-gpu', '--use-angle=d3d11'])
    pg = br.new_page(viewport={'width': 1100, 'height': 900})
    def slow(route):
        pg.wait_for_timeout(LAT); route.continue_()
    pg.route('**/atlas/**', slow)
    pg.goto('http://localhost:8765/' + PAGE); pg.wait_for_timeout(6000)
    pg.evaluate("async()=>{const d=document; d.getElementById('goY').value=600; d.getElementById('goU').value='ce'; d.getElementById('go').requestSubmit(); await new Promise(r=>setTimeout(r,4000));}")
    res = pg.evaluate("""async()=>{
      const c=document.getElementById('tl'), b=c.getBoundingClientRect(), y=b.top+b.height*0.6, x0=b.left+b.width*0.85;
      const ev=(t,x)=>c.dispatchEvent(new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,pointerId:1,pointerType:'mouse',isPrimary:true,buttons:1}));
      const info=()=>document.getElementById('mapinfo').innerText;
      let frames=0, loading=0; const samples=[];
      ev('pointerdown',x0);
      for(let i=1;i<=90;i++){ ev('pointermove',x0-i*6); await new Promise(r=>requestAnimationFrame(()=>setTimeout(r,30)));
        frames++; const t=info(); if(/Loading cultures/.test(t)) loading++; samples.push(document.getElementById('ph').textContent); }
      ev('pointerup',x0-540);
      return {frames, loading, from:samples[0], to:samples[samples.length-1]}; }""")
    print(PAGE, f'latency {LAT} ms', json.dumps(res)); pg.unroute_all(behavior='ignoreErrors')
    br.close()

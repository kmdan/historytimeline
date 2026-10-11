"""Save GPU, CPU and difference images of the map canvas at one year.  python dev/test/diff.py 4500 bce outdir"""
import sys, numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
v, u, out = sys.argv[1], sys.argv[2], sys.argv[3]
GO = "async ([v,u])=>{const d=document; d.getElementById('goY').value=v; d.getElementById('goU').value=u; d.getElementById('go').requestSubmit(); await new Promise(r=>setTimeout(r,3000)); const c=d.getElementById('map'); return [c.width,c.height,Array.from(c.getContext('2d').getImageData(0,0,c.width,c.height).data)];}"
with sync_playwright() as p:
    br = p.chromium.launch(channel='msedge', headless=True, args=['--enable-gpu', '--use-angle=d3d11'])
    imgs = []
    for q in sys.argv[4:6] if len(sys.argv)>5 else ('', '?cpu'):
        pg = br.new_page(viewport={'width': 1100, 'height': 900}); pg.goto('http://localhost:8765/' + (q if q.endswith('html') or '.html?' in q else 'karahan-era.html'+q)); pg.wait_for_timeout(6000)
        w, h, d = pg.evaluate(GO, [int(v), u]); imgs.append(np.array(d, np.uint8).reshape(h, w, 4)[..., :3])
    br.close()
a, b = (i.astype(int) for i in imgs)
dm = (np.abs(a - b).sum(2) > 30)
Image.fromarray(imgs[0]).save(f'{out}/gpu.png'); Image.fromarray(imgs[1]).save(f'{out}/cpu.png')
Image.fromarray(np.where(dm[..., None], [255, 0, 0], imgs[0] // 3).astype(np.uint8)).save(f'{out}/diff.png')
print('pct off', dm.mean() * 100)

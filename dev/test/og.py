"""Social preview image atlas/og.png (1200x630): the atlas at a chosen year, dark theme. Local server on 8765.
Run:  python dev/test/og.py [signed_year]
"""
import os
import sys, io
from playwright.sync_api import sync_playwright
from PIL import Image

Y = sys.argv[1] if len(sys.argv) > 1 else '-18000'
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True, args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    pg = b.new_page(viewport={'width': 1300, 'height': 1000}, device_scale_factor=2, color_scheme='dark')
    pg.goto(os.environ.get('KE_BASE','http://localhost:8765/')+f'karahan-era.html?y={Y}'); pg.wait_for_timeout(9000)
    pg.add_style_tag(content='#mapinfo,.maptools{visibility:hidden}')
    png = pg.locator('#map').screenshot()
    b.close()
im = Image.open(io.BytesIO(png)).convert('RGB')
w, h = im.size   # map is wider than 1200:630, so trim the sides (Pacific) a little
tw = min(w, round(h * 1200 / 630)); left = (w - tw) // 2
im.crop((left, 0, left + tw, h)).resize((1200, 630), Image.LANCZOS).save('atlas/og.png', optimize=True)
print('atlas/og.png', im.size)

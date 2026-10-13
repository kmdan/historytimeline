import sys, pathlib
from playwright.sync_api import sync_playwright
d = pathlib.Path(sys.argv[1]).resolve()
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True)
    pg = b.new_page(viewport={'width': 1700, 'height': 1000})
    n=sys.argv[2] if len(sys.argv)>2 else 'page'
    pg.goto(d.joinpath(n+'.html').as_uri()); pg.wait_for_function("document.title==='done'", timeout=120000)
    pg.locator('#c').screenshot(path=str(d / (n+'.png')))
    b.close()
print('saved', d / 'europe.png')

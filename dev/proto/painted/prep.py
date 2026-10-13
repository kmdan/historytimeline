"""Prototype: painted gouache map of Europe at one year from the real atlas data.
Writes base.png (painted ground + water, per pixel), meta.png (type, clump, dist/elev), clim.png (cold, dry),
rivers.json (pixel polylines) and page.html (overlays: brush dabs, water chop, rivers, symbols).
Run from the repo root:  .venv/Scripts/python -I <this> <outdir> [year]
"""
import sys, json, base64, io, math
import numpy as np, netCDF4 as nc
from PIL import Image
from scipy import ndimage as nd

OUT = sys.argv[1]; YEAR = int(sys.argv[2]) if len(sys.argv) > 2 else -6000
BP = 1950 - YEAR
import os
LON0, LON1, LAT0, LAT1, S = [float(v) for v in os.environ.get('BBOX', '-11,41,34,61,5').split(',')]          # S = render px per 1/6 deg cell
W, H = int((LON1 - LON0) * 6 * S), int((LAT1 - LAT0) * 6 * S)
rng = np.random.default_rng(4)

t = np.array(Image.open('atlas/terrain.png')).astype(np.int16); R, G = t[..., 0], t[..., 1]
slw = np.array(Image.open('atlas/slw.png')).astype(int)
l = slw[..., 2] > 127
for ch in (0, 1):
    l ^= (slw[..., ch] > 0) & (BP <= (slw[..., ch] - 1) / 254 * 26000)
land = l & (R != 135)
farmc = np.array(Image.open('atlas/ice.png'))[..., 2].astype(int)

X, Y = np.meshgrid(np.arange(W), np.arange(H))
lon = LON0 + (X + .5) / (6 * S); lat = LAT1 - (Y + .5) / (6 * S)
cx, cy = (lon + 180) * 6 - .5, (90 - lat) * 6 - .5
samp = lambda a, o=1, xx=None, yy=None: nd.map_coordinates(a, [cy if yy is None else yy, cx if xx is None else xx], order=o, mode='nearest')

def noise(scale, seed):                       # smooth value noise, ~scale px features, 0..1
    r = np.random.default_rng(seed); g = r.random((H // scale + 4, W // scale + 4))
    z = nd.zoom(g, scale, order=3)[:H, :W]; z -= z.min(); return z / z.max()
fbm = lambda s, seed: .6 * noise(s, seed) + .3 * noise(max(2, s // 3), seed + 1) + .1 * noise(max(2, s // 8), seed + 2)
sstep = lambda a, b, v: (lambda q: q * q * (3 - 2 * q))(np.clip((v - a) / (b - a), 0, 1))

# land/sea with a natural coast at render resolution
Ls = samp(nd.gaussian_filter(land.astype(np.float32), .85)) + (fbm(12, 1) - .5) * .28
isL = Ls > .5
# ETOPO 2022 (60 arc-sec) at render resolution: fine relief, true depth, coast detail inside coastal cells
EP = 'dev/raw/etopo/etopo60_i16.npy'; E = None
if os.path.exists(EP):
    EA = np.load(EP, mmap_mode='r')
    y0, y1 = int((90 - LAT1) * 60) - 4, int((90 - LAT0) * 60) + 4; x0, x1 = int((LON0 + 180) * 60) - 4, int((LON1 + 180) * 60) + 4
    sub = np.asarray(EA[y0:y1, x0:x1], np.float32)
    E = nd.map_coordinates(sub, [(90 - lat) * 60 - .5 - y0, (lon + 180) * 60 - .5 - x0], order=3, mode='nearest')
    SL = float(os.environ.get('SEALEVEL', '-12'))                     # global mean sea level for the year (m), estimate
    isL = (Ls > .85) | ((Ls > .15) & (E > SL + (fbm(6, 3) - .5) * 4))
lab, nlab = nd.label(~isL); Rn0 = samp(R, 0)
seaid = np.unique(lab[(~isL) & (Rn0 <= 130)]); lake = ~isL & ~np.isin(lab, seaid)   # water bodies with no sea-depth code are lakes
sea = ~isL & ~lake

# vegetation: Beyer snapshot (0.5 deg), nearest class with jittered lookup
years = [-40050,-38050,-36050,-34050,-32050,-30050,-28050,-26050,-24050,-22050,-20050,-19050,-18050,-17050,-16050,-15050,-14050,-13050,-12050,-11050,-10050,-9050,-8050,-7050,-6050,-5050,-4050,-3050,-2050,-1050,-50,950,1950]
si = int(np.argmin([abs(y - YEAR) for y in years]))
bimg = np.array(Image.open('atlas/biome_beyer.png'))
bio = bimg[(si // 3) * 360:(si // 3 + 1) * 360, :, si % 3]
jx, jy = (noise(9, 5) - .5) * 1.4, (noise(9, 6) - .5) * 1.4
cls = nd.map_coordinates(bio, [(90 - lat) * 2 - .5 + jy, (lon + 180) * 2 - .5 + jx], order=0, mode='nearest')

# climate tints from Beyer BIO1 / BIO12 at the same snapshot
d = nc.Dataset('dev/raw/beyer/LateQuaternary_Environment.nc'); d.set_auto_mask(False)
ti = int(np.argmin(np.abs(d['time'][:] + 1950 - years[si]))); la = d['latitude'][:]; lo = d['longitude'][:]
def field(name):
    a = d[name][ti].astype(np.float32); m = ~np.isfinite(a) | (a < -1e3)
    if m.any():
        _, (iy, ix) = nd.distance_transform_edt(m, return_indices=True); a = a[iy, ix]
    return nd.map_coordinates(a, [(lat - la[0]) / (la[1] - la[0]), (lon - lo[0]) / (lo[1] - lo[0])], order=1, mode='nearest')
bio1, bio12 = field('BIO1'), field('BIO12')
cold = np.clip((12 - bio1) / 18, 0, 1); dry = np.clip(1 - bio12 / 800, 0, 1)

# farming (ice.png B = farming start code) -> share grows over 2500 years, scaled by biome suitability
FSUIT = np.array([0, .18, .32, .05, .5, .62, .68, .22, .02, 0, 0])
fc = samp(farmc, 0); fy = np.where(fc <= 150, -10000 + (fc - 1) / 149 * 10000, (fc - 150) / 104 * 2000)
ffrac = np.where(fc > 0, np.clip((YEAR - fy) / 2500, 0, 1), 0) * FSUIT[np.clip(cls, 0, 10)]
farm = isL & (cls != 9) & (fbm(14, 9) < ffrac * .95)

# types: 0 sea 1 lake 2 ice 3 farm 4 rain 5 savanna 6 desert 7 steppe 8 med 9 temp 10 taiga 11 tundra 12 mstep
CM = np.array([9, 4, 5, 6, 7, 8, 9, 10, 11, 2, 12])
typ = np.where(sea, 0, np.where(lake, 1, CM[np.clip(cls, 0, 10)]))
typ = np.where(farm, 3, typ).astype(np.uint8)

hx = lambda c: np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
C3 = lambda c: np.broadcast_to(hx(c) if isinstance(c, str) else np.array(c, np.float32), (H, W, 3))
mixc = lambda a, b, tt: a + (b - a) * tt[..., None]
# darker, earthier ground
PAL = {4: ('#34482a', '#3f5531'), 5: ('#8d8452', '#99905d'), 6: ('#a99070', '#b79e7c'), 7: ('#958d5f', '#a1986a'), 8: ('#817a57', '#8d8562'),
       9: ('#66714a', '#717c52'), 10: ('#56634c', '#606d55'), 11: ('#7f8068', '#8c8c74'), 12: ('#938859', '#9f9363'), 2: ('#d8e0e4', '#e6ecef')}
col = np.zeros((H, W, 3), np.float32)
nv = fbm(18, 11)
for k, (a, b) in PAL.items():
    m = typ == k; col[m] = mixc(C3(a), C3(b), nv)[m]
col = mixc(col, col * np.array([1.05, .97, .85], np.float32), dry * .35)                 # drier = warmer
col = mixc(col, col * np.array([.92, .97, 1.04], np.float32), cold * .35)                # colder = cooler
# vegetation as an embossed canopy texture: blobby noise = crowns, lit from the northwest
clump = sstep(.3, .62, fbm(26, 13))
DEN = np.zeros(13, np.float32); DEN[[4, 9, 10]] = [1, .8, .82]; DEN[8] = .38; DEN[5] = .18; DEN[7] = .05; DEN[11] = .12; DEN[12] = .06; DEN[3] = .04
den = DEN[typ] * np.where(np.isin(typ, [9, 10]), .45 + .55 * clump, 1)
def canopy(scale, seed):
    n = noise(scale, seed); e = n - np.roll(np.roll(n, 1, 0), 1, 1)          # emboss: + on NW-facing sides
    return n, e
n1, e1 = canopy(3, 51); n2, e2 = canopy(2, 52)
crowns = np.clip((n1 - (1 - den * .9)) * 6, 0, 1)                                     # crown cover per pixel
CD = {4: ('#1c2c18', '#4e6d39'), 9: ('#26331d', '#5f7243'), 10: ('#1f2b22', '#4d5f4a'), 8: ('#3d4130', '#7c7d5b'), 5: ('#3a3f25', '#6f7344'),
      7: ('#4a4a2e', '#7a7650'), 11: ('#4c4c38', '#77775c'), 12: ('#4a4a2e', '#7a7650'), 3: ('#2f3a24', '#5d6b41')}
can = np.zeros_like(col)
for k, (dk, lt) in CD.items():
    m = typ == k
    lit = np.clip(.45 + e1 * 9 + e2 * 4, 0, 1)
    can[m] = mixc(C3(dk), C3(lt), lit)[m]
can = mixc(can, can * np.array([.9, .98, 1.08], np.float32), cold * .4)
can = mixc(can, can * np.array([1.08, 1.0, .82], np.float32), dry * .4)
gap = col * .62                                                                       # shadowed floor between crowns
veg = np.where(den[..., None] > 0, mixc(gap, can, crowns), col)
col = mixc(col, veg, np.clip(den * 1.6, 0, 1))
# fields: muted patchwork, irregular orientation
fa = .35 + (noise(90, 41) - .5) * 1.6; ca, sa = np.cos(fa), np.sin(fa)
u = X * ca + Y * sa + noise(20, 42) * 6; v = -X * sa + Y * ca + noise(20, 43) * 6
fu, fv = (u / 7) % 1, (v / 4.5) % 1
FC = np.array([hx(c) for c in ['#a08f55', '#7f8550', '#8a7350', '#968f5c', '#a59660']])
fid = ((np.floor(u / 7).astype(np.int64) * 73856093) ^ (np.floor(v / 4.5).astype(np.int64) * 19349663)) % 5
fcol = FC[fid] * (1 + (noise(2, 44)[..., None] - .5) * .12)
fcol = np.where(((fu < .12) | (fv < .16))[..., None], np.array([62, 72, 45], np.float32), fcol)
col[farm] = mixc(col, fcol, np.full((H, W), .85, np.float32))[farm]
# water: deep and dark, shelves greener, restrained coastal lines
dW = nd.distance_transform_edt(~isL)
Dc = np.where(R < 140, R, np.nan).astype(np.float32); _, (iy, ix) = nd.distance_transform_edt(np.isnan(Dc), return_indices=True)
d01 = np.clip(samp(nd.gaussian_filter(Dc[iy, ix], 1.2)) / 139, 0, 1)
ts = .25 * (1 - np.exp(-dW / 7)) + .75 * d01 ** .6
seac = mixc(mixc(C3('#3d6571'), C3('#29495a'), np.clip(ts * 2, 0, 1) ** .7), C3('#152c3e'), np.clip(ts * 2 - 1, 0, 1))
lakec = mixc(C3('#46695e'), C3('#1d3a40'), 1 - np.exp(-dW / 4))
wat = sea | lake
col[sea] = seac[sea]; col[lake] = lakec[lake]
col[wat] *= (1 + (fbm(40, 21) - .5) * .16)[wat][:, None]
glow = np.clip(1 - np.hypot(X / W - .25, Y / H - .15) * 1.4, 0, 1) ** 2                 # soft sky reflection from the northwest
col[wat] = mixc(col, C3('#8fa9a8'), glow * .22)[wat]
brk = np.where(noise(8, 22) > .4, 1, .1)
wl = np.where((dW > 1.6) & (dW < 13), np.maximum(0, np.cos(dW / 3.2 * 2 * np.pi)) ** 6 * (1 - dW / 13) * brk, 0)
col[wat] = mixc(col, C3('#a9c0bd'), wl * .22)[wat]
fo = np.where(dW < 1.3, (1 - dW / 1.3) * .5 * np.where(noise(3, 23) > .35, 1, .3), 0)
col[wat] = mixc(col, C3('#cfd8d2'), fo)[wat]
col[wat] = mixc(col, col * .7, np.clip(1 - dW / 3, 0, 1) * .25 * (1 - fo))[wat]           # thin dark line just off the shore
refl = np.zeros((H, W), np.float32)
for k in range(1, 6):
    sh = np.zeros_like(isL); sh[k:] = isL[:-k]; refl = np.maximum(refl, np.where(sh, (1 - k / 6) * .45, 0))
col[lake] = mixc(col, C3('#14241c'), refl)[lake]
dS = nd.distance_transform_edt(~sea); dLk = nd.distance_transform_edt(~lake)
bf = np.where(isL & (dS < 1.8), (1 - dS / 1.8) * .55 * np.where(lat < 52, 1, .4), 0)
col = mixc(col, C3('#b9a77c'), bf)
# relief: Natural Earth shading + ridged detail in mountains, rock and snow by elevation
Rs = samp(R, 1); el = np.where(isL, Rs, 0) + (noise(5, 31) - .5) * 10
mtn = sstep(165, 205, el) * isL
rid = lambda sc, sd: 1 - np.abs(2 * noise(sc, sd) - 1)
rd = .6 * rid(7, 61) + .4 * rid(3, 62)
rdx = rd - np.roll(np.roll(rd, 1, 0), 1, 1)
col = mixc(col, C3('#7d7465'), sstep(188, 210, el) * .6 * isL)
col = mixc(col, C3('#e9ecef'), sstep(206, 220, el + rd * 8) * .85 * isL)
shd = (samp(G, 1) - 127) / 128 * 1.15 / np.sqrt(S / 5) + rdx * mtn * 2.0 + (n1 - np.roll(np.roll(n1, 2, 0), 2, 1)) * .25 * isL
shd = np.where(isL, shd, 0)
col = np.where((shd < 0)[..., None], mixc(col, C3('#1f2430'), np.minimum(.5, -shd * 1.05)),
               mixc(col, C3('#fff0d0'), np.minimum(.32, shd * .8)))
# grade: gentle S-curve, slight desaturation, warm highlights, vignette, canvas grain
lum = col.mean(-1, keepdims=True); col = lum + (col - lum) * .85
col = 255 * (lambda q: q * q * (3 - 2 * q))(np.clip(col / 255, 0, 1)) * .35 + col * .65
vig = 1 - .3 * np.clip(np.hypot(X / W - .5, Y / H - .5) * 1.5, 0, 1) ** 2.2
col *= vig[..., None]
canvas = (noise(2, 71) - .5) * .05 + ((X + Y * 3) % 4 < 1) * .012
col *= (1 + canvas + (rng.random((H, W)) - .5) * .03)[..., None]
if os.environ.get('STYLE') == 'shelton':
    # Hal Shelton-like natural colour: bright land-cover colours cross-blended, light seas, crisp warm relief
    SP = {4: '#4f8a3c', 5: '#bdb86a', 6: '#e6d3a0', 7: '#c9c47e', 8: '#a9b267', 9: '#86ad55', 10: '#5f8f52', 11: '#a8ad8c', 12: '#c2bb7c', 2: '#f4f6f8'}
    col = np.zeros((H, W, 3), np.float32)
    for k, c in SP.items(): col[typ == k] = hx(c)
    col[farm] = hx('#b9be6e')
    lw = isL.astype(np.float32); bl = lambda a, sg: nd.gaussian_filter(a, (sg, sg, 0)) / np.maximum(nd.gaussian_filter(lw, sg), 1e-3)[..., None]
    col = np.where(isL[..., None], bl(col * lw[..., None], 3.5 * S / 5), col)                       # cross-blend biome colours
    col = mixc(col, col * np.array([.72, .82, .68], np.float32), np.clip(den * (.55 + .45 * clump), 0, 1) * .5 * np.isin(typ, [4, 9, 10]))  # tree cover darker
    col = mixc(col, col * np.array([1.06, 1.0, .86], np.float32), dry * .3)
    col *= (1 + (fbm(10, 81) - .5) * .1 + (noise(2, 82) - .5) * .05)[..., None]
    fcl = np.where(((fu < .12) | (fv < .16)), .9, 1.0) * (1 + (fid - 2) * .03)                       # faint field pattern
    col[farm] *= fcl[farm][:, None]
    # high ground: warm rock, then snow
    col = mixc(col, C3('#b9a98a'), sstep(178, 205, el) * .7 * isL)
    col = mixc(col, C3('#fbfbfc'), sstep(206, 218, el + rd * 8) * .95 * isL)
    # seas: pale near the coast and over shelves, mid blue offshore
    ts2 = .35 * (1 - np.exp(-dW / 10)) + .65 * d01 ** .6
    sc2 = mixc(mixc(C3('#d6ecf5'), C3('#9cc9e6'), np.clip(ts2 * 2, 0, 1)), C3('#6aa4d4'), np.clip(ts2 * 2 - 1, 0, 1))
    lk2 = mixc(C3('#b9dcec'), C3('#6fa9d4'), 1 - np.exp(-dW / 4))
    col[sea] = sc2[sea]; col[lake] = lk2[lake]
    col[wat] *= (1 + (fbm(40, 21) - .5) * .05)[wat][:, None]
    col[wat] = mixc(col, col * .82, np.clip(1 - dW / 2.2, 0, 1) * .5)[wat]                          # crisp dark shore line
    if E is not None:
        # true depth for seas (m): pale shallows, shelf, deep
        dep = np.clip(-(E - SL), 0, None)
        tsE = np.clip(np.log1p(dep / 15) / np.log1p(4000 / 15), 0, 1)
        scE = mixc(mixc(C3('#bfe0ee'), C3('#93c3e3'), np.clip(tsE * 1.7, 0, 1)), C3('#5f9cd0'), np.clip(tsE * 1.7 - .7, 0, 1) / .3 * .3 + np.clip(tsE - .6, 0, 1) * 1.2)
        col[sea] = scE[sea]
        col[wat] = mixc(col, col * .8, np.clip(1 - dW / 2.2, 0, 1) * .45)[wat]
        # snow line by true elevation, lower toward the north
        snowz = 3100 - (lat - 42) * 95
        col = mixc(col, C3('#c3b293'), sstep(snowz - 1400, snowz - 500, E) * .6 * isL)
        col = mixc(col, C3('#fbfbfc'), sstep(snowz - 150, snowz + 250, E + (noise(3, 91) - .5) * 300) * .95 * isL)
    # relief: Natural Earth shading + ridges, green-grey shadows, warm light
    inner = nd.binary_erosion(R >= 140, iterations=1); _, (gy_, gx_) = nd.distance_transform_edt(~inner, return_indices=True)
    Gf = G[gy_, gx_].astype(np.float32)                                                      # coastal ring + sea filled from inland
    Gl = Gf - nd.gaussian_filter(Gf, 5) + 127                                                # high-pass: slopes only, no lowland tint                                      # no sea values leaking into coastal shading
    shd2 = (samp(Gl, 1) - 127) / 128 * 1.35 / np.sqrt(S / 5) + rdx * mtn * 2.6
    shd2 = np.where(isL, shd2, 0)
    if E is not None:
        pxm = 111320 / (6 * S)                                              # metres per render pixel (north-south)
        VE = float(os.environ.get('VEXAG', '2.2'))
        Ez = nd.gaussian_filter(E, .6) * VE
        gy_, gx_ = np.gradient(Ez, pxm, pxm); gx_ = gx_ / np.cos(np.radians(lat))
        def hs(az, alt=45):
            a_, b_ = np.radians(az), np.radians(alt)
            lx, ly, lz = np.sin(a_) * np.cos(b_), -np.cos(a_) * np.cos(b_), np.sin(b_)    # light vector (x east, y south-down)
            n = np.sqrt(gx_ ** 2 + gy_ ** 2 + 1)
            return (-gx_ * lx - gy_ * ly + lz) / n
        H3 = .55 * hs(315) + .25 * hs(270) + .2 * hs(350)
        flat = np.sin(np.radians(45))
        ao = np.clip((E - nd.gaussian_filter(E, 10)) / 500, -1, .5)       # valleys (negative) darker, ridges lighter
        shd2 = np.where(isL, (H3 - flat) * 1.6 + ao * .35, 0)
        sfl = np.where(sea, (H3 - flat) * .5, 0)                             # faint seafloor relief
        col[sea] = mixc(col, C3('#3c6f9c'), np.clip(-sfl, 0, .25))[sea]
        col[sea] = mixc(col, C3('#ffffff'), np.clip(sfl, 0, .15))[sea]
    col = np.where((shd2 < 0)[..., None], mixc(col, C3('#2e3f30'), np.minimum(.6, -shd2 * 1.2)), mixc(col, C3('#fffbe6'), np.minimum(.45, shd2 * 1.1)))
Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).save(f'{OUT}/base.png')
meta = np.stack([typ, (clump * 255).astype(np.uint8), np.where(isL, np.clip(Rs, 0, 255), np.clip(dW * 10, 0, 255)).astype(np.uint8)], -1)
Image.fromarray(meta.astype(np.uint8)).save(f'{OUT}/meta.png')
Image.fromarray(np.stack([cold * 255, dry * 255, np.zeros_like(cold)], -1).astype(np.uint8)).save(f'{OUT}/clim.png')
# rivers (today's courses) in px
rv = []
for pl in json.load(open('atlas/rivers.json')):
    pts = [((pl[i] / 20 - LON0) * 6 * S, (LAT1 - pl[i + 1] / 20) * 6 * S) for i in range(0, len(pl) - 1, 2)]
    pts = [p for p in pts if -20 < p[0] < W + 20 and -20 < p[1] < H + 20]
    if len(pts) < 2: continue
    L = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    if L < 4: continue
    rv.append({'p': [[round(a, 1), round(b, 1)] for a, b in pts], 'w': round(.55 + min(.9, L / 300) + max(0, S - 5) * .08, 2)})
b64 = lambda f: 'data:image/png;base64,' + base64.b64encode(open(f'{OUT}/{f}', 'rb').read()).decode()
tpl = open(sys.argv[0].replace('prep.py', 'page.tpl.html'), encoding='utf-8').read()
html = (tpl.replace('%BASE%', b64('base.png')).replace('%META%', b64('meta.png')).replace('%CLIM%', b64('clim.png'))
        .replace('%RIV%', json.dumps(rv)).replace('%STYLE%', os.environ.get('STYLE', 'dark')).replace('%LON0%', str(LON0)).replace('%LAT1%', str(LAT1)).replace('%PPD%', str(6 * S)).replace('%W%', str(W)).replace('%H%', str(H)).replace('%YEAR%', f'{-YEAR:,} BCE' if YEAR < 0 else f'{YEAR} CE'))
open(f"{OUT}/{os.environ.get('NAME', 'page')}.html", 'w', encoding='utf-8').write(html)
print('ok', W, H, 'snapshot', years[si], 'rivers', len(rv), 'farm px', int(farm.sum()))

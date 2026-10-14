"""Build routes.json (trade routes + voyages). Paths may use hub names (strings) or [lon,lat];
longitudes may run past 180 for continuity and are split at the dateline automatically."""
import json, sys
W = 'https://en.wikipedia.org/wiki/'

H = {  # hubs: name -> (lon, lat)
 # Silk Road
 "Chang'an (Xi'an)": (108.94, 34.34), 'Lanzhou': (103.83, 36.06), 'Wuwei': (102.64, 37.93), 'Zhangye': (100.45, 38.93),
 'Jiuquan': (98.50, 39.73), 'Dunhuang': (94.66, 40.14), 'Hami': (93.51, 42.83), 'Turpan': (89.19, 42.95),
 'Karasahr': (86.57, 42.06), 'Kucha': (82.96, 41.72), 'Aksu': (80.26, 41.17), 'Kashgar': (75.99, 39.47),
 'Miran': (88.97, 39.22), 'Charklik': (88.17, 39.02), 'Cherchen': (85.53, 38.13), 'Niya': (82.69, 37.07),
 'Keriya': (81.67, 36.86), 'Khotan': (79.92, 37.11), 'Yarkand': (77.24, 38.42),
 'Osh': (72.80, 40.53), 'Khujand': (69.62, 40.28), 'Samarkand': (66.96, 39.65), 'Bukhara': (64.42, 39.77),
 'Merv': (61.84, 37.66), 'Sarakhs': (61.16, 36.53), 'Nishapur': (58.80, 36.21), 'Rey': (51.43, 35.59),
 'Hamadan (Ecbatana)': (48.51, 34.80), 'Ctesiphon': (44.58, 33.09), 'Dura-Europos': (40.73, 34.75),
 'Palmyra': (38.27, 34.55), 'Antioch': (36.16, 36.20), 'Tarsus': (34.90, 36.92), 'Konya (Iconium)': (32.48, 37.87),
 'Nicaea': (29.72, 40.43), 'Constantinople': (28.98, 41.01), 'Tabriz': (46.29, 38.08), 'Erzurum': (41.27, 39.91),
 'Sivas': (37.02, 39.75), 'Ankara': (32.86, 39.93),
 # Indian Ocean
 'Guangzhou': (113.26, 23.13), 'Quanzhou': (118.59, 24.91), 'Malacca': (102.25, 2.19), 'Calicut': (75.78, 11.25),
 'Quilon (Kollam)': (76.60, 8.89), 'Aden': (45.03, 12.79), 'Aydhab': (35.60, 22.33), 'Suez (Qulzum)': (32.55, 29.95),
 'Cairo': (31.24, 30.04), 'Alexandria': (29.92, 31.20), 'Galle': (80.22, 6.03), 'Hormuz': (56.46, 27.10),
 'Mogadishu': (45.34, 2.04), 'Malindi': (40.12, -3.22), 'Mombasa': (39.67, -4.06), 'Zanzibar': (39.19, -6.16),
 'Kilwa': (39.51, -8.96), 'Mozambique Island': (40.73, -15.03), 'Sofala': (34.74, -20.33),
 # Incense
 'Qana': (48.40, 13.99), 'Shabwa': (47.01, 15.37), 'Timna': (45.72, 15.05), "Ma'rib": (45.33, 15.42),
 'Najran': (44.13, 17.49), 'Mecca': (39.83, 21.42), 'Yathrib (Medina)': (39.61, 24.47), 'Dedan (al-Ula)': (37.92, 26.62),
 'Hegra': (37.95, 26.79), 'Tayma': (38.55, 27.63), 'Petra': (35.44, 30.33), 'Gaza': (34.46, 31.50),
 'Khor Rori (Sumhuram)': (54.43, 17.04),
 # Amber
 'Sambia amber coast': (20.10, 54.90), 'Gdańsk': (18.65, 54.35), 'Biskupin': (17.75, 52.79), 'Kalisz': (18.09, 51.76),
 'Wrocław': (17.04, 51.11), 'Kłodzko': (16.66, 50.44), 'Brno': (16.61, 49.20), 'Carnuntum': (16.86, 48.11),
 'Scarbantia (Sopron)': (16.59, 47.68), 'Savaria (Szombathely)': (16.62, 47.23), 'Poetovio (Ptuj)': (15.87, 46.42),
 'Celeia (Celje)': (15.27, 46.23), 'Emona (Ljubljana)': (14.51, 46.05), 'Aquileia': (13.37, 45.77),
 # Tin
 'Ictis (St Michael\'s Mount?)': (-5.48, 50.12), 'Corbilo (Loire mouth)': (-2.20, 47.28), 'Nantes': (-1.55, 47.22),
 'Tours': (0.69, 47.39), 'Roanne': (4.07, 46.04), 'Lugdunum (Lyon)': (4.83, 45.76), 'Massalia': (5.37, 43.30),
 'Arles': (4.63, 43.68),
 # Sahara
 'Fez': (-5.00, 34.03), 'Sijilmasa': (-4.27, 31.28), 'Taghaza': (-4.97, 23.62), 'Araouane': (-3.53, 18.90),
 'Oualata': (-7.03, 17.30), 'Timbuktu': (-3.00, 16.77), 'Gao': (-0.04, 16.27), 'Kano': (8.52, 12.00),
 'Agadez': (7.99, 16.97), 'Ghat': (10.17, 24.96), 'Ghadames': (9.50, 30.13), 'Tripoli': (13.18, 32.89),
 'Tlemcen': (-1.32, 34.88), 'Tunis': (10.17, 36.81),
 # Royal Road
 'Sardis': (28.04, 38.49), 'Gordion': (31.99, 39.65), 'Ancyra': (32.86, 39.93), 'Kanesh (Kültepe)': (35.63, 38.85),
 'Melitene': (38.31, 38.35), 'Amida': (40.23, 37.91), 'Nisibis': (41.22, 37.07), 'Nineveh': (43.15, 36.36),
 'Arbela': (44.01, 36.19), 'Arrapha': (44.39, 35.47), 'Susa': (48.26, 32.19),
 # Rome
 'Rome': (12.48, 41.89), 'Terracina': (13.25, 41.29), 'Capua': (14.25, 41.08), 'Beneventum': (14.78, 41.13),
 'Venusia': (15.81, 40.96), 'Tarentum': (17.24, 40.47), 'Brundisium': (17.94, 40.64), 'Dyrrachium': (19.45, 41.32),
 'Lychnidos (Ohrid)': (20.80, 41.12), 'Heraclea Lyncestis': (21.34, 41.01), 'Edessa': (22.05, 40.80),
 'Pella': (22.52, 40.76), 'Thessalonica': (22.94, 40.64), 'Amphipolis': (23.85, 40.82), 'Philippi': (24.29, 41.01),
 'Traianopolis': (25.87, 40.93), 'Kypsela': (26.40, 40.92), 'Perinthus': (27.96, 40.98),
 # Grand Canal
 'Hangzhou': (120.16, 30.27), 'Jiaxing': (120.75, 30.75), 'Suzhou': (120.62, 31.30), 'Wuxi': (120.30, 31.57),
 'Changzhou': (119.97, 31.81), 'Zhenjiang': (119.45, 32.20), 'Yangzhou': (119.42, 32.39), 'Gaoyou': (119.45, 32.78),
 "Huai'an": (119.02, 33.60), 'Suqian': (118.28, 33.96), 'Weishan': (117.13, 34.80), 'Jining': (116.59, 35.41),
 'Liaocheng': (115.98, 36.46), 'Linqing': (115.70, 36.84), 'Dezhou': (116.36, 37.44), 'Cangzhou': (116.84, 38.30),
 'Tianjin': (117.20, 39.13), 'Tongzhou': (116.66, 39.90), 'Beijing': (116.40, 39.90),
 # Tea Horse
 "Ya'an": (103.00, 29.98), 'Luding': (102.23, 29.91), 'Kangding (Dartsedo)': (101.96, 30.05), 'Litang': (100.27, 30.00),
 'Batang': (99.11, 30.00), 'Markam': (98.59, 29.68), 'Zogang': (97.84, 29.67), 'Baxoi': (96.92, 30.05),
 'Pomê': (95.77, 29.86), 'Nyingchi': (94.36, 29.65), 'Gongbo\'gyamda': (93.25, 29.89), 'Lhasa': (91.13, 29.65),
 "Pu'er": (100.97, 22.79), 'Dali': (100.23, 25.60), 'Lijiang': (100.23, 26.87), 'Shangri-La (Gyalthang)': (99.70, 27.83),
 'Deqin': (98.91, 28.48),
 # Varangian / Hansa
 'Birka': (17.54, 59.33), 'Neva mouth': (30.20, 59.95), 'Staraya Ladoga': (32.30, 60.00), 'Novgorod': (31.27, 58.52),
 'Lake Ilmen': (31.30, 58.25), 'Velikiye Luki': (30.53, 56.34), 'Gnezdovo (Smolensk)': (31.88, 54.78),
 'Lyubech': (30.65, 51.71), 'Kiev': (30.52, 50.45), 'Dnieper rapids': (35.10, 48.00), 'Khortytsia': (35.08, 47.82),
 'Berezan (Dnieper mouth)': (31.60, 46.60), 'Visby': (18.29, 57.64),
 'London (Steelyard)': (-0.09, 51.51), 'Bruges (Zwin)': (3.30, 51.30), 'Hamburg': (9.99, 53.55), 'Lübeck': (10.69, 53.87),
 'Reval (Tallinn)': (24.75, 59.44), 'Bergen (Bryggen)': (5.32, 60.39), 'Danzig': (18.65, 54.35),
 # Pacific / Atlantic
 'Manila (Cavite)': (120.90, 14.48), 'San Bernardino Strait': (124.20, 12.60), 'Guam': (144.75, 13.45),
 'Acapulco': (-99.88, 16.85), 'Liverpool': (-2.99, 53.40), 'Gorée': (-17.40, 14.67), 'Elmina': (-1.35, 5.08),
 'Ouidah': (2.09, 6.36), 'Bonny': (7.15, 4.43), 'Bridgetown (Barbados)': (-59.62, 13.10), 'Kingston (Jamaica)': (-76.80, 17.97),
 # Spice
 'Goa': (73.83, 15.50), 'Banda Neira': (129.90, -4.53), 'Ambon': (128.18, -3.70), 'Ternate': (127.38, 0.79),
 'Tidore': (127.40, 0.68), 'Cape of Good Hope': (18.47, -34.36), 'Cape Town': (18.42, -33.92), 'Batavia': (106.81, -6.12),
 'Lisbon': (-9.14, 38.70), 'Texel': (4.80, 53.05),
 # Inca
 'Pasto (Los Pastos)': (-77.28, 1.21), 'Quito': (-78.51, -0.22), 'Riobamba': (-78.65, -1.67), 'Tumebamba (Cuenca)': (-79.00, -2.90),
 'Loja': (-79.20, -4.00), 'Cajamarca': (-78.50, -7.16), 'Huamachuco': (-78.05, -7.81), 'Huánuco Pampa': (-76.60, -9.88),
 'Jauja': (-75.50, -11.77), 'Vilcashuamán': (-73.95, -13.65), 'Cusco': (-71.97, -13.53), 'Chucuito': (-69.89, -15.89),
 'Paria': (-67.00, -17.95), 'Tupiza': (-65.72, -21.44), 'Mendoza': (-68.84, -32.89),
 # voyages
 'Palos de la Frontera': (-6.89, 37.23), 'San Sebastián de La Gomera': (-17.11, 28.09), 'Guanahani (San Salvador?)': (-74.48, 24.05),
 'La Navidad (Hispaniola)': (-72.10, 19.75), 'Santa Maria (Azores)': (-25.10, 36.95),
 'Mossel Bay': (22.15, -34.18), 'Walvis Bay': (14.50, -22.95), 'Kwaaihoek': (26.48, -33.71),
 'Sanlúcar de Barrameda': (-6.35, 36.78), 'Rio de Janeiro': (-43.17, -22.90), 'Puerto San Julián': (-67.72, -49.31),
 'Cebu': (123.90, 10.30), 'Mactan': (123.99, 10.30), 'Mauritius': (57.50, -20.16),
 'Golden Bay': (172.80, -40.70), 'Tongatapu': (184.80, -21.13), 'Plymouth': (-4.14, 50.36), 'Matavai Bay (Tahiti)': (-149.48, -17.50),
 'Poverty Bay': (178.40, -38.75), 'Botany Bay': (151.23, -34.00), 'Endeavour Reef': (145.57, -15.78), 'Deal': (1.40, 51.22),
 'Brattahlíð': (-45.50, 61.15), "L'Anse aux Meadows": (-55.53, 51.60),
 'Tangier': (-5.80, 35.77), 'Damascus': (36.29, 33.51), 'Baghdad': (44.37, 33.31), 'Isfahan': (51.67, 32.65),
 'Sinop': (35.15, 42.02), 'Kaffa': (35.38, 45.03), 'Astrakhan': (48.03, 46.35), 'Balkh': (66.90, 36.76),
 'Multan': (71.47, 30.20), 'Delhi': (77.21, 28.61), 'Maldives (Malé)': (73.51, 4.18), "Adam's Peak": (80.50, 6.81),
 'Chittagong': (91.80, 22.33), 'Samudra Pasai': (97.20, 5.15), 'Zaitun (Quanzhou)': (118.59, 24.91), 'Granada': (-3.60, 37.18),
 'Dhofar (Zafar)': (54.10, 17.00), 'Kazeh': (0, 0),
 'Petropavlovsk': (158.65, 53.02), 'Mount Saint Elias / Kayak Island': (-144.40, 59.90), 'Shumagin Islands': (-160.00, 55.10),
 'Bering Island': (166.20, 55.00),
 'Camp Dubois': (-90.13, 38.82), 'St. Charles': (-90.48, 38.78), 'Council Bluff': (-95.95, 41.45), 'Fort Mandan': (-101.27, 47.30),
 'Great Falls of the Missouri': (-111.30, 47.50), 'Three Forks': (-111.50, 45.92), 'Lemhi Pass': (-113.44, 44.97),
 "Traveler's Rest": (-114.07, 46.75), 'Lolo Pass': (-114.58, 46.63), 'Weippe Prairie': (-115.94, 46.38),
 'Fort Clatsop': (-123.88, 46.13), 'Nanjing': (118.78, 32.06), 'Liujiagang': (121.20, 31.60), 'Changle': (119.52, 25.96),
 'Surabaya': (112.73, -7.20), 'Palembang': (104.75, -2.98),
 'Massalia (Marseille)': (5.37, 43.30), 'Gades (Cádiz)': (-6.29, 36.53), 'Belerion (Land\'s End)': (-5.71, 50.07),
 'Orkney (Orcas)': (-3.00, 59.00), 'Thule? (Norway, debated)': (5.00, 62.50), 'Kantion (Kent)': (1.45, 51.37),
}
del H['Kazeh']

def pt(p):
    if isinstance(p, str): return [round(H[p][0], 2), round(H[p][1], 2)], p
    return [round(p[0], 2), round(p[1], 2)], None

def split_dateline(pts):
    """pts with possibly unwrapped lon (beyond +-180) -> list of paths within -180..180."""
    import math
    def band(l): return math.floor((l + 180) / 360)
    pts = [list(p) for p in pts]
    for i in range(1, len(pts)):
        while pts[i][0] - pts[i-1][0] > 180: pts[i][0] -= 360
        while pts[i][0] - pts[i-1][0] < -180: pts[i][0] += 360
    out, cur = [], []
    for i, (lo, la) in enumerate(pts):
        if i and band(pts[i-1][0]) != band(lo):
            (a0, a1), (b0, b1) = pts[i-1], (lo, la)
            k = max(band(a0), band(lo)); cross = -180 + 360 * k
            t = (cross - a0) / (b0 - a0); lat = round(a1 + t * (b1 - a1), 2)
            east = b0 > a0
            cur.append([180.0 if east else -180.0, lat]); out.append(cur)
            cur = [[-180.0 if east else 180.0, lat]]
        cur.append([round(lo - 360 * band(lo), 2), la])
    out.append(cur)
    return out

def build(entry, kinds_ok=True):
    e = dict(entry); hubs = {}
    raw = e.pop('route')  # list of segments; each segment list of points (str or [lon,lat])
    segs = raw if isinstance(raw[0], list) and raw and (isinstance(raw[0][0], (list, str))) else [raw]
    allpaths, kinds = [], []
    for si, s in enumerate(segs):
        pts = []
        for p in s:
            c, name = pt(p)
            if name: hubs[name] = c
            pts.append(c)
        sp = split_dateline(pts); allpaths += sp
        if 'kinds' in e: kinds += [e['kinds'][si]] * len(sp)
    if 'kinds' in e: e['kinds'] = kinds
    # normalise hub lon too
    e['hubs'] = [{'n': n, 'lon': ((c[0] + 180) % 360) - 180 if abs(c[0]) > 180 else c[0], 'lat': c[1]} for n, c in hubs.items()]
    if len(allpaths) == 1: e['path'] = allpaths[0]
    else: e['paths'] = allpaths
    e['src'] = [W + e['w'].replace(' ', '_')] + e.get('src', [])
    return e

T = []  # trade routes
def tr(n, w, f, t, kind, goods, d, route, src=(), **kw):
    T.append(build(dict(n=n, w=w, **{'from': f, 'to': t}, kind=kind, goods=goods, d=d, route=route, src=list(src), **kw)))

# ---------------- A) TRADE ROUTES ----------------
tr('Silk Road – northern Tarim route', 'Silk Road', -114, 1450, 'land', ['silk', 'horses', 'paper', 'glass', 'silver'],
   'Opened after Zhang Qian\'s missions under the Han (c. 114 BCE); from Chang\'an through the Gansu Corridor and the oases north of the Taklamakan to Kashgar.',
   ["Chang'an (Xi'an)", 'Lanzhou', 'Wuwei', 'Zhangye', 'Jiuquan', 'Dunhuang', 'Hami', 'Turpan', 'Karasahr', 'Kucha', 'Aksu', 'Kashgar'])
tr('Silk Road – southern Tarim route', 'Silk Road', -114, 1450, 'land', ['silk', 'jade', 'textiles'],
   'Branch skirting the south rim of the Taklamakan and Lop Nur through oasis towns such as Khotan, famed for jade, rejoining the northern route at Kashgar.',
   ['Dunhuang', 'Miran', 'Charklik', 'Cherchen', 'Niya', 'Keriya', 'Khotan', 'Yarkand', 'Kashgar'])
tr('Silk Road – western trunk (Kashgar–Antioch)', 'Silk Road', -114, 1450, 'land', ['silk', 'spices', 'silver', 'glassware'],
   'From Kashgar over the Pamir/Tian Shan passes via Samarkand and Merv to Parthian and Sasanian Ctesiphon; the Parthian Empire bridged the network to Roman Syria.',
   ['Kashgar', 'Osh', 'Khujand', 'Samarkand', 'Bukhara', 'Merv', 'Sarakhs', 'Nishapur', 'Rey', 'Hamadan (Ecbatana)', 'Ctesiphon', 'Dura-Europos', 'Palmyra', 'Antioch'])
tr('Silk Road – Anatolian branch to Constantinople', 'Silk Road', 330, 1450, 'land', ['silk', 'spices'],
   'Medieval western end: caravans from Tabriz crossed Anatolia to Constantinople, the Byzantine capital founded 330; overland trade declined in the mid-15th century.',
   ['Tabriz', 'Erzurum', 'Sivas', 'Ankara', 'Nicaea', 'Constantinople'])
tr('Maritime Silk Road / monsoon route', 'Maritime Silk Road', -200, 1500, 'sea', ['silk', 'porcelain', 'spices', 'pepper', 'incense'],
   'Sea network from the 2nd century BCE, first run by Austronesian sailors, later Persian, Arab, Tamil and Chinese ships riding the monsoon winds; Quanzhou joined Guangzhou by the 10th century.',
   [['Guangzhou', [113.6, 21.6], [111.2, 17.0], [109.9, 12.0], [106.3, 7.8], [105.0, 3.0], [104.0, 1.2], 'Malacca', [100.5, 3.4],
     [97.8, 5.9], [95.0, 6.3], [88.0, 5.8], [81.5, 5.5], 'Galle', [76.6, 7.8], 'Quilon (Kollam)', [75.6, 10.0], 'Calicut', [68.0, 13.0], [58.0, 13.5],
     [50.0, 12.9], 'Aden', [43.4, 12.6], [41.2, 15.5], [38.6, 20.0], [36.0, 23.5], [34.6, 26.5], [33.0, 28.8], 'Suez (Qulzum)'],
    ['Suez (Qulzum)', 'Cairo', 'Alexandria']], kinds=['sea', 'land'])
tr('Swahili coast monsoon route', 'Swahili coast', 800, 1900, 'sea', ['gold', 'ivory', 'slaves', 'timber', 'cloth', 'beads'],
   'Monsoon winds carried dhows between Arabia and the Swahili ports; Kilwa grew rich on Sofala gold. The coast is described in the 1st-century Periplus and by Ibn Battuta.',
   ['Aden', [49.0, 12.4], [51.4, 12.1], [51.8, 11.6], [51.3, 8.0], [48.8, 4.5], [46.0, 2.0], 'Mogadishu', [43.3, -1.0], 'Malindi', 'Mombasa', 'Zanzibar', [39.8, -7.5], 'Kilwa',
    [40.3, -9.8], [40.9, -11.5], [41.2, -14.5], 'Mozambique Island', [40.3, -16.3], [38.2, -18.0], [36.0, -19.8], 'Sofala'])
tr('Incense Route', 'Incense trade route', -300, 200, 'land', ['frankincense', 'myrrh', 'spices', 'Indian goods'],
   'Aromatics from Dhofar, shipped to the South Arabian coast, went by caravan north via Shabwa, Qataban, Saba and Ma\'in to Petra and Gaza; flourished c. 3rd c. BCE–2nd c. CE.',
   [['Khor Rori (Sumhuram)', [53.8, 16.4], [52.0, 15.0], [50.0, 14.5], 'Qana'],
    ['Qana', 'Shabwa', 'Timna', "Ma'rib", 'Najran', [42.6, 19.5], 'Mecca', 'Yathrib (Medina)', 'Dedan (al-Ula)', 'Hegra', 'Tayma', [36.6, 28.6], 'Petra', 'Gaza']],
   kinds=['sea', 'land'])
tr('Amber Road', 'Amber Road', -1500, 400, 'land', ['amber', 'furs', 'bronze', 'Roman wares'],
   'Baltic amber reached the Mediterranean from at least the 16th c. BCE; the Roman-era road ran from the Baltic coast via Carnuntum on the Danube to Aquileia.',
   ['Sambia amber coast', 'Gdańsk', 'Biskupin', 'Kalisz', 'Wrocław', 'Kłodzko', 'Brno', 'Carnuntum', 'Scarbantia (Sopron)',
    'Savaria (Szombathely)', 'Poetovio (Ptuj)', 'Celeia (Celje)', 'Emona (Ljubljana)', 'Aquileia'])
tr('Tin route (Cornwall–Massalia, debated)', 'Tin sources and trade during antiquity', -600, -50, 'sea', ['tin'],
   '(debated) Diodorus says Cornish tin went to the island of Ictis, then across Gaul by horse to the Rhône mouth; Massalia (founded c. 600 BCE) traded Brittany and Cornwall tin overland.',
   [['Ictis (St Michael\'s Mount?)', [-5.3, 49.6], [-5.6, 48.3], [-4.8, 47.5], [-3.0, 47.1], 'Corbilo (Loire mouth)'],
    ['Corbilo (Loire mouth)', 'Nantes', 'Tours', 'Roanne', 'Lugdunum (Lyon)', 'Arles', 'Massalia']], kinds=['sea', 'land'])
tr('Trans-Saharan gold–salt route (western)', 'Trans-Saharan trade', 700, 1600, 'land', ['gold', 'salt', 'slaves', 'copper', 'cloth'],
   'Camel caravans of 1,000 or more swapped West African gold for Saharan salt; Sijilmasa peaked in the 11th–12th centuries, Taghaza\'s buildings were made of salt (Ibn Battuta).',
   ['Fez', [-4.6, 32.8], 'Sijilmasa', [-4.8, 27.5], 'Taghaza', 'Araouane', 'Timbuktu', 'Gao'])
tr('Trans-Saharan route (Kano–Tripoli)', 'Trans-Saharan trade', 900, 1900, 'land', ['gold', 'slaves', 'leather', 'salt', 'textiles'],
   'Central route from the Hausa city of Kano via Agadez and the oases of Ghat and Ghadames to Tripoli; Gao was linked to the same road (the Ghadames Road).',
   ['Kano', [8.6, 14.5], 'Agadez', [9.0, 20.5], 'Ghat', 'Ghadames', [11.5, 31.6], 'Tripoli'])
tr('Royal Road (Persian)', 'Royal Road', -500, -330, 'land', ['state post', 'tribute', 'trade goods'],
   'Achaemenid highway from Susa to Sardis, perfected under Darius I with 111 posting stations; couriers covered it in nine days, a ninety-day walk.',
   ['Sardis', 'Gordion', 'Ancyra', 'Kanesh (Kültepe)', 'Melitene', 'Amida', 'Nisibis', 'Nineveh', 'Arbela', 'Arrapha', [46.2, 33.6], 'Susa'])
tr('Via Appia – Via Egnatia (Rome–Byzantium axis)', 'Via Egnatia', -312, 1450, 'land', ['troops', 'post', 'trade goods'],
   'Via Appia (begun 312 BCE) ran from Rome to Brundisium; across the Adriatic, the 2nd-century BCE Via Egnatia linked Dyrrachium via Thessalonica to Byzantium.',
   [['Rome', 'Terracina', 'Capua', 'Beneventum', 'Venusia', 'Tarentum', 'Brundisium'],
    ['Brundisium', [18.6, 40.9], 'Dyrrachium'],
    ['Dyrrachium', 'Lychnidos (Ohrid)', 'Heraclea Lyncestis', 'Edessa', 'Pella', 'Thessalonica', 'Amphipolis', 'Philippi', 'Traianopolis', 'Kypsela', 'Perinthus', 'Constantinople']],
   kinds=['land', 'sea', 'land'], src=[W + 'Appian_Way'])
tr('Grand Canal of China', 'Grand Canal (China)', 609, 1900, 'river', ['grain', 'tribute rice', 'salt', 'silk'],
   'Completed by Emperor Yang of Sui in 609; the Yuan moved the capital to Beijing and built the Huitong Canal (1289), giving the 1,776 km Jing–Hang line shown.',
   ['Hangzhou', 'Jiaxing', 'Suzhou', 'Wuxi', 'Changzhou', 'Zhenjiang', 'Yangzhou', 'Gaoyou', "Huai'an", 'Suqian', 'Weishan', 'Jining',
    'Liaocheng', 'Linqing', 'Dezhou', 'Cangzhou', 'Tianjin', 'Tongzhou', 'Beijing'])
tr('Tea Horse Road', 'Tea Horse Road', 700, 1900, 'land', ['brick tea', 'horses', 'salt', 'medicinal herbs'],
   'Caravan paths through Sichuan, Yunnan and Tibet trading Chinese tea for Tibetan horses from the Tang–Song era; Kangding (Dartsedo) was the busiest tea-horse market. Start date approximate.',
   [["Ya'an", 'Luding', 'Kangding (Dartsedo)', 'Litang', 'Batang', 'Markam', 'Zogang', 'Baxoi', 'Pomê', 'Nyingchi', "Gongbo'gyamda", 'Lhasa'],
    ["Pu'er", 'Dali', 'Lijiang', 'Shangri-La (Gyalthang)', 'Deqin', 'Markam']])
tr('Route from the Varangians to the Greeks', 'Route from the Varangians to the Greeks', 800, 1200, 'river', ['furs', 'slaves', 'wax', 'honey', 'silver', 'silk'],
   'Probably established in the late 8th–early 9th century: Baltic, Neva, Volkhov, Lake Ilmen and Lovat, portage to the Dnieper, then Kiev, the rapids and the Black Sea to Constantinople.',
   [['Birka', [19.3, 59.6], [22.0, 59.6], [26.0, 59.9], [27.5, 59.85], [29.0, 59.95], 'Neva mouth'],
    ['Neva mouth', [31.0, 60.0], 'Staraya Ladoga', 'Novgorod', 'Lake Ilmen', [31.2, 57.6], 'Velikiye Luki', 'Gnezdovo (Smolensk)', [30.9, 53.0], 'Lyubech', 'Kiev', [32.1, 49.4], [34.6, 48.5], 'Dnieper rapids', 'Khortytsia', [33.5, 46.9], 'Berezan (Dnieper mouth)'],
    ['Berezan (Dnieper mouth)', [30.8, 45.6], [29.8, 43.6], [29.3, 41.6], 'Constantinople']], kinds=['sea', 'river', 'sea'])
tr('Hanseatic trade route', 'Hanseatic League', 1200, 1669, 'sea', ['cloth', 'furs', 'wax', 'stockfish', 'salt', 'grain', 'timber'],
   'Network of Lübeck-led merchant towns with Kontors in London (Steelyard), Bruges, Bergen and Novgorod (Peterhof); it disintegrated in 1669.',
   [['London (Steelyard)', [1.4, 51.5], [2.8, 51.5], 'Bruges (Zwin)', [4.0, 52.4], [6.0, 53.7], [8.2, 54.0], 'Hamburg'],
    ['Hamburg', 'Lübeck'],
    ['Lübeck', [11.2, 54.2], [13.0, 54.8], [15.5, 55.5], [17.5, 56.8], 'Visby', [21.0, 58.9], [22.5, 59.4], 'Reval (Tallinn)', [26.0, 59.9], [27.5, 59.85], [29.0, 59.95], 'Neva mouth'],
    ['Neva mouth', [31.0, 60.0], 'Staraya Ladoga', 'Novgorod'],
    ['Lübeck', [11.2, 54.2], [12.7, 55.6], [11.5, 57.5], [10.6, 57.9], [8.0, 57.7], [5.5, 58.2], [4.8, 59.0], 'Bergen (Bryggen)']],
   kinds=['sea', 'land', 'sea', 'river', 'sea'])
tr('Manila galleon route', 'Manila galleon', 1565, 1815, 'sea', ['silver', 'silk', 'porcelain', 'spices'],
   'Galleons left Cavite in late June/early July, rode the Kuroshio north-east to reach Acapulco around March–April; the return ran at lower latitudes via the Marianas. Opened by Urdaneta\'s 1565 tornaviaje.',
   [['Manila (Cavite)', [120.4, 13.8], [122.5, 12.9], 'San Bernardino Strait', [126.5, 14.5], [132, 22], [142, 31], [155, 37], [170, 39.5],
     [190, 40], [210, 40], [225, 39], [235.5, 39.5], [238.5, 33.5], [243, 29.5], [247.2, 24.0], [250.5, 22.3], [255.5, 18.5], 'Acapulco'],
    ['Acapulco', [255, 14], [240, 13.5], [220, 13], [200, 13], [180, 13], [160, 13.3], 'Guam', [135, 13], 'San Bernardino Strait', [122.5, 12.9], [120.4, 13.8], 'Manila (Cavite)']],
   kinds=['sea', 'sea'])
tr('Atlantic triangular trade – outward leg', 'Triangular trade', 1519, 1867, 'sea', ['textiles', 'guns', 'alcohol', 'metalware'],
   'Classic model: manufactured goods shipped from European ports such as Liverpool to West Africa and exchanged for enslaved people. Direct Africa–Americas voyages began by 1519.',
   ['Liverpool', [-4.0, 53.5], [-5.5, 52.5], [-7.0, 50.5], [-11.0, 46.0], [-12.5, 38.0], [-14.5, 30.0], [-18.5, 21.0], 'Gorée', [-17.0, 10.5],
    [-13.5, 6.5], [-8.0, 4.0], [-4.5, 4.6], 'Elmina', [0.5, 5.0], 'Ouidah', [5.0, 4.5], 'Bonny'], src=[W + 'Atlantic_slave_trade'])
tr('Atlantic triangular trade – Middle Passage', 'Middle Passage', 1519, 1867, 'sea', ['enslaved Africans'],
   'About 12.75 million Africans were loaded onto slave ships for the Americas; up to 2 million died on the crossing. The last known slave ship reached Cuba in 1867.',
   ['Bonny', [5.0, 3.5], 'Ouidah', [0.0, 3.5], [-10.0, 3.0], [-20.0, 5.0], [-35.0, 9.0], [-50.0, 12.0], 'Bridgetown (Barbados)', [-66.0, 15.0], 'Kingston (Jamaica)'],
   src=[W + 'Atlantic_slave_trade'])
tr('Atlantic triangular trade – return leg', 'Triangular trade', 1519, 1867, 'sea', ['sugar', 'rum', 'tobacco', 'cotton'],
   'Ships returned to Europe with plantation produce – sugar, rum, tobacco, cotton – riding the Gulf Stream and westerlies home.',
   ['Kingston (Jamaica)', [-74.0, 19.9], [-73.2, 23.5], [-70.0, 30.0], [-60.0, 38.0], [-45.0, 45.0], [-25.0, 50.0], [-10.5, 51.0], [-6.0, 51.7], [-5.5, 52.3], [-5.0, 53.3], [-3.8, 53.5], 'Liverpool'],
   src=[W + 'Atlantic_slave_trade'])
tr('Portuguese spice route to the Moluccas', 'Spice trade', 1512, 1605, 'sea', ['cloves', 'nutmeg', 'mace', 'pepper'],
   'After taking Malacca (1511), Albuquerque sent António de Abreu east; in early 1512 the Portuguese became the first Europeans at the Banda Islands, then the world\'s only nutmeg source.',
   [['Goa', [73.2, 13.5], [75.3, 9.0], [77.5, 7.4], [80.6, 5.4], [90.0, 5.6], [95.0, 6.3], [98.0, 5.8], [100.5, 3.4], 'Malacca', [104.0, 1.2],
     [105.5, -0.5], [106.9, -2.5], [109.0, -5.0], [113.0, -5.6], [117.5, -6.4], [121.0, -6.6], [125.5, -5.5], [127.5, -4.4], 'Ambon', [129.0, -4.2], 'Banda Neira'],
    ['Ambon', [127.6, -3.1], [126.9, -1.3], [127.0, 0.3], 'Ternate']])
tr('Dutch Brouwer Route to the spice islands', 'Brouwer Route', 1611, 1799, 'sea', ['nutmeg', 'cloves', 'pepper', 'textiles'],
   'Devised by Hendrik Brouwer in 1611: from the Cape into the Roaring Forties, east across the Indian Ocean, then north to Java – about 6 months instead of 12; compulsory for VOC ships by 1616.',
   ['Cape Town', [18.0, -35.5], [22.0, -39.0], [40.0, -39.5], [60.0, -39.5], [80.0, -39.0], [100.0, -37.0], [106.0, -28.0], [105.5, -15.0],
    [105.0, -7.0], [105.75, -5.95], 'Batavia', [110.0, -5.5], [115.0, -6.0], [120.5, -6.6], [125.5, -5.5], 'Banda Neira'],
   src=[W + 'Dutch_East_India_Company'])
tr('Qhapaq Ñan (Inca road, sierra trunk)', 'Inca road system', 1438, 1533, 'land', ['state goods', 'textiles', 'maize', 'troops', 'chaski messengers'],
   'About 40,000 km in all; Hyslop measured the mountain trunk via Quito, Tumebamba, Huánuco, Cusco, Chucuito and Paria to the Mendoza River at 5,658 km. Built without wheeled transport.',
   ['Pasto (Los Pastos)', 'Quito', 'Riobamba', 'Tumebamba (Cuenca)', 'Loja', 'Cajamarca', 'Huamachuco', 'Huánuco Pampa', 'Jauja',
    'Vilcashuamán', 'Cusco', 'Chucuito', 'Paria', 'Tupiza', [-65.6, -24.5], [-66.8, -27.5], [-68.3, -30.5], 'Mendoza'],
   src=[W + 'Inca_Empire'])

# ---------------- B) VOYAGES ----------------
V = []
def vo(n, w, who, f, t, d, route, src=()):
    V.append(build(dict(n=n, w=w, who=who, **{'from': f, 'to': t}, d=d, route=route, src=list(src))))

vo('Pytheas\' voyage to the North (route debated)', 'Pytheas', 'Pytheas of Massalia', -325, -324,
   '(debated) Around 325 BCE he circumnavigated much of Britain, described Belerion (Cornwall), the midnight sun and Thule; his route and Thule (Norway or Iceland?) are reconstructed from later authors.',
   ['Massalia (Marseille)', [4.5, 42.8], [1.2, 40.0], [0.6, 38.5], [-1.6, 36.9], [-3.5, 36.3], [-5.6, 35.95], 'Gades (Cádiz)', [-9.3, 36.8], [-9.8, 40.0],
    [-9.8, 43.0], [-8.5, 44.0], [-6.0, 44.2], [-5.6, 48.3], [-5.9, 49.9], 'Belerion (Land\'s End)', [-5.6, 52.2], [-5.2, 54.0], [-5.6, 55.3], [-8.0, 57.0], [-6.4, 58.7],
    'Orkney (Orcas)', [-1.3, 60.6], 'Thule? (Norway, debated)', [0.0, 58.0], [-1.5, 57.0], [0.5, 54.5], [1.8, 52.8], 'Kantion (Kent)', [3.5, 52.5], [6.0, 53.7], [8.2, 54.1]])
vo('Zheng He\'s seventh voyage', 'Ming treasure voyages', 'Zheng He', 1431.05, 1433.56,
   'The last treasure voyage left Nanjing on 19 January 1431, reached Hormuz on 17 January 1433 while detached squadrons went to Arabia and East Africa, and was back by 22 July 1433.',
   ['Nanjing', 'Liujiagang', [122.6, 30.5], [122.3, 28.5], [121.0, 27.0], 'Changle', [119.8, 24.5], [118.0, 23.0], [111.5, 17.0], [109.8, 13.5], [109.5, 11.5], [108.0, 10.0], [106.3, 7.8], [107.5, 2.0], [109.5, -4.0],
    [112.6, -6.6], 'Surabaya', [111.0, -6.0], [107.0, -5.0], [105.4, -2.4], 'Palembang', [105.0, -2.2], [105.3, -1.2], [104.8, 0.3], [104.0, 1.2], 'Malacca', [100.5, 3.4], [97.8, 5.9], 'Samudra Pasai', [95.3, 6.2],
    [88.0, 5.8], [81.5, 5.5], 'Galle', [76.6, 7.8], 'Calicut', [68.0, 17.0], [60.5, 23.0], [57.5, 25.5], 'Hormuz'])
vo('Columbus\'s first voyage', 'Voyages of Christopher Columbus', 'Christopher Columbus', 1492.59, 1493.2,
   'Left Palos on 3 August 1492, sailed from La Gomera on 6 September, landed on Guanahani (San Salvador) on 12 October; back in Palos on 15 March 1493 after a storm forced him into Lisbon.',
   ['Palos de la Frontera', [-7.2, 36.8], [-12.0, 32.0], [-16.0, 28.0], 'San Sebastián de La Gomera', [-25.0, 28.0], [-35.0, 28.0], [-45.0, 27.5], [-55.0, 26.0],
    [-65.0, 25.0], 'Guanahani (San Salvador?)', [-75.3, 23.4], [-75.8, 21.3], [-74.3, 20.4], [-73.4, 20.0], 'La Navidad (Hispaniola)', [-70.5, 20.0],
    [-69.0, 19.4], [-65.0, 25.0], [-55.0, 33.0], [-45.0, 37.0], [-35.0, 37.5], 'Santa Maria (Azores)', [-15.0, 38.5], [-9.6, 38.6], 'Lisbon', [-9.3, 38.0],
    [-8.5, 36.8], 'Palos de la Frontera'])
vo('Vasco da Gama\'s first voyage to India', 'Vasco da Gama', 'Vasco da Gama', 1497.52, 1499.66,
   'Left Lisbon on 8 July 1497, rounded the Cape, crossed from Malindi and landed at Calicut on 20 May 1498 – the first sea route from Europe to India. Home 29 August 1499.',
   ['Lisbon', [-11.0, 35.0], [-15.5, 28.5], [-23.0, 14.5], [-25.0, 5.0], [-28.0, -15.0], [-25.0, -25.0], [-12.0, -32.0], [17.8, -32.6], [18.3, -34.6], [20.0, -35.1],
    'Mossel Bay', [27.0, -34.2], [32.0, -29.5], [33.5, -27.0], [36.2, -24.0], [36.5, -20.0], [40.4, -16.5], 'Mozambique Island', [41.0, -11.0], 'Mombasa', 'Malindi', [50.0, 0.0], [62.0, 6.0],
    [72.0, 10.5], 'Calicut', [65.0, 8.0], [52.0, 4.0], 'Mogadishu', 'Malindi', [41.0, -11.0], [41.3, -14.0], [40.4, -16.5], [38.5, -18.5], [36.5, -20.0], [36.2, -24.0], [33.5, -27.0], [32.0, -29.5], [28.0, -33.6], [25.0, -34.4], [20.0, -35.1], [18.3, -34.6], [5.0, -20.0],
    [-12.0, -5.0], [-23.0, 14.5], [-27.2, 38.5], 'Lisbon'])
vo('Magellan–Elcano circumnavigation', 'Magellan expedition', 'Ferdinand Magellan, Juan Sebastián Elcano', 1519.72, 1522.68,
   'Five ships left Spain on 20 September 1519; Magellan was killed at Mactan in 1521. The Victoria under Elcano returned on 6 September 1522 – the first circumnavigation, with 18 survivors aboard.',
   ['Sanlúcar de Barrameda', [-12.0, 31.0], [-16.2, 28.4], [-20.0, 15.0], [-15.0, 7.0], [-25.0, -2.0], [-33.5, -8.0], [-37.5, -15.0], [-39.0, -20.0], [-41.0, -23.2], 'Rio de Janeiro', [-48.0, -28.0], [-51.0, -33.0], [-55.5, -35.5],
    [-56.0, -37.5], [-60.0, -40.0], [-61.0, -42.0], [-65.0, -47.5], 'Puerto San Julián', [-68.2, -52.4], [-70.8, -53.2], [-71.3, -53.95], [-74.8, -52.7], [-77.0, -48.0], [-80.0, -35.0],
    [-100.0, -22.0], [-138.8, -15.0], [-160.0, -5.0], [-175.0, 5.0], [-200.0, 13.0], 'Guam', [125.9, 10.6], 'Cebu', 'Mactan', [123.5, 9.0], [121.5, 8.5], [119.2, 9.6], [117.0, 7.8], [115.0, 5.2], [117.0, 7.8], [120.0, 7.0], [123.0, 6.0],
    [125.8, 4.5], [127.0, 2.0], 'Tidore', [126.0, -2.5], [125.5, -4.5], [125.3, -8.3], [123.5, -9.3], [122.5, -10.6], [100.0, -25.0], [70.0, -36.0], [20.0, -36.0], [5.0, -25.0],
    [-23.0, 14.5], [-27.0, 37.5], 'Sanlúcar de Barrameda'])
vo('Abel Tasman\'s first voyage', 'Abel Tasman', 'Abel Tasman', 1642.62, 1643.45,
   'Left Batavia on 14 August 1642 via Mauritius and the Roaring Forties; first European to reach Tasmania and New Zealand, then Tonga and Fiji; back in Batavia on 15 June 1643.',
   ['Batavia', [105.75, -5.95], [95.0, -12.0], [57.3, -20.0], [70.0, -45.0], [90.0, -45.0], [120.0, -44.0], [140.0, -43.5], [144.8, -42.0], [146.5, -44.0], [148.0, -43.5],
    [148.1, -42.8], [160.0, -42.0], [170.3, -42.5], [171.6, -41.0], [172.8, -40.5], [174.2, -40.5], [173.2, -39.3], [173.0, -37.0], [172.0, -34.0], [178.0, -25.0],
    'Tongatapu', [181.5, -17.0], [178.0, -15.0], [170.0, -10.0], [159.5, -5.0], [153.2, -3.5], [150.0, -2.0], [145.0, -3.0], [140.0, -2.0],
    [136.0, -0.6], [132.0, 0.0], [130.0, 0.4], [129.0, -1.5], [126.0, -2.7], [123.0, -5.0], [121.0, -7.0], [115.0, -6.0], 'Batavia'])
vo('James Cook\'s first voyage', 'First voyage of James Cook', 'James Cook', 1768.65, 1771.53,
   'HMS Endeavour left Plymouth on 26 August 1768 to observe the 1769 transit of Venus at Tahiti, charted New Zealand and Australia\'s east coast, and reached Deal on 12 July 1771.',
   ['Plymouth', [-8.0, 46.0], [-16.9, 32.5], [-22.0, 20.0], [-28.0, 0.0], [-33.0, -8.0], [-38.5, -16.0], [-39.0, -20.0], [-41.0, -23.2], 'Rio de Janeiro', [-50.0, -35.0],
    [-65.0, -55.0], [-68.0, -57.0], [-110.0, -35.0], 'Matavai Bay (Tahiti)', [-150.0, -35.0], [-178.0, -38.6], 'Poverty Bay', [178.7, -37.6],
    [173.0, -34.1], [173.3, -39.4], [174.6, -41.0], [173.9, -43.9], [168.0, -47.6], [166.0, -45.5], [172.7, -40.3], [149.4, -38.0], [150.4, -36.5],
    'Botany Bay', [153.4, -31.0], [154.0, -28.0], [152.0, -23.0], [149.5, -20.0], 'Endeavour Reef', [144.8, -14.0], [143.4, -12.0], [141.8, -10.4],
    [122.2, -10.4], [120.0, -10.6], [114.0, -9.2], [106.0, -7.6], [105.75, -5.95], 'Batavia', [105.75, -5.95], [70.0, -30.0], [19.5, -35.2], 'Cape Town', [-5.7, -15.9],
    [-25.0, 30.0], [-15.0, 45.0], [-5.5, 49.5], [0.5, 50.5], 'Deal'])
vo('Leif Erikson\'s voyage to Vinland', 'Leif Erikson', 'Leif Erikson', 1000, 1001,
   'Around 1000 Leif sailed Bjarni\'s route in reverse: Helluland (Baffin Island?), Markland (Labrador?), then Vinland. The Norse site at L\'Anse aux Meadows may be his camp (debated).',
   ['Brattahlíð', [-47.5, 60.5], [-48.5, 60.0], [-51.0, 62.0], [-53.5, 65.5], [-60.0, 65.0], [-62.5, 63.0], [-61.0, 60.0], [-59.0, 57.0], [-56.8, 54.5], [-55.0, 53.5], [-55.4, 52.2],
    "L'Anse aux Meadows", [-53.0, 54.0], [-50.0, 58.0], [-48.5, 60.0], [-47.5, 60.5], 'Brattahlíð'])
vo('Bartolomeu Dias rounds the Cape', 'Bartolomeu Dias', 'Bartolomeu Dias', 1487.55, 1488.95,
   'Left Lisbon around July 1487; after 30 days on open ocean reached Mossel Bay on 4 February 1488, first European to round southern Africa; turned back at Kwaaihoek 12 March.',
   ['Lisbon', [-12.0, 33.0], [-18.5, 21.0], [-17.8, 14.5], [-17.0, 10.5], [-13.5, 6.5], [-8.0, 4.0], [-4.5, 4.6], 'Elmina', [5.0, 2.0], [8.5, -2.0], [11.8, -6.2],
    [12.3, -13.0], [11.5, -17.5], 'Walvis Bay', [14.0, -24.5], [15.0, -26.6], [10.0, -33.0], [15.0, -39.0], [22.0, -38.0], 'Mossel Bay', [24.9, -34.5],
    'Kwaaihoek', [24.9, -34.5], [20.0, -35.1], [18.3, -34.6], [14.0, -28.0], [11.5, -17.5], [8.5, -2.0], [5.0, 2.0], 'Elmina', [-4.5, 4.6], [-8.0, 4.0],
    [-13.5, 6.5], [-17.0, 10.5], [-18.5, 21.0], [-12.0, 33.0], 'Lisbon'])
vo('Travels of Ibn Battuta (main loop)', 'Ibn Battuta', 'Ibn Battuta', 1325.45, 1354,
   'Left Tangier on 14 June 1325 for the hajj and travelled ~30 years across Africa, Asia and Iberia; parts of the Rihla, such as China, are doubted by some scholars (debated).',
   ['Tangier', 'Tunis', 'Alexandria', 'Cairo', 'Damascus', 'Mecca', 'Baghdad', 'Mecca', 'Aden',
    'Mogadishu', 'Kilwa', 'Hormuz', 'Konya (Iconium)', 'Sinop', 'Kaffa', 'Astrakhan', 'Constantinople', 'Bukhara',
    'Samarkand', 'Balkh', 'Delhi', 'Calicut', 'Maldives (Malé)', 'Chittagong', 'Samudra Pasai', 'Zaitun (Quanzhou)',
    'Calicut', 'Damascus', 'Mecca', 'Cairo', 'Tunis', 'Fez', 'Granada', 'Sijilmasa', 'Taghaza', 'Oualata', 'Timbuktu', 'Gao', 'Sijilmasa', 'Fez'])
vo('Bering\'s voyage to Alaska (Great Northern Expedition)', 'Great Northern Expedition', 'Vitus Bering, Georg Steller', 1741.43, 1741.93,
   'The St. Peter left Petropavlovsk in June 1741, sighted Mount Saint Elias on 16 July and landed near Kayak Island; wrecked on the return, Bering died on Bering Island in December 1741 (Julian dates).',
   ['Petropavlovsk', [160.5, 52.5], [170.0, 47.0], [185.0, 48.0], [200.0, 52.5], [210.0, 56.0], [215.6, 59.7], 'Mount Saint Elias / Kayak Island',
    [210.0, 57.5], [204.5, 56.0], 'Shumagin Islands', [195.0, 52.5], [185.0, 51.3], [178.0, 52.2], [170.0, 54.0], [166.0, 55.3]])
vo('Lewis and Clark Expedition', 'Lewis and Clark Expedition', 'Meriwether Lewis, William Clark', 1804.37, 1806.73,
   'Set out from Camp Dubois on 14 May 1804 up the Missouri, wintered at Fort Mandan, crossed the Continental Divide at Lemhi Pass, reached the Pacific in 1805; returned 23 September 1806.',
   ['Camp Dubois', 'St. Charles', [-92.2, 38.6], [-94.6, 39.1], [-95.3, 40.0], 'Council Bluff', [-96.4, 42.5], [-97.4, 42.85], [-99.0, 43.2], [-100.35, 44.37],
    [-100.6, 45.6], 'Fort Mandan', [-103.97, 47.98], [-106.4, 48.0], [-108.7, 47.7], 'Great Falls of the Missouri', 'Three Forks', [-112.65, 45.25],
    'Lemhi Pass', [-113.9, 45.2], "Traveler's Rest", 'Lolo Pass', 'Weippe Prairie', [-116.25, 46.48], [-117.03, 46.42], [-119.05, 46.21], [-121.18, 45.6],
    [-122.6, 45.65], [-123.3, 46.2], 'Fort Clatsop'])

json.dump({'trade': T, 'voyages': V}, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(T), 'trade', len(V), 'voyages')

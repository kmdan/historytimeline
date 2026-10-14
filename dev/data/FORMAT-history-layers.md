# Data format for history layers and tours (research agents fill these)

Years are signed civil years (CE positive, BCE negative, no year 0); fractional years give months/days
(1789.54 = mid-July 1789: year + (day_of_year-0.5)/365). Coordinates in decimal degrees (lat, lon).
Facts checked against Wikipedia (en, or de/fr/nl/sv where better) or cited papers; every record has "src": [urls].
Mark contested numbers/claims with "debated" in the text. Mainstream scholarship only.

## <topic>.json
{
 "places": [   // dated points: revolts, republics, trading posts, colonies, sieges, cities taken...
  {"n": "Batavian Republic (The Hague)", "lat": 52.08, "lon": 4.31, "y": 1795.05, "end": 1806.4, "approx": false,
   "kind": "republic|uprising|post|colony|naval-base|fort|city|treaty|other", "who": "France|Britain|EIC|...",
   "what": "one short sentence", "w": "English Wikipedia title", "src": ["https://..."]}
 ],
 "battles": [
  {"n": "Battle of Austerlitz", "y": 1805.92, "date": "2 December 1805", "lat": 49.13, "lon": 16.76,
   "war": "War of the Third Coalition", "a": "France", "b": "Russia, Austria", "won": "a|b|draw",
   "men": [73000, 85000], "loss": [9000, 36000], "what": "one sentence", "w": "Battle of Austerlitz", "src": ["..."]}
 ],
 "campaigns": [   // armies or fleets moving: a dated track, optionally with strength at each point (Minard-style)
  {"n": "Napoleon's invasion of Russia", "who": "Grande Armée", "side": "France",
   "pts": [[lon, lat, y, men_or_null], ...],   // in order of travel, 8-40 points, y increasing
   "what": "one or two sentences", "w": "French invasion of Russia", "src": ["..."]}
 ],
 "routes": [   // long-lived lines (shipping lanes, roads) while in use
  {"n": "...", "from": 1600, "to": 1858, "kind": "sea|land|river", "path": [[lon, lat], ...], "goods": ["..."],
   "d": "one sentence", "w": "...", "src": ["..."]}
 ]
}

## tour_<id>.json
{"id": "...", "title": "...", "blurb": "one sentence", "cat": "Revolutions & empires", "steps": [step, ...]}
step = {"y": 1789.54, "lat": 48.85, "lon": 2.37, "z": 6, "t": "short title", "c": "2-4 sentences, plain English, concrete numbers",
        "w": "English Wikipedia title", "look": [[lat, lon, "label"], ...],
        "tips": [{"h": "short title", "t": "1-2 sentence did-you-know", "lat": .., "lon": ..}],   // 2 per step, other places than the step centre
        "img_alt": {"file": "File:....jpg", "by": "artist, year", "lic": "Public domain"},   // a COLOUR painting of the scene, verified on Commons
        "src": ["https://en.wikipedia.org/wiki/..."]}
z = map zoom: 1 whole world, 2 a continent, 4 a region (e.g. Central Europe), 6 a country, 8+ a city.

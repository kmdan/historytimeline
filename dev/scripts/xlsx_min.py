"""Minimal .xlsx reader (standard library only): rows of one sheet as lists of strings/floats."""
import zipfile, re, xml.etree.ElementTree as ET
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

def sheets(path):
    z = zipfile.ZipFile(path)
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rel = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    tgt = {r.get('Id'): r.get('Target') for r in rel}
    return {s.get('name'): 'xl/' + tgt[s.get('{%s}id' % NS['r'])].lstrip('/').replace('xl/', '') for s in wb.find('m:sheets', NS)}

def rows(path, sheet):
    z = zipfile.ZipFile(path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    root = ET.fromstring(z.read(sheets(path)[sheet]))
    col = lambda ref: sum((ord(c) - 64) * 26 ** i for i, c in enumerate(reversed(re.match(r'[A-Z]+', ref).group())))
    for r in root.iter('{%s}row' % NS['m']):
        out = {}
        for c in r.findall('m:c', NS):
            v = c.find('m:v', NS); t = c.get('t')
            if t == 'inlineStr': val = ''.join(x.text or '' for x in c.iter('{%s}t' % NS['m']))
            elif v is None: continue
            elif t == 's': val = ss[int(v.text)]
            else:
                try: val = float(v.text)
                except ValueError: val = v.text
            out[col(c.get('r')) - 1] = val
        yield [out.get(i, '') for i in range(max(out) + 1)] if out else []

import json

rows = None
for line in open('klines_hfq.jsonl', encoding='utf-8'):
    r = json.loads(line)
    if r.get('code') == '300394':
        rows = [{'close': round(c, 3), 'date': d} for d, c in r['rows']]
        break
assert rows and len(rows) == 81

allk = json.load(open('klines_all.json', encoding='utf-8'))
allk['300394'] = {'market': '0', 'code': '300394', 'rows': rows}
with open('klines_all.json', 'w', encoding='utf-8') as f:
    json.dump(allk, f, ensure_ascii=False, indent=1)
print('saved. keys:', sorted(allk.keys()))

base = rows[0]['close']
peak = 0.0
segs = []
s = None
out = ['i  date        close     wan     ret%']
prev = None
for i, r in enumerate(rows):
    wan = 100 * r['close'] / base
    ret = (r['close'] / prev - 1) * 100 if prev else 0
    prev = r['close']
    peak = max(peak, wan)
    if wan < peak and s is None:
        s = i
    if wan >= peak and s is not None:
        segs.append((s, i - 1))
        s = None
    out.append('%2d %s %9.3f %8.2f %7.1f' % (i, r['date'], r['close'], wan, ret))
if s is not None:
    segs.append((s, len(rows) - 1))
out.append('segs %s' % (segs,))
mn = min(range(len(rows)), key=lambda i: rows[i]['close'])
out.append('min idx %d %s' % (mn, rows[mn]))
pk = max(range(len(rows)), key=lambda i: rows[i]['close'])
out.append('peak idx %d %s' % (pk, rows[pk]))
open('_ep009_table.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, "klines_all.json"), encoding="utf-8-sig"))
rows = raw["300502"]["rows"]
base = rows[0]["close"]
nav = [100.0 * r["close"] / base for r in rows]
peak = 0.0
dd = []
for v in nav:
    peak = max(peak, v)
    dd.append((v - peak) / peak)

print("idx  date        close     wan      dd")
for i, (r, v, d) in enumerate(zip(rows, nav, dd)):
    mark = ""
    if d < 0 and i > 0 and dd[i - 1] == 0:
        mark = " <-DD start"
    if d == 0 and i > 0 and dd[i - 1] < 0:
        mark = " <-new high"
    if abs(d + 0.625) < 0.002:
        mark = " <-MAX DD"
    print("%3d  %s %7.2f %8.1f %7.1f%%%s" % (i, r["date"], r["close"], v, d * 100, mark))

pk = max(range(len(nav)), key=lambda i: nav[i])
print("\npeak idx=%d %s %.1f" % (pk, rows[pk]["date"], nav[pk]))
print("end   idx=%d %s %.1f" % (len(nav) - 1, rows[-1]["date"], nav[-1]))
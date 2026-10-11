"""全图逐行墨迹剖面：找出所有文本/图形所在的 y 带"""
import sys
from PIL import Image

im = Image.open(sys.argv[1]).convert("L")
w, h = im.size
px = im.load()
dark = lambda v: v < 150

rows = []
for y in range(h):
    rows.append(sum(1 for x in range(w) if dark(px[x, y])))

# 合并连续非零行为带
bands, cur = [], None
for y, c in enumerate(rows):
    if c > 0:
        cur = [y, y, c] if cur is None else [cur[0], y, max(cur[2], c)]
    else:
        if cur:
            bands.append(cur)
            cur = None
if cur:
    bands.append(cur)

print(f"{'y0':>6}{'y1':>6}{'h':>5}{'maxInk':>9}")
for y0, y1, mx in bands:
    print(f"{y0:>6}{y1:>6}{y1-y0+1:>5}{mx:>9}")

"""定位：标题带墨迹分布 + 安全区越界像素的行列范围"""
import sys
from PIL import Image

path = sys.argv[1]
im = Image.open(path).convert("L")
w, h = im.size
px = im.load()
dark = lambda v: v < 140

print(f"--- {path} ---")

# 1) 标题带 140-500 逐 20px 行墨迹
print("[title band 140-500]")
for y in range(140, 500, 20):
    c = sum(1 for x in range(w) if dark(px[x, y]))
    print(f"  y{y:>4}-{y+20:<4} ink={c}")

# 2) 左/右/下越界像素的 y 范围与 x 范围
excl = [(0, 10), (1852, 1920)]
def rowspan(x0, x1, y0, y1):
    hits = []
    for y in range(y0, y1):
        if any(a <= y < b for a, b in excl):
            continue
        c = sum(1 for x in range(x0, x1) if dark(px[x, y]))
        if c:
            hits.append((y, c))
    return hits

for label, x0, x1, y0, y1 in [
    ("LEFT  x<80", 0, 80, 100, h - 100),
    ("RIGHT x>=1000", 1000, w, 100, h - 100),
    ("BOTTOM y>=1820", 0, w, 1820, h - 100),
]:
    hits = rowspan(x0, x1, y0, y1)
    if not hits:
        print(f"[{label}] clean")
        continue
    ys = [y for y, _ in hits]
    tot = sum(c for _, c in hits)
    xset = []
    for y, _ in hits[:400]:
        xset += [x for x in range(x0, x1) if dark(px[x, y])]
    print(f"[{label}] total={tot} y:{min(ys)}-{max(ys)} "
          f"x:{min(xset) if xset else '-'}..{max(xset) if xset else '-'} "
          f"rows={len(hits)}")

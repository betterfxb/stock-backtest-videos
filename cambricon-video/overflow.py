"""定位越界墨迹的具体坐标（安全区外）"""
import sys
from PIL import Image

SL, SR, ST, SB = 80, 1000, 140, 1780
BANDS = [("标题", 140, 500), ("数据卡", 500, 770), ("主图", 770, 1340),
         ("上下文", 1340, 1420), ("阶段条", 1420, 1540), ("事件卡", 1540, 1780)]


def band_of(y):
    for n, a, b in BANDS:
        if a <= y < b:
            return n
    return "其他"


for p in sys.argv[1:]:
    im = Image.open(p).convert("L")
    px = im.load()
    W, H = im.size
    hits = {}
    for y in range(H):
        for x in range(W):
            if px[x, y] < 235:
                if x < SL or x > SR or y < ST or y > SB:
                    k = (band_of(y), "L" if x < SL else "R" if x > SR else "B" if y > SB else "T")
                    v = hits.get(k)
                    hits[k] = (min(x, v[0]), max(x, v[1]), min(y, v[2]), max(y, v[3])) if v else (x, x, y, y)
    print(f"=== {p} ===")
    if not hits:
        print("  安全区内，无越界")
    for (band, side), v in sorted(hits.items()):
        print(f"  {band:<5}{side}  x{v[0]}..{v[1]}  y{v[2]}..{v[3]}")

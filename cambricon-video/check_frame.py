"""画面校验：尺寸 / 安全区溢出 / 区块墨迹分布 / 亮度"""
import sys
from PIL import Image

SAFE_X, SAFE_TOP, SAFE_BOT = 80, 100, 100

BANDS = [
    ("brand", 0, 10),
    ("meta", 90, 145),
    ("title", 150, 490),
    ("datacard", 496, 692),
    ("chart", 700, 1440),
    ("stage", 1462, 1522),
    ("event", 1552, 1814),
    ("compliance", 1852, 1920),
]


def check(path):
    im = Image.open(path).convert("L")
    w, h = im.size
    print(f"\n=== {path} ===")
    print(f"size {w}x{h}", "OK" if (w, h) == (1080, 1920) else "!! SIZE MISMATCH")

    px = im.load()
    dark = lambda v: v < 140

    # 安全区溢出：左右 80px 内、上下 100px 内的墨迹（品牌条与合规条为通栏，单独排除）
    bands = [(0, 10), (1852, 1920)]
    viol = {"left": 0, "right": 0, "top": 0, "bottom": 0}
    for y in range(SAFE_TOP, h - SAFE_BOT):
        if any(a <= y < b for a, b in bands):
            continue
        for x in range(SAFE_X):
            if dark(px[x, y]):
                viol["left"] += 1
        for x in range(w - SAFE_X, w):
            if dark(px[x, y]):
                viol["right"] += 1
    for y in range(100):
        row = sum(1 for x in range(w) if dark(px[x, y]))
        if row > 0 and not any(a <= y < b for a, b in bands):
            viol["top"] += row
    for y in range(h - 100, h):
        row = sum(1 for x in range(w) if dark(px[x, y]))
        if row > 0 and not any(a <= y < b for a, b in bands):
            viol["bottom"] += row
    tot = sum(viol.values())
    print(f"safe-area ink  L{viol['left']} R{viol['right']} T{viol['top']} B{viol['bottom']}",
          "OK" if tot == 0 else "!! OVERFLOW")

    # 区块墨迹 + 亮度
    print(f"{'band':<11}{'ink%':>7}{'mean':>8}  note")
    for name, a, b in BANDS:
        crop = im.crop((0, a, w, min(b, h)))
        data = list(crop.getdata())
        ink = sum(1 for v in data if v < 140) / len(data) * 100
        mean = sum(data) / len(data)
        note = ""
        if 0 < a < 145 and ink < 0.05:
            note = "!! EMPTY"
        print(f"{name:<11}{ink:>6.2f}%{mean:>8.1f}  {note}")

    allv = list(im.getdata())
    print(f"overall mean brightness {sum(allv)/len(allv):.1f}/255",
          "OK (bright)" if sum(allv) / len(allv) > 200 else "!! too dark")


for p in sys.argv[1:]:
    check(p)

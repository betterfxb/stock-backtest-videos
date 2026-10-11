"""验证固定轴 + 连续揭示：网格线行位置必须跨帧完全一致，粉色曲线像素必须单调增长。"""
import sys
from pathlib import Path
from PIL import Image
import numpy as np

OUT = Path(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\cambricon-video\out")
FRAMES = [240, 900, 1400, 1900, 2460]

GRID = np.array([0x22, 0x16, 0x1E])
PINK = np.array([0xF0, 0x48, 0x78])
INK = np.array([0xF0, 0xF0, 0xF0])


def load(f):
    return np.asarray(Image.open(OUT / f"s_{f}.png").convert("RGB")).astype(np.int16)


def near(px, ref, tol=14):
    return (np.abs(px - ref).max(axis=-1) <= tol)


def main():
    ref_rows = None
    print("frame | gridline rows (y)                     | pink px | curve x-extent | bg")
    for f in FRAMES:
        a = load(f)
        H, W, _ = a.shape

        # 绘图区内网格线：x 200..1000 连续长横线
        band = a[700:1300, 200:1000]
        gmask = near(band, GRID, 16)
        rowcnt = gmask.sum(axis=1)
        rows = [int(y + 700) for y in np.where(rowcnt > 700)[0]]

        # 粉色曲线像素 + 横向范围
        plot = a[790:1280, 80:1000]
        pmask = near(plot, PINK, 26)
        pink = int(pmask.sum())
        xs = np.where(pmask.any(axis=0))[0]
        xext = (int(xs.min() + 80), int(xs.max() + 80)) if xs.size else None

        bg = a[1700, 40].tolist()

        if ref_rows is None:
            ref_rows = rows
            mark = "(baseline)"
        else:
            mark = "SAME" if rows == ref_rows else f"!! MOVED (diff {set(rows) ^ set(ref_rows)})"

        print(f"{f:5d} | {str(rows):38s} | {pink:7d} | {str(xext):15s} | {bg} {mark}")

    # 单调性
    print()
    a = load(FRAMES[0])
    plot = a[790:1280, 80:1000]
    counts = [int(near(a[790:1280, 80:1000], PINK, 26).sum()) for _ in [0]]
    counts = []
    for f in FRAMES:
        b = load(f)
        counts.append(int(near(b[790:1280, 80:1000], PINK, 26).sum()))
    mono = all(counts[i] < counts[i + 1] for i in range(len(counts) - 1))
    print("pink pixel count:", counts, "-> strictly increasing:", mono)

    # 版面占用检查：关键 y 带是否有墨迹
    print()
    checks = {
        "readout 690-770": (690, 775),
        "plot 800-1270": (800, 1275),
        "axis 1325-1378": (1325, 1380),
        "stage 1390-1425": (1390, 1426),
        "counter 1450-1510": (1450, 1512),
        "eventcard 1552-1814": (1552, 1816),
        "compliance 1852-1920": (1852, 1920),
    }
    a = load(1400)
    for name, (y0, y1) in checks.items():
        seg = a[y0:y1]
        n_ink = int(near(seg, INK, 60).sum())
        n_pink = int(near(seg, PINK, 40).sum())
        flag = "OK " if (n_ink + n_pink) > 200 else "EMPTY"
        print(f"  {flag} {name:22s} ink={n_ink:6d} pink={n_pink:6d}")

    # 左右边界溢出
    marg = np.ones(a.shape[0], dtype=bool)
    left = int(near(a[:, 0:14], INK, 60).sum())
    right = int(near(a[:, 1066:1080], INK, 60).sum())
    print(f"  edge ink: left={left} right={right} (应接近 0，避免出血)")


if __name__ == "__main__":
    sys.exit(main())
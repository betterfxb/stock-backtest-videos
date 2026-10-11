import numpy as np, glob, os, json
from PIL import Image

D = r"C:\Users\19560\AppData\Local\Temp\opencode\ref2"
files = sorted(glob.glob(os.path.join(D, "r*.png")))

PINK = np.array([240, 72, 120])

def load(f):
    return np.asarray(Image.open(f).convert("RGB"), dtype=np.int16)

print("=== 粉色(240,72,120)像素逐帧追踪（每 0.5s）===")
print(f"{'帧':>4} {'秒':>5} {'像素数':>7} {'x范围':>11} {'y范围':>11} {'质心x':>6} {'质心y':>6}")
rows = []
for i, f in enumerate(files):
    a = load(f)
    d = np.abs(a - PINK).sum(axis=2)
    m = d < 90
    n = int(m.sum())
    t = i * 0.5
    if n < 30:
        rows.append((i, t, n, None))
        print(f"{i:>4} {t:>5.1f} {n:>7} {'-':>11} {'-':>11} {'-':>6} {'-':>6}")
        continue
    ys, xs = np.nonzero(m)
    rows.append((i, t, n, (xs.min(), xs.max(), ys.min(), ys.max(), xs.mean(), ys.mean())))
    print(f"{i:>4} {t:>5.1f} {n:>7} {f'{xs.min()}-{xs.max()}':>11} {f'{ys.min()}-{ys.max()}':>11} {xs.mean():>6.1f} {ys.mean():>6.1f}")

np.save(os.path.join(D, "pink.npy"), np.array([1]))
json.dump([(i, t, n, b) for i, t, n, b in rows], open(os.path.join(D, "pink.json"), "w"))
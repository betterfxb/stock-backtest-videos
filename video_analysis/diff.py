import numpy as np, glob, os
from PIL import Image

D = r"C:\Users\19560\AppData\Local\Temp\opencode\ref2"
files = sorted(glob.glob(os.path.join(D, "r*.png")))
N = len(files)

def load(f):
    return np.asarray(Image.open(f).convert("RGB"), dtype=np.int16)

prev = load(files[0])
print("=== 帧间差分：每 0.5s 相对上一帧，什么在动 ===")
print(f"{'帧':>4} {'秒':>5} {'变化像素':>8}  {'变化区域 x范围':>13} {'y范围':>11}   活动列数")
tot = []
for i in range(1, N):
    a = load(files[i])
    d = np.abs(a - prev).sum(axis=2)
    m = d > 70
    n = int(m.sum())
    t = i * 0.5
    if n < 100:
        print(f"{i:>4} {t:>5.1f} {n:>8}  {'静止':>13}")
        tot.append((i, t, n, None))
    else:
        ys, xs = np.nonzero(m)
        colcount = len(np.unique(xs))
        print(f"{i:>4} {t:>5.1f} {n:>8}  {f'{xs.min()}-{xs.max()}':>13} {f'{ys.min()}-{ys.max()}':>11}   {colcount}")
        tot.append((i, t, n, (xs.min(), xs.max(), ys.min(), ys.max())))
    prev = a

print("\n=== 静止帧占比 ===")
still = [t for i, t, n, b in tot if b is None]
print(f"完全静止的采样点: {len(still)}/{len(tot)}  -> {[round(x,1) for x in still]}")

print("\n=== 变化区域的纵向分布（活动集中在哪一层）===")
bands = np.zeros(10)
for i, t, n, b in tot:
    if b is None: continue
    a = load(files[i]); p = load(files[i-1])
    d = np.abs(a - p).sum(axis=2) > 70
    for k in range(10):
        y0, y1 = k * 102, (k + 1) * 102
        bands[k] += d[y0:y1].sum() / 1024
tot_sum = bands.sum()
for k in range(10):
    bar = "#" * int(bands[k] / tot_sum * 200)
    print(f"  y {k*102:>4}-{(k+1)*102:>4}  {bands[k]/tot_sum*100:5.1f}%  {bar}")
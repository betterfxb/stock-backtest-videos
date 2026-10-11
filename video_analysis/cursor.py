import numpy as np, glob, os
from PIL import Image

D = r"C:\Users\19560\AppData\Local\Temp\opencode\ref2"
files = sorted(glob.glob(os.path.join(D, "r*.png")))
Y0, Y1 = 405, 775
X0, X1 = 44, 532
NB = 43

print("=== 游标追踪（干净行进段 t=10..26）：每个 x 桶的墨迹 y 范围与质心 ===")
print(f"{'t':>5} {'桶':>3} {'x':>5} {'墨迹':>6} {'y最小':>6} {'y最大':>6} {'y质心':>7}  分布")
for i in range(20, 53):
    a = np.asarray(Image.open(files[i]).convert("RGB"), dtype=int)
    bg = np.median(a.reshape(-1, 3), axis=0)
    ink = (np.abs(a - bg).sum(axis=2) > 70)[Y0:Y1, X0:X1]
    xs = np.linspace(0, X1 - X0, NB + 1).astype(int)
    counts = np.array([ink[:, xs[b]:xs[b + 1]].sum() for b in range(NB)])
    b = int(counts.argmax())
    col = ink[:, xs[b]:xs[b + 1]]
    ys = np.nonzero(col)[0]
    if len(ys) == 0:
        continue
    span = ys.max() - ys.min() + 1
    ymin, ymax, ycen = ys.min() + Y0, ys.max() + Y0, ys.mean() + Y0
    bar = "#" * min(40, len(ys) // 3)
    print(f"{i*0.5:>5.1f} {b:>3} {int((xs[b]+xs[b+1])/2+X0):>5} {int(counts[b]):>6} {ymin:>6} {ymax:>6} {ycen:>7.0f}  {bar}")

print("\n=== 对照：同一时段最右侧固定元素（桶42）的 y 质心是否稳定 ===")
for i in range(20, 53, 3):
    a = np.asarray(Image.open(files[i]).convert("RGB"), dtype=int)
    bg = np.median(a.reshape(-1, 3), axis=0)
    ink = (np.abs(a - bg).sum(axis=2) > 70)[Y0:Y1, X0:X1]
    xs = np.linspace(0, X1 - X0, NB + 1).astype(int)
    col = ink[:, xs[40]:xs[41]]
    ys = np.nonzero(col)[0]
    print(f"t={i*0.5:>5.1f}s  桶40 x={int(xs[40]+X0)}  墨迹={len(ys):>5}  y质心={(ys.mean()+Y0 if len(ys) else -1):>6.0f}")
import numpy as np, glob, os
from PIL import Image

D = r"C:\Users\19560\AppData\Local\Temp\opencode\ref2"
files = sorted(glob.glob(os.path.join(D, "r*.png")))

Y0, Y1 = 405, 775
X0, X1 = 44, 532
NB = 43

print("=== 逐帧(0.5s)：图表区最右墨迹x / 墨迹最多的x桶 / 该桶坐标 / 总墨迹 ===")
print(f"{'帧':>4}{'t':>6} {'最右x':>6} {'峰值桶':>7} {'峰值桶x':>8} {'峰值像素':>8} {'总墨迹':>7}")
prev_peak = None
for i in range(3, len(files)):
    a = np.asarray(Image.open(files[i]).convert("RGB"), dtype=int)
    bg = np.median(a.reshape(-1, 3), axis=0)
    ink = (np.abs(a - bg).sum(axis=2) > 70)[Y0:Y1, X0:X1]
    xs = np.linspace(0, X1 - X0, NB + 1).astype(int)
    counts = np.array([ink[:, xs[b]:xs[b + 1]].sum() for b in range(NB)])
    live = np.nonzero(counts > 25)[0]
    if len(live) == 0:
        print(f"{i:>4}{i*0.5:>6.1f}  空")
        continue
    right = int(xs[live[-1] + 1] + X0)
    pk = int(counts.argmax())
    pkx = int((xs[pk] + xs[pk + 1]) / 2 + X0)
    mark = ""
    if prev_peak is not None and pk != prev_peak:
        mark = f"  <-- 峰值左移 {prev_peak-pk} 桶"
    prev_peak = pk
    print(f"{i:>4}{i*0.5:>6.1f} {right:>6} {pk:>7} {pkx:>8} {counts[pk]:>8} {int(ink.sum()):>7}{mark}")
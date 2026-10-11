import numpy as np, glob, os
from PIL import Image
from scipy import ndimage

D = r"C:\Users\19560\AppData\Local\Temp\opencode\ref2"
files = sorted(glob.glob(os.path.join(D, "r*.png")))

def clusters(a):
    q = (a.astype(int) // 40) * 40
    key = q[:, :, 0].astype(np.int32) * 4096 + q[:, :, 1].astype(np.int32) * 64 + q[:, :, 2].astype(np.int32)
    return key

def report(idx):
    a = np.asarray(Image.open(files[idx]).convert("RGB"), dtype=int)
    bg = np.median(a.reshape(-1, 3), axis=0)
    ink = np.abs(a - bg).sum(axis=2) > 70
    key = clusters(a)
    key[~ink] = -1
    print(f"\n{'='*104}\n=== 帧 {idx}  t={idx*0.5:.1f}s   背景 RGB{tuple(int(x) for x in bg)}\n{'='*104}")
    out = []
    for k in np.unique(key):
        if k < 0: continue
        m = key == k
        if m.sum() < 400: continue
        lab, n = ndimage.label(m, structure=np.ones((3, 3)))
        for i in range(1, n + 1):
            comp = lab == i
            area = int(comp.sum())
            if area < 500: continue
            ys, xs = np.nonzero(comp)
            mean = a[comp].mean(axis=0).astype(int)
            out.append((area, xs.min(), xs.max(), ys.min(), ys.max(), tuple(mean), xs.mean()))
    out.sort(key=lambda r: -r[0])
    print(f"{'面积':>7} {'x范围':>11} {'y范围':>11} {'均色':>17} {'质心x':>6}")
    for area, x0, x1, y0, y1, col, cx in out[:12]:
        print(f"{area:>7} {f'{x0}-{x1}':>11} {f'{y0}-{y1}':>11} {str(col):>17} {cx:>6.0f}")

for idx in [4, 10, 12, 30, 60, 90, 120, 150, 168]:
    report(idx)
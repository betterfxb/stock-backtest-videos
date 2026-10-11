"""用强对比阈值排除柔光渐变，测真实内容包围盒；重点看后段帧。"""
import glob, os
import numpy as np
from PIL import Image

TMP = r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\video_analysis\_safe_frames"
files = sorted(glob.glob(os.path.join(TMP, "*.png")))

print("=== 真实内容包围盒（阈值 60，排除满宽色条/合规条） ===")
g = {}
for i, f in enumerate(files):
    a = np.asarray(Image.open(f).convert("RGB")).astype(np.int16)
    bg = np.median(a.reshape(-1, 3), axis=0)
    c = np.abs(a - bg).max(axis=-1) > 60
    c[:12, :] = False
    c[1852:, :] = False
    ys, xs = np.where(c)
    if xs.size == 0:
        print(f"  帧{i:2d}: 无"); continue
    l, r, t, b = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    g[i] = (l, r, t, b)
    print(f"  帧{i:2d}: x={l:4d}..{r:4d} (边距 {l}/{1079-r})  y={t:4d}..{b:4d} (边距 {t}/{1919-b})")

if g:
    print(f"\n全局: x={min(v[0] for v in g.values())}..{max(v[1] for v in g.values())}  "
          f"y={min(v[2] for v in g.values())}..{max(v[3] for v in g.values())}")

print("\n=== 后段帧右边缘 x>1000 的内容（帧9-12） ===")
for i in (9, 10, 11, 12):
    if i >= len(files): continue
    a = np.asarray(Image.open(files[i]).convert("RGB")).astype(np.int16)
    bg = np.median(a.reshape(-1, 3), axis=0)
    c = np.abs(a - bg).max(axis=-1) > 60
    for x in (1000, 1020, 1040, 1060, 1079):
        ys = np.where(c[:, x])[0]
        if ys.size == 0:
            continue
        px = tuple(int(v) for v in a[ys[len(ys)//2], x])
        print(f"  帧{i} x={x:4d}: {ys.size:4d}px y={ys.min():4d}..{ys.max():4d} {px}")

print("\n=== 底部分行密度（帧4，y>1400） ===")
a = np.asarray(Image.open(files[4]).convert("RGB")).astype(np.int16)
bg = np.median(a.reshape(-1, 3), axis=0)
c = np.abs(a - bg).max(axis=-1) > 60
c[:12, :] = False
rowcnt = c.sum(axis=1)
for y in range(1400, 1920, 20):
    print(f"  y{y:4d}-{y+19:4d}: {rowcnt[y:y+20].mean():7.1f} px/行")
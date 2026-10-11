"""定位哪些元素顶到画布边缘：分列/分行密度 + 边缘元素的颜色归属。"""
import glob, os
import numpy as np
from PIL import Image

TMP = r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\video_analysis\_safe_frames"
files = sorted(glob.glob(os.path.join(TMP, "*.png")))
PINK = np.array([0xF0, 0x48, 0x78])
INK = np.array([0xF0, 0xF0, 0xF0])

print("=== 左边缘 x=0..40 内容归属（帧1/4/11/12） ===")
for i in (1, 4, 11, 12):
    a = np.asarray(Image.open(files[i]).convert("RGB")).astype(np.int16)
    bg = np.median(a.reshape(-1, 3), axis=0)
    c = np.abs(a - bg).max(axis=-1) > 25
    for x in range(0, 40, 8):
        col = c[:, x]
        ys = np.where(col)[0]
        if ys.size == 0:
            continue
        px = a[ys[len(ys)//2], x]
        kind = "粉" if np.abs(px-PINK).max() < 50 else ("白" if np.abs(px-INK).max() < 40 else "暗/其他")
        print(f"  帧{i:2d} x={x:3d}: {ys.size:4d}px  y={ys.min():4d}..{ys.max():4d}  {kind} {tuple(px)}")

print("\n=== 右边缘 x=1040..1079 内容归属 ===")
for i in (1, 4, 11, 12):
    a = np.asarray(Image.open(files[i]).convert("RGB")).astype(np.int16)
    bg = np.median(a.reshape(-1, 3), axis=0)
    c = np.abs(a - bg).max(axis=-1) > 25
    for x in range(1040, 1080, 8):
        ys = np.where(c[:, x])[0]
        if ys.size == 0:
            continue
        px = a[ys[len(ys)//2], x]
        kind = "粉" if np.abs(px-PINK).max() < 50 else ("白" if np.abs(px-INK).max() < 40 else "暗/其他")
        print(f"  帧{i:2d} x={x:4d}: {ys.size:4d}px  y={ys.min():4d}..{ys.max():4d}  {kind} {tuple(px)}")

print("\n=== 顶部 y=0..12 满宽色条? ===")
a = np.asarray(Image.open(files[4]).convert("RGB")).astype(np.int16)
print(f"  y=0..5 颜色: {tuple(a[2,540])}  y=12..16: {tuple(a[14,540])}")

print("\n=== 底部 y>1850 合规条? ===")
print(f"  y=1860 颜色: {tuple(a[1860,540])}")

print("\n=== 主体内容（排除满宽色条与合规条）分列密度，帧4 ===")
c = np.abs(a - np.median(a.reshape(-1,3),axis=0)).max(axis=-1) > 25
c[:12,:]=False; c[1852:,:]=False
colcnt = c.sum(axis=0)
for x in range(0, 1080, 40):
    seg = colcnt[x:x+40]
    print(f"  x{x:4d}-{x+39:4d}: {seg.mean():7.1f} px/列")
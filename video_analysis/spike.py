# -*- coding: utf-8 -*-
"""孤立尖峰检测：真正的硬切 = 单帧变化远高于前后帧；持续高变化 = 正常运动"""
import numpy as np, glob, os, sys
from PIL import Image

def diffs(d, x0=759, x1=1421):
    fs = sorted(glob.glob(os.path.join(d, "*.png")))
    prev, ds = None, []
    for f in fs:
        a = np.asarray(Image.open(f).convert("RGB"), dtype=int)[x0:x1, 95:880]
        if prev is not None:
            ds.append(int((np.abs(a - prev).sum(axis=2) > 70).sum()))
        prev = a
    return np.array(ds)

for tag, d in [("v1 粘性轴", r"C:\Users\19560\AppData\Local\Temp\opencode\fullchk"),
               ("v2 固定轴", r"C:\Users\19560\AppData\Local\Temp\opencode\full2chk")]:
    if not os.path.isdir(d):
        print(tag, "缺目录"); continue
    ds = diffs(d)
    # 孤立尖峰：该帧 > 4x 中位 且 > 2.5x 前后各3帧的均值
    med = np.median(ds)
    iso = []
    for i in range(3, len(ds) - 3):
        nb = (ds[i-3:i] .mean() + ds[i+1:i+4].mean()) / 2
        if ds[i] > med * 3 and ds[i] > nb * 2.5:
            iso.append((i + 1, round((i + 1) / 30.0, 2), int(ds[i]), int(nb)))
    print(f"\n=== {tag} ===")
    print(f"  帧数 {len(ds)+1}  中位变化 {int(med)}  均值 {int(ds.mean())}  最大 {ds.max()}")
    print(f"  孤立尖峰（硬切）数量: {len(iso)}")
    for fr, t, v, nb in iso[:10]:
        print(f"    帧 {fr:>4}  t={t:>5.2f}s  变化 {v:>6}  邻帧均值 {nb:>5}  倍数 {v/max(nb,1):.1f}x")
    # 持续高变化段
    hi = ds > med * 3
    runs, s = [], None
    for i, v in enumerate(hi):
        if v and s is None: s = i
        elif not v and s is not None:
            runs.append((s, i - 1)); s = None
    if s is not None: runs.append((s, len(hi) - 1))
    long_runs = [r for r in runs if r[1] - r[0] > 3]
    print(f"  持续高变化段（>4帧，属正常连续运动）: {[(a+1,b+1) for a,b in long_runs][:6]}")
    print(f"  单帧尖峰（仅1-2帧）: {[(a+1,b+1) for a,b in runs if b-a<2][:10]}")
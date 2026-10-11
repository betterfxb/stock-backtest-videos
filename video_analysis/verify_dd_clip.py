from pathlib import Path
from PIL import Image
import numpy as np

OUT = Path(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\cambricon-video\out")
DD = (62, 22, 32)
PX0, PX1, N = 80.0, 1000.0, 44.0
DD_START = PX0 + (PX1 - PX0) * 4 / N

print("frame   kf    期望揭示右界   DD实达右界   判定")
for f in (150, 900, 1400, 1900, 2460):
    a = np.asarray(Image.open(OUT / f"x_{f}.png").convert("RGB")).astype(int)
    seg = a[800:1270, :]
    m = (seg[:, :, 0] == DD[0]) & (seg[:, :, 1] == DD[1]) & (seg[:, :, 2] == DD[2])
    ys, xs = np.where(m)
    kf = (f - 150) / (2460 - 150) * N
    exp = PX0 + (PX1 - PX0) * kf / N
    r = int(xs.max()) if m.sum() else None
    l = int(xs.min()) if m.sum() else None
    if r is None:
        ok = exp < DD_START + 1
        verdict = "OK 未到 DD 段" if ok else "!! 异常"
    else:
        ok = r <= exp + 2 and l >= DD_START - 2
        verdict = "OK 被笔尖裁住" if ok else "!! 越过笔尖"
    print(f"{f:5d} {kf:6.2f}  {exp:11.1f}   {str(r):>8}   {verdict}  (左界 {l})")

print()
print(f"DD 段起点 x={DD_START:.1f}，frame150 揭示右界仅 {PX0+10:.0f}px，不应出现 DD")
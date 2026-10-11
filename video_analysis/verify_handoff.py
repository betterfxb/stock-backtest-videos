"""末段镜头交还的平滑性：smoothstep 在 t=0 处导数为 0，
因此 kf=TAIL_KF 两侧的播放头速度应完全连续，不产生速度突变。"""
import numpy as np

N, WIN, LOCK, TAIL_KF, TAIL_END = 44.0, 13.0, 0.26, 30.0, 0.94
F0, F1 = 150, 2460


def frac(kf):
    t = min(max((kf - TAIL_KF) / (N - TAIL_KF), 0.0), 1.0)
    e = t * t * (3 - 2 * t)
    return LOCK + (TAIL_END - LOCK) * e


def cam(f):
    kf = (f - F0) / (F1 - F0) * N
    fr = frac(kf)
    return kf, fr, kf - WIN * fr


print("交接点 frame = 150 + 30/44*(2460-150) =", 150 + 30 / 44 * (F1 - F0))
print()
print("frame   kf      frac       L        d(playhead x)/df   d(L)/df")
prev = None
worst_ph = 0.0
worst_L = 0.0
for f in range(1700, 1780, 4):
    kf, fr, L = cam(f)
    phx = 80 + 920 * fr
    if prev:
        dph = (phx - prev[0]) / (f - prev[2])
        dL = (L - prev[1]) / (f - prev[2])
        print(f"{f:5d} {kf:6.3f}  {fr:8.5f}  {L:8.3f}   {dph:12.5f}  {dL:9.5f}")
        if abs(f - 1725) <= 8:
            worst_ph = max(worst_ph, abs(dph))
            worst_L = max(worst_L, abs(dL))
    prev = (phx, L, f)

print()
print(f"交接点 ±8 帧内播放头速度最大波动 = {worst_ph:.5f} px/frame")
print(f"交接点 ±8 帧内窗口速度最大波动   = {worst_L:.5f} index/frame")
print()
# 全程速度单调性：播放头速度应始终 >= 0，窗口速度应始终 > 0
ph = []
Ls = []
for f in range(F0, F1 + 1):
    kf, fr, L = cam(f)
    ph.append(80 + 920 * fr)
    Ls.append(L)
dph = np.diff(ph)
dL = np.diff(Ls)
print(f"全程播放头速度: min={dph.min():.5f} max={dph.max():.5f} 恒非负={bool((dph >= -1e-12).all())}")
print(f"全程窗口速度:   min={dL.min():.5f} max={dL.max():.5f} 恒为正={bool((dL > 0).all())}")
print()
# 加速度最大值 -> 决定 jerk 感知
acc = np.diff(dph)
print(f"播放头加速度: min={acc.min():.5f} max={acc.max():.5f}（平滑, 无突变）")
print(f"窗口加速度:   min={np.diff(dL).min():.5f} max={np.diff(dL).max():.5f}")
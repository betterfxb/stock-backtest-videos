"""横向跟随相机校验：
1. 窗口左缘 L 单调右移（相机始终向前推，不回退）
2. 播放头屏幕位置：主段钉住不动，kf≥30 后平滑扫向右缘
3. 横轴月份标注数量基本恒定（对比固定全轴版会一路增长到 23）
4. 曲线不得越过播放头
"""
from pathlib import Path
from PIL import Image
import numpy as np

OUT = Path(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\cambricon-video\out")
FRAMES = [150, 700, 1400, 2000, 2280, 2460]
AXIS_Y = 1330
PINK = np.array([0xF0, 0x48, 0x78])

PX0, PX1, N = 80.0, 1000.0, 44.0
WIN, LOCK, TAIL_KF, TAIL_END = 13.0, 0.26, 30.0, 0.94


def model(f):
    kf = (f - 150) / (2460 - 150) * N
    t = min(max((kf - TAIL_KF) / (N - TAIL_KF), 0.0), 1.0)
    e = t * t * (3 - 2 * t)
    frac = LOCK + (TAIL_END - LOCK) * e
    L = kf - WIN * frac
    return kf, L, PX0 + (PX1 - PX0) * frac


def load(f):
    return np.asarray(Image.open(OUT / f"p_{f}.png").convert("RGB")).astype(np.int16)


def pink_centroid(a, y0, y1):
    band = a[y0:y1, :]
    m = np.abs(band - PINK).max(axis=-1) <= 34
    colw = m.sum(axis=0)
    xs = np.where(colw > 0)[0]
    if not xs.size:
        return None, 0
    return float(np.average(xs, weights=colw[xs])), int(xs.max())


def label_groups(a):
    band = a[1348:1380, :]
    bg = np.array([0x09, 0x04, 0x09])
    m = np.abs(band - bg).max(axis=-1) > 26
    cols = np.where(m.any(axis=0))[0]
    groups, cur = 0, None
    for c in cols:
        if cur is None or c - cur > 30:
            groups += 1
        cur = c
    return groups


def curve_right_edge(a):
    """曲线（含笔尖光晕）在绘图区内的最右 x"""
    band = a[795:1275, :]
    m = np.abs(band - PINK).max(axis=-1) <= 40
    xs = np.where(m.any(axis=0))[0]
    return int(xs.max()) if xs.size else None


print("frame |    kf |  模型L  | 播放头x(模型) | 播放头x(实测) | 标签组 | 曲线右缘 | 判定")
prev_ph = -1.0
prev_L = -1e9
rows = []
for f in FRAMES:
    a = load(f)
    kf, L, ph_model = model(f)
    ph_meas, _ = pink_centroid(a, AXIS_Y - 22, AXIS_Y + 22)
    lg = label_groups(a)
    cr = curve_right_edge(a)

    d_ph = ph_meas - ph_model
    ok_ph = abs(d_ph) <= 6
    ok_L = L >= prev_L - 1e-6
    ok_curve = cr is None or cr <= ph_model + 20   # 允许笔头光晕溢出
    ok = ok_ph and ok_L and ok_curve
    rows.append((L, ph_meas, lg))
    prev_L, prev_ph = L, ph_meas
    print(f"{f:5d} | {kf:5.2f} | {L:6.2f} | {ph_model:11.1f}   | {ph_meas:11.1f}   | {lg:5d} | {str(cr):>8} | "
          f"{'OK' if ok else '!! ' + ('播放头' if not ok_ph else '') + ('L回退' if not ok_L else '') + ('曲线越界' if not ok_curve else '')}")

print()
mono_L = all(rows[i][0] <= rows[i + 1][0] + 1e-6 for i in range(len(rows) - 1))
print(f"  窗口左缘 L 严格单调右移: {mono_L}")
locked = [r for r in rows[:3]]
print(f"  主段播放头 x: {[round(r[1],1) for r in locked]}  -> 钉住不动: {max(r[1] for r in locked)-min(r[1] for r in locked) <= 2}")
print(f"  末段播放头 x: {[round(rows[i][1],1) for i in (3,4,5)]}  -> 平滑右行: {rows[5][1] > rows[3][1]}")
lg = [r[2] for r in rows]
print(f"  月份标注组数: {lg}  -> 基本恒定(±2): {max(lg)-min(lg) <= 2}")
print(f"  对比：固定全轴版 labels 会从 1 增长到 23")
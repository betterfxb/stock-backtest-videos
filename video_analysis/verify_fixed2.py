import sys
from pathlib import Path
from PIL import Image
import numpy as np

OUT = Path(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\cambricon-video\out")
FRAMES = [240, 900, 1400, 1900, 2460]
GRID = np.array([0x22, 0x16, 0x1E])
BG = np.array([0x09, 0x04, 0x09])


def load(f):
    return np.asarray(Image.open(OUT / f"s_{f}.png").convert("RGB")).astype(np.int16)


def rows_of(a):
    band = a[700:1300, 200:1000]
    m = (np.abs(band - GRID).max(axis=-1) <= 16)
    return set(int(y + 700) for y in np.where(m.sum(axis=1) > 700)[0])


sets = {f: rows_of(load(f)) for f in FRAMES}
base = sets[FRAMES[0]]

print("=== 网格线行位置：判据是「是否出现基准里没有的新行」 ===")
ok = True
for f in FRAMES:
    new = sets[f] - base
    lost = base - sets[f]
    if new:
        ok = False
    print(f"  frame {f:5d}: 新增行={sorted(new) or '无'}  被曲线遮挡消失={sorted(lost) or '无'}")
print(f"  => 无任何新网格线位置出现：{ok}（新增行只在粘性轴时出现）")

print()
print("=== 预期固定刻度位置（yMAX=4000, 绘图区 800..1270） ===")
for v, exp in [(4000, 800), (3000, 917.5), (2000, 1035), (1000, 1152.5), (0, 1270)]:
    hit = [r for r in base if abs(r - exp) <= 2]
    print(f"  {v:>5} 万 -> 期望 y≈{exp:<7} 实测 {hit or '被遮挡'}")

print()
print("=== 内容占用复核（含暗灰文字） ===")
for f, y0, y1, name in [(1400, 690, 775, "实时读数"), (1400, 1325, 1382, "时间轴标签"),
                        (1400, 1390, 1426, "阶段条"), (1400, 1450, 1512, "进度计数"),
                        (1400, 1552, 1816, "事件卡"), (1400, 1852, 1920, "合规条"),
                        (240, 0, 1852, "开场钩子整屏")]:
    a = load(f)[y0:y1]
    nonbg = int((np.abs(a - BG).max(axis=-1) > 22).sum())
    print(f"  {'OK ' if nonbg > 300 else 'EMPTY'} frame{f:<5d} {name:14s} y{y0}-{y1}  非背景像素={nonbg}")

print()
print("=== 开场钩子数值滚动（frame 8->72 应 0 -> 2484.66 万） ===")
for f in (8, 30, 50, 72):
    a = load(f)[470:800]
    p = (np.abs(a - np.array([0xF0, 0x48, 0x78])).max(axis=-1) <= 30).sum()
    print(f"  frame {f:3d}: 粉色数字像素={p}")
print("  => 单调增长说明在滚动计数而非硬切")

print()
print("=== 事件卡交叉淡化（应连续，无突跳） ===")
a = load(1400)
print(f"  frame 1400 事件卡墨迹={int((np.abs(a[1552:1816] - BG).max(axis=-1) > 22).sum())}")
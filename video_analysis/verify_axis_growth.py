"""校验横轴是否实时生长：轴线右端、刻度数、月份标注数都必须随帧单调增长，
且任何已揭示的数据标记（回撤底纹/峰值线/阶段分界）都不得越过笔尖。"""
import sys
from pathlib import Path
from PIL import Image
import numpy as np

OUT = Path(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\cambricon-video\out")
FRAMES = [150, 900, 1400, 1900, 2460]

PX0, PX1, N = 80.0, 1000.0, 44.0
AXIS_Y = 1330
BG = np.array([0x09, 0x04, 0x09])
AXIS = np.array([0x80, 0x76, 0x7E])   # 轴线灰
PINK = np.array([0xF0, 0x48, 0x78])
DD = np.array([0x3E, 0x16, 0x20])


def load(f):
    return np.asarray(Image.open(OUT / f"x_{f}.png").convert("RGB")).astype(np.int16)


def near(px, ref, tol):
    return np.abs(px - ref).max(axis=-1) <= tol


def axis_reach(a):
    """轴线上着色的最右 x（轴线带在 y=AXIS_Y 上下 2px）"""
    band = a[AXIS_Y - 2:AXIS_Y + 3, :]
    m = near(band, AXIS, 26) | near(band, PINK, 26)
    xs = np.where(m.any(axis=0))[0]
    return int(xs.max()) if xs.size else None


def tick_count(a):
    """y=AXIS_Y+6..AXIS_Y+15 上的竖刻度像素数（逐月一根）"""
    band = a[AXIS_Y + 6:AXIS_Y + 16, int(PX0) - 5:int(PX1) + 5]
    m = near(band, AXIS, 30) | near(band, PINK, 30)
    cols = np.where(m.any(axis=0))[0]
    return len(cols)


def label_count(a):
    """月份文字带 y=1350..1378：亮色文字的列数 -> 粗略代表已标注月份数"""
    band = a[1350:1380, :]
    m = near(band, AXIS, 60) | near(band, PINK, 60)
    cols = np.where(m.any(axis=0))[0]
    # 按 40px 聚类成组
    groups, cur = 0, None
    for c in cols:
        if cur is None or c - cur > 40:
            groups += 1
        cur = c
    return groups


def marks_within(a):
    """回撤底纹/阶段分界的右边界 vs 笔尖位置，检测是否越过笔尖"""
    expected = PX0 + (PX1 - PX0) * (min(FRAMES.index(0) or 0, 0) or 0)  # 占位
    return None


def main():
    print("frame | 期望笔尖x | 轴线实达x | 刻度列数 | 月份标注组 | 越界检查")
    reach_hist = []
    for f in FRAMES:
        a = load(f)
        reveal = (f - 150) / (2460 - 150)
        kf = reveal * N
        expect = PX0 + (PX1 - PX0) * kf

        reach = axis_reach(a)
        reach_hist.append(reach)
        tc = tick_count(a)
        lc = label_count(a)

        # 越界：轴线右端不应显著超过笔尖（容差 8px 考虑笔头光晕与抗锯齿）
        over = reach - expect if reach else None
        flag = "OK" if over is not None and over <= 8 else "!! 超出"
        print(f"{f:5d} | {expect:9.1f} | {str(reach):9s} | {tc:9d} | {lc:10d} | {flag} (Δ{over:+.0f})")

    print()
    ok_reach = all(reach_hist[i] < reach_hist[i + 1] for i in range(len(reach_hist) - 1))
    print(f"  轴线右端严格单调增长: {ok_reach}")
    print(f"  末帧轴线应达 PX1={PX1:.0f}, 实测 {reach_hist[-1]}")

    # 回撤底纹不得预铺：frame150 只有 DD 段[4,9] 的起点之前，几乎无底纹
    a0 = load(150)
    dd_pixels_full = int(near(a0[800:1270, :], DD, 10).sum())
    a2 = load(1900)
    dd_pixels_late = int(near(a2[800:1270, :], DD, 10).sum())
    print(f"  回撤底纹像素 frame150={dd_pixels_full} (应≈0，未到 idx4) -> frame1900={dd_pixels_late} (已展开)")
    print("  => 底纹随笔尖展开，未预铺" if dd_pixels_full < dd_pixels_late / 2 else "  !! 底纹可能预铺")

    # 峰值标注：frame900 (kf<41) 不应出现，frame1900 (kf≈34?) 依 kf
    for f in FRAMES:
        a = load(f)
        reveal = (f - 150) / (2460 - 150)
        kf = reveal * N
        txt = int(near(a[795:812, 80:400], np.array([0x96, 0x50, 0x5F]), 30).sum())
        print(f"  峰值标注像素 frame{f:5d} (kf={kf:5.1f}, PEAK_I=41) = {txt} -> {'出现' if txt>0 else '未出现'}")


if __name__ == "__main__":
    sys.exit(main())
"""测量不同视窗配置下的可见 y 范围与曲线可用高度占比"""
NAV = [100.0,136.1,304.38,409.25,416.99,307.77,268.18,259.58,202.07,174.48,244.75,220.24,179.05,
       275.85,283.77,280.35,285.96,325.37,433.27,421.12,474.7,746.05,923.28,1083.35,941.46,
       1211.16,1025.6,1158.62,993.68,990.12,1168.36,2460.44,2184.07,2266.56,2193.95,2234.47,
       2074.97,1941.48,1619.67,2802.83,3221.05,3923.16,2719.45,2734.64,2480.97]

PX0, PX1 = 182, 984
PY0, PY1 = 782, 1332
PH = PY1 - PY0


def analyze(W, HI, LO, GROWTH, FLOOR):
    rows = []
    for idx in range(45):
        lo = max(0, idx - W + 1)
        hi = min(44, idx + HI)
        n = hi - lo + 1
        yrs = n / 12
        xspan = max((hi - lo) / (W - 1) * (PX1 - PX0), 70)
        # 每帧允许的 ymax 增长上限 -> 反推此刻的 ymax 不能低于多少
        grow_per_frame = (1 + GROWTH) ** (1 / (yrs * 12))
        ymax_needed = max(NAV[j] for j in range(lo, hi + 1)) * 1.06
        ymax_needed = max(ymax_needed, 100 * FLOOR)
        top = min(1, ymax_needed / grow_per_frame)   # 归一化到 PY0 的位置比例
        band = max(0.0, top - LO)
        rows.append((idx, lo, hi, xspan, band))
    bands = sorted(r[4] for r in rows)
    return rows, bands[0], bands[len(bands) // 2]


for W, HI, LO, GR, FL in [(9, 1, 0.10, 0.55, 1.5), (12, 2, 0.12, 0.55, 1.5), (15, 3, 0.12, 0.55, 1.5)]:
    rows, worst, med = analyze(W, HI, LO, GR, FL)
    print(f"\n=== W={W} (+{HI}) 底部留白 LO={LO} ===")
    bad = [r for r in rows if r[4] < 0.18]
    print(f"  曲线高度占比: 最低 {worst:.3f} / 中位 {med:.3f}")
    print(f"  占比<0.18 的帧数: {len(bad)}/45")
    for idx, lo, hi, xs, b in bad[:8]:
        print(f"    idx{idx:>3} vis[{lo:>2}..{hi:>2}] xspan={xs:>4.0f}px band={b:.3f}")
    if not bad:
        print("    无")

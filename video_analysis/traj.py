import numpy as np, glob, os
from PIL import Image

D = r"C:\Users\19560\AppData\Local\Temp\opencode\ref2"
files = sorted(glob.glob(os.path.join(D, "r*.png")))

Y0, Y1 = 405, 775          # 图表带（排除顶部文字 296-400 与底部条 778-801）
X0, X1 = 44, 532
NB = 49                    # x 分桶数

def profile(idx):
    a = np.asarray(Image.open(files[idx]).convert("RGB"), dtype=int)
    bg = np.median(a.reshape(-1, 3), axis=0)
    ink = (np.abs(a - bg).sum(axis=2) > 70)[Y0:Y1, X0:X1]
    xs = np.linspace(0, X1 - X0, NB + 1).astype(int)
    cy, cnt = [], []
    for i in range(NB):
        blk = ink[:, xs[i]:xs[i + 1]]
        n = int(blk.sum())
        cnt.append(n)
        cy.append(round(float(np.nonzero(blk)[0].mean() + Y0), 0) if n > 25 else -1)
    return cy, cnt

frames = [4, 8, 12, 16, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 168]
print("=== 各 x 桶的墨迹质心 y（-1 = 该列无内容）；列 = x 从 44 到 532 ===")
print(f"{'t(s)':>5} " + " ".join(f"{c:>4}" for c in range(NB)))
store = {}
for idx in frames:
    cy, cnt = profile(idx)
    store[idx] = (cy, cnt)
    print(f"{idx*0.5:>5.1f} " + " ".join(f"{v:>4.0f}" if v > 0 else "   ." for v in cy))

print("\n=== 每帧有内容的 x 桶数（判断曲线是否横向生长/平移）===")
for idx in frames:
    cy, cnt = store[idx]
    live = [i for i, v in enumerate(cy) if v > 0]
    print(f"t={idx*0.5:>5.1f}s  活跃桶 {len(live):>2}/{NB}  范围 桶{live[0] if live else '-'}..桶{live[-1] if live else '-'}")

print("\n=== 墨迹总量（判断整体在长大还是在移动）===")
for idx in frames:
    cy, cnt = store[idx]
    print(f"t={idx*0.5:>5.1f}s  图表区墨迹 {sum(cnt):>6} px")
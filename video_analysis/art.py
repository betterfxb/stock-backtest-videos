import numpy as np, glob, os
from PIL import Image

D = r"C:\Users\19560\AppData\Local\Temp\opencode\ref2"
files = sorted(glob.glob(os.path.join(D, "r*.png")))

Y0, Y1 = 296, 824
X0, X1 = 40, 536
CW, CH = 116, 46   # 输出列/行

def art(idx, label):
    a = np.asarray(Image.open(files[idx]).convert("RGB"), dtype=np.int16)
    reg = a[Y0:Y1, X0:X1]
    bg = np.median(a.reshape(-1, 3), axis=0)
    ink = np.abs(reg - bg).sum(axis=2) > 70
    h, w = ink.shape
    ys = np.linspace(0, h, CH + 1).astype(int)
    xs = np.linspace(0, w, CW + 1).astype(int)
    print(f"\n{'='*CW}\n=== {label} (帧{idx} t={idx*0.5:.1f}s)  图区 y{Y0}-{Y1} x{X0}-{X1}\n{'='*CW}")
    for r in range(CH):
        line = ""
        for c in range(CW):
            blk = ink[ys[r]:max(ys[r+1], ys[r]+1), xs[c]:max(xs[c+1], xs[c]+1)]
            f = blk.mean() if blk.size else 0
            line += " " if f < 0.06 else ("." if f < 0.25 else ("+" if f < 0.55 else "#"))
        print(f"{Y0 + int(ys[r]):>4}|{line}")

for idx, lab in [(4, "硬切后第一帧"), (12, "运行中"), (60, "运行中"), (120, "运行中")]:
    art(idx, lab)
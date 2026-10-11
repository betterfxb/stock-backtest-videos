import numpy as np, glob, os
from PIL import Image

D = r"C:\Users\19560\AppData\Local\Temp\opencode\ref"
files = sorted(glob.glob(os.path.join(D, "r*.png")))
print(f"帧数 {len(files)}  尺寸 {Image.open(files[0]).size}\n")

def palette(a, top=6):
    q = (a // 24) * 24
    cols, cnt = np.unique(q.reshape(-1, 3), axis=0, return_counts=True)
    idx = np.argsort(-cnt)[:top]
    out = []
    for i in idx:
        r, g, b = cols[i]
        out.append((tuple(int(x) for x in (r, g, b)), cnt[i] / a.shape[0] / a.shape[1] * 100))
    return out

print("=== 全片主色构成（采样 10 帧） ===")
acc = np.zeros(3)
for f in files[::5]:
    a = np.asarray(Image.open(f).convert("RGB"), dtype=float)
    acc += a.reshape(-1, 3).mean(axis=0)
print(f"全局均色 RGB = {tuple(int(x) for x in acc/len(files[::5]))}\n")

for f in files[:4]:
    a = np.asarray(Image.open(f).convert("RGB"), dtype=float)
    print(f"--- {os.path.basename(f)} ---")
    for c, p in palette(a):
        print(f"  RGB{c}  占{p:5.1f}%")
    print()

print("=== 逐帧：背景色 + 非背景像素的纵向分布（判断版式分层） ===")
for f in files:
    a = np.asarray(Image.open(f).convert("RGB"), dtype=float)
    bg = np.median(a.reshape(-1, 3), axis=0)
    d = np.abs(a - bg).sum(axis=2)
    ink = d > 60
    rows = ink.sum(axis=1)
    H = a.shape[0]
    # 找出有内容的连续行段
    segs, s = [], None
    for y in range(H):
        if rows[y] > 3 and s is None:
            s = y
        elif rows[y] <= 3 and s is not None:
            if y - s > 8: segs.append((s, y))
            s = None
    if s is not None: segs.append((s, H))
    desc = " ".join(f"{y0}-{y1}" for y0, y1 in segs)
    print(f"{os.path.basename(f)} bg={tuple(int(x) for x in bg)} ink={ink.sum()/1000:6.1f}k  行段: {desc}")
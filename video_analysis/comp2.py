import numpy as np, glob, os
from collections import deque
from PIL import Image

D = r"C:\Users\19560\AppData\Local\Temp\opencode\ref2"
files = sorted(glob.glob(os.path.join(D, "r*.png")))

def components(mask, minarea=500):
    H, W = mask.shape
    lab = np.zeros((H, W), dtype=np.int32)
    cur = 0
    out = []
    for sy in range(H):
        row = mask[sy]
        for sx in np.nonzero(row)[0]:
            if lab[sy, sx]: continue
            cur += 1
            q = deque([(sy, sx)])
            lab[sy, sx] = cur
            cnt = 0
            x0 = x1 = sx; y0 = y1 = sy
            while q:
                y, x = q.popleft()
                cnt += 1
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = cur
                            q.append((ny, nx))
            if cnt >= minarea:
                out.append((cnt, x0, x1, y0, y1, cur))
    return out, lab

def report(idx):
    a = np.asarray(Image.open(files[idx]).convert("RGB"), dtype=int)
    bg = np.median(a.reshape(-1, 3), axis=0)
    ink = np.abs(a - bg).sum(axis=2) > 70
    q = (a // 40) * 40
    key = q[:, :, 0].astype(np.int32) * 4096 + q[:, :, 1].astype(np.int32) * 64 + q[:, :, 2].astype(np.int32)
    key[~ink] = -1
    print(f"\n{'='*100}\n=== 帧 {idx}  t={idx*0.5:.1f}s   背景 RGB{tuple(int(x) for x in bg)}   墨迹 {ink.sum()} px\n{'='*100}")
    rowsout = []
    for k in np.unique(key):
        if k < 0: continue
        comps, lab = components(key == k, 500)
        for area, x0, x1, y0, y1, cid in comps:
            sel = lab == cid
            mean = tuple(int(v) for v in a[sel].mean(axis=0))
            rowsout.append((area, x0, x1, y0, y1, mean, (x0 + x1) / 2))
    rowsout.sort(key=lambda r: -r[0])
    print(f"{'面积':>7} {'x范围':>11} {'y范围':>11} {'均色':>18} {'中心x':>5}")
    for area, x0, x1, y0, y1, col, cx in rowsout[:10]:
        print(f"{area:>7} {f'{x0}-{x1}':>11} {f'{y0}-{y1}':>11} {str(col):>18} {cx:>5.0f}")

import sys
for idx in [int(x) for x in sys.argv[1:]] or [4, 12, 60, 120]:
    report(idx)
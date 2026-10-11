"""核查播放头读数是否真的渲染出来：读数区 y650-790, x650-1005。"""
import glob, os
import numpy as np
from PIL import Image

TMP = r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\video_analysis\_safe_frames"
files = sorted(glob.glob(os.path.join(TMP, "*.png")))
INK = np.array([0xF0, 0xF0, 0xF0])
PINK = np.array([0xF0, 0x48, 0x78])

for i in (2, 4, 8, 11):
    a = np.asarray(Image.open(files[i]).convert("RGB")).astype(np.int16)
    bg = np.median(a.reshape(-1, 3), axis=0)
    c = np.abs(a - bg).max(axis=-1) > 40

    # 读数整块：左标签 + 右数字 + 环比
    blk = c[650:790, :]
    ys, xs = np.where(blk)
    if xs.size == 0:
        print(f"帧{i}: 读数区完全空白 <<< 无读数")
        continue

    px = a[650:790, :]
    pink = int((np.abs(px - PINK).max(axis=-1) <= 60).sum())
    print(f"帧{i}: 读数区 x={xs.min()}..{xs.max()} y={650+ys.min()}..{650+ys.max()} "
          f"像素={int(blk.sum())} 亮粉={pink}")

    # 分块看左右
    lft = int(blk[:, :650].sum()); rgt = int(blk[:, 650:].sum())
    print(f"      左半(当前时点/日期)={lft}  右半(数值/环比)={rgt}")

    # 读数右边界 vs 抖音安全区 880
    rx = xs.max()
    print(f"      读数最右 x={rx} -> {'越界(>880) 会被右侧交互栏压住' if rx>880 else 'OK'}")

    # 播放头端点附近有无浮动数值标注 (x±160, y 900-1250)
    near = c[900:1270, :]
    print()

# 抽查一帧读数区的实际像素，确认是文字不是噪点
a = np.asarray(Image.open(files[4]).convert("RGB")).astype(np.int16)
print("帧4 读数区右侧最亮像素:", tuple(int(v) for v in a[660:790, 650:1005].reshape(-1,3)[np.abs(a[660:790,650:1005]-np.median(a.reshape(-1,3),axis=0)).max(axis=-1).argmax()]))
"""测量成片内容包围盒，量化抖音 UI 遮挡风险。"""
import glob, os, subprocess
import numpy as np
from PIL import Image

VID = r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\deliverables\ep003_cambrian_sh688256_2023-2026_ai_v3_pan_camera.mp4"
TMP = r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\video_analysis\_safe_frames"
os.makedirs(TMP, exist_ok=True)
for f in glob.glob(os.path.join(TMP, "*.png")):
    os.remove(f)

subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-i", VID,
     "-vf", "select='not(mod(n,210))'", "-vsync", "0", os.path.join(TMP, "f_%03d.png")],
    check=True,
)
files = sorted(glob.glob(os.path.join(TMP, "*.png")))
print(f"采样帧数: {len(files)}\n")

lmin, rmax, tmin, bmax = 10**9, -1, 10**9, -1
for i, f in enumerate(files):
    a = np.asarray(Image.open(f).convert("RGB")).astype(np.int16)
    bg = np.median(a.reshape(-1, 3), axis=0)
    content = np.abs(a - bg).max(axis=-1) > 25
    content[:12, :] = False          # 顶部满宽色条是 chrome，排除
    content[1852:, :] = False        # 底部合规条是 chrome，排除
    ys, xs = np.where(content)
    if xs.size == 0:
        print(f"  帧{i:2d}: 空"); continue
    l, r, t, b = xs.min(), xs.max(), ys.min(), ys.max()
    lmin, rmax, tmin, bmax = min(lmin, l), max(rmax, r), min(tmin, t), max(bmax, b)
    # 右侧交互栏与底部文案区的实际占用
    rail = int(content[420:1330, 880:].sum())
    bot = int(content[1440:, :].sum())
    print(f"  帧{i:2d}: x={l:4d}..{r:4d}  y={t:4d}..{b:4d}   右栏(x>880)={rail:6d}  底部(y>1440)={bot:6d}")

print(f"\n全局包围盒: x={lmin}..{rmax}   y={tmin}..{bmax}")
print(f"画布 1080x1920")
print(f"  左边距={lmin}  右边距={1079-rmax}")
print(f"  上边距={tmin}  下边距={1919-bmax}")
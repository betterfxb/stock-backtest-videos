"""孤立硬切检测：逐帧像素差，尖峰=单帧内大幅变化而前后平稳。
用户反馈的 6 处卡顿（粘性轴重标定）应全部表现为孤立尖峰。
"""
import sys
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image

FF = r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\cambricon-video\node_modules\@remotion\compositor-win32-x64-msvc\ffmpeg.exe"
OUT = Path(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\cambricon-video\out")
TMP = Path(r"C:\Users\19560\AppData\Local\Temp\opencode\spikef")
TMP.mkdir(parents=True, exist_ok=True)

FPS = 30
CROP = "crop=1080:800:0:700"  # 只取读数+绘图区+时间轴，纵轴跳变必然体现在此
SCALE = 540


def extract(mp4, tag, fps, scale):
    d = TMP / tag
    if d.exists():
        for p in d.glob("*.png"):
            p.unlink()
    else:
        d.mkdir(parents=True)
    subprocess.run([FF, "-v", "error", "-i", str(mp4),
                    "-vf", f"{CROP},scale={scale}:-1",
                    "-r", str(fps), str(d / "f_%05d.png")], check=True)
    return d


def diffs(d):
    fs = sorted(d.glob("f_*.png"))
    out = []
    prev = None
    for p in fs:
        a = np.asarray(Image.open(p).convert("RGB")).astype(np.int16)
        if prev is not None:
            out.append(float(np.abs(a - prev).mean()))
        prev = a
    return np.array(out)


def scan(dfs, fps):
    med = np.median(dfs)
    mad = np.median(np.abs(dfs - med)) + 1e-6
    z = (dfs - med) / (1.4826 * mad)
    spikes = []
    for i in range(1, len(dfs) - 1):
        if z[i] > 12 and z[i] > z[i - 1] * 2 and z[i] > z[i + 1] * 2:
            spikes.append((i / fps, dfs[i], z[i]))
    return med, mad, spikes


def main():
    targets = [
        (r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\deliverables\mock4_full_25s.mp4", "mock4_sticky", "对照: 已否决的粘性轴 (应能测出尖峰)"),
        (r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\deliverables\mock5_fixed_25s.mp4", "mock5_fixed", "对照: 旧固定轴样片"),
        (str(OUT / "ep003_v3_pan_camera.mp4"), "final_v3", "本次成片: 横向跟随相机"),
    ]

    for path, tag, desc in targets:
        p = Path(path)
        if not p.exists():
            print(f"skip {tag}: not found")
            continue
        d = extract(p, tag, FPS, SCALE)
        dfs = diffs(d)
        med, mad, spikes = scan(dfs, FPS)
        print(f"\n=== {desc}  [{p.name}] ===")
        print(f"  抽帧{FPS}fps 帧数={len(dfs)+1}  图表区差分 中位数={med:.3f}  MAD={mad:.3f}  最大值={dfs.max():.2f}")
        print(f"  孤立硬切尖峰数 = {len(spikes)}")
        for t, v, zz in spikes[:20]:
            print(f"    t={t:6.2f}s  diff={v:7.2f}  z={zz:6.1f}")
        if not spikes:
            print("    -> 无单帧突变，运动连续")


if __name__ == "__main__":
    sys.exit(main())
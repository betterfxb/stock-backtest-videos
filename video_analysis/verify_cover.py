"""封面校验：文字不越界、不贴边、关键区块有内容、角标与页脚不重叠。
用法: python verify_cover.py [目录] [文件前缀]   （默认 cambricon-video/out 与 coverA|coverB）"""
import sys
from pathlib import Path
from PIL import Image
import numpy as np

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\cambricon-video\out")
PREFIX = sys.argv[2] if len(sys.argv) > 2 else ""
BG = np.array([0x09, 0x04, 0x09])
INK = np.array([0xF0, 0xF0, 0xF0])
PINK = np.array([0xF0, 0x48, 0x78])
RED = np.array([0xE8, 0x6E, 0x6E])

BLOCKS = {
    "期号行 y104-150": (104, 150),
    "主标题区 y230-640": (230, 640),
    "图表区 y780-1420": (780, 1420),
    "角标 y1690-1840": (1690, 1840),
    "合规条 y1852-1920": (1852, 1920),
}

for tag in ("coverA", "coverB"):
    a = np.asarray(Image.open(OUT / f"{PREFIX}{tag}.png").convert("RGB")).astype(np.int16)
    H, W, _ = a.shape
    nonbg = np.abs(a - BG).max(axis=-1) > 20

    print(f"\n=== {tag}.png  {W}x{H} ===")
    for name, (y0, y1) in BLOCKS.items():
        seg = nonbg[y0:y1]
        cnt = int(seg.sum())
        print(f"  {'OK ' if cnt > 400 else 'EMPTY'} {name:24s} 像素={cnt}")

    # 正文安全边距：排除顶部色条(y<12)、底部合规条(y>=1852)、右上柔光圆(y<300)
    # 柔光是居中的 radial 渐变，允许延伸到右边缘
    body = nonbg.copy()
    body[:12, :] = False
    body[1852:, :] = False
    body[:300, 700:] = False
    cols = np.where(body[:, :].any(axis=0))[0]
    print(f"  正文横向范围 x={cols.min()}..{cols.max()}  (安全区 80..1000)")

    # 竖向是否顶到最上/最下
    rows = np.where(nonbg[:, :].any(axis=1))[0]
    print(f"  竖向范围 y={rows.min()}..{rows.max()}  (画布 0..1919, 底部余量 {1919-rows.max()})")

    # 主数字块是否有亮粉/白字，且左侧起点不越界
    main = a[280:640]
    mp = int((np.abs(main - PINK).max(axis=-1) <= 40).sum())
    mi = int((np.abs(main - INK).max(axis=-1) <= 30).sum())
    mr = int((np.abs(main - RED).max(axis=-1) <= 30).sum())
    print(f"  主视觉块: 亮粉={mp} 白字={mi} 红={mr}")

    # 角标（右半区 x>640）与左下信息（左半区 x<640）是否真的水平重叠
    corner = np.where(nonbg[1690:1840, 640:])[1] + 640
    left = np.where(nonbg[1720:1845, 0:640])[1]
    if corner.size and left.size:
        gap = corner.min() - left.max()
        print(f"  角标 x={corner.min()}..{corner.max()} | 左下信息 x={left.min()}..{left.max()} -> "
              f"{'!! 重叠' if gap < 0 else f'OK 左右分离，间隙 {gap}px'}")
    else:
        print("  左下信息缺失" if not left.size else "  角标缺失")

    # 出血：顶部色条与底部合规条是满宽设计，只检查左右两侧是否有元素贴边
    side = int(nonbg[12:1852, :4].sum() + nonbg[12:1852, -4:].sum())
    print(f"  左右侧出血像素={side} -> {'!! 正文贴边' if side > 0 else 'OK 正文未贴边'}")
    # 曲线与峰值标注必须落在图表区内
    chart = a[780:1420]
    cpk = int((np.abs(chart - PINK).max(axis=-1) <= 60).sum())
    print(f"  图表区曲线像素={cpk} -> {'OK 曲线已渲染' if cpk > 5000 else '!! 曲线缺失'}")
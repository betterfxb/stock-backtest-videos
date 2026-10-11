"""
新版画面渲染器 —— 1080×1920 高清母版
色系：绛蓝 + 金铜 + 米白（完全脱离原片黑底荧光粉）
特点：亮底、高对比、大字号、粗笔画，为高码率压缩预留信息量
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 1080, 1920
OUT = os.path.dirname(os.path.abspath(__file__))

# ── 新色系令牌 ──────────────────────────────────────
BG        = (247, 244, 239)   # 米白主背景
SURFACE   = (255, 255, 255)   # 纯白卡片
LINE      = (232, 226, 214)   # 暖灰分隔
NAVY      = (27, 58, 107)     # 绛蓝 标题/轴线
BLUE      = (46, 107, 168)    # 亮蓝 曲线主线
GOLD      = (201, 162, 39)    # 金铜 强调/收益率
UP_RED    = (192, 57, 43)     # 涨 深砖红
DOWN_GREEN= (30, 132, 73)     # 跌 松绿
FLAT_AMBER= (183, 121, 31)    # 横盘 琥珀
DD_RED    = (123, 36, 28)     # 回撤 暗红
INK       = (20, 17, 12)      # 标题文字
INK2      = (74, 68, 56)      # 正文
INK3      = (125, 117, 101)   # 辅助

F_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
F_REG  = "C:/Windows/Fonts/msyh.ttc"
F_NUM  = "C:/Windows/Fonts/segoeuib.ttf"   # 数字用 Segoe UI Bold，更紧凑有力
F_NUMC = "C:/Windows/Fonts/msyhbd.ttc"     # 含中文单位「万」时用雅黑粗体

def wan(n, size=62, color=INK):
    """带「万」单位的数字，字体切换到含中文字形的字体"""
    s = f"{n:,.2f} 万"
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    f = font(F_NUMC, size)
    d.text((0, 0), s, font=f, fill=color)
    return s, f

def font(path, size):
    return ImageFont.truetype(path, size)

# ── 数据（复刻原片曲线节点，含回撤段）─────────────────
SERIES = [
    ("2020-01", 100.0), ("2020-04", 103.2), ("2020-07", 124.0), ("2020-11", 112.5),
    ("2021-02", 114.2), ("2021-05", 118.6), ("2021-08", 110.0), ("2021-11", 108.4),
    ("2022-02", 120.5), ("2022-06", 108.0), ("2022-10", 109.6), ("2023-01", 121.0),
    ("2023-05", 128.4), ("2023-09", 131.0), ("2024-01", 142.6), ("2024-04", 158.2),
    ("2024-08", 164.0), ("2024-11", 182.2), ("2025-02", 205.4), ("2025-05", 223.0),
    ("2025-08", 219.0), ("2025-11", 248.0), ("2026-01", 286.3), ("2026-04", 297.0),
    ("2026-06", 268.0), ("2026-08", 245.3), ("2026-09", 254.1),
]

def draw_frame(idx_total=None, mode="main"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ── 顶部：标题区（三行，等宽对齐）──
    d.rectangle([0, 0, W, 10], fill=NAVY)   # 顶部品牌色条

    y = 120
    d.text((72, y), "假如你不小心", font=font(F_BOLD, 96), fill=INK)
    y += 124
    d.text((72, y), "2020年买", font=font(F_BOLD, 96), fill=INK)
    x = 72 + d.textlength("2020年买", font=font(F_BOLD, 96))
    d.text((x, y), "100万", font=font(F_NUMC, 96), fill=GOLD)
    x += d.textlength("100万", font=font(F_NUMC, 96))
    d.text((x, y), "黄金", font=font(F_BOLD, 96), fill=UP_RED)
    y += 124
    d.text((72, y), "坚持拿满6年", font=font(F_BOLD, 96), fill=INK)

    # ── 主数据块：独立卡片，不再与标题争空间 ──
    d.rounded_rectangle([72, 540, 1008, 716], radius=22, fill=SURFACE,
                        outline=LINE, width=3)
    d.text((112, 566), "总收益率", font=font(F_REG, 42), fill=INK3)
    d.text((112, 614), "154.12%", font=font(F_NUM, 108), fill=GOLD)
    d.text((1008 - 40, 566), "2026-09-28", font=font(F_NUM, 44), fill=INK3, anchor="ra")
    d.text((1008 - 40, 630), "期末 254.12 万", font=font(F_NUMC, 44), fill=INK2, anchor="ra")

    # ── 中部：图表区 ──
    cx0, cy0, cx1, cy1 = 150, 862, 1000, 1432
    vals = [v for _, v in SERIES]
    vmin, vmax = 88, 380
    def px(i): return cx0 + (cx1 - cx0) * i / (len(SERIES) - 1)
    def py(v): return cy1 - (cy1 - cy0) * (v - vmin) / (vmax - vmin)

    # 网格 + Y 轴刻度
    for gv in [100, 150, 200, 250, 300, 350]:
        gy = py(gv)
        d.line([cx0, gy, cx1, gy], fill=LINE, width=2)
        d.text((cx0 - 20, gy), f"{gv}", font=font(F_NUM, 32), fill=INK3, anchor="rm")
    d.text((cx0 - 20, cy1 + 30), "万", font=font(F_REG, 30), fill=INK3, anchor="rm")

    # X 轴刻度（防重叠：只保留首尾与中段，锚点错开）
    for i, (lab, _) in enumerate(SERIES):
        if lab in ("2020-01", "2026-09"):
            d.text((px(i), cy1 + 24), lab[:7], font=font(F_NUM, 30), fill=INK3, anchor="ma")
        elif lab in ("2023-01", "2026-01"):
            d.text((px(i), cy1 + 24), lab[:7], font=font(F_NUM, 30), fill=INK3, anchor="ma")
    d.text((cx0 - 22, cy0 - 30), "万元", font=font(F_NUMC, 30), fill=INK3, anchor="lm")

    # 成本基准线（虚线）
    d.line([cx0, py(100), cx1, py(100)], fill=INK3, width=3)
    d.text((cx1 + 10, py(100) - 26), "本金 100 万", font=font(F_NUMC, 30), fill=INK3, anchor="la")

    # 曲线：先画浅色粗底线（抗锯齿补偿），再画主色
    pts = [(px(i), py(v)) for i, (_, v) in enumerate(SERIES)]
    d.line(pts, fill=(198, 214, 232), width=18, joint="curve")
    d.line(pts, fill=BLUE, width=9, joint="curve")

    # 回撤段高亮：从峰值到期末
    peak_i = max(range(len(SERIES)), key=lambda i: SERIES[i][1])
    dd_pts = [(px(i), py(SERIES[i][1])) for i in range(peak_i, len(SERIES))]
    d.line(dd_pts, fill=DD_RED, width=10, joint="curve")

    # 终点游标 + 标签（下移至曲线下方，避开峰值标签）
    ex, ey = pts[-1]
    d.ellipse([ex-18, ey-18, ex+18, ey+18], fill=DD_RED, outline=BG, width=6)
    lab_txt, lab_font = wan(254.12, 50, SURFACE)
    tw = d.textlength(lab_txt, font=lab_font)
    d.rounded_rectangle([ex - tw - 76, ey + 46, ex - 16, ey + 128], radius=14, fill=NAVY)
    d.text((ex - 46 - tw / 2, ey + 62), lab_txt, font=lab_font, fill=SURFACE, anchor="ma")

    # 峰值标注（峰值点正上方，自动收边防止出血）
    mx, my = pts[peak_i]
    pk_txt, pk_font = wan(297.0, 42, (255, 255, 255))
    pw = d.textlength(pk_txt, font=pk_font)
    left = min(mx - pw / 2 - 30, 1010 - pw - 30)
    d.ellipse([mx-13, my-13, mx+13, my+13], fill=UP_RED, outline=BG, width=5)
    d.rounded_rectangle([left, my - 150, left + pw + 60, my - 82],
                        radius=14, fill=UP_RED)
    d.text((left + 30 + pw / 2, my - 142), pk_txt, font=pk_font,
           fill=(255, 255, 255), anchor="ma")

    # ── 阶段标签（横排，左侧琥珀块）──
    d.rounded_rectangle([72, 1498, 500, 1588], radius=14, fill=FLAT_AMBER)
    d.text((286, 1514), "冲顶后回落", font=font(F_BOLD, 44), fill=(255, 255, 255), anchor="ma")
    d.text((524, 1520), "最高点下来，回撤三成", font=font(F_REG, 36), fill=INK2)

    # ── 事件卡（白底 + 左侧色条）──
    cy = 1626
    d.rounded_rectangle([72, cy, 1008, cy + 208], radius=22, fill=SURFACE,
                        outline=LINE, width=3)
    d.rounded_rectangle([72, cy, 86, cy + 208], radius=7, fill=DD_RED)
    d.text((116, cy + 22), "2026年7月 · 回撤", font=font(F_BOLD, 42), fill=DD_RED)
    d.text((116, cy + 78), "从 353.10 万跌到 245.33 万", font=font(F_BOLD, 50), fill=INK)
    body = ["2026 年 1 月 29 日冲上区间最高 353.10 万后掉头向下，",
            "7 月 1 日只剩 245.33 万，最大回撤 −30.52%；期末 254.12 万。"]
    for i, ln in enumerate(body):
        d.text((116, cy + 142 + i * 40), ln, font=font(F_REG, 32), fill=INK2)

    # ── 底部合规条 ──
    d.line([72, 1866, 1008, 1866], fill=LINE, width=2)
    d.text((72, 1878), "历史数据模拟，切勿作为投资建议",
           font=font(F_REG, 30), fill=INK3)
    d.text((1008, 1878), "数据源：上金所", font=font(F_REG, 30), fill=INK3, anchor="ra")

    return img


if __name__ == "__main__":
    im = draw_frame()
    im.save(os.path.join(OUT, "new_main_1080x1920.png"))
    print("主画面已输出", im.size)

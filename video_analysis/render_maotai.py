"""
贵州茅台 sh600519 单期画面渲染 —— 严格按方案 v2 规范
1080×1920 · 绛蓝+金铜+米白 · 涨红跌绿 · 数据来自 backtest_maotai.py 实测
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1080, 1920
OUT = os.path.dirname(os.path.abspath(__file__))

# ── v2 色系令牌 ──────────────────────────────────────
BG      = (247, 244, 239)
SURFACE = (255, 255, 255)
LINE    = (232, 226, 214)
NAVY    = (27, 58, 107)
BLUE    = (46, 107, 168)
GOLD    = (201, 162, 39)
UP_RED  = (192, 57, 43)
DOWN_GR = (30, 132, 73)
FLAT_AM = (183, 121, 31)
DD_RED  = (123, 36, 28)
INK     = (20, 17, 12)
INK2    = (74, 68, 56)
INK3    = (125, 117, 101)

F_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
F_REG  = "C:/Windows/Fonts/msyh.ttc"
F_NUM  = "C:/Windows/Fonts/segoeuib.ttf"

def font(p, s): return ImageFont.truetype(p, s)

def wan(n, size=50, color=INK):
    s = f"{n:,.2f} 万"
    return s, font(F_BOLD, size)

# ── 实测净值序列（backtest_maotai.py 输出，81 个月）──
NAV = [
    ("2020-01",100.00),("2020-02",99.66),("2020-03",106.31),("2020-04",125.87),
    ("2020-05",138.47),("2020-06",152.69),("2020-07",179.71),("2020-08",193.29),
    ("2020-09",178.19),("2020-10",178.25),("2020-11",183.83),("2020-12",219.14),
    ("2021-01",234.22),("2021-02",234.94),("2021-03",220.79),("2021-04",220.49),
    ("2021-05",248.98),("2021-06",229.63),("2021-07",182.10),("2021-08",167.06),
    ("2021-09",200.99),("2021-10",200.52),("2021-11",213.59),("2021-12",228.54),
    ("2022-01",208.13),("2022-02",196.05),("2022-03",187.13),("2022-04",200.80),
    ("2022-05",197.74),("2022-06",230.54),("2022-07",212.21),("2022-08",215.44),
    ("2022-09",209.02),("2022-10",144.76),("2022-11",174.53),("2022-12",193.21),
    ("2023-01",208.01),("2023-02",204.00),("2023-03",204.69),("2023-04",197.30),
    ("2023-05",180.84),("2023-06",191.87),("2023-07",215.61),("2023-08",211.28),
    ("2023-09",205.21),("2023-10",191.00),("2023-11",204.40),("2023-12",198.64),
    ("2024-01",183.47),("2024-02",194.75),("2024-03",195.87),("2024-04",196.15),
    ("2024-05",189.12),("2024-06",170.35),("2024-07",164.62),("2024-08",167.33),
    ("2024-09",205.40),("2024-10",177.90),("2024-11",177.66),("2024-12",180.38),
    ("2025-01",169.29),("2025-02",177.53),("2025-03",185.05),("2025-04",183.31),
    ("2025-05",180.20),("2025-06",169.58),("2025-07",171.08),("2025-08",178.36),
    ("2025-09",173.89),("2025-10",172.13),("2025-11",174.67),("2025-12",168.55),
    ("2026-01",171.51),("2026-02",178.24),("2026-03",177.60),("2026-04",169.47),
    ("2026-05",162.14),("2026-06",148.17),("2026-07",168.71),("2026-08",162.32),
    ("2026-09",157.19),
]

def draw():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=NAVY)

    # 标题三行
    TF = 80  # 标题字号：实测 80px 行宽 975px，1080-72×2=936 安全
    y = 124
    d.text((72, y), "假如你不小心", font=font(F_BOLD, TF), fill=INK)
    y += 106
    d.text((72, y), "2020年买", font=font(F_BOLD, TF), fill=INK)
    x = 72 + d.textlength("2020年买", font=font(F_BOLD, TF))
    d.text((x, y), "100万", font=font(F_BOLD, TF), fill=GOLD)
    x += d.textlength("100万", font=font(F_BOLD, TF))
    d.text((x, y), "贵州茅台", font=font(F_BOLD, TF), fill=UP_RED)
    y += 106
    d.text((72, y), "坚持拿满6年", font=font(F_BOLD, TF), fill=INK)

    # 主数据卡
    d.rounded_rectangle([72, 506, 1008, 682], radius=22, fill=SURFACE,
                        outline=LINE, width=3)
    d.text((112, 530), "总收益率 · 含分红", font=font(F_REG, 40), fill=INK3)
    d.text((112, 574), "91.29%", font=font(F_NUM, 104), fill=GOLD)
    d.text((1008 - 40, 530), "2026-09-30", font=font(F_NUM, 42), fill=INK3, anchor="ra")
    d.text((1008 - 40, 590), "含息年化 10.15%", font=font(F_BOLD, 40),
           fill=NAVY, anchor="ra")

    # 图表区
    cx0, cy0, cx1, cy1 = 150, 830, 1000, 1400
    vals = [v for _, v in NAV]
    vmin, vmax = 88, 340
    def px(i): return cx0 + (cx1 - cx0) * i / (len(NAV) - 1)
    def py(v): return cy1 - (cy1 - cy0) * (v - vmin) / (vmax - vmin)

    for gv in [100, 150, 200, 250, 300]:
        gy = py(gv)
        d.line([cx0, gy, cx1, gy], fill=LINE, width=2)
        d.text((cx0 - 22, gy), f"{gv}", font=font(F_NUM, 30), fill=INK3, anchor="rm")
    d.text((cx0 - 22, cy0 - 28), "万元", font=font(F_BOLD, 28), fill=INK3, anchor="lm")

    for i, (lab, _) in enumerate(NAV):
        if lab in ("2020-01", "2022-10", "2026-09"):
            anc = "la" if i == 0 else "ma"
            d.text((px(i), cy1 + 22), lab[:7], font=font(F_NUM, 28),
                   fill=INK3, anchor=anc)

    # 本金基准线
    d.line([cx0, py(100), cx1, py(100)], fill=INK3, width=3)
    d.text((cx1 + 8, py(100) - 26), "本金 100 万", font=font(F_BOLD, 28),
           fill=INK3, anchor="la")

    # 曲线：抗锯齿双描
    pts = [(px(i), py(v)) for i, (_, v) in enumerate(NAV)]
    d.line(pts, fill=(198, 214, 232), width=18, joint="curve")
    d.line(pts, fill=BLUE, width=9, joint="curve")

    # 回撤段：2021-05 峰值 → 2022-10 谷底
    peak_i = 24   # 2021-05
    trough_i = 33 # 2022-10
    d.line([(px(i), py(NAV[i][1])) for i in range(peak_i, trough_i + 1)],
           fill=DD_RED, width=10, joint="curve")

    # 峰值标注
    mx, my = pts[peak_i]
    pk_txt, pk_font = wan(248.98, 40, SURFACE)
    pw = d.textlength(pk_txt, font=pk_font)
    d.ellipse([mx-12, my-12, mx+12, my+12], fill=UP_RED, outline=BG, width=5)
    left = min(mx - pw/2 - 28, 1008 - pw - 28)
    d.rounded_rectangle([left, my - 148, left + pw + 56, my - 86],
                        radius=14, fill=UP_RED)
    d.text((left + 28 + pw/2, my - 142), pk_txt, font=pk_font,
           fill=SURFACE, anchor="ma")

    # 谷底标注
    tx, ty = pts[trough_i]
    tr_txt, tr_font = wan(144.76, 40, SURFACE)
    tw = d.textlength(tr_txt, font=tr_font)
    d.ellipse([tx-12, ty-12, tx+12, ty+12], fill=DD_RED, outline=BG, width=5)
    l2 = max(min(tx - tw/2 - 28, 1008 - tw - 28), 72)
    d.rounded_rectangle([l2, ty + 34, l2 + tw + 56, ty + 94],
                        radius=14, fill=DD_RED)
    d.text((l2 + 28 + tw/2, ty + 40), tr_txt, font=tr_font,
           fill=SURFACE, anchor="ma")

    # 终点游标 + 标签（下方）
    ex, ey = pts[-1]
    d.ellipse([ex-16, ey-16, ex+16, ey+16], fill=NAVY, outline=BG, width=6)
    ed_txt, ed_font = wan(191.29, 46, SURFACE)
    ew = d.textlength(ed_txt, font=ed_font)
    l3 = max(ex - ew - 76, 72)
    d.rounded_rectangle([l3, ey + 42, l3 + ew + 60, ey + 122], radius=14, fill=NAVY)
    d.text((l3 + 30 + ew/2, ey + 56), ed_txt, font=ed_font, fill=SURFACE, anchor="ma")

    # 阶段标签
    d.rounded_rectangle([72, 1496, 528, 1586], radius=14, fill=FLAT_AM)
    d.text((300, 1512), "跌了五年没回本", font=font(F_BOLD, 44),
           fill=SURFACE, anchor="ma")
    d.text((552, 1520), "最大回撤 −41.86%", font=font(F_BOLD, 38), fill=DD_RED)

    # 事件卡
    cy = 1624
    d.rounded_rectangle([72, cy, 1008, cy + 210], radius=22, fill=SURFACE,
                        outline=LINE, width=3)
    d.rounded_rectangle([72, cy, 86, cy + 210], radius=7, fill=DD_RED)
    d.text((116, cy + 22), "2021年5月 – 2022年10月 · 回撤", font=font(F_BOLD, 40), fill=DD_RED)
    d.text((116, cy + 76), "从 248.98 万跌到 144.76 万", font=font(F_BOLD, 48), fill=INK)
    for i, ln in enumerate([
        "2021 年 5 月见到区间最高点后一路下行，2022 年 10 月触及最低点，",
        "最大回撤 −41.86%，此后 64 个月仍未回到前高。"]):
        d.text((116, cy + 138 + i * 42), ln, font=font(F_REG, 29), fill=INK2)

    # 合规条
    d.line([72, 1864, 1008, 1864], fill=LINE, width=2)
    d.text((72, 1876), "历史数据模拟，切勿作为投资建议",
           font=font(F_REG, 30), fill=INK3)
    d.text((1008, 1876), "数据源：腾讯自选股 sh600519",
           font=font(F_REG, 30), fill=INK3, anchor="ra")

    return img

if __name__ == "__main__":
    im = draw()
    im.save(os.path.join(OUT, "maotai_frame_1080x1920.png"))
    print("茅台画面已输出", im.size)

# -*- coding: utf-8 -*-
import csv, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG      = (9, 4, 9)
PINK    = (240, 72, 120)
WHITE   = (240, 240, 240)
DIM     = (128, 118, 126)
GRID    = (38, 26, 34)
AXIS    = (74, 58, 68)
CURVE_A = (58, 44, 52)

# 版式（按参考实测比例 ×1.875）
L, R   = 82, 891
T, B   = 759, 1420
AXY    = 1462
CMP_Y  = 1740

F = r"C:\Windows\Fonts\msyh.ttc"
def f(sz, bold=False):
    try:
        return ImageFont.truetype(F, sz, index=1 if bold else 0)
    except Exception:
        return ImageFont.load_default()

rows = list(csv.DictReader(open(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\deliverables\backtest_nav.csv", encoding="utf-8")))
nav  = [float(r["nav"]) / 10000.0 for r in rows]          # 万元
mon  = [r["date"][:7] for r in rows]
N    = len(nav)
YMAX = 4000.0

def px(i):  return L + (R - L) * i / (N - 1)
def py(v):  return B - (B - T) * (v / YMAX)

def draw(idx, name):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im, "RGBA")

    # ---- 网格 + 纵轴刻度（全程固定，不随游标变化）----
    for gv in range(0, 4001, 1000):
        y = py(gv)
        d.line([(L, y), (R, y)], fill=GRID, width=2)
        d.text((L - 16, y), f"{gv:,}", font=f(24), fill=DIM, anchor="rm")
    d.line([(L, T), (L, B)], fill=AXIS, width=3)
    d.line([(L, B), (R, B)], fill=AXIS, width=3)

    # ---- 时间轴刻度 ----
    for i in range(0, N, 6):
        d.line([(px(i), B), (px(i), B + 10)], fill=AXIS, width=3)
        d.text((px(i), AXY), mon[i], font=f(23), fill=DIM, anchor="ma")

    # ---- 曲线：全程可见的暗色底稿 ----
    pts = [(px(i), py(v)) for i, v in enumerate(nav)]
    d.line(pts, fill=CURVE_A, width=9, joint="curve")

    # ---- 已扫过部分：亮粉 ----
    if idx >= 0:
        d.line(pts[:idx + 1], fill=PINK, width=9, joint="curve")

    # ---- 扫描游标 ----
    cx, cy = px(idx), py(nav[idx])
    d.rectangle([cx - 13, T - 26, cx + 13, cy], fill=(240, 72, 120, 46))
    for gy in range(T, int(cy), 26):                       # 游标内虚线
        d.line([(cx, gy), (cx, gy + 13)], fill=(240, 72, 120, 150), width=3)
    d.ellipse([cx - 17, cy - 17, cx + 17, cy + 17], fill=PINK)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 220, 232))
    d.line([(cx, cy), (R + 8, cy)], fill=(240, 72, 120, 120), width=2)

    # ---- 顶部节拍读数区（每 2s 换一次）----
    d.text((L, 247), "当前时点", font=f(30), fill=DIM)
    d.text((L, 288), mon[idx].replace("-", " / "), font=f(62, True), fill=WHITE)
    val = f"{nav[idx]:,.0f} 万"
    d.text((R, 262), val, font=f(96, True), fill=PINK, anchor="ra")
    if idx > 0:
        chg = (nav[idx] / nav[idx - 1] - 1) * 100
        d.text((R, 372), f"环比 {'+' if chg >= 0 else ''}{chg:.1f}%", font=f(34),
               fill=(120, 214, 168) if chg >= 0 else (232, 110, 110), anchor="ra")

    # ---- 右上静态信息块（参考里这块全片不动）----
    d.text((R, 440), "寒武纪 688256", font=f(30, True), fill=WHITE, anchor="ra")
    d.text((R, 486), "区间 2023-01 → 2026-09", font=f(26), fill=DIM, anchor="ra")
    d.text((R, 524), f"累计 {nav[-1]/nav[0]:.1f} 倍", font=f(26), fill=DIM, anchor="ra")

    # ---- 左侧静态标签列 ----
    d.text((L, 470), "累计净值", font=f(26), fill=DIM)
    d.text((L, 506), f"{nav[idx]:,.0f}", font=f(40, True), fill=WHITE)
    d.text((L, 566), "距峰值", font=f(26), fill=DIM)
    peak = max(nav[:idx + 1])
    dd = (nav[idx] / peak - 1) * 100
    d.text((L, 602), f"{dd:.1f}%", font=f(40, True), fill=(232, 110, 110) if dd < -0.5 else WHITE)

    # ---- 底部合规条（y1740–1830）----
    d.rectangle([0, 1722, W, 1848], fill=(16, 8, 14))
    d.line([(0, 1722), (W, 1722)], fill=(240, 72, 120, 90), width=2)
    d.text((L, 1748), "数据来源：权威回测净值 · 仅为历史表现记录", font=f(23), fill=DIM)
    d.text((L, 1790), "本视频不构成任何投资建议，市场有风险，决策需谨慎", font=f(23), fill=(150, 90, 100))

    out = rf"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\deliverables\mock_{name}.png"
    im.save(out)
    print(f"{name}  时点={mon[idx]}  净值={nav[idx]:,.0f}万  ->  {out}")

draw(8,  "a_2023_09")
draw(17, "b_2024_06")
draw(32, "c_2025_08")
draw(44, "d_2026_09")
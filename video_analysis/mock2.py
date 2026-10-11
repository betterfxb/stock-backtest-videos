# -*- coding: utf-8 -*-
import csv
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG   = (9, 4, 9)
PINK = (240, 72, 120)
WHITE= (240, 240, 240)
DIM  = (128, 118, 126)
GRID = (34, 24, 31)
AXIS = (70, 54, 64)

L, R = 82, 891
T, B = 759, 1420
AXY  = 1462

FT = r"C:\Windows\Fonts\msyh.ttc"
def f(sz, bold=False):
    try:    return ImageFont.truetype(FT, sz, index=1 if bold else 0)
    except Exception: return ImageFont.load_default()

rows = list(csv.DictReader(open(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\deliverables\backtest_nav.csv", encoding="utf-8")))
nav = [float(r["nav"]) / 10000.0 for r in rows]
mon = [r["date"][:7] for r in rows]
N   = len(nav)

def px(i): return L + (R - L) * i / (N - 1)

def render(idx, name, sticky=False):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im, "RGBA")

    ymax = 4000.0
    if sticky:
        ymax = max(500.0, (int(max(nav[:idx + 1]) / 500) + 1) * 500)
    py = lambda v: B - (B - T) * (v / ymax)

    for gv in range(0, int(ymax) + 1, int(ymax / 4)):
        y = py(gv)
        d.line([(L, y), (R, y)], fill=GRID, width=2)
        d.text((L - 16, y), f"{gv:,.0f}", font=f(24), fill=DIM, anchor="rm")

    d.line([(L, T), (L, B)], fill=AXIS, width=3)
    d.line([(L, B), (R, B)], fill=AXIS, width=3)

    # 整条时间轴刻度一次性画全（固定时间轴，不随节点变化）
    for i in range(N):
        major = mon[i].endswith("-01")
        d.line([(px(i), B), (px(i), B + (14 if major else 6))], fill=AXIS if major else (46, 34, 42), width=3)
        if i % 6 == 0:
            d.text((px(i), AXY), mon[i], font=f(23), fill=DIM, anchor="ma")

    # 只画到当前节点，之后留空
    pts = [(px(i), py(nav[i])) for i in range(idx + 1)]
    if len(pts) > 1:
        d.line(pts, fill=PINK, width=10, joint="curve")
    for i in range(idx + 1):                       # 已揭示节点的小圆点
        x, y = pts[i]
        r = 9 if i == idx else 5
        d.ellipse([x - r, y - r, x + r, y + r], fill=PINK)

    # 当前节点端点高亮
    cx, cy = pts[-1]
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(240, 72, 120, 55))
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 226, 236))
    for gy in range(int(cy) + 34, B, 24):
        d.line([(cx, gy), (cx, min(gy + 12, B))], fill=(240, 72, 120, 130), width=3)

    # 顶部节拍读数
    d.text((L, 247), "当前时点", font=f(30), fill=DIM)
    d.text((L, 288), mon[idx].replace("-", " / "), font=f(62, True), fill=WHITE)
    d.text((R, 262), f"{nav[idx]:,.0f} 万", font=f(96, True), fill=PINK, anchor="ra")
    if idx > 0:
        c = (nav[idx] / nav[idx - 1] - 1) * 100
        d.text((R, 372), f"环比 {'+' if c >= 0 else ''}{c:.1f}%", font=f(34),
               fill=(120, 214, 168) if c >= 0 else (232, 110, 110), anchor="ra")

    d.text((R, 440), "寒武纪 688256", font=f(30, True), fill=WHITE, anchor="ra")
    d.text((R, 486), "2023-01 → 2026-09 · 共 45 个月", font=f(26), fill=DIM, anchor="ra")
    d.text((R, 524), f"已揭示 {idx + 1} / {N} 个月", font=f(26), fill=DIM, anchor="ra")

    d.text((L, 470), "累计净值", font=f(26), fill=DIM)
    d.text((L, 506), f"{nav[idx]:,.0f}", font=f(40, True), fill=WHITE)
    d.text((L, 566), "距峰值", font=f(26), fill=DIM)
    pk = max(nav[:idx + 1]); dd = (nav[idx] / pk - 1) * 100
    d.text((L, 602), f"{dd:.1f}%", font=f(40, True), fill=(232, 110, 110) if dd < -0.5 else WHITE)

    d.rectangle([0, 1722, W, 1848], fill=(16, 8, 14))
    d.line([(0, 1722), (W, 1722)], fill=(240, 72, 120, 90), width=2)
    d.text((L, 1748), "数据来源：权威回测净值 · 仅为历史表现记录", font=f(23), fill=DIM)
    d.text((L, 1790), "本视频不构成任何投资建议，市场有风险，决策需谨慎", font=f(23), fill=(150, 90, 100))

    out = rf"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\deliverables\mock2_{name}.png"
    im.save(out); print(f"{name}  {mon[idx]}  {nav[idx]:,.0f}万  轴上限 {ymax:,.0f}")

for i, n in [(8, "p08_2023_09"), (17, "p17_2024_06"), (32, "p32_2025_09"), (44, "p44_2026_09")]:
    render(i, n, sticky=False)
for i, n in [(8, "s08_2023_09"), (32, "s32_2025_09")]:
    render(i, n, sticky=True)
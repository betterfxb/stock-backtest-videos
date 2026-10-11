# -*- coding: utf-8 -*-
"""固定坐标轴 + 匀速连续揭示 的运动样片（8s / 30fps / 240 帧）"""
import csv, os, shutil
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
DUR, I0, I1 = 8.0, 0, 20          # 8 秒内从 idx0 匀速走到 idx20 -> 0.4s/节点
OUT = r"C:\Users\19560\AppData\Local\Temp\opencode\smooth"
BG=(9,4,9); PINK=(240,72,120); WHITE=(240,240,240); DIM=(128,118,126)
GRID=(34,24,31); AXIS=(70,54,64)
L,R = 82, 891
T,B = 759, 1420
AXY = 1462

FT = r"C:\Windows\Fonts\msyh.ttc"
_fc = {}
def f(sz, bold=False):
    k = (sz, bold)
    if k not in _fc:
        try:    _fc[k] = ImageFont.truetype(FT, sz, index=1 if bold else 0)
        except Exception: _fc[k] = ImageFont.load_default()
    return _fc[k]

rows = list(csv.DictReader(open(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\deliverables\backtest_nav.csv", encoding="utf-8")))
nav = [float(r["nav"])/10000.0 for r in rows]
mon = [r["date"][:7] for r in rows]
N = len(nav)
px = lambda i: L + (R-L)*i/(N-1)

def smoothstep(t):
    t = min(1.0, max(0.0, t))
    return t*t*(3-2*t)

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)

NF = int(DUR*FPS)
for fr in range(NF):
    t  = fr/FPS
    p  = t/DUR                                  # 线性 -> 匀速
    kf = I0 + (I1-I0)*p                        # 连续小数端点
    ki = min(int(kf), N-1)
    frac = kf - ki

    # 粘性纵轴：上限只涨不跌，500 万步进
    ymax = max(500.0, (int(max(nav[:ki+1])/500)+1)*500)
    if ki+1 < N:
        ymax = max(ymax, (int(max(max(nav[:ki+1]), nav[ki+1])/500)+1)*500)
    py = lambda v: B - (B-T)*(v/ymax)

    im = Image.new("RGB", (W,H), BG); d = ImageDraw.Draw(im, "RGBA")

    for gv in range(0, int(ymax)+1, int(ymax/4)):
        y = py(gv)
        d.line([(L,y),(R,y)], fill=GRID, width=2)
        d.text((L-16,y), f"{gv:,.0f}", font=f(24), fill=DIM, anchor="rm")
    d.line([(L,T),(L,B)], fill=AXIS, width=3)
    d.line([(L,B),(R,B)], fill=AXIS, width=3)
    for i in range(N):
        maj = mon[i].endswith("-01")
        d.line([(px(i),B),(px(i),B+(14 if maj else 6))], fill=AXIS if maj else (46,34,42), width=3)
        if i % 6 == 0:
            d.text((px(i),AXY), mon[i], font=f(23), fill=DIM, anchor="ma")

    # 连续揭示：端点在 frac 上插值，不跳格
    cx = px(kf); cy = py(nav[ki] + (nav[ki+1]-nav[ki])*frac if ki+1 < N else 0)
    pts = [(px(i), py(nav[i])) for i in range(ki+1)]
    pts.append((cx, cy))
    if len(pts) > 1:
        d.line(pts, fill=PINK, width=10, joint="curve")
    for i, (x, y) in enumerate(pts[:-1]):
        d.ellipse([x-5,y-5,x+5,y+5], fill=PINK)

    d.ellipse([cx-22,cy-22,cx+22,cy+22], fill=(240,72,120,55))
    d.ellipse([cx-13,cy-13,cx+13,cy+13], fill=(255,226,236))
    for gy in range(int(cy)+36, B, 24):
        d.line([(cx,gy),(cx,min(gy+12,B))], fill=(240,72,120,130), width=3)

    # 读数连续跟随（滚动取整，不是每节点跳一次）
    lab_i = min(int(kf+0.5), N-1)          # 月份标签取最近节点
    fade = 1.0 - abs(kf - lab_i)            # 0.5 边界处最暗 -> 交叉淡化
    a_val = int(nav[ki] + (nav[ki+1]-nav[ki])*frac) if ki+1 < N else int(nav[ki])
    d.text((L,247), "当前时点", font=f(30), fill=DIM)
    d.text((L,288), mon[lab_i].replace("-"," / "), font=f(62,True),
           fill=tuple(int(WHITE[c]*fade + DIM[c]*(1-fade)) for c in range(3)))
    d.text((R,262), f"{a_val:,} 万", font=f(96,True), fill=PINK, anchor="ra")
    if ki > 0:
        c = (nav[lab_i]/nav[lab_i-1]-1)*100
        d.text((R,372), f"环比 {'+' if c>=0 else ''}{c:.1f}%", font=f(34),
               fill=(120,214,168) if c>=0 else (232,110,110), anchor="ra")

    d.text((R,440), "寒武纪 688256", font=f(30,True), fill=WHITE, anchor="ra")
    d.text((R,486), "2023-01 → 2026-09 · 共 45 个月", font=f(26), fill=DIM, anchor="ra")
    d.text((R,524), f"已揭示 {int(kf)+1} / {N} 个月", font=f(26), fill=DIM, anchor="ra")

    d.text((L,470), "累计净值", font=f(26), fill=DIM)
    d.text((L,506), f"{a_val:,}", font=f(40,True), fill=WHITE)
    d.text((L,566), "距峰值", font=f(26), fill=DIM)
    pk = max(nav[:lab_i+1]); dd = (nav[lab_i]/pk-1)*100
    d.text((L,602), f"{dd:.1f}%", font=f(40,True), fill=(232,110,110) if dd<-0.5 else WHITE)

    d.rectangle([0,1722,W,1848], fill=(16,8,14))
    d.line([(0,1722),(W,1722)], fill=(240,72,120,90), width=2)
    d.text((L,1748), "数据来源：权威回测净值 · 仅为历史表现记录", font=f(23), fill=DIM)
    d.text((L,1790), "本视频不构成任何投资建议，市场有风险，决策需谨慎", font=f(23), fill=(150,90,100))

    im.save(os.path.join(OUT, f"s{fr:04d}.png"))

print(f"frames: {NF}  ->  {OUT}")
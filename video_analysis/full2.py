# -*- coding: utf-8 -*-
"""完整图表段样片 v2：固定轴 0-4000 万（零跳变）+ 匀速连续揭示 + 阶段/事件柔和淡化"""
import csv, os, shutil
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
LEAD, TAIL, SEC_PER_NODE = 1.0, 2.0, 0.5
OUT = r"C:\Users\19560\AppData\Local\Temp\opencode\full2"

BG=(9,4,9); PINK=(240,72,120); WHITE=(240,240,240); DIM=(128,118,126)
GRID=(34,24,31); AXIS=(70,54,64); DD=(58,20,26); GREEN=(120,214,168); RED=(232,110,110)
L,R = 82, 891
T,B = 759, 1420
AXY = 1462
YMAX = 4000.0

FT = r"C:\Windows\Fonts\msyh.ttc"
_fc={}
def f(sz,b=False):
    k=(sz,b)
    if k not in _fc:
        try:    _fc[k]=ImageFont.truetype(FT,sz,index=1 if b else 0)
        except Exception: _fc[k]=ImageFont.load_default()
    return _fc[k]
def mix(c1,c2,a): return tuple(int(c1[i]*a + c2[i]*(1-a)) for i in range(3))

rows=list(csv.DictReader(open(r"C:\Users\19560\WorkBuddy\2026-10-04-14-04-24\deliverables\backtest_nav.csv",encoding="utf-8")))
nav=[float(r["nav"])/10000.0 for r in rows]
mon=[r["date"][:7] for r in rows]
N=len(nav)
px=lambda i: L+(R-L)*i/(N-1)

STAGES=[(0,4,"AI 行情"),(4,9,"行情退潮"),(9,13,"磨底"),(13,23,"国产替代"),
        (23,31,"算力爆发"),(31,41,"冲顶"),(41,44,"回落")]
DD_RANGES=[(4,9),(41,44)]
EVENTS=[(0,"2023年1月","起投","100.00 万","AI 芯片板块情绪低点，1 月 31 日收盘 40.67 元买入 100 万元。"),
        (4,"2023年5月","主升","416.99 万","ChatGPT 引爆 AI 行情，芯片龙头领涨，4 个月账户翻倍。"),
        (9,"2023年10月","回撤","174.48 万","行情退潮，商业化落地受质疑，5 个月回撤 58.16%。"),
        (13,"2024年2月","反弹","275.85 万","AI 落地预期升温，股价两个月反弹约 58%。"),
        (18,"2024年7月","继续反弹","433.27 万","国产替代逻辑强化，账户重回 400 万上方。"),
        (23,"2024年12月","翻倍","1083.35 万","新一代 AI 芯片发布，账户一年站上千万。"),
        (25,"2025年2月","继续上涨","1211.16 万","算力需求爆发，订单预期带动股价再创新高。"),
        (31,"2025年8月","10 倍","2460.44 万","股价破 1000 元，成为 A 股 AI 芯片第一股。"),
        (41,"2026年6月","区间最高","3923.16 万","算力景气延续，股价冲至 1595.55 元创区间新高。"),
        (44,"2026年9月","期末","2480.97 万","含 1 次分红 3.69 万，含息总资产 2484.66 万。")]

def stage_at(k):
    for i,(a,b,n) in enumerate(STAGES):
        if a<=k<b or (i==len(STAGES)-1 and k>=a): return i,a,b,n
    return 0,0,4,STAGES[0][2]

def alphas(kf):
    si,sa_,sb,sn = stage_at(kf)
    sa=1.0
    if kf-sa_<0.55: sa*=max(0.0,(kf-sa_)/0.55)
    if sb-kf<0.55 and sb<N: sa*=max(0.0,(sb-kf)/0.55)
    ei=-1
    for i,(st,*_ ) in enumerate(EVENTS):
        if kf>=st: ei=i
    ea=0.0
    if ei>=0:
        st=EVENTS[ei][0]; nxt=EVENTS[ei+1][0] if ei+1<len(EVENTS) else N+99
        ea=min(1.0,max(0.0,(kf-st)/0.5))
        if nxt-kf<0.45: ea=min(ea,max(0.0,(nxt-kf)/0.45))
    return sn,sa,ei,ea

LEAD_F=int(LEAD*FPS); SWEEP=int((N-1)*SEC_PER_NODE*FPS); TAIL_F=int(TAIL*FPS)
NF=LEAD_F+SWEEP+TAIL_F
py=lambda v: B-(B-T)*(v/YMAX)
pk_i=max(range(N), key=lambda i: nav[i]); pk_y=py(nav[pk_i])

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)

for fr in range(NF):
    if fr < LEAD_F: kf=0.0
    elif fr < LEAD_F+SWEEP: kf=(fr-LEAD_F)/FPS/SEC_PER_NODE
    else: kf=float(N-1)
    kf=min(kf,N-1.0)
    ki=min(int(kf),N-2); frac=kf-ki
    cv=nav[ki]+(nav[ki+1]-nav[ki])*frac

    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im,"RGBA")

    for a,b in DD_RANGES:
        d.rectangle([px(a),T,px(min(b,N-1)),B], fill=DD)
    for gv in range(0,int(YMAX)+1,int(YMAX/4)):
        y=py(gv); d.line([(L,y),(R,y)],fill=GRID,width=2)
        d.text((L-16,y),f"{gv:,.0f}",font=f(24),fill=DIM,anchor="rm")
    for gx in range(L,R,22):
        d.line([(gx,pk_y),(min(gx+12,R),pk_y)],fill=(84,44,58),width=2)
    d.text((R-6,pk_y-34),"区间峰值 3,923 万",font=f(23),fill=(150,80,96),anchor="ra")

    d.line([(L,T),(L,B)],fill=AXIS,width=3); d.line([(L,B),(R,B)],fill=AXIS,width=3)
    for a,b,n in STAGES:
        if a==0: continue
        d.line([(px(a),T),(px(a),B)],fill=(52,38,48),width=2)
    for i in range(N):
        maj=mon[i].endswith("-01")
        d.line([(px(i),B),(px(i),B+(14 if maj else 6))],fill=AXIS if maj else (46,34,42),width=3)
        if i%6==0: d.text(((px(i)),AXY),mon[i],font=f(23),fill=DIM,anchor="ma")

    cx,cy=px(kf),py(cv)
    pts=[(px(i),py(nav[i])) for i in range(ki+1)]+[(cx,cy)]
    if len(pts)>1: d.line(pts,fill=PINK,width=13,joint="curve")
    for st in [e[0] for e in EVENTS]:
        if st<=kf:
            x,y=px(st),py(nav[st]); d.ellipse([x-8,y-8,x+8,y+8],fill=WHITE)
    if kf>=pk_i:
        x,y=px(pk_i),py(nav[pk_i]); d.ellipse([x-11,y-11,x+11,y+11],fill=WHITE)
    d.ellipse([cx-24,cy-24,cx+24,cy+24],fill=(240,72,120,55))
    d.ellipse([cx-14,cy-14,cx+14,cy+14],fill=(255,226,236))
    for gy in range(int(cy)+38,B,24):
        d.line([(cx,gy),(cx,min(gy+12,B))],fill=(240,72,120,130),width=3)

    lab=min(int(kf+0.5),N-1); fa=1.0-abs(kf-lab); av=int(cv)
    d.text((L,247),"当前时点",font=f(30),fill=DIM)
    d.text((L,288),mon[lab].replace("-"," / "),font=f(62,True),fill=mix(WHITE,DIM,fa))
    d.text((R,262),f"{av:,} 万",font=f(96,True),fill=PINK,anchor="ra")
    if lab>0:
        c=(nav[lab]/nav[lab-1]-1)*100
        d.text((R,372),f"环比 {'+' if c>=0 else ''}{c:.1f}%",font=f(34),
               fill=(GREEN if c>=0 else RED),anchor="ra")

    sn,sa,ei,ea=alphas(kf)
    d.text((L,432),"阶段",font=f(26),fill=DIM)
    d.text((L+70,428),sn,font=f(38,True),fill=mix(PINK,DIM,sa))
    si=stage_at(kf)[0]
    for j in range(len(STAGES)):
        d.rectangle([L+j*54,488,L+j*54+44,494],fill=PINK if j<=si else (44,32,40))
    d.text((L,516),f"{STAGES[si][2]} · 阶段 {si+1}/{len(STAGES)}",font=f(24),fill=DIM)

    if ei>=0 and ea>0.01:
        tag,typ,val,body=EVENTS[ei][1],EVENTS[ei][2],EVENTS[ei][3],EVENTS[ei][4]
        y0=572
        d.rectangle([L,y0,R,y0+176],fill=(20,10,17))
        d.line([(L,y0),(L,y0+176)],fill=PINK,width=4)
        d.text((L+22,y0+18),tag,font=f(26),fill=mix(DIM,BG,ea))
        d.text((L+22,y0+52),typ,font=f(40,True),fill=mix(PINK,BG,ea))
        d.text((R-22,y0+56),val,font=f(40,True),fill=mix(WHITE,BG,ea),anchor="ra")
        d.text((L+22,y0+116),body[:30],font=f(23),fill=mix(DIM,BG,ea))
        d.text((L+22,y0+142),body[30:],font=f(23),fill=mix(DIM,BG,ea))

    d.text((R,440),"寒武纪 688256",font=f(30,True),fill=WHITE,anchor="ra")
    d.text((R,486),"2023-01 → 2026-09 · 共 45 个月",font=f(26),fill=DIM,anchor="ra")
    d.text((R,524),f"已揭示 {int(kf)+1} / {N} 个月",font=f(26),fill=DIM,anchor="ra")
    d.text((L,470),"累计净值",font=f(26),fill=DIM)
    d.text((L,506),f"{av:,}",font=f(40,True),fill=WHITE)
    d.text((L,566),"距峰值",font=f(26),fill=DIM)
    pk=max(nav[:lab+1]); dd=(nav[lab]/pk-1)*100
    d.text((L,602),f"{dd:.1f}%",font=f(40,True),fill=RED if dd<-0.5 else WHITE)

    d.rectangle([0,1722,W,1848],fill=(16,8,14))
    d.line([(0,1722),(W,1722)],fill=(240,72,120,90),width=2)
    d.text((L,1748),"数据来源：权威回测净值 · 仅为历史表现记录",font=f(23),fill=DIM)
    d.text((L,1790),"本视频不构成任何投资建议，市场有风险，决策需谨慎",font=f(23),fill=(150,90,100))
    d.text((R,1790),"最大回撤 −58.16% · 年化 140.17%",font=f(23),fill=(150,90,100),anchor="ra")

    im.save(os.path.join(OUT,f"f{fr:04d}.png"))
print(f"frames={NF}  dur={NF/FPS:.1f}s  ymax={YMAX:.0f}  ->  {OUT}")
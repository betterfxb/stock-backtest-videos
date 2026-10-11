# -*- coding: utf-8 -*-
"""瀹屾暣鍥捐〃娈垫牱鐗囷細鍥哄畾杞?+ 绮樻€х旱杞?+ 鍖€閫熻繛缁彮绀?+ 闃舵/浜嬩欢鏌斿拰娣″寲"""
import csv, os, shutil
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
LEAD, TAIL, SEC_PER_NODE = 1.0, 2.0, 0.5
OUT = r"C:\Users\19560\AppData\Local\Temp\opencode\full"

BG=(9,4,9); PINK=(240,72,120); WHITE=(240,240,240); DIM=(128,118,126)
GRID=(34,24,31); AXIS=(70,54,64); DD=(58,20,26); GREEN=(120,214,168); RED=(232,110,110)
L,R = 82, 891
T,B = 759, 1420
AXY = 1462

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

STAGES=[(0,4,"AI 琛屾儏"),(4,9,"琛屾儏閫€娼?),(9,13,"纾ㄥ簳"),(13,23,"鍥戒骇鏇夸唬"),
        (23,31,"绠楀姏鐖嗗彂"),(31,41,"鍐查《"),(41,44,"鍥炶惤")]
DD_RANGES=[(4,9),(41,44)]
EVENTS=[(0,"2023骞?鏈?,"璧锋姇","100.00 涓?,"AI 鑺墖鏉垮潡鎯呯华浣庣偣锛? 鏈?31 鏃ユ敹鐩?40.67 鍏冧拱鍏?100 涓囧厓銆?),
        (4,"2023骞?鏈?,"涓诲崌","416.99 涓?,"ChatGPT 寮曠垎 AI 琛屾儏锛岃姱鐗囬緳澶撮娑紝4 涓湀璐︽埛缈诲€嶃€?),
        (9,"2023骞?0鏈?,"鍥炴挙","174.48 涓?,"琛屾儏閫€娼紝鍟嗕笟鍖栬惤鍦板彈璐ㄧ枒锛? 涓湀鍥炴挙 58.16%銆?),
        (13,"2024骞?鏈?,"鍙嶅脊","275.85 涓?,"AI 钀藉湴棰勬湡鍗囨俯锛岃偂浠蜂袱涓湀鍙嶅脊绾?58%銆?),
        (18,"2024骞?鏈?,"缁х画鍙嶅脊","433.27 涓?,"鍥戒骇鏇夸唬閫昏緫寮哄寲锛岃处鎴烽噸鍥?400 涓囦笂鏂广€?),
        (23,"2024骞?2鏈?,"缈诲€?,"1083.35 涓?,"鏂颁竴浠?AI 鑺墖鍙戝竷锛岃处鎴蜂竴骞寸珯涓婂崈涓囥€?),
        (25,"2025骞?鏈?,"缁х画涓婃定","1211.16 涓?,"绠楀姏闇€姹傜垎鍙戯紝璁㈠崟棰勬湡甯﹀姩鑲′环鍐嶅垱鏂伴珮銆?),
        (31,"2025骞?鏈?,"10 鍊?,"2460.44 涓?,"鑲′环鐮?1000 鍏冿紝鎴愪负 A 鑲?AI 鑺墖绗竴鑲°€?),
        (41,"2026骞?鏈?,"鍖洪棿鏈€楂?,"3923.16 涓?,"绠楀姏鏅皵寤剁画锛岃偂浠峰啿鑷?1595.55 鍏冨垱鍖洪棿鏂伴珮銆?),
        (44,"2026骞?鏈?,"鏈熸湯","2480.97 涓?,"鍚?1 娆″垎绾?3.69 涓囷紝鍚伅鎬昏祫浜?2484.66 涓囥€?)]

def stage_at(k):
    for i,(a,b,n) in enumerate(STAGES):
        if a<=k<b or (i==len(STAGES)-1 and k>=a): return i,a,b,n
    return 0,0,4,STAGES[0][2]

def alphas(kf,t):
    # 闃舵娣″寲
    si,sa,sb,sn = stage_at(kf)
    sa_ = 1.0
    if kf-sa<0.55: sa_*=max(0.0,(kf-sa)/0.55)
    if sb-kf<0.55 and sb<N: sa_*=max(0.0,(sb-kf)/0.55)
    # 浜嬩欢娣″寲
    ei=-1
    for i,(st,*_ ) in enumerate(EVENTS):
        if kf>=st: ei=i
    ea=0.0
    if ei>=0:
        st=EVENTS[ei][0]
        nxt=EVENTS[ei+1][0] if ei+1<len(EVENTS) else N+99
        ea=min(1.0,max(0.0,(kf-st)/0.5))
        if nxt-kf<0.45: ea=min(ea,max(0.0,(nxt-kf)/0.45))
    return sn,sa_,ei,ea

LEAD_F=int(LEAD*FPS); SWEEP=int((N-1)*SEC_PER_NODE*FPS); TAIL_F=int(TAIL*FPS)
NF=LEAD_F+SWEEP+TAIL_F

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)

for fr in range(NF):
    if fr < LEAD_F:
        kf=0.0
    elif fr < LEAD_F+SWEEP:
        kf=(fr-LEAD_F)/FPS/SEC_PER_NODE
    else:
        kf=float(N-1)
    kf=min(kf,N-1.0)
    ki=min(int(kf),N-2); frac=kf-ki
    cv=nav[ki]+(nav[ki+1]-nav[ki])*frac

    ymax=4000.0
    py=lambda v: B-(B-T)*(v/ymax)

    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im,"RGBA")

    for a,b in DD_RANGES:
        d.rectangle([px(a),T,px(min(b,N-1)),B], fill=DD)
for gv in range(0,int(ymax)+1,int(ymax/4)):
        y=py(gv); d.line([(L,y),(R,y)],fill=GRID,width=2)
        d.text((L-16,y),f"{gv:,.0f}",font=f(24),fill=DIM,anchor="rm")
    pk_i=int(np.argmax(nav)); pk_y=py(nav[pk_i])
    for gx in range(L,R,22): d.line([(gx,pk_y),(min(gx+12,R),pk_y)],fill=(84,44,58),width=2)
    d.text((R-6,pk_y-34),"区间峰值 3,923 万",font=f(23),fill=(150,80,96),anchor="ra")
    d.line([(L,T),(L,B)],fill=AXIS,width=3); d.line([(L,B),(R,B)],fill=AXIS,width=3)

    for a,b,n in STAGES:
        if a==0: continue
        d.line([(px(a),T),(px(a),B)],fill=(52,38,48),width=2)
    for i in range(N):
        maj=mon[i].endswith("-01")
        d.line([(px(i),B),(px(i),B+(14 if maj else 6))],fill=AXIS if maj else (46,34,42),width=3)
        if i%6==0: d.text((px(i),AXY),mon[i],font=f(23),fill=DIM,anchor="ma")

    cx,cy=px(kf),py(cv)
    pts=[(px(i),py(nav[i])) for i in range(ki+1)]+[(cx,cy)]
    if len(pts)>1: d.line(pts,fill=PINK,width=13,joint="curve")
    for st,_,_,_,_ in EVENTS:
        if st<=kf:
            x,y=px(st),py(nav[st]); d.ellipse([x-8,y-8,x+8,y+8],fill=WHITE)
    d.ellipse([cx-22,cy-22,cx+22,cy+22],fill=(240,72,120,55))
    d.ellipse([cx-13,cy-13,cx+13,cy+13],fill=(255,226,236))
    for gy in range(int(cy)+36,B,24):
        d.line([(cx,gy),(cx,min(gy+12,B))],fill=(240,72,120,130),width=3)

    lab=min(int(kf+0.5),N-1); fa=1.0-abs(kf-lab)
    av=int(cv)
    d.text((L,247),"褰撳墠鏃剁偣",font=f(30),fill=DIM)
    d.text((L,288),mon[lab].replace("-"," / "),font=f(62,True),fill=mix(WHITE,DIM,fa))
    d.text((R,262),f"{av:,} 涓?,font=f(96,True),fill=PINK,anchor="ra")
    if lab>0:
        c=(nav[lab]/nav[lab-1]-1)*100
        d.text((R,372),f"鐜瘮 {'+' if c>=0 else ''}{c:.1f}%",font=f(34),
               fill=(GREEN if c>=0 else RED),anchor="ra")

    sn,sa,ei,ea=alphas(kf,fr)
    d.text((L,432),"闃舵",font=f(26),fill=DIM)
    d.text((L+70,428),sn,font=f(38,True),fill=mix(PINK,DIM,sa))
    si=stage_at(kf)[0]
    for j,(a,b,n) in enumerate(STAGES):
        d.rectangle([L+j*54,488,L+j*54+44,494],fill=PINK if j<=si else (44,32,40))
    d.text((L,516),f"{STAGES[si][2]} 路 闃舵 {si+1}/{len(STAGES)}",font=f(24),fill=DIM)

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

    d.text((R,440),"瀵掓绾?688256",font=f(30,True),fill=WHITE,anchor="ra")
    d.text((R,486),"2023-01 鈫?2026-09 路 鍏?45 涓湀",font=f(26),fill=DIM,anchor="ra")
    d.text((R,524),f"宸叉彮绀?{int(kf)+1} / {N} 涓湀",font=f(26),fill=DIM,anchor="ra")
    d.text((L,470),"绱鍑€鍊?,font=f(26),fill=DIM)
    d.text((L,506),f"{av:,}",font=f(40,True),fill=WHITE)
    d.text((L,566),"璺濆嘲鍊?,font=f(26),fill=DIM)
    pk=max(nav[:lab+1]); dd=(nav[lab]/pk-1)*100
    d.text((L,602),f"{dd:.1f}%",font=f(40,True),fill=RED if dd<-0.5 else WHITE)

    d.rectangle([0,1722,W,1848],fill=(16,8,14))
    d.line([(0,1722),(W,1722)],fill=(240,72,120,90),width=2)
    d.text((L,1748),"鏁版嵁鏉ユ簮锛氭潈濞佸洖娴嬪噣鍊?路 浠呬负鍘嗗彶琛ㄧ幇璁板綍",font=f(23),fill=DIM)
    d.text((L,1790),"鏈棰戜笉鏋勬垚浠讳綍鎶曡祫寤鸿锛屽競鍦烘湁椋庨櫓锛屽喅绛栭渶璋ㄦ厧",font=f(23),fill=(150,90,100))
    d.text((R,1790),"鏈€澶у洖鎾?鈭?8.16% 路 骞村寲 140.17%",font=f(23),fill=(150,90,100),anchor="ra")

    im.save(os.path.join(OUT,f"f{fr:04d}.png"))
print(f"frames={NF}  dur={NF/FPS:.1f}s  ->  {OUT}")



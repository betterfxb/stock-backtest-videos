r"""从 klines_all.json 生成完整的 src/data.ts（单一数据源，杜绝手工转录错误）。

用法: python gen_data_ts.py <code> [输出路径]
  python gen_data_ts.py 002371            -> video_analysis/data_002371.ts
  python gen_data_ts.py 002371 ..\naura-video\src\data.ts

数值全部现算；叙事文案来自 episodes.py（人工核验）。
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from episodes import EPISODES, UNIVERSE

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)
code = sys.argv[1]

if code not in EPISODES:
    print(f"未知标的 {code}；episodes.py 里没有它的叙事配置。可选: {sorted(EPISODES)}")
    sys.exit(1)

cfg = EPISODES[code]
STAGES, EVENTS = cfg["stages"], cfg["events"]
BEATS = cfg.get("beats")
if BEATS is None:
    # 兜底：没写 beats 就按事件类型关键词自动挑 ≤4 个（老期配置不漏改）
    KEY = ("跌破本金", "破发", "翻倍", "最深回撤", "区间最高")
    BEATS = [(i, ty if ty != "破发" else "跌破本金")
             for i, _t, ty, _b in EVENTS if any(k in ty for k in KEY)][:4]
name, secid, episode = UNIVERSE[code]

SRC_NOTE = cfg.get("srcNote", "东方财富 push2his 月K（klt=103，前复权 fqt=1），随附 klines_all.json 快照")
CAL_NOTE = cfg.get("calNote", '按前复权收盘价推算模拟净值；现金分红未单独计入，故全文不宣称"含息"。')
SRC_TAG = cfg.get("srcTag", "东方财富 push2his 月K 前复权")

raw = json.load(open(os.path.join(HERE, "klines_all.json"), encoding="utf-8-sig"))[code]
rows = raw["rows"]

base = rows[0]["close"]
wan = [100.0 * r["close"] / base for r in rows]
peak, dd = 0.0, []
for v in wan:
    peak = max(peak, v)
    dd.append(round((v - peak) / peak, 4))

n = len(rows)
months = n - 1
total = wan[-1] - 100.0
cagr = ((wan[-1] / 100.0) ** (12 / months) - 1) * 100
CAGR_TXT = ("\u2212" if cagr < 0 else "") + f"{abs(cagr):.2f}%"
mdd = min(dd) * 100
rets = [(wan[i] / wan[i - 1] - 1) * 100 for i in range(1, n)]
mu = sum(rets) / len(rets)
vol = (sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)) ** 0.5 * (12 ** 0.5)
win = sum(1 for r in rets if r > 0) / len(rets) * 100

# 自动检出回撤段
segs, start = [], None
for i, d in enumerate(dd):
    if d < 0 and start is None:
        start = i
    elif d == 0 and start is not None:
        segs.append([start, i - 1]); start = None
if start is not None:
    segs.append([start, n - 1])

# 收敛：丢弃仅单月的浅回撤，避免底纹闪烁
merged = [s for s in segs if s[1] - s[0] >= 1]
# 最长回撤段（收尾文案与封面 B 都用它，不手写"34 个月"这种数）
longest = max(merged, key=lambda s: s[1] - s[0]) if merged else [0, 0]
longest_months = longest[1] - longest[0] + 1
min_i = min(range(n), key=lambda i: wan[i])

peak_i = max(range(n), key=lambda i: wan[i])
# 纵轴上限取自与 src/axis.ts 同一套档位表（AXIS_STEPS）：顶值恒为 step×4，
# 保证 0/25%/50%/75%/100% 五条刻度都是整数。
# 旧公式 int(峰值*1.08/1000+1)*1000 只适配「峰值上千」的题材；亏损题材（峰值
# 两百万级）会被顶到 1000，曲线压在底部 20%，封面与开场预览直接失去可读性。
AXIS_STEPS = [25, 50, 100, 200, 250, 500, 1000, 2000, 2500]
_need = max(wan[-1], wan[peak_i]) * 1.08
ymax = next((s * 4 for s in AXIS_STEPS if s * 4 >= _need), AXIS_STEPS[-1] * 4)

# ── 叙事自检：文案引用的索引必须与真实数据一致 ────────────────────
errs = []
if STAGES[0][0] != 0:
    errs.append(f"STAGES 未从 idx 0 开始（实际 {STAGES[0][0]}）")
if STAGES[-1][1] != months:
    errs.append(f"STAGES 未覆盖到 idx {months}（实际 {STAGES[-1][1]}）")
for (a0, a1, _), (b0, b1, _) in zip(STAGES, STAGES[1:]):
    if a1 != b0:
        errs.append(f"STAGES 断层/重叠：{a1} -> {b0}")
for e_idx, tag, _ty, body in EVENTS:
    if not 0 <= e_idx <= months:
        errs.append(f"EVENTS idx {e_idx}（{tag}）越界 0..{months}")
    if len(body) > 50:
        errs.append(f"EVENTS 正文 {len(body)} 字 > 50（{tag}）")
for b_idx, _lb in BEATS:
    if not 0 <= b_idx <= months:
        errs.append(f"BEATS idx {b_idx} 越界 0..{months}")
if len(BEATS) > 4:
    errs.append(f"BEATS {len(BEATS)} 个 > 4，标注太密等于没有重点")
for idx in [e[0] for e in EVENTS]:
    if idx in (min_i, peak_i) and idx not in (0, months):
        pass  # 极值事件可缺席，由人工判断
if errs:
    print("叙事配置自检失败：")
    for e in errs:
        print("  ✗", e)
    sys.exit(1)


def f2(v):
    return f"{v:.2f}"


nav_txt = "\n".join(
    f'  {{ date: "{r["date"]}", close: {r["close"]}, wan: {f2(wan[i])}, dd: {dd[i]} }},'
    for i, r in enumerate(rows))
st_txt = "\n".join(f'  {{ from: {a}, to: {b}, name: "{nm}" }},' for a, b, nm in STAGES)
ev_txt = "\n".join(
    f'  {{\n    idx: {i},\n    tag: "{t}",\n    type: "{ty}",\n'
    f'    value: "{f2(wan[i])} 万",\n    body: "{bd}",\n  }},'
    for i, t, ty, bd in EVENTS)
dd_txt = "\n" + "\n".join(f"  [{a}, {b}]," for a, b in merged) + "\n"
bt_txt = "\n".join(f'  {{ idx: {i}, label: "{lb}" }},' for i, lb in BEATS)

out = f"""// {episode} {name} {secid} —— 数据层（本文件由 gen_data_ts.py 自动生成，勿手改）
// 数据来源：{SRC_NOTE}
// 口径：{CAL_NOTE}
// 区间 {rows[0]['date']} ~ {rows[-1]['date']}  共 {months} 个月
// 累计 {total:.2f}%  年化 {cagr:.2f}%  最大回撤 {mdd:.2f}%  年化波动 {vol:.2f}%  月胜率 {win:.1f}%

export const NAV: {{ date: string; close: number; wan: number; dd: number }}[] = [
{nav_txt}
];

// 回撤段（暗红底纹）。脚本按 dd<0 自动检出，剔除单月浅回撤后共 {len(merged)} 段。
export const DD_RANGES: [number, number][] = [{dd_txt}];

// 阶段标签（按数据索引区间）
export const STAGES: {{ from: number; to: number; name: string }}[] = [
{st_txt}
];

// 事件卡（正文 ≤ 50 字）。idx = {n} 个月序列的数据下标（0..{months}），
// 出帧时间由分段配速 src/reveal.ts 推导（事件密集处最短停留 90 帧），
// 保证事件卡与图表笔尖严格同步。
export const EVENTS: {{
  idx: number;
  tag: string;
  type: string;
  value: string;
  body: string;
}}[] = [
{ev_txt}
];

// 关键节点标注（BeatOverlay，≤4 个）：最新到达的保留、旧的交叉淡出；
// 标注金额由渲染端现取 NAV[idx]，这里只给人工核验的标签。
export const BEATS: {{ idx: number; label: string }}[] = [
{bt_txt}
];

export const METRICS = {{
  code: "{secid}",
  name: "{name}",
  episode: "{episode}",
  range: "{rows[0]['date']} ~ {rows[-1]['date']}",
  startYM: "{rows[0]['date'][:7]}",
  totalRet: "{total:.2f}%",
  cagr: "{CAGR_TXT}",
  mdd: "\u2212{abs(mdd):.2f}%",
  vol: "{vol:.2f}%",
  winRate: "{win:.1f}%",
  months: "{n} 个月",
  endAsset: "{f2(wan[-1])} 万",
  peakAsset: "{f2(wan[peak_i])} 万",
  peakDate: "{rows[peak_i]['date']}",
  minAsset: "{f2(wan[min_i])} 万",
  minDate: "{rows[min_i]['date']}",
  minMonth: "第 {min_i + 1} 个月",
  longestDdMonths: "{longest_months}",
  endVsPeak: "{(wan[-1] / wan[peak_i] - 1) * 100:.2f}%",
  principal: 100,
  source: "{SRC_TAG}",
}};

// 钩子/收尾/封面用定稿文案（人工核验，随叙事配置一起改）
export const COPY = {{
  hold: "{cfg['holdText']}",
  hookSub: "{cfg['hookSub']}",
  closingQ: "{cfg['closingQ']}",
}};

// 纵轴上限：脚本按峰值上浮 8% 后取整到千位
export const YMAX = {ymax};

// 配色：深海军蓝底 + 金强调（数字/品牌）+ 亮蓝曲线（金融终端风）
export const C = {{
  bg: "#0A1128",
  paper: "#0E1730",
  panel: "#141F3D",
  brand: "#F0B860",
  brandSoft: "#F8DCA4",
  line: "#4E9EFF",
  glow: "#16407C",
  dd: "#3E2438",
  gold: "#F0B860",
  amber: "#F5CE6A",
  peak: "#FFD58A",
  grid: "#1C2A4A",
  axis: "#8A93B5",
  ink: "#F2F5FF",
  inkSoft: "#B6BFD8",
  up: "#4FD39A",
  down: "#FF6B6B",
}};
"""

dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, f"data_{code}.ts")
open(dst, "w", encoding="utf-8").write(out)
print(f"{name}({secid})  {months} 个月  {rows[0]['date']} ~ {rows[-1]['date']}")
print(f"累计 {total:.2f}%  年化 {cagr:.2f}%  回撤 {mdd:.2f}%  波动 {vol:.2f}%  胜率 {win:.1f}%")
print(f"峰值 {wan[peak_i]:.2f} 万 @ {rows[peak_i]['date']}   "
      f"终点 {wan[-1]:.2f} 万 ({(wan[-1] / wan[peak_i] - 1) * 100:+.2f}% vs peak)")
print(f"最低 {wan[min_i]:.2f} 万 @ {rows[min_i]['date']} (第 {min_i+1} 个月)  最长回撤 {longest_months} 个月")
print(f"回撤段 {merged}\nYMAX={ymax}\n-> {dst}")
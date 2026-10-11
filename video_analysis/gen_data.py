"""从 klines_all.json 生成新标的 data.ts 骨架。
用法: python gen_data.py 300502
输出: gen_data_300502.ts（含 NAV / DD_RANGES / 指标）
事件与阶段文案由人工补，脚本只负责真实数据部分。
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
code = sys.argv[1]

with open(os.path.join(HERE, "klines_all.json"), encoding="utf-8-sig") as f:
    raw = json.load(f)

it = raw[code]
rows = it["rows"]
NAMES = {
    "300308": "中际旭创", "002463": "沪电股份", "300502": "新易盛",
    "688981": "中芯国际", "688012": "中微公司", "002371": "北方华创",
    "002415": "海康威视", "300750": "宁德时代",
}
name = NAMES[code]

base = rows[0]["close"]
nav, dd = [], []
peak = 0.0
for r in rows:
    wan = 100.0 * r["close"] / base
    wan = round(wan, 2)
    if wan > peak:
        peak = wan
    dd.append(round((wan - peak) / peak, 4))
    nav.append({"date": r["date"], "close": r["close"], "wan": wan})

n = len(nav)
months = n - 1
total = (nav[-1]["wan"] / 100.0 - 1) * 100
cagr = ((nav[-1]["wan"] / 100.0) ** (12 / months) - 1) * 100
mdd = min(dd) * 100

rets = [(nav[i]["wan"] / nav[i - 1]["wan"] - 1) * 100 for i in range(1, n)]
mu = sum(rets) / len(rets)
var = sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)
vol = var ** 0.5 * (12 ** 0.5)
win = sum(1 for r in rets if r > 0) / len(rets) * 100

peak_i = max(range(n), key=lambda i: nav[i]["wan"])
print(f"{name}({code})  {months} 个月  {rows[0]['date']} ~ {rows[-1]['date']}")
print(f"累计 {total:.2f}%  年化 {cagr:.2f}%  回撤 {mdd:.2f}%  波动 {vol:.2f}%  胜率 {win:.1f}%")
print(f"峰值 {nav[peak_i]['wan']:.2f} 万 @ {nav[peak_i]['date']}   终点 {nav[-1]['wan']:.2f} 万")
print(f"YMAX 建议 {int(max(nav[-1]['wan'], nav[peak_i]['wan']) * 1.08 / 500 + 1) * 500}")

# 回撤段
segs, start = [], None
for i, d in enumerate(dd):
    if d < 0 and start is None:
        start = i
    elif d == 0 and start is not None:
        segs.append([start, i - 1])
        start = None
if start is not None:
    segs.append([start, n - 1])
print(f"\n回撤段: {segs}")

lines = []
for i, p in enumerate(nav):
    lines.append(f'  {{ date: "{p["date"]}", close: {p["close"]}, wan: {p["wan"]}, dd: {dd[i]} }},')
body = "\n".join(lines)

with open(os.path.join(HERE, f"gen_data_{code}.ts"), "w", encoding="utf-8") as f:
    f.write(f"""// 自动生成：真实月K（东方财富 push2his，前复权）
// {name} {code}  {months} 个月  {rows[0]['date']} ~ {rows[-1]['date']}
// 累计 {total:.2f}%  年化 {cagr:.2f}%  最大回撤 {mdd:.2f}%  波动 {vol:.2f}%  胜率 {win:.1f}%

export const NAV: {{ date: string; close: number; wan: number; dd: number }}[] = [
{body}
];

export const DD_RANGES: [number, number][] = {segs};
""")

print(f"\n已生成 gen_data_{code}.ts（NAV {n} 行, 回撤段 {len(segs)} 段）")
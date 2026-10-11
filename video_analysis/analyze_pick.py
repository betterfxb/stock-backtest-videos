"""为第 005 期挑标的前，先把候选的真实叙事节点算清楚（不靠印象）。
用法: python analyze_pick.py 002371
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
code = sys.argv[1]
NAMES = {
    "300308": "中际旭创", "002463": "沪电股份", "300502": "新易盛",
    "688981": "中芯国际", "688012": "中微公司", "002371": "北方华创",
    "002415": "海康威视", "300750": "宁德时代",
}

rows = json.load(open(os.path.join(HERE, "klines_all.json"), encoding="utf-8-sig"))[code]["rows"]
n = len(rows)
base = rows[0]["close"]
wan = [100.0 * r["close"] / base for r in rows]
months = n - 1

peak, dd = 0.0, []
for v in wan:
    peak = max(peak, v)
    dd.append((v - peak) / peak)

rets = [(wan[i] / wan[i - 1] - 1) * 100 for i in range(1, n)]
mu = sum(rets) / len(rets)
vol = (sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)) ** 0.5 * (12 ** 0.5)
win = sum(1 for r in rets if r > 0) / len(rets) * 100
total = wan[-1] - 100
cagr = ((wan[-1] / 100.0) ** (12 / months) - 1) * 100
mdd_i = min(range(n), key=lambda i: dd[i])
peak_i = max(range(n), key=lambda i: wan[i])
peak_before = max(range(0, mdd_i + 1), key=lambda i: wan[i])
mn_i = min(range(n), key=lambda i: wan[i])
mx_i = max(range(n), key=lambda i: wan[i])

print(f"=== {NAMES[code]} {code}  {rows[0]['date']} ~ {rows[-1]['date']}  {months} 个月 ===")
print(f"累计 {total:.2f}%  年化 {cagr:.2f}%  最大回撤 {dd[mdd_i]*100:.2f}%  波动 {vol:.2f}%  胜率 {win:.1f}%")
print(f"区间最低 {wan[mn_i]:.2f} 万 @ {rows[mn_i]['date']} (idx{mn_i})")
print(f"区间最高 {wan[mx_i]:.2f} 万 @ {rows[mx_i]['date']} (idx{mx_i})")
print(f"终点 {wan[-1]:.2f} 万  距峰值 {(wan[-1]/wan[mx_i]-1)*100:.2f}%")
print(f"最深回撤 {dd[mdd_i]*100:.2f}%  {rows[peak_before]['date']}({wan[peak_before]:.2f}) -> {rows[mdd_i]['date']}({wan[mdd_i]:.2f})")
print(f"是否跌破本金 100 万: {'是' if wan[mn_i] < 100 else '否，最低 %.2f 万' % wan[mn_i]}")

print("\n-- 单月涨跌幅 Top5 --")
rank = sorted(range(1, n), key=lambda i: -rets[i - 1])[:5]
for i in rank:
    print(f"  idx{i:3d} {rows[i]['date']}  {rets[i-1]:+7.2f}%  {wan[i-1]:8.2f} -> {wan[i]:8.2f} 万")

print("\n-- 单月跌幅 Top5 --")
for i in sorted(range(1, n), key=lambda i: rets[i - 1])[:5]:
    print(f"  idx{i:3d} {rows[i]['date']}  {rets[i-1]:+7.2f}%  {wan[i-1]:8.2f} -> {wan[i]:8.2f} 万")

print("\n-- 回撤段（>=2 个月）--")
segs, st = [], None
for i, d in enumerate(dd):
    if d < 0 and st is None:
        st = i
    elif d == 0 and st is not None:
        segs.append([st, i - 1]); st = None
if st is not None:
    segs.append([st, n - 1])
for a, b in segs:
    if b - a < 1:
        continue
    print(f"  [{a:3d},{b:3d}]  {rows[a]['date']} ~ {rows[b]['date']}  {b-a+1:2d}月  "
          f"{wan[a]:7.2f} -> {min(wan[a:b+1]):7.2f} 万  最深 {min(dd[a:b+1])*100:6.2f}%")

print("\n-- 是否存在长期横盘（连续同档位震荡 >=12 个月）--")
for a in range(0, n - 11):
    lo, hi = min(wan[a:a + 12]), max(wan[a:a + 12])
    if hi / lo < 1.35 and a == 0:
        pass
segs2 = []
i = 0
while i < n:
    j = i
    while j + 1 < n and wan[j + 1] / wan[i] < 2.2 and wan[j + 1] / wan[i] > 0.55:
        j += 1
    if j - i >= 11:
        segs2.append((i, j))
    i = max(j, i + 1)
for a, b in segs2:
    print(f"  [{a:3d},{b:3d}]  {rows[a]['date']} ~ {rows[b]['date']}  {b-a+1:2d}月  "
          f"{wan[a]:7.2f} ~ {wan[b]:7.2f} 万")

print("\n-- 逐月全量（供挑选事件节点）--")
for i in range(n):
    r = f"{rets[i-1]:+6.2f}%" if i else "   —   "
    print(f"  idx{i:3d} {rows[i]['date']}  close {rows[i]['close']:7.2f}  {wan[i]:8.2f} 万  {r}  dd {dd[i]*100:7.2f}%")
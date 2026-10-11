"""校验 data.ts 与接口原始数据完全一致，并复算所有指标。
用法: python verify_data.py <data.ts 路径> <code>
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ts_path = sys.argv[1]
code = sys.argv[2]

raw = json.load(open(os.path.join(HERE, "klines_all.json"), encoding="utf-8-sig"))[code]
rows = raw["rows"]
lines = open(ts_path, encoding="utf-8").read().splitlines()
src = "\n".join(lines)

ROW = re.compile(r'date:\s*"([\d-]+)",\s*close:\s*([\d.]+),\s*wan:\s*([\d.]+),\s*dd:\s*(-?[\d.]+)')


def block_after(marker):
    """取 marker 所在行到其闭合 ';' 之间的文本（按括号深度扫描，避免正则回溯歧义）。"""
    start = next(k for k, l in enumerate(lines) if marker in l and "export const" in l)
    depth, out = 0, []
    for k in range(start, len(lines)):
        l = lines[k]
        out.append(l)
        depth += l.count("[") + l.count("{") - l.count("]") - l.count("}")
        if depth == 0 and k > start:
            return "\n".join(out)
    return "\n".join(out)


nav = [{"date": m[0], "close": float(m[1]), "wan": float(m[2]), "dd": float(m[3])}
       for m in ROW.findall(block_after("const NAV"))]

fail = 0
print(f"NAV 条数: ts={len(nav)}  api={len(rows)}")
if len(nav) != len(rows):
    fail += 1
    print("  [FAIL] 数量不符")

base = rows[0]["close"]
peak = 0.0
nav_round = True  # 生成器先 round wan 到 2 位，再据此算 dd
for i, (n, r) in enumerate(zip(nav, rows)):
    if n["date"] != r["date"]:
        print(f"  [FAIL] idx{i} date {n['date']} != {r['date']}"); fail += 1
    if abs(n["close"] - r["close"]) > 1e-9:
        print(f"  [FAIL] idx{i} close {n['close']} != {r['close']}"); fail += 1
    exp_wan = round(100.0 * r["close"] / base, 2)
    if abs(n["wan"] - exp_wan) > 0.011:
        print(f"  [FAIL] idx{i} wan {n['wan']} != {exp_wan}"); fail += 1
    peak = max(peak, exp_wan)
    exp_dd = round((n["wan"] - peak) / peak, 4)
    if abs(n["dd"] - exp_dd) > 0.0002:
        print(f"  [FAIL] idx{i} dd {n['dd']} != {exp_dd}"); fail += 1

print("逐行核对:", "全部通过" if fail == 0 else f"{fail} 处不符")

n = len(nav)
months = n - 1
total = (nav[-1]["wan"] / 100.0 - 1) * 100
cagr = ((nav[-1]["wan"] / 100.0) ** (12 / months) - 1) * 100
mdd = min(x["dd"] for x in nav) * 100
rets = [(nav[i]["wan"] / nav[i - 1]["wan"] - 1) * 100 for i in range(1, n)]
mu = sum(rets) / len(rets)
var = sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)
vol = var ** 0.5 * (12 ** 0.5)
win = sum(1 for r in rets if r > 0) / len(rets) * 100
pk = max(range(n), key=lambda i: nav[i]["wan"])

print(f"\n复算: {months} 个月  累计 {total:.2f}%  年化 {cagr:.2f}%  回撤 {mdd:.2f}%  "
      f"波动 {vol:.2f}%  胜率 {win:.1f}%")
print(f"峰值 {nav[pk]['wan']:.2f} 万 @ {nav[pk]['date']}   终点 {nav[-1]['wan']:.2f} 万")

mm = block_after("const METRICS")


def g(key):
    m = re.search(key + r':\s*"([^"]*)"', mm)
    return m.group(1) if m else None


checks = [("range", f"{nav[0]['date']} ~ {nav[-1]['date']}"),
          ("totalRet", f"{total:.2f}%"),
          ("cagr", f"{cagr:.2f}%"),
          ("mdd", "\u2212" + f"{abs(mdd):.2f}%"),
          ("vol", f"{vol:.2f}%"),
          ("winRate", f"{win:.1f}%"),
          ("months", f"{n} 个月"),
          ("endAsset", f"{nav[-1]['wan']:.2f} 万")]
print()
for k, exp in checks:
    got = g(k)
    ok = got == exp
    if not ok:
        fail += 1
    print(f"  [{'ok  ' if ok else 'FAIL'}] {k}: {got!r}" + ("" if ok else f"  应为 {exp!r}"))

print()
for idx, val in re.findall(r'idx:\s*(\d+),[\s\S]*?value:\s*"([\d.]+) 万"', src):
    i = int(idx)
    ok = abs(nav[i]["wan"] - float(val)) < 0.011
    if not ok:
        fail += 1
    print(f"  [{'ok  ' if ok else 'FAIL'}] event idx{i} value={val} vs NAV {nav[i]['wan']}")

dd_txt = block_after("const DD_RANGES")
print()
for a, b in re.findall(r"\[(\d+),\s*(\d+)\]", dd_txt):
    a, b = int(a), int(b)
    bad = [i for i in range(a, b + 1) if nav[i]["dd"] >= 0]
    if bad:
        fail += 1
        print(f"  [FAIL] DD段 [{a},{b}] 含非回撤点 {bad[:5]}")
    else:
        print(f"  [ok  ] DD段 [{a},{b}] 全为回撤 ({nav[a]['date']} ~ {nav[b]['date']})")

st_txt = block_after("const STAGES")
print()
prev_to = None
for f_, t_, nm in re.findall(r"from:\s*(\d+),\s*to:\s*(\d+),\s*name:\s*\"([^\"]+)\"", st_txt):
    f_, t_ = int(f_), int(t_)
    ok = (prev_to is None or f_ == prev_to) and 0 <= f_ < t_ <= n - 1
    if not ok:
        fail += 1
    print(f"  [{'ok  ' if ok else 'FAIL'}] stage {nm}: [{f_},{t_}]"
          + ("" if ok else f"  需首尾相接且 0<=from<to<={months}，prev_to={prev_to}"))
    prev_to = t_
if prev_to != months:
    fail += 1
    print(f"  [FAIL] 阶段未覆盖到末月: 末段 to={prev_to}, 应为 {months}")

print("\n== 结论:", "PASS" if fail == 0 else f"{fail} 项 FAIL", "==")
sys.exit(1 if fail else 0)
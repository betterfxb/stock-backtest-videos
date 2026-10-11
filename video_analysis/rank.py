"""从 klines_all.json 计算指标并按叙事张力排序。用法: python rank.py"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "klines_all.json"), encoding="utf-8-sig") as f:
    raw = json.load(f)

# 接口 fields1=f1,f2 不返回名称，这里补权威中文名（已人工核对）
NAMES = {
    "300308": "中际旭创", "002463": "沪电股份", "300502": "新易盛",
    "688981": "中芯国际", "688012": "中微公司", "002371": "北方华创",
    "002415": "海康威视", "300750": "宁德时代",
}

items = raw.values() if isinstance(raw, dict) else raw


def analyse(rows):
    n = len(rows)
    base = rows[0]["close"]
    nav = [100.0 * r["close"] / base for r in rows]
    months = n - 1
    if months < 12:
        return None
    total = nav[-1] - 100.0
    cagr = ((nav[-1] / 100.0) ** (12 / months) - 1) * 100
    peak, peak_i = nav[0], 0
    mdd, mdd_f, mdd_t = 0.0, 0, 0
    for i, v in enumerate(nav):
        if v > peak:
            peak, peak_i = v, i
        dd = (v - peak) / peak * 100
        if dd < mdd:
            mdd, mdd_f, mdd_t = dd, peak_i, i
    rets = [(nav[i] / nav[i - 1] - 1) * 100 for i in range(1, n)]
    mu = sum(rets) / len(rets)
    var = sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)
    vol = var ** 0.5 * (12 ** 0.5)
    wins = sum(1 for r in rets if r > 0)
    bi = max(range(len(rets)), key=lambda i: rets[i]) + 1
    pi = nav.index(max(nav))
    return dict(months=months, start=rows[0]["date"], end=rows[-1]["date"],
                total=total, cagr=cagr, mdd=mdd, vol=vol,
                winrate=wins / len(rets) * 100, end_nav=nav[-1],
                peak_nav=max(nav), peak_date=rows[pi]["date"],
                mdd_from=rows[mdd_f]["date"], mdd_to=rows[mdd_t]["date"],
                best_month=rows[bi]["date"], best_ret=rets[bi - 1],
                nav=nav, rows=rows)


print(f"{'名称':10}{'月':>4}{'累计%':>9}{'年化%':>8}{'回撤%':>8}{'波动%':>7}{'胜率%':>7}{'峰值':>8}{'终点':>9}")
print("-" * 78)
res = []
for it in items:
    m = analyse(it["rows"])
    if not m:
        continue
    nm = NAMES.get(it["code"], it["code"])
    res.append((it["code"], nm, m))
    print(f"{nm:10}{m['months']:>4}{m['total']:>9.0f}{m['cagr']:>8.0f}{m['mdd']:>8.0f}"
          f"{m['vol']:>7.0f}{m['winrate']:>7.0f}{m['peak_nav']:>8.0f}{m['end_nav']:>9.0f}")

print("\n=== 叙事张力 = 0.4*最大月涨 + 0.6*|最大回撤| ===")
for code, name, m in sorted(res, key=lambda t: -(abs(t[2]["best_ret"]) * .4 + abs(t[2]["mdd"]) * .6)):
    s = abs(m["best_ret"]) * .4 + abs(m["mdd"]) * .6
    print(f"  {name}({code})  张力={s:5.1f}  累计={m['total']:6.0f}%  年化={m['cagr']:5.0f}%  "
          f"回撤={m['mdd']:5.0f}%  最大月涨={m['best_ret']:5.0f}%({m['best_month']})  "
          f"峰值日={m['peak_date']}  谷底日={m['mdd_to']}")

with open(os.path.join(HERE, "ranked.json"), "w", encoding="utf-8") as f:
    json.dump([{"code": c, "name": n, **{k: v for k, v in m.items() if k != "rows"}}
               for c, n, m in res], f, ensure_ascii=False, indent=1)
print("\n已存 ranked.json")
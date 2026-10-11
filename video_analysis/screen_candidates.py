"""
候选科技股筛选：抓真实月K，算净值与指标，按「叙事张力」排序。
数据源：东方财富 push2his（月K，前复权）。
用法：python screen_candidates.py
"""
import json, time, urllib.request

CANDIDATES = [
    ("300308", "中际旭创", "1"),   # 光模块
    ("002463", "沪电股份", "0"),   # PCB/AI服务器
    ("300502", "新易盛", "0"),     # 光模块
    ("688981", "中芯国际", "1"),   # 晶圆代工
    ("002415", "海康威视", "0"),   # 安防
    ("300750", "宁德时代", "0"),   # 电池（非科技，但对照）
    ("688012", "中微公司", "1"),   # 半导体设备
    ("002371", "北方华创", "0"),   # 半导体设备
]

START = "20200101"


def fetch(code, market):
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        f"?secid={market}.{code}&fields1=f1,f2,f3&fields2=f51,f53"
        f"&klt=103&fqt=1&beg={START}&end=20500101"
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "*/*",
            "Referer": "https://quote.eastmoney.com/",
            "Connection": "close",
        },
    )
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode("utf-8"))
            break
        except Exception as e:
            last = e
            time.sleep(1.5 * (attempt + 1))
    else:
        raise last
    data = d.get("data")
    if not data:
        return None, d.get("data")
    rows = []
    for k in data["klines"]:
        parts = k.split(",")
        rows.append({"date": parts[0], "close": float(parts[1])})
    return rows, data["name"]


def metrics(rows):
    """月度净值：以首月收盘建仓 100 万，逐月复利。"""
    n = len(rows)
    if n < 13:
        return None
    base = rows[0]["close"]
    nav = [100.0 * r["close"] / base for r in rows]
    months = n - 1
    total = nav[-1] - 100.0
    cagr = ((nav[-1] / 100.0) ** (12 / months) - 1) * 100

    peak, peak_i = nav[0], 0
    mdd = 0.0
    mdd_from = mdd_to = 0
    for i, v in enumerate(nav):
        if v > peak:
            peak, peak_i = v, i
        dd = (v - peak) / peak * 100
        if dd < mdd:
            mdd, mdd_from, mdd_to = dd, peak_i, i

    rets = [(nav[i] / nav[i - 1] - 1) * 100 for i in range(1, n)]
    mu = sum(rets) / len(rets)
    var = sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)
    vol = var ** 0.5 * (12 ** 0.5)

    wins = sum(1 for r in rets if r > 0)
    # 最大单月涨幅与最大回撤月份
    best_i = max(range(len(rets)), key=lambda i: rets[i]) + 1
    return {
        "months": months, "start": rows[0]["date"], "end": rows[-1]["date"],
        "total": total, "cagr": cagr, "mdd": mdd,
        "vol": vol, "winrate": wins / len(rets) * 100,
        "end_nav": nav[-1], "peak_nav": max(nav),
        "peak_date": rows[nav.index(max(nav))]["date"],
        "mdd_from": rows[mdd_from]["date"], "mdd_to": rows[mdd_to]["date"],
        "best_month": rows[best_i]["date"], "best_ret": rets[best_i - 1],
        "nav": nav,
    }


print(f"{'代码':8}{'名称':10}{'月数':>4}{'累计%':>9}{'年化%':>9}{'回撤%':>8}{'波动%':>8}{'胜率%':>7}{'峰值日':>12}{'谷底日':>12}")
print("-" * 100)
out = []
for code, name, market in CANDIDATES:
    try:
        rows, real = fetch(code, market)
    except Exception as e:
        print(f"{code:8}{name:10} 抓取失败: {type(e).__name__} {e}")
        continue
    if not rows:
        print(f"{code:8}{name:10} 无数据")
        continue
    m = metrics(rows)
    if not m:
        print(f"{code:8}{name:10} 区间不足 12 个月")
        continue
    out.append((code, name, rows, m))
    print(f"{code:8}{name:10}{m['months']:>4}{m['total']:>9.1f}{m['cagr']:>9.1f}"
          f"{m['mdd']:>8.1f}{m['vol']:>8.1f}{m['winrate']:>7.1f}{m['peak_date']:>12}{m['mdd_to']:>12}")

# 叙事张力打分：要有大涨、要有深回撤、起点低
print("\n=== 叙事张力排序 ===")
ranked = sorted(out, key=lambda t: -(abs(t[3]["best_ret"]) * 0.4 + abs(t[3]["mdd"]) * 0.6))
for code, name, rows, m in ranked:
    score = abs(m["best_ret"]) * 0.4 + abs(m["mdd"]) * 0.6
    print(f"  {name}({code}): 张力={score:.1f}  累计={m['total']:.0f}%  "
          f"最大月涨={m['best_ret']:.0f}%({m['best_month']})  回撤={m['mdd']:.0f}%")

with open("screen_result.json", "w", encoding="utf-8") as f:
    json.dump([{"code": c, "name": n, "rows": r, "metrics": {k: v for k, v in m.items() if k != "nav"}}
               for c, n, r, m in out], f, ensure_ascii=False, indent=1)
print("\n已写 screen_result.json")
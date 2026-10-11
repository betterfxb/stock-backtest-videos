"""
A 股全市场月K涨幅榜：读 klines_full.jsonl，算指标，按累计涨幅排序。
输出 high_gainers.json / high_gainers.csv / high_gainers.md
用法：python A_rank.py
"""
import os
import json
import csv
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "klines_hfq.jsonl")

# 已用过的标的（前 8 期）——列表里标出，避免重复选
USED = {
    "600519": "第001期 贵州茅台",
    "002594": "第002期 比亚迪",
    "688256": "第003期 寒武纪",
    "300502": "第004期 新易盛",
    "002371": "第005期 北方华创",
    "300308": "第006期 中际旭创",
    "518880": "第007期 黄金ETF",
    "000823": "第008期 超声电子",
}

PREFIX = re.compile(r"^(?:\*?ST|N|C|U|W|XD|XR|DR|XD|退)+")


def clean_name(name: str) -> str:
    n = name.strip()
    # 反复剥离交易所前缀（XD/XR/DR/N/C/ST/*ST…）
    for _ in range(3):
        m = PREFIX.match(n)
        if not m or m.end() == 0:
            break
        n = n[m.end():].strip()
    return n


def is_st(name: str) -> bool:
    return ("ST" in name) or ("退" in name)


def analyse(rows):
    n = len(rows)
    if n < 13:
        return None
    closes = [r[1] for r in rows]
    if any(c <= 0 for c in closes):
        return None
    base = closes[0]
    nav = [100.0 * c / base for c in closes]
    months = n - 1
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

    # 最大区间拉升：任一时刻相对此前最低点的涨幅
    lo, runup, runup_at = nav[0], 0.0, 0
    for i, v in enumerate(nav):
        lo = min(lo, v)
        r = (v / lo - 1) * 100
        if r > runup:
            runup, runup_at = r, i

    rets = [(nav[i] / nav[i - 1] - 1) * 100 for i in range(1, n)]
    mu = sum(rets) / len(rets)
    var = sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)
    vol = var ** 0.5 * (12 ** 0.5)
    wins = sum(1 for r in rets if r > 0)
    bi = max(range(len(rets)), key=lambda i: rets[i]) + 1
    pi = nav.index(max(nav))

    return dict(
        months=months, start=rows[0][0], end=rows[-1][0],
        total=round(total, 1), cagr=round(cagr, 1), mdd=round(mdd, 1),
        vol=round(vol, 1), winrate=round(wins / len(rets) * 100, 1),
        max_runup=round(runup, 1), runup_date=rows[runup_at][0],
        end_nav=round(nav[-1], 1), peak_nav=round(max(nav), 1),
        peak_date=rows[pi][0], min_nav=round(min(nav), 1),
        mdd_from=rows[mdd_f][0], mdd_to=rows[mdd_t][0],
        best_month=rows[bi][0], best_ret=round(rets[bi - 1], 1),
    )


def main():
    reg = {}
    for line in open(SRC, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if not r.get("rows"):
            continue
        prev = reg.get(r["symbol"])
        if not prev or len(r["rows"]) > len(prev["rows"]):
            reg[r["symbol"]] = r

    out = []
    for r in reg.values():
        rows = r["rows"]
        m = analyse(rows)
        if not m:
            continue
        raw_name = r["name"]
        out.append({
            "code": r["code"], "symbol": r["symbol"],
            "name": clean_name(raw_name), "raw": raw_name,
            "is_st": is_st(raw_name), "used": USED.get(r["code"], ""),
            **m,
        })

    # 全区间（>=60 个月）单独排一份，供"同期可比"参考
    full = [x for x in out if x["months"] >= 60]
    out.sort(key=lambda x: -x["total"])
    full.sort(key=lambda x: -x["total"])

    with open(os.path.join(HERE, "high_gainers.json"), "w", encoding="utf-8") as f:
        json.dump({"all": out, "full_window": full}, f, ensure_ascii=False, indent=1)

    with open(os.path.join(HERE, "high_gainers.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "code", "symbol", "name", "months", "start", "end",
                    "total_%", "cagr_%", "mdd_%", "vol_%", "winrate_%",
                    "max_runup_%", "best_month_%", "best_month", "peak_date", "is_st", "used"])
        for i, x in enumerate(out, 1):
            w.writerow([i, x["code"], x["symbol"], x["name"], x["months"], x["start"], x["end"],
                        x["total"], x["cagr"], x["mdd"], x["vol"], x["winrate"],
                        x["max_runup"], x.get("best_ret", ""), x.get("best_month", ""),
                        x["peak_date"], int(x["is_st"]), x["used"]])

    def md_table(rows, limit):
        L = ["", "| 排名 | 名称 | 代码 | 月数 | 累计涨幅 | 年化 | 最大回撤 | 最大月涨 | 峰值日 | 起始→终点 | 备注 |",
             "|---:|---|---|---:|---:|---:|---:|---:|---|---|---|"]
        for i, x in enumerate(rows[:limit], 1):
            note = x["used"] or ("ST" if x["is_st"] else "")
            L.append(
                f"| {i} | {x['name']} | {x['code']} | {x['months']} | "
                f"**{x['total']:.0f}%** | {x['cagr']:.0f}% | {x['mdd']:.0f}% | "
                f"{x.get('best_ret', 0):.0f}% | {x['peak_date']} | {x['start']}→{x['end']} | {note} |"
            )
        return L

    lines = [
        "# A 股月K涨幅榜（2020-01 起，后复权）",
        "",
        f"- 样本：{len(out)} 只（剔除上市不足 12 个月）；数据源：腾讯 fqkline 月K（后复权 hfq）",
        "- 口径：2020-01 首个交易日收盘买入，持有至最新月收盘；**后复权（含分红再投，近似总回报）**",
        "- 说明：腾讯 qfq 为加法复权（高分红股产生负价，已弃用）；本表统一用乘法复权 hfq",
        "- 涨幅 = 期末净值 / 100 − 1；月数为持有月度数据点数",
        "",
        "## 〇、可创作候选（排除已用期次与 ST，按累计涨幅）Top 40",
        "",
        "> 供选题：均为未使用、非 ST 的高涨幅标的。",
    ]
    lines += md_table([x for x in out if not x["used"] and not x["is_st"]], 40)
    lines += [
        "",
        "## 一、全市场累计涨幅 Top 60（含次新/ST/已用，按其上市以来区间）",
    ]
    lines += md_table(out, 60)
    lines += [
        "",
        "## 二、完整 6 年区间（≥60 个月）累计涨幅 Top 40",
    ]
    lines += md_table(full, 40)
    with open(os.path.join(HERE, "high_gainers.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"样本 {len(out)} 只，全区间 {len(full)} 只")
    print("Top 25（全市场）:")
    for i, x in enumerate(out[:25], 1):
        print(f"{i:>3} {x['name']:<9}{x['code']:<8}{x['months']:>3}月 {x['total']:>9.0f}%  "
              f"年化{x['cagr']:>6.0f}%  回撤{x['mdd']:>6.0f}%  {x['peak_date']}  {x['used']}")
    print("\nTop 15（完整6年）:")
    for i, x in enumerate(full[:15], 1):
        print(f"{i:>3} {x['name']:<9}{x['code']:<8}{x['total']:>9.0f}%  年化{x['cagr']:>5.0f}%  "
              f"回撤{x['mdd']:>6.0f}%  {x['used']}")


if __name__ == "__main__":
    main()
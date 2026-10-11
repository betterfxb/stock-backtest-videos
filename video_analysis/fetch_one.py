"""单标的抓取，带长间隔重试。用法: python fetch_one.py <code> <market 0=深 1=沪>"""
import json, sys, time, urllib.request


def fetch(code, market, beg="20200101"):
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        f"?secid={market}.{code}&fields1=f1,f2,f3&fields2=f51,f53"
        f"&klt=103&fqt=1&beg={beg}&end=20500101"
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Referer": "https://quote.eastmoney.com/",
            "Connection": "close",
        },
    )
    last = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode("utf-8"))
            break
        except Exception as e:
            last = e
            time.sleep(3 + attempt * 4)
    else:
        raise last
    data = d.get("data")
    if not data:
        return None, None
    rows = [{"date": p.split(",")[0], "close": float(p.split(",")[1])} for p in data["klines"]]
    return rows, data["name"]


if __name__ == "__main__":
    code, market = sys.argv[1], sys.argv[2]
    rows, name = fetch(code, market)
    if rows:
        print(f"{name}({code}) {len(rows)} 个月  {rows[0]['date']} ~ {rows[-1]['date']}")
        with open(f"kline_{code}.json", "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        print(f"已存 kline_{code}.json")
    else:
        print("无数据")
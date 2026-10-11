"""
A 股全市场月K抓取（可断点续跑）。
- 股票池：新浪 Market_Center.getHQNodeData（node=hs_a，含沪深主板/创业板/科创板/北交所）
- 行情：腾讯 fqkline 月K，前复权（qfq），区间 2020-01-01 ~ 2050-01-01
用法：python A_fetch.py [limit]
输出：universe.json（股票池）、klines_full.jsonl（每行一只，增量写）
"""
import os
import sys
import json
import time
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# 复权口径：腾讯 qfq 为「加法」复权（高分红股会产生负价，已证伪），hfq 为「乘法」复权，
# 与东财前复权同源，故统一用 hfq。
FQ = os.environ.get("FQ", "hfq")
OUTNAME = os.environ.get("OUT", f"klines_{FQ}.jsonl")


def get(url, headers, tries=4, timeout=30):
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            last = e
            time.sleep(0.8 * (a + 1))
    raise last


def fetch_universe():
    out, page = [], 1
    h = dict(UA)
    h["Referer"] = "https://finance.sina.com.cn/"
    while True:
        url = (
            "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
            f"Market_Center.getHQNodeData?page={page}&num=100&sort=symbol&asc=1"
            "&node=hs_a&symbol=&_s_r_a=page"
        )
        raw = get(url, h).strip()
        if not raw or raw == "null":
            break
        arr = json.loads(raw)
        if not arr:
            break
        for it in arr:
            out.append({"code": it["code"], "symbol": it["symbol"], "name": it["name"]})
        print(f"  page {page}: +{len(arr)} total {len(out)}", flush=True)
        if len(arr) < 100:
            break
        page += 1
        time.sleep(0.2)
    return out


HOSTS = [
    "https://ifzq.gtimg.cn/appstock/app/fqkline/get",
    "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/fqkline/get",
]
_host = {"i": 0}
_host_lock = threading.Lock()


def _next_host():
    with _host_lock:
        u = HOSTS[_host["i"] % len(HOSTS)]
        _host["i"] += 1
        return u


def fetch_kline(symbol):
    with _host_lock:
        i0 = _host["i"]
        _host["i"] += 1
    ordered = HOSTS[i0 % len(HOSTS):] + HOSTS[: i0 % len(HOSTS)]
    last = None
    for host in ordered:
        try:
            url = host + f"?param={symbol},month,2020-01-01,2050-01-01,1000,{FQ}"
            d = json.loads(get(url, UA, tries=2))
            node = (d.get("data") or {}).get(symbol)
            if not node:
                continue
            arr = None
            for key in (f"{FQ}month", "month"):
                if isinstance(node.get(key), list):
                    arr = node[key]
                    break
            if not arr:
                continue
            rows = []
            for k in arr:
                try:
                    rows.append([k[0], float(k[2])])
                except Exception:
                    pass
            if rows:
                return rows
        except Exception as e:
            last = e
    if last:
        raise last
    return None


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    up = os.path.join(HERE, "universe.json")
    if os.path.exists(up):
        with open(up, encoding="utf-8") as f:
            uni = json.load(f)
        print(f"[universe] cached {len(uni)}")
    else:
        uni = fetch_universe()
        with open(up, "w", encoding="utf-8") as f:
            json.dump(uni, f, ensure_ascii=False)
        print(f"[universe] fetched {len(uni)}")

    outp = os.path.join(HERE, OUTNAME)
    done = set()
    if os.path.exists(outp):
        with open(outp, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get("rows"):
                        done.add(r["symbol"])
                except Exception:
                    pass
    # 北交所（bj）腾讯 fqkline 不返回数据，暂跳过
    todo = [u for u in uni if u["symbol"] not in done and not u["symbol"].startswith("bj")]
    if limit:
        todo = todo[:limit]
    print(f"[klines] done={len(done)} todo={len(todo)}")

    lock = threading.Lock()
    cnt = {"n": 0, "ok": 0}
    fout = open(outp, "a", encoding="utf-8")

    def work(u):
        rec = {"code": u["code"], "symbol": u["symbol"], "name": u["name"]}
        try:
            rec["rows"] = fetch_kline(u["symbol"])
        except Exception as e:
            rec["error"] = type(e).__name__
        with lock:
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fout.flush()
            cnt["n"] += 1
            if rec.get("rows"):
                cnt["ok"] += 1
            if cnt["n"] % 200 == 0:
                print(f"  ...{cnt['n']}/{len(todo)} ok={cnt['ok']}", flush=True)

    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(work, todo))
    fout.close()
    print(f"[klines] finished +{cnt['n']} ok={cnt['ok']}")


if __name__ == "__main__":
    main()
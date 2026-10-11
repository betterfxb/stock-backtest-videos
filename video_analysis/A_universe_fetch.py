"""A股全市场涨幅榜取数：拉全 A 股列表 + 逐只月K（前复权，2020-01 起），写 JSONL 可续传。
用法：python A_universe_fetch.py [limit]
数据源：东方财富 push2his（月K，fqt=1 前复权）。
"""
import os
import sys
import json
import time
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "*/*",
    "Referer": "https://quote.eastmoney.com/",
    "Connection": "close",
}
FS = "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048"
BEG = "20200101"


def get(url, tries=4):
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(0.8 * (a + 1))
    raise last


def fetch_universe():
    out, pn = [], 1
    while True:
        url = (
            "https://push2.eastmoney.com/api/qt/clist/get"
            f"?pn={pn}&pz=100&po=1&np=1&fltt=2&invt=2&fid=f3&fs={FS}&fields=f12,f13,f14"
        )
        d = get(url)
        data = d.get("data")
        if not data or not data.get("diff"):
            break
        for it in data["diff"]:
            out.append({"code": str(it["f12"]), "market": int(it["f13"]), "name": it["f14"]})
        if len(out) >= data["total"]:
            break
        pn += 1
        time.sleep(0.3)
    return out


def fetch_klines(code, market):
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        f"?secid={market}.{code}&fields1=f1,f2&fields2=f51,f53"
        f"&klt=103&fqt=1&beg={BEG}&end=20500101"
    )
    d = get(url)
    data = d.get("data")
    if not data or not data.get("klines"):
        return None
    rows = []
    for k in data["klines"]:
        p = k.split(",")
        rows.append([p[0], float(p[1])])
    return rows


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    uni_path = os.path.join(HERE, "universe.json")
    if os.path.exists(uni_path):
        with open(uni_path, encoding="utf-8") as f:
            uni = json.load(f)
        print(f"[universe] cached {len(uni)}")
    else:
        uni = fetch_universe()
        with open(uni_path, "w", encoding="utf-8") as f:
            json.dump(uni, f, ensure_ascii=False)
        print(f"[universe] fetched {len(uni)}")

    out_path = os.path.join(HERE, "klines_full.jsonl")
    done = set()
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(json.loads(line)["code"])
                except Exception:
                    pass
    todo = [u for u in uni if u["code"] not in done]
    if limit:
        todo = todo[:limit]
    print(f"[klines] done={len(done)} todo={len(todo)}")

    lock = threading.Lock()
    cnt = {"n": 0, "ok": 0}
    fout = open(out_path, "a", encoding="utf-8")

    def work(u):
        rec = {"code": u["code"], "market": u["market"], "name": u["name"]}
        try:
            rows = fetch_klines(u["code"], u["market"])
            rec["rows"] = rows
        except Exception as e:
            rec["error"] = f"{type(e).__name__}"
        with lock:
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fout.flush()
            cnt["n"] += 1
            if rec.get("rows"):
                cnt["ok"] += 1
            if cnt["n"] % 200 == 0:
                print(f"  ...{cnt['n']}/{len(todo)} ok={cnt['ok']}", flush=True)

    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(work, todo))

    fout.close()
    print(f"[klines] finished +{cnt['n']} ok={cnt['ok']}")


if __name__ == "__main__":
    main()
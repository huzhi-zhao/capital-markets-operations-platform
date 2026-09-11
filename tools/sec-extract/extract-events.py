import glob, json, gzip, os, sys, time, urllib.request, urllib.error

UA = os.environ.get("CMOP_SEC_UA", "CMOP research (huzhi.zhao.smecta@gmail.com)")
BASE = os.environ.get("CMOP_SEC_RAW",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "..", "data", "reference", "sec", "raw"))
MIN_INTERVAL = 0.13          # ~7.7 req/s, under SEC's 10/s ceiling
_last = [0.0]

def get(url, binary=False):
    wait = MIN_INTERVAL - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Encoding": "gzip, deflate", "Host": url.split("/")[2]})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                data = gzip.decompress(data)
            return data if binary else data.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return None
    except Exception as e:
        sys.stderr.write("ERR %s %s\n" % (url, e))
        return None
    finally:
        _last[0] = time.time()

for d in ("", "/frames", "/idx"):
    os.makedirs(BASE + d, exist_ok=True)

QUARTERS = [(y, q) for y in range(2016, 2026) for q in (1, 2, 3, 4)]
log = lambda *a: (print(*a, flush=True))

# 1. ticker / exchange universe
t = get("https://www.sec.gov/files/company_tickers_exchange.json")
with gzip.open(BASE + "/tickers.json.gz", "wt") as f:
    f.write(t or "")
log("tickers bytes", len(t or ""))

# 2. frames
SPECS = [
    ("splits", "StockholdersEquityNoteStockSplitConversionRatio1", "pure", True),
    ("dividends", "CommonStockDividendsPerShareDeclared", "USD-per-shares", False),
]
summary = {"splits": {}, "dividends": {}}
for name, concept, unit, instant in SPECS:
    for y, q in QUARTERS:
        period = "CY%dQ%d%s" % (y, q, "I" if instant else "")
        url = "https://data.sec.gov/api/xbrl/frames/us-gaap/%s/%s/%s.json" % (concept, unit, period)
        body = get(url)
        n = 0
        if body:
            try:
                n = len(json.loads(body).get("data", []))
                with gzip.open("%s/frames/%s-%s.json.gz" % (BASE, name, period), "wt") as f:
                    f.write(body)
            except Exception as e:
                sys.stderr.write("parse %s %s\n" % (period, e))
        summary[name][period] = n
        log(name, period, n)

# 3. delistings from the quarterly form index
delist = {}
for y, q in QUARTERS:
    url = "https://www.sec.gov/Archives/edgar/full-index/%d/QTR%d/form.idx" % (y, q)
    body = get(url)
    rows = []
    if body:
        for line in body.splitlines():
            ft = line[:12].strip()
            if ft in ("25", "25-NSE"):
                rows.append(line)
    key = "%dQ%d" % (y, q)
    delist[key] = len(rows)
    if rows:
        with gzip.open("%s/idx/form25-%s.txt.gz" % (BASE, key), "wt") as f:
            f.write("\n".join(rows))
    log("delist", key, len(rows))

universe = set()
for name, _, _, _ in SPECS:
    for f in glob.glob("%s/frames/%s-*.json.gz" % (BASE, name)):
        for x in json.loads(gzip.open(f, "rt").read()).get("data", []):
            universe.add(x["cik"])
for f in glob.glob(BASE + "/idx/form25-*.txt.gz"):
    for line in gzip.open(f, "rt").read().splitlines():
        for tok in [q.strip() for q in line.split("  ") if q.strip()]:
            if tok.isdigit() and len(tok) <= 10:
                universe.add(int(tok))
                break
for r in json.loads(gzip.open(BASE + "/tickers.json.gz", "rt").read())["data"]:
    universe.add(r[0])
open(BASE + "/universe-ciks.txt", "w").write("\n".join(str(c) for c in sorted(universe)))
log("universe CIKs", len(universe))

json.dump({"frames": summary, "delistings": delist}, open(BASE + "/summary.json", "w"), indent=1)
log("DONE")

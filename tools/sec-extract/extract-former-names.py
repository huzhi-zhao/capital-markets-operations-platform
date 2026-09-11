import json, gzip, os, sys, time, urllib.request, urllib.error
UA = os.environ.get("CMOP_SEC_UA", "CMOP research (huzhi.zhao.smecta@gmail.com)")
BASE = os.environ.get("CMOP_SEC_RAW",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "..", "data", "reference", "sec", "raw"))
MIN = 0.13
_last=[0.0]
def get(url):
    w = MIN-(time.time()-_last[0])
    if w>0: time.sleep(w)
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept-Encoding":"gzip","Host":"data.sec.gov"})
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            d=r.read()
            if r.headers.get("Content-Encoding")=="gzip": d=gzip.decompress(d)
            return d
    except Exception:
        return None
    finally:
        _last[0]=time.time()

os.makedirs(BASE, exist_ok=True)
ciks=[int(x) for x in open(BASE+"/universe-ciks.txt").read().split()]
out={}; miss=0
t0=time.time()
for i,c in enumerate(ciks,1):
    b=get("https://data.sec.gov/submissions/CIK%010d.json"%c)
    if b is None:
        miss+=1
    else:
        try:
            j=json.loads(b)
            fn=j.get("formerNames") or []
            if fn:
                out[c]={"name":j.get("name"),"tickers":j.get("tickers"),
                        "exchanges":j.get("exchanges"),"formerNames":fn}
        except Exception:
            miss+=1
    if i%500==0:
        el=time.time()-t0
        print("%d/%d  withFormerNames=%d miss=%d  %.0fs elapsed  eta %.0fs"
              % (i,len(ciks),len(out),miss,el,el/i*(len(ciks)-i)), flush=True)
with gzip.open(BASE+"/former-names.json.gz","wt") as f:
    json.dump(out,f)
print("DONE ciks=%d withFormerNames=%d miss=%d"%(len(ciks),len(out),miss), flush=True)

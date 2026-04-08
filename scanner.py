import sys, os, json, time, argparse
from datetime import datetime
from pathlib import Path
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sources.prozorro import get_tenders, to_telegram_message
from notify.telegram import send_tenders, send_digest as tg_digest
from notify.email_sender import send_digest as email_digest

DATA_DIR = Path(__file__).parent / "data"
SEEN_FILE = DATA_DIR / "seen_ids.json"
RESULTS_FILE = Path(__file__).parent / "results.json"
DASHBOARD_FILE = Path(__file__).parent / "uze_tender_dashboard.html"

def load_seen():
    if SEEN_FILE.exists():
        try:
            with open(SEEN_FILE,"r",encoding="utf-8") as f: return set(json.load(f))
        except: pass
    return set()

def save_seen(ids):
    DATA_DIR.mkdir(exist_ok=True)
    with open(SEEN_FILE,"w",encoding="utf-8") as f: json.dump(list(ids),f,ensure_ascii=False)

def load_results():
    if RESULTS_FILE.exists():
        try:
            with open(RESULTS_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

def save_results(t):
    with open(RESULTS_FILE,"w",encoding="utf-8") as f: json.dump(t,f,ensure_ascii=False,indent=2,default=str)
    print(f"[OK] Results saved: {len(t)} tenders")

def update_dashboard(tenders):
    import re
    if not DASHBOARD_FILE.exists():
        print("[WARN] Dashboard not found"); return
    with open(DASHBOARD_FILE,"r",encoding="utf-8") as f: html = f.read()
    pm = {"prozorro":"prozorro","smarttender":"smart","ungm":"ungm","nefco":"nefco","ted":"ted","dream":"dream","dtek":"dtek"}
    tm = {"BESS":"bess","Inverter":"inverter","Solar":"solar","Other":"bess"}
    dt = []
    for t in tenders:
        dt.append({"id":t.get("id",""),"title":t.get("title","").replace("'","\\'").replace('"','\\"'),
            "platform":pm.get(t.get("platform",t.get("source","")),"prozorro"),
            "cpv":t.get("cpv",t.get("cpvs",[""])[0] if t.get("cpvs") else ""),
            "amount":t.get("amount",0),"deadline":t.get("deadline",""),
            "status":t.get("status","active"),"score":t.get("score",50),
            "type":tm.get(t.get("type",""),"bess")})
    js = json.dumps(dt, ensure_ascii=False, indent=2)
    html = re.sub(r"const TENDERS = \\[.*?\\];", f"const TENDERS = {js};", html, flags=re.DOTALL)
    with open(DASHBOARD_FILE,"w",encoding="utf-8") as f: f.write(html)
    print(f"[OK] Dashboard updated: {len(dt)} tenders")

def merge(existing, new):
    by_id = {}
    for t in existing:
        k = t.get("id") or t.get("_raw_id","")
        if k: t["is_new"]=False; by_id[k]=t
    for t in new:
        k = t.get("id") or t.get("_raw_id","")
        if k: by_id[k]=t
    m = list(by_id.values())
    m.sort(key=lambda x: x.get("score",0), reverse=True)
    return m

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hours",type=int,default=12)
    p.add_argument("--no-telegram",action="store_true")
    p.add_argument("--no-email",action="store_true")
    p.add_argument("--digest-only",action="store_true")
    p.add_argument("--no-dashboard",action="store_true")
    a = p.parse_args()
    print("="*50)
    print(f"  UZE TENDER SCANNER  {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"  Period: last {a.hours} hours")
    print("="*50)
    seen = load_seen()
    print(f"[INFO] Memory: {len(seen)} prev tenders")
    new = get_tenders(hours_back=a.hours, seen_ids=seen)
    print(f"\n{'-'*40}")
    print(f"  TOTAL FOUND: {len(new)}")
    if new:
        u=[t for t in new if t.get("status")=="urgent"]
        b=[t for t in new if t.get("type")=="BESS"]
        i=[t for t in new if t.get("type")=="Inverter"]
        s=[t for t in new if t.get("type")=="Solar"]
        print(f"  Urgent: {len(u)} | BESS: {len(b)} | Inv: {len(i)} | Solar: {len(s)}")
        print(f"  Amount: UAH {sum(t.get('amount',0) for t in new):,.0f}")
        print(f"\n  Top tenders:")
        for t in sorted(new,key=lambda x:x.get("score",0),reverse=True)[:5]:
            print(f"  [{t.get('score',0)}] {t['title'][:70]}")
            print(f"       UAH {t.get('amount',0):,.0f} | {t.get('deadline','--')} | {t.get('type','')}")
    print(f"{'-'*40}\n")
    if sys.stdin.isatty() and new:
        print("[1] Telegram + dashboard  [2] Dashboard only  [3] JSON only  [0] Cancel")
        c = input("Choice: ").strip()
        if c=="0": print("Cancelled."); return
        if c=="2": a.no_telegram=True
        if c=="3": a.no_telegram=True; a.no_dashboard=True
    elif sys.stdin.isatty():
        print("[OK] No new tenders.")
    if new and not a.no_telegram:
        if a.digest_only: tg_digest(new)
        else: send_tenders(new, formatter=to_telegram_message)
    if new and not a.no_email: email_digest(new)
    ex = load_results()
    all_t = merge(ex, new)
    save_results(all_t)
    for t in new:
        rid = t.get("_raw_id",t.get("id",""))
        if rid: seen.add(rid)
    save_seen(seen)
    if not a.no_dashboard: update_dashboard(all_t)
    print(f"\n[DONE] {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__": main()

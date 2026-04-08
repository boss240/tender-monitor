"""
UZE Tender Monitor - File Generator
Run: python generate.py
Creates: scanner.py, sources/prozorro.py, test_api.py
"""
import os, json

os.makedirs("sources", exist_ok=True)

# === SOURCES/PROZORRO.PY ===
CPV_W = ["31154000-0","31155000-7","31440000-2","31150000-2","09331200-0","09332000-5"]
CPV_B = ["31430000-9","31431000-6","31432000-3","31434000-7","42662000-4","42662100-5","44512000-2","35613000-4"]
KW_IN = json.dumps(["bess","lifepo4","battery storage","energy storage","ess","solar pv","ups","deye","poweroad","renewable energy","\u0430\u043a\u0443\u043c\u0443\u043b\u044f\u0442\u043e\u0440","\u043d\u0430\u043a\u043e\u043f\u0438\u0447\u0443\u0432\u0430\u0447 \u0435\u043d\u0435\u0440\u0433\u0456\u0457","\u0456\u043d\u0432\u0435\u0440\u0442\u043e\u0440","\u0431\u0435\u0437\u043f\u0435\u0440\u0435\u0431\u0456\u0439\u043d\u0435 \u0436\u0438\u0432\u043b\u0435\u043d\u043d\u044f","\u0433\u0456\u0431\u0440\u0438\u0434\u043d\u0438\u0439 \u0456\u043d\u0432\u0435\u0440\u0442\u043e\u0440","\u0437\u0431\u0435\u0440\u0456\u0433\u0430\u043d\u043d\u044f \u0435\u043d\u0435\u0440\u0433\u0456\u0457","\u0432\u0456\u0434\u043d\u043e\u0432\u043b\u044e\u0432\u0430\u043d\u0430 \u0435\u043d\u0435\u0440\u0433\u0456\u044f","\u0441\u043e\u043d\u044f\u0447\u043d\u0430 \u043f\u0430\u043d\u0435\u043b\u044c","\u0444\u043e\u0442\u043e\u0432\u043e\u043b\u044c\u0442\u0430\u0457\u0447\u043d\u0438\u0439","\u0434\u0431\u0436","\u043d\u0430\u043a\u043e\u043f\u0438\u0447\u0443\u0432\u0430\u0447"], ensure_ascii=False)
KW_EX = json.dumps(["dji","matrice","drone","mavic","phantom","fpv","mma-","mig-","tig-","\u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0456\u043b","\u0442\u0440\u0430\u043a\u0442\u043e\u0440","\u043d\u043e\u0443\u0442\u0431\u0443\u043a","\u0441\u043c\u0430\u0440\u0442\u0444\u043e\u043d","\u0442\u0435\u043b\u0435\u0444\u043e\u043d","\u043c\u043e\u0442\u043e\u0446\u0438\u043a\u043b","\u0441\u043a\u0443\u0442\u0435\u0440","\u043b\u0456\u0445\u0442\u0430\u0440","\u0434\u0440\u043e\u043d","\u043a\u0432\u0430\u0434\u0440\u043e\u043a\u043e\u043f\u0442\u0435\u0440","\u0431\u043f\u043b\u0430","\u0437\u0432\u0430\u0440\u044e\u0432","\u043f\u043b\u0430\u0437\u043c\u043e\u0440","\u0434\u0435\u0444\u0456\u0431\u0440\u0438\u043b","\u0440\u0435\u043d\u0442\u0433\u0435\u043d","\u0456\u0433\u0440\u0430\u0448\u043a","\u0434\u0438\u0442\u044f\u0447","\u0432\u0435\u043b\u043e\u0441\u0438\u043f\u0435\u0434","\u0448\u0443\u0440\u0443\u043f\u043e\u0432\u0435\u0440\u0442","\u043f\u0438\u043b\u043e\u0441\u043e\u0441","\u0430\u0432\u0442\u043e\u0431\u0443\u0441","\u043d\u0430\u0432\u0430\u043d\u0442\u0430\u0436\u0443\u0432\u0430\u0447","\u0441\u0430\u043c\u043e\u043a\u0430\u0442","\u043a\u043e\u043d\u0434\u0438\u0446\u0456\u043e\u043d\u0435\u0440","\u043f\u043b\u0430\u043d\u0448\u0435\u0442","\u0435\u043b\u0435\u043a\u0442\u0440\u043e\u0456\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442","\u0435\u043b\u0435\u043a\u0442\u0440\u043e\u043a\u0430\u0440","\u0442\u043e\u043c\u043e\u0433\u0440\u0430\u0444","\u043a\u0430\u0440\u0434\u0456\u043e"], ensure_ascii=False)

BESS_KW = json.dumps(["bess","\u043d\u0430\u043a\u043e\u043f\u0438\u0447\u0443\u0432\u0430\u0447","\u0430\u043a\u0443\u043c\u0443\u043b\u044f\u0442\u043e\u0440","lifepo4","battery"], ensure_ascii=False)
INV_KW = json.dumps(["\u0456\u043d\u0432\u0435\u0440\u0442\u043e\u0440","inverter"], ensure_ascii=False)
SOL_KW = json.dumps(["solar","\u0441\u043e\u043d\u044f\u0447\u043d"], ensure_ascii=False)

prozorro_code = f'''import requests, time, json
from datetime import datetime, timedelta

BASE = "https://public-api.prozorro.gov.ua/api/2.5"
CPV_WHITELIST = set({json.dumps(CPV_W)})
CPV_BLACKLIST = set({json.dumps(CPV_B)})
KEYWORDS_INCLUDE = {KW_IN}
KEYWORDS_EXCLUDE = {KW_EX}
_BESS_KW = {BESS_KW}
_INV_KW = {INV_KW}
_SOL_KW = {SOL_KW}

def _fetch_all_ids(hours_back):
    since = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%S")
    offset = since + "Z"
    all_ids = []
    for page in range(50):
        url = f"{{BASE}}/tenders?offset={{offset}}&limit=100&opt_fields=id"
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"[Prozorro] Page {{page}} error: {{e}}")
            break
        items = data.get("data", [])
        if not items:
            break
        all_ids.extend([t["id"] for t in items])
        np = data.get("next_page", {{}}).get("offset", "")
        if not np or np == offset:
            break
        offset = np
        print(f"[Prozorro] Page {{page+1}}: +{{len(items)}} (total: {{len(all_ids)}})")
        time.sleep(0.3)
    return all_ids

def get_tenders(hours_back=12, seen_ids=None):
    if seen_ids is None:
        seen_ids = set()
    raw_ids = _fetch_all_ids(hours_back)
    if not raw_ids:
        print("[Prozorro] No IDs fetched.")
        return []
    print(f"[Prozorro] Total IDs: {{len(raw_ids)}}, checking...")
    results = []
    sb = se = sn = ck = 0
    for idx, tid in enumerate(raw_ids):
        if tid in seen_ids:
            continue
        try:
            r = requests.get(f"{{BASE}}/tenders/{{tid}}", timeout=20)
            r.raise_for_status()
            d = r.json().get("data", {{}})
        except:
            time.sleep(0.5)
            continue
        ck += 1
        items = d.get("items", [])
        cpvs = [i.get("classification", {{}}).get("id", "") for i in items]
        title = d.get("title", "") or ""
        tl = title.lower()
        if any(c in CPV_BLACKLIST for c in cpvs):
            sb += 1; time.sleep(0.3); continue
        mc = [c for c in cpvs if c in CPV_WHITELIST]
        mk = [k for k in KEYWORDS_INCLUDE if k in tl]
        bk = [k for k in KEYWORDS_EXCLUDE if k in tl]
        if bk:
            se += 1; time.sleep(0.3); continue
        if not mc and not mk:
            sn += 1; time.sleep(0.3); continue
        if not mc and mk:
            if not any(c.startswith(("31","09")) for c in cpvs) and cpvs:
                sn += 1; time.sleep(0.3); continue
        period = d.get("tenderPeriod", {{}})
        val = d.get("value", {{}}) or {{}}
        dl_raw = period.get("endDate", "")
        dl = dl_raw[:10] if dl_raw else ""
        amt = val.get("amount", 0) or 0
        tcpvs = list(set(mc)) or cpvs[:3]
        tp = "Other"
        if any(c in {{"31440000-2","31154000-0"}} for c in tcpvs) or any(k in tl for k in _BESS_KW):
            tp = "BESS"
        elif any(c in {{"31155000-7"}} for c in tcpvs) or any(k in tl for k in _INV_KW):
            tp = "Inverter"
        elif any(c in {{"09331200-0","09332000-5"}} for c in tcpvs) or any(k in tl for k in _SOL_KW):
            tp = "Solar"
        st = "new"
        if dl:
            try:
                if (datetime.strptime(dl, "%Y-%m-%d") - datetime.now()).days <= 3:
                    st = "urgent"
            except: pass
        if d.get("status","") in ("active.tendering","active.enquiries"):
            st = "active"
        sc = 50 + min(len([c for c in tcpvs if c in CPV_WHITELIST])*15, 30)
        sc += min(len(mk)*5, 15)
        if amt > 5000000: sc += 5
        sc = max(0, min(sc, 99))
        results.append({{
            "id": d.get("tenderID", tid), "_raw_id": tid,
            "title": title, "org": d.get("procuringEntity",{{}}).get("name","---"),
            "source": "prozorro", "platform": "prozorro", "type": tp,
            "amount": amt, "currency": val.get("currency","UAH"),
            "deadline": dl, "cpvs": tcpvs,
            "cpv": tcpvs[0] if tcpvs else "",
            "status": st, "url": f"https://prozorro.gov.ua/tender/{{tid}}",
            "is_new": True, "score": sc,
            "fetched_at": datetime.utcnow().isoformat(),
        }})
        seen_ids.add(tid)
        time.sleep(0.3)
        if (idx+1) % 50 == 0:
            print(f"[Prozorro] Checked {{idx+1}}/{{len(raw_ids)}}, found: {{len(results)}}")
    print(f"[Prozorro] Done. Checked: {{ck}}, Found: {{len(results)}}")
    print(f"[Prozorro] Skipped: {{sb}} (CPV black) | {{se}} (kw excl) | {{sn}} (no match)")
    return results

def to_telegram_message(t):
    days = 0
    if t.get("deadline"):
        try: days = (datetime.strptime(t["deadline"],"%Y-%m-%d") - datetime.now()).days
        except: pass
    ic = "\\U0001f534" if days<=3 else "\\U0001f7e1" if days<=7 else "\\U0001f7e2"
    a = f"UAH {{t['amount']:,.0f}}" if t.get("amount") else "---"
    cpv = ", ".join(t.get("cpvs",[])[:2])
    return (f"{{ic}} *New UZE tender*\\n\\n"
        f"\\U0001f4cb {{t['title']}}\\n"
        f"\\U0001f3e2 {{t.get('org','---')}}\\n"
        f"\\U0001f4b0 {{a}}\\n"
        f"\\U0001f4e6 CPV: `{{cpv}}`\\n"
        f"\\u23f0 Deadline: {{t.get('deadline','---')}} ({{days}} d.)\\n"
        f"\\U0001f3af Score: {{t.get('score',0)}}/100\\n"
        f"\\U0001f517 {{t.get('url','')}}")
'''

with open("sources/prozorro.py", "w", encoding="utf-8") as f:
    f.write(prozorro_code)
print("[OK] sources/prozorro.py created")

# === SCANNER.PY ===
scanner_code = '''import sys, os, json, time, argparse
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
        dt.append({"id":t.get("id",""),"title":t.get("title","").replace("'","\\\\'").replace('"','\\\\"'),
            "platform":pm.get(t.get("platform",t.get("source","")),"prozorro"),
            "cpv":t.get("cpv",t.get("cpvs",[""])[0] if t.get("cpvs") else ""),
            "amount":t.get("amount",0),"deadline":t.get("deadline",""),
            "status":t.get("status","active"),"score":t.get("score",50),
            "type":tm.get(t.get("type",""),"bess")})
    js = json.dumps(dt, ensure_ascii=False, indent=2)
    html = re.sub(r"const TENDERS = \\\\[.*?\\\\];", f"const TENDERS = {js};", html, flags=re.DOTALL)
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
    print(f"\\n{'-'*40}")
    print(f"  TOTAL FOUND: {len(new)}")
    if new:
        u=[t for t in new if t.get("status")=="urgent"]
        b=[t for t in new if t.get("type")=="BESS"]
        i=[t for t in new if t.get("type")=="Inverter"]
        s=[t for t in new if t.get("type")=="Solar"]
        print(f"  Urgent: {len(u)} | BESS: {len(b)} | Inv: {len(i)} | Solar: {len(s)}")
        print(f"  Amount: UAH {sum(t.get('amount',0) for t in new):,.0f}")
        print(f"\\n  Top tenders:")
        for t in sorted(new,key=lambda x:x.get("score",0),reverse=True)[:5]:
            print(f"  [{t.get('score',0)}] {t['title'][:70]}")
            print(f"       UAH {t.get('amount',0):,.0f} | {t.get('deadline','--')} | {t.get('type','')}")
    print(f"{'-'*40}\\n")
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
    print(f"\\n[DONE] {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__": main()
'''

with open("scanner.py", "w", encoding="utf-8") as f:
    f.write(scanner_code)
print("[OK] scanner.py created")

# === TEST_API.PY ===
test_code = '''import sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
from datetime import datetime
print("="*50)
print("[TEST] Prozorro API check")
print("="*50)
print("\\n[1] API connection...")
try:
    r = requests.get("https://public-api.prozorro.gov.ua/api/2.5/tenders?limit=3", timeout=15)
    r.raise_for_status()
    print(f"   [OK] API works! Got {len(r.json().get('data',[]))} tenders")
except Exception as e:
    print(f"   [FAIL] {e}"); sys.exit(1)
print("\\n[2] Scanning UZE tenders (48h with pagination)...")
from sources.prozorro import get_tenders
t = get_tenders(hours_back=48, seen_ids=set())
print(f"\\n   Result: {len(t)} UZE tenders found")
if t:
    print("\\n   Top results:")
    for x in sorted(t, key=lambda x: x.get("score",0), reverse=True)[:10]:
        print(f"   [{x.get('score',0)}] {x['title'][:70]}...")
        print(f"       CPV: {','.join(x.get('cpvs',[]))} | UAH {x.get('amount',0):,.0f} | {x.get('deadline','---')}")
        print()
else:
    print("   (No UZE tenders in 48h. Try: python scanner.py --hours 168)")
print(f"\\n{'='*50}")
print(f"[DONE] {datetime.now().strftime('%H:%M:%S')}")
'''

with open("test_api.py", "w", encoding="utf-8") as f:
    f.write(test_code)
print("[OK] test_api.py created")

print("\n=== ALL FILES GENERATED ===")
print("Now run:  python test_api.py")

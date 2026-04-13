import sys, json, os, time, re
sys.path.insert(0, ".")
from datetime import datetime
from sources.prozorro import get_tenders as prozorro_scan, to_telegram_message
from sources.power import detect_power
from sources.nefco import get_tenders as nefco_scan
from sources.ted import get_tenders as ted_scan
from sources.smarttender import get_tenders as smart_scan
from sources.ungm import get_tenders as ungm_scan
from sources.dream import get_tenders as dream_scan
import requests

BOT = os.environ.get("TG_BOT_TOKEN", "8605180032:AAEM88qW1csZ8QerdShf9vdMY7oyUpw_7Yw")
CHAT = os.environ.get("TG_CHAT_ID", "-5175531486")
API = "https://api.telegram.org/bot" + BOT
DASH = "uze_tender_dashboard.html"

def tg(text):
    try:
        requests.post(API + "/sendMessage", json={"chat_id":CHAT,"text":text,
            "parse_mode":"HTML","disable_web_page_preview":False}, timeout=15)
        time.sleep(0.5)
    except: pass

def tg_msg(t):
    days = t.get("days_left", 0)
    if not days and t.get("deadline"):
        try: days = (datetime.strptime(t["deadline"],"%Y-%m-%d") - datetime.now()).days
        except: days = 0
    ic = "\xf0\x9f\x94\x94" if days<=3 else "\xf0\x9f\x9f\xa1" if days<=7 else "\xf0\x9f\x9f\xa2"
    a = f"UAH {t['amount']:,.0f}" if t.get("amount") else "---"
    cpv = ", ".join(t.get("cpvs",[])[:2]) or t.get("cpv","")
    pw = t.get("power_kw",0) or detect_power(t.get("title",""))
    pw_s = f"\n\u26a1 <b>{pw} kW</b>" if pw else ""
    src = (t.get("platform","") or t.get("source","")).upper()
    url = t.get("url", "")
    org = t.get("org","---")[:60]
    dl = t.get("deadline","---")
    return (f"{ic} <b>UZE [{src}]</b>\n\n"
        f"\ud83d\udccb {t['title'][:150]}\n"
        f"\ud83c\udfe2 {org}\n"
        f"\ud83d\udcb0 <b>{a}</b>{pw_s}\n"
        f"\ud83d\udce6 CPV: <code>{cpv}</code>\n"
        f"\u23f0 Deadline: <b>{dl}</b> ({days} d.)\n"
        f"\ud83c\udfaf Score: {t.get('score',0)}/100\n\n"
        f"\ud83d\udd17 <a href=\"{url}\">Open tender</a>")

def tg_digest(tenders):
    urg = [t for t in tenders if t.get("status")=="urgent"]
    bess = len([t for t in tenders if t.get("type")=="BESS"])
    inv = len([t for t in tenders if t.get("type")=="Inverter"])
    sol = len([t for t in tenders if t.get("type")=="Solar"])
    total = sum(t.get("amount",0) for t in tenders)
    a = f"UAH {total/1e6:.1f}M" if total>1e6 else f"UAH {total:,.0f}"
    msg = (f"<b>UZE Digest</b>\n"
        f"{datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Total: <b>{len(tenders)}</b>\n"
        f"Urgent: <b>{len(urg)}</b>\n"
        f"BESS: {bess} | Inv: {inv} | Sol: {sol}\n"
        f"Amount: {a}\n\n")
    if urg:
        msg += "<b>Critical:</b>\n"
        for t in urg[:5]:
            pw = t.get("power_kw",0)
            pw_s = f" | {pw}kW" if pw else ""
            a2 = f"UAH {t['amount']:,.0f}" if t.get("amount") else ""
            msg += f"{t['title'][:40]}...\n  {a2}{pw_s} | {t.get('deadline','')} | <a href=\"{t.get('url','')}\">Link</a>\n"
        msg += "\n"
    top5 = sorted(tenders, key=lambda x:x.get("score",0), reverse=True)[:5]
    msg += "<b>Top 5:</b>\n"
    for i,t in enumerate(top5,1):
        a2 = f"UAH {t['amount']:,.0f}" if t.get("amount") else "---"
        pw = t.get("power_kw",0)
        pw_s = f" | {pw}kW" if pw else ""
        org = t.get("org","")[:25]
        msg += f"{i}. <b>{t['title'][:40]}...</b>\n   {a2}{pw_s} | {org}\n   <a href=\"{t.get('url','')}\">Open</a>\n\n"
    msg += f"<a href=\"https://boss240.github.io/tender-monitor/uze_tender_dashboard.html\">Dashboard</a>"
    tg(msg)

def run():
    print(f"=== UZE {datetime.now().strftime('%d.%m.%Y %H:%M')} ===")
    seen = set()
    try:
        with open("data/seen_ids.json","r") as f: seen = set(json.load(f))
    except: pass
    print(f"Memory: {len(seen)}")
    new_t = prozorro_scan(24, seen)
    for name,fn in [('NEFCO',nefco_scan),('TED',ted_scan),('Smart',smart_scan),('UNGM',ungm_scan),('DREAM',dream_scan)]:
        try: new_t.extend(fn(seen))
        except Exception as e: print(f'[{name}] Failed: {e}')
    print(f'New: {len(new_t)}')
    existing = []
    try:
        with open("results.json","r",encoding="utf-8") as f: existing = json.load(f)
    except: pass
    by_id = {}
    for x in existing:
        k=x.get("id","")
        if k: by_id[k]=x
    for x in new_t:
        k=x.get("id","")
        if k: by_id[k]=x
    all_t = sorted(by_id.values(), key=lambda x:x.get("score",0), reverse=True)
    with open("results.json","w",encoding="utf-8") as f:
        json.dump(all_t, f, ensure_ascii=False, indent=2, default=str)
    for x in new_t:
        rid=x.get("_raw_id",x.get("id",""))
        if rid: seen.add(rid)
    os.makedirs("data",exist_ok=True)
    with open("data/seen_ids.json","w") as f: json.dump(list(seen),f)
    print(f"Total: {len(all_t)}")
    if new_t:
        tg("<b>UZE Monitor</b>\nFound <b>" + str(len(new_t)) + "</b> new tenders")
        for x in sorted(new_t, key=lambda x:x.get("score",0), reverse=True)[:20]:
            tg(tg_msg(x))
            print(f"  TG: [{x.get('score',0)}] {x['title'][:50]}")
    active = [t for t in all_t if t.get("deadline","")>=datetime.now().strftime("%Y-%m-%d") or not t.get("deadline")]
    if active: tg_digest(active)
    print(f"=== DONE {datetime.now().strftime('%H:%M:%S')} ===")

if __name__=="__main__": run()

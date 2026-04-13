import sys, json, os, time, threading
sys.path.insert(0, ".")
import requests
from datetime import datetime

BOT = os.environ.get("TG_BOT_TOKEN", "8605180032:AAEM88qW1csZ8QerdShf9vdMY7oyUpw_7Yw")
CHAT = os.environ.get("TG_CHAT_ID", "-5175531486")
API = "https://api.telegram.org/bot" + BOT

def send(cid, text):
    try: requests.post(API + "/sendMessage", json={"chat_id":cid,"text":text,"parse_mode":"HTML","disable_web_page_preview":True}, timeout=15)
    except: pass

def load_results():
    try:
        with open("results.json","r",encoding="utf-8") as f: return json.load(f)
    except: return []

def cmd_status(cid):
    t = load_results()
    urg = len([x for x in t if x.get("status")=="urgent"])
    bess = len([x for x in t if x.get("type")=="BESS"])
    inv = len([x for x in t if x.get("type")=="Inverter"])
    sol = len([x for x in t if x.get("type")=="Solar"])
    total = sum(x.get("amount",0) for x in t)
    a = "UAH " + (f"{total/1e6:.1f}M" if total>1e6 else f"{total:,.0f}")
    send(cid, "<b>UZE Status</b>\nTotal: <b>" + str(len(t)) + "</b>\nUrgent: <b>" + str(urg) + "</b>\nBESS:" + str(bess) + " Inv:" + str(inv) + " Sol:" + str(sol) + "\nAmount: " + a)

def cmd_top5(cid):
    t = load_results()
    if not t: send(cid,"No tenders"); return
    top = sorted(t, key=lambda x:x.get("score",0), reverse=True)[:5]
    msg = "<b>Top 5:</b>\n\n"
    for i,x in enumerate(top,1):
        a = "UAH " + f"{x.get('amount',0):,.0f}"
        msg += str(i) + ". [" + str(x.get("score",0)) + "] " + x.get("title","")[:60] + "\n   <a href=\"" + x.get("url","") + "\">" + a + "</a>\n\n"
    send(cid, msg)

def cmd_scan(cid):
    send(cid,"Scanning... wait 3-5 min")
    def do():
        try:
            from sources.prozorro import get_tenders, to_telegram_message
            t = get_tenders(24)
            if t:
                send(cid, "Found <b>" + str(len(t)) + "</b> tenders!")
                for x in sorted(t,key=lambda x:x.get("score",0),reverse=True)[:10]:
                    send(cid, to_telegram_message(x))
                    time.sleep(0.5)
            else: send(cid,"No new tenders.")
        except Exception as e: send(cid, "Error: " + str(e))
    threading.Thread(target=do, daemon=True).start()

def handle(u):
    msg = u.get("message",{})
    text = (msg.get("text","") or "").strip().lower()
    cid = msg.get("chat",{}).get("id")
    if not cid or not text: return
    if "/status" in text: cmd_status(cid)
    elif "/top5" in text: cmd_top5(cid)
    elif "/scan" in text: cmd_scan(cid)
    elif "/start" in text or "/help" in text:
        send(cid,"<b>UZE Tender Bot</b>\n\n/status - stats\n/top5 - top tenders\n/scan - manual scan\n/help - this")

print("=== UZE Bot started ===")
try: requests.post(API + "/setMyCommands", json={"commands":[{"command":"status","description":"Stats"},{"command":"top5","description":"Top 5"},{"command":"scan","description":"Scan"},{"command":"help","description":"Help"}]})
except: pass

offset = 0
while True:
    try:
        r = requests.get(API + "/getUpdates", params={"offset":offset,"timeout":30}, timeout=35)
        for u in r.json().get("result",[]):
            offset = u["update_id"]+1
            handle(u)
    except KeyboardInterrupt: break
    except: time.sleep(5)

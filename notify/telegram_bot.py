import os, asyncio, requests
from datetime import datetime

BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
CHAT_ID   = os.getenv("TG_CHAT_ID", "")

def send_sync(text):
    """Синхронна відправка (використовується в scanner.py)"""
    if not BOT_TOKEN or not CHAT_ID:
        print("[TG] Немає токена/chat_id, пропуск")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text,
            "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        r = requests.post(url, json=data, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[TG] Помилка відправки: {e}")


def format_tender(t):
    days = ""
    if t.get("deadline"):
        try:
            d = datetime.fromisoformat(t["deadline"])
            n = (d - datetime.utcnow()).days
            if n <= 0:  days = " 🔴 ЗАКРИТО"
            elif n <= 3: days = f" 🔴 {n} дн!"
            elif n <= 7: days = f" 🟡 {n} дн"
            else:        days = f" 🟢 {n} дн"
        except:
            pass

    type_icon = {"BESS":"🔋","Inverter":"⚡","Solar":"☀️"}.get(t.get("type",""),"📋")
    src_label = {"prozorro":"Prozorro","ungm":"UNGM","ted":"TED EU",
                 "dream":"DREAM","dtek":"DTEK"}.get(t.get("source",""),"—")

    amt = t.get("amount", 0)
    cur = t.get("currency","UAH")
    if amt:
        if cur == "UAH": amt_str = f"₴{amt/1e6:.2f}M"
        elif cur == "USD": amt_str = f"${amt/1e6:.2f}M"
        else: amt_str = f"€{amt/1e6:.2f}M"
    else:
        amt_str = "—"

    return (
        f"{type_icon} <b>Новий тендер УЗЕ</b> [{src_label}]\n\n"
        f"📋 {t.get('title','')}\n"
        f"🏢 {t.get('org','')}\n"
        f"💰 {amt_str}\n"
        f"⏰ Дедлайн: {t.get('deadline','—')}{days}\n"
        f"📊 Релевантність: {t.get('score',0)}/100\n"
        f"🔗 <a href=\"{t.get('url','')}\">Відкрити →</a>"
    )


def send_new_tenders(tenders):
    if not tenders:
        print("[TG] Нових тендерів нема, мовчимо")
        return
    for t in tenders:
        msg = format_tender(t)
        send_sync(msg)
        import time; time.sleep(0.5)
    print(f"[TG] Надіслано {len(tenders)} сповіщень")


def send_digest(all_tenders):
    if not all_tenders:
        return
    lines = [f"📊 <b>Дайджест УЗЕ-тендерів</b> — {datetime.utcnow().strftime('%d.%m.%Y')}\n",
             f"Всього активних: {len(all_tenders)}\n"]
    for t in sorted(all_tenders, key=lambda x: x.get("score",0), reverse=True)[:10]:
        dl = t.get("deadline","—")
        amt = t.get("amount",0)
        cur = t.get("currency","UAH")
        s = f"• {t.get('title','')[:60]}…\n"
        s += f"  💰 {amt/1e6:.1f}M {cur} | ⏰ {dl} | {t.get('source','').upper()}\n"
        lines.append(s)
    lines.append(f"\n🔗 <a href=\"https://YOUR-ORG.github.io/tender-monitor/\">Відкрити дашборд →</a>")
    send_sync("\n".join(lines))

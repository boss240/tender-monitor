import requests, time, json
from datetime import datetime, timedelta

BASE = "https://public-api.prozorro.gov.ua/api/2.5"
CPV_WHITELIST = set(["31154000-0", "31155000-7", "31440000-2", "31150000-2", "09331200-0", "09332000-5"])
CPV_BLACKLIST = set(["31430000-9", "31431000-6", "31432000-3", "31434000-7", "42662000-4", "42662100-5", "44512000-2", "35613000-4"])
KEYWORDS_INCLUDE = ["bess", "lifepo4", "battery storage", "energy storage", "ess", "solar pv", "ups", "deye", "poweroad", "renewable energy", "акумулятор", "накопичувач енергії", "інвертор", "безперебійне живлення", "гібридний інвертор", "зберігання енергії", "відновлювана енергія", "сонячна панель", "фотовольтаїчний", "дбж", "накопичувач"]
KEYWORDS_EXCLUDE = ["dji", "matrice", "drone", "mavic", "phantom", "fpv", "mma-", "mig-", "tig-", "автомобіл", "трактор", "ноутбук", "смартфон", "телефон", "мотоцикл", "скутер", "ліхтар", "дрон", "квадрокоптер", "бпла", "зварюв", "плазмор", "дефібрил", "рентген", "іграшк", "дитяч", "велосипед", "шуруповерт", "пилосос", "автобус", "навантажувач", "самокат", "кондиціонер", "планшет", "електроінструмент", "електрокар", "томограф", "кардіо","генератор","батарейк","зарядн","конденсатор","для авто","стартерн","фонар","радіостанці","вимірювальн","комп'ютер","принтер","баласти для розрядних","лампа","освітлен","світильник","прожектор","ремонтних робіт","матеріалів для","портативн","майно зв'язку","запасні частини","kia","solid state","газ-66","військов","marsriva","lpm-"]
_BESS_KW = ["bess", "накопичувач", "акумулятор", "lifepo4", "battery"]
_INV_KW = ["інвертор", "inverter"]
_SOL_KW = ["solar", "сонячн"]

MIN_AMOUNT = 30000

def _fetch_all_ids(hours_back):
    since = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%S")
    offset = since + "Z"
    all_ids = []
    for page in range(50):
        url = f"{BASE}/tenders?offset={offset}&limit=100&opt_fields=id"
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"[Prozorro] Page {page} error: {e}")
            break
        items = data.get("data", [])
        if not items:
            break
        all_ids.extend([t["id"] for t in items])
        np = data.get("next_page", {}).get("offset", "")
        if not np or np == offset:
            break
        offset = np
        print(f"[Prozorro] Page {page+1}: +{len(items)} (total: {len(all_ids)})")
        time.sleep(0.3)
    return all_ids

def get_tenders(hours_back=12, seen_ids=None):
    if seen_ids is None:
        seen_ids = set()
    raw_ids = _fetch_all_ids(hours_back)
    if not raw_ids:
        print("[Prozorro] No IDs fetched.")
        return []
    print(f"[Prozorro] Total IDs: {len(raw_ids)}, checking...")
    results = []
    sb = se = sn = ck = 0
    for idx, tid in enumerate(raw_ids):
        if tid in seen_ids:
            continue
        try:
            r = requests.get(f"{BASE}/tenders/{tid}", timeout=20)
            r.raise_for_status()
            d = r.json().get("data", {})
        except:
            time.sleep(0.5)
            continue
        ck += 1
        items = d.get("items", [])
        cpvs = [i.get("classification", {}).get("id", "") for i in items]
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
        period = d.get("tenderPeriod", {})
        val = d.get("value", {}) or {}
        dl_raw = period.get("endDate", "")
        dl = dl_raw[:10] if dl_raw else ""
        amt = val.get("amount", 0) or 0
        if 0 < amt < MIN_AMOUNT: time.sleep(0.3); continue
        tcpvs = list(set(mc)) or cpvs[:3]
        tp = "Other"
        if any(c in {"31440000-2","31154000-0"} for c in tcpvs) or any(k in tl for k in _BESS_KW):
            tp = "BESS"
        elif any(c in {"31155000-7"} for c in tcpvs) or any(k in tl for k in _INV_KW):
            tp = "Inverter"
        elif any(c in {"09331200-0","09332000-5"} for c in tcpvs) or any(k in tl for k in _SOL_KW):
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
        results.append({
            "id": d.get("tenderID", tid), "_raw_id": tid,
            "title": title, "org": d.get("procuringEntity",{}).get("name","---"),
            "source": "prozorro", "platform": "prozorro", "type": tp,
            "amount": amt, "currency": val.get("currency","UAH"),
            "deadline": dl, "cpvs": tcpvs,
            "cpv": tcpvs[0] if tcpvs else "",
            "status": st, "url": f"https://prozorro.gov.ua/tender/{tid}",
            "is_new": True, "score": sc,
            "fetched_at": datetime.utcnow().isoformat(),
        })
        seen_ids.add(tid)
        time.sleep(0.3)
        if (idx+1) % 50 == 0:
            print(f"[Prozorro] Checked {idx+1}/{len(raw_ids)}, found: {len(results)}")
    print(f"[Prozorro] Done. Checked: {ck}, Found: {len(results)}")
    print(f"[Prozorro] Skipped: {sb} (CPV black) | {se} (kw excl) | {sn} (no match)")
    return results

def to_telegram_message(t):
    days = 0
    if t.get("deadline"):
        try: days = (datetime.strptime(t["deadline"],"%Y-%m-%d") - datetime.now()).days
        except: pass
    ic = "\U0001f534" if days<=3 else "\U0001f7e1" if days<=7 else "\U0001f7e2"
    a = f"UAH {t['amount']:,.0f}" if t.get("amount") else "---"
    cpv = ", ".join(t.get("cpvs",[])[:2])
    return (f"{ic} *New UZE tender*\n\n"
        f"\U0001f4cb {t['title']}\n"
        f"\U0001f3e2 {t.get('org','---')}\n"
        f"\U0001f4b0 {a}\n"
        f"\U0001f4e6 CPV: `{cpv}`\n"
        f"\u23f0 Deadline: {t.get('deadline','---')} ({days} d.)\n"
        f"\U0001f3af Score: {t.get('score',0)}/100\n"
        f"\U0001f517 {t.get('url','')}")

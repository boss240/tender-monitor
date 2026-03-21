import requests
import json
from datetime import datetime, timedelta
import time

BASE = "https://public.api.prozorro.gov.ua/api/2.5"

CPV_CODES = {
    "31154000-0": "ДБЖ (безперебійні джерела живлення)",
    "31155000-7": "Інвертори",
    "31440000-2": "Батареї / акумулятори",
    "31150000-2": "Баластні дроселі",
    "09331200-0": "Сонячні фотоелектричні модулі",
    "09332000-5": "Сонячні установки",
    "31521000-4": "Стаціонарне освітлення",
}

KEYWORDS = [
    "bess", "lifepo4", "акумулятор", "накопичувач енергії",
    "інвертор", "battery storage", "energy storage", "ess",
    "solar pv", "фотовольтаїчний", "сонячна панель",
    "відновлювана енергія", "renewable energy", "дбж",
]

def get_tenders(hours_back=6, seen_ids=None):
    if seen_ids is None:
        seen_ids = set()

    since = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%S")
    url = f"{BASE}/tenders?offset={since}&limit=100&opt_fields=id"
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        ids = [t["id"] for t in resp.json().get("data", [])]
    except Exception as e:
        print(f"[Prozorro] Помилка отримання списку: {e}")
        return []

    results = []
    for tender_id in ids:
        if tender_id in seen_ids:
            continue
        try:
            r = requests.get(f"{BASE}/tenders/{tender_id}", timeout=20)
            r.raise_for_status()
            d = r.json().get("data", {})
        except Exception as e:
            print(f"[Prozorro] Пропуск {tender_id}: {e}")
            time.sleep(0.5)
            continue

        items = d.get("items", [])
        cpvs = [i.get("classification", {}).get("id", "") for i in items]
        title = d.get("title", "")
        title_lower = title.lower()

        matched_cpv = [c for c in cpvs if c in CPV_CODES]
        matched_kw  = [k for k in KEYWORDS if k in title_lower]

        if matched_cpv or matched_kw:
            period = d.get("tenderPeriod", {})
            val    = d.get("value", {})
            deadline_raw = period.get("endDate", "")
            deadline = deadline_raw[:10] if deadline_raw else ""

            results.append({
                "id":       d.get("tenderID", tender_id),
                "_raw_id":  tender_id,
                "title":    title,
                "org":      d.get("procuringEntity", {}).get("name", "—"),
                "source":   "prozorro",
                "type":     _classify_type(matched_cpv, title_lower),
                "amount":   val.get("amount", 0),
                "currency": val.get("currency", "UAH"),
                "deadline": deadline,
                "cpvs":     list(set(matched_cpv)) or cpvs[:3],
                "status":   d.get("status", "active"),
                "url":      f"https://prozorro.gov.ua/tender/{tender_id}",
                "is_new":   True,
                "score":    _score(matched_cpv, matched_kw, val.get("amount", 0)),
                "fetched_at": datetime.utcnow().isoformat(),
            })
            seen_ids.add(tender_id)

        time.sleep(0.3)

    print(f"[Prozorro] Знайдено: {len(results)}")
    return results


def _classify_type(cpvs, title):
    if any(c in ["31440000-2", "31154000-0"] for c in cpvs) or \
       any(k in title for k in ["bess", "накопичувач", "акумулятор", "lifepo4", "battery"]):
        return "BESS"
    if any(c in ["31155000-7"] for c in cpvs) or "інвертор" in title or "inverter" in title:
        return "Inverter"
    if any(c in ["09331200-0", "09332000-5"] for c in cpvs) or "solar" in title or "сонячн" in title:
        return "Solar"
    return "BESS"


def _score(matched_cpv, matched_kw, amount):
    score = 50
    score += min(len(matched_cpv) * 15, 30)
    score += min(len(matched_kw) * 5, 15)
    if amount > 5_000_000:   score += 5
    return min(score, 99)

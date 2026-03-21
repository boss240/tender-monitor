import requests
import json
from datetime import datetime, timedelta
import time

BASE = "https://public-api.prozorro.gov.ua/api/2.5"

CPV_CODES = {
    "31154000-0": "ДБЖ (безперебійні джерела живлення)",
    "31155000-7": "Інвертори",
    "31440000-2": "Батареї / акумулятори",
    "31150000-2": "Баластні дроселі",
    "09331200-0": "Сонячні фотоелектричні модулі",
    "09332000-5": "Сонячні установки",
    "31521000-4": "Стаціонарне освітлення",
}

# Whitelist CPV (усі ключі зі словника)
CPV_WHITELIST = set(CPV_CODES.keys())

# Ключові слова, які повинні натякати на УЗЕ‑тематику
KEYWORDS_INCLUDE = [
    "bess", "lifepo4", "акумулятор", "накопичувач енергії",
    "інвертор", "battery storage", "energy storage", "ess",
    "solar pv", "фотовольтаїчний", "сонячна панель",
    "відновлювана енергія", "renewable energy", "дбж",
]

# Слова, які краще відсікти (акб для авто, гаджетів тощо)
KEYWORDS_EXCLUDE = [
    "автомобіл", "трактор", "ноутбук", "смартфон", "телефон",
]


def get_tenders(hours_back: int = 6, seen_ids: set | None = None) -> list[dict]:
    """
    Повертає список нових тендерів за останні `hours_back` годин.
    Фільтрує по CPV_WHITELIST і KEYWORDS_INCLUDE / KEYWORDS_EXCLUDE.
    """
    if seen_ids is None:
        seen_ids = set()

    since = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%S")
    offset = f"{since}Z"  # UTC‑мітка

    url = f"{BASE}/tenders?offset={offset}&limit=100&opt_fields=id"

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        ids = [t["id"] for t in resp.json().get("data", [])]
    except Exception as e:
        print(f"[Prozorro] Помилка отримання списку: {e}")
        return []

    results: list[dict] = []

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

        title = d.get("title", "") or ""
        title_lower = title.lower()

        # CPV, які потрапили у whitelist
        matched_cpv = [c for c in cpvs if c in CPV_WHITELIST]

        # Ключові слова
        matched_kw = [k for k in KEYWORDS_INCLUDE if k in title_lower]
        blocked_kw = [k for k in KEYWORDS_EXCLUDE if k in title_lower]

        # Якщо в назві є "заборонені" слова — одразу пропускаємо
        if blocked_kw:
            time.sleep(0.3)
            continue

        # Якщо не збігся жоден CPV і жодне з ключових слів — теж пропускаємо
        if not matched_cpv and not matched_kw:
            time.sleep(0.3)
            continue

        period = d.get("tenderPeriod", {})
        val = d.get("value", {}) or {}

        deadline_raw = period.get("endDate", "")
        deadline = deadline_raw[:10] if deadline_raw else ""

        amount = val.get("amount", 0)
        currency = val.get("currency", "UAH")

        tender_cpvs = list(set(matched_cpv)) or cpvs[:3]

        results.append(
            {
                "id": d.get("tenderID", tender_id),
                "_raw_id": tender_id,
                "title": title,
                "org": d.get("procuringEntity", {}).get("name", "—"),
                "source": "prozorro",
                "type": _classify_type(tender_cpvs, title_lower),
                "amount": amount,
                "currency": currency,
                "deadline": deadline,
                "cpvs": tender_cpvs,
                "status": d.get("status", "active"),
                "url": f"https://prozorro.gov.ua/tender/{tender_id}",
                "is_new": True,
                "score": _score(tender_cpvs, matched_kw, amount),
                "fetched_at": datetime.utcnow().isoformat(),
            }
        )

        seen_ids.add(tender_id)
        time.sleep(0.3)

    print(f"[Prozorro] Знайдено: {len(results)}")
    return results


def _classify_type(cpvs: list[str], title: str) -> str:
    """
    Груба класифікація типу УЗЕ за CPV + ключовими словами.
    """
    title_l = title.lower()

    if any(c in {"31440000-2", "31154000-0"} for c in cpvs) or any(
        k in title_l for k in ["bess", "накопичувач", "акумулятор", "lifepo4", "battery"]
    ):
        return "BESS"

    if any(c in {"31155000-7"} for c in cpvs) or ("інвертор" in title_l or "inverter" in title_l):
        return "Inverter"

    if any(c in {"09331200-0", "09332000-5"} for c in cpvs) or ("solar" in title_l or "сонячн" in title_l):
        return "Solar"

    return "Other"


def _score(cpvs: list[str], matched_kw: list[str], amount: float) -> int:
    """
    Простий скоринг релевантності:
    - базові 50 балів
    - за кожен CPV із whitelist +15 (макс +30)
    - за кожне ключове слово +5 (макс +15)
    - бонус за велику суму
    """
    score = 50

    # CPV у whitelist
    cpv_hits = len([c for c in cpvs if c in CPV_WHITELIST])
    score += min(cpv_hits * 15, 30)

    # Ключові слова
    score += min(len(matched_kw) * 5, 15)

    # Бонус за суму
    if amount > 5_000_000:
        score += 5

    return max(0, min(score, 99))

import requests, os
from datetime import datetime

# Безкоштовний ключ: https://api.ted.europa.eu → Register
TED_KEY = os.getenv("TED_API_KEY", "")
BASE    = "https://api.ted.europa.eu/v3"

def get_tenders(seen_ids=None):
    if seen_ids is None:
        seen_ids = set()
    if not TED_KEY:
        print("[TED] Немає API ключа, пропуск")
        return []

    headers = {"Authorization": f"Bearer {TED_KEY}"}
    payload = {
        "query":  '(ukraine OR "UA") AND (BESS OR "battery storage" OR inverter OR "solar PV" OR "renewable energy")',
        "fields": ["notice-number","title","deadline-date","estimated-value","currency",
                   "buyer-name","cpv-codes","ted-notice-url"],
        "page":   1,
        "limit":  50,
        "scope":  "ACTIVE",
    }
    try:
        r = requests.post(f"{BASE}/notices/search", json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        notices = r.json().get("notices", [])
    except Exception as e:
        print(f"[TED] Помилка: {e}")
        return []

    results = []
    for n in notices:
        ref = str(n.get("notice-number", ""))
        if ref in seen_ids:
            continue
        deadline = (n.get("deadline-date") or "")[:10]
        results.append({
            "id":       ref,
            "_raw_id":  ref,
            "title":    n.get("title", {}).get("eng") or n.get("title", "TED Notice"),
            "org":      n.get("buyer-name", [{}])[0].get("eng", "EU Agency") if n.get("buyer-name") else "EU Agency",
            "source":   "ted",
            "type":     _classify(n.get("title", {}), n.get("cpv-codes", [])),
            "amount":   n.get("estimated-value", 0) or 0,
            "currency": n.get("currency", "EUR"),
            "deadline": deadline,
            "cpvs":     n.get("cpv-codes", [])[:3],
            "status":   "active",
            "url":      n.get("ted-notice-url", f"https://ted.europa.eu/udl?uri=TED:NOTICE:{ref}"),
            "is_new":   True,
            "score":    88,
            "fetched_at": datetime.utcnow().isoformat(),
        })
        seen_ids.add(ref)

    print(f"[TED] Знайдено: {len(results)}")
    return results

def _classify(title_dict, cpvs):
    title = str(title_dict).lower()
    if "bess" in title or "battery" in title or "storage" in title: return "BESS"
    if "inverter" in title: return "Inverter"
    if "solar" in title or "photovoltaic" in title: return "Solar"
    return "BESS"

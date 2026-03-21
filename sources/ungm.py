import requests, os
from datetime import datetime

# Безкоштовний ключ: https://developer.ungm.org → Register
UNGM_KEY = os.getenv("UNGM_API_KEY", "")
BASE = "https://www.ungm.org/API"

KEYWORDS = "battery storage BESS inverter solar PV renewable energy Ukraine"

def get_tenders(seen_ids=None):
    if seen_ids is None:
        seen_ids = set()
    if not UNGM_KEY:
        print("[UNGM] Немає API ключа, пропуск")
        return []

    headers = {"Authorization": f"Token {UNGM_KEY}"}
    params  = {
        "keyword":   KEYWORDS,
        "country":   "Ukraine",
        "pageSize":  50,
        "status":    "active",
    }
    try:
        r = requests.get(f"{BASE}/Tender", headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[UNGM] Помилка: {e}")
        return []

    results = []
    for t in data.get("tenders", data if isinstance(data, list) else []):
        ref = str(t.get("ReferenceNumber") or t.get("id", ""))
        if ref in seen_ids:
            continue
        deadline = (t.get("DeadlineDate") or t.get("deadline", ""))[:10]
        results.append({
            "id":       ref,
            "_raw_id":  ref,
            "title":    t.get("Title") or t.get("title", "UNGM Tender"),
            "org":      t.get("Agency") or t.get("organization", "UN Agency"),
            "source":   "ungm",
            "type":     "BESS",
            "amount":   t.get("EstimatedValue") or 0,
            "currency": t.get("Currency") or "USD",
            "deadline": deadline,
            "cpvs":     [],
            "status":   "active",
            "url":      f"https://www.ungm.org/Public/Notice/{ref}",
            "is_new":   True,
            "score":    82,
            "fetched_at": datetime.utcnow().isoformat(),
        })
        seen_ids.add(ref)

    print(f"[UNGM] Знайдено: {len(results)}")
    return results

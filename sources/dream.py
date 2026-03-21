import requests, re
from datetime import datetime
from bs4 import BeautifulSoup

BASE = "https://dream.gov.ua"

KEYWORDS = ["bess", "акумулятор", "накопичувач", "інвертор",
            "solar", "сонячн", "відновлювана", "renewable", "ess"]

def get_tenders(seen_ids=None):
    if seen_ids is None:
        seen_ids = set()

    urls_to_scan = [
        f"{BASE}/en/projects?categories=energy",
        f"{BASE}/uk/projects?categories=energy",
    ]
    results = []
    for url in urls_to_scan:
        try:
            r = requests.get(url, timeout=20,
                headers={"User-Agent": "Mozilla/5.0 TenderMonitor/1.0"})
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # Шукаємо картки проєктів (структура може змінюватись)
            cards = soup.find_all(["article", "div"],
                                  class_=re.compile(r"project|card|tender", re.I))

            for card in cards:
                title_el = card.find(["h2","h3","h4","a"])
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                title_lower = title.lower()
                if not any(k in title_lower for k in KEYWORDS):
                    continue

                link = title_el.get("href") or card.find("a", href=True)
                link = link if isinstance(link, str) else (link["href"] if link else "")
                if link and not link.startswith("http"):
                    link = BASE + link

                ref = link.split("/")[-1] or title[:20]
                if ref in seen_ids:
                    continue

                results.append({
                    "id":        f"DREAM-{ref}",
                    "_raw_id":   ref,
                    "title":     title,
                    "org":       "DREAM / Мінекоенерго",
                    "source":    "dream",
                    "type":      "BESS",
                    "amount":    0,
                    "currency":  "UAH",
                    "deadline":  "",
                    "cpvs":      [],
                    "status":    "active",
                    "url":       link or f"{BASE}/en/projects",
                    "is_new":    True,
                    "score":     72,
                    "fetched_at": datetime.utcnow().isoformat(),
                })
                seen_ids.add(ref)

        except Exception as e:
            print(f"[DREAM] Помилка {url}: {e}")

    print(f"[DREAM] Знайдено: {len(results)}")
    return results

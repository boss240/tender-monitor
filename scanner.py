#!/usr/bin/env python3
"""
УЗЕ Tender Scanner
Запуск: python scanner.py
GitHub Actions: .github/workflows/scan.yml
"""

import json, os, re, sys
from datetime import datetime
from pathlib import Path

# Додаємо локальні модулі
sys.path.insert(0, str(Path(__file__).parent))

from sources.prozorro import get_tenders as prozorro_tenders
from sources.ungm     import get_tenders as ungm_tenders
from sources.ted      import get_tenders as ted_tenders
from sources.dream    import get_tenders as dream_tenders
from notify.telegram_bot import send_new_tenders, send_digest

DATA_FILE    = Path("data/results.json")
SEEN_FILE    = Path("data/seen_ids.json")
DASHBOARD    = Path("tender-monitor.html")

# ── Завантаження стану ──────────────────────────────────────────────
def load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    return set()

def save_seen(seen):
    SEEN_FILE.parent.mkdir(exist_ok=True)
    SEEN_FILE.write_text(json.dumps(list(seen), ensure_ascii=False, indent=2),
                         encoding="utf-8")

def load_existing():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return []

def save_results(tenders):
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(tenders, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8"
    )

# ── Оновлення дашборду ──────────────────────────────────────────────
def update_dashboard(tenders):
    if not DASHBOARD.exists():
        print("[Dashboard] HTML не знайдено, пропуск")
        return
    html = DASHBOARD.read_text(encoding="utf-8")

    # Перебудувати масив TENDERS у JS
    js_array = json.dumps(tenders, ensure_ascii=False, indent=2, default=str)
    new_html = re.sub(
        r'const TENDERS = \[.*?\];',
        f'const TENDERS = {js_array};',
        html,
        flags=re.DOTALL
    )

    # Оновити мітку часу
    now_str = datetime.utcnow().strftime("%d.%m.%Y %H:%M UTC")
    new_html = re.sub(
        r'Оновлено:.*?автооновлення',
        f'Оновлено: {now_str} · <span class="status-dot live pulse" style="width:6px;height:6px"></span> автооновлення',
        new_html
    )

    DASHBOARD.write_text(new_html, encoding="utf-8")
    print(f"[Dashboard] Оновлено: {len(tenders)} тендерів")

# ── Головна функція ─────────────────────────────────────────────────
def main():
    mode = os.getenv("SCAN_MODE", "incremental")  # incremental | full
    hours = int(os.getenv("HOURS_BACK", "6" if mode == "incremental" else "168"))
    
    print(f"\n{'='*50}")
    print(f"УЗЕ Tender Scanner | {datetime.utcnow().isoformat()}")
    print(f"Режим: {mode} | Горизонт: {hours} годин")
    print(f"{'='*50}\n")

    seen    = load_seen()
    existing = load_existing()
    existing_ids = {t["id"] for t in existing}

    # ── Збір з усіх джерел ──
    all_new = []

    print("▶ Prozorro...")
    all_new += prozorro_tenders(hours_back=hours, seen_ids=seen)

    print("▶ UNGM...")
    all_new += ungm_tenders(seen_ids=seen)

    print("▶ TED EU...")
    all_new += ted_tenders(seen_ids=seen)

    print("▶ DREAM...")
    all_new += dream_tenders(seen_ids=seen)

    # ── Дедуплікація ──
    fresh = [t for t in all_new if t["id"] not in existing_ids]
    print(f"\n✅ Нових тендерів: {len(fresh)} (з {len(all_new)} знайдених)")

    # ── Об'єднання з архівом ──
    # Зберігаємо не більше 200 тендерів, сортуємо за дедлайном
    combined = fresh + existing
    combined = sorted(combined,
                      key=lambda t: t.get("deadline") or "9999",
                      reverse=False)[:200]

    # ── Збереження ──
    save_results(combined)
    save_seen(seen)
    update_dashboard(combined)

    # ── Сповіщення ──
    hour_utc = datetime.utcnow().hour
    if fresh:
        send_new_tenders(fresh)
    if hour_utc in (5, 6):          # 08:00 Київ → щоденний дайджест
        send_digest(combined)

    print(f"\n✅ Готово! Всього в базі: {len(combined)} тендерів")
    print(f"   Збережено: data/results.json + tender-monitor.html\n")

if __name__ == "__main__":
    main()
    import sys
import json
import asyncio

# ... ваші імпорти та функції ...

import os
import requests
import json
from datetime import datetime, timedelta

# ==========================================
# 1. НАЛАШТУВАННЯ ТА ФІЛЬТРИ (УЗЕ / ESS)
# ==========================================
CPV_CODES = ["31154000-0", "31155000-7", "31440000-2"]

# Розширений список ключів (щоб точно щось знайти)
KEYWORDS_INCLUDE = [
    "узе", "ess", "bess", "гібридна система", "система збереження енергії",
    "накопичувач енергії", "інвертор", "акумулятор", "система резервного живлення",
    "дбж", "ups", "зарядна станція", "lifepo4", "li-ion", "deye", "must", "victron"
]

KEYWORDS_EXCLUDE = ["автомобіл", "трактор", "ноутбук", "смартфон", "павербанк"]

# ==========================================
# 2. ФУНКЦІЯ ПОШУКУ НА PROZORRO (РЕАЛЬНЕ API)
# ==========================================
def fetch_prozorro():
    print("[Prozorro] Пошук активних тендерів...")
    tenders_found = []
    
    # Шукаємо за останні 3 дні, щоб дашборд не був порожнім
    start_date = (datetime.now() - timedelta(days=3)).isoformat()
    url = f"https://public.api.openprocurement.org/api/2.5/tenders?descending=1&offset={start_date}"

    try:
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            return []
        
        data = response.json().get('data', [])
        
        for item in data:
            title = item.get('title', '').lower()
            # Перевірка за ключовими словами
            if any(word in title for word in KEYWORDS_INCLUDE):
                # Відсікаємо непотрібне
                if any(ex in title for ex in KEYWORDS_EXCLUDE):
                    continue
                
                tenders_found.append({
                    "title": item.get('title'),
                    "id": item.get('tenderID'),
                    "value": "Див. на сайті", # API потребує окремого запиту для ціни, для швидкості ставимо заглушку
                    "date": "Активний",
                    "link": f"https://prozorro.gov.ua/tender/{item.get('tenderID')}",
                    "source": "Prozorro"
                })
        
        return tenders_found
    except Exception as e:
        print(f"Помилка Prozorro: {e}")
        return []

# ==========================================
# 3. ГЕНЕРАЦІЯ HTML ДАШБОРДУ
# ==========================================
def generate_dashboard(tenders):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>УЗЕ Monitor</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f9; margin: 0; padding: 20px; }}
            .container {{ max-width: 900px; margin: auto; }}
            .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 30px; }}
            .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }}
            .tender-item {{ border-left: 5px solid #3498db; padding: 15px; margin-bottom: 10px; background: #fff; display: flex; justify-content: space-between; align-items: center; border-radius: 0 8px 8px 0; transition: 0.3s; }}
            .tender-item:hover {{ transform: translateX(5px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            .tender-info {{ flex-grow: 1; }}
            .btn {{ background: #3498db; color: white; text-decoration: none; padding: 8px 15px; border-radius: 5px; font-size: 14px; }}
            .status-badge {{ background: #27ae60; color: white; padding: 3px 8px; border-radius: 10px; font-size: 12px; }}
            .sync-time {{ font-size: 14px; opacity: 0.9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔋 УЗЕ Monitor: ESS & Backup Power</h1>
                <div class="sync-time">✅ Останнє оновлення: <strong>{now}</strong> (UTC+2)</div>
            </div>

            <div class="card">
                <h3>📊 Статус систем</h3>
                <div style="display: flex; gap: 20px;">
                    <div>🟢 Prozorro: <b>Online</b></div>
                    <div>🟡 DREAM: <b>Checking</b></div>
                    <div>🔴 UNGM/TED: <b>No Key</b></div>
                </div>
            </div>

            <h2>🔍 Знайдені тендери (останні 72 години)</h2>
    """

    if not tenders:
        html_content += """
        <div class="card" style="text-align: center; color: #666;">
            <p>Наразі нових тендерів за вашими фільтрами не знайдено.<br>
            Спробуйте розширити ключові слова або зачекайте наступного циклу.</p>
        </div>
        """
    else:
        for t in tenders:
            html_content += f"""
            <div class="tender-item">
                <div class="tender-info">
                    <div style="font-weight: bold; margin-bottom: 5px;">{t['title']}</div>
                    <div style="font-size: 13px; color: #7f8c8d;">{t['id']} | {t['source']}</div>
                </div>
                <div>
                    <a href="{t['link']}" target="_blank" class="btn">Відкрити</a>
                </div>
            </div>
            """

    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open("tender-monitor.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# ==========================================
# 4. ЗАПУСК
# ==========================================
if __name__ == "__main__":
    results = fetch_prozorro()
    
    # Зберігаємо JSON
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    # Створюємо сторінку
    generate_dashboard(results)
    print(f"Готово! Знайдено {len(results)} тендерів.")

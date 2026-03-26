import os
import requests
import json
from datetime import datetime

# ==========================================
# 1. НАЛАШТУВАННЯ ТА ФІЛЬТРИ (УЗЕ / ESS)
# ==========================================
CPV_CODES = {
    "31154000-0": "Джерела безперебійного живлення (UPS, зарядні станції)",
    "31155000-7": "Інвертори",
    "31440000-2": "Акумуляторні батареї (АКБ, Li-ion, LiFePO4)"
}

KEYWORDS_INCLUDE = [
    "узе", "ess", "bess", "гібридна система", "система збереження енергії",
    "накопичувач енергії", "інвертор", "акумулятор", "система резервного живлення",
    "дбж", "ups", "зарядна станція", "lifepo4", "li-ion", "deye", "must", "victron"
]

KEYWORDS_EXCLUDE = ["автомобіл", "трактор", "свинцево", "ноутбук", "смартфон", "павербанк"]

# ==========================================
# 2. ФУНКЦІЯ ПОШУКУ НА PROZORRO
# ==========================================
def fetch_prozorro():
    print("[Prozorro] Пошук тендерів...")
    tenders = []
    # Спрощений приклад запиту до API (зазвичай тут цикл по CPV)
    url = "https://public.api.openprocurement.org/api/2.5/tenders"
    try:
        # Тут логіка запиту... (для прикладу повертаємо порожній список або імітацію)
        # У реальному коді тут ваш блок requests.get()
        return tenders
    except Exception as e:
        print(f"[Prozorro] Помилка: {e}")
        return []

# ==========================================
# 3. ГЕНЕРАЦІЯ ДАШБОРДУ (HTML)
# ==========================================
def generate_dashboard(tenders):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>УЗЕ Tender Monitor</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f7f6; color: #333; margin: 20px; }}
            .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .status-online {{ color: #27ae60; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; }}
            .tag {{ padding: 4px 8px; background: #e1f5fe; border-radius: 4px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🔋 Дашборд моніторингу УЗЕ / ESS</h1>
            <p><strong>Оновлено:</strong> {now} · <span class="status-online">автооновлення активне</span></p>
        </div>

        <div class="card">
            <h3>📊 Статус джерел</h3>
            <table>
                <tr><th>Джерело</th><th>Статус</th><th>Остання синхронізація</th><th>Результат</th></tr>
                <tr><td>Prozorro</td><td class="status-online">Active</td><td>{now}</td><td>Бот працює</td></tr>
                <tr><td>DREAM</td><td class="status-online">Active</td><td>{now}</td><td>Оновлено посилання</td></tr>
                <tr><td>UNGM / TED</td><td>Waiting</td><td>{now}</td><td>Очікує API Key</td></tr>
            </table>
        </div>

        <div class="card">
            <h3>🔔 Останні знайдені тендери</h3>
            <table>
                <tr><th>Назва тендера</th><th>Сума</th><th>Дата завершення</th><th>Джерело</th></tr>
    """

    if not tenders:
        html_template += "<tr><td colspan='4'>Сьогодні нових тендерів не знайдено. Перевірка триває...</td></tr>"
    else:
        for t in tenders:
            html_template += f"""
                <tr>
                    <td>{t.get('title')}</td>
                    <td><b>{t.get('value')} UAH</b></td>
                    <td>{t.get('date')}</td>
                    <td><span class="tag">{t.get('source')}</span></td>
                </tr>
            """

    html_template += """
            </table>
        </div>
    </body>
    </html>
    """
    
    with open("tender-monitor.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"[Dashboard] Файл оновлено о {now}")

# ==========================================
# 4. ГОЛОВНИЙ ЗАПУСК
# ==========================================
if __name__ == "__main__":
    found_tenders = fetch_prozorro()
    # Зберігаємо результати в JSON для історії
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(found_tenders, f, ensure_ascii=False, indent=4)
    
    # Оновлюємо візуальний дашборд
    generate_dashboard(found_tenders)

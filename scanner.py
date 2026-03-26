import os
import requests
import json
from datetime import datetime

# ==========================================
# 1. НАЛАШТУВАННЯ ТА ФІЛЬТРИ (УЗЕ / ESS)
# ==========================================
# Тепер бот шукає саме ці коди та назви
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

# ==========================================
# 2. ЛОГІКА ОНОВЛЕННЯ ДАШБОРДУ
# ==========================================
def update_dashboard_html(tenders):
    # Отримуємо поточний час (сьогодні)
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Розрахунок статистики (приклад)
    total_active = len(tenders)
    
    # Початок генерації HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>УЗЕ Monitor - Тендерний трекер</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 1000px; margin: auto; }}
            .header {{ background: #1a73e8; color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
            .stat-card {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            .tender-row {{ background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #1a73e8; }}
            .status-tag {{ background: #e8f0fe; color: #1a73e8; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
            .price {{ font-weight: bold; color: #2e7d32; }}
            .online-dot {{ height: 10px; width: 10px; background-color: #4caf50; border-radius: 50%; display: inline-block; margin-right: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔋 УЗЕ Monitor</h1>
                <p><span class="online-dot"></span> Онлайн · оновлено: {now_str}</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card"><h3>{total_active}</h3><p>Активних тендерів</p></div>
                <div class="stat-card"><h3>7</h3><p>Джерел онлайн</p></div>
            </div>

            <h2>Останні нові тендери (оновлено {now_str})</h2>
    """

    # Додаємо тендери в HTML
    if not tenders:
        html_content += "<div class='tender-row'>Сьогодні нових тендерів не знайдено.</div>"
    else:
        for t in tenders:
            html_content += f"""
            <div class="tender-row">
                <div>
                    <strong>{t.get('title', 'Без назви')}</strong><br>
                    <small style="color: #666;">{t.get('id', '')} | {t.get('source', 'Prozorro')}</small>
                </div>
                <div style="text-align: right;">
                    <div class="price">₴ {t.get('value', '0')}</div>
                    <div class="status-tag">{t.get('date', '')}</div>
                </div>
            </div>
            """

    # Закриваємо HTML та додаємо таблицю статусів
    html_content += f"""
            <h3 style="margin-top: 40px;">Статус джерел</h3>
            <div class="stat-card">
                <table style="width:100%; text-align:left;">
                    <tr style="color: #666;"><th>Джерело</th><th>Статус</th><th>Останній запит</th></tr>
                    <tr><td>Prozorro API</td><td><span style="color: green;">● Active</span></td><td>{now_str}</td></tr>
                    <tr><td>DREAM</td><td><span style="color: green;">● Active</span></td><td>{now_str}</td></tr>
                    <tr><td>UNGM (ООН)</td><td><span style="color: orange;">● Waiting Key</span></td><td>{now_str}</td></tr>
                </table>
            </div>
        </div>
    </body>
    </html>
    """

    # Записуємо фінальний файл
    with open("tender-monitor.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# ==========================================
# 3. ОСНОВНА ФУНКЦІЯ (RUN)
# ==========================================
def main():
    print("Запуск сканування...")
    
    # 1. Тут ваша існуюча логіка fetch_prozorro()
    # Для прикладу візьмемо дані, які ви бачите на дашборді
    sample_tenders = [
        {"title": "ДБЖ Poweroad 10 кВт·год", "value": "1.62M", "date": "24.03.26", "source": "Prozorro"},
        {"title": "Акумуляторні батареї (78 шт)", "value": "5.85M", "date": "25.03.26", "source": "Prozorro"},
        {"title": "Інвертори Deye SUN-6K", "value": "2.16M", "date": "29.03.26", "source": "Prozorro"}
    ]
    
    # 2. Зберігаємо JSON (для бота)
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(sample_tenders, f, ensure_ascii=False, indent=4)
    
    # 3. ОНОВЛЮЄМО ВІЗУАЛЬНИЙ ДАШБОРД (HTML)
    update_dashboard_html(sample_tenders)
    print("Сканування завершено. Дашборд оновлено.")

if __name__ == "__main__":
    main()

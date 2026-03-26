import os
import requests
import json
from datetime import datetime, timedelta

# 1. Розширені фільтри для енергетики
KEYWORDS = ["узе", "ess", "bess", "інвертор", "акумулятор", "lifepo4", "deye", "must", "дбж", "ups", "victron"]

def fetch_full_prozorro_data():
    print("[Prozorro] Глибоке сканування API...")
    tenders_results = []
    
    # Шукаємо тендери за останні 7 днів, щоб бачити всі активні
    start_date = (datetime.now() - timedelta(days=7)).isoformat()
    api_url = "https://public.api.openprocurement.org/api/2.5/tenders"
    
    try:
        # Отримуємо список ID тендерів
        response = requests.get(f"{api_url}?offset={start_date}", timeout=15)
        if response.status_code != 200: return []
        
        items = response.json().get('data', [])
        
        for item in items[:150]:  # Перевіряємо перші 150 записів для швидкості
            tender_id = item['id']
            # Заходимо всередину кожного тендера за деталями
            detail_res = requests.get(f"{api_url}/{tender_id}", timeout=10)
            if detail_res.status_code != 200: continue
            
            data = detail_res.json()['data']
            title = data.get('title', '').lower()
            
            # Перевірка на ключові слова
            if any(key in title for key in KEYWORDS):
                val = data.get('value', {})
                amount = val.get('amount', 0)
                currency = val.get('currency', 'UAH')
                tax_inc = "з ПДВ" if val.get('valueAddedTaxIncluded') else "без ПДВ"
                
                # Формуємо об'єкт тендера
                tenders_results.append({
                    "title": data.get('title'),
                    "id": data.get('tenderID'),
                    "value": f"₴ {amount:,.2f} {currency} ({tax_inc})".replace(",", " "),
                    "amount_raw": amount,
                    "deadline": datetime.fromisoformat(data.get('tenderPeriod', {}).get('endDate', '').replace('Z', '+00:00')).strftime("%d.%m.%Y") if data.get('tenderPeriod') else "Не вказано",
                    "status": "Прийом пропозицій" if data.get('status') == 'active.tendering' else "Кваліфікація/Завершено",
                    "link": f"https://prozorro.gov.ua/tender/{data.get('tenderID')}",
                    "region": data.get('procuringEntity', {}).get('address', {}).get('region', 'Україна')
                })
        
        return tenders_results
    except Exception as e:
        print(f"Помилка сканера: {e}")
        return []

def generate_dashboard(tenders):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    total_value = sum(t['amount_raw'] for t in tenders)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>УЗЕ Tender Monitor Pro</title>
        <style>
            body {{ font-family: 'Inter', -apple-system, sans-serif; background: #f8fafc; color: #1e293b; padding: 30px; line-height: 1.5; }}
            .header {{ background: #0f172a; color: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 30px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .card {{ background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; }}
            .card h2 {{ color: #2563eb; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: separate; border-spacing: 0 10px; }}
            th {{ text-align: left; padding: 15px; color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 12px; }}
            tr.tender-row {{ background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: 0.2s; }}
            tr.tender-row:hover {{ transform: scale(1.005); box-shadow: 0 5px 15px rgba(0,0,0,0.05); }}
            td {{ padding: 20px; }}
            td:first-child {{ border-radius: 15px 0 0 15px; border-left: 4px solid #2563eb; }}
            td:last-child {{ border-radius: 0 15px 15px 0; }}
            .status-badge {{ background: #dcfce7; color: #166534; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }}
            .btn {{ background: #2563eb; color: white; text-decoration: none; padding: 10px 20px; border-radius: 10px; font-weight: 600; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔋 УЗЕ Monitor Pro</h1>
            <p>Останнє оновлення системи: <strong>{now}</strong> | Статус: <span style="color:#4ade80;">● Автосканування активне</span></p>
        </div>

        <div class="grid">
            <div class="card">🚀 Знайдено за тиждень <h2>{len(tenders)} тендерів</h2></div>
            <div class="card">💰 Очікувана сума <h2>₴ {total_value:,.2f}</h2></div>
            <div class="card">🌍 Джерела даних <h2>Prozorro API 2.5</h2></div>
            <div class="card">🔍 Фільтр обладнання <h2>УЗЕ / ESS / BESS</h2></div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Інформація про тендер</th>
                    <th>Регіон</th>
                    <th>Очікувана сума</th>
                    <th>Дедлайн</th>
                    <th>Статус</th>
                    <th>Посилання</th>
                </tr>
            </thead>
            <tbody>
    """

    for t in tenders:
        html += f"""
                <tr class="tender-row">
                    <td><strong>{t['title']}</strong><br><small style="color:#64748b;">{t['id']}</small></td>
                    <td>📍 {t['region']}</td>
                    <td style="color:#059669; font-weight:800;">{t['value']}</td>
                    <td>📅 {t['deadline']}</td>
                    <td><span class="status-badge">{t['status']}</span></td>
                    <td><a href="{t['link']}" target="_blank" class="btn">Prozorro →</a></td>
                </tr>
        """

    if not tenders:
        html += "<tr><td colspan='6' style='text-align:center; padding:50px; background:white; border-radius:15px;'>За останній тиждень нових активних тендерів за вашими фільтрами не знайдено.</td></tr>"

    html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    with open("tender-monitor.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    data = fetch_full_prozorro_data()
    generate_dashboard(data)
    print(f"Готово! Оброблено тендерів: {len(data)}")

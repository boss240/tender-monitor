import os
import requests
import json
from datetime import datetime, timedelta

# 1. Розширені фільтри для енергетики
KEYWORDS = ["узе", "ess", "bess", "інвертор", "акумулятор", "lifepo4", "deye", "must", "дбж", "ups", "victron"]

def fetch_full_prozorro_data():
    print("[Prozorro] Глибоке сканування API...")
    tenders_results = []
    
    # Шукаємо тендери за останні 7 днів
    start_date = (datetime.now() - timedelta(days=7)).isoformat()
    api_url = "https://public.api.openprocurement.org/api/2.5/tenders"
    
    try:
        response = requests.get(f"{api_url}?offset={start_date}&descending=1", timeout=15)
        if response.status_code != 200: return []
        
        items = response.json().get('data', [])
        
        for item in items[:150]:  # Перевіряємо останні 150 тендерів
            tender_id = item['id']
            # Заходимо в картку тендера
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
                
                tenders_results.append({
                    "title": data.get('title'),
                    "id": data.get('tenderID'),
                    "value": f"₴ {amount:,.2f} {currency}".replace(",", " "),
                    "amount_raw": amount,
                    "deadline": datetime.fromisoformat(data.get('tenderPeriod', {}).get('endDate', '').replace('Z', '+00:00')).strftime("%d.%m.%Y") if data.get('tenderPeriod') else "Не вказано",
                    "status": "Прийом пропозицій" if data.get('status') == 'active.tendering' else "Інший",
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
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #1e293b; padding: 20px; }}
            .header {{ background: #0f172a; color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
            .card {{ background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; }}
            .card h2 {{ color: #2563eb; margin: 10px 0 0 0; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
            th {{ background: #f1f5f9; color: #475569; font-weight: 600; }}
            .status-badge {{ background: #dcfce7; color: #166534; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }}
            .btn {{ background: #2563eb; color: white; text-decoration: none; padding: 8px 15px; border-radius: 8px; font-size: 14px; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔋 УЗЕ Monitor Pro</h1>
            <p>Останнє оновлення: <strong>{now}</strong> | Джерело: Prozorro API</p>
        </div>

        <div class="grid">
            <div class="card">Знайдено тендерів (7 днів) <h2>{len(tenders)}</h2></div>
            <div class="card">Загальна сума <h2>₴ {total_value / 1000000:,.1f} млн</h2></div>
            <div class="card">Статус системи <h2><span style="color: #10b981;">● Онлайн</span></h2></div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Назва / ID</th>
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
                <tr>
                    <td><strong>{t['title']}</strong><br><small style="color:#64748b;">{t['id']}</small></td>
                    <td>{t['region']}</td>
                    <td style="color:#059669; font-weight:bold;">{t['value']}</td>
                    <td>{t['deadline']}</td>
                    <td><span class="status-badge">{t['status']}</span></td>
                    <td><a href="{t['link']}" target="_blank" class="btn">Відкрити →</a></td>
                </tr>
        """

    if not tenders:
        html += "<tr><td colspan='6' style='text-align:center; padding:30px;'>За останні 7 днів нових тендерів не знайдено.</td></tr>"

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
    
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    generate_dashboard(data)
    print("Дашборд успішно оновлено реальними даними!")

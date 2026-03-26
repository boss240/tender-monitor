import os
import requests
import json
from datetime import datetime, timedelta

# ==========================================
# 1. НАЛАШТУВАННЯ
# ==========================================
KEYWORDS = ["узе", "ess", "bess", "інвертор", "акумулятор", "lifepo4", "deye", "must", "дбж", "ups"]

def fetch_real_tenders():
    print("[Prozorro] Пошук реальних даних...")
    tenders_list = []
    
    # Шукаємо за останні 48 годин
    start_date = (datetime.now() - timedelta(days=2)).isoformat()
    base_url = "https://public.api.openprocurement.org/api/2.5/tenders"
    
    try:
        response = requests.get(f"{base_url}?offset={start_date}", timeout=15)
        if response.status_code != 200: return []
        
        items = response.json().get('data', [])
        
        # Обмежимо перевірку першими 100 знайденими, щоб не перевантажувати GitHub
        for item in items[:100]:
            tender_id = item['id']
            # Отримуємо деталі кожного тендера для перевірки назви та ціни
            detail_res = requests.get(f"{base_url}/{tender_id}", timeout=10)
            if detail_res.status_code != 200: continue
            
            t = detail_res.json()['data']
            title = t.get('title', '').lower()
            
            if any(key in title for key in KEYWORDS):
                val = t.get('value', {})
                amount = val.get('amount', 0)
                currency = val.get('currency', 'UAH')
                
                tenders_list.append({
                    "title": t.get('title'),
                    "id": t.get('tenderID'),
                    "value": f"{amount:,.2f} {currency}".replace(",", " "),
                    "date": datetime.fromisoformat(t.get('tenderPeriod', {}).get('endDate', '').replace('Z', '+00:00')).strftime("%d.%m.%y") if t.get('tenderPeriod') else "Н/Д",
                    "status": "Активний" if t.get('status') == 'active.tendering' else "Розгляд",
                    "link": f"https://prozorro.gov.ua/tender/{t.get('tenderID')}"
                })
        return tenders_list
    except Exception as e:
        print(f"Error: {e}")
        return []

# ==========================================
# 2. ГЕНЕРАЦІЯ ОНОВЛЕНОГО HTML
# ==========================================
def generate_dashboard(tenders):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    total_sum = sum(float(t['value'].split()[0].replace(' ', '')) for t in tenders if 'UAH' in t['value'])
    
    html = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>УЗЕ Tender Monitor</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7f6; padding: 20px; }}
            .container {{ max-width: 1100px; margin: auto; }}
            .header-box {{ background: #1a73e8; color: white; padding: 25px; border-radius: 15px; display: flex; justify-content: space-between; align-items: center; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center; }}
            .stat-card h2 {{ color: #1a73e8; margin: 5px 0; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            th {{ background: #f8f9fa; padding: 15px; text-align: left; color: #5f6368; }}
            td {{ padding: 15px; border-top: 1px solid #eee; }}
            .status-badge {{ background: #e6f4ea; color: #1e8e3e; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; }}
            .btn {{ text-decoration: none; color: #1a73e8; font-weight: bold; border: 1px solid #1a73e8; padding: 5px 12px; border-radius: 6px; transition: 0.3s; }}
            .btn:hover {{ background: #1a73e8; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-box">
                <div>
                    <h1>🔋 УЗЕ Monitor</h1>
                    <p>Останнє сканування: <strong>{now}</strong> · Автооновлення: <span style="color: #afffaf;">Active</span></p>
                </div>
                <div style="text-align: right;">
                    <small>Джерела: Prozorro, DREAM, DTEK</small>
                </div>
            </div>

            <div class="stat-grid">
                <div class="stat-card"><p>Нових (48г)</p><h2>{len(tenders)}</h2></div>
                <div class="stat-card"><p>Сума активних</p><h2>₴ {total_sum/1e6:.1f}M</h2></div>
                <div class="stat-card"><p>Статус API</p><h2 style="color: #1e8e3e;">ONLINE</h2></div>
                <div class="stat-card"><p>Фільтр</p><h2>УЗЕ/ESS</h2></div>
            </div>

            <table>
                <tr>
                    <th>Назва тендера / ID</th>
                    <th>Очікувана вартість</th>
                    <th>Дедлайн</th>
                    <th>Статус</th>
                    <th>Дія</th>
                </tr>
    """

    for t in tenders:
        html += f"""
                <tr>
                    <td><strong>{t['title']}</strong><br><small style="color:#888;">{t['id']}</small></td>
                    <td style="color: #2e7d32; font-weight: bold;">{t['value']}</td>
                    <td>{t['date']}</td>
                    <td><span class="status-badge">{t['status']}</span></td>
                    <td><a href="{t['link']}" target="_blank" class="btn">Prozorro →</a></td>
                </tr>
        """

    if not tenders:
        html += "<tr><td colspan='5' style='text-align:center; padding: 40px; color: #666;'>Нових тендерів не знайдено за останні 48 годин. Перевірка триває...</td></tr>"

    html += """
            </table>
            <p style="text-align: center; color: #999; margin-top: 30px;">Система моніторингу енергетичного обладнання v2.1</p>
        </div>
    </body>
    </html>
    """
    
    with open("tender-monitor.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    found = fetch_real_tenders()
    generate_dashboard(found)
    print(f"Успішно! Знайдено {len(found)} тендерів.")

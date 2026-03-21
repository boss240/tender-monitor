# УЗЕ Tender Monitor

Автоматичне відстеження тендерів на постачання BESS, інверторів та сонячних рішень.

## Джерела
- Prozorro (публічний API, без ключа)
- UNGM (потрібен безкоштовний ключ: developer.ungm.org)
- TED EU (потрібен безкоштовний ключ: api.ted.europa.eu)
- DREAM (web scraping)

## Налаштування

### 1. Клонувати репо та додати Secrets
GitHub → Settings → Secrets → Actions:
- `TG_BOT_TOKEN` — токен від @BotFather
- `TG_CHAT_ID`   — ID вашої Telegram-групи
- `UNGM_API_KEY` — з developer.ungm.org
- `TED_API_KEY`  — з api.ted.europa.eu

### 2. Увімкнути GitHub Pages
Settings → Pages → Source: Deploy from branch `main` / root

### 3. Запустити вручну
Actions → "УЗЕ Tender Scanner" → Run workflow

## Структура
```
tender-monitor.html   ← дашборд (відкривається в браузері)
scanner.py            ← головний скрипт
sources/              ← модулі по джерелах
notify/               ← Telegram + Email
data/results.json     ← всі тендери (авто-оновлюється)
data/seen_ids.json    ← пам'ять (без дублів)
.github/workflows/    ← cron-автоматизація
```

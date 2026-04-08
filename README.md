# ⚡ УЗЕ Tender Monitor v2.0

Автоматичний моніторинг тендерів на постачання BESS, інверторів та комплектних рішень зберігання енергії в Україні.

## 📁 Структура проєкту

```
tender-monitor/
├── scanner.py                    ← Головний скрипт
├── test_api.py                   ← Тест з'єднання з API
├── run_scanner.bat               ← Запуск на Windows (подвійний клік)
├── uze_tender_dashboard.html     ← Інтерактивний дашборд
├── results.json                  ← Поточні тендери (генерується автоматично)
├── requirements.txt              ← Python-залежності
├── .env.example                  ← Шаблон конфігурації
├── sources/
│   ├── __init__.py
│   └── prozorro.py               ← Модуль Prozorro API
├── notify/
│   ├── __init__.py
│   ├── telegram.py               ← Telegram-сповіщення
│   └── email_sender.py           ← Email-дайджест
├── data/
│   └── seen_ids.json             ← Пам'ять (вже надіслані)
└── .github/workflows/
    └── tender-scan.yml           ← Автоматизація (07:00 / 12:00 / 18:00)
```

---

## 🚀 ПОКРОКОВА АКТИВАЦІЯ

### Крок 1: Встановлення (одноразово)

```bash
# Клонувати репо (або розпакувати архів)
cd tender-monitor

# Встановити Python-залежності
pip install -r requirements.txt
```

### Крок 2: Тест з'єднання з API

```bash
python test_api.py
```

Якщо бачите `✅ API доступний!` — все працює.

### Крок 3: Налаштування Telegram-бота

1. Написати [@BotFather](https://t.me/BotFather) → `/newbot` → отримати **Bot Token**
2. Створити групу в Telegram, додати бота
3. Написати будь-що в групу
4. Відкрити: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Знайти `chat.id` (починається з `-100`)
6. Створити файл `.env`:

```
TG_BOT_TOKEN=1234567890:ABCdef...
TG_CHAT_ID=-1001234567890
```

### Крок 4: Перший запуск

**Windows:**
```
Подвійний клік на run_scanner.bat
```

**Або в терміналі:**
```bash
# Завантажити .env
export $(cat .env | xargs)

# Запустити сканер
python scanner.py
```

Інтерактивне меню запитає, що робити з результатами.

### Крок 5: Відкрити дашборд

Подвійний клік на `uze_tender_dashboard.html` — відкриється в браузері з реальними даними.

### Крок 6: Автоматизація через GitHub Actions

1. Push проєкт на GitHub:
```bash
git init
git add .
git commit -m "Initial: УЗЕ Tender Monitor"
git remote add origin https://github.com/boss240/tender-monitor.git
git push -u origin main
```

2. Додати Secrets (Settings → Secrets → Actions):
   - `TG_BOT_TOKEN` — токен бота
   - `TG_CHAT_ID` — ID групи

3. Workflow автоматично запускатиметься о **07:00, 12:00, 18:00** за Києвом.

4. Ручний запуск: Actions → УЗЕ Tender Scanner → Run workflow.

### Крок 7 (опційно): GitHub Pages для дашборду

1. Settings → Pages → Source: main / root
2. Дашборд буде доступний за посиланням:
   `https://boss240.github.io/tender-monitor/uze_tender_dashboard.html`

---

## 📋 Команди scanner.py

```bash
python scanner.py                   # Стандартний скан (12 годин)
python scanner.py --hours 24        # За останні 24 години
python scanner.py --no-telegram     # Без Telegram
python scanner.py --digest-only     # Тільки зведений дайджест
python scanner.py --no-dashboard    # Без оновлення HTML
```

## 🔍 CPV-коди моніторингу

| Код | Назва |
|-----|-------|
| 31154000-0 | Джерела безперебійного живлення (ДБЖ) |
| 31155000-7 | Інвертори |
| 31440000-2 | Акумуляторні батареї / BESS |
| 31150000-2 | Баласти (ДБЖ + зарядні пристрої) |
| 09331200-0 | Сонячні фотоелектричні модулі |
| 09332000-5 | Сонячні установки |

## 📡 Джерела моніторингу

| Платформа | Метод | Частота |
|-----------|-------|---------|
| **Prozorro** | REST API (безкоштовний) | Кожні 6 годин |
| Prozorro Market | REST API | Кожні 6 годин |
| SmartTender | Web scraping | 1 раз/день |
| UNGM (UNDP, UNICEF) | UNGM API | 1 раз/день |
| TED EU (EIB, WB) | TED API v3 | 1 раз/день |
| НЕФКО | Web scraping | 1 раз/день |
| ДТЕК / SAP Ariba | Manual alerts | За потребою |

---

*Phage Energy / ТОВ «БАЛАНСЕНЕРГО» — 2026*

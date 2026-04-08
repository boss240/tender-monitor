"""
Telegram Bot -- сповiщення про новi тендери УЗЕ
Використовує requests замiсть python-telegram-bot для простоти.
"""

import os
import time
import requests

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TG_CHAT_ID", "")

TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(text: str, parse_mode: str = "Markdown") -> bool:
    """Надсилає одне повiдомлення в Telegram."""
    if not BOT_TOKEN or not CHAT_ID:
        print("[Telegram] BOT_TOKEN або CHAT_ID не налаштовано!")
        return False

    try:
        resp = requests.post(
            f"{TG_API}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
        if resp.status_code == 200:
            return True
        else:
            print(f"[Telegram] Помилка: {resp.status_code} -- {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"[Telegram] Exception: {e}")
        return False


def send_tenders(tenders: list, formatter=None) -> int:
    """
    Надсилає список тендерiв у Telegram.
    formatter -- функцiя (tender) -> str для форматування.
    Повертає кiлькiсть успiшно надiсланих.
    """
    if not tenders:
        print("[Telegram] Немає тендерiв для надсилання.")
        return 0

    if formatter is None:
        from sources.prozorro import to_telegram_message
        formatter = to_telegram_message

    sent = 0

    # Зведка
    summary = (
        "\U0001f4ca *УЗЕ Tender Monitor*\n\n"
        f"\U0001f514 Нових тендерiв: *{len(tenders)}*\n"
        f"\u23f0 {time.strftime('%d.%m.%Y %H:%M')}\n"
        f"{'---' * 8}"
    )
    send_message(summary)
    time.sleep(0.5)

    for t in tenders:
        msg = formatter(t)
        if send_message(msg):
            sent += 1
        time.sleep(0.5)

    print(f"[Telegram] Надiслано: {sent}/{len(tenders)}")
    return sent


def send_digest(tenders: list) -> bool:
    """Надсилає короткий дайджест."""
    if not tenders:
        return False

    urgent = [t for t in tenders if t.get("status") == "urgent"]
    bess = [t for t in tenders if t.get("type") == "BESS"]
    inv = [t for t in tenders if t.get("type") == "Inverter"]
    solar = [t for t in tenders if t.get("type") == "Solar"]
    total_amount = sum(t.get("amount", 0) for t in tenders)

    amount_str = f"UAH {total_amount/1e6:.1f}M" if total_amount > 1e6 else f"UAH {total_amount:,.0f}"

    msg = (
        f"\U0001f4ca *Дайджест тендерiв УЗЕ*\n"
        f"\U0001f4c5 {time.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"\U0001f514 Всього: *{len(tenders)}*\n"
        f"\U0001f534 Термiново (<=3 дн.): *{len(urgent)}*\n"
        f"\U0001f50b BESS: {len(bess)} | \u26a1 Iнвертори: {len(inv)} | \u2600\ufe0f Solar: {len(solar)}\n"
        f"\U0001f4b0 Загальна сума: {amount_str}\n\n"
    )

    top5 = sorted(tenders, key=lambda x: x.get("score", 0), reverse=True)[:5]
    msg += "*Топ-5 за релевантнiстю:*\n"
    for i, t in enumerate(top5, 1):
        dl = t.get("deadline", "---")
        msg += f"{i}. `{t.get('score',0)}` {t['title'][:60]}... ({dl})\n"

    return send_message(msg)

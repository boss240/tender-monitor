"""
Email дайджест — щоденна розсилка тендерів УЗЕ
Потребує SMTP-налаштування через змінні середовища.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", SMTP_USER)
EMAIL_TO = os.environ.get("EMAIL_TO", "").split(",")  # comma-separated


def send_digest(tenders: list) -> bool:
    """Надсилає HTML-дайджест на email."""
    if not SMTP_USER or not SMTP_PASS or not any(EMAIL_TO):
        print("[Email] SMTP не налаштовано, пропускаю.")
        return False

    if not tenders:
        print("[Email] Немає тендерів для дайджесту.")
        return False

    html = _build_html(tenders)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[УЗЕ Monitor] {len(tenders)} нових тендерів — {datetime.now().strftime('%d.%m.%Y')}"
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as srv:
            srv.login(SMTP_USER, SMTP_PASS)
            srv.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f"[Email] Дайджест надіслано на {len(EMAIL_TO)} адрес(и).")
        return True
    except Exception as e:
        print(f"[Email] Помилка: {e}")
        return False


def _build_html(tenders: list) -> str:
    rows = ""
    for t in sorted(tenders, key=lambda x: x.get("score", 0), reverse=True):
        status_color = "#ef4444" if t.get("status") == "urgent" else "#10b981" if t.get("status") == "new" else "#64748b"
        status_label = "Терміново" if t.get("status") == "urgent" else "Новий" if t.get("status") == "new" else "Активний"
        amount = f"₴{t['amount']:,.0f}" if t.get("amount") else "—"
        rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #e2e8f0">
                <span style="background:{status_color};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px">{status_label}</span>
            </td>
            <td style="padding:8px;border-bottom:1px solid #e2e8f0">
                <a href="{t.get('url','#')}" style="color:#2563eb;text-decoration:none;font-weight:600">{t['title'][:80]}</a>
                <br><span style="color:#94a3b8;font-size:11px">{t.get('id','')}</span>
            </td>
            <td style="padding:8px;border-bottom:1px solid #e2e8f0;font-family:monospace;font-size:12px">{', '.join(t.get('cpvs',[])[:2])}</td>
            <td style="padding:8px;border-bottom:1px solid #e2e8f0;font-weight:600;white-space:nowrap">{amount}</td>
            <td style="padding:8px;border-bottom:1px solid #e2e8f0;white-space:nowrap">{t.get('deadline','—')}</td>
            <td style="padding:8px;border-bottom:1px solid #e2e8f0;text-align:center;font-weight:700">{t.get('score',0)}</td>
        </tr>"""

    return f"""
    <div style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;padding:20px">
        <h2 style="color:#1e293b;border-bottom:2px solid #00d4ff;padding-bottom:8px">
            ⚡ УЗЕ Tender Monitor — Дайджест
        </h2>
        <p style="color:#64748b;font-size:14px">
            {datetime.now().strftime('%d.%m.%Y %H:%M')} | Знайдено тендерів: <strong>{len(tenders)}</strong>
        </p>
        <table style="width:100%;border-collapse:collapse;font-size:13px">
            <thead>
                <tr style="background:#f1f5f9">
                    <th style="padding:8px;text-align:left;font-size:11px;color:#64748b">Статус</th>
                    <th style="padding:8px;text-align:left;font-size:11px;color:#64748b">Назва</th>
                    <th style="padding:8px;text-align:left;font-size:11px;color:#64748b">CPV</th>
                    <th style="padding:8px;text-align:left;font-size:11px;color:#64748b">Сума</th>
                    <th style="padding:8px;text-align:left;font-size:11px;color:#64748b">Дедлайн</th>
                    <th style="padding:8px;text-align:center;font-size:11px;color:#64748b">Score</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <p style="color:#94a3b8;font-size:11px;margin-top:16px">
            Phage Energy / БАЛАНСЕНЕРГО — УЗЕ Tender Monitor v2.0
        </p>
    </div>"""

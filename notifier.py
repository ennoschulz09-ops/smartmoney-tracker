"""
Sendet Alerts ueber Telegram, wenn ein Coin ein starkes Signal erreicht.
"""

import os
import requests


def send_telegram_alert(signal: dict):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print(f"[Alert, kein Telegram konfiguriert] {signal}")
        return

    text = (
        f"🚨 Smart-Money-Signal: {signal['token']}\n"
        f"Wallets: {signal['wallet_count']}\n"
        f"Kapital: ${signal['total_usd']:,.0f}\n"
        f"Score: {signal['score']:.1f}"
    )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=10)

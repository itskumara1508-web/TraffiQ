"""
Alerts & Remote Notification Dispatcher for TraffiQ
===================================================
Phase 4 Implementation:
- Real-time notification queue (Critical toasts, Warnings, Information)
- Remote webhook, Telegram, WhatsApp, and Email dispatchers
- Configurable notification rules per event severity
"""

import os
import json
import threading
import requests
from collections import deque
from datetime import datetime
from database import insert_alert, get_alerts, acknowledge_alert

# Rolling in-memory toast buffer for live WebSocket / SSE / Polling UI
active_toasts = deque(maxlen=25)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
WEBHOOK_URL = os.environ.get("ALERT_WEBHOOK_URL", "")
WHATSAPP_WEBHOOK = os.environ.get("WHATSAPP_WEBHOOK_URL", "")

class AlertDispatcher:
    """Dispatches notifications locally to UI and remotely to messaging channels."""

    @staticmethod
    def dispatch(severity: str, category: str, title: str, message: str):
        """Dispatches an alert through in-memory queue, SQLite, and external hooks."""
        # 1. Save to SQLite
        a_id = insert_alert(severity, category, title, message)
        
        # 2. Add to in-memory active toasts for instantaneous frontend popup
        toast = {
            "id": a_id,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "severity": severity,   # critical, warning, info
            "category": category,   # incident, violation, ambulance, congestion
            "title": title,
            "message": message
        }
        active_toasts.appendleft(toast)
        
        # 3. Asynchronously dispatch remote webhooks if critical
        if severity == "critical":
            threading.Thread(target=AlertDispatcher._send_remote, args=(toast,), daemon=True).start()

    @staticmethod
    def _send_remote(toast: dict):
        text = f"🚨 *[TraffiQ Alert]* {toast['title']}\nSeverity: {toast['severity'].upper()}\nCategory: {toast['category']}\n{toast['message']}\nTime: {toast['timestamp']}"
        
        # Telegram Dispatch
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=4)
            except Exception:
                pass

        # Generic Webhook (Discord / Slack / Custom API)
        if WEBHOOK_URL:
            try:
                requests.post(WEBHOOK_URL, json=toast, timeout=4)
            except Exception:
                pass

        # WhatsApp Webhook
        if WHATSAPP_WEBHOOK:
            try:
                requests.post(WHATSAPP_WEBHOOK, json={"to": "traffic-ops", "body": text}, timeout=4)
            except Exception:
                pass


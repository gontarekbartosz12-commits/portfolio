"""Świstak Telegram sender — chunked for Telegram's 4096-char limit.

Świstak is the Telegram bot that is the unified human-facing channel for all my
autonomous agents (trends scout, trading bots, monitors). Secrets via env only.
"""
import os
import requests
import time

from config import TG_PREFIX


def send(text: str, urgent: bool = False) -> bool:
    token = os.getenv("TG_BOT_TOKEN", "")
    chat = os.getenv("TG_CHAT_ID", "")
    if not token or not chat:
        print("[notify] missing TG_BOT_TOKEN/TG_CHAT_ID")
        return False

    prefix = f"🚨 {TG_PREFIX}\n" if urgent else f"{TG_PREFIX}\n"
    body = (prefix + text).strip()
    # Telegram caps messages at 4096 chars — split into safe chunks.
    chunks = [body[i:i + 3900] for i in range(0, len(body), 3900)]

    ok = True
    for i, chunk in enumerate(chunks):
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": chat,
                    "text": chunk if i == 0 else f"{TG_PREFIX} (cont.)\n{chunk}",
                    "disable_web_page_preview": True,
                },
                timeout=20,
            )
            if not r.ok:
                print(f"[notify] chunk {i} failed: {r.status_code} {r.text[:200]}")
                ok = False
            time.sleep(0.5)
        except Exception as e:
            print(f"[notify] chunk {i} exc: {e}")
            ok = False
    return ok

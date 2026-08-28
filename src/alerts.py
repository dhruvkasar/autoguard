import os
import time
import requests
from typing import List


class TelegramAlerter:
    def __init__(self, enabled: bool, token: str, chat_ids: List[str], camera_id: str, logger):
        self.enabled = enabled and bool(token) and bool(chat_ids)
        self.token = token
        self.chat_ids = chat_ids
        self.camera_id = camera_id
        self.logger = logger
        if enabled and (not token or not chat_ids):
            self.logger.warning("Telegram alerting enabled but token/chat_ids not configured; alerts will be skipped.")

    def send_photo(self, image_path: str, caption: str):
        if not self.enabled:
            self.logger.info("Alerting disabled or not configured; skipping Telegram send.")
            return
        url_base = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        for chat_id in self.chat_ids:
            backoff = 1.0
            attempts = 0
            while attempts < 3:
                attempts += 1
                try:
                    with open(image_path, "rb") as img:
                        files = {"photo": img}
                        data = {"chat_id": chat_id, "caption": caption}
                        r = requests.post(url_base, files=files, data=data, timeout=15)
                    if r.status_code == 200:
                        self.logger.info(f"Alert sent to chat_id={chat_id} for {image_path}")
                        break
                    else:
                        self.logger.error(f"Telegram send failed ({r.status_code}): {r.text}")
                except Exception as e:
                    self.logger.error(f"Telegram send error for chat_id={chat_id}: {e}")
                if attempts < 3:
                    time.sleep(backoff)
                    backoff *= 2

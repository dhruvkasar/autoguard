import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import yaml


def load_config() -> Dict[str, Any]:
    """Load YAML config and environment variables."""
    load_dotenv()  # loads .env if present
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml"), "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Env secrets and runtime overrides
    cfg.setdefault("alerts", {})
    cfg["alerts"]["token"] = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_ids = os.getenv("TELEGRAM_CHAT_IDS", "").strip()
    cfg["alerts"]["chat_ids"] = [s.strip() for s in chat_ids.split(",") if s.strip()] if chat_ids else []
    cfg["alerts"]["camera_id"] = os.getenv("CAMERA_ID", "CAM01")

    return cfg

import json
from pathlib import Path
from typing import Dict, Any, Optional
from bot.config import DATA_DIR

STORE_FILE = DATA_DIR / "funpay_boost.json"

DEFAULT_USER = {
    "interval_hours": 4,
    "active": False,
    "last_boost_at": None,
    "last_reminder_message_id": None,
    "next_override_at": None,
}


def _load() -> Dict[str, Any]:
    if not STORE_FILE.exists():
        return {"users": {}}
    try:
        with STORE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}}


def _save(data: Dict[str, Any]) -> None:
    STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STORE_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(chat_id: int) -> Dict[str, Any]:
    data = _load()
    u = data["users"].get(str(chat_id))
    if not u:
        u = DEFAULT_USER.copy()
        data["users"][str(chat_id)] = u
        _save(data)
    return u


def update_user(chat_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
    data = _load()
    u = data["users"].get(str(chat_id), DEFAULT_USER.copy())
    u.update(patch)
    data["users"][str(chat_id)] = u
    _save(data)
    return u


def set_next_override_at(chat_id: int, iso: Optional[str]) -> None:
    """تنظیم/حذف زمان Override برای یادآور بعدی (ISO یا None)."""
    update_user(chat_id, {"next_override_at": iso})

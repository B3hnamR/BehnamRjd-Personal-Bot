from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo
from persiantools.jdatetime import JalaliDateTime

TEHRAN_TZ = ZoneInfo("Asia/Tehran")


def to_shamsi_text(iso_str: Optional[str]) -> str:
    """تبدیل رشته ISO (UTC) به نمایش تاریخ/زمان شمسی در منطقه زمانی تهران.
    اگر مقدار نامعتبر باشد، همان مقدار اولیه برگردانده می‌شود.
    خروجی به‌صورت YYYY/MM/DD HH:MM است.
    """
    if not iso_str:
        return "—"
    try:
        dt_utc = datetime.fromisoformat(iso_str)
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        dt_local = dt_utc.astimezone(TEHRAN_TZ)
        jdt = JalaliDateTime.fromgregorian(datetime=dt_local)
        return jdt.strftime("%Y/%m/%d %H:%M")
    except Exception:
        return iso_str

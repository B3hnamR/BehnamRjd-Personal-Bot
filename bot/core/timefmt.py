from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Union
from zoneinfo import ZoneInfo
from persiantools.jdatetime import JalaliDateTime
from persiantools import digits

TEHRAN_TZ = ZoneInfo("Asia/Tehran")


def to_fa_digits(value: Union[str, int, float]) -> str:
    try:
        return digits.en_to_fa(str(value))
    except Exception:
        return str(value)


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
        dt_local_naive = dt_local.replace(tzinfo=None)
        jdt = JalaliDateTime.fromgregorian(datetime=dt_local_naive)
        return digits.en_to_fa(jdt.strftime("%Y/%m/%d %H:%M"))
    except Exception:
        return iso_str

from pathlib import Path
import os
from dotenv import load_dotenv

# بارگذاری .env (اختیاری)
load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN در .env یا محیط تنظیم نشده است.")

OWNER_USER_ID_STR = os.getenv("OWNER_USER_ID")
if not OWNER_USER_ID_STR:
    raise RuntimeError("OWNER_USER_ID در .env یا محیط تنظیم نشده است.")
try:
    OWNER_USER_ID = int(OWNER_USER_ID_STR)
except ValueError:
    raise RuntimeError("OWNER_USER_ID باید یک عدد صحیح باشد.")

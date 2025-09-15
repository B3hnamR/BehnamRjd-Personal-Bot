# Personal Telegram Bot

## Setup (Local)
1. Python 3.10+ نصب کنید.
2. یک فایل `.env` کنار این فایل بسازید و مقدار `TELEGRAM_BOT_TOKEN` را قرار دهید (مطابق `.env.example`).
3. نصب وابستگی‌ها:

```bash
pip install -r requirements.txt
```

## Run (Local)

```bash
python -m bot.app
```

## Docker

### Build & Run با Docker Compose
1. یک فایل `.env` کنار `docker-compose.yml` بسازید و مقادیر زیر را قرار دهید:

```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
OWNER_USER_ID=123456789
```

2. اجرای کانتینر:

```bash
docker compose up -d --build
```

3. مشاهده لاگ‌ها:

```bash
docker compose logs -f
```

- Volume `./data:/app/data` برای پایداری فایل‌های ذخیره‌سازی استفاده می‌شود.

## Features
- FunPay Boost Reminder:
  - منوی اصلی با دکمه "FunPay Boost Reminder"
  - Start/Stop/Status/Set Interval
  - پیام یادآور با دکمه "Boost زدم" برای ریست تایمر
  - داده‌ها در `data/funpay_boost.json` ذخیره می‌شود

# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Tehran

WORKDIR /app

# داشتن tzdata برای تایم‌زون
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

# وابستگی‌ها
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# کد برنامه
COPY bot ./bot
COPY README.md ./

# اجرای ربات
CMD ["python", "-m", "bot.app"]

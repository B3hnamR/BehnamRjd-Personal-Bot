from functools import wraps
from typing import Callable, Awaitable
from datetime import datetime, timezone
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from bot.config import OWNER_USER_ID


def _describe_attempt(update: Update) -> str:
    if update.callback_query:
        data = update.callback_query.data
        return f"callback: {data}"
    if update.message:
        if update.message.text:
            return f"message: {update.message.text}"
        if update.message.caption:
            return f"message(caption): {update.message.caption}"
        return "message: (non-text)"
    return "unknown"


async def _notify_owner(context: ContextTypes.DEFAULT_TYPE, update: Update) -> None:
    user = update.effective_user
    chat = update.effective_chat
    attempted = _describe_attempt(update)
    uid = user.id if user else None
    uname = f"@{user.username}" if user and user.username else "-"
    full_name = f"{(user.first_name or '')} {(user.last_name or '')}".strip() if user else "-"
    chat_id = chat.id if chat else "-"
    ts = datetime.now(timezone.utc).isoformat()
    text = (
        "\U0001F6AB Unauthorized access attempt\n"
        f"- User ID: {uid}\n"
        f"- Username: {uname}\n"
        f"- Name: {full_name}\n"
        f"- Chat ID: {chat_id}\n"
        f"- Attempt: {attempted}\n"
        f"- At (UTC): {ts}"
    )
    try:
        await context.bot.send_message(chat_id=OWNER_USER_ID, text=text)
    except Exception:
        # در صورت عدم امکان ارسال پیام (مثلاً هنوز چت با مالک ایجاد نشده)، صرف‌نظر کن
        pass


def owner_only(handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable]):
    @wraps(handler)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id if update.effective_user else None
        if user_id != OWNER_USER_ID:
            # اطلاع به مالک
            await _notify_owner(context, update)
            # اطلاع به کاربر غیرمجاز و حذف کیبوردهای پاسخ‌گو
            if update.callback_query:
                try:
                    await update.callback_query.answer(
                        "You are not authorized to use this bot.", show_alert=True
                    )
                except Exception:
                    pass
            else:
                if update.message:
                    try:
                        await update.message.reply_text(
                            "شما دسترسی ندارید.",
                            reply_markup=ReplyKeyboardRemove(),
                        )
                    except Exception:
                        pass
            return
        return await handler(update, context)

    return wrapper

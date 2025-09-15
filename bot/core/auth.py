from functools import wraps
from typing import Callable, Awaitable
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import OWNER_USER_ID

# دکوریتور محدودکننده دسترسی فقط برای مالک

def owner_only(handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable]):
    @wraps(handler)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id if update.effective_user else None
        if user_id != OWNER_USER_ID:
            # اگر /start باشد پیام متنی بده، اگر callback باشد به صورت alert پاسخ بده
            if update.callback_query:
                await update.callback_query.answer("You are not authorized to use this bot.", show_alert=True)
                # اگر پیام دگمه‌ای وجود دارد تغییری ایجاد نمی‌کنیم
            else:
                if update.message:
                    await update.message.reply_text("شما دسترسی ندارید.")
            return
        return await handler(update, context)

    return wrapper

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from bot.core.auth import owner_only

MAIN_MENU_BUTTON = "FunPay Boost Reminder"


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(MAIN_MENU_BUTTON)]],
        resize_keyboard=True,
    )


@owner_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من ربات شخصی شما هستم.",
        reply_markup=get_main_keyboard(),
    )

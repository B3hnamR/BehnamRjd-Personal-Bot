import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.config import TELEGRAM_BOT_TOKEN
from bot.core.start import start, MAIN_MENU_BUTTON
from bot.features.funpay_boost.handlers import (
    open_funpay_menu,
    register_funpay_handlers,
)


def build_application() -> Application:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    # /start
    app.add_handler(CommandHandler("start", start))
    # متن کیبورد اصلی => منوی FunPay
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{MAIN_MENU_BUTTON}$"), open_funpay_menu))

    # هندلرهای فیچر FunPay Boost
    register_funpay_handlers(app)
    return app


def main():
    logging.basicConfig(level=logging.INFO)
    app = build_application()
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()

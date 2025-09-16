from telegram import InlineKeyboardMarkup, InlineKeyboardButton

PLATI_MENU = "PLATI_MENU"
PLATI_START = "PLATI_START"
PLATI_BACK = "PLATI_BACK"


def plati_menu_kb():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Start Finder", callback_data=PLATI_START)],
            [InlineKeyboardButton("بازگشت", callback_data=PLATI_BACK)],
        ]
    )

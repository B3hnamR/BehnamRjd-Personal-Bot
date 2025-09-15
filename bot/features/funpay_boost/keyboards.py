from telegram import InlineKeyboardMarkup, InlineKeyboardButton

FUNPAY_MENU = "FUNPAY_MENU"
FUNPAY_START = "FUNPAY_START"
FUNPAY_STOP = "FUNPAY_STOP"
FUNPAY_STATUS = "FUNPAY_STATUS"
FUNPAY_SET_INTERVAL_PREFIX = "FUNPAY_SET_INTERVAL_"
FUNPAY_BOOST_DONE = "FUNPAY_BOOST_DONE"


def funpay_menu_kb():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Start", callback_data=FUNPAY_START),
                InlineKeyboardButton("Stop", callback_data=FUNPAY_STOP),
            ],
            [
                InlineKeyboardButton(
                    "Set Interval", callback_data=f"{FUNPAY_SET_INTERVAL_PREFIX}OPEN"
                ),
                InlineKeyboardButton("Status", callback_data=FUNPAY_STATUS),
            ],
        ]
    )


def funpay_interval_options_kb():
    options = [1, 2, 3, 4, 6]
    rows = [
        [InlineKeyboardButton(f"{h}h", callback_data=f"{FUNPAY_SET_INTERVAL_PREFIX}{h}")]
        for h in options
    ]
    rows.append([InlineKeyboardButton("بازگشت", callback_data=FUNPAY_MENU)])
    return InlineKeyboardMarkup(rows)


def reminder_kb():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Boost زدم", callback_data=FUNPAY_BOOST_DONE)]]
    )

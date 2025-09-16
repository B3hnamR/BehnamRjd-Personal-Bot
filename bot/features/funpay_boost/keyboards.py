from telegram import InlineKeyboardMarkup, InlineKeyboardButton

FUNPAY_MENU = "FUNPAY_MENU"
FUNPAY_START = "FUNPAY_START"
FUNPAY_STOP = "FUNPAY_STOP"
FUNPAY_STATUS = "FUNPAY_STATUS"
FUNPAY_SET_INTERVAL_PREFIX = "FUNPAY_SET_INTERVAL_"
FUNPAY_BOOST_DONE = "FUNPAY_BOOST_DONE"
FUNPAY_SET_NEXT_OPEN = "FUNPAY_SET_NEXT_OPEN"
FUNPAY_SET_NEXT_PRESET_PREFIX = "FUNPAY_SET_NEXT_PRESET_"
FUNPAY_SET_NEXT_BY_TIME = "FUNPAY_SET_NEXT_BY_TIME"


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
            [
                InlineKeyboardButton("Set Next Reminder", callback_data=FUNPAY_SET_NEXT_OPEN),
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


def funpay_set_next_menu_kb():
    rows = [
        [InlineKeyboardButton("15m", callback_data=f"{FUNPAY_SET_NEXT_PRESET_PREFIX}15"),
         InlineKeyboardButton("30m", callback_data=f"{FUNPAY_SET_NEXT_PRESET_PREFIX}30")],
        [InlineKeyboardButton("45m", callback_data=f"{FUNPAY_SET_NEXT_PRESET_PREFIX}45"),
         InlineKeyboardButton("60m", callback_data=f"{FUNPAY_SET_NEXT_PRESET_PREFIX}60")],
        [InlineKeyboardButton("تنظیم با ساعت (HH:MM)", callback_data=FUNPAY_SET_NEXT_BY_TIME)],
        [InlineKeyboardButton("بازگشت", callback_data=FUNPAY_MENU)],
    ]
    return InlineKeyboardMarkup(rows)

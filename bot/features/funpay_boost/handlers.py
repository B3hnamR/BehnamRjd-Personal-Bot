from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import Application, ContextTypes, CallbackQueryHandler
from bot.core.auth import owner_only

from .keyboards import (
    FUNPAY_MENU,
    FUNPAY_START,
    FUNPAY_STOP,
    FUNPAY_STATUS,
    FUNPAY_SET_INTERVAL_PREFIX,
    FUNPAY_BOOST_DONE,
    funpay_menu_kb,
    funpay_interval_options_kb,
    reminder_kb,
)
from .storage import get_user, update_user

JOB_NAME_FMT = "funpay_boost_{chat_id}"


def _job_name(chat_id: int) -> str:
    return JOB_NAME_FMT.format(chat_id=chat_id)


def _find_job(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    name = _job_name(chat_id)
    jobs = context.job_queue.get_jobs_by_name(name)
    return jobs[0] if jobs else None


async def _schedule_next_reminder(
    context: ContextTypes.DEFAULT_TYPE, chat_id: int, after_hours: int
):
    job = _find_job(context, chat_id)
    if job:
        job.schedule_removal()
    when = timedelta(hours=after_hours)
    context.job_queue.run_once(
        funpay_reminder_job, when=when, chat_id=chat_id, name=_job_name(chat_id)
    )


async def funpay_reminder_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id  # type: ignore[attr-defined]
    user = get_user(chat_id)
    text = (
        "یادآور FunPay Boost\n"
        f"فاصله فعلی: {user.get('interval_hours', 4)} ساعت\n\n"
        "لطفاً در سایت FunPay دکمه Boost را بزنید و سپس پایین روی «Boost زدم» کلیک کنید تا تایمر ریست شود."
    )
    msg = await context.bot.send_message(
        chat_id=chat_id, text=text, reply_markup=reminder_kb()
    )
    update_user(chat_id, {"last_reminder_message_id": msg.message_id})


@owner_only
async def open_funpay_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    text = (
        "FunPay Boost Reminder\n"
        f"- وضعیت: {'فعال' if user.get('active') else 'غیرفعال'}\n"
        f"- فاصله: {user.get('interval_hours', 4)} ساعت\n"
        f"- آخرین بوست: {user.get('last_boost_at') or 'نامشخص'}"
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=text, reply_markup=funpay_menu_kb()
        )
    else:
        await update.message.reply_text(text=text, reply_markup=funpay_menu_kb())


@owner_only
async def on_start_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    chat_id = update.effective_chat.id
    now_iso = datetime.now(timezone.utc).isoformat()
    user = update_user(chat_id, {"active": True, "last_boost_at": now_iso})
    await _schedule_next_reminder(context, chat_id, user["interval_hours"])
    await update.callback_query.edit_message_text(
        f"یادآور فعال شد. اولین یادآور پس از {user['interval_hours']} ساعت ارسال می‌شود.",
        reply_markup=funpay_menu_kb(),
    )


@owner_only
async def on_stop_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    chat_id = update.effective_chat.id
    job = _find_job(context, chat_id)
    if job:
        job.schedule_removal()
    update_user(chat_id, {"active": False})
    await update.callback_query.edit_message_text(
        "یادآور غیرفعال شد.", reply_markup=funpay_menu_kb()
    )


@owner_only
async def on_status_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await open_funpay_menu(update, context)


@owner_only
async def on_set_interval_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "فاصله بوست را انتخاب کنید:", reply_markup=funpay_interval_options_kb()
    )


@owner_only
async def on_set_interval_value(
    update: Update, context: ContextTypes.DEFAULT_TYPE, hours: int
):
    await update.callback_query.answer()
    chat_id = update.effective_chat.id
    user = update_user(chat_id, {"interval_hours": hours})
    if user.get("active"):
        await _schedule_next_reminder(context, chat_id, hours)
    await update.callback_query.edit_message_text(
        f"فاصله روی {hours} ساعت تنظیم شد.", reply_markup=funpay_menu_kb()
    )


@owner_only
async def on_boost_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("ثبت شد. تایمر از حالا ریست می‌شود.")
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    now_iso = datetime.now(timezone.utc).isoformat()
    update_user(chat_id, {"last_boost_at": now_iso})
    await _schedule_next_reminder(context, chat_id, user["interval_hours"])
    try:
        if user.get("last_reminder_message_id"):
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=user["last_reminder_message_id"],
                text="✅ Boost ثبت شد. یادآور بعدی زمان‌بندی شد.",
            )
    except Exception:
        pass


def register_funpay_handlers(app: Application):
    app.add_handler(CallbackQueryHandler(open_funpay_menu, pattern=f"^{FUNPAY_MENU}$"))
    app.add_handler(CallbackQueryHandler(on_start_cb, pattern=f"^{FUNPAY_START}$"))
    app.add_handler(CallbackQueryHandler(on_stop_cb, pattern=f"^{FUNPAY_STOP}$"))
    app.add_handler(CallbackQueryHandler(on_status_cb, pattern=f"^{FUNPAY_STATUS}$"))
    app.add_handler(CallbackQueryHandler(on_boost_done, pattern=f"^{FUNPAY_BOOST_DONE}$"))
    app.add_handler(
        CallbackQueryHandler(on_set_interval_open, pattern=f"^{FUNPAY_SET_INTERVAL_PREFIX}OPEN$")
    )
    for h in [1, 2, 3, 4, 6]:
        app.add_handler(
            CallbackQueryHandler(
                lambda u, c, hh=h: on_set_interval_value(u, c, hh),
                pattern=f"^{FUNPAY_SET_INTERVAL_PREFIX}{h}$",
            )
        )

from telegram import Update, ForceReply
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from bot.core.auth import owner_only
from .keyboards import PLATI_MENU, PLATI_START, PLATI_BACK, plati_menu_kb
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


PLATI_MAIN_BUTTON = "Plati Product Finder"

ASK_URL = "لینک صفحه Plati را ارسال کنید (مثلاً https://plati.io/cat/fixed-nominal/11355/?sort=price_asc):"
ASK_QUERY = "عبارت جستجو در عنوان محصول را ارسال کنید:" 


@owner_only
async def on_plati_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # بازگشت به منوی اصلی با ارسال پیام جدید
    from bot.core.start import get_main_keyboard
    await update.callback_query.edit_message_text("بازگشت.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="منوی اصلی", reply_markup=get_main_keyboard()) 


@owner_only
async def open_plati_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plati_state"] = None
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Plati Product Finder", reply_markup=plati_menu_kb())
    else:
        await update.message.reply_text("Plati Product Finder", reply_markup=plati_menu_kb())


@owner_only
async def on_plati_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    context.user_data["plati_state"] = "await_url"
    await update.callback_query.message.reply_text(ASK_URL, reply_markup=ForceReply(selective=True))


async def _fetch_all_items(session: httpx.AsyncClient, start_url: str) -> list[tuple[str, str]]:
    """
    تلاش ساده: صفحات plati دارای بارگذاری lazy هستند؛ HTML اولیه ممکن است لیست را کامل ندهد.
    رویکرد: صفحه را واکشی می‌کنیم و لینک‌های آیتم‌ها را از بلوک‌های پیشنهاد/لیست استخراج می‌کنیم.
    توجه: اگر هیچ محصولی داده نشد، فعلاً همان صفحه را پارس می‌کنیم (بهبود آینده: استفاده از API رسمی category list اگر موجود باشد).
    خروجی: لیست (title, url)
    """
    items: list[tuple[str, str]] = []
    resp = await session.get(start_url, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # کارت‌ها دارای لینک‌های /itm/... هستند
    for a in soup.select('a[href^="/itm/"]'):
        href = a.get("href")
        title = (a.get("title") or a.get_text(" ").strip())
        if not href or not title:
            continue
        full = urljoin(start_url, href)
        items.append((title, full))
    # حذف تکراری‌ها با حفظ ترتیب
    seen = set()
    uniq: list[tuple[str, str]] = []
    for t, u in items:
        if u in seen:
            continue
        seen.add(u)
        uniq.append((t, u))
    return uniq


@owner_only
async def on_receive_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("plati_state") != "await_url":
        return
    url = (update.message.text or "").strip()
    context.user_data["plati_url"] = url
    context.user_data["plati_state"] = "await_query"
    await update.message.reply_text(ASK_QUERY, reply_markup=ForceReply(selective=True))


@owner_only
async def on_receive_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("plati_state") != "await_query":
        return
    query = (update.message.text or "").strip()
    context.user_data["plati_state"] = None
    url = context.user_data.get("plati_url")
    if not url:
        await update.message.reply_text("ابتدا لینک صفحه را ارسال کنید.")
        return
    await update.message.reply_text("در حال جستجو... ممکن است کمی زمان ببرد.")

    results: list[tuple[str, str]] = []
    # واکشی ��اده: یک صفحه. (در آینده می‌توان توسعه داد)
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
        try:
            items = await _fetch_all_items(client, url)
            q = query.lower()
            for title, link in items:
                if q in title.lower():
                    results.append((title, link))
        except Exception as e:
            await update.message.reply_text(f"خطا در واکشی: {e}")
            return

    if not results:
        await update.message.reply_text("چیزی مطابق جستجو یافت نشد.")
        return

    # ارسال لینک‌ها
    lines = [f"- {t}\n{u}" for t, u in results[:50]]  # محدودیت ایمن
    await update.message.reply_text("\n\n".join(lines))


def register_plati_handlers(app: Application):
    app.add_handler(CallbackQueryHandler(open_plati_menu, pattern=f"^{PLATI_MENU}$"))
    app.add_handler(CallbackQueryHandler(on_plati_start, pattern=f"^{PLATI_START}$"))
    app.add_handler(CallbackQueryHandler(on_plati_back, pattern=f"^{PLATI_BACK}$"))
    # دریافت URL و عبارت بدون وابستگی به Reply، با اتکا به state
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_receive_url))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_receive_query))

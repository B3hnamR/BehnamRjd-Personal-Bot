from telegram import Update, ForceReply
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from bot.core.auth import owner_only
from .keyboards import PLATI_MENU, PLATI_START, PLATI_BACK, plati_menu_kb
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from bot.config import GUID_AGENT
import xml.etree.ElementTree as ET


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


async def _fetch_all_items_html(session: httpx.AsyncClient, start_url: str) -> list[tuple[str, str]]:
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


def _parse_section_and_order(cat_url: str) -> tuple[int | None, str | None]:
    try:
        u = urlparse(cat_url)
        parts = [p for p in u.path.split('/') if p]
        section_id = None
        for p in parts:
            if p.isdigit():
                section_id = int(p)
        qs = parse_qs(u.query)
        sort = qs.get('sort', [None])[0]
        order = None
        if sort == 'price_asc':
            order = 'priceDESC'  # ascending
        elif sort == 'price_desc':
            order = 'price'      # descending
        return section_id, order
    except Exception:
        return None, None


async def _fetch_all_items_api(session: httpx.AsyncClient, cat_url: str) -> list[tuple[str, str]]:
    if not GUID_AGENT:
        return []
    section_id, order = _parse_section_and_order(cat_url)
    if not section_id:
        return []
    items: list[tuple[str, str]] = []
    page = 1
    rows = 500
    while True:
        root = ET.Element('digiseller.request')
        ET.SubElement(root, 'guid_agent').text = GUID_AGENT
        ET.SubElement(root, 'id_section').text = str(section_id)
        ET.SubElement(root, 'lang').text = 'en-US'
        ET.SubElement(root, 'encoding').text = 'utf-8'
        ET.SubElement(root, 'page').text = str(page)
        ET.SubElement(root, 'rows').text = str(rows)
        ET.SubElement(root, 'currency').text = 'USD'
        if order:
            ET.SubElement(root, 'order').text = order
        data = ET.tostring(root, encoding='utf-8')
        resp = await session.post('https://plati.io/xml/goods.asp', content=data, headers={'Content-Type': 'application/xml'})
        resp.raise_for_status()
        tree = ET.fromstring(resp.content)
        retval = tree.findtext('retval') or '0'
        if retval != '0':
            break
        rows_node = tree.find('rows')
        if rows_node is None:
            break
        for row in rows_node.findall('row'):
            pid = row.findtext('id_goods')
            name = (row.findtext('name_goods') or '').strip()
            if not pid or not name:
                continue
            items.append((name, pid))
        total_pages_text = tree.findtext('pages')
        try:
            total_pages = int(total_pages_text) if total_pages_text else page
        except Exception:
            total_pages = page
        if page >= total_pages:
            break
        page += 1
    results: list[tuple[str, str]] = []
    for name, pid in items:
        try:
            p = await session.get(f'https://api.digiseller.com/api/products/{pid}/data?format=json')
            p.raise_for_status()
            j = p.json()
            url = None
            if isinstance(j, dict):
                if 'product' in j and isinstance(j['product'], dict):
                    url = j['product'].get('url')
                elif 'content' in j and isinstance(j['content'], dict):
                    url = j['content'].get('url')
            if not url:
                url = f'https://plati.io/itm/{pid}'
            results.append((name, url))
        except Exception:
            results.append((name, f'https://plati.io/itm/{pid}'))
    return results


async def _fetch_all_items(session: httpx.AsyncClient, start_url: str) -> list[tuple[str, str]]:
    api_items = await _fetch_all_items_api(session, start_url)
    if api_items:
        return api_items
    return await _fetch_all_items_html(session, start_url)


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

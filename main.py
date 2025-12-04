import asyncio
import aiohttp
import json
import os
from datetime import datetime
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import TelegramError
import logging

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

SAKANI_API_URL = "https://sakani.sa/api/web/lands/tax-incurred"
CHECK_INTERVAL = 300  # 5 minutes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

previous_lands = {}

async def fetch_lands_data():
    """سحب البيانات مع تجاوز الصيانة وإعادة المحاولة"""
    retries = 5
    delay = 3

    for attempt in range(retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
                'Accept-Language': 'ar',
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(SAKANI_API_URL, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status in (500, 502, 503, 504):
                        logger.warning(f"Sakani maintenance ({response.status})... retrying...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"Unexpected error: {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Error: {str(e)} - Retrying...")
            await asyncio.sleep(delay)

    return None


async def send_telegram_message(bot, message, url=None):
    """إرسال رسالة + زر حجز"""
    try:
        buttons = None
        if url:
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 رابط الحجز", url=url)]
            ])

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False,
            reply_markup=buttons
        )
        logger.info("Message sent.")
    except TelegramError as e:
        logger.error(f"Telegram error: {str(e)}")


def extract_lands_info(data):
    lands = {}

    try:
        lands_list = data.get("data", []) or data.get("items", [])

        for land in lands_list:
            land_id = land.get("id") or land.get("landId")
            if not land_id:
                continue

            lands[str(land_id)] = {
                "id": land_id,
                "number": land.get("plotNumber") or land.get("landNumber") or str(land_id),
                "area": land.get("area") or "غير محدد",
                "location": land.get("city") or land.get("location") or "غير محدد",
                "status": land.get("status") or "متاح",
                "url": f"https://sakani.sa/app/tax-incurred-form?id={land_id}"
            }

    except Exception as e:
        logger.error(f"Data extract error: {str(e)}")

    return lands


async def check_for_changes(bot):
    global previous_lands

    logger.info("Checking updates...")

    data = await fetch_lands_data()
    if data is None:
        logger.warning("Failed fetching data from Sakani.")
        return

    current_lands = extract_lands_info(data)

    if not previous_lands:
        previous_lands = current_lands
        await send_telegram_message(
            bot,
            f"🚀 بدأ تشغيل البوت!\nعدد القطع المسجلة: {len(current_lands)}"
        )
        return

    # --------------------------------------------------
    #  القطع الجديدة
    # --------------------------------------------------
    new_lands = set(current_lands) - set(previous_lands)

    for land_id in new_lands:
        land = current_lands[land_id]

        message = (
            f"🟢 <b>قطعة جديدة ظهرت!</b>\n\n"
            f"رقم القطعة: <b>{land['number']}</b>\n"
            f"الموقع: {land['location']}\n"
            f"المساحة: {land['area']}\n"
            f"الحالة: {land['status']}\n\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        await send_telegram_message(bot, message, land["url"])
        await asyncio.sleep(1)

    # --------------------------------------------------
    #  القطع الملغاة
    # --------------------------------------------------
    removed_lands = set(previous_lands) - set(current_lands)

    for land_id in removed_lands:
        land = previous_lands[land_id]

        message = (
            f"🔴 <b>قطعة تم إلغاؤها</b>\n\n"
            f"رقم القطعة: <b>{land['number']}</b>\n"
            f"الموقع: {land['location']}\n"
            f"المساحة: {land['area']}\n\n"
            f"❌ القطعة اختفت من النظام\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        await send_telegram_message(bot, message, land["url"])
        await asyncio.sleep(1)

    previous_lands = current_lands


async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    try:
        info = await bot.get_me()
        logger.info(f"Bot connected: @{info.username}")
    except Exception as e:
        logger.error(f"Bot token error: {str(e)}")
        return

    while True:
        await check_for_changes(bot)
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())

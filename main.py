import asyncio
import aiohttp
import json
import os
from datetime import datetime
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import TelegramError
import logging

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SAKANI_API_URL = "https://sakani.sa/api/web/lands/tax-incurred"
CHECK_INTERVAL = 300

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

previous_lands = {}

async def fetch_lands():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Accept-Language": "ar",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SAKANI_API_URL, headers=headers, timeout=20) as res:
                if res.status == 200:
                    return await res.json()
                else:
                    logger.warning(f"Sakani maintenance: {res.status}")
                    return None
    except Exception as e:
        logger.error(f"Fetch error: {str(e)}")
        return None

def extract_lands(data):
    lands = {}
    try:
        items = data.get("data", []) or data.get("items", [])

        for land in items:
            land_id = str(land.get("id"))
            lands[land_id] = {
                "id": land_id,
                "number": land.get("plotNumber", "غير معروف"),
                "area": land.get("area", "غير محدد"),
                "location": land.get("city", "غير معروف"),
                "url": f"https://sakani.sa/app/tax-incurred-form?id={land_id}",
            }
        return lands
    except:
        return {}

async def send_alert(bot, land, msg_type):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 عرض القطعة", url=land["url"])],
        [InlineKeyboardButton("🟢 حجز القطعة", url=land["url"])]
    ])

    message = (
        f"🔔 <b>{msg_type}</b>\n\n"
        f"رقم القطعة: {land['number']}\n"
        f"المساحة: {land['area']}\n"
        f"الموقع: {land['location']}\n\n"
        f"<a href='{land['url']}'>رابط القطعة</a>\n"
        f"⏱ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except TelegramError as e:
        logger.error(str(e))

async def check(bot):
    global previous_lands

    data = await fetch_lands()
    if not data:
        return

    lands = extract_lands(data)

    if not previous_lands:
        previous_lands = lands
        return

    # قطع جديدة
    new_ids = set(lands.keys()) - set(previous_lands.keys())
    for land_id in new_ids:
        await send_alert(bot, lands[land_id], "ظهرت قطعة جديدة")

    # قطع ألغيت
    removed_ids = set(previous_lands.keys()) - set(lands.keys())
    for land_id in removed_ids:
        await send_alert(bot, previous_lands[land_id], "❌ قطعة ألغيت")

    previous_lands = lands

async def main():
    bot = Bot(TELEGRAM_BOT_TOKEN)
    
    try:
        me = await bot.get_me()
        logger.info(f"Bot started: @{me.username}")
    except:
        logger.error("❌ التوكن غير صحيح")
        return

    while True:
        await check(bot)
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())

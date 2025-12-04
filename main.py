import asyncio
import aiohttp
import json
import os
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
import logging

# -----------------------------
# Environment Variables
# -----------------------------
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

SAKANI_API_URL = "https://sakani.sa/api/web/lands/tax-incurred"
CHECK_INTERVAL = 60   # كل دقيقة

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SAKANI-BOT")

previous_lands = {}

# -----------------------------
# Fetch API
# -----------------------------
async def fetch_lands_data():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'Accept-Language': 'ar',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(SAKANI_API_URL, headers=headers, timeout=20) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Sakani error {response.status} (Site may be under maintenance)")
                    return None

    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return None

# -----------------------------
# Send message
# -----------------------------
async def send_message(bot, text, url=None):
    try:
        if url:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 رابط الحجز", url=url)]
            ])
            await bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=keyboard, parse_mode="HTML")
        else:
            await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="HTML")

        logger.info("Message sent")

    except TelegramError as e:
        logger.error(f"Telegram Error: {e}")

# -----------------------------
# Extract land info
# -----------------------------
def extract_lands(data):
    lands = {}

    try:
        items = data.get("data", [])
        for land in items:
            land_id = land.get("id")
            lands[str(land_id)] = {
                "id": land_id,
                "number": land.get("landNumber") or land_id,
                "area": land.get("area"),
                "status": land.get("status", "متاحة"),
                "url": f"https://sakani.sa/app/tax-incurred-form?id={land_id}"
            }
        return lands

    except Exception as e:
        logger.error(f"Extract error: {e}")
        return {}

# -----------------------------
# Monitor changes
# -----------------------------
async def check_updates(bot):
    global previous_lands

    data = await fetch_lands_data()
    if not data:
        logger.info("No data (Sakani down). Retrying...")
        return

    lands = extract_lands(data)

    # أول تشغيل فقط
    if not previous_lands:
        previous_lands = lands
        await send_message(bot, f"✨ تم تشغيل البوت\nعدد الأراضي: {len(lands)}")
        return

    # أراضي جديدة
    new_ids = set(lands.keys()) - set(previous_lands.keys())
    for land_id in new_ids:
        land = lands[land_id]
        msg = (
            f"🌟 أرض جديدة ظهرت!\n\n"
            f"رقم القطعة: {land['number']}\n"
            f"المساحة: {land['area']}\n"
            f"الحالة: {land['status']}\n\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await send_message(bot, msg, url=land["url"])

    # أراضي ألغيت
    removed_ids = set(previous_lands.keys()) - set(lands.keys())
    for land_id in removed_ids:
        land = previous_lands[land_id]
        msg = (
            f"❌ قطعة ملغاة!\n\n"
            f"رقم القطعة: {land['number']}\n"
            f"المساحة: {land['area']}\n"
            f"تم حذفها من النظام.\n\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await send_message(bot, msg)

    previous_lands = lands


# -----------------------------
# MAIN LOOP
# -----------------------------
async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    try:
        info = await bot.get_me()
        logger.info(f"Bot connected → @{info.username}")
    except Exception as e:
        logger.error(f"Token incorrect → {e}")
        return

    while True:
        await check_updates(bot)
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())

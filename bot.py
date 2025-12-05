# ========== ملف: bot.py ==========

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import logging

# ========== الإعدادات ==========

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SAKANI_API_URL = "https://sakani.sa/api/web/lands/tax-incurred"
CHECK_INTERVAL = 300  # كل 5 دقائق

# ========== إعداد السجلات ==========

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

previous_lands = {}

# ========== دوال البوت ==========

async def fetch_lands_data():
    """يجلب بيانات API من موقع سكني"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'ar',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(SAKANI_API_URL, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"خطأ في الاستجابة: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"خطأ في جلب البيانات: {str(e)}")
        return None


async def send_telegram_message(bot, message):
    """إرسال رسالة تلغرام"""
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
    except TelegramError as e:
        logger.error(f"خطأ عند إرسال الرسالة: {str(e)}")


def extract_lands_info(data):
    """تحليل بيانات الأراضي"""
    try:
        lands = {}
        for land in data.get("data", []):
            land_id = str(land.get("id", ""))
            lands[land_id] = {
                'number': land.get('plotNumber') or land.get('landNumber') or land_id,
                'location': land.get('location') or land.get('city') or "غير محدد",
                'area': land.get('area') or land.get('size') or "غير محدد",
                'status': land.get('status') or "غير معروف",
                'url': land.get('url') or f"https://sakani.sa/app/tax-incurred-form?id={land_id}"
            }
        return lands
    except Exception as e:
        logger.error(f"خطأ في استخراج المعلومات: {str(e)}")
        return {}


async def check_for_changes(bot):
    global previous_lands

    logger.info("جاري التحقق من التغييرات...")

    data = await fetch_lands_data()
    if data is None:
        logger.warning("فشل في جلب البيانات")
        return

    current_lands = extract_lands_info(data)
    if not current_lands:
        logger.warning("لا توجد بيانات مسترجعة")
        return

    # أول تشغيل
    if not previous_lands:
        previous_lands = current_lands
        await send_telegram_message(bot, f"🚀 تم تشغيل البوت!\n📌 عدد القطع الحالية: {len(current_lands)}")
        return

    # مقارنة الجديد
    new_ids = set(current_lands.keys()) - set(previous_lands.keys())
    removed_ids = set(previous_lands.keys()) - set(current_lands.keys())

    # إرسال الجديد
    for land_id in new_ids:
        land = current_lands[land_id]
        message = (
            f"🟢 <b>قطعة جديدة ظهرت:</b>\n\n"
            f"🔢 <b>رقم القطعة:</b> {land['number']}\n"
            f"📍 <b>الموقع:</b> {land['location']}\n"
            f"📏 <b>المساحة:</b> {land['area']}\n"
            f"📘 <b>الحالة:</b> {land['status']}\n"
            f"<a href='{land['url']}'>رابط التفاصيل</a>\n\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await send_telegram_message(bot, message)
        await asyncio.sleep(1)

    # إرسال الملغي
    for land_id in removed_ids:
        land = previous_lands[land_id]
        message = (
            f"🔴 <b>قطعة تم إلغاؤها:</b>\n\n"
            f"🔢 <b>رقم القطعة:</b> {land['number']}\n"
            f"📍 <b>الموقع:</b> {land['location']}\n"
            f"📏 <b>المساحة:</b> {land['area']}\n"
            f"❗ تم إزالتها من النظام\n\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await send_telegram_message(bot, message)
        await asyncio.sleep(1)

    previous_lands = current_lands


async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    logger.info("تم تشغيل البوت...")

    try:
        bot_info = await bot.get_me()
        logger.info(f"البوت يعمل: @{bot_info.username}")
    except Exception as e:
        logger.error(f"خطأ في التحقق من البوت: {str(e)}")
        return

    while True:
        try:
            await check_for_changes(bot)
        except Exception as e:
            logger.error(f"خطأ في التنفيذ: {str(e)}")

        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت يدوياً")
    except Exception as e:
        logger.error(f"خطأ نهائي: {str(e)}")

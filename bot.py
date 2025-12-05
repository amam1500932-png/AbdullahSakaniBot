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

# سيحفظ آخر حالة للأراضي
previous_lands: dict[str, dict] = {}


# ========== دوال البوت ==========

async def fetch_lands_data() -> dict | None:
    """جلب بيانات الأراضي من API سكني"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, مثل Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Accept-Language": "ar",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(SAKANI_API_URL, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"خطأ في الاستجابة من API: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"خطأ في جلب البيانات من سكني: {str(e)}")
        return None


async def send_telegram_message(bot: Bot, message: str) -> None:
    """إرسال رسالة إلى تليجرام"""
    if not CHAT_ID:
        logger.error("CHAT_ID غير موجود في المتغيرات البيئية!")
        return

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
        logger.info("تم إرسال رسالة إلى التليجرام")
    except TelegramError as e:
        logger.error(f"خطأ عند إرسال الرسالة إلى التليجرام: {str(e)}")


def extract_lands_info(data: dict) -> dict[str, dict]:
    """تحويل بيانات API إلى شكل بسيط نستعمله في المقارنة"""
    lands: dict[str, dict] = {}

    try:
        for land in data.get("data", []):
            land_id = str(land.get("id", ""))

            lands[land_id] = {
                "number": land.get("plotNumber") or land.get("landNumber") or land_id,
                "location": land.get("location") or land.get("city") or "غير محدد",
                "area": land.get("area") or land.get("size") or "غير محدد",
                "status": land.get("status") or "غير معروف",
                "url": land.get("url") or f"https://sakani.sa/app/tax-incurred-form?id={land_id}",
            }

    except Exception as e:
        logger.error(f"خطأ في استخراج معلومات القطع: {str(e)}")

    return lands


async def check_for_changes(bot: Bot) -> None:
    """التحقق من أي تغييرات (قطع جديدة أو محذوفة)"""
    global previous_lands

    logger.info("جاري التحقق من التغييرات في الأراضي...")

    data = await fetch_lands_data()
    if data is None:
        logger.warning("فشل في جلب البيانات من سكني")
        return

    current_lands = extract_lands_info(data)
    if not current_lands:
        logger.warning("لا توجد بيانات مسترجعة من API")
        return

    # أول تشغيل للبوت
    if not previous_lands:
        previous_lands = current_lands
        msg = (
            "🚀 <b>تم تشغيل البوت لمراقبة الأراضي المجانية</b>\n\n"
            f"📊 عدد القطع الحالية في سكني: {len(current_lands)}\n"
            f"⏱ سيتم التحقق كل {CHECK_INTERVAL // 60} دقيقة."
        )
        await send_telegram_message(bot, msg)
        return

    # حساب القطع الجديدة والملغاة
    old_ids = set(previous_lands.keys())
    new_ids = set(current_lands.keys())

    added_ids = new_ids - old_ids
    removed_ids = old_ids - new_ids

    # إرسال تنبيه بالقطع الجديدة
    for land_id in added_ids:
        land = current_lands[land_id]
        message = (
            "🟢 <b>قطعة جديدة متاحة:</b>\n\n"
            f"🔢 <b>رقم القطعة:</b> {land['number']}\n"
            f"📍 <b>الموقع:</b> {land['location']}\n"
            f"📏 <b>المساحة:</b> {land['area']}\n"
            f"📘 <b>الحالة:</b> {land['status']}\n"
            f"<a href='{land['url']}'>رابط التفاصيل في سكني</a>\n\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await send_telegram_message(bot, message)
        await asyncio.sleep(1)

    # إرسال تنبيه بالقطع الملغاة
    for land_id in removed_ids:
        land = previous_lands.get(land_id)
        if not land:
            continue

        message = (
            "🔴 <b>قطعة تم إلغاؤها / إزالتها:</b>\n\n"
            f"🔢 <b>رقم القطعة:</b> {land['number']}\n"
            f"📍 <b>الموقع:</b> {land['location']}\n"
            f"📏 <b>المساحة:</b> {land['area']}\n"
            "❗ تم إزالتها من قائمة سكني.\n\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await send_telegram_message(bot, message)
        await asyncio.sleep(1)

    if added_ids or removed_ids:
        logger.info(f"تم العثور على {len(added_ids)} جديدة و {len(removed_ids)} ملغاة.")
    else:
        logger.info("لا توجد تغييرات في هذه الدورة.")

    previous_lands = current_lands


async def main() -> None:
    """الدالة الرئيسية لتشغيل البوت"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN غير موجود في المتغيرات البيئية!")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    logger.info("جاري تشغيل بوت سكني...")

    # التأكد أن التوكن صحيح
    try:
        bot_info = await bot.get_me()
        logger.info(f"البوت يعمل بنجاح: @{bot_info.username}")
    except Exception as e:
        logger.error(f"خطأ في التحقق من البوت (توكن؟): {str(e)}")
        return

    # حلقة لا نهائية للتحقق كل فترة
    while True:
        try:
            await check_for_changes(bot)
        except Exception as e:
            logger.error(f"خطأ أثناء التحقق من التغييرات: {str(e)}")

        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت يدويًا من السيرفر")
    except Exception as e:
        logger.error(f"خطأ نهائي غير متوقع: {str(e)}")

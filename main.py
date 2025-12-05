import os
import logging
import requests
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError

# قراءة التوكن والـ Chat ID من render
BOT_TOKEN = os.environ.get("TELE_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = Bot(BOT_TOKEN)

# API سكني
SAKANI_API = "https://sakani.sa/api/web/lands/tax-incurred"

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تخزين البيانات السابقة للمقارنة
previous_lands = {}


def fetch_sakani_lands():
    """جلب بيانات الأراضي من سكني"""
    try:
        response = requests.get(SAKANI_API, timeout=10)

        if response.status_code != 200:
            logger.error(f"خطأ API: {response.status_code}")
            return None

        return response.json()

    except Exception as e:
        logger.error(f"فشل طلب API: {e}")
        return None


def format_land(land):
    """صياغة التنبيه بشكل جميل"""
    land_id = land.get("id")
    project_id = land.get("projectId")
    project_name = land.get("projectName")
    city = land.get("cityName")
    status = land.get("statusName")
    land_no = land.get("landNumber")

    url = f"https://sakani.sa/app/units/{land_id}"

    msg = (
        f"📍 *تحديث جديد في سكني!*\n\n"
        f"🏡 *المشروع:* {project_name}\n"
        f"🌆 *المدينة:* {city}\n"
        f"🔢 *رقم القطعة:* {land_no}\n"
        f"📌 *الحالة:* {status}\n"
        f"🔗 *رابط القطعة:* {url}"
    )

    return msg


def check_updates():
    """مقارنة البيانات الحالية مع السابقة"""
    global previous_lands

    lands = fetch_sakani_lands()
    if lands is None:
        return

    for land in lands:

        land_id = land["id"]

        # أول تشغيل — حفظ البيانات فقط
        if land_id not in previous_lands:
            previous_lands[land_id] = land
            continue

        old_status = previous_lands[land_id]["statusName"]
        new_status = land["statusName"]

        # إذا تغيرت حالة القطعة — إرسال تنبيه
        if old_status != new_status:
            msg = format_land(land)
            try:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=msg,
                    parse_mode="Markdown"
                )
            except TelegramError as e:
                logger.error(f"فشل إرسال التلقرام: {e}")

            # تحديث الحفظ
            previous_lands[land_id] = land

    logger.info("تم فحص الأراضي (OK)")


@app.route("/")
def home():
    return "Sakani Bot Running Successfully!"


if __name__ == "__main__":
    check_updates()
    app.run(host="0.0.0.0", port=10000)

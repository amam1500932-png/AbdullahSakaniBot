import os
import logging
import requests
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError

# ------------------------------------
# قراءة القيم من Render Environment
# ------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELE_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# رابط API الأراضي (سكني)
SAKANI_API = "https://sakani.sa/api/web/lands/tax-incurred"

# إعداد اللوق
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN)

app = Flask(__name__)

previous_data = None


def check_sakani():
    global previous_data

    try:
        response = requests.get(SAKANI_API, timeout=10)
        if response.status_code != 200:
            logger.error(f"خطأ في API سكني: {response.status_code}")
            return

        data = response.json()

        # أول تشغيل فقط حفظ البيانات
        if previous_data is None:
            previous_data = data
            return

        # مقارنة التغيير
        if data != previous_data:
            bot.send_message(
                CHAT_ID,
                "📢 تم تحديث بيانات سكني! يوجد تغييرات جديدة في الأراضي."
            )
            previous_data = data

        logger.info("تم فحص التحديثات بنجاح")

    except Exception as e:
        logger.error(f"فشل في جلب البيانات: {e}")


@app.route("/")
def home():
    return "Sakani bot is running"


if __name__ == "__main__":
    check_sakani()
    app.run(host="0.0.0.0", port=10000)

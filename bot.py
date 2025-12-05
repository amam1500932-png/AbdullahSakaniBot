import os
import time
import threading
import logging
import requests
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError

# =========================
# الإعدادات
# =========================

# من Environment في Render:
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SAKANI_API_URL = "https://sakani.sa/api/web/lands/tax-incurred"
CHECK_INTERVAL = 300  # كل 5 دقائق

# =========================
# السجلات (Logs)
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# تخزين آخر حالة للأراضي
previous_lands = {}

# Flask عشان Render
app = Flask(__name__)

# البوت
bot = Bot(token=TELEGRAM_BOT_TOKEN)


# =========================
# دوال سكني
# =========================

def fetch_lands_data():
    """يجلب بيانات الأراضي من API سكني"""
    try:
        headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
    "Origin": "https://sakani.sa",
    "Referer": "https://sakani.sa/",
    "Connection": "keep-alive",
    "Cookie": "sakani_locale=ar; visid_incap_2266985=; incap_ses_1549_2266985=;"
}

        resp = requests.get(SAKANI_API_URL, headers=headers, timeout=30)

        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error(f"خطأ في استجابة API: {resp.status_code}")
            return None

    except Exception as e:
        logger.error(f"خطأ في جلب بيانات سكني: {e}")
        return None


def extract_lands_info(data):
    """تحويل بيانات API إلى شكل مبسط"""
    lands = {}
    try:
        for land in data.get("data", []):
            land_id = str(land.get("id", ""))

            lands[land_id] = {
                "number": land.get("landNumber") or land.get("plotNumber") or land_id,
                "project": land.get("projectName") or "غير معروف",
                "city": land.get("cityName") or land.get("city") or "غير محدد",
                "area": land.get("area") or land.get("size") or "غير محدد",
                "status": land.get("statusName") or land.get("status") or "غير معروف",
                "url": f"https://sakani.sa/app/land-projects/{land.get('projectId', '')}",
            }
        return lands
    except Exception as e:
        logger.error(f"خطأ في تحليل بيانات الأراضي: {e}")
        return {}


# =========================
# دوال التلقرام
# =========================

def send_telegram_message(message: str):
    """إرسال رسالة لتلجرام"""
    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        logger.error("TELE_BOT_TOKEN أو CHAT_ID غير مضبوطين في Environment")
        return

    try:
        bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
        logger.info("تم إرسال رسالة إلى تلجرام")
    except TelegramError as e:
        logger.error(f"خطأ أثناء إرسال رسالة تلجرام: {e}")


def format_new_land_msg(land):
    return (
        "🟢 <b>قطعة جديدة ظهرت في سكني</b>\n\n"
        f"🏡 <b>المخطط/المشروع:</b> {land['project']}\n"
        f"🌆 <b>المدينة:</b> {land['city']}\n"
        f"🔢 <b>رقم القطعة:</b> {land['number']}\n"
        f"📏 <b>المساحة:</b> {land['area']}\n"
        f"📘 <b>الحالة:</b> {land['status']}\n"
        f"<a href='{land['url']}'>🔗 رابط المخطط</a>"
    )


def format_removed_land_msg(land):
    return (
        "🔴 <b>قطعة تم إلغاؤها / اختفائها من القائمة</b>\n\n"
        f"🏡 <b>المخطط/المشروع:</b> {land['project']}\n"
        f"🌆 <b>المدينة:</b> {land['city']}\n"
        f"🔢 <b>رقم القطعة:</b> {land['number']}\n"
        f"📏 <b>المساحة:</b> {land['area']}\n"
        "❗ تم إزالتها من النظام (قد تكون ملغاة أو محجوزة نهائيًا)"
    )


# =========================
# حلقة المراقبة
# =========================

def check_for_changes_loop():
    """تعمل في ثريد مستقل وتراقب التغييرات باستمرار"""
    global previous_lands

    logger.info("بدء حلقة مراقبة سكني ...")

    # أول تشغيل: تحميل البيانات وحفظها فقط
    data = fetch_lands_data()
    if data:
        current = extract_lands_info(data)
        previous_lands = current
        send_telegram_message(
            f"🚀 تم تشغيل البوت بنجاح.\n"
            f"📌 عدد القطع الحالية في النظام: {len(current)}"
        )
    else:
        logger.warning("فشل في جلب البيانات عند التشغيل الأول.")

    # حلقة مستمرة
    while True:
        try:
            time.sleep(CHECK_INTERVAL)

            data = fetch_lands_data()
            if not data:
                logger.warning("لا توجد بيانات مسترجعة من سكني.")
                continue

            current_lands = extract_lands_info(data)
            if not current_lands:
                logger.warning("فشل في تحليل بيانات الأراضي.")
                continue

            # الجديد
            new_ids = set(current_lands.keys()) - set(previous_lands.keys())
            # الملغي
            removed_ids = set(previous_lands.keys()) - set(current_lands.keys())

            # إرسال القطع الجديدة
            for land_id in new_ids:
                land = current_lands[land_id]
                msg = format_new_land_msg(land)
                send_telegram_message(msg)
                time.sleep(1)

            # إرسال الملغاة
            for land_id in removed_ids:
                land = previous_lands[land_id]
                msg = format_removed_land_msg(land)
                send_telegram_message(msg)
                time.sleep(1)

            previous_lands = current_lands
            logger.info("تم فحص التغييرات بنجاح.")

        except Exception as e:
            logger.error(f"خطأ في حلقة المراقبة: {e}")


# =========================
# Flask Routes
# =========================

@app.route("/")
def index():
    return "Abdullah Sakani Bot is running ✅"


# =========================
# نقطة البداية
# =========================

def main():
    # تشغيل ثريد المراقبة
    watcher_thread = threading.Thread(target=check_for_changes_loop, daemon=True)
    watcher_thread.start()

    # تشغيل Flask على البورت الذي تحدده Render
    port = int(os.environ.get("PORT", "10000"))
    logger.info(f"تشغيل Flask على البورت {port}")
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

import os
import time
import threading
import logging
import requests
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError

# =======================
# الإعدادات
# =======================

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SAKANI_API_URL = "https://sakani.sa/api/web/lands/tax-incurred"
CHECK_INTERVAL = 300  # كل 5 دقائق

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

previous_lands = {}

app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# =======================
# جلب بيانات سكني
# =======================

def fetch_lands_data():
    """جلب بيانات الأراضي من API"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Origin": "https://sakani.sa",
            "Referer": "https://sakani.sa/",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "Connection": "keep-alive",
            "DNT": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }

        # محاولة بدون cookies أولاً
        resp = requests.get(SAKANI_API_URL, headers=headers, timeout=30)

        if resp.status_code == 200:
            logger.info("تم جلب البيانات بنجاح من سكني")
            return resp.json()
        
        # إذا فشل، نحاول مع session
        elif resp.status_code == 403:
            logger.warning("تم رفض الطلب 403، محاولة مع session...")
            
            session = requests.Session()
            session.headers.update(headers)
            
            # زيارة الصفحة الرئيسية أولاً للحصول على cookies
            session.get("https://sakani.sa/", timeout=15)
            time.sleep(2)
            
            # المحاولة مرة أخرى
            resp = session.get(SAKANI_API_URL, timeout=30)
            
            if resp.status_code == 200:
                logger.info("نجح الطلب بعد استخدام session")
                return resp.json()
            else:
                logger.error(f"فشل الطلب مع session: {resp.status_code}")
                return None
        
        else:
            logger.error(f"خطأ في استجابة API: {resp.status_code}")
            logger.debug(f"Response: {resp.text[:200]}")
            return None

    except requests.exceptions.Timeout:
        logger.error("انتهت مهلة الاتصال بـ API")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("خطأ في الاتصال بـ API")
        return None
    except Exception as e:
        logger.error(f"خطأ غير متوقع أثناء جلب بيانات سكني: {e}")
        return None


# =======================
# تحليل البيانات
# =======================

def extract_lands_info(data):
    """يبسط بيانات API ويعيدها بشكل منظم"""
    lands = {}
    try:
        # تحقق من وجود البيانات
        if not data or "data" not in data:
            logger.error("البيانات المستلمة لا تحتوي على 'data'")
            return {}
        
        data_list = data.get("data", [])
        
        if not data_list:
            logger.warning("قائمة البيانات فارغة")
            return {}
        
        for land in data_list:
            land_id = str(land.get("id", ""))
            
            if not land_id:
                continue

            lands[land_id] = {
                "number": land.get("landNumber") or land.get("plotNumber") or land_id,
                "project": land.get("projectName") or "غير محدد",
                "city": land.get("cityName") or land.get("city") or "غير محدد",
                "area": str(land.get("area") or land.get("size") or "غير محدد"),
                "status": land.get("statusName") or land.get("status") or "غير محدد",
                "url": f"https://sakani.sa/app/land-projects/{land.get('projectId', '')}"
            }

        logger.info(f"تم تحليل {len(lands)} قطعة أرض")
        return lands

    except Exception as e:
        logger.error(f"خطأ في تحليل بيانات الأراضي: {e}")
        return {}


# =======================
# إرسال رسائل تلجرام
# =======================

def send_telegram_message(message: str):
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
        "<b>🟢 قطعة جديدة ظهرت في سكني</b>\n\n"
        f"🏘️ <b>المخطط:</b> {land['project']}\n"
        f"📍 <b>المدينة:</b> {land['city']}\n"
        f"🔢 <b>رقم القطعة:</b> {land['number']}\n"
        f"📏 <b>المساحة:</b> {land['area']}\n"
        f"🔗 <a href='{land['url']}'>رابط العرض</a>"
    )


def format_removed_land_msg(land):
    return (
        "<b>🔴 قطعة تم إزالتها / اختفت من النظام</b>\n\n"
        f"🏘️ <b>المخطط:</b> {land['project']}\n"
        f"📍 <b>المدينة:</b> {land['city']}\n"
        f"🔢 <b>رقم القطعة:</b> {land['number']}\n"
        f"📏 <b>المساحة:</b> {land['area']}\n"
        "❗ تم إزالتها من النظام (قد تكون محجوزة أو مباعة)."
    )


# =======================
# حلقة المراقبة
# =======================

def check_for_changes_loop():
    global previous_lands

    logger.info("بدء عملية فحص سكني...")

    # تحميل أول دفعة
    data = fetch_lands_data()
    if data:
        current = extract_lands_info(data)
        if current:
            previous_lands = current
            send_telegram_message(
                f"🔔 تم تشغيل البوت بنجاح.\n"
                f"📊 عدد القطع الحالية في النظام: {len(current)}"
            )
        else:
            logger.warning("تم جلب البيانات لكن فشل التحليل")
    else:
        logger.warning("فشل جلب البيانات عند التشغيل الأول - سيحاول مجدداً بعد 5 دقائق")

    # حلقة مستمرة
    while True:
        try:
            time.sleep(CHECK_INTERVAL)

            data = fetch_lands_data()
            if not data:
                logger.warning("لا توجد بيانات مسترجعة من سكني - محاولة تالية بعد 5 دقائق")
                continue

            current_lands = extract_lands_info(data)
            if not current_lands:
                logger.warning("فشل في تحليل بيانات الأراضي - محاولة تالية بعد 5 دقائق")
                continue

            # الجديد
            new_ids = set(current_lands.keys()) - set(previous_lands.keys())

            # المحذوف
            removed_ids = set(previous_lands.keys()) - set(current_lands.keys())

            # إرسال الجديد
            if new_ids:
                logger.info(f"تم اكتشاف {len(new_ids)} قطعة جديدة")
                for land_id in new_ids:
                    land = current_lands[land_id]
                    send_telegram_message(format_new_land_msg(land))
                    time.sleep(1)

            # إرسال المحذوف
            if removed_ids:
                logger.info(f"تم اكتشاف {len(removed_ids)} قطعة محذوفة")
                for land_id in removed_ids:
                    land = previous_lands[land_id]
                    send_telegram_message(format_removed_land_msg(land))
                    time.sleep(1)

            if not new_ids and not removed_ids:
                logger.info("لا توجد تغييرات في البيانات")

            previous_lands = current_lands

        except Exception as e:
            logger.error(f"خطأ في حلقة المراقبة: {e}")


# =======================
# واجهة Render
# =======================

@app.route("/")
def index():
    return "Abdullah Sakani Bot is running ✔️"


@app.route("/health")
def health():
    """نقطة صحة لـ Render"""
    return {"status": "ok", "lands_count": len(previous_lands)}


# =======================
# تشغيل البوت
# =======================

def main():
    watcher_thread = threading.Thread(target=check_for_changes_loop, daemon=True)
    watcher_thread.start()

    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

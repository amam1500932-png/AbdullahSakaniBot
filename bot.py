import os
import time
import threading
import logging
import requests
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError
from bs4 import BeautifulSoup
import json

# =======================
# الإعدادات
# =======================

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# استخدام صفحة الويب بدلاً من API
SAKANI_WEB_URL = "https://sakani.sa/Individuals/LandWithFees"
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
# جلب بيانات سكني من صفحة الويب
# =======================

def fetch_lands_data():
    """جلب بيانات الأراضي من صفحة الويب"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }

        session = requests.Session()
        
        # زيارة الصفحة الرئيسية أولاً
        logger.info("زيارة الصفحة الرئيسية...")
        session.get("https://sakani.sa/", headers=headers, timeout=15)
        time.sleep(2)
        
        # زيارة صفحة الأراضي
        logger.info("جلب بيانات الأراضي...")
        resp = session.get(SAKANI_WEB_URL, headers=headers, timeout=30)

        if resp.status_code == 200:
            logger.info("✅ تم جلب الصفحة بنجاح")
            
            # محاولة استخراج البيانات من الصفحة
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # البحث عن script tags التي قد تحتوي على البيانات
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'lands' in script.string.lower():
                    try:
                        # محاولة استخراج JSON من السكريبت
                        script_content = script.string
                        # يمكن تحسين هذا حسب بنية الصفحة
                        logger.info(f"وجدت سكريبت يحتوي على 'lands'")
                    except:
                        pass
            
            # في حالة عدم وجود بيانات في السكريبت، نرجع رسالة
            logger.warning("لم يتم العثور على بيانات مباشرة - قد تحتاج المراقبة اليدوية")
            
            # إرجاع بيانات وهمية للاختبار (ستحتاج لتعديل هذا حسب بنية الصفحة الفعلية)
            return {"data": []}
            
        else:
            logger.error(f"❌ خطأ في استجابة الصفحة: {resp.status_code}")
            return None

    except Exception as e:
        logger.error(f"⚠️ خطأ أثناء جلب البيانات: {e}")
        return None


# =======================
# تحليل البيانات
# =======================

def extract_lands_info(data):
    """يبسط بيانات ويعيدها بشكل منظم"""
    lands = {}
    try:
        if not data or "data" not in data:
            return {}
        
        data_list = data.get("data", [])
        
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

        logger.info(f"📊 تم تحليل {len(lands)} قطعة أرض")
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
        logger.info("📤 تم إرسال رسالة إلى تلجرام")
    except TelegramError as e:
        logger.error(f"❌ خطأ أثناء إرسال رسالة تلجرام: {e}")


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

    logger.info("🚀 بدء عملية فحص سكني...")
    
    send_telegram_message(
        "🔔 تم تشغيل بوت مراقبة سكني\n\n"
        "⚠️ ملاحظة: قد تكون المراقبة محدودة بسبب قيود الموقع.\n"
        "سيتم المحاولة كل 5 دقائق."
    )

    # حلقة مستمرة
    while True:
        try:
            data = fetch_lands_data()
            
            if data:
                current_lands = extract_lands_info(data)
                
                if current_lands and previous_lands:
                    # الجديد
                    new_ids = set(current_lands.keys()) - set(previous_lands.keys())
                    # المحذوف
                    removed_ids = set(previous_lands.keys()) - set(current_lands.keys())

                    # إرسال الجديد
                    if new_ids:
                        logger.info(f"🆕 تم اكتشاف {len(new_ids)} قطعة جديدة")
                        for land_id in new_ids:
                            land = current_lands[land_id]
                            send_telegram_message(format_new_land_msg(land))
                            time.sleep(1)

                    # إرسال المحذوف
                    if removed_ids:
                        logger.info(f"🗑️ تم اكتشاف {len(removed_ids)} قطعة محذوفة")
                        for land_id in removed_ids:
                            land = previous_lands[land_id]
                            send_telegram_message(format_removed_land_msg(land))
                            time.sleep(1)

                    if not new_ids and not removed_ids:
                        logger.info("✅ لا توجد تغييرات")

                if current_lands:
                    previous_lands = current_lands

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"❌ خطأ في حلقة المراقبة: {e}")
            time.sleep(CHECK_INTERVAL)


# =======================
# واجهة Render
# =======================

@app.route("/")
def index():
    return "Abdullah Sakani Bot is running ✔️"


@app.route("/health")
def health():
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

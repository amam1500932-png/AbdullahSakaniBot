import time
import threading
import requests
import telebot
import json
import os
from flask import Flask

# =========================
# إعدادات رئيسية
# =========================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # من Render
CHAT_ID = os.environ.get("CHAT_ID")               # معرف المحادثة
CHECK_INTERVAL = 60  # كل دقيقة يفحص

SAKANI_API_URL = "https://sakani.sa/api/web/lands/tax-incurred"

# وضع التجربة (شغال الآن)
# إذا صار عندك لابتوب والكوكي الجاهز: غيّرها إلى False
USE_TEST_DATA = True

# =========================
# إنشاء البوت
# =========================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =========================
# بيانات محفوظة
# =========================

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"lands": {}}
    return {"lands": {}}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

state = load_state()


# =========================
# جلب بيانات سكني
# =========================

def fetch_lands_data():
    """دالة تجيب بيانات الأراضي (تجريبية أو من سكني)"""

    # ---- وضع التجربة ----
    if USE_TEST_DATA:
        print("🔵 وضع التجربة شغال — استخدام بيانات تجريبية")
        fake_data = {
            "data": [
                {
                    "id": 1,
                    "landNumber": "1001",
                    "projectName": "مخطط تجريبي 1",
                    "cityName": "الرياض",
                    "area": "400 م²",
                    "statusName": "متاحة",
                    "projectId": 111
                },
                {
                    "id": 2,
                    "landNumber": "1002",
                    "projectName": "مخطط تجريبي 2",
                    "cityName": "جدة",
                    "area": "500 م²",
                    "statusName": "متاحة",
                    "projectId": 222
                }
            ]
        }
        return fake_data

    # ---- وضع حقيقي (لاحقًا نضيف الكوكي هنا) ----
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://sakani.sa/"
            # "Cookie": "ضع الكوكي هنا بعد ما نجيبه من اللابتوب"
        }

        resp = requests.get(SAKANI_API_URL, headers=headers, timeout=20)

        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"❌ خطأ API: {resp.status_code}")
            return None
    except Exception as e:
        print(f"❌ استثناء أثناء الجلب: {e}")
        return None


# =========================
# مقارنة البيانات القديمة بالجديدة
# =========================

def check_changes():
    global state

    lands_data = fetch_lands_data()
    if lands_data is None or "data" not in lands_data:
        print("⚠️ لم يتم استلام بيانات")
        return

    new_list = lands_data["data"]
    old_list = state.get("lands", {})

    # البحث عن أراضي جديدة
    for item in new_list:
        land_id = str(item["id"])

        if land_id not in old_list:
            send_land_notification(item)
            old_list[land_id] = item

    save_state(state)


# =========================
# إرسال إشعار تلجرام
# =========================

def send_land_notification(item):
    msg = (
        f"🔔 <b>قطعة جديدة متاحة</b>\n"
        f"📌 <b>رقم القطعة:</b> {item['landNumber']}\n"
        f"🏘 <b>المخطط:</b> {item['projectName']}\n"
        f"🏙 <b>المدينة:</b> {item['cityName']}\n"
        f"📐 <b>المساحة:</b> {item['area']}\n"
        f"🔗 <a href='https://sakani.sa/app/land-projects/{item['projectId']}'>رابط المخطط</a>"
    )
    bot.send_message(CHAT_ID, msg)


# =========================
# حلقة الفحص المتكرر
# =========================

def background_loop():
    while True:
        check_changes()
        time.sleep(CHECK_INTERVAL)


# =========================
# تشغيل Flask عشان Render يبقي السيرفر شغال
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Sakani bot is running."


# =========================
# تشغيل الخيوط
# =========================

threading.Thread(target=background_loop, daemon=True).start()


# =========================
# تشغيل ويب Render
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

import time
import threading
import requests
import telebot
import json
import os
from flask import Flask

# ============================
# إعدادات رئيسية
# ============================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

CHECK_INTERVAL = 30  # كل 30 ثانية

# رابط API سكني (نستخدمه لاحقاً عندما نضيف الكوكي الحقيقي)
SAKANI_API_URL = "https://sakani.sa/api/web/lands/tax-incurred"

# وضع التجربة = True
# إذا صار عندك لابتوب بنخليه False ونضيف الكوكي الحقيقي
USE_TEST_DATA = True


# ============================
# إنشاء البوت
# ============================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ============================
# الملفات المحفوظة
# ============================

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


# ============================
# جلب بيانات الأراضي
# ============================

def fetch_lands_data():
    """ترجع بيانات الأراضي — تجريبية أو من سكني"""

    # ---- وضع التجربة ----
    if USE_TEST_DATA:
        print("🔵 وضع التجربة فعال — استخدام بيانات تجريبية")
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
                    "landNumber": "2005",
                    "projectName": "مخطط تجريبي 2",
                    "cityName": "جدة",
                    "area": "500 م²",
                    "statusName": "ملغاة",
                    "projectId": 222
                }
            ]
        }
        return fake_data

    # ---- وضع حقيقي لاحقاً ----
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://sakani.sa/",
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


# ============================
# تهيئة رسالة الإشعار
# ============================

def format_land(land):
    return (
        f"📍 <b>قطعة:</b> {land['landNumber']}\n"
        f"🏘️ <b>المخطط:</b> {land['projectName']}\n"
        f"📌 <b>المدينة:</b> {land['cityName']}\n"
        f"📐 <b>المساحة:</b> {land['area']}\n"
        f"📊 <b>الحالة:</b> {land['statusName']}\n"
    )

def send(msg):
    if CHAT_ID:
        bot.send_message(CHAT_ID, msg)


# ============================
# حلقة مراقبة التغييرات
# ============================

def watcher():
    global state

    print("🚀 المراقبة بدأت…")

    while True:
        data = fetch_lands_data()

        if not data or "data" not in data:
            time.sleep(CHECK_INTERVAL)
            continue

        current = {str(l["id"]): l for l in data["data"]}
        previous = state["lands"]

        # الجديد
        new_ids = set(current.keys()) - set(previous.keys())

        # المحذوف
        removed_ids = set(previous.keys()) - set(current.keys())

        # إرسال الجديد
        for land_id in new_ids:
            msg = "🟢 <b>قطعة جديدة ظهرت!</b>\n\n" + format_land(current[land_id])
            send(msg)

        # إرسال المحذوف
        for land_id in removed_ids:
            msg = "🔴 <b>قطعة اختفت / ألغيت!</b>\n\n" + format_land(previous[land_id])
            send(msg)

        # حفظ الحالة
        state["lands"] = current
        save_state(state)

        time.sleep(CHECK_INTERVAL)


# ============================
# تشغيل Flask (لـ Render)
# ============================

app = Flask(__name__)

@app.route("/")
def home():
    return "Sakani Bot Running ✔️"


# ============================
# بدء التشغيل
# ============================

def main():
    t = threading.Thread(target=watcher, daemon=True)
    t.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

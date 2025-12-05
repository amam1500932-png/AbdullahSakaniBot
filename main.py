import os
import time
import requests
from flask import Flask
from threading import Thread

# =========================
# المتغيرات السرية
# =========================
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SAKANI_API = "https://sakani.sa/api/web/lands/tax-incurred"

previous_status = {}

# =========================
# إرسال رسالة تلجرام
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg})
    except:
        pass


# =========================
# رابط قطعة — زر جاهز
# =========================
def land_link(land_id):
    return f"https://sakani.sa/app/units/{land_id}"

# =========================
# رابط مخطط — زر جاهز
# =========================
def project_link(project_id):
    return f"https://sakani.sa/app/land-projects/{project_id}"


# =========================
# جلب بيانات سكني
# =========================
def get_sakani():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }
        r = requests.get(SAKANI_API, headers=headers, timeout=10)

        if r.status_code == 403:
            print("❌ سكني فعل حماية 403 — نعطي مهلة")
            time.sleep(5)
            return None

        return r.json()

    except Exception as e:
        print("⚠ خطأ في الاتصال:", e)
        return None


# =========================
# مقارنة التغييرات
# =========================
def check_updates():
    global previous_status

    data = get_sakani()
    if not data:
        print("⚠ لا يوجد رد من سكني")
        return

    lands = data.get("data", [])

    for item in lands:
        land_id = item.get("id")
        project_name = item.get("projectName")
        project_id = item.get("projectId")
        status = item.get("unitStatusName")

        if land_id not in previous_status:  
            previous_status[land_id] = status
            continue

        old = previous_status[land_id]
        if old != status:
            msg = (
                f"🔔 *تغيير جديد في قطعة*\n"
                f"🔹 رقم القطعة: {land_id}\n"
                f"🔹 المخطط: {project_name}\n"
                f"🔹 الحالة القديمة: {old}\n"
                f"🔹 الحالة الجديدة: {status}\n"
                f"📍 رابط القطعة:\n{land_link(land_id)}\n"
                f"📍 رابط المخطط:\n{project_link(project_id)}"
            )
            send(msg)

        previous_status[land_id] = status


# =========================
# لوب التشغيل
# =========================
def worker():
    time.sleep(4)
    send("✅ البوت يعمل الآن بنجاح!")

    while True:
        check_updates()
        time.sleep(40)  # كل 40 ثانية


# =========================
# Flask لـ Render
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Sakani Bot Running Successfully"


# =========================
# تشغيل الخادم
# =========================
if __name__ == "__main__":
    Thread(target=worker).start()
    app.run(host="0.0.0.0", port=10000)

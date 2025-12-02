import requests
import time
from flask import Flask
from threading import Thread
from telegram import Bot

# توكن البوت والمعرّف
BOT_TOKEN = "هنا التوكن حقك"
CHAT_ID = "هنا الآي دي"
bot = Bot(token=BOT_TOKEN)

# رابط قطعة سكني
SAKANI_URL = "https://sakani.sa/app/api/lands/737899"
last_status = None

# فحص حالة القطعة
def check_sakani():
    global last_status
    while True:
        try:
            response = requests.get(SAKANI_URL)
            status_code = response.status_code

            if last_status is None:
                last_status = status_code

            if status_code != last_status:
                msg = f"🔔 تنبيه جديد – تغيرت حالة القطعة! الكود الجديد: {status_code}"
                bot.send_message(chat_id=CHAT_ID, text=msg)
                last_status = status_code

        except Exception as e:
            print("Error:", e)

        time.sleep(10)  # كل 10 ثواني

# سيرفر Flask لإبقاء Replit شغال
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

# تشغيل الخادم والوظيفة معًا
Thread(target=run_server).start()
Thread(target=check_sakani).start()
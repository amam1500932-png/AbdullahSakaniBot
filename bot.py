import os
import telebot
from flask import Flask
from threading import Thread
import requests
import time

# --- 1. إعداد سيرفر Flask الصغير لإرضاء منصة Render ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive"

def run():
    # Render يعطي المنفذ تلقائياً في متغير البيئة PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعدادات البوت ---
TOKEN = "ضع_هنا_توكن_البوت"
CHAT_ID = "ضع_هنا_ايدي_حسابك"
bot = telebot.TeleBot(TOKEN)

# --- 3. وظيفة مراقبة سكني ---
def monitor_sakani():
    url = "https://sakani.sa/app/land-projects"
    last_content = ""
    print("بدأ فحص موقع سكني...")
    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # نتحقق من وجود تغيير في الصفحة
                if response.text != last_content and last_content != "":
                    bot.send_message(CHAT_ID, f"⚠️ تنبيه: حدث تغيير في أراضي سكني!\nالرابط: {url}")
                last_content = response.text
        except Exception as e:
            print(f"Error in monitor: {e}")
        time.sleep(300) # فحص كل 5 دقائق

# --- 4. تشغيل كل شيء ---
if __name__ == "__main__":
    # تشغيل السيرفر الوهمي
    keep_alive()
    
    # تشغيل خيط المراقبة
    monitor_thread = Thread(target=monitor_sakani)
    monitor_thread.start()
    
    # تشغيل استقبال أوامر تلجرام
    print("البوت يعمل الآن...")
    bot.polling(none_stop=True)

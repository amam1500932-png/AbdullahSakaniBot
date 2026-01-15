import os
import telebot
from flask import Flask
from threading import Thread
import requests
import time

# --- إعدادات البوت ---
TOKEN = "ضع_هنا_توكن_البوت"
CHAT_ID = "ضع_هنا_ايدي_حسابك"

# --- إعداد سيرفر Flask (لإبقاء البوت حياً على Render) ---
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل الآن بنجاح!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- برمجة البوت ومراقبة سكني ---
bot = telebot.TeleBot(TOKEN)

def monitor_sakani():
    url = "https://sakani.sa/app/land-projects"
    last_content = ""
    while True:
        try:
            # محاكاة متصفح حقيقي
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200 and response.text != last_content:
                bot.send_message(CHAT_ID, f"⚠️ تحديث جديد في أراضي سكني!\nالرابط: {url}")
                last_content = response.text
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(600) # فحص كل 10 دقائق

# تشغيل السيرفر والبوت
if __name__ == "__main__":
    keep_alive() # تشغيل الويب سيرفر في الخلفية
    print("بدأ تشغيل البوت...")
    
    # تشغيل مراقبة الموقع في خيط منفصل
    monitor_thread = Thread(target=monitor_sakani)
    monitor_thread.start()
    
    # تشغيل استقبال أوامر تلجرام
    bot.polling(none_stop=True)

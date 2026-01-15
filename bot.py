import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# --- البيانات الخاصة ---
TOKEN = "8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo"
CHAT_ID = "652646153"
URL_SAKANI = "https://sakani.sa/app/land-projects"

app = Flask('')
@app.route('/')
def home(): return "✅ البوت يعمل ومستقر!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

bot = telebot.TeleBot(TOKEN)

# دالة التذكير قبل النزول بـ 10 دقائق
def send_reminder(target_time_str):
    bot.send_message(CHAT_ID, f"⏰ **تذكير يا عبدالله!**\nبقي 10 دقائق على موعد النزول المتوقع ({target_time_str}). ادخل للموقع الآن!")

def monitor_sakani():
    last_state = ""
    last_ping = time.time()
    print("بدأ الفحص...")
    
    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(URL_SAKANI, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                current_state = soup.get_text()

                # رصد التغيير (إلغاء أو إضافة)
                if last_state != "" and current_state != last_state:
                    now = datetime.now() + timedelta(hours=3)
                    target_time = now + timedelta(hours=2)
                    
                    msg = (f"⚠️ **رصد تغيير/إلغاء الآن!**\n\n"
                           f"⏰ وقت الرصد: {now.strftime('%I:%M %p')}\n"
                           f"🚀 **موعد النزول المتوقع:** {target_time.strftime('%I:%M %p')}\n"
                           f"🔗 [رابط الموقع]({URL_SAKANI})")
                    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                    
                    # جدولة التذكير قبل النزول بـ 10 دقائق
                    delay = (target_time - timedelta(minutes=10) - now).total_seconds()
                    if delay > 0:
                        t = Thread(target=lambda: (time.sleep(delay), send_reminder(target_time.strftime('%I:%M %p'))))
                        t.start()

                last_state = current_state

            # رسالة طمأنينة كل 10 دقائق
            if time.time() - last_ping >= 600:
                bot.send_message(CHAT_ID, "🔍 أنا أعمل على الفحص يا عبدالله، ولا يوجد أي تطور حالياً.")
                last_ping = time.time()

        except Exception as e: print(f"Error: {e}")
        time.sleep(60)

# --- التشغيل الصحيح لإصلاح التوقف ---
if __name__ == "__main__":
    # 1. تنظيف أي جلسة قديمة (حل مشكلة عدم الرد)
    bot.remove_webhook()
    
    # 2. تشغيل سيرفر الويب
    Thread(target=run_flask).start()
    
    # 3. تشغيل المراقبة
    Thread(target=monitor_sakani).start()
    
    # 4. بدء استقبال الرسائل (Start/Test)
    print("البوت جاهز للاستقبال...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

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
def home(): return "✅ نظام المراقبة المطور يعمل!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

bot = telebot.TeleBot(TOKEN)

# دالة لإرسال تذكير بعد وقت محدد
def schedule_reminder(wait_seconds, message_text):
    time.sleep(wait_seconds)
    bot.send_message(CHAT_ID, message_text, parse_mode='Markdown')

def monitor_sakani():
    print("بدأ نظام الرصد المطور...")
    last_state = ""
    last_ping_time = time.time()
    
    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(URL_SAKANI, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                current_state = soup.get_text()

                # 1. رصد التغيير الفوري (إلغاء أو إضافة)
                if last_state != "" and current_state != last_state:
                    now = datetime.now() + timedelta(hours=3) # توقيت السعودية
                    target_time = now + timedelta(hours=2) # موعد النزول المتوقع
                    reminder_time = target_time - timedelta(minutes=10) # التذكير قبل بـ 10 دقائق
                    
                    msg = (f"⚠️ **تنبيه: رصد تغيير/إلغاء الآن!**\n\n"
                           f"⏰ وقت الرصد: {now.strftime('%I:%M %p')}\n"
                           f"🚀 **موعد النزول المتوقع:** {target_time.strftime('%I:%M %p')}\n"
                           f"🔔 سأقوم بتذكيرك قبل النزول بـ 10 دقائق.")
                    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                    
                    # جدولة التذكير قبل النزول بـ 10 دقائق في خيط منفصل
                    seconds_to_reminder = (reminder_time - now).total_seconds()
                    if seconds_to_reminder > 0:
                        rem_msg = f"⏰ **تذكير يا عبدالله!**\nبقي 10 دقائق على موعد النزول المتوقع ({target_time.strftime('%I:%M %p')}). ادخل للموقع الآن!"
                        Thread(target=schedule_reminder, args=(seconds_to_reminder, rem_msg)).start()

                last_state = current_state

            # 2. إرسال رسالة طمأنينة كل 10 دقائق
            if time.time() - last_ping_time >= 600: # 600 ثانية = 10 دقائق
                bot.send_message(CHAT_ID, "🔍 أنا أعمل على الفحص يا عبدالله، ولا يوجد أي تطور حالياً. سأخبرك فور حدوث أي شيء.")
                last_ping_time = time.time()

        except Exception as e:
            print(f"خطأ في الفحص: {e}")
        
        time.sleep(60) # فحص كل دقيقة لضمان السرعة

if __name__ == "__main__":
    Thread(target=run).start()
    bot.remove_webhook()
    Thread(target=monitor_sakani).start()
    bot.infinity_polling()

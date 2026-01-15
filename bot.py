import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# --- البيانات ---
TOKEN = "8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo"
CHAT_ID = "-1003269925362"
URL_SAKANI = "https://sakani.sa/app/land-projects"

app = Flask('')
@app.route('/')
def home(): return "✅ النظام يعمل بكامل طاقته!"

bot = telebot.TeleBot(TOKEN)

# --- 1. ميزة الرد على رسائلك (تم إصلاحها) ---
@bot.message_handler(commands=['start', 'test'])
def send_welcome(message):
    bot.reply_to(message, "🚀 أهلاً عبدالله! أنا استجيب لك الآن.\nنظام المراقبة والرصد يعمل في الخلفية وسأخبرك فور حدوث أي إلغاء.")

# --- 2. ميزة التذكير بـ 10 دقائق ---
def send_reminder(target_time_str):
    try:
        bot.send_message(CHAT_ID, f"⏰ **تذكير يا عبدالله!**\nبقي 10 دقائق على موعد النزول المتوقع ({target_time_str}). ادخل للموقع الآن!")
    except: pass

# --- 3. ميزة المراقبة والرصد ---
def monitor_sakani():
    last_state = ""
    last_ping = time.time()
    
    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(URL_SAKANI, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                current_state = soup.get_text()

                # رصد الإلغاء/التغيير
                if last_state != "" and current_state != last_state:
                    now = datetime.now() + timedelta(hours=3) # توقيت السعودية
                    target_time = now + timedelta(hours=2) # موعد النزول
                    
                    msg = (f"⚠️ **تنبيه: رصد إلغاء/تغيير الآن!**\n\n"
                           f"⏰ وقت الرصد: {now.strftime('%I:%M %p')}\n"
                           f"🚀 **موعد النزول المتوقع:** {target_time.strftime('%I:%M %p')}\n"
                           f"🔗 [رابط الموقع]({URL_SAKANI})")
                    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                    
                    # جدولة التذكير
                    delay = (target_time - timedelta(minutes=10) - now).total_seconds()
                    if delay > 0:
                        Thread(target=lambda: (time.sleep(delay), send_reminder(target_time.strftime('%I:%M %p')))).start()

                last_state = current_state

            # رسالة الطمأنينة كل 10 دقائق
            if time.time() - last_ping >= 600:
                bot.send_message(CHAT_ID, "🔍 أنا أعمل على الفحص يا عبدالله، ولا يوجد أي تطور حالياً.")
                last_ping = time.time()

        except Exception as e: print(f"Error: {e}")
        time.sleep(60)

# --- 4. التشغيل الصحيح (السر هنا) ---
if __name__ == "__main__":
    bot.remove_webhook() # تنظيف الجلسات العالقة
    time.sleep(1)
    
    # تشغيل السيرفر والمراقبة في خيوط منفصلة
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    Thread(target=monitor_sakani).start()
    
    # تشغيل استقبال الرسائل في الخيط الرئيسي لضمان الاستجابة
    print("البوت جاهز...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# --- بياناتك ---
TOKEN = "8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo"
CHAT_ID = "652646153"
URL_SAKANI = "https://sakani.sa/app/land-projects"

app = Flask('')
@app.route('/')
def home(): return "✅ البوت المطور يعمل!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

bot = telebot.TeleBot(TOKEN)

# --- دالة المراقبة الذكية للإلغاء ---
def monitor_sakani():
    print("بدأ نظام رصد الإلغاء المبكر...")
    # حفظ الحالة الأخيرة للنصوص والأرقام
    last_state = ""
    
    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(URL_SAKANI, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                current_state = soup.get_text()

                # إذا تغير محتوى الصفحة (نقص عدد المحجوز أو تغير نص)
                if last_state != "" and current_state != last_state:
                    now = datetime.now() + timedelta(hours=3) # توقيت السعودية
                    target_time = now + timedelta(hours=2) # موعد النزول المتوقع
                    
                    msg = (f"⚠️ **رصد إلغاء محتمل!**\n\n"
                           f"تغيرت بيانات المخططات الآن. إذا كان هذا إلغاءً لقطعة:\n"
                           f"⏰ وقت الإلغاء: {now.strftime('%I:%M %p')}\n"
                           f"🚀 **موعد النزول المتوقع:** {target_time.strftime('%I:%M %p')}\n\n"
                           f"جهز نفسك للدخول بعد ساعتين!")
                    
                    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                
                last_state = current_state
        except Exception as e:
            print(f"خطأ: {e}")
        
        time.sleep(60) # فحص كل دقيقة لرصد اللحظة بدقة

if __name__ == "__main__":
    Thread(target=run).start()
    bot.remove_webhook()
    # تشغيل المراقبة
    Thread(target=monitor_sakani).start()
    bot.infinity_polling()

import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup

# --- 1. البيانات الخاصة ---
TOKEN = "8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo"
CHAT_ID = "652646153"
URL_SAKANI = "https://sakani.sa/app/land-projects"

# --- 2. سيرفر Flask لإبقاء البوت حياً ---
app = Flask('')

@app.route('/')
def home():
    return "✅ البوت يعمل ومستقر الآن!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 3. إعداد البوت والرد الآلي ---
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'test'])
def send_welcome(message):
    bot.reply_to(message, "🚀 أهلاً عبدالله! أنا الآن أعمل وأراقب أراضي سكني بدقة.\nسأرسل لك تفاصيل القطع فور توفرها.")

# --- 4. ميزة مراقبة صفحة سكني واستخراج النصوص ---
def monitor_sakani():
    print("بدأت عملية المراقبة...")
    last_lands = set()
    
    while True:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
            }
            response = requests.get(URL_SAKANI, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                current_lands = []
                
                # البحث عن أي نصوص داخل مربعات المشاريع
                projects = soup.find_all(['h3', 'div', 'span'], class_=lambda x: x and ('card' in x or 'project' in x))
                for p in projects:
                    text = p.get_text(strip=True)
                    if text: current_lands.append(text)

                # تنبيه في حال وجود شيء جديد
                for land in current_lands:
                    if land not in last_lands and len(last_lands) > 0:
                        msg = f"🆕 **تنبيه: تم رصد تحديث في سكني!**\n\n📍 **التفاصيل:**\n{land}\n\n🔗 **الرابط:** {URL_SAKANI}"
                        bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                
                last_lands = set(current_lands)
        except Exception as e:
            print(f"خطأ فحص: {e}")
        
        time.sleep(180) # فحص كل 3 دقائق

# --- 5. التشغيل النهائي وحل مشكلة التعارض ---
if __name__ == "__main__":
    # تشغيل السيرفر
    Thread(target=run).start()
    
    # تشغيل المراقبة
    monitor_thread = Thread(target=monitor_sakani)
    monitor_thread.start()
    
    # الحل السحري لمشكلة Conflict التي ظهرت في الصور
    bot.remove_webhook() 
    print("تم تنظيف الجلسات القديمة.. البوت يستمع الآن.")
    
    # بدء الاستماع للرسائل
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

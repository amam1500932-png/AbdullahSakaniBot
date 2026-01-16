import requests
import telebot
import time
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Elite Monitoring Active"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

PROJECT_ID = "584"
API_URL = f"https://sakani.sa/api/v1/land-projects/{PROJECT_ID}/units_summary"
URL_SAKANI = f"https://sakani.sa/app/land-projects/{PROJECT_ID}"

last_available_count = None
last_heartbeat_time = time.time()

def check_sakani_final():
    global last_available_count, last_heartbeat_time
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        # إضافة متغير عشوائي لتجاوز الكاش
        response = requests.get(f"{API_URL}?t={time.time()}", headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # استخراج العدد الفعلي للأراضي المتاحة
            current_available = data.get('available_units_count', 0)
            
            # 1. إرسال العدد الحالي عند أول تشغيل
            if last_available_count is None:
                last_available_count = current_available
                bot.send_message(CHAT_ID, f"✅ تم بدء الرادار بنجاح.\n📊 العدد المتوفر حالياً في المخطط: {current_available}")
                return

            # 2. رصد الزيادة (إلغاء حجز)
            if current_available > last_available_count:
                diff = current_available - last_available_count
                bot.send_message(CHAT_ID, f"✨ **عاجل: توفرت {diff} أرض جديدة!**\n📊 الإجمالي الآن: {current_available}\n🔗 {URL_SAKANI}")
                last_available_count = current_available
            
            # 3. رصد النقص (حجز جديد)
            elif current_available < last_available_count:
                diff = last_available_count - current_available
                bot.send_message(CHAT_ID, f"🚫 **تم حجز {diff} أرض.**\n📊 المتبقي الآن: {current_available}")
                last_available_count = current_available

        # 4. رسالة "أنا أعمل" كل 10 دقائق (600 ثانية)
        current_time = time.time()
        if current_time - last_heartbeat_time >= 600:
            bot.send_message(CHAT_ID, f"🤖 نظام الرادار يعمل بنشاط...\n📊 العدد الحالي للأراضي: {last_available_count if last_available_count is not None else 'جاري الفحص'}")
            last_heartbeat_time = current_time

    except Exception as e:
        print(f"Error: {e}")

def bot_loop():
    while True:
        check_sakani_final()
        time.sleep(30) # فحص سريع كل 30 ثانية

if __name__ == "__main__":
    Thread(target=run).start()
    bot_loop()

import requests
import telebot
import time
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Final Radar Active"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

PROJECT_ID = "584"
API_URL = f"https://sakani.sa/api/v1/land-projects/{PROJECT_ID}/units_summary"

last_available_count = None
last_heartbeat_time = time.time()

def check_sakani():
    global last_available_count, last_heartbeat_time
    
    # رأسية طلب (Headers) مطابقة تماماً لمتصفح كروم حقيقي
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
        'Referer': 'https://sakani.sa/app/land-projects/584',
        'Origin': 'https://sakani.sa',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    try:
        # استخدام رابط مباشر مع رقم عشوائي لمنع الكاش
        response = requests.get(f"{API_URL}?cache_bust={int(time.time())}", headers=headers, timeout=25)
        
        if response.status_code == 200:
            data = response.json()
            current_available = data.get('available_units_count', 0)
            
            if last_available_count is None:
                last_available_count = current_available
                bot.send_message(CHAT_ID, f"🏁 **تم الاتصال بنجاح!**\n📊 العدد الحالي للأراضي المكتشفة: {current_available}")
                return

            if current_available > last_available_count:
                bot.send_message(CHAT_ID, f"✨ **تنبيه: توفرت أرض جديدة!**\n📊 المجموع: {current_available}")
                last_available_count = current_available
            elif current_available < last_available_count:
                bot.send_message(CHAT_ID, f"🚫 **تنبيه: تم حجز أرض.**\n📊 المتبقي: {current_available}")
                last_available_count = current_available
        
        # إذا رفض السيرفر (مثل خطأ 403 أو 429) سيعطيك تنبيه
        elif response.status_code in [403, 429]:
             print("Sakani is blocking the request. Need to wait.")

        # رسالة كل 10 دقائق
        if time.time() - last_heartbeat_time >= 600:
            bot.send_message(CHAT_ID, f"🤖 الرادار يعمل بنشاط...\n📊 العدد الحالي: {last_available_count if last_available_count is not None else 'قيد الانتظار'}")
            last_heartbeat_time = time.time()

    except Exception as e:
        print(f"Connection Error: {e}")

def bot_loop():
    # إرسال رسالة فورية عند تشغيل الكود ليطمئن المستخدم
    bot.send_message(CHAT_ID, "🚀 البوت بدأ التشغيل على Render وهو الآن يحاول الاتصال بسيرفر سكني...")
    while True:
        check_sakani()
        time.sleep(40) # فحص كل 40 ثانية

if __name__ == "__main__":
    Thread(target=run).start()
    bot_loop()

import requests
import telebot
import time
import os
import re
from flask import Flask
from threading import Thread

# خادم الويب لضمان استمرار الخدمة على Render
app = Flask('')
@app.route('/')
def home(): return "Sakani Elite Radar Active"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# إعدادات البوت والقناة
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# روابط المخطط
PROJECT_ID = "584"
URL_SAKANI = f"https://sakani.sa/app/land-projects/{PROJECT_ID}"
MAP_LINK = f"https://sakani.sa/app/land-projects/{PROJECT_ID}/map"

last_count = None

def check_sakani_elite():
    global last_count
    # استخدام جسر AllOrigins لتخطي الحماية
    bridge_url = f"https://api.allorigins.win/get?url={URL_SAKANI}&ts={time.time()}"
    
    try:
        response = requests.get(bridge_url, timeout=25)
        if response.status_code == 200:
            content = response.json().get('contents', '')
            
            # البحث عن أرقام الأراضي أو الوحدات المتاحة في الكود المصدري
            found_lands = re.findall(r'unit_id":(\d+)|"id":(\d+)|"land_number":"(.*?)"', content)
            current_count = len(set(found_lands))
            
            if last_count is None:
                last_count = current_count
                return

            # حالة 1: توفرت أراضي جديدة (شخص ألغى حجز)
            if current_count > last_count:
                diff = current_count - last_count
                msg = (f"✨ **عاجل: توفرت {diff} قطعة أرض جديدة!**\n"
                       f"📍 المخطط: {PROJECT_ID}\n"
                       f"📊 العدد الإجمالي الحالي: {current_count}\n\n"
                       f"⚠️ **ملاحظة عبدالله**: قد يستغرق ظهورها في الخريطة ساعتين من الآن.\n\n"
                       f"🔗 رابط المخطط: {URL_SAKANI}\n"
                       f"🗺 رابط الخريطة: {MAP_LINK}")
                bot.send_message(CHAT_ID, msg)
                last_count = current_count
            
            # حالة 2: تم حجز قطعة أرض
            elif current_count < last_count:
                diff = last_count - current_count
                msg = (f"🚫 **تنبيه: تم حجز {diff} قطعة أرض.**\n"
                       f"📉 العدد المتبقي: {current_count}\n"
                       f"🔗 تابع المخطط من هنا: {URL_SAKANI}")
                bot.send_message(CHAT_ID, msg)
                last_count = current_count
                
    except Exception as e:
        print(f"Error in checking: {e}")

def bot_loop():
    bot.send_message(CHAT_ID, "🚀 تم تشغيل الرادار الشامل للمخطط 584.\nسأرصد الإلغاء والحجز وأزودك بالروابط فوراً.")
    while True:
        check_sakani_elite()
        time.sleep(60) # فحص دقيق كل دقيقة

if __name__ == "__main__":
    Thread(target=run).start()
    bot_loop()

import requests
import telebot
import time
import os
import re
from flask import Flask
from threading import Thread

# 1. إعداد خادم الويب للبقاء حياً على Render
app = Flask('')
@app.route('/')
def home(): return "Multi-Feature Radar is Active"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. إعدادات التليجرام
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# 3. بيانات المخطط 584 وروابط التجاوز
URL_SAKANI = "https://sakani.sa/app/land-projects/584"
MAP_LINK = "https://sakani.sa/app/land-projects/584/map"
# جسر AllOrigins لتخطي الحظر
BRIDGE_URL = "https://api.allorigins.win/get?url="

last_count = None
last_heartbeat = time.time()

def fetch_data_securely():
    """محاولة جلب البيانات عبر جسر خارجي لتغيير الـ IP وتخطي الحجب"""
    try:
        # إضافة توقيت عشوائي لمنع الكاش
        target = f"{URL_SAKANI}?t={int(time.time())}"
        response = requests.get(f"{BRIDGE_URL}{target}", timeout=35)
        
        if response.status_code == 200:
            content = response.json().get('contents', '')
            # البحث عن عدد الوحدات المتاحة في كود الصفحة (برمجي ونصي)
            match = re.search(r'available_units_count["\s:]+(\d+)', content)
            if match:
                return int(match.group(1))
        return None
    except Exception as e:
        print(f"Fetch Error: {e}")
        return None

def bot_loop():
    global last_count, last_heartbeat
    bot.send_message(CHAT_ID, "🛡️ **بدء تشغيل الرادار الشامل...**\nجاري محاولة تجاوز الحجب وجلب البيانات.")
    
    while True:
        current = fetch_data_securely()
        
        if current is not None:
            # أول قراءة ناجحة
            if last_count is None:
                last_count = current
                bot.send_message(CHAT_ID, f"🎯 **تم الاتصال بنجاح!**\n📊 العدد الحالي للأراضي المتاحة: {current}\n✅ تم تفعيل كل المميزات (رصد الإلغاء والحجز).")
            
            # حالة توفر أرض جديدة (إلغاء من شخص آخر)
            elif current > last_count:
                diff = current - last_count
                msg = (f"✨ **عاجل: توفرت {diff} أرض جديدة!**\n"
                       f"📊 الإجمالي الآن: {current}\n"
                       f"⚠️ **ملاحظة**: قد يستغرق ظهورها في الخريطة ساعتين.\n\n"
                       f"🔗 المخطط: {URL_SAKANI}\n"
                       f"🗺 الخريطة: {MAP_LINK}")
                bot.send_message(CHAT_ID, msg)
                last_count = current
            
            # حالة حجز أرض
            elif current < last_count:
                diff = last_count - current
                bot.send_message(CHAT_ID, f"🚫 **تنبيه: تم حجز {diff} أرض.**\n📊 المتبقي الآن: {current}")
                last_count = current

        # رسالة الطمأنة كل 10 دقائق
        if time.time() - last_heartbeat >= 600:
            status_text = f"📊 العدد الحالي: {last_count}" if last_count is not None else "⚠️ لا زال الحظر مستمراً"
            bot.send_message(CHAT_ID, f"🤖 **الرادار يعمل بنشاط...**\n{status_text}")
            last_heartbeat = time.time()
            
        time.sleep(60) # فحص كل دقيقة لضمان استقرار الاتصال

if __name__ == "__main__":
    # تشغيل خادم الويب والفحص في وقت واحد
    Thread(target=run).start()
    bot_loop()

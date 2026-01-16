import requests
import telebot
import time
import os
import re
from flask import Flask
from threading import Thread

# 1. نظام الحماية من التوقف (Keep-Alive)
app = Flask('')
@app.route('/')
def home(): return "Elite Sakani Radar is Active"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. إعدادات البوت والقناة
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# بيانات المخطط 584
PROJECT_ID = "584"
URL_SAKANI = f"https://sakani.sa/app/land-projects/{PROJECT_ID}"
MAP_LINK = f"https://sakani.sa/app/land-projects/{PROJECT_ID}/map"
API_URL = f"https://sakani.sa/api/v1/land-projects/{PROJECT_ID}/units_summary"

last_count = None
last_heartbeat = time.time()

def fetch_data():
    """محاولة جلب البيانات بأكثر من طريقة لتجاوز حظر سكني"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': URL_SAKANI
    }
    try:
        # المحاولة الأولى: الرابط المباشر للبيانات
        res = requests.get(f"{API_URL}?t={int(time.time())}", headers=headers, timeout=20)
        if res.status_code == 200:
            return res.json().get('available_units_count')
        
        # المحاولة الثانية: قراءة كود الصفحة إذا فشل الرابط المباشر
        res_page = requests.get(f"{URL_SAKANI}?t={int(time.time())}", headers=headers, timeout=20)
        if res_page.status_code == 200:
            match = re.search(r'available_units_count["\s:]+(\d+)', res_page.text)
            if match: return int(match.group(1))
            
        return None
    except:
        return None

def bot_loop():
    global last_count, last_heartbeat
    bot.send_message(CHAT_ID, "🚀 **انطلاق الرادار الشامل (النسخة النهائية)**\nيتم الآن محاولة جلب أول قراءة للمخطط 584...")
    
    while True:
        current = fetch_data()
        
        if current is not None:
            # أول قراءة بعد التشغيل
            if last_count is None:
                last_count = current
                bot.send_message(CHAT_ID, f"🎯 **تم الاتصال بنجاح!**\n📊 العدد الحالي للأراضي: {current}\n✅ الرادار الآن يراقب الزيادة والنقصان.")
            
            # حالة التوفر (إلغاء حجز)
            elif current > last_count:
                diff = current - last_count
                msg = (f"✨ **عاجل: توفرت {diff} أرض جديدة!**\n"
                       f"📊 الإجمالي المتاح: {current}\n"
                       f"⚠️ **تنبيه عبدالله**: قد تظهر في الخريطة بعد ساعتين.\n\n"
                       f"🔗 المخطط: {URL_SAKANI}\n"
                       f"🗺 الخريطة: {MAP_LINK}")
                bot.send_message(CHAT_ID, msg)
                last_count = current
            
            # حالة الحجز
            elif current < last_count:
                diff = last_count - current
                bot.send_message(CHAT_ID, f"🚫 **تنبيه: تم حجز {diff} أرض.**\n📊 المتبقي الآن: {current}")
                last_count = current
        
        # رسالة الطمأنة كل 10 دقائق
        if time.time() - last_heartbeat >= 600:
            status_text = f"📊 العدد: {last_count}" if last_count is not None else "⚠️ فشل جلب الرقم"
            bot.send_message(CHAT_ID, f"🤖 **نظام الرادار يعمل بنشاط...**\n{status_text}")
            last_heartbeat = time.time()
            
        time.sleep(40) # فحص متوازن كل 40 ثانية

if __name__ == "__main__":
    Thread(target=run).start()
    bot_loop()

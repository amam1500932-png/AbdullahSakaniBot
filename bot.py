import requests
import telebot
import time
import os
import random
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Advanced Deep Radar Active"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# الروابط والمخطط
PROJECT_ID = "584"
URL_SAKANI = f"https://sakani.sa/app/land-projects/{PROJECT_ID}"
MAP_LINK = f"https://sakani.sa/app/land-projects/{PROJECT_ID}/map"
# رابط بيانات تطبيق الجوال (أكثر دقة وأقل حظراً)
DEEP_API = f"https://sakani.sa/api/v1/land-projects/{PROJECT_ID}/units_summary"

last_count = None
last_heartbeat = time.time()

def fetch_data_advanced():
    """محاكاة تصفح حقيقية جداً لتجاوز الحماية"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ar-SA,ar;q=0.9',
        'Origin': 'https://sakani.sa',
        'Referer': URL_SAKANI,
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        # إضافة باراميتر عشوائي لتجاوز كاش السيرفر
        response = requests.get(f"{DEEP_API}?v={random.randint(100,999)}", headers=headers, timeout=25)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('available_units_count')
        return None
    except:
        return None

def bot_loop():
    global last_count, last_heartbeat
    bot.send_message(CHAT_ID, "🚀 **تفعيل الرادار العميق (محاكاة الجوال)...**\nجاري محاولة تجاوز الحظر الأخير.")
    
    while True:
        current = fetch_data_advanced()
        
        if current is not None:
            if last_count is None:
                last_count = current
                bot.send_message(CHAT_ID, f"🎯 **نجح الاختراق!**\n📊 العدد الحالي: {current}\n✅ الرادار يراقب الزيادة والنقصان الآن.")
            
            elif current > last_count:
                diff = current - last_count
                bot.send_message(CHAT_ID, f"✨ **عاجل: توفرت {diff} أرض جديدة!**\n📊 الإجمالي: {current}\n⚠️ قد تظهر في الخريطة بعد ساعتين.\n\n🔗 {URL_SAKANI}")
                last_count = current
            
            elif current < last_count:
                diff = last_count - current
                bot.send_message(CHAT_ID, f"🚫 **تنبيه: حجز أرض.**\n📊 المتبقي: {current}")
                last_count = current
        
        if time.time() - last_heartbeat >= 600:
            status = f"📊 العدد: {last_count}" if last_count is not None else "⚠️ الحماية لا تزال نشطة"
            bot.send_message(CHAT_ID, f"🤖 **الرادار يعمل...**\n{status}")
            last_heartbeat = time.time()
            
        # وقت فحص عشوائي قليلاً لتجنب اكتشاف البوت
        time.sleep(random.randint(40, 60))

if __name__ == "__main__":
    Thread(target=run).start()
    bot_loop()

import requests
import telebot
import time
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "API Radar Active"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# هذا الرابط يحاول سحب البيانات الخام مباشرة من نظام سكني
API_URL = "https://sakani.sa/api/v1/land-projects/584/units_summary"

last_available_count = None

def check_sakani_api():
    global last_available_count
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        # محاولة الوصول للبيانات الخام
        response = requests.get(API_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # استخراج عدد الوحدات المتاحة من داخل ملف البيانات
            current_available = data.get('available_units_count', 0)
            
            if last_available_count is None:
                last_available_count = current_available
                return

            if current_available > last_available_count:
                bot.send_message(CHAT_ID, f"✨ **تنبيه ذكي: توفرت أرض!**\nالعدد الحالي المتاح: {current_available}\nسارع للدخول: https://sakani.sa/app/land-projects/584")
            elif current_available < last_available_count:
                bot.send_message(CHAT_ID, f"🚫 **تنبيه ذكي: تم حجز أرض.**\nالمتبقي: {current_available}")
            
            last_available_count = current_available
    except:
        # في حال فشل الرابط المباشر، نعود للطريقة السابقة تلقائياً
        pass

def bot_loop():
    bot.send_message(CHAT_ID, "🎯 تم تفعيل (رادار البيانات المباشرة).\nهذا النظام يراقب الأرقام من خلف الكواليس.")
    while True:
        check_sakani_api()
        time.sleep(45)

if __name__ == "__main__":
    Thread(target=run).start()
    bot_loop()

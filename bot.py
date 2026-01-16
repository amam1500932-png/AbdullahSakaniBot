import requests
import telebot
import time
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Final Proxy Shield Active"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# رابط جسر خارجي يحاول جلب البيانات من زاوية مختلفة
# هذا الرابط يستخدم بروكسي مجاني مدمج
PROXY_BRIDGE = "https://api.codetabs.com/v1/proxy?quest="
TARGET_URL = "https://sakani.sa/api/v1/land-projects/584/units_summary"

last_count = None
last_heart = time.time()

def fetch_data_final_attempt():
    try:
        # محاولة الطلب عبر البروكسي المجاني لتغيير الـ IP
        full_url = f"{PROXY_BRIDGE}{TARGET_URL}"
        response = requests.get(full_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('available_units_count')
        return None
    except:
        return None

def bot_loop():
    global last_count, last_heart
    bot.send_message(CHAT_ID, "⚠️ **محاولة كسر الحماية عبر جسر (Proxy Shield)...**")
    
    while True:
        current = fetch_data_final_attempt()
        
        if current is not None:
            if last_count is None:
                last_count = current
                bot.send_message(CHAT_ID, f"🎯 **نجح الاختراق!**\n📊 العدد الحالي: {current}\n✅ الرادار مدمج به كل المميزات الآن.")
            elif current > last_count:
                bot.send_message(CHAT_ID, f"✨ **عاجل: توفرت أرض!**\n📊 المجموع: {current}\n🔗 https://sakani.sa/app/land-projects/584")
                last_count = current
            elif current < last_count:
                bot.send_message(CHAT_ID, f"🚫 **تنبيه: حجز أرض.**\n📊 المتبقي: {current}")
                last_count = current
        
        if time.time() - last_heart >= 600:
            status = f"📊 العدد: {last_count}" if last_count is not None else "⚠️ الحظر مستمر حتى مع البروكسي"
            bot.send_message(CHAT_ID, f"🤖 الرادار يعمل...\n{status}")
            last_heart = time.time()
            
        time.sleep(45)

if __name__ == "__main__":
    Thread(target=run).start()
    bot_loop()

import requests
import telebot
import time
import re
from flask import Flask
from threading import Thread
import os

# خادم الويب لإبقاء البوت حياً
app = Flask('')
@app.route('/')
def home(): return "Radar is Online"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# إعدادات البوت
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

URL_SAKANI = "https://sakani.sa/app/land-projects/584"
last_known_count = None

def check_sakani_ultra_fast():
    global last_known_count
    # استخدام جسر AllOrigins للوصول للبيانات اللحظية وتجاوز حظر Render
    bridge_url = f"https://api.allorigins.win/get?url={URL_SAKANI}"

    try:
        response = requests.get(bridge_url, timeout=20)
        if response.status_code == 200:
            content = response.json().get('contents', '')
            # البحث عن أي أرقام تدل على الوحدات في الكود المصدري
            found_units = re.findall(r'unit_id":(\d+)|"id":(\d+)|"land_number":"(.*?)"', content)
            current_count = len(set(found_units))

            if last_known_count is None:
                last_known_count = current_count
                print(f"تم بدء الرادار السريع. العدد الحالي: {current_count}")
                return

            # رصد أي تغيير في العدد
            if current_count != last_known_count:
                if current_count > last_known_count:
                    bot.send_message(CHAT_ID, f"✨ **عاجل: قطعة أرض توفرت الآن!**\nالعدد زاد إلى: {current_count}\n🔗 {URL_SAKANI}")
                else:
                    bot.send_message(CHAT_ID, f"🚫 **تم حجز قطعة أرض.**\nالعدد الحالي: {current_count}")
                last_known_count = current_count
    except Exception as e:
        print(f"Error: {e}")

def bot_loop():
    bot.send_message(CHAT_ID, "⚡️ تم تفعيل الرادار السريع (فحص كل 30 ثانية).\nسأقوم الآن برصد حجزك الأخير.")
    while True:
        check_sakani_ultra_fast()
        time.sleep(30) # فحص سريع جداً

if __name__ == "__main__":
    Thread(target=run).start()
    bot_loop()

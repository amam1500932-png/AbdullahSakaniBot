import requests
import telebot
import time
import re
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# 1. إعداد خادم ويب وهمي لمنع Render من إغلاق البوت
app = Flask('')
@app.route('/')
def home():
    return "البوت يعمل بنجاح!"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# 2. إعدادات البوت
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

URL_SAKANI = "https://sakani.sa/app/land-projects/584"
last_known_count = None

def check_sakani_logic():
    global last_known_count
    search_url = f"https://www.google.com/search?q={URL_SAKANI}"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # استخراج كافة الأرقام التي قد تدل على قطع أو مؤشرات
            current_units = re.findall(r'\d{3,4}', soup.get_text())
            current_count = len(set(current_units))

            if last_known_count is None:
                last_known_count = current_count
                return

            if current_count != last_known_count:
                msg = "🚨 **تنبيه: رصد تغيير رقمي في المخطط 584!**"
                if current_count > last_known_count:
                    msg += "\n✨ احتمال: قطعة أرض توفرت الآن (إلغاء حجز)."
                else:
                    msg += "\n🚫 احتمال: تم حجز قطعة جديدة."
                
                bot.send_message(CHAT_ID, msg)
                last_known_count = current_count
    except Exception as e:
        print(f"Error: {e}")

def bot_loop():
    bot.send_message(CHAT_ID, "🚀 تم تفعيل المراقبة الدائمة (نظام الويب + العداد الرقمي).")
    while True:
        check_sakani_logic()
        time.sleep(120) # فحص كل دقيقتين

if __name__ == "__main__":
    # تشغيل خادم الويب في الخلفية
    Thread(target=run_web_server).start()
    # تشغيل حلقة البوت
    bot_loop()

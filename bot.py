import requests
import telebot
import time
import re
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import os

# خادم الويب لإبقاء البوت حياً على Render
app = Flask('')
@app.route('/')
def home(): return "Bot is Active"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# إعدادات البوت
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

URL_SAKANI = "https://sakani.sa/app/land-projects/584"
last_known_count = None

def check_sakani_silent():
    global last_known_count
    # استخدام جسر جوجل للوصول للبيانات المخفية
    search_url = f"https://www.google.com/search?q=site:sakani.sa+{URL_SAKANI}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        if response.status_code == 200:
            # استخراج أرقام القطع والروابط من محتوى البحث
            current_found = re.findall(r'unit/\d+|land-projects/\d+/\d+', response.text)
            current_count = len(set(current_found))

            # أول تشغيل للبوت: يخزن العدد فقط دون إرسال رسالة
            if last_known_count is None:
                last_known_count = current_count
                print(f"تم بدء المراقبة الصامتة. العدد الحالي: {current_count}")
                return

            # إرسال تنبيه فقط عند حدوث تغيير حقيقي
            if current_count > last_known_count:
                bot.send_message(CHAT_ID, f"✨ **عاجل: قطعة أرض توفرت الآن!**\nالعدد زاد من {last_known_count} إلى {current_count}\n🔗 افحص الرابط فوراً:\n{URL_SAKANI}")
                last_known_count = current_count
            elif current_count < last_known_count:
                bot.send_message(CHAT_ID, f"🚫 **تم حجز قطعة أرض.**\nالعدد نقص من {last_known_count} إلى {current_count}")
                last_known_count = current_count

    except Exception as e:
        print(f"خطأ في الفحص الصامت: {e}")

def bot_loop():
    bot.send_message(CHAT_ID, "🔕 تم تفعيل المراقبة الصامتة للمخطط 584.\nسأرسل تنبيهاً فقط عند توفر أرض أو حجزها.")
    while True:
        check_sakani_silent()
        time.sleep(120) # فحص كل دقيقتين

if __name__ == "__main__":
    Thread(target=run).start()
    bot_loop()

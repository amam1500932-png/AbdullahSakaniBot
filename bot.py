import requests
import telebot
import time
from bs4 import BeautifulSoup

# إعدادات البوت
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

URL_SAKANI = "https://sakani.sa/app/land-projects/584"
last_content_hash = None

def check_sakani():
    global last_content_hash
    # جسر جوجل لتجاوز حظر 403
    search_url = f"https://www.google.com/search?q={URL_SAKANI}"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        if response.status_code == 200:
            current_text = BeautifulSoup(response.text, 'html.parser').get_text()
            current_hash = hash(current_text)

            if last_content_hash is None:
                last_content_hash = current_hash
                print("تم بدء المراقبة بنجاح...")
                return

            if current_hash != last_content_hash:
                bot.send_message(CHAT_ID, f"🚨 **تنبيه: تم رصد تغيير في المخطط 584!**\nافحص الرابط الآن: {URL_SAKANI}")
                last_content_hash = current_hash
        else:
            print(f"فشل الجسر كود: {response.status_code}")
    except Exception as e:
        print(f"خطأ: {e}")

# حلقة التكرار لضمان عدم توقف البوت
if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🚀 البوت يعمل الآن بنظام المراقبة المستمرة.")
    while True:
        check_sakani()
        # الانتظار لمدة 5 دقائق بين كل فحص لعدم إجهاد السيرفر
        time.sleep(300) 

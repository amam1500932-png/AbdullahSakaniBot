import requests
import telebot
import time
import re
from bs4 import BeautifulSoup

# إعدادات البوت
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

URL_SAKANI = "https://sakani.sa/app/land-projects/584"
# قائمة الأراضي المسجلة في الذاكرة
last_known_units = set()

def check_sakani_units():
    global last_known_units
    # استخدام محرك البحث كجسر
    search_url = f"https://www.google.com/search?q={URL_SAKANI}"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # البحث عن أي أرقام أو روابط تخص الوحدات (Units)
            # سنقوم باستخراج كافة الأرقام المكونة من 3 خانات فأكثر كدليل على وجود قطع
            current_units = set(re.findall(r'\d{3,4}', soup.get_text()))

            if not last_known_units:
                last_known_units = current_units
                bot.send_message(CHAT_ID, f"✅ تم تحديث الحساسية.\n🔢 رصدت حالياً {len(current_units)} مؤشر أرض.")
                return

            # إذا نقص عدد المؤشرات (يعني حجزت قطعة)
            if len(current_units) < len(last_known_units):
                diff = len(last_known_units) - len(current_units)
                bot.send_message(CHAT_ID, f"🚨 **تنبيه حجز!**\nتم اختفاء {diff} قطعة من المخطط 584.\nهذا يعني أن حجزك تم رصده بنجاح! ✅")
            
            # إذا زاد عدد المؤشرات (يعني إلغاء حجز)
            elif len(current_units) > len(last_known_units):
                bot.send_message(CHAT_ID, "✨ **تنبيه: قطعة أرض توفرت الآن (إلغاء حجز)!**")

            last_known_units = current_units
        else:
            print(f"فشل الجسر: {response.status_code}")
    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🔍 بدأت المراقبة بالعدّاد الرقمي..")
    while True:
        check_sakani_units()
        # تقليل وقت الانتظار لـ دقيقتين لسرعة الاستجابة
        time.sleep(120)

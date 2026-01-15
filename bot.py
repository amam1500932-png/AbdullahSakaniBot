import requests
from bs4 import BeautifulSoup
import telebot
import time
import os

# إعدادات البوت (التوكن ومعرف القناة)
API_TOKEN = '7669528628:AAHj3pXW7W7D6-9T9vR_5N-5Rj2G3b_OQ-E'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# رابط المخطط المحدد الذي أرسلته (مخطط 584)
URL_SAKANI = "https://sakani.sa/app/land-projects/584"

# متغير لتخزين آخر حالة للموقع
last_state = None

def check_sakani():
    global last_state
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(URL_SAKANI, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # سحب النص الخاص بالمخطط للمقارنة
        current_state = soup.get_text()

        if last_state is None:
            last_state = current_state
            bot.send_message(CHAT_ID, "🔍 بدأ رصد مخطط 584.. سأبلغك بأي تغيير فوراً.")
            return

        # إذا حدث أي تغيير في نص الصفحة (حجز أو إلغاء)
        if current_state != last_state:
            last_state = current_state
            msg = (
                "⚠️ **تنبيه: رصد تغيير في مخطط 584!**\n\n"
                f"📅 الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                "⏳ قد يكون هناك إلغاء أو حجز جديد الآن.\n\n"
                f"🔗 رابط المخطط المباشر:\n{URL_SAKANI}"
            )
            bot.send_message(CHAT_ID, msg)
        else:
            # رسالة طمأنينة أن الفحص يعمل
            bot.send_message(CHAT_ID, "🔍 الفحص مستمر لمخطط 584: لا يوجد تغيير حالياً.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sakani()

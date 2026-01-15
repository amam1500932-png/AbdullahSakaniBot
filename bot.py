import requests
from bs4 import BeautifulSoup
import telebot
import time

# التوكن الجديد الذي أرسلته
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# رابط المخطط المحدد (584)
URL_SAKANI = "https://sakani.sa/app/land-projects/584"

def check_sakani():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("جاري محاولة الاتصال وتحديث الحالة...")
        response = requests.get(URL_SAKANI, headers=headers, timeout=20)
        
        if response.status_code == 200:
            # إرسال رسالة للقناة لإثبات أن التوكن الجديد يعمل
            bot.send_message(CHAT_ID, "✅ تم تحديث البوت بالتوكن الجديد.\n🔍 أنا الآن أراقب مخطط 584 بدقة.")
        else:
            print(f"فشل الاتصال بموقع سكني، كود الخطأ: {response.status_code}")

    except Exception as e:
        print(f"حدث خطأ أثناء التشغيل: {e}")

if __name__ == "__main__":
    check_sakani()

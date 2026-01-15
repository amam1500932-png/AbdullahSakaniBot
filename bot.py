import requests
from bs4 import BeautifulSoup
import telebot
import time

# التوكن الصحيح الذي أرسلته
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# رابط المخطط 584
URL_SAKANI = "https://sakani.sa/app/land-projects/584"

def check_sakani():
    # تحديث الـ Headers لتبدو كمتصفح حقيقي لتجنب خطأ 403
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
    }
    
    try:
        print("جاري فحص المخطط بأمان...")
        response = requests.get(URL_SAKANI, headers=headers, timeout=25)
        
        if response.status_code == 200:
            bot.send_message(CHAT_ID, "✅ تم الاتصال بمخطط 584 بنجاح.\n🔍 البوت يراقب أي حجز أو إلغاء الآن.")
        else:
            # إذا استمر الخطأ، سنرسل تنبيهاً للقناة لنعرف السبب
            bot.send_message(CHAT_ID, f"❌ تنبيه: فشل الاتصال بسكني (كود {response.status_code}). سأحاول مجدداً.")
            print(f"خطأ: {response.status_code}")

    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    check_sakani()

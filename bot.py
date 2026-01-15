import cloudscraper
from bs4 import BeautifulSoup
import telebot
import time

# بياناتك الصحيحة
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# الرابط المباشر للمخطط
URL_SAKANI = "https://sakani.sa/app/land-projects/584"

def check_sakani():
    # إنشاء متصفح يحاكي متصفح Chrome على ويندوز 10 تماماً
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        print("محاولة تجاوز الحماية والدخول المباشر...")
        # زيادة وقت الانتظار لضمان تحميل الصفحة
        response = scraper.get(URL_SAKANI, timeout=30)
        
        if response.status_code == 200:
            bot.send_message(CHAT_ID, "✅ اخترقنا الحماية! البوت دخل المخطط 584 بنجاح.\n🔍 المراقبة تعمل الآن.")
        elif response.status_code == 403:
            bot.send_message(CHAT_ID, "⚠️ لا يزال الموقع يحظر السيرفر (403). سأجرب وسيلة أخرى.")
        else:
            bot.send_message(CHAT_ID, f"⚠️ خطأ غير متوقع: {response.status_code}")

    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    check_sakani()

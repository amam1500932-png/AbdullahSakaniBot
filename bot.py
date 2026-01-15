import cloudscraper
from bs4 import BeautifulSoup
import telebot
import time

# معلومات البوت
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# رابط المخطط
URL_SAKANI = "https://sakani.sa/app/land-projects/584"

def check_sakani():
    # إنشاء متصفح وهمي متطور لتجاوز خطأ 403
    scraper = cloudscraper.create_scraper()
    
    try:
        print("محاولة تجاوز الحماية وفحص المخطط...")
        response = scraper.get(URL_SAKANI, timeout=30)
        
        if response.status_code == 200:
            bot.send_message(CHAT_ID, "✅ نجحت في الدخول للمخطط 584!\n🔍 المراقبة تعمل الآن بأمان.")
        else:
            # إرسال تنبيه في حال استمرار الحظر
            bot.send_message(CHAT_ID, f"⚠️ الموقع لا يزال يرفض الدخول (كود {response.status_code})")
            print(f"فشل الاتصال: {response.status_code}")

    except Exception as e:
        print(f"حدث خطأ تقني: {e}")

if __name__ == "__main__":
    check_sakani()

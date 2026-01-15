import cloudscraper
from bs4 import BeautifulSoup
import telebot
import re
import time
import random

# إعدادات البوت
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

URL_SAKANI = "https://sakani.sa/app/land-projects/584"

# ذاكرة البوت للأراضي
last_known_lands = set()

def check_sakani_proxy():
    global last_known_lands
    
    # سنستخدم وسيط خارجي (Free Proxy Bridge) لتغيير عنوان السيرفر
    # هذه الطريقة تجعل سكني يرى طلبنا كأنه قادم من متصفح عادي وليس من Render
    proxy_gateways = [
        "https://api.allorigins.win/get?url=",
        "https://thingproxy.freeboard.io/fetch/"
    ]
    
    selected_proxy = random.choice(proxy_gateways)
    full_proxy_url = f"{selected_proxy}{URL_SAKANI}"
    
    scraper = cloudscraper.create_scraper()
    
    try:
        print(f"محاولة الدخول عبر الوسيط: {selected_proxy}")
        response = scraper.get(full_proxy_url, timeout=30)
        
        # إذا كان الرد ناجحاً (كود 200)
        if response.status_code == 200:
            # معالجة البيانات القادمة من الوسيط
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            
            # البحث عن الروابط والقطع
            all_links = soup.find_all('a', href=True)
            current_lands = {}
            
            for link in all_links:
                href = link['href']
                if '/units/' in href or '/land-projects/584/' in href:
                    nums = re.findall(r'\d+', href)
                    if nums:
                        unit_id = nums[-1]
                        current_lands[unit_id] = f"https://sakani.sa{href}" if href.startswith('/') else href

            current_set = set(current_lands.keys())

            if last_known_lands and current_set != last_known_lands:
                # رصد الإلغاء
                new_ones = current_set - last_known_lands
                for land in new_ones:
                    bot.send_message(CHAT_ID, f"✨ **تم فك حظر أرض جديدة!**\n🔢 رقم القطعة: {land}\n🔗 الرابط المباشر:\n{current_lands[land]}")
                
                # رصد الحجز
                sold_ones = last_known_lands - current_set
                for land in sold_ones:
                    bot.send_message(CHAT_ID, f"🚫 **تم حجز القطعة رقم: {land}**")

            last_known_lands = current_set
            bot.send_message(CHAT_ID, f"✅ تم تجاوز الحظر بنجاح.\n📊 المتاح حالياً: {len(current_set)} قطعة.")
            
        else:
            print(f"لا يزال هناك حظر، كود: {response.status_code}")
            # إذا فشل البروكسي، سنحاول محاولة أخيرة مباشرة
            direct_response = scraper.get(URL_SAKANI, timeout=20)
            if direct_response.status_code == 200:
                 bot.send_message(CHAT_ID, "✅ نجح الاتصال المباشر هذه المرة!")

    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == "__main__":
    check_sakani_proxy()

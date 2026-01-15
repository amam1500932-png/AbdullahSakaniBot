import cloudscraper
from bs4 import BeautifulSoup
import telebot
import re
import time
import random
from datetime import datetime

# بيانات البوت
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

URL_SAKANI = "https://sakani.sa/app/land-projects/584"

# ذاكرة البوت
last_known_lands = {}
reserved_lands_log = {}

def check_sakani_stealth():
    global last_known_lands, reserved_lands_log
    
    # اختيار بصمة متصفح عشوائية في كل مرة لتجاوز حظر 403
    browsers = ['chrome', 'firefox', 'safari']
    current_browser = random.choice(browsers)
    
    scraper = cloudscraper.create_scraper(
        browser={'browser': current_browser, 'platform': 'windows', 'desktop': True}
    )
    
    try:
        # تأخير عشوائي بسيط قبل الطلب لكسر نمط البوت
        time.sleep(random.uniform(2, 5))
        
        response = scraper.get(URL_SAKANI, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            all_links = soup.find_all('a', href=True)
            
            current_lands = {}
            for link in all_links:
                href = link['href']
                if '/units/' in href or '/land-projects/584/' in href:
                    nums = re.findall(r'\d+', href)
                    if nums:
                        unit_number = nums[-1]
                        current_lands[unit_number] = f"https://sakani.sa{href}" if href.startswith('/') else href

            current_set = set(current_lands.keys())
            last_set = set(last_known_lands.keys())

            # رصد حجز أو إلغاء
            if last_set:
                # إلغاء حجز (أرض ظهرت)
                new_ones = current_set - last_set
                for land_id in new_ones:
                    bot.send_message(CHAT_ID, f"✨ **عاجل: قطعة أرض توفرت الآن!**\n🔢 رقم القطعة: {land_id}\n🔗 الرابط:\n{current_lands[land_id]}")
                
                # حجز جديد (أرض اختفت)
                removed_ones = last_set - current_set
                for land_id in removed_ones:
                    reserved_lands_log[land_id] = datetime.now()
                    bot.send_message(CHAT_ID, f"🚫 **تم حجز قطعة أرض: {land_id}**\n⏰ وقت الحجز: {datetime.now().strftime('%H:%M:%S')}")

            last_known_lands = current_lands
            bot.send_message(CHAT_ID, f"🔍 فحص ناجح للمخطط 584.\n✅ متاح: {len(current_set)} أرض.\n🎯 يراقب {len(reserved_lands_log)} قطعة محجوزة.")
        
        else:
            print(f"فشل الاتصال: كود {response.status_code}")
            # إذا استمر 403 سنرسل تنبيهاً واحداً فقط
            if response.status_code == 403:
                bot.send_message(CHAT_ID, "⚠️ تنبيه: الموقع قام بتحديث الحماية (403)، جاري محاولة التجاوز تلقائياً...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sakani_stealth()

import cloudscraper
from bs4 import BeautifulSoup
import telebot
import re
import time
import random

# بيانات البوت
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

URL_SAKANI = "https://sakani.sa/app/land-projects/584"

# ذاكرة البوت لتخزين أرقام القطع
last_known_lands = set()

def check_sakani_stable():
    global last_known_lands
    
    # قائمة بمتصفحات حقيقية ومتنوعة لتجاوز حظر 403
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    scraper = cloudscraper.create_scraper()
    
    try:
        # تأخير عشوائي لتبدو كإنسان
        time.sleep(random.uniform(3, 7))
        
        headers = {'User-Agent': random.choice(user_agents)}
        response = scraper.get(URL_SAKANI, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
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

            # المقارنة والرصد
            if last_known_lands:
                # أراضي جديدة (إلغاء حجز)
                new_lands = current_set - last_known_lands
                for land in new_lands:
                    bot.send_message(CHAT_ID, f"✨ **أرض توفرت الآن (إلغاء حجز)!**\n🔢 رقم القطعة: {land}\n🔗 الرابط:\n{current_lands[land]}")
                
                # أراضي اختفت (تم حجزها)
                sold_lands = last_known_lands - current_set
                for land in sold_lands:
                    bot.send_message(CHAT_ID, f"🚫 **تم حجز القطعة رقم: {land}**")

            last_known_lands = current_set
            bot.send_message(CHAT_ID, f"✅ تم الفحص بنجاح.\n📊 المتاح حالياً: {len(current_set)} قطعة.")
            
        else:
            print(f"خطأ {response.status_code}")
            if response.status_code == 403:
                bot.send_message(CHAT_ID, "⚠️ الموقع لا يزال يحظر السيرفر، سأحاول تغيير الهوية مجدداً.")

    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    check_sakani_stable()

import cloudscraper
from bs4 import BeautifulSoup
import telebot
import re
from datetime import datetime

# بيانات البوت الصحيحة
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

URL_SAKANI = "https://sakani.sa/app/land-projects/584"

# ذاكرة البوت
last_known_lands = {} 
reserved_lands_log = {} 

def check_sakani_intelligent():
    global last_known_lands, reserved_lands_log
    # استخدام نفس الصيغة الناجحة لتجاوز خطأ 403
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','desktop': True})
    
    try:
        response = scraper.get(URL_SAKANI, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            all_links = soup.find_all('a', href=True)
            
            current_lands = {}
            for link in all_links:
                href = link['href']
                # استخراج القطع التي تحتوي على روابط وحدات
                if '/units/' in href or '/land-projects/584/' in href:
                    unit_numbers = re.findall(r'\d+', href)
                    if unit_numbers:
                        unit_number = unit_numbers[-1]
                        full_url = f"https://sakani.sa{href}" if href.startswith('/') else href
                        current_lands[unit_number] = full_url

            current_set = set(current_lands.keys())
            last_set = set(last_known_lands.keys())

            # رصد حجز جديد
            if last_set:
                new_reservations = last_set - current_set
                for land_id in new_reservations:
                    reserved_lands_log[land_id] = datetime.now()
                    bot.send_message(CHAT_ID, f"🚫 **حجز جديد!**\n🔢 قطعة رقم: {land_id}\n⏰ وقت الرصد: {datetime.now().strftime('%H:%M:%S')}\nالبوت يراقبها الآن تمهيداً لإلغائها.")

            # رصد إلغاء حجز (عودة قطعة)
            if last_set:
                cancelled_reservations = current_set - last_set
                for land_id in cancelled_reservations:
                    msg = (
                        f"✨ **عاجل: أرض متاحة (إلغاء حجز)!**\n\n"
                        f"🔢 رقم القطعة: {land_id}\n"
                        f"🔗 الرابط المباشر:\n{current_lands[land_id]}"
                    )
                    bot.send_message(CHAT_ID, msg)
                    if land_id in reserved_lands_log:
                        del reserved_lands_log[land_id]

            # تحديث الذاكرة
            last_known_lands = current_lands
            
            # رسالة الحالة لتأكيد العمل بدون خطأ 403
            bot.send_message(CHAT_ID, f"🔍 فحص ذكي: لا تغيير.\n✅ متاح: {len(current_set)} أرض.\n🎯 يراقب {len(reserved_lands_log)} حجوزات.")

        else:
            # تنبيه في حال عودة خطأ 403 أو غيره
            print(f"خطأ {response.status_code}")
            
    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    check_sakani_intelligent()

import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup

# --- إعداداتك الخاصة ---
TOKEN = "8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo"
CHAT_ID = "652646153"
URL_SAKANI = "https://sakani.sa/app/land-projects"

app = Flask('')
@app.route('/')
def home(): return "البوت يعمل بدقة عالية الآن!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

bot = telebot.TeleBot(TOKEN)

def monitor_sakani():
    last_lands = set() 
    print("بدأت المراقبة التفصيلية للأراضي...")
    
    while True:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Accept-Language': 'ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            response = requests.get(URL_SAKANI, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # البحث عن مربعات المشاريع (تعديل الـ Selector بناءً على بنية سكني)
                # سنحاول استخراج أي نصوص تدل على اسم المشروع أو رقم القطعة
                current_lands = []
                projects = soup.find_all(['h3', 'div'], class_=lambda x: x and ('card' in x or 'project' in x))
                
                for p in projects:
                    text = p.get_text(strip=True)
                    if text: current_lands.append(text)

                # إذا وجدنا شيئاً جديداً لم يكن موجوداً في الفحص السابق
                for land in current_lands:
                    if land not in last_lands and last_lands:
                        msg = f"🆕 **تحديث جديد في سكني!**\n\n📍 **التفاصيل المرصودة:**\n{land}\n\n🔗 **الرابط المباشر:**\n{URL_SAKANI}"
                        bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                
                last_lands = set(current_lands)
            
        except Exception as e:
            print(f"خطأ فني: {e}")
            
        time.sleep(180) # فحص كل 3 دقائق (توازن مثالي لتجنب الحظر)

if __name__ == "__main__":
    Thread(target=run).start()
    monitor_thread = Thread(target=monitor_sakani)
    monitor_thread.start()
    bot.polling(none_stop=True)

import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread
from bs4 import BeautifulSoup

# --- 1. بياناتك الخاصة (تم دمجها وجاهزة) ---
TOKEN = "8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo"
CHAT_ID = "652646153"
URL_SAKANI = "https://sakani.sa/app/land-projects"

# --- 2. سيرفر Flask لإبقاء البوت حياً على Render ---
app = Flask('')

@app.route('/')
def home():
    return "✅ البوت يعمل ومستقر الآن!"

def run():
    # Render يتطلب فتح هذا المنفذ لمنع الخطأ الذي ظهر عندك
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 3. إعداد البوت والرد على الرسائل ---
bot = telebot.TeleBot(TOKEN)

# رد آلي للتأكد من أن البوت يعمل
@bot.message_handler(commands=['start', 'test'])
def send_welcome(message):
    bot.reply_to(message, "🚀 أهلاً عبدالله! أنا الآن أعمل وأراقب أراضي سكني.\nسأرسل لك تنبيهاً فور توفر أي قطعة أو مشروع جديد.")

# --- 4. ميزة مراقبة صفحة سكني ---
def monitor_sakani():
    print("بدأت عملية المراقبة...")
    last_content = ""
    
    while True:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            }
            response = requests.get(URL_SAKANI, headers=headers, timeout=20)
            
            if response.status_code == 200:
                # نستخدم BeautifulSoup لتحليل الصفحة بشكل أفضل
                soup = BeautifulSoup(response.text, 'html.parser')
                current_text = soup.get_text() # نأخذ النصوص فقط للمقارنة

                if last_content != "" and current_text != last_content:
                    msg = f"🆕 **تنبيه عاجل من سكني!**\n\nتم رصد تحديث أو تغيير في صفحة الأراضي والمشاريع. قد تكون هناك قطع جديدة متاحة الآن!\n\n🔗 الرابط: {URL_SAKANI}"
                    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                
                last_content = current_text
        except Exception as e:
            print(f"حدث خطأ في الفحص: {e}")
        
        # الفحص كل 3 دقائق (توازن بين السرعة وتجنب الحظر)
        time.sleep(180)

# --- 5. تشغيل كل شيء معاً ---
if __name__ == "__main__":
    # تشغيل السيرفر في الخلفية لفتح الـ Port
    t = Thread(target=run)
    t.start()
    
    # تشغيل خيط المراقبة في الخلفية
    monitor_thread = Thread(target=monitor_sakani)
    monitor_thread.start()
    
    # بدء استقبال الأوامر من تلجرام (polling)
    print("البوت بدأ الاستماع للرسائل...")
    bot.infinity_polling()

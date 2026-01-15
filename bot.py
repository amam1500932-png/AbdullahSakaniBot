import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread

# --- إعدادات البوت والبيانات الخاصة بك ---
TOKEN = "8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo"
CHAT_ID = "652646153"
URL_SAKANI = "https://sakani.sa/app/land-projects"

# --- 1. سيرفر Flask الصغير لإبقاء البوت حياً على Render ---
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل الآن بنجاح!"

def run():
    # Render يتطلب فتح منفذ محدد لاستمرار الخدمة
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. برمجة البوت ومراقبة التغييرات ---
bot = telebot.TeleBot(TOKEN)

def monitor_sakani():
    print("بدأ البوت بمراقبة صفحة الأراضي...")
    last_content = ""
    
    # رسالة ترحيبية عند بدء التشغيل
    try:
        bot.send_message(CHAT_ID, "🚀 تم تشغيل بوت مراقبة أراضي سكني بنجاح!\nسأقوم بتنبيهك فور حدوث أي تغيير في المشاريع.")
    except Exception as e:
        print(f"خطأ في إرسال رسالة الترحيب: {e}")

    while True:
        try:
            # محاكاة متصفح حقيقي لتجنب الحظر
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(URL_SAKANI, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # إذا تغير محتوى الصفحة عن المرة السابقة
                if response.text != last_content and last_content != "":
                    msg = f"⚠️ <b>تنبيه عاجل من سكني!</b>\n\nحدث تغيير في صفحة المشاريع/الأراضي. قد تكون هناك قطع جديدة توفرت.\n\nالرابط: {URL_SAKANI}"
                    bot.send_message(CHAT_ID, msg, parse_mode='HTML')
                
                last_content = response.text
            
        except Exception as e:
            print(f"حدث خطأ أثناء الفحص: {e}")
            
        # فحص كل 5 دقائق (300 ثانية) لضمان عدم حظر الـ IP
        time.sleep(300)

# --- 3. تشغيل النظام بالكامل ---
if __name__ == "__main__":
    # تشغيل سيرفر الويب
    keep_alive()
    
    # تشغيل عملية المراقبة في خيط منفصل
    monitor_thread = Thread(target=monitor_sakani)
    monitor_thread.start()
    
    # تشغيل استقبال أوامر تلجرام (مثل /start)
    print("البوت قيد التشغيل...")
    bot.polling(none_stop=True)

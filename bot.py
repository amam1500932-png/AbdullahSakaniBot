import requests
import telebot
import time
import os
from flask import Flask
from threading import Thread

# 1. إعداد خادم الويب لضمان استقرار البوت على Render
app = Flask('')
@app.route('/')
def home(): return "Elite Monitoring System is LIVE"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. إعدادات التليجرام والمخطط
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

PROJECT_ID = "584"
URL_SAKANI = f"https://sakani.sa/app/land-projects/{PROJECT_ID}"
API_URL = f"https://sakani.sa/api/v1/land-projects/{PROJECT_ID}/units_summary"

# 3. متغيرات التتبع
last_available_count = None
last_heartbeat_time = time.time()

def check_sakani():
    global last_available_count, last_heartbeat_time
    
    # هوية متصفح (User-Agent) لتبدو كإنسان يتصفح من آيفون لتجنب الحظر
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://sakani.sa/',
        'Origin': 'https://sakani.sa'
    }
    
    try:
        # إضافة توقيت عشوائي للرابط لضمان سحب أحدث بيانات (تجاوز الكاش)
        response = requests.get(f"{API_URL}?t={int(time.time())}", headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            current_available = data.get('available_units_count', 0)
            
            # أ. عند أول تشغيل للبوت: إرسال الحالة الحالية
            if last_available_count is None:
                last_available_count = current_available
                bot.send_message(CHAT_ID, f"✅ **تم تفعيل الرادار الشامل بنجاح!**\n📊 العدد المتوفر حالياً في المخطط: {current_available}\n🔎 المراقبة مستمرة كل 30 ثانية.")
                return

            # ب. في حال توفر أرض جديدة (إلغاء حجز من شخص آخر)
            if current_available > last_available_count:
                diff = current_available - last_available_count
                msg = (f"✨ **عاجل: توفرت {diff} أرض جديدة!**\n"
                       f"📊 العدد الإجمالي المتاح: {current_available}\n"
                       f"⚠️ **تذكير**: قد تظهر في الخريطة بعد ساعتين.\n"
                       f"🔗 الرابط: {URL_SAKANI}")
                bot.send_message(CHAT_ID, msg)
                last_available_count = current_available
            
            # ج. في حال تم حجز أرض
            elif current_available < last_available_count:
                diff = last_available_count - current_available
                bot.send_message(CHAT_ID, f"🚫 **تنبيه: تم حجز {diff} أرض.**\n📊 المتبقي الآن: {current_available}")
                last_available_count = current_available

        # د. رسالة الطمأنة (أنا أعمل) كل 10 دقائق
        if time.time() - last_heartbeat_time >= 600:
            bot.send_message(CHAT_ID, f"🤖 رادار سكني يعمل بنشاط...\n📊 العدد الحالي للأراضي: {last_available_count}")
            last_heartbeat_time = time.time()

    except Exception as e:
        print(f"Error: {e}")

def bot_loop():
    while True:
        check_sakani()
        time.sleep(30) # فحص كل 30 ثانية لسرعة الاستجابة

if __name__ == "__main__":
    # بدء خادم الويب في خلفية منفصلة
    Thread(target=run).start()
    # بدء حلقة الفحص
    bot_loop()

import requests
import telebot
import time
import os
from flask import Flask
from threading import Thread

# خادم الويب
app = Flask('')
@app.route('/')
def home(): return "Deep Radar is Active"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

URL_SAKANI = "https://sakani.sa/app/land-projects/584"

def check_sakani_deep():
    # استخدام جسر مختلف هذه المرة لتجاوز أي حظر محتمل
    bridge_url = f"https://api.allorigins.win/get?url={URL_SAKANI}"
    
    try:
        response = requests.get(bridge_url, timeout=20)
        if response.status_code == 200:
            content = response.json().get('contents', '').lower()
            
            # البحث عن كلمات تدل على "التوفر" داخل الكود المخفي
            # سنبحث عن كلمات مثل "available", "unit", "land"
            is_available = "available" in content or "status_id\":1" in content
            
            if is_available:
                bot.send_message(CHAT_ID, f"📢 **بشرى سارة!**\nتم رصد توفر أرض أو تحديث في المخطط 584.\nافحص الآن: {URL_SAKANI}")
                return True
        return False
    except:
        return False

def bot_loop():
    bot.send_message(CHAT_ID, "🔎 بدأ رادار البيانات العميقة.\nسأرسل لك فقط عند رصد أرض متاحة فعلياً.")
    while True:
        found = check_sakani_deep()
        if found:
            # إذا وجد أرض، سيتوقف قليلاً ثم يعاود المراقبة
            time.sleep(600) 
        else:
            # فحص كل 3 دقائق لضمان عدم الحظر وبقاء البيانات طازجة
            time.sleep(180)

if __name__ == "__main__":
    Thread(target=run).start()
    bot_loop()

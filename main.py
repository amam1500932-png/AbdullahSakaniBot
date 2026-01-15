import os
import telebot
from flask import Flask
from threading import Thread

# --- إعداد السيرفر لـ Render ---
app = Flask('')
@app.route('/')
def home():
    return "البوت شغال!"

def run():
    # هذا السطر يحل مشكلة Port scan timeout
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- إعدادات البوت ---
TOKEN = "ضع_هنا_توكن_بوتك"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أنا بوت مراقبة سكني، سأرسل لك تنبيهاً عند أي تغيير.")

if __name__ == "__main__":
    # تشغيل السيرفر في الخلفية
    t = Thread(target=run)
    t.start()
    
    # تشغيل البوت
    print("جاري تشغيل البوت...")
    bot.polling(none_stop=True)

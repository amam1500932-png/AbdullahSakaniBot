import telebot
import requests
import time
import os
import random
import threading
from flask import Flask

# --- بياناتك ---
TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362' 
PROXY_URL = "http://9fc0be730450f5b0e2f3:1ee7512fcb506872@gw.dataimpulse.com:823"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@server.route('/')
def home(): return "Bot is Active"

def run_server():
    # هذا السطر يحل مشكلة الـ Failed والـ Port تماماً
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

def check_lands():
    bot.send_message(CHAT_ID, "✅ تم حل مشكلة التوقف.. الرادار الآن صاحي ويبحث عن الأراضي!")
    last_known_lands = {}
    proxies = {"http": PROXY_URL, "https": PROXY_URL}
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}

    while True:
        try:
            # إضافة رقم عشوائي لكسر الكاش
            api_url = f"https://sakani.sa/api/v1/market_place/products?category=free_land&v={random.random()}"
            res = requests.get(api_url, proxies=proxies, headers=headers, timeout=20)
            if res.status_code == 200:
                projects = res.json().get('data', [])
                for project in projects:
                    p_id = project.get('id')
                    p_name = project.get('name')
                    
                    p_res = requests.get(f"https://sakani.sa/api/v1/plots?project_id={p_id}&v={random.random()}", proxies=proxies, headers=headers, timeout=20)
                    if p_res.status_code == 200:
                        plots = p_res.json().get('data', [])
                        for plot in plots:
                            key = f"{p_id}_{plot.get('id')}"
                            status = plot.get('status')
                            
                            if key in last_known_lands and status == 'available' and last_known_lands[key] == 'reserved':
                                bot.send_message(CHAT_ID, f"🚀 **صيد جديد! أرض توفرت الآن**\n🏙️ {p_name}\n📍 قطعة رقم: {plot.get('plot_number')}\n🔗 https://sakani.sa/app/map/{p_id}?land={plot.get('id')}")
                            last_known_lands[key] = status
            time.sleep(25) # فحص سريع جداً
        except: time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    check_lands()

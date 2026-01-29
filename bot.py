import telebot
import requests
import time
import os
import random

# --- بياناتك المعتمدة ---
TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362' 
PROXY_URL = "http://9fc0be730450f5b0e2f3:1ee7512fcb506872@gw.dataimpulse.com:823"

bot = telebot.TeleBot(TOKEN)
proxies = {"http": PROXY_URL, "https": PROXY_URL}

# رأس طلب يحاكي المتصفح بشكل كامل
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept': 'application/json',
    'Accept-Language': 'ar',
    'Referer': 'https://sakani.sa/',
    'Origin': 'https://sakani.sa'
}

def check_lands():
    # رسالة انطلاق للتأكد أن البوت يكلمك الآن
    bot.send_message(CHAT_ID, "⚠️ بدأت الفحص بنظام المحاكاة المتقدم ⚠️\nسأقوم بجلب البيانات الحقيقية الآن وتجاوز الحجب.")
    
    last_known_lands = {}
    
    while True:
        try:
            # 1. جلب قائمة المخططات أولاً
            api_url = f"https://sakani.sa/api/v1/market_place/products?category=free_land&v={random.random()}"
            res = requests.get(api_url, proxies=proxies, headers=HEADERS, timeout=20)
            
            # إذا كان الرد ناجحاً وحجمه معقول
            if res.status_code == 200:
                data = res.json().get('data', [])
                for project in data:
                    p_id = project.get('id')
                    p_name = project.get('name')
                    
                    # 2. جلب قطع الأرض لهذا المشروع
                    plots_url = f"https://sakani.sa/api/v1/plots?project_id={p_id}&v={random.random()}"
                    p_res = requests.get(plots_url, proxies=proxies, headers=HEADERS, timeout=20)
                    
                    if p_res.status_code == 200:
                        plots = p_res.json().get('data', [])
                        for plot in plots:
                            land_id = plot.get('id')
                            status = plot.get('status') # available أو reserved
                            land_num = plot.get('plot_number')
                            
                            key = f"{p_id}_{land_id}"
                            
                            # أول مرة نخزن البيانات
                            if key not in last_known_lands:
                                last_known_lands[key] = status
                                continue
                            
                            # كشف التغيير الحقيقي
                            if status == 'available' and last_known_lands[key] == 'reserved':
                                bot.send_message(CHAT_ID, f"🎉 صيد مؤكد! أرض توفرت الآن\n🏙️ المخطط: {p_name}\n📍 رقم القطعة: {land_num}\n🔗 https://sakani.sa/app/map/{p_id}?land={land_id}")
                            
                            last_known_lands[key] = status
            
            # انتظر قليلاً لضمان عدم الحظر
            time.sleep(30)
            
        except Exception as e:
            # لا ترسل أخطاء للقناة، فقط حاول مرة أخرى
            time.sleep(10)

if __name__ == "__main__":
    check_lands()

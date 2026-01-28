import telebot
import requests
import time
import os
import threading
import http.server
import socketserver

# --- بياناتك المعتمدة ---
TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362' 
PROXY_URL = "http://9fc0be730450f5b0e2f3:1ee7512fcb506872@gw.dataimpulse.com:823"

bot = telebot.TeleBot(TOKEN)
proxies = {"http": PROXY_URL, "https": PROXY_URL}

# رأس الطلب لإقناع الموقع أننا متصفح حقيقي
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}

def keep_alive():
    try:
        port = int(os.environ.get("PORT", 10000))
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

def check_all_free_lands():
    # إشعار عند التشغيل للتأكد من الاتصال
    bot.send_message(CHAT_ID, "🔄 تم إعادة تشغيل الرادار بنظام التحديث الفوري...")
    
    last_known_lands = {}

    while True:
        try:
            # طلب قائمة المخططات مع منع التخزين المؤقت (Cache)
            response = requests.get(
                "https://sakani.sa/api/v1/market_place/products?category=free_land", 
                proxies=proxies, 
                headers=HEADERS, 
                timeout=30
            )
            all_products = response.json().get('data', [])

            for product in all_products:
                p_id = product.get('id')
                p_name = product.get('name')
                p_city = product.get('city_name')
                
                # طلب بيانات المخطط
                plot_res = requests.get(
                    f"https://sakani.sa/api/v1/plots?project_id={p_id}", 
                    proxies=proxies, 
                    headers=HEADERS, 
                    timeout=25
                )
                plots_data = plot_res.json().get('data', [])

                for plot in plots_data:
                    land_id, land_num, status = plot.get('id'), plot.get('plot_number'), plot.get('status')
                    unique_key = f"{p_id}_{land_id}"

                    # إذا كانت أول مرة يرى فيها البوت الأرض، يخزنها فقط
                    if unique_key not in last_known_lands:
                        last_known_lands[unique_key] = status
                        continue

                    # إذا تغيرت الحالة من محجوزة إلى متاحة
                    if status == 'available' and last_known_lands[unique_key] == 'reserved':
                        bot.send_message(CHAT_ID, f"🔔 **أرض توفرت الآن!**\n🏙️ {p_name} ({p_city})\n📍 قطعة: `{land_num}`\n🔗 https://sakani.sa/app/map/{p_id}?land={land_id}", parse_mode="Markdown")
                    
                    # إذا تم حجز أرض كانت متاحة
                    elif status == 'reserved' and last_known_lands[unique_key] == 'available':
                        bot.send_message(CHAT_ID, f"🔒 **تم الحجز**\n🏙️ {p_name} ({p_city})\n📍 قطعة: `{land_num}`", parse_mode="Markdown")

                    last_known_lands[unique_key] = status
                    
        except Exception as e:
            print(f"خطأ في الاتصال: {e}")
        
        # الانتظار لمدة دقيقة لتقليل الضغط وضمان جلب بيانات جديدة
        time.sleep(60)

check_all_free_lands()

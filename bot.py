import telebot
import requests
import time
import os
import threading
import random # لإضافة التمويه ومنع التخزين

TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362' 
PROXY_URL = "http://9fc0be730450f5b0e2f3:1ee7512fcb506872@gw.dataimpulse.com:823"

bot = telebot.TeleBot(TOKEN)
proxies = {"http": PROXY_URL, "https": PROXY_URL}

# نظام البقاء حياً لـ Render
def keep_alive():
    from http.server import SimpleHTTPRequestHandler
    from socketserver import TCPServer
    try:
        port = int(os.environ.get("PORT", 10000))
        with TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

def check_sakani():
    # رسالة تأكيد عند التشغيل
    bot.send_message(CHAT_ID, "⚠️ تم تشغيل الرادار الخارق (تحديث كل 20 ثانية) ⚠️\nسيتم تجاهل البيانات المخزنة وجلب الأراضي فور نزولها.")
    
    last_known_lands = {}
    
    while True:
        try:
            # إضافة رقم عشوائي (v=...) لمنع الـ Cache تماماً
            search_api = f"https://sakani.sa/api/v1/market_place/products?category=free_land&v={random.random()}"
            headers = {'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{random.randint(100,120)}.0.0.0'}
            
            response = requests.get(search_api, proxies=proxies, headers=headers, timeout=20)
            all_products = response.json().get('data', [])

            for product in all_products:
                p_id, p_name, p_city = product.get('id'), product.get('name'), product.get('city_name')
                
                # طلب بيانات القطع مع منع التخزين أيضاً
                plot_res = requests.get(f"https://sakani.sa/api/v1/plots?project_id={p_id}&v={random.random()}", proxies=proxies, headers=headers, timeout=15)
                plots_data = plot_res.json().get('data', [])

                for plot in plots_data:
                    land_id, land_num, status = plot.get('id'), plot.get('plot_number'), plot.get('status')
                    unique_key = f"{p_id}_{land_id}"

                    if unique_key not in last_known_lands:
                        last_known_lands[unique_key] = status
                        continue

                    if status == 'available' and last_known_lands[unique_key] == 'reserved':
                        bot.send_message(CHAT_ID, f"🚀 **صيد ثقيل! أرض توفرت الآن**\n🏙️ {p_name} ({p_city})\n📍 قطعة: `{land_num}`\n🔗 https://sakani.sa/app/map/{p_id}?land={land_id}", parse_mode="Markdown")
                    
                    last_known_lands[unique_key] = status
        except: pass
        
        # تقليل وقت الفحص لـ 20 ثانية للحاق بالأراضي السريعة
        time.sleep(20)

check_sakani()

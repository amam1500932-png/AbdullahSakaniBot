import telebot
import requests
import time
import os
import threading
import http.server
import socketserver

# --- بياناتك الخاصة ---
TOKEN = '7611681755:AAH_GNo887z0Ff6N6B_p9tG6H7-526Eoy_c'
CHAT_ID = '7091490226'
PROXY = "http://brd-customer-hl_59665809-zone-residential_proxy1:y06f691h8u67@brd.superproxy.io:22225"

bot = telebot.TeleBot(TOKEN)
proxies = {"http": PROXY, "https": PROXY}

# --- 1. حل مشكلة توقف Render ---
def keep_alive():
    try:
        port = int(os.environ.get("PORT", 10000))
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

# --- 2. رادار سكني الشامل للمخططات المجانية ---
def check_all_free_lands():
    # رابط البحث عن جميع المخططات المجانية (Free Lands)
    search_api = "https://sakani.sa/api/v1/market_place/products?category=free_land"
    
    last_known_lands = {} # لمراقبة التغيرات في الحالة

    while True:
        try:
            # طلب قائمة المخططات/المنتجات
            response = requests.get(search_api, proxies=proxies, timeout=25)
            all_products = response.json().get('data', [])

            for product in all_products:
                p_id = product.get('id') # معرف المخطط
                p_name = product.get('name') # اسم المخطط
                p_city = product.get('city_name') # المدينة
                
                # الآن ندخل داخل كل مخطط لنفحص حالة القطع (إذا كان الـ API يوفرها)
                # ملاحظة: بعض المخططات تحتاج طلب منفصل لكل مشروع p_id
                plots_url = f"https://sakani.sa/api/v1/plots?project_id={p_id}"
                plot_res = requests.get(plots_url, proxies=proxies, timeout=20)
                plots_data = plot_res.json().get('data', [])

                for plot in plots_data:
                    land_id = plot.get('id')
                    land_num = plot.get('plot_number')
                    status = plot.get('status') # available أو reserved

                    # مفتاح فريد لكل أرض (معرف المخطط + معرف الأرض)
                    unique_key = f"{p_id}_{land_id}"

                    if unique_key not in last_known_lands:
                        last_known_lands[unique_key] = status
                        continue

                    # الحالة 1: كانت محجوزة وصارت متاحة (إلغاء حجز)
                    if status == 'available' and last_known_lands[unique_key] == 'reserved':
                        msg = (f"✅ **إلغاء حجز قطعة أرض!**\n\n"
                               f"🏙️ المخطط: `{p_name}` ({p_city})\n"
                               f"📍 رقم القطعة: `{land_num}`\n"
                               f"🗺️ رابط المخطط: https://sakani.sa/app/map/{p_id}\n"
                               f"🔗 رابط القطعة: https://sakani.sa/app/map/{p_id}?land={land_id}")
                        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

                    # الحالة 2: تم حجز أرض كانت متاحة
                    elif status == 'reserved' and last_known_lands[unique_key] == 'available':
                        msg = (f"🔒 **تم حجز أرض جديدة**\n\n"
                               f"🏙️ المخطط: `{p_name}` ({p_city})\n"
                               f"📍 رقم الأرض: `{land_num}`\n"
                               f"🔗 رابط الأرض: https://sakani.sa/app/map/{p_id}?land={land_id}")
                        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

                    last_known_lands[unique_key] = status

        except Exception as e:
            print(f"خطأ في الفحص الشامل: {e}")
        
        time.sleep(45) # فحص الدورة كاملة كل 45 ثانية

print("الرادار الشامل لكل المخططات المجانية بدأ العمل...")
check_all_free_lands()

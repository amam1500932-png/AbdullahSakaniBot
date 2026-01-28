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

# --- حل مشكلة التوقف (Keep Alive) ---
def keep_alive():
    try:
        port = int(os.environ.get("PORT", 10000))
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

# رسالة تأكيد التشغيل
bot.send_message(CHAT_ID, "🚀 تم تشغيل الرادار الشامل لكل المخططات بنجاح! جاري الفحص الآن...")

# --- الرادار الشامل ---
def check_all_free_lands():
    search_api = "https://sakani.sa/api/v1/market_place/products?category=free_land"
    last_known_lands = {}

    while True:
        try:
            response = requests.get(search_api, proxies=proxies, timeout=25)
            all_products = response.json().get('data', [])

            for product in all_products:
                p_id = product.get('id')
                p_name = product.get('name')
                p_city = product.get('city_name')
                
                # فحص قطع الأراضي داخل كل مخطط
                plots_url = f"https://sakani.sa/api/v1/plots?project_id={p_id}"
                plot_res = requests.get(plots_url, proxies=proxies, timeout=20)
                plots_data = plot_res.json().get('data', [])

                for plot in plots_data:
                    land_id = plot.get('id')
                    land_num = plot.get('plot_number')
                    status = plot.get('status')
                    unique_key = f"{p_id}_{land_id}"

                    if unique_key not in last_known_lands:
                        last_known_lands[unique_key] = status
                        continue

                    # إشعار إلغاء حجز (أصبحت متاحة)
                    if status == 'available' and last_known_lands[unique_key] == 'reserved':
                        msg = (f"✅ **إلغاء حجز قطعة أرض!**\n\n"
                               f"🏙️ المخطط: `{p_name}` ({p_city})\n"
                               f"📍 رقم القطعة: `{land_num}`\n"
                               f"🗺️ المخطط: https://sakani.sa/app/map/{p_id}\n"
                               f"🔗 القطعة: https://sakani.sa/app/map/{p_id}?land={land_id}")
                        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

                    # إشعار حجز جديد
                    elif status == 'reserved' and last_known_lands[unique_key] == 'available':
                        msg = (f"🔒 **تم حجز أرض جديدة**\n\n"
                               f"🏙️ المخطط: `{p_name}` ({p_city})\n"
                               f"📍 رقم الأرض: `{land_num}`\n"
                               f"🔗 الرابط: https://sakani.sa/app/map/{p_id}?land={land_id}")
                        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

                    last_known_lands[unique_key] = status

        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(60)

check_all_free_lands()

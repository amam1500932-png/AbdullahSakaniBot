import telebot
import requests
import time
import os
import threading
import http.server
import socketserver

# --- بياناتك الحقيقية من الصور ---
TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362' # أيدي القناة
# البروكسي الجديد من صورتك الأخيرة
PROXY_URL = "http://9fc0be730450f5b0e2f3:1ee7512fcb506872@gw.dataimpulse.com:823"

bot = telebot.TeleBot(TOKEN)
proxies = {"http": PROXY_URL, "https": PROXY_URL}

# --- حل مشكلة توقف Render (المنفذ 10000) ---
def keep_alive():
    try:
        port = int(os.environ.get("PORT", 10000))
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

# --- رادار سكني الشامل ---
def check_all_free_lands():
    try:
        # رسالة ترحيبية للقناة للتأكد من الاتصال
        bot.send_message(CHAT_ID, "🚀 تم تشغيل الرادار الشامل بنجاح!\n📡 يتم الآن مراقبة كافة المخططات المجانية...")
    except Exception as e:
        print(f"خطأ في إرسال التنبيه: {e}")

    search_api = "https://sakani.sa/api/v1/market_place/products?category=free_land"
    last_known_lands = {}

    while True:
        try:
            # استخدام البروكسي الجديد لطلب البيانات
            response = requests.get(search_api, proxies=proxies, timeout=25)
            all_products = response.json().get('data', [])

            for product in all_products:
                p_id = product.get('id')
                p_name = product.get('name')
                p_city = product.get('city_name')
                
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

                    # تنبيه إلغاء الحجز
                    if status == 'available' and last_known_lands[unique_key] == 'reserved':
                        msg = (f"✅ **إلغاء حجز قطعة أرض!**\n\n"
                               f"🏙️ المخطط: `{p_name}` ({p_city})\n"
                               f"📍 رقم القطعة: `{land_num}`\n"
                               f"🔗 الرابط: https://sakani.sa/app/map/{p_id}?land={land_id}")
                        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

                    # تنبيه حجز جديد
                    elif status == 'reserved' and last_known_lands[unique_key] == 'available':
                        msg = (f"🔒 **تم حجز أرض جديدة**\n\n"
                               f"🏙️ المخطط: `{p_name}` ({p_city})\n"
                               f"📍 رقم الأرض: `{land_num}`\n"
                               f"🔗 الرابط: https://sakani.sa/app/map/{p_id}?land={land_id}")
                        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

                    last_known_lands[unique_key] = status
        except Exception as e:
            print(f"فشل في الدورة: {e}")
        
        time.sleep(60)

check_all_free_lands()

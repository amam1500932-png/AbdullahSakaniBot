import requests
import telebot
import time

# --- إعداداتك الخاصة ---
TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(TOKEN)

# --- إعدادات البروكسي من صورتك ---
proxy_url = "http://9fc0be730450f5b0e2f3:1ee7512fcb506872@gw.dataimpulse.com:823"
proxies = {"http": proxy_url, "https": proxy_url}

last_counts = {}

def scan_sakani():
    global last_counts
    url = "https://sakani.sa/api/v1/land-projects/summary"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        # الفحص باستخدام البروكسي لتجاوز 403
        response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        if response.status_code == 200:
            projects = response.json()
            for p in projects:
                p_id = str(p['id'])
                name = p['name']
                count = p.get('available_units_count', 0)
                
                if p_id not in last_counts:
                    last_counts[p_id] = count
                    continue
                
                if count > last_counts[p_id]:
                    msg = f"✨ **أرض متوفرة الآن!**\n🏗 المخطط: {name}\n📊 العدد المتوفر: {count}"
                    bot.send_message(CHAT_ID, msg)
                last_counts[p_id] = count
            print(f"✅ Scan Success at {time.strftime('%H:%M:%S')}")
        else:
            print(f"❌ Error {response.status_code}")
    except Exception as e:
        print(f"⚠️ Proxy Error: {e}")

bot.send_message(CHAT_ID, "🚀 رادار المحترفين يعمل الآن عبر البروكسي السكني..")

while True:
    scan_sakani()
    time.sleep(45) # وقت آمن جداً مع البروكسي

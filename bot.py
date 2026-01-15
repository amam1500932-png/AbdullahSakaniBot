import requests
import telebot

# إعدادات البوت
API_TOKEN = '8499439468:AAEOKClXi93_bmOeAO7aQ9bvpGOi5w-jOQo'
CHAT_ID = '-1003269925362'
bot = telebot.TeleBot(API_TOKEN)

# رابط المخطط
URL_SAKANI = "https://sakani.sa/app/land-projects/584"

def check_sakani():
    # سنستخدم خدمة Google Proxy لتجاوز حظر 403
    proxy_url = f"https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?container=focus&refresh=60&url={URL_SAKANI}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        print("محاولة الدخول عبر وسيط جوجل...")
        response = requests.get(proxy_url, headers=headers, timeout=30)
        
        # إذا نجحنا في تجاوز الحماية (كود 200)
        if response.status_code == 200:
            bot.send_message(CHAT_ID, "✅ نجحت في تجاوز الحظر والدخول للمخطط 584 عبر وسيط جوجل!\n🔍 المراقبة تعمل الآن.")
        else:
            print(f"لا يزال هناك حظر، كود: {response.status_code}")
            bot.send_message(CHAT_ID, f"⚠️ الموقع لا يزال يرفض الاتصال (كود {response.status_code})")

    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    check_sakani()

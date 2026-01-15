import requests
import time
import hashlib

# --- إعداداتك الخاصة (يجب تعبئتها) ---
TOKEN = "ضع_هنا_توكن_البوت"
CHAT_ID = "ضع_هنا_ايدي_حسابك"
# رابط صفحة الأراضي (يفضل الرابط بعد اختيار المدينة في المتصفح)
URL_TO_MONITOR = "https://sakani.sa/app/land-projects"

def send_telegram_msg(text):
    """وظيفة إرسال التنبيه إلى تلجرام"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"خطأ في إرسال الرسالة: {e}")

def get_page_hash():
    """وظيفة تجلب محتوى الصفحة وتحولها لرمز مشفر لمقارنة التغييرات"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(URL_TO_MONITOR, headers=headers)
    if response.status_code == 200:
        # نأخذ جزء من المحتوى لتقليل التنبيهات الخاطئة
        return hashlib.md5(response.text.encode('utf-8')).hexdigest()
    return None

def main():
    print("بدأ البوت في مراقبة أراضي سكني...")
    send_telegram_msg("🚀 تم تشغيل بوت مراقبة الأراضي بنجاح!")
    
    last_hash = get_page_hash()
    
    while True:
        try:
            time.sleep(300) # فحص كل 5 دقائق
            current_hash = get_page_hash()
            
            if current_hash and current_hash != last_hash:
                send_telegram_msg(f"⚠️ <b>تحديث جديد في سكني!</b>\nهناك تغيير في صفحة الأراضي، افحص الرابط الآن:\n{URL_TO_MONITOR}")
                last_hash = current_hash
            else:
                print("لا يوجد تغيير...")
                
        except Exception as e:
            print(f"حدث خطأ: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()

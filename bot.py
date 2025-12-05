# ========== ملف: bot.py ==========

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import logging

# ================== الإعدادات ==================


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SAKANI_API_URL = "https://sakani.sa/api/web/lands/tax-incurred"
CHECK_INTERVAL = 300  # 5 دقائق

# ================== إعداد السجلات ==================

logging.basicConfig(
level=logging.INFO,
format=’%(asctime)s - %(name)s - %(levelname)s - %(message)s’
)
logger = logging.getLogger(**name**)

previous_lands = {}

# ================== دوال البوت ==================

async def fetch_lands_data():
“”“جلب بيانات القطع من API موقع سكني”””
try:
headers = {
‘User-Agent’: ‘Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36’,
‘Accept’: ‘application/json’,
‘Accept-Language’: ‘ar’,
}

```
    async with aiohttp.ClientSession() as session:
        async with session.get(SAKANI_API_URL, headers=headers, timeout=30) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logger.error(f"خطأ في الاستجابة: {response.status}")
                return None
except Exception as e:
    logger.error(f"خطأ في جلب البيانات: {str(e)}")
    return None
```

async def send_telegram_message(bot, message):
“”“إرسال رسالة عبر تلجرام”””
try:
await bot.send_message(
chat_id=CHAT_ID,
text=message,
parse_mode=‘HTML’,
disable_web_page_preview=False
)
logger.info(“تم إرسال الرسالة بنجاح”)
except TelegramError as e:
logger.error(f”خطأ في إرسال الرسالة: {str(e)}”)

def extract_lands_info(data):
“”“استخراج معلومات القطع من البيانات”””
lands = {}

```
try:
    if isinstance(data, dict):
        lands_list = data.get('data', []) or data.get('lands', []) or data.get('items', [])
        
        for land in lands_list:
            land_id = land.get('id') or land.get('landId') or land.get('plotId')
            if land_id:
                lands[str(land_id)] = {
                    'id': land_id,
                    'number': land.get('plotNumber') or land.get('landNumber') or land_id,
                    'location': land.get('location') or land.get('city') or 'غير محدد',
                    'area': land.get('area') or land.get('size') or 'غير محدد',
                    'status': land.get('status') or 'متاح',
                    'url': land.get('url') or f"https://sakani.sa/app/tax-incurred-form?id={land_id}"
                }
    
    return lands
except Exception as e:
    logger.error(f"خطأ في استخراج البيانات: {str(e)}")
    return {}
```

async def check_for_changes(bot):
“”“التحقق من التغييرات في القطع”””
global previous_lands

```
logger.info("جاري التحقق من التحديثات...")

data = await fetch_lands_data()

if data is None:
    logger.warning("فشل في جلب البيانات")
    return

current_lands = extract_lands_info(data)

if not current_lands:
    logger.warning("لا توجد قطع في البيانات المسترجعة")
    return

if not previous_lands:
    previous_lands = current_lands
    logger.info(f"تم تخزين {len(current_lands)} قطعة للمراقبة")
    await send_telegram_message(
        bot,
        f"🤖 <b>بدأ البوت بالعمل!</b>\n\n"
        f"📊 عدد القطع المسجلة: {len(current_lands)}\n"
        f"⏰ وقت المراقبة: كل {CHECK_INTERVAL//60} دقيقة"
    )
    return

new_lands = set(current_lands.keys()) - set(previous_lands.keys())

for land_id in new_lands:
    land = current_lands[land_id]
    message = (
        f"🆕 <b>قطعة جديدة!</b>\n\n"
        f"📍 <b>رقم القطعة:</b> {land['number']}\n"
        f"📌 <b>الموقع:</b> {land['location']}\n"
        f"📏 <b>المساحة:</b> {land['area']}\n"
        f"✅ <b>الحالة:</b> {land['status']}\n\n"
        f"🔗 <a href='{land['url']}'>عرض التفاصيل</a>\n\n"
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await send_telegram_message(bot, message)
    await asyncio.sleep(1)

removed_lands = set(previous_lands.keys()) - set(current_lands.keys())

for land_id in removed_lands:
    land = previous_lands[land_id]
    message = (
        f"❌ <b>قطعة ملغاة!</b>\n\n"
        f"📍 <b>رقم القطعة:</b> {land['number']}\n"
        f"📌 <b>الموقع:</b> {land['location']}\n"
        f"📏 <b>المساحة:</b> {land['area']}\n\n"
        f"ℹ️ تم إلغاء هذه القطعة من القائمة\n\n"
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await send_telegram_message(bot, message)
    await asyncio.sleep(1)

previous_lands = current_lands

if new_lands or removed_lands:
    logger.info(f"قطع جديدة: {len(new_lands)}, قطع ملغاة: {len(removed_lands)}")
else:
    logger.info("لا توجد تغييرات")
```

async def main():
“”“الدالة الرئيسية”””
bot = Bot(token=TELEGRAM_BOT_TOKEN)

```
logger.info("بدء البوت...")

try:
    bot_info = await bot.get_me()
    logger.info(f"البوت متصل: @{bot_info.username}")
except Exception as e:
    logger.error(f"خطأ في التوكن: {str(e)}")
    return

while True:
    try:
        await check_for_changes(bot)
    except Exception as e:
        logger.error(f"خطأ في المراقبة: {str(e)}")
    
    await asyncio.sleep(CHECK_INTERVAL)
```

if **name** == “**main**”:
try:
asyncio.run(main())
except KeyboardInterrupt:
logger.info(“تم إيقاف البوت بواسطة المستخدم”)
except Exception as e:
logger.error(f”خطأ عام: {str(e)}”)

# ========== ملف: requirements.txt ==========

# احفظ هذا في ملف منفصل اسمه requirements.txt

python-telegram-bot==20.7
aiohttp==3.9.1

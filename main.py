import asyncio
import aiohttp
import json
import os
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import logging

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

SAKANI_API_URL = "https://sakani.sa/api/web/lands/tax-incurred"
CHECK_INTERVAL = 300

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

previous_lands = {}

async def fetch_lands_data():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'ar',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(SAKANI_API_URL, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Error: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return None

async def send_telegram_message(bot, message):
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )
        logger.info("Message sent successfully")
    except TelegramError as e:
        logger.error(f"Telegram error: {str(e)}")

def extract_lands_info(data):
    lands = {}
    
    try:
        if isinstance(data, dict):
            lands_list = data.get('data', []) or data.get('lands', []) or data.get('items', [])
            
            for land in lands_list:
                land_id = land.get('id') or land.get('landId') or land.get('plotId')
                if land_id:
                    lands[str(land_id)] = {
                        'id': land_id,
                        'number': land.get('plotNumber') or land.get('landNumber') or land_id,
                        'location': land.get('location') or land.get('city') or 'Not specified',
                        'area': land.get('area') or land.get('size') or 'Not specified',
                        'status': land.get('status') or 'Available',
                        'url': land.get('url') or f"https://sakani.sa/app/tax-incurred-form?id={land_id}"
                    }
        
        return lands
    except Exception as e:
        logger.error(f"Error extracting data: {str(e)}")
        return {}

async def check_for_changes(bot):
    global previous_lands
    
    logger.info("Checking for updates...")
    
    data = await fetch_lands_data()
    
    if data is None:
        logger.warning("Failed to fetch data")
        return
    
    current_lands = extract_lands_info(data)
    
    if not current_lands:
        logger.warning("No lands found")
        return
    
    if not previous_lands:
        previous_lands = current_lands
        logger.info(f"Stored {len(current_lands)} lands")
        await send_telegram_message(
            bot,
            f"Bot started!\n\nRegistered lands: {len(current_lands)}\nCheck interval: {CHECK_INTERVAL//60} minutes"
        )
        return
    
    new_lands = set(current_lands.keys()) - set(previous_lands.keys())
    
    for land_id in new_lands:
        land = current_lands[land_id]
        message = (
            f"New land!\n\n"
            f"Land number: {land['number']}\n"
            f"Location: {land['location']}\n"
            f"Area: {land['area']}\n"
            f"Status: {land['status']}\n\n"
            f"<a href='{land['url']}'>View details</a>\n\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await send_telegram_message(bot, message)
        await asyncio.sleep(1)
    
    removed_lands = set(previous_lands.keys()) - set(current_lands.keys())
    
    for land_id in removed_lands:
        land = previous_lands[land_id]
        message = (
            f"Land cancelled!\n\n"
            f"Land number: {land['number']}\n"
            f"Location: {land['location']}\n"
            f"Area: {land['area']}\n\n"
            f"This land has been removed\n\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await send_telegram_message(bot, message)
        await asyncio.sleep(1)
    
    previous_lands = current_lands
    
    if new_lands or removed_lands:
        logger.info(f"New: {len(new_lands)}, Removed: {len(removed_lands)}")
    else:
        logger.info("No changes")

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    logger.info("Starting bot...")
    
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot connected: @{bot_info.username}")
    except Exception as e:
        logger.error(f"Token error: {str(e)}")
        return
    
    while True:
        try:
            await check_for_changes(bot)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"General error: {str(e)}")

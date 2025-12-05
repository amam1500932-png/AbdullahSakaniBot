import asyncio
import aiohttp
import os
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import logging
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
SAKANI_URL = "https://sakani.sa/app/tax-incurred-form"
CHECK_INTERVAL = 300

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

previous_lands = set()

async def fetch_lands():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession() as session:
            async with session.get(SAKANI_URL, headers=headers, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                logger.error(f"Status: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Fetch error: {str(e)}")
        return None

async def send_message(bot, message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='HTML')
        logger.info("Message sent")
    except TelegramError as e:
        logger.error(f"Telegram error: {str(e)}")

def extract_lands(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        lands = set()
        for item in soup.find_all('div', class_=['land-item', 'property-item']):
            land_id = item.get('data-id') or item.get('id')
            if land_id:
                lands.add(land_id)
        return lands
    except Exception as e:
        logger.error(f"Parse error: {str(e)}")
        return set()

async def check_changes(bot):
    global previous_lands
    logger.info("Checking...")
    html = await fetch_lands()
    if not html:
        return
    current_lands = extract_lands(html)
    if not current_lands:
        logger.warning("No lands found")
        return
    if not previous_lands:
        previous_lands = current_lands
        await send_message(bot, f"Bot started! Monitoring {len(current_lands)} lands. Check interval: {CHECK_INTERVAL//60} min")
        return
    new = current_lands - previous_lands
    removed = previous_lands - current_lands
    for land_id in new:
        await send_message(bot, f"New land detected! ID: {land_id}\n{SAKANI_URL}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await asyncio.sleep(1)
    for land_id in removed:
        await send_message(bot, f"Land removed! ID: {land_id}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await asyncio.sleep(1)
    previous_lands = current_lands
    if new or removed:
        logger.info(f"New: {len(new)}, Removed: {len(removed)}")

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    logger.info("Starting...")
    try:
        info = await bot.get_me()
        logger.info(f"Connected: @{info.username}")
    except Exception as e:
        logger.error(f"Token error: {str(e)}")
        return
    while True:
        try:
            await check_changes(bot)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped")

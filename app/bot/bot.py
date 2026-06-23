import os
from dotenv import load_dotenv
load_dotenv()

from telebot import TeleBot
from telebot import apihelper
if len(os.getenv('TELEGRAM_BOT_PROXY', '')) > 2:
    apihelper.proxy = {
        'http': os.getenv('TELEGRAM_BOT_PROXY'),
        'https': os.getenv('TELEGRAM_BOT_PROXY')
    }

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN: exit('Не указан токен для бота')
ADMINS = os.getenv('TELEGRAM_BOT_ADMIN_IDS', '')

bot = TeleBot(TOKEN.strip(), parse_mode='html')

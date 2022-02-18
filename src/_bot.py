import os

import aiogram
import dotenv


dotenv.load_dotenv()

TOKEN = os.getenv('BOT_TOKEN', None)
if TOKEN is None:
    raise ValueError('Environment variable "BOT_TOKEN" was not set.')

bot = aiogram.Bot(token=os.getenv('BOT_TOKEN'))
dp = aiogram.Dispatcher(bot)

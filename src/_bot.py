import aiogram

import _config


bot = aiogram.Bot(token=_config.CONFIG['BOT_TOKEN'])
dp = aiogram.Dispatcher(bot)

import aiogram

import _utils


bot = aiogram.Bot(token=_utils.CONFIG['BOT_TOKEN'])
dp = aiogram.Dispatcher(bot)

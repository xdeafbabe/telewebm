import logging
import os

import aiogram
import dotenv

import _bot
import _handlers  # noqa: F401


if __name__ == '__main__':
    dotenv.load_dotenv()
    logging.basicConfig(level=os.getenv('LOGGING_LEVEL', logging.DEBUG))
    aiogram.executor.start_polling(_bot.dp, skip_updates=True)

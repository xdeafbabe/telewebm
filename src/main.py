import logging
import os

import aiogram
import dotenv

import _bot


if __name__ == '__main__':
    dotenv.load_dotenv()
    logging.basicConfig(level=os.getenv('LOGGING_LEVEL', logging.DEBUG))
    aiogram.executor.start_polling(_bot.dp, skip_updates=True)

    print('Hello from WebM2MP4Bot!')

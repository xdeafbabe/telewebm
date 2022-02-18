import logging

import aiogram

import _bot
import _handlers  # noqa: F401
import _config


if __name__ == '__main__':
    logging.basicConfig(level=_config.CONFIG['LOGGING_LEVEL'])
    aiogram.executor.start_polling(_bot.dp, skip_updates=True)

import logging

import aiogram

import _bot
import _chat  # noqa: F401
import _inline  # noqa: F401
import _utils


if __name__ == '__main__':
    logging.basicConfig(level=_utils.CONFIG['LOGGING_LEVEL'])
    aiogram.executor.start_polling(_bot.dp, skip_updates=True)

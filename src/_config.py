import os

import dotenv


dotenv.load_dotenv()

KEYS: list[str] = [
    'STUB_VIDEO_URL', 'STUB_THUMBNAIL_URL', 'UPLOAD_CHANNEL_ID',
    'BOT_TOKEN', 'LOGGING_LEVEL', 'DB_URL',
]

CONFIG: dict[str, str] = {}

for key in KEYS:
    value = os.getenv(key, None)

    if value is None:
        raise ValueError(f'Environment variable {key!r} was not set.')

    CONFIG[key] = value

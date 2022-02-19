import enum
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


class StatusEnum(enum.Enum):
    NOTFOUND = 'Provided file was not found.'
    NOTAWEBM = 'Provided file is not a WebM.'
    NOTAURL = 'Provided string is not a URL.'
    FAILED = 'Conversion failed.'
    TIMEOUT = 'Conversion took too long.'
    SUCCESS = 'Success.'

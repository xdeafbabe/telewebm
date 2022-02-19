import enum
import os

import dotenv


dotenv.load_dotenv()

KEYS: list[str] = [
    'STUB_VIDEO_URL', 'STUB_THUMBNAIL_URL', 'UPLOAD_CHANNEL_ID',
    'BOT_TOKEN', 'LOGGING_LEVEL', 'DATABASE_URL', 'MAX_FILE_SIZE',
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
    TOOLARGE = 'Provided file is too large.'
    NOTAURL = 'Provided string is not a URL.'
    FAILED = 'Conversion failed.'
    SUCCESS = 'Success.'

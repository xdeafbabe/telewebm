import os
import typing

import async_lru
import asyncpg
import asyncpg.connection
import dotenv


dotenv.load_dotenv()

DB_URL = os.getenv('DB_URL', None)
if DB_URL is None:
    raise ValueError('Environment variable "DB_URL" was not set.')


@async_lru.alru_cache
async def get_session() -> asyncpg.connection.Connection:
    session = await asyncpg.connect(DB_URL)
    await session.execute((
        'CREATE TABLE IF NOT EXISTS uploaded '
        '(url text PRIMARY KEY, file_id text NOT NULL)'
    ))
    return session


async def insert(url: str, file_id: str) -> None:
    session = await get_session()
    await session.execute(
        'INSERT INTO uploaded (url, file_id) VALUES ($1, $2);',
        url, file_id,
    )


async def get(url: str) -> typing.Optional[str]:
    session = await get_session()
    row = await session.execute('SELECT file_id FROM uploaded WHERE url = $1', url)
    if row:
        return row.url

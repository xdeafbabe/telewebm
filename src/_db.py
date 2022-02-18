import typing

import asyncpg
import asyncpg.connection

import _config


SESSION: typing.Optional[asyncpg.connection.Connection] = None


async def get_session() -> asyncpg.connection.Connection:
    global SESSION

    if SESSION is None:
        SESSION = await asyncpg.connect(_config.CONFIG['DB_URL'])
        await SESSION.execute((
            'CREATE TABLE IF NOT EXISTS uploaded '
            '(url text PRIMARY KEY, file_id text NOT NULL)'
        ))

    return SESSION


async def insert(url: str, file_id: str) -> None:
    session = await get_session()
    await session.execute(
        'INSERT INTO uploaded (url, file_id) VALUES ($1, $2);',
        url, file_id,
    )


async def get(url: str) -> typing.Optional[str]:
    session = await get_session()
    row = await session.fetchrow('SELECT file_id FROM uploaded WHERE url = $1', url)
    if row:
        return row['file_id']

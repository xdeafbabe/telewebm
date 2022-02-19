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
            'CREATE TABLE IF NOT EXISTS by_url '
            '(url text PRIMARY KEY, file_id text NOT NULL);'
            'CREATE TABLE IF NOT EXISTS by_document_id '
            '(document_id text PRIMARY KEY, file_id text NOT NULL);'))

    return SESSION


async def insert_by_url(url: str, file_id: str) -> None:
    session = await get_session()
    await session.execute(
        'INSERT INTO by_url (url, file_id) VALUES ($1, $2);',
        url, file_id)


async def get_by_url(url: str) -> typing.Optional[str]:
    session = await get_session()
    row = await session.fetchrow('SELECT file_id FROM by_url WHERE url = $1', url)
    if row:
        return row['file_id']


async def insert_by_document_id(document_id: str, file_id: str) -> None:
    session = await get_session()
    await session.execute(
        'INSERT INTO by_document_id (document_id, file_id) VALUES ($1, $2);',
        document_id, file_id)


async def get_by_document_id(document_id: str) -> typing.Optional[str]:
    session = await get_session()
    row = await session.fetchrow(
        'SELECT file_id FROM by_document_id WHERE document_id = $1', document_id)
    if row:
        return row['file_id']

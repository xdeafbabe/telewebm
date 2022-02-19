import typing

import asyncpg
import asyncpg.connection

import _utils


SESSION: typing.Optional[asyncpg.connection.Connection] = None


async def get_session() -> asyncpg.connection.Connection:
    global SESSION

    if SESSION is None:
        SESSION = await asyncpg.connect(_utils.CONFIG['DB_URL'])
        await SESSION.execute((
            'CREATE TABLE IF NOT EXISTS by_url '
            '(url text PRIMARY KEY, file_id text, error text);'
            'CREATE TABLE IF NOT EXISTS by_document_id '
            '(document_id text PRIMARY KEY, file_id text, error text);'))

    return SESSION


async def insert_by_url(
    url: str, file_id: typing.Optional[str], error: typing.Optional[str],
) -> None:
    session = await get_session()
    await session.execute(
        'INSERT INTO by_url (url, file_id, error) VALUES ($1, $2, $3);',
        url, file_id, error)


async def get_by_url(url: str) -> typing.Tuple[
    typing.Optional[str], typing.Optional[str],
]:
    session = await get_session()
    row = await session.fetchrow(
        'SELECT file_id, error FROM by_url WHERE url = $1', url)
    if not row:
        return None, None
    return row['file_id'], row['error']


async def insert_by_document_id(
    document_id: str, file_id: typing.Optional[str], error: typing.Optional[str],
) -> None:
    session = await get_session()
    await session.execute(
        'INSERT INTO by_document_id (document_id, file_id, error) VALUES ($1, $2, $3);',
        document_id, file_id, error)


async def get_by_document_id(document_id: str) -> typing.Tuple[
    typing.Optional[str], typing.Optional[str],
]:
    session = await get_session()
    row = await session.fetchrow(
        'SELECT file_id, error FROM by_document_id WHERE document_id = $1', document_id)
    if not row:
        return None, None
    return row['file_id'], row['error']

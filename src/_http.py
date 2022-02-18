import re
import typing

import aiofiles
import httpx
import pydantic

import _enum


class URL(pydantic.BaseModel):
    address: pydantic.HttpUrl


url_pattern = re.compile('^https://2ch.life/\\w+/src/\\d+/\\d+\\.webm$')


async def validate_url(url: str) -> typing.Optional[str]:
    try:
        URL(address=url)
    except pydantic.ValidationError:
        return

    url.replace('http://', 'https://')
    url.replace('https://2ch.hk', 'https://2ch.life')

    if url_pattern.match(url):
        return url


async def check_headers(url: str) -> _enum.StatusEnum:
    async with httpx.AsyncClient(http2=True) as client:
        resp = await client.head(url)

        if resp.status_code == 404:
            return _enum.StatusEnum.NOTFOUND

        if resp.status_code != 200 or resp.headers.get('content-type') != 'video/webm':
            return _enum.StatusEnum.NOTAWEBM

    return _enum.StatusEnum.SUCCESS


async def download_file(url: str, output_file_path: str) -> _enum.StatusEnum:
    async with aiofiles.open(output_file_path, 'wb') as output_file:
        async with httpx.AsyncClient(http2=True) as client:
            async with client.stream('GET', url) as r:
                async for chunk in r.aiter_bytes():
                    await output_file.write(chunk)

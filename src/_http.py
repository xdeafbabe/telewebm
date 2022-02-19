import re
import typing

import aiofiles
import httpx
import pydantic

import _utils


class URL(pydantic.BaseModel):
    address: pydantic.HttpUrl


url_pattern = re.compile('^https://2ch.life/\\w+/src/\\d+/\\d+\\.webm$')


def validate_url(url: str) -> typing.Tuple[
    typing.Optional[str],
    _utils.StatusEnum,
]:
    try:
        URL(address=url)
    except pydantic.ValidationError:
        return None, _utils.StatusEnum.NOTAURL

    url.replace('http://', 'https://')
    url.replace('https://2ch.hk', 'https://2ch.life')

    if not url_pattern.match(url):
        return None, _utils.StatusEnum.NOTAWEBM

    return url, _utils.StatusEnum.SUCCESS


async def check_headers(url: str) -> _utils.StatusEnum:
    async with httpx.AsyncClient(http2=True) as client:
        resp = await client.head(url)

        if resp.status_code == 404:
            return _utils.StatusEnum.NOTFOUND

        if resp.status_code != 200 or resp.headers.get('content-type') != 'video/webm':
            return _utils.StatusEnum.NOTAWEBM

    return _utils.StatusEnum.SUCCESS


async def download_file(url: str, output_file_path: str) -> _utils.StatusEnum:
    async with aiofiles.open(output_file_path, 'wb') as output_file:
        async with httpx.AsyncClient(http2=True) as client:
            async with client.stream('GET', url) as r:
                async for chunk in r.aiter_bytes():
                    await output_file.write(chunk)

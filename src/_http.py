import aiofiles
import httpx

import _utils


async def check_headers(url: str) -> _utils.StatusEnum:
    async with httpx.AsyncClient(http2=True) as client:
        resp = await client.head(url)

        if resp.status_code == 404:
            return _utils.StatusEnum.NOTFOUND

        if resp.status_code != 200 or resp.headers.get('content-type') != 'video/webm':
            return _utils.StatusEnum.NOTAWEBM

        if resp.headers.get('content-length') > int(_utils.CONFIG['MAX_FILE_SIZE']):
            return _utils.StatusEnum.TOOLARGE

    return _utils.StatusEnum.SUCCESS


async def download_file(url: str, output_file_path: str) -> None:
    async with aiofiles.open(output_file_path, 'wb') as output_file:
        async with httpx.AsyncClient(http2=True) as client:
            async with client.stream('GET', url) as resp:
                async for chunk in resp.aiter_bytes():
                    await output_file.write(chunk)

import asyncio
import contextlib
import enum
import typing

import aiofiles
import httpx


class ConversionStatusEnum(enum.Enum):
    NOTAWEBM = 'File at provided link is not a WebM.'
    TIMEOUT = 'Conversion took too long.'
    SUCCESS = 'Success.'


@contextlib.asynccontextmanager
async def convert(url: str) -> typing.Tuple[typing.Optional[str], ConversionStatusEnum]:
    async with httpx.AsyncClient(http2=True) as client:
        resp = await client.head(url)

        if resp.status_code != 200 or resp.headers.get('content-type') != 'video/webm':
            yield None, ConversionStatusEnum.NOTAWEBM
            return

        async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
            input_file_path = f'{tmpdir}/in.webm'
            output_file_path = f'{tmpdir}/out.mp4'

            async with aiofiles.open(input_file_path, 'wb') as input_file:
                async with client.stream('GET', url) as r:
                    async for chunk in r.aiter_bytes():
                        await input_file.write(chunk)

            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-i', input_file_path, output_file_path,
                stderr=asyncio.subprocess.DEVNULL)

            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                yield None, ConversionStatusEnum.TIMEOUT
                return

            if process.returncode != 0:
                yield None, ConversionStatusEnum.NOTAWEBM
                return

            async with aiofiles.open(output_file_path, 'rb') as output_file:
                yield output_file, ConversionStatusEnum.SUCCESS
                return

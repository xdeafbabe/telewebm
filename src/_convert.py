import asyncio
import enum
import os
import typing

import aiofiles
import aiogram
import dotenv
import httpx


dotenv.load_dotenv()

UPLOAD_CHANNEL_ID = os.getenv('UPLOAD_CHANNEL_ID', None)
if UPLOAD_CHANNEL_ID is None:
    raise ValueError('Environment variable "UPLOAD_CHANNEL_ID" was not set.')


class ConversionStatusEnum(enum.Enum):
    NOTAWEBM = 'File at provided link is not a WebM.'
    TIMEOUT = 'Conversion took too long.'
    SUCCESS = 'Success.'


async def convert(
    bot: aiogram.Bot,
    url: str,
) -> typing.Tuple[typing.Optional[str], ConversionStatusEnum]:
    async with httpx.AsyncClient(http2=True) as client:
        resp = await client.head(url)

        if resp.status_code != 200 or resp.headers.get('content-type') != 'video/webm':
            return None, ConversionStatusEnum.NOTAWEBM

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
                return None, ConversionStatusEnum.TIMEOUT

            if process.returncode != 0:
                return None, ConversionStatusEnum.NOTAWEBM

            async with aiofiles.open(output_file_path, 'rb') as output_file:
                sent_video = await bot.send_video(UPLOAD_CHANNEL_ID, output_file)

    return sent_video.video.file_id, ConversionStatusEnum.SUCCESS

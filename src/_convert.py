import asyncio
import contextlib
import typing

import aiofiles
import aiogram

import _http
import _utils


async def upload(bot: aiogram.Bot, video_path: str) -> str:
    async with aiofiles.open(video_path, 'rb') as video:
        post = await bot.send_video(_utils.CONFIG['UPLOAD_CHANNEL_ID'], video)
        return post.video.file_id


async def download(
    document: aiogram.types.Document,
    document_path: str,
) -> _utils.StatusEnum:
    await document.download(destination_file=document_path)


async def run_ffmpeg(
    input_file_path: str, output_file_path: str,
) -> _utils.StatusEnum:
    process = await asyncio.create_subprocess_exec(
        'ffmpeg', '-y', '-i',
        input_file_path, output_file_path,
        stderr=asyncio.subprocess.DEVNULL,
    )

    try:
        await asyncio.wait_for(process.wait(), timeout=30)
    except asyncio.TimeoutError:
        process.kill()
        return _utils.StatusEnum.TIMEOUT

    if process.returncode != 0:
        return _utils.StatusEnum.FAILED

    return _utils.StatusEnum.SUCCESS


@contextlib.asynccontextmanager
async def convert_from_url(url: str) -> typing.Tuple[
    typing.Optional[str],
    _utils.StatusEnum,
]:
    header_status = await _http.check_headers(url)
    if header_status != _utils.StatusEnum.SUCCESS:
        yield None, header_status
        return

    async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
        input_file_path = f'{tmpdir}/in.webm'
        output_file_path = f'{tmpdir}/out.mp4'
        await _http.download_file(url, input_file_path)

        conversion_status = await run_ffmpeg(input_file_path, output_file_path)
        if conversion_status != _utils.StatusEnum.SUCCESS:
            yield None, conversion_status
            return

        yield output_file_path, _utils.StatusEnum.SUCCESS


@contextlib.asynccontextmanager
async def convert_from_document(document: aiogram.types.Document) -> typing.Tuple[
    typing.Optional[str],
    _utils.StatusEnum,
]:
    async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
        input_file_path = f'{tmpdir}/in.webm'
        output_file_path = f'{tmpdir}/out.mp4'
        await download(document, input_file_path)

        conversion_status = await run_ffmpeg(input_file_path, output_file_path)
        if conversion_status != _utils.StatusEnum.SUCCESS:
            yield None, conversion_status
            return

        yield output_file_path, _utils.StatusEnum.SUCCESS

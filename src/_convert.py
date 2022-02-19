import asyncio
import typing

import aiofiles
import aiogram

import _http
import _utils


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
        return _utils.StatusEnum.TOOLARGE

    if process.returncode != 0:
        return _utils.StatusEnum.FAILED

    return _utils.StatusEnum.SUCCESS


async def convert(
    bot: aiogram.Bot, source: typing.Union[str, aiogram.types.Document],
) -> typing.Tuple[typing.Optional[str], _utils.StatusEnum]:
    async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
        input_file_path = f'{tmpdir}/in.webm'
        output_file_path = f'{tmpdir}/out.mp4'

        if isinstance(source, str):
            await _http.download_file(source, input_file_path)
        else:
            await source.download(destination_file=input_file_path)

        conversion_status = await run_ffmpeg(input_file_path, output_file_path)
        video_id = None

        if conversion_status == _utils.StatusEnum.SUCCESS:
            async with aiofiles.open(output_file_path, 'rb') as video:
                post = await bot.send_video(_utils.CONFIG['UPLOAD_CHANNEL_ID'], video)
                video_id = post.video.file_id

        return video_id, conversion_status

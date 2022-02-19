import aiofiles
import aiogram

import _config
import _enum


async def upload(bot: aiogram.Bot, video_path: str) -> str:
    async with aiofiles.open(video_path, 'rb') as video:
        post = await bot.send_video(_config.CONFIG['UPLOAD_CHANNEL_ID'], video)
        return post.video.file_id


async def download(
    document: aiogram.types.Document,
    document_path: str,
) -> _enum.StatusEnum:
    await document.download(destination_file=document_path)

import aiogram

import _bot
import _convert
import _db


@_bot.dp.message_handler(commands=['start', 'help'])
async def welcome(message: aiogram.types.Message) -> None:
    await message.reply((
        'Hello! This is TeleWebM bot. \n'
        'It can help you download a WebM file from 2ch, '
        'convert it to MP4 and send as a regular video.\n'
        'Please send a WebM file or use the bot in inline mode.'
    ))


@_bot.dp.message_handler(content_types=aiogram.types.ContentTypes.DOCUMENT)
async def handle_document(message: aiogram.types.Message) -> None:
    if message.document.mime_type != 'video/webm':
        return
    status = await message.reply('Working...')
    db_document_id = f'{message.document.file_name}{message.document.file.size}'
    video_id = await _db.get_by_document_id(db_document_id)

    if video_id is None:
        async with _convert.convert(
            message.document,
        ) as (video_path, conversion_status):
            if video_path is None:
                status.edit_text(conversion_status.value)
                return

            video_id = await _convert.upload_video(_bot.bot, video_path)
            await _db.insert_by_document_id(db_document_id, video_id)

    await status.delete()
    await message.reply_video(video_id)

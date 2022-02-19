import aiogram

import _bot
import _convert
import _db
import _utils


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
    if message.document.file_size > _utils.CONFIG['MAX_FILE_SIZE']:
        await message.reply('Provided file is too large.')
        return
    status = await message.reply('Working...')
    db_document_id = f'{message.document.file_name}{message.document.file.size}'
    video_id, err = await _db.get_by_document_id(db_document_id)

    if video_id is None:
        if err is not None:
            await status.edit_text(err)
            return

        video_id, conversion_status = await _convert.convert(_bot.bot, message.document)
        if conversion_status != _utils.StatusEnum.SUCCESS:
            await status.edit_text(conversion_status.value)
            await _db.insert_by_document_id(db_document_id, None, conversion_status.value)
            return

        await _db.insert_by_document_id(db_document_id, video_id, None)

    await status.delete()
    await message.reply_video(video_id)

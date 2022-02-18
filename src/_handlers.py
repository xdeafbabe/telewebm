import hashlib

import aiogram.types

import _bot
import _convert
import _db
import _config
import _http


@_bot.dp.message_handler(commands=['start', 'help'])
async def welcome(message: aiogram.types.Message):
    await message.reply((
        'Hello! This is TeleWebM bot. \n'
        'It can help you download a WebM file from 2ch, '
        'convert it to MP4 and send as a regular video.\n'
        'Please note that this bot only works in inline mode.'
    ))


@_bot.dp.inline_handler()
async def inline_handler(inline_query: aiogram.types.InlineQuery) -> None:
    text = inline_query.query.strip() or ''
    url = await _http.validate_url(text)
    result_id = hashlib.md5(text.encode('utf-8')).hexdigest()

    if url is None:
        item = aiogram.types.InlineQueryResultArticle(
            id=result_id,
            title='Invalid 2ch WebM URL.',
            input_message_content=aiogram.types.InputTextMessageContent(
                message_text='Query is not a valid 2ch WebM URL.',
            ),
        )
    else:
        item = aiogram.types.InlineQueryResultVideo(
            id=result_id,
            title='Convert and send!',
            mime_type='video/mp4',
            thumb_url=_config.CONFIG['STUB_THUMBNAIL_URL'],
            video_url=_config.CONFIG['STUB_VIDEO_URL'],
            reply_markup=aiogram.types.InlineKeyboardMarkup(
                inline_keyboard=[[aiogram.types.InlineKeyboardButton(
                    'Tap to convert', callback_data=url,
                )]],
            ),
        )

    await _bot.bot.answer_inline_query(
        inline_query.id, results=[item], cache_time=60 * 60 * 4)


@_bot.dp.callback_query_handler()
async def inline_callback_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    await callback_query.answer('Working...')
    await _bot.bot.edit_message_caption(
        inline_message_id=callback_query.inline_message_id,
        caption='Working...')
    url = callback_query.data
    video_id = await _db.get(url)

    if video_id is None:
        async with _convert.convert_from_url(url) as (
            converted_video, conversion_status,
        ):
            if converted_video is None:
                await _bot.bot.edit_message_caption(
                    inline_message_id=callback_query.inline_message_id,
                    caption=conversion_status.value)
                return

            sent_video = await _bot.bot.send_video(
                _config.CONFIG['UPLOAD_CHANNEL_ID'], converted_video)
            video_id = sent_video.video.file_id
            await _db.insert(url, video_id)

    await _bot.bot.edit_message_media(
        inline_message_id=callback_query.inline_message_id,
        media=aiogram.types.InputMediaVideo(video_id),
    )

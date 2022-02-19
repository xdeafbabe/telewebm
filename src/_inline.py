import functools
import hashlib

import aiogram.types

import _bot
import _convert
import _db
import _config
import _http
import _uploads


@_bot.dp.inline_handler()
async def inline_handler(inline_query: aiogram.types.InlineQuery) -> None:
    text = inline_query.query.strip() or ''
    url, validation_status = _http.validate_url(text)
    result_id = hashlib.md5(text.encode('utf-8')).hexdigest()

    if url is None:
        item = aiogram.types.InlineQueryResultArticle(
            id=result_id,
            title='Invalid 2ch WebM URL.',
            input_message_content=aiogram.types.InputTextMessageContent(
                message_text=validation_status.value,
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

    edit_message_caption = functools.partial(
        _bot.bot.edit_message_caption,
        inline_message_id=callback_query.inline_message_id)

    await edit_message_caption(caption='Working...')
    url = callback_query.data
    video_id = await _db.get_by_url(url)

    if video_id is None:
        async with _convert.convert_from_url(url) as (video_path, conversion_status):
            if video_path is None:
                await edit_message_caption(caption=conversion_status.value)
                return

            video_id = await _uploads.upload(_bot.bot, video_path)
            await _db.insert_by_url(url, video_id)

    await _bot.bot.edit_message_media(
        inline_message_id=callback_query.inline_message_id,
        media=aiogram.types.InputMediaVideo(video_id))

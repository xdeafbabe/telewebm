import functools
import hashlib
import re
import typing

import aiogram.types
import pydantic

import _bot
import _convert
import _db
import _http
import _utils


url_pattern = re.compile('^https://2ch.life/\\w+/src/\\d+/\\d+\\.webm$')


class URL(pydantic.BaseModel):
    address: pydantic.HttpUrl


def validate_url(url: str) -> typing.Tuple[
    typing.Optional[str],
    _utils.StatusEnum,
]:
    try:
        URL(address=url)
    except pydantic.ValidationError:
        return None, _utils.StatusEnum.NOTAURL

    url.replace('http://', 'https://')
    url.replace('https://2ch.hk', 'https://2ch.life')

    if not url_pattern.match(url):
        return None, _utils.StatusEnum.NOTAWEBM

    return url, _utils.StatusEnum.SUCCESS


@_bot.dp.inline_handler()
async def inline_handler(inline_query: aiogram.types.InlineQuery) -> None:
    text = inline_query.query.strip() or ''
    url, validation_status = validate_url(text)
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
            thumb_url=_utils.CONFIG['STUB_THUMBNAIL_URL'],
            video_url=_utils.CONFIG['STUB_VIDEO_URL'],
            reply_markup=aiogram.types.InlineKeyboardMarkup(
                inline_keyboard=[[aiogram.types.InlineKeyboardButton(
                    'Tap to convert', callback_data=url,
                )]],
            ),
        )

    await _bot.bot.answer_inline_query(
        inline_query.id, results=[item], cache_time=60 * 60 * 24)


@_bot.dp.callback_query_handler()
async def inline_callback_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    await callback_query.answer('Working...')

    edit_message_caption = functools.partial(
        _bot.bot.edit_message_caption,
        inline_message_id=callback_query.inline_message_id)

    await edit_message_caption(caption='Working...')
    url = callback_query.data
    video_id, err = await _db.get_by_url(url)

    if video_id is None:
        if err is not None:
            await edit_message_caption(caption=err)
            return

        header_status = await _http.check_headers(url)
        if header_status != _utils.StatusEnum.SUCCESS:
            await edit_message_caption(caption=header_status.value)
            await _db.insert_by_url(url, None, header_status.value)
            return

        video_id, conversion_status = await _convert.convert(_bot.bot, url)
        if conversion_status != _utils.StatusEnum.SUCCESS:
            await edit_message_caption(caption=conversion_status.value)
            await _db.insert_by_url(url, None, conversion_status.value)
            return

        await _db.insert_by_url(url, video_id, None)

    await _bot.bot.edit_message_media(
        inline_message_id=callback_query.inline_message_id,
        media=aiogram.types.InputMediaVideo(video_id))

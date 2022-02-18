import hashlib
import os
import typing

import aiogram.types
import dotenv
import httpx
import pydantic

import _bot
import _convert
import _db


dotenv.load_dotenv()

STUB_VIDEO_URL = os.getenv('STUB_VIDEO_URL', None)
STUB_THUMBNAIL_URL = os.getenv('STUB_THUMBNAIL_URL', None)
UPLOAD_CHANNEL_ID = os.getenv('UPLOAD_CHANNEL_ID', None)
if STUB_VIDEO_URL is None:
    raise ValueError('Environment variable "STUB_VIDEO_URL" was not set.')
if STUB_THUMBNAIL_URL is None:
    raise ValueError('Environment variable "STUB_THUMBNAIL_URL" was not set.')
if UPLOAD_CHANNEL_ID is None:
    raise ValueError('Environment variable "UPLOAD_CHANNEL_ID" was not set.')


class URL(pydantic.BaseModel):
    address: pydantic.HttpUrl


async def validate_url(url: str) -> typing.Optional[str]:
    try:
        URL(address=url)
    except pydantic.ValidationError:
        return

    url.replace('https://2ch.hk', 'https://2ch.life')

    if not url.startswith('https://2ch.life'):
        return

    async with httpx.AsyncClient(http2=True) as client:
        resp = await client.head(url)

        if resp.status_code != 200 or resp.headers.get('content-type') != 'video/webm':
            return

    return url


@_bot.dp.message_handler(commands=['start', 'help'])
async def welcome(message: aiogram.types.Message):
    await message.reply((
        'Hello! This is TeleWebM bot. \n'
        'It can help you download a WebM file from 2ch.hk, '
        'convert them to MP4 and send as a regular video.\n'
        'Please note that this bot only works in inline mode.'
    ))


@_bot.dp.inline_handler()
async def inline(inline_query: aiogram.types.InlineQuery) -> None:
    text = inline_query.query.strip() or ''
    url = await validate_url(text)
    result_id = hashlib.md5(text.encode('utf-8')).hexdigest()

    if url is None:
        item = aiogram.types.InlineQueryResultArticle(
            id=result_id,
            title='Invalid URL',
            input_message_content=aiogram.types.InputTextMessageContent(
                message_text='Query is not a valid 2ch.hk or 2ch.life WebM URL.',
            ),
        )
    else:
        item = aiogram.types.InlineQueryResultVideo(
            id=result_id,
            title='Convert and send!',
            mime_type='video/mp4',
            thumb_url=STUB_THUMBNAIL_URL,
            video_url=STUB_VIDEO_URL,
            reply_markup=aiogram.types.InlineKeyboardMarkup(
                inline_keyboard=[[aiogram.types.InlineKeyboardButton(
                    'Tap to convert', callback_data=url,
                )]],
            ),
        )

    await _bot.bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)


@_bot.dp.callback_query_handler()
async def callback_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    await _bot.bot.edit_message_caption(
        inline_message_id=callback_query.inline_message_id,
        caption='Working...',
    )

    url = callback_query.data

    video_id = await _db.get(url)

    if video_id is None:
        async with _convert.convert(url) as (converted_video, conversion_status):
            if converted_video is None:
                await _bot.bot.edit_message_caption(
                    inline_message_id=callback_query.inline_message_id,
                    caption=conversion_status.value,
                )
                return

            sent_video = await _bot.bot.send_video(UPLOAD_CHANNEL_ID, converted_video)
            video_id = sent_video.video.file_id
            await _db.insert(url, video_id)

    await _bot.bot.edit_message_media(
        inline_message_id=callback_query.inline_message_id,
        media=aiogram.types.InputMediaVideo(video_id),
    )

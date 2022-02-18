import hashlib
import os

import aiogram.types
import dotenv
import pydantic

import _bot
import _convert
import _db


dotenv.load_dotenv()

STUB_VIDEO_URL = os.getenv('STUB_VIDEO_URL', None)
STUB_THUMBNAIL_URL = os.getenv('STUB_THUMBNAIL_URL', None)
if STUB_VIDEO_URL is None:
    raise ValueError('Environment variable "STUB_VIDEO_URL" was not set.')
if STUB_THUMBNAIL_URL is None:
    raise ValueError('Environment variable "STUB_THUMBNAIL_URL" was not set.')


class URL(pydantic.BaseModel):
    address: pydantic.HttpUrl


def validate_url(url: str) -> bool:
    try:
        URL(address=url)
    except pydantic.ValidationError:
        return False

    url.replace('https://2ch.hk', 'https://2ch.life')

    if not url.startswith('https://2ch.life'):
        return False

    return True


@_bot.dp.message_handler(commands=['start', 'help'])
async def welcome(message: aiogram.types.Message):
    await message.reply('This bot only works in inline mode.')


@_bot.dp.inline_handler()
async def inline(inline_query: aiogram.types.InlineQuery) -> None:
    text = inline_query.query.strip() or ''

    if not validate_url(text):
        await _bot.bot.answer_inline_query(inline_query.id, results=[], cache_time=1)
        return

    result_id = hashlib.md5(text.encode('utf-8')).hexdigest()

    item = aiogram.types.InlineQueryResultVideo(
        id=result_id,
        title='Convert and send!',
        mime_type='video/mp4',
        thumb_url=STUB_THUMBNAIL_URL,
        video_url=STUB_VIDEO_URL,
        reply_markup=aiogram.types.InlineKeyboardMarkup(
            row_width=1,
            inline_keyboard=[[aiogram.types.InlineKeyboardButton(
                'Convert', callback_data=text,
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
        video_id, conversion_status = await _convert.convert(_bot.bot, url)

        if video_id is None:
            await _bot.bot.edit_message_caption(
                inline_message_id=callback_query.inline_message_id,
                caption=conversion_status.value,
            )

            return

        await _db.insert(url, video_id)

    await _bot.bot.edit_message_media(
        inline_message_id=callback_query.inline_message_id,
        media=aiogram.types.InputMediaVideo(video_id),
    )

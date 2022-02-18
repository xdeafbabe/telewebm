import asyncio
import asyncio.subprocess
import hashlib
import functools

import aiofiles
import aiogram.types
import httpx
import pydantic

import _bot


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
        thumb_url='https://2ch.life/favicon.ico',
        video_url='https://raw.githubusercontent.com/Euromance/telewebm/main/static/converting_stub.mp4',
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
    message_id = callback_query.inline_message_id
    edit_text = functools.partial(
        _bot.bot.edit_message_caption, inline_message_id=message_id)
    await edit_text(caption='Working...')

    url = callback_query.data

    async with httpx.AsyncClient(http2=True) as client:
        resp = await client.head(url)

        if resp.status_code != 200 or resp.headers.get('content-type') != 'video/webm':
            await edit_text(caption='Link target is not a WebM file. Aborted.')
            return

        async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
            input_file_path = f'{tmpdir}/in.webm'
            output_file_path = f'{tmpdir}/out.mp4'

            await edit_text(caption='Downloading...')

            async with aiofiles.open(input_file_path, 'wb') as input_file:
                async with client.stream('GET', url) as r:
                    async for chunk in r.aiter_bytes():
                        await input_file.write(chunk)

            await edit_text(caption='Converting...')

            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-i', input_file_path, output_file_path,
                stderr=asyncio.subprocess.DEVNULL)

            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                await edit_text(caption='Conversion took too long. Aborted.')
                return

            if process.returncode != 0:
                await edit_text(caption='Conversion failed. Aborted.')
                return

            async with aiofiles.open(output_file_path, 'rb') as output_file:
                sent_video = await _bot.bot.send_video('-1001669171944', output_file)

    await edit_text(caption='')
    await _bot.bot.edit_message_media(
        inline_message_id=callback_query.inline_message_id,
        media=aiogram.types.InputMediaVideo(sent_video.video.file_id),
    )

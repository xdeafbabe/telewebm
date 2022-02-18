import asyncio
import asyncio.subprocess
import hashlib

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
async def send_welcome(message: aiogram.types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@_bot.dp.message_handler()
async def convert(message: aiogram.types.Message) -> None:
    status_message = await message.answer('Working...')

    if not validate_url(message.text):
        await status_message.edit_text('Not a 2ch link. Aborted.')
        return

    url = message.text

    async with httpx.AsyncClient(http2=True) as client:
        resp = await client.head(url)

        if resp.status_code != 200 or resp.headers.get('content-type') != 'video/webm':
            await status_message.edit_text('Link target is not a WebM file. Aborted.')
            return

        async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
            input_file_path = f'{tmpdir}/in.webm'
            output_file_path = f'{tmpdir}/out.mp4'

            await status_message.edit_text('Downloading...')

            async with aiofiles.open(input_file_path, 'wb') as input_file:
                async with client.stream('GET', url) as r:
                    async for chunk in r.aiter_bytes():
                        await input_file.write(chunk)

            await status_message.edit_text('Converting...')

            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-i', input_file_path, output_file_path,
                stderr=asyncio.subprocess.DEVNULL)

            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                await status_message.edit_text('Conversion took too long. Aborted.')
                return

            if process.returncode != 0:
                await status_message.edit_text('Failed to convert. Aborted.')
                return

            async with aiofiles.open(output_file_path, 'rb') as output_file:
                await _bot.bot.send_video(message.chat.id, output_file)

    await status_message.delete()


@_bot.dp.inline_handler()
async def inline(inline_query: aiogram.types.InlineQuery) -> None:
    text = inline_query.query.strip() or ''

    if not validate_url(text):
        await _bot.bot.answer_inline_query(inline_query.id, results=[], cache_time=3600)
        return

    url = text

    input_content = aiogram.types.InputTextMessageContent(url)
    result_id: str = hashlib.md5(text.encode()).hexdigest()

    item = aiogram.types.InlineQueryResultArticle(
        id=result_id,
        title='Convert and send!',
        input_message_content=input_content,
        reply_markup=aiogram.types.InlineKeyboardMarkup(
            row_width=1,
            inline_keyboard=[aiogram.types.InlineKeyboardButton('Converting...')],
        ),
    )

    await _bot.bot.answer_inline_query(inline_query.id, results=[item], cache_time=3600)

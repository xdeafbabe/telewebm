import aiogram.types

import _bot


@_bot.dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: aiogram.types.Message) -> None:
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

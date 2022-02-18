import asyncio
import asyncio.subprocess
import secrets

import aiofiles


async def convert() -> None:
    temp_file_name = secrets.token_urlsafe(32) + '.mp4'

    async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
        temp_file_path = f'{tmpdir}/{temp_file_name}'

        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-i',
            'static/bitch.webm',
            temp_file_path,
            stderr=asyncio.subprocess.DEVNULL,
        )

        try:
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            print('Conversion took too long.')
            return

        if process.returncode != 0:
            print('Failed to convert.')
            return

        async with aiofiles.open(temp_file_path, 'rb') as converted_temp:
            async with aiofiles.open('static/bitch.mp4', 'wb') as converted:
                while True:
                    chunk = await converted_temp.read(1024)

                    if not chunk:
                        break

                    await converted.write(chunk)


if __name__ == '__main__':
    asyncio.run(convert())

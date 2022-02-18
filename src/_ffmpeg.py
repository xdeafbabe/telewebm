import asyncio

import _enum


async def run_ffmpeg(
    input_file_path: str, output_file_path: str,
) -> _enum.StatusEnum:
    process = await asyncio.create_subprocess_exec(
        'ffmpeg', '-y', '-i',
        input_file_path, output_file_path,
        stderr=asyncio.subprocess.DEVNULL,
    )

    try:
        await asyncio.wait_for(process.wait(), timeout=30)
    except asyncio.TimeoutError:
        process.kill()
        return _enum.StatusEnum.TIMEOUT

    if process.returncode != 0:
        return _enum.StatusEnum.FAILED

    return _enum.StatusEnum.SUCCESS

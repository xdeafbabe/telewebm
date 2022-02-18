import contextlib
import typing

import aiofiles
import aiogram

import _enum
import _ffmpeg
import _http
import _uploads


@contextlib.asynccontextmanager
async def convert_from_url(url: str) -> typing.Tuple[
    typing.Optional[str],
    _enum.StatusEnum,
]:
    header_status = await _http.check_headers(url)
    if header_status != _enum.StatusEnum.SUCCESS:
        yield None, header_status
        return

    async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
        input_file_path = f'{tmpdir}/in.webm'
        output_file_path = f'{tmpdir}/out.mp4'

        await _http.download_file(url, input_file_path)

        conversion_status = await _ffmpeg.run_ffmpeg(input_file_path, output_file_path)
        if conversion_status != _enum.StatusEnum.SUCCESS:
            yield None, conversion_status
            return

        yield output_file_path, _enum.StatusEnum.SUCCESS


@contextlib.asynccontextmanager
async def convert_from_document(document: aiogram.types.Document) -> typing.Tuple[
    typing.Optional[str],
    _enum.StatusEnum,
]:
    async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
        input_file_path = f'{tmpdir}/in.webm'
        output_file_path = f'{tmpdir}/out.mp4'

        download_status = await _uploads.download(document, input_file_path)
        if download_status != _enum.StatusEnum.SUCCESS:
            yield None, download_status

        conversion_status = await _ffmpeg.run_ffmpeg(input_file_path, output_file_path)
        if conversion_status != _enum.StatusEnum.SUCCESS:
            yield None, conversion_status
            return

        yield output_file_path, _enum.StatusEnum.SUCCESS

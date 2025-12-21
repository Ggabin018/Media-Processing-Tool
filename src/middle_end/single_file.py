import os
import shutil
import tempfile
from pathlib import Path

from toolbox.utils import regularize_path
from back_end.video_manip import video_cut, video_compress, is_video, multiple_cuts_plus_concatenate
from back_end.audio_manip import audio_replace, audio_combine
from back_end.media_converter import convert_media
from toolbox.wrapper import exception_as_str

temp_file = None


def make_temp_copy(src_path: Path) -> str | None:
    global temp_file

    _, file_extension = os.path.splitext(src_path)
    if temp_file is not None and os.path.exists(temp_file):
        os.unlink(temp_file)
    with tempfile.NamedTemporaryFile(mode='w', suffix=file_extension, delete=False) as temp_path:
        temp_file = temp_path.name
    tmp = shutil.copy(src_path, temp_file)
    if is_video(tmp):
        return video_compress(tmp, target_bitrate=1000, min_resolution=480, vcodec="libx264")

@exception_as_str(2)
def cut_video(video_path: str, start: str | None, end: str | None) -> tuple[str, str | None]:
    video_path = Path(video_path)

    path = video_cut(video_path, start=start, end=end)
    return path, make_temp_copy(path)

@exception_as_str(3)
def convert_media_to_media(video_path: str, ext: str) -> tuple[str, str | None, str | None]:
    """
    :returns: file_path, video_path, audio_path
    """
    video_path = Path(video_path)
    
    path = convert_media(video_path, ext)
    if ext in ["mp4", "mov", "avi", "webm", "mkv"]:
        return path, make_temp_copy(path), None
    return path, None, make_temp_copy(path)

@exception_as_str(2)
def modify_audio(video_path: str, audio_path: str, opt: str = "replace") -> tuple[str, str | None]:
    video_path = Path(video_path)
    audio_path = Path(audio_path)

    if opt == "replace":
        path = audio_replace(regularize_path(video_path), regularize_path(audio_path))
    else:
        path = audio_combine(regularize_path(video_path), regularize_path(audio_path))
    return path, make_temp_copy(path)


@exception_as_str(2)
def compress_vid(video_path: str, bitrate: int = 8000, min_res: str = 1080, vcodec: str = "hevc_nvenc"):
    video_path = Path(video_path)
    path = video_compress(video_path, target_bitrate=bitrate, min_resolution=int(min_res), vcodec=vcodec)
    return path, make_temp_copy(path)


@exception_as_str(2)
def cut_and_concate(video_path_str: str, times: list[list[str, str]]) -> tuple[str, str | None]:
    video_path = Path(video_path_str)

    path = multiple_cuts_plus_concatenate(video_path, times)
    return path, make_temp_copy(path)

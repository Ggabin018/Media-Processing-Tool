import os
import shutil
import tempfile

from toolbox.utils import to_seconds
from toolbox.paths import require_file
from toolbox.wrapper import exception_as_str
from back_end.video_manip import video_cut, video_compress, is_video, multiple_cuts_plus_concatenate
from back_end.audio_manip import audio_replace, audio_combine
from back_end.media_converter import convert_media

temp_file = None


def make_temp_copy(src_path: str) -> str | None:
    """Small copy for the Gradio preview. Optional: returns None on any error."""
    global temp_file
    try:
        _, file_extension = os.path.splitext(src_path)
        if temp_file is not None and os.path.exists(temp_file):
            os.unlink(temp_file)
        with tempfile.NamedTemporaryFile(mode='w', suffix=file_extension, delete=False) as temp_path:
            temp_file = temp_path.name
        tmp = shutil.copy(src_path, temp_file)
        if is_video(tmp):
            return video_compress(tmp, target_bitrate=1000, min_resolution=480, vcodec="libx264")
    except Exception:
        return None


@exception_as_str(2)
def cut_video(video_path: str, start: str | None, end: str | None) -> tuple[str, str | None]:
    path = video_cut(require_file(video_path), start=start, end=end)
    return path, make_temp_copy(path)


@exception_as_str(3)
def convert_media_to_media(video_path: str, ext: str) -> tuple[str, str | None, str | None]:
    """:returns: result text, video preview, audio preview"""
    path = convert_media(require_file(video_path), ext)
    if ext in ["mp4", "mov", "avi", "webm", "mkv"]:
        return path, make_temp_copy(path), None
    return path, None, make_temp_copy(path)


@exception_as_str(2)
def modify_audio(video_path: str, audio_path: str, opt: str = "replace") -> tuple[str, str | None]:
    video_path = require_file(video_path)
    audio_path = require_file(audio_path)
    if opt == "replace":
        path = audio_replace(video_path, audio_path)
    else:
        path = audio_combine(video_path, audio_path)
    return path, make_temp_copy(path)


@exception_as_str()
def compress_vid(video_path: str, bitrate: int = 8000, min_res: str = "1080", vcodec: str = "hevc_nvenc") -> str:
    return video_compress(require_file(video_path), target_bitrate=bitrate, min_resolution=int(min_res),
                          vcodec=vcodec)


def parse_input(input_str: str | None) -> list[str]:
    """One time per line (seconds or HH:MM:SS). Empty lines are ignored."""
    lines = [line.strip() for line in (input_str or "").splitlines() if line.strip()]
    for line in lines:
        if to_seconds(line) is None:
            raise ValueError(f"invalid time {line!r}")
    return lines


@exception_as_str(2)
def cut_and_concate(video_path: str, input_start: str, input_end: str) -> tuple[str, str | None]:
    video_path = require_file(video_path)

    starts = parse_input(input_start)
    ends: list[str | None] = parse_input(input_end)

    if not starts:
        raise ValueError("no start time")

    # last segment can go to the end of the video
    if len(ends) + 1 == len(starts):
        ends.append(None)

    if len(starts) != len(ends):
        raise ValueError(f"starts={len(starts)} != ends={len(ends)}")

    path = multiple_cuts_plus_concatenate(video_path, list(zip(starts, ends)))
    return path, make_temp_copy(path)

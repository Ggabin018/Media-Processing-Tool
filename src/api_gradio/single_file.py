import os
import shutil
import tempfile

from toolbox.utils import regularize_path
from file_manipulation.video_manip import video_cut, video_compress, is_video
from file_manipulation.audio_manip import audio_replace, audio_combine
from file_manipulation.media_converter import convert_media

temp_file = None


def make_temp_copy(src_path: str) -> str | None:
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


def cut_video(video_path: str, start: str | None, end: str | None, fast_flag: bool = False) -> tuple[str, str | None]:
    video_path = regularize_path(video_path)
    if not os.path.exists(video_path):
        return f"{video_path} does not exit", None

    path = video_cut(video_path, start=start, end=end, fast_flag=fast_flag)
    return path, make_temp_copy(path)


def convert_media_to_media(video_path: str, ext: str) -> tuple[str, str | None, str | None]:
    try:
        path = convert_media(regularize_path(video_path), ext)
        if ext in ["mp4", "mov", "avi", "webm", "mkv"]:
            return path, make_temp_copy(path), None
        return path, None, make_temp_copy(path)
    except Exception as e:
        return f"Error: {str(e)}", None, None


def modify_audio(video_path: str, audio_path: str, opt: str = "replace") -> tuple[str, str | None]:
    try:
        if opt == "replace":
            path = audio_replace(regularize_path(video_path), regularize_path(audio_path))
        else:
            path = audio_combine(regularize_path(video_path), regularize_path(audio_path))
        return path, make_temp_copy(path)
    except Exception as e:
        return f"Error: {str(e)}", None


def compress_vid(video_path: str, bitrate: int = 8000, min_res: int = 1080, vcodec: str = "hevc_nvenc"):
    try:
        path = video_compress(video_path, target_bitrate=bitrate, min_resolution=min_res, vcodec=vcodec)
        return path, make_temp_copy(path)
    except Exception as e:
        return f"Error: {str(e)}", None

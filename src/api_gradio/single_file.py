import os
import shutil
import tempfile

from toolbox.utils import regularize_path

from file_manipulation.video_modif import (
    video_cut,
    video_compress
)

from file_manipulation.audio_modif import (
    audio_replace,
    audio_combine
)

from file_manipulation.convert import (
    convert_media
)

temp_file = None

def make_temp_copy(src_path:str)->str:
    global temp_file
    _, file_extension = os.path.splitext(src_path)
    if temp_file is not None and os.path.exists(temp_file):
        os.unlink(temp_file)
    with tempfile.NamedTemporaryFile(mode='w', suffix=file_extension, delete=False) as temp_path:
        temp_file = temp_path.name
    return shutil.copy(src_path, temp_file)

def cut_video(video_path: str, start, end) -> tuple[str, str|None]:
    video_path = regularize_path(video_path)
    if not os.path.exists(video_path):
        return f"{video_path} does not exit", None

    path = video_cut(video_path, start=start, end=end)
    return path, make_temp_copy(path)


def convert_media_to_media(video_path: str, ext: str) -> tuple[str,str|None,str|None]:
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
        return path, path
    except Exception as e:
        return f"Error: {str(e)}", None


def compress_vid(video_path: str, bitrate: int = 8000):
    try:
        dir_path = os.path.split(video_path)[0]
        output_folder = os.path.join(dir_path, "output")
        os.makedirs(output_folder, exist_ok=True)
        path = video_compress(video_path, target_bitrate=bitrate)
        return path, path
    except Exception as e:
        return f"Error: {str(e)}", None
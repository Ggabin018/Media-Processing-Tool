import os

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


def cut_video(video_path: str, start, end) -> str:
    video_path = regularize_path(video_path)
    if not os.path.exists(video_path):
        raise Exception(f"{video_path} does not exit")

    path = video_cut(video_path, start=start, end=end)
    return path

def convert_video_to_mp3(video_path: str) -> tuple[str, str | None]:
    try:
        path = convert_media(regularize_path(video_path))
        return path, path
    except Exception as e:
        return f"Error: {str(e)}", None


def convert_video_to_video(video_path: str, ext: str) -> str:
    try:
        return convert_media(regularize_path(video_path), ext)
    except Exception as e:
        return f"Error: {str(e)}"


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
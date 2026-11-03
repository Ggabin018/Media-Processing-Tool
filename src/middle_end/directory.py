from back_end.dir_manip import (
    dir_convert_media,
    dir_audio_replace,
    dir_audio_combine,
    dir_convert_video_to_video,
    dir_compress_videos, compress_videos_dossier_parent
)

from toolbox.paths import require_dir
from toolbox.wrapper import exception_as_str


@exception_as_str()
def directory_media2media(video_dir_path: str, ext: str) -> str:
    return dir_convert_media(require_dir(video_dir_path), ext)


@exception_as_str()
def directory_audio_modify(video_dir_path: str, audio_dir_path: str, opt: str = "replace", randomize: bool = True) -> str:
    video_dir_path = require_dir(video_dir_path)
    audio_dir_path = require_dir(audio_dir_path)
    if opt == "replace":
        return dir_audio_replace(video_dir_path, audio_dir_path, randomize)
    return dir_audio_combine(video_dir_path, audio_dir_path, randomize)


@exception_as_str()
def directory_convert(dir_path: str, ext: str) -> str:
    return dir_convert_video_to_video(require_dir(dir_path), ext)


@exception_as_str()
def directory_compress(dir_path: str, bitrate: int = 8000, min_res: str = "1080", vcodec="hevc_nvenc") -> str:
    return dir_compress_videos(require_dir(dir_path), bitrate, int(min_res), vcodec)


def pdirectory_compress(dir_path: str, bitrate: int = 8000, min_res: str = "1080", vcodec="hevc_nvenc") -> None:
    """No Gradio output: errors are printed in the console."""
    try:
        compress_videos_dossier_parent(require_dir(dir_path), bitrate, int(min_res), vcodec)
    except Exception as e:
        print(f"Error: {e}")

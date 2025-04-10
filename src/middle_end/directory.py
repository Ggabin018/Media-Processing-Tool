from back_end.dir_manip import (
    dir_convert_media,
    dir_audio_replace,
    dir_audio_combine,
    dir_convert_video_to_video,
    dir_compress_videos
)

from toolbox.utils import regularize_path

def directory_media2media(video_dir_path: str, ext: str) -> str:
    try:
        return dir_convert_media(regularize_path(video_dir_path), ext)
    except Exception as e:
        return f"Error: {str(e)}"


def directory_audio_modify(video_dir_path: str, audio_dir_path: str, opt: str = "replace") -> str:
    try:
        if opt == "replace":
            return dir_audio_replace(video_dir_path, audio_dir_path)
        return dir_audio_combine(video_dir_path, audio_dir_path)
    except Exception as e:
        return f"Error: {str(e)}"


def directory_convert(dir_path: str, ext: str) -> str:
    try:
        return dir_convert_video_to_video(dir_path, ext)
    except Exception as e:
        return f"Error: {str(e)}"


def directory_compress(dir_path: str, bitrate: int = 8000, min_res: int = 1080, vcodec="hevc_nvenc") -> str:
    try:
        return dir_compress_videos(dir_path, bitrate, min_res, vcodec)
    except Exception as e:
        return f"Error: {str(e)}"
from file_manipulation.files_manip import (
    files_audio_combine,
    files_audio_replace,
    files_compress_videos,
    files_audio_extract,
    files_convert_video_to_video
)

from toolbox.utils import regularize_path

def batch_convert_video_to_video(videos: list[str], ext: str) -> str:
    try:
        videos = [regularize_path(p) for p in videos]
        path = files_convert_video_to_video(videos, ext)
        return path
    except Exception as e:
        return f"Error: {str(e)}"


def batch_modify_audio(videos: list[str], audios: list[str], opt: str = "replace") -> str:
    try:
        videos = [regularize_path(p) for p in videos]
        audios = [regularize_path(p) for p in audios]
        if opt == "replace":
            paths = files_audio_replace(videos, audios)
        else:
            paths = files_audio_combine(videos, audios)
        return paths
    except Exception as e:
        return f"Error: {str(e)}"


def batch_compress(videos: list[str], bitrate: int = 8000) -> str:
    try:
        videos = [regularize_path(p) for p in videos]
        return files_compress_videos(videos, bitrate)
    except Exception as e:
        return f"Error: {str(e)}"


def batch_extract_audio(videos: list[str]) -> str:
    try:
        videos = [regularize_path(p) for p in videos]
        return files_audio_extract(videos)
    except Exception as e:
        return f"Error: {str(e)}"
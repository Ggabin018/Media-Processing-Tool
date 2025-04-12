from back_end.files_manip import (
    files_audio_combine,
    files_audio_replace,
    files_compress_videos,
    files_convert,
    files_convert_video_to_video
)

from toolbox.utils import get_correct_files


def batch_convert_video_to_video(videos: list[str], ext: str) -> str:
    try:
        videos = get_correct_files(videos)
        if not videos:
            return "No provided videos"
        path = files_convert_video_to_video(videos, ext)
        return path
    except Exception as e:
        return f"Error: {str(e)}"


def batch_modify_audio(videos: list[str], audios: list[str], opt: str = "replace") -> str:
    try:
        videos = get_correct_files(videos)
        if not videos:
            return "No provided videos"
        audios = get_correct_files(audios)
        if not audios:
            return "No provided audios"
        if opt == "replace":
            paths = files_audio_replace(videos, audios)
        else:
            paths = files_audio_combine(videos, audios)
        return paths
    except Exception as e:
        return f"Error: {str(e)}"


def batch_compress(videos: list[str], bitrate, min_res, vcodec) -> str:
    try:
        videos = get_correct_files(videos)
        if not videos:
            return "No provided videos"
        return files_compress_videos(videos, bitrate, min_res, vcodec)
    except Exception as e:
        return f"Error: {str(e)}"


def batch_convert(medias: list[str], ext: str) -> str:
    try:
        medias = get_correct_files(medias)
        if not medias:
            return "No provided medias"
        return files_convert(medias, ext)
    except Exception as e:
        return f"Error: {str(e)}"

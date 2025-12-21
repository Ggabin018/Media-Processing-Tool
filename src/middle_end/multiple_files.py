from back_end.files_manip import (
    files_audio_combine,
    files_audio_replace,
    files_compress_videos,
    files_convert,
    files_convert_video_to_video
)
from back_end.video_manip import videos_concat
from pathlib import Path

def get_files_path(files: list[str]) -> list[Path]:
    res = []
    files = [f[0] for f in files]
    for f in files:
        if f == "":
            continue
        f = Path(f)
        if f.exists():
            res.append(f)
    return res


def batch_convert_video_to_video(videos: list[str], ext: str) -> str:
    try:
        videos = get_files_path(videos)
        if not videos:
            return "No provided videos"
        paths = files_convert_video_to_video(videos, ext)
        return paths
    except Exception as e:
        return f"Error: {str(e)}"


def batch_modify_audio(videos: list[str], audios: list[str], opt: str = "replace", randomize: bool = True) -> str:
    try:
        videos = get_files_path(videos)
        if not videos:
            return "No provided videos"
        audios = get_files_path(audios)
        if not audios:
            return "No provided audios"
        if opt == "replace":
            paths = files_audio_replace(videos, audios, randomize)
        else:
            paths = files_audio_combine(videos, audios, randomize)
        return paths
    except Exception as e:
        return f"Error: {str(e)}"


def batch_compress(videos: list[str], bitrate, min_res, vcodec) -> str:
    try:
        videos = get_files_path(videos)
        if not videos:
            return "No provided videos"
        return files_compress_videos(videos, bitrate, min_res, vcodec)
    except Exception as e:
        return f"Error: {str(e)}"


def batch_convert(medias: list[str], ext: str) -> str:
    try:
        medias = get_files_path(medias)
        if not medias:
            return "No provided medias"
        return files_convert(medias, ext)
    except Exception as e:
        return f"Error: {str(e)}"

def batch_concat(videos: list[str]) -> str:
    try:
        videos = get_files_path(videos)
        if not videos:
            return "No provided videos"
        return videos_concat(videos)
    except Exception as e:
        return f"Error: {str(e)}"

from back_end.files_manip import (
    files_audio_combine,
    files_audio_replace,
    files_compress_videos,
    files_convert,
    files_convert_video_to_video
)
from back_end.video_manip import videos_concat

from toolbox.paths import clean_file_list
from toolbox.wrapper import exception_as_str


@exception_as_str()
def batch_convert_video_to_video(videos: list, ext: str) -> str:
    videos = clean_file_list(videos)
    if not videos:
        return "No provided videos"
    return files_convert_video_to_video(videos, ext)


@exception_as_str()
def batch_modify_audio(videos: list, audios: list, opt: str = "replace", randomize: bool = True) -> str:
    videos = clean_file_list(videos)
    if not videos:
        return "No provided videos"
    audios = clean_file_list(audios)
    if not audios:
        return "No provided audios"
    if opt == "replace":
        return files_audio_replace(videos, audios, randomize)
    return files_audio_combine(videos, audios, randomize)


@exception_as_str()
def batch_compress(videos: list, bitrate, min_res, vcodec) -> str:
    videos = clean_file_list(videos)
    if not videos:
        return "No provided videos"
    return files_compress_videos(videos, bitrate, min_res, vcodec)


@exception_as_str()
def batch_convert(medias: list, ext: str) -> str:
    medias = clean_file_list(medias)
    if not medias:
        return "No provided medias"
    return files_convert(medias, ext)


@exception_as_str()
def batch_concat(videos: list) -> str:
    videos = clean_file_list(videos)
    if not videos:
        return "No provided videos"
    return videos_concat(videos)

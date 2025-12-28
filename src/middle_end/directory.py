from back_end.dir_manip import (
    dir_convert_media,
    dir_audio_replace,
    dir_audio_combine,
    dir_convert_video_to_video,
    dir_compress_videos
)
from toolbox.wrapper import exception_as_str
from pathlib import Path

@exception_as_str
def directory_media2media(video_dir_path: str, ext: str) -> str:
    video_dir_path = Path(video_dir_path)
    
    return dir_convert_media(video_dir_path, ext)

@exception_as_str
def directory_audio_modify(video_dir_path: str, audio_dir_path: str, opt: str = "replace", randomize: bool = True) -> str:
    video_dir_path = Path(video_dir_path)
    audio_dir_path = Path(audio_dir_path)

    if opt == "replace":
        return dir_audio_replace(video_dir_path, audio_dir_path, randomize)
    return dir_audio_combine(video_dir_path, audio_dir_path, randomize)

@exception_as_str
def directory_convert(dir_path: str, ext: str) -> str:
    dir_path = Path(dir_path)

    return dir_convert_video_to_video(dir_path, ext)

@exception_as_str
def directory_compress(dir_path: str, bitrate: int = 8000, min_res: str = "1080", vcodec="hevc_nvenc") -> str:
    dir_path = Path(dir_path)

    return dir_compress_videos(dir_path, bitrate, int(min_res), vcodec)
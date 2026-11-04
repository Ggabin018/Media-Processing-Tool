import gradio as gr

from back_end.dir_manip import (
    dir_convert_media,
    dir_audio_replace,
    dir_audio_combine,
    dir_convert_video_to_video,
    dir_compress_videos, compress_videos_dossier_parent
)
from middle_end.live import run_live
from toolbox.paths import require_dir
from toolbox.wrapper import exception_as_str


@exception_as_str()
def directory_media2media(video_dir_path: str, ext: str, progress=gr.Progress()):
    video_dir_path = require_dir(video_dir_path)
    yield from run_live(lambda: dir_convert_media(video_dir_path, ext), progress, "Fichiers")


@exception_as_str()
def directory_audio_modify(video_dir_path: str, audio_dir_path: str, opt: str = "replace", randomize: bool = True,
                           progress=gr.Progress()):
    video_dir_path = require_dir(video_dir_path)
    audio_dir_path = require_dir(audio_dir_path)
    fn = dir_audio_replace if opt == "replace" else dir_audio_combine
    yield from run_live(lambda: fn(video_dir_path, audio_dir_path, randomize), progress, "Vidéos")


@exception_as_str()
def directory_convert(dir_path: str, ext: str, progress=gr.Progress()):
    dir_path = require_dir(dir_path)
    yield from run_live(lambda: dir_convert_video_to_video(dir_path, ext), progress, "Vidéos")


@exception_as_str()
def directory_compress(dir_path: str, bitrate: int = 8000, min_res: str = "1080", vcodec="hevc_nvenc",
                       progress=gr.Progress()):
    dir_path = require_dir(dir_path)
    min_res = int(min_res)
    yield from run_live(lambda: dir_compress_videos(dir_path, bitrate, min_res, vcodec), progress, "Vidéos")


@exception_as_str()
def pdirectory_compress(dir_path: str, bitrate: int = 8000, min_res: str = "1080", vcodec="hevc_nvenc",
                        progress=gr.Progress()):
    dir_path = require_dir(dir_path)
    min_res = int(min_res)
    yield from run_live(lambda: compress_videos_dossier_parent(dir_path, bitrate, min_res, vcodec), progress,
                        "Vidéos")

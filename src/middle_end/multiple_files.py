import gradio as gr

from back_end.files_manip import (
    files_audio_combine,
    files_audio_replace,
    files_compress_videos,
    files_convert,
    files_convert_video_to_video
)
from back_end.video_manip import videos_concat
from middle_end.live import run_live
from toolbox.paths import clean_file_list
from toolbox.progress import run_task
from toolbox.wrapper import exception_as_str


@exception_as_str()
def batch_convert_video_to_video(videos: list, ext: str, progress=gr.Progress()):
    videos = clean_file_list(videos)
    if not videos:
        yield "No provided videos"
        return
    yield from run_live(lambda: files_convert_video_to_video(videos, ext), progress, "Vidéos")


@exception_as_str()
def batch_modify_audio(videos: list, audios: list, opt: str = "replace", randomize: bool = True,
                       progress=gr.Progress()):
    videos = clean_file_list(videos)
    if not videos:
        yield "No provided videos"
        return
    audios = clean_file_list(audios)
    if not audios:
        yield "No provided audios"
        return
    fn = files_audio_replace if opt == "replace" else files_audio_combine
    yield from run_live(lambda: fn(videos, audios, randomize), progress, "Vidéos")


@exception_as_str()
def batch_compress(videos: list, bitrate, min_res, vcodec, progress=gr.Progress()):
    videos = clean_file_list(videos)
    if not videos:
        yield "No provided videos"
        return
    yield from run_live(lambda: files_compress_videos(videos, bitrate, min_res, vcodec), progress, "Vidéos")


@exception_as_str()
def batch_convert(medias: list, ext: str, progress=gr.Progress()):
    medias = clean_file_list(medias)
    if not medias:
        yield "No provided medias"
        return
    yield from run_live(lambda: files_convert(medias, ext), progress, "Fichiers")


@exception_as_str()
def batch_concat(videos: list, progress=gr.Progress()):
    videos = clean_file_list(videos)
    if not videos:
        yield "No provided videos"
        return
    yield from run_live(lambda: run_task(f"{len(videos)} vidéos", videos_concat, videos), progress, "Vidéos")

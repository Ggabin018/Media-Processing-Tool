import gradio as gr

from toolbox.paths import require_file
from toolbox.progress import run_task, task_name
from toolbox.wrapper import exception_as_str
from back_end.video_manip import video_cut, video_compress, multiple_cuts_plus_concatenate
from back_end.audio_manip import audio_replace, audio_combine
from back_end.media_converter import convert_media
from middle_end.live import run_live


def _live(path: str, fn, *args, progress=None, **kwargs):
    """One file: live "name : NN%" in Result, then the output path."""
    return run_live(lambda: run_task(task_name(path), fn, *args, **kwargs), progress)


Segments = list[tuple[int, int | None]]  # from the TimeSegments component, in seconds; end None = until the end


@exception_as_str()
def cut_video(video_path: str, segments: Segments, progress=gr.Progress()):
    video_path = require_file(video_path)
    if not segments:
        raise ValueError("no segment")
    start, end = segments[0]
    yield from _live(video_path, video_cut, video_path, start=start, end=end, progress=progress)


@exception_as_str()
def convert_media_to_media(video_path: str, ext: str, progress=gr.Progress()):
    video_path = require_file(video_path)
    yield from _live(video_path, convert_media, video_path, ext, progress=progress)


@exception_as_str()
def modify_audio(video_path: str, audio_path: str, opt: str = "replace", progress=gr.Progress()):
    video_path = require_file(video_path)
    audio_path = require_file(audio_path)
    fn = audio_replace if opt == "replace" else audio_combine
    yield from _live(video_path, fn, video_path, audio_path, progress=progress)


@exception_as_str()
def compress_vid(video_path: str, bitrate: int = 8000, min_res: str = "1080", vcodec: str = "hevc_nvenc",
                 progress=gr.Progress()):
    video_path = require_file(video_path)
    min_res = int(min_res)
    yield from _live(video_path, video_compress, video_path, target_bitrate=bitrate, min_resolution=min_res,
                     vcodec=vcodec, progress=progress)


@exception_as_str()
def cut_and_concate(video_path: str, segments: Segments, progress=gr.Progress()):
    """Values are checked all at once by back_end.video_manip.validate_segments before any cut."""
    video_path = require_file(video_path)
    if not segments:
        raise ValueError("no segment")
    yield from _live(video_path, multiple_cuts_plus_concatenate, video_path, list(segments), progress=progress)

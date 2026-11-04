import gradio as gr

from toolbox.utils import to_seconds
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


@exception_as_str()
def cut_video(video_path: str, start: str | None, end: str | None, progress=gr.Progress()):
    video_path = require_file(video_path)
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


def parse_input(input_str: str | None) -> list[str]:
    """One time per line (seconds or HH:MM:SS). Empty lines are ignored."""
    lines = [line.strip() for line in (input_str or "").splitlines() if line.strip()]
    for line in lines:
        if to_seconds(line) is None:
            raise ValueError(f"invalid time {line!r}")
    return lines


@exception_as_str()
def cut_and_concate(video_path: str, input_start: str, input_end: str, progress=gr.Progress()):
    video_path = require_file(video_path)

    starts = parse_input(input_start)
    ends: list[str | None] = parse_input(input_end)

    if not starts:
        raise ValueError("no start time")

    # last segment can go to the end of the video
    if len(ends) + 1 == len(starts):
        ends.append(None)

    if len(starts) != len(ends):
        raise ValueError(f"starts={len(starts)} != ends={len(ends)}")

    yield from _live(video_path, multiple_cuts_plus_concatenate, video_path, list(zip(starts, ends)),
                     progress=progress)

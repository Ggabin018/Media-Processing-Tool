import os
import subprocess

import ffmpeg
import pytest

from conftest import TESTS_DIR, VIDEOS
from back_end.media_converter import convert_media
from back_end.video_manip import get_video_duration
from toolbox import ffmpeg_runner
from toolbox.exceptions import FfmpegError
from toolbox.ffmpeg_runner import parse_progress, run_ffmpeg, build_args
from toolbox.progress import ProgressBoard, current_board, run_task


def blocks(text: str):
    """Split a -progress output into its key=value blocks."""
    block = {}
    for line in text.splitlines():
        key, sep, value = line.strip().partition("=")
        if sep:
            block[key] = value
            if key == "progress":
                yield block
                block = {}


# --- parse_progress (pure) ---

@pytest.mark.parametrize("block, expected", [
    ({"out_time_us": "2500000", "out_time": "00:00:02.500000"}, 2.5),
    ({"out_time_ms": "1000000"}, 1.0),  # ffmpeg's out_time_ms is in microseconds too
    ({"out_time": "01:02:03.500000"}, 3723.5),
    ({"out_time_us": "N/A", "out_time": "N/A"}, None),
    ({"out_time_us": "-1500"}, 0.0),
    ({}, None),
])
def test_parse_progress(block, expected):
    assert parse_progress(block) == expected


def test_parse_real_output_with_na():
    # recorded from a real VP9 encode: "out_time=N/A" blocks crashed the old progress bar
    text = (TESTS_DIR / "data" / "progress_na.txt").read_text()
    parsed = [parse_progress(b) for b in blocks(text)]
    assert None in parsed
    known = [p for p in parsed if p is not None]
    assert known == sorted(known) and known[-1] > 0


def test_build_args_adds_progress_options(tmp_path):
    args = build_args(ffmpeg.output(ffmpeg.input("in.mp4"), str(tmp_path / "out.mp4")))
    assert args[0] == "ffmpeg"
    for opt in ("-nostats", "-progress", "pipe:1", "-hide_banner"):
        assert opt in args
    assert args.index("-progress") < args.index("-i")  # global options before the input


# --- real ffmpeg ---

@pytest.fixture
def broken_video(tmp_path) -> str:
    """Stream whose beginning is cut mid-GOP: the decoder logs 'non-existing PPS', 'no frame!'..."""
    full = tmp_path / "full.ts"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(VIDEOS / "1.mp4"), "-c", "copy", "-f", "mpegts",
                    str(full)], check=True)
    data = full.read_bytes()
    offset = (len(data) // 3) // 188 * 188  # keep whole TS packets
    broken = tmp_path / "broken.ts"
    broken.write_bytes(data[offset:])
    return str(broken)


def encode(src, out, **kwargs):
    return ffmpeg.output(ffmpeg.input(src), out, **kwargs).overwrite_output()


@pytest.mark.ffmpeg
def test_decoding_errors_are_ignored(broken_video, tmp_path):
    out = str(tmp_path / "out.mp4")
    board = ProgressBoard()
    token = current_board.set(board)
    try:
        result = run_task("broken.ts", run_ffmpeg, encode(broken_video, out, vcodec="libx264", preset="ultrafast"),
                          duration=7.0)
    finally:
        current_board.reset(token)

    assert result.decode_errors > 0
    assert os.path.isfile(out) and get_video_duration(out) > 5
    assert any("images illisibles ignorées" in n for n in board.notes())


@pytest.mark.ffmpeg
def test_failure_raises_with_stderr(tmp_video, tmp_path):
    with pytest.raises(FfmpegError) as err:
        run_ffmpeg(encode(tmp_video, str(tmp_path / "o.mp4"), vcodec="no_such_codec"), duration=10)
    assert err.value.returncode != 0
    assert any("encoder" in line.lower() for line in err.value.stderr_tail)


@pytest.mark.ffmpeg
def test_reports_increasing_fractions(tmp_video, tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(ffmpeg_runner, "report", seen.append)

    run_ffmpeg(encode(tmp_video, str(tmp_path / "o.mp4"), vcodec="libx264", preset="ultrafast"),
               duration=get_video_duration(tmp_video))

    assert seen and seen == sorted(seen)
    assert seen[-1] == 1.0 and all(0 <= f <= 1 for f in seen)


@pytest.mark.ffmpeg
def test_no_orphan_ffmpeg_when_python_fails(tmp_video, tmp_path, monkeypatch):
    started = []
    real_popen = subprocess.Popen

    def popen(*args, **kwargs):
        started.append(real_popen(*args, **kwargs))
        return started[-1]

    def boom(_fraction):
        raise RuntimeError("UI crashed")

    monkeypatch.setattr(ffmpeg_runner.subprocess, "Popen", popen)
    monkeypatch.setattr(ffmpeg_runner, "report", boom)

    with pytest.raises(RuntimeError, match="UI crashed"):
        run_ffmpeg(encode(tmp_video, str(tmp_path / "o.mp4"), vcodec="libx264", preset="veryslow"), duration=10)

    assert started and started[0].poll() is not None  # killed, not left running


@pytest.mark.ffmpeg
def test_convert_to_webm(tmp_path):
    # used to fail every time: VP9 reports out_time=N/A
    src = str(tmp_path / "short.mp4")  # 2 s extract: VP9 is slow
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(VIDEOS / "1.mp4"), "-t", "2", "-c", "copy", src],
                   check=True)
    out = convert_media(src, "webm")
    assert out == os.path.splitext(src)[0] + ".webm", out
    assert os.path.isfile(out)

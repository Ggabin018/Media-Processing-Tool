"""Back-end on real samples. Every output is written in tmp_path (inputs are copied there first)."""
import os
import shutil

import pytest

from conftest import VIDEOS, AUDIOS
from back_end.video_manip import is_video, video_cut, videos_concat, multiple_cuts_plus_concatenate, \
    video_compress, get_video_duration, get_resolution, validate_segments
from back_end.audio_manip import is_audio, get_audio_duration
from back_end.media_converter import convert_media


@pytest.mark.parametrize("name, expected", [
    ("a.mp4", True), ("a.mov", True), ("a.avi", True), ("a.webm", True), ("a.mkv", True),
    ("a.wav", False), ("a.mp3", False), ("a", False),
])
def test_is_video(name, expected):
    assert is_video(name) is expected


@pytest.mark.parametrize("name, expected", [
    ("a.mp3", True), ("a.wav", True), ("a.ogg", True), ("a.flac", True),
    ("a.mp4", False), ("a", False),
])
def test_is_audio(name, expected):
    assert is_audio(name) is expected


def test_not_a_video_returns_error_message():
    assert get_video_duration(str(AUDIOS / "sample1.wav")).startswith("Error")


@pytest.mark.ffmpeg
def test_get_audio_duration():
    assert get_audio_duration(str(AUDIOS / "sample1.wav")) == pytest.approx(18.4615, abs=1e-3)


@pytest.mark.ffmpeg
def test_video_cut(tmp_video):
    out = video_cut(tmp_video, "1", "3")

    assert out == os.path.splitext(tmp_video)[0] + "__cut.mp4"
    assert os.path.isfile(out)
    # stream copy: start snaps to a keyframe
    assert get_video_duration(out) == pytest.approx(2, abs=1)


@pytest.mark.ffmpeg
def test_video_cut_rejects_start_after_end(tmp_video):
    assert video_cut(tmp_video, "5", "2").startswith("Error")


@pytest.mark.ffmpeg
def test_videos_concat(tmp_video, tmp_video2):
    out = videos_concat([tmp_video, tmp_video2])

    assert os.path.isfile(out)
    expected = get_video_duration(tmp_video) + get_video_duration(tmp_video2)
    assert get_video_duration(out) == pytest.approx(expected, abs=0.5)


def test_videos_concat_needs_two_videos(tmp_path):
    assert videos_concat([str(tmp_path / "a.mp4")]).startswith("Error")


@pytest.mark.ffmpeg
def test_video_cut_explicit_output(tmp_video, tmp_path):
    target = str(tmp_path / "my cut.mp4")
    assert video_cut(tmp_video, "1", "3", output_video=target) == target
    assert os.path.isfile(target)
    assert not os.path.exists(os.path.splitext(tmp_video)[0] + "__cut.mp4")


@pytest.mark.ffmpeg
def test_videos_concat_explicit_output(tmp_video, tmp_video2, tmp_path):
    target = str(tmp_path / "joined.mp4")
    assert videos_concat([tmp_video, tmp_video2], output_video=target) == target
    assert os.path.isfile(target)


def base(path):
    return os.path.splitext(path)[0]


@pytest.mark.ffmpeg
def test_multiple_cuts_plus_concatenate(tmp_video):
    out = multiple_cuts_plus_concatenate(tmp_video, [("0", "2"), ("5", "7")])

    assert out == base(tmp_video) + "__concat.mp4"  # not <video>__cut__0__concat.mp4
    assert get_video_duration(out) == pytest.approx(4, abs=1.5)
    # segments are kept next to the video for later edits
    assert os.path.isfile(base(tmp_video) + "__cut__0.mp4")
    assert os.path.isfile(base(tmp_video) + "__cut__1.mp4")


@pytest.mark.ffmpeg
def test_cut_and_concat_single_segment(tmp_video):
    out = multiple_cuts_plus_concatenate(tmp_video, [("1", "3")])

    assert out == base(tmp_video) + "__concat.mp4"
    assert get_video_duration(out) == pytest.approx(2, abs=1)
    assert os.path.isfile(base(tmp_video) + "__cut__0.mp4")


@pytest.mark.ffmpeg
def test_cut_and_concat_keeps_existing_cut(tmp_video):
    # a result of the "Cut Video" tab must not be overwritten
    previous_cut = base(tmp_video) + "__cut.mp4"
    with open(previous_cut, "wb") as f:
        f.write(b"my previous cut")

    multiple_cuts_plus_concatenate(tmp_video, [("0", "2"), ("5", "7")])

    with open(previous_cut, "rb") as f:
        assert f.read() == b"my previous cut"


@pytest.mark.ffmpeg
def test_cut_and_concat_invalid_segments_create_nothing(tmp_video, tmp_path):
    before = set(os.listdir(tmp_path))

    out = multiple_cuts_plus_concatenate(tmp_video, [("0", "2"), ("7", "5"), ("l0", "12")])

    assert out.startswith("Error: invalid segments")
    assert "segment 2: start 00:00:07 >= end 00:00:05" in out
    assert "segment 3: invalid start 'l0'" in out  # every problem at once
    assert set(os.listdir(tmp_path)) == before  # nothing cut


# --- validate_segments (pure, no ffmpeg) ---

@pytest.mark.parametrize("times", [
    [("0", "2"), ("5", "7")],
    [("00:00:01", "00:00:03")],
    [("0", "2"), ("5", None)],  # last segment until the end
    [("5", "7"), ("0", "2")],  # reordering on purpose
    [("0", "5"), ("3", "8")],  # overlaps allowed
    [("0", "10")],  # end == rounded duration
])
def test_validate_segments_ok(times):
    assert validate_segments(times, duration=10.04) == []


@pytest.mark.parametrize("times, expected", [
    ([("abc", "2")], "segment 1: invalid start 'abc'"),
    ([("0", "1:2")], "segment 1: invalid end '1:2'"),
    ([("", "2")], "segment 1: missing start"),
    ([("4", "4")], "segment 1: start 00:00:04 >= end 00:00:04"),
    ([("0", "2"), ("12", None)], "segment 2: start 00:00:12 is after the end of the video (00:00:10)"),
    ([("0", "00:01:00")], "segment 1: end 00:01:00 is after the end of the video (00:00:10)"),
    ([("0", None), ("3", "5")], "segment 1: missing end (only the last segment can go to the end of the video)"),
])
def test_validate_segments_errors(times, expected):
    assert validate_segments(times, duration=10.04) == [expected]


def test_validate_segments_lists_every_problem():
    errors = validate_segments([("0", "2"), ("x", "3"), ("5", "4"), ("9", "99")], duration=10.04)
    assert errors == [
        "segment 2: invalid start 'x'",
        "segment 3: start 00:00:05 >= end 00:00:04",
        "segment 4: end 00:01:39 is after the end of the video (00:00:10)",
    ]


def test_validate_segments_without_duration():
    assert validate_segments([("0", "9999")], duration=None) == []


@pytest.mark.ffmpeg
def test_convert_video_to_mp3(tmp_video):
    out = convert_media(tmp_video, "mp3")

    assert out == os.path.splitext(tmp_video)[0] + ".mp3"
    assert os.path.isfile(out)
    assert get_audio_duration(out) == pytest.approx(get_video_duration(tmp_video), abs=0.5)


@pytest.mark.ffmpeg
def test_convert_audio_to_ogg(tmp_path):
    wav = str(shutil.copy(AUDIOS / "sample1.wav", tmp_path / "s.wav"))

    out = convert_media(wav, "ogg")

    assert os.path.isfile(out)
    assert get_audio_duration(out) == pytest.approx(18.46, abs=0.5)


@pytest.mark.gpu
def test_video_compress(tmp_video):
    out = video_compress(tmp_video, target_bitrate=2000, min_resolution=720, vcodec="hevc_nvenc")

    assert os.path.isfile(out), out
    assert get_resolution(out) == (1280, 720)

"""Back-end on real samples. Every output is written in tmp_path (inputs are copied there first)."""
import os
import shutil

import pytest

from conftest import VIDEOS, AUDIOS
from back_end.video_manip import is_video, video_cut, videos_concat, multiple_cuts_plus_concatenate, \
    video_compress, get_video_duration, get_resolution
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
def test_multiple_cuts_plus_concatenate(tmp_video):
    out = multiple_cuts_plus_concatenate(tmp_video, [("0", "2"), ("5", "7")])

    assert os.path.isfile(out), out
    assert get_video_duration(out) == pytest.approx(4, abs=1.5)


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

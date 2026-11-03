"""Former unittest test_video_modif.py, ported to pytest on the sample videos of the repo."""
import pytest

from conftest import VIDEOS
from back_end.video_manip import get_video_duration, get_resolution, get_video_bitrate, get_original_codecs, \
    is_video

V_PATH = str(VIDEOS / "1.mp4")  # values below measured with ffprobe


def test_file_exists():
    assert (VIDEOS / "1.mp4").exists()


@pytest.mark.ffmpeg
def test_get_video_duration():
    assert get_video_duration(V_PATH) == pytest.approx(10.0415, abs=1e-3)


@pytest.mark.ffmpeg
def test_get_resolution():
    assert get_resolution(V_PATH) == (1920, 1080)


@pytest.mark.ffmpeg
def test_get_video_bitrate():
    assert get_video_bitrate(V_PATH) == pytest.approx(9048.38, abs=0.01)


@pytest.mark.ffmpeg
def test_get_original_codecs():
    assert get_original_codecs(V_PATH) == ("h264", "aac")


def test_not_a_video():
    assert not is_video(str(VIDEOS / "not_a_video.wav"))

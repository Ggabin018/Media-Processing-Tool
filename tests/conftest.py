import shutil
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent
ROOT = TESTS_DIR.parent
VIDEOS = TESTS_DIR / "videos"
AUDIOS = TESTS_DIR / "audios"

HAS_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def pytest_collection_modifyitems(config, items):
    if HAS_FFMPEG:
        return
    skip = pytest.mark.skip(reason="ffmpeg/ffprobe not found on PATH")
    for item in items:
        if "ffmpeg" in item.keywords or "gpu" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def tmp_video(tmp_path) -> str:
    """Copy of a sample video in tmp_path (back-end writes outputs next to the input)."""
    return str(shutil.copy(VIDEOS / "1.mp4", tmp_path / "1.mp4"))


@pytest.fixture
def tmp_video2(tmp_path) -> str:
    return str(shutil.copy(VIDEOS / "2.mp4", tmp_path / "2.mp4"))

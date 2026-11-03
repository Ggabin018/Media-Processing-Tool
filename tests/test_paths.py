import os

import pytest

from toolbox.paths import clean_path, require_file, require_dir, clean_file_list

# Every way a path can arrive from the UI (typed, pasted from Explorer "Copy as path", ...)
VARIANTS = [
    lambda p: p,
    lambda p: f'"{p}"',
    lambda p: f"'{p}'",
    lambda p: f'  "{p}"  ',
    lambda p: f"{p}\n",
    lambda p: p.replace("\\", "/"),
    lambda p: p.replace("\\", "/").replace("/", "\\", 1),
]
VARIANT_IDS = ["plain", "double_quotes", "single_quotes", "quotes_and_spaces", "newline", "slashes", "mixed"]


@pytest.fixture
def video(tmp_path) -> str:
    f = tmp_path / "my video.mp4"
    f.write_bytes(b"")
    return str(f)


@pytest.mark.parametrize("variant", VARIANTS, ids=VARIANT_IDS)
def test_require_file_accepts_all_forms(video, variant):
    assert require_file(variant(video)) == os.path.normpath(video)


@pytest.mark.parametrize("variant", VARIANTS, ids=VARIANT_IDS)
def test_require_dir_accepts_all_forms(tmp_path, variant):
    assert require_dir(variant(str(tmp_path))) == os.path.normpath(str(tmp_path))


@pytest.mark.parametrize("raw", ["", "   ", '""', "''", ' " " ', None])
def test_empty_path_is_an_error(raw):
    # os.path.normpath("") == "." : an empty field must not mean "current directory"
    with pytest.raises(ValueError):
        clean_path(raw)


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        require_file(str(tmp_path / "nope.mp4"))


def test_dir_is_not_a_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        require_file(str(tmp_path))


def test_file_is_not_a_dir(video):
    with pytest.raises(NotADirectoryError):
        require_dir(video)


def test_clean_file_list(video, tmp_path):
    other = tmp_path / "b.mp4"
    other.write_bytes(b"")
    rows = [[f'"{video}"'], [""], ["   "], [None], [], [f"  {other}  "]]
    assert clean_file_list(rows) == [os.path.normpath(video), os.path.normpath(str(other))]


def test_clean_file_list_accepts_flat_strings(video):
    assert clean_file_list([video]) == [os.path.normpath(video)]


@pytest.mark.parametrize("rows", [None, [], [[""]]])
def test_clean_file_list_empty(rows):
    assert clean_file_list(rows) == []


def test_clean_file_list_reports_missing(video, tmp_path):
    missing = str(tmp_path / "missing.mp4")
    with pytest.raises(FileNotFoundError, match="missing.mp4"):
        clean_file_list([[video], [missing]])

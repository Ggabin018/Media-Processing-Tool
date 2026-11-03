"""
The middle_end is the guard between Gradio and the back-end:
- it cleans every path (quotes, spaces, slashes) before the back-end sees it,
- it never raises: errors come back as "Error: ..." with as many values as Gradio outputs.
Back-end functions are mocked: no ffmpeg needed.
"""
import os
from dataclasses import dataclass
from typing import Callable

import pytest

from middle_end import single_file, directory, multiple_files


@dataclass
class Entry:
    module: object
    func: str
    backend: str  # back-end function mocked in the module namespace
    make_args: Callable  # (raw_path_fn, files) -> args
    n_outputs: int  # number of Gradio outputs

    def __str__(self):
        return self.func


def rows(*paths):
    return [[p] for p in paths]


ENTRIES = [
    # Single file
    Entry(single_file, "cut_video", "video_cut", lambda r, f: (r(f["video"]), "1", "3"), 2),
    Entry(single_file, "convert_media_to_media", "convert_media", lambda r, f: (r(f["video"]), "mp3"), 3),
    Entry(single_file, "modify_audio", "audio_replace", lambda r, f: (r(f["video"]), r(f["audio"]), "replace"), 2),
    Entry(single_file, "modify_audio", "audio_combine", lambda r, f: (r(f["video"]), r(f["audio"]), "combine"), 2),
    Entry(single_file, "compress_vid", "video_compress", lambda r, f: (r(f["video"]), "8000", "1080", "libx264"), 1),
    Entry(single_file, "cut_and_concate", "multiple_cuts_plus_concatenate",
          lambda r, f: (r(f["video"]), "0\n4", "2\n6"), 2),
    # Directory
    Entry(directory, "directory_media2media", "dir_convert_media", lambda r, f: (r(f["vdir"]), "mp3"), 1),
    Entry(directory, "directory_audio_modify", "dir_audio_replace",
          lambda r, f: (r(f["vdir"]), r(f["adir"]), "replace", False), 1),
    Entry(directory, "directory_audio_modify", "dir_audio_combine",
          lambda r, f: (r(f["vdir"]), r(f["adir"]), "combine", False), 1),
    Entry(directory, "directory_convert", "dir_convert_video_to_video", lambda r, f: (r(f["vdir"]), "mp4"), 1),
    Entry(directory, "directory_compress", "dir_compress_videos",
          lambda r, f: (r(f["vdir"]), "8000", "1080", "libx264"), 1),
    Entry(directory, "pdirectory_compress", "compress_videos_dossier_parent",
          lambda r, f: (r(f["vdir"]), "8000", "1080", "libx264"), 0),
    # Multiple files
    Entry(multiple_files, "batch_convert_video_to_video", "files_convert_video_to_video",
          lambda r, f: (rows(r(f["video"]), r(f["video2"])), "mkv"), 1),
    Entry(multiple_files, "batch_modify_audio", "files_audio_replace",
          lambda r, f: (rows(r(f["video"])), rows(r(f["audio"])), "replace", False), 1),
    Entry(multiple_files, "batch_modify_audio", "files_audio_combine",
          lambda r, f: (rows(r(f["video"])), rows(r(f["audio"])), "combine", False), 1),
    Entry(multiple_files, "batch_compress", "files_compress_videos",
          lambda r, f: (rows(r(f["video"])), "8000", "1080", "libx264"), 1),
    Entry(multiple_files, "batch_convert", "files_convert", lambda r, f: (rows(r(f["video"])), "mp3"), 1),
    Entry(multiple_files, "batch_concat", "videos_concat", lambda r, f: (rows(r(f["video"]), r(f["video2"])),), 1),
]
IDS = [f"{e.func}->{e.backend}" for e in ENTRIES]


@pytest.fixture
def files(tmp_path) -> dict[str, str]:
    """Fake media files (names with spaces on purpose). Content does not matter: back-end is mocked."""
    vdir = tmp_path / "my videos"
    adir = tmp_path / "my audios"
    vdir.mkdir()
    adir.mkdir()
    for p in (vdir / "a b.mp4", vdir / "c.mp4", adir / "s 1.wav"):
        p.write_bytes(b"")
    return {
        "video": str(vdir / "a b.mp4"),
        "video2": str(vdir / "c.mp4"),
        "audio": str(adir / "s 1.wav"),
        "vdir": str(vdir),
        "adir": str(adir),
    }


@pytest.fixture(autouse=True)
def no_preview(monkeypatch):
    # make_temp_copy would call ffmpeg to build the preview
    monkeypatch.setattr(single_file, "make_temp_copy", lambda path: None)


def install_fake(monkeypatch, entry, raises=None):
    calls = []

    def fake(*args, **kwargs):
        calls.append((args, kwargs))
        if raises:
            raise raises
        return "OK"

    monkeypatch.setattr(entry.module, entry.backend, fake)
    return calls


def call(entry, *args):
    return getattr(entry.module, entry.func)(*args)


def all_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from all_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from all_strings(v)


def assert_error_shape(entry, result, capsys=None):
    """Error returned (not raised) with exactly as many values as Gradio outputs."""
    if entry.n_outputs == 0:
        assert result is None
        assert "Error:" in capsys.readouterr().out
    elif entry.n_outputs == 1:
        assert isinstance(result, str) and result.startswith("Error:"), result
    else:
        assert isinstance(result, tuple) and len(result) == entry.n_outputs, result
        assert result[0].startswith("Error:"), result
        assert all(v is None for v in result[1:])


QUOTED_FORMS = {
    "double_quotes": lambda p: f'"{p}"',
    "quotes_and_spaces": lambda p: f'  "{p}" ',
    "single_quotes": lambda p: f"'{p}'",
    "forward_slashes": lambda p: p.replace("\\", "/"),
}


@pytest.mark.parametrize("form", QUOTED_FORMS.values(), ids=QUOTED_FORMS.keys())
@pytest.mark.parametrize("entry", ENTRIES, ids=IDS)
def test_backend_receives_clean_paths(entry, form, files, monkeypatch):
    calls = install_fake(monkeypatch, entry)
    used = []

    def raw(p):
        used.append(p)
        return form(p)

    call(entry, *entry.make_args(raw, files))

    assert len(calls) == 1, f"{entry.backend} was not called"
    received = set(all_strings(calls[0]))
    for p in used:
        assert os.path.normpath(p) in received, f"{entry.backend} did not get the clean path of {p!r}: {received}"
    assert not any(c in s for s in received for c in "\"'"), f"quotes reached the back-end: {received}"


@pytest.mark.parametrize("entry", ENTRIES, ids=IDS)
def test_missing_path_returns_error(entry, files, monkeypatch, capsys):
    calls = install_fake(monkeypatch, entry)
    missing = {k: v + "_missing" for k, v in files.items()}

    result = call(entry, *entry.make_args(lambda p: p, missing))

    assert calls == []
    assert_error_shape(entry, result, capsys)


@pytest.mark.parametrize("entry", [e for e in ENTRIES if e.module is not multiple_files],
                         ids=[i for e, i in zip(ENTRIES, IDS) if e.module is not multiple_files])
def test_empty_path_returns_error(entry, files, monkeypatch, capsys):
    calls = install_fake(monkeypatch, entry)

    result = call(entry, *entry.make_args(lambda p: "", files))

    assert calls == []  # an empty field must not become "." (current directory)
    assert_error_shape(entry, result, capsys)


@pytest.mark.parametrize("entry", [e for e in ENTRIES if e.module is multiple_files],
                         ids=[i for e, i in zip(ENTRIES, IDS) if e.module is multiple_files])
def test_multiple_files_empty_list(entry, files, monkeypatch):
    calls = install_fake(monkeypatch, entry)

    result = call(entry, *entry.make_args(lambda p: "", files))

    assert calls == []
    assert isinstance(result, str) and result.startswith("No provided")


@pytest.mark.parametrize("entry", ENTRIES, ids=IDS)
def test_backend_exception_becomes_error(entry, files, monkeypatch, capsys):
    install_fake(monkeypatch, entry, raises=RuntimeError("boom"))

    result = call(entry, *entry.make_args(lambda p: p, files))

    assert_error_shape(entry, result, capsys)
    if entry.n_outputs:
        msg = result if entry.n_outputs == 1 else result[0]
        assert msg == "Error: boom"


# --- cut_and_concate: parsing of the start/end text boxes ---

@pytest.fixture
def fake_cuts(monkeypatch):
    calls = []
    monkeypatch.setattr(single_file, "multiple_cuts_plus_concatenate",
                        lambda path, times: calls.append(times) or "OK")
    return calls


def test_cut_and_concate_pairs_times(files, fake_cuts):
    assert single_file.cut_and_concate(files["video"], "0\n00:00:04\n", "2\n6") == ("OK", None)
    assert fake_cuts == [[("0", "2"), ("00:00:04", "6")]]


def test_cut_and_concate_last_segment_to_end(files, fake_cuts):
    single_file.cut_and_concate(files["video"], "0\n4", "2")
    assert fake_cuts == [[("0", "2"), ("4", None)]]


@pytest.mark.parametrize("starts, ends, expected", [
    ("0\n4\n8", "2", "starts=3 != ends=1"),
    ("0", "2\n4\n6", "starts=1 != ends=3"),
    ("abc", "2", "invalid time 'abc'"),
    ("0", "1:2", "invalid time '1:2'"),
    ("", "", "no start time"),
])
def test_cut_and_concate_bad_times(files, fake_cuts, starts, ends, expected):
    result = single_file.cut_and_concate(files["video"], starts, ends)
    assert result == (f"Error: {expected}", None)  # exactly one "Error:" prefix
    assert fake_cuts == []

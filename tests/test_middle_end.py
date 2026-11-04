"""
The middle_end is the guard between Gradio and the back-end:
- it cleans every path (quotes, spaces, slashes) before the back-end sees it,
- it never raises: errors come back as "Error: ..." in the Result field,
- its handlers are generators: live progress board, then the result (last value).
Back-end functions are mocked: no ffmpeg needed.
"""
import inspect
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


def rows(*paths):
    return [[p] for p in paths]


ENTRIES = [
    # Single file
    Entry(single_file, "cut_video", "video_cut", lambda r, f: (r(f["video"]), "1", "3")),
    Entry(single_file, "convert_media_to_media", "convert_media", lambda r, f: (r(f["video"]), "mp3")),
    Entry(single_file, "modify_audio", "audio_replace", lambda r, f: (r(f["video"]), r(f["audio"]), "replace")),
    Entry(single_file, "modify_audio", "audio_combine", lambda r, f: (r(f["video"]), r(f["audio"]), "combine")),
    Entry(single_file, "compress_vid", "video_compress", lambda r, f: (r(f["video"]), "8000", "1080", "libx264")),
    Entry(single_file, "cut_and_concate", "multiple_cuts_plus_concatenate",
          lambda r, f: (r(f["video"]), "0\n4", "2\n6")),
    # Directory
    Entry(directory, "directory_media2media", "dir_convert_media", lambda r, f: (r(f["vdir"]), "mp3")),
    Entry(directory, "directory_audio_modify", "dir_audio_replace",
          lambda r, f: (r(f["vdir"]), r(f["adir"]), "replace", False)),
    Entry(directory, "directory_audio_modify", "dir_audio_combine",
          lambda r, f: (r(f["vdir"]), r(f["adir"]), "combine", False)),
    Entry(directory, "directory_convert", "dir_convert_video_to_video", lambda r, f: (r(f["vdir"]), "mp4")),
    Entry(directory, "directory_compress", "dir_compress_videos",
          lambda r, f: (r(f["vdir"]), "8000", "1080", "libx264")),
    Entry(directory, "pdirectory_compress", "compress_videos_dossier_parent",
          lambda r, f: (r(f["vdir"]), "8000", "1080", "libx264")),
    # Multiple files
    Entry(multiple_files, "batch_convert_video_to_video", "files_convert_video_to_video",
          lambda r, f: (rows(r(f["video"]), r(f["video2"])), "mkv")),
    Entry(multiple_files, "batch_modify_audio", "files_audio_replace",
          lambda r, f: (rows(r(f["video"])), rows(r(f["audio"])), "replace", False)),
    Entry(multiple_files, "batch_modify_audio", "files_audio_combine",
          lambda r, f: (rows(r(f["video"])), rows(r(f["audio"])), "combine", False)),
    Entry(multiple_files, "batch_compress", "files_compress_videos",
          lambda r, f: (rows(r(f["video"])), "8000", "1080", "libx264")),
    Entry(multiple_files, "batch_convert", "files_convert", lambda r, f: (rows(r(f["video"])), "mp3")),
    Entry(multiple_files, "batch_concat", "videos_concat", lambda r, f: (rows(r(f["video"]), r(f["video2"])),)),
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


def install_fake(monkeypatch, entry, raises=None, returns="OK"):
    calls = []

    def fake(*args, **kwargs):
        calls.append((args, kwargs))
        if raises:
            raise raises
        return returns

    monkeypatch.setattr(entry.module, entry.backend, fake)
    return calls


def call(entry, *args):
    """Run a handler like Gradio does and return its last value (the final Result)."""
    gen = getattr(entry.module, entry.func)(*args, progress=None)
    assert inspect.isgenerator(gen)
    values = list(gen)
    assert values, "handler yielded nothing"
    return values[-1]


def all_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from all_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from all_strings(v)


@pytest.mark.parametrize("entry", ENTRIES, ids=IDS)
def test_handlers_are_generators(entry):
    assert inspect.isgeneratorfunction(inspect.unwrap(getattr(entry.module, entry.func)))


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

    assert call(entry, *entry.make_args(raw, files)) == "OK"

    assert len(calls) == 1, f"{entry.backend} was not called"
    received = set(all_strings(calls[0]))
    for p in used:
        assert os.path.normpath(p) in received, f"{entry.backend} did not get the clean path of {p!r}: {received}"
    assert not any(c in s for s in received for c in "\"'"), f"quotes reached the back-end: {received}"


@pytest.mark.parametrize("entry", ENTRIES, ids=IDS)
def test_missing_path_returns_error(entry, files, monkeypatch):
    calls = install_fake(monkeypatch, entry)
    missing = {k: v + "_missing" for k, v in files.items()}

    result = call(entry, *entry.make_args(lambda p: p, missing))

    assert calls == []
    assert isinstance(result, str) and result.startswith("Error:"), result


@pytest.mark.parametrize("entry", [e for e in ENTRIES if e.module is not multiple_files],
                         ids=[i for e, i in zip(ENTRIES, IDS) if e.module is not multiple_files])
def test_empty_path_returns_error(entry, files, monkeypatch):
    calls = install_fake(monkeypatch, entry)

    result = call(entry, *entry.make_args(lambda p: "", files))

    assert calls == []  # an empty field must not become "." (current directory)
    assert result == "Error: Empty path"


@pytest.mark.parametrize("entry", [e for e in ENTRIES if e.module is multiple_files],
                         ids=[i for e, i in zip(ENTRIES, IDS) if e.module is multiple_files])
def test_multiple_files_empty_list(entry, files, monkeypatch):
    calls = install_fake(monkeypatch, entry)

    result = call(entry, *entry.make_args(lambda p: "", files))

    assert calls == []
    assert result.startswith("No provided")


@pytest.mark.parametrize("entry", ENTRIES, ids=IDS)
def test_backend_exception_becomes_error(entry, files, monkeypatch):
    install_fake(monkeypatch, entry, raises=RuntimeError("boom"))

    result = call(entry, *entry.make_args(lambda p: p, files))

    assert result.startswith("Error:") and result.endswith("boom"), result


@pytest.mark.parametrize("entry", [e for e in ENTRIES if e.module is single_file],
                         ids=[i for e, i in zip(ENTRIES, IDS) if e.module is single_file])
def test_single_result_is_output_path(entry, files, monkeypatch, tmp_path):
    out = tmp_path / "out.mp4"
    out.write_bytes(b"")
    install_fake(monkeypatch, entry, returns=str(out))

    assert call(entry, *entry.make_args(lambda p: p, files)) == str(out)


def test_progress_is_reported_to_gradio(files, monkeypatch):
    import time
    from toolbox.progress import report

    def slow_compress(*args, **kwargs):
        for i in range(1, 5):
            report(i / 4)
            time.sleep(0.3)  # > one poll (0.5 s) in total: intermediate states are shown
        return "OK"

    monkeypatch.setattr(single_file, "video_compress", slow_compress)
    seen = []
    values = list(single_file.compress_vid(files["video"], "8000", "1080", "libx264",
                                           progress=lambda fraction, desc=None: seen.append(fraction)))

    assert values[-1] == "OK"
    assert any(v.startswith("a b.mp4 : ") and v.endswith("%") for v in values[:-1]), values
    assert seen and seen == sorted(seen) and 0 < seen[-1] <= 1


# --- cut_and_concate: parsing of the start/end text boxes ---

@pytest.fixture
def fake_cuts(monkeypatch):
    calls = []
    monkeypatch.setattr(single_file, "multiple_cuts_plus_concatenate",
                        lambda path, times: calls.append(times) or "OK")
    return calls


def run_cc(*args):
    return list(single_file.cut_and_concate(*args, progress=None))[-1]


def test_cut_and_concate_pairs_times(files, fake_cuts):
    assert run_cc(files["video"], "0\n00:00:04\n", "2\n6") == "OK"
    assert fake_cuts == [[("0", "2"), ("00:00:04", "6")]]


def test_cut_and_concate_last_segment_to_end(files, fake_cuts):
    run_cc(files["video"], "0\n4", "2")
    assert fake_cuts == [[("0", "2"), ("4", None)]]


@pytest.mark.parametrize("starts, ends, expected", [
    ("0\n4\n8", "2", "starts=3 != ends=1"),
    ("0", "2\n4\n6", "starts=1 != ends=3"),
    ("abc", "2", "invalid time 'abc'"),
    ("0", "1:2", "invalid time '1:2'"),
    ("", "", "no start time"),
])
def test_cut_and_concate_bad_times(files, fake_cuts, starts, ends, expected):
    assert run_cc(files["video"], starts, ends) == f"Error: {expected}"  # exactly one "Error:" prefix
    assert fake_cuts == []

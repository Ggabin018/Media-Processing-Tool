import os

import pytest

from toolbox import os_open


@pytest.fixture
def calls(monkeypatch):
    recorded = []
    monkeypatch.setattr(os_open.subprocess, "Popen", lambda args: recorded.append(("popen", args)))
    monkeypatch.setattr(os_open.os, "startfile", lambda p: recorded.append(("startfile", p)), raising=False)
    return recorded


@pytest.fixture
def video(tmp_path):
    f = tmp_path / "v.mp4"
    f.write_bytes(b"")
    return str(f)


@pytest.mark.parametrize("platform, expected", [
    ("win32", ("startfile", "{f}")),
    ("darwin", ("popen", ["open", "{f}"])),
    ("linux", ("popen", ["xdg-open", "{f}"])),
])
def test_open_file(monkeypatch, calls, video, platform, expected):
    monkeypatch.setattr(os_open.sys, "platform", platform)
    os_open.open_file(video)
    kind, arg = expected
    arg = arg.format(f=video) if isinstance(arg, str) else [a.format(f=video) for a in arg]
    assert calls == [(kind, arg)]


@pytest.mark.parametrize("platform, expected", [
    ("win32", ["explorer", "/select,{f}"]),
    ("darwin", ["open", "-R", "{f}"]),
    ("linux", ["xdg-open", "{d}"]),
])
def test_reveal_file(monkeypatch, calls, video, platform, expected):
    monkeypatch.setattr(os_open.sys, "platform", platform)
    os_open.reveal_in_folder(video)
    assert calls == [("popen", [a.format(f=video, d=os.path.dirname(video)) for a in expected])]


@pytest.mark.parametrize("platform, expected", [
    ("win32", ["explorer", "{d}"]),
    ("darwin", ["open", "{d}"]),
    ("linux", ["xdg-open", "{d}"]),
])
def test_reveal_directory(monkeypatch, calls, tmp_path, platform, expected):
    monkeypatch.setattr(os_open.sys, "platform", platform)
    os_open.reveal_in_folder(str(tmp_path))
    assert calls == [("popen", [a.format(d=str(tmp_path)) for a in expected])]


def test_missing_path(calls, tmp_path):
    with pytest.raises(FileNotFoundError):
        os_open.open_file(str(tmp_path / "nope.mp4"))
    with pytest.raises(FileNotFoundError):
        os_open.reveal_in_folder(str(tmp_path / "nope"))
    with pytest.raises(FileNotFoundError):
        os_open.open_file(str(tmp_path))  # a directory is not a file to play
    assert calls == []

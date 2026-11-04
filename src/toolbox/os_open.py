"""Open a file with its default application, or show it in the file explorer (on the machine running the app)."""
import os
import subprocess
import sys


def open_file(path: str) -> None:
    """Open a file with the default application (video player...)."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"{path} does not exist")
    if sys.platform.startswith("win"):
        os.startfile(path)  # noqa: S606 - local desktop app
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def reveal_in_folder(path: str) -> None:
    """Open the file explorer on a directory, or on the directory of a file (with the file selected when possible)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist")
    is_file = os.path.isfile(path)
    if sys.platform.startswith("win"):
        subprocess.Popen(["explorer", f"/select,{path}"] if is_file else ["explorer", path])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-R", path] if is_file else ["open", path])
    else:
        subprocess.Popen(["xdg-open", os.path.dirname(path) if is_file else path])

"""
Running without a console (pythonw.exe, launched by webui.vbs).

- sys.stdout / sys.stderr are None without a console: print / tqdm / logging would crash,
  they are redirected to a log file,
- on Windows, every child process (ffmpeg, ffprobe...) would open its own console window:
  CREATE_NO_WINDOW is added by default to subprocess.Popen (also used by subprocess.run,
  ffmpeg-python, pydub...).
"""
import functools
import logging
import os
import subprocess
import sys

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


def redirect_missing_stdio(log_path: str) -> bool:
    """Send stdout / stderr to `log_path` if there is no console. Returns True if redirected."""
    if sys.stdout is not None and sys.stderr is not None:
        return False
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    log = open(log_path, "a", encoding="utf-8", errors="replace", buffering=1)
    if sys.stdout is None:
        sys.stdout = log
    if sys.stderr is None:
        sys.stderr = log
    logging.basicConfig(stream=log, level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return True


def hide_child_consoles(platform: str = sys.platform) -> bool:
    """Add CREATE_NO_WINDOW to every subprocess.Popen without creationflags (Windows only)."""
    if platform != "win32" or getattr(subprocess.Popen.__init__, "_no_window", False):
        return False
    original = subprocess.Popen.__init__

    @functools.wraps(original)
    def __init__(self, *args, **kwargs):
        if not kwargs.get("creationflags"):
            kwargs["creationflags"] = CREATE_NO_WINDOW
        original(self, *args, **kwargs)

    __init__._no_window = True
    subprocess.Popen.__init__ = __init__
    return True

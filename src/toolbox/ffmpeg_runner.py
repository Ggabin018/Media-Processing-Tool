"""
The only place where ffmpeg is executed.

- progress read from `-progress pipe:1` (robust to "N/A"), shown with tqdm in the console
  and reported to the current ProgressBoard (UI),
- stderr drained in a thread (decoding errors can be numerous: an unread pipe would block ffmpeg),
- success decided on the return code only: decoding errors such as
  "non-existing PPS 0 referenced" are harmless and only counted,
- ffmpeg is always killed if Python stops reading (no orphan process).
"""
import re
import subprocess
import threading
from collections import deque
from dataclasses import dataclass

import ffmpeg
from tqdm import tqdm

from toolbox.exceptions import FfmpegError
from toolbox.progress import report, add_note

GLOBAL_ARGS = ["-hide_banner", "-nostats", "-loglevel", "error", "-progress", "pipe:1"]

_DECODER_LINE = re.compile(r"^\[[\w:/.-]+ @ (0x)?[0-9a-fA-F]+\]")
_REPEATED = re.compile(r"Last message repeated (\d+) times?")


@dataclass
class FfmpegResult:
    decode_errors: int = 0


def parse_progress(block: dict[str, str]) -> float | None:
    """
    Seconds already encoded, from one `-progress` block (key=value lines up to "progress=...").
    None when unknown: ffmpeg writes "N/A" until the first frame is out.
    """
    for key in ("out_time_us", "out_time_ms"):  # both are microseconds (historical ffmpeg naming)
        value = block.get(key, "").strip()
        if value.lstrip("-").isdigit():
            return max(0.0, int(value) / 1_000_000)
    value = block.get("out_time", "").strip()
    try:
        h, m, s = value.split(":")
        return max(0.0, int(h) * 3600 + int(m) * 60 + float(s))
    except ValueError:
        return None


def build_args(stream) -> list[str]:
    args = ffmpeg.compile(stream)
    return [args[0], *GLOBAL_ARGS, *args[1:]]


# console: one tqdm line per running ffmpeg
_slots_lock = threading.Lock()
_used_slots: set[int] = set()


def _take_slot() -> int:
    with _slots_lock:
        slot = 0
        while slot in _used_slots:
            slot += 1
        _used_slots.add(slot)
        return slot


def _release_slot(slot: int) -> None:
    with _slots_lock:
        _used_slots.discard(slot)


def run_ffmpeg(stream, duration: float | None = None, desc: str = "ffmpeg") -> FfmpegResult:
    """
    Run an ffmpeg-python stream and wait for the end.
    :param duration: expected output duration in seconds (for the percentage), None if unknown
    :raise FfmpegError: if ffmpeg fails
    """
    args = build_args(stream)
    process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    tail: deque[str] = deque(maxlen=50)
    decode_errors = 0

    def drain_stderr():
        nonlocal decode_errors
        for raw in process.stderr:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            tail.append(line)
            if _DECODER_LINE.match(line):
                decode_errors += 1
            elif m := _REPEATED.search(line):
                decode_errors += int(m.group(1))

    stderr_thread = threading.Thread(target=drain_stderr, daemon=True)
    stderr_thread.start()

    total = round(duration, 2) if duration and duration > 0 else None
    slot = _take_slot()
    bar = tqdm(total=total, desc=desc, unit="s", leave=False, position=slot, dynamic_ncols=True,
               bar_format="{desc}: {percentage:3.0f}%|{bar}| {n:.0f}/{total:.0f}s [{elapsed}<{remaining}]"
               if total else "{desc}: {n:.0f}s [{elapsed}]")
    try:
        block: dict[str, str] = {}
        for raw in process.stdout:
            line = raw.decode("utf-8", errors="replace").strip()
            key, sep, value = line.partition("=")
            if not sep:
                continue
            block[key] = value
            if key != "progress":
                continue

            seconds = parse_progress(block)
            block = {}
            if value == "end":
                seconds = total if total else seconds
            if seconds is None:
                continue
            if total:
                seconds = min(seconds, total)
                if seconds > bar.n:
                    bar.update(seconds - bar.n)
                report(seconds / total)
            else:
                bar.update(max(0.0, seconds - bar.n))
        process.wait()
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        stderr_thread.join(timeout=5)
        bar.close()
        _release_slot(slot)

    if process.returncode != 0:
        raise FfmpegError(process.returncode, list(tail))

    report(1.0)
    if decode_errors:
        add_note(f"{decode_errors} images illisibles ignorées")
    return FfmpegResult(decode_errors=decode_errors)

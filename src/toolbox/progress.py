"""
Live progress of the current processing, shown in the UI.

A ProgressBoard holds the state of every file of a processing (single file, directory or list).
It travels through ContextVars, so the back-end does not need an extra parameter:
- middle_end sets `current_board` for the whole processing,
- each task (one file) sets `current_task`,
- run_ffmpeg calls `report(fraction)` / `add_note(text)`, which update the right line.
"""
import os
import threading
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Callable

PENDING, RUNNING, DONE, ERROR = "pending", "running", "done", "error"


@dataclass
class _Task:
    state: str = PENDING
    fraction: float = 0.0
    message: str = ""
    notes: list[str] = field(default_factory=list)


class ProgressBoard:
    """Thread-safe state of a processing: one line per file."""

    def __init__(self, label: str = "Fichiers"):
        self.label = label
        self._tasks: dict[str, _Task] = {}
        self._lock = threading.Lock()

    def add(self, names: list[str]) -> list[str]:
        """Register files (pending). Returns their unique keys (duplicated names get ' (2)', ' (3)'...)."""
        keys = []
        with self._lock:
            for name in names:
                key, n = name, 2
                while key in self._tasks:
                    key = f"{name} ({n})"
                    n += 1
                self._tasks[key] = _Task()
                keys.append(key)
        return keys

    def start(self, key: str) -> None:
        with self._lock:
            self._tasks[key].state = RUNNING

    def update(self, key: str, fraction: float) -> None:
        with self._lock:
            task = self._tasks[key]
            task.fraction = min(1.0, max(task.fraction, fraction))  # never goes back

    def note(self, key: str, text: str) -> None:
        with self._lock:
            self._tasks[key].notes.append(text)

    def finish(self, key: str, ok: bool, message: str = "") -> None:
        with self._lock:
            task = self._tasks[key]
            task.state = DONE if ok else ERROR
            task.fraction = 1.0
            task.message = message

    def overall(self) -> float:
        with self._lock:
            if not self._tasks:
                return 0.0
            return sum(t.fraction if t.state == RUNNING else 1.0 if t.state in (DONE, ERROR) else 0.0
                       for t in self._tasks.values()) / len(self._tasks)

    def summary(self) -> str:
        with self._lock:
            return self._summary()

    def _summary(self) -> str:
        total = len(self._tasks)
        finished = sum(t.state in (DONE, ERROR) for t in self._tasks.values())
        errors = sum(t.state == ERROR for t in self._tasks.values())
        text = f"{self.label} {finished}/{total} traités"
        if errors:
            text += f", {errors} en erreur"
        return text

    def notes(self) -> list[str]:
        """'name: note' for every note, in registration order."""
        with self._lock:
            return [f"{k} : {n}" for k, t in self._tasks.items() for n in t.notes]

    def render(self) -> str:
        """
        B.mp4 : 50%
        C.mp4 : 20%
        D.mp4 : ✖ <message>
        2 en attente
        Vidéos 1/4 traités
        """
        with self._lock:
            lines = [f"{k} : {int(t.fraction * 100)}%" for k, t in self._tasks.items() if t.state == RUNNING]
            lines += [f"{k} : ✖ {t.message}".rstrip() for k, t in self._tasks.items() if t.state == ERROR]
            pending = sum(t.state == PENDING for t in self._tasks.values())
            if pending:
                lines.append(f"{pending} en attente")
            if len(self._tasks) > 1 or not lines:
                lines.append(self._summary())
            return "\n".join(lines)


current_board: ContextVar[ProgressBoard | None] = ContextVar("current_board", default=None)
current_task: ContextVar[str | None] = ContextVar("current_task", default=None)


def report(fraction: float) -> None:
    """Progress (0..1) of the current task. No-op outside of a processing."""
    board, key = current_board.get(), current_task.get()
    if board is not None and key is not None:
        board.update(key, fraction)


def add_note(text: str) -> None:
    """Remark on the current task (e.g. ignored decoding errors). No-op outside of a processing."""
    board, key = current_board.get(), current_task.get()
    if board is not None and key is not None:
        board.note(key, text)


def first_line(result) -> str:
    return result.strip().splitlines()[0].strip() if isinstance(result, str) and result.strip() else ""


def is_success(result) -> bool:
    """Back-end functions return the output path on success, a message otherwise."""
    return os.path.isfile(first_line(result))


def run_task(name: str, fn: Callable, *args, **kwargs):
    """
    Run one task (one file) on the current board: pending -> running -> done/error.
    Exceptions are turned into "Error: ..." strings. Works without a board too.
    """
    board_token = current_board.set(ProgressBoard()) if current_board.get() is None else None
    try:
        key = current_board.get().add([name])[0]
        return run_registered(key, fn, *args, **kwargs)
    finally:
        if board_token is not None:
            current_board.reset(board_token)


def run_registered(key: str, fn: Callable, *args, **kwargs):
    """Same as run_task, for a task already added to the current board."""
    board = current_board.get()
    token = current_task.set(key)
    board.start(key)
    try:
        result = fn(*args, **kwargs)
    except Exception as e:
        result = f"Error: {key}: {e}"
    finally:
        current_task.reset(token)
    ok = is_success(result)
    board.finish(key, ok, "" if ok else _short_error(first_line(result), key))
    return result


def _short_error(message: str, name: str) -> str:
    for prefix in (f"Error: {name}: ", "Error: "):
        if message.startswith(prefix):
            message = message[len(prefix):]
            break
    return message if len(message) <= 120 else message[:119] + "…"


def task_name(path) -> str:
    return os.path.basename(str(path)) or str(path)

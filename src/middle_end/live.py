"""Run a back-end job in a thread and stream its ProgressBoard to Gradio."""
import contextvars
import threading
from typing import Callable, Iterator

from toolbox.progress import ProgressBoard, current_board

POLL_SECONDS = 0.5


def run_live(job: Callable[[], str], progress=None, label: str = "Fichiers",
             poll: float = POLL_SECONDS) -> Iterator[str]:
    """
    Yield the live board (multi-line text) every `poll` seconds while `job` runs, then its result.
    :param job: back-end call without arguments, returns the result text
    :param progress: gr.Progress (global bar + summary), optional
    :raise: the exception raised by `job` (exception_as_str turns it into "Error: ...")
    """
    board = ProgressBoard(label)
    outcome: dict = {}

    def target():
        current_board.set(board)
        try:
            outcome["value"] = job()
        except Exception as e:
            outcome["error"] = e

    # copy_context: the job thread keeps the caller's ContextVars (and gets its own board)
    thread = threading.Thread(target=contextvars.copy_context().run, args=(target,), daemon=True)
    thread.start()

    last = None
    while thread.is_alive():
        thread.join(poll)
        if not thread.is_alive():
            break
        if progress is not None:
            progress(board.overall(), desc=board.summary())
        text = board.render()
        if text != last:
            last = text
            yield text

    if "error" in outcome:
        raise outcome["error"]
    result = outcome.get("value") or ""
    notes = board.notes()
    yield "\n".join([result, *notes]) if notes else result

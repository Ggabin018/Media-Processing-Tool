import contextvars
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable

from toolbox.parameters import Params
from toolbox.progress import ProgressBoard, current_board, run_registered, task_name


def map_in_threads(fn: Callable, items: Iterable, name: Callable = task_name) -> list:
    """
    Run fn(item) for every item in a thread pool (max_workers from the parameters).
    - every item is shown on the current ProgressBoard (pending, then its percentage, then ✔/✖),
    - results come back in the order of the items,
    - an exception becomes an "Error: <file>: <msg>" result instead of being lost.
    """
    items = list(items)
    board_token = current_board.set(ProgressBoard()) if current_board.get() is None else None
    try:
        keys = current_board.get().add([name(item) for item in items])
        with ThreadPoolExecutor(max_workers=max(1, Params().get_max_workers())) as executor:
            # one context copy per task: ContextVars (the board) are not inherited by pool threads
            futures = [executor.submit(contextvars.copy_context().run, run_registered, key, fn, item)
                       for key, item in zip(keys, items)]
            return [f.result() for f in futures]
    finally:
        if board_token is not None:
            current_board.reset(board_token)

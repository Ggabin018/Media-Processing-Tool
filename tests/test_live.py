import time

import pytest

from middle_end.live import run_live
from toolbox.progress import current_board, report, run_task


def test_streams_board_then_result():
    def job():
        return run_task("a.mp4", slow)

    def slow():
        for i in range(1, 6):
            report(i / 5)
            time.sleep(0.05)
        return "done"

    fractions = []
    values = list(run_live(job, progress=lambda f, desc=None: fractions.append((f, desc)), poll=0.02))

    assert values[-1] == "done"
    assert any(v.startswith("a.mp4 : ") for v in values[:-1])
    assert fractions and [f for f, _ in fractions] == sorted(f for f, _ in fractions)
    assert all(desc == "Fichiers 0/1 traités" for _, desc in fractions)


def test_identical_states_are_not_repeated():
    values = list(run_live(lambda: time.sleep(0.2) or "ok", poll=0.02))
    assert values[-1] == "ok"
    assert len(values) == len(set(values))


def test_job_exception_is_raised():
    def job():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        list(run_live(job, poll=0.01))


def test_notes_are_appended_to_the_result():
    from toolbox.progress import add_note

    def job():
        return run_task("a.mp4", lambda: add_note("3 images illisibles ignorées") or "out.mp4")

    assert list(run_live(job, poll=0.01))[-1] == "out.mp4\na.mp4 : 3 images illisibles ignorées"


def test_each_run_has_its_own_board():
    boards = []
    list(run_live(lambda: boards.append(current_board.get()) or "x", poll=0.01))
    list(run_live(lambda: boards.append(current_board.get()) or "x", poll=0.01))
    assert boards[0] is not None and boards[0] is not boards[1]
    assert current_board.get() is None  # nothing leaks into the caller

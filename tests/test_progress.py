import threading
import time

import pytest

from toolbox import threads
from toolbox.progress import ProgressBoard, current_board, current_task, report, add_note, run_task, is_success
from toolbox.threads import map_in_threads


@pytest.fixture
def out_file(tmp_path):
    f = tmp_path / "out.mp4"
    f.write_bytes(b"")
    return str(f)


# --- ProgressBoard ---

def test_render_like_the_mockup():
    board = ProgressBoard("Vidéos")
    a, b, c, d = board.add(["A.mp4", "B.mp4", "C.mp4", "D.mp4"])
    board.start(a)
    board.finish(a, ok=True)
    board.start(b)
    board.update(b, 0.5)
    board.start(c)
    board.update(c, 0.2)

    assert board.render() == "B.mp4 : 50%\nC.mp4 : 20%\n1 en attente\nVidéos 1/4 traitées"
    assert board.overall() == pytest.approx((1 + 0.5 + 0.2) / 4)


def test_errors_are_listed():
    board = ProgressBoard()
    a, b = board.add(["a.mp4", "b.mp4"])
    for key in (a, b):
        board.start(key)
    board.finish(a, ok=False, message="encoder not found")
    board.finish(b, ok=True)
    assert board.render() == "a.mp4 : ✖ encoder not found\nFichiers 2/2 traités, 1 en erreur"


def test_single_file_shows_only_its_line():
    board = ProgressBoard()
    (a,) = board.add(["a.mp4"])
    board.start(a)
    board.update(a, 0.42)
    assert board.render() == "a.mp4 : 42%"


def test_progress_never_goes_back_and_is_capped():
    board = ProgressBoard()
    (a,) = board.add(["a.mp4"])
    board.start(a)
    board.update(a, 0.6)
    board.update(a, 0.3)
    assert board.overall() == pytest.approx(0.6)
    board.update(a, 7)
    assert board.overall() == 1.0


def test_duplicate_names_get_a_suffix():
    assert ProgressBoard().add(["a.mp4", "a.mp4", "a.mp4"]) == ["a.mp4", "a.mp4 (2)", "a.mp4 (3)"]


def test_empty_board():
    board = ProgressBoard()
    assert board.overall() == 0.0
    assert board.render() == "Fichiers 0/0 traités"


def test_concurrent_updates():
    board = ProgressBoard()
    keys = board.add([f"{i}.mp4" for i in range(20)])

    def work(key):
        board.start(key)
        for i in range(100):
            board.update(key, i / 100)
        board.finish(key, ok=True)

    ts = [threading.Thread(target=work, args=(k,)) for k in keys]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert board.overall() == 1.0
    assert board.summary() == "Fichiers 20/20 traités"


# --- report / run_task ---

def test_report_is_a_noop_outside_a_processing():
    report(0.5)
    add_note("nothing")


def test_run_task_tracks_success(out_file):
    board = ProgressBoard()
    token = current_board.set(board)
    try:
        def job():
            assert current_task.get() == "a.mp4"
            report(0.5)
            add_note("hello")
            return out_file
        assert run_task("a.mp4", job) == out_file
    finally:
        current_board.reset(token)
    assert board.summary() == "Fichiers 1/1 traités"
    assert board.notes() == ["a.mp4 : hello"]
    assert current_task.get() is None


def test_run_task_turns_exception_into_error():
    board = ProgressBoard()
    token = current_board.set(board)
    try:
        result = run_task("a.mp4", lambda: 1 / 0)
    finally:
        current_board.reset(token)
    assert result.startswith("Error: a.mp4: ")
    assert "a.mp4 : ✖ division by zero" in board.render()


def test_run_task_without_board_leaves_no_board():
    assert run_task("a", lambda: "x") == "x"
    assert current_board.get() is None


@pytest.mark.parametrize("result, ok", [
    ("{out}", True), ("{out}\n24 images illisibles ignorées", True),
    ("Error: boom", False), ("", False), (None, False), ("C:/nope.mp4", False),
])
def test_is_success(result, ok, out_file):
    result = result.format(out=out_file) if isinstance(result, str) else result
    assert is_success(result) is ok


# --- map_in_threads ---

@pytest.fixture
def two_workers(monkeypatch):
    monkeypatch.setattr(threads.Params, "get_max_workers", lambda self: 2)


def test_map_in_threads_order_and_board(two_workers, out_file):
    board = ProgressBoard("Vidéos")
    token = current_board.set(board)
    snapshots = []

    def work(item):
        report(0.5)
        snapshots.append(board.render())
        time.sleep(0.05 * (3 - item))  # finish in reverse order
        return out_file if item != 1 else f"Error: bad {item}"

    try:
        results = map_in_threads(work, [0, 1, 2], name=lambda i: f"{i}.mp4")
    finally:
        current_board.reset(token)

    assert results == [out_file, "Error: bad 1", out_file]  # input order
    assert any("en attente" in s for s in snapshots)  # 2 workers for 3 items
    assert board.summary() == "Vidéos 3/3 traitées, 1 en erreur"
    assert "1.mp4 : ✖ bad 1" in board.render()


def test_map_in_threads_exception_is_not_lost(two_workers):
    def work(item):
        if item == "b":
            raise ValueError("broken file")
        return item

    results = map_in_threads(work, ["a", "b", "c"], name=str)
    assert results == ["a", "Error: b: broken file", "c"]


def test_map_in_threads_with_one_worker(monkeypatch):
    monkeypatch.setattr(threads.Params, "get_max_workers", lambda self: 1)
    assert map_in_threads(lambda x: x * 2, [1, 2, 3], name=str) == [2, 4, 6]


def test_map_in_threads_empty():
    assert map_in_threads(lambda x: x, []) == []

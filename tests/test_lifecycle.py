import subprocess
import sys
import threading

import pytest

from toolbox import lifecycle, windowless
from toolbox.lifecycle import TabWatcher, track_job, jobs_running, TAB_SCRIPT, ALIVE_PATH, CLOSED_PATH


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def make_watcher():
    def make(busy=lambda: False):
        clock, calls = Clock(), []
        w = TabWatcher(on_idle=lambda: calls.append(1), grace=10, timeout=120, first_tab_timeout=60,
                       is_busy=busy, clock=clock)
        return w, clock, calls
    return make


def test_last_tab_closed_stops_after_grace(make_watcher):
    w, clock, calls = make_watcher()
    w.alive("a")
    clock.now += 30
    w.closed("a")
    assert not w.tick()                 # grace starts
    clock.now += 9
    assert not w.tick() and calls == []
    clock.now += 1
    assert w.tick() and calls == [1]


def test_refresh_does_not_stop(make_watcher):
    w, clock, calls = make_watcher()
    w.alive("a")
    w.closed("a")                       # reload: pagehide of the old page...
    w.tick()
    clock.now += 2
    w.alive("b")                        # ... then the new page pings
    clock.now += 60
    w.alive("b")
    assert not w.tick() and calls == [] and w.tabs == 1


def test_one_tab_closed_among_two_keeps_running(make_watcher):
    w, clock, calls = make_watcher()
    w.alive("a")
    w.alive("b")
    w.closed("a")
    clock.now += 60
    w.alive("b")
    assert not w.tick() and w.tabs == 1


def test_silent_tab_expires(make_watcher):
    """No pagehide (browser crash): the tab expires after `timeout` without ping, then grace."""
    w, clock, calls = make_watcher()
    w.alive("a")
    clock.now += 119
    assert not w.tick() and w.tabs == 1
    clock.now += 1
    assert not w.tick() and w.tabs == 0
    clock.now += 10
    assert w.tick() and calls == [1]


def test_waits_for_running_job(make_watcher):
    busy = [True]
    w, clock, calls = make_watcher(busy=lambda: busy[0])
    w.alive("a")
    w.closed("a")
    w.tick()
    clock.now += 600
    assert not w.tick() and calls == []
    busy[0] = False
    assert w.tick() and calls == [1]


def test_no_tab_ever_connects(make_watcher):
    w, clock, calls = make_watcher()
    clock.now += 59
    assert not w.tick()
    clock.now += 1
    assert w.tick() and calls == [1]


def test_on_idle_called_once(make_watcher):
    w, clock, calls = make_watcher()
    w.closed("unknown")                 # closed without alive: ignored
    clock.now += 100
    assert w.tick() and w.tick()
    assert calls == [1]


def test_start_loop_stops(make_watcher):
    calls = []
    w = TabWatcher(on_idle=lambda: calls.append(1), first_tab_timeout=0)
    w.start(interval=0.01).join(timeout=5)
    assert calls == [1]


def test_tab_script_uses_routes():
    assert ALIVE_PATH in TAB_SCRIPT and CLOSED_PATH in TAB_SCRIPT and "sendBeacon" in TAB_SCRIPT


def test_track_job():
    assert not jobs_running()
    with track_job():
        assert jobs_running()
        with track_job():
            pass
        assert jobs_running()
    assert not jobs_running()


def test_track_job_released_on_error():
    with pytest.raises(ValueError):
        with track_job():
            raise ValueError
    assert not jobs_running()


def test_run_live_tracks_job():
    from middle_end.live import run_live
    seen = []
    release = threading.Event()

    def job():
        seen.append(jobs_running())
        release.set()
        return "ok"

    assert list(run_live(job, poll=0.01))[-1] == "ok"
    assert seen == [True] and not lifecycle.jobs_running()


# region windowless

def test_redirect_noop_with_console(tmp_path):
    assert not windowless.redirect_missing_stdio(str(tmp_path / "app.log"))


def test_redirect_without_console(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)
    log = tmp_path / "logs" / "app.log"
    assert windowless.redirect_missing_stdio(str(log))
    print("hello")
    sys.stderr.write("oops\n")
    sys.stdout.flush()
    text = log.read_text(encoding="utf-8")
    assert "hello" in text and "oops" in text
    sys.stdout.close()


def test_hide_child_consoles_only_on_windows():
    assert not windowless.hide_child_consoles(platform="linux")


@pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
def test_hide_child_consoles_adds_flag(monkeypatch):
    seen = {}

    def fake_init(self, *args, **kwargs):
        seen.update(kwargs)

    monkeypatch.setattr(subprocess.Popen, "__init__", fake_init)
    assert windowless.hide_child_consoles()
    assert not windowless.hide_child_consoles()     # not wrapped twice
    subprocess.Popen.__init__(object.__new__(subprocess.Popen), ["x"])
    assert seen["creationflags"] == windowless.CREATE_NO_WINDOW
    subprocess.Popen.__init__(object.__new__(subprocess.Popen), ["x"], creationflags=0x10)
    assert seen["creationflags"] == 0x10            # explicit flags kept


# region Gradio wiring

def test_tab_routes_feed_the_watcher():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from front_end.gradio_manager import GradioManager
    m = GradioManager()
    assert TAB_SCRIPT in m.interface.head
    app = FastAPI()
    m.add_tab_routes(app)
    client = TestClient(app)
    assert client.get(ALIVE_PATH, params={"tab": "t1"}).status_code == 204
    assert m.watcher.tabs == 1
    assert client.post(CLOSED_PATH, params={"tab": "t1"}).status_code == 204
    assert m.watcher.tabs == 0

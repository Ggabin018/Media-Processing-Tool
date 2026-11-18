"""
App lifecycle: stop the server when no browser tab is left, without losing a running job.

- `track_job()` wraps every back-end job (run_live), `jobs_running()` tells if one is in progress,
- every page pings the server (`TAB_SCRIPT`: /app/alive every few seconds, /app/closed on pagehide),
- `TabWatcher` calls `on_idle` once no tab is alive for `grace` seconds and no job is running.
  The grace period covers a refresh (closed, then the new page pings); a tab that disappears
  without "closed" (browser crash) expires after `timeout` seconds without ping (hidden tabs
  are throttled by the browser, down to one timer per minute: the timeout must stay above that).

Gradio's own load / unload events are not used: in Gradio 5.23 unload needs the heartbeat, only
enabled when the last event is an unload, and load is not triggered again after a page reload.
"""
import threading
import time
from contextlib import contextmanager
from typing import Callable

ALIVE_PATH = "/app/alive"
CLOSED_PATH = "/app/closed"
PING_SECONDS = 5

TAB_SCRIPT = f"""
<script>
(function () {{
    const tab = Math.random().toString(36).slice(2);
    const ping = () => fetch("{ALIVE_PATH}?tab=" + tab, {{cache: "no-store"}}).catch(() => {{}});
    ping();
    setInterval(ping, {PING_SECONDS * 1000});
    window.addEventListener("pageshow", ping);  // back from the bfcache
    window.addEventListener("pagehide", () => navigator.sendBeacon("{CLOSED_PATH}?tab=" + tab));
}})();
</script>
"""

_jobs_lock = threading.Lock()
_jobs = 0


@contextmanager
def track_job():
    global _jobs
    with _jobs_lock:
        _jobs += 1
    try:
        yield
    finally:
        with _jobs_lock:
            _jobs -= 1


def jobs_running() -> bool:
    with _jobs_lock:
        return _jobs > 0


class TabWatcher:
    def __init__(self, on_idle: Callable[[], None], grace: float = 10.0, timeout: float = 120.0,
                 first_tab_timeout: float = 60.0, is_busy: Callable[[], bool] = jobs_running,
                 clock: Callable[[], float] = time.monotonic):
        self._on_idle = on_idle
        self._grace = grace
        self._timeout = timeout
        self._is_busy = is_busy
        self._clock = clock
        self._lock = threading.Lock()
        self._tabs: dict[str, float] = {}  # tab id -> last ping
        self._stopped = False
        # until the first tab connects, the app waits longer (browser starting)
        self._idle_since = clock()
        self._idle_delay = first_tab_timeout

    @property
    def tabs(self) -> int:
        with self._lock:
            return len(self._tabs)

    def alive(self, tab: str) -> None:
        with self._lock:
            self._tabs[tab] = self._clock()
            self._idle_since = None

    def closed(self, tab: str) -> None:
        with self._lock:
            self._tabs.pop(tab, None)

    def tick(self) -> bool:
        """Check the tabs; calls on_idle (once) when it is time to stop. Returns True if stopped."""
        with self._lock:
            if self._stopped:
                return True
            now = self._clock()
            self._tabs = {t: last for t, last in self._tabs.items() if now - last < self._timeout}
            if self._tabs:
                self._idle_since = None
                return False
            if self._idle_since is None:
                self._idle_since, self._idle_delay = now, self._grace
            if now - self._idle_since < self._idle_delay or self._is_busy():
                return False  # a running job goes on, the app stops right after it
            self._stopped = True
        self._on_idle()
        return True

    def start(self, interval: float = 1.0) -> threading.Thread:
        def loop():
            while not self.tick():
                time.sleep(interval)

        thread = threading.Thread(target=loop, name="tab-watcher", daemon=True)
        thread.start()
        return thread

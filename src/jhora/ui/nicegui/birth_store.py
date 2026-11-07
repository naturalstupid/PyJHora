#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Memory-only storage for personal birth details.

PERSONAL_KEYS (date and time of birth, place name, latitude, longitude, time zone) are held only
in the memory of the server process, per browser. They are never written to disk or to a cookie,
are discarded when a browser has been idle for more than IDLE_SECONDS (environment variable
JHORA_BIRTH_IDLE_SECONDS, default 3600) and are lost when the server stops. A browser counts as active
when it loads a page or changes one of these values. Idle browsers are found by a small background
thread that checks every few minutes, and also whenever a page is loaded. All other keys stay in
app.storage.user.

SessionState behaves like a dict, so page code can use state["date_dob"], state.update({...}),
state.get(...) and dict(state).
"""
import os
import time
import threading
from collections.abc import MutableMapping

from nicegui import app

PERSONAL_KEYS = frozenset({
    "date_dob", "time_tob", "place_name",
    "latitude", "longitude", "timezone",
})
IDLE_SECONDS = int(os.environ.get("JHORA_BIRTH_IDLE_SECONDS", "3600"))

_lock = threading.Lock()
_data = {}  # browser_id -> [last_seen_epoch, {key: value}]
_purger_started = False


def _browser_id():
    """Returns the id of the current browser (from app.storage.browser)."""
    return app.storage.browser["id"]


def _purge_idle(now):
    """Deletes the birth details of every browser idle for more than IDLE_SECONDS. Call with _lock held.

    Args:
        now: current time in seconds since the epoch.
    """
    for bid, (seen, _) in list(_data.items()):
        if now - seen > IDLE_SECONDS:
            del _data[bid]


def purge_idle():
    """Deletes the birth details of every browser idle for more than IDLE_SECONDS."""
    with _lock:
        _purge_idle(time.time())


def _ensure_purger():
    """Starts, once, a daemon thread that calls purge_idle() every few minutes, so that idle details are
    deleted even when nobody loads a page.
    """
    global _purger_started
    if _purger_started:
        return
    _purger_started = True
    interval = max(30, min(300, IDLE_SECONDS // 4))

    def _loop():
        while True:
            time.sleep(interval)
            try:
                purge_idle()
            except Exception:
                pass

    threading.Thread(target=_loop, name="birth-store-purge", daemon=True).start()


def _touch(bid, temp):
    """Restarts the idle timer of a browser after one of its values changed, and registers its dict again
    if it had been purged meanwhile.

    Args:
        bid: browser id.
        temp: the browser's in-memory dict.
    """
    with _lock:
        entry = _data.get(bid)
        if entry is None:
            _data[bid] = [time.time(), temp]
        else:
            entry[0] = time.time()


def _temp_dict():
    """Returns the in-memory dict of the current browser, creating it if needed, and restarts its idle
    timer. Also purges idle entries of other browsers and starts the background purge thread.
    """
    _ensure_purger()
    bid = _browser_id()
    now = time.time()
    with _lock:
        _purge_idle(now)
        entry = _data.setdefault(bid, [now, {}])
        entry[0] = now
        return entry[1]


def forget_me():
    """Deletes the birth details of the current browser immediately."""
    with _lock:
        _data.pop(_browser_id(), None)


def purge_from_disk_storage():
    """Removes any PERSONAL_KEYS from app.storage.user, so birth details are never kept on disk."""
    for k in PERSONAL_KEYS:
        app.storage.user.pop(k, None)


class SessionState(MutableMapping):
    """Dict-like view of the page state. PERSONAL_KEYS are stored in memory (this module); all other keys
    are stored in app.storage.user.
    """

    def __init__(self):
        self._persist = app.storage.user
        self._bid = _browser_id()
        self._temp = _temp_dict()

    def _target(self, key):
        return self._temp if key in PERSONAL_KEYS else self._persist

    def __getitem__(self, key):
        return self._target(key)[key]

    def __setitem__(self, key, value):
        self._target(key)[key] = value
        if key in PERSONAL_KEYS:
            _touch(self._bid, self._temp)

    def __delitem__(self, key):
        del self._target(key)[key]

    def __iter__(self):
        yield from (k for k in list(self._persist) if k not in PERSONAL_KEYS)
        yield from list(self._temp)

    def __len__(self):
        return sum(1 for _ in self)

    def __repr__(self):
        return f"SessionState({dict(self)!r})"

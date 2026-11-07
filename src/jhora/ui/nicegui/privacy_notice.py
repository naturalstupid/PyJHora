#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""One-time privacy notice.

Shows the visitor a notification that the birth details they enter are held only in the memory of
the server (see birth_store.py). It is shown once per browser: on the first page load, and again
after that browser has been idle for longer than birth_store.IDLE_SECONDS or after a server restart.
Only random browser ids are remembered here, in memory.

Use: call show_privacy_notice() in navigation_header() (components.py), after adding the page CSS.
Translation: add the key privacy_temp_notice_str to the language message files; otherwise the
English text _DEFAULT_TEXT is shown.
"""
import time

from nicegui import ui, app
from jhora import utils
import birth_store

_seen = {}  # random browser id -> time the notice was last shown

_DEFAULT_TEXT = (
    "Privacy: the birth details you enter (date, time and place) are held only in the server's memory "
    "while you use this site. They are never written to disk or stored in a cookie, are discarded after "
    "a period of inactivity, and are lost whenever the server restarts. The cookie holds only a random ID "
    "that remembers your settings (such as language)."
)


def _text():
    """Returns the notice text: resource string privacy_temp_notice_str, or _DEFAULT_TEXT if it is not available."""
    try:
        return utils.resource_strings.get('privacy_temp_notice_str', _DEFAULT_TEXT)
    except Exception:
        return _DEFAULT_TEXT


def show_privacy_notice():
    """Shows the privacy notification (top of the page, closable, 20 s) unless this browser has already
    seen it. Errors are printed (exception type only) and never interrupt page loading.
    """
    try:
        bid = app.storage.browser["id"]
        now = time.time()
        for k, t in list(_seen.items()):  # forget browsers whose notice is older than the birth-data timeout
            if now - t > birth_store.IDLE_SECONDS:
                del _seen[k]
        if bid in _seen:
            return
        _seen[bid] = now
        ui.notify(_text(), type='info', position='top', multi_line=True,
                  close_button=True, timeout=20000)
    except Exception as e:  # a notice must never interrupt page loading
        print(f"show_privacy_notice: {type(e).__name__}")

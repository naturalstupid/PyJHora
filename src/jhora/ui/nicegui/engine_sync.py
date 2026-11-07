#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Synchronization helpers for jhora's process-global calculation state.

jhora.const, jhora.utils and jhora.config are module-level state shared by every request in the
server process. calc_lock() serialises access to them and, in public mode, applies the current
browser's settings for the duration of the block. The first time it is entered it also runs
web_settings.install().
"""
import functools
import threading
from contextlib import contextmanager, nullcontext
from jhora import const, utils

_CALC_LOCK = threading.Lock()
_INSTALLED = False


def _ensure_installed():
    """Runs web_settings.install() once; a failure is printed and not retried."""
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True            # set first: never retry/recurse if it fails
    try:
        import web_settings
        web_settings.install()
    except Exception as e:
        print(f"[calc_lock] web_settings.install() failed: {e}")


def _user_runtime():
    """Returns web_settings.user_runtime(), or a no-op context manager if it is unavailable."""
    try:
        import web_settings
        return web_settings.user_runtime()
    except Exception as e:
        print(f"[calc_lock] per-user settings unavailable: {e}")
        return nullcontext()

import swisseph as swe, threading

def _apply_thread_swe_state():
    """Swiss Ephemeris path and sidereal mode are per thread; pool threads start without them."""
    utils.set_ephemeris_data_path()
    utils.hora_engine_proxy.set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE)
    r = swe.calc_ut(2461333.1, swe.SUN, swe.FLG_SWIEPH)[1]      # temporary probe
    #print("[calc_lock]", threading.current_thread().name,"moshier_fallback=", bool(r & swe.FLG_MOSEPH), flush=True)

@contextmanager
def calc_lock():
    with _CALC_LOCK:
        _ensure_installed()
        with _user_runtime():
            _apply_thread_swe_state()   # after the visitor's settings, so their ayanamsa applies
            yield

def apply_current_language():
    """Loads the language tables for const._DEFAULT_LANGUAGE (utils.set_language()) under the lock.
    config.apply_setting('language') only sets the constant, so call this once at startup and after
    the baseline language changes.
    """
    with calc_lock():
        try:
            utils.set_language(const._DEFAULT_LANGUAGE)
        except Exception as e:
            print(f"apply_current_language: failed to apply language '{const._DEFAULT_LANGUAGE}': {e}")


def _is_client_disconnected_error(exc: Exception) -> bool:
    """Returns True if `exc` is the RuntimeError NiceGUI raises when the page's client has already gone."""
    return isinstance(exc, RuntimeError) and 'parent element' in str(exc).lower() and 'deleted' in str(exc).lower()


def safe_notify(message, type='info'):
    """Shows a notification, ignoring the error raised when the client has disconnected.

    Args:
        message: text to show.
        type: NiceGUI notification type ('info', 'positive', 'warning', 'negative').
    """
    from nicegui import ui
    try:
        ui.notify(message, type=type)
    except RuntimeError as e:
        if _is_client_disconnected_error(e):
            # The message text is not logged: error messages can contain what the visitor typed.
            print("[safe_notify] client disconnected before notify could show")
        else:
            raise


def ignore_disconnected_client(func):
    """Decorator for event handlers: returns None instead of raising when the client has disconnected.
    Other exceptions are re-raised.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if _is_client_disconnected_error(e):
                print(f"[ignore_disconnected_client] client disconnected during '{func.__name__}' - ignoring: {e}")
                return None
            raise
    return wrapper

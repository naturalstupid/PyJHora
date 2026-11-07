#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Per-browser settings for JHoraWeb.

The settings loaded by jhora.config (factory_settings.json plus user_settings.json) are the
server baseline. In public mode each browser keeps only its own overrides in app.storage.user and
the baseline files are never rewritten.

user_runtime() is entered by calc_lock() around every calculation. It
  1. snapshots the simple jhora.const values and the language globals of utils,
  2. applies this browser's overrides through config.apply_setting() and swaps in its language,
  3. points function default arguments listed in jhora_default_bindings.json at the current
     const values,
  4. runs the caller's block,
  5. undoes steps 3 and 2 and restores the snapshots, which also undoes global changes PyJHora
     makes by itself during the call.

install() (public mode, call once at startup) makes language reads outside calc_lock()
visitor-aware, replaces config.get_value() with a per-visitor version and turns off IP-based
location lookup.

Environment variables:
  JHORA_PUBLIC=1        per-browser mode. Default: admin mode (every setting visible, saving
                        writes the baseline files).
  JHORA_MULTIUSER=0     disable per-browser settings.
  JHORA_CLEAR_CACHES=1  clear the lru_caches of jhora modules around each calculation.
  JHORA_BINDINGS, JHORA_CONFIG_DIR   location of jhora_default_bindings.json.
  JHORA_LANG_DIR        folder of the language files.
"""
import copy
import json
import os
import sys
import threading
from contextlib import contextmanager

from nicegui import app
from jhora import config, const
import web_language

MULTI_USER = os.environ.get("JHORA_MULTIUSER", "1") != "0"
ADMIN = os.environ.get("JHORA_PUBLIC", "0") != "1"
CLEAR_CACHES = os.environ.get("JHORA_CLEAR_CACHES", "0") == "1"

# Settings that stay server-wide and are not offered to visitors: they are read while pages are built,
# change list sizes that pages index by, or (hora_chart_by_pvr_method) are read once at import of charts.py.
SERVER_WIDE_KEYS = frozenset({
    "database_engine", "maximum_search_places",
    "expand_all_tabs_to_save_as_pdf",
    "hora_chart_by_pvr_method",
})

# const attribute -> setting whose setter also changes engine state outside const (Swiss Ephemeris sidereal
# mode, astrology-model dispatch, planet list). If PyJHora changes one of these during a call, the setter is
# re-run with the baseline value afterwards.
_ENGINE_OWNERS = (
    ("_DEFAULT_AYANAMSA_MODE", "default_ayanamsa_mode"),
    ("astrology_model_default", "astrology_engine"),
    ("_INCLUDE_URANUS_TO_PLUTO", "include_uranus_to_pluto"),
    ("_use_true_nodes_for_rahu_ketu", "use_true_nodes_for_rahu_ketu"),
)

# Settings that only have a const_name (no setter). Changing one requires the Swiss Ephemeris flags kept in
# drik to be rebuilt (rebuild_engine_flags()).
FLAG_KEYS = frozenset({
    "planet_position_reference_frame", "planet_position_type",
    "use_aberration_of_light", "use_gravitational_deflection", "use_nutation",
    "rise_set_use_refraction", "rise_set_use_disc_center_for_rising",
    "rise_set_hindu_rising",
})


def rebuild_engine_flags():
    """Rebuilds the Swiss Ephemeris planet-position and rise/set flags stored in drik (PLANET_FLAGS,
    RISE_FLAGS, SET_FLAGS) from the current const values. utils.set_flags_for_*() only return flags,
    so drik.refresh_planet_flags() is used to store them.
    """
    try:
        from jhora.panchanga import drik
        drik.refresh_planet_flags()
    except Exception as e:
        print(f"[web_settings] could not rebuild planet/rise-set flags: {e}")


_MISSING = object()
_SIMPLE = (int, float, str, bool, type(None))
_EXTRA_CONST_ATTRS = ("DHASA_STRONGER_PAIR_RULES",)
_orig_get_value = getattr(config.get_value, "_jhora_orig", config.get_value)
_tls = threading.local()
_installed = False
_bindings_cache = None


def _public():
    """Returns True when per-browser settings are active (MULTI_USER and not ADMIN)."""
    return MULTI_USER and not ADMIN


def is_user_setting(key):
    """Returns True if `key` is a known setting that a visitor may change (not in SERVER_WIDE_KEYS)."""
    return key in config._FACTORY and key not in SERVER_WIDE_KEYS


# ---------------------------------------------------------------- visitor overrides
# How a visitor's settings are resolved (the usual app model):
#   * The release decides. factory_settings.json (schema + defaults) plus user_settings.json
#     (this release's values) form the baseline; every setting the visitor has not changed
#     follows it, so new defaults reach those visitors automatically.
#   * A visitor's own change is kept across releases, and is stored only when it differs from
#     the baseline.
#   * A stored change is dropped (the visitor goes back to the release value and gets a short
#     notice) when this release no longer accepts it:
#       - the setting was removed or made server-wide,
#       - the stored value no longer has the setting's type, or is no longer one of its choices,
#       - the label of the chosen choice changed (the choice probably means something else now),
#       - the setting's "revision" in factory_settings.json was raised. Raise it (default 0) in
#         the same edit when you change what an existing value of that setting means.
#   Nothing has to be remembered per release; the checks run against the schema shipped with it.
_STORE_KEY = "jhora_setting_overrides_v2"   # {key: {"v": value, "rev": int, "label": str|None}}
_OLD_STORE_KEY = "jhora_setting_overrides"  # older format {key: value}; converted on first visit


def _same(a, b):
    """Equality that does not treat True as 1 (Python's True == 1); int and float compare by value."""
    num = (int, float)
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, num) and isinstance(b, num):
        return a == b
    return type(a) is type(b) and a == b


def _choices(meta):
    """Returns the setting's choices as [(stored value, label), ...]."""
    out = []
    for c in meta.get("choices", []):
        if isinstance(c, (list, tuple)) and len(c) == 2:
            out.append((c[0], str(c[1])))
        else:
            out.append((c, str(c)))
    return out


def _choice_label(meta, value):
    """Returns the label of `value` among the setting's choices, or None."""
    for stored, label in _choices(meta):
        if _same(stored, value):
            return label
    return None


def _value_ok(meta, value):
    """Returns True if `value` has the setting's declared type (and, for a choice, is one of its choices)."""
    type_ = str(meta.get("type", "string")).strip().lower()
    if type_ == "choice":
        return any(_same(stored, value) for stored, _ in _choices(meta))
    if value is None:
        return bool(meta.get("nullable", False))
    is_int = isinstance(value, int) and not isinstance(value, bool)
    if type_ == "bool":
        return isinstance(value, bool)
    if type_ == "int":
        return is_int
    if type_ == "float":
        return is_int or isinstance(value, float)
    if type_ == "string":
        return isinstance(value, str)
    if type_ in ("int_list", "float_list", "string_list"):
        if not isinstance(value, list):
            return False
        item_ok = {
            "int_list": lambda x: isinstance(x, int) and not isinstance(x, bool),
            "float_list": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
            "string_list": lambda x: isinstance(x, str),
        }[type_]
        return all(item_ok(x) for x in value)
    return True                       # unknown type in the schema: accept, as config.py does


def _is_valid_value(key, value):
    """Returns True if `value` is acceptable for setting `key` in this release."""
    meta = config._FACTORY.get(key)
    return meta is not None and _value_ok(meta, value)


def _make_entry(key, value):
    """Returns the stored form of a visitor's change: the value plus what it meant when chosen."""
    meta = config._FACTORY[key]
    return {"v": copy.deepcopy(value), "rev": int(meta.get("revision", 0)),
            "label": _choice_label(meta, value)}


def _entry_ok(key, entry):
    """Returns True if a stored entry is still accepted by this release (see the rules above)."""
    if not is_user_setting(key) or not isinstance(entry, dict) or "v" not in entry:
        return False
    meta = config._FACTORY[key]
    value = entry["v"]
    if not _value_ok(meta, value):
        return False
    if int(entry.get("rev", 0)) != int(meta.get("revision", 0)):
        return False
    old_label = entry.get("label")
    if old_label is not None and _choice_label(meta, value) != old_label:
        return False
    return True


def _stored_entries():
    """Returns (entries, from_old_format) for this browser; ({}, False) without a client context."""
    try:
        store = app.storage.user
    except Exception:          # no client context (startup, background thread)
        return {}, False
    try:
        entries = store.get(_STORE_KEY)
        if isinstance(entries, dict):
            return dict(entries), False
        old = store.get(_OLD_STORE_KEY)
        if isinstance(old, dict):          # older format: plain values, no label/revision recorded
            return {k: {"v": v, "rev": int(config._FACTORY.get(k, {}).get("revision", 0)), "label": None}
                    for k, v in old.items()}, True
    except Exception:
        pass
    return {}, False


def _clean(entries):
    """Splits stored entries into (kept entries, dropped keys). Changes equal to the current baseline
    are dropped silently, so the visitor follows that setting's release value from now on."""
    kept, dropped = {}, []
    for key, entry in entries.items():
        if not _entry_ok(key, entry):
            dropped.append(key)
        elif not _same(entry["v"], _orig_get_value(key)):
            kept[key] = entry
    return kept, dropped


def get_user_overrides():
    """Returns this browser's valid overrides as {key: value}, limited to settings a visitor may change."""
    entries, _ = _stored_entries()
    kept, _ = _clean(entries)
    return {k: copy.deepcopy(e["v"]) for k, e in kept.items()}


def migrate_overrides():
    """Brings this browser's stored changes in line with this release, writing only when something
    changed. Call it once per page load (ensure_default_state() does).

    Returns:
        Labels of the settings whose stored change was dropped because this release no longer
        accepts it ([] if none), for a notice to the visitor.
    """
    if not _public():
        return []
    entries, from_old = _stored_entries()
    if not entries and not from_old:
        return []
    kept, dropped = _clean(entries)
    if from_old or len(kept) != len(entries):
        try:
            app.storage.user[_STORE_KEY] = kept
            app.storage.user.pop(_OLD_STORE_KEY, None)
        except Exception:
            return []
    labels = []
    for key in dropped:
        meta = config._FACTORY.get(key)
        if meta is not None and key not in SERVER_WIDE_KEYS:
            labels.append(str(meta.get("label", key)))
    return labels


def baseline_value(key, fallback=None):
    """Returns the server baseline value of a setting.

    Args:
        key: setting key.
        fallback: value returned if the key is unknown.
    """
    return _orig_get_value(key, fallback)


def effective_value(key):
    """Returns a copy of this visitor's value for `key`: the override if there is one, otherwise the
    server baseline. Use it, instead of const.X, for values needed while a page is being built
    (outside calc_lock()).
    """
    ov = get_user_overrides() if _public() else {}
    return copy.deepcopy(ov[key]) if key in ov else _orig_get_value(key)


def set_user_values(values):
    """Stores this browser's changes. A value equal to the baseline removes the change, so the
    visitor follows the release value of that setting again.

    Args:
        values: {setting key: value} - pass only the settings the visitor changed; keys a visitor
            may not change and values not valid in this release are ignored.
    """
    entries, _ = _stored_entries()
    kept, _ = _clean(entries)
    for key, value in values.items():
        if not is_user_setting(key):
            continue
        norm = config._normalize_value(config._FACTORY[key], value)
        if not _is_valid_value(key, norm) or _same(norm, _orig_get_value(key)):
            kept.pop(key, None)
        else:
            kept[key] = _make_entry(key, norm)
    app.storage.user[_STORE_KEY] = kept
    app.storage.user.pop(_OLD_STORE_KEY, None)


def reset_user_values():
    """Deletes all of this browser's overrides."""
    app.storage.user[_STORE_KEY] = {}
    app.storage.user.pop(_OLD_STORE_KEY, None)


# ---------------------------------------------------------------- internals
def _apply_value(key, value, rebuild=True):
    """Applies `value` for setting `key` through config.apply_setting() (including its setter), then
    restores config's own stored value.

    Args:
        key: setting key.
        value: value to apply.
        rebuild: also rebuild the engine flags when `key` is one of FLAG_KEYS.
    """
    if key not in config._FACTORY:
        return
    prev = config._USER.get(key, _MISSING)
    config._USER[key] = copy.deepcopy(value)
    _tls.bypass = True
    try:
        config.apply_setting(key)
        if rebuild and key in FLAG_KEYS:
            rebuild_engine_flags()
    finally:
        _tls.bypass = False
        if prev is _MISSING:
            config._USER.pop(key, None)
        else:
            config._USER[key] = prev


def _clear_jhora_caches():
    """Clears every lru_cache found in jhora modules. Returns the number of caches cleared."""
    n = 0
    for name, mod in list(sys.modules.items()):
        if mod is None or not (name == "jhora" or name.startswith("jhora.")):
            continue
        for obj in list(vars(mod).values()):
            clear = getattr(obj, "cache_clear", None)
            if callable(clear):
                try:
                    clear(); n += 1
                except Exception:
                    pass
    return n


def _snapshot_const():
    """Returns (simple, extra): the simple-typed values of jhora.const (int, float, str, bool, None) and
    deep copies of the attributes in _EXTRA_CONST_ATTRS.
    """
    d = vars(const)
    simple = {k: v for k, v in d.items() if isinstance(v, _SIMPLE) and not k.startswith("__")}
    extra = {k: copy.deepcopy(d[k]) for k in _EXTRA_CONST_ATTRS if k in d}
    return simple, extra


def _restore_const(snap):
    """Restores jhora.const from a _snapshot_const() result.

    Args:
        snap: tuple returned by _snapshot_const().
    """
    simple, extra = snap
    d = vars(const)
    for k, v in simple.items():
        if d.get(k, _MISSING) != v:
            d[k] = v
    for k in _EXTRA_CONST_ATTRS:
        if k in extra:
            d[k] = extra[k]
        else:
            d.pop(k, None)


def _bindings():
    """Returns [(module, function, param, const_name), ...] read from jhora_default_bindings.json (the
    first of JHORA_BINDINGS, JHORA_CONFIG_DIR and the current folder that exists), or [].
    """
    global _bindings_cache
    if _bindings_cache is None:
        _bindings_cache = []
        cands = [os.environ.get("JHORA_BINDINGS"),
                 os.path.join(os.environ.get("JHORA_CONFIG_DIR", ""), "jhora_default_bindings.json"),
                 "jhora_default_bindings.json"]
        for p in cands:
            if p and os.path.exists(p):
                try:
                    with open(p, encoding="utf-8") as f:
                        _bindings_cache = [tuple(x) for x in json.load(f)]
                except Exception as e:
                    print(f"[web_settings] could not read {p}: {e}")
                break
    return _bindings_cache


def _rebind_defaults():
    """Sets the default argument `param` of each function listed in the bindings file to the current
    value of const.<const_name>. Functions without a plain __code__ (decorated or cached) are skipped.

    Returns:
        undo list for _undo_rebind().
    """
    undo = []
    for mod_name, fn_name, param, const_name in _bindings():
        mod = sys.modules.get(mod_name)
        fn = getattr(mod, fn_name, None) if mod else None
        code = getattr(fn, "__code__", None)
        if code is None or not hasattr(const, const_name):
            continue
        new = getattr(const, const_name)
        names = code.co_varnames[:code.co_argcount]
        defaults = fn.__defaults__ or ()
        first = code.co_argcount - len(defaults)
        if param in names and names.index(param) >= first:
            i = names.index(param) - first
            if defaults[i] != new:
                undo.append((fn, "__defaults__", fn.__defaults__))
                fn.__defaults__ = defaults[:i] + (new,) + defaults[i + 1:]
        elif fn.__kwdefaults__ and param in fn.__kwdefaults__ and fn.__kwdefaults__[param] != new:
            undo.append((fn, "__kwdefaults__", dict(fn.__kwdefaults__)))
            fn.__kwdefaults__ = {**fn.__kwdefaults__, param: new}
    return undo


def _undo_rebind(undo):
    """Restores the default arguments changed by _rebind_defaults() (undo: its return value)."""
    for fn, attr, old in reversed(undo):
        setattr(fn, attr, old)


def _per_user_get_value(key, fallback=None):
    """Replacement for config.get_value() in public mode: returns this visitor's override if there is
    one, otherwise the baseline.

    Args:
        key: setting key.
        fallback: value returned if the key is unknown.
    """
    if _public() and not getattr(_tls, "bypass", False) and key in config._FACTORY:
        ov = get_user_overrides()
        if key in ov:
            return copy.deepcopy(ov[key])
    return _orig_get_value(key, fallback)


_per_user_get_value._jhora_orig = _orig_get_value


def install():
    """Call once at startup after config.initialize_runtime(). Rebuilds the engine flags from the
    baseline settings. In public mode it also turns off IP-based location lookup (it would use the
    server's IP), applies JHORA_LANG_DIR, installs the per-visitor language and replaces
    config.get_value() with a per-visitor version.
    """
    global _installed
    if _installed:
        return
    rebuild_engine_flags()          # baseline flags from user_settings.json (admin AND public)
    if not _public():
        _installed = True
        return
    const.use_internet_for_location_check = False   # geocoder.ip('me') = the SERVER's IP
    lang_dir = os.environ.get("JHORA_LANG_DIR")
    if lang_dir:
        const._LANGUAGE_PATH = lang_dir.rstrip("/\\") + os.sep
    web_language.install(lambda: get_user_overrides().get("language"))
    config.get_value = _per_user_get_value           # config.* internals see it too
    _installed = True


@contextmanager
def user_runtime():
    """Context manager entered by calc_lock() while the lock is held.

    Public mode: applies this browser's overrides and language for the duration of the block and
    restores the server baseline afterwards (also undoing global changes PyJHora makes during the
    call). Admin mode: only rebinds the default arguments listed in the bindings file.
    """
    if not _public():
        undo = _rebind_defaults()
        try:
            yield
        finally:
            _undo_rebind(undo)
        return
    changes = get_user_overrides()
    const_snap = _snapshot_const()
    lang_snap = web_language.snapshot()
    applied = []
    undo = []
    flags_dirty = False
    try:
        if CLEAR_CACHES:
            _clear_jhora_caches()
        for key, value in changes.items():
            if key == "language":
                continue
            applied.append(key)
            _apply_value(key, value, rebuild=False)
            flags_dirty = flags_dirty or key in FLAG_KEYS
        if flags_dirty:
            rebuild_engine_flags()
        if changes.get("language"):
            web_language.swap_in(changes["language"])
        undo = _rebind_defaults()
        yield
    finally:
        _undo_rebind(undo)
        # engine state PyJHora changed by itself (not via this visitor's overrides)
        leaked = [k for a, k in _ENGINE_OWNERS
                  if k in config._FACTORY and k not in applied
                  and getattr(const, a, _MISSING) != const_snap[0].get(a, _MISSING)]
        web_language.restore(lang_snap)
        for key in applied:
            _apply_value(key, _orig_get_value(key), rebuild=False)
        _restore_const(const_snap)
        if flags_dirty:
            rebuild_engine_flags()      # back to the server's flags
        for key in leaked:
            _apply_value(key, _orig_get_value(key))     # re-run the setter at baseline
        if CLEAR_CACHES:
            _clear_jhora_caches()

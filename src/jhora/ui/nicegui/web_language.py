#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Per-visitor language for PyJHora (public mode only).

jhora.utils.set_language() overwrites about 20 module globals of utils (PLANET_NAMES, RAASI_LIST,
resource_strings, ...). This module loads each language once into a private bundle, without
touching those globals, and makes it visible in two ways:
  - code outside utils that reads utils.PLANET_NAMES etc. gets the current visitor's bundle,
    because the module class of utils is replaced by a language-aware one;
  - code inside utils, and anything running during a calculation, gets it because calc_lock()
    swaps the utils globals to the visitor's bundle (swap_in) and restores them on exit
    (snapshot / restore).
"""
import os
import sys
import types

from jhora import const

_MISSING = object()
_BUNDLES = {}
_NAMES = frozenset()
_STATE = {"server": None, "provider": None, "installed": False}


def _utils():
    """Returns the jhora.utils module (imported on first use)."""
    import jhora.utils as u
    return u


def _parse_list_file(path):
    """Reads a language list file ("name=a,b,c" lines; lines starting with ### are skipped).

    Returns:
        dict mapping each name to the list of its comma-separated values.
    """
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("###") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            out[name.strip()] = value.split(",")
    return out

def _pad_short_lists(bundle, base_bundle):
    """Extends every list in `bundle` that is shorter than the matching list in `base_bundle`,
    appending the base bundle's own trailing values.
    This covers a translation file that predates a later addition to one of the lists it holds
    (e.g. Uranus/Neptune/Pluto entries added to PLANET_NAMES after most language files were
    written): the untranslated values are shown only for the entries missing from the
    translation, instead of the list raising IndexError wherever code indexes past its length.
    """
    if not base_bundle:
        return
    for key, value in list(bundle.items()):
        if key == "resource_strings":
            continue
        base_value = base_bundle.get(key)
        if isinstance(value, list) and isinstance(base_value, list) and len(value) < len(base_value):
            bundle[key] = value + base_value[len(value):]

def get_bundle(lang):
    """Returns the bundle of language-dependent utils globals for `lang` (loaded once and cached), or
    None if its language files are missing.

    Args:
        lang: language name, e.g. 'English' or 'Tamil'.
    """
    global _NAMES
    if lang in _BUNDLES:
        return _BUNDLES[lang]
    u = _utils()
    list_f = const._LANGUAGE_PATH + const._DEFAULT_LANGUAGE_LIST_STR + lang + ".txt"
    msg_f = const._LANGUAGE_PATH + const._DEFAULT_LANGUAGE_MSG_STR + lang + ".txt"
    if not (os.path.exists(list_f) and os.path.exists(msg_f)):
        print(f"[web_language] missing language files for '{lang}'")
        _BUNDLES[lang] = None
        return None
    b = _parse_list_file(list_f)
    b["resource_strings"] = u._read_resource_messages_from_file(msg_f)
    _pad_short_lists(b, _BUNDLES.get(_STATE["server"]))
    u.pad_western_planet_lists(b)
    try:  # derived tables that utils builds once at import
        d = u.__dict__
        b["_main_planets"] = {p: b["PLANET_NAMES"][p] for p in range(12)}
        b["_ascendant"] = {const._ascendant_symbol: b["resource_strings"]["ascendant_str"]}
        b["all_chart_planets"] = (b["_ascendant"] | b["_main_planets"] | d["_drik_upagrahas"]
                                  | d["_chart_upagrahas"] | d["_special_lagnas"] | d["_arudha_lagnas"]
                                  | d["_varnada_lagnas"] | d["_sphutas"] | d["_sahams"])
    except Exception as e:
        print(f"[web_language] derived tables for '{lang}' not built: {e}")
    _BUNDLES[lang] = b
    _NAMES = _NAMES | frozenset(b)
    return b


def _active_language():
    """Returns the current visitor's language if it differs from the server's, otherwise None."""
    prov = _STATE["provider"]
    if prov is None:
        return None
    try:
        lang = prov()
    except Exception:
        return None
    if not lang or lang == _STATE["server"]:
        return None
    return lang


class _LangAwareModule(types.ModuleType):
    def __getattribute__(self, name):
        """Returns the visitor's value for language-dependent names, otherwise the normal module attribute."""
        if name in _NAMES:
            lang = _active_language()
            if lang is not None:
                b = _BUNDLES.get(lang) or get_bundle(lang)
                if b is not None and name in b:
                    return b[name]
        return types.ModuleType.__getattribute__(self, name)


def install(provider):
    """Installs the language-aware utils module class. Does nothing if already installed.
    Args:
        provider: callable returning the current visitor's language name, or None.
    """
    if _STATE["installed"]:
        return
    u = _utils()
    _STATE["server"] = const._DEFAULT_LANGUAGE
    _STATE["provider"] = provider
    b = get_bundle(_STATE["server"])
    if b is not None:
        u.__dict__.update(b)      # the module globals now really hold the server language
    u.__class__ = _LangAwareModule
    _STATE["installed"] = True
    
def snapshot():
    """Returns the current values of all language globals in utils, so that a hidden set_language() call
    during a locked calculation can be undone with restore().
    """
    d = _utils().__dict__
    return {k: d.get(k, _MISSING) for k in _NAMES}


def restore(snap):
    """Puts back the utils language globals saved by snapshot().

    Args:
        snap: dict returned by snapshot().
    """
    d = _utils().__dict__
    for k, v in snap.items():
        if v is _MISSING:
            d.pop(k, None)
        elif d.get(k, _MISSING) is not v:
            d[k] = v


def swap_in(lang):
    """Makes the utils globals (and const._DEFAULT_LANGUAGE) use `lang`. Call only while holding
    calc_lock() and undo with restore(snapshot()).

    Args:
        lang: language name.

    Returns:
        True if the language bundle was found, otherwise False.
    """
    b = get_bundle(lang)
    if b is None:
        return False
    _utils().__dict__.update(b)
    const._DEFAULT_LANGUAGE = lang
    return True

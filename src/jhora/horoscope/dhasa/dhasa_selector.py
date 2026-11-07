#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
jhora.horoscope.dhasa.dhasa_selector

Central, Horoscope-independent home for the lazy-dhasa-tree support
functions. One pair of thin wrapper functions per dhasa, following a
strict naming convention:

    _<dhasa_name>_root_nodes(dob, tob, place, divisional_chart_factor=1,
                              dhasa_method=None, chart_method=1, **kwargs)
        -> [(lords, label, start, end), ...]   MD-level rows only

    _<dhasa_name>_immediate_children(parent_lords, parent_start,
                                      parent_duration=None, parent_end=None,
                                      **kwargs)
        -> [(child_lords, label, start, end), ...]   one level down only

`dhasa_name` is always one of the keys from const.planet_dhasas /
const.rasi_dhasas / const.nakshathra_dhasas / const.karaka_dhasas /
const.special_dhasas.

-----------------------------------------------------------------------------
NO REGISTRY DICT - functions are looked up dynamically by naming convention
-----------------------------------------------------------------------------
get_dhasa_root_nodes()/get_dhasa_children() resolve the right function via
globals().get(f"_{dhasa_name}_root_nodes"/f"_{dhasa_name}_immediate_children")
instead of a separate registry dict. A dhasa with no wrapper pair defined
yet raises a clean AttributeError, caught gracefully by DhasaTreeWidget and
shown as a friendly "<dhasa> dhasa is not available yet" message instead of
crashing.

-----------------------------------------------------------------------------
HAND-WRITTEN wrappers (vimsottari, yogini, yoga_vimsottari, tithi_yogini,
tithi_ashtottari, tara, shodasottari, shattrimsa_sama) vs. GENERIC-ENGINE
wrappers (everything else)
-----------------------------------------------------------------------------
The 8 dhasas above were written and individually debugged/verified one at a
time (each import path, each jd/jd_at_dob quirk, each get_dhasa_antardhasa
return-shape confirmed against real output) - they are left EXACTLY as-is
below, untouched.

Every other dhasa (the remaining ~52 keys across planet_dhasas/rasi_dhasas/
annual dhasas) is wired up via a SHARED generic engine
(_generic_dhasa_root_nodes / _generic_dhasa_immediate_children), built on
top of _import_dhasa_module() (module/import-path resolution, reusing
const.SPECIAL_DASHA_OPTIONS exactly as already used in
dhasa_bhukthi_options_dialog - handles every known module-name mismatch and
default-option override, e.g. satabdika->sataatbika,
pinda_aayu->aayu+aayur_type=PINDA, chathurvidha_*_utthara->
chathurvidha_utthara+dhasa_method=1..4, etc). Each of the ~52 remaining
dhasas then only needs a 2-LINE wrapper pair that calls into this shared
engine with its own dhasa_name string - no hand-written import statement,
no per-dhasa signature guessing.

WHY THIS IS SAFER THAN WRITING ~52 MORE HAND-ROLLED PAIRS: the
tithi_yogini/tithi_ashtottari duplicate-function-name bug earlier this
project was caused by copy-pasting individual wrapper bodies one at a time.
Routing everything through one shared, already-tested engine removes that
entire class of copy-paste risk for the remaining dhasas.

RETURN-SHAPE HANDLING for get_dhasa_antardhasa (root level): confirmed so
far, two conventions exist across modules:
    - vimsottari, yoga_vimsottari: return (something, md_rows) - a 2-tuple
    - yogini, tithi_yogini, tithi_ashtottari, tara, shodasottari,
      shattrimsa_sama: return md_rows directly (a plain list)
_generic_dhasa_root_nodes() below detects this generically: if the raw
return value is a tuple, its 2nd element is taken as md_rows; if it's a
list, it's used directly as md_rows. If some other dhasa returns a
different shape (e.g. a dict, or a 3-tuple), this WILL raise a clear
attribute/index error visible in that dhasa's tree row/console - please
share that dhasa's real get_dhasa_antardhasa return shape and the generic
engine (or that one dhasa specifically) will be adjusted.

get_immediate_children is assumed to always return a plain list of
[lords_tuple, start_tuple, end_tuple] rows directly (no wrapping tuple) -
confirmed true for every dhasa migrated so far.

If ANY of the ~52 generic-engine dhasas below hits an import error, a
signature mismatch, or a return-shape surprise, share the specific error and
that one dhasa's real module - it can be fixed individually (either inside
the shared engine if the fix generalizes, or via a small dhasa-specific
override function if it's truly one-off) without touching anything else.
"""
import inspect
import importlib
from jhora import const, utils
""" 
    drik here is generic model name can be surya_sidhantha or drik depending on value 
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
Date = drik.Date
Place = drik.Place


def _filter_kwargs(target_func, kwargs):
    """
    Keep only the keys that target_func's REAL signature declares, UNLESS
    target_func itself has a **kwargs catch-all (in which case everything is
    passed through as-is). Always inspect the REAL raw-module function being
    called here - never the wrapper around it, since the wrapper always
    declares **kwargs and filtering against it would be a no-op.
    """
    sig = inspect.signature(target_func)
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        return dict(kwargs)
    return {k: v for k, v in kwargs.items() if k in sig.parameters}


def _resolve_jd_kwarg(target_func, jd_value, kwargs):
    """
    Injects jd_value into kwargs under WHICHEVER single name target_func's
    real signature declares - 'jd_at_dob' preferred, 'jd' as fallback - and
    strips any stale/duplicate jd-alias keys already in kwargs first. Never
    injects both. If target_func declares neither name explicitly and has no
    **kwargs catch-all, jd_value is safely omitted rather than guessed.
    """
    call_kwargs = dict(kwargs)
    for name in ('jd_at_dob', 'jd'):
        call_kwargs.pop(name, None)
    if jd_value is None:
        return call_kwargs
    sig = inspect.signature(target_func)
    for name in ('jd_at_dob', 'jd'):
        if name in sig.parameters:
            call_kwargs[name] = jd_value
            return call_kwargs
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        call_kwargs['jd_at_dob'] = jd_value
    return call_kwargs


def _convert_md_rows(md_rows, place, dhasa_name=None):
    """ md_rows: [[lords_tuple, (y,m,d,fh), duration_years], ...] """
    result = []
    for lords, (y, m, d, fh), duration in md_rows:
        start_jd = utils.julian_day_number(Date(y, m, d), (fh, 0, 0))
        end_jd = drik._get_dhasa_end_jd(start_jd, place, total_dasa_years=duration)
        end = utils.jd_to_gregorian(end_jd)
        label = (utils.PLANET_NAMES[lords[-1]] if dhasa_name is None
                 else utils.get_dhasa_lord_resource_name(dhasa_name, lords[-1]))
        result.append((lords, label, (y, m, d, fh), end))
    return result


def _convert_child_rows(_children, dhasa_name=None):
    """ _children: [[lords_tuple, start_tuple, end_tuple], ...] """
    result = []
    for lords, start, end in _children:
        label = (utils.PLANET_NAMES[lords[-1]] if dhasa_name is None
                 else utils.get_dhasa_lord_resource_name(dhasa_name, lords[-1]))
        result.append((lords, label, start, end))
    return result


# =============================================================================
# GENERIC ENGINE - module resolution (mirrors dhasa_bhukthi_options_dialog's
# own _get_import_dhasa_module exactly), plus two shared calling functions
# used by every dhasa below that does NOT have a hand-written wrapper.
# =============================================================================
def _import_dhasa_module(dhasa_name):
    """
    Resolves and imports the raw dhasa module for dhasa_name, using
    const.SPECIAL_DASHA_OPTIONS for any name/domain/defaults override
    (e.g. satabdika -> module 'sataatbika'; pinda_aayu -> module 'aayu'
    with aayur_type=AAYU_TYPE.PINDA baked in as a default), falling back to
    a graha -> direct -> raasi -> annual search order when no preferred
    domain is specified.

    Returns (module, defaults) where defaults is a dict of kwargs that
    should always be applied for this dhasa_name (may be empty).
    """
    entry = const.SPECIAL_DASHA_OPTIONS.get(dhasa_name)
    module_name = entry["module"] if entry else dhasa_name
    defaults = entry.get("defaults", {}) if entry else {}
    preferred = entry.get("domain") if entry else ""
    try_paths = []
    if preferred in ("graha", "raasi", "annual"):
        try_paths.append(f"jhora.horoscope.dhasa.{preferred}.{module_name}")
    else:
        try_paths.extend([f"jhora.horoscope.dhasa.graha.{module_name}",
                          f"jhora.horoscope.dhasa.{module_name}",
                          f"jhora.horoscope.dhasa.raasi.{module_name}",
                          f"jhora.horoscope.dhasa.annual.{module_name}"])
    module = None
    for mp in try_paths:
        try:
            module = importlib.import_module(mp)
            break
        except ImportError:
            continue
    if module is None:
        raise ImportError(f"{module_name} Could not import any of: {', '.join(try_paths)}")
    return module, defaults


def _looks_like_md_rows(x):
    """
    True if x already looks like an md_rows list: [[lords, (y,m,d,fh), duration], ...]
    Used to disambiguate get_dhasa_antardhasa's two observed return
    conventions - see module docstring.
    """
    if isinstance(x, list) and len(x) == 0:
        return True
    if not isinstance(x, (list, tuple)) or len(x) == 0:
        return False
    first = x[0]
    if not isinstance(first, (list, tuple)) or len(first) != 3:
        return False
    lords, date_tuple, duration = first
    return (isinstance(lords, (list, tuple)) and
            isinstance(date_tuple, (list, tuple)) and len(date_tuple) == 4 and
            isinstance(duration, (int, float)))


def _generic_dhasa_root_nodes(dhasa_name, dob, tob, place, divisional_chart_factor=1,
                               dhasa_method=None, chart_method=1, **kwargs):
    """ Shared engine used by every generic-engine dhasa's _<name>_root_nodes wrapper. """
    module, defaults = _import_dhasa_module(dhasa_name)
    func = getattr(module, 'get_dhasa_antardhasa', None)
    if func is None:
        raise AttributeError(f"{module.__name__} has no get_dhasa_antardhasa function")
    call_kwargs = {'divisional_chart_factor': divisional_chart_factor, 'chart_method': chart_method, **kwargs}
    if dhasa_method is not None:
        call_kwargs['dhasa_method'] = dhasa_method
    call_kwargs.update(defaults)  # defaults always win - they define this dhasa's fixed identity
    filtered = _filter_kwargs(func, call_kwargs)
    result = func(dob, tob, place, dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY, **filtered)
    if isinstance(result, tuple):
        md_rows = result[1]
    else:
        md_rows = result
    return _convert_md_rows(md_rows, place, dhasa_name=dhasa_name)


def _generic_dhasa_immediate_children(dhasa_name, parent_lords, parent_start, parent_duration=None,
                                       parent_end=None, jd=None, jd_at_dob=None, **kwargs):
    """ Shared engine used by every generic-engine dhasa's _<name>_immediate_children wrapper. """
    module, defaults = _import_dhasa_module(dhasa_name)
    func = getattr(module, 'get_immediate_children', None)
    if func is None:
        raise AttributeError(f"{module.__name__} has no get_immediate_children function")
    call_kwargs = {**kwargs, **defaults}
    jd_value = jd_at_dob if jd_at_dob is not None else jd
    call_kwargs = _resolve_jd_kwarg(func, jd_value, call_kwargs)
    filtered = _filter_kwargs(func, call_kwargs)
    _children = func(parent_lords=parent_lords, parent_start=parent_start,
                      parent_duration=parent_duration, parent_end=parent_end, **filtered)
    return _convert_child_rows(_children, dhasa_name=dhasa_name)


# =============================================================================
# VIMSOTTARI  (hand-written, verified working end-to-end)
# =============================================================================
def _vimsottari_root_nodes(dob, tob, place, divisional_chart_factor=1,
                            dhasa_method=None, chart_method=1,
                            use_rasi_bhukthi_variation = False,
                            **kwargs):
    from jhora.horoscope.dhasa.graha.vimsottari import get_dhasa_antardhasa
    call_kwargs = {'divisional_chart_factor': divisional_chart_factor,
                   'chart_method': chart_method, **kwargs}
    if dhasa_method is not None:
        call_kwargs['dhasa_method'] = dhasa_method
    filtered = _filter_kwargs(get_dhasa_antardhasa, call_kwargs)
    _, md_rows = get_dhasa_antardhasa(
        dob, tob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        use_rasi_bhukthi_variation=use_rasi_bhukthi_variation,
        **filtered)
    return _convert_md_rows(md_rows, place)

def _vimsottari_immediate_children(parent_lords, parent_start, parent_duration=None,
                                    parent_end=None, jd=None, jd_at_dob=None,
                                     use_rasi_bhukthi_variation=False, **kwargs):
    from jhora.horoscope.dhasa.graha.vimsottari import get_immediate_children
    jd_value = jd_at_dob if jd_at_dob is not None else jd
    call_kwargs = _resolve_jd_kwarg(get_immediate_children, jd_value, kwargs)
    filtered = _filter_kwargs(get_immediate_children, call_kwargs)
    _children = get_immediate_children(
        parent_lords=parent_lords, parent_start=parent_start,
        parent_duration=parent_duration, parent_end=parent_end,
        use_rasi_bhukthi_variation=use_rasi_bhukthi_variation, **filtered)
    return _convert_child_rows(_children)
def _rasi_bhukthi_vimsottari_root_nodes(dob, tob, place, divisional_chart_factor=1,
                                         dhasa_method=None, chart_method=1, **kwargs):
    kwargs.pop('use_rasi_bhukthi_variation', None)
    return _vimsottari_root_nodes(dob, tob, place,
                                   divisional_chart_factor=divisional_chart_factor,
                                   dhasa_method=dhasa_method,
                                   chart_method=chart_method,
                                   use_rasi_bhukthi_variation=True, **kwargs)


def _rasi_bhukthi_vimsottari_immediate_children(parent_lords, parent_start, parent_duration=None,
                                                 parent_end=None, jd=None, jd_at_dob=None, **kwargs):
    kwargs.pop('use_rasi_bhukthi_variation', None)
    return _vimsottari_immediate_children(parent_lords, parent_start,
                                           parent_duration=parent_duration,
                                           parent_end=parent_end,
                                           jd=jd, jd_at_dob=jd_at_dob,
                                           use_rasi_bhukthi_variation=True, **kwargs)
# =============================================================================
# YOGINI  (hand-written, verified working end-to-end)
# =============================================================================
def _yogini_root_nodes(dob, tob, place, divisional_chart_factor=1,
                        dhasa_method=None, chart_method=1, **kwargs):
    from jhora.horoscope.dhasa.graha.yogini import get_dhasa_antardhasa
    call_kwargs = {'divisional_chart_factor': divisional_chart_factor,
                   'chart_method': chart_method, **kwargs}
    if dhasa_method is not None:
        call_kwargs['dhasa_method'] = dhasa_method
    filtered = _filter_kwargs(get_dhasa_antardhasa, call_kwargs)
    md_rows = get_dhasa_antardhasa(
        dob, tob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        **filtered)
    return _convert_md_rows(md_rows, place)


def _yogini_immediate_children(parent_lords, parent_start, parent_duration=None,
                                parent_end=None, jd=None, jd_at_dob=None, **kwargs):
    from jhora.horoscope.dhasa.graha.yogini import get_immediate_children
    jd_value = jd_at_dob if jd_at_dob is not None else jd
    call_kwargs = _resolve_jd_kwarg(get_immediate_children, jd_value, kwargs)
    filtered = _filter_kwargs(get_immediate_children, call_kwargs)
    _children = get_immediate_children(
        parent_lords=parent_lords, parent_start=parent_start,
        parent_duration=parent_duration, parent_end=parent_end, **filtered)
    return _convert_child_rows(_children)


# =============================================================================
# YOGA_VIMSOTTARI  (hand-written)
# =============================================================================
def _yoga_vimsottari_root_nodes(dob, tob, place, divisional_chart_factor=1,
                        dhasa_method=None, chart_method=1, **kwargs):
    from jhora.horoscope.dhasa.graha.yoga_vimsottari import get_dhasa_antardhasa
    call_kwargs = {'divisional_chart_factor': divisional_chart_factor,
                   'chart_method': chart_method, **kwargs}
    if dhasa_method is not None:
        call_kwargs['dhasa_method'] = dhasa_method
    filtered = _filter_kwargs(get_dhasa_antardhasa, call_kwargs)
    _, md_rows = get_dhasa_antardhasa(
        dob, tob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        **filtered)
    return _convert_md_rows(md_rows, place)


def _yoga_vimsottari_immediate_children(parent_lords, parent_start, parent_duration=None,
                                parent_end=None, jd=None, jd_at_dob=None, **kwargs):
    from jhora.horoscope.dhasa.graha.yoga_vimsottari import get_immediate_children
    jd_value = jd_at_dob if jd_at_dob is not None else jd
    call_kwargs = _resolve_jd_kwarg(get_immediate_children, jd_value, kwargs)
    filtered = _filter_kwargs(get_immediate_children, call_kwargs)
    _children = get_immediate_children(
        parent_lords=parent_lords, parent_start=parent_start,
        parent_duration=parent_duration, parent_end=parent_end, **filtered)
    return _convert_child_rows(_children)


# =============================================================================
# TITHI_YOGINI  (hand-written)
# =============================================================================
def _tithi_yogini_root_nodes(dob, tob, place, divisional_chart_factor=1,
                        dhasa_method=None, chart_method=1, **kwargs):
    from jhora.horoscope.dhasa.graha.tithi_yogini import get_dhasa_antardhasa
    call_kwargs = {'divisional_chart_factor': divisional_chart_factor,
                   'chart_method': chart_method, **kwargs}
    if dhasa_method is not None:
        call_kwargs['dhasa_method'] = dhasa_method
    filtered = _filter_kwargs(get_dhasa_antardhasa, call_kwargs)
    md_rows = get_dhasa_antardhasa(
        dob, tob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        **filtered)
    return _convert_md_rows(md_rows, place)


def _tithi_yogini_immediate_children(parent_lords, parent_start, parent_duration=None,
                                parent_end=None, jd=None, jd_at_dob=None, **kwargs):
    from jhora.horoscope.dhasa.graha.tithi_yogini import get_immediate_children
    jd_value = jd_at_dob if jd_at_dob is not None else jd
    call_kwargs = _resolve_jd_kwarg(get_immediate_children, jd_value, kwargs)
    filtered = _filter_kwargs(get_immediate_children, call_kwargs)
    _children = get_immediate_children(
        parent_lords=parent_lords, parent_start=parent_start,
        parent_duration=parent_duration, parent_end=parent_end, **filtered)
    return _convert_child_rows(_children)


# =============================================================================
# TITHI_ASHTOTTARI  (hand-written)
# =============================================================================
def _tithi_ashtottari_root_nodes(dob, tob, place, divisional_chart_factor=1,
                        dhasa_method=None, chart_method=1, **kwargs):
    from jhora.horoscope.dhasa.graha.tithi_ashtottari import get_dhasa_antardhasa
    call_kwargs = {'divisional_chart_factor': divisional_chart_factor,
                   'chart_method': chart_method, **kwargs}
    if dhasa_method is not None:
        call_kwargs['dhasa_method'] = dhasa_method
    filtered = _filter_kwargs(get_dhasa_antardhasa, call_kwargs)
    md_rows = get_dhasa_antardhasa(
        dob, tob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        **filtered)
    return _convert_md_rows(md_rows, place)


def _tithi_ashtottari_immediate_children(parent_lords, parent_start, parent_duration=None,
                                parent_end=None, jd=None, jd_at_dob=None, **kwargs):
    from jhora.horoscope.dhasa.graha.tithi_ashtottari import get_immediate_children
    jd_value = jd_at_dob if jd_at_dob is not None else jd
    call_kwargs = _resolve_jd_kwarg(get_immediate_children, jd_value, kwargs)
    filtered = _filter_kwargs(get_immediate_children, call_kwargs)
    _children = get_immediate_children(
        parent_lords=parent_lords, parent_start=parent_start,
        parent_duration=parent_duration, parent_end=parent_end, **filtered)
    return _convert_child_rows(_children)


# =============================================================================
# TARA  (hand-written)
# =============================================================================
def _tara_root_nodes(dob, tob, place, divisional_chart_factor=1,
                        dhasa_method=None, chart_method=1, **kwargs):
    from jhora.horoscope.dhasa.graha.tara import get_dhasa_antardhasa
    call_kwargs = {'divisional_chart_factor': divisional_chart_factor,
                   'chart_method': chart_method, **kwargs}
    if dhasa_method is not None:
        call_kwargs['dhasa_method'] = dhasa_method
    filtered = _filter_kwargs(get_dhasa_antardhasa, call_kwargs)
    md_rows = get_dhasa_antardhasa(
        dob, tob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        **filtered)
    return _convert_md_rows(md_rows, place, dhasa_name="tara")


def _tara_immediate_children(parent_lords, parent_start, parent_duration=None,
                                parent_end=None, jd=None, jd_at_dob=None, **kwargs):
    from jhora.horoscope.dhasa.graha.tara import get_immediate_children
    jd_value = jd_at_dob if jd_at_dob is not None else jd
    call_kwargs = _resolve_jd_kwarg(get_immediate_children, jd_value, kwargs)
    filtered = _filter_kwargs(get_immediate_children, call_kwargs)
    _children = get_immediate_children(
        parent_lords=parent_lords, parent_start=parent_start,
        parent_duration=parent_duration, parent_end=parent_end, **filtered)
    return _convert_child_rows(_children, dhasa_name="tara")


# =============================================================================
# SHODASOTTARI  (hand-written)
# =============================================================================
def _shodasottari_root_nodes(dob, tob, place, divisional_chart_factor=1,
                        dhasa_method=None, chart_method=1, **kwargs):
    from jhora.horoscope.dhasa.graha.shodasottari import get_dhasa_antardhasa
    call_kwargs = {'divisional_chart_factor': divisional_chart_factor,
                   'chart_method': chart_method, **kwargs}
    if dhasa_method is not None:
        call_kwargs['dhasa_method'] = dhasa_method
    filtered = _filter_kwargs(get_dhasa_antardhasa, call_kwargs)
    md_rows = get_dhasa_antardhasa(
        dob, tob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        **filtered)
    return _convert_md_rows(md_rows, place, dhasa_name="shodasottari")


def _shodasottari_immediate_children(parent_lords, parent_start, parent_duration=None,
                                parent_end=None, jd=None, jd_at_dob=None, **kwargs):
    from jhora.horoscope.dhasa.graha.shodasottari import get_immediate_children
    jd_value = jd_at_dob if jd_at_dob is not None else jd
    call_kwargs = _resolve_jd_kwarg(get_immediate_children, jd_value, kwargs)
    filtered = _filter_kwargs(get_immediate_children, call_kwargs)
    _children = get_immediate_children(
        parent_lords=parent_lords, parent_start=parent_start,
        parent_duration=parent_duration, parent_end=parent_end, **filtered)
    return _convert_child_rows(_children, dhasa_name="shodasottari")


# =============================================================================
# SHATTRIMSA_SAMA  (hand-written)
# =============================================================================
def _shattrimsa_sama_root_nodes(dob, tob, place, divisional_chart_factor=1,
                        dhasa_method=None, chart_method=1, **kwargs):
    from jhora.horoscope.dhasa.graha.shattrimsa_sama import get_dhasa_antardhasa
    call_kwargs = {'divisional_chart_factor': divisional_chart_factor,
                   'chart_method': chart_method, **kwargs}
    if dhasa_method is not None:
        call_kwargs['dhasa_method'] = dhasa_method
    filtered = _filter_kwargs(get_dhasa_antardhasa, call_kwargs)
    md_rows = get_dhasa_antardhasa(
        dob, tob, place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
        **filtered)
    return _convert_md_rows(md_rows, place, dhasa_name="shattrimsa_sama")


def _shattrimsa_sama_immediate_children(parent_lords, parent_start, parent_duration=None,
                                parent_end=None, jd=None, jd_at_dob=None, **kwargs):
    from jhora.horoscope.dhasa.graha.shattrimsa_sama import get_immediate_children
    jd_value = jd_at_dob if jd_at_dob is not None else jd
    call_kwargs = _resolve_jd_kwarg(get_immediate_children, jd_value, kwargs)
    filtered = _filter_kwargs(get_immediate_children, call_kwargs)
    _children = get_immediate_children(
        parent_lords=parent_lords, parent_start=parent_start,
        parent_duration=parent_duration, parent_end=parent_end, **filtered)
    return _convert_child_rows(_children, dhasa_name="shattrimsa_sama")


# =============================================================================
# GENERIC-ENGINE DHASAS - every remaining key from _graha_dhasa_dict,
# _rasi_dhasa_dict and _annual_dhasa_dict. Each pair is a 2-line call into
# the shared engine above - see module docstring for the rationale.
# =============================================================================


def _ashtottari_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('ashtottari', dob, tob, place, **kwargs)
def _ashtottari_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('ashtottari', parent_lords, parent_start, **kwargs)

def _dwadasottari_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('dwadasottari', dob, tob, place, **kwargs)
def _dwadasottari_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('dwadasottari', parent_lords, parent_start, **kwargs)

def _dwisatpathi_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('dwisatpathi', dob, tob, place, **kwargs)
def _dwisatpathi_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('dwisatpathi', parent_lords, parent_start, **kwargs)

def _panchottari_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('panchottari', dob, tob, place, **kwargs)
def _panchottari_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('panchottari', parent_lords, parent_start, **kwargs)

def _satabdika_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('satabdika', dob, tob, place, **kwargs)
def _satabdika_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('satabdika', parent_lords, parent_start, **kwargs)

def _chaturaaseeti_sama_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('chaturaaseeti_sama', dob, tob, place, **kwargs)
def _karana_chaturaaseethi_sama_root_nodes(dob, tob, place, **kwargs):
    rows = _generic_dhasa_root_nodes('karana_chathuraaseethi_sama', dob, tob, place, **kwargs)
    # The generic engine's label lookup used the MODULE spelling ('chathuraaseethi', matching the
    # real file); every other usage site in the app (control bar, option dicts, resource keys) uses
    # the canonical 'karana_chaturaaseethi_sama' (no h) instead - re-label each row with that
    # spelling so utils.get_dhasa_lord_resource_name() can find a match, instead of falling back to "?".
    return [(lords, utils.get_dhasa_lord_resource_name('karana_chaturaaseethi_sama', lords[-1]), start, end)
            for lords, _wrong_label, start, end in rows]
def _karana_chaturaaseethi_sama_immediate_children(parent_lords, parent_start, **kwargs):
    rows = _generic_dhasa_immediate_children('karana_chathuraaseethi_sama', parent_lords, parent_start, **kwargs)
    return [(lords, utils.get_dhasa_lord_resource_name('karana_chaturaaseethi_sama', lords[-1]), start, end)
            for lords, _wrong_label, start, end in rows]

def _karana_chaturaaseethi_sama_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('karana_chathuraaseethi_sama', parent_lords, parent_start, **kwargs)

def _shashtisama_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('shashtisama', dob, tob, place, **kwargs)
def _shashtisama_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('shashtisama', parent_lords, parent_start, **kwargs)

def _naisargika_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('naisargika', dob, tob, place, **kwargs)
def _naisargika_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('naisargika', parent_lords, parent_start, **kwargs)

def _karaka_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('karaka', dob, tob, place, **kwargs)
def _karaka_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('karaka', parent_lords, parent_start, **kwargs)

def _buddhi_gathi_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('buddhi_gathi', dob, tob, place, **kwargs)
def _buddhi_gathi_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('buddhi_gathi', parent_lords, parent_start, **kwargs)

def _kaala_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('kaala', dob, tob, place, **kwargs)
def _kaala_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('kaala', parent_lords, parent_start, **kwargs)

def _aayu_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('aayu', dob, tob, place, **kwargs)
def _aayu_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('aayu', parent_lords, parent_start, **kwargs)

def _saptharishi_nakshathra_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('saptharishi_nakshathra', dob, tob, place, **kwargs)
def _saptharishi_nakshathra_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('saptharishi_nakshathra', parent_lords, parent_start, **kwargs)

def _rashmi_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('rashmi', dob, tob, place, **kwargs)
def _rashmi_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('rashmi', parent_lords, parent_start, **kwargs)

def _ashtaka_varga_planet_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('ashtaka_varga_planet', dob, tob, place, **kwargs)
def _ashtaka_varga_planet_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('ashtaka_varga_planet', parent_lords, parent_start, **kwargs)

def _ashtaka_varga_pinda_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('ashtaka_varga_pinda', dob, tob, place, **kwargs)
def _ashtaka_varga_pinda_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('ashtaka_varga_pinda', parent_lords, parent_start, **kwargs)


# ---- RASI (sign-based) dhasas -----------------------------------------------
def _narayana_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('narayana', dob, tob, place, **kwargs)
def _narayana_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('narayana', parent_lords, parent_start, **kwargs)

def _lagna_kendraadhi_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('lagna_kendraadhi', dob, tob, place, **kwargs)
def _lagna_kendraadhi_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('lagna_kendraadhi', parent_lords, parent_start, **kwargs)

def _sudasa_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('sudasa', dob, tob, place, **kwargs)
def _sudasa_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('sudasa', parent_lords, parent_start, **kwargs)

def _drig_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('drig', dob, tob, place, **kwargs)
def _drig_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('drig', parent_lords, parent_start, **kwargs)

def _nirayana_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('nirayana', dob, tob, place, **kwargs)
def _nirayana_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('nirayana', parent_lords, parent_start, **kwargs)

def _shoola_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('shoola', dob, tob, place, **kwargs)
def _shoola_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('shoola', parent_lords, parent_start, **kwargs)

def _karaka_kendraadhi_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('karaka_kendraadhi', dob, tob, place, **kwargs)
def _karaka_kendraadhi_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('karaka_kendraadhi', parent_lords, parent_start, **kwargs)

def _chara_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('chara', dob, tob, place, **kwargs)
def _chara_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('chara', parent_lords, parent_start, **kwargs)

def _lagnamsaka_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('lagnamsaka', dob, tob, place, **kwargs)
def _lagnamsaka_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('lagnamsaka', parent_lords, parent_start, **kwargs)

def _padhanadhamsa_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('padhanadhamsa', dob, tob, place, **kwargs)
def _padhanadhamsa_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('padhanadhamsa', parent_lords, parent_start, **kwargs)

def _mandooka_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('mandooka', dob, tob, place, **kwargs)
def _mandooka_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('mandooka', parent_lords, parent_start, **kwargs)

def _sthira_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('sthira', dob, tob, place, **kwargs)
def _sthira_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('sthira', parent_lords, parent_start, **kwargs)

def _tara_lagna_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('tara_lagna', dob, tob, place, **kwargs)
def _tara_lagna_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('tara_lagna', parent_lords, parent_start, **kwargs)

def _brahma_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('brahma', dob, tob, place, **kwargs)
def _brahma_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('brahma', parent_lords, parent_start, **kwargs)

def _varnada_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('varnada', dob, tob, place, **kwargs)
def _varnada_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('varnada', parent_lords, parent_start, **kwargs)

def _yogardha_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('yogardha', dob, tob, place, **kwargs)
def _yogardha_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('yogardha', parent_lords, parent_start, **kwargs)

def _navamsa_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('navamsa', dob, tob, place, **kwargs)
def _navamsa_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('navamsa', parent_lords, parent_start, **kwargs)

def _paryaaya_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('paryaaya', dob, tob, place, **kwargs)
def _paryaaya_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('paryaaya', parent_lords, parent_start, **kwargs)

def _trikona_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('trikona', dob, tob, place, **kwargs)
def _trikona_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('trikona', parent_lords, parent_start, **kwargs)

def _kalachakra_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('kalachakra', dob, tob, place, **kwargs)
def _kalachakra_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('kalachakra', parent_lords, parent_start, **kwargs)

def _chakra_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('chakra', dob, tob, place, **kwargs)
def _chakra_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('chakra', parent_lords, parent_start, **kwargs)

def _sandhya_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('sandhya', dob, tob, place, **kwargs)
def _sandhya_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('sandhya', parent_lords, parent_start, **kwargs)

def _pachaka_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('pachaka', dob, tob, place, **kwargs)
def _pachaka_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('pachaka', parent_lords, parent_start, **kwargs)

def _raashiyanka_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('raashiyanka', dob, tob, place, **kwargs)
def _raashiyanka_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('raashiyanka', parent_lords, parent_start, **kwargs)

def _ashtaka_varga_sign_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('ashtaka_varga_sign', dob, tob, place, **kwargs)
def _ashtaka_varga_sign_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('ashtaka_varga_sign', parent_lords, parent_start, **kwargs)

def _chathurvidha_lagna_utthara_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('chathurvidha_lagna_utthara', dob, tob, place, **kwargs)
def _chathurvidha_lagna_utthara_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('chathurvidha_lagna_utthara', parent_lords, parent_start, **kwargs)

def _chathurvidha_kendra_utthara_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('chathurvidha_kendra_utthara', dob, tob, place, **kwargs)
def _chathurvidha_kendra_utthara_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('chathurvidha_kendra_utthara', parent_lords, parent_start, **kwargs)

def _chathurvidha_trikona_utthara_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('chathurvidha_trikona_utthara', dob, tob, place, **kwargs)
def _chathurvidha_trikona_utthara_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('chathurvidha_trikona_utthara', parent_lords, parent_start, **kwargs)

def _chathurvidha_dasha_utthara_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('chathurvidha_dasha_utthara', dob, tob, place, **kwargs)
def _chathurvidha_dasha_utthara_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('chathurvidha_dasha_utthara', parent_lords, parent_start, **kwargs)


# ---- ANNUAL dhasas -----------------------------------------------------------
def _patyayini_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('patyayini', dob, tob, place, **kwargs)
def _patyayini_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('patyayini', parent_lords, parent_start, **kwargs)

def _varsha_vimsottari_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('varsha_vimsottari', dob, tob, place, **kwargs)
def _varsha_vimsottari_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('varsha_vimsottari', parent_lords, parent_start, **kwargs)

def _varsha_narayana_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('varsha_narayana', dob, tob, place, **kwargs)
def _varsha_narayana_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('varsha_narayana', parent_lords, parent_start, **kwargs)

def _sudarsana_chakra_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('sudarsana_chakra', dob, tob, place, **kwargs)
def _sudarsana_chakra_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('sudarsana_chakra', parent_lords, parent_start, **kwargs)

def _panchasvara_root_nodes(dob, tob, place, **kwargs):
    return _generic_dhasa_root_nodes('panchasvara', dob, tob, place, **kwargs)
def _panchasvara_immediate_children(parent_lords, parent_start, **kwargs):
    return _generic_dhasa_immediate_children('panchasvara', parent_lords, parent_start, **kwargs)


# =============================================================================
# GENERIC DISPATCHERS - dhasa-agnostic, call these from the UI. Resolve the
# right wrapper pair purely by naming convention - no registry dict.
# =============================================================================
def get_dhasa_root_nodes(dhasa_type_index, dhasa_name, dob, tob, place,
                          divisional_chart_factor=1, **kwargs):
    """
    Returns MD-level rows for `dhasa_name`: [(lords, label, start, end), ...]
    Raises AttributeError (caught gracefully by DhasaTreeWidget) if
    _<dhasa_name>_root_nodes is not defined yet.
    """
    func = globals().get(f"_{dhasa_name}_root_nodes")
    if not callable(func):
        raise AttributeError(
            f"_{dhasa_name}_root_nodes is not defined in dhasa_selector.py "
            f"(dhasa_name='{dhasa_name}')."
        )
    call_kwargs = {'divisional_chart_factor': divisional_chart_factor, **kwargs}
    filtered = _filter_kwargs(func, call_kwargs)
    return func(dob, tob, place, **filtered)


def get_dhasa_children(dhasa_name, parent_lords, parent_start,
                        parent_duration=None, parent_end=None, **kwargs):
    """
    Returns one level of children below parent_lords for `dhasa_name`:
    [(child_lords, label, start, end), ...]
    Raises AttributeError (caught gracefully by DhasaTreeWidget) if
    _<dhasa_name>_immediate_children is not defined yet.

    NOTE: kwargs here may still contain EITHER 'jd' or 'jd_at_dob' (or both,
    depending on caller). This is intentionally NOT filtered/resolved at this
    outer layer - doing so would require inspecting the WRAPPER's own
    signature (always **kwargs, a no-op) rather than the REAL target
    function, which is exactly the bug that broke yogini earlier. Each
    per-dhasa wrapper above is responsible for resolving/forwarding jd
    correctly via _resolve_jd_kwarg()/_filter_kwargs() against its own real
    target function.
    """
    func = globals().get(f"_{dhasa_name}_immediate_children")
    if not callable(func):
        raise AttributeError(
            f"_{dhasa_name}_immediate_children is not defined in dhasa_selector.py "
            f"(dhasa_name='{dhasa_name}')."
        )
    return func(parent_lords, parent_start, parent_duration=parent_duration,
                parent_end=parent_end, **kwargs)


# =============================================================================
# Introspection helpers - auto-derived, nothing to hand-maintain.
# =============================================================================
def is_dhasa_supported(dhasa_name):
    """ True if both wrapper functions are defined for dhasa_name. """
    return (callable(globals().get(f"_{dhasa_name}_root_nodes")) and
            callable(globals().get(f"_{dhasa_name}_immediate_children")))


def list_supported_dhasas():
    """ All dhasa names (from const's category lists) that are fully wired up so far. """
    all_names = (const.planet_dhasas + const.rasi_dhasas + const.nakshathra_dhasas +
                 const.karaka_dhasas + const.special_dhasas)
    seen = set()
    ordered_unique = [n for n in all_names if not (n in seen or seen.add(n))]
    return [name for name in ordered_unique if is_dhasa_supported(name)]


if __name__ == "__main__":
    from jhora import const

    supported = set(list_supported_dhasas())
    expected = set(const.supported_dhasas)

    missing = sorted(expected - supported)      # in const.supported_dhasas but NOT wired up yet
    extra = sorted(supported - expected)        # wired up but NOT in const.supported_dhasas (unexpected)

    print(f"Wired up ({len(supported)}): {sorted(supported)}")
    print(f"Expected ({len(expected)}): {sorted(expected)}")
    print()
    if missing:
        print(f"MISSING ({len(missing)}) - in const.supported_dhasas but no wrapper pair yet:")
        for name in missing:
            print(f"  - {name}")
    else:
        print("Nothing missing - all of const.supported_dhasas is wired up.")

    if extra:
        print(f"\nEXTRA ({len(extra)}) - wrapper pair exists but NOT in const.supported_dhasas (check spelling/category lists):")
        for name in extra:
            print(f"  - {name}")    
"""
engine.py -- single-app support for both astrology models.

DESIGN PREMISE
--------------
surya_sidhantha.py and drik.py are ~95% signature-compatible. The app should
NOT branch on model at every call site. Instead, one thin adapter normalizes
the handful of real divergences, and the rest passes straight through.

The divergences fall into exactly four categories:

  (A) IDENTICAL          -- same name, same signature, same return shape.
                            ~90% of the API. Pass through untouched via
                            __getattr__. Never enumerate these.

  (B) SIGNATURE ADAPTER  -- same concept, different parameter list.
                            e.g. sidereal_longitude, ascendant, new_moon,
                            full_moon, bhaava_madhya's method kwarg.
                            Fix: explicit method on the adapter.

  (C) RETURN NORMALIZER  -- same concept, different return shape.
                            e.g. sunrise -> bare jd (SS) vs tuple (drik);
                            lunar eclipse -> 3 elems (SS) vs 5 (drik).
                            Fix: adapter returns ONE canonical shape,
                            with absent data as None.

  (D) CAPABILITY GAP     -- genuinely does not exist in one model.
                            e.g. penumbral eclipse phases, global solar
                            eclipse ground track, true-node positions.
                            Fix: declare via .supports(); raise
                            NotSupportedByModel. Do NOT silently fake it.

THE HARD PART IS NOT THE API -- IT IS THE GLOBAL STATE
------------------------------------------------------
drik.set_planet_list(), drik.set_ayanamsa_mode() and
const.astrology_model_default are PROCESS-GLOBAL and MUTUALLY EXCLUSIVE:
SS needs mean nodes, drik needs true nodes. You cannot have both models
live simultaneously in one process. This is the constraint that actually
shapes the architecture -- see the concurrency notes on EngineSession.
"""
from __future__ import annotations

import inspect
import threading
from contextlib import contextmanager

from jhora import const, utils
from jhora.panchanga import drik, surya_sidhantha


class NotSupportedByModel(NotImplementedError):
    """Requested feature has no meaning/implementation in the active model."""


# =====================================================================
# Global-state guard
# =====================================================================
_state_lock = threading.RLock()
_active_engine = None


class _EngineState:
    """
    Applies the process-global configuration one model requires, and
    restores nothing on exit -- because there is no neutral state to
    restore to. Whoever runs next must configure again. The lock makes
    that safe; the _active_engine check makes violations loud.
    """

    def __init__(self, engine):
        self.engine = engine

    def __enter__(self):
        global _active_engine
        _state_lock.acquire()
        self.engine._apply_global_state()
        _active_engine = self.engine.name
        return self.engine

    def __exit__(self, *exc):
        global _active_engine
        _active_engine = None
        _state_lock.release()
        return False


def assert_active(engine_name):
    """Call inside long computations to catch state drift early."""
    if _active_engine != engine_name:
        raise RuntimeError(
            f"{engine_name} calculation running while active engine is "
            f"{_active_engine!r}. Global node/ayanamsa state is wrong -- "
            f"wrap the call in `with get_engine('{engine_name}'):`."
        )


# =====================================================================
# Base adapter
# =====================================================================
class AstroEngine:
    name = None
    module = None
    eclipse_module = None

    #: category (D) -- declared capability flags
    CAPABILITIES = {}

    # -- state -------------------------------------------------------
    def _apply_global_state(self):
        raise NotImplementedError

    def session(self):
        """`with engine.session(): ...` -- serializes + configures."""
        return _EngineState(self)

    def supports(self, feature):
        return self.CAPABILITIES.get(feature, False)

    def require(self, feature):
        if not self.supports(feature):
            raise NotSupportedByModel(
                f"'{feature}' is not available in the {self.name} model."
            )

    # -- (A) passthrough ---------------------------------------------
    def __getattr__(self, item):
        """
        Anything not explicitly overridden goes straight to the backing
        module. This is what keeps the adapter ~200 lines instead of 6000.
        """
        try:
            return getattr(self.module, item)
        except AttributeError:
            raise AttributeError(
                f"{self.name} model exposes no '{item}'"
            ) from None

    def has(self, item):
        """Cheap probe before calling something you're unsure about."""
        return getattr(self.module, item, None) is not None

    # -- (B) signature adapters --------------------------------------
    def sidereal_longitude(self, jd, place, body):
        raise NotImplementedError

    def ascendant(self, jd, place):
        raise NotImplementedError

    def new_moon(self, jd, place, tithi_index, opt=-1):
        raise NotImplementedError

    def full_moon(self, jd, place, tithi_index, opt=-1):
        raise NotImplementedError

    def bhaava_madhya(self, jd, place, method=None):
        """Normalizes the differing method-kwarg name across modules."""
        func = getattr(self.module, 'bhaava_madhya', None)
        if func is None:
            raise NotSupportedByModel(f"{self.name} has no bhaava_madhya")
        if method is None:
            return func(jd, place)
        kw = self._bhava_method_kw(func)
        if kw is None:
            return func(jd, place)
        return func(jd, place, **{kw: method})

    def bhava_methods(self):
        return getattr(self.module, 'SUPPORTED_BHAVA_METHODS', [])

    @staticmethod
    def _bhava_method_kw(func):
        try:
            params = inspect.signature(func).parameters
        except (TypeError, ValueError):
            return None
        if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values()):
            return 'bhava_madhya_method'
        for pname in params:
            if 'method' in pname.lower():
                return pname
        return None

    # -- (C) return normalizers --------------------------------------
    def _rise_set(self, func_name, jd, place):
        raise NotImplementedError

    def sunrise(self, jd, place):
        """-> julian day (float) or None. Canonical shape, both models."""
        return self._rise_set('sunrise', jd, place)

    def sunset(self, jd, place):
        return self._rise_set('sunset', jd, place)

    def moonrise(self, jd, place):
        return self._rise_set('moonrise', jd, place)

    def moonset(self, jd, place):
        return self._rise_set('moonset', jd, place)

    def lunar_eclipse(self, jd, place, search_backward=False):
        """
        Canonical shape for BOTH models -- a dict, never a positional
        tuple, because the element counts differ (3 vs 5):

            {'type': str,
             'penumbra_begin': t|None,   # None in SS (category D)
             'partial_begin':  t|None,
             'max':            t|None,
             'partial_end':    t|None,
             'penumbra_end':   t|None}

        Callers render None as "n/a" and never index by position.
        """
        raise NotImplementedError

    def solar_eclipse(self, jd, place, search_backward=False, local=True):
        """-> {'type': str, 'begin': t, 'max': t, 'end': t}"""
        ecl = self.eclipse_module
        if not local:
            self.require('solar_eclipse_global')
        loc = ecl.EclipseLocation.LOCAL if local else ecl.EclipseLocation.GLOBAL
        res = ecl.next_solar_eclipse(
            jd, place, loc, ecl.SolarEclipseType.ANY,
            search_backward=search_backward)
        if not isinstance(res, tuple):
            return None
        etype, times = res
        return {'type': etype, 'begin': times[0], 'max': times[1], 'end': times[2]}


# =====================================================================
# Surya Siddhanta
# =====================================================================
class SuryaSiddhanthaEngine(AstroEngine):
    name = 'SS'
    module = surya_sidhantha

    CAPABILITIES = {
        'true_nodes': False,          # classical model: mean nodes only
        'ayanamsa': False,            # not required/used
        'penumbral_eclipse': False,
        'solar_eclipse_global': False,
        'eclipse_ground_track': False,
        'annular_hybrid_types': False,
    }

    @property
    def eclipse_module(self):
        from jhora.panchanga import eclipse_ss
        return eclipse_ss

    def _apply_global_state(self):
        const.astrology_model_default = const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=False)   # MEAN

    @property
    def _model_kw(self):
        return {'model': const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA}

    def sidereal_longitude(self, jd, place, body):
        return surya_sidhantha.sidereal_longitude(jd, place, body, **self._model_kw)

    def ascendant(self, jd, place):
        return surya_sidhantha.ascendant(jd, place, **self._model_kw)

    def new_moon(self, jd, place, tithi_index, opt=-1):
        return surya_sidhantha.new_moon(jd, place, tithi_index, opt)

    def full_moon(self, jd, place, tithi_index, opt=-1):
        return surya_sidhantha.full_moon(jd, place, tithi_index, opt)

    def _rise_set(self, func_name, jd, place):
        f = getattr(self.module, func_name, None)
        return None if f is None else f(jd, place)      # bare jd already

    def lunar_eclipse(self, jd, place, search_backward=False):
        ecl = self.eclipse_module
        res = ecl.next_lunar_eclipse(
            jd, place, ecl.EclipseLocation.LOCAL, ecl.LunarEclipseType.ANY,
            search_backward=search_backward)
        if not isinstance(res, tuple):
            return None
        etype, t = res                     # 3 elements
        return {'type': etype,
                'penumbra_begin': None,    # category (D): absent in SS
                'partial_begin': t[0],
                'max': t[1],
                'partial_end': t[2],
                'penumbra_end': None}


# =====================================================================
# Drik
# =====================================================================
class DrikEngine(AstroEngine):
    name = 'DRIK'
    module = drik

    CAPABILITIES = {
        'true_nodes': True,
        'ayanamsa': True,
        'penumbral_eclipse': True,
        'solar_eclipse_global': True,
        'eclipse_ground_track': True,
        'annular_hybrid_types': True,
    }

    ayanamsa_mode = 'LAHIRI'

    @property
    def eclipse_module(self):
        from jhora.panchanga import eclipse
        return eclipse

    def _apply_global_state(self):
        drik_model = getattr(const.ASTROLOGY_MODELS, 'DRIK',
                             getattr(const.ASTROLOGY_MODELS, 'DRIK_GANITHA', None))
        if drik_model is not None:
            const.astrology_model_default = drik_model
        drik.set_ayanamsa_mode(self.ayanamsa_mode)
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=True)    # TRUE

    def sidereal_longitude(self, jd, place, body):
        """Note: drik wants UTC jd -- the adapter hides that conversion."""
        return drik.sidereal_longitude(jd - place.timezone / 24.0, body)

    def ascendant(self, jd, place):
        return drik.ascendant(jd, place)

    def new_moon(self, jd, place, tithi_index, opt=-1):
        return drik.new_moon(jd, tithi_index, opt)     # no `place`

    def full_moon(self, jd, place, tithi_index, opt=-1):
        return drik.full_moon(jd, tithi_index, opt)

    def _rise_set(self, func_name, jd, place):
        f = getattr(self.module, func_name, None)
        if f is None:
            return None
        v = f(jd, place)
        try:
            return v[2]                    # (…, time_str, jd)
        except (TypeError, IndexError):
            return v

    def lunar_eclipse(self, jd, place, search_backward=False):
        ecl = self.eclipse_module
        res = ecl.next_lunar_eclipse(
            jd, place, ecl.EclipseLocation.LOCAL, ecl.LunarEclipseType.ANY,
            search_backward=search_backward)
        if not isinstance(res, tuple):
            return None
        etype, t = res                     # 5 elements
        return {'type': etype,
                'penumbra_begin': t[0],
                'partial_begin': t[1],
                'max': t[2],
                'partial_end': t[3],
                'penumbra_end': t[4]}


# =====================================================================
# Registry
# =====================================================================
_ENGINES = {
    'SS': SuryaSiddhanthaEngine(),
    'DRIK': DrikEngine(),
}


def get_engine(name):
    try:
        return _ENGINES[name.upper()]
    except KeyError:
        raise ValueError(
            f"Unknown model {name!r}; expected one of {sorted(_ENGINES)}"
        ) from None


def available_engines():
    return sorted(_ENGINES)


@contextmanager
def using(name):
    """
    Primary app entry point:

        with using('SS') as eng:
            lon = eng.sidereal_longitude(jd, place, const._SUN)
            rise = eng.sunrise(jd, place)
            t = eng.tithi(jd, place)        # passthrough, category (A)

    Holds the global lock for the duration. Keep blocks SHORT: compute
    everything you need for one model, return plain data, then exit.
    """
    eng = get_engine(name)
    with eng.session():
        yield eng


def compute_both(fn):
    """
    Run the same callable under each model sequentially and return
    {'SS': ..., 'DRIK': ...}. `fn` takes the engine and must return
    plain data -- never a lazy object that calls back into the module
    after the session has closed.
    """
    out = {}
    for name in ('SS', 'DRIK'):
        with using(name) as eng:
            out[name] = fn(eng)
    return out

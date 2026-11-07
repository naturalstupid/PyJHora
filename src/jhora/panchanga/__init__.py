"""
jhora/panchanga/__init__.py

Package initializer for jhora.panchanga.

Purpose
-------
Provide a single, transparent dispatch point ("hora_engine_proxy") so that
every module across the ~90+ files in PyJHora can keep doing:

    from jhora.panchanga import drik

...unchanged, while the actual calculations are routed at call time to
whichever engine is currently active:

    - jhora.panchanga.drik            (default / classic model)
    - jhora.panchanga.surya_sidhantha (const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA
                                        or SURYA_SIDDHANTHA_MODERN_SIGHRA)

No module outside this file needs to know a proxy exists. There is no
separate get_hora_engine() function anywhere else in the codebase --
all of that logic now lives inside _HoraEngineProxy._resolve() below.

IMPORTANT - avoiding a circular import
---------------------------------------
Once this file swaps sys.modules['jhora.panchanga.drik'] to point at the
proxy, ANY later "from jhora.panchanga import drik" (including inside this
proxy's own resolve logic) would just return the proxy itself -- not the
real module -- causing infinite recursion.

To avoid that, we import the two real engine modules ONCE, right here,
BEFORE doing the sys.modules swap, and cache the real module objects in
module-level names (_real_drik / _real_surya_sidhantha). The proxy only
ever dispatches to these cached references, never by re-importing
'jhora.panchanga.drik' by name.

PERFORMANCE NOTE
----------------
Because this proxy is installed package-wide (via the sys.modules swap
below), EVERY module that does `from jhora.panchanga import drik` --
including hot loops in yoga.py (100+ yogas), dhasa/*.py (vimsottari,
ashtottari, narayana, etc.), ashtavarga.py, charts.py, etc. -- would pay
the __getattr__ + _resolve() indirection cost on EVERY single call if we
did nothing further. Previously, only a handful of UI modules opted into
that cost via `drik = utils.hora_engine_proxy`; the ~80+ worker modules
underneath called the real module directly with zero overhead. Swapping
sys.modules made ALL of them pay that tax, which is why UI performance
dropped by a factor of 2-3.

To keep the dynamic-switch capability WITHOUT paying that tax on every
call, resolved attributes are cached directly onto the proxy instance's
__dict__ the first time they're accessed. Python checks instance __dict__
before falling back to __getattr__, so every subsequent access to the same
name (e.g. drik.sunrise) is a plain, fast instance attribute lookup -- no
dispatch overhead, same speed as calling the real module directly.

The cache is only correct as long as it is invalidated whenever the active
model actually changes. That happens rarely (only when the user switches
astrology models), so ALWAYS switch models via set_astrology_model() below
instead of assigning const.astrology_model_default directly anywhere else
in the codebase.
"""
import sys

from jhora import const

# --- Step 1: import the REAL engine modules once, before hijacking
# sys.modules. These are genuine references to drik.py and
# surya_sidhantha.py and are what the proxy will dispatch to.
from jhora.panchanga import drik as _real_drik
from jhora.panchanga import surya_sidhantha as _real_surya_sidhantha


class _HoraEngineProxy:
    """
    Module-like object. Every attribute access (function, constant, etc.)
    is redirected to whichever engine module is "active" right now,
    based on const.astrology_model_default.

    This replaces the old utils.get_hora_engine() function entirely --
    the same resolution logic now lives in _resolve() below, and nothing
    else needs to call it directly.
    """

    def _resolve(self):
        model = const.astrology_model_default
        if model in (const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA,
                     const.ASTROLOGY_MODELS.SURYA_SIDDHANTHA_MODERN_SIGHRA):
            return _real_surya_sidhantha
        return _real_drik

    def __getattr__(self, name):
        # Only invoked when `name` is NOT already in self.__dict__ --
        # i.e. on first access for this name, or right after a cache
        # invalidation triggered by a model switch.
        value = getattr(self._resolve(), name)
        object.__setattr__(self, name, value)  # cache for future lookups
        return value

    def _invalidate_cache(self):
        """Call this whenever the active engine model changes."""
        self.__dict__.clear()


# --- Step 2: create the single shared proxy instance.
hora_engine_proxy = _HoraEngineProxy()


def set_astrology_model(engine_model):
    """
    The ONLY supported way to switch the active panchanga engine.

    Do NOT do `const.astrology_model_default = X` directly anywhere else
    in the codebase -- doing so would leave hora_engine_proxy's cached
    attributes (functions bound from the PREVIOUS engine) stale, silently
    computing results with the wrong model until some uncached name is
    accessed.

    @param engine_model: one of const.ASTROLOGY_MODELS.*
    """
    const.astrology_model_default = engine_model
    hora_engine_proxy._invalidate_cache()


# --- Step 3: install the proxy so every existing
# "from jhora.panchanga import drik" transparently receives it.
#
# - sys.modules['jhora.panchanga.drik'] covers `import jhora.panchanga.drik`
#   (dotted-path imports) and any future first-time import of the submodule.
# - sys.modules[__name__].drik covers `from jhora.panchanga import drik`,
#   since that statement resolves via getattr(package, 'drik') first.
sys.modules['jhora.panchanga.drik'] = hora_engine_proxy
sys.modules[__name__].drik = hora_engine_proxy

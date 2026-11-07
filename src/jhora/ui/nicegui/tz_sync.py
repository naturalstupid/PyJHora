"""Keeps the Time Zone field equal to the place's UTC offset on the entered date, daylight saving included.

components.render_control_bar() calls install(); pages that read the Time Zone field need no code of their own.
The correction follows const.apply_daylight_savings_correction, as the desktop app does.
"""
import asyncio
import contextvars

from nicegui import run

from engine_sync import calc_lock
from jhora import const, utils

DEBOUNCE_S = 0.4
TRIGGER_INPUTS = ('dob_input', 'tob_input', 'lat_input', 'lon_input')
TOLERANCE_H = 0.01
CACHE_LIMIT = 256

_cache = {}


def _to_float(text):
    """Returns `text` as a float, or None when it is not a number."""
    try:
        return float(str(text).strip())
    except (TypeError, ValueError):
        return None


def read_inputs(widgets):
    """Reads the control bar's date, time, latitude and longitude.

    Args:
        widgets: dict returned by components.render_control_bar().

    Returns:
        ((year, month, day), (hour, minute, second), latitude, longitude), or None when a field is missing or invalid.
    """
    try:
        year, month, day = (int(p) for p in widgets['dob_input'].value.strip().split(','))
        parts = [int(p) for p in widgets['tob_input'].value.strip().split(':')]
        tob = tuple((parts + [0, 0])[:3])
    except (KeyError, AttributeError, TypeError, ValueError):
        return None
    lat, lon = _to_float(widgets['lat_input'].value), _to_float(widgets['lon_input'].value)
    if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
        return None
    return (year, month, day), tob, lat, lon


def offset_hours(dob, tob, lat, lon):
    """Returns the UTC offset in hours of (lat, lon) at the local date and time given, or None if it
    could not be determined (e.g. a date far outside the timezone database's supported range, such as
    a proleptic Kali-era date); blocking, results are cached.
    """
    key = (round(lat, 3), round(lon, 3), dob, tob[0])
    if key not in _cache:
        if len(_cache) >= CACHE_LIMIT:
            _cache.clear()
        jd = utils.julian_day_number(utils.hora_engine_proxy.Date(*dob), tob)
        raw = utils.get_place_timezone_offset(lat, lon, jd)
        _cache[key] = float(raw) if raw is not None else None
    return _cache[key]

def correction_enabled():
    """Returns True when the visitor's settings ask for the daylight saving correction."""
    with calc_lock():
        return bool(getattr(const, 'apply_daylight_savings_correction', False))


def _write(widgets, offset):
    """Puts `offset` into the Time Zone field when it differs from what is there."""
    if offset is None:
        return
    field = widgets['tz_input']
    current = _to_float(field.value)
    if current is None or abs(current - offset) > TOLERANCE_H:
        field.value = str(offset)

class TzSync:
    """Recomputes the Time Zone field after the date, time or place change.

    Args:
        widgets: dict returned by components.render_control_bar().
    """

    def __init__(self, widgets):
        self.widgets = widgets
        self.pending = None

    def apply_now(self):
        """Corrects the field immediately (blocking); used once when the page is built."""
        inputs = read_inputs(self.widgets)
        if inputs is not None and correction_enabled():
            _write(self.widgets, offset_hours(*inputs))

    def schedule(self, *_event):
        """Schedules a correction shortly after the last change, replacing one that has not run yet."""
        if self.pending is not None:
            self.pending.cancel()
        self.pending = asyncio.ensure_future(self._run())

    async def _run(self):
        """Waits out the debounce, then computes the offset in a worker thread and writes it."""
        await asyncio.sleep(DEBOUNCE_S)
        inputs = read_inputs(self.widgets)
        if inputs is None or not correction_enabled():
            return
        context = contextvars.copy_context()
        try:
            offset = await run.io_bound(context.run, offset_hours, *inputs)
        except Exception as error:
            print(f'[tz_sync] time zone lookup failed: {type(error).__name__}: {error}')
            return
        if inputs == read_inputs(self.widgets):  # the fields have not changed while it was computed
            _write(self.widgets, offset)


def install(widgets):
    """Corrects the Time Zone field now and whenever the date, time, latitude or longitude change.

    Args:
        widgets: dict returned by components.render_control_bar(); needs the date, time, latitude, longitude and
            time zone inputs. Install before calc_highlight so the first correction does not highlight the button.

    Returns:
        The TzSync, or None when a needed input is missing.
    """
    if any(widgets.get(key) is None for key in TRIGGER_INPUTS + ('tz_input',)):
        return None
    sync = TzSync(widgets)
    try:
        sync.apply_now()
    except Exception as error:
        print(f'[tz_sync] time zone lookup failed: {type(error).__name__}: {error}')
    for key in TRIGGER_INPUTS:
        widgets[key].on_value_change(sync.schedule)
    return sync

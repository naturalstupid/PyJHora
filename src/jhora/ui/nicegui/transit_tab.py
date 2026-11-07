"""Transit page (/transit).
Draws a chart (any divisional chart, any chart style, as on the Kundali page) for a date and time that is
derived from the entered birth details by a "pravesha type":
  present_str                 now, at the entered place
  birth_str                   the entered date and time
  annual_str                  the solar return of year number N (1 = birth year; default: current age + 1,
                              at most const.annual_maximum_age + 1)
  tithi_pravesha_str          the day in a calendar year (default: current year at the place) on which the birth
                              tithi and the birth Tamil solar month recur (vratha.tithi_pravesha)
  prenatal_time_str           the nisheka (prenatal) time, drik._nisheka_time()
  customized_str              the solar return for the given Years, Months and 60 Hrs counts (1 / 1 / 1 is the birth
                              moment itself, as in charts.rasi_chart())
  lunar_month_year_str        an Amantha, Purnimantha or Solar month or year start
  planetary_conjunctions_str  a conjunction (or another separation angle) of two planets
  planet_transit_str          the entry of a planet into a rasi (any rasi, or the chosen one)
  vakra_gathi_change_str      the start or end of the retrograde motion of a planet (Mars to Saturn)
  eclipse_str                 a solar or lunar eclipse; the chart is cast for its first time, as in the desktop dialog
  nakshathra_dhasa_progression_str
                              the natal chart progressed to a chosen date by a star dhasa (see below)
The last five types find an event by searching. The first search starts at the birth moment; the Previous / Next
buttons then step to the event before / after the one shown, counted +1, +2, ... after the birth and -1, -2, ...
before it. Changing the birth details or any option of the search starts again from the birth moment. Selecting any
type calculates it at once with the default options of that type. After that the four types from
planetary_conjunctions_str on (not the lunar month / year type) run again only when Calculate or a Previous / Next
button is pressed, because a search can take seconds; changing the chart style or the varga only redraws the result
shown.
Nakshathra dhasa progression is not a search and has no Previous / Next buttons. The chosen star dhasa, starting
planet and dhasa level give a correction (degrees) from the dhasa running at the "current date" entered; the natal
chart is drawn with that correction added to all longitudes. It is computed when the type is selected (current
date and time = now at the place) and again when Calculate is pressed.
The derived date and time are computed inside calc_lock(), kept on the page only and never stored. The chart
information panel shows the birth details and the derived moment.
Every chart style shows the decorative centre icon (const._IMAGE_ICON_PATH if set, otherwise the temple icon), as the
Kundali page and the desktop app do.
Sudarsana Chakra is drawn as on the Kundali page (three concentric bhava rings - Lagna, Moon and Sun - for one solar
year after the moment the chart is cast for); Western is drawn as a wheel chart (4 concentric circles, 12 house-cusp
spokes, zodiac glyphs in the outer ring - see _render_western() below). The chart menu is not offered for Sudarsana
Chakra or Western, so its combos are hidden while one of them is selected.
Both control rows are one line without a scrollbar: their controls shrink and use a smaller font to fit; they are
fitted by components.render_control_bar() (see row_fit.py).
The chart menu combos beside the chart style (see chart_details.py; the web equivalent of the desktop app's
right-click menu on the chart) describe the chart that is shown: they are built for the moment the chart is cast for
and, for the nakshathra dhasa progression, with its longitude correction. They are emptied when there is no chart
(a search type before its first search).

--- FIX (Western chart ring width) ---
_WESTERN_RING_RADII_PCT was widened from (9, 34, 40, 46) to (9, 28, 44, 49) and the planet-label box width from a
fixed 14% to _WESTERN_LABEL_WIDTH_PCT = 20%, so crowded houses (4+ planets) have more room to wrap onto their own
lines without colliding with the zodiac-glyph ring just outside it. The same change was made in chart_render.py's
copy of this function (used by the Kundali page) so both pages' Western charts match.
"""
import importlib
import math
import re
from datetime import datetime, timedelta, timezone
from nicegui import ui
from jhora import const, utils
from jhora.horoscope import info as horo_info
from jhora.panchanga import vratha, eclipse
drik = utils.hora_engine_proxy
from components import (
    navigation_header, render_control_bar, ensure_default_state,
    calc_lock, res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
    render_footer, run_io_bound_ctx, 
)
from kundali_chart import (
    _CHART_SIZE_PX, _SOUTH_MAP_TO_2D, _SOUTH_IRREGULAR_MAP_TO_2D, _NORTH_LABEL_POSITIONS, _NORTH_BADGE_ANCHORS,
    _EAST_EDGE_CELLS, _EAST_CORNER_CELLS, _RASI_SHORT, _chart_names, _division_chart_factors,
    _varga_label, _chart_style_label, _parse_tob, _planet_label, _cell_text, _planet_text_classes,
    _south_cell_for_rasi, _south_irregular_cell_for_rasi, _NORTH_OVERLAY_POSITIONS, _SC_RING_RADII_PCT,
)
import chart_details  # chart menu combos: web equivalent of the desktop right-click menu on a chart
# Pravesha types offered by this page, in selector order. The first seven are offered only if they are in
# const._PRAVESHA_LIST; the search types and the nakshathra dhasa progression are always offered.
_PRAVESHA_KEYS = ['present_str', 'birth_str', 'annual_str', 'tithi_pravesha_str', 'prenatal_time_str',
                  'customized_str', 'lunar_month_year_str', 'planetary_conjunctions_str', 'planet_transit_str',
                  'vakra_gathi_change_str', 'eclipse_str', 'nakshathra_dhasa_progression_str']
_PRAVESHA_FALLBACK_LABELS = {
    'present_str': 'Present', 'birth_str': 'Birth', 'annual_str': 'Annual', 'tithi_pravesha_str': 'Tithi Pravesha',
    'prenatal_time_str': 'Prenatal Time', 'customized_str': 'Customized', 'lunar_month_year_str': 'Lunar Month / Year',
    'planetary_conjunctions_str': 'Planetary Conjunctions', 'planet_transit_str': 'Planet Transit',
    'vakra_gathi_change_str': 'Vakra Gathi Change', 'eclipse_str': 'Eclipse',
    'nakshathra_dhasa_progression_str': 'Nakshathra Dhasa Progression',
}
# Lunar month / year choice -> (lunar month type: 0 Amantha, 1 Purnimantha, 2 Solar; is_year)
_LUNAR_CHOICES = {
    'amantha_month': (0, False), 'purnimantha_month': (1, False), 'solar_month': (2, False),
    'amantha_year': (0, True), 'purnimantha_year': (1, True), 'solar_year': (2, True),
}
# Types that step with the Previous / Next buttons -> shift (days) of the search start from the event found last,
# so that a search never returns that event again. The vakra gathi and eclipse searches add one day themselves.
_STEP_NUDGE_DAYS = {
    'lunar_month_year_str': 1.0 / 1440.0,
    'planetary_conjunctions_str': 1.0 / 86400.0,
    'planet_transit_str': 1.0 / 86400.0,
    'vakra_gathi_change_str': 0.0,
    'eclipse_str': 0.0,
}
_STEP_KINDS = tuple(_STEP_NUDGE_DAYS)
# Search types: they run only when Calculate or a Previous / Next button is pressed, because a search can take seconds.
_SEARCH_KINDS = tuple(k for k in _STEP_KINDS if k != 'lunar_month_year_str')
_NAK_KEY = 'nakshathra_dhasa_progression_str'
# Star dhasas that provide nakshathra_dhasa_progression() (module names in jhora.horoscope.dhasa.graha).
_ALLOWED_STAR_DHASAS = ['vimsottari', 'yogini', 'ashtottari', 'chaturaaseeti_sama', 'dwadasottari', 'dwisatpathi',
                        'panchottari', 'satabdika', 'shodasottari', 'shastihayani', 'shattrimsa_sama']
_GRAHA_DHASA_PKG = 'jhora.horoscope.dhasa.graha'
# Dhasa levels in selector order; the level index passed to the dhasa module is the selector index + 1.
_DHASA_LEVEL_KEYS = ['maha', 'antara', 'prathyanthara', 'sookshma', 'praana', 'deha']
def _int_or_none(value):
    """Returns int(value), or None if the value is empty."""
    if value is None or value == '':
        return None
    return int(float(value))
def _from_jd(jd):
    """Converts a local Julian day number to ((year, month, day), (hour, minute, second)).
    Args:
        jd: Julian day number (local time).
    """
    jd = round(jd * 86400.0) / 86400.0    # snap to the nearest second so that the seconds never read 60
    y, m, d, fh = utils.jd_to_gregorian(jd)
    seconds = min(int(round(fh * 3600.0)), 86399)
    return (y, m, d), (seconds // 3600, (seconds % 3600) // 60, seconds % 60)
def _from_date_and_hours(date_tuple, fractional_hours):
    """Converts a date and a float hour value (may be negative or above 24) to ((y, m, d), (h, m, s)).
    Args:
        date_tuple: (year, month, day).
        fractional_hours: hours after the start of that date.
    """
    return _from_jd(utils.julian_day_number(drik.Date(*date_tuple), (fractional_hours, 0, 0)))
def _hours_from(value):
    """Returns a time of day as float hours.
    Args:
        value: hours (number), 'H:M:S' text or an (h, m[, s]) sequence.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        parts = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', value)][:3]
    else:
        parts = [float(x) for x in list(value)[:3]]
    parts += [0.0] * (3 - len(parts))
    return parts[0] + parts[1] / 60.0 + parts[2] / 3600.0
def _date_from(value):
    """Returns (year, month, day) from a date given as a sequence of numbers or as 'Y-M-D' / 'Y,M,D' text."""
    if isinstance(value, str):
        return tuple(int(x) for x in re.findall(r'\d+', value)[:3])
    return tuple(int(x) for x in list(value)[:3])
def _planet_arg(index):
    """Returns the planet argument of the drik search functions for a selector index (0 = ascendant, 1.. = planets)."""
    return const._ascendant_symbol if index == 0 else index - 1
def _planet_name(planet):
    """Returns the display name of a planet index, or of the ascendant symbol."""
    if planet == const._ascendant_symbol:
        return res_str('ascendant_str', 'Ascendant')
    return utils.PLANET_NAMES[planet]
def _lunar_start(jd_from, place, lunar_type, is_year, go_next):
    """Returns the ((y, m, d), (h, m, s)) of the previous / next lunar month or year start.
    Args:
        jd_from: Julian day number (local time) the search starts from.
        place: drik.Place of the location.
        lunar_type: 0 Amantha, 1 Purnimantha, 2 Solar.
        is_year: True for the year start, False for the month start.
        go_next: True for the first start after jd_from, False for the last start before it.
    Raises:
        ValueError: if no start was found.
    """
    if is_year:
        func = drik.next_lunar_year if go_next else drik.previous_lunar_year
    else:
        func = drik.next_lunar_month if go_next else drik.previous_lunar_month
    res = func(jd_from, place, lunar_type)
    if res is None:
        raise ValueError('The requested lunar month / year start could not be found.')
    if len(res) == 2:
        date_part, hours = res
        return _from_date_and_hours((date_part[0], date_part[1], date_part[2]), hours)
    return _from_date_and_hours((res[0], res[1], res[2]), res[3])
def _lunar_search(place, lunar_type, is_year, caption):
    """Returns the search function of the Lunar Month / Year type (see _step()).
    Args:
        place: drik.Place of the location.
        lunar_type: 0 Amantha, 1 Purnimantha, 2 Solar.
        is_year: True for year starts, False for month starts.
        caption: caption of the result.
    """
    def search(origin_jd, go_next):
        return _lunar_start(origin_jd, place, lunar_type, is_year, go_next), caption, []
    return search
def _conjunction_search(place, planet1, planet2, separation_index):
    """Returns the search function of the Planetary Conjunctions type (see _step()).
    Args:
        place: drik.Place of the location.
        planet1, planet2: planet indexes or the ascendant symbol.
        separation_index: index of the separation angle; the angle is index * 30 degrees (0 = conjunction).
    """
    def search(origin_jd, go_next):
        ret = drik.next_conjunction_of_planet_pair(origin_jd, place, planet1, planet2,
                                                   direction=1 if go_next else -1,
                                                   separation_angle=separation_index * 30.0)
        if ret is None:
            raise ValueError('No conjunction was found for that separation angle in the search range.')
        jd, long1, long2 = ret
        name1, name2 = _planet_name(planet1), _planet_name(planet2)
        caption = f"{res_str('planetary_conjunctions_str', 'Planetary Conjunctions')}: {name1} / {name2}"
        lines = [f"{res_str('longitude_str', 'Longitude')} {name1}: {utils.to_dms(long1, is_lat_long='plong')}",
                 f"{res_str('longitude_str', 'Longitude')} {name2}: {utils.to_dms(long2, is_lat_long='plong')}"]
        return _from_jd(jd), caption, lines
    return search
def _transit_search(place, planet, raasi):
    """Returns the search function of the Planet Transit type (see _step()).
    Args:
        place: drik.Place of the location.
        planet: planet index or the ascendant symbol.
        raasi: rasi number 1..12 the planet enters, or None for any rasi.
    """
    def search(origin_jd, go_next):
        jd, longitude = drik.next_planet_entry_date(planet, origin_jd, place, direction=1 if go_next else -1,
                                                    raasi=raasi)
        rasi, rasi_long = drik.dasavarga_from_long(longitude, divisional_chart_factor=1)
        name = _planet_name(planet)
        caption = f"{res_str('planet_transit_str', 'Planet Transit')}: {name} \u2192 {utils.RAASI_LIST[rasi]}"
        lines = [f"{res_str('longitude_str', 'Longitude')} {name}: {utils.RAASI_LIST[rasi]} "
                 f"{utils.to_dms(rasi_long, is_lat_long='plong')}"]
        return _from_jd(jd), caption, lines
    return search
def _vakra_search(place, planet):
    """Returns the search function of the Vakra Gathi Change type (see _step()).
    The search starts on the day after (Next) or before (Previous) the date of the origin. The result is marked with
    the retrograde symbol when the planet turns retrograde; no mark means it turns direct.
    Args:
        place: drik.Place of the location.
        planet: planet index (Mars to Saturn).
    """
    def search(origin_jd, go_next):
        direction = 1 if go_next else -1
        y, m, d, _ = utils.jd_to_gregorian(origin_jd + direction)
        jd, ret_sign = drik.next_planet_retrograde_change_date(planet, drik.Date(y, m, d), place, direction=direction)
        mark = '' if ret_sign == 1 else getattr(const, '_retrogade_symbol', 'R')
        name = f"{_planet_name(planet)}{mark}"
        return _from_jd(jd), f"{res_str('vakra_gathi_change_str', 'Vakra Gathi Change')}: {name}", [name]
    return search
def _eclipse_engine_info():
    """Returns (classical, module) for the astrology model in effect: classical is True for the non-Drik models
    (types any / total / partial; Local and Global both offered) and module is the matching eclipse module. Call it inside
    calc_lock(), where const holds the visitor's settings.
    """
    engine = const.astrology_model_default
    classical = engine != const.ASTROLOGY_MODELS.DRIK
    return classical, (utils.get_eclipse_engine(engine) if classical else eclipse)
def _eclipse_type_keys(is_lunar, classical):
    """Returns the eclipse type keys offered: any, total, partial and, for the Drik model, penumbral (lunar) or
    hybrid and annular (solar).
    """
    if classical:
        return ['any', 'total', 'partial']
    return ['any', 'total', 'partial', 'penumbral'] if is_lunar else ['any', 'total', 'partial', 'hybrid', 'annular']
def _eclipse_search(place, is_lunar, type_key, use_global):
    """Returns the search function of the Eclipse type (see _step()).
    The chart is cast for the first valid time of the result (the first contact), as in the desktop dialog. The
    search starts one day after (Next) or before (Previous) the origin.
    Args:
        place: drik.Place of the location.
        is_lunar: True for lunar eclipses, False for solar.
        type_key: 'any', 'total', 'partial', 'penumbral', 'hybrid' or 'annular'.
        use_global: True for a global search (the next eclipse whether or not it is seen at the place), False for a search for
            an eclipse seen at the place.
    """
    classical, module = _eclipse_engine_info()
    location = module.EclipseLocation.GLOBAL if use_global else module.EclipseLocation.LOCAL
    types = module.LunarEclipseType if is_lunar else module.SolarEclipseType
    eclipse_type = int(getattr(types, type_key.upper(), types.ANY))
    find = module.next_lunar_eclipse if is_lunar else module.next_solar_eclipse
    def fmt(entry):
        if entry is None:
            return 'N/A'
        (y, m, d), (h, mi, s) = _from_date_and_hours(tuple(entry[:3]), entry[3])
        return f"{y:04d}-{m:02d}-{d:02d} {h:02d}:{mi:02d}:{s:02d}"
    def search(origin_jd, go_next):
        ret = find(origin_jd + (1 if go_next else -1), place, location, eclipse_type, not go_next,
                   show_maximum_eclipse_global_location=False)
        if ret is None:
            raise ValueError('No eclipse was found in the search range.')
        type_str, entries = ret
        first = next((e for e in entries if e is not None), None)
        if first is None:
            raise ValueError('The eclipse search returned no times.')
        kind_label = (res_str('lunar_str', 'Lunar') if is_lunar else res_str('solar_str', 'Solar')) + ' ' + \
            res_str('eclipse_str', 'Eclipse')
        caption = f"{res_str(type_str + '_str', type_str)} {kind_label}"
        if len(entries) == 3:
            names = ['Begin', 'Maximum', 'End']
        elif len(entries) == 5 and is_lunar and not classical:
            names = ['Penumbral begin', 'Partial begin', 'Maximum', 'Partial end', 'Penumbral end']
        elif len(entries) == 5 and is_lunar:
            names = ['Begin', 'Totality begin', 'Maximum', 'Totality end', 'End']
        else:
            names = [str(i + 1) for i in range(len(entries))]
        lines = [f"{n}: {fmt(e)}" for n, e in zip(names, entries)]
        return _from_date_and_hours(tuple(first[:3]), first[3]), caption, lines
    return search
def _nakshathra_progression(jd_dob, place, jd_current, dhasa_name, planet, level):
    """Returns (correction, running) for a star dhasa progressed to a date.
    Args:
        jd_dob: Julian day number (local time) of the birth moment.
        place: drik.Place of the location.
        jd_current: Julian day number (local time) of the date progressed to.
        dhasa_name: one of _ALLOWED_STAR_DHASAS.
        planet: dhasa starting planet: planet index or the ascendant symbol.
        level: dhasa level index, 1 (maha) to 6 (deha).
    Returns:
        (correction, running): the correction in degrees to add to all planet longitudes, and
        (lords, start, end) of the dhasa running at jd_current at the given level.
    Raises:
        ValueError: if the dhasa is not supported.
    """
    if dhasa_name not in _ALLOWED_STAR_DHASAS:
        raise ValueError(f'Unsupported dhasa: {dhasa_name}')
    module = importlib.import_module(f'{_GRAHA_DHASA_PKG}.{dhasa_name}')
    func = getattr(module, 'nakshathra_dhasa_progression', None)
    if not callable(func):
        raise ValueError(f'{dhasa_name} does not provide a nakshathra dhasa progression.')
    return func(jd_dob, place, jd_current, dhasa_starting_planet=planet, dhasa_level_index=level)
def _nak_period_text(moment_tuple):
    """Returns 'YYYY-MM-DD HH:MM:SS' for a (year, month, day, fractional_hours) tuple."""
    (y, m, d), (h, mi, s) = _from_date_and_hours(tuple(moment_tuple[:3]), moment_tuple[3])
    return f"{y:04d}-{m:02d}-{d:02d} {h:02d}:{mi:02d}:{s:02d}"
def _nak_report(dob, tob, place, nak_opts):
    """Returns (moment, caption, lines, correction) for the nakshathra dhasa progression. Call it inside calc_lock().
    Args:
        dob: birth date (year, month, day).
        tob: birth time (hour, minute, second).
        place: drik.Place of the location.
        nak_opts: (dhasa index, planet index, level index, date text, time text, show all levels). The planet index
            is 0 for the ascendant and 1.. for the planets; the level index is 0 (maha) to 5 (deha); the date is
            'Y,M,D' and the time 'H:M:S': the "current date" the dhasa is progressed to.
    Returns:
        moment: ((year, month, day), (hour, minute, second)) of the date progressed to.
        caption: caption of the chart.
        lines: report lines: the dhasa name; the running dhasa lords of each level up to the selected one with the
            start and end of the running period (with "show all levels": one line per level, the lord of that
            level and its period); and the correction.
        correction: degrees to add to all planet longitudes (the value of the selected level).
    Raises:
        ValueError: if the date is missing or invalid.
    """
    dhasa_index, planet_index, level_index, date_text, time_text, show_all = nak_opts
    if not date_text or not str(date_text).strip():
        raise ValueError('Enter the date to progress to (Y,M,D).')
    cur_date = _date_from(date_text)
    if len(cur_date) != 3:
        raise ValueError('The date to progress to must be Y,M,D.')
    hours = _hours_from(time_text) if time_text and str(time_text).strip() else 0.0
    jd_current = utils.julian_day_number(drik.Date(*cur_date), (hours, 0, 0))
    jd_dob = utils.julian_day_number(dob, tob)
    dhasa_name = _ALLOWED_STAR_DHASAS[dhasa_index]
    planet = _planet_arg(planet_index)
    level = level_index + 1
    level_names = [res_str(k + '_str', k.title()) for k in _DHASA_LEVEL_KEYS]
    levels = range(1, len(_DHASA_LEVEL_KEYS) + 1) if show_all else [level]
    rows = []
    correction = 0.0
    for lv in levels:
        corr, running = _nakshathra_progression(jd_dob, place, jd_current, dhasa_name, planet, lv)
        if lv == level:
            correction = corr
        rows.append((lv, running))
    dhasa_label = res_str(dhasa_name + '_str', dhasa_name.replace('_', ' ').title())
    starts_at, ends_at = res_str('starts_at_str', 'Starts At'), res_str('ends_at_str', 'Ends At')
    lines = [f"<b>{dhasa_label} {res_str('dhasa_str', 'Dhasa')}</b>"]
    for lv, (lords, start, end) in rows:
        if not isinstance(lords, (tuple, list)):
            lords = [lords]
        lords = list(lords)[:lv]
        if show_all:
            lord = _planet_name(lords[lv - 1]) if len(lords) >= lv else '/'.join(_planet_name(p) for p in lords)
            lines.append(f"{level_names[lv - 1]}: {lord} ({_nak_period_text(start)} - {_nak_period_text(end)})")
        else:
            lines.append(', '.join(f"{level_names[i]}: {_planet_name(p)}" for i, p in enumerate(lords)))
            lines.append(f"{starts_at}: {_nak_period_text(start)}")
            lines.append(f"{ends_at}: {_nak_period_text(end)}")
    lines.append(f"{res_str('dhasa_progression_correction_str', 'Dhasa Progression Correction')}: "
                 f"{utils.to_dms(correction, is_lat_long='plong')}")
    caption = (f"{res_str(_NAK_KEY, 'Nakshathra Dhasa Progression')}: {dhasa_label} "
               f"({_planet_name(planet)})")
    return _from_jd(jd_current), caption, lines, correction
def _make_search(kind, place, opts):
    """Returns (search, signature, nudge_days) for a step type.
    Args:
        kind: one of _STEP_KINDS.
        place: drik.Place of the location.
        opts: selector values: 'lunar' (lunar_type, is_year), 'lunar_label', 'conj' (planet1, planet2, separation
            index), 'transit' (planet, rasi), 'vakra' (planet), 'eclipse' (kind, type key, location key).
    Raises:
        ValueError: if a required selection is missing.
    """
    nudge = _STEP_NUDGE_DAYS[kind]
    if kind == 'lunar_month_year_str':
        lunar_type, is_year = opts['lunar']
        return _lunar_search(place, lunar_type, is_year, opts['lunar_label']), ('lunar', lunar_type, is_year), nudge
    if kind == 'planetary_conjunctions_str':
        p1, p2, sep = opts['conj']
        if p1 is None or p2 is None or sep is None:
            raise ValueError('Select both planets and the separation angle.')
        return _conjunction_search(place, _planet_arg(p1), _planet_arg(p2), sep), ('conj', p1, p2, sep), nudge
    if kind == 'planet_transit_str':
        p, r = opts['transit']
        if p is None:
            raise ValueError('Select a planet.')
        raasi = None if r in (None, 0) else r
        return _transit_search(place, _planet_arg(p), raasi), ('transit', p, raasi), nudge
    if kind == 'vakra_gathi_change_str':
        if opts['vakra'] is None:
            raise ValueError('Select a planet.')
        return _vakra_search(place, opts['vakra']), ('vakra', opts['vakra']), nudge
    if kind == 'eclipse_str':
        e_kind, e_type, e_loc = opts['eclipse']
        return (_eclipse_search(place, e_kind == 'lunar', e_type, e_loc == 'global'),
                ('eclipse', e_kind, e_type, e_loc), nudge)
    raise ValueError(f'Unsupported pravesha type: {kind}')
def _step(step_state, signature, jd_birth, direction, nudge_days, search, first_search=True):
    """Returns (moment, caption, lines, n) for the current step of a step type.
    Call it inside calc_lock(). The first search starts at the birth moment; each later search starts at the event
    found last, moved by `nudge_days` in the stepping direction. n counts the events after the birth as +1, +2, ...
    and the events before it as -1, -2, ... (there is no 0).
    Args:
        step_state: dict kept by the page (empty at first); holds the last signature and result.
        signature: tuple of every input the result depends on; when it differs from the stored one, the stepping
            starts again from the birth moment.
        jd_birth: Julian day number of the birth moment.
        direction: 'next' or 'previous' to step; None to show the current step unchanged (on a first or restarted
            call, None means 'next' from the birth moment).
        nudge_days: shift of the search start from the event found last.
        search: function (origin_jd, go_next) -> (moment, caption, lines) that finds the event.
        first_search: False to return None, instead of searching, when there is no stored result for `signature`
            and direction is None.
    Raises:
        ValueError: if the search finds nothing.
    """
    same = step_state.get('signature') == signature
    if direction is None and same:
        return step_state['result']
    if direction is None and not first_search:
        return None
    if same:
        go_next = (direction == 'next')
        origin = step_state['jd'] + (nudge_days if go_next else -nudge_days)
        n = step_state['n'] + (1 if go_next else -1)
        if n == 0:
            n = 1 if go_next else -1
    else:
        step_state.clear()
        go_next = (direction != 'previous')
        origin = jd_birth
        n = 1 if go_next else -1
    moment, caption, lines = search(origin, go_next)
    result = (moment, caption, lines, n)
    step_state.update(signature=signature, result=result, n=n, jd=utils.julian_day_number(moment[0], moment[1]))
    return result
def _derive_chart_moment(kind, dob, tob, place, years, months, sixty_hours, tithi_year):
    """Returns the ((year, month, day), (hour, minute, second)) at which the chart is cast, for the types that
    need no search (the step types are handled by _step()). Call it inside calc_lock().
    Args:
        kind: pravesha type key (see _PRAVESHA_KEYS).
        dob: birth date (year, month, day).
        tob: birth time (hour, minute, second).
        place: drik.Place of the location.
        years: annual: year number (None = current age + 1); customized: Years count (None = 1).
        months, sixty_hours: customized: Months and 60 Hrs counts (None = 1).
        tithi_year: tithi pravesha: calendar year (None = current year at the place).
    Raises:
        ValueError: if the pravesha type is unknown or no matching date is found.
    """
    if kind == 'birth_str':
        return tuple(dob), tuple(tob)
    if kind == 'present_str':
        now = datetime.now(timezone(timedelta(hours=place.timezone)))
        return (now.year, now.month, now.day), (now.hour, now.minute, now.second)
    jd_dob = utils.julian_day_number(dob, tob)
    if kind == 'annual_str':
        if years is None:
            years = min(datetime.now().year - dob[0], const.annual_maximum_age) + 1
        years, months, sixty_hours = max(1, years), 1, 1
    elif kind == 'customized_str':
        years, months, sixty_hours = years or 1, months or 1, sixty_hours or 1
    if kind in ('annual_str', 'customized_str'):
        if years == 1 and months == 1 and sixty_hours == 1:
            return tuple(dob), tuple(tob)       # charts.rasi_chart() uses the birth moment itself for 1 / 1 / 1
        return _from_jd(drik.next_solar_date(jd_dob, place, years, months, sixty_hours))
    if kind == 'prenatal_time_str':
        return _from_jd(drik._nisheka_time(jd_dob, place))
    if kind == 'tithi_pravesha_str':
        if tithi_year is None:
            tithi_year = datetime.now(timezone(timedelta(hours=place.timezone))).year
        tp = vratha.tithi_pravesha(drik.Date(*dob), tuple(tob), place, tithi_year)
        if not tp:
            raise ValueError('No tithi pravesha was found for that year.')
        return _from_date_and_hours(_date_from(tp[0][0]), _hours_from(tp[0][1]))
    raise ValueError(f'Unsupported pravesha type: {kind}')
def _method_count_and_default_mod(varga_idx):
    """Module-level copy of transit_page()'s _method_count_and_default(), usable from _transit_locked()
    (which runs in a worker thread and has no closure access to the page's nested helpers). See that
    closure's docstring for details; the logic is identical.
    """
    if varga_idx == 0:
        return 1, 1
    varga_factor = _division_chart_factors[varga_idx]
    try:
        method_count, default_method, _base_rasi_idx, _count_from_end = utils.get_varga_option_dict()[varga_factor]
    except (KeyError, TypeError, ValueError) as e:
        print(f"[transit_page] get_varga_option_dict() lookup/unpack failed for varga_factor={varga_factor} (varga_idx={varga_idx}): {e}")
        return 1, 1
    if method_count is None:
        return 1, 1
    return method_count, (default_method if default_method is not None else 1)
def _transit_locked(dob, tob, place_val, lat_val, lon_val, tz_val, kind, opts, varga_idx, dcf,
                     direction, auto, step_state, nak_state, moment_cache, years, months, sixty_hours, tithi_year,
                     chart_options_state, chart_style=None):
    """Derives the chart moment and computes the chart under calc_lock().
    This is the slow part of compute_transit(); pulled out to a plain, blocking function so it can run
    in a worker thread via components.DelayedBusyIndicator.run(); a non-intrusive "please wait" message
    then appears only if this turns out to take more than a moment. step_state, nak_state and
    moment_cache are the page's own dicts, mutated in place exactly as before (passing a dict to a
    worker thread and back is safe here because only one computation - whichever holds calc_lock() -
    touches them at a time, same as when this ran directly on the event loop).
    Returns:
        (moment, caption, extra_lines, step_n, cast_moment, correction, horo, chart_1d, asc_house,
        chart_info, chart_method, sc_rings). moment is None if no event was found or shown (not an error) - the
        caller should then show the search/progression hint instead of drawing a chart. chart_method is the
        (1-based) calculation method the chart was drawn with, which the chart menu must use too. sc_rings is the
        Sudarsana Chakra data ([lagna, moon, sun rings, retrograde planets]) when chart_style is Sudarsana Chakra,
        otherwise None; it is computed here, with the rest of the chart, so that it also runs in the worker thread.
    """
    moment = None
    cast_moment = None      # the moment the chart is cast for, when it differs from `moment`
    correction = 0.0        # dhasa progression correction added to all longitudes
    caption = None
    extra_lines = []
    step_n = None
    horo = chart_1d = asc_house = chart_info = sc_rings = None
    with calc_lock():
        _, default_method = _method_count_and_default_mod(varga_idx)
        chart_method = chart_options_state.get(varga_idx, default_method)
        if kind in _STEP_KINDS:
            place_obj = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
            search, signature, nudge = _make_search(kind, place_obj, opts)
            result = _step(step_state, (dob, tob, lat_val, lon_val, tz_val, signature),
                           utils.julian_day_number(dob, tob), direction, nudge, search,
                           first_search=(not auto) or kind not in _SEARCH_KINDS)
            if result is not None:
                moment, caption, extra_lines, step_n = result
        elif kind == _NAK_KEY:
            signature = (dob, tob, lat_val, lon_val, tz_val, opts['nak'])
            if nak_state.get('signature') != signature and not auto:
                place_obj = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
                nak_state.clear()
                nak_state.update(signature=signature, result=_nak_report(dob, tob, place_obj, opts['nak']))
            if nak_state.get('signature') == signature:
                moment, caption, extra_lines, correction = nak_state['result']
                cast_moment = (dob, tob)
        else:
            cache_key = (kind, dob, tob, lat_val, lon_val, tz_val, years, months, sixty_hours, tithi_year)
            moment = moment_cache.get(cache_key) if kind != 'present_str' else None
            if moment is None:
                place_obj = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
                moment = _derive_chart_moment(kind, dob, tob, place_obj, years, months, sixty_hours,
                                              tithi_year)
                if kind != 'present_str':
                    moment_cache[cache_key] = moment
        if moment is not None:
            chart_date, chart_time = cast_moment or moment
            horo = horo_info.Horoscope(
                latitude=lat_val, longitude=lon_val, timezone_offset=tz_val,
                date_in=drik.Date(*chart_date),
                birth_time=f"{chart_time[0]:02d}:{chart_time[1]:02d}:{chart_time[2]:02d}",
                calculation_type='drik', language=const._DEFAULT_LANGUAGE,
            )
            chart_info, chart_cells, asc_house = horo.get_horoscope_information_for_chart(
                chart_index=varga_idx, chart_method=chart_method, divisional_chart_factor=dcf,
                dhasa_progression_correction=correction,
            )
            # Remove trailing '/' separators only; they are never part of a planet token.
            chart_1d = [x.rstrip('/') for x in chart_cells]
            if chart_style == const.CHART_STYLE.SUDARSANA_CHAKRA:
                # Lagna, Moon and Sun concentric bhava rings, one solar year after the moment the chart is cast for
                # (the same call and arguments as the Kundali page); see jhora.horoscope.dhasa.sudharsana_chakra.
                from jhora.horoscope.dhasa import sudharsana_chakra
                place_obj = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
                jd_chart = utils.julian_day_number(drik.Date(*chart_date), chart_time)
                sc_rings = sudharsana_chakra.sudharshana_chakra_chart(
                    jd_chart, place_obj, chart_date, years_from_dob=1,
                    divisional_chart_factor=dcf, chart_method=chart_method,
                )
    return (moment, caption, extra_lines, step_n, cast_moment, correction, horo, chart_1d, asc_house, chart_info,
            chart_method, sc_rings)
@ui.page('/transit')
def transit_page():
    """Transit page: control bar, pravesha type and its inputs, chart style / varga selectors, chart information
    and the chart cast for the derived date and time.
    """
    navigation_header()
    state = ensure_default_state()
    # "overlay": 12-list (indexed by absolute rasi) that a chart menu item writes into the chart cells, or None.
    # "render": (chart_style, chart_1d, asc_house, sc_rings) of the displayed chart, so it can be redrawn without
    # recomputing (sc_rings is None unless the style is Sudarsana Chakra).
    # "detail_ctx": what the chart menu needs (see chart_details.make_context()).
    # "prasna": absolute rasi of a Prasna Lagna that replaces the ascendant (see chart_details.chart_with_prasna()), or
    # None. The real chart stays in "render"; the replaced one is derived when it is drawn.
    transit_state = {"horo": None, "overlay": None, "render": None, "detail_ctx": None, "prasna": None}
    def _place_center_icon():
        """Draws the decorative centre icon of a chart (South Indian's unused 2x2 centre cell): the configured image
        (const._IMAGE_ICON_PATH) if the setting is present, otherwise a generic temple icon. Call it inside a
        container that already centres its content. Same as the Kundali page.
        """
        icon_path = getattr(const, '_IMAGE_ICON_PATH', None)
        if icon_path:
            ui.image(icon_path).classes('w-16 h-16 object-contain')
        else:
            ui.icon('temple_hindu', size='2rem').classes('text-amber-700')
    def _place_center_icon_absolute(left_pct, top_pct, size_pct):
        """Draws the decorative centre icon at an absolute position, for the North and East Indian charts, whose unused
        centre is not a single grid cell. Same as the Kundali page.
        Args:
            left_pct, top_pct: left / top position of the icon box, in % of the chart size.
            size_pct: width and height of the icon box, in % of the chart size (the icon itself is scaled to fit
                inside it, preserving its aspect ratio).
        """
        icon_path = getattr(const, '_IMAGE_ICON_PATH', None)
        with ui.element('div').style(
            f'position:absolute; left:{left_pct}%; top:{top_pct}%; width:{size_pct}%; height:{size_pct}%; '
            'display:flex; align-items:center; justify-content:center;'
        ):
            if icon_path:
                ui.image(icon_path).classes('w-full h-full object-contain')
            else:
                ui.icon('temple_hindu', size='2rem').classes('text-amber-700')
    def _overlay_at(rasi_idx):
        """Returns the chart menu overlay text of an absolute rasi index, or '' (none shown / no such rasi)."""
        overlay = transit_state.get("overlay")
        if not overlay or rasi_idx is None:
            return ''
        return overlay[rasi_idx]
    moment_cache = {}   # inputs -> derived moment, for this page only (cleared when the settings change)
    step_state = {}     # stepping state of the step types (see _step()); this page only
    nak_state = {}      # last nakshathra dhasa progression result and the inputs it belongs to; this page only
    _pravesha_options = {k: res_str(k, _PRAVESHA_FALLBACK_LABELS[k]) for k in _PRAVESHA_KEYS
                         if k in _SEARCH_KINDS or k == _NAK_KEY or k in const._PRAVESHA_LIST}
    if not _pravesha_options:
        _pravesha_options = {'birth_str': res_str('birth_str', 'Birth')}
    _default_pravesha = 'present_str' if 'present_str' in _pravesha_options else next(iter(_pravesha_options))
    _month_str = res_str('month_str', 'Month')
    _year_str = res_str('year_str', 'Year')
    _lunar_options = {
        'amantha_month': res_str('amantha_str', 'Amantha') + ' ' + _month_str,
        'purnimantha_month': res_str('purnimantha_str', 'Purnimantha') + ' ' + _month_str,
        'solar_month': res_str('solar_str', 'Solar') + ' ' + _month_str,
        'amantha_year': res_str('amantha_str', 'Amantha') + ' ' + _year_str,
        'purnimantha_year': res_str('purnimantha_str', 'Purnimantha') + ' ' + _year_str,
        'solar_year': res_str('solar_str', 'Solar') + ' ' + _year_str,
    }
    _planet_options = {0: res_str('ascendant_str', 'Ascendant')}
    _planet_options.update({i + 1: utils.PLANET_NAMES[i] for i in range(9)})
    _sep_labels = res_str('planet_separation_angle_list', ','.join(str(a) for a in range(0, 360, 30))).split(',')
    _sep_options = {i: s for i, s in enumerate(_sep_labels)}
    _raasi_options = {0: res_str('raasi_str', 'Raasi')}
    _raasi_options.update({i + 1: utils.RAASI_LIST[i] for i in range(12)})
    _star_dhasa_options = {i: res_str(d + '_str', d.replace('_', ' ').title()) for i, d in enumerate(_ALLOWED_STAR_DHASAS)}
    _level_options = {i: res_str(k + '_str', k.title()) for i, k in enumerate(_DHASA_LEVEL_KEYS)}
    _eclipse_label = res_str('eclipse_str', 'Eclipse')
    _eclipse_kind_options = {'solar': res_str('solar_str', 'Solar') + ' ' + _eclipse_label,
                            'lunar': res_str('lunar_str', 'Lunar') + ' ' + _eclipse_label}
    with calc_lock():   # the astrology model and node mode in effect decide what each combo offers
        _eclipse_classical, _ = _eclipse_engine_info()
        _eclipse_loc_default = 'local' if getattr(const, 'eclipse_default_local_search', False) else 'global'
        _vakra_rahu_ketu_supported = (const.astrology_model_default == const.ASTROLOGY_MODELS.DRIK
                                    and const._use_true_nodes_for_rahu_ketu)
    _vakra_last_id = const.KETU_ID if _vakra_rahu_ketu_supported else const.SATURN_ID
    _vakra_options = {i: utils.PLANET_NAMES[i] for i in range(const.MARS_ID, _vakra_last_id + 1)}
    def _eclipse_type_options(is_lunar):
        return {k: res_str(k + '_str', k.title()) for k in _eclipse_type_keys(is_lunar, _eclipse_classical)}
    _chart_style_options = {i: _chart_style_label(s) for i, s in enumerate(const.AVAILABLE_CHART_STYLES.keys())}
    _chart_style_keys = list(const.AVAILABLE_CHART_STYLES.keys())
    _varga_options = {i: _varga_label(i) for i in range(len(_division_chart_factors))}
    # Chart method (1-based) chosen in the Chart Options dialog, per varga index.
    chart_options_state = {}
    saved_style_index = state.get('kundali_chart_style_index', 0)
    try:
        saved_style_index = int(saved_style_index)
        if saved_style_index not in range(len(const.AVAILABLE_CHART_STYLES)):
            saved_style_index = 0
    except Exception:
        saved_style_index = 0
    with ui.column().classes('w-full p-2 gap-1'):
        ui.label(res_str('transit_str','Transit')).classes('text-xl font-bold text-green-700')
        async def _on_options_saved():
            moment_cache.clear(); step_state.clear(); nak_state.clear()
            await compute_transit(auto=True)
        w = render_control_bar(show_dob_tob=True,
                                on_options_saved=_on_options_saved,
                                on_calculate=lambda: compute_transit())
        # Both control rows are one line without a scrollbar: render_control_bar() fits them (see row_fit.py).
        _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
        with w['row2']:
            pravesha_select = ui.select(options=_pravesha_options, value=_default_pravesha,
                                        label='Pravesha').props('outlined dense').classes('w-48 shrink-0')
            years_input = ui.number(res_str('years_str', 'Years'), value=None, min=1, max=300,
                                    format='%.0f').props('outlined dense').classes('w-24 shrink-0')
            months_input = ui.number(res_str('months_str', 'Months'), value=1, min=1, max=12,
                                     format='%.0f').props('outlined dense').classes('w-24 shrink-0')
            sixty_input = ui.number(res_str('60hrs_str', '60 Hrs'), value=1, min=1, max=12,
                                    format='%.0f').props('outlined dense').classes('w-24 shrink-0')
            tithi_year_input = ui.number(_year_str, value=None, format='%.0f') \
                .props('outlined dense').classes('w-28 shrink-0')
            lunar_type_select = ui.select(options=_lunar_options, value='amantha_month',
                                          label=res_str('lunar_month_year_str', 'Lunar Month / Year')) \
                .props('outlined dense').classes('w-48 shrink-0')
            conj_sep_select = ui.select(options=_sep_options, value=0,
                                        label=res_str('separation_angle_str', 'Separation')) \
                .props('outlined dense').classes('w-32 shrink-0')
            conj_p1_select = ui.select(options=_planet_options, value=const.SATURN_ID + 1,
                                       label=res_str('planet_str', 'Planet') + ' 1') \
                .props('outlined dense').classes('w-36 shrink-0')
            conj_p2_select = ui.select(options=_planet_options, value=const.JUPITER_ID + 1,
                                       label=res_str('planet_str', 'Planet') + ' 2') \
                .props('outlined dense').classes('w-36 shrink-0')
            transit_p_select = ui.select(options=_planet_options, value=const.SATURN_ID + 1,
                                         label=res_str('planet_str', 'Planet')) \
                .props('outlined dense').classes('w-36 shrink-0')
            transit_raasi_select = ui.select(options=_raasi_options, value=0,
                                             label=res_str('raasi_str', 'Raasi')) \
                .props('outlined dense').classes('w-36 shrink-0')
            vakra_p_select = ui.select(options=_vakra_options, value=const.SATURN_ID,
                                       label=res_str('planet_str', 'Planet')) \
                .props('outlined dense').classes('w-36 shrink-0')
            ecl_kind_select = ui.select(options=_eclipse_kind_options, value='solar',
                                        label=_eclipse_label).props('outlined dense').classes('w-44 shrink-0')
            ecl_type_select = ui.select(options=_eclipse_type_options(False), value='any',
                                        label=res_str('type_str', 'Type')) \
                .props('outlined dense').classes('w-32 shrink-0')
            ecl_loc_select = ui.select(options={'global': res_str('global_str', 'Global'),
                                                'local': res_str('local_str', 'Local')},
                                       value=_eclipse_loc_default,
                                       label=res_str('location_str', 'Location')) \
                .props('outlined dense').classes('w-32 shrink-0')
            nak_dhasa_select = ui.select(options=_star_dhasa_options, value=0,
                                         label=res_str('dhasa_str', 'Dhasa')) \
                .props('outlined dense').classes('w-44 shrink-0')
            nak_planet_select = ui.select(options=_planet_options, value=const.MOON_ID + 1,
                                          label=res_str('planet_str', 'Planet')) \
                .props('outlined dense').classes('w-36 shrink-0')
            nak_level_select = ui.select(options=_level_options, value=const.MAHA_DHASA_DEPTH.ANTARA - 1,
                                         label=res_str('dhasa_level_str', 'Dhasa Level')) \
                .props('outlined dense').classes('w-40 shrink-0')
            nak_date_input = ui.input(res_str('current_date_str', 'Current Date'), value='') \
                .props('outlined dense').classes('w-32 shrink-0')
            nak_time_input = ui.input(res_str('time_str', 'Time'), value='').props('outlined dense').classes('w-28 shrink-0')
            nak_all_levels = ui.checkbox(res_str('show_all_dhasa_levels_str', 'Show all dhasa levels'), value=False) \
                .classes('shrink-0')
            step_prev_button = ui.button(icon='chevron_left', on_click=lambda: compute_transit('previous')) \
                .props('outlined dense').classes('shrink-0')
            with step_prev_button:
                ui.tooltip(res_str('previous_str', 'Previous'))
            step_next_button = ui.button(icon='chevron_right', on_click=lambda: compute_transit('next')) \
                .props('outlined dense').classes('shrink-0')
            with step_next_button:
                ui.tooltip(res_str('next_str', 'Next'))
            chart_style_select = ui.select(options=_chart_style_options, value=saved_style_index,
                                           label='Chart Style').props('outlined dense').classes('w-48 shrink-0')
            varga_select = ui.select(options=_varga_options, value=0,
                                     label='Varga (Divisional Chart)').props('outlined dense').classes('w-56 shrink-0')
            chart_options_button = ui.button(_chart_options_nls, on_click=lambda: _open_chart_options_dialog()) \
                .props('outlined dense').classes('shrink-0')
            with chart_options_button:
                chart_options_tooltip = ui.tooltip('')
            # The desktop app's right-click menu on the chart, as combos (see chart_details.py). Its content is for the
            # chart shown, so it is rebuilt after each calculation. apply_overlay / overlay_supported are defined
            # further down, hence the lambdas.
            chart_menu = chart_details.ChartMenu(
                apply_overlay=lambda overlay: _apply_overlay(overlay),
                overlay_supported=lambda: _overlay_supported(),
                apply_prasna=lambda rasi, replace: _apply_prasna(rasi, replace))
        ecl_note_label = ui.label('').classes('text-xs text-gray-600')   # what the selected Local / Global option does (eclipse type only)
        ui.separator()
        # Non-intrusive "please wait" UI: stays hidden unless compute_transit() is still running after
        # a short delay (see components.DelayedBusyIndicator). Search types (conjunctions, transits,
        # eclipses, etc.) and nakshathra dhasa progression can take seconds, so the Calculate and
        # Previous/Next buttons are disabled immediately while one runs, even before the message appears.
        busy = DelayedBusyIndicator(buttons=[b for b in (w.get('calculate_button'), step_prev_button, step_next_button)
                                             if b is not None],
                                    stop_label=res_str('stop_str', 'Stop'))
        with ui.row().classes('w-full items-start gap-4 flex-nowrap'):
            with ui.column().classes('w-80 shrink-0 gap-2'):
                ui.label('Chart Information').classes('font-bold text-green-700')
                with ui.card().classes('w-full min-h-[400px] p-3 bg-gray-50 shadow text-xs overflow-y-auto max-h-[650px]'):
                    info_html = ui.html('Click "Calculate" to cast the chart.')
            with ui.column().classes('flex-1 gap-2 items-center'):
                chart_title_label = ui.label('').classes('text-lg font-bold text-green-700 text-center w-full')
                chart_container = ui.column().classes('items-center mt-4 keep-ltr')
        def _render_south_indian_generic(chart_1d, asc_house, cell_lookup_fn):
            """Draws a South Indian chart (4x4 border grid, empty 2x2 centre); regular and irregular differ only
            in the rasi-to-cell map.
            Args:
                chart_1d: 12 house strings of '/'-joined planet tokens, indexed by rasi.
                asc_house: rasi index of the ascendant (its cell is highlighted).
                cell_lookup_fn: _south_cell_for_rasi or _south_irregular_cell_for_rasi.
            """
            chart_2d = [[''] * 4 for _ in range(4)]
            rasi_2d = [[None] * 4 for _ in range(4)]
            for rasi_idx in range(12):
                r, c = cell_lookup_fn(rasi_idx)
                if r is not None:
                    chart_2d[r][c] = _cell_text(chart_1d[rasi_idx])
                    rasi_2d[r][c] = rasi_idx
            # The ascendant highlight uses the same lookup as the cell contents.
            asc_r, asc_c = cell_lookup_fn(asc_house)
            chart_container.clear()
            with chart_container:
                # The centre 2x2 area is one grid item spanning rows 2-3 and columns 2-3 (CSS grid, 1-indexed).
                with ui.grid(columns=4).classes('gap-1 bg-white p-2 border-2 border-brown-700 rounded') \
                        .style(f'width:{_CHART_SIZE_PX}px; grid-template-rows: repeat(4, minmax(0, 1fr));'):
                    with ui.card().classes('flex items-center justify-center bg-yellow-50 border border-brown-300') \
                            .style('grid-column: 2 / span 2; grid-row: 2 / span 2;'):
                        _place_center_icon()
                    for r in range(4):
                        for c in range(4):
                            is_center = (1 <= r <= 2 and 1 <= c <= 2)
                            if is_center:
                                continue
                            is_asc = (r == asc_r and c == asc_c)
                            bg = 'bg-emerald-100 border-2 border-green-600' if is_asc else 'bg-yellow-50 border border-brown-300'
                            # The rasi badge is placed absolutely at the cell's top-left corner so that it does not shift the planet text.
                            with ui.card().classes(f'h-24 {bg} p-1 flex items-center justify-center text-center relative'):
                                if rasi_2d[r][c] is not None:
                                    ui.label(_RASI_SHORT[rasi_2d[r][c]]).classes(
                                        'absolute top-0.5 left-1 text-[10px] text-gray-400 font-normal leading-none'
                                    )
                                ui.label(chart_2d[r][c]).classes(
                                    f'{_planet_text_classes(chart_1d[(rasi_2d[r][c] if rasi_2d[r][c] is not None else 0)])} '
                                    'font-bold text-brown-800 whitespace-pre-line'
                                )
                                # Chart menu overlay (arudhas, special lagnas...): bottom-left, as the desktop app does.
                                _ov = _overlay_at(rasi_2d[r][c])
                                if _ov:
                                    ui.label(_ov).classes(
                                        'absolute bottom-0.5 left-1 text-[9px] text-blue-700 font-bold '
                                        'whitespace-pre-line leading-tight text-left'
                                    )
        def _render_south_indian(chart_1d, asc_house):
            """Draws the South Indian regular chart."""
            _render_south_indian_generic(chart_1d, asc_house, _south_cell_for_rasi)
        def _render_south_indian_irregular(chart_1d, asc_house):
            """Draws the South Indian irregular chart."""
            _render_south_indian_generic(chart_1d, asc_house, _south_irregular_cell_for_rasi)
        def _render_east_indian(chart_1d, asc_house, draw_frame):
            """Draws an East Indian chart (3x3 layout, see the East Indian map above).
            Args:
                chart_1d: 12 house strings of '/'-joined planet tokens, indexed by rasi.
                asc_house: rasi index of the ascendant (its planet text is highlighted).
                draw_frame: draw the outer square frame.
            """
            chart_container.clear()
            frame_stroke = 'stroke="#5c3a21" stroke-width="1"' if draw_frame else 'stroke="none"'
            with chart_container:
                with ui.element('div').style(f'position:relative; width:{_CHART_SIZE_PX}px; height:{_CHART_SIZE_PX}px;'):
                    ui.html(f'''
                        <svg viewBox="0 0 99 99" style="position:absolute;top:0;left:0;width:100%;height:100%;">
                          <rect x="0.5" y="0.5" width="98" height="98" fill="none" {frame_stroke}/>
                          <line x1="33" y1="0" x2="33" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="66" y1="0" x2="66" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="33" y1="66" x2="33" y2="99" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="66" y1="66" x2="66" y2="99" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="0" y1="33" x2="33" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="0" y1="66" x2="33" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="66" y1="33" x2="99" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="66" y1="66" x2="99" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="33" y1="33" x2="66" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="33" y1="66" x2="66" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="33" y1="33" x2="33" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="66" y1="33" x2="66" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="0" y1="0" x2="33" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="99" y1="0" x2="66" y2="33" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="0" y1="99" x2="33" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="99" y1="99" x2="66" y2="66" stroke="#5c3a21" stroke-width="0.6"/>
                        </svg>
                    ''')
                    _place_center_icon_absolute(40, 40, 20)
                    def _place_text(px, py, rasi_idx, width=15, align='center'):
                        """Places the planet text of one rasi at (px %, py %) of the chart.
                        Args:
                            px, py: left / top position in %.
                            rasi_idx: rasi whose planets are written.
                            width: text width in %.
                            align: 'left', 'right' or 'center'.
                        """
                        text = _cell_text(chart_1d[rasi_idx])
                        is_asc = (rasi_idx == asc_house)
                        color = 'color:#15803d; font-weight:bold;' if is_asc else 'color:#5c3a21; font-weight:bold;'
                        font_size = '9px' if len([t for t in chart_1d[rasi_idx].split('/') if t.strip()]) >= 4 else '10px'
                        with ui.element('div').style(
                            f'position:absolute; left:{px}%; top:{py}%; width:{width}%; '
                            f'font-size:{font_size}; text-align:{align}; white-space:pre-line; {color}; line-height:1.25;'
                        ):
                            ui.label(text)
                        # Chart menu overlay: just below the planet text, same anchor and alignment.
                        _ov = _overlay_at(rasi_idx)
                        if _ov:
                            with ui.element('div').style(
                                f'position:absolute; left:{px}%; top:{py + 10}%; width:{width}%; '
                                f'font-size:9px; text-align:{align}; white-space:pre-line; color:#1d4ed8; '
                                f'font-weight:bold; line-height:1.15;'
                            ):
                                ui.label(_ov)
                    def _place_badge(px, py, rasi_idx):
                        """Places the zodiac glyph of a rasi at (px %, py %) of the chart.
                        Args:
                            px, py: left / top position in %.
                            rasi_idx: rasi whose glyph is written.
                        """
                        with ui.element('div').style(
                            f'position:absolute; left:{px}%; top:{py}%; '
                            f'font-size:11px; color:#9ca3af; line-height:1;'
                        ):
                            ui.label(_RASI_SHORT[rasi_idx])
                    # Edge cells: badge at the edge-middle of the frame, text centred in the cell body.
                    _place_badge(41, 1, _EAST_EDGE_CELLS['top']); _place_text(42, 8, _EAST_EDGE_CELLS['top'])
                    _place_badge(41, 95, _EAST_EDGE_CELLS['bottom']); _place_text(42, 78, _EAST_EDGE_CELLS['bottom'])
                    _place_badge(1, 46, _EAST_EDGE_CELLS['left']); _place_text(9, 42, _EAST_EDGE_CELLS['left'])
                    _place_badge(95, 46, _EAST_EDGE_CELLS['right']); _place_text(75, 42, _EAST_EDGE_CELLS['right'])
                    # Corner cells hold two rasis split diagonally. Each half has its own badge, placed near the frame edge
                    # that belongs to that half only. The planet text of each half is anchored at the right-angle vertex of
                    # its triangle and aligned toward the side that vertex is on, so more planets extend along that edge.
                    tl_top, tl_left = _EAST_CORNER_CELLS['top_left']
                    _place_badge(14, 2, tl_top); _place_text(14, 6, tl_top, width=17, align='right')
                    _place_badge(2, 14, tl_left); _place_text(3, 23, tl_left, width=17, align='left')
                    tr_right, tr_top = _EAST_CORNER_CELLS['top_right']
                    _place_badge(85, 2, tr_top); _place_text(68, 6, tr_top, width=17, align='left')
                    _place_badge(95, 14, tr_right); _place_text(80, 23, tr_right, width=17, align='right')
                    bl_left, bl_bottom = _EAST_CORNER_CELLS['bottom_left']
                    _place_badge(2, 84, bl_left); _place_text(3, 57, bl_left, width=17, align='left')
                    _place_badge(14, 95, bl_bottom); _place_text(14, 80, bl_bottom, width=17, align='right')
                    br_bottom, br_right = _EAST_CORNER_CELLS['bottom_right']
                    _place_badge(85, 95, br_bottom); _place_text(68, 80, br_bottom, width=17, align='left')
                    _place_badge(95, 84, br_right); _place_text(80, 57, br_right, width=17, align='right')
        def _render_north_indian(chart_1d, asc_house):
            """Draws the North Indian chart (diamond layout).
            Args:
                chart_1d: 12 house strings of '/'-joined planet tokens, indexed by rasi.
                asc_house: rasi index of the ascendant; house 0 of the drawing.
            """
            rotated = chart_1d[asc_house:] + chart_1d[0:asc_house]
            chart_container.clear()
            with chart_container:
                with ui.element('div').style(f'position:relative; width:{_CHART_SIZE_PX}px; height:{_CHART_SIZE_PX}px;'):
                    ui.html('''
                        <svg viewBox="0 0 100 100" style="position:absolute;top:0;left:0;width:100%;height:100%;">
                          <rect x="0" y="0" width="100" height="100" fill="none" stroke="#5c3a21" stroke-width="1"/>
                          <line x1="0" y1="0" x2="100" y2="100" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="100" y1="0" x2="0" y2="100" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="0" y1="50" x2="50" y2="0" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="50" y1="0" x2="100" y2="50" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="100" y1="50" x2="50" y2="100" stroke="#5c3a21" stroke-width="0.6"/>
                          <line x1="50" y1="100" x2="0" y2="50" stroke="#5c3a21" stroke-width="0.6"/>
                        </svg>
                    ''')
                    _place_center_icon_absolute(42, 42, 16)
                    for l, (px, py) in enumerate(_NORTH_LABEL_POSITIONS):
                        text = _cell_text(rotated[l])
                        is_asc = (l == 0)
                        color = 'color:#15803d; font-weight:bold;' if is_asc else 'color:#5c3a21; font-weight:bold;'
                        font_size = '9px' if len([t for t in rotated[l].split('/') if t.strip()]) >= 4 else '10px'
                        # Text alignment is approximate: houses left of the centre align left, houses right of the centre align
                        # right and the middle houses are centred.
                        if px < 45:
                            align = 'left'
                        elif px > 55:
                            align = 'right'
                        else:
                            align = 'center'
                        with ui.element('div').style(
                            f'position:absolute; left:{px}%; top:{py}%; width:15%; '
                            f'font-size:{font_size}; text-align:{align}; white-space:pre-line; {color}; line-height:1.25;'
                        ):
                            ui.label(text)
                        # Chart menu overlay at the house's overlay position (see _NORTH_OVERLAY_POSITIONS). The data is
                        # rotated by asc_house, so house l is absolute rasi (asc_house + l) % 12.
                        _ov = _overlay_at((asc_house + l) % 12)
                        if _ov:
                            ox, oy = _NORTH_OVERLAY_POSITIONS[l]
                            side = f'right:{100 - ox}%; text-align:right;' if ox >= 80 else f'left:{ox}%; text-align:left;'
                            with ui.element('div').style(
                                f'position:absolute; {side} top:{oy}%; width:15%; font-size:9px; '
                                f'white-space:pre-line; color:#1d4ed8; font-weight:bold; line-height:1.15;'
                            ):
                                ui.label(_ov)
                        # The rasi badge sits at the nearest frame vertex of the house (see _NORTH_BADGE_ANCHORS).
                        vx, vy, ndx, ndy = _NORTH_BADGE_ANCHORS[l]
                        # Absolute rasi of house l is (asc_house + l) % 12, because the data was rotated by asc_house.
                        abs_rasi = (asc_house + l) % 12
                        with ui.element('div').style(
                            f'position:absolute; left:{vx + ndx}%; top:{vy + ndy}%; '
                            f'font-size:10px; color:#9ca3af; line-height:1;'
                        ):
                            ui.label(_RASI_SHORT[abs_rasi])
        def _render_sudarsana_chakra(sc_rings):
            """Draws the Sudarsana Chakra chart: three concentric bhava rings (Lagna, Moon and Sun, from
            the centre outward), each divided into its 12 houses, for a solar year after birth (as the
            desktop app does for this tab). See jhora.horoscope.dhasa.sudharsana_chakra for the source.
            Args:
                sc_rings: [lagna_chart, moon_chart, sun_chart, retrograde_planets] from
                    sudharsana_chakra.sudharshana_chakra_chart(); each of the first three is 12
                    (absolute rasi index, '/'-joined planet tokens) tuples, indexed by house from that
                    reference point (index 0 is the reference point's own house, highlighted).
            """
            lagna_chart, moon_chart, sun_chart, _retrograde = sc_rings
            ring_defs = [
                (lagna_chart, res_str('ascendant_str', 'Lagna'), _SC_RING_RADII_PCT[0]),
                (moon_chart, utils.PLANET_NAMES[const.MOON_ID], _SC_RING_RADII_PCT[1]),
                (sun_chart, utils.PLANET_NAMES[const.SUN_ID], _SC_RING_RADII_PCT[2]),
            ]
            hole_r = ring_defs[0][2][0]
            outer_r = ring_defs[-1][2][1]
            chart_container.clear()
            with chart_container:
                with ui.element('div').style(f'position:relative; width:{_CHART_SIZE_PX}px; height:{_CHART_SIZE_PX}px;'):
                    circles = f'<circle cx="50" cy="50" r="{hole_r}" fill="none" stroke="#5c3a21" stroke-width="0.4"/>'
                    circles += ''.join(
                        f'<circle cx="50" cy="50" r="{r_out}" fill="none" stroke="#5c3a21" stroke-width="0.4"/>'
                        for _, _, (_, r_out) in ring_defs
                    )
                    # One spoke per house boundary (between houses, not through their centres), from the
                    # centre hole out to the outermost ring.
                    spokes = ''.join(
                        f'<line x1="{50 + hole_r * math.cos(math.radians(-90 + h * 30 - 15)):.2f}" '
                        f'y1="{50 + hole_r * math.sin(math.radians(-90 + h * 30 - 15)):.2f}" '
                        f'x2="{50 + outer_r * math.cos(math.radians(-90 + h * 30 - 15)):.2f}" '
                        f'y2="{50 + outer_r * math.sin(math.radians(-90 + h * 30 - 15)):.2f}" '
                        f'stroke="#5c3a21" stroke-width="0.3"/>'
                        for h in range(12)
                    )
                    ui.html(f'''
                        <svg viewBox="0 0 100 100" style="position:absolute;top:0;left:0;width:100%;height:100%;">
                          {circles}
                          {spokes}
                        </svg>
                    ''')
                    _place_center_icon_absolute(42, 42, 2 * hole_r * 0.9)
                    for ring_data, _ring_label, (r_in, r_out) in ring_defs:
                        r_label = (r_in + r_out) / 2
                        for h in range(12):
                            abs_rasi, raw_cell = ring_data[h]
                            angle = math.radians(-90 + h * 30)
                            cx = 50 + r_label * math.cos(angle)
                            cy = 50 + r_label * math.sin(angle)
                            is_ref_house = (h == 0)
                            color = 'color:#15803d; font-weight:bold;' if is_ref_house else 'color:#5c3a21; font-weight:bold;'
                            with ui.element('div').style(
                                f'position:absolute; left:{cx:.2f}%; top:{cy:.2f}%; width:12%; '
                                f'transform:translate(-50%,-40%); font-size:8px; text-align:center; '
                                f'white-space:pre-line; {color} line-height:1.1;'
                            ):
                                ui.label(_cell_text(raw_cell))
                            with ui.element('div').style(
                                f'position:absolute; left:{cx:.2f}%; top:{cy - (r_out - r_in) * 0.32:.2f}%; '
                                f'font-size:7px; color:#9ca3af; line-height:1; transform:translate(-50%,-100%);'
                            ):
                                ui.label(_RASI_SHORT[abs_rasi])
                    with ui.element('div').style(
                        'position:absolute; left:2%; top:2%; font-size:9px; color:#5c3a21; white-space:nowrap;'
                    ):
                        ui.label(
                            f"{res_str('inner_str', 'Inner')}: {ring_defs[0][1]}  |  "
                            f"{res_str('middle_str', 'Middle')}: {ring_defs[1][1]}  |  "
                            f"{res_str('outer_str', 'Outer')}: {ring_defs[2][1]}"
                        )
        def _render_not_yet_implemented(style_label):
            """Shows a placeholder for a chart style that cannot be drawn yet."""
            chart_container.clear()
            with chart_container:
                with ui.card().classes('w-full max-w-md p-8 bg-gray-50 border-2 border-dashed border-gray-300 text-center'):
                    ui.icon('construction', size='2rem').classes('text-gray-400')
                    ui.label(f'{style_label} chart rendering is not yet implemented.').classes('text-gray-500 mt-2')
                    ui.label('Switch to South Indian, East Indian, North Indian, or Sudarsana Chakra for now.').classes('text-gray-400 text-sm')
        # Western chart: (r1, r2, r3, r4) radii of the four concentric circles, in % of chart size. r2..r3 is
        # the planet-label ring - widened from the original (9, 34, 40, 46) to give crowded houses (4+ planets)
        # more room to wrap onto their own lines without colliding with the zodiac-glyph ring just outside it.
        _WESTERN_RING_RADII_PCT = (9, 28, 44, 49)
        # Width of each planet-label box, in % of chart size (was 14; widened along with the ring itself).
        _WESTERN_LABEL_WIDTH_PCT = 20
        def _render_western(chart_1d, asc_house):
            """Wheel-style Western chart: 4 concentric circles, 12 house-cusp spokes starting at the ascendant
            (9 o'clock, going anticlockwise), zodiac glyphs in the outer ring, planet text in the middle ring.
            Ported from the desktop app's WesternChart (chart_styles.py), using the web's sign-indexed chart_1d
            (whole-sign houses) in place of the desktop version's exact per-planet degree strings.
            """
            r1, r2, r3, r4 = _WESTERN_RING_RADII_PCT
            chart_container.clear()
            with chart_container:
                with ui.element('div').style(f'position:relative; width:{_CHART_SIZE_PX}px; height:{_CHART_SIZE_PX}px;'):
                    circles = ''.join(
                        f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="#5c3a21" stroke-width="0.4"/>'
                        for r in (r1, r2, r3, r4)
                    )
                    spokes = ''.join(
                        f'<line x1="{50 + r3*math.cos(math.radians(180-h*30)):.2f}" y1="{50 - r3*math.sin(math.radians(180-h*30)):.2f}" '
                        f'x2="{50 + r4*math.cos(math.radians(180-h*30)):.2f}" y2="{50 - r4*math.sin(math.radians(180-h*30)):.2f}" '
                        f'stroke="#5c3a21" stroke-width="0.5"/>' for h in range(12)
                    )
                    ticks = ''.join(
                        f'<line x1="{50 + r2*math.cos(math.radians(d)):.2f}" y1="{50 - r2*math.sin(math.radians(d)):.2f}" '
                        f'x2="{50 + r3*math.cos(math.radians(d)):.2f}" y2="{50 - r3*math.sin(math.radians(d)):.2f}" '
                        f'stroke="#5c3a21" stroke-width="0.2"/>' for d in range(0, 360, 10)
                    )
                    ui.html(f'<svg viewBox="0 0 100 100" style="position:absolute;top:0;left:0;width:100%;height:100%;">{circles}{ticks}{spokes}</svg>')
                    _place_center_icon_absolute(42, 42, 2 * r1 * 0.9)
                    for h in range(12):
                        abs_rasi = (asc_house + h) % 12
                        mid = 180 - (h * 30 + 15)
                        px, py = 50 + ((r2+r3)/2)*math.cos(math.radians(mid)), 50 - ((r2+r3)/2)*math.sin(math.radians(mid))
                        color = 'color:#15803d; font-weight:bold;' if h == 0 else 'color:#5c3a21; font-weight:bold;'
                        with ui.element('div').style(f'position:absolute; left:{px:.2f}%; top:{py:.2f}%; width:{_WESTERN_LABEL_WIDTH_PCT}%; '
                                f'transform:translate(-50%,-50%); font-size:9px; text-align:center; white-space:pre-line; {color} line-height:1.1;'):
                            ui.label(_cell_text(chart_1d[abs_rasi]))
                        zx, zy = 50 + ((r3+r4)/2)*math.cos(math.radians(mid)), 50 - ((r3+r4)/2)*math.sin(math.radians(mid))
                        with ui.element('div').style(f'position:absolute; left:{zx:.2f}%; top:{zy:.2f}%; '
                                f'transform:translate(-50%,-50%); font-size:11px; color:#9ca3af; line-height:1;'):
                            ui.label(_RASI_SHORT[abs_rasi])
                        _ov = _overlay_at(abs_rasi)
                        if _ov:
                            with ui.element('div').style(f'position:absolute; left:{px:.2f}%; top:{py+6:.2f}%; width:{_WESTERN_LABEL_WIDTH_PCT}%; '
                                    f'transform:translate(-50%,0); font-size:8px; text-align:center; white-space:pre-line; color:#1d4ed8; font-weight:bold; line-height:1.1;'):
                                ui.label(_ov)
        def _render_current_chart():
            """Draws the last computed chart (transit_state["render"]) in the chart style it was computed for, with the
            current chart menu overlay. It does not recompute anything, so it is also used when only the overlay
            changes.
            """
            rendered = transit_state.get("render")
            if rendered is None:
                return
            chart_style, chart_1d, asc_house, sc_rings = rendered
            if transit_state.get("prasna") is not None:
                # A Prasna Lagna that replaces the ascendant: the chart is drawn with it (the real chart stays stored).
                chart_1d, asc_house = chart_details.chart_with_prasna(chart_1d, asc_house, transit_state["prasna"])
            if chart_style == const.CHART_STYLE.SOUTH_INDIAN_REGULAR:
                _render_south_indian(chart_1d, asc_house)
            elif chart_style == const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR:
                _render_south_indian_irregular(chart_1d, asc_house)
            elif chart_style == const.CHART_STYLE.NORTH_INDIAN:
                _render_north_indian(chart_1d, asc_house)
            elif chart_style == const.CHART_STYLE.EAST_INDIAN_WITH_FRAME:
                _render_east_indian(chart_1d, asc_house, draw_frame=True)
            elif chart_style == const.CHART_STYLE.EAST_INDIAN_NO_FRAME:
                _render_east_indian(chart_1d, asc_house, draw_frame=False)
            elif chart_style == const.CHART_STYLE.SUDARSANA_CHAKRA:
                _render_sudarsana_chakra(sc_rings)
            elif chart_style == const.CHART_STYLE.WESTERN:
                _render_western(chart_1d, asc_house)
            else:
                _render_not_yet_implemented(_chart_style_label(chart_style))
        def _sync_menu_visibility():
            """Hides the chart menu combos for a chart style the menu is not offered for (Sudarsana Chakra, Western) and
            shows them again for any other."""
            idx = chart_style_select.value if isinstance(chart_style_select.value, int) else 0
            chart_menu.set_hidden(not chart_details.style_supports_menu(_chart_style_keys[idx]))
        def _apply_overlay(overlay):
            """Writes a chart menu overlay (12-list indexed by absolute rasi; None clears it) into the chart cells.
            Like every entry other than Prasna Lagna on the desktop, it also drops a Prasna Lagna replacement."""
            transit_state["overlay"] = overlay
            transit_state["prasna"] = None
            _render_current_chart()
        def _apply_prasna(rasi, replace):
            """Shows a Prasna Lagna: replace=True moves the ascendant to that rasi (the chart is drawn with
            chart_details.chart_with_prasna()), False draws its short label in that rasi's cell."""
            transit_state["prasna"] = rasi if replace else None
            transit_state["overlay"] = None if replace else chart_details.prasna_marker_overlay(rasi)
            _render_current_chart()
        def _overlay_supported():
            """True if the displayed chart style can draw a chart menu overlay in its cells."""
            rendered = transit_state.get("render")
            return rendered is not None and rendered[0] in (
                const.CHART_STYLE.SOUTH_INDIAN_REGULAR, const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR,
                const.CHART_STYLE.NORTH_INDIAN, const.CHART_STYLE.EAST_INDIAN_WITH_FRAME,
                const.CHART_STYLE.EAST_INDIAN_NO_FRAME)
        def _current_varga_idx():
            """Returns the index of the selected divisional chart (0 if the selection is not a valid index)."""
            v = varga_select.value
            if isinstance(v, bool):
                return 0
            if isinstance(v, int):
                return v
            if isinstance(v, str) and v.strip().lstrip('-').isdigit():
                return int(v)
            return 0
        def _method_count_and_default(varga_idx):
            """Returns (method_count, default_method) of the divisional chart at index `varga_idx`; the default
            method is 1-based. D1 (index 0) and a failed lookup give (1, 1).
            The values come from utils.get_varga_option_dict(), whose entries are (method_count, method_index,
            base_rasi_index, count_from_end_of_sign), so they follow the visitor's settings.
            """
            if varga_idx == 0:
                return 1, 1
            varga_factor = _division_chart_factors[varga_idx]
            try:
                method_count, default_method, _base_rasi_idx, _count_from_end = utils.get_varga_option_dict()[varga_factor]
            except (KeyError, TypeError, ValueError) as e:
                # Lookup failed: report it on the console and treat the varga as having a single method.
                print(f"[transit_page] get_varga_option_dict() lookup/unpack failed for varga_factor={varga_factor} (varga_idx={varga_idx}): {e}")
                return 1, 1
            if method_count is None:
                return 1, 1
            return method_count, (default_method if default_method is not None else 1)
        def _refresh_chart_options_button(varga_idx=None):
            """Enables the Chart Options button, with a tooltip, only when the selected divisional chart has more
            than one method; otherwise disables it.
            Args:
                varga_idx: index to use; None reads the current selection.
            """
            if varga_idx is None:
                varga_idx = _current_varga_idx()
            try:
                method_count, _ = _method_count_and_default(varga_idx)
            except Exception as e:
                print(f"[transit_page] _refresh_chart_options_button error for varga_idx={varga_idx}: {e}")
                method_count = 1
            if method_count > 1:
                chart_options_button.enable()
                chart_options_button.classes(remove='text-gray-400')
                chart_options_tooltip.set_text(f'Choose which of the {method_count} calculation methods to use for this varga.')
            else:
                chart_options_button.disable()
                chart_options_button.classes(add='text-gray-400')
                chart_options_tooltip.set_text('This varga has only one calculation method - nothing to configure.')
        def _open_chart_options_dialog():
            """Opens the dialog for choosing the calculation method of the selected divisional chart. Accept stores
            the choice (1-based) in chart_options_state and recomputes.
            """
            varga_idx = _current_varga_idx()
            method_count, default_method = _method_count_and_default(varga_idx)
            if method_count <= 1:
                safe_notify('This varga has only one calculation method - nothing to configure.', type='warning')
                return
            varga_factor = _division_chart_factors[varga_idx]
            current_method = chart_options_state.get(varga_idx, default_method)
            # Method labels use the resource keys d{factor}_option{n}_str.
            method_items = {
                mc: res_str(f'd{varga_factor}_option{mc + 1}_str', f'Method {mc + 1}')
                for mc in range(method_count)
            }
            with ui.dialog() as dialog, ui.card().classes('gap-3'):
                ui.label(
                    res_str('varga_option_str', 'Varga Chart Options') + ' - ' + _varga_label(varga_idx)
                ).classes('text-lg font-bold text-green-700')
                method_radio = ui.radio(method_items, value=current_method - 1).props('inline' if method_count <= 3 else '')
                async def _on_accept():
                    ind = method_radio.value if isinstance(method_radio.value, int) else (default_method - 1)
                    chart_options_state[varga_idx] = ind + 1  # stored 1-based
                    dialog.close()
                    safe_notify('Chart options applied - recomputing.', type='positive')
                    await compute_transit()
                with ui.row().classes('gap-2 justify-end w-full'):
                    ui.button(res_str('cancel_str', 'Cancel'), on_click=dialog.close).props('outlined dense')
                    ui.button(res_str('accept_str', 'Accept'), on_click=_on_accept).classes('bg-green-600 text-white')
            dialog.open()
        def _refresh_conj_planet2():
            """Rebuilds the second planet list of the conjunction search: every selector entry except the first
            planet; after Rahu or Ketu only the first 7 entries remain.
            """
            p1 = conj_p1_select.value
            remaining = [i for i in range(10) if i != p1]
            if p1 in (8, 9):
                remaining = remaining[:7]
            options = {i: _planet_options[i] for i in remaining}
            conj_p2_select.set_options(options, value=conj_p2_select.value if conj_p2_select.value in options
                                       else remaining[0])
        def _eclipse_note_text():
            """Returns the text that says what the selected Local / Global option does for the selected kind of eclipse."""
            is_lunar = ecl_kind_select.value == 'lunar'
            if ecl_loc_select.value == 'local':
                if is_lunar:
                    return res_str('eclipse_note_lunar_local_str', 'Lunar eclipses are shown only if the Moon is above the horizon at one or more of the contacts at this place.')
                return res_str('eclipse_note_solar_local_str', 'Solar eclipses are shown only if the Sun is above the horizon at one or more of the contacts at this place.')
            if is_lunar:
                return res_str('eclipse_note_lunar_global_str', 'The next lunar eclipse is shown whether or not the Moon is above the horizon at this place.')
            if _eclipse_classical:
                return res_str('eclipse_note_solar_global_str', 'The next solar eclipse at this place is shown whether or not the Sun is above the horizon.')
            return res_str('eclipse_note_solar_global_drik_str', 'The next solar eclipse on Earth is shown, with its global begin, maximum and end times.')
        def _refresh_eclipse_note():
            """Shows the note of the selected Local / Global option, for the Eclipse pravesha type only."""
            ecl_note_label.set_text(_eclipse_note_text())
            ecl_note_label.set_visibility(pravesha_select.value == 'eclipse_str')
        def _refresh_eclipse_types():
            """Fills the eclipse type selector for the selected solar / lunar kind."""
            ecl_type_select.set_options(_eclipse_type_options(ecl_kind_select.value == 'lunar'), value='any')
            _refresh_eclipse_note()
        def _fill_nak_current_moment():
            """Fills the empty "current date" and time of the progression with now at the entered place."""
            if nak_date_input.value and nak_time_input.value:
                return
            try:
                tz = float(w['tz_input'].value.strip())
            except (TypeError, ValueError, AttributeError):
                tz = 0.0
            now = datetime.now(timezone(timedelta(hours=tz)))
            if not nak_date_input.value:
                nak_date_input.value = f"{now.year},{now.month},{now.day}"
            if not nak_time_input.value:
                nak_time_input.value = now.strftime('%H:%M:%S')
        def _refresh_pravesha_inputs():
            """Shows only the inputs that the selected pravesha type uses."""
            kind = pravesha_select.value
            years_input.set_visibility(kind in ('annual_str', 'customized_str'))
            months_input.set_visibility(kind == 'customized_str')
            sixty_input.set_visibility(kind == 'customized_str')
            tithi_year_input.set_visibility(kind == 'tithi_pravesha_str')
            lunar_type_select.set_visibility(kind == 'lunar_month_year_str')
            for widget in (conj_sep_select, conj_p1_select, conj_p2_select):
                widget.set_visibility(kind == 'planetary_conjunctions_str')
            for widget in (transit_p_select, transit_raasi_select):
                widget.set_visibility(kind == 'planet_transit_str')
            vakra_p_select.set_visibility(kind == 'vakra_gathi_change_str')
            for widget in (ecl_kind_select, ecl_type_select, ecl_loc_select):
                widget.set_visibility(kind == 'eclipse_str')
            for widget in (nak_dhasa_select, nak_planet_select, nak_level_select, nak_date_input, nak_time_input,
                           nak_all_levels):
                widget.set_visibility(kind == _NAK_KEY)
            if kind == _NAK_KEY:
                _fill_nak_current_moment()
            for button in (step_prev_button, step_next_button):
                button.set_visibility(kind in _STEP_KINDS)
            _refresh_eclipse_note()
        def _show_search_hint(kind):
            """Clears the chart (and the chart menu, which describes the chart) and tells how to start the calculation of
            the selected type."""
            chart_title_label.set_text('')
            chart_container.clear()
            transit_state.update({"overlay": None, "render": None, "detail_ctx": None, "prasna": None})
            chart_menu.clear()
            _sync_menu_visibility()
            if kind == _NAK_KEY:
                info_html.set_content(res_str('transit_progression_hint_str',
                                              'Choose the options, then press Calculate.'))
                return
            info_html.set_content(res_str(
                'transit_search_hint_str',
                'Choose the options, then press Calculate to search from the birth moment, or the arrow buttons to '
                'step to the event before / after the one shown.'))
        @ignore_disconnected_client
        async def compute_transit(direction=None, auto=False):
            """Reads the control bar and the pravesha inputs, derives the chart moment and computes the chart in
            a worker thread (showing a non-intrusive "please wait" message via DelayedBusyIndicator only if it
            takes more than a moment), then draws the chart and the chart information.
            Args:
                direction: 'previous' or 'next' to step a step type (Previous / Next buttons); None for any other
                    trigger, which shows the current step.
                auto: True when the call was caused by a new chart style, varga or lunar type, or by saved settings,
                    and not by a new pravesha type, Calculate or a step button. A search type and the nakshathra
                    dhasa progression are then not calculated; the result shown is only redrawn, or the hint is
                    shown when there is none.
            """
            if busy.is_busy:
                safe_notify('Already computing. Please wait.', type='warning')
                return
            try:
                dob_val = w['dob_input'].value.strip()
                tob_val = w['tob_input'].value.strip()
                place_val = w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
                lat_val = float(w['lat_input'].value.strip())
                lon_val = float(w['lon_input'].value.strip())
                tz_val = float(w['tz_input'].value.strip())
                year, month, day = dob_val.split(",")
                dob = (int(year), int(month), int(day))
                tob = _parse_tob(tob_val)
                kind = pravesha_select.value
                years = _int_or_none(years_input.value)
                months = _int_or_none(months_input.value)
                sixty_hours = _int_or_none(sixty_input.value)
                tithi_year = _int_or_none(tithi_year_input.value)
                lunar_choice = _LUNAR_CHOICES.get(lunar_type_select.value, (0, False))
                opts = {
                    'lunar': lunar_choice, 'lunar_label': _lunar_options.get(lunar_type_select.value, ''),
                    'conj': (conj_p1_select.value, conj_p2_select.value, conj_sep_select.value),
                    'transit': (transit_p_select.value, transit_raasi_select.value),
                    'vakra': vakra_p_select.value,
                    'eclipse': (ecl_kind_select.value, ecl_type_select.value, ecl_loc_select.value),
                    'nak': (nak_dhasa_select.value, nak_planet_select.value, nak_level_select.value,
                            (nak_date_input.value or '').strip(), (nak_time_input.value or '').strip(),
                            bool(nak_all_levels.value)),
                }
                varga_idx = _current_varga_idx()
                dcf = _division_chart_factors[varga_idx]
                chart_style_index = chart_style_select.value if isinstance(chart_style_select.value, int) else 0
                chart_style = _chart_style_keys[chart_style_index]
            except Exception as e:
                safe_notify(f'Error computing transit chart: {str(e)}', type='negative')
                info_html.set_content(f'<span style="color:red">Error: {e}</span>')
                return
            try:
                result = await busy.run(
                    _transit_locked, dob, tob, place_val, lat_val, lon_val, tz_val, kind, opts, varga_idx, dcf,
                    direction, auto, step_state, nak_state, moment_cache, years, months, sixty_hours, tithi_year,
                    chart_options_state, chart_style,
                    wait_text=res_str('transit_wait_str', 'Searching... this can take a while. Please wait for the results.'))
            except Exception as e:
                safe_notify(f'Error computing transit chart: {str(e)}', type='negative')
                info_html.set_content(f'<span style="color:red">Error: {e}</span>')
                return
            if result is DelayedBusyIndicator.STOPPED:
                return  # Stop (or a newer call) superseded this one; discard the stale result quietly
            try:
                (moment, caption, extra_lines, step_n, cast_moment, correction, horo, chart_1d, asc_house,
                 chart_info, chart_method, sc_rings) = result
                if moment is None:
                    _show_search_hint(kind)
                    return
                transit_state.update({"horo": horo})
                moment_text = (f"{moment[0][0]:04d}-{moment[0][1]:02d}-{moment[0][2]:02d} "
                               f"{moment[1][0]:02d}:{moment[1][1]:02d}:{moment[1][2]:02d}")
                label = caption or _pravesha_options.get(kind, kind)
                if step_n is not None:
                    label = f"{label} ({step_n:+d})"
                chart_title_label.set_text(f"{label} \u2014 {_varga_label(varga_idx)} "
                                           f"({_chart_style_label(chart_style)}) \u2014 {moment_text}")
                # A new chart starts without a chart menu overlay; the menu itself is rebuilt for it (in the background, so
                # the information panel below is not held up). The chart is cast for cast_moment when it differs from
                # the displayed moment (the nakshathra dhasa progression), with that progression's correction.
                chart_date, chart_time = cast_moment or moment
                transit_state["overlay"] = None
                transit_state["prasna"] = None
                transit_state["render"] = (chart_style, chart_1d, asc_house, sc_rings)
                transit_state["detail_ctx"] = chart_details.make_context(
                    horo, chart_date, chart_time, varga_idx, dcf, chart_method, chart_style, correction=correction)
                _render_current_chart()
                _sync_menu_visibility()   # the menu follows the chart style that was just drawn, however it was selected
                chart_menu.schedule_rebuild(transit_state["detail_ctx"])
                sep = '<br>'
                lines = []
                lines.append(f"<b>{res_str('place_str','Place')}:</b> {place_val}")
                lines.append(f"<b>{res_str('date_of_birth_str','Date of Birth')}:</b> {dob_val}")
                lines.append(f"<b>{res_str('time_of_birth_str','Time of Birth')}:</b> {tob_val}")
                lines.append(f"<b>{label}:</b> {moment_text}")
                lines.extend(extra_lines)
                lines.append('')
                lines.append(f"<b>{res_str('chart_information_str','Chart Information')}</b>")
                for k, v in chart_info.items():
                    k1 = str(k).split('-')[-1]
                    v1 = str(v).split('-')[0]
                    lines.append(f"<span style='color:brown'>{k1}</span>: <span style='color:blue'>{v1}</span>")
                info_html.set_content(sep.join(lines))
            except Exception as e:
                safe_notify(f'Error computing transit chart: {str(e)}', type='negative')
                info_html.set_content(f'<span style="color:red">Error: {e}</span>')
        async def _on_pravesha_changed(e):
            _refresh_pravesha_inputs()
            await compute_transit()
        async def _on_varga_changed(e):
            _refresh_chart_options_button(e.value if isinstance(e.value, int) else None)
            await compute_transit(auto=True)
        pravesha_select.on_value_change(_on_pravesha_changed)
        async def _on_chart_style_changed(e):
            _sync_menu_visibility()
            await compute_transit(auto=True)
        chart_style_select.on_value_change(_on_chart_style_changed)
        varga_select.on_value_change(_on_varga_changed)
        lunar_type_select.on_value_change(lambda e: compute_transit(auto=True))
        conj_p1_select.on_value_change(lambda e: _refresh_conj_planet2())
        ecl_kind_select.on_value_change(lambda e: _refresh_eclipse_types())
        ecl_loc_select.on_value_change(lambda e: _refresh_eclipse_note())
        _refresh_conj_planet2()
        _refresh_pravesha_inputs()
        _refresh_chart_options_button()
        _sync_menu_visibility()
        ui.timer(0.1, lambda: compute_transit(auto=True), once=True)
    render_footer()

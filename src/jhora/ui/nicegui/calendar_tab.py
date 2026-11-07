#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora
# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Vedic Calendar page (/calendar): a month grid (tithi, nakshatra, sunrise, sunset, festivals and the
date of the chosen calendar for each day) and, for the selected day, its panchangam summary with a
"Show full Panchangam" button. Hijri, Nanakshahi and Bangladesh calendars are offered when enabled in the
settings.
cal_type_key() gives the language-independent key stored in the page state for a calendar type.
The month grid is drawn first without festivals; the festival icons are added a moment later, one day at a
time, so that other requests are not held up while they are computed.
NOTE on printing: this page is NOT registered with print_registry.py's central "Save as PDF" dialog -
Calendar was deliberately left out of scope for that combined PDF. However, render_control_bar() (called
below) ALWAYS draws the one global "Save as PDF" button (see components.py), since that button lives in
the shared control bar used by every page. This page's own on-screen content (the day-info panel and the
month grid) is therefore wrapped in 'single-chart-print-block' - see components.py's _PRINT_CSS - so that
body.printing-all (set while the combined dialog is building its PDF) hides it. Without this, visiting
this page and using the global dialog to print OTHER pages still leaked this page's own live grid into the
combined PDF, appended at the very end (confirmed from an actual printed PDF) - even though Calendar
itself was never checked in the dialog and never appears as one of its own selectable entries.
"""
import contextvars
from nicegui import ui, run
from jhora import const, utils
from jhora.panchanga import info, vratha
drik = utils.hora_engine_proxy
from components import (
    navigation_header, render_control_bar, ensure_default_state, TITHI_ICONS, calc_lock,
    render_full_panchangam_popup, res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
    render_footer, 
)
from panchangam_tab import HEADER_FORMAT, KEY_VALUE_FORMAT
import web_settings
_ACTIVE_BG = 'bg-emerald-100 border-2 border-green-600'
_MONTH_CACHE_SIZE = 24
_DAY_HEADER_COLOR = 'maroon'
_DAY_HEADER_FORMAT_ = '<b><span style="color:' + _DAY_HEADER_COLOR + ';">{}</span></b>'
_CALENDAR_GRID_CELLS = 42
NAKSHATRA_ICONS = [
    'ashvini','bharani','kritthika','rohini','mrigashirsha','ardra','punarvasu','pushya','ashlesha',
    'magha','purva_phalguni','uttara_phalguni','hastha','chitra','swathi','vishaka','anuradha','jyeshta',
    'mula','purva_ashada','uttara_ashada','shravana','dhanishta','shatabisha','purva_bhadrapada',
    'uttara_bhadrapada','revathi'
]
_NANAKSHAHI_MONTH_LIST = ['Chet','Vaisakh','Jeth','Harh','Sawan','Bhadon','Assu','Katik','Maghar','Poh','Magh','Phagun']
_BANGLADESH_MONTH_LIST = ['Boishakh','Joishtho','Asharh','Srabon','Bhadro','Ashshin','Kartik','Ogrohayon','Poush','Magh','Falgun','Choitro']
# Month names of the Nepal Bikram Sambat calendar. vedic_date() returns the month 1-based (1 = Baisakh).
# English transliterations are used for every language; everyday Nepali (Devanagari) names when the UI language is Nepali.
_NEPAL_BS_MONTH_LIST = ['Baisakh','Jestha','Ashadh','Shrawan','Bhadra','Ashwin','Kartik','Mangsir','Poush','Magh','Falgun','Chaitra']
_NEPAL_BS_MONTH_LIST_NE = ['वैशाख','जेठ','असार','साउन','भदौ','असोज','कात्तिक','मङ्सिर','पुस','माघ','फागुन','चैत']
def _nepal_bs_month_name(month, language_code):
    """Name of month `month` (1 = Baisakh ... 12 = Chaitra) of the Nepal Bikram Sambat calendar.
    @param month: 1-based month as returned by drik.vedic_date().
    @param language_code: UI language code, e.g. 'ne' (Nepali names); any other code gives the English names.
    @return: month name.
    """
    _names = _NEPAL_BS_MONTH_LIST_NE if str(language_code).strip().lower() == 'ne' else _NEPAL_BS_MONTH_LIST
    return _names[(month-1) % 12]
# BCE (negative year) support: Solar/Amantha/Purnimantha all work fine for BCE dates (see
# _build_month_grid_locked()'s own BCE-capable date arithmetic); Hijri, Nanakshahi and Bangladesh
# do not (hijri.py's islamic_lunar_date() raises a ValueError for a BCE year). This message only
# fires when the CURRENTLY SELECTED calendar itself is Hijri/Nanakshahi/Bangladesh and the
# entered date is BCE -> generate_grid() refuses outright with the "BCE unsupported" message (see
# its own guard below). If the SELECTED calendar is instead Solar/Amantha/Purnimantha
# (BCE-capable), no special handling is needed HERE even if Hijri/Nanakshahi/Bangladesh also
# happen to be enabled: vratha.py's own get_festivals_of_the_day() (see its
# '_get_criteria_for_the_day()' try/except ValueError) already handles a BCE day safely at the
# source - by catching the underlying Hijri library's "out of range" error for just that one
# calendar type on that one day and skipping it, the same way it already unconditionally skips
# Nanakshahi/Bangladesh (no festival data rows exist for either). An EARLIER version of this fix
# instead toggled const.include_islamic_calendar off/on from the CALLER side (a global, shared
# const attribute) for the duration of that one call - functionally correct for a
# single-threaded/serialized caller, but riskier than necessary (any other code reading that
# same flag concurrently, e.g. the "Charts"/Calendar System dropdown-building logic, could
# momentarily observe it as False) - replaced with the source-level fix in vratha.py instead, so
# no global state is mutated by this page at all anymore.
# Mirrors the identical guard kept in vedic_calendar.py's own computeCalendar() (the PyQt6 app
# this page mirrors), after an actual confirmed crash: "ValueError: year -3102 is out of range"
# with Solar selected but include_islamic_calendar=True.
def _parse_tob(tob_str, fallback=(12, 0, 0)):
    """Parses a time string 'H:M' or 'H:M:S'.
    Args:
        tob_str: time text.
        fallback: value returned when the text cannot be parsed (default noon).
    Returns:
        (hour, minute, second) tuple.
    """
    try:
        parts = [int(x) for x in str(tob_str).strip().split(':')]
        if len(parts) == 2: parts.append(0)
        if len(parts) != 3: raise ValueError(f"expected H:M:S, got {tob_str!r}")
        return tuple(parts)
    except Exception as e:
        print(f"_parse_tob: could not parse the time ({type(e).__name__}); using noon as fallback.")
        return fallback
def cal_type_key(cal_type):
    """Returns the language-independent key stored for a calendar type (its enum member name, e.g.
    'SOLAR'), so the visitor's choice survives a language change."""
    return getattr(cal_type, 'name', str(cal_type))
def _civil_weekday_label(jd):
    """Returns the localized weekday name of a Gregorian date.
    Args:
        jd: Julian day number. drik.civil_weekday(jd) is pure jd arithmetic
            (math.floor(jd+1.5)%7) with no datetime module involved, so it is already BCE-safe
            (jd itself comes from utils.julian_day_number(), which - per that function's own
            docstring - accepts negative/BCE years) with no extra conversion needed here -
            unlike Python's datetime.date (which this used to call directly via
            date(y,m,d).weekday(), and which raises ValueError outside 1 <= year <= 9999).
            drik.civil_weekday() already returns 0=Sunday..6=Saturday, the same convention
            utils.DAYS_LIST is indexed by (see vedic_calendar.py's own
            utils.DAYS_LIST[drik.vaara(jd,place)] for a precedent), so no remapping is needed.
    """
    return utils.DAYS_LIST[drik.civil_weekday(jd)]
def _build_day_header(jd, place_obj, cal_type):
    """Returns the heading text of a calendar day: year, Gregorian date, weekday and the month / day of
    the chosen calendar, followed by paksha and tithi for the solar and lunar calendars.
    Args:
        jd: Julian day number.
        place_obj: drik.Place of the location.
        cal_type: const.CALENDAR_TYPE value.
    """
    y, m, d, _ = utils.jd_to_gregorian(jd)
    weekday_str = _civil_weekday_label(jd)
    tithi_res = drik.tithi(jd, place_obj)
    tit = tithi_res[0]
    paksha = 1 if tit > 15 else 0
    tm, td, ty, am, nm, km = drik.vedic_date(jd, place_obj, calendar_type=cal_type)
    _HIJRI = getattr(const.CALENDAR_TYPE, 'HIJRI_ISLAMIC', None)
    _NANAK = getattr(const.CALENDAR_TYPE, 'NANAKSHAHI_PUNJAB', None)
    _BANGLA = getattr(const.CALENDAR_TYPE, 'BANGLADESH_REFORMED', None)
    _NEPALI = getattr(const.CALENDAR_TYPE, 'NEPAL_BIKRAM_SAMBAT', None)
    if cal_type == const.CALENDAR_TYPE.SOLAR:
        solar_label = res_str('solar_str', 'Solar')
        spl_month_text = f"{utils.MONTH_LIST[tm-1]} {td} ({solar_label})"
        try: year_str = utils.YEAR_LIST[ty] if ty < len(utils.YEAR_LIST) else str(ty)
        except Exception: year_str = str(ty)
    elif cal_type == _HIJRI:
        hijri_label = res_str('hijri_str', 'Hijri')
        spl_month_text = f"{utils.ISLAMIC_MONTH_LIST[tm-1]} {td}* ({hijri_label})"
        year_str = f"({ty})"
    elif cal_type in (_NANAK, _BANGLA, _NEPALI):
        if cal_type == _NANAK:
            month_list = getattr(utils, 'NANAKSHAHI_MONTH_LIST', _NANAKSHAHI_MONTH_LIST); cal_name = res_str('nanakshahi_str', 'Nanakshahi')
        elif cal_type == _BANGLA:
            month_list = getattr(utils, 'BANGLADESH_MONTH_LIST', _BANGLADESH_MONTH_LIST); cal_name = res_str('bangladesh_str', 'Bangladesh')
        else:
            month_list = getattr(utils, 'NEPAL_BS_MONTH_LIST', _NEPAL_BS_MONTH_LIST); cal_name = res_str('nepal_bikram_sambat_str', 'Nepal Bikram Sambat')
        spl_month_text = f"{month_list[(tm-1) % 12]} {td} ({cal_name})"
        year_str = f"({ty})"
    else:
        adhik = utils.resource_strings.get('adhika_maasa_str', '') if am else ''
        nija = utils.resource_strings.get('nija_month_str', '') if nm else ''
        kshaya = utils.resource_strings.get('kshaya_month_str', '') if km else ''
        lsys_label = res_str('purnimantha_str', 'Purnimantha') if cal_type == const.CALENDAR_TYPE.LUNAR_PURNIMANTHA else res_str('amantha_str', 'Amantha')
        spl_month_text = f"{utils.MONTH_LIST[(tm-1)]} {adhik}{nija}{kshaya} {td} ({lsys_label})"
        try: year_str = utils.YEAR_LIST[ty] if ty < len(utils.YEAR_LIST) else str(ty)
        except Exception: year_str = str(ty)
    header = f"{year_str} {y} {utils.MONTH_LIST_EN[m-1]} {d} {weekday_str} — {spl_month_text}"
    if cal_type not in (_HIJRI, _NANAK, _BANGLA):
        paksha_label = utils.PAKSHA_LIST[paksha] if paksha < len(utils.PAKSHA_LIST) else ''
        tithi_label = utils.TITHI_LIST[tit-1] if 0 < tit <= len(utils.TITHI_LIST) else ''
        if paksha_label and tithi_label:
            header += f" {paksha_label} {tithi_label}"
    return header
class _FloatingBusy(DelayedBusyIndicator):
    """DelayedBusyIndicator drawn in a box fixed near the top of the window, so it is visible wherever the
    page is scrolled. The box is hidden unless the indicator is shown."""
    def __init__(self, **kwargs):
        """Draws the (initially hidden) box.
        Args:
            **kwargs: passed to DelayedBusyIndicator.
        """
        with ui.element('div').classes(
                'fixed top-14 left-1/2 -translate-x-1/2 z-[2500] w-max max-w-[90vw] bg-white border '
                'border-green-600 shadow-lg rounded px-4 py-2') as box:
            super().__init__(**kwargs)
        self._box = box
        box.set_visibility(False)
    def _reveal(self, wait_text):
        """Shows the box with the spinner, `wait_text` and the Stop button."""
        self._box.set_visibility(True)
        super()._reveal(wait_text)
    def _hide(self):
        """Hides the spinner, the text, the Stop button and the box."""
        super()._hide()
        self._box.set_visibility(False)
    def stop(self):
        """Stops waiting for the running computation; the box closes after two seconds."""
        was_busy = self.is_busy
        super().stop()
        if was_busy:
            ui.timer(2.0, self._hide_if_idle, once=True)
    def _hide_if_idle(self):
        """Hides the box unless a new computation has started."""
        if not self.is_busy:
            self._hide()
def _day_info_locked(jd, place_obj, cal_type):
    """Computes the heading and the basic panchangam of one calendar day under calc_lock(); blocking, so it
    is run in a worker thread. Only the basic resources are computed: the day summary shows their first lines.
    Args:
        jd: Julian day number of the day.
        place_obj: drik.Place of the location.
        cal_type: calendar type of the grid.
    Returns:
        (header_text, results_dict) - the day heading and the panchangam resources.
    """
    with calc_lock():
        header_text = _build_day_header(jd, place_obj, cal_type)
        results_dict = info.get_panchangam_resources(jd, place_obj, resource_type=1,
                                                     ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE)
    return header_text, results_dict
def _month_festivals(days_cells_data, place_obj, still_wanted):
    """Computes the festival icons of every day of a month grid; blocking, so it is run in a worker thread.
    calc_lock() is taken for one day at a time, so a day click made meanwhile waits for one day only.
    Args:
        days_cells_data: the month's day cells (None for empty cells), as built by _build_month_grid_locked().
        place_obj: drik.Place of the location.
        still_wanted: callable returning False once the result is no longer needed.
    Returns:
        {index in days_cells_data: [{'icon': file, 'tooltip': text}, ...]}, or None when no longer wanted.
    """
    found = {}
    for index, cell in enumerate(days_cells_data):
        if cell is None:
            continue
        if not still_wanted():
            return None
        with calc_lock():
            fest_info = []
            # For a BCE day (cell['year'] < 0), vratha.get_festivals_of_the_day() safely skips
            # Hijri on its own (see the module-level comment above for the full history,
            # including the "ValueError: year -3102 is out of range" this avoids) - no special
            # handling is needed at this call site.
            for f_row in vratha.get_festivals_of_the_day(cell['jd'], place_obj):
                if 'icon_file' in f_row:
                    f_tip = f_row.get(
                        'Festival_' + const.available_languages[const.reverse_languages[const._DEFAULT_LANGUAGE]],
                        f_row.get('Festival_en', 'Festival'))
                    fest_info.append({'icon': f_row['icon_file'], 'tooltip': f_tip})
        found[index] = fest_info
    return found
def _build_month_grid_locked(p_name, lat, lon, tz, y, m, tob, cal_type):
    """Computes one month's grid of day cells (tithi, nakshatra, sunrise/sunset and the date of the chosen
    calendar, for up to _CALENDAR_GRID_CELLS days) under calc_lock(). The festivals of each cell are left
    empty; _month_festivals() computes them.
    This is the slow part of the Vedic Calendar page's generate_grid() - up to _CALENDAR_GRID_CELLS
    astronomical calculations - pulled out to a plain, blocking function so it can run in a worker
    thread via components.DelayedBusyIndicator.run(); a non-intrusive "please wait" message then
    appears only if this turns out to take more than a moment.
    Returns:
        (place_obj, days_cells_data) - see generate_grid() for the shape of each cell.
    """
    with calc_lock():
        place_obj = drik.Place(p_name, lat, lon, tz, 0.0)
        # Uses drik.Date + utils.previous_panchanga_day()/next_panchanga_day() (numpy-based)
        # instead of Python's datetime.date/timedelta - unlike datetime.date, which raises
        # ValueError outside 1 <= year <= 9999, these support BCE years (year <= 0), so this
        # grid can now be built for a BCE "Month Date" the same way vedic_calendar.py's own
        # computeCalendar() (the PyQt6 app this page mirrors) already does.
        first_of_month = drik.Date(y, m, 1)
        previous_month_end = utils.previous_panchanga_day(first_of_month, minus_days=1)
        next_month_start = drik.Date(y + 1, 1, 1) if m == 12 else drik.Date(y, m + 1, 1)
        # drik.civil_weekday(jd) (jd arithmetic only - see _civil_weekday_label()'s own docstring)
        # already returns 0=Sunday..6=Saturday directly, so no '+1' remapping is needed here,
        # unlike the old '(date(...).weekday()+1)%7' pattern this replaces.
        _prev_month_end_jd = utils.julian_day_number(
            (previous_month_end.year, previous_month_end.month, previous_month_end.day), (0, 0, 0))
        start_day = drik.civil_weekday(_prev_month_end_jd)
        days_cells_data = []
        current_civil_date = previous_month_end
        reached_end = False
        for row_idx in range(_CALENDAR_GRID_CELLS):
            if row_idx >= start_day and not reached_end:
                _year, _month, _day = current_civil_date.year, current_civil_date.month, current_civil_date.day
                _jd = utils.julian_day_number((_year, _month, _day), tob)
                tithi_res = drik.tithi(_jd, place_obj)
                tit = tithi_res[0]
                paksha = 1 if tit > 15 else 0
                tithi_name = utils.TITHI_SHORT_LIST[tit-1] if tit <= len(utils.TITHI_SHORT_LIST) else ""
                tithi_full_name = utils.TITHI_LIST[tit-1] if tit <= len(utils.TITHI_LIST) else ""
                paksha_icon = "shukla_paksha.png" if paksha == 0 else "krishna_paksha.png"
                tithi_icon = TITHI_ICONS.get(tit, "")
                srise = utils.to_dms(drik.sunrise(_jd, place_obj)[0], round_to_minutes=True).strip()
                sset = utils.to_dms(drik.sunset(_jd, place_obj)[0], round_to_minutes=True).strip()
                naks = drik.nakshatra(_jd, place_obj)
                nak_id = naks[0]
                nak_short = utils.NAKSHATRA_SHORT_LIST[nak_id-1] if nak_id <= len(utils.NAKSHATRA_SHORT_LIST) else ""
                nak_icon = f"{NAKSHATRA_ICONS[nak_id-1]}.png" if 1 <= nak_id <= len(NAKSHATRA_ICONS) else ""
                tm, td, ty, am, nm, km = drik.vedic_date(_jd, place_obj, calendar_type=cal_type)
                overflow = 'prev' if current_civil_date == previous_month_end else ('next' if current_civil_date == next_month_start else None)
                days_cells_data.append({
                    'jd': _jd, 'year': _year, 'month': _month, 'day_num': _day, 'cal_day': td,
                    'tithi': tithi_name, 'tithi_full': tithi_full_name, 'paksha_icon': paksha_icon,
                    'tithi_icon': tithi_icon, 'nak_short': nak_short, 'nak_icon': nak_icon,
                    'sunrise': srise, 'sunset': sset, 'festivals': [], 'festivals_loaded': False,
                    'is_current_month': (_month == m), 'overflow': overflow,
                })
                if current_civil_date == next_month_start: reached_end = True
                current_civil_date = utils.next_panchanga_day(current_civil_date, add_days=1)
            else:
                days_cells_data.append(None)
        return place_obj, days_cells_data
@ui.page('/calendar')
def calendar_page():
    """Vedic Calendar page (/calendar): a month grid (tithi, nakshatra, sunrise, sunset, festivals and the
    date of the chosen calendar for each day) and, for the selected day, its panchangam summary with a
    "Show full Panchangam" button. Hijri, Nanakshahi and Bangladesh calendars are offered when enabled
    in the settings.
    """
    navigation_header()
    state = ensure_default_state()
    selection = {"jd": None, "place_obj": None, "cal_type": None}
    day_cards = {}       # (year, month, day) -> (card, background classes when not selected)
    day_cache = {}       # (jd, calendar type, settings) -> (header_text, results_dict) of days already computed
    month_cache = {}     # (place, month, time, calendar type, settings) -> (place_obj, day cells) of months already built
    day_state = {"running": False, "pending": None}
    calendar_state = {"grid_data": None, "place_obj": None, "cal_type": None,
                       "place_name_str": None, "active_date": None, "header_text": "", "festival_token": 0}
    _CAL_TYPE_SEQUENCE = [
        (const.CALENDAR_TYPE.SOLAR, res_str('solar_str', 'Solar')),
        (const.CALENDAR_TYPE.LUNAR_AMANTHA, res_str('amantha_str', 'Amantha')),
        (const.CALENDAR_TYPE.LUNAR_PURNIMANTHA, res_str('purnimantha_str', 'Purnimantha')),
    ]
    # Calendar options are read inside calc_lock() so the visitor's own settings apply.
    with calc_lock():
        _inc_hijri = getattr(const, 'include_islamic_calendar', False) and utils.astro_engine_is_drik()
        _inc_nanak = getattr(const, 'include_nanashahi_punjab_calendar', False)
        _inc_bangla = getattr(const, 'include_bangladesh_reformed_calendar', False)
        _inc_bikram = getattr(const, 'include_nepal_bikram_sambat_calendar', False)
    if _inc_hijri:
        _CAL_TYPE_SEQUENCE.append((const.CALENDAR_TYPE.HIJRI_ISLAMIC, res_str('hijri_str', 'Hijri')))
    if _inc_nanak:
        _CAL_TYPE_SEQUENCE.append((const.CALENDAR_TYPE.NANAKSHAHI_PUNJAB, res_str('nanakshahi_str', 'Nanakshahi')))
    if _inc_bangla:
        _CAL_TYPE_SEQUENCE.append((const.CALENDAR_TYPE.BANGLADESH_REFORMED, res_str('bangladesh_str', 'Bangladesh')))
    if _inc_bikram:
        _CAL_TYPE_SEQUENCE.append((const.CALENDAR_TYPE.NEPAL_BIKRAM_SAMBAT, res_str('nepal_bikram_sambat_str', 'Nepal Bikram Sambat')))
    _cal_type_options = {i: label for i, (_t, label) in enumerate(_CAL_TYPE_SEQUENCE)}
    _default_cal_idx = 0
    for i, (_t, label) in enumerate(_CAL_TYPE_SEQUENCE):
        if cal_type_key(_t) == state["cal_system"]:
            _default_cal_idx = i; break
    with ui.column().classes('w-full p-2 gap-1'):
        ui.label(res_str('calendar_str','Vedic Calendar View')).classes('text-xl font-bold text-green-700')
        def current_cal_type():
            idx = cal_type_select.value
            if isinstance(idx, int) and 0 <= idx < len(_CAL_TYPE_SEQUENCE):
                return _CAL_TYPE_SEQUENCE[idx][0]
            return const.CALENDAR_TYPE.SOLAR
        def current_cal_type_label():
            idx = cal_type_select.value
            if isinstance(idx, int) and 0 <= idx < len(_CAL_TYPE_SEQUENCE):
                return _CAL_TYPE_SEQUENCE[idx][1]
            return res_str('solar_str', 'Solar')
        def settings_signature():
            """Returns text identifying this visitor's current setting overrides, so that cached results are
            never reused after the settings changed."""
            try:
                return repr(sorted(web_settings.get_user_overrides().items()))
            except Exception:
                return ''
        async def load_festivals(days_cells_data, place_obj):
            """Computes the festivals of the month in a worker thread and redraws the grid with their icons,
            unless another month has been shown meanwhile. Does nothing when they are already loaded."""
            calendar_state["festival_token"] += 1
            token = calendar_state["festival_token"]
            if all(c is None or c['festivals_loaded'] for c in days_cells_data):
                return
            try:
                found = await run.io_bound(contextvars.copy_context().run, _month_festivals, days_cells_data,
                                           place_obj, lambda: calendar_state["festival_token"] == token)
            except Exception as e:
                print(f"[calendar] festivals could not be loaded: {type(e).__name__}: {e}")
                return
            if found is None or calendar_state["festival_token"] != token:
                return
            for index, fest_info in found.items():
                days_cells_data[index]['festivals'] = fest_info
                days_cells_data[index]['festivals_loaded'] = True
            if calendar_state["grid_data"] is days_cells_data:
                try:
                    render_grid_from_cache()
                except RuntimeError:
                    pass          # the page was closed meanwhile
        async def navigate_to_month(target_jd):
            y, m, d, _ = utils.jd_to_gregorian(target_jd)
            await generate_grid(display_year=y, display_month=m, force_select_date=(y, m, d), use_cache=True)
        @ignore_disconnected_client
        async def generate_grid(display_year=None, display_month=None, force_select_date=None, use_cache=False):
            """Computes the month grid in a worker thread (showing a non-intrusive "please wait"
            message via DelayedBusyIndicator only if it takes more than a moment) and draws it.
            Args:
                display_year, display_month: month to show; if None, the month of the "Month Date" field.
                force_select_date: (year, month, day) to select after drawing; if None, the typed day is used
                    when the month comes from the field.
                use_cache: show a month already built with the same place, time, calendar and settings instead
                    of computing it again.
            """
            try:
                if display_year is not None and display_month is not None:
                    y, m = display_year, display_month
                else:
                    y, m, typed_day = map(int, date_input.value.strip().split(','))
                    if force_select_date is None:
                        force_select_date = (y, m, typed_day)
                lat = float(w['lat_input'].value); lon = float(w['lon_input'].value); tz = float(w['tz_input'].value)
                p_name = w['place_select'].value or "Chennai"
                cal_type = current_cal_type()
                tob = _parse_tob(time_input.value)
            except Exception as e:
                safe_notify(f'Error generating calendar: {str(e)}', type='negative')
                return
            # Hijri/Nanakshahi/Bangladesh do not support BCE (negative year) dates. This message
            # only fires when the CURRENTLY SELECTED calendar is one of those three - see the
            # module-level comment above for why a BCE-capable SELECTED calendar (Solar/Amantha/
            # Purnimantha) needs no special handling here even if Hijri/Nanakshahi/Bangladesh
            # also happen to be enabled (vratha.py's own get_festivals_of_the_day() already
            # handles that safely at the source). This single check covers every call site that
            # reaches generate_grid() - the initial page load, "Generate Calendar", a Calendar
            # System change, and clicking an overflow cell to navigate months.
            _BCE_UNSUPPORTED_SELECTED_CAL_LABELS = {
                const.CALENDAR_TYPE.HIJRI_ISLAMIC: res_str('hijri_str', 'Hijri'),
                const.CALENDAR_TYPE.NANAKSHAHI_PUNJAB: res_str('nanakshahi_str', 'Nanakshahi'),
                const.CALENDAR_TYPE.BANGLADESH_REFORMED: res_str('bangladesh_str', 'Bangladesh'),
            }
            if y < 0 and cal_type in _BCE_UNSUPPORTED_SELECTED_CAL_LABELS:
                safe_notify(res_str('bce_unsupported_calendar_str',
                                    'BCE dates are not supported for the selected calendar')
                            + ': ' + _BCE_UNSUPPORTED_SELECTED_CAL_LABELS[cal_type], type='negative')
                return
            month_key = (p_name, lat, lon, tz, y, m, tob, cal_type, settings_signature())
            result = month_cache.get(month_key) if use_cache else None
            if result is None:
                try:
                    result = await busy.run(_build_month_grid_locked, p_name, lat, lon, tz, y, m, tob, cal_type,
                                            wait_text=res_str('generating_calendar_str', 'Generating calendar... please wait.'))
                except Exception as e:
                    safe_notify(f'Error generating calendar: {str(e)}', type='negative')
                    return
                if result is DelayedBusyIndicator.STOPPED:
                    return  # Stop (or a newer call) superseded this one; discard the stale result quietly
                month_cache[month_key] = result
                while len(month_cache) > _MONTH_CACHE_SIZE:
                    month_cache.pop(next(iter(month_cache)))
            try:
                place_obj, days_cells_data = result
                day_cache.clear()
                calendar_state.update({
                    "grid_data": days_cells_data, "place_obj": place_obj, "cal_type": cal_type,
                    "place_name_str": p_name, "header_text": f"{utils.MONTH_LIST_EN[m-1]} {y}",
                })
                if force_select_date is not None:
                    fy, fm, fd = force_select_date
                    target_cell = next((c for c in days_cells_data if c and c['year'] == fy and c['month'] == fm and c['day_num'] == fd), None)
                    calendar_state["active_date"] = force_select_date
                    render_grid_from_cache()
                    if target_cell:
                        await select_day(target_cell, place_obj, cal_type)
                else:
                    calendar_state["active_date"] = None
                    render_grid_from_cache()
            except Exception as e:
                safe_notify(f'Error generating calendar: {str(e)}', type='negative')
                return
            await load_festivals(days_cells_data, place_obj)
        def move_highlight(date_key):
            """Highlights the card of `date_key` (year, month, day) and un-highlights the previous one, without
            redrawing the grid."""
            old_key = calendar_state["active_date"]
            calendar_state["active_date"] = date_key
            old, new = day_cards.get(old_key), day_cards.get(date_key)
            if old is not None and old_key != date_key:
                old[0].classes(add=old[1], remove=_ACTIVE_BG)
            if new is not None:
                new[0].classes(add=_ACTIVE_BG, remove=new[1])
        def show_day_info(header_text, results_dict):
            """Shows a day's heading and the first lines of its panchangam, and the "Show full Panchangam" button."""
            day_header_label.set_content(_DAY_HEADER_FORMAT_.format(header_text))
            sep_str = '<br>'
            info_str = ''.join([
                HEADER_FORMAT.format(k) if v.strip() == '' else KEY_VALUE_FORMAT.format(k, v)
                for k, v in results_dict.items()
            ])
            info_list = [ele for ele in info_str.split(sep_str) if ele.strip() != '']
            left_info_html.set_content(sep_str.join(info_list[:14]))
            show_more_button.set_visibility(True)
        async def show_day(cell, place_obj, cal_type):
            """Computes (or takes from the cache) the panchangam of one day and shows it unless a newer click
            has arrived meanwhile."""
            jd = cell['jd']
            cache_key = (jd, cal_type, settings_signature())
            cached = day_cache.get(cache_key)
            if cached is None:
                wait_text = res_str('please_wait_str', 'Please wait...')
                left_info_html.set_content('<i>' + wait_text + '</i>')
                try:
                    cached = await busy.run(_day_info_locked, jd, place_obj, cal_type, wait_text=wait_text)
                except Exception as e:
                    left_info_html.set_content(f'Error: {e}')
                    return
                if cached is DelayedBusyIndicator.STOPPED:
                    if day_state["pending"] is None:
                        left_info_html.set_content('Click a day in the calendar to see its Panchangam summary.')
                    return
                day_cache[cache_key] = cached
            if day_state["pending"] is None:
                show_day_info(*cached)
        async def select_day(cell, place_obj, cal_type):
            """Selects a day: highlights it at once, then shows its heading and panchangam summary. Clicks made
            while a day is being computed are not lost: only the latest one is shown afterwards.
            Args:
                cell: the day's cell of the grid data.
                place_obj: drik.Place of the location.
                cal_type: calendar type of the grid.
            """
            selection["jd"] = cell['jd']; selection["place_obj"] = place_obj; selection["cal_type"] = cal_type
            move_highlight((cell['year'], cell['month'], cell['day_num']))
            day_state["pending"] = (cell, place_obj, cal_type)
            if day_state["running"]:
                return
            day_state["running"] = True
            try:
                while day_state["pending"] is not None:
                    next_cell, next_place, next_type = day_state["pending"]
                    day_state["pending"] = None
                    await show_day(next_cell, next_place, next_type)
            finally:
                day_state["running"] = False
        @ignore_disconnected_client
        async def on_cell_click(cell):
            if cell['overflow'] is not None:
                if busy.is_busy:
                    safe_notify(res_str('please_wait_str', 'Please wait...'), type='warning')
                    return
                await navigate_to_month(cell['jd'])
            else:
                if busy.is_busy and not day_state["running"]:
                    safe_notify(res_str('please_wait_str', 'Please wait...'), type='warning')
                    return
                await select_day(cell, calendar_state["place_obj"], calendar_state["cal_type"])
        def on_options_saved():
            """Drops the cached months and days (the settings changed) and rebuilds the grid."""
            month_cache.clear()
            day_cache.clear()
            return generate_grid()
        @ignore_disconnected_client
        def on_show_more_clicked():
            if selection["jd"] is None: return
            render_full_panchangam_popup(selection["jd"], selection["place_obj"], None)  # ayanamsa_mode=None: resolved inside calc_lock() to the visitor's ayanamsa
        _row1_box = {}
        def _build_date_time_fields():
            date_input = ui.input('Month Date (YYYY,MM,DD)', value=state["date_dob"]).props('outlined dense').classes('w-32 shrink-0')
            date_input.on_value_change(lambda e: state.update({"date_dob": e.value}))
            time_input = ui.input(res_str('time_of_birth_str', 'Time'), value=state["time_tob"]).props('outlined dense').classes('w-24 shrink-0')
            with time_input:
                ui.tooltip('Time used to compute each day\u2019s Panchangam details below (shared with the Panchangam page).')
            time_input.on_value_change(lambda e: state.update({"time_tob": e.value}))
            _row1_box['date_input'] = date_input
            _row1_box['time_input'] = time_input
        def _build_cal_type_field():
            cal_type_select = ui.select(options=_cal_type_options, value=_default_cal_idx, label='Calendar System').props('outlined dense').classes('w-40 shrink-0')
            async def _on_cal_type_changed(e):
                if isinstance(e.value, int) and 0 <= e.value < len(_CAL_TYPE_SEQUENCE):
                    state.update({"cal_system": cal_type_key(_CAL_TYPE_SEQUENCE[e.value][0])})
                await generate_grid(use_cache=True)
            cal_type_select.on_value_change(_on_cal_type_changed)
            _row1_box['cal_type_select'] = cal_type_select
        w = render_control_bar(show_dob_tob=False, on_options_saved=on_options_saved,
                                on_calculate=lambda: generate_grid(),
                                calculate_label=res_str('show_calendar_str', 'Generate Calendar'),
                                extra_fields_before=_build_date_time_fields,
                                extra_fields_after=_build_cal_type_field)
        date_input = _row1_box['date_input']
        time_input = _row1_box['time_input']
        cal_type_select = _row1_box['cal_type_select']
        ui.separator()
        # "Please wait" box fixed near the top of the window: stays hidden unless generate_grid() or a day
        # click is still running after a short delay (see components.DelayedBusyIndicator).
        busy = _FloatingBusy(buttons=w.get('calculate_button'), stop_label=res_str('stop_str', 'Stop'), delay=0.4)
        # 'single-chart-print-block' (on the WRAPPER): hides this page's own on-screen content - BOTH
        # day_header_label AND the day-info/calendar-grid row below - during the global combined
        # "Save as PDF" print (body.printing-all - see components.py's _PRINT_CSS). This page is NOT
        # registered with print_registry.py (Calendar is deliberately out of scope for that combined
        # PDF), but render_control_bar() above still draws the one global "Save as PDF" button (it
        # lives in the shared control bar used by every page) - so without this class, visiting this
        # page and using that dialog to print OTHER pages still left this page's own live content
        # visible, appended at the very end of the combined PDF (confirmed from an actual printed
        # PDF) - the same leak already fixed for every REGISTERED page's own on-screen content.
        with ui.column().classes('w-full gap-1 single-chart-print-block'):
            day_header_label = ui.html('<i>Select a day below to see its Panchangam header.</i>').classes('w-full border-2 border-black rounded p-2 bg-gray-50 text-center text-lg')
            with ui.row().classes('w-full items-start gap-4 flex-nowrap'):
                with ui.column().classes('w-72 shrink-0 gap-2'):
                    ui.label('Day Information').classes('font-bold text-green-700')
                    with ui.card().classes('w-full min-h-[300px] p-3 bg-gray-50 shadow text-xs overflow-y-auto max-h-[500px]'):
                        left_info_html = ui.html('Click a day in the calendar to see its Panchangam summary.')
                    show_more_button = ui.button('Show full Panchangam', on_click=on_show_more_clicked).classes('bg-green-700 text-white font-bold w-full')
                    show_more_button.set_visibility(False)
                with ui.column().classes('flex-1 gap-2'):
                    month_title_label = ui.label('').classes('text-lg font-bold text-green-700 text-center w-full')
                    calendar_grid_container = ui.column().classes('w-full gap-2')
        def render_grid_from_cache():
            """Draws the month grid from the data stored by generate_grid()."""
            grid_data = calendar_state["grid_data"]
            if grid_data is None: return
            active_date = calendar_state["active_date"]
            month_title_label.set_text(f"{calendar_state['header_text']} — {calendar_state['place_name_str']}")
            calendar_grid_container.clear()
            day_cards.clear()
            with calendar_grid_container:
                with ui.grid(columns=7).classes('w-full gap-1 text-center font-bold text-green-800 bg-green-100 p-2 rounded'):
                    for day_name in utils.DAYS_SHORT_NAMES:
                        ui.label(day_name)
                with ui.grid(columns=7).classes('w-full gap-1'):
                    for cell in grid_data:
                        if cell is None:
                            with ui.card().classes('h-28 bg-gray-100 opacity-40 p-1'): pass
                        else:
                            is_active = (active_date is not None and (cell['year'], cell['month'], cell['day_num']) == active_date)
                            if cell['overflow'] == 'prev': normal_bg = 'bg-orange-200 border-2 border-orange-500'
                            elif cell['overflow'] == 'next': normal_bg = 'bg-sky-200 border-2 border-sky-500'
                            elif cell['is_current_month']: normal_bg = 'bg-yellow-50'
                            else: normal_bg = 'bg-gray-50'
                            bg_color = _ACTIVE_BG if is_active else normal_bg
                            day_card = ui.card().classes(f'h-32 {bg_color} p-1 flex flex-col justify-between border border-brown-300 overflow-hidden shadow-sm cursor-pointer hover:ring-2 hover:ring-green-500')
                            day_cards[(cell['year'], cell['month'], cell['day_num'])] = (day_card, normal_bg)
                            day_card.on('click', lambda c=cell: on_cell_click(c))
                            if cell['overflow'] == 'prev':
                                with day_card: ui.tooltip('Click to go to previous month')
                            elif cell['overflow'] == 'next':
                                with day_card: ui.tooltip('Click to go to next month')
                            with day_card:
                                with ui.row().classes('w-full justify-between items-center text-xs'):
                                    with ui.row().classes('items-center gap-1'):
                                        if cell['paksha_icon']:
                                            img_el = ui.image(f'/img/{cell["paksha_icon"]}').classes('w-3 h-3')
                                            with img_el: ui.tooltip('Paksha Phase')
                                        t_label = ui.label(cell['tithi']).classes('text-purple-700 font-bold text-[10px]')
                                        with t_label: ui.tooltip(cell['tithi_full'])
                                    with ui.row().classes('items-center gap-0.5'):
                                        sunrise_img = ui.image('/img/sunrise1.png').classes('w-3 h-3')
                                        with sunrise_img: ui.tooltip(f"Sunrise: {cell['sunrise']}")
                                        ui.label(cell['sunrise']).classes('text-[9px] text-gray-600')
                                with ui.row().classes('w-full justify-between items-center'):
                                    cal_day_label = ui.label(str(cell['cal_day'])).classes('text-sm font-bold text-red-600')
                                    with cal_day_label:
                                        ui.tooltip(current_cal_type_label() + ' ' + res_str('calendar_str', 'Calendar') + ' ' + res_str('date_str', 'date'))
                                    greg_label = ui.label(str(cell['day_num'])).classes('text-2xl font-extrabold text-black')
                                    with greg_label: ui.tooltip('Gregorian date')
                                if cell['festivals']:
                                    with ui.row().classes('w-full justify-center items-center gap-1'):
                                        if cell['tithi_icon']:
                                            t_icon = ui.image(f'/img/{cell["tithi_icon"]}').classes('w-4 h-4')
                                            with t_icon: ui.tooltip(cell['tithi_full'])
                                        for f in cell['festivals']:
                                            f_img = ui.image(f'/img/{f["icon"]}').classes('w-4 h-4')
                                            with f_img: ui.tooltip(f['tooltip'])
                                with ui.row().classes('w-full justify-between items-center text-xs'):
                                    with ui.row().classes('items-center gap-1'):
                                        if cell['nak_icon']:
                                            nak_img = ui.image(f'/img/{cell["nak_icon"]}').classes('w-3 h-3')
                                            with nak_img: ui.tooltip(cell['nak_short'])
                                        ui.label(cell['nak_short']).classes('text-green-700 font-bold text-[9px]')
                                    with ui.row().classes('items-center gap-0.5'):
                                        sunset_img = ui.image('/img/sunset1.png').classes('w-3 h-3')
                                        with sunset_img: ui.tooltip(f"Sunset: {cell['sunset']}")
                                        ui.label(cell['sunset']).classes('text-[9px] text-gray-600')
        ui.timer(0.1, generate_grid, once=True)
    render_footer()

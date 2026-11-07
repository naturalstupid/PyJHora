#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Vrathas page (/vratha).

Lists the days between two dates on which a vratha (observance) or a festival falls, for the entered place.

Controls: the vratha type (every key of vratha.special_vratha_map, plus "Customized"), the From and To dates
('Y,M,D'; default: today and one year later at the place) and, for "Customized", a search mode:
  - show all festivals: every festival of the festival file between the dates (vratha.search());
  - search by combination: the days on which the chosen tithi, nakshatra, yogam and Tamil month (each optional) occur
    together (vratha.search());
  - search by festival name: the festivals whose ENGLISH name contains the text typed, ignoring case
    (vratha.search(); the festival file column Festival_en is searched, whatever the page language is).
Any other type is found by vratha.special_vratha_dates().

Each result row shows the date, the time (the start or end time the vratha function returns, as h:m:s) and the
description. The count of different dates found is shown above the table. The description column takes the width
left by the other two.

The search runs in a worker thread, so that the page keeps answering the browser while it works. The shared
components.DelayedBusyIndicator shows a non-intrusive "please wait" message with a spinner (and a Stop button) -
only if the search is still running after a short delay - and disables the Compute button until the result
arrives; a second search cannot start meanwhile. The worker thread runs in a copy of the context of the page, so
the settings of the visitor apply inside calc_lock().

Stop (reachable once the message has been revealed) lets the visitor regain control at once (re-enables the
controls so the From/To dates, the vratha type or any other option can be changed and a new search started right
away) instead of waiting for a long search to finish. It cannot kill the worker thread itself - Python cannot
safely interrupt code that is in the middle of a calculation - so the abandoned search keeps running under
calc_lock() until it finishes on its own; a generation counter is used to discard its result silently when it
eventually arrives, so it never overwrites what is shown afterwards.

The first list is calculated when the page opens (Pradosham for the next year) and when another vratha type is chosen
(except "Customized"); the other controls clear the list, and Compute calculates again. A search holds the server
lock, so the span between the dates is limited to MAX_SPAN_DAYS (MAX_SPAN_DAYS_FESTIVALS for the searches of the
festival file).

The controls of the second row share the width of the window (each has a minimum width); the row scrolls sideways
only when even the minimum widths do not fit.
"""
import html
from datetime import datetime, timedelta, timezone
from nicegui import ui
from jhora import utils
from jhora.panchanga import vratha
drik = utils.hora_engine_proxy
from components import (
    navigation_header, render_control_bar, ensure_default_state,
    calc_lock, res_str, safe_notify, DelayedBusyIndicator, render_footer, 
)

CUSTOM_KEY = 'customized'
MODE_ALL, MODE_COMBINATION, MODE_NAME = 0, 1, 2
# Kept small on purpose: this is the span used to prefill the To date, and the page computes automatically on
# load (see the ui.timer() call at the end of vratha_page()). calc_lock() is a single, server-wide, non-reentrant
# lock shared with every other page, so a long automatic search here holds that lock and makes every other page
# the visitor (or anyone else) opens meanwhile wait behind it. A one-month default keeps that automatic search
# short; a visitor can still widen the From/To dates and press Compute for a bigger, deliberate search.
DEFAULT_SPAN_DAYS = 30
MAX_SPAN_DAYS = 731
MAX_SPAN_DAYS_FESTIVALS = 366
_CELL_STYLE = 'border:1px solid #d1d5db;padding:4px 8px;vertical-align:top;'


def _parse_date(text):
    """Returns the drik.Date of a 'Y,M,D' text.

    Args:
        text: year, month and day separated by commas; the year may be negative.

    Raises:
        ValueError: if the text is not three integers.
    """
    parts = [p.strip() for p in str(text or '').split(',')]
    if len(parts) != 3:
        raise ValueError('Enter the date as Year,Month,Day.')
    return drik.Date(int(parts[0]), int(parts[1]), int(parts[2]))


def _date_text(value):
    """Returns 'YYYY-MM-DD' for a date sequence (any elements after the first three, such as a time, are ignored)."""
    y, m, d = (int(x) for x in list(value)[:3])
    return f"{y:04d}-{m:02d}-{d:02d}"


def _time_text(value):
    """Returns h:m:s text for a time given in hours; '' for an empty value, str(value) if it is not a number."""
    if value is None or value == '':
        return ''
    try:
        return str(utils.to_dms(value))
    except Exception:
        return str(value)


def _format_results(vdates):
    """Returns (rows, count) for the result of a vratha search.

    Args:
        vdates: list of tuples (date, time, ..., description) as returned by jhora.panchanga.vratha. The time is
            the second element; the description is the last element (shown when the tuple has 3 or more elements).

    Returns:
        rows: list of (date text, time text, description).
        count: number of different dates.
    """
    rows = []
    dates = set()
    for values in vdates or []:
        date_key = tuple(int(x) for x in list(values[0])[:3])
        dates.add(date_key)
        time_text = _time_text(values[1]) if len(values) > 1 else ''
        description = str(values[-1]) if len(values) > 2 else ''
        rows.append((_date_text(values[0]), time_text, description))
    return rows, len(dates)


def _heading(text):
    """Returns a column heading without the trailing colon some resource strings carry."""
    return str(text).strip().rstrip(':').strip()


def _table_html(rows, headers):
    """Returns the HTML of the results table (inline styles, because the page CSS removes default table borders).

    The date and time columns are as narrow as their text; the last column (description) is given all the remaining
    width and wraps long text.

    Args:
        rows: list of (date text, time text, description).
        headers: the three column headings.
    """
    narrow = _CELL_STYLE + 'white-space:nowrap;width:1%;'
    wide = _CELL_STYLE + 'width:99%;word-break:break-word;'
    styles = (narrow, narrow, wide)
    head = ''.join(f"<th style='{styles[i]}background:#ecfdf5;text-align:left;'>{html.escape(_heading(h))}</th>"
                   for i, h in enumerate(headers))
    body = ''.join(
        '<tr>' + ''.join(f"<td style='{styles[i]}'>{html.escape(str(c))}</td>" for i, c in enumerate(row)) + '</tr>'
        for row in rows)
    return f"<table style='border-collapse:collapse;font-size:0.875rem;width:100%;'><tr>{head}</tr>{body}</table>"


def _search(place, start, end, kind, mode, name, indexes):
    """Finds the vratha dates. Call it inside calc_lock().

    Args:
        place: drik.Place of the location.
        start, end: drik.Date of the first and the last day.
        kind: a key of vratha.special_vratha_map, or CUSTOM_KEY.
        mode: MODE_ALL, MODE_COMBINATION or MODE_NAME (used for CUSTOM_KEY only).
        name: text the English festival name must contain (MODE_NAME).
        indexes: (tithi, nakshatra, yogam, tamil month) selector indexes; 0 means "not selected" (MODE_COMBINATION).

    Returns:
        List of tuples (date, time, ..., description), or None.
    """
    if kind != CUSTOM_KEY:
        return vratha.special_vratha_dates(place, start, end, kind)
    festival = (name or '').strip() if mode == MODE_NAME else None
    tithi, nakshatra, yogam, month = (None,) * 4
    if mode == MODE_COMBINATION:
        tithi, nakshatra, yogam, month = (i or None for i in indexes)
    return vratha.search(place, start, end, tithi, nakshatra, yogam, month, festival_name_contains=festival or None)


def _search_locked(place_args, start, end, kind, mode, name, indexes):
    """Runs _search() under calc_lock(); meant to run in a worker thread (see vratha_page()).

    Args:
        place_args: (name, latitude, longitude, time zone hours) of the location.
        start, end, kind, mode, name, indexes: see _search().

    Returns:
        The result of _search().
    """
    with calc_lock():
        place = drik.Place(*place_args, 0.0)
        return _search(place, start, end, kind, mode, name, indexes)


def _today_text(timezone_hours, days=0):
    """Returns the date 'Y,M,D' of today (plus `days`) at a time zone given in hours."""
    try:
        now = datetime.now(timezone(timedelta(hours=float(timezone_hours))))
    except (TypeError, ValueError):
        now = datetime.now()
    day = now + timedelta(days=days)
    return f"{day.year},{day.month},{day.day}"


def _span_days(start, end):
    """Returns the number of days from the drik.Date `start` to the drik.Date `end`."""
    return utils.julian_day_number(end, (0, 0, 0)) - utils.julian_day_number(start, (0, 0, 0))


@ui.page('/vratha')
def vratha_page():
    """Vrathas page: control bar, vratha type and search options, count and results table."""
    navigation_header()
    state = ensure_default_state()
    kind_options = {key: res_str(key + '_str', key.replace('_', ' ').title())
                    for key in list(vratha.special_vratha_map.keys()) + [CUSTOM_KEY]}
    mode_options = {
        MODE_ALL: res_str('show_all_festivals_str', 'Show all festivals'),
        MODE_COMBINATION: res_str('search_festival_by_combination_str', 'Search by combination'),
        MODE_NAME: res_str('search_festival_str', 'Search festival'),
    }
    tithi_options = {0: res_str('tithi_str', 'Tithi')}
    tithi_options.update({i + 1: label for i, label in enumerate(
        [utils.PAKSHA_LIST[0] + '-' + t for t in utils.TITHI_LIST[0:14]] + [utils.TITHI_LIST[14]] +
        [utils.PAKSHA_LIST[1] + '-' + t for t in utils.TITHI_LIST[0:14]] + [utils.TITHI_LIST[29]])})
    nakshatra_options = {0: res_str('nakshatra_str', 'Nakshatra')}
    nakshatra_options.update({i + 1: n for i, n in enumerate(utils.NAKSHATRA_LIST)})
    yogam_options = {0: res_str('yogam_str', 'Yogam')}
    yogam_options.update({i + 1: y for i, y in enumerate(utils.YOGAM_LIST)})
    month_options = {0: res_str('tamil_month_str', 'Tamil Month')}
    month_options.update({i + 1: m for i, m in enumerate(utils.MONTH_LIST)})

    with ui.column().classes('w-full p-2 gap-1'):
        ui.label(res_str('vrathas_str', 'Vrathas')).classes('text-xl font-bold text-green-700')
        w = render_control_bar(show_dob_tob=False, on_options_saved=lambda: show_hint(),
                               on_calculate=lambda: compute(),
                               calculate_label=res_str('compute_str', 'Compute'))
        # Row 2 never wraps: its widgets share the width (flex-grow with a minimum width); the row scrolls sideways
        # only when the minimum widths do not fit.
        w['row2'].classes(add='flex-nowrap overflow-x-auto', remove='flex-wrap')
        with w['row2']:
            kind_select = ui.select(options=kind_options, value=next(iter(kind_options)),
                                    label=res_str('vratha_str', 'Vratha')).props('outlined dense') \
                .classes('flex-[1.3] min-w-[8rem]')
            from_input = ui.input(res_str('starts_at_str', 'From'), value=_today_text(state.get('timezone'))) \
                .props('outlined dense').classes('flex-[0.8] min-w-[6.5rem]')
            to_input = ui.input(res_str('ends_at_str', 'To'),
                                value=_today_text(state.get('timezone'), DEFAULT_SPAN_DAYS)) \
                .props('outlined dense').classes('flex-[0.8] min-w-[6.5rem]')
            mode_select = ui.select(options=mode_options, value=MODE_ALL, label=res_str('search_str', 'Search')) \
                .props('outlined dense').classes('flex-[1.4] min-w-[8rem]')
            name_input = ui.input(res_str('festival_name_english_str', 'Festival name (English)'), value='') \
                .props('outlined dense').classes('flex-[1.2] min-w-[8rem]')
            with name_input:
                ui.tooltip(res_str('festival_name_english_tip_str',
                                   'Part of the English name of the festival, e.g. Deepam. Case is ignored.'))
            tithi_select = ui.select(options=tithi_options, value=0).props('outlined dense') \
                .classes('flex-[1.2] min-w-[6rem]')
            nakshatra_select = ui.select(options=nakshatra_options, value=0).props('outlined dense') \
                .classes('flex-1 min-w-[6rem]')
            yogam_select = ui.select(options=yogam_options, value=0).props('outlined dense') \
                .classes('flex-1 min-w-[6rem]')
            month_select = ui.select(options=month_options, value=0).props('outlined dense') \
                .classes('flex-1 min-w-[6rem]')
        ui.separator()
        stats_label = ui.label('').classes('font-bold text-green-700')
        # Non-intrusive "please wait" UI: stays hidden unless the search is still running after a short
        # delay (the default 30-day span normally finishes well within that - see
        # components.DelayedBusyIndicator), so a quick search never flashes a spinner at all.
        busy = DelayedBusyIndicator(
            buttons=w.get('calculate_button'),
            stop_label=res_str('stop_str', 'Stop'),
            stop_message=res_str(
                'vratha_stopped_str',
                'Stopped. The previous search keeps finishing quietly in the background and its result will be '
                'ignored. Change the options and press Compute to search again.'),
            on_stop=lambda: result_html.set_content(''),
        )
        with ui.column().classes('w-full max-h-[640px] overflow-y-auto'):
            result_html = ui.html('').classes('w-full')

    def _refresh_inputs():
        """Shows only the inputs that the selected type and search mode use."""
        custom = kind_select.value == CUSTOM_KEY
        mode_select.set_visibility(custom)
        name_input.set_visibility(custom and mode_select.value == MODE_NAME)
        for widget in (tithi_select, nakshatra_select, yogam_select, month_select):
            widget.set_visibility(custom and mode_select.value == MODE_COMBINATION)

    def show_hint():
        """Clears the results and tells how to calculate (does nothing while a search is running)."""
        if busy.is_busy:
            return
        stats_label.set_text('')
        result_html.set_content(res_str('vratha_hint_str', 'Choose the options, then press Compute.'))

    def _show_error(error):
        """Shows an error message; a client that has already gone away is ignored."""
        try:
            safe_notify(f'Error computing Vrathas: {str(error)}', type='negative')
            stats_label.set_text('')
            result_html.set_content(f'<span style="color:red">Error: {html.escape(str(error))}</span>')
        except RuntimeError:
            pass

    async def compute():
        """Reads the control bar and the options, then finds the dates in a worker thread (under calc_lock()) and
        shows the count and the table. A "please wait" message appears only if the search is still running
        after a short delay (the default 30-day span normally finishes well within that).
        """
        if busy.is_busy:
            safe_notify(res_str('vratha_busy_str', 'A search is already running. Please wait.'), type='warning')
            return
        try:
            start = _parse_date(from_input.value)
            end = _parse_date(to_input.value)
            kind = kind_select.value
            mode = mode_select.value
            festival_file_search = kind == CUSTOM_KEY and mode in (MODE_ALL, MODE_NAME)
            limit = MAX_SPAN_DAYS_FESTIVALS if festival_file_search else MAX_SPAN_DAYS
            span = _span_days(start, end)
            if span < 0:
                raise ValueError('The To date must not be before the From date.')
            if span > limit:
                raise ValueError(f'Search at most {limit} days at a time.')
            place_args = (w['place_select'].value.strip() if w['place_select'].value else 'Chennai',
                          float(w['lat_input'].value.strip()), float(w['lon_input'].value.strip()),
                          float(w['tz_input'].value.strip()))
            indexes = (tithi_select.value, nakshatra_select.value, yogam_select.value, month_select.value)
            name = name_input.value
            no_dates = res_str('no_matching_dates_found_str', 'No matching dates found')
            found = res_str('matching_dates_found_str', 'matching dates found')
            headers = (res_str('date_str', 'Date'), res_str('time_str', 'Time'),
                       res_str('description_str', 'Description'))
            wait_text = res_str('vratha_wait_str', 'Searching... this can take a while. Please wait for the results.')
        except Exception as e:
            _show_error(e)
            return
        stats_label.set_text('')
        result_html.set_content('')
        try:
            vdates = await busy.run(_search_locked, place_args, start, end, kind, mode, name, indexes,
                                    wait_text=wait_text)
        except Exception as e:
            _show_error(e)
            return
        if vdates is DelayedBusyIndicator.STOPPED:
            return  # Stop (or a newer search) superseded this one; discard the stale result quietly
        rows, count = _format_results(vdates)
        if not rows:
            stats_label.set_text(no_dates)
            result_html.set_content('')
        else:
            stats_label.set_text(f"{count} {found}")
            result_html.set_content(_table_html(rows, headers))

    async def _on_kind_changed():
        _refresh_inputs()
        if kind_select.value == CUSTOM_KEY:
            show_hint()
        else:
            await compute()

    def _on_search_option_changed():
        _refresh_inputs()
        show_hint()

    kind_select.on_value_change(lambda e: _on_kind_changed())
    mode_select.on_value_change(lambda e: _on_search_option_changed())
    for widget in (name_input, tithi_select, nakshatra_select, yogam_select, month_select):
        widget.on_value_change(lambda e: show_hint())
    _refresh_inputs()
    ui.timer(0.1, compute, once=True)
    render_footer()
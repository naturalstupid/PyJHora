#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Pancha Pakshi Sastra page (/pancha_pakshi).

Shows the Pancha Pakshi schedule for the entered date, time and place and the chosen birth bird
(default 1, Vulture), computed by pancha_paksha.construct_pancha_pakshi_information().

Each parent row is one main-activity period, collapsed to a summary row. The parent row that contains
the current moment (in the place's local time) is expanded automatically and shows its sub-bird rows,
with a sandclock on the sub-period running now. Clicking a parent row expands it and collapses the
others. A timer re-checks every 60 seconds, so the expanded row and the sandclock follow the clock -
starting from the entered Date/Time (not necessarily the real-world moment) and advancing from there by
the real elapsed time since the schedule was computed; see _reference_moment()/_resync_timer().

Columns: start, end, duration, main bird, main activity, sub bird, sub activity, relation, power,
effect and rating; power and rating are drawn as progress bars. All rows share one CSS grid template
so the columns align.

Timezone/DST: the Timezone field shown in the control bar may be a stale, non-DST-aware value (e.g.
auto-filled from a place search at some earlier/unrelated moment). Rather than trust it, compute_pps()
recomputes the UTC offset itself from the place's latitude/longitude using
utils.get_place_timezone_offset(lat, lon, jd_local=<entered Date/Time>) - which correctly resolves
standard vs. daylight time *for the date actually being queried*, not for whenever the offset happened
to be looked up - and uses that corrected value (reflecting it back into the Timezone field) instead of
whatever was already in the field. See _corrected_tz_offset()/_pps_locked().

The Date, Time and Place fields of this page are independent of the other pages (isolated=True):
edits here do not change the other pages and the other way round. The default date and time are the
current local time at the seeded place. Icons are served from the '/img' static mount of main.py.
"""
from datetime import datetime, timedelta
from nicegui import ui
from jhora import utils
from jhora.panchanga import pancha_paksha
drik = utils.hora_engine_proxy
from components import (
    navigation_header, render_control_bar, ensure_default_state,
    calc_lock, res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
    render_footer,
)
def _corrected_tz_offset(lat, lon, jd_local, fallback):
    """Returns the UTC offset (hours) for (lat, lon) at the instant `jd_local`, correctly resolving
    standard vs. daylight time *for that date* - unlike a stale/auto-filled offset that may have been
    looked up at an unrelated moment (e.g. "today", rather than the date actually being queried).

    Uses utils.get_place_timezone_offset(), which internally uses TimezoneFinder + pytz against the
    given jd_local (see that function's docstring). Falls back to `fallback` (the value already in the
    Timezone field) only if the lookup raises; get_place_timezone_offset() itself already has its own
    internal fallback (+5.0) for lookup failures, which is intentionally NOT used here, since the
    visitor's own entered/auto-filled offset is a better guess than a hardcoded default.
    """
    try:
        return float(utils.get_place_timezone_offset(lat, lon, jd_local=jd_local))
    except Exception as e:
        print(f"[pancha_pakshi_page] _corrected_tz_offset failed, keeping entered value {fallback}: {e}")
        return fallback
def _pps_locked(dob, tob, lat, lon, place_name, tz_fallback, bird_index):
    """Computes the Pancha Pakshi schedule under calc_lock(); the slow part of compute_pps(), run in a
    worker thread via components.DelayedBusyIndicator.run().

    The UTC offset used for the Place passed to construct_pancha_pakshi_information() is recomputed
    here from (lat, lon) for the entered date (see _corrected_tz_offset()) rather than trusting
    `tz_fallback` (whatever was already sitting in the Timezone field), so the schedule's own internal
    time arithmetic is anchored to the correct standard/daylight offset for the date being queried.

    Returns:
        (schedule_result, tz_offset_used) - schedule_result is construct_pancha_pakshi_information()'s
        return value; tz_offset_used is the corrected offset actually used, so the caller can reflect it
        back into the Timezone field for the visitor to see.
    """
    with calc_lock():
        jd_local = utils.julian_day_number(dob, tob)
        tz_offset_used = _corrected_tz_offset(lat, lon, jd_local, tz_fallback)
        place = drik.Place(place_name, lat, lon, tz_offset_used, 0.0)
        schedule_result = pancha_paksha.construct_pancha_pakshi_information(
            dob, tob, place, nakshathra_bird_index=bird_index)
        return schedule_result, tz_offset_used
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# Pixel widths of the 11 columns (start, end, duration, main bird, main activity, sub bird, sub activity,
# relation, power, effect, rating), shared by the header row and every data row.
_COL_WIDTHS_PX = [168, 168, 96, 148, 160, 148, 160, 112, 104, 148, 104]
_GRID_TEMPLATE = ' '.join(f'{w}px' for w in _COL_WIDTHS_PX)
def _clean_text(text):
    """Returns `text` on one line: backslash-n escape sequences and newlines are replaced by a space."""
    return str(text).replace('\\n', ' ').replace('\n', ' ').strip()
def _css_color(color):
    """Returns a CSS-valid color keyword by removing spaces ('light green' -> 'lightgreen'); None for an empty value."""
    if not color:
        return None
    return str(color).replace(' ', '')
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
        if len(parts) == 2:
            parts.append(0)
        if len(parts) != 3:
            raise ValueError
        return tuple(parts)
    except Exception:
        return fallback
def _bird_label(i):
    """Returns the localized name of the bird at index `i` of pancha_paksha.pancha_pakshi_birds."""
    name = pancha_paksha.pancha_pakshi_birds[i]
    return res_str(name + '_str', name.title())
def _cell(value):
    """Splits a raw cell value of construct_pancha_pakshi_information() into (icon_url, text, css_color).

    The value is a string, (icon, text) or (icon, text, color). icon_url is '/img/<icon>' or None, text is
    cleaned with _clean_text() and css_color is None unless a color is given.
    """
    if isinstance(value, tuple):
        if len(value) == 3:
            icon, text, color = value
            return (f'/img/{icon}' if icon else None, _clean_text(text), _css_color(color))
        icon, text = value
        return (f'/img/{icon}' if icon else None, _clean_text(text), None)
    return (None, _clean_text(value), None)
def _default_dob_tob_strings(tz_offset_hours):
    """Returns (dob, tob) for the current local date and time at the place, as 'Y,M,D' and 'HH:MM:SS'.

    Args:
        tz_offset_hours: time-zone offset of the place in hours.
    """
    try:
        offset = float(tz_offset_hours)
    except Exception:
        offset = 0.0
    now_local = datetime.utcnow() + timedelta(hours=offset)
    dob_str = f'{now_local.year},{now_local.month},{now_local.day}'
    tob_str = now_local.strftime('%H:%M:%S')
    return dob_str, tob_str
def _now_within(start_text, end_text, reference_now):
    """Returns True if `reference_now` lies within [start, end]; False if either text cannot be parsed.

    Args:
        start_text, end_text: times in _DATE_FORMAT.
        reference_now: datetime to test.
    """
    try:
        start = datetime.strptime(start_text, _DATE_FORMAT)
        end = datetime.strptime(end_text, _DATE_FORMAT)
        return start <= reference_now <= end
    except Exception:
        return False
def _find_current_group_index(top_level_list, reference_now):
    """Returns the index of the parent row whose [start, end] window contains `reference_now`, or None.

    Args:
        top_level_list: parent rows from construct_pancha_pakshi_information().
        reference_now: datetime to test.
    """
    for idx, parent_row in enumerate(top_level_list):
        _s_icon, start_text, _sc = _cell(parent_row[0])
        _e_icon, end_text, _ec = _cell(parent_row[1])
        if _now_within(start_text, end_text, reference_now):
            return idx
    return None
def _grid_row(extra_classes=''):
    """Creates a CSS-grid row with the template _GRID_TEMPLATE, so the header and all data rows share the
    same column boundaries. Use it as a context manager.

    Args:
        extra_classes: additional CSS classes.
    """
    return ui.element('div').classes(f'grid items-center w-max {extra_classes}') \
        .style(f'grid-template-columns:{_GRID_TEMPLATE}; column-gap:6px;')
def _progress_cell(raw_value, *, as_fraction):
    """Draws a percentage label and a progress bar in the current cell; draws nothing if `raw_value` is
    '' or None.

    Args:
        raw_value: power factor (0..1) or rating (0..10).
        as_fraction: True if raw_value is already 0..1, False if it is on a 0..10 scale.
    """
    if raw_value in ('', None):
        return
    try:
        v = float(raw_value)
    except Exception:
        return
    frac = v if as_fraction else v / 10.0
    frac = max(0.0, min(1.0, frac))
    with ui.column().classes('w-full gap-0'):
        ui.label(f'{round(frac * 100)}%').classes('text-[10px] text-gray-600')
        ui.linear_progress(value=frac, show_value=False) \
            .classes('w-full').props('color=green track-color=grey-4 size=8px')
@ui.page('/pancha_pakshi')
def pancha_pakshi_page():
    """Pancha Pakshi page: control bar, birth bird selector, schedule tree and the 60-second timer."""
    navigation_header()
    state = ensure_default_state()
    pps_state = {"headers": None, "top_level": None, "child_level": None,
                 "parent_labels": None, "error": None, "expanded_index": None,
                 "tz_offset": 0.0, "reference_moment": None, "reference_computed_at": None}
    _pps_str = res_str('pancha_pakshi_sastra_str', 'Pancha Pakshi Sastra')
    with ui.column().classes('w-full p-2 gap-1'):
        ui.label(_pps_str).classes('text-xl font-bold text-green-700')
        # isolated=True: the Place / Date / Time widgets are bound to a page-local copy of the shared state, so edits here
        # do not affect other pages and the other way round. initial_overrides sets the default date and time to the
        # current time in the seeded place's time zone (the shared state's time zone is only read to compute it).
        try:
            _seed_tz = float(state.get("timezone", 0.0))
        except Exception:
            _seed_tz = 0.0
        _default_dob, _default_tob = _default_dob_tob_strings(_seed_tz)
        w = render_control_bar(
            show_dob_tob=True, on_options_saved=lambda: compute_pps(),
            on_calculate=lambda: compute_pps(),
            calculate_label=res_str('compute_str', 'Compute'),
            isolated=True,
            initial_overrides={"date_dob": _default_dob, "time_tob": _default_tob},
        )
        with w['row2']:
            bird_options = {i + 1: _bird_label(i) for i in range(len(pancha_paksha.pancha_pakshi_birds))}
            bird_select = ui.select(options=bird_options, value=1,
                                     label=res_str('birth_bird_str', 'Birth Bird')) \
                .props('outlined dense').classes('w-48')
        ui.separator()
        busy = DelayedBusyIndicator(buttons=w.get('calculate_button'), stop_label=res_str('stop_str', 'Stop'))
        def _reference_moment():
            """Returns the current reference moment used for highlighting: the entered Date/Time,
            advanced by the real elapsed wall-clock time since it was last computed by compute_pps() (or
            by a resync). This way the sandclock/auto-expand track forward from whatever moment the
            visitor typed into the Date/Time fields - not from the real-world "now" - while still
            ticking forward live, exactly like a clock started at that entered moment.

            Returns None if no schedule has been computed yet (nothing to reference against).
            """
            base = pps_state.get("reference_moment")
            if base is None:
                return None
            computed_at = pps_state.get("reference_computed_at")
            if computed_at is None:
                return base
            elapsed = datetime.utcnow() - computed_at
            return base + elapsed
        scroll_container = ui.element('div').classes('w-full overflow-x-auto')
        def _render_cells(row, *, bold, is_now):
            """Draws the 11 cells of one data row in column order: start, end, duration, main bird, main activity,
            sub bird, sub activity, relation, power, effect, rating.

            Args:
                row: row from construct_pancha_pakshi_information().
                bold: parent (summary) row style.
                is_now: show the sandclock in the start cell.
            """
            start_icon, start_text, _sc = _cell(row[0])
            end_icon, end_text, _ec = _cell(row[1])
            _di, dur_text, _dc = _cell(row[2])
            mb_icon, mb_text, _mbc = _cell(row[3])
            ma_icon, ma_text, ma_color = _cell(row[4])
            sb_icon, sb_text, _sbc = _cell(row[5])
            sa_icon, sa_text, sa_color = _cell(row[6])
            rel_icon, rel_text, rel_color = _cell(row[7])
            pf_val = row[8]
            eff_icon, eff_text, eff_color = _cell(row[9])
            rtng_val = row[10]
            label_cls = ('font-bold text-brown-800 ' if bold else '') + 'text-xs'
            # col 1: start (+ sandclock / start icon)
            with ui.row().classes('items-center gap-1'):
                if is_now:
                    ui.image('/img/sandclock.gif').classes('w-4 h-4 shrink-0')
                elif start_icon:
                    ui.image(start_icon).classes('w-4 h-4 shrink-0')
                ui.label(start_text).classes(label_cls)
            # col 2: end
            ui.label(end_text).classes(label_cls)
            # col 3: duration
            ui.label(dur_text).classes(label_cls)
            # col 4: main bird
            with ui.row().classes('items-center gap-1'):
                if mb_icon:
                    ui.image(mb_icon).classes('w-4 h-4 shrink-0')
                ui.label(mb_text).classes(label_cls)
            # col 5: main activity (colored badge)
            with ui.row().classes('items-center gap-1 rounded px-1') \
                    .style(f'background-color:{ma_color}' if ma_color else ''):
                if ma_icon:
                    ui.image(ma_icon).classes('w-4 h-4 shrink-0')
                ui.label(ma_text).classes(label_cls)
            # col 6: sub bird
            with ui.row().classes('items-center gap-1'):
                if sb_icon:
                    ui.image(sb_icon).classes('w-4 h-4 shrink-0')
                ui.label(sb_text).classes(label_cls)
            # col 7: sub activity (colored badge)
            with ui.row().classes('items-center gap-1 rounded px-1') \
                    .style(f'background-color:{sa_color}' if sa_color else ''):
                if sa_icon:
                    ui.image(sa_icon).classes('w-4 h-4 shrink-0')
                ui.label(sa_text).classes(label_cls)
            # col 8: relation (colored badge)
            with ui.row().classes('items-center gap-1 rounded px-1') \
                    .style(f'background-color:{rel_color}' if rel_color else ''):
                ui.label(rel_text).classes(label_cls)
            # col 9: power (progress bar - child rows only have a value)
            _progress_cell(pf_val, as_fraction=True)
            # col 10: effect (colored badge)
            with ui.row().classes('items-center gap-1 rounded px-1') \
                    .style(f'background-color:{eff_color}' if eff_color else ''):
                ui.label(eff_text).classes(label_cls)
            # col 11: rating (progress bar - child rows only have a value)
            _progress_cell(rtng_val, as_fraction=False)
        @ignore_disconnected_client
        def _on_parent_row_clicked(p_idx):
            """Expands parent row `p_idx` (collapsing the others), or collapses it if it is already expanded, and
            redraws.
            """
            pps_state["expanded_index"] = None if pps_state["expanded_index"] == p_idx else p_idx
            _render_tree()
        def _render_tree():
            """Redraws the schedule from the stored data; the current sub-period is marked with the sandclock."""
            reference_now = _reference_moment()
            scroll_container.clear()
            with scroll_container:
                if pps_state["error"]:
                    ui.label(pps_state["error"]).classes('text-red-600')
                    return
                if not pps_state["top_level"]:
                    ui.label('Click "Show" to compute the Pancha Pakshi schedule.').classes('text-gray-500')
                    return
                headers = [_clean_text(h) for h in pps_state["headers"]]
                with _grid_row('font-bold text-green-700 border-b-2 border-green-700 pb-1 mb-1'):
                    for h in headers:
                        ui.label(h).classes('text-xs')
                expanded_idx = pps_state["expanded_index"]
                for p_idx, parent_row in enumerate(pps_state["top_level"]):
                    labels = pps_state["parent_labels"][p_idx]
                    is_expanded = (p_idx == expanded_idx)
                    with ui.column().classes('w-max gap-0'):
                        with ui.row().classes('items-center gap-3 flex-wrap text-xs pt-2'):
                            for (text, icon) in labels:
                                with ui.row().classes('items-center gap-1'):
                                    if icon:
                                        ui.image(f'/img/{icon}').classes('w-4 h-4')
                                    ui.label(_clean_text(text)).classes('font-bold text-brown-800')
                        box_classes = ('w-max border-2 border-green-600 bg-emerald-50 rounded p-2 gap-1'
                                       if is_expanded else 'w-max gap-1 cursor-pointer hover:bg-gray-50')
                        with ui.column().classes(box_classes) as group_box:
                            if not is_expanded:
                                group_box.on('click', lambda i=p_idx: _on_parent_row_clicked(i))
                            with ui.row().classes('items-center gap-1 w-max'):
                                chevron = ui.icon('expand_more' if is_expanded else 'chevron_right') \
                                    .classes('text-gray-600 cursor-pointer shrink-0')
                                chevron.on('click', lambda i=p_idx: _on_parent_row_clicked(i))
                                with _grid_row():
                                    _render_cells(parent_row, bold=True, is_now=False)
                            if is_expanded:
                                ui.separator()
                                for child_row in pps_state["child_level"][p_idx]:
                                    c_start_text = _cell(child_row[0])[1]
                                    c_end_text = _cell(child_row[1])[1]
                                    is_now = reference_now is not None and _now_within(c_start_text, c_end_text, reference_now)
                                    with ui.row().classes(
                                        'items-center gap-1 w-max rounded ' +
                                        ('bg-blue-50 ring-1 ring-blue-400' if is_now else '')
                                    ):
                                        ui.element('div').classes('w-5 shrink-0')
                                        with _grid_row():
                                            _render_cells(child_row, bold=False, is_now=is_now)
        @ignore_disconnected_client
        async def compute_pps():
            """Reads the control bar, computes the schedule in a worker thread (showing a non-intrusive
            "please wait" message via DelayedBusyIndicator only if it takes more than a moment), expands
            the parent row that contains the current moment and draws the tree.

            The "current moment" used for highlighting is the entered Date/Time - not the real-world
            clock - so that typing a specific time (e.g. to check a different place/time) is honored by
            the sandclock/auto-expand instead of being silently overridden by "now". See
            _reference_moment() for how this then keeps advancing live after this computation.

            The UTC offset used to build the schedule is recomputed from the place's latitude/longitude
            for the entered date (see _corrected_tz_offset()/_pps_locked()), overriding whatever was
            already in the Timezone field, and the field is updated to show the corrected value - so a
            stale or non-DST-aware offset never silently skews the schedule.
            """
            if busy.is_busy:
                safe_notify('Already computing. Please wait.', type='warning')
                return
            try:
                # The values come from this page's own widgets (isolated=True), so they are page-local.
                dob_val = w['dob_input'].value.strip()
                tob_val = w['tob_input'].value.strip()
                place_val = w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
                lat_val = float(w['lat_input'].value.strip())
                lon_val = float(w['lon_input'].value.strip())
                tz_val = float(w['tz_input'].value.strip())
                year, month, day = dob_val.split(",")
                dob = drik.Date(int(year), int(month), int(day))
                tob = _parse_tob(tob_val)
                bird_index = bird_select.value if isinstance(bird_select.value, int) else 1
                # The reference moment for highlighting is the entered Date/Time itself (not
                # datetime.utcnow()), so the sandclock/auto-expand reflect what was actually typed.
                entered_moment = datetime(int(year), int(month), int(day), tob[0], tob[1], tob[2])
            except Exception as e:
                pps_state.update({"headers": None, "top_level": None, "child_level": None,
                                   "parent_labels": None, "expanded_index": None,
                                   "error": f"(error computing Pancha Pakshi Sastra: {e})"})
                _render_tree()
                safe_notify(f'Error computing Pancha Pakshi Sastra: {str(e)}', type='negative')
                return
            try:
                result = await busy.run(_pps_locked, dob, tob, lat_val, lon_val, place_val, tz_val, bird_index,
                                        wait_text=res_str('computing_str', 'Computing... please wait.'))
            except Exception as e:
                pps_state.update({"headers": None, "top_level": None, "child_level": None,
                                   "parent_labels": None, "expanded_index": None,
                                   "error": f"(error computing Pancha Pakshi Sastra: {e})"})
                _render_tree()
                safe_notify(f'Error computing Pancha Pakshi Sastra: {str(e)}', type='negative')
                return
            if result is DelayedBusyIndicator.STOPPED:
                return
            (headers, top_level_list, child_level_list, parent_level_labels), tz_offset_used = result
            if abs(tz_offset_used - tz_val) > 0.01:
                # The corrected, DST-aware offset differs from what was in the field (e.g. a stale
                # auto-filled value) - reflect the correction in the field and tell the visitor why the
                # schedule may look different from what the previous offset would have produced.
                w['tz_input'].value = str(tz_offset_used)
                safe_notify(
                    f'Timezone adjusted from {tz_val:g} to {tz_offset_used:g} to account for daylight '
                    f'saving time on the entered date.', type='info')
            pps_state.update({
                "headers": headers, "top_level": top_level_list,
                "child_level": child_level_list, "parent_labels": parent_level_labels,
                "error": None, "tz_offset": tz_offset_used,
                "reference_moment": entered_moment, "reference_computed_at": datetime.utcnow(),
            })
            # Expand the group that contains the entered moment (see _reference_moment()).
            reference_now = _reference_moment()
            pps_state["expanded_index"] = _find_current_group_index(top_level_list, reference_now)
            _render_tree()
        @ignore_disconnected_client
        def _resync_timer():
            """Timer callback (every 60 s): finds the parent row that contains the current reference
            moment (the entered Date/Time, advanced by real elapsed time - see _reference_moment()),
            expands it and redraws, so the highlighted sub-period and the sandclock advance live from
            whatever moment was entered. Uses the stored data; nothing is recomputed.
            """
            if not pps_state["top_level"]:
                return
            reference_now = _reference_moment()
            if reference_now is None:
                return
            current_idx = _find_current_group_index(pps_state["top_level"], reference_now)
            pps_state["expanded_index"] = current_idx
            _render_tree()
        ui.timer(60.0, _resync_timer)
        ui.timer(0.1, compute_pps, once=True)
    render_footer()
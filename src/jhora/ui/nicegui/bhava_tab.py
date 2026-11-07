#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bhava (house) chart page (/bhava).
Shows the bhava chart of the chosen divisional chart in the chosen chart style (South Indian regular
and irregular, North Indian, East Indian with / without frame, Western, and Sudarsana Chakra) and a
table of the 12 houses (start, middle, end and planets). "Chart Options" selects the calculation
method of the divisional chart.
The house system can be chosen only with the Drik astrology model, which supports all of them; with
the other models the default house system (const.bhaava_madhya_method) is always used.
Sudarsana Chakra's three rings are built here from horo.get_bhava_chart_information() (the same
house-system-aware call used for the Bhava Information table) rather than
sudharsana_chakra.sudharshana_chakra_chart() - that library helper only builds whole-sign rasi rings
from charts.divisional_chart() and has no bhaava_madhya_method parameter at all, so it never reflects
the selected House System. See _sc_rings_with_house_system() below for details.
The chart-drawing code is shared with kundali_chart.py via chart_render.py (this page has no
chart-menu overlay of its own, so it always draws with overlay=None / no overlay table).
"Print / Save as PDF" prints the currently displayed chart - this page intentionally has no
"Save All Vargas" mode (unlike Kundali): only the current selection is meant to be printed.
"""
from nicegui import ui
from jhora import const, utils, config
from jhora.horoscope import info as horo_info
drik = utils.hora_engine_proxy
from components import (
    navigation_header, render_control_bar, ensure_default_state,
    calc_lock, res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator, print_button,
    render_footer, 
)
import chart_render as cr
_division_chart_factors = const.division_chart_factors
def _sc_rings_with_house_system(horo, jd, place, dcf, chart_method, bhaava_madhya_method, years_from_dob=1):
    """Builds Sudarsana Chakra ring data - same [lagna_chart, moon_chart, sun_chart, retrograde_planets]
    shape as sudharsana_chakra.sudharshana_chakra_chart() - but with each ring's 12 houses assigned by
    the selected house system (bhaava_madhya_method), instead of that library function's naive
    whole-sign-only rings (it calls utils.get_house_planet_list_from_planet_positions(), which has no
    house-system awareness at all, so Sudarsana Chakra never used to move when the House System
    selector changed).
    Preserves the chart's Tajaka (solar-return) basis: like the library function, planetary positions
    are evaluated one year after birth (years_from_dob, default 1 to match it), not at birth.
    Args:
        horo: the page's horo_info.Horoscope instance (reused so lat/long/tz/date match the visitor).
        jd: natal julian day (birth moment) - used only to compute the solar-return julian day.
        place: drik.Place of birth.
        dcf, chart_method: divisional chart factor and calculation method, same as elsewhere on this page.
        bhaava_madhya_method: selected house system key (or the default, already resolved by the caller).
        years_from_dob: which solar return to use; 1 matches the library function's own default.
    Returns:
        [lagna_chart, moon_chart, sun_chart, retrograde_planets] in the format render_sudarsana_chakra()
        expects: each of the first three is 12 (absolute rasi index, raw cell text) tuples indexed by
        house from that reference point (index 0 is the reference point's own house).
    """
    from jhora.horoscope.dhasa import sudharsana_chakra as sc_mod
    try:
        # Private helper the library itself always calls before next_solar_date(); best-effort, since
        # it is not part of the public API - if it ever disappears/changes, fall back to proceeding
        # without it rather than breaking the whole chart.
        sc_mod._set_year_duration(jd, place, use_sidereal=False, dhasa_duration_type=None, savana_year_method=None)
    except Exception as e:
        print(f"[bhava_page] sudharsana_chakra._set_year_duration failed, continuing without it: {e}")
    jd_at_years = drik.next_solar_date(jd, place, years=years_from_dob, use_sidereal=False)
    chart_1d_sc, _info_sc, asc_rasi_sc = horo.get_bhava_chart_information(
        jd_at_years, place, divisional_chart_factor=dcf,
        bhaava_madhya_method=bhaava_madhya_method, chart_method=chart_method,
    )
    # Moon's/Sun's own bhava bucket under this house system - a planet can sit in a different rasi
    # bucket than its natal rasi when the house cusps don't align with sign boundaries, so (as with
    # Lagna) we read off whichever bucket get_bhava_chart_information() actually placed them in,
    # rather than assuming it always equals their rasi.
    moon_name, sun_name = utils.PLANET_NAMES[const.MOON_ID], utils.PLANET_NAMES[const.SUN_ID]
    moon_rasi_sc = next((r for r, cell in enumerate(chart_1d_sc) if moon_name in cell), asc_rasi_sc)
    sun_rasi_sc = next((r for r, cell in enumerate(chart_1d_sc) if sun_name in cell), asc_rasi_sc)
    def _ring(start_rasi):
        return [((start_rasi + p) % 12, chart_1d_sc[(start_rasi + p) % 12]) for p in range(12)]
    retrograde_planets = drik.planets_in_retrograde(jd_at_years, place)
    return [_ring(asc_rasi_sc), _ring(moon_rasi_sc), _ring(sun_rasi_sc), retrograde_planets]
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
def _house_system_items():
    """Returns (keys, labels) of const.available_house_systems(), in the same order, for the house-system selector."""
    systems = const.available_house_systems()
    keys = list(systems.keys())
    labels = [systems[k] for k in keys]
    return keys, labels
def _bhava_locked(dob, tob, place_val, lat_val, lon_val, tz_val, dcf, chart_method,
                   house_select_idx, house_keys, default_house_idx, chart_style):
    """Computes the bhava chart and its information table under calc_lock().
    This is the slow part of compute_bhava(); pulled out to a plain, blocking function so it can run in
    a worker thread via components.DelayedBusyIndicator.run(); a non-intrusive "please wait" message
    then appears only if this turns out to take more than a moment.
    Args:
        house_select_idx: index selected in the House System selector, or None/invalid to use the default.
        house_keys, default_house_idx: const.available_house_systems() keys and the default index.
        chart_style: const.CHART_STYLE value currently selected; when it is SUDARSANA_CHAKRA the three
            concentric bhava rings (Lagna / Moon / Sun) are also computed here via
            _sc_rings_with_house_system(), so that chart style reflects the selected house system too.
    Returns:
        (chart_1d, bhava_chart_info, bhava_ascendant_house, used_default_house_system, sc_rings): the
        used_default_house_system flag is True when the selected house system was not supported and
        the default was used instead; sc_rings is None unless chart_style is SUDARSANA_CHAKRA.
    """
    with calc_lock():  # read inside calc_lock() so the visitor's astrology engine and default house system apply
        is_drik = utils.astro_engine_is_drik()
        visitor_default_bm = const.bhaava_madhya_method
        if is_drik:
            h_idx = house_select_idx if isinstance(house_select_idx, int) else default_house_idx
            if not (0 <= h_idx < len(house_keys)):
                h_idx = default_house_idx
            bhaava_madhya_method = house_keys[h_idx]
        else:
            # Other astrology models: always use the default house system.
            bhaava_madhya_method = visitor_default_bm
        horo = horo_info.Horoscope(
            latitude=lat_val, longitude=lon_val, timezone_offset=tz_val,
            date_in=drik.Date(*dob), birth_time=f"{tob[0]:02d}:{tob[1]:02d}:{tob[2]:02d}",
            calculation_type='drik', language=const._DEFAULT_LANGUAGE,
        )
        jd = utils.julian_day_number(drik.Date(*dob), tob)
        place = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
        used_default_house_system = False
        try:
            bhava_chart_data, bhava_chart_info, bhava_ascendant_house = horo.get_bhava_chart_information(
                jd, place, divisional_chart_factor=dcf,
                bhaava_madhya_method=bhaava_madhya_method, chart_method=chart_method,
            )
        except AttributeError as e:
            # The selected house system is not supported by the current model: retry with the default house system.
            print(f"[bhava_page] get_bhava_chart_information with bhaava_madhya_method={bhaava_madhya_method} not supported: {e}; retrying with default.")
            bhaava_madhya_method = const.bhaava_madhya_method
            bhava_chart_data, bhava_chart_info, bhava_ascendant_house = horo.get_bhava_chart_information(
                jd, place, divisional_chart_factor=dcf,
                bhaava_madhya_method=bhaava_madhya_method, chart_method=chart_method,
            )
            used_default_house_system = True
        # Remove trailing '/' separators from each house's planet string.
        chart_1d = [x.rstrip('/') for x in bhava_chart_data]
        sc_rings = None
        if chart_style == const.CHART_STYLE.SUDARSANA_CHAKRA:
            sc_rings = _sc_rings_with_house_system(horo, jd, place, dcf, chart_method, bhaava_madhya_method)
    return chart_1d, bhava_chart_info, bhava_ascendant_house, used_default_house_system, sc_rings
@ui.page('/bhava')
def bhava_page():
    """Bhava page: control bar, chart style / varga / house system selectors, bhava information table and chart."""
    navigation_header()
    state = ensure_default_state()
    bhava_state = {"bhava_chart_data": None, "bhava_ascendant_house": None, "bhava_chart_info": None,
                   "sc_rings": None}
    chart_options_state = {}  # chart_method chosen in the Chart Options dialog (1-based), per varga index
    _chart_style_options = {i: cr.chart_style_label(s) for i, s in enumerate(const.AVAILABLE_CHART_STYLES.keys())}
    _chart_style_keys = list(const.AVAILABLE_CHART_STYLES.keys())
    _varga_options = {i: cr.varga_label(i) for i in range(len(_division_chart_factors))}
    _house_keys, _house_labels = _house_system_items()
    _house_options = {i: lbl for i, lbl in enumerate(_house_labels)}
    with calc_lock():  # read inside calc_lock() so the visitor's own setting applies
        _visitor_bhaava_method = const.bhaava_madhya_method
    try:
        _default_house_idx = _house_keys.index(_visitor_bhaava_method)
    except ValueError:
        _default_house_idx = 0
    # Chart style index stored in the page state, so Kundali, Bhava and Ashtakavarga stay in sync across pages.
    saved_style_index = state.get('kundali_chart_style_index', 0)
    _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
    try:
        saved_style_index = int(saved_style_index)
        if saved_style_index not in range(len(const.AVAILABLE_CHART_STYLES)):
            saved_style_index = 0
    except Exception:
        saved_style_index = 0
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('bhaava_str', 'Bhava Chart')).classes('text-xl font-bold text-green-700')
            print_button()
        w = render_control_bar(show_dob_tob=True, on_options_saved=lambda: compute_bhava(),
                                on_calculate=lambda: compute_bhava())
        with w['row2']:
            chart_style_select = ui.select(options=_chart_style_options, value=saved_style_index, label='Chart Style').props('outlined dense').classes('w-48')
            varga_select = ui.select(options=_varga_options, value=0, label='Varga (Divisional Chart)').props('outlined dense').classes('w-56')
            chart_options_button = ui.button(_chart_options_nls, on_click=lambda: _open_chart_options_dialog()).props('outlined dense')
            with chart_options_button:
                chart_options_tooltip = ui.tooltip('')
            house_system_select = ui.select(options=_house_options, value=_default_house_idx, label='House System').props('outlined dense').classes('w-56')
            with house_system_select:
                house_system_tooltip = ui.tooltip('')
        ui.separator()
        # Non-intrusive "please wait" UI: stays hidden unless compute_bhava() is still running after a
        # short delay (see components.DelayedBusyIndicator).
        busy = DelayedBusyIndicator(buttons=w.get('calculate_button'), stop_label=res_str('stop_str', 'Stop'))
        # print-two-col-layout (see components.py's _PRINT_CSS): on screen this is a side-by-side flex
        # row (info table, chart); for print it becomes a CSS Grid with the chart column sized "auto"
        # (not a fixed fraction), so with the table kept compact there is real spare width on an
        # A4-landscape page for the chart to be drawn considerably larger than its on-screen default -
        # same technique already confirmed working for Kundali's single-chart print.
        with ui.row().classes('w-full items-start gap-4 flex-nowrap print-two-col-layout'):
            with ui.column().classes('w-96 shrink-0 gap-2 print-info-col'):
                ui.label('Bhava Information').classes('font-bold text-green-700 no-print')
                with ui.card().classes('w-full min-h-[400px] p-3 bg-gray-50 shadow text-xs overflow-y-auto max-h-[650px] print-expand print-compact-text'):
                    info_html = ui.html('Click "Show Bhava Chart" to compute.')
            with ui.column().classes('flex-1 gap-2 items-center print-chart-col'):
                chart_title_label = ui.label('').classes('text-lg font-bold text-green-700 text-center w-full')
                chart_container = ui.column().classes('items-center mt-4')
        def _render_current_chart(chart_style, chart_1d, asc_house, sc_rings):
            """Draws the chart via chart_render.py. This page has no chart-menu overlay (no Saham
            picker etc., unlike Kundali), so it always calls render_chart_into() with overlay=None
            and overlay_table_el=None - the overlay_too_crowded_fn / overlay_side_table_html_fn
            arguments are required by that function's signature but are never actually invoked when
            overlay is falsy (short-circuited before either is called), so a plain lambda is enough.
            Every chart style render_chart_into() knows how to draw - South/North/East Indian, Western
            and Sudarsana Chakra - is supported here; sc_rings (computed by _bhava_locked() only for
            Sudarsana Chakra, via _sc_rings_with_house_system()) is passed through so it dispatches to
            render_sudarsana_chakra() exactly as it does for Kundali.
            """
            cr.render_chart_into(
                chart_container, None, chart_style, chart_1d, asc_house, sc_rings, None,
                lambda overlay: False, lambda overlay, label: '', ''
            )
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
        def _refresh_chart_options_button(varga_idx=None):
            """Enables the Chart Options button, with a tooltip, only when the selected divisional chart has more
            than one method; otherwise disables it.
            """
            if varga_idx is None:
                varga_idx = _current_varga_idx()
            try:
                method_count, _ = cr.method_count_and_default_for(varga_idx)
            except Exception as e:
                print(f"[bhava_page] _refresh_chart_options_button error for varga_idx={varga_idx}: {e}")
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
            method_count, default_method = cr.method_count_and_default_for(varga_idx)
            if method_count <= 1:
                safe_notify('This varga has only one calculation method - nothing to configure.', type='warning')
                return
            varga_factor = _division_chart_factors[varga_idx]
            current_method = chart_options_state.get(varga_idx, default_method)
            method_items = {
                mc: res_str(f'd{varga_factor}_option{mc + 1}_str', f'Method {mc + 1}')
                for mc in range(method_count)
            }
            with ui.dialog() as dialog, ui.card().classes('gap-3'):
                ui.label(
                    res_str('varga_option_str', 'Varga Chart Options') + ' - ' + cr.varga_label(varga_idx)
                ).classes('text-lg font-bold text-green-700')
                method_radio = ui.radio(method_items, value=current_method - 1).props('inline' if method_count <= 3 else '')
                async def _on_accept():
                    ind = method_radio.value if isinstance(method_radio.value, int) else (default_method - 1)
                    chart_options_state[varga_idx] = ind + 1
                    dialog.close()
                    safe_notify('Chart options applied - recomputing.', type='positive')
                    await compute_bhava()
                with ui.row().classes('gap-2 justify-end w-full'):
                    ui.button(res_str('cancel_str', 'Cancel'), on_click=dialog.close).props('outlined dense')
                    ui.button(res_str('accept_str', 'Accept'), on_click=_on_accept).classes('bg-green-600 text-white')
            dialog.open()
        def _refresh_house_system_select():
            """Enables the house-system selector when the astrology model is Drik (all house systems are
            supported); otherwise disables it with an explanatory tooltip, and the default house system is used.
            """
            with calc_lock():  # read inside calc_lock() so the visitor's astrology engine applies
                is_drik = utils.astro_engine_is_drik()
            if is_drik:
                house_system_select.enable()
                house_system_tooltip.set_text('Choose the house-cusp calculation method.')
            else:
                house_system_select.disable()
                house_system_tooltip.set_text(
                    'Only the Drik astrology model supports all house systems - '
                    'other models support only a limited subset, so this is locked '
                    'to the default house system for now.'
                )
        @ignore_disconnected_client
        async def compute_bhava():
            """Reads the control bar, computes the bhava chart in a worker thread (showing a
            non-intrusive "please wait" message via DelayedBusyIndicator only if it takes more than a
            moment) and draws the chart and the bhava information table.
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
                varga_idx = _current_varga_idx()
                dcf = _division_chart_factors[varga_idx]
                _, default_method = cr.method_count_and_default_for(varga_idx)
                chart_method = chart_options_state.get(varga_idx, default_method)
                chart_style_index = chart_style_select.value if isinstance(chart_style_select.value, int) else 0
                chart_style = _chart_style_keys[chart_style_index]
                # Store the chart style where the other chart pages read it.
                state['kundali_chart_style_index'] = chart_style_index
                state['kundali_chart_style'] = getattr(chart_style, 'name', str(chart_style))
                house_select_idx = house_system_select.value if isinstance(house_system_select.value, int) else None
            except Exception as e:
                safe_notify(f'Error computing bhava chart: {str(e)}', type='negative')
                info_html.set_content(f'<span style="color:red">Error: {e}</span>')
                return
            try:
                result = await busy.run(_bhava_locked, dob, tob, place_val, lat_val, lon_val, tz_val, dcf,
                                        chart_method, house_select_idx, _house_keys, _default_house_idx,
                                        chart_style,
                                        wait_text=res_str('computing_str', 'Computing... please wait.'))
            except Exception as e:
                safe_notify(f'Error computing bhava chart: {str(e)}', type='negative')
                info_html.set_content(f'<span style="color:red">Error: {e}</span>')
                return
            if result is DelayedBusyIndicator.STOPPED:
                return  # Stop (or a newer call) superseded this one; discard the stale result quietly
            try:
                chart_1d, bhava_chart_info, bhava_ascendant_house, used_default_house_system, sc_rings = result
                if used_default_house_system:
                    safe_notify('That house system is not supported for the current astrology model - using the default instead.', type='warning')
                bhava_state.update({
                    "bhava_chart_data": chart_1d, "bhava_ascendant_house": bhava_ascendant_house,
                    "bhava_chart_info": bhava_chart_info, "sc_rings": sc_rings,
                })
                chart_title_label.set_text(
                    f"{cr.varga_label(varga_idx)} ({cr.chart_style_label(chart_style)}) \u2014 {place_val}"
                )
                _render_current_chart(chart_style, chart_1d, bhava_ascendant_house, sc_rings)
                # Bhava information table: House, Starts At, Middle, Ends At, Planets (one row per house).
                _th_style = 'border:1px solid #5c3a21; padding:6px 10px; background:#f0fdf4; text-align:left; white-space:nowrap;'
                _td_style = 'border:1px solid #d1d5db; padding:6px 10px; white-space:nowrap;'
                headers = [res_str('house_str', 'House'), res_str('starts_at_str', 'Starts At'),
                           res_str('middle_str', 'Middle'), res_str('ends_at_str', 'Ends At'),
                           res_str('planets_str', 'Planets')]
                html = "<table style='border-collapse:collapse;'>"
                html += "<tr>" + "".join(f"<th style='{_th_style}'>{h}</th>" for h in headers) + "</tr>"
                for row in bhava_chart_info:
                    cells = list(row) + [''] * (5 - len(row))  # pad short rows to 5 cells
                    html += "<tr>" + "".join(f"<td style='{_td_style}'>{c}</td>" for c in cells[:5]) + "</tr>"
                html += "</table>"
                info_html.set_content(html)
            except Exception as e:
                safe_notify(f'Error computing bhava chart: {str(e)}', type='negative')
                info_html.set_content(f'<span style="color:red">Error: {e}</span>')
        chart_style_select.on_value_change(lambda e: compute_bhava())
        async def _on_varga_changed(e):
            _refresh_chart_options_button(e.value if isinstance(e.value, int) else None)
            await compute_bhava()
        varga_select.on_value_change(_on_varga_changed)
        house_system_select.on_value_change(lambda e: compute_bhava())
        _refresh_chart_options_button()
        _refresh_house_system_select()
        ui.timer(0.1, compute_bhava, once=True)
    render_footer()

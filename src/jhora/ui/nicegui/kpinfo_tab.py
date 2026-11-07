#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""KP-Lord page (/kpinfo).
Shows the KP lords of every planet, the ascendant and the 12 house cusps for the chosen
divisional chart: KP number and the nakshatra, antara, prathyanthara, sookshma, praana and deha
lords. "Chart Options" selects the calculation method of the varga.
"Print / Save as PDF" prints the current selection only (single page) - no "all vargas" mode, same
scope decision as Bhava.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()), using the D1 (Rasi) default - not whatever varga/method this page's own
widgets currently show, since the registry calls this function HEADLESSLY (no live widgets exist
for a page the visitor is not currently on) - see print_registry.py's own module docstring for the
full contract.
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope.chart import charts
drik = utils.hora_engine_proxy
from components import (
    navigation_header, render_control_bar, ensure_default_state,
    calc_lock, res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator, print_button,
    render_footer, run_io_bound_ctx, 
)
import print_registry
_chart_names = const._chart_names
_division_chart_factors = const.division_chart_factors
def _varga_label(i):
    return res_str(_chart_names[i], _chart_names[i].replace('_str', '').replace('_', ' ').title())
def _parse_tob(tob_str, fallback=(12, 0, 0)):
    try:
        parts = [int(x) for x in str(tob_str).strip().split(':')]
        if len(parts) == 2:
            parts.append(0)
        if len(parts) != 3:
            raise ValueError
        return tuple(parts)
    except Exception:
        return fallback
def _name(pid):
    try:
        return utils.PLANET_NAMES[pid]
    except Exception:
        return str(pid)
def _kpinfo_locked(dob, tob, place_val, lat_val, lon_val, tz_val, dcf, chart_method, base_rasi, from_end):
    """Computes the KP lord rows (planets, ascendant and 12 house cusps) under calc_lock(); the slow
    part of compute_kpinfo(), run in a worker thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        jd = utils.julian_day_number(drik.Date(*dob), tob)
        place = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
        planet_positions = charts.divisional_chart(
            jd, place, divisional_chart_factor=dcf, chart_method=chart_method,
            base_rasi=base_rasi, count_from_end_of_sign=from_end,
            exclude_non_planets=True,
        )
        planet_count = const._pp_count_upto_pluto if const._INCLUDE_URANUS_TO_PLUTO else const._pp_count_upto_ketu
        kp_info = charts.get_KP_lords_from_planet_positions(planet_positions[:planet_count])
        rows = []
        for p, details in kp_info.items():
            label = res_str('ascendant_str', 'Ascendant') if p == const._ascendant_symbol else _name(p)
            rows.append((label, details))
        bhava_info = charts._bhaava_madhya_new(jd, place, divisional_chart_factor=dcf, bhava_madhya_method=1)
        for house_no, (_, (_, bm, _), _) in enumerate(bhava_info, start=1):
            details = utils.kp_lords_for_longitude(f'House-{house_no}', bm)[f'House-{house_no}']
            rows.append((f"{res_str('house_str', 'House')}-{house_no}", details))
        return rows
def _kp_table_html(rows):
    """Returns the KP lord table as an HTML string. Extracted to module level so BOTH the page's own
    _render() (called via ui.html(_kp_table_html(rows))) and print_registry.py's headless
    _build_print_section() below use the SAME markup - a single source of truth that cannot drift.
    """
    headers = [
        'Object',
        'KP ' + res_str('number_str', 'Number'),
        res_str('nakshatra_lord_str', 'Nakshatra Lord'),
        res_str('antara_lord_str', 'Antara Lord'),
        res_str('prathyanthara_lord_str', 'Prathyanthara Lord'),
        res_str('sookshma_lord_str', 'Sookshma Lord'),
        res_str('praana_lord_str', 'Praana Lord'),
        res_str('deha_lord_str', 'Deha Lord'),
    ]
    th = 'border:1px solid #5c3a21;padding:6px 9px;background:#f0fdf4;text-align:left;white-space:nowrap;'
    td = 'border:1px solid #d1d5db;padding:6px 9px;white-space:nowrap;'
    html = "<table style='border-collapse:collapse;font-size:12px;width:max-content;min-width:100%'><tr>"
    html += ''.join(f"<th style='{th}'>{h}</th>" for h in headers) + '</tr>'
    for label, details in rows:
        vals = [str(details[0])] + [_name(x) for x in details[1:7]]
        html += '<tr>' + f"<td style='{td};font-weight:bold'>{label}</td>" + ''.join(f"<td style='{td}'>{x}</td>" for x in vals) + '</tr>'
    html += '</table>'
    return html
@ui.page('/kpinfo')
def kpinfo_page():
    navigation_header()
    ensure_default_state()
    chart_options_state = {}
    varga_options = {i: _varga_label(i) for i in range(len(_division_chart_factors))}
    _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label('KP-' + res_str('lord_str','Lord')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w = render_control_bar(show_dob_tob=True, on_options_saved=lambda: compute_kpinfo(),
                                on_calculate=lambda: compute_kpinfo())
        busy = DelayedBusyIndicator(buttons=w.get('calculate_button'), stop_label=res_str('stop_str', 'Stop'))
        with w['row2']:
            varga_select = ui.select(options=varga_options, value=0, label='Varga (Divisional Chart)').props('outlined dense').classes('w-56')
            chart_options_button = ui.button(_chart_options_nls, on_click=lambda: _open_chart_options_dialog()).props('outlined dense')
            with chart_options_button:
                chart_options_tooltip = ui.tooltip('')
            option_info = ui.html('').classes('text-sm font-semibold text-gray-700')
        # 'print-attach-next': keeps this title attached to the start of its own table below -
        # without this, a page break can land between them even with nothing overcrowded, since
        # they are separate sibling elements with nothing tying them together. Confirmed from an
        # actual printed PDF (title alone on page 1, the table starting fresh on page 2, despite
        # the combined content easily fitting one page) - see components.py's module docstring,
        # "full-bleed table width" note, for the full history.
        # 'single-chart-print-block' (on the WRAPPER): hides this page's own on-screen content -
        # BOTH title_label AND table_container - during the global combined "Save as PDF" print
        # (body.printing-all - see components.py's _PRINT_CSS). Without this, this page's own live
        # content stays visible (and duplicates print_registry.py's own headless-built copy) - the
        # same bug confirmed and fixed for amsa_ruler_tab.py's identical title+table pattern.
        with ui.column().classes('w-full gap-1 single-chart-print-block'):
            title_label = ui.label('').classes('text-lg font-bold text-green-700 print-attach-next')
            # 'print-expand': removes the on-screen overflow-x-auto scroll clipping for print (and any
            # scrollbar-reserved space that could otherwise linger even once content fits) - see
            # components.py's module docstring for the full history.
            table_container = ui.column().classes('w-full overflow-x-auto print-expand')
    def _current_varga_idx():
        v = varga_select.value
        if isinstance(v, bool):
            return 0
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.strip().lstrip('-').isdigit():
            return int(v)
        return 0
    def _method_count_and_default(varga_idx):
        if varga_idx == 0:
            return 1, 1, None, None
        factor = _division_chart_factors[varga_idx]
        try:
            count, method, base_rasi, from_end = utils.get_varga_option_dict()[factor]
        except (KeyError, TypeError, ValueError) as e:
            print(f'[kpinfo_page] varga option lookup failed for D{factor}: {e}')
            return 1, 1, None, None
        return (count or 1), (method or 1), base_rasi, from_end
    def _refresh_chart_options_button(varga_idx=None):
        if varga_idx is None:
            varga_idx = _current_varga_idx()
        count, method, _, _ = _method_count_and_default(varga_idx)
        factor = _division_chart_factors[varga_idx]
        if count > 1:
            chart_options_button.enable()
            chart_options_button.classes(remove='text-gray-400')
            chart_options_tooltip.set_text(f'Choose which of the {count} calculation methods to use for this varga.')
            option_info.set_content(res_str(f'd{factor}_option{chart_options_state.get(varga_idx, method)}_str', f'Method {chart_options_state.get(varga_idx, method)}'))
        else:
            chart_options_button.disable()
            chart_options_button.classes(add='text-gray-400')
            chart_options_tooltip.set_text('This varga has only one calculation method - nothing to configure.')
            option_info.set_content('')
    def _open_chart_options_dialog():
        varga_idx = _current_varga_idx()
        count, default_method, _, _ = _method_count_and_default(varga_idx)
        if count <= 1:
            safe_notify('This varga has only one calculation method - nothing to configure.', type='warning')
            return
        factor = _division_chart_factors[varga_idx]
        current_method = chart_options_state.get(varga_idx, default_method)
        method_items = {mc: res_str(f'd{factor}_option{mc + 1}_str', f'Method {mc + 1}') for mc in range(count)}
        with ui.dialog() as dialog, ui.card().classes('gap-3'):
            ui.label(res_str('varga_option_str', 'Varga Chart Options') + ' - ' + _varga_label(varga_idx)).classes('text-lg font-bold text-green-700')
            method_radio = ui.radio(method_items, value=current_method - 1).props('inline' if count <= 3 else '')
            async def _accept():
                ind = method_radio.value if isinstance(method_radio.value, int) else default_method - 1
                chart_options_state[varga_idx] = ind + 1
                dialog.close()
                _refresh_chart_options_button(varga_idx)
                await compute_kpinfo()
            with ui.row().classes('gap-2 justify-end w-full'):
                ui.button(res_str('cancel_str', 'Cancel'), on_click=dialog.close).props('outlined dense')
                ui.button(res_str('accept_str', 'Accept'), on_click=_accept).classes('bg-green-600 text-white')
        dialog.open()
    @ignore_disconnected_client
    async def compute_kpinfo():
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
            year, month, day = dob_val.split(',')
            dob = (int(year), int(month), int(day))
            tob = _parse_tob(tob_val)
            varga_idx = _current_varga_idx()
            dcf = _division_chart_factors[varga_idx]
            _, default_method, base_rasi, from_end = _method_count_and_default(varga_idx)
            chart_method = chart_options_state.get(varga_idx, default_method)
        except Exception as e:
            safe_notify(f"Error computing KP-{res_str('lord_str', 'Lord')}: {e}", type='negative')
            return
        try:
            rows = await busy.run(_kpinfo_locked, dob, tob, place_val, lat_val, lon_val, tz_val, dcf,
                                  chart_method, base_rasi, from_end,
                                  wait_text=res_str('computing_str', 'Computing... please wait.'))
        except Exception as e:
            safe_notify(f"Error computing KP-{res_str('lord_str', 'Lord')}: {e}", type='negative')
            table_container.clear()
            with table_container:
                ui.label(f'Error: {e}').classes('text-red-600')
            return
        if rows is DelayedBusyIndicator.STOPPED:
            return
        title_label.set_text(f"KP-{res_str('lord_str', 'Lord')} - {_varga_label(varga_idx)}")
        table_container.clear()
        with table_container:
            ui.html(_kp_table_html(rows))
    async def _on_varga_changed(e):
        _refresh_chart_options_button(e.value if isinstance(e.value, int) else None)
        await compute_kpinfo()
    varga_select.on_value_change(_on_varga_changed)
    _refresh_chart_options_button()
    ui.timer(0.1, compute_kpinfo, once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Uses D1 (Rasi) - the default varga this page
    itself shows on first load - since there is no live varga selector to read headlessly. Reuses
    _kpinfo_locked() and _kp_table_html(), the SAME functions the page's own compute_kpinfo() calls.
    """
    varga_idx = 0
    dcf = _division_chart_factors[varga_idx]
    try:
        rows = await run_io_bound_ctx(_kpinfo_locked, dob, tob, place_val, lat_val, lon_val, tz_val, dcf, 1, None, None)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing KP-Lord: {e}</i>")
        return
    with container:
        ui.label(f"KP-{res_str('lord_str', 'Lord')} - {_varga_label(varga_idx)}").classes('text-base font-bold text-green-700 print-attach-next')
        # 'print-compact-text' (6pt !important - components.py's _PRINT_CSS): _kp_table_html()
        # hardcodes an INLINE 12px font-size, which (with no shrink class applied) left this
        # 22-row table (10 planet/ascendant lords + 12 house cusps) just barely too tall for one
        # printed page - the global 'table, tr { break-inside: avoid }' rule cannot split a single
        # <tr>, so confirmed from an actual printed PDF: row 22 (House-12) alone was pushed to a
        # near-blank second page. '.print-compact-text' uses !important, so it overrides the
        # table's own inline style and shrinks every row enough for all 22 to fit on one page -
        # the same fix already applied to Amsa Ruler/Saham/Dhasa's own large print tables.
        with ui.column().classes('print-compact-text'):
            ui.html(_kp_table_html(rows))
print_registry.register('kpinfo', 'KP-' + res_str('lord_str', 'Lord'), 'Calculations', _build_print_section)

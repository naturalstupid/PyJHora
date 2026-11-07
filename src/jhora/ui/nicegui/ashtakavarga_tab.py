#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Ashtakavarga page (/ashtakavarga).
Shows the sarvashtakavarga (SAV) and the bhinnashtakavarga (BAV) of the seven planets and the
ascendant for the chosen divisional chart, as a table: one row per planet (and SAV), one column per
rasi in fixed Aries .. Pisces order, each cell the bindu (point) count, with a row Total column.
"Chart Options" selects the calculation method of the varga.
"Print / Save as PDF" prints the current selection only (single page) - no "all vargas" mode, same
scope decision as Bhava.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()), using the D1 (Rasi) default - not whatever varga/method this page's own
widgets currently show, since the registry calls this function HEADLESSLY (no live widgets exist
for a page the visitor is not currently on).
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope import info as horo_info
from jhora.horoscope.chart import ashtakavarga
from components import (
    navigation_header, render_control_bar, ensure_default_state,
    calc_lock, res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator, print_button,
    render_footer, run_io_bound_ctx, 
)
import print_registry
drik = utils.hora_engine_proxy
_FACTORS = const.division_chart_factors
_NAMES = const._chart_names
_CELL = 'border:1px solid #d1d5db; padding:3px 10px; text-align:center;'
_CELL_SAV = 'border:1px solid #d1d5db; padding:3px 10px; text-align:center; font-weight:bold; background:#fef9c3;'
_HEAD = 'border:1px solid #5c3a21; padding:3px 10px; text-align:center; background:#f0fdf4; font-weight:bold;'
_ROWLABEL = 'border:1px solid #5c3a21; padding:3px 10px; text-align:left; background:#ecfdf5; font-weight:bold; white-space:nowrap;'
def _rasi_heads():
    """Returns the 12 rasi header labels (Aries .. Pisces) in this visitor's language, read from
    utils.RAASI_SHORT_LIST so the table header is translated instead of always showing the English
    abbreviations (utils is the per-visitor, language-aware module - see web_language.py)."""
    return utils.RAASI_SHORT_LIST
def _varga_label(i):
    """Returns the localized name of the divisional chart at index `i` of const.division_chart_factors."""
    return res_str(_NAMES[i], _NAMES[i].replace('_str', '').replace('_', ' ').title())
def _method_count_and_default(varga_idx):
    """Returns (method_count, default_method) of the divisional chart at index `varga_idx`; the default
    method is 1-based. D1 (index 0) and a failed lookup give (1, 1, None, None).
    Returns:
        (method_count, default_method, base_rasi_index, count_from_end_of_sign).
    """
    if varga_idx == 0:
        return 1, 1, None, None
    try:
        method_count, default_method, base_rasi, count_from_end = utils.get_varga_option_dict()[_FACTORS[varga_idx]]
        return (method_count or 1), (default_method or 1), base_rasi, count_from_end
    except Exception:
        return 1, 1, None, None
def _convert_chart_tokens(chart):
    """Returns `chart` (a list of 12 '/'-joined house strings) with the planet names and the ascendant
    symbol replaced by the plain tokens jhora.horoscope.chart.ashtakavarga.get_ashtaka_varga() expects:
    '0'..'8' for the nine planets, const._ascendant_symbol for the ascendant.
    """
    out = list(chart)
    local_names = utils.PLANET_NAMES + [res_str('ascendant_str', 'Ascendant')]
    english_names = ['Sun   ', 'Moon   ', 'Mars   ', 'Mercury   ', 'Jupiter   ', 'Venus   ', 'Saturn   ',
                     'Raagu   ', 'Kethu   ', 'Uranus', 'Neptune', 'Pluto', 'Lagnam']
    index_tokens = [str(i) for i in range(12)] + [const._ascendant_symbol]
    for localized, english in zip(local_names, english_names):
        out = [x.replace(localized, english) for x in out]
    for english, token in zip(english_names, index_tokens):
        out = [x.replace(english, token).replace(const._stationary_symbol, '').replace(const._retrogade_symbol, '')
               for x in out]
    return out
def _table_html(names, rows):
    """Returns the HTML of the Ashtakavarga table.
    Args:
        names: row labels (SAV, then the seven planets Sun..Saturn, then the ascendant label).
        rows: matching list of 12 bindu counts each, in fixed Aries .. Pisces order.
    """
    rasi_heads = _rasi_heads()
    head = (f"<th style='{_HEAD}'>{res_str('planet_str', 'Planet')}</th>"
            + ''.join(f"<th style='{_HEAD}'>{r}</th>" for r in rasi_heads)
            + f"<th style='{_HEAD}'>{res_str('balance_str', 'Total')}</th>")
    body = []
    for idx, (name, vals) in enumerate(zip(names, rows)):
        vals = [int(v) for v in vals]
        cell_style = _CELL_SAV if idx == 0 else _CELL
        cells = ''.join(f"<td style='{cell_style}'>{v}</td>" for v in vals)
        body.append(f"<tr><td style='{_ROWLABEL}'>{name}</td>{cells}<td style='{cell_style}'>{sum(vals)}</td></tr>")
    return f"<table style='border-collapse:collapse;'><tr>{head}</tr>{''.join(body)}</table>"
def _ashtakavarga_locked(year, month, day, tob, place_val, lat_val, lon_val, tz_val, varga_idx, varga_factor,
                          chart_method, base_rasi, count_from_end):
    """Computes the BAV/SAV under calc_lock(); the slow part of compute(), run in a worker thread via
    components.DelayedBusyIndicator.run()."""
    with calc_lock():
        horo = horo_info.Horoscope(
            place_with_country_code=place_val, latitude=lat_val, longitude=lon_val, timezone_offset=tz_val,
            date_in=drik.Date(year, month, day), birth_time=f'{tob[0]:02d}:{tob[1]:02d}:{tob[2]:02d}',
            calculation_type='drik', language=const._DEFAULT_LANGUAGE,
        )
        _, chart, asc_house = horo.get_horoscope_information_for_chart(
            varga_idx, chart_method, divisional_chart_factor=varga_factor,
            base_rasi=base_rasi, count_from_end_of_sign=count_from_end,
            varnada_method=1, dhasa_progression_correction=0.0,
        )
        bav, sav, _ = ashtakavarga.get_ashtaka_varga(_convert_chart_tokens(chart))
        return bav, sav
@ui.page('/ashtakavarga')
def ashtakavarga_page():
    """Ashtakavarga page: control bar, varga selector, Chart Options and the SAV/BAV table."""
    navigation_header()
    ensure_default_state()
    chart_options_state = {}  # chart_method chosen in the Chart Options dialog (1-based), per varga index
    _chart_options_nls = res_str('horoscope_str', 'Chart') + ' ' + res_str('options_str', 'Options')
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('ashtaka_varga_str', 'Ashtakavarga')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w = render_control_bar(show_dob_tob=True, on_options_saved=lambda: compute(), on_calculate=lambda: compute())
        busy = DelayedBusyIndicator(buttons=w.get('calculate_button'), stop_label=res_str('stop_str', 'Stop'))
        with w['row2']:
            varga_select = ui.select({i: _varga_label(i) for i in range(len(_FACTORS))}, value=0,
                                     label=res_str('varga_option_str', 'Varga')).props('outlined dense').classes('w-56')
            chart_options_button = ui.button(_chart_options_nls, on_click=lambda: _open_chart_options_dialog()) \
                .props('outlined dense')
            with chart_options_button:
                chart_options_tooltip = ui.tooltip('')
        ui.separator()
        # 'single-chart-print-block' (on the WRAPPER): hides this page's own on-screen content -
        # BOTH table_title AND table_container - during the global combined "Save as PDF" print
        # (body.printing-all - see components.py's _PRINT_CSS). Without this, this page's own live
        # content stays visible (and duplicates print_registry.py's own headless-built copy) - the
        # same bug confirmed and fixed for amsa_ruler_tab.py's identical title+table pattern.
        # 'print-attach-next' (added): keeps table_title attached to table_container below it -
        # this page did not previously carry that class at all.
        with ui.column().classes('w-full gap-1 single-chart-print-block'):
            table_title = ui.label('').classes('font-bold text-green-700 print-attach-next')
            table_container = ui.column().classes('w-full overflow-x-auto')
    def _current_varga_idx():
        """Returns the index of the selected divisional chart (0 if the selection is not a valid index)."""
        v = varga_select.value
        return v if isinstance(v, int) else 0
    def _refresh_chart_options_button():
        """Enables the Chart Options button, with a tooltip, only when the selected divisional chart has
        more than one calculation method; otherwise disables it.
        """
        method_count, _, _, _ = _method_count_and_default(_current_varga_idx())
        if method_count > 1:
            chart_options_button.enable()
            chart_options_tooltip.set_text(f'Choose which of the {method_count} calculation methods to use for this varga.')
        else:
            chart_options_button.disable()
            chart_options_tooltip.set_text('This varga has only one calculation method - nothing to configure.')
    def _open_chart_options_dialog():
        """Opens the dialog for choosing the calculation method of the selected divisional chart. Accept
        stores the choice (1-based) in chart_options_state and recomputes.
        """
        varga_idx = _current_varga_idx()
        method_count, default_method, _, _ = _method_count_and_default(varga_idx)
        if method_count <= 1:
            safe_notify('This varga has only one calculation method - nothing to configure.', type='warning')
            return
        varga_factor = _FACTORS[varga_idx]
        current_method = chart_options_state.get(varga_idx, default_method)
        method_items = {m: res_str(f'd{varga_factor}_option{m + 1}_str', f'Method {m + 1}') for m in range(method_count)}
        with ui.dialog() as dialog, ui.card().classes('gap-3'):
            ui.label(res_str('varga_option_str', 'Varga Chart Options') + ' - ' + _varga_label(varga_idx)) \
                .classes('text-lg font-bold text-green-700')
            method_radio = ui.radio(method_items, value=current_method - 1).props('inline' if method_count <= 3 else '')
            async def _on_accept():
                ind = method_radio.value if isinstance(method_radio.value, int) else (default_method - 1)
                chart_options_state[varga_idx] = ind + 1
                dialog.close()
                _refresh_chart_options_button()
                await compute()
            with ui.row().classes('gap-2 justify-end w-full'):
                ui.button(res_str('cancel_str', 'Cancel'), on_click=dialog.close).props('outlined dense')
                ui.button(res_str('accept_str', 'Accept'), on_click=_on_accept).classes('bg-green-600 text-white')
        dialog.open()
    @ignore_disconnected_client
    async def compute():
        """Reads the control bar, computes the BAV/SAV in a worker thread (showing a "please wait"
        message via DelayedBusyIndicator if it takes more than a moment) and draws the table."""
        if busy.is_busy:
            safe_notify('Already computing. Please wait.', type='warning')
            return
        try:
            year, month, day = (int(x) for x in w['dob_input'].value.strip().split(','))
            tob_parts = [int(x) for x in w['tob_input'].value.strip().split(':')]
            tob = tuple((tob_parts + [0])[:3])
            place_val = w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat_val = float(w['lat_input'].value)
            lon_val = float(w['lon_input'].value)
            tz_val = float(w['tz_input'].value)
            varga_idx = _current_varga_idx()
            varga_factor = _FACTORS[varga_idx]
            _, default_method, base_rasi, count_from_end = _method_count_and_default(varga_idx)
            chart_method = chart_options_state.get(varga_idx, default_method)
        except Exception as e:
            safe_notify(f'Error computing Ashtakavarga: {e}', type='negative')
            return
        try:
            result = await busy.run(_ashtakavarga_locked, year, month, day, tob, place_val, lat_val, lon_val,
                                    tz_val, varga_idx, varga_factor, chart_method, base_rasi, count_from_end,
                                    wait_text=res_str('computing_str', 'Computing... please wait.'))
        except Exception as e:
            safe_notify(f'Error computing Ashtakavarga: {e}', type='negative')
            return
        if result is DelayedBusyIndicator.STOPPED:
            return
        bav, sav = result
        names = [res_str('sav_str','SAV')] + utils.PLANET_NAMES[:7] + [res_str('ascendant_str', 'Lagna')]
        rows = [sav] + list(bav[:8])
        table_title.set_text(f"{res_str('ashtaka_varga_str', 'Ashtakavarga')} \u2014 {_varga_label(varga_idx)}")
        table_container.clear()
        with table_container:
            ui.html(_table_html(names, rows))
    async def _on_varga_changed(e):
        _refresh_chart_options_button()
        await compute()
    varga_select.on_value_change(_on_varga_changed)
    _refresh_chart_options_button()
    ui.timer(0.1, compute, once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Uses D1 (Rasi) - the default varga this page
    itself shows on first load. Reuses _ashtakavarga_locked() and _table_html(), the SAME functions
    the page's own compute() calls.
    """
    varga_idx = 0
    varga_factor = _FACTORS[varga_idx]
    try:
        bav, sav = await run_io_bound_ctx(_ashtakavarga_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val,
                                      lon_val, tz_val, varga_idx, varga_factor, 1, None, None)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing Ashtakavarga: {e}</i>")
        return
    names = [res_str('sav_str','SAV')] + utils.PLANET_NAMES[:7] + [res_str('ascendant_str', 'Lagna')]
    rows = [sav] + list(bav[:8])
    with container:
        ui.label(f"{res_str('ashtaka_varga_str', 'Ashtakavarga')} \u2014 {_varga_label(varga_idx)}") \
            .classes('text-base font-bold text-green-700 print-attach-next')
        ui.html(_table_html(names, rows))
print_registry.register('ashtakavarga', res_str('ashtaka_varga_str', 'Ashtakavarga'), 'Calculations', _build_print_section)

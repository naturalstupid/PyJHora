#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Kundali chart page (/kundali).
Shows the chart of the chosen divisional chart (Rasi D1 to Nadiamsa D150) in the chosen chart style,
with the chart information (planet longitudes etc.) split into two columns and the chart on the right.
"Print / Save as PDF" prints just the currently displayed chart on one page. "Save All Vargas as PDF"
builds a hidden, print-only multi-page report - one page per varga (D1..D150), each with the SAME
chart-menu selection re-applied (e.g. if a Saham is currently shown, every varga's page shows that
varga's own version of it) - and prints all of them in one PDF.
The actual chart-box drawing, AND the varga-chart computation / "every varga, one page per varga"
report logic, now live in the shared chart_render.py module, so a second page (Panchangam's own
"+ include charts" PDF option) can reuse the exact same code instead of a second hand-copied version.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()), using D1 (Rasi) + the first available chart style (south_indian_regular),
Planets only (no chart-menu overlay) - since the registry calls this function HEADLESSLY (no live
varga/chart-style/chart-menu selectors exist for a page the visitor is not currently on). Reuses
chart_render.py's compute_varga_chart_locked()/build_chart_info_html()/render_chart_into(), the SAME
functions this page's own compute_kundali()/_render_current_chart() call.
"""
import html as _html
from nicegui import ui, run
from jhora import const, utils, config
drik = utils.hora_engine_proxy
from nicegui import app
from components import (
    navigation_header, render_control_bar, ensure_default_state,
    calc_lock, res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
    render_footer, run_io_bound_ctx, 
)
# print_button / trigger_print_js imports REMOVED - this page no longer has its own print button at
# all (see the button-row removal note inside kundali_page() below for the full reasoning).
import chart_details
import chart_render as cr
import print_registry
# --- Backward-compatible aliases ---
# These private names used to be defined directly in this file; the chart-drawing code (and the
# data/helpers it needs), plus the varga-chart computation / "every varga" report logic, were moved
# to chart_render.py so a second page could reuse them (see this file's module docstring). Other
# files in this app (e.g. transit_tab.py) import some of the chart-drawing names directly from
# kundali_chart - rather than track down and edit every such import site, every old name is
# re-exported here, pointing at its new home in chart_render.py, so existing imports elsewhere keep
# working unchanged. If you see an ImportError for a name not listed here, it was also moved - add
# the matching alias below (see chart_render.py for the full new, public name of whatever old
# private name is missing).
_CHART_SIZE_PX = cr.CHART_SIZE_PX
_SOUTH_MAP_TO_2D = cr.SOUTH_MAP_TO_2D
_south_cell_for_rasi = cr.south_cell_for_rasi
_SOUTH_IRREGULAR_MAP_TO_2D = cr.SOUTH_IRREGULAR_MAP_TO_2D
_south_irregular_cell_for_rasi = cr.south_irregular_cell_for_rasi
_NORTH_LABEL_POSITIONS = cr.NORTH_LABEL_POSITIONS
_NORTH_BADGE_ANCHORS = cr.NORTH_BADGE_ANCHORS
_NORTH_OVERLAY_POSITIONS = cr.NORTH_OVERLAY_POSITIONS
_EAST_EDGE_CELLS = cr.EAST_EDGE_CELLS
_EAST_CORNER_CELLS = cr.EAST_CORNER_CELLS
_RASI_SHORT = cr.RASI_SHORT
_SC_RING_RADII_PCT = cr.SC_RING_RADII_PCT
_planet_label = cr.planet_label
_cell_text = cr.cell_text
_planet_text_classes = cr.planet_text_classes
_chart_names = const._chart_names
_division_chart_factors = const.division_chart_factors
_varga_label = cr.varga_label
_chart_style_label = cr.chart_style_label
_method_count_and_default_for = cr.method_count_and_default_for
_kundali_locked = cr.compute_varga_chart_locked
_resolve_menu_path_locked = cr.resolve_menu_path_locked
_build_info_html = cr.build_chart_info_html
_all_vargas_locked = cr.build_all_vargas_pages
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
@ui.page('/kundali')
def kundali_page():
    navigation_header()
    state = ensure_default_state()
    def _populate_info_panels(dob_val, tob_val, place_val, kundali_info, vim_balance, vim_db):
        h1, h2 = cr.build_chart_info_html(dob_val, tob_val, place_val, kundali_info, vim_balance, vim_db)
        info_html_1.set_content(h1)
        info_html_2.set_content(h2)
    kundali_state = {"horo": None, "chart_cell_text": None, "asc_house": None,
                     "overlay": None, "render": None, "detail_ctx": None, "prasna": None}
    _chart_style_options = {i: cr.chart_style_label(s) for i, s in enumerate(const.AVAILABLE_CHART_STYLES.keys())}
    _chart_style_keys = list(const.AVAILABLE_CHART_STYLES.keys())
    _varga_options = {i: cr.varga_label(i) for i in range(len(_division_chart_factors))}
    chart_options_state = {}
    saved_style_index = state.get('kundali_chart_style_index', 0)
    try:
        saved_style_index = int(saved_style_index)
        if saved_style_index not in range(len(const.AVAILABLE_CHART_STYLES)):
            saved_style_index = 0
    except Exception:
        saved_style_index = 0
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('horoscope_str','Kundali Chart')).classes('text-xl font-bold text-green-700')
            # Both print_button() AND the former "Save All Vargas as PDF" button are REMOVED -
            # printing is now exclusively via the ONE global "Save as PDF" button
            # (print_registry.py). This page remains registered there, WITH its own real
            # sub_option_ui (chart style / varga / "all vargas" - see _kundali_sub_option_ui()
            # below) so the central dialog can replicate what both removed buttons used to do. The
            # one capability NOT carried over: applying the live chart-menu's current overlay
            # selection (e.g. a specific Saham) to the all-vargas report - that selection only
            # exists in THIS page's own live chart_menu widget, which does not exist headlessly for
            # the central dialog (see print_registry.py's own module docstring for why); the
            # central dialog's own "all vargas" sub-option always shows Planets only, same
            # simplification already used by every other page's own headless registration.
        _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
        w = render_control_bar(show_dob_tob=True, on_options_saved=lambda: compute_kundali(),
                                on_calculate=lambda: compute_kundali())
        with w['row2']:
            chart_style_select = ui.select(options=_chart_style_options, value=saved_style_index, label='Chart Style').props('outlined dense').classes('w-48')
            varga_select = ui.select(options=_varga_options, value=0, label='Varga (Divisional Chart)').props('outlined dense').classes('w-56')
            chart_options_button = ui.button(_chart_options_nls, on_click=lambda: _open_chart_options_dialog()).props('outlined dense').classes('no-print')
            with chart_options_button:
                chart_options_tooltip = ui.tooltip('')
            chart_menu = chart_details.ChartMenu(
                apply_overlay=lambda overlay: _apply_overlay(overlay),
                overlay_supported=lambda: _overlay_supported(),
                apply_prasna=lambda rasi, replace: _apply_prasna(rasi, replace))
        ui.separator()
        busy = DelayedBusyIndicator(buttons=[w.get('calculate_button')], stop_label=res_str('stop_str', 'Stop'))
        with ui.row().classes('w-full items-start gap-4 flex-wrap lg:flex-nowrap print-three-col-layout single-chart-print-block'):
            with ui.column().classes('flex-1 gap-2 print-info-col'):
                with ui.card().classes('w-full p-2 bg-gray-50 shadow text-xs print-expand print-compact-text'):
                    info_html_1 = ui.html('Click "Show Chart" to compute.')
            with ui.column().classes('flex-1 gap-2 print-info-col'):
                with ui.card().classes('w-full p-2 bg-gray-50 shadow text-xs print-expand print-compact-text'):
                    info_html_2 = ui.html('')
            with ui.column().classes('flex-1 gap-2 items-center print-chart-col'):
                chart_title_label = ui.label('').classes('text-base font-bold text-green-700 text-center w-full')
                with ui.row().classes('items-start justify-center gap-2 flex-wrap'):
                    chart_container = ui.column().classes('items-center mt-2')
                    overlay_table = ui.html('').classes('mt-2')
                    overlay_table.set_visibility(False)
        # all_report_container REMOVED along with _build_all_vargas_report() - see that removal note
        # further below for the full explanation.
        def _render_current_chart():
            rendered = kundali_state.get("render")
            if rendered is None:
                return
            chart_style, chart_1d, asc_house, sc_rings = rendered
            overlay = kundali_state.get("overlay")
            if kundali_state.get("prasna") is not None:
                chart_1d, asc_house = chart_details.chart_with_prasna(chart_1d, asc_house, kundali_state["prasna"])
            cr.render_chart_into(chart_container, overlay_table, chart_style, chart_1d, asc_house, sc_rings,
                                 overlay, chart_details.overlay_too_crowded, chart_details.overlay_side_table_html,
                                 chart_menu.applied_label())
        def _sync_menu_visibility():
            idx = chart_style_select.value if isinstance(chart_style_select.value, int) else 0
            chart_menu.set_hidden(not chart_details.style_supports_menu(_chart_style_keys[idx]))
        def _apply_overlay(overlay):
            kundali_state["overlay"] = overlay
            kundali_state["prasna"] = None
            _render_current_chart()
        def _apply_prasna(rasi, replace):
            kundali_state["prasna"] = rasi if replace else None
            kundali_state["overlay"] = None if replace else chart_details.prasna_marker_overlay(rasi)
            _render_current_chart()
        def _overlay_supported():
            rendered = kundali_state.get("render")
            return rendered is not None and rendered[0] in (
                const.CHART_STYLE.SOUTH_INDIAN_REGULAR, const.CHART_STYLE.SOUTH_INDIAN_IRREGULAR,
                const.CHART_STYLE.NORTH_INDIAN, const.CHART_STYLE.EAST_INDIAN_WITH_FRAME,
                const.CHART_STYLE.EAST_INDIAN_NO_FRAME)
        def _current_varga_idx():
            v = varga_select.value
            if isinstance(v, bool):
                return 0
            if isinstance(v, int):
                return v
            if isinstance(v, str) and v.strip().lstrip('-').isdigit():
                return int(v)
            return 0
        def _refresh_chart_options_button(varga_idx=None):
            if varga_idx is None:
                varga_idx = _current_varga_idx()
            try:
                method_count, _ = cr.method_count_and_default_for(varga_idx)
            except Exception as e:
                print(f"[kundali_page] _refresh_chart_options_button error for varga_idx={varga_idx}: {e}")
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
                    await compute_kundali()
                with ui.row().classes('gap-2 justify-end w-full'):
                    ui.button(res_str('cancel_str', 'Cancel'), on_click=dialog.close).props('outlined dense')
                    ui.button(res_str('accept_str', 'Accept'), on_click=_on_accept).classes('bg-green-600 text-white')
            dialog.open()
        @ignore_disconnected_client
        async def compute_kundali():
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
                state['kundali_chart_style_index'] = chart_style_index
                state['kundali_chart_style'] = getattr(chart_style, 'name', str(chart_style))
            except Exception as e:
                safe_notify(f'Error computing kundali chart: {str(e)}', type='negative')
                info_html_1.set_content(f'<span style="color:red">Error: {_html.escape(str(e))}</span>')
                info_html_2.set_content('')
                return
            try:
                result = await busy.run(cr.compute_varga_chart_locked, dob, tob, place_val, lat_val, lon_val, tz_val,
                                        varga_idx, dcf, chart_method, chart_style,
                                        wait_text=res_str('computing_str', 'Computing... please wait.'))
            except Exception as e:
                safe_notify(f'Error computing kundali chart: {str(e)}', type='negative')
                info_html_1.set_content(f'<span style="color:red">Error: {_html.escape(str(e))}</span>')
                info_html_2.set_content('')
                return
            if result is DelayedBusyIndicator.STOPPED:
                return
            try:
                horo, kundali_info, chart_1d, asc_house, vim_db, vim_balance, sc_rings = result
                kundali_state.update({"horo": horo})
                chart_title_label.set_text(f"{cr.varga_label(varga_idx)} ({cr.chart_style_label(chart_style)}) \u2014 {place_val}")
                kundali_state["overlay"] = None
                kundali_state["prasna"] = None
                kundali_state["render"] = (chart_style, chart_1d, asc_house, sc_rings)
                kundali_state["detail_ctx"] = chart_details.make_context(
                    horo, dob, tob, varga_idx, dcf, chart_method, chart_style)
                _render_current_chart()
                _sync_menu_visibility()
                chart_menu.schedule_rebuild(kundali_state["detail_ctx"])
                _populate_info_panels(dob_val, tob_val, place_val, kundali_info, vim_balance, vim_db)
            except Exception as e:
                safe_notify(f'Error computing kundali chart: {str(e)}', type='negative')
                info_html_1.set_content(f'<span style="color:red">Error: {_html.escape(str(e))}</span>')
                info_html_2.set_content('')
                return
        # _build_all_vargas_report() and all_report_container (the former "Save All Vargas as PDF"
        # button's own implementation) are REMOVED entirely - see the button-row removal note above
        # for why (the capability is replaced by this page's own print_registry.py sub_option_ui,
        # see _kundali_sub_option_ui()/ _build_print_section() below, minus the live chart-menu
        # overlay-application part, which cannot exist headlessly).
        async def _on_chart_style_changed(e):
            _sync_menu_visibility()
            await compute_kundali()
        chart_style_select.on_value_change(_on_chart_style_changed)
        async def _on_varga_changed(e):
            _refresh_chart_options_button(e.value if isinstance(e.value, int) else None)
            await compute_kundali()
        varga_select.on_value_change(_on_varga_changed)
        _refresh_chart_options_button()
        _sync_menu_visibility()
        ui.timer(0.1, compute_kundali, once=True)
    render_footer()
_kundali_chart_style_options = {i: cr.chart_style_label(s) for i, s in enumerate(const.AVAILABLE_CHART_STYLES.keys())}
_kundali_chart_style_keys = list(const.AVAILABLE_CHART_STYLES.keys())
_kundali_varga_options = {i: cr.varga_label(i) for i in range(len(_division_chart_factors))}
def _kundali_sub_option_ui():
    """Draws this entry's OWN custom widgets inside print_registry.py's dialog - replicates what the
    (now-removed) "Save All Vargas as PDF" button used to offer: a Chart Style picker, a Varga
    picker, and an "All vargas (D1-D150)" checkbox that, when checked, ignores the Varga picker and
    prints every varga instead (see _build_print_section() below for how these 3 widgets' own
    values are actually used). Returned as a plain {name: widget} dict - print_registry.py's own
    _collect_sub_option_values() reads each widget's `.value` generically, so this function does not
    need to hand-write that part itself.
    """
    chart_style_select = ui.select(options=_kundali_chart_style_options, value=0, label='Chart Style') \
        .props('dense outlined').classes('w-48')
    varga_select = ui.select(options=_kundali_varga_options, value=0, label='Varga (ignored if "All vargas" is checked)') \
        .props('dense outlined').classes('w-64')
    all_vargas_cb = ui.checkbox('All vargas (D1-D150) - Planets only, no chart-menu overlay', value=False)
    return {'chart_style_idx': chart_style_select, 'varga_idx': varga_select, 'all_vargas': all_vargas_cb}
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_values):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract, and _kundali_sub_option_ui() above for where
    sub_option_values comes from. Reuses chart_render.py's compute_varga_chart_locked()/
    build_chart_info_html()/render_chart_into()/build_all_vargas_pages(), the SAME functions this
    page's own compute_kundali()/_render_current_chart() (and the former
    _build_all_vargas_report()) called.
    NOT replicated here (see the module docstring's own note on this): applying the live chart-
    menu's current overlay selection (e.g. a specific Saham) - that selection only exists in this
    page's own live chart_menu widget, which does not exist headlessly. "All vargas" here always
    shows Planets only, same simplification every other page's own headless registration already
    uses.
    """
    chart_style_idx = sub_option_values.get('chart_style_idx')
    if not isinstance(chart_style_idx, int) or not (0 <= chart_style_idx < len(_kundali_chart_style_keys)):
        chart_style_idx = 0
    chart_style = _kundali_chart_style_keys[chart_style_idx]
    all_vargas = bool(sub_option_values.get('all_vargas'))
    if all_vargas:
        try:
            pages = await run_io_bound_ctx(cr.build_all_vargas_pages, dob, tob, place_val, lat_val, lon_val, tz_val,
                                       chart_style, {}, None)
        except Exception as e:
            with container:
                ui.html(f"<i>Error computing Kundali (all vargas): {e}</i>")
            return
        if not pages:
            with container:
                ui.html("<i>Could not compute any varga (see the server console).</i>")
            return
        with container:
            for i, page in enumerate(pages):
                page_break_class = ' print-report-page-break' if i > 0 else ''
                with ui.column().classes('w-full print-report-page' + page_break_class):
                    with ui.row().classes('w-full items-start gap-4 flex-wrap lg:flex-nowrap print-three-col-layout'):
                        with ui.column().classes('flex-1 gap-2 print-info-col'):
                            with ui.card().classes('w-full p-2 bg-gray-50 shadow text-xs print-expand print-compact-text'):
                                ui.html(page['info_html_1'])
                        with ui.column().classes('flex-1 gap-2 print-info-col'):
                            with ui.card().classes('w-full p-2 bg-gray-50 shadow text-xs print-expand print-compact-text'):
                                ui.html(page['info_html_2'])
                        with ui.column().classes('flex-1 gap-2 items-center print-chart-col'):
                            ui.label(page['title']).classes('text-base font-bold text-green-700 text-center w-full')
                            with ui.row().classes('items-start justify-center gap-2 flex-wrap'):
                                page_chart_container = ui.column().classes('items-center mt-2')
                                page_overlay_table = ui.html('').classes('mt-2')
                                page_overlay_table.set_visibility(False)
                            cr.render_chart_into(page_chart_container, page_overlay_table, page['chart_style'],
                                                 page['chart_1d'], page['asc_house'], page['sc_rings'], page['overlay'],
                                                 chart_details.overlay_too_crowded, chart_details.overlay_side_table_html, '')
        return
    varga_idx = sub_option_values.get('varga_idx')
    if not isinstance(varga_idx, int) or not (0 <= varga_idx < len(_division_chart_factors)):
        varga_idx = 0
    dcf = _division_chart_factors[varga_idx]
    _, default_method = cr.method_count_and_default_for(varga_idx)
    try:
        result = await run_io_bound_ctx(cr.compute_varga_chart_locked, dob, tob, place_val, lat_val, lon_val, tz_val,
                                    varga_idx, dcf, default_method, chart_style)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing Kundali chart: {e}</i>")
        return
    horo, kundali_info, chart_1d, asc_house, vim_db, vim_balance, sc_rings = result
    dob_val = f"{dob[0]},{dob[1]},{dob[2]}"
    tob_val = f"{tob[0]:02d}:{tob[1]:02d}:{tob[2]:02d}"
    h1, h2 = cr.build_chart_info_html(dob_val, tob_val, place_val, kundali_info, vim_balance, vim_db)
    with container:
        with ui.row().classes('w-full items-start gap-4 flex-wrap lg:flex-nowrap print-three-col-layout'):
            with ui.column().classes('flex-1 gap-2 print-info-col'):
                with ui.card().classes('w-full p-2 bg-gray-50 shadow text-xs print-expand print-compact-text'):
                    ui.html(h1)
            with ui.column().classes('flex-1 gap-2 print-info-col'):
                with ui.card().classes('w-full p-2 bg-gray-50 shadow text-xs print-expand print-compact-text'):
                    ui.html(h2)
            with ui.column().classes('flex-1 gap-2 items-center print-chart-col'):
                ui.label(f"{cr.varga_label(varga_idx)} ({cr.chart_style_label(chart_style)}) \u2014 {place_val}") \
                    .classes('text-base font-bold text-green-700 text-center w-full')
                with ui.row().classes('items-start justify-center gap-2 flex-wrap'):
                    page_chart_container = ui.column().classes('items-center mt-2')
                    page_overlay_table = ui.html('').classes('mt-2')
                    page_overlay_table.set_visibility(False)
                cr.render_chart_into(page_chart_container, page_overlay_table, chart_style, chart_1d, asc_house,
                                     sc_rings, None, chart_details.overlay_too_crowded,
                                     chart_details.overlay_side_table_html, '')
print_registry.register('kundali', res_str('horoscope_str', 'Kundali'), 'Charts', _build_print_section,
                        sub_option_ui=_kundali_sub_option_ui)

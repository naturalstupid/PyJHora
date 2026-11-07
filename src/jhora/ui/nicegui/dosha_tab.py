#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Dosha page (/dosha).
Lists the doshas found in the chart on the left; selecting one shows its description on the
right.
"Print / Save as PDF" prints every dosha found (state['results'], from
dosha.get_dosha_details(), already holds only the doshas PRESENT in this chart - not every dosha
that could theoretically exist - so there is no separate "identify which are present" step needed
for print; the existing calculation result already is the "present" list). Each dosha prints with
its own heading, flowing continuously across as many pages as needed. The interactive list+detail
view is marked 'no-print' and never printed; a separate, plain '.print-only' container shows every
dosha's full description instead.
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope.chart import dosha
from components import (navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        render_footer, print_button, run_io_bound_ctx, )
import print_registry
drik = utils.hora_engine_proxy
def _dosha_locked(y, m, d, t, pv, lat, lon, tz):
    """Computes the dosha details under calc_lock(); the slow part of compute(), run in a worker
    thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        jd = utils.julian_day_number(drik.Date(y, m, d), t)
        place = drik.Place(pv, lat, lon, tz, 0.0)
        return dosha.get_dosha_details(jd, place, language=const._DEFAULT_LANGUAGE)
@ui.page('/dosha')
def dosha_page():
    navigation_header(); ensure_default_state()
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('dosha_str', 'Dosha')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w = render_control_bar(show_dob_tob=True, on_options_saved=lambda: compute(), on_calculate=lambda: compute())
        busy = DelayedBusyIndicator(buttons=w.get('calculate_button'), stop_label=res_str('stop_str', 'Stop'))
        with ui.row().classes('w-full gap-6 items-start flex-nowrap no-print'):
            with ui.column().classes('w-80 shrink-0 gap-1'):
                ui.label(res_str('dosha_str', 'Dosha') + ' ' + res_str('list_str', 'List')).classes('font-bold text-green-700')
                dosha_list = ui.column().classes('max-h-[640px] overflow-y-auto gap-1 border rounded p-2 bg-gray-50')
            with ui.column().classes('flex-1') as detail_col:
                detail_html = ui.html('').classes('text-sm')
        # 'print-only' (components.py's utility): hidden on screen, shown ONLY for print - lists
        # EVERY dosha found (all of state['results'] - already only the doshas PRESENT in this
        # chart, see the module docstring), not just the one currently selected in detail_html above.
        # 'single-chart-print-block' (added): 'print-only' alone shows this during ANY print, but
        # does not hide it during the global combined "Save as PDF" print (body.printing-all - see
        # components.py's _PRINT_CSS) - without this class, this page's own live print_container
        # stayed visible on whatever page a visitor happened to be sitting on AND
        # print_registry.py's own _build_print_section() built a SECOND, independent copy into the
        # hidden '.all-charts-report' container, duplicating Dosha - the same bug confirmed and
        # fixed for amsa_ruler_tab.py's and 12 other pages' identical title+content pattern.
        print_container = ui.column().classes('w-full gap-3 print-only single-chart-print-block')
    state = {'results': {}}
    def show_detail(name, desc):
        detail_html.set_content(f"<b><u>{name}</u></b><br>{desc}<br>")
        # Scroll the detail panel into view.
        ui.run_javascript(
            f'getElement({detail_col.id}).scrollIntoView({{behavior: "smooth", block: "start"}});'
        )
    def render_list():
        dosha_list.clear()
        with dosha_list:
            for name, desc in state['results'].items():
                ui.label(name).classes('cursor-pointer hover:bg-green-100 rounded px-1').on(
                    'click', lambda n=name, d=desc: show_detail(n, d)
                )
    def render_print_content():
        """Fills print_container with EVERY dosha's own heading + full description - see the module
        docstring for why state['results'] is already exactly "the doshas present", and why this is
        a separate, print-only view rather than just printing whatever happens to be selected in the
        on-screen detail pane.
        """
        print_container.clear()
        with print_container:
            if not state['results']:
                ui.html(f"<i>{res_str('no_results_str', 'No doshas found.')}</i>")
                return
            for name, desc in state['results'].items():
                with ui.column().classes('gap-1'):
                    # 'print-attach-next': keeps this dosha's own heading attached to the start of
                    # its own description below.
                    ui.html(f"<b><u>{name}</u></b>").classes('print-attach-next')
                    ui.html(desc).classes('text-sm')
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.', type='warning'); return
        try:
            dv = w['dob_input'].value.strip(); tv = w['tob_input'].value.strip()
            pv = w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat = float(w['lat_input'].value); lon = float(w['lon_input'].value); tz = float(w['tz_input'].value)
            y, m, d = map(int, dv.split(',')); tp = [int(x) for x in tv.split(':')]; t = tuple((tp + [0])[:3])
        except Exception as ex:
            safe_notify(f'Error computing Doshas: {ex}', type='negative'); return
        try:
            results = await busy.run(_dosha_locked, y, m, d, t, pv, lat, lon, tz,
                                     wait_text=res_str('computing_str', 'Computing... please wait.'))
        except Exception as ex:
            safe_notify(f'Error computing Doshas: {ex}', type='negative'); return
        if results is DelayedBusyIndicator.STOPPED:
            return
        state['results'] = results
        render_list()
        render_print_content()
        if results:
            first_name = next(iter(results))
            show_detail(first_name, results[first_name])
        else:
            detail_html.set_content(f"<i>{res_str('no_results_str', 'No doshas found.')}</i>")
    ui.timer(0.1, compute, once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Reuses _dosha_locked() (the SAME calculation
    function this page's own compute() calls), draws EVERY dosha found directly into `container`
    (no live widgets of this page are read - everything comes from the birth details passed in).
    """
    try:
        results = await run_io_bound_ctx(_dosha_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val, lon_val, tz_val)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing Doshas: {e}</i>")
        return
    with container:
        ui.label(res_str('dosha_str', 'Dosha')).classes('text-base font-bold text-green-700 print-attach-next')
        if not results:
            ui.html(f"<i>{res_str('no_results_str', 'No doshas found.')}</i>")
            return
        for name, desc in results.items():
            with ui.column().classes('gap-1'):
                ui.html(f"<b><u>{name}</u></b>").classes('print-attach-next')
                ui.html(desc).classes('text-sm')
print_registry.register('dosha', 'Dosha', 'Yoga / Dosha / Prediction', _build_print_section)

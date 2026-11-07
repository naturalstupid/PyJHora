#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Yoga page (/yoga).
Lists the raja yogas and the other yogas found in the chart on the left; selecting one shows its
description and prediction on the right. All divisional charts are checked when
const.check_yogas_on_all_divisional_charts is set, otherwise only the Rasi chart.
Some yoga predictions are gender-specific (see jhora.horoscope.chart.yoga.get_yoga_details()'s
`gender` parameter); the Gender field is a shared, top-level control (components.render_control_bar()'s
`gender_select` widget, mirroring the PyQt desktop app's main-window Gender combo box) rather than a
selector local to this page, since the chart owner's gender is a single fact that other pages (e.g.
Compatibility) also depend on. Yoga predictions that are not gender-specific are unaffected by this
value; the underlying jhora calculation decides which of its own yogas, if any, depend on gender.
"Print / Save as PDF" prints EVERY yoga found (both Raja Yoga and regular Yoga sections, not just
the one currently selected in the detail pane), each with its own heading, description and
prediction, flowing continuously across as many pages as needed - including the caution message
(const.show_yoga_caution_message) once at the top if it applies, same as the on-screen detail pane
shows it. The interactive list+detail view is marked 'no-print' and never printed; a separate,
plain '.print-only' container shows every yoga's full detail instead.
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope import info as horo_info
from jhora.horoscope.chart import yoga, raja_yoga
from components import ( navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        render_footer, print_button, run_io_bound_ctx, )
import print_registry
drik = utils.hora_engine_proxy
def _trim_name(name):
    parts = name.split()
    return ' '.join(parts[:-1]) if len(parts) > 1 else name
def _yoga_locked(y, m, d, t, pv, lat, lon, tz, gender):
    """Computes the raja yogas and regular yogas under calc_lock(); the slow part of compute() -
    potentially checking every divisional chart - run in a worker thread via
    components.DelayedBusyIndicator.run().
    Args:
        gender: const.GENDER value (0=Male, 1=Female - the only two currently offered in the shared
            control bar) passed through to the yoga calculation, since some yoga predictions are
            gender-specific; yogas that are not gender-specific are unaffected by this value.
    """
    with calc_lock():
        caution = bool(const.show_yoga_caution_message)
        jd = utils.julian_day_number(drik.Date(y, m, d), t)
        place = drik.Place(pv, lat, lon, tz, 0.0)
        if const.check_yogas_on_all_divisional_charts:
            raja_results, _, _ = raja_yoga.get_raja_yoga_details_for_all_charts(jd, place, language=const._DEFAULT_LANGUAGE)
            yoga_results, _, _ = yoga.get_yoga_details_for_all_charts(jd, place, language=const._DEFAULT_LANGUAGE, gender=gender)
        else:
            raja_results, _, _ = raja_yoga.get_raja_yoga_details(jd, place, divisional_chart_factor=1, language=const._DEFAULT_LANGUAGE)
            yoga_results, _, _ = yoga.get_yoga_details(jd, place, divisional_chart_factor=1, language=const._DEFAULT_LANGUAGE, gender=gender)
        return caution, raja_results, yoga_results
@ui.page('/yoga')
def yoga_page():
    navigation_header(); ensure_default_state()
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('yoga_str', 'Yoga')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w = render_control_bar(show_dob_tob=True, on_options_saved=lambda: compute(), on_calculate=lambda: compute())
        busy = DelayedBusyIndicator(buttons=w.get('calculate_button'), stop_label=res_str('stop_str', 'Stop'))
        with ui.row().classes('w-full gap-6 items-start flex-nowrap no-print'):
            with ui.column().classes('w-80 shrink-0 gap-1'):
                ui.label(res_str('yoga_str', 'Yoga') + ' ' + res_str('list_str', 'List')).classes('font-bold text-green-700')
                yoga_list = ui.column().classes('max-h-[640px] overflow-y-auto gap-1 border rounded p-2 bg-gray-50')
            with ui.column().classes('flex-1') as detail_col:
                detail_html = ui.html('').classes('text-sm')
        # 'print-only' (components.py's utility): hidden on screen, shown ONLY for print - lists
        # EVERY yoga found (both Raja Yoga and regular Yoga), not just the one currently selected in
        # detail_html above.
        # 'single-chart-print-block' (added): 'print-only' alone shows this during ANY print, but
        # does not hide it during the global combined "Save as PDF" print (body.printing-all - see
        # components.py's _PRINT_CSS) - without this class, this page's own live print_container
        # stayed visible on whatever page a visitor happened to be sitting on AND
        # print_registry.py's own _build_print_section() built a SECOND, independent copy into the
        # hidden '.all-charts-report' container, duplicating Yoga - the same bug confirmed and
        # fixed for amsa_ruler_tab.py's and 12 other pages' identical pattern.
        print_container = ui.column().classes('w-full gap-3 print-only single-chart-print-block')
    state = {'raja': [], 'regular': [], 'caution': False}
    def show_detail(chart, name, desc, pred):
        parts = []
        if state['caution']:  # set in compute() from const.show_yoga_caution_message
            parts.append(f"<b>{res_str('yoga_caution_str', 'Yogas shown here are indicative only.')}</b><br><br>")
        parts.append(f"<b><u>{name} ({chart})</u></b><br>")
        parts.append(f"<b>{res_str('description_str', 'Description')}:</b> {desc}<br>")
        parts.append(f"<b>{res_str('prediction_str', 'Prediction')}:</b> {pred}<br>")
        detail_html.set_content(''.join(parts))
        # Scroll the detail panel into view.
        ui.run_javascript(
            f'getElement({detail_col.id}).scrollIntoView({{behavior: "smooth", block: "start"}});'
        )
    def render_list():
        yoga_list.clear()
        with yoga_list:
            if state['raja']:
                ui.label(res_str('raja_yoga_str', 'Raja Yoga')).classes('font-bold text-brown-700 mt-1')
                for key, (chart, name, desc, pred) in state['raja']:
                    ui.label(_trim_name(name)).classes('cursor-pointer hover:bg-green-100 rounded px-1').on('click', lambda c=chart, n=name, d=desc, p=pred: show_detail(c, n, d, p))
            if state['regular']:
                ui.label(res_str('yoga_str', 'Yoga')).classes('font-bold text-brown-700 mt-2')
                for key, (chart, name, desc, pred) in state['regular']:
                    ui.label(_trim_name(name)).classes('cursor-pointer hover:bg-green-100 rounded px-1').on('click', lambda c=chart, n=name, d=desc, p=pred: show_detail(c, n, d, p))
    def render_print_content():
        """Fills print_container with EVERY yoga's own heading, description and prediction (both
        Raja Yoga and regular Yoga sections) - see the module docstring for why this is a separate,
        print-only view rather than just printing whatever happens to be selected in the on-screen
        detail pane.
        """
        print_container.clear()
        with print_container:
            if not state['raja'] and not state['regular']:
                ui.html(f"<i>{res_str('no_results_str', 'No yogas found.')}</i>")
                return
            if state['caution']:
                ui.html(f"<b>{res_str('yoga_caution_str', 'Yogas shown here are indicative only.')}</b>").classes('mb-2')
            def _section(title_key, title_fallback, items):
                if not items:
                    return
                ui.label(res_str(title_key, title_fallback)).classes('font-bold text-brown-700 mt-2')
                for key, (chart, name, desc, pred) in items:
                    with ui.column().classes('gap-1'):
                        # 'print-attach-next': keeps this yoga's own heading attached to the start
                        # of its own description/prediction below.
                        ui.html(f"<b><u>{name} ({chart})</u></b>").classes('print-attach-next')
                        ui.html(f"<b>{res_str('description_str', 'Description')}:</b> {desc}").classes('text-sm')
                        ui.html(f"<b>{res_str('prediction_str', 'Prediction')}:</b> {pred}").classes('text-sm')
            _section('raja_yoga_str', 'Raja Yoga', state['raja'])
            _section('yoga_str', 'Yoga', state['regular'])
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.', type='warning'); return
        try:
            dv = w['dob_input'].value.strip(); tv = w['tob_input'].value.strip()
            pv = w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat = float(w['lat_input'].value); lon = float(w['lon_input'].value); tz = float(w['tz_input'].value)
            y, m, d = map(int, dv.split(',')); tp = [int(x) for x in tv.split(':')]; t = tuple((tp + [0])[:3])
            # Gender is a shared, top-level field (components.render_control_bar()'s gender_select),
            # not a selector local to this page - see the module docstring.
            gender_widget = w.get('gender_select')
            gender = gender_widget.value if gender_widget is not None and isinstance(gender_widget.value, int) else int(const.GENDER.FEMALE)
        except Exception as ex:
            safe_notify(f'Error computing Yogas: {ex}', type='negative'); return
        try:
            result = await busy.run(_yoga_locked, y, m, d, t, pv, lat, lon, tz, gender,
                                    wait_text=res_str('computing_str', 'Computing... please wait.'))
        except Exception as ex:
            safe_notify(f'Error computing Yogas: {ex}', type='negative'); return
        if result is DelayedBusyIndicator.STOPPED:
            return
        caution, raja_results, yoga_results = result
        state['caution'] = caution
        state['raja'] = list(raja_results.items())
        state['regular'] = list(yoga_results.items())
        render_list()
        render_print_content()
        if state['raja']:
            k, v = state['raja'][0]; show_detail(*v)
        elif state['regular']:
            k, v = state['regular'][0]; show_detail(*v)
        else:
            detail_html.set_content(f"<i>{res_str('no_results_str', 'No yogas found.')}</i>")
    ui.timer(0.1, compute, once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Reuses _yoga_locked() (the SAME calculation
    function this page's own compute() calls), draws EVERY yoga found (both Raja Yoga and regular
    Yoga) directly into `container` (no live widgets of this page are read).
    Gender is read from the SAME shared, per-browser state every page reads via
    components.ensure_default_state() (the same object print_registry.py's own dialog already read
    to get the birth details passed in here) - NOT from this page's own gender_select widget, which
    does not exist headlessly. This mirrors the live page's own default of
    const.GENDER.FEMALE when nothing else is set.
    """
    gender_value = int(const.GENDER.FEMALE)
    try:
        state = ensure_default_state()
        stored = state.get('gender')
        if isinstance(stored, int):
            gender_value = stored
    except Exception:
        pass
    try:
        caution, raja_results, yoga_results = await run_io_bound_ctx(
            _yoga_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val, lon_val, tz_val, gender_value)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing Yogas: {e}</i>")
        return
    with container:
        ui.label(res_str('yoga_str', 'Yoga')).classes('text-base font-bold text-green-700 print-attach-next')
        if not raja_results and not yoga_results:
            ui.html(f"<i>{res_str('no_results_str', 'No yogas found.')}</i>")
            return
        if caution:
            ui.html(f"<b>{res_str('yoga_caution_str', 'Yogas shown here are indicative only.')}</b>").classes('mb-2')
        def _section(title_key, title_fallback, items):
            if not items:
                return
            ui.label(res_str(title_key, title_fallback)).classes('font-bold text-brown-700 mt-2')
            for key, (chart, name, desc, pred) in items.items():
                with ui.column().classes('gap-1'):
                    ui.html(f"<b><u>{name} ({chart})</u></b>").classes('print-attach-next')
                    ui.html(f"<b>{res_str('description_str', 'Description')}:</b> {desc}").classes('text-sm')
                    ui.html(f"<b>{res_str('prediction_str', 'Prediction')}:</b> {pred}").classes('text-sm')
        _section('raja_yoga_str', 'Raja Yoga', raja_results)
        _section('yoga_str', 'Yoga', yoga_results)
print_registry.register('yoga', 'Yoga', 'Yoga / Dosha / Prediction', _build_print_section)

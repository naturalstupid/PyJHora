#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Shad Bala page (/shad_bala).
Shows, for the seven planets, the sthaana, kaala, dig, chesta, naisargika and drik bala, the
total shad bala, its rupas and its strength.
"Print / Save as PDF" prints the current result only (single page) - no sub-options, same scope
decision as the rest of the Calculate/Strength menus.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()).
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope import info as horo_info
from components import ( navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        print_button, render_footer, run_io_bound_ctx, )
import print_registry
drik=utils.hora_engine_proxy
ROWS=['sthaana_bala_str','kaala_bala_str','dig_bala_str','chesta_bala_str','naisargika_bala_str','drik_bala_str','shad_bala_str','shad_bala_rupas_str','shad_bala_strength_str']
def _shad_bala_locked(y,m,d,t,pv,lat,lon,tz):
    """Computes the Shad Bala table under calc_lock(); the slow part of compute(), run in a worker
    thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        horo=horo_info.Horoscope(place_with_country_code=pv,latitude=lat,longitude=lon,timezone_offset=tz,date_in=drik.Date(y,m,d),birth_time=f'{t[0]:02d}:{t[1]:02d}:{t[2]:02d}',calculation_type='drik',language=const._DEFAULT_LANGUAGE)
        return horo._get_shad_bala(horo.Date,horo.birth_time,horo.Place)
def _render_shad_bala_table(result, data):
    """Draws the Shad Bala table into `result` - extracted to module level so BOTH the page's own
    on-screen render() and print_registry.py's headless _build_print_section() below use the SAME
    markup.
    """
    with result:
        planets=utils.PLANET_NAMES[:7]
        with ui.element('table').classes('border-collapse text-sm min-w-[900px]'):
            with ui.element('tr'):
                with ui.element('th').classes('border border-gray-400 px-3 py-2 bg-green-50'):ui.label(res_str('shad_bala_str','Shad Bala'))
                for p in planets:
                    with ui.element('th').classes('border border-gray-400 px-3 py-2 bg-green-50'):ui.label(p)
            for r,key in enumerate(ROWS):
                with ui.element('tr'):
                    with ui.element('td').classes('border border-gray-300 px-3 py-2 font-semibold bg-green-50'):ui.label(res_str(key,key.replace('_str','').replace('_',' ').title()))
                    for c in range(7):
                        value=data[r][c] if r < len(data) and c < len(data[r]) else ''
                        with ui.element('td').classes('border border-gray-300 px-3 py-2 text-center'):ui.label(str(value))
@ui.page('/shad_bala')
def shad_bala_page():
    navigation_header();ensure_default_state()
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('shad_bala_str','Shad Bala')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w=render_control_bar(show_dob_tob=True,on_options_saved=lambda:compute(),on_calculate=lambda:compute())
        busy=DelayedBusyIndicator(buttons=w.get('calculate_button'),stop_label=res_str('stop_str','Stop'))
        # Separate, PRINT-VISIBLE title - see bhava_bala_tab.py's own comment for the bug this fixes
        # (the page header above is hidden for print along with print_button(), since they share
        # one 'no-print' row).
        # 'single-chart-print-block' (on the WRAPPER): hides this page's own on-screen content -
        # BOTH the title label AND 'result' - during the global combined "Save as PDF" print
        # (body.printing-all - see components.py's _PRINT_CSS). Without this, this page's own live
        # content stays visible (and duplicates print_registry.py's own headless-built copy) - the
        # same bug confirmed and fixed for amsa_ruler_tab.py's identical title+table pattern.
        with ui.column().classes('w-full gap-1 single-chart-print-block'):
            title=ui.label(res_str('shad_bala_str','Shad Bala')).classes('text-lg font-bold text-green-700 print-attach-next')
            result=ui.column().classes('w-full overflow-x-auto')
    def render(data):
        result.clear()
        _render_shad_bala_table(result, data)
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.',type='warning');return
        try:
            dv=w['dob_input'].value.strip();tv=w['tob_input'].value.strip();pv=w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat=float(w['lat_input'].value);lon=float(w['lon_input'].value);tz=float(w['tz_input'].value);y,m,d=map(int,dv.split(','));tp=[int(x) for x in tv.split(':')];t=tuple((tp+[0])[:3])
        except Exception as ex:safe_notify(f'Error computing Shad Bala: {ex}',type='negative');return
        try:
            data=await busy.run(_shad_bala_locked,y,m,d,t,pv,lat,lon,tz,wait_text=res_str('computing_str','Computing... please wait.'))
        except Exception as ex:safe_notify(f'Error computing Shad Bala: {ex}',type='negative');return
        if data is DelayedBusyIndicator.STOPPED:return
        render(data)
    ui.timer(0.1,compute,once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Reuses _shad_bala_locked() and
    _render_shad_bala_table(), the SAME functions this page's own compute()/render() call.
    """
    try:
        data = await run_io_bound_ctx(_shad_bala_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val, lon_val, tz_val)
    except Exception as ex:
        with container:
            ui.html(f"<i>Error computing Shad Bala: {ex}</i>")
        return
    with container:
        ui.label(res_str('shad_bala_str', 'Shad Bala')).classes('text-base font-bold text-green-700 print-attach-next')
        result = ui.column().classes('w-full')
        _render_shad_bala_table(result, data)
print_registry.register('shad_bala', res_str('shad_bala_str', 'Shad Bala'), 'Strength', _build_print_section)

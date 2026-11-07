#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Vaiseshikamsa Bala page (/vaiseshikamsa_bala).
Shows the vaiseshikamsa score of the planets for the shadvarga, sapthavarga, dhasavarga and
shodhasavarga schemes, one table each.
"Print / Save as PDF" prints the current result only (single page) - no sub-options, same scope
decision as the rest of the Calculate/Strength menus.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()).
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope import info as horo_info
from components import (navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        print_button, render_footer, run_io_bound_ctx, )
import print_registry
drik=utils.hora_engine_proxy
SETS=['shadvarga_bala_str','sapthavarga_bala_str','dhasavarga_bala_str','shodhasavarga_bala_str']
def _vaiseshikamsa_bala_locked(y,m,d,t,pv,lat,lon,tz):
    """Computes the Vaiseshikamsa Bala info under calc_lock(); the slow part of compute(), run in a
    worker thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        horo=horo_info.Horoscope(place_with_country_code=pv,latitude=lat,longitude=lon,timezone_offset=tz,date_in=drik.Date(y,m,d),birth_time=f'{t[0]:02d}:{t[1]:02d}:{t[2]:02d}',calculation_type='drik',language=const._DEFAULT_LANGUAGE)
        return horo._get_vaiseshikamsa_bala(horo.Date,horo.birth_time,horo.Place)
def _render_vaiseshikamsa_table(box, title, items):
    """Draws one Vaiseshikamsa Bala scheme table into `box` - extracted to module level so BOTH the
    page's own on-screen table() and print_registry.py's headless _build_print_section() below use
    the SAME markup.
    """
    with box:
        ui.label(title+'\n'+res_str('vaiseshikamsa_score_str','Vaiseshikamsa Score')).classes('font-bold text-green-700 whitespace-pre-line print-attach-next')
        with ui.element('table').classes('border-collapse text-sm min-w-64'):
            for k,v in items:
                with ui.element('tr'):
                    with ui.element('td').classes('border border-gray-300 px-3 py-2 font-semibold'):ui.label(str(k))
                    with ui.element('td').classes('border border-gray-300 px-3 py-2'):ui.label(str(v))
@ui.page('/vaiseshikamsa_bala')
def vaiseshikamsa_bala_page():
    navigation_header();ensure_default_state()
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('vaiseshikamsa_bala_str','Vaiseshikamsa Bala')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w=render_control_bar(show_dob_tob=True,on_options_saved=lambda:compute(),on_calculate=lambda:compute())
        busy=DelayedBusyIndicator(buttons=w.get('calculate_button'),stop_label=res_str('stop_str','Stop'))
        # 'print-side-by-side': opts these 4 tables back OUT of the global 'table { width: 100% }'
        # print rule, pre-emptively - this page has the identical 4-table-side-by-side shape as
        # Amsa Ruler/Saham/Drishti/Argala, which were all confirmed (via actual printed PDFs) to
        # break into multiple mostly-empty pages without this fix. See components.py's module
        # docstring, "full-bleed table width" note, for the full history.
        # Separate, PRINT-VISIBLE title - see bhava_bala_tab.py's own comment for the bug this fixes
        # (the page header above is hidden for print along with print_button(), since they share
        # one 'no-print' row).
        # 'single-chart-print-block' (on the WRAPPER): hides this page's own on-screen content -
        # BOTH the title label AND 'result' - during the global combined "Save as PDF" print
        # (body.printing-all - see components.py's _PRINT_CSS). Without this, this page's own live
        # content stays visible (and duplicates print_registry.py's own headless-built copy) - the
        # same bug confirmed and fixed for amsa_ruler_tab.py's identical title+table pattern.
        with ui.column().classes('w-full gap-1 single-chart-print-block'):
            title=ui.label(res_str('vaiseshikamsa_bala_str','Vaiseshikamsa Bala')).classes('text-lg font-bold text-green-700 print-attach-next')
            result=ui.row().classes('w-full gap-4 items-start flex-nowrap overflow-x-auto print-side-by-side')
    def table(title,items):
        box = ui.column().classes('min-w-64')
        _render_vaiseshikamsa_table(box, title, items)
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.',type='warning');return
        try:
            dv=w['dob_input'].value.strip();tv=w['tob_input'].value.strip();pv=w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat=float(w['lat_input'].value);lon=float(w['lon_input'].value);tz=float(w['tz_input'].value);y,m,d=map(int,dv.split(','));tp=[int(x) for x in tv.split(':')];t=tuple((tp+[0])[:3])
        except Exception as ex:safe_notify(f'Error computing Vaiseshikamsa Bala: {ex}',type='negative');return
        try:
            info=await busy.run(_vaiseshikamsa_bala_locked,y,m,d,t,pv,lat,lon,tz,wait_text=res_str('computing_str','Computing... please wait.'))
        except Exception as ex:safe_notify(f'Error computing Vaiseshikamsa Bala: {ex}',type='negative');return
        if info is DelayedBusyIndicator.STOPPED:return
        result.clear()
        with result:
            for i,dct in enumerate(info[:4]):
                table(res_str(SETS[i],SETS[i].replace('_str','').replace('_',' ').title()),list(dct.items()))
    ui.timer(0.1,compute,once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Reuses _vaiseshikamsa_bala_locked() and
    _render_vaiseshikamsa_table(), the SAME functions this page's own compute()/table() call.
    """
    try:
        info = await run_io_bound_ctx(_vaiseshikamsa_bala_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val, lon_val, tz_val)
    except Exception as ex:
        with container:
            ui.html(f"<i>Error computing Vaiseshikamsa Bala: {ex}</i>")
        return
    with container:
        ui.label(res_str('vaiseshikamsa_bala_str', 'Vaiseshikamsa Bala')).classes('text-base font-bold text-green-700 print-attach-next')
        result = ui.row().classes('w-full gap-4 items-start flex-nowrap print-side-by-side')
        with result:
            for i, dct in enumerate(info[:4]):
                box = ui.column().classes('min-w-64')
                _render_vaiseshikamsa_table(box, res_str(SETS[i], SETS[i].replace('_str', '').replace('_', ' ').title()), list(dct.items()))
print_registry.register('vaiseshikamsa_bala', res_str('vaiseshikamsa_bala_str', 'Vaiseshikamsa Bala'), 'Strength', _build_print_section)

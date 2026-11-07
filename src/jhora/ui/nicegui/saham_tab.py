#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Saham page (/saham).
Shows the sahams with their rasi and longitude for the chosen divisional chart, in two tables
(the first 18 and the rest). "Chart Options" selects the calculation method of the varga.
"Print / Save as PDF" prints the current selection only (single page) - no "all vargas" mode, same
scope decision as Bhava.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()), using D1 (Rasi) - since the registry calls this function HEADLESSLY (no
live varga selector exists for a page the visitor is not currently on).
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope import info as horo_info
from components import ( navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        print_button, render_footer, run_io_bound_ctx, )
import print_registry
drik=utils.hora_engine_proxy
FACTORS=const.division_chart_factors
NAMES=const._chart_names
VARNADA_OPTIONS=['1=>BV Raman','2=>Sharma/Santhanam','3=>Sanjay Rath','4=>Sitaram Jha']
def label(i):return res_str(NAMES[i],NAMES[i].replace('_str','').replace('_',' ').title())
def _saham_locked(y,m,d,t,lat,lon,tz,f,method,b,e):
    """Computes the Sahams under calc_lock(); the slow part of compute(), run in a worker thread via
    components.DelayedBusyIndicator.run()."""
    with calc_lock():
        horo=horo_info.Horoscope(latitude=lat,longitude=lon,timezone_offset=tz,date_in=drik.Date(y,m,d),birth_time=f'{t[0]:02d}:{t[1]:02d}:{t[2]:02d}',calculation_type='drik',language=const._DEFAULT_LANGUAGE)
        jd=utils.julian_day_number(horo.Date,horo.birth_time)
        _,values=horo.get_sahams(jd,horo.Place,divisional_chart_factor=f,chart_method=method,base_rasi=b,count_from_end_of_sign=e,dhasa_progression_correction=0.0)
        return values
def _render_saham_table(rows):
    """Draws one Saham table (returned as a NiceGUI table element) - extracted to module level so
    BOTH the page's own on-screen table() and print_registry.py's headless _build_print_section()
    below use the SAME markup. Must be called inside the context it should appear in (e.g. `with
    result:`), since it does not take a container argument.
    """
    with ui.element('table').classes('border-collapse text-sm min-w-80'):
        with ui.element('tr'):
            for h in (res_str('saham_str','Saham'),res_str('raasi_str','Raasi')+' '+res_str('longitude_str','Longitude')):
                with ui.element('th').classes('border border-gray-400 px-3 py-2 bg-green-50'): ui.label(h).classes('font-bold')
        for a,b in rows:
            with ui.element('tr'):
                with ui.element('td').classes('border border-gray-300 px-3 py-1'): ui.label(str(a))
                with ui.element('td').classes('border border-gray-300 px-3 py-1'): ui.label(str(b))
def _render_saham_rows(container, rows):
    """Splits `rows` into the first 18 and the rest, and draws each half's table (via
    _render_saham_table()) into `container`."""
    with container:
        items=list(rows); left=items[:18]; right=items[18:]
        _render_saham_table(left)
        if right: _render_saham_table(right)
@ui.page('/saham')
def saham_page():
    navigation_header(); ensure_default_state(); methods={}
    _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('saham_str','Saham')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w=render_control_bar(show_dob_tob=True,on_options_saved=lambda:compute(),on_calculate=lambda:compute())
        busy=DelayedBusyIndicator(buttons=w.get('calculate_button'),stop_label=res_str('stop_str','Stop'))
        with w['row2']:
            sel=ui.select({i:label(i) for i in range(len(FACTORS))},value=0,label='Varga').props('outlined dense').classes('w-56')
            chart_btn=ui.button(_chart_options_nls,on_click=lambda:chart_options()).props('outlined dense')
            chart_info=ui.label('').classes('text-sm font-semibold')
        # 'print-attach-next' / 'print-side-by-side' - see components.py's module docstring,
        # "full-bleed table width" note, for the full history (confirmed from an actual printed PDF
        # that this exact pattern - 2 tables meant to sit side by side - was turning 1 compact page
        # into 2 because the global 'table { width: 100% }' print rule forced each table to claim
        # the full row width, stacking them instead of sitting side by side).
        # 'single-chart-print-block' (on the WRAPPER): hides this page's own on-screen content -
        # BOTH the title label AND 'result' - during the global combined "Save as PDF" print
        # (body.printing-all - see components.py's _PRINT_CSS). Without this, this page's own live
        # content stays visible (and duplicates print_registry.py's own headless-built copy) - the
        # same bug confirmed and fixed for amsa_ruler_tab.py's identical title+table pattern.
        with ui.column().classes('w-full gap-1 single-chart-print-block'):
            title=ui.label('').classes('text-lg font-bold text-green-700 print-attach-next')
            result=ui.row().classes('w-full gap-5 items-start flex-wrap print-side-by-side')
    def idx(): return sel.value if isinstance(sel.value,int) else 0
    def md(i):
        if i==0:return 1,1,None,None
        try:
            n,m,b,e=utils.get_varga_option_dict()[FACTORS[i]];return n or 1,m or 1,b,e
        except Exception:return 1,1,None,None
    def refresh():
        i=idx();n,m,_,_=md(i);f=FACTORS[i];m=methods.get(i,m);chart_info.set_text(res_str(f'd{f}_option{m}_str',f'Method {m}'))
        chart_btn.enable() if n>1 else chart_btn.disable()
    def chart_options():
        i=idx();n,m,_,_=md(i)
        if n<=1:return
        f=FACTORS[i];cur=methods.get(i,m)
        with ui.dialog() as dlg,ui.card().classes('gap-3'):
            r=ui.radio({x:res_str(f'd{f}_option{x+1}_str',f'Method {x+1}') for x in range(n)},value=cur-1)
            async def save(): methods[i]=int(r.value)+1;dlg.close();refresh();await compute()
            ui.button('Accept',on_click=save)
        dlg.open()
    def render(rows):
        result.clear()
        _render_saham_rows(result, rows)
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.',type='warning');return
        try:
            dv=w['dob_input'].value.strip();tv=w['tob_input'].value.strip();lat=float(w['lat_input'].value);lon=float(w['lon_input'].value);tz=float(w['tz_input'].value);y,m,d=map(int,dv.split(','));tp=[int(x) for x in tv.split(':')];t=tuple((tp+[0])[:3]);i=idx();f=FACTORS[i];_,dm,b,e=md(i);method=methods.get(i,dm)
        except Exception as ex: safe_notify(f'Error computing Sahams: {ex}',type='negative');return
        try:
            values=await busy.run(_saham_locked,y,m,d,t,lat,lon,tz,f,method,b,e,wait_text=res_str('computing_str','Computing... please wait.'))
        except Exception as ex: safe_notify(f'Error computing Sahams: {ex}',type='negative');return
        if values is DelayedBusyIndicator.STOPPED:return
        title.set_text(f"{label(i)} - {res_str('saham_str','Saham')}");render(list(values.items()))
    async def _on_sel_changed(e):refresh();await compute()
    sel.on_value_change(_on_sel_changed);refresh();ui.timer(0.1,compute,once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Uses D1 (Rasi) - the default varga this page
    itself shows on first load. Reuses _saham_locked() and _render_saham_rows(), the SAME functions
    this page's own compute()/render() call.
    """
    try:
        values = await run_io_bound_ctx(_saham_locked, dob[0], dob[1], dob[2], tob, lat_val, lon_val, tz_val, 1, 1, None, None)
    except Exception as ex:
        with container:
            ui.html(f"<i>Error computing Sahams: {ex}</i>")
        return
    with container:
        ui.label(f"{label(0)} - {res_str('saham_str', 'Saham')}").classes('text-base font-bold text-green-700 print-attach-next')
        result = ui.row().classes('w-full gap-5 items-start flex-wrap print-side-by-side')
        _render_saham_rows(result, list(values.items()))
print_registry.register('saham', res_str('saham_str', 'Saham'), 'Calculations', _build_print_section)

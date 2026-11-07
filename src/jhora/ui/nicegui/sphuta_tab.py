#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Sphuta and Varnada Lagna page (/sphuta).
Shows the sphutas and the varnada lagnas for the chosen divisional chart as two tables.
"Chart Options" selects the calculation method of the varga; "Varnada Options" selects the
varnada method (1 BV Raman, 2 Sharma/Santhanam, 3 Sanjay Rath, 4 Sitaram Jha).
"Print / Save as PDF" prints the current selection only (single page) - no "all vargas" mode, same
scope decision as Bhava.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()), using D1 (Rasi) and the default Varnada method (1, BV Raman) - since the
registry calls this function HEADLESSLY (no live selectors exist for a page the visitor is not
currently on).
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope import info as horo_info
from components import (navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        print_button, render_footer, run_io_bound_ctx,  )
import print_registry
drik=utils.hora_engine_proxy
FACTORS=const.division_chart_factors
NAMES=const._chart_names
VARNADA_OPTIONS=['1=>BV Raman','2=>Sharma/Santhanam','3=>Sanjay Rath','4=>Sitaram Jha']
def label(i):return res_str(NAMES[i],NAMES[i].replace('_str','').replace('_',' ').title())
def _sphuta_locked(y,m,d,t,lat,lon,tz,f,method,b,e,varnada_method_value):
    """Computes the Sphuta and Varnada Lagna values under calc_lock(); the slow part of compute(), run
    in a worker thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        horo=horo_info.Horoscope(latitude=lat,longitude=lon,timezone_offset=tz,date_in=drik.Date(y,m,d),birth_time=f'{t[0]:02d}:{t[1]:02d}:{t[2]:02d}',calculation_type='drik',language=const._DEFAULT_LANGUAGE)
        sv=horo._get_sphuta(horo.Date,horo.birth_time,horo.Place,divisional_chart_factor=f,chart_method=method,base_rasi=b,count_from_end_of_sign=e,dhasa_progression_correction=0.0)
        vv=horo._get_varnada(horo.Date,horo.birth_time,horo.Place,divisional_chart_factor=f,chart_method=method,base_rasi=b,count_from_end_of_sign=e,dhasa_progression_correction=0.0,varnada_method=varnada_method_value)
        return sv,vv
def _render_sphuta_table(box, heading, rows):
    """Draws one Sphuta/Varnada table into `box` - extracted to module level so BOTH the page's own
    on-screen render() and print_registry.py's headless _build_print_section() below use the SAME
    markup.
    """
    with box:
        ui.label(heading).classes('font-bold text-green-700 print-attach-next')
        with ui.element('table').classes('border-collapse text-sm'):
            with ui.element('tr'):
                for h in (heading,res_str('raasi_str','Raasi')):
                    with ui.element('th').classes('border border-gray-400 px-3 py-2 bg-green-50'):ui.label(h)
            for a,b in rows:
                with ui.element('tr'):
                    with ui.element('td').classes('border border-gray-300 px-3 py-1'):ui.label(str(a))
                    with ui.element('td').classes('border border-gray-300 px-3 py-1'):ui.label(str(b))
@ui.page('/sphuta')
def sphuta_page():
    navigation_header();ensure_default_state();methods={};varnada_method={'value':1}
    _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
    _vernada_option_str = res_str('varnada_str','Varnada')+' '+res_str('options_str','Options')
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(f"{res_str('sphuta_str','Sphuta')} - {res_str('varnada_lagna_str','Varnada Lagna')}").classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w=render_control_bar(show_dob_tob=True,on_options_saved=lambda:compute(),on_calculate=lambda:compute())
        busy=DelayedBusyIndicator(buttons=w.get('calculate_button'),stop_label=res_str('stop_str','Stop'))
        with w['row2']:
            sel=ui.select({i:label(i) for i in range(len(FACTORS))},value=0,label='Varga').props('outlined dense').classes('w-56')
            chart_btn=ui.button(_chart_options_nls,on_click=lambda:chart_options()).props('outlined dense')
            chart_info=ui.label('').classes('text-sm font-semibold')
            var_btn=ui.button(_vernada_option_str,on_click=lambda:varnada_options()).props('outlined dense')
            var_info=ui.label(VARNADA_OPTIONS[0]).classes('text-sm font-semibold')
        # 'single-chart-print-block' (on the WRAPPER): hides this page's own on-screen content -
        # BOTH the title label AND the sphuta/varnada boxes below - during the global combined
        # "Save as PDF" print (body.printing-all - see components.py's _PRINT_CSS). Without this,
        # this page's own live content stays visible (and duplicates print_registry.py's own
        # headless-built copy) - the same bug confirmed and fixed for amsa_ruler_tab.py's identical
        # title+table pattern.
        with ui.column().classes('w-full gap-1 single-chart-print-block'):
            title=ui.label('').classes('text-lg font-bold text-green-700 print-attach-next')
            with ui.row().classes('w-full gap-6 items-start flex-wrap print-side-by-side'):
                sphuta_box=ui.column().classes('min-w-80')
                varnada_box=ui.column().classes('min-w-80')
    def idx():return sel.value if isinstance(sel.value,int) else 0
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
        with ui.dialog() as dlg,ui.card():
            r=ui.radio({x:res_str(f'd{f}_option{x+1}_str',f'Method {x+1}') for x in range(n)},value=cur-1)
            async def save():methods[i]=int(r.value)+1;dlg.close();refresh();await compute()
            ui.button('Accept',on_click=save)
        dlg.open()
    def varnada_options():
        with ui.dialog() as dlg,ui.card():
            r=ui.radio({i:x for i,x in enumerate(VARNADA_OPTIONS)},value=varnada_method['value']-1)
            async def save():varnada_method['value']=int(r.value)+1;var_info.set_text(VARNADA_OPTIONS[int(r.value)]);dlg.close();await compute()
            ui.button('Accept',on_click=save)
        dlg.open()
    def render(box,heading,rows):
        box.clear()
        _render_sphuta_table(box, heading, rows)
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.',type='warning');return
        try:
            dv=w['dob_input'].value.strip();tv=w['tob_input'].value.strip();lat=float(w['lat_input'].value);lon=float(w['lon_input'].value);tz=float(w['tz_input'].value);y,m,d=map(int,dv.split(','));tp=[int(x) for x in tv.split(':')];t=tuple((tp+[0])[:3]);i=idx();f=FACTORS[i];_,dm,b,e=md(i);method=methods.get(i,dm)
        except Exception as ex:safe_notify(f'Error computing Sphuta/Varnada: {ex}',type='negative');return
        try:
            result=await busy.run(_sphuta_locked,y,m,d,t,lat,lon,tz,f,method,b,e,varnada_method['value'],wait_text=res_str('computing_str','Computing... please wait.'))
        except Exception as ex:safe_notify(f'Error computing Sphuta/Varnada: {ex}',type='negative');return
        if result is DelayedBusyIndicator.STOPPED:return
        sv,vv=result
        title.set_text(f"{res_str('sphuta_str','Sphuta')} - {res_str('varnada_lagna_str','Varnada Lagna')} - {label(i)}");render(sphuta_box,res_str('sphuta_str','Sphuta'),list(sv.items()));render(varnada_box,res_str('varnada_lagna_str','Varnada Lagna'),list(vv.items()))
    async def _on_sel_changed(e):refresh();await compute()
    sel.on_value_change(_on_sel_changed);refresh();ui.timer(0.1,compute,once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Uses D1 (Rasi) and Varnada method 1 (BV Raman) -
    the defaults this page itself shows on first load. Reuses _sphuta_locked() and
    _render_sphuta_table(), the SAME functions this page's own compute()/render() call.
    """
    try:
        sv, vv = await run_io_bound_ctx(_sphuta_locked, dob[0], dob[1], dob[2], tob, lat_val, lon_val, tz_val, 1, 1, None, None, 1)
    except Exception as ex:
        with container:
            ui.html(f"<i>Error computing Sphuta/Varnada: {ex}</i>")
        return
    with container:
        ui.label(f"{res_str('sphuta_str', 'Sphuta')} - {res_str('varnada_lagna_str', 'Varnada Lagna')} - {label(0)}") \
            .classes('text-base font-bold text-green-700 print-attach-next')
        with ui.row().classes('w-full gap-6 items-start flex-wrap print-side-by-side'):
            sphuta_box = ui.column().classes('min-w-80')
            varnada_box = ui.column().classes('min-w-80')
        _render_sphuta_table(sphuta_box, res_str('sphuta_str', 'Sphuta'), list(sv.items()))
        _render_sphuta_table(varnada_box, res_str('varnada_lagna_str', 'Varnada Lagna'), list(vv.items()))
print_registry.register('sphuta', res_str('sphuta_str', 'Sphuta') + ' / ' + res_str('varnada_lagna_str', 'Varnada Lagna'), 'Calculations', _build_print_section)

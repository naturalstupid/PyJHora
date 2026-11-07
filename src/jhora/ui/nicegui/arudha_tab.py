#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Graha / Bhava Arudha page (/arudha).
Shows, for the chosen divisional chart, the Graha Arudhas (ascendant and the nine planets) and
the Bhava Arudhas (A1-A12, or the planet-based equivalents for another base), each as rasi and
longitude. "Chart Options" selects the calculation method of the varga; the base selector
chooses the Bhava Arudha base.
"Print / Save as PDF" prints the current selection only (single page) - no "all vargas" mode, same
scope decision as Bhava.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()), using the D1 (Rasi) default and Bhava Arudha base 0 (A1..A12) - not
whatever this page's own widgets currently show, since the registry calls this function
HEADLESSLY.
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope.chart import charts, arudhas
from components import (navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        print_button, render_footer, run_io_bound_ctx,)
import print_registry
drik=utils.hora_engine_proxy
FACTORS=const.division_chart_factors
NAMES=const._chart_names
def vlabel(i): return res_str(NAMES[i],NAMES[i].replace('_str','').replace('_',' ').title())
def parse_time(s):
    p=[int(x) for x in str(s).strip().split(':')];return tuple((p+[0])[:3])
def _arudha_locked(y,m,d,t,pv,lat,lon,tz,f,method,br,ce,base_idx):
    """Computes the Graha/Bhava Arudha longitudes under calc_lock(); the slow part of compute(), run
    in a worker thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        jd=utils.julian_day_number(drik.Date(y,m,d),t);place=drik.Place(pv,lat,lon,tz,0.0)
        pp=charts.divisional_chart(jd,place,divisional_chart_factor=f,chart_method=method,base_rasi=br,count_from_end_of_sign=ce,dhasa_progression_correction=0.0,exclude_non_planets=True)
        ba=arudhas.bhava_arudha_longitudes(jd,place,arudha_base=base_idx,divisional_chart_factor=f,chart_method=method)
        ga=arudhas.graha_arudhas_from_planet_positions(pp)
        return ba,ga
def _render_arudha_table(box, heading, rows):
    """Draws one Arudha table (name/value rows) into `box` - extracted to module level so BOTH the
    page's own on-screen render() and print_registry.py's headless _build_print_section() below use
    the SAME markup.
    """
    with box:
        ui.label(heading).classes('font-bold text-green-700 print-attach-next')
        with ui.element('table').classes('border-collapse text-sm min-w-80'):
            for a,b in rows:
                with ui.element('tr'):
                    with ui.element('td').classes('border border-gray-300 px-3 py-2 font-semibold'):ui.label(str(a))
                    with ui.element('td').classes('border border-gray-300 px-3 py-2'):ui.label(str(b))
@ui.page('/arudha')
def arudha_page():
    navigation_header();ensure_default_state();methods={}
    bases=list(const._bhava_arudha_list)
    _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('bhava_graha_arudha_str','Bhava / Graha Arudha')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w=render_control_bar(show_dob_tob=True,on_options_saved=lambda:compute(),on_calculate=lambda:compute())
        busy=DelayedBusyIndicator(buttons=w.get('calculate_button'),stop_label=res_str('stop_str','Stop'))
        with w['row2']:
            varga=ui.select({i:vlabel(i) for i in range(len(FACTORS))},value=0,label='Varga (Divisional Chart)').props('outlined dense').classes('w-56')
            opt=ui.button(_chart_options_nls,on_click=lambda:open_options()).props('outlined dense')
            opt_info=ui.label('').classes('text-sm font-semibold')
            base=ui.select({i:res_str(x,x) for i,x in enumerate(bases)},value=0,label=res_str('bhava_arudha_str','Bhava Arudha Base')).props('outlined dense').classes('w-64')
        # 'single-chart-print-block' (on the WRAPPER): hides this page's own on-screen content -
        # BOTH the title label AND the graha/bhava boxes below - during the global combined
        # "Save as PDF" print (body.printing-all - see components.py's _PRINT_CSS). Without this,
        # this page's own live content stays visible (and duplicates print_registry.py's own
        # headless-built copy) - the same bug confirmed and fixed for amsa_ruler_tab.py's identical
        # title+table pattern.
        with ui.column().classes('w-full gap-1 single-chart-print-block'):
            title=ui.label('').classes('text-lg font-bold text-green-700 print-attach-next')
            with ui.row().classes('w-full gap-8 items-start flex-wrap print-side-by-side'):
                graha_box=ui.column().classes('min-w-96')
                bhava_box=ui.column().classes('min-w-96')
    def idx():return varga.value if isinstance(varga.value,int) else 0
    def md(i):
        if i==0:return 1,1,None,None
        try:
            n,m,b,e=utils.get_varga_option_dict()[FACTORS[i]];return n or 1,m or 1,b,e
        except Exception:return 1,1,None,None
    def refresh():
        i=idx();n,m,_,_=md(i);f=FACTORS[i];m=methods.get(i,m);opt_info.set_text('' if i==0 else res_str(f'd{f}_option{m}_str',f'Method {m}'));opt.enable() if n>1 else opt.disable()
    def open_options():
        i=idx();n,m,_,_=md(i)
        if n<=1:return
        f=FACTORS[i];cur=methods.get(i,m)
        with ui.dialog() as dlg,ui.card().classes('gap-3'):
            r=ui.radio({x:res_str(f'd{f}_option{x+1}_str',f'Method {x+1}') for x in range(n)},value=cur-1)
            async def save():methods[i]=int(r.value)+1;dlg.close();refresh();await compute()
            ui.button('Accept',on_click=save)
        dlg.open()
    def render(box,heading,rows):
        box.clear()
        _render_arudha_table(box, heading, rows)
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.',type='warning');return
        try:
            dv=w['dob_input'].value.strip();tv=w['tob_input'].value.strip();pv=w['place_select'].value.strip() if w['place_select'].value else 'Chennai';lat=float(w['lat_input'].value);lon=float(w['lon_input'].value);tz=float(w['tz_input'].value);y,m,d=map(int,dv.split(','));t=parse_time(tv);i=idx();f=FACTORS[i];_,dm,br,ce=md(i);method=methods.get(i,dm);base_idx=int(base.value or 0)
        except Exception as ex:safe_notify(f'Error computing Arudhas: {ex}',type='negative');return
        try:
            result=await busy.run(_arudha_locked,y,m,d,t,pv,lat,lon,tz,f,method,br,ce,base_idx,
                                  wait_text=res_str('computing_str','Computing... please wait.'))
        except Exception as ex:safe_notify(f'Error computing Arudhas: {ex}',type='negative');return
        if result is DelayedBusyIndicator.STOPPED:return
        ba,ga=result
        grows=[(res_str('ascendant_str','Ascendant'),utils.RAASI_LIST[ga[0][0]]+' '+utils.to_dms(ga[0][1],is_lat_long='plong'))]
        for p in range(9):grows.append((utils.PLANET_NAMES[p],utils.RAASI_LIST[ga[p+1][0]]+' '+utils.to_dms(ga[p+1][1],is_lat_long='plong')))
        brows=[]
        for h,val in enumerate(ba):
            z,l=drik.dasavarga_from_long(val)
            name=res_str(f'bhava_arudha_a{h+1}_str',f'A{h+1}') if base_idx==0 else utils.PLANET_NAMES[base_idx-1]+'-'+str(h+1)
            brows.append((name,utils.RAASI_LIST[z]+' '+utils.to_dms(l,is_lat_long='plong')))
        title.set_text(f"{res_str('bhava_graha_arudha_str','Bhava / Graha Arudha')} - {vlabel(i)}");render(graha_box,res_str('graha_arudha_str','Graha Arudha'),grows);render(bhava_box,res_str('bhava_arudha_str','Bhava Arudha'),brows)
    varga.on_value_change(lambda e:refresh());base.on_value_change(lambda e:compute());refresh();ui.timer(0.1,compute,once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Uses D1 (Rasi) and Bhava Arudha base 0
    (A1..A12) - the defaults this page itself shows on first load. Reuses _arudha_locked() and
    _render_arudha_table(), the SAME functions this page's own compute()/render() call.
    """
    try:
        ba, ga = await run_io_bound_ctx(_arudha_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val, lon_val,
                                    tz_val, 1, 1, None, None, 0)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing Arudhas: {e}</i>")
        return
    grows = [(res_str('ascendant_str', 'Ascendant'), utils.RAASI_LIST[ga[0][0]] + ' ' + utils.to_dms(ga[0][1], is_lat_long='plong'))]
    for p in range(9):
        grows.append((utils.PLANET_NAMES[p], utils.RAASI_LIST[ga[p + 1][0]] + ' ' + utils.to_dms(ga[p + 1][1], is_lat_long='plong')))
    brows = []
    for h, val in enumerate(ba):
        z, l = drik.dasavarga_from_long(val)
        brows.append((res_str(f'bhava_arudha_a{h + 1}_str', f'A{h + 1}'), utils.RAASI_LIST[z] + ' ' + utils.to_dms(l, is_lat_long='plong')))
    with container:
        ui.label(f"{res_str('bhava_graha_arudha_str', 'Bhava / Graha Arudha')} - {vlabel(0)}").classes('text-base font-bold text-green-700 print-attach-next')
        with ui.row().classes('w-full gap-8 items-start flex-wrap print-side-by-side'):
            graha_box = ui.column().classes('min-w-96')
            bhava_box = ui.column().classes('min-w-96')
        _render_arudha_table(graha_box, res_str('graha_arudha_str', 'Graha Arudha'), grows)
        _render_arudha_table(bhava_box, res_str('bhava_arudha_str', 'Bhava Arudha'), brows)
print_registry.register('arudha', res_str('bhava_graha_arudha_str', 'Bhava / Graha Arudha'), 'Calculations', _build_print_section)

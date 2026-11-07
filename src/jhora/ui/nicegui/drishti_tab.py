#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Drishti page (/drishti).
Shows, for the chosen divisional chart, the graha drishti (seven planets) and the raasi drishti
(nine planets): the rasis, houses and planets aspected by each. "Chart Options" selects the
calculation method of the varga.
"Print / Save as PDF" prints the current selection only (single page) - no "all vargas" mode, same
scope decision as Bhava.
"""
from nicegui import ui
from jhora import const, utils
from jhora.horoscope import info as horo_info
from jhora.horoscope.chart import house
from components import (navigation_header, render_control_bar, ensure_default_state, 
                        calc_lock, res_str, safe_notify, ignore_disconnected_client, 
                        DelayedBusyIndicator, print_button, run_io_bound_ctx,
)
drik = utils.hora_engine_proxy
FACTORS = const.division_chart_factors
NAMES = const._chart_names
def varga_label(i):
    return res_str(NAMES[i], NAMES[i].replace('_str','').replace('_',' ').title())
def _parse_time(value):
    p=[int(x) for x in str(value).strip().split(':')]
    return tuple((p+[0])[:3])
def _chart_to_indices(chart_1d):
    # Replaces localized planet names in the chart strings by planet indices.
    result=list(chart_1d)
    local_names=utils.PLANET_NAMES+[res_str('ascendant_str','Ascendant')]
    english=['Sun   ','Moon   ','Mars   ','Mercury   ','Jupiter   ','Venus   ','Saturn   ','Raagu   ','Kethu   ','Uranus','Neptune','Pluto','Lagnam']
    for src,dst in zip(local_names,english):
        result=[x.replace(src,dst) for x in result]
    values=[str(i) for i in range(12)]+[const._ascendant_symbol]
    for src,dst in zip(english,values):
        result=[x.replace(src,dst).replace(const._stationary_symbol,'').replace(const._retrogade_symbol,'') for x in result]
    return result
def _drishti_locked(y,m,d,t,pv,lat,lon,tz,i,method,f,b,e):
    """Computes the graha and raasi drishti under calc_lock(); the slow part of compute(), run in a
    worker thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        horo=horo_info.Horoscope(place_with_country_code=pv,latitude=lat,longitude=lon,timezone_offset=tz,date_in=drik.Date(y,m,d),birth_time=f'{t[0]:02d}:{t[1]:02d}:{t[2]:02d}',calculation_type='drik',language=const._DEFAULT_LANGUAGE)
        _,chart_1d,_=horo.get_horoscope_information_for_chart(i,method,divisional_chart_factor=f,base_rasi=b,count_from_end_of_sign=e,varnada_method=1,dhasa_progression_correction=0.0)
        chart_ind=_chart_to_indices(chart_1d)
        r_arp,r_ahp,r_app=house.raasi_drishti_from_chart(chart_ind,'\n')
        g_arp,g_ahp,g_app=house.graha_drishti_from_chart(chart_ind,'\n')
        return r_arp,r_ahp,r_app,g_arp,g_ahp,g_app
@ui.page('/drishti')
def drishti_page():
    navigation_header(); ensure_default_state(); method_state={}
    _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('drishti_str','Drishti')).classes('text-xl font-bold text-green-700')
            print_button()
        w=render_control_bar(show_dob_tob=True,on_options_saved=lambda:compute(),on_calculate=lambda:compute())
        busy=DelayedBusyIndicator(buttons=w.get('calculate_button'),stop_label=res_str('stop_str','Stop'))
        with w['row2']:
            varga=ui.select({i:varga_label(i) for i in range(len(FACTORS))},value=0,label='Varga (Divisional Chart)').props('outlined dense').classes('w-56')
            option_btn=ui.button(_chart_options_nls,on_click=lambda:open_options()).props('outlined dense')
            option_info=ui.label('').classes('text-sm font-semibold')
        # 'print-attach-next' / 'print-side-by-side' - see components.py's module docstring,
        # "full-bleed table width" note, for the full history (confirmed from an actual printed PDF
        # that this exact pattern - 2 boxes meant to sit side by side - was turning 1 compact page
        # into 3 because the global 'table { width: 100% }' print rule forced each table to claim
        # the full row width, stacking them instead of sitting side by side).
        title=ui.label('').classes('text-lg font-bold text-green-700 print-attach-next')
        with ui.row().classes('w-full gap-6 items-start flex-wrap print-side-by-side'):
            graha_box=ui.column().classes('min-w-[520px]')
            raasi_box=ui.column().classes('min-w-[620px]')
    def index(): return varga.value if isinstance(varga.value,int) else 0
    def method_data(i):
        if i==0:return 1,1,None,None
        try:
            n,m,b,e=utils.get_varga_option_dict()[FACTORS[i]];return n or 1,m or 1,b,e
        except Exception:return 1,1,None,None
    def refresh_options():
        i=index(); n,m,_,_=method_data(i); f=FACTORS[i]; chosen=method_state.get(i,m)
        option_info.set_text('' if i==0 else res_str(f'd{f}_option{chosen}_str',f'Method {chosen}'))
        option_btn.enable() if n>1 else option_btn.disable()
    def open_options():
        i=index(); n,m,_,_=method_data(i)
        if n<=1:return
        f=FACTORS[i];cur=method_state.get(i,m)
        with ui.dialog() as dlg,ui.card().classes('gap-3'):
            ui.label(f'{varga_label(i)} Options').classes('font-bold text-green-700')
            r=ui.radio({x:res_str(f'd{f}_option{x+1}_str',f'Method {x+1}') for x in range(n)},value=cur-1)
            async def save(): method_state[i]=int(r.value)+1;dlg.close();refresh_options();await compute()
            with ui.row(): ui.button('Cancel',on_click=dlg.close).props('outlined');ui.button('Accept',on_click=save)
        dlg.open()
    def table(box, heading, row_names, arp, ahp, app):
        box.clear()
        headers=[res_str('raasis_str','Raasis'),res_str('houses_str','Houses'),res_str('planets_str','Planets')]
        with box:
            # 'print-attach-next': keeps THIS box's own heading attached to the start of its own
            # table (each box's heading+table pair could otherwise be split apart from each other
            # independently of the fix above, which only addresses the two boxes sitting side by
            # side).
            ui.label(heading).classes('font-bold text-green-700 print-attach-next')
            with ui.element('table').classes('border-collapse text-sm w-full'):
                with ui.element('tr'):
                    with ui.element('th').classes('border border-gray-400 px-3 py-2 bg-green-50'):ui.label(res_str('planet_str','Planet'))
                    for h in headers:
                        with ui.element('th').classes('border border-gray-400 px-3 py-2 bg-green-50'):ui.label(h)
                for row,pname in enumerate(row_names):
                    ras='\n'.join(utils.RAASI_LIST[x] for x in arp[row])
                    houses='\n'.join(const.houses_str[x-1] for x in ahp[row])
                    planets='\n'.join(utils.PLANET_NAMES[int(x)] for x in app[row] if x!='' and x!=const._ascendant_symbol)
                    with ui.element('tr'):
                        for text,bold in [(pname,True),(ras,False),(houses,False),(planets,False)]:
                            with ui.element('td').classes('border border-gray-300 px-3 py-2 align-top whitespace-pre-line'):
                                ui.label(text).classes(('font-bold ' if bold else '')+'whitespace-pre-line')
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.',type='warning');return
        try:
            dv=w['dob_input'].value.strip(); tv=w['tob_input'].value.strip(); pv=w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat=float(w['lat_input'].value); lon=float(w['lon_input'].value); tz=float(w['tz_input'].value)
            y,m,d=map(int,dv.split(',')); t=_parse_time(tv); i=index(); f=FACTORS[i]; _,dm,b,e=method_data(i); method=method_state.get(i,dm)
        except Exception as ex:
            safe_notify(f'Error computing Drishti: {ex}',type='negative');return
        try:
            result=await busy.run(_drishti_locked,y,m,d,t,pv,lat,lon,tz,i,method,f,b,e,
                                  wait_text=res_str('computing_str','Computing... please wait.'))
        except Exception as ex:
            safe_notify(f'Error computing Drishti: {ex}',type='negative');return
        if result is DelayedBusyIndicator.STOPPED:
            return
        r_arp,r_ahp,r_app,g_arp,g_ahp,g_app=result
        title.set_text(f"{varga_label(i)} - {res_str('graha_str','Graha')}-{res_str('raasi_str','Rasi')}-{res_str('drishti_str','Drishti')}")
        table(graha_box,res_str('graha_str','Graha')+' '+res_str('drishti_str','Drishti'),utils.PLANET_NAMES[:7],g_arp,g_ahp,g_app)
        table(raasi_box,res_str('raasi_str','Raasi')+' '+res_str('drishti_str','Drishti'),utils.PLANET_NAMES[:9],r_arp,r_ahp,r_app)
    varga.on_value_change(lambda e:refresh_options());refresh_options();ui.timer(0.1,compute,once=True)

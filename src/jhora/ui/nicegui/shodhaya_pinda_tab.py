"""Shodhaya Pinda page (/shodhaya_pinda).
Shows, for the chosen divisional chart, the ashtakavarga after trikona and ekadhipatya sodhana
(seven planets, ascendant and SAV by rasi) and the graha, raasi and shodhaya pindas of the seven
planets. "Chart Options" selects the calculation method of the varga.
"Print / Save as PDF" prints the current selection only (single page) - no "all vargas" mode, same
scope decision as Bhava.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()), using D1 (Rasi) - since the registry calls this function HEADLESSLY (no
live varga selector exists for a page the visitor is not currently on).
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope import info as horo_info
from jhora.horoscope.chart import ashtakavarga
import numpy as np
from components import (navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        print_button, render_footer, run_io_bound_ctx,  )
import print_registry
drik=utils.hora_engine_proxy; FACTORS=const.division_chart_factors; NAMES=const._chart_names
def vlabel(i): return res_str(NAMES[i],NAMES[i].replace('_str','').replace('_',' ').title())
def _convert(chart):
    o=list(chart);local=utils.PLANET_NAMES+[res_str('ascendant_str','Ascendant')];eng=['Sun   ','Moon   ','Mars   ','Mercury   ','Jupiter   ','Venus   ','Saturn   ','Raagu   ','Kethu   ','Uranus','Neptune','Pluto','Lagnam'];vals=[str(i) for i in range(12)]+[const._ascendant_symbol]
    for s,d in zip(local,eng):o=[x.replace(s,d) for x in o]
    for s,d in zip(eng,vals):o=[x.replace(s,d).replace(const._stationary_symbol,'').replace(const._retrogade_symbol,'') for x in o]
    return o
def _shodhaya_pinda_locked(y,m,d,t,pv,lat,lon,tz,i,method,f,b,e):
    """Computes the Shodhaya Pinda tables under calc_lock(); the slow part of compute(), run in a
    worker thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        h=horo_info.Horoscope(place_with_country_code=pv,latitude=lat,longitude=lon,timezone_offset=tz,date_in=drik.Date(y,m,d),birth_time=f'{t[0]:02d}:{t[1]:02d}:{t[2]:02d}',calculation_type='drik',language=const._DEFAULT_LANGUAGE);_,chart,_=h.get_horoscope_information_for_chart(i,method,divisional_chart_factor=f,base_rasi=b,count_from_end_of_sign=e,varnada_method=1,dhasa_progression_correction=0.0);bav,_,_=ashtakavarga.get_ashtaka_varga(_convert(chart)); tri=ashtakavarga._trikona_sodhana(bav); eka=ashtakavarga._ekadhipatya_sodhana(tri,_convert(chart)); sav=np.asarray(eka).sum(axis=0).tolist(); raasi_pindas,graha_pindas,shodya_pindas=ashtakavarga._sodhya_pindas(eka,_convert(chart))
        return eka,sav,raasi_pindas,graha_pindas,shodya_pindas
def _render_shodhaya_pinda(container, eka,sav,raasi_pindas,graha_pindas,shodya_pindas):
    """Draws both Shodhaya Pinda tables into `container` - extracted to module level so BOTH the
    page's own on-screen render() and print_registry.py's headless _build_print_section() below use
    the SAME markup.
    """
    names=utils.PLANET_NAMES[:7]+[res_str('ascendant_str','Ascendant'),res_str('sav_str','SAV')]
    rows=list(eka[:8])+[sav]
    with container:
        ui.label(res_str('ashtaka_varga_str','Ashtakavarga')+' ('+res_str('trikona_str','Trikona')+' - '+res_str('ekadhipathya_str','Ekadhipathya')+')').classes('font-bold text-green-700 print-attach-next')
        with ui.element('table').classes('border-collapse text-sm min-w-[1000px]'):
            with ui.element('tr'):
                with ui.element('th').classes('border px-2 py-2 bg-green-50'):ui.label('')
                for r in utils.RAASI_LIST:
                    with ui.element('th').classes('border px-2 py-2 bg-green-50'):ui.label(r)
            for n,vals in zip(names,rows):
                with ui.element('tr'):
                    with ui.element('td').classes('border px-2 py-2 font-bold bg-green-50'):ui.label(n)
                    for v in vals:
                        with ui.element('td').classes('border px-2 py-2 text-center'):ui.label(str(v))
        ui.label(res_str('shodhaya_pinda_str','Shodhaya Pinda')).classes('font-bold text-green-700 mt-4 print-attach-next')
        with ui.element('table').classes('border-collapse text-sm min-w-[800px]'):
            with ui.element('tr'):
                with ui.element('th').classes('border px-2 py-2 bg-green-50'):ui.label('')
                for p in utils.PLANET_NAMES[:7]:
                    with ui.element('th').classes('border px-2 py-2 bg-green-50'):ui.label(p)
            for key,vals in [('graha_pinda_str',raasi_pindas),('raasi_pinda_str',graha_pindas),('shodhaya_pinda_str',shodya_pindas)]:
                with ui.element('tr'):
                    with ui.element('td').classes('border px-2 py-2 font-bold bg-green-50'):ui.label(res_str(key,key.replace('_str','').replace('_',' ').title()))
                    for v in vals:
                        with ui.element('td').classes('border px-2 py-2 text-center'):ui.label(str(v))
@ui.page('/shodhaya_pinda')
def page():
    navigation_header();ensure_default_state();methods={}
    _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('shodhaya_pinda_str','Shodhaya Pinda')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w=render_control_bar(show_dob_tob=True,on_options_saved=lambda:compute(),on_calculate=lambda:compute())
        busy=DelayedBusyIndicator(buttons=w.get('calculate_button'),stop_label=res_str('stop_str','Stop'))
        with w['row2']:
            varga=ui.select({i:vlabel(i) for i in range(len(FACTORS))},value=0,label='Varga').props('outlined dense').classes('w-56')
            opt=ui.button(_chart_options_nls,on_click=lambda:options()).props('outlined dense'); oi=ui.label('')
        # 'single-chart-print-block': hides this page's own on-screen content during the global
        # combined "Save as PDF" print (body.printing-all - see components.py's _PRINT_CSS).
        # Without this, this page's own live content stays visible (and duplicates
        # print_registry.py's own headless-built copy) - the same bug confirmed and fixed for
        # amsa_ruler_tab.py's identical title+table pattern.
        out=ui.column().classes('w-full overflow-x-auto single-chart-print-block')
    def idx():return varga.value if isinstance(varga.value,int) else 0
    def md(i):
        if i==0:return 1,1,None,None
        try:n,m,b,e=utils.get_varga_option_dict()[FACTORS[i]];return n or 1,m or 1,b,e
        except:return 1,1,None,None
    def refresh():
        i=idx();n,m,_,_=md(i);m=methods.get(i,m);oi.set_text('' if i==0 else f'Method {m}');opt.enable() if n>1 else opt.disable()
    def options():
        i=idx();n,m,_,_=md(i)
        if n<=1:return
        f=FACTORS[i]
        with ui.dialog() as d,ui.card():
            r=ui.radio({x:res_str(f'd{f}_option{x+1}_str',f'Method {x+1}') for x in range(n)},value=methods.get(i,m)-1)
            async def save():methods[i]=int(r.value)+1;d.close();refresh();await compute()
            ui.button('Accept',on_click=save)
        d.open()
    def render(eka,sav,raasi_pindas,graha_pindas,shodya_pindas):
        out.clear()
        _render_shodhaya_pinda(out, eka,sav,raasi_pindas,graha_pindas,shodya_pindas)
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.',type='warning');return
        try:
            y,m,d=map(int,w['dob_input'].value.strip().split(','));tp=[int(x) for x in w['tob_input'].value.strip().split(':')];t=tuple((tp+[0])[:3]);pv=w['place_select'].value.strip() if w['place_select'].value else 'Chennai';lat=float(w['lat_input'].value);lon=float(w['lon_input'].value);tz=float(w['tz_input'].value);i=idx();f=FACTORS[i];_,dm,b,e=md(i);method=methods.get(i,dm)
        except Exception as ex:safe_notify(f'Error computing Shodhaya Pinda: {ex}',type='negative');return
        try:
            result=await busy.run(_shodhaya_pinda_locked,y,m,d,t,pv,lat,lon,tz,i,method,f,b,e,wait_text=res_str('computing_str','Computing... please wait.'))
        except Exception as ex:safe_notify(f'Error computing Shodhaya Pinda: {ex}',type='negative');return
        if result is DelayedBusyIndicator.STOPPED:return
        eka,sav,raasi_pindas,graha_pindas,shodya_pindas=result
        render(eka,sav,raasi_pindas,graha_pindas,shodya_pindas)
    varga.on_value_change(lambda e:refresh());refresh();ui.timer(0.1,compute,once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Uses D1 (Rasi) - the default varga this page
    itself shows on first load. Reuses _shodhaya_pinda_locked() and _render_shodhaya_pinda(), the
    SAME functions this page's own compute()/render() call.
    """
    try:
        eka, sav, raasi_pindas, graha_pindas, shodya_pindas = await run_io_bound_ctx(
            _shodhaya_pinda_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val, lon_val, tz_val, 0, 1, 1, None, None)
    except Exception as ex:
        with container:
            ui.html(f"<i>Error computing Shodhaya Pinda: {ex}</i>")
        return
    with container:
        ui.label(f"{res_str('shodhaya_pinda_str', 'Shodhaya Pinda')} - {vlabel(0)}").classes('text-base font-bold text-green-700 print-attach-next')
    _render_shodhaya_pinda(container, eka, sav, raasi_pindas, graha_pindas, shodya_pindas)
print_registry.register('shodhaya_pinda', res_str('shodhaya_pinda_str', 'Shodhaya Pinda'), 'Calculations', _build_print_section)

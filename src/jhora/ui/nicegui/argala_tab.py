"""Argala page (/argala).
Shows, for the chosen divisional chart, the Argala and the Virodhargala of each rasi as two
tables (the planets causing each argala / virodhargala, by house). "Chart Options" selects the
calculation method of the varga.
"Print / Save as PDF" prints the current selection only (single page) - no "all vargas" mode, same
scope decision as Bhava.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()), using the D1 (Rasi) default - since the registry calls this function
HEADLESSLY (no live varga selector exists for a page the visitor is not currently on).
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope import info as horo_info
from jhora.horoscope.chart import house
from components import ( navigation_header, render_control_bar, ensure_default_state, calc_lock,
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        print_button, render_footer, run_io_bound_ctx, )
import print_registry
drik=utils.hora_engine_proxy; FACTORS=const.division_chart_factors; NAMES=const._chart_names
def vlabel(i): return res_str(NAMES[i],NAMES[i].replace('_str','').replace('_',' ').title())
def _convert(chart):
    out=list(chart); local=utils.PLANET_NAMES+[res_str('ascendant_str','Ascendant')]; eng=['Sun   ','Moon   ','Mars   ','Mercury   ','Jupiter   ','Venus   ','Saturn   ','Raagu   ','Kethu   ','Uranus','Neptune','Pluto','Lagnam']; vals=[str(i) for i in range(12)]+[const._ascendant_symbol]
    for s,d in zip(local,eng):out=[x.replace(s,d) for x in out]
    for s,d in zip(eng,vals):out=[x.replace(s,d).replace(const._stationary_symbol,'').replace(const._retrogade_symbol,'') for x in out]
    return out
def _argala_locked(y,m,d,t,pv,lat,lon,tz,i,method,f,b,e):
    """Computes the Argala/Virodhargala under calc_lock(); the slow part of compute(), run in a worker
    thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        h=horo_info.Horoscope(place_with_country_code=pv,latitude=lat,longitude=lon,timezone_offset=tz,date_in=drik.Date(y,m,d),birth_time=f'{t[0]:02d}:{t[1]:02d}:{t[2]:02d}',calculation_type='drik',language=const._DEFAULT_LANGUAGE)
        _,chart,_=h.get_horoscope_information_for_chart(i,method,divisional_chart_factor=f,base_rasi=b,count_from_end_of_sign=e,varnada_method=1,dhasa_progression_correction=0.0); a,v=house.get_argala(_convert(chart))
        return a,v
def _render_argala_table(box, title, data, headers):
    """Draws one Argala/Virodhargala table into `box` - extracted to module level so BOTH the page's
    own on-screen render() and print_registry.py's headless _build_print_section() below use the
    SAME markup.
    """
    with box:
        ui.label(title).classes('font-bold text-green-700 print-attach-next')
        with ui.element('table').classes('border-collapse text-sm w-full'):
            with ui.element('tr'):
                with ui.element('th').classes('border px-2 py-2 bg-green-50'):ui.label(res_str('raasi_str','Raasi'))
                for h in headers:
                    with ui.element('th').classes('border px-2 py-2 bg-green-50'):ui.label(str(h))
            for r in range(12):
                with ui.element('tr'):
                    vals=[utils.RAASI_LIST[r]]
                    for c in range(4): vals.append('\n'.join(utils.PLANET_NAMES[int(p)] for p in data[r][c].split('/') if p.strip() and p.strip()!=const._ascendant_symbol))
                    for x in vals:
                        with ui.element('td').classes('border px-2 py-2 whitespace-pre-line align-top'):ui.label(x).classes('whitespace-pre-line')
@ui.page('/argala')
def argala_page():
    navigation_header(); ensure_default_state(); methods={}
    _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('argala_str','Argala')+' / '+res_str('virodhargala_str','Virodhargala')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py). This page remains registered there.
        w=render_control_bar(show_dob_tob=True,on_options_saved=lambda:compute(),on_calculate=lambda:compute())
        busy=DelayedBusyIndicator(buttons=w.get('calculate_button'),stop_label=res_str('stop_str','Stop'))
        with w['row2']:
            varga=ui.select({i:vlabel(i) for i in range(len(FACTORS))},value=0,label='Varga').props('outlined dense').classes('w-56')
            opt=ui.button(_chart_options_nls,on_click=lambda:open_options()).props('outlined dense'); info=ui.label('').classes('text-sm font-semibold')
        # 'print-side-by-side': opts these 2 boxes' tables back OUT of the global 'table { width:
        # 100% }' print rule, so they can sit side by side in print the same way they do on screen -
        # see components.py's module docstring, "full-bleed table width" note, for the full history
        # (confirmed from an actual printed PDF that this exact pattern was turning 1 compact page
        # into 2).
        # 'single-chart-print-block': hides this page's own on-screen content during the global
        # combined "Save as PDF" print (body.printing-all - see components.py's _PRINT_CSS).
        # Without this, this page's own live content stays visible (and duplicates
        # print_registry.py's own headless-built copy) - the same bug confirmed and fixed for
        # amsa_ruler_tab.py's identical pattern.
        with ui.row().classes('w-full gap-5 items-start flex-wrap print-side-by-side single-chart-print-block'):
            a_box=ui.column().classes('min-w-[520px]'); v_box=ui.column().classes('min-w-[520px]')
    def idx(): return varga.value if isinstance(varga.value,int) else 0
    def md(i):
        if i==0:return 1,1,None,None
        try:n,m,b,e=utils.get_varga_option_dict()[FACTORS[i]];return n or 1,m or 1,b,e
        except:return 1,1,None,None
    def refresh():
        i=idx();n,m,_,_=md(i);m=methods.get(i,m);f=FACTORS[i];info.set_text('' if i==0 else res_str(f'd{f}_option{m}_str',f'Method {m}')); opt.enable() if n>1 else opt.disable()
    def open_options():
        i=idx();n,m,_,_=md(i)
        if n<=1:return
        f=FACTORS[i]
        with ui.dialog() as dlg,ui.card():
            r=ui.radio({x:res_str(f'd{f}_option{x+1}_str',f'Method {x+1}') for x in range(n)},value=methods.get(i,m)-1)
            async def save():methods[i]=int(r.value)+1;dlg.close();refresh();await compute()
            ui.button('Accept',on_click=save)
        dlg.open()
    def render(box,title,data,headers):
        box.clear()
        _render_argala_table(box, title, data, headers)
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.',type='warning');return
        try:
            y,m,d=map(int,w['dob_input'].value.strip().split(','));tp=[int(x) for x in w['tob_input'].value.strip().split(':')];t=tuple((tp+[0])[:3]);pv=w['place_select'].value.strip() if w['place_select'].value else 'Chennai';lat=float(w['lat_input'].value);lon=float(w['lon_input'].value);tz=float(w['tz_input'].value);i=idx();f=FACTORS[i];_,dm,b,e=md(i);method=methods.get(i,dm)
        except Exception as ex:safe_notify(f'Error computing Argala: {ex}',type='negative');return
        try:
            result=await busy.run(_argala_locked,y,m,d,t,pv,lat,lon,tz,i,method,f,b,e,
                                  wait_text=res_str('computing_str','Computing... please wait.'))
        except Exception as ex:safe_notify(f'Error computing Argala: {ex}',type='negative');return
        if result is DelayedBusyIndicator.STOPPED:return
        a,v=result
        render(a_box,res_str('argala_str','Argala'),a,const.argala_houses_str);render(v_box,res_str('virodhargala_str','Virodhargala'),v,const.virodhargala_houses_str)
    varga.on_value_change(lambda e:refresh());refresh();ui.timer(0.1,compute,once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Uses D1 (Rasi) - the default varga this page
    itself shows on first load. Reuses _argala_locked() and _render_argala_table(), the SAME
    functions this page's own compute()/render() call.
    """
    try:
        a, v = await run_io_bound_ctx(_argala_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val, lon_val, tz_val, 0, 1, 1, None, None)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing Argala: {e}</i>")
        return
    with container:
        ui.label(res_str('argala_str', 'Argala') + ' / ' + res_str('virodhargala_str', 'Virodhargala') + ' - ' + vlabel(0)) \
            .classes('text-base font-bold text-green-700 print-attach-next')
        with ui.row().classes('w-full gap-5 items-start flex-wrap print-side-by-side'):
            a_box = ui.column().classes('min-w-[520px]')
            v_box = ui.column().classes('min-w-[520px]')
        _render_argala_table(a_box, res_str('argala_str', 'Argala'), a, const.argala_houses_str)
        _render_argala_table(v_box, res_str('virodhargala_str', 'Virodhargala'), v, const.virodhargala_houses_str)
print_registry.register('argala', res_str('argala_str', 'Argala') + ' / ' + res_str('virodhargala_str', 'Virodhargala'), 'Calculations', _build_print_section)

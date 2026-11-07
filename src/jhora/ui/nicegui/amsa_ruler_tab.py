#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Amsa Ruler page (/amsa_ruler).
Lists the amsa ruler of every chart object (planets, ascendant, special lagnas, upagrahas,
sphutas, arudha lagnas, varnada lagnas and sahams) for the chosen amsa varga, in five
side-by-side tables. "Chart Options" selects the calculation method of the varga.
"Print / Save as PDF" prints the current selection only (single page) - no "all vargas" mode, same
scope decision as Bhava.
Also registered with print_registry.py's central "Save as PDF" dialog (see
_build_print_section()), using this page's own default_index (the same amsa varga shown on first
load) - since the registry calls this function HEADLESSLY (no live varga selector exists for a
page the visitor is not currently on).
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.horoscope.chart import charts
from components import (navigation_header, render_control_bar, ensure_default_state,
                        calc_lock, res_str, safe_notify, ignore_disconnected_client,
                        DelayedBusyIndicator, print_button, render_footer, run_io_bound_ctx,
                        )
import print_registry
drik = utils.hora_engine_proxy
VARGAS = const.amsa_supported_vargas
_DEFAULT_INDEX = min(13, len(VARGAS) - 1)
def varga_label(factor):
    try:
        i = const.division_chart_factors.index(factor)
        key = const._chart_names[i]
        return res_str(key, f'D{factor}')
    except Exception:
        return f'D{factor}'
def _label_for(p):
    if p in utils._main_planets or p==const._ascendant_symbol:
        return res_str('ascendant_str','Ascendant') if p==const._ascendant_symbol else utils.PLANET_NAMES[p]
    if p in utils._special_lagnas:return res_str(utils._special_lagnas[p]+'_str',utils._special_lagnas[p])
    if p in utils._upagrahas:return res_str(utils._upagrahas[p]+'_str',utils._upagrahas[p])
    if p in utils._sphutas:return res_str(utils._sphutas[p]+'_sphuta_str',utils._sphutas[p])+' '+res_str('sphuta_str','Sphuta')
    if p in utils._arudha_lagnas:return res_str(utils._arudha_lagnas[p]+'_str',utils._arudha_lagnas[p])+f' ({p})'
    if p in utils._varnada_lagnas:return res_str('varnada_lagna_str','Varnada Lagna')+f' ({p})'
    if p in utils._sahams:return res_str(utils._sahams[p]+'_saham_str',utils._sahams[p])+' '+res_str('saham_str','Saham')
    return str(p)
def _amsa_ruler_locked(y,m,d,t,pv,lat,lon,tz,f,method,b,e):
    """Computes the amsa ruler rows under calc_lock(); the slow part of compute(), run in a worker
    thread via components.DelayedBusyIndicator.run()."""
    with calc_lock():
        jd=utils.julian_day_number(drik.Date(y,m,d),t);place=drik.Place(pv,lat,lon,tz,0.0)
        pp=charts.divisional_chart(jd,place,divisional_chart_factor=1,exclude_non_planets=False,chart_method=method,base_rasi=b,count_from_end_of_sign=e)
        rulers=charts.amsa_rulers(pp,dcf=f); resources=charts.get_amsa_resources(const._DEFAULT_LANGUAGE); names=resources[str(f)]
        return [(_label_for(p),names[ai-1]) for p,ai in rulers.items()]
def _render_amsa_ruler_tables(tables_row, rows):
    """Draws the 5 side-by-side amsa-ruler tables into `tables_row` - extracted to module level so
    BOTH the page's own on-screen render() and print_registry.py's headless _build_print_section()
    below use the SAME markup.
    """
    with tables_row:
        total=len(rows); count=5; base=total//count; extra=total%count; start=0
        for ti in range(count):
            n=base+(1 if ti<extra else 0); part=rows[start:start+n]; start+=n
            with ui.element('table').classes('text-xs border-collapse min-w-48'):
                for a,b in part:
                    with ui.element('tr'):
                        with ui.element('td').classes('border border-gray-300 px-2 py-1 font-semibold'):
                            ui.label(str(a)).classes('text-xs')
                        with ui.element('td').classes('border border-gray-300 px-2 py-1'):
                            ui.label(str(b)).classes('text-xs')
@ui.page('/amsa_ruler')
def amsa_ruler_page():
    navigation_header(); ensure_default_state(); method_state={}
    default_index = _DEFAULT_INDEX
    _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(res_str('amsa_ruler_str','Amsa Ruler')).classes('text-xl font-bold text-green-700')
            # print_button() REMOVED - printing is now exclusively via the ONE global "Save as PDF"
            # button (print_registry.py), per the user's own explicit final requirement. This page
            # is still registered with that registry (see _build_print_section() below) - only its
            # OWN, separate per-page button is gone.
        w=render_control_bar(show_dob_tob=True,on_options_saved=lambda:compute(),on_calculate=lambda:compute())
        busy=DelayedBusyIndicator(buttons=w.get('calculate_button'),stop_label=res_str('stop_str','Stop'))
        with w['row2']:
            sel=ui.select({i:varga_label(f) for i,f in enumerate(VARGAS)}, value=default_index, label='Amsa Varga').props('outlined dense').classes('w-56')
            opt=ui.button(_chart_options_nls,on_click=lambda:open_options()).props('outlined dense')
            option_info=ui.label('').classes('text-sm font-semibold text-gray-700')
        # 'print-attach-next': keeps this title attached to the start of 'tables' below (otherwise a
        # page break can land between them with nothing to stop it - see components.py's module
        # docstring, "full-bleed table width" note, for the full history).
        # 'single-chart-print-block' (on the WRAPPER, not just 'tables'): hides this page's own
        # on-screen content - BOTH the title label AND the tables row - during the global combined
        # "Save as PDF" print (body.printing-all - see components.py's _PRINT_CSS). An EARLIER
        # version of this fix added the class only to 'tables' and missed 'title' (a separate
        # sibling element) - since 'title' was still unhidden, it kept rendering wherever it
        # naturally sits in the DOM (after the hidden combined-report container, i.e. at the very
        # END of the printed output) even after the tables row itself stopped duplicating -
        # confirmed from an actual printed PDF showing an orphaned "Amsa Ruler - Sashtiamsa (D60)"
        # heading alone on the last page, with its own table already correctly gone. Wrapping BOTH
        # elements in one container with this class (rather than tagging each separately) avoids
        # this exact class of "missed one sibling" bug recurring again.
        with ui.column().classes('w-full gap-1 single-chart-print-block'):
            title=ui.label('').classes('text-lg font-bold text-green-700 print-attach-next')
            # 'print-side-by-side': opts these 5 tables back OUT of the global 'table { width: 100% }'
            # print rule, so they can sit side by side in print the same way they do on screen -
            # without this, each table claims the full row width and they stack vertically instead,
            # turning 1 compact page into several mostly-empty ones (confirmed from an actual
            # printed PDF).
            tables=ui.row().classes('w-full items-start gap-2 flex-nowrap overflow-x-auto print-side-by-side')
    def idx(): return sel.value if isinstance(sel.value,int) else default_index
    def method_data(f):
        try:
            n,m,b,e=utils.get_varga_option_dict()[f]; return n or 1,m or 1,b,e
        except Exception:return 1,1,None,None
    def refresh():
        f=VARGAS[idx()]; n,m,_,_=method_data(f); chosen=method_state.get(f,m)
        option_info.set_text(res_str(f'd{f}_option{chosen}_str',f'Method {chosen}'))
        opt.enable() if n>1 else opt.disable()
    def open_options():
        f=VARGAS[idx()]; n,m,_,_=method_data(f)
        if n<=1:return
        current=method_state.get(f,m)
        with ui.dialog() as dlg,ui.card().classes('gap-3'):
            ui.label(f'{varga_label(f)} Options').classes('font-bold text-green-700')
            r=ui.radio({x:res_str(f'd{f}_option{x+1}_str',f'Method {x+1}') for x in range(n)},value=current-1)
            async def save(): method_state[f]=int(r.value)+1;dlg.close();refresh();await compute()
            with ui.row():ui.button('Cancel',on_click=dlg.close).props('outlined');ui.button('Accept',on_click=save)
        dlg.open()
    def render(rows):
        tables.clear()
        _render_amsa_ruler_tables(tables, rows)
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.',type='warning');return
        try:
            dv=w['dob_input'].value.strip();tv=w['tob_input'].value.strip();pv=w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat=float(w['lat_input'].value);lon=float(w['lon_input'].value);tz=float(w['tz_input'].value);y,m,d=map(int,dv.split(','));tp=[int(x) for x in tv.split(':')];t=tuple((tp+[0])[:3])
            f=VARGAS[idx()];_,dm,b,e=method_data(f);method=method_state.get(f,dm)
        except Exception as ex:safe_notify(f'Error computing Amsa rulers: {ex}',type='negative');return
        try:
            rows=await busy.run(_amsa_ruler_locked,y,m,d,t,pv,lat,lon,tz,f,method,b,e,
                                wait_text=res_str('computing_str','Computing... please wait.'))
        except Exception as ex:safe_notify(f'Error computing Amsa rulers: {ex}',type='negative');return
        if rows is DelayedBusyIndicator.STOPPED:return
        title.set_text(f"{res_str('amsa_ruler_str','Amsa Ruler')} - {varga_label(f)}") ; render(rows)
    async def _on_sel_changed(e):refresh();await compute()
    sel.on_value_change(_on_sel_changed);refresh();ui.timer(0.1,compute,once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_value):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Uses this page's own default_index - the default
    amsa varga it shows on first load. Reuses _amsa_ruler_locked() and _render_amsa_ruler_tables(),
    the SAME functions this page's own compute()/render() call.
    """
    f = VARGAS[_DEFAULT_INDEX]
    try:
        n, default_method, b, e = utils.get_varga_option_dict().get(f, (1, 1, None, None))
    except Exception:
        default_method, b, e = 1, None, None
    try:
        rows = await run_io_bound_ctx(_amsa_ruler_locked, dob[0], dob[1], dob[2], tob, place_val, lat_val, lon_val,
                                  tz_val, f, default_method or 1, b, e)
    except Exception as ex:
        with container:
            ui.html(f"<i>Error computing Amsa rulers: {ex}</i>")
        return
    with container:
        ui.label(f"{res_str('amsa_ruler_str', 'Amsa Ruler')} - {varga_label(f)}").classes('text-base font-bold text-green-700 print-attach-next')
        tables = ui.row().classes('w-full items-start gap-2 flex-nowrap overflow-x-auto print-side-by-side')
        _render_amsa_ruler_tables(tables, rows)
print_registry.register('amsa_ruler', res_str('amsa_ruler_str', 'Amsa Ruler'), 'Calculations', _build_print_section)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Chakra page (/chakra).

Draws one of nine chakras (Kota, Kaala, Sarvatobadra, Surya Kalanala, Chandra Kalanala, Shoola,
Tripataki, Saptha Shalaka, Pancha Shalaka) for the chosen divisional chart, with the planets
placed in the nakshatra or rasi cells of the chakra. The Kota chakra also shows the Kota Swami
and Kota Paala. "Chart Options" selects the calculation method of the varga.
"""
import html
from nicegui import ui
from jhora import const, utils
from jhora.horoscope.chart import charts
from components import (navigation_header, render_control_bar, ensure_default_state, calc_lock, 
                        res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator,
                        render_footer,)
drik = utils.hora_engine_proxy
CHAKRAS = ['kota','kaala','sarvatobadra','surya_kalanala','chandra_kalanala','shoola','tripataki','saptha_shalaka','pancha_shalaka']
FACTORS = const.division_chart_factors
NAMES = const._chart_names
def _varga_label(i): return res_str(NAMES[i], NAMES[i].replace('_str','').replace('_',' ').title())
def _tob(s):
    p=[int(x) for x in str(s).split(':')]; return tuple((p+[0])[:3])
def _esc(s): return html.escape(str(s))
def _chakra_locked(y,m,d,t,pv,lat,lon,tz,f,method,b,e):
    """Computes the planet positions, retrograde set and ascendant under calc_lock(); the slow part of
    compute() (the divisional chart and the birth nakshatra), run in a worker thread via
    components.DelayedBusyIndicator.run(). The actual drawing (pure SVG/HTML, no further astronomical
    calls) stays on the main thread in compute(), using the values this returns.
    """
    with calc_lock():
        jd=utils.julian_day_number(drik.Date(y,m,d),t);place=drik.Place(pv,lat,lon,tz,0.0)
        retro=drik.planets_in_retrograde(jd,place);asc=drik.ascendant(jd,place)[0]
        pp=charts.divisional_chart(jd,place,divisional_chart_factor=f,chart_method=method,base_rasi=b,count_from_end_of_sign=e,exclude_non_planets=True)
        nk=drik.nakshatra(jd,place)
        return jd,place,retro,asc,pp,nk

@ui.page('/chakra')
def chakra_page():
    navigation_header(); ensure_default_state(); choices={}
    _chart_options_nls = res_str('horoscope_str','Chart')+' '+res_str('options_str','Options')
    with ui.column().classes('w-full p-2 gap-1'):
        ui.label(res_str('chakra_str','Chakra')).classes('text-xl font-bold text-green-700')
        w=render_control_bar(show_dob_tob=True,on_options_saved=lambda:compute(),on_calculate=lambda:compute())
        busy=DelayedBusyIndicator(buttons=w.get('calculate_button'),stop_label=res_str('stop_str','Stop'))
        with w['row2']:
            varga=ui.select({i:_varga_label(i) for i in range(len(FACTORS))},value=0,label='Varga (Divisional Chart)').props('outlined dense').classes('w-56')
            opt_btn=ui.button(_chart_options_nls,on_click=lambda:open_options()).props('outlined dense')
            with opt_btn: opt_tip=ui.tooltip('')
        kind=ui.radio({i:res_str(x+'_str',x.replace('_',' ').title()) for i,x in enumerate(CHAKRAS)},value=0).props('inline')
        title=ui.label('').classes('text-lg font-bold text-green-700')
        info=ui.label('').classes('font-bold text-brown-700')
        out=ui.column().classes('w-full items-center overflow-auto')
    def vidx(): return varga.value if isinstance(varga.value,int) and not isinstance(varga.value,bool) else 0
    def method_data(i):
        if i==0:return 1,1,None,None
        try:
            n,m,b,e=utils.get_varga_option_dict()[FACTORS[i]]; return n or 1,m or 1,b,e
        except Exception:return 1,1,None,None
    def refresh(i=None):
        i=vidx() if i is None else i; n,_,_,_=method_data(i)
        if n>1: opt_btn.enable(); opt_tip.set_text(f'Choose one of {n} calculation methods.')
        else: opt_btn.disable(); opt_tip.set_text('This varga has only one calculation method.')
    def open_options():
        i=vidx(); n,d,_,_=method_data(i)
        if n<=1:return
        f=FACTORS[i]; cur=choices.get(i,d)
        with ui.dialog() as dlg,ui.card().classes('gap-3'):
            ui.label(f'{_varga_label(i)} Options').classes('font-bold text-green-700')
            r=ui.radio({x:res_str(f'd{f}_option{x+1}_str',f'Method {x+1}') for x in range(n)},value=cur-1)
            async def save(): choices[i]=int(r.value)+1; dlg.close(); await compute()
            with ui.row(): ui.button('Cancel',on_click=dlg.close).props('outlined'); ui.button('Accept',on_click=save)
        dlg.open()
    def pname(p,retro):
        s=res_str('ascendant_short_str','Asc') if p==const._ascendant_symbol else utils.PLANET_SHORT_NAMES[p]
        return s+(const._retrogade_symbol if p in retro else '')
    def pstar(pp,retro,abhijit=True):
        d={}
        for p,(h,l) in pp:
            n=utils.nakshatra_pada(h*30+l)[0]
            if abhijit and n>const._ABHIJITH_STAR_INDEX:n+=1
            d.setdefault(n,[]).append(pname(p,retro))
        return d
    def base_star(pp,i):
        q=pp[1] if i==0 else pp[0]; return utils.nakshatra_pada(q[1][0]*30+q[1][1])[0]
    def star_names(): return [utils.NAKSHATRA_SHORT_LIST[i] for i in const.abhijit_order_of_stars]
    def svg_text_lines(x, y, text, *, font_size=11, fill='#174ea6', anchor='start', line_height=14, weight='600'):
        """Returns SVG <text> markup in which each line of `text` (split on newline or <br>) is a tspan.

        Args:
            x, y: position of the first line.
            text: text to draw; newline or <br> starts a new line.
            font_size, fill, weight: font size, color and font weight.
            anchor: SVG text-anchor ('start', 'middle' or 'end').
            line_height: vertical distance between lines.
        """
        normalized = str(text).replace('<br/>', '\n').replace('<br />', '\n').replace('<br>', '\n')
        lines = normalized.split('\n')
        parts = [f'<text x="{x}" y="{y}" font-size="{font_size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">']
        for line_no, line in enumerate(lines):
            dy = 0 if line_no == 0 else line_height
            parts.append(f'<tspan x="{x}" dy="{dy}">{_esc(line)}</tspan>')
        parts.append('</text>')
        return ''.join(parts)
    def svg_finish(parts,wid=660,hei=660):
        parts.append('</svg>'); out.clear()
        with out: ui.html(''.join(parts))
    def line_chart(lines,pos,pp,retro,base=1,flip=None,circle=False,scale=42,canvas=700,font_size=11,line_height=14):
        pm=pstar(pp,retro); stars=star_names(); pad=42
        X=lambda x:pad+x*scale; Y=lambda y:pad+(((flip+1-y) if flip else y)*scale)
        s=[f'<svg viewBox="0 0 {canvas} {canvas}" style="width:{canvas}px;height:{canvas}px;max-width:none;background:white">']
        if circle:s.append(f'<circle cx="{X(5)}" cy="{Y(5)}" r="68" fill="none" stroke="#4b2e1f" stroke-width="2"/>')
        for a,b in lines:s.append(f'<line x1="{X(a[0])}" y1="{Y(a[1])}" x2="{X(b[0])}" y2="{Y(b[1])}" stroke="#4b2e1f" stroke-width="2"/>')
        for k,(x,y) in pos.items():
            actual=((base-1)+(k-1))%28+1; txt=stars[actual-1]
            if actual in pm: txt += '\n' + '\n'.join(pm[actual])
            s.append(svg_text_lines(X(x)+3, Y(y)-3, txt, font_size=font_size, line_height=line_height))
        svg_finish(s)
    def grid(values,pp,retro,sarva=False):
        pm=pstar(pp,retro,False); out.clear()
        with out:
            with ui.grid(columns=len(values[0])).classes('gap-0 border border-gray-500'):
                for i,row in enumerate(values):
                    for j,v in enumerate(row):
                        border=i in (0,len(values)-1) or j in (0,len(row)-1)
                        if isinstance(v,int):
                            text=(utils.NAKSHATRA_SHORT_LIST[v-1] if not sarva or border else utils.RAASI_SHORT_LIST[v-1])
                            if (not sarva or border) and v in pm:text+='\n'+' '.join(pm[v])
                        else:text=res_str(v,v) if str(v).endswith('_str') else str(v).replace('<br>',' / ')
                        ui.label(text).classes('w-20 h-16 border border-gray-300 p-1 text-xs whitespace-pre-line')
    def kota(pp,retro,bs,bp):
        from jhora.horoscope.chart import house
        stars=star_names(); rows=[[stars[((bs-1)+(e-1))%28] for e in r] for r in const.kota_chakra_star_placement_from_birth_star]
        for p,(h,l) in pp:
            sn=utils.NAKSHATRA_SHORT_LIST[utils.nakshatra_pada(h*30+l)[0]-1]
            for row in rows:
                for j,v in enumerate(row):
                    if v.split('\n')[0]==sn:row[j]+='\n'+pname(p,retro)
        moon_house=pp[2][1][0]; kl=utils.PLANET_NAMES[house.house_owner_from_planet_positions(pp,moon_house)]
        kp=utils.PLANET_NAMES[const.kota_paala_lord_for_star_paadha[bs-1][bp-1]]
        info.set_text(f"{res_str('kota_swami_str','Kota Swami')}: {kl}   {res_str('kota_paala_str','Kota Paala')}: {kp}")
        out.clear(); colors=['#fecaca','#bbf7d0','#bfdbfe','#fef08a']
        with out:
            with ui.element('div').style('position:relative;width:620px;height:620px;'):
                for i,row in enumerate(rows):
                    inset=i*74; size=620-2*inset
                    with ui.element('div').style(f'position:absolute;left:{inset}px;top:{inset}px;width:{size}px;height:{size}px;border:2px solid #593c25;background:{colors[i]};'):
                        places=([(8,5),(43,5),(78,5),(82,45),(78,82),(43,82),(8,82),(5,45)] if i<3 else [(43,8),(80,43),(43,78),(5,43)])
                        for j,t in enumerate(row):
                            x,y=places[j]; ui.label(t).style(f'position:absolute;left:{x}%;top:{y}%;font-size:11px;font-weight:600;white-space:pre-line')
    def tripataki(pp,retro,asc):
        coords=[(3,1),(2,1),(1,2),(1,3),(1,4),(2,5),(3,5),(4,5),(5,4),(5,3),(5,2),(4,1)]
        paths={(2,5):[(1,4),(2,1),(5,2)],(3,5):[(1,3),(3,1),(5,3)],(4,5):[(1,2),(4,1),(5,4)],(2,1):[(1,2),(5,4)],(3,1):[(1,3),(5,3)],(4,1):[(1,4),(5,2)],(1,2):[(5,2)],(1,3):[(5,3)],(1,4):[(5,4)]}
        hm={}
        for p,(h,l) in pp:hm.setdefault(h,[]).append(pname(p,retro))
        sc=105;s=['<svg viewBox="0 0 640 640" style="width:660px;height:660px;background:white">']
        for a,ends in paths.items():
            for b in ends:s.append(f'<line x1="{a[0]*sc}" y1="{a[1]*sc}" x2="{b[0]*sc}" y2="{b[1]*sc}" stroke="#4b2e1f" stroke-width="2"/>')
        for px,py in [(3,1),(2,1),(4,1)]:
            x=px*sc; y=py*sc
            s.append(f'<polygon points="{x},{y} {x-22},{y-14} {x-22},{y+14}" fill="white" stroke="#111" stroke-width="2"/>')
        for i,(x,y) in enumerate(coords):
            h=(asc+i)%12; text=utils.RAASI_SHORT_LIST[h] + (('\n' + '\n'.join(hm.get(h,[]))) if hm.get(h) else ''); s.append(svg_text_lines(x*sc-30, y*sc-8, text, font_size=12, weight='400'))
        svg_finish(s)
    @ignore_disconnected_client
    async def compute():
        if busy.is_busy:
            safe_notify('Already computing. Please wait.',type='warning');return
        try:
            dv=w['dob_input'].value.strip(); tv=w['tob_input'].value.strip(); pv=w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
            lat=float(w['lat_input'].value);lon=float(w['lon_input'].value);tz=float(w['tz_input'].value);y,m,d=map(int,dv.split(','));t=_tob(tv)
            i=vidx(); n,default,b,e=method_data(i); method=choices.get(i,default); c=int(kind.value or 0)
        except Exception as ex:
            safe_notify(f'Error computing Chakra: {ex}',type='negative');return
        try:
            result=await busy.run(_chakra_locked,y,m,d,t,pv,lat,lon,tz,FACTORS[i],method,b,e,
                                  wait_text=res_str('computing_str','Computing... please wait.'))
        except Exception as ex:
            safe_notify(f'Error computing Chakra: {ex}',type='negative');return
        if result is DelayedBusyIndicator.STOPPED:
            return
        jd,place,retro,asc,pp,nk=result
        try:
            title.set_text(f"{res_str('chakra_str','Chakra')} - {res_str(CHAKRAS[c]+'_str',CHAKRAS[c].replace('_',' ').title())} - {_varga_label(i)}") ; info.set_text('')
            if c==0:
                kota(pp,retro,nk[0],nk[1])
            elif c==1:
                # Kaala chakra: a centre circle with 4 inner nakshatra cells and 8 radial arms of 3 nakshatras each.
                bs=base_star(pp,i); inner=[4,25,18,11]; outer=[[5,6,7],[3,2,1],[26,27,28],[24,23,22],[19,20,21],[17,16,15],[12,13,14],[10,9,8]];pm=pstar(pp,retro);stars=star_names()
                s=['<svg viewBox="0 0 700 700" style="width:660px;height:660px;background:white">'];cx=350;cy=350;r=75
                import math
                s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#4b2e1f" stroke-width="2"/>')
                for q,k in enumerate(inner):
                    a=math.radians(45+q*90);actual=((bs-1)+(k-1))%28+1;txt=stars[actual-1] + (('\n' + '\n'.join(pm.get(actual,[]))) if pm.get(actual) else ''); s.append(svg_text_lines(cx+40*math.cos(a), cy-40*math.sin(a), txt, font_size=10, fill='#174ea6'))
                for q,row in enumerate(outer):
                    a=math.radians(45+q*45);x2=cx+275*math.cos(a);y2=cy-275*math.sin(a);s.append(f'<line x1="{cx+r*math.cos(a)}" y1="{cy-r*math.sin(a)}" x2="{x2}" y2="{y2}" stroke="#4b2e1f"/>')
                    for z,k in enumerate(row,1):
                        actual=((bs-1)+(k-1))%28+1;txt=stars[actual-1] + (('\n' + '\n'.join(pm.get(actual,[]))) if pm.get(actual) else ''); rr=r+z*58; s.append(svg_text_lines(cx+rr*math.cos(a), cy-rr*math.sin(a), txt, font_size=10, fill='#174ea6'))
                direction_keys=['kaala_chakra_southeast_str','kaala_chakra_east_str','kaala_chakra_northeast_str','kaala_chakra_north_str','kaala_chakra_northwest_str','kaala_chakra_west_str','kaala_chakra_southwest_str','kaala_chakra_south_str']
                for q,key in enumerate(direction_keys):
                    a=math.radians(45+q*45); rr=315; label=res_str(key,key.replace('kaala_chakra_','').replace('_str','').replace('_',' ').title())
                    s.append(svg_text_lines(cx+rr*math.cos(a),cy-rr*math.sin(a),label,font_size=11,fill='green',anchor='middle',line_height=13))
                svg_finish(s)
            elif c==2:
                grid([['ii',23,24,25,26,27,1,2,'a'],[22,'rii','g','s','d','ch','l','u',3],[28,'kh','ai',11,12,1,'lu','a',4],[21,'j',10,'ah','Rikita<br>Fri','o',2,'v',5],[20,'bh',9,'Jaya<br>Thu','Pooma<br>Sat','Nanda<br>Sun<br>Tue',3,'k',6],[19,'y',8,'am','Bhadra<br>Mon<br>Wed','au',4,'h',7],[18,'n','e',7,6,5,'luu','d',8],[17,'ri','t','r','p','t~','m','uu',9],['i',16,15,14,13,12,11,10,'aa']],pp,retro,True)
            elif c==3:
                line_chart([((1,6),(15,6)),((1,8),(15,8)),((1,10),(15,10)),((5,1),(5,15)),((8,1),(8,15)),((11,1),(11,15)),((4,6),(2,3)),((5,6),(2,2)),((5,5),(3,2)),((5,4),(4,2)),((12,6),(14,3)),((11,6),(14,2)),((11,5),(13,2)),((11,4),(12,2)),((5,12),(3,14)),((3,10),(2,12)),((11,12),(13,14)),((13,10),(14,12)),((5,4),(6,2)),((8,4),(7,2)),((8,4),(9,2)),((11,4),(12,2)),((11,4),(10,2))],{1:(8,15),2:(5,15),3:(3,15),4:(1,14),5:(1,10),6:(1,8),7:(1,6),8:(1,4),9:(1,1),10:(3,1),11:(4,1),12:(5,1),13:(6,1),14:(7,1),15:(8,1),16:(9,1),17:(10,1),18:(11,1),19:(12,1),20:(13,1),21:(15,1),22:(15,4),23:(15,6),24:(15,8),25:(15,10),26:(15,14),27:(13,15),28:(11,15)},pp,retro,base_star(pp,i))
            elif c==4:
                line_chart([((4,8),(4,7)),((4,7),(6,7)),((6,7),(6,8)),((5,8),(5,2)),((4,2),(4,3)),((4,3),(6,3)),((6,3),(6,2)),((2,4),(3,4)),((3,4),(3,6)),((3,6),(2,6)),((2,5),(8,5)),((8,4),(7,4)),((7,4),(7,6)),((7,6),(8,6))],{1:(5,1),2:(4,1),3:(4,3),4:(4,4),5:(4,5),6:(3,4),7:(2,4),8:(2,5),9:(2,6),10:(3,6),11:(4,6),12:(5,6),13:(4,7),14:(4,8),15:(5,8),16:(6,8),17:(6,7),18:(6,6),19:(6,5),20:(7,6),21:(8,6),22:(8,5),23:(8,4),24:(7,4),25:(6,4),26:(5,4),27:(6,3),28:(6,2)},pp,retro,base_star(pp,i),circle=True,scale=62,canvas=720,font_size=11,line_height=15)
            elif c==5:
                line_chart([((5,1),(5,10)),((2,7),(8,7)),((2,7),(2,10)),((8,7),(8,10))],{1:(5,1),2:(4,2),3:(4,3),4:(4,4),5:(4,5),6:(4,6),7:(4,7),8:(3,10),9:(2,11),10:(1,10),11:(1,9),12:(1,8),13:(2,7),14:(4,10),15:(5,11),16:(6,10),17:(6,9),18:(6,8.5),19:(6,8),20:(7,10),21:(8,11),22:(9,10),23:(9,9),24:(9,8),25:(8,7),26:(6,4),27:(6,3),28:(6,2)},pp,retro,base_star(pp,i),flip=11)
            elif c==6:tripataki(pp,retro,asc)
            elif c==7:
                line_chart([*((((x,1),(x,9)) for x in range(2,9))),*((((1,y),(9,y)) for y in range(2,9)))],{1:(7,1),2:(8,1),3:(9,2),4:(9,3),5:(9,4),6:(9,5),7:(9,6),8:(9,7),9:(9,8),10:(8,9),11:(7,9),12:(6,9),13:(5,9),14:(4,9),15:(3,9),16:(2,9),17:(1,8),18:(1,7),19:(1,6),20:(1,5),21:(1,4),22:(1,3),23:(1,2),24:(2,1),25:(3,1),26:(4,1),27:(5,1),28:(6,1)},pp,retro)
            else:
                line_chart([*((((x,1),(x,7)) for x in range(2,7))),*((((1,y),(7,y)) for y in range(2,7))),((1,6.5),(6.5,1)),((1.5,7),(7,1.5)),((1.5,1),(7,6.5)),((1,1.5),(6.5,7))],{1:(1,2),2:(1,1.5),3:(1.5,1),4:(2,1),5:(3,1),6:(4,1),7:(5,1),8:(6,1),9:(6.5,1),10:(7,1.5),11:(7,2),12:(7,3),13:(7,4),14:(7,5),15:(7,6),16:(7,6.5),17:(6.5,7),18:(6,7),19:(5,7),20:(4,7),21:(3,7),22:(2,7),23:(1.5,7),24:(1,6.5),25:(1,6),26:(1,5),27:(1,4),28:(1,3)},pp,retro,scale=70,canvas=700,font_size=11,line_height=15)
        except Exception as ex:
            out.clear()
            with out:ui.label(f'Error: {ex}').classes('text-red-600')
            safe_notify(f'Error computing Chakra: {ex}',type='negative')
    async def _on_varga_changed(e):refresh(e.value if isinstance(e.value,int) else None);await compute()
    varga.on_value_change(_on_varga_changed)
    kind.on_value_change(lambda e:compute());refresh();ui.timer(0.1,compute,once=True)
    render_footer()
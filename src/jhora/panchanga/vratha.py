#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Ref: https://vedanshcraft.com/en-us/blogs/news/types-of-ekadashi

from itertools import combinations
from jhora.panchanga import drik as panchanga
from jhora.horoscope.chart import charts
from jhora import utils, const
import swisseph as swe
import datetime
"""
    TODO: Convert all return values [(Date,start_time,end_time,tag),...] 
    Note: end_time is optional but last item should be tag which contains descrption of the vratha
"""
_sukla_ashtami = 8
_krishna_ashtami = 23
_purattaasi = 6                     #V2.2.2
_chandra_darshan_tithi = [1]        #V2.2.2
_third_crescent_tithi = [3]         #V2.2.2
_amavasya_tithi = [30]
_pournami_tithi = [15]
_sashti_tithi = [6]
_sankatahara_chathurthi_tithi = [19]
_sankatahara_tag = "Sankatahara"
#_vinayaka_chathurthi_tithi = [4]
_vinayaka_tag = "Vinayaka"
_shivarathri_tithi = [29]
_shivarathri_tag = 'Shivarathri'
_pradosham_tithi = [13,28]
_pradosham_tag = "Pradosham"
_yoga_tag = "Yoga"
_sukla_paksha_tag = "Sukla Paksha"; _krishna_paksha_tag = "Krishna Paksha"
_tithi_tag = "Tithi"
_ekadhashi_thithi = [11,26]
_ekadhashi_list = ['varuthini','mohini','apara','nirjala','yogini','devshayani','kamika','shravan_puthraada',
                   'parivarthini','aja','indhra','paapankusha','raama','devathuna','uthapanna','mokshadha','saphala',
                   'pausha_puthraada','sathilla','jaya','vijaya','kaamadha','paapamochani']
_mahalaya_paksha_start = (15,6)
_mahalaya_paksha_tag = "Mahalaya Paksha"
_mahalaya_paksha_days = 17 
pradosham_sunset_offset = (-1.5, 1.5)
_srartha_yogas = [17,27]
_sankranthi_increment_days = 28 # Changed from 50 to 28 in V2.2.1
amavasya_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date:tithi_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_amavasya_tithi,tag_t='amavasya')
pournami_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date:tithi_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_pournami_tithi,tag_t='pournami')
sashti_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date:tithi_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_sashti_tithi,tag_t='sashti')
sankatahara_chathurthi_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date:tithi_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_sankatahara_chathurthi_tithi,tag_t='sankatahara_chathurthi')
shivarathri_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date:tithi_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_shivarathri_tithi,tag_t='shivarathri')
ekadhashi_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date:tithi_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_ekadhashi_thithi,tag_t='ekadhashi')
srartha_yoga_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date:yoga_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_srartha_yogas,tag_y='srartha')
special_vratha_map = { 'pradosham':'pradosham_dates',
                       'sankranti':'sankranti_dates',
                       'amavasya':'amavasya_dates',
                       'pournami':'pournami_dates',
                       'ekadhashi':'ekadhashi_dates',
                       'sashti':'sashti_dates',
                       'sankatahara_chathurthi':'sankatahara_chathurthi_dates',
                       'vinayaka_chathurthi':'vinayaka_chathurthi_dates',
                       'shivarathri':'shivarathri_dates',
                       'chandra_dharshan':'chandra_dharshan_dates',
                       'moondraam_pirai':'moondraam_pirai_dates',
                       'srartha':'srartha_dates',
                       'ashtaka':'ashtaka_dates',
                       'manvaadhi':'manvaadhi_dates',
                       'yugadhi':'yugadhi_dates',
                       'mahalaya_paksha':'mahalaya_paksha_dates',
                       'sathyanarayana_puja':'sathyanarayana_puja_dates',
                       'durgashtami':'durgashtami_dates',
                       'kaalashtami':'kaalashtami_dates',
                      }
_vinayaka_chathurthi_tithis = {'vinayaka_chathurthi':(4,5)}
""" 14 - Manvaadhi / Manvantra tithis - tithi/tamil-month combinations """
_manvaadhi_tithis = {'swayambhuva_manvadhi':(3,1),'swarochisha_manvadhi':(15,1),'uttama_manvadhi':(15,8),
                     'tamasa_manvadhi':(12,8),'raivata_manvadhi':(10,4),'chakshusha_manvadhi':(15,4),
                     'vaivaswata_manvadhi':(15,3),'savarni_manvadhi':(15,12),'daksha_savarni_manvadhi':(9,7),
                     'brahma_savarni_manvadhi':(7,11),'dharma_savarni_manvadhi':(11,10),
                     'rudra_savarni_manvadhi':(3,6), 'daiva_savarni_manvadhi':(30,5),
                     'indra_savarni_manvadhi':(23,5)}
""" 15 - Purvedyu/Ashtaka/Anvashtaka tithis - tithi/tamil-month combinations """
_ashtaka_tithis = {'purvedyu':[(22,6),(22,9),(22,10),(22,11),(22,12)],
                   'ashtaka':[(23,6),(23,9),(23,10),(23,11),(23,12)],
                   'anuvashtaka':[(24,6),(24,9),(24,10),(24,11),(24,12)]}
""" 4 Yugaadhi tithis  - tithi/tamil-month combinations  """
_yugadhi_tithis = {'dwapara_yuga':(30,11),'tretha_yuga':(3,2),'kali_yuga':(28,6),'sathya_yuga':(9,8)}
ashtaka_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date=None: _ashtaka_manvaadhi_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_ashtaka_tithis,tag='ashtaka')
manvaadhi_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date=None: _ashtaka_manvaadhi_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_manvaadhi_tithis,tag='manvaadhi')
yugadhi_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date=None: _ashtaka_manvaadhi_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_yugadhi_tithis,tag='yugadhi')
vinayaka_chathurthi_dates = lambda panchanga_place,panchanga_start_date,panchanga_end_date=None: _ashtaka_manvaadhi_dates(panchanga_place,panchanga_start_date,panchanga_end_date,_vinayaka_chathurthi_tithis,tag='vinayaka_chathurthi')

def _ashtaka_manvaadhi_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None,tithi_tamil_month_tuples=None,tag=None):
    res = utils.resource_strings
    tag_t = res[tag+'_str']
    _debug_print = False
    results = []
    for key,value in tithi_tamil_month_tuples.items():
        if not isinstance(value, list): value = [value] 
        for tithi_index,tamil_month_index in value:
            key_translated = utils.resource_strings[key+'_str']
            mr = search(panchanga_place, panchanga_start_date, panchanga_end_date, tithi_index=tithi_index, 
                        tamil_month_index=tamil_month_index,description=key_translated)
            if mr is not None and len(mr) > 0:
                for m,_ in enumerate(mr):
                    mrl = list(mr[m]); mrl[-1] += ' / '+ tag_t
                    mr[m] = tuple(mrl)
                results.append(mr)
    if len(results)==0: return
    results = utils.flatten_list(results)
    results = sorted(results)
    if _debug_print: print('_ashtaka_manvaadhi_dates before sorting',results)
    if panchanga_end_date is None :
        results = results[:1]
    results = sorted([results], key=lambda x:x[0])
    results = utils.flatten_list(results)
    if _debug_print: print('_ashtaka_manvaadhi_dates after sorting and flattening',results)
    return results
def special_vratha_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None,vratha_type=None,vratha_index_list=None):
    """
        Find vratha dates between dates
        If panchanga_end_date is None  - find next vratha date
        Available vratha keys are:
        'pradosham','sankranti','amavasya','pournami','ekadhashi','sashti','sankatahara chathurthi','vinayaka chathurthi',
        'shivarathri','chandra dharshan','moondraam pirai','srartha','tithi':,'nakshathra','ashtaka','manvaadhi','yugadhi'
        
    """
    res = utils.resource_strings
    if vratha_type.lower() not in special_vratha_map.keys():
        print('Allowed vratha options:',special_vratha_map.keys())
        return None
    vratha_function = special_vratha_map.get(vratha_type.lower())
    #print('Calling',vratha_function,'Arguments',panchanga_place,panchanga_start_date,panchanga_end_date)
    if vratha_type.lower() == 'tithi' or vratha_type.lower() == 'nakshathra':
        return utils.flatten_list(eval(vratha_function)(panchanga_place,panchanga_start_date,panchanga_end_date,vratha_index_list))
    else:
        return eval(vratha_function)(panchanga_place,panchanga_start_date,panchanga_end_date)
def pradosham_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None):
    _tz = panchanga_place.timezone
    res = utils.resource_strings
    _pradosha_list = res['PRADOSHA_LIST'].split(',')
    pdates = tithi_dates(panchanga_place, panchanga_start_date, panchanga_end_date, tithi_index_list=_pradosham_tithi)
    special_vratha_dates = []
    for pdate,_,_ ,tag_t in pdates:
        panch_date = panchanga.Date(pdate[0],pdate[1],pdate[2])
        cur_jd = utils.gregorian_to_jd(panch_date); jd_utc=cur_jd
        sunset = panchanga.sunset(cur_jd, panchanga_place)[2]
        pradosham_start = (sunset - jd_utc) * 24 + _tz+pradosham_sunset_offset[0]
        pradosham_end = (sunset - jd_utc) * 24 + _tz+pradosham_sunset_offset[1]
        day = panchanga.vaara(cur_jd); tag = _pradosha_list[day]+' '+res['pradosham_str']+' / '+tag_t
        special_vratha_dates.append((pdate,pradosham_start,pradosham_end,tag))
        if panchanga_end_date is None :
            return special_vratha_dates
    return special_vratha_dates
def tithi_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None,tithi_index_list=None,tag_t=''):
    """ TODO For Amavasya select Date that has amavasya spreads in the afternoon """ 
    jd = utils.julian_day_number(panchanga_start_date, (6.5,0,0))
    sunrise_hours = panchanga.sunrise(jd,panchanga_place)[0]+0.5
    res = utils.resource_strings
    if tag_t != '': tag_t = ' / '+ res[tag_t+'_str']
    _start_date = panchanga.Date(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day)
    if panchanga_end_date is None :
        _end_date = utils.next_panchanga_day(_start_date, 365)
    else:
        _end_date = panchanga.Date(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day)
    cur_date = _start_date
    cur_jd = swe.julday(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day,sunrise_hours)
    end_jd = swe.julday(_end_date.year,_end_date.month,_end_date.day,sunrise_hours)
    special_vratha_dates = []
    skip_days = 14
    if len(tithi_index_list) > 1:
        skip_days = 1
    while cur_jd < end_jd:
        cur_tithi = panchanga.tithi(cur_jd, panchanga_place)
        cur_date = panchanga.jd_to_gregorian(cur_jd)[0:3]
        if cur_tithi[0] in tithi_index_list:
            #print('cur tithi',cur_date,cur_tithi,len(cur_tithi))
            starts_at = cur_tithi[1]
            ends_at = cur_tithi[2]
            paksha = 0 if cur_tithi[0]<=15 else 1
            tag = utils.PAKSHA_LIST[paksha]+' / '+utils.TITHI_LIST[cur_tithi[0]-1]
            if tag_t not in tag: tag += tag_t
            special_vratha_dates.append((cur_date,starts_at,ends_at,tag))
            if panchanga_end_date is None :
                return special_vratha_dates
            cur_jd += skip_days
        elif len(cur_tithi) > 3 and cur_tithi[3] in tithi_index_list:
            #print('cur tithi',cur_date,cur_tithi,len(cur_tithi))        
            starts_at = cur_tithi[4]
            ends_at = cur_tithi[5]
            paksha = 0 if cur_tithi[3]<=15 else 1
            tag = utils.PAKSHA_LIST[paksha]+' / '+utils.TITHI_LIST[cur_tithi[3]-1]
            if tag_t not in tag: tag += tag_t
            special_vratha_dates.append((cur_date,starts_at,ends_at,tag))
            if panchanga_end_date is None :
                return special_vratha_dates
            cur_jd += skip_days
        cur_jd += 1 
    return special_vratha_dates
def nakshathra_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None,nakshathra_index_list=None):
    res = utils.resource_strings
    _start_date = panchanga.Date(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day)
    if panchanga_end_date is None :
        _end_date = utils.next_panchanga_day(_start_date, 365)
    else:
        _end_date = panchanga.Date(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day)
    cur_date = _start_date
    cur_jd = swe.julday(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day,0.0)
    end_jd = swe.julday(_end_date.year,_end_date.month,_end_date.day,0.0)
    special_vratha_dates = []
    skip_days = 26
    if len(nakshathra_index_list) > 1:
        skip_days = 1
    while cur_jd < end_jd:
        current_nakshathra = panchanga.nakshatra(cur_jd, panchanga_place)
        cur_date = panchanga.jd_to_gregorian(cur_jd)[0:3]
        if current_nakshathra[0] in nakshathra_index_list and cur_date not in special_vratha_dates:
            starts_at = current_nakshathra[1]
            ends_at = current_nakshathra[2]
            tag = utils.NAKSHATRA_LIST[current_nakshathra[0]-1]
            special_vratha_dates.append((cur_date,starts_at,ends_at,tag))
            if ends_at < 0:
                days = int(abs(ends_at)//24)+1
                new_ends_at = abs(ends_at)%24
                new_cur_date = utils.previous_panchanga_day(panchanga.Date(cur_date[0],cur_date[1],cur_date[2]), minus_days=days)
                special_vratha_dates[-1]= (new_cur_date,starts_at,new_ends_at,tag)
            if panchanga_end_date is None :
                return special_vratha_dates
            cur_jd += skip_days
        cur_jd += 1 
    return special_vratha_dates
def yoga_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None,yoga_index_list=None,tag_y=''):
    res = utils.resource_strings
    if tag_y != '': tag_y = ' / '+ res[tag_y+'_str']
    _start_date = panchanga.Date(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day)
    if panchanga_end_date is None :
        _end_date = utils.next_panchanga_day(_start_date, 365)
    else:
        _end_date = panchanga.Date(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day)
    cur_date = _start_date
    cur_jd = swe.julday(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day,0.0)
    end_jd = swe.julday(_end_date.year,_end_date.month,_end_date.day,0.0)
    special_vratha_dates = []
    skip_days = 26
    if len(yoga_index_list) > 0:
        skip_days = 1
    while cur_jd < end_jd:
        cur_yoga = panchanga.yogam(cur_jd, panchanga_place)
        cur_date = panchanga.jd_to_gregorian(cur_jd)[0:3]
        if cur_yoga[0] in yoga_index_list:
            ends_at = cur_yoga[1]; tag = utils.YOGAM_LIST[cur_yoga[0]-1] +' '+res['yogam_str']
            if tag_y not in tag: tag += tag_y
            special_vratha_dates.append((cur_date,ends_at,tag))
            if panchanga_end_date is None :
                return special_vratha_dates
            cur_jd += skip_days
        cur_jd += 1 
    return special_vratha_dates
def _get_planets_in_conjunction(planet_positions,minimum_separation_longitude):
    """ Exlcude Lagnam, Sun, Moon, Rahu and Ketu  planet_positions[3:8] """
    planets_in_conjunction = []
    pcomb = combinations(range(2,7),2) # Planets from Mars to Saturn
    for p1,p2 in pcomb:
        p1_long = planet_positions[p1+1][1][0]*30+planet_positions[p1+1][1][1]
        p2_long = planet_positions[p2+1][1][0]*30+planet_positions[p2+1][1][1]
        if abs(p1_long-p2_long) < minimum_separation_longitude:
            print(p1,p1_long,p2,p2_long)
            planets_in_conjunction.append((p1,p2))
    return planets_in_conjunction    
def _get_planets_in_conjunction_same_house(planet_positions,minimum_separation_longitude):
    """ Exlcude Lagnam, Sun, Moon, Rahu and Ketu  planet_positions[3:8] """
    planets_in_conjunction = []
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions[1:8])
    #print(h_to_p)
    for h,pls in enumerate(h_to_p):
        ps = [int(p) for p in pls.split('/') if p.isdigit()]
        coms = combinations(ps,2)
        #print(h,pls,ps)
        for p1, p2 in coms:
            p1_long = planet_positions[p1+1][1][0]*30+planet_positions[p1+1][1][1]
            p2_long = planet_positions[p2+1][1][0]*30+planet_positions[p2+1][1][1]
            if abs(p1_long-p2_long) < minimum_separation_longitude:
                print(h,p1,p1_long,p2,p2_long)
                planets_in_conjunction.append((h,[p1,p2]))
    return planets_in_conjunction
def conjunctions(panchanga_place,panchanga_start_date,panchanga_end_date,minimum_separation_longitude,planets_in_same_house=False):
    #if planets_in_same_house:
    #    minimum_separation_longitude = 30.0
    _start_date = panchanga.Date(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day)
    _end_date = panchanga.Date(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day)
    cur_date = _start_date
    #cur_jd = swe.julday(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day,0.0)
    #end_jd = swe.julday(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day,0.0)
    cur_jd = utils.julian_day_number(panchanga_start_date, (0,0,0))
    end_jd = utils.julian_day_number(panchanga_end_date, (0,0,0))
    special_vratha_dates = []
    while cur_jd < end_jd:
        cur_date = panchanga.jd_to_gregorian(cur_jd)[0:3] # Ignore time
        planet_positions = charts.divisional_chart(cur_jd, panchanga_place)
        if planets_in_same_house:
            result_local = _get_planets_in_conjunction_same_house(planet_positions,minimum_separation_longitude)
        else:
            result_local = _get_planets_in_conjunction(planet_positions,minimum_separation_longitude)
        if result_local:
            special_vratha_dates.append((cur_date,result_local))
        cur_jd += 1 
    return utils.flatten_list(special_vratha_dates)
def _get_conjunction_time_1(jd,place,p1,p2):
    tz = place.timezone
    yjd, mjd, djd, _ = utils.jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(panchanga.Date(yjd, mjd, djd))
    n=24; offsets = [s/n for s in range(-n,n)]
    rise = panchanga.sunrise(jd, place)[2]
    p1_long = [];p2_long=[]
    ya = 0;
    for t in offsets:
        pp = charts.rasi_chart(jd+(t/24.0/60.0),place)
        p1_long=pp[p1+1][1][0]*30+pp[p1+1][1][1]
        p2_long=pp[p2+1][1][0]*30+pp[p2+1][1][1]
        print(utils.to_dms((jd + t -jd_utc) * 24 + tz),utils.to_dms(p1_long,is_lat_long='plong'),utils.to_dms(p2_long,is_lat_long='plong'))
        if abs(p1_long-p2_long)<.01:
            print('found matching long')
            ya = t; return ya;
    #print('p1_long',[utils.to_dms(p1l,is_lat_long='plong') for p1l in p1_long])
    #print('p2_long',[utils.to_dms(p2l,is_lat_long='plong') for p2l in p2_long])
    #long_diff = [ p1 - p2 for (p1, p2) in zip(p1_long, p2_long) ]
    #y = long_diff; x= offsets;
    #ya = utils.inverse_lagrange(x, y, 0.0)
    vt = (rise + ya -jd_utc) * 24 + tz
    return ya# vt
def _get_conjunction_time(jd,place,p1,p2):
    tz = place.timezone
    yjd, mjd, djd, _ = utils.jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(panchanga.Date(yjd, mjd, djd))
    #jd_utc = jd - tz/24. ### It appears this way calculating jd_utc is incorrect
    n=10; offsets = [s/n for s in range(0,n)]
    rise = panchanga.sunrise(jd, place)[2]
    p1_long = [];p2_long=[]
    for t in offsets:
        pp = charts.rasi_chart(rise+t,place)
        p1_long.append(pp[p1+1][1][0]*30+pp[p1+1][1][1])
        p2_long.append(pp[p2+1][1][0]*30+pp[p2+1][1][1])
    #print('p1_long',[utils.to_dms(p1l,is_lat_long='plong') for p1l in p1_long])
    #print('p2_long',[utils.to_dms(p2l,is_lat_long='plong') for p2l in p2_long])
    long_diff = [ abs(p1 - p2) for (p1, p2) in zip(p1_long, p2_long) ]
    print(long_diff)
    y = long_diff; x= offsets;
    ya = utils.inverse_lagrange(x, y, 0.0)
    vt = (rise + ya -jd_utc) * 24 + tz
    print(utils.to_dms(vt,as_string=True))
    return ya# vt
def search(panchanga_place,panchanga_start_date,panchanga_end_date=None,tithi_index=None,nakshathra_index=None,
           yoga_index=None,tamil_month_index=None,description='',festival_name_contains=None):
    _special_vratha_dates = []
    tithi_results = []
    nakshathra_results = []
    yoga_results = []
    tm_results = []
    _debug_print = False
    start_time = datetime.datetime.now()
    if _debug_print: print('search',panchanga_place,panchanga_start_date,panchanga_end_date,tithi_index,nakshathra_index,yoga_index,tamil_month_index,description)
    if panchanga_end_date is None :
        _panchanga_end_date = utils.next_panchanga_day(panchanga_start_date, 365)
    else:
        _panchanga_end_date = panchanga.Date(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day)
    # Search for all festivals if all panchanga indices are None
    if all(x is None for x in (tithi_index, nakshathra_index, yoga_index, tamil_month_index)):
        if _debug_print: print('search for festival from csv')
        fest_data = get_festivals_between_the_dates(panchanga_start_date, panchanga_end_date, panchanga_place,festival_name_contains=festival_name_contains)
        if len(fest_data)>0:
            for fdate,fest in fest_data:
                if _debug_print: print(fdate,fest)
                jd = utils.julian_day_number(panchanga.Date(fdate[0],fdate[1],fdate[2]), (fdate[3],0,0))
                sunrise_hours = panchanga.sunrise(jd,panchanga_place)[0]
                if len(fest)!=0:
                    _special_vratha_dates.append([(fdate,sunrise_hours,f['Festival_'+const._DEFAULT_LANGUAGE]) for f in fest][0])
    # Tithi search
    if tithi_index !=None:
        tithi_results = tithi_dates(panchanga_place, panchanga_start_date, _panchanga_end_date, [tithi_index])
        if _debug_print: print('tithi_results',tithi_results)
        if len(tithi_results) == 0: return []
        _special_vratha_dates = tithi_results
    #print('_special_vratha_dates',_special_vratha_dates)
    # Nakshathra search
    if nakshathra_index is not None:
        if _debug_print: print('finding nakshathra dates ')
        if len(_special_vratha_dates)==0:
            nakshathra_results = nakshathra_dates(panchanga_place, panchanga_start_date, panchanga_end_date, [nakshathra_index])
            if len(nakshathra_results) == 0: return []
            _special_vratha_dates = nakshathra_results
        else:    
            if _debug_print: print('finding nakshathra dates from vratha dates')
            for t_date in _special_vratha_dates:
                p_date1 = panchanga.Date(t_date[0][0],t_date[0][1],t_date[0][2])
                vratha_tag = t_date[-1]
                cur_jd = swe.julday(p_date1.year,p_date1.month,p_date1.day,0.0)
                nr = panchanga.nakshatra(cur_jd, panchanga_place)
                if _debug_print: print('nakshathra',p_date1,nr,nakshathra_index)
                if nakshathra_index in [nr[0],nr[3]]:
                    if _debug_print: print('Found nakshathra',p_date1,nr,nakshathra_index,nr[0],nr[3])
                    start_time = nr[1]; end_time = nr[2]
                    nak_tag = utils.NAKSHATRA_LIST[nakshathra_index-1]
                    nakshathra_results.append((p_date1,start_time, end_time,vratha_tag+' / '+nak_tag)) #(t_date,tag))
            if len(nakshathra_results) == 0: return []
            _special_vratha_dates = nakshathra_results
    # yoga search
    if yoga_index is not None:
        if _debug_print: print('finding yoga dates')
        if len(_special_vratha_dates)==0:
            yoga_results = yoga_dates(panchanga_place, panchanga_start_date, panchanga_end_date, [yoga_index])
            if len(yoga_results) == 0: return []
            _special_vratha_dates = yoga_results 
        else:           
            if _debug_print: print('finding yoga from vratha dates')
            for t_date in _special_vratha_dates:
                vratha_tag = t_date[-1]
                p_date1 = panchanga.Date(t_date[0][0],t_date[0][1],t_date[0][2])
                cur_jd = swe.julday(p_date1.year,p_date1.month,p_date1.day,0.0)
                #yr = yoga_dates(panchanga_place, p_date1, p_date2, [yoga_index])
                yr = panchanga.yogam(cur_jd, panchanga_place)
                #if len(yr) > 0:
                #    yoga_results += yr
                if yoga_index == yr[0]:
                    yoga_tag = utils.YOGAM_LIST[yoga_index-1]
                    end_time = yr[1]
                    yoga_results.append((p_date1,end_time,vratha_tag+' / '+yoga_tag))
                elif len(yr) > 2 and yoga_index == yr[2]:
                    yoga_tag = utils.YOGAM_LIST[yoga_index-1]
                    end_time = yr[3]
                    yoga_results.append((p_date1,end_time,vratha_tag+' / '+yoga_tag))
            if len(yoga_results) == 0: return []
            _special_vratha_dates = yoga_results
    # Tamil month search
    if tamil_month_index is not None:
        if _debug_print: print('finding also tamil month dates', _special_vratha_dates)
        for sv_result in _special_vratha_dates: #V2.3.0
            t_date = sv_result[0]; ts_time = sv_result[1]; te_time = sv_result[2]
            vratha_tag = sv_result[-1]
            if _debug_print: print(t_date)#,ts_time,te_time)
            panchanga_date = panchanga.Date(t_date[0],t_date[1],t_date[2])
            tamil_month_day = panchanga.tamil_solar_month_and_date(panchanga_date, panchanga_place)            
            if _debug_print: print(t_date,'tamil_maadham/day',tamil_month_day,'search tamil_month',tamil_month_index)
            if tamil_month_day[0]+1 == tamil_month_index:
                #srise = panchanga.sunrise(utils.julian_day_number(t_date, (0,0,0)),panchanga_place)[0]
                tm_tag = utils.MONTH_LIST[tamil_month_index-1]
                tm_results.append((t_date,ts_time,te_time,vratha_tag+' / '+tm_tag)) # V2.3.0
                if _debug_print: print('found',t_date,tamil_month_day[0]+1,tamil_month_day[1])#,lunar_month)
        if _debug_print: print('tamil month dates',tm_results)
        if len(tm_results) == 0: return []
        _special_vratha_dates = tm_results
    if panchanga_end_date is None :
        _special_vratha_dates = _special_vratha_dates[:1]
    if _debug_print: print(tithi_index,nakshathra_index,yoga_index,tamil_month_index,_special_vratha_dates)
    if _debug_print: print('_special_vratha_dates',_special_vratha_dates)
    _special_vratha_dates = [tup[:-1] + (tup[-1]+' / '+description,) for tup in _special_vratha_dates]
    end_time = datetime.datetime.now()
    if _debug_print: print('search cpu time elapsed',end_time-start_time,' seconds')
    return _special_vratha_dates
def sankranti_dates(place,start_date,end_date=None):
    res = utils.resource_strings
    results = []
    jd_start = swe.julday(start_date.year,start_date.month,start_date.day,9.0)# get around cur_sunrise
    if end_date is None :
        _end_date = utils.next_panchanga_day(start_date, 365)
    else:
        _end_date = panchanga.Date(end_date.year,end_date.month,end_date.day)
    jd_end = swe.julday(_end_date.year,_end_date.month,_end_date.day,9.0)
    day_inc= _sankranthi_increment_days
    jd_inc = jd_start
    while jd_inc < jd_end:#-day_inc:#for i in range(12):
        p_date = panchanga.jd_to_gregorian(jd_inc)
        p_date = panchanga.Date(p_date[0],p_date[1],p_date[2])
        sd = panchanga.next_sankranti_date(p_date, place)
        sank_tag = utils.RAASI_LIST[sd[2]] +' '+res['sankranti_str']
        results.append(((sd[0][0],sd[0][1],sd[0][2]),sd[1],sank_tag))
        if end_date is None :
            return results
        jd_inc +=  day_inc
    return results
def sathyanarayana_puja_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None):
    return search(panchanga_place, panchanga_start_date, panchanga_end_date, tithi_index=_pournami_tithi[0],
                  description=utils.resource_strings['sathyanarayana_puja_str'])
def durgashtami_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None):
    return search(panchanga_place, panchanga_start_date, panchanga_end_date, tithi_index=_sukla_ashtami,
                  description=utils.resource_strings['durgashtami_str'])
def kaalashtami_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None):
    return search(panchanga_place, panchanga_start_date, panchanga_end_date, tithi_index=_krishna_ashtami,
                  description=utils.resource_strings['kaalashtami_str'])
def mahalaya_paksha_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None):
    res = utils.resource_strings
    mpds = search(panchanga_place,panchanga_start_date,panchanga_end_date,tithi_index=_amavasya_tithi[0],tamil_month_index=_purattaasi)
    if len(mpds) > 0:
        mpds = mpds[0]
    else:
        return []
    jd = utils.gregorian_to_jd(panchanga.Date(mpds[0][0],mpds[0][1],mpds[0][2]))
    mpd = []; mpd.append(mpds)
    for d in range(1,_mahalaya_paksha_days):
        cur_tithi = panchanga.tithi(jd-d, panchanga_place)
        mpd.append((panchanga.jd_to_gregorian(jd-d),cur_tithi[1],cur_tithi[2],res['mahalaya_paksha_str']+' / '+utils.TITHI_LIST[cur_tithi[0]-1])) #V2.3.0
        if panchanga_end_date is None  or cur_tithi[0]==_pournami_tithi[0] or (len(cur_tithi)>3 and cur_tithi[3]==_pournami_tithi[0]):
            mpd = sorted(mpd)
            return mpd
    mpd = sorted(mpd)
    return mpd
def srartha_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None):
    res = utils.resource_strings
    _debug_print = False
    results = []
    results += amavasya_dates(panchanga_place,panchanga_start_date,panchanga_end_date)
    if _debug_print: print('amavasya dates results',results)
    results += sankranti_dates(panchanga_place,panchanga_start_date,panchanga_end_date)#,True)
    if _debug_print: print('sankranthi dates results',results)
    results += mahalaya_paksha_dates(panchanga_place,panchanga_start_date,panchanga_end_date)
    if _debug_print: print('mahalaya dates results',results)
    results += yoga_dates(panchanga_place, panchanga_start_date, panchanga_end_date, _srartha_yogas)
    if _debug_print: print('yoga dates results',results)
    results += manvaadhi_dates(panchanga_place,panchanga_start_date,panchanga_end_date)
    if _debug_print: print('manvaadhi dates results',results)
    results += ashtaka_dates(panchanga_place,panchanga_start_date,panchanga_end_date)
    if _debug_print: print('ashtaka dates results',results)
    results += yugadhi_dates(panchanga_place,panchanga_start_date,panchanga_end_date)
    if _debug_print: print('yugadhi dates results',results)
    results = [utils.flatten_list([results])]
    if _debug_print: print('srartha dates results',results)
    results = utils.flatten_list(results)
    results = sorted(results, key=lambda x:x[0])
    if panchanga_end_date is None :
        return results[:1]
    return results
def chandra_dharshan_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None):
    res = utils.resource_strings
    c_dates = tithi_dates(panchanga_place, panchanga_start_date, panchanga_end_date, _chandra_darshan_tithi) #V2.2.2
    results = []
    for c_date,_,_,tag_t in c_dates:
        jd = utils.gregorian_to_jd(panchanga.Date(c_date[0],c_date[1],c_date[2]))
        sunset = panchanga.sunset(jd, panchanga_place)[0]
        moonset = panchanga.moonset(jd, panchanga_place)[0]
        tag = res['chandra_dharshan_str']+' / '+tag_t
        results.append((c_date,sunset,moonset,tag))
        if panchanga_end_date is None :
            return results
    return results
def moondraam_pirai_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None):
    res = utils.resource_strings
    c_dates = tithi_dates(panchanga_place, panchanga_start_date, panchanga_end_date, _third_crescent_tithi) #V2.2.2
    results = []
    for c_date,_,_,tag_t in c_dates:
        jd = utils.gregorian_to_jd(panchanga.Date(c_date[0],c_date[1],c_date[2]))
        sunset = panchanga.sunset(jd, panchanga_place)[0]
        moonset = panchanga.moonset(jd, panchanga_place)[0]
        tag = res['moondraam_pirai_str']+' / '+tag_t
        results.append((c_date,sunset,moonset,tag))
        if panchanga_end_date is None :
            return results
    return results
def _sankalpa_mantra(panchanga_date,panchanga_place,ritu_per_solar_tamil_month=const.ritu_per_solar_tamil_month):  #V2.3.0
    """ TODO: Ritu may be INCORRECT """
    vasara_list = ['bAnu','indhu','bhaumya','saumya','guru','bhrigu','sthira']
    raasi_list = ['mEsha','rishaba','mithuna','kataka','simha','kanyA','thulA','viruchiga','dhanur','makara','kumbha','meena']
    ritu_list = ['vasantha','greeshma','varsha','sharad','hEmantha','sisira']
    jd = swe.julday(panchanga_date.year,panchanga_date.month,panchanga_date.day,0.0)
    maasa_index = panchanga.lunar_month(jd, panchanga_place)[0]-1
    lunar_month = raasi_list[maasa_index]
    ritu = ritu_list[panchanga.ritu(maasa_index+1)]
    if ritu_per_solar_tamil_month:
        tamil_maasa_index,_ = panchanga.tamil_solar_month_and_date(panchanga_date, panchanga_place)
        ritu = ritu_list[panchanga.ritu(tamil_maasa_index+1)]
    samvastra = utils.YEAR_LIST[panchanga.samvatsara(panchanga_date, place, maasa_index, zodiac=0)-1]
    tithi_index = panchanga.tithi(jd, panchanga_place)[0]-1
    paksha = utils.PAKSHA_LIST[0].split()[0]
    if tithi_index > 15:
        paksha = utils.PAKSHA_LIST[1].split()[0]
    tithi = utils.TITHI_LIST[tithi_index]
    vasara = vasara_list[panchanga.vaara(jd)]
    nakshathra = utils.NAKSHATRA_LIST[panchanga.nakshatra(jd, panchanga_place)[0]-1]
    """ TODO Solstice calculation not right - find shortest and logest days of year """
    solistice="dakshiNAyanE "
    if maasa_index < 3 or maasa_index > 8:
        solistice="uttharAyanE "
    mantra_str = "{0} nAma samvathsarE, {1} {7} rithou, {2} mAsE, {3} pakshE, "+ \
                            "{4} puNyathithou, {5} vAsara, {6} nakshatra yukthAyAm, asyAm "+ \
                            "amAvAsyAyAm  puNyakAlE darsa srardham thila tharppaNa roopENa adhya karishyE"
    return mantra_str.format(samvastra,solistice,lunar_month,paksha,tithi,vasara,nakshathra,ritu)
def tithi_pravesha(birth_date:panchanga.Date=None,birth_time:tuple=None,birth_place:panchanga.Place=None,year_number=None, plus_or_minus_duration_in_days=30):
    """
        Find tithi pravesha - current date with same tithi and lunar month as birth tithi/lunar_month
        @param birth_date: birth_date as drik.Date tuple
        @param birth_time: birth time as tuple
        @param birth place: birth place as drik.Place tuple
        @param current_date_start: start date as drik.Date - default = (current_year,1,1) Jan 1st of current
        @param current_date_end: end date as drik.Date - default = (current_year,12,31) Dec 31st of current year
        @return: [date between current_date_start and current_date_end at which birth tithi/lunar_month occurs,
                 tithi_time, month_tithi_name_as_string]
                 Example return value: [((2024, 11, 27), '06:24:58 AM (+1)', 'Kaarthigai Krishna Dhuvadhasi')]
    """
    current_year = datetime.datetime.today().year
    """
    if current_year <= birth_date.year:
        print("Tithi Pravesha can be calculated only years greater than birth_year")
        return []
    """
    if year_number is None or year_number <= birth_date.year:
        year_number = current_year
    cds = list(birth_date)
    current_date_start = panchanga.Date(year_number,cds[1],cds[2])
    current_date_start = utils.previous_panchanga_day(current_date_start, plus_or_minus_duration_in_days)
    current_date_end = utils.next_panchanga_day(current_date_start, 2*plus_or_minus_duration_in_days)
    #print(current_date_start,current_date_end)
    jd = utils.julian_day_number(birth_date, birth_time); _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    t = panchanga.tithi(jd, birth_place); tm = panchanga.tamil_solar_month_and_date(birth_date, birth_place)
    t_frac = utils.get_fraction(t[1], t[2], birth_time_hrs)
    #print('tithi',(t[0],utils.to_dms(t[1]),utils.to_dms(t[2]),t_frac),'tamil month/day',tm)
    sr = search(birth_place, current_date_start, current_date_end, tithi_index=t[0], tamil_month_index=tm[0]+1)
    tp = []
    for s_result in sr:
        #print('search result',s_result)
        s_date = s_result[0]; s_start = s_result[1]; s_end=s_result[2]; s_desc=s_result[3]
        t_len = s_end - s_start
        if s_start > 23.99:
            t_len += 24
        t_time = s_end - t_frac*t_len
        tp.append((s_date,t_time,s_end,s_desc))
    return tp

import csv

# Global variable to store festival data
festival_data = []

# Function to load festival data from CSV file
def load_festival_data(file_path=const._FESTIVAL_FILE):
    global festival_data
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        festival_data = [row for row in reader]
def _get_criteria_for_the_day(jd,place,use_purnimanta_system=None):
    y,m,d,_ = utils.jd_to_gregorian(jd); date_in = panchanga.Date(y,m,d)
    _tithi_returned = panchanga.tithi(jd, place)
    _tithis = [_tithi_returned[0],_tithi_returned[3]] if len(_tithi_returned)>3 else [_tithi_returned[0]]
    _naks = panchanga.nakshatra(jd, place)
    _nak_ids = [_naks[0],_naks[3]] if len(_naks)>3 else [_naks[0]]
    tm = None; td = None; adhik_maasa = None; _vaara = panchanga.vaara(jd)+1
    day_id = panchanga.vaara(jd)
    if use_purnimanta_system is None:
        tm,td = panchanga.tamil_solar_month_and_date(date_in, place)
    else:
        tm,td,_,adhik_maasa,_ = panchanga.lunar_month_date(jd,place,
                                                use_purnimanta_system=use_purnimanta_system)
        tm -= 1
    criteria = {
        'Tithi': _tithis,
        'Nakshatra': _nak_ids,
        'tamil_month': tm+1,
        'tamil_day': td,
        'vaara':day_id+1,
        'adhik_maasa':adhik_maasa,
    }
    return criteria
def get_festivals_between_the_dates(start_date:panchanga.Date, end_date:panchanga.Date, place:panchanga.Place,
                                    festival_name_contains=None):
    #global festival_data
    #if len(festival_data) == 0: load_festival_data(const._FESTIVAL_FILE)
    start_jd = utils.julian_day_number(start_date, (12,0,0))
    end_jd = utils.julian_day_number(end_date, (12,0,0))
    matching_festivals = []
    while start_jd <= end_jd:
        mfd = get_festivals_of_the_day(start_jd, place,festival_name_contains=festival_name_contains)
        matching_festivals.append((utils.jd_to_gregorian(start_jd),mfd))
        start_jd += 1
    return matching_festivals
def get_festivals_of_the_day(jd,place,festival_name_contains=None):
    global festival_data
    if len(festival_data) == 0: load_festival_data(const._FESTIVAL_FILE)
    matching_festivals = []
    criteria_list = [_get_criteria_for_the_day(jd, place, use_purnimanta_system=c) for c in [None,False,True]]
    check_rows = festival_data if festival_name_contains is None \
        else [row for row in festival_data if festival_name_contains.casefold() in row['Festival_en'].casefold()]
    for row in check_rows:#festival_data:
        criteria = criteria_list[int(row['calendar_type'])]
        #print(row['Festival_name'],utils.jd_to_gregorian(jd),criteria)
        match = True
        for key, value in criteria.items():
            if row.get(key):
                try:
                    # Convert both to float for comparison (handles empty strings gracefully)
                    if isinstance(value,list):
                        match = match and any([float(row[key]) ==float(v) for v in value])# == float(value)
                    else:
                        match = match and float(row[key]) == float(value)
                    if festival_name_contains is not None:
                        match = match and festival_name_contains.casefold() in row['Festival_en'].casefold()
                        #print(row['Festival_en'],festival_name_contains,match)
                except:
                    match = False
                    break
        if match:
            matching_festivals.append(row)
    return matching_festivals
# Function to get festival row based on input parameters
def get_festival(tithi=None, nakshatra=None, tamil_month=None, tamil_day=None,vaara=None,adhik_maasa=None):
    """
        TODO: Mahalaya Paksha dates cannot be checked directly.
        It has to be checked first getting mahalaya amavasya date on purattasi.
        And comparing current tithi if in between
        TODO: Some festival dates have to be calculated not directly associated with tithi/nak/etc combinations
    """
    criteria = {
        'Tithi': tithi,
        'Nakshatra': nakshatra,
        'tamil_month': tamil_month,
        'tamil_day': tamil_day,
        'vaara':vaara,
        'adhik_maasa':adhik_maasa,
    }
    matching_festivals = []
    for row in festival_data:
        match = True
        for key, value in criteria.items():
            if row.get(key):
                try:
                    # Convert both to float for comparison (handles empty strings gracefully)
                    match = match and float(row[key]) == float(value)
                except:
                    match = False
                    break
        if match:
            matching_festivals.append(row)
    return matching_festivals

if __name__ == "__main__":
    utils.set_language('en')
    from jhora.tests import pvr_tests
    place = panchanga.Place('Chennai,India',13.0878,80.2785,5.5)
    start_date = panchanga.Date(2025,1,1); end_date = panchanga.Date(2025,12,31)
    start_time = datetime.datetime.now()
    fest_data = search(place,start_date,end_date,festival_name_contains='pongal')
    for fdate,ftime,fest in fest_data:
        print('fdate,fest',fdate,ftime,fest)
    end_time = datetime.datetime.now()
    print('cpu time ',end_time-start_time,' seconds')
    exit()
    dob = (1996,12,7) ; tob = (5,34,0); place = panchanga.Place('Chennai',13.0878,80.2785,5.5)
    const.use_planet_speed_for_panchangam_end_timings = False
    jd = utils.julian_day_number(start_date, tob)
    print(panchanga.tithi(jd,place))
    _festival_file = const._DATA_DIR +const._sep+'hindu_festivals_multilingual_unicode_bom.csv'
    load_festival_data(_festival_file)
    print(get_festivals_of_the_day(jd,place))
    exit()
    mp_dates = mahalaya_paksha_dates(place, start_date, end_date)
    print('mahalaya dates',mp_dates)
    exit()
    p_date = panchanga.Date(dob[0],dob[1],dob[2])    
    sr_dates = sathyanarayana_puja_dates(place, start_date, end_date)
    print(sr_dates)
    exit()
    p1=3; p2=6
    cdate_jd,p_long = panchanga.previous_conjunction_of_planet_pair(p1,p2,place,start_date)
    yc,dc,mc,fhc = utils.jd_to_gregorian(cdate_jd)
    print('Conjunction of planets',utils.PLANET_NAMES[p1],'and',utils.PLANET_NAMES[p2],'is',\
          yc,dc,mc,utils.to_dms(fhc,as_string=True),'at longitude',utils.to_dms(p_long,is_lat_long='plong'),\
          'Before date:',start_date)
    cdate_jd,p_long = panchanga.next_conjunction_of_planet_pair(p1,p2,place,start_date)
    yc,dc,mc,fhc = utils.jd_to_gregorian(cdate_jd)
    print('Conjunction of planets',utils.PLANET_NAMES[p1],'and',utils.PLANET_NAMES[p2],'is',\
          yc,dc,mc,utils.to_dms(fhc,as_string=True),'at longitude',utils.to_dms(p_long,is_lat_long='plong'),\
          'After date:',start_date)
    exit()
    pvr_tests.tithi_pravesha_tests()
    exit()
    utils.set_language('ta')
    utils.get_resource_lists()
    msgs = utils.get_resource_messages()
    panchanga.set_ayanamsa_mode(ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE)
    lat =  42.1181#13.0389 # 13.0389 # 41.881832 # 65.8252 N # Latitude - N+/S-
    lon = -88.0962 #80.2619#-87.623177# -144.0657 W # Longitude  - E+/W-
    tz = -5.0#5.5#
    place = panchanga.Place('PlacePerLatLong',lat, lon, tz)#('Chennai,IN',lat, lon, tz)
    #"""
    start_date = panchanga.Date(2024,1,1)
    end_date = panchanga.Date(2025,4,31)
    tithi_index = _amavasya_tithi
    vdates = tithi_dates(place, start_date, end_date, tithi_index)
    #vdates = srartha_dates(place, start_date, end_date)
    for vdate in vdates:
        #print('vdate',vdate)
        jd = utils.julian_day_number(vdate[0], (9,0,0))
        v = panchanga.vaara(jd)
        adate = panchanga.Date(vdate[0][0],vdate[0][1],vdate[0][2])
        sdate = str(vdate[0][1])+'-'+str(vdate[0][2])+'-'+str(vdate[0][0])
        print(sdate+'\t'+utils.DAYS_LIST[v]+'\t'+vdate[2]+'\t upto '+vdate[1],'\n',_sankalpa_mantra(adate,place,ritu_per_solar_tamil_month=False))
    exit()
    #"""
    print('amavasya dates',vdates)
    s_dates = sankranti_dates(place, start_date, end_date, return_as_str=False)
    print('sankranti dates',s_dates)
    #exit()
    #"""
    vdates = search(place,start_date,end_date,tithi_index=_pournami_tithi[0])
    print(vdates)
    mpds = search(place,start_date,end_date,tithi_index=_pournami_tithi[0],tamil_month_index=_purattaasi)
    print(mpds)
    sr_dates = srartha_dates(place, start_date, end_date)
    print('Srartha Dates',start_date,end_date,'\n',sr_dates)
    exit()
    sr_dates = special_vratha_dates(place, start_date, end_date, 'srartha', vratha_index_list=None)
    print(sr_dates)
    print(special_vratha_dates(place,start_date,end_date,'yugadhi'))
    #Sankranti Test
    s_dates = sankranti_dates(place, start_date, end_date, return_as_str=False)
    print(s_dates)
    #"""
    vdates = manvaadhi_dates(place, start_date, end_date)
    print(vdates)
    vdates = ashtaka_dates(place, start_date, end_date)
    print(vdates)
    vdates = yugadhi_dates(place, start_date, end_date)
    print(vdates)
    print(nakshathra_dates(place,start_date,end_date,_pournami_tithi))
    print(special_vratha_dates(place,start_date,end_date,'nakshathra',_pournami_tithi))
    tithi_index = _pournami_tithi
    vdates = tithi_dates(place, start_date, end_date, tithi_index)
    print(vdates)
    vdates = sankatahara_chathurthi_dates(place, start_date, end_date)
    print(vdates)
    vdates = shivarathri_dates(place, start_date, end_date)
    print(vdates)
    vdates = pradosham_dates(place,start_date,end_date)
    print(vdates)
    #nakshathra_index = 15
    start_date = panchanga.Date(-3101,1,22)
    end_date = panchanga.Date(-3101,1,23)
    vdates = conjunctions(place,start_date,end_date,30.0,planets_in_same_house=True)
    print(vdates)

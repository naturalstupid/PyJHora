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
from jhora import utils, const
"""
    drik here is generic model name can be surya_sidhantha or drik depending on value
    of const.astrology_model_default value
"""
drik = utils.hora_engine_proxy
from jhora.horoscope.chart import charts
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
        panch_date = drik.Date(pdate[0],pdate[1],pdate[2])
        cur_jd = utils.gregorian_to_jd(panch_date); jd_utc=cur_jd
        sunset = drik.sunset(cur_jd, panchanga_place)[2]
        pradosham_start = (sunset - jd_utc) * 24 + _tz+pradosham_sunset_offset[0]
        pradosham_end = (sunset - jd_utc) * 24 + _tz+pradosham_sunset_offset[1]
        day = drik.vaara(cur_jd,panchanga_place); tag = _pradosha_list[day]+' '+res['pradosham_str']+' / '+tag_t
        special_vratha_dates.append((pdate,pradosham_start,pradosham_end,tag))
        if panchanga_end_date is None :
            return special_vratha_dates
    return special_vratha_dates
def _sunrise_jd_of_date(date_tuple, place):
    """ Local Julian day of the sunrise of the civil date (year, month, day). """
    return drik.sunrise(utils.julian_day_number(drik.Date(date_tuple[0], date_tuple[1], date_tuple[2]), (0, 0, 0)), place)[2]
def _sunrise_tithis_of_the_day(jd, place):
    """ Tithis of the civil (panchanga) day of jd, taken at SUNRISE (same rule as drik._get_tithi_type()):
        the tithi prevailing at this day's sunrise, followed by any kshaya (lost) tithi - a tithi that starts after
        this day's sunrise and ends before the next day's sunrise and so belongs to this day.
        A vriddhi (repeated) tithi is the sunrise tithi of two consecutive days and so is returned for both days.
        @param jd: Julian day number of any time of the day
        @param place: drik.Place
        @return: (tithi_at_sunrise, [kshaya tithis], sunrise_jd)  tithi numbers are 1..30
    """
    y, m, d, _ = utils.jd_to_gregorian(jd)
    sr_jd = _sunrise_jd_of_date((y, m, d), place)
    t_today = drik.tithi(sr_jd, place)[0]
    ny, nm, nd, _ = utils.jd_to_gregorian(utils.julian_day_number(drik.Date(y, m, d), (12, 0, 0)) + 1)
    t_next = drik.tithi(_sunrise_jd_of_date((ny, nm, nd), place), place)[0]
    kshaya = [(t_today + k - 1) % 30 + 1 for k in range(1, (t_next - t_today) % 30)]
    return t_today, kshaya, sr_jd
def _kshaya_tithi_times(sr_jd, place, kshaya_tithi):
    """ Start / end of a kshaya tithi of the day of sr_jd, as float hours from that day's local midnight
        (may exceed 24 when it falls after midnight). Returns (None, None) if it cannot be found. """
    y, m, d, _ = utils.jd_to_gregorian(sr_jd)
    midnight_jd = utils.julian_day_number(drik.Date(y, m, d), (0, 0, 0))
    t = drik.tithi(sr_jd, place)
    jd_k = midnight_jd + t[2]/24.0                      # end of the sunrise tithi
    for _ in range(3):                                  # step over intermediate tithis (if two are lost)
        jd_k += 1.0/1440.0
        tk = drik.tithi(jd_k, place)
        ky, km, kd, _ = utils.jd_to_gregorian(jd_k)
        offset = 24.0*round(utils.julian_day_number(drik.Date(ky, km, kd), (0, 0, 0)) - midnight_jd)
        if tk[0] == kshaya_tithi:
            return tk[1] + offset, tk[2] + offset
        jd_k = utils.julian_day_number(drik.Date(ky, km, kd), (0, 0, 0)) + tk[2]/24.0
    return None, None
def tithi_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None,tithi_index_list=None,tag_t=''):
    """
        Dates (civil / panchanga days) on which any of the given tithis falls.
        A day's tithi is the tithi prevailing at its SUNRISE, so a tithi is listed only on the day it is at sunrise -
        not also on the previous day just because it starts before that day's midnight.
        A kshaya (lost) tithi - one that touches no sunrise - is listed on the day it falls in (between that day's
        sunrise and the next sunrise). A vriddhi (repeated) tithi is at two consecutive sunrises; only the first day
        is listed.
        @return: [((year,month,day), tithi start hours, tithi end hours, tag), ...]
            hours are from local midnight of that day (negative: previous day, > 24: next day)
    """
    res = utils.resource_strings
    if tag_t != '': tag_t = ' / '+ res[tag_t+'_str']
    _start_date = drik.Date(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day)
    if panchanga_end_date is None :
        _end_date = utils.next_panchanga_day(_start_date, 365)
    else:
        _end_date = drik.Date(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day)
    cur_jd = utils.julian_day_number(_start_date, (12, 0, 0))     # noon: any time of the day; sunrise is found per day
    end_jd = utils.julian_day_number(_end_date, (12, 0, 0))
    special_vratha_dates = []
    skip_days = 14
    if len(tithi_index_list) > 1:
        skip_days = 1
    previous_day = None                                            # (jd, sunrise tithi) of the day just checked
    while cur_jd < end_jd:
        cur_date = utils.jd_to_gregorian(cur_jd)[0:3]
        t_sunrise, kshaya_tithis, sr_jd = _sunrise_tithis_of_the_day(cur_jd, panchanga_place)
        is_vriddhi_second_day = (previous_day is not None and previous_day[0] == cur_jd - 1
                                 and previous_day[1] == t_sunrise)
        previous_day = (cur_jd, t_sunrise)
        matched = None
        if t_sunrise in tithi_index_list and not is_vriddhi_second_day:
            cur_tithi = drik.tithi(sr_jd, panchanga_place)
            matched = (t_sunrise, cur_tithi[1], cur_tithi[2])
        else:
            for kt in kshaya_tithis:
                if kt in tithi_index_list:
                    starts_at, ends_at = _kshaya_tithi_times(sr_jd, panchanga_place, kt)
                    matched = (kt, starts_at, ends_at)
                    break
        if matched is not None:
            t_no, starts_at, ends_at = matched
            paksha = 0 if t_no <= 15 else 1
            tag = utils.PAKSHA_LIST[paksha]+' / '+utils.TITHI_LIST[t_no-1]
            if t_no != t_sunrise:
                tag += ' (' + res.get('kshaya_str', 'Kshaya') + ')'
            if tag_t not in tag: tag += tag_t
            special_vratha_dates.append((cur_date,starts_at,ends_at,tag))
            if panchanga_end_date is None :
                return special_vratha_dates
            cur_jd += skip_days
        cur_jd += 1
    return special_vratha_dates
def nakshathra_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None,nakshathra_index_list=None):
    res = utils.resource_strings
    _start_date = drik.Date(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day)
    if panchanga_end_date is None :
        _end_date = utils.next_panchanga_day(_start_date, 365)
    else:
        _end_date = drik.Date(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day)
    cur_date = _start_date
    cur_jd = swe.julday(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day,0.0)
    end_jd = swe.julday(_end_date.year,_end_date.month,_end_date.day,0.0)
    special_vratha_dates = []
    skip_days = 26
    if len(nakshathra_index_list) > 1:
        skip_days = 1
    while cur_jd < end_jd:
        current_nakshathra = drik.nakshatra(cur_jd, panchanga_place)
        cur_date = utils.jd_to_gregorian(cur_jd)[0:3]
        if current_nakshathra[0] in nakshathra_index_list and cur_date not in special_vratha_dates:
            starts_at = current_nakshathra[1]
            ends_at = current_nakshathra[2]
            tag = utils.NAKSHATRA_LIST[current_nakshathra[0]-1]
            special_vratha_dates.append((cur_date,starts_at,ends_at,tag))
            if ends_at < 0:
                days = int(abs(ends_at)//24)+1
                new_ends_at = abs(ends_at)%24
                new_cur_date = utils.previous_panchanga_day(drik.Date(cur_date[0],cur_date[1],cur_date[2]), minus_days=days)
                special_vratha_dates[-1]= (new_cur_date,starts_at,new_ends_at,tag)
            if panchanga_end_date is None :
                return special_vratha_dates
            cur_jd += skip_days
        cur_jd += 1
    return special_vratha_dates
def yoga_dates(panchanga_place,panchanga_start_date,panchanga_end_date=None,yoga_index_list=None,tag_y=''):
    res = utils.resource_strings
    if tag_y != '': tag_y = ' / '+ res[tag_y+'_str']
    _start_date = drik.Date(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day)
    if panchanga_end_date is None :
        _end_date = utils.next_panchanga_day(_start_date, 365)
    else:
        _end_date = drik.Date(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day)
    cur_date = _start_date
    cur_jd = swe.julday(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day,0.0)
    end_jd = swe.julday(_end_date.year,_end_date.month,_end_date.day,0.0)
    special_vratha_dates = []
    skip_days = 26
    if len(yoga_index_list) > 0:
        skip_days = 1
    while cur_jd < end_jd:
        cur_yoga = drik.yogam(cur_jd, panchanga_place)
        cur_date = utils.jd_to_gregorian(cur_jd)[0:3]
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
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions[const.SUN_ID+1:const._pp_count_upto_saturn])
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
    _start_date = drik.Date(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day)
    _end_date = drik.Date(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day)
    cur_date = _start_date
    #cur_jd = swe.julday(panchanga_start_date.year,panchanga_start_date.month,panchanga_start_date.day,0.0)
    #end_jd = swe.julday(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day,0.0)
    cur_jd = utils.julian_day_number(panchanga_start_date, (0,0,0))
    end_jd = utils.julian_day_number(panchanga_end_date, (0,0,0))
    special_vratha_dates = []
    while cur_jd < end_jd:
        cur_date = utils.jd_to_gregorian(cur_jd)[0:3] # Ignore time
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
    jd_utc = utils.gregorian_to_jd(drik.Date(yjd, mjd, djd))
    n=24; offsets = [s/n for s in range(-n,n)]
    rise = drik.sunrise(jd, place)[2]
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
    jd_utc = utils.gregorian_to_jd(drik.Date(yjd, mjd, djd))
    #jd_utc = jd - tz/24. ### It appears this way calculating jd_utc is incorrect
    n=10; offsets = [s/n for s in range(0,n)]
    rise = drik.sunrise(jd, place)[2]
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
        _panchanga_end_date = drik.Date(panchanga_end_date.year,panchanga_end_date.month,panchanga_end_date.day)
    # Search for all festivals if all panchanga indices are None
    if all(x is None for x in (tithi_index, nakshathra_index, yoga_index, tamil_month_index)):
        if _debug_print: print('search for festival from csv')
        fest_data = get_festivals_between_the_dates(panchanga_start_date, panchanga_end_date, panchanga_place,festival_name_contains=festival_name_contains)
        if len(fest_data)>0:
            for fdate,fest in fest_data:
                if _debug_print: print(fdate,fest)
                jd = utils.julian_day_number(drik.Date(fdate[0],fdate[1],fdate[2]), (fdate[3],0,0))
                sunrise_hours = drik.sunrise(jd,panchanga_place)[0]
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
                p_date1 = drik.Date(t_date[0][0],t_date[0][1],t_date[0][2])
                vratha_tag = t_date[-1]
                cur_jd = swe.julday(p_date1.year,p_date1.month,p_date1.day,0.0)
                nr = drik.nakshatra(cur_jd, panchanga_place)
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
                p_date1 = drik.Date(t_date[0][0],t_date[0][1],t_date[0][2])
                cur_jd = swe.julday(p_date1.year,p_date1.month,p_date1.day,0.0)
                #yr = yoga_dates(panchanga_place, p_date1, p_date2, [yoga_index])
                yr = drik.yogam(cur_jd, panchanga_place)
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
            panchanga_date = drik.Date(t_date[0],t_date[1],t_date[2])
            tamil_month_day = drik.tamil_solar_month_and_date(panchanga_date, panchanga_place)
            if _debug_print: print(t_date,'tamil_maadham/day',tamil_month_day,'search tamil_month',tamil_month_index)
            if tamil_month_day[0]+1 == tamil_month_index:
                #srise = drik.sunrise(utils.julian_day_number(t_date, (0,0,0)),panchanga_place)[0]
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
        _end_date = drik.Date(end_date.year,end_date.month,end_date.day)
    jd_end = swe.julday(_end_date.year,_end_date.month,_end_date.day,9.0)
    day_inc= _sankranthi_increment_days
    jd_inc = jd_start
    while jd_inc < jd_end:#-day_inc:#for i in range(12):
        p_date = utils.jd_to_gregorian(jd_inc)
        p_date = drik.Date(p_date[0],p_date[1],p_date[2])
        sd = drik.next_sankranti_date(p_date, place)
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
    jd = utils.gregorian_to_jd(drik.Date(mpds[0][0],mpds[0][1],mpds[0][2]))
    mpd = []; mpd.append(mpds)
    for d in range(1,_mahalaya_paksha_days):
        cur_tithi = drik.tithi(jd-d, panchanga_place)
        mpd.append((utils.jd_to_gregorian(jd-d),cur_tithi[1],cur_tithi[2],res['mahalaya_paksha_str']+' / '+utils.TITHI_LIST[cur_tithi[0]-1])) #V2.3.0
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
        jd = utils.gregorian_to_jd(drik.Date(c_date[0],c_date[1],c_date[2]))
        sunset = drik.sunset(jd, panchanga_place)[0]
        moonset = drik.moonset(jd, panchanga_place)[0]
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
        jd = utils.gregorian_to_jd(drik.Date(c_date[0],c_date[1],c_date[2]))
        sunset = drik.sunset(jd, panchanga_place)[0]
        moonset = drik.moonset(jd, panchanga_place)[0]
        tag = res['moondraam_pirai_str']+' / '+tag_t
        results.append((c_date,sunset,moonset,tag))
        if panchanga_end_date is None :
            return results
    return results
def _sankalpa_mantra(panchanga_date,panchanga_place,ritu_per_solar_tamil_month=None):  #V2.3.0
    """ TODO: Ritu may be INCORRECT """
    if ritu_per_solar_tamil_month is None: ritu_per_solar_tamil_month = const.ritu_per_solar_tamil_month
    vasara_list = ['bAnu','indhu','bhaumya','saumya','guru','bhrigu','sthira']
    raasi_list = ['mEsha','rishaba','mithuna','kataka','simha','kanyA','thulA','viruchiga','dhanur','makara','kumbha','meena']
    ritu_list = ['vasantha','greeshma','varsha','sharad','hEmantha','sisira']
    jd = swe.julday(panchanga_date.year,panchanga_date.month,panchanga_date.day,0.0)
    maasa_index = drik.lunar_month(jd, panchanga_place)[0]-1
    lunar_month = raasi_list[maasa_index]
    ritu = ritu_list[drik.ritu(maasa_index+1)]
    if ritu_per_solar_tamil_month:
        tamil_maasa_index,_ = drik.tamil_solar_month_and_date(panchanga_date, panchanga_place)
        ritu = ritu_list[drik.ritu(tamil_maasa_index+1)]
    samvastra = utils.YEAR_LIST[drik.samvatsara(panchanga_date, place, maasa_index, zodiac=0)-1]
    tithi_index = drik.tithi(jd, panchanga_place)[0]-1
    paksha = utils.PAKSHA_LIST[0].split()[0]
    if tithi_index > 15:
        paksha = utils.PAKSHA_LIST[1].split()[0]
    tithi = utils.TITHI_LIST[tithi_index]
    vasara = vasara_list[drik.vaara(jd,panchanga_place)]
    nakshathra = utils.NAKSHATRA_LIST[drik.nakshatra(jd, panchanga_place)[0]-1]
    """ TODO Solstice calculation not right - find shortest and logest days of year """
    solistice="dakshiNAyanE "
    if maasa_index < 3 or maasa_index > 8:
        solistice="uttharAyanE "
    mantra_str = "{0} nAma samvathsarE, {1} {7} rithou, {2} mAsE, {3} pakshE, "+ \
                            "{4} puNyathithou, {5} vAsara, {6} nakshatra yukthAyAm, asyAm "+ \
                            "amAvAsyAyAm  puNyakAlE darsa srardham thila tharppaNa roopENa adhya karishyE"
    return mantra_str.format(samvastra,solistice,lunar_month,paksha,tithi,vasara,nakshathra,ritu)
def tithi_pravesha(birth_date:drik.Date=None,birth_time:tuple=None,birth_place:drik.Place=None,year_number=None, plus_or_minus_duration_in_days=30):
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
    current_date_start = drik.Date(year_number,cds[1],cds[2])
    current_date_start = utils.previous_panchanga_day(current_date_start, plus_or_minus_duration_in_days)
    current_date_end = utils.next_panchanga_day(current_date_start, 2*plus_or_minus_duration_in_days)
    #print(current_date_start,current_date_end)
    jd = utils.julian_day_number(birth_date, birth_time); _,_,_,birth_time_hrs = utils.jd_to_gregorian(jd)
    t = drik.tithi(jd, birth_place); tm = drik.tamil_solar_month_and_date(birth_date, birth_place)
    t_frac = utils.get_fraction(t[1], t[2], birth_time_hrs)
    #print('tithi',(t[0],utils.to_dms(t[1]),utils.to_dms(t[2]),t_frac),'tamil month/day',tm)
    # V5.0.4 Tithi pravesha is an instant, not a sunrise-based vratha day, so it does not use tithi_dates()/search().
    #   Same as V5.0.2 (verified against Jagannatha Hora): sample tithi daily at (first day's sunrise + 0.5h), match the
    #   tithi at that time or the next tithi of that day, then filter by the birth tamil month.
    _sr_hours = drik.sunrise(utils.julian_day_number(current_date_start, (6.5,0,0)), birth_place)[0] + 0.5
    cur_jd = swe.julday(current_date_start.year, current_date_start.month, current_date_start.day, _sr_hours)
    end_jd = swe.julday(current_date_end.year, current_date_end.month, current_date_end.day, _sr_hours)
    sr = []
    while cur_jd < end_jd:
        ct = drik.tithi(cur_jd, birth_place)
        if ct[0] == t[0]:                       _match = (ct[1], ct[2])
        elif len(ct) > 3 and ct[3] == t[0]:     _match = (ct[4], ct[5])
        else:                                   _match = None
        if _match is not None:
            s_date = utils.jd_to_gregorian(cur_jd)[0:3]
            if drik.tamil_solar_month_and_date(drik.Date(*s_date), birth_place)[0] == tm[0]:
                paksha = 0 if t[0] <= 15 else 1
                tag = utils.PAKSHA_LIST[paksha]+' / '+utils.TITHI_LIST[t[0]-1]+' / '+utils.MONTH_LIST[tm[0]]
                sr.append((s_date, _match[0], _match[1], tag))
            cur_jd += 14                        # skip past this tithi (avoids a vriddhi duplicate)
        cur_jd += 1
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
def load_festival_data(file_path=None):
    file_path = const._FESTIVAL_FILE if file_path is None else file_path
    global festival_data
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        festival_data = [row for row in reader]
def _get_day_values(jd,place):
    """Returns the part of a day's festival criteria that does not depend on the calendar type.
    Args:
        jd: Julian day number.
        place: drik.Place of the location.
    Returns:
        (tithis, nakshatra ids, weekday id) - the tithi and nakshatra lists hold two entries when the
        day has two of them.
    """
    # Tithi of the day = tithi at SUNRISE, plus any kshaya (lost) tithi falling before the next sunrise (it has
    # no day of its own). A tithi that merely starts later in the day belongs to the next day, so its festival
    # is no longer shown on two consecutive days.
    _t_sunrise, _kshaya, _ = _sunrise_tithis_of_the_day(jd, place)
    _tithis = [_t_sunrise] + _kshaya
    _naks = drik.nakshatra(jd, place)
    _nak_ids = [_naks[0],_naks[4]] if len(_naks)>4 else [_naks[0]]
    day_id = drik.vaara(jd,place)
    return _tithis, _nak_ids, day_id
def _get_criteria_for_the_day(jd,place,calendar_type=None,day_values=None):
    """Returns the festival matching criteria of one day for one calendar type.
    Args:
        jd: Julian day number.
        place: drik.Place of the location.
        calendar_type: const.CALENDAR_TYPE member (default SOLAR).
        day_values: result of _get_day_values(jd, place) when the caller already has it; computed if None.
    Returns:
        dict with keys Tithi, Nakshatra, month, day, weekday, adhik_maasa and calendar_type.
    """
    if calendar_type is None: calendar_type = const.CALENDAR_TYPE.SOLAR
    y,m,d,_ = utils.jd_to_gregorian(jd); date_in = drik.Date(y,m,d)
    _tithis, _nak_ids, day_id = day_values if day_values is not None else _get_day_values(jd, place)
    tm,td,_,adhik_maasa,_,_ = drik.vedic_date(jd, place, calendar_type=calendar_type)
    if calendar_type == const.CALENDAR_TYPE.GREGORIAN:
        _,tm,td,_ = utils.jd_to_gregorian(jd)
    criteria = {
        'Tithi': _tithis,
        'Nakshatra': _nak_ids,
        'month': tm,
        'day': td,
        'weekday':day_id+1,
        'adhik_maasa':adhik_maasa,
        'calendar_type': calendar_type
    }
    return criteria
def get_festivals_between_the_dates(start_date:drik.Date, end_date:drik.Date, place:drik.Place,
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
    """Returns the festival rows of the festival file that match the given day.
    Args:
        jd: Julian day number.
        place: drik.Place of the location.
        festival_name_contains: if given, only festivals whose English name contains this text (any case).
    Returns:
        list of festival rows (dicts).
    """
    global festival_data
    if len(festival_data) == 0: load_festival_data(const._FESTIVAL_FILE)
    matching_festivals = []
    _include_islamic = const.include_islamic_calendar and utils.astro_engine_is_drik()
    # Calendars with NO festival data rows at all -- unconditionally skipped.
    # (Nanakshahi/Bangladesh-reformed are fixed-arithmetic civil calendars added
    # purely for date-conversion; festival_data has no entries keyed to either.)
    _no_festival_data_calendars = (const.CALENDAR_TYPE.NANAKSHAHI_PUNJAB,
                                    const.CALENDAR_TYPE.BANGLADESH_REFORMED)
    calendar_types = list(const.CALENDAR_TYPE)
    day_values_by_offset = {}                    # per day offset: the same for every calendar type, computed once
    criteria_by_index = {}                       # criteria of (calendar type, day offset): computed when a row needs it
    check_rows = festival_data if festival_name_contains is None \
        else [row for row in festival_data if festival_name_contains.casefold() in row['Festival_en'].casefold()]
    for row in check_rows:#festival_data:
        index = int(row['calendar_type'])
        # V5.0.4 optional CSV column 'day_offset': the row's criteria describe a reference day and the festival falls
        #   day_offset civil days from it (e.g. -20 = 20 days before; 21-day vratham ending on Diwali). Blank/missing = 0.
        try:
            _offset = int(float(row.get('day_offset') or 0))
        except ValueError:
            _offset = 0
        _key = (index, _offset)
        if _key not in criteria_by_index:
            c = calendar_types[index]
            if c in _no_festival_data_calendars or (c == const.CALENDAR_TYPE.HIJRI_ISLAMIC and not _include_islamic):
                criteria_by_index[_key] = None
            else:
                _ref_jd = jd - _offset
                if _offset not in day_values_by_offset:
                    day_values_by_offset[_offset] = _get_day_values(_ref_jd, place)
                try:
                    criteria_by_index[_key] = _get_criteria_for_the_day(_ref_jd, place, calendar_type=c,
                                                                        day_values=day_values_by_offset[_offset])
                except ValueError:
                    # e.g. Hijri's underlying conversion library cannot represent a BCE (or
                    # otherwise out-of-range) Gregorian year - confirmed from an actual crash,
                    # "ValueError: year -3102 is out of range" - skip just THIS ONE calendar type
                    # for THIS ONE day (same outcome as _no_festival_data_calendars above), rather
                    # than letting the whole call crash. Cached in criteria_by_index like every
                    # other outcome, so this is only attempted once per (day, calendar_type) rather
                    # than re-raising for every remaining row of the same calendar_type.
                    criteria_by_index[_key] = None
        criteria = criteria_by_index[_key]
        if criteria is None: continue
        match = True
        for key, value in criteria.items():
            if row.get(key):
                try:
                    # Convert both to float for comparison (handles empty strings gracefully)
                    if isinstance(value,list):
                        match = match and any([float(row[key]) ==float(v) for v in value])# == float(value)
                    else:
                        match = match and float(row[key]) == float(value)
                    #print(key,value,row['month'],row['day'],row['weekday'],row['calendar_type'],match,row['Festival_en'])
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
        'month': tamil_month,
        'day': tamil_day,
        'weekday':vaara,
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
    from datetime import datetime
    _,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    hh,mm,ss = current_time_str.split(":")
    dob = drik.Date(2026,8,28); tob = (int(hh),int(mm),int(ss)); place = drik.Place('Inverness,IL,USA',42.113275,-88.098433,-5.0)
    jd = utils.julian_day_number(dob,tob)
    _festival_file = const._DATA_DIR +const._sep+'hindu_festivals_multilingual_unicode_bom.csv'
    load_festival_data(_festival_file)
    print(get_festivals_of_the_day(jd,place))
    exit()

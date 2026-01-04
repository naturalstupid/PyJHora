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

"""
Calculates Ashtottari (=108) Dasha-bhukthi-antara-sukshma-prana
"""

from collections import OrderedDict as Dict
from jhora import const,utils
from jhora.panchanga import drik
from jhora.horoscope.chart import house
year_duration = const.sidereal_year# const.tropical_year  # some say 360 days, others 365.25 or 365.2563 etc
human_life_span_for_ashtottari_dhasa = 108
""" 
    {ashtottari adhipati:[(starting_star_number,ending_star_number),dasa_length]} 
        ashtottari longitude range: (starting_star_number-1) * 360/27 TO (ending_star_number) * 360/27
        Example: 66.67 to 120.00 = 53 deg 20 min range
"""
ashtottari_adhipathi_list = [0,1,2,3,6,4,7,5]
ashtottari_adhipathi_dict_seed = {0:[(6,9),6],1:[(10,12),15],2:[(13,16),8],3:[(17,19),17],
                             6:[(20,22),10],4:[(23,25),19],7:[(26,2),12],5:[(3,5),21]}
def applicability_check(planet_positions):
    asc_house = planet_positions[0][1][0]
    lagna_lord = house.house_owner_from_planet_positions(planet_positions, asc_house)
    house_of_lagna_lord = planet_positions[lagna_lord+1][1][0]
    rahu_house = planet_positions[8][1][0]
    chk1 =  rahu_house in house.trines_of_the_raasi(house_of_lagna_lord) and rahu_house != asc_house
    chk2 =  rahu_house in house.quadrants_of_the_raasi(house_of_lagna_lord) and rahu_house != asc_house 
    return chk1 or chk2
def _get_dhasa_dict(seed_star=6):
    if seed_star==6: return ashtottari_adhipathi_dict_seed
    ashtottari_adhipathi_dict = {}
    nak = seed_star
    for p,[(nb,ne),durn] in ashtottari_adhipathi_dict_seed.items():
        nak_diff = ne-nb
        nsb = nak; nse = (nsb + nak_diff)%28
        ashtottari_adhipathi_dict[p] = [(nsb,nse),durn]
        nak = (nse+1)%28
    return ashtottari_adhipathi_dict
def ashtottari_adhipathi(nak):
    for key,value in ashtottari_adhipathi_dict.items():
        starting_star = value[0][0]
        ending_star = value[0][1]
        nak1 = nak
        if ending_star < starting_star:# and nak < starting_star:
            ending_star += 27
            if nak1 < starting_star:
                nak1 += 27
        if nak1 >= starting_star and nak1 <= ending_star:
            return key,value
def ashtottari_dasha_start_date(jd,place,divisional_chart_factor=1,chart_method=1,star_position_from_moon=1,
                                dhasa_starting_planet=1):
    y,m,d,fh = utils.jd_to_gregorian(jd); dob=drik.Date(y,m,d); tob=(fh,0,0)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    from jhora.horoscope.chart import charts,sphuta
    _special_planets = ['M','G','T','I','B','I','P']
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,
                                               chart_method=chart_method)
    if dhasa_starting_planet in [*range(9)]:
        planet_long = planet_positions[dhasa_starting_planet+1][1][0]*30+planet_positions[dhasa_starting_planet+1][1][1]
    elif dhasa_starting_planet==const._ascendant_symbol:
        planet_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    elif dhasa_starting_planet.upper()=='M':
        mn = drik.maandi_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
        planet_long = mn[0]*30+mn[1]
    elif dhasa_starting_planet.upper()=='G':
        gl = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='B':
        gl = drik.bhrigu_bindhu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='I':
        gl = drik.indu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='P':
        gl = drik.pranapada_lagna(jd, place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='T':
        sp = sphuta.tri_sphuta(dob,tob,place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = sp[0]*30+sp[1]
    else:
        planet_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    if dhasa_starting_planet==1:
        planet_long += (star_position_from_moon-1)*one_star
    nak = int(planet_long / one_star)
    lord,res = ashtottari_adhipathi(nak+1)          # ruler of current nakshatra
    period = res[1]; start_nak = res[0][0]; end_nak = res[0][1]
    period_elapsed = ( planet_long - (start_nak-1)*one_star)/((end_nak-start_nak+1)*one_star)
    period_elapsed *= (period*year_duration)        # days
    start_date = jd - period_elapsed      # so many days before current day
    return [lord, start_date]
def ashtottari_next_adhipati(lord,dirn=1):
    """Returns next lord after `lord` in the adhipati_list"""
    current = ashtottari_adhipathi_list.index(lord)
    #print(current)
    next_index = (current + dirn) % len(ashtottari_adhipathi_list)
    #print(next_index)
    return ashtottari_adhipathi_list[next_index]
def ashtottari_mahadasa(jd,place,divisional_chart_factor=1,chart_method=1,star_position_from_moon=1,
                        dhasa_starting_planet=1):
    """
        returns a dictionary of all mahadashas and their start dates
        @return {mahadhasa_lord_index, (starting_year,starting_month,starting_day,starting_time_in_hours)}
    """
    lord, start_date = ashtottari_dasha_start_date(jd,place,divisional_chart_factor=divisional_chart_factor,
                                chart_method=chart_method,star_position_from_moon=star_position_from_moon,
                                dhasa_starting_planet=dhasa_starting_planet)
    retval = Dict()
    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        start_date += lord_duration * year_duration
        lord = ashtottari_next_adhipati(lord)
    return retval
def ashtottari_bhukthi(dhasa_lord, start_date,antardhasa_option=1):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa and its start date
    """
    lord = dhasa_lord
    if antardhasa_option in [3,4]:
        lord = ashtottari_next_adhipati(dhasa_lord, dirn=1) 
    elif antardhasa_option in [5,6]:
        lord = ashtottari_next_adhipati(dhasa_lord, dirn=-1) 
    dirn = 1 if antardhasa_option in [1,3,5] else -1
    retval = Dict()
    #lord = dhasa_lord if const.ashtottari_bhukthi_starts_from_dhasa_lord else ashtottari_next_adhipati(dhasa_lord)
    dhasa_lord_duration = ashtottari_adhipathi_dict[lord][1]
    for _ in range(len(ashtottari_adhipathi_list)):
        retval[lord] = start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        start_date += factor * year_duration
        lord = ashtottari_next_adhipati(lord,dirn)
    return retval
def ashtottari_anthara(dhasa_lord, bhukthi_lord,bhukthi_lord_start_date):
    """
        Compute all bhukthis of given nakshatra-lord of Mahadasa, its bhukthi lord and bhukthi_lord's start date
    """
    dhasa_lord_duration = ashtottari_adhipathi_dict[dhasa_lord][1]
    retval = Dict()
    lord = bhukthi_lord# if const.ashtottari_bhukthi_starts_from_dhasa_lord else ashtottari_next_adhipati(bhukthi_lord)
    for i in range(len(ashtottari_adhipathi_list)):
        retval[lord] = bhukthi_lord_start_date
        lord_duration = ashtottari_adhipathi_dict[lord][1]
        factor = lord_duration * dhasa_lord_duration / human_life_span_for_ashtottari_dhasa
        bhukthi_lord_start_date += factor * year_duration
        lord = ashtottari_next_adhipati(lord)
    return retval
def get_ashtottari_dhasa_bhukthi(jd, place,divisional_chart_factor=1,chart_method=1,star_position_from_moon=1,
                                 use_tribhagi_variation=False,include_antardhasa=True,
                                 antardhasa_option=1,dhasa_starting_planet=1,seed_star=6):
    """
        provides Ashtottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param chart_method: Default 1; various methods available for each divisional chart. See charts module
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @param seed_star 1..27. Default = 6
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    global human_life_span_for_ashtottari_dhasa, ashtottari_adhipathi_dict
    ashtottari_adhipathi_dict = _get_dhasa_dict(seed_star)
    _dhasa_cycles = 1
    _tribhagi_factor = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.
        _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
        human_life_span_for_ashtottari_dhasa *= _tribhagi_factor
        for k,(v1,v2) in ashtottari_adhipathi_dict.items():
            ashtottari_adhipathi_dict[k] = [v1,v2*_tribhagi_factor]#[v1,round(v2*_tribhagi_factor,2)]
    dashas = ashtottari_mahadasa(jd,place,divisional_chart_factor=divisional_chart_factor,
                                 star_position_from_moon=star_position_from_moon,
                                 dhasa_starting_planet=dhasa_starting_planet)
    dhasa_bhukthi=[]
    for _ in range(_dhasa_cycles):
        for i in dashas:
            dhasa_lord = i
            if include_antardhasa:
                bhukthis = ashtottari_bhukthi(i, dashas[i],antardhasa_option)
                for j in bhukthis:
                    bhukthi_lord = j
                    jd1 = bhukthis[j]
                    y, m, d, h = utils.jd_to_gregorian(jd1)
                    """ TODO: Need to figure out passing date and time string to UI, main.py and pvr_tests.py """
                    date_str = '%04d-%02d-%02d' %(y,m,d)+' '+utils.to_dms(h,as_string=True)
                    dhasa_bhukthi.append([dhasa_lord,bhukthi_lord,date_str]) 
            else:
                jd1 = dashas[i]
                y, m, d, h = utils.jd_to_gregorian(jd1)
                """ TODO: Need to figure out passing date and time string to UI, main.py and pvr_tests.py """
                date_str = '%04d-%02d-%02d' %(y,m,d)+' '+utils.to_dms(h,as_string=True)
                dhasa_bhukthi.append([dhasa_lord,date_str])                 
    return dhasa_bhukthi
'------ main -----------'
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.ashtottari_tests()
    
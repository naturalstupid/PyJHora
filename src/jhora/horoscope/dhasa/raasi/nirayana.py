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
""" Called Nirayana or Nirayana Shoola Dhasa """
from jhora import const, utils
from jhora.horoscope.chart import house,charts
def nirayana_shoola_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,include_antardhasa=True):
    jd = utils.julian_day_number(dob,tob)
    planet_positions = charts.divisional_chart(jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    return nirayana_shoola_dhasa(planet_positions,dob,tob,include_antardhasa)
def nirayana_shoola_dhasa(planet_positions,dob,tob,include_antardhasa=True):
    """
        calculate Nirayana Shoola Dhasa
        @param chart: house_to_planet_list
          Example: ['','','','','2','7','1/5','0','3/4','L','','6/8'] 1st element is Aries and last is Pisces
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
    chart = utils.get_house_planet_list_from_planet_positions(planet_positions)
    h_to_p = chart[:]
    #print(h_to_p)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)    
    #print(p_to_h)
    asc_house = p_to_h[const._ascendant_symbol]
    #print('asc_house',asc_house)
    second_house = (asc_house+2-1)%12 # 2nd house
    eighth_house = (asc_house+8-1)%12 # 8th house
    dhasa_seed_sign = house.stronger_rasi_from_planet_positions(planet_positions, second_house,eighth_house)
    #dhasa_seed_sign = house.stronger_rasi(h_to_p,second_house,eighth_house)
    #if dhasa_seed_sign != asc_house:
    #    dhasa_seed_sign = (dhasa_seed_sign+asc_house - 1)%12
    #print('dhasa_seed_sign',dhasa_seed_sign)
    direction = 1
    if dhasa_seed_sign in const.even_signs:
        direction = -1
    dhasa_progression = [(dhasa_seed_sign+direction*k)%12 for k in range(12)]
    dhasa_info = []
    start_jd = utils.julian_day_number(dob, tob)
    for dhasa_lord in dhasa_progression:
        dhasa_duration = 7 # movable sign
        if dhasa_lord in const.fixed_signs:
            dhasa_duration = 8
        elif dhasa_lord in const.dual_signs:
            dhasa_duration = 9
        if include_antardhasa:
            bhukthis = _antardhasa(dhasa_lord,p_to_h)
            dd = dhasa_duration/12
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                start_jd += dd * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,dhasa_duration))
            start_jd += dhasa_duration * const.sidereal_year
    # Second cycle
    dhasa_start = start_jd
    total_dhasa_duration = sum([row[-1] for row in dhasa_info ])
    for c,dhasa_lord in enumerate(dhasa_progression):
        dhasa_duration = 12 - dhasa_info[c][-1]
        dhasa_duration = round(dhasa_duration,2)
        total_dhasa_duration += dhasa_duration
        if dhasa_duration <=0: # no need for second cycle as first cycle had 12 years
            continue
        if include_antardhasa:
            bhukthis = _antardhasa(dhasa_lord,p_to_h)
            dd = dhasa_duration/12
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                start_jd += dd * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,dhasa_duration))
            start_jd += dhasa_duration * const.sidereal_year
        if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
            break
    return dhasa_info
def _antardhasa(antardhasa_seed_rasi,p_to_h):
    direction = -1
    if p_to_h[6]==antardhasa_seed_rasi or antardhasa_seed_rasi in const.odd_signs: # Forward
        direction = 1
    if p_to_h[8]==antardhasa_seed_rasi:
        direction *= -1
    return [(antardhasa_seed_rasi+direction*i)%12 for i in range(12)]
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests.nirayana_shoola_dhasa_tests()
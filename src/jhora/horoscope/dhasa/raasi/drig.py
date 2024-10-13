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
""" Computes Drig Dhasa from the chart """
from jhora import const,utils
from jhora.horoscope.chart import house,charts
from jhora.horoscope.dhasa.raasi import narayana
def drig_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,include_antardhasa=True):
    jd = utils.julian_day_number(dob,tob)
    planet_positions = charts.divisional_chart(jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, divisional_chart_factor=divisional_chart_factor)
    return drig_dhasa(planet_positions, dob,tob,include_antardhasa=include_antardhasa)
def drig_dhasa(planet_positions,dob,tob,include_antardhasa=True):
    """
        computes drig dhasa from the chart
        @param chart: chart list 1-D. Format ['1/2','3/L',...,'',5/6/7','9','0'] # 12 houses with planets and Lagnam
        @param dob: tuple of date of birth format: (year,month,day)
        @return: list of drig dhasa from date of birth 
          Format: [ [dhasa_lord, dhasa_start_date, dhasa_end_date, [bhukthi_lord1, bhukthi_lord2...], dhasa_duration],...]
          Example: [[2, '1912-1-1', '1916-1-1', [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1], 4], 
                    [5, '1916-1-1', '1927-1-1', [5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7, 6], 11], ...]]
    """
    start_jd = utils.julian_day_number(dob, tob)
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)  
    asc_house = p_to_h[const._ascendant_symbol]
    ninth_house = (asc_house+9-1)%12
    dhasa_progression= []
    for s in range(ninth_house,(ninth_house+3)):
        s %= 12
        aspected_kendras = house.aspected_kendras_of_raasi(s,s in const.even_footed_signs)
        dp = [s]+ aspected_kendras
        #print(s,dp)
        dhasa_progression.append(dp)
    dhasa_progression = sum(dhasa_progression,[])
    dhasa_info = []
    for dhasa_lord in dhasa_progression:
        dhasa_duration = round(narayana._dhasa_duration(planet_positions,dhasa_lord),2)
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
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.drig_dhasa_tests()

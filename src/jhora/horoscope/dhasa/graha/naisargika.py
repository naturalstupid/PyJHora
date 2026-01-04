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
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, house
_bhukthi_house_list = [0,3,6,9,1,4,7,10,2,5,8,11]
_bhukthi_exempt_list_1 = [2,9]
_bhukthi_exempt_list_2 = [1,5,10,11] 
dhasa_adhipathi_dict = {1:1,2:2,3:9,5:20,4:18,0:20,6:50,'L':12} 
def get_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,chart_method=1,years=1,months=1,sixty_hours=1,
                      include_antardhasa=True,mahadhasa_lord_has_no_antardhasa=True,
                      antardhasa_option1=False,antardhasa_option2=False):
    """
        provides Naisargika dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param chart_method: Default=1, various chart methods available for each div chart. See charts module
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param mahadhasa_lord_has_no_antardhasa=True => Mahadhasa lord has no antardhasa. Default=True
        @param antardhasa_option1=True => Planets in 3rd and 10th from dasa lord have no antardhasa. Default=False
        @param antardhasa_option2=True => Planets in 2nd,6th,11th and 12th from dasa lord have no antardhasa. Default=False
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    bhukthi_house_list = _bhukthi_house_list
    if antardhasa_option1:
        bhukthi_house_list = [p for p in bhukthi_house_list if p not in _bhukthi_exempt_list_1]
    if antardhasa_option2:
        bhukthi_house_list = [p for p in bhukthi_house_list if p not in _bhukthi_exempt_list_2]
    start_jd = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(start_jd, place, divisional_chart_factor=divisional_chart_factor, 
                                               chart_method=chart_method,years=years, months=months, 
                                               sixty_hours=sixty_hours)[:8]# Ignore Rahu onwards
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    dhasa_lords = list(dhasa_adhipathi_dict.keys())
    dhasa_info = []
    for dhasa_lord in dhasa_lords:
        duration = dhasa_adhipathi_dict[dhasa_lord]
        lord_house = planet_positions[dhasa_lord+1][1][0] if dhasa_lord != const._ascendant_symbol else planet_positions[0][1][0] 
        bhukthis = [h_to_p[(h+lord_house)%12].split('/') for h in bhukthi_house_list if h_to_p[(h+lord_house)%12] != '']
        bhukthis = utils.flatten_list(bhukthis)
        [bhukthis.remove(p) for p in ['L','7','8'] if p in bhukthis]
        if mahadhasa_lord_has_no_antardhasa and dhasa_lord != const._ascendant_symbol and str(dhasa_lord) in bhukthis:
            bhukthis.remove(str(dhasa_lord))   
        bhukthis = list(map(int,bhukthis))
        if include_antardhasa:
            """ 
                TODO: Antardasa period should be based on weights per planets' placement 
                See: https://srath.com/jyoti%E1%B9%A3a/dasa/naisargika-dasha/ for details
            """
            dd = round(duration/len(bhukthis),2)
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                start_jd += dd * const.sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,duration))
            start_jd += duration * const.sidereal_year
    return dhasa_info
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.naisargika_test()
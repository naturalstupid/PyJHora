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

""" Tara Dasa - applicable if all the four quadrants are occupied """
"""
    TODO: To implement following options for sanjay rath method:
        1. No dhasa sesham OR 2. Dasa sesham from moon as per vimsottari 
        OR 3. Dhasa sesham from moon but in reverse for apasavya nakshatras
"""

from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, house

dhasa_adhipathi_dict_sanjay_rath = {5:20,1:10,8:7,6:19,4:16,3:17,7:18,2:7,0:6}
dhasa_adhipathi_dict_parasara = {5:20,0:6,1:10,2:7,7:18,4:16,6:19,3:17,8:7}
human_life_span = sum(dhasa_adhipathi_dict_parasara.values())
year_duration = const.sidereal_year

def _next_adhipati(lord,dirn=1,dhasa_method=1):
    dhasa_adhipathi_dict = dhasa_adhipathi_dict_sanjay_rath if dhasa_method==1 else dhasa_adhipathi_dict_parasara
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_dict.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_dict.keys())[((current + dirn) % len(dhasa_adhipathi_dict))]
    return next_lord
def _antardhasa(lord,dhasa_method=1):
    dhasa_adhipathi_dict = dhasa_adhipathi_dict_sanjay_rath if dhasa_method==1 else dhasa_adhipathi_dict_parasara
    _bhukthis = []
    for _ in range(len(dhasa_adhipathi_dict)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord,dhasa_method=dhasa_method)
    return _bhukthis
def _dhasa_start(jd,place,period,star_position_from_moon=1,divisional_chart_factor=1,chart_method=1):
    one_star = (360 / 27.)
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,
                                               chart_method=chart_method)
    moon = planet_positions[2][1][0]*30+planet_positions[2][1][1]+(star_position_from_moon-1)*one_star
    nak = int(moon / one_star); rem = (moon - nak * one_star)
    period_elapsed = rem / one_star * period # years
    period_elapsed *= year_duration        # days
    start_date = jd - period_elapsed      # so many days before current day
    return start_date
        
def get_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,chart_method=1,years=1,months=1,sixty_hours=1,
                      include_antardasa=True,dhasa_method=1):
    """
        provides Tara dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param chart_method: Default=1, various chart methods available for each div chart. See charts module
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True
        @param dhasa_method: 
            1=>Sanjay Rath method dhasa order 5,1,8,6,4,3,7,2,0  (Default)
            2=>Parasara method dhasa order 5,0,1,2,7,4,6,3,8
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
    dhasa_adhipathi_dict = dhasa_adhipathi_dict_sanjay_rath if dhasa_method==1 else dhasa_adhipathi_dict_parasara
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                            divisional_chart_factor=divisional_chart_factor, chart_method=chart_method,
                            years=years,months=months, sixty_hours=sixty_hours)[:const._pp_count_upto_ketu] # Exclude Western Planets
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    asc_house = planet_positions[0][1][0]
    ds = sorted([h_to_p[(h+asc_house)%12].split('/') for h in [0,3,6,9] if h_to_p[(h+asc_house)%12] != ''],key=len,reverse=True)
    ds = utils.flatten_list(ds)
    """ TODO If ds is empty list - what to do? """
    if len(ds)==0:
        print('tara dhasa ds list is empty, returning empty list')
        return []
    if 'L' in ds:
        ds.remove('L')
    if len(ds)==0:
        print('tara dhasa ds list is empty, returning empty list')
        return []
    if len(ds) >= 2:
        ds1 = ds; sp = int(ds1[0])
        for p in range(1,len(ds1)):
            sp = house.stronger_planet_from_planet_positions(planet_positions, int(ds1[p]), int(sp))
        dhasa_lord = sp
    else:#if len(ds)==1:
        dhasa_lord = int(ds[0])#int(ds[0][0])
    _dhasa_duration = dhasa_adhipathi_dict[dhasa_lord]
    start_jd = _dhasa_start(jd_at_dob,place, _dhasa_duration, star_position_from_moon=1,
                            divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
    dhasa_info = []
    for _ in range(len(dhasa_adhipathi_dict)):
        _dhasa_lord_duration = dhasa_adhipathi_dict[dhasa_lord]
        bhukthis = _antardhasa(dhasa_lord,dhasa_method=dhasa_method)
        if include_antardasa:
            for bhukthi_lord in bhukthis:
                _bhukthi_duration = dhasa_adhipathi_dict[bhukthi_lord]
                factor = _bhukthi_duration *  _dhasa_lord_duration / human_life_span
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,_dhasa_duration))
                start_jd += factor * year_duration
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,_dhasa_duration))
            lord_duration = dhasa_adhipathi_dict[dhasa_lord]
            start_jd += lord_duration * year_duration
        dhasa_lord = _next_adhipati(dhasa_lord,dhasa_method=dhasa_method)
        _dhasa_duration = dhasa_adhipathi_dict[dhasa_lord]
    return dhasa_info
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.tara_dhasa_test()
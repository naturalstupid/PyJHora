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

dhasa_adhipathi_dict = {5:20,1:10,8:7,6:19,4:16,3:17,7:18,2:7,0:6}
human_life_span = sum(dhasa_adhipathi_dict.values())
year_duration = const.sidereal_year

def _next_adhipati(lord):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_dict.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_dict.keys())[((current + 1) % len(dhasa_adhipathi_dict))]
    return next_lord
def _antardhasa(lord):
    _bhukthis = []
    for _ in range(len(dhasa_adhipathi_dict)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord)
    return _bhukthis
def _dhasa_start(jd,place,period,star_position_from_moon=1,divisional_chart_factor=1):
    from jhora.horoscope.chart import charts
    one_star = (360 / 27.)
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)
    moon = planet_positions[2][1][0]*30+planet_positions[2][1][1]+(star_position_from_moon-1)*one_star
    nak = int(moon / one_star); rem = (moon - nak * one_star)
    period_elapsed = rem / one_star * period # years
    period_elapsed *= year_duration        # days
    start_date = jd - period_elapsed      # so many days before current day
    return start_date
        
def get_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardasa=True):
    """
        provides Tara dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                                               divisional_chart_factor=divisional_chart_factor, years=years, 
                                               months=months, sixty_hours=sixty_hours)[:const._upto_ketu] # Exclude Western Planets
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
    start_jd = _dhasa_start(jd_at_dob,place, _dhasa_duration, star_position_from_moon=1,divisional_chart_factor=divisional_chart_factor)
    dhasa_info = []
    for _ in range(len(dhasa_adhipathi_dict)):
        _dhasa_lord_duration = dhasa_adhipathi_dict[dhasa_lord]
        bhukthis = _antardhasa(dhasa_lord)
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
        dhasa_lord = _next_adhipati(dhasa_lord)
        _dhasa_duration = dhasa_adhipathi_dict[dhasa_lord]
    return dhasa_info
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.tara_dhasa_test()
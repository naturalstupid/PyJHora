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

year_duration = const.sidereal_year

def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,chart_method=1,years=1,months=1,
                         sixty_hours=1,include_antardhasa=True):
    """
        provides karaka dhasa bhukthi for a given date in julian day (includes birth time)
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
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                                               divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                               years=years,months=months, sixty_hours=sixty_hours)
    karakas = house.chara_karakas(planet_positions)
    asc_house = planet_positions[0][1][0]
    dhasa_info = []
    start_jd = jd_at_dob
    human_life_span = sum([(planet_positions[k+1][1][0] - asc_house +12)%12 for k in karakas])
    kl = len(karakas)
    for ki,k in enumerate(karakas):
        k_h = planet_positions[k+1][1][0]
        duration = (k_h - asc_house + 12)%12
        bhukthis = karakas[ki+1:kl]+karakas[0:ki+1]
        if include_antardhasa:
            for bhukthi_lord in bhukthis:
                b_h = planet_positions[bhukthi_lord+1][1][0]
                dd = (b_h - asc_house + 12)%12
                factor = dd *  duration / human_life_span
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((k,bhukthi_lord,dhasa_start,dd))
                start_jd += factor * year_duration
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((k,dhasa_start,duration))
            start_jd += duration * year_duration
    return dhasa_info
        

if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests.karaka_dhasa_test()

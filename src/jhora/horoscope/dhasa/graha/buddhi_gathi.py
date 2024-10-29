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
from jhora import utils, const
from jhora.horoscope.chart import charts
from jhora.panchanga import drik
def get_dhasa_bhukthi(dob,tob,place,divisional_chart_factor=1,chart_method=1,years=1,months=1,sixty_hours=1,
                      include_antardhasa=True):
    """
        provides Buddhi Gathi dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param chart_method: default=1; various methods available for each div chart. see charts module. 
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
    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions[1:])
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    planet_dict = {int(p):p_long for p,(_,p_long) in planet_positions[1:]}
    asc_house = p_to_h[const._ascendant_symbol]
    dhasa_progression = []
    h1 = 0
    start_jd = jd_at_dob
    for h in range(12):
        hs = (asc_house+3+h)%12
        # Get planets from the house
        if h_to_p[hs] == '': continue
        planets = list(map(int,h_to_p[hs].split('/')))
        d1 = {p:l for p,l in planet_dict.items() if p in planets}
        pl_new = [p for (p,_) in sorted(d1.items(), key=lambda item:item[1],reverse=True)]
        for pl in pl_new:
            durn = ((asc_house+h1+12) - p_to_h[pl])%12
            dhasa_progression.append((pl,durn))
            h1 += 1
    dhasa_bhukthi_info = []; dhasa_len = len(dhasa_progression); total_dhasa_duration = 0
    for dhasa_cycle in range(2):
        for dhasa in range(dhasa_len):
            dhasa_lord,dhasa_duration = dhasa_progression[dhasa]
            total_dhasa_duration += dhasa_duration
            if include_antardhasa:
                bhukthi_duration = dhasa_duration/dhasa_len
                for bhukthi in range(dhasa_len):
                    y,m,d,h = utils.jd_to_gregorian(start_jd)
                    dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                    bhukthi_lord = dhasa_progression[(dhasa+bhukthi)%dhasa_len][0]
                    dhasa_bhukthi_info.append((dhasa_lord,bhukthi_lord,dhasa_start,round(bhukthi_duration,2)))
                    start_jd += bhukthi_duration*const.sidereal_year
            else:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_bhukthi_info.append((dhasa_lord,dhasa_start,dhasa_duration))
                start_jd += dhasa_duration*const.sidereal_year
            if total_dhasa_duration >= const.human_life_span_for_narayana_dhasa:
                break
    return dhasa_bhukthi_info
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.buddhi_gathi_test()
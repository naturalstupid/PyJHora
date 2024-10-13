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

def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True):
    start_jd = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(start_jd, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                                               divisional_chart_factor=divisional_chart_factor, years=years, 
                                               months=months, sixty_hours=sixty_hours)
    asc_house = planet_positions[0][1][0]
    moon_longitude = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    one_star = 360 / 27
    nak_frac = one_star / 12.0
    nak,_,_ = drik.nakshatra_pada(moon_longitude)
    #print('moon_longitude',moon_longitude,nak,'nak_frac',nak_frac,(nak-1)*one_star,(moon_longitude - nak * one_star))
    dhasa_seed = (asc_house + int ((moon_longitude - (nak-1) * one_star) // nak_frac)) %12 
    #print('dhasa_seed',dhasa_seed)
    dhasa_lords = [(dhasa_seed+h+12)%12 for h in range(12)]
    if dhasa_seed in const.even_signs:
        dhasa_lords = [(dhasa_seed-h+12)%12 for h in range(12)]
    #print(dhasa_lords)
    ak = house.chara_karakas(planet_positions)[0]
    akh = planet_positions[ak+1][1][0]
    dhasa_info = []
    for dhasa_lord in dhasa_lords:
        duration = 9
        bhukthis = [(akh+h+12)%12 for h in range(12)]
        if akh in [1,5,7,10]:
            bhukthis = [(akh-h+12)%12 for h in range(12)]
        if include_antardhasa:
            dd = duration/len(bhukthis)
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
    pvr_tests.tara_lagna_dhasa_test()
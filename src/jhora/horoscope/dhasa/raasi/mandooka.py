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
""" method = 2 KN Rao Method - Working. Method 1=> Sanjay Rath - yet to be implemented """
sidereal_year = const.sidereal_year
dhasa_order = {0:([0,3,6,9, 2,5,8,11, 1,4,7,10],[0,9,6,3, 2,11,8,5, 1,10,7,4]),
               3:([3,6,9,0, 2,5,8,11, 1,4,7,10],[3,0,9,6, 2,11,8,5, 1,10,7,4]),
               6:([6,9,0,3, 2,5,8,11, 1,4,7,10],[6,3,0,9, 2,11,8,5, 1,10,7,4]),
               9:([9,0,3,6, 2,5,8,11, 1,4,7,10],[9,6,3,0, 2,11,8,5, 1,10,7,4]),
               2:([2,5,8,11, 1,4,7,10, 0,3,6,9],[2,11,8,5, 1,10,7,4,0,9,6,3]),
               5:([5,8,11,2, 1,4,7,10,0,3,6,9],  [5,2,11,8, 1,10,7,4,0,9,6,3]),
               8:([8,11,2,5, 1,4,7,10,0,3,6,9 ],[8,5,2,11, 1,10,7,4,0,9,6,3]),
               11:([11,2,5,8, 1,4,7,10, 0,3,6,9],[11,8,5,2, 1,10,7,4,0,9,6,3]),
               1:([1,4,7,10, 0,3,6,9, 2,5,8,11],[1,10,7,4, 0,9,6,3, 2,11,8,5]),
               4:([4,7,10,1, 0,3,6,9, 2,5,8,11],[4,1,10,7, 0,9,6,3, 2,11,8,5]),
               7:([7,10,1,4, 0,3,6,9, 2,5,8,11],[7,4,1,10, 0,9,6,3, 2,11,8,5]),
               10:([10,1,4,7, 0,3,6,9, 2,5,8,11],[10,7,4,1, 0,9,6,3, 2,11,8,5])
               }
               
def _dhasa_duration_kn_rao(planet_positions,sign):
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)
    lord_of_sign = house.house_owner_from_planet_positions(planet_positions, sign)
    house_of_lord = p_to_h[lord_of_sign]
    #print('dhasa_lord',sign,'lord_of_sign',lord_of_sign,'house_of_lord',house_of_lord,'strength',const.house_strengths_of_planets[lord_of_sign][house_of_lord])
    dhasa_period = 0
    #print('start woth dhasa years 0 - sign lord of sign house of lord dhasa years',sign,lord_of_sign,house_of_lord,dhasa_period)
    """ The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi."""
    if sign in const.even_footed_signs: # count back from sign to house_of_lord
        dhasa_period = (sign-house_of_lord+1)%12
            #print('house_of_lord',house_of_lord,'> sign',sign,'dhasa_period',dhasa_period)
    else:
        dhasa_period = (house_of_lord-sign+1)%12
    if dhasa_period <=0 or const.house_strengths_of_planets[lord_of_sign][house_of_lord] == const._OWNER_RULER:# or \
            #house_of_lord==(sign+11)%12:
        dhasa_period = 12
    if house_of_lord==(sign+6)%12:
        dhasa_period = 10
    return dhasa_period
def _dhasa_duration(lord):
    if lord in const.movable_signs:
        return 7
    elif lord in const.fixed_signs:
        return 8
    else:
        return 9
def get_dhasa_antardhasa(dob,tob,place,divisional_chart_factor=1,years=1,months=1,sixty_hours=1,include_antardhasa=True):
    method = 2 # KN Rao Method - Working 1=< Sanjay Rath - yet to be implemented
    jd_at_dob = utils.julian_day_number(dob, tob)
    planet_positions = charts.divisional_chart(jd_at_dob, place, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE, 
                                               divisional_chart_factor=divisional_chart_factor, years=years, 
                                               months=months, sixty_hours=sixty_hours)
    asc_house = planet_positions[0][1][0] ; seventh_house = (asc_house+6)%12
    dhasa_seed = asc_house
    if method == 1 and asc_house in const.even_signs: # Sanjay Rath Method
        dhasa_seed = 8
        if asc_house in const.fixed_signs:
            dhasa_seed = 6
        elif asc_house in const.dual_signs:
            dhasa_seed = 7
    else:
        dhasa_seed = house.stronger_rasi_from_planet_positions(planet_positions, asc_house, seventh_house)
    dir = 0
    if dhasa_seed in const.even_signs:
        dir = 1
    dhasa_lords = dhasa_order[dhasa_seed][dir]
    #print('dhasa_seed',dhasa_seed,'dhasa_lords',dhasa_lords)
    dhasa_info = []
    start_jd = jd_at_dob
    for dhasa_lord in dhasa_lords:
        dhasa_index = dhasa_lords.index(dhasa_lord)
        duration = _dhasa_duration_kn_rao(planet_positions,dhasa_lord) # 
        if method == 1:
            duration = _dhasa_duration(dhasa_lord)
        #print(house.rasi_names_en[dhasa_lord],duration,'years')
        bhukthis =  [dhasa_lords[(dhasa_index+h)%12] for h in range(12)]
        if include_antardhasa:
            dd = duration/12
            for bhukthi_lord in bhukthis:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                dhasa_info.append((dhasa_lord,bhukthi_lord,dhasa_start,dd))
                start_jd += dd * sidereal_year
        else:
            y,m,d,h = utils.jd_to_gregorian(start_jd)
            dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
            dhasa_info.append((dhasa_lord,dhasa_start,duration))
            start_jd += duration * sidereal_year
    return dhasa_info
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    pvr_tests.mandooka_dhasa_test()